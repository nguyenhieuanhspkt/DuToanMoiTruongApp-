from typing import List, Dict, Any

class NormCalcService:
    """
    Business service calculating labor, material, tool, and equipment breakdowns
    based on TT20 standard norms and sample quantities.
    """
    @staticmethod
    def extract_labor_details(item: Dict[str, Any]) -> List[Dict[str, Any]]:
        labor_list = []
        tt = item.get("tt20_data")
        qty = item.get("so_luong_mau", 1)
        if not tt:
            return labor_list

        # Field (Ngoại nghiệp)
        field = tt.get("field")
        if field:
            norm = float(field.get("dinh_muc_cong", 0) or 0)
            rank = field.get("dinh_bien", "QTVTNMT")
            labor_list.append({
                "loai": "Ngoại nghiệp",
                "chuc_danh": rank,
                "dinh_muc_1_mau": norm,
                "so_cong_tong": round(norm * qty, 4)
            })

        # Lab (Nội nghiệp)
        lab = tt.get("lab")
        if lab:
            norm = float(lab.get("dinh_muc_cong", 0) or 0)
            rank = lab.get("dinh_bien", "QTVTNMT")
            labor_list.append({
                "loai": "Nội nghiệp",
                "chuc_danh": rank,
                "dinh_muc_1_mau": norm,
                "so_cong_tong": round(norm * qty, 4)
            })

        # Single table
        single = tt.get("single")
        if single:
            norm = float(single.get("dinh_muc_cong", 0) or 0)
            rank = single.get("dinh_bien", "QTVTNMT")
            labor_list.append({
                "loai": "Toàn phần",
                "chuc_danh": rank,
                "dinh_muc_1_mau": norm,
                "so_cong_tong": round(norm * qty, 4)
            })

        return labor_list

    @staticmethod
    def calculate_totals(items: List[Dict[str, Any]]) -> Dict[str, Any]:
        total_items = len(items)
        total_samples = sum(item.get("so_luong_mau", 0) for item in items)
        total_field_days = 0.0
        total_lab_days = 0.0

        for item in items:
            labors = NormCalcService.extract_labor_details(item)
            for lb in labors:
                if lb["loai"] == "Ngoại nghiệp":
                    total_field_days += lb["so_cong_tong"]
                elif lb["loai"] == "Nội nghiệp":
                    total_lab_days += lb["so_cong_tong"]
                else:
                    total_field_days += lb["so_cong_tong"]

        return {
            "total_items": total_items,
            "total_samples": total_samples,
            "total_field_days": round(total_field_days, 2),
            "total_lab_days": round(total_lab_days, 2),
            "total_days": round(total_field_days + total_lab_days, 2)
        }
