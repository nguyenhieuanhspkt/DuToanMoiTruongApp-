from typing import List, Dict, Any

class NormCalcService:
    """
    Dịch vụ tính toán bóc tách Định mức Kinh tế - Kỹ thuật theo Thông tư 20/2017/TT-BTNMT:
    - Khoản 4.1.3: Nhân công ngoại nghiệp nhân hệ số thời tiết +20% (k_tt = 0,2 => factor 1,2).
    - Khoản 4.2: Dụng cụ tính niên hạn chuẩn 22 ca/tháng + 10% dụng cụ nhỏ phụ (factor 1,10).
    - Khoản 4.3: Thiết bị tính chuẩn 250 ca/năm (ngoại nghiệp), 200 ca/năm (biển II.6), 500 ca/năm (lab).
    - Khoản 4.4: Vật liệu tự động cộng +8% vật liệu phụ, vụn vặt và hao hụt (factor 1,08).
    """

    @staticmethod
    def extract_labor_details(item: Dict[str, Any]) -> List[Dict[str, Any]]:
        labor_list = []
        if item.get("is_header") or not item.get("tt20_data"):
            return labor_list
        qty = item.get("so_luong_mau", 0) or 0
        if qty <= 0:
            return labor_list
        m_shared = item.get("m_dung_chung", 1) or 1
        tt = item.get("tt20_data")

        # 1. Field (Ngoại nghiệp) - Khoản 4.1.3 TT20: Nhân hệ số thời tiết +20% (x1,2)
        field = tt.get("field")
        if field:
            norm_raw = float(field.get("dinh_muc_cong", 0) or 0)
            rank = field.get("dinh_bien", "1QTVTNMT hạng III.3")
            # Áp dụng hệ số thời tiết 1,2 và chia sẻ M dùng chung
            norm_weather = round((norm_raw * 1.2) / m_shared, 4)
            labor_list.append({
                "loai": "Ngoại nghiệp",
                "chuc_danh": rank,
                "dinh_muc_goc": norm_raw,
                "he_so_thoi_tiet": 1.2,
                "m_dung_chung": m_shared,
                "dinh_muc_1_mau": norm_weather,
                "so_cong_tong": round(norm_weather * qty, 4)
            })

        # 2. Lab (Nội nghiệp) - Giữ nguyên định mức phòng lab (x1,0)
        lab = tt.get("lab")
        if lab:
            norm_raw = float(lab.get("dinh_muc_cong", 0) or 0)
            rank = lab.get("dinh_bien", "1QTVTNMT hạng III.2")
            labor_list.append({
                "loai": "Nội nghiệp",
                "chuc_danh": rank,
                "dinh_muc_goc": norm_raw,
                "he_so_thoi_tiet": 1.0,
                "m_dung_chung": 1,
                "dinh_muc_1_mau": norm_raw,
                "so_cong_tong": round(norm_raw * qty, 4)
            })

        # 3. Single table (Đo nhanh / Trực tiếp toàn phần)
        single = tt.get("single")
        if single:
            norm_raw = float(single.get("dinh_muc_cong", 0) or 0)
            rank = single.get("dinh_bien", "1QTVTNMT hạng III.3")
            norm_weather = round(norm_raw * 1.2, 4)
            labor_list.append({
                "loai": "Toàn phần",
                "chuc_danh": rank,
                "dinh_muc_goc": norm_raw,
                "he_so_thoi_tiet": 1.2,
                "m_dung_chung": 1,
                "dinh_muc_1_mau": norm_weather,
                "so_cong_tong": round(norm_weather * qty, 4)
            })

        return labor_list

    @staticmethod
    def extract_materials_details(item: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Khoản 4.4 TT20: Mức vật liệu phụ, vụn vặt và hao hụt được tính bằng 8% (factor 1,08)
        """
        materials_list = []
        if item.get("is_header") or not item.get("tt20_data"):
            return materials_list
        qty = item.get("so_luong_mau", 0) or 0
        if qty <= 0:
            return materials_list
        tt = item.get("tt20_data")

        for stage, stage_name in [("field", "Ngoại nghiệp"), ("lab", "Nội nghiệp"), ("single", "Toàn phần")]:
            sub_data = tt.get(stage)
            if not sub_data:
                continue
            for mat in sub_data.get("materials", []):
                norm_raw = float(mat.get("norm", 0) or 0)
                norm_with_waste = round(norm_raw * 1.08, 6)
                materials_list.append({
                    "stage": stage_name,
                    "name": mat.get("name", "").strip(),
                    "unit": mat.get("unit", "").strip(),
                    "norm_raw": norm_raw,
                    "waste_factor": 1.08,
                    "norm_per_sample": norm_with_waste,
                    "total_qty": round(norm_with_waste * qty, 4)
                })

        return materials_list

    @staticmethod
    def extract_tools_details(item: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Khoản 4.2 TT20:
        - Thời hạn của dụng cụ tính bằng tháng (1 tháng = 22 ca).
        - Dụng cụ nhỏ, phụ được tính bằng 10% (factor 1,10).
        """
        tools_list = []
        if item.get("is_header") or not item.get("tt20_data"):
            return tools_list
        qty = item.get("so_luong_mau", 0) or 0
        if qty <= 0:
            return tools_list
        tt = item.get("tt20_data")

        for stage, stage_name in [("field", "Ngoại nghiệp"), ("lab", "Nội nghiệp"), ("single", "Toàn phần")]:
            sub_data = tt.get(stage)
            if not sub_data:
                continue
            for tool in sub_data.get("tools", []):
                raw_name = str(tool.get("name", "")).strip()
                raw_unit = str(tool.get("unit", "")).strip()
                raw_lifespan = tool.get("lifespan_months")
                raw_norm = tool.get("norm")

                # Chuẩn hóa nếu cấu trúc cột bị tráo từ file số hóa
                if raw_name.isdigit():
                    tool_name = raw_unit
                    tool_unit = str(raw_lifespan).strip()
                    try:
                        lifespan_months = float(raw_norm or 12)
                    except (ValueError, TypeError):
                        lifespan_months = 12.0
                else:
                    tool_name = raw_name
                    tool_unit = raw_unit
                    try:
                        lifespan_months = float(raw_lifespan or 12)
                    except (ValueError, TypeError):
                        lifespan_months = 12.0

                if lifespan_months <= 0:
                    lifespan_months = 12.0

                standard_shifts = lifespan_months * 22.0
                # Mức hao phí 1 mẫu = (1 / standard_shifts) x 1.10
                norm_shift_per_sample = round((1.0 / standard_shifts) * 1.10, 6)
                total_shifts = round(norm_shift_per_sample * qty, 4)

                tools_list.append({
                    "stage": stage_name,
                    "name": tool_name,
                    "unit": tool_unit,
                    "lifespan_months": lifespan_months,
                    "standard_shifts": standard_shifts,
                    "minor_tool_factor": 1.10,
                    "norm_shift_per_sample": norm_shift_per_sample,
                    "total_shifts": total_shifts
                })

        return tools_list

    @staticmethod
    def extract_equipment_details(item: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Khoản 4.3 TT20:
        - Số ca máy chuẩn/năm: Ngoại nghiệp thường = 250 ca; Biển II.6 = 200 ca; Nội nghiệp = 500 ca.
        - Đơn vị tính: ca/mẫu.
        - Tính điện năng tiêu thụ (kWh) theo công suất thiết bị.
        """
        equipment_list = []
        if item.get("is_header") or not item.get("tt20_data"):
            return equipment_list
        qty = item.get("so_luong_mau", 0) or 0
        if qty <= 0:
            return equipment_list
        tt = item.get("tt20_data")
        sec_id = item.get("sec_id", "")

        for stage, stage_name in [("field", "Ngoại nghiệp"), ("lab", "Nội nghiệp"), ("single", "Toàn phần")]:
            sub_data = tt.get(stage)
            if not sub_data:
                continue

            # Xác định số ca máy chuẩn năm
            if stage_name == "Ngoại nghiệp":
                annual_shifts = 200.0 if "II.6" in str(sec_id) else 250.0
            else:
                annual_shifts = 500.0

            for eq in sub_data.get("equipment", []):
                norm_shift = float(eq.get("norm", 0) or 0)
                spec_str = str(eq.get("spec", "")).strip().replace(",", ".")
                power_kw = 0.0
                try:
                    if spec_str and any(c.isdigit() for c in spec_str):
                        # Trích xuất số kW từ spec
                        power_kw = float(''.join(c for c in spec_str if c.isdigit() or c == '.'))
                except (ValueError, TypeError):
                    power_kw = 0.0

                total_shifts = round(norm_shift * qty, 4)
                # Điện năng = Công suất (kW) x Số giờ chạy (8h/ca) x Số ca
                total_kwh = round(power_kw * 8.0 * total_shifts, 2)

                equipment_list.append({
                    "stage": stage_name,
                    "name": eq.get("name", "").strip(),
                    "unit": eq.get("unit", "bộ").strip(),
                    "spec": eq.get("spec", "").strip(),
                    "power_kw": power_kw,
                    "annual_standard_shifts": annual_shifts,
                    "norm_shift_per_sample": norm_shift,
                    "total_shifts": total_shifts,
                    "total_kwh": total_kwh,
                    "is_inherited": norm_shift == 0.0
                })

        return equipment_list

    @staticmethod
    def calculate_material_summary(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Tổng hợp toàn bộ nhu cầu hóa chất/vật liệu toàn gói thầu trần theo quy cách và đơn vị tính
        """
        summary_map: Dict[str, Dict[str, Any]] = {}
        for item in items:
            mats = NormCalcService.extract_materials_details(item)
            for m in mats:
                key = f"{m['name']}___{m['unit']}"
                if key not in summary_map:
                    summary_map[key] = {
                        "name": m["name"],
                        "unit": m["unit"],
                        "total_quantity": 0.0,
                        "used_by_parameters_count": 0
                    }
                summary_map[key]["total_quantity"] += m["total_qty"]
                summary_map[key]["used_by_parameters_count"] += 1

        res = []
        for v in summary_map.values():
            v["total_quantity"] = round(v["total_quantity"], 4)
            res.append(v)

        return sorted(res, key=lambda x: x["name"])

    @staticmethod
    def calculate_totals(items: List[Dict[str, Any]]) -> Dict[str, Any]:
        total_items = len(items)
        total_samples = sum(item.get("so_luong_mau", 0) for item in items)
        total_field_days = 0.0
        total_lab_days = 0.0
        total_equipment_shifts = 0.0
        total_kwh = 0.0

        for item in items:
            # Labor totals
            labors = NormCalcService.extract_labor_details(item)
            for lb in labors:
                if lb["loai"] == "Ngoại nghiệp":
                    total_field_days += lb["so_cong_tong"]
                elif lb["loai"] == "Nội nghiệp":
                    total_lab_days += lb["so_cong_tong"]
                else:
                    total_field_days += lb["so_cong_tong"]

            # Equipment totals
            eqs = NormCalcService.extract_equipment_details(item)
            for eq in eqs:
                total_equipment_shifts += eq["total_shifts"]
                total_kwh += eq["total_kwh"]

        return {
            "total_items": total_items,
            "total_samples": total_samples,
            "total_field_days": round(total_field_days, 2),
            "total_lab_days": round(total_lab_days, 2),
            "total_days": round(total_field_days + total_lab_days, 2),
            "total_equipment_shifts": round(total_equipment_shifts, 2),
            "total_power_kwh": round(total_kwh, 2)
        }
