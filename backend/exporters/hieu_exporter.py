# Trong file hieu_exporter.py
import sys, os, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from typing import List, Dict, Optional
from backend.models.hieu_models_dto import (
    JobItemDTO, SubtotalGroupDTO, DetailItemDTO,
    DinhMucRowDTO, DinhMucHaoPhiDTO
)

# ==============================================================
# HÀM 1: Xây dựng Sheet "Dữ liệu định mức" từ JSON TT20
# ==============================================================
def build_dinh_muc_sheet(wb, data_dir: str) -> Dict[str, DinhMucRowDTO]:
    """
    Đọc toàn bộ 13 file JSON định mức TT20, ghi ra sheet 'Dữ liệu định mức'.
    Trả về dict: { ma_thong_so → DinhMucRowDTO } để sheet ĐGCT có thể link sang.

    Cấu trúc sheet (8 cột, A-H):
      A: Mã TT | B: Tên thông số | C: Phân loại | D: Định biên
      E: Loại hao phí (Nhân công / VL / DC / M)
      F: Đơn vị | G: Định mức | H: Tên vật tư / Tiêu chuẩn
    """
    ws = wb.create_sheet(title="Dữ liệu định mức")
    ws.append(["Mã TT", "Tên thông số", "Phân loại", "Định biên",
               "Loại hao phí", "Đơn vị", "Định mức", "Tên VT / Tiêu chuẩn"])
    ws.row_dimensions[1].height = 20

    row_map: Dict[str, DinhMucRowDTO] = {}
    curr_row = 2

    json_files = sorted([f for f in os.listdir(data_dir) if f.endswith('.json')])

    for fn in json_files:
        fpath = os.path.join(data_dir, fn)
        with open(fpath, encoding='utf-8') as f:
            section_data = json.load(f)

        section_id    = section_data.get('section_id', '')
        section_title = section_data.get('section_title', '')
        parameters    = section_data.get('parameters', {})

        # Dòng tiêu đề section
        ws.append([f"=== {section_id}: {section_title} ==="])
        curr_row += 1

        for ma, param in parameters.items():
            dm_dto = DinhMucRowDTO(
                ma            = ma,
                ten           = param.get('ten_thong_so', ''),
                phan_loai     = param.get('phan_loai', ''),
                dinh_bien     = param.get('dinh_bien', ''),
                dinh_muc_cong = float(param.get('dinh_muc_cong') or 0.0),
                tieu_chuan    = param.get('tieu_chuan', ''),
            )

            # Vật liệu
            for m in param.get('materials', []):
                m_norm = float(m.get('norm') or 0.0)
                if m_norm > 0:
                    dm_dto.add_hao_phi('VL', m.get('name', ''), m.get('unit', ''), m_norm)

            # Dụng cụ / CCDC (tools)
            for t in param.get('tools', []):
                t_norm = float(t.get('norm') or 0.0)
                t_name = t.get('unit') or t.get('name') or ''
                if t_norm > 0:
                    dm_dto.add_hao_phi('DC', t_name, t.get('lifespan_months', ''), t_norm)

            # Máy / thiết bị (equipment)
            for e in param.get('equipment', []):
                e_norm = float(e.get('norm') or 0.0)
                if e_norm > 0:
                    dm_dto.add_hao_phi('M', e.get('name', ''), e.get('unit', ''), e_norm)

            # Ghi dòng Nhân công (dòng đầu block)
            dm_dto.block_start  = curr_row
            dm_dto.nc_row_index = curr_row
            ws.append(dm_dto.to_nc_row(curr_row))
            curr_row += 1

            # Ghi các dòng hao phí VL / DC / M
            for hp in dm_dto.hao_phi:
                hp.row_index = curr_row
                ws.append(dm_dto.to_haophi_row(hp))
                curr_row += 1

            dm_dto.block_end = curr_row - 1
            row_map[ma] = dm_dto

        ws.append([])
        curr_row += 1

    ws.freeze_panes = "A2"
    return row_map


# ==============================================================
# HÀM 2: Xây dựng Sheet "Đơn giá chi tiết" (có link định mức)
# ==============================================================
def build_sheet_12_with_dto(
    wb, pakt_items, mats_map, tools_map, eq_map, mat_items, tools_items, equip_items,
    font_title_15b, font_sub_11i, font_header_11b, font_sec_12b, font_data_11r, font_data_11b,
    fill_header_gray, fill_sub_gray, fill_total_pale, border_cell, border_total,
    FMT_CURRENCY, FMT_NORM, FMT_PCT,
    dinh_muc_row_map: Optional[Dict[str, DinhMucRowDTO]] = None
):
    """
    Xây dựng Sheet 'Đơn giá chi tiết' hoàn toàn bằng mô hình DTO.
    Nếu dinh_muc_row_map được truyền vào, các ô định mức (cột G) sẽ
    dùng công thức link sang sheet 'Dữ liệu định mức' thay vì giá trị cứng.
    """

    ws_dgct = wb.create_sheet(title="Đơn giá chi tiết")
    ws_dgct.views.sheetView[0].showGridLines = True
    ws_dgct.append(["BẢNG ĐƠN GIÁ CHI TIẾT 1 ĐƠN VỊ CÔNG TÁC QUAN TRẮC MÔI TRƯỜNG"])
    ws_dgct.append(["='Công trình'!A3"])
    ws_dgct.append(["='Công trình'!A4"])
    ws_dgct.append([])
    ws_dgct.append([
        "STT", "Mã hiệu đơn giá", "TT Vật tư", "Mã hiệu VL, NC, M",
        "Tên công tác / Thành phần hao phí chi tiết", "Đơn vị", "Định mức", "Đơn giá (VNĐ)", "Hệ số", "Thành tiền (VNĐ)"
    ])

    # Mapping tọa độ dòng sang các sheet tổng hợp
    vl_row_mapping = {str(m.get('name', '')).lower().strip(): idx_m for idx_m, m in enumerate(mat_items, start=7)}
    nc_row_mapping = {"nc_ldkt": 7, "nc_ldpt": 8}
    eq_row_mapping = {str(e.get('name', '')).lower().strip(): idx_e for idx_e, e in enumerate(equip_items, start=7)}
    tools_row_mapping = {str(t.get('name', '')).lower().strip(): idx_t for idx_t, t in enumerate(tools_items, start=7)}

    # BƯỚC 1: CHUYỂN ĐỔI DỮ LIỆU THÔ THÀNH DANH SÁCH OBJECT DTO
    jobs_dtos: List[JobItemDTO] = []
    for idx, it in enumerate(pakt_items, start=1):
        code_str = it.get("ma_gop", f"TT20_{idx:03d}")
        name_str = it.get("thong_so", "Thông số quan trắc")
        dvt_str  = it.get("dvt", "mẫu")
        core_code = it.get("code", f"P_{idx}")
        ma_thong_so = it.get("ma_thong_so", core_code)   # key tra cứu trong dinh_muc_row_map
        tt20_data = it.get("tt20_data", {})

        job_dto = JobItemDTO(stt=idx, code=code_str, name=name_str, unit=dvt_str, quantity=1.0)

        for stage_key, stage_lbl in [('field', 'Ngoại nghiệp'), ('lab', 'Nội nghiệp'), ('single', 'Toàn phần')]:
            sub = tt20_data.get(stage_key)
            if not sub or not isinstance(sub, dict):
                continue

            # --- Lấy DinhMucRowDTO tương ứng (nếu có) ---
            dm_dto = (dinh_muc_row_map or {}).get(ma_thong_so)

            # Nhân công
            nc_norm = sub.get('dinh_muc_cong')
            nc_title = sub.get('dinh_bien') or f'Quan trắc viên ({stage_lbl})'
            if nc_norm and float(nc_norm) > 0:
                is_pt = ("phổ thông" in nc_title.lower() or "phụ việc" in nc_title.lower())
                target_row_nc = nc_row_mapping.get("nc_ldpt" if is_pt else "nc_ldkt", 7)
                # Nếu có row_map: link norm sang sheet định mức (cột G = cột 7)
                if dm_dto and dm_dto.nc_row_index:
                    norm_val = f"='Dữ liệu định mức'!$G${dm_dto.nc_row_index}"
                else:
                    norm_val = float(nc_norm)
                job_dto.add_detail("NC", DetailItemDTO(
                    code=f"NC_{core_code}", sub_code="1", name=nc_title, unit="công",
                    norm=norm_val, price_formula=f"='Nhân công'!$F${target_row_nc}", stage=stage_lbl
                ))

            # Vật liệu
            for m_idx, m in enumerate(sub.get('materials', []), 1):
                m_name = m.get('name', '').strip()
                m_norm = float(m.get('norm') or 0.0)
                if m_norm > 0:
                    target_row_vl = vl_row_mapping.get(m_name.lower().strip(), 7)
                    # Tìm dòng VL tương ứng trong định mức sheet
                    norm_val = m_norm
                    if dm_dto:
                        hp_match = next(
                            (hp for hp in dm_dto.hao_phi
                             if hp.loai == 'VL' and hp.name.strip().lower() == m_name.lower()),
                            None
                        )
                        if hp_match and hp_match.row_index:
                            norm_val = f"='Dữ liệu định mức'!$G${hp_match.row_index}"
                    job_dto.add_detail("VL", DetailItemDTO(
                        code=f"VL_{core_code}", sub_code=str(m_idx), name=m_name,
                        unit=m.get('unit', '').strip(),
                        norm=norm_val,
                        price_formula=f"='Vật liệu'!$F${target_row_vl}", stage=stage_lbl
                    ))

            # CCDC / Dụng cụ → nhóm DC
            for t_idx, t in enumerate(sub.get('tools', []), 1):
                t_norm = float(t.get('norm') or 0.0)
                t_name = t.get('unit') or t.get('name') or 'cái'
                if t_norm > 0:
                    target_row_t = tools_row_mapping.get(str(t_name).lower().strip(), 7)
                    norm_val = t_norm
                    if dm_dto:
                        hp_match = next(
                            (hp for hp in dm_dto.hao_phi
                             if hp.loai == 'DC' and hp.name.strip().lower() == str(t_name).lower()),
                            None
                        )
                        if hp_match and hp_match.row_index:
                            norm_val = f"='Dữ liệu định mức'!$G${hp_match.row_index}"
                    job_dto.add_detail("DC", DetailItemDTO(
                        code=f"DC_{core_code}", sub_code=f"DC_{t_idx}", name=f"DC: {t_name}",
                        unit=t.get('lifespan_months', 'cái'),
                        norm=norm_val,
                        price_formula=f"='Công cụ dụng cụ'!$F${target_row_t}", stage=stage_lbl
                    ))

            # Máy / Thiết bị → nhóm M
            for e_idx, e in enumerate(sub.get('equipment', []), 1):
                e_norm = float(e.get('norm') or 0.0)
                e_name = e.get('name', '').strip()
                if e_norm > 0:
                    target_row_e = eq_row_mapping.get(e_name.lower().strip(), 7)
                    norm_val = e_norm
                    if dm_dto:
                        hp_match = next(
                            (hp for hp in dm_dto.hao_phi
                             if hp.loai == 'M' and hp.name.strip().lower() == e_name.lower()),
                            None
                        )
                        if hp_match and hp_match.row_index:
                            norm_val = f"='Dữ liệu định mức'!$G${hp_match.row_index}"
                    job_dto.add_detail("M", DetailItemDTO(
                        code=f"M_{core_code}", sub_code=f"M_{e_idx}", name=e_name,
                        unit=e.get('unit', ''),
                        norm=norm_val,
                        price_formula=f"='Máy thi công'!$F${target_row_e}", stage=stage_lbl
                    ))

        jobs_dtos.append(job_dto)


    curr_dgct_r = 6
    map_dgct = {}

    for job in jobs_dtos:
        job.row_index = curr_dgct_r
        
        # 1. Ghi dòng Công việc Cha (Master Row)
        ws_dgct.append(job.to_master_row())
        ws_dgct.row_dimensions[curr_dgct_r].outlineLevel = 0
        curr_dgct_r += 1

        # Lưu lại các dòng tổng hợp subtotal của từng nhóm để sau này tính Tổng trực tiếp (T)
        group_subtotal_rows = {}

        # Định nghĩa 4 nhóm chuẩn nghiệp vụ TT20: Vật liệu, Nhân công, CCDC, Máy
        group_configs = [
            ("VL", "Vật liệu"),
            ("NC", "Nhân công"),
            ("DC", "Công cụ dụng cụ"),
            ("M",  "Máy thi công & Thiết bị"),
        ]

        # 2. Duyệt qua từng nhóm con trong 4 nhóm
        for g_key, g_label in group_configs:
            group_obj = job.groups[g_key]
            
            # Ghi dòng tiêu đề nhóm (ví dụ: "Vật liệu", "Nhân công"...)
            ws_dgct.append(["", "", "", g_label, "", "", "", "", "", ""])
            ws_dgct.row_dimensions[curr_dgct_r].outlineLevel = 1
            curr_dgct_r += 1

            if group_obj.items:
                # Ghi nhận mốc dòng bắt đầu của các item con trong nhóm
                group_obj.start_child_row = curr_dgct_r
                
                # Bơm các dòng thành phần chi tiết (Detail Items) vào
                for item in group_obj.items:
                    ws_dgct.append(item.to_row_data(curr_dgct_r))
                    ws_dgct.row_dimensions[curr_dgct_r].outlineLevel = 2
                    ws_dgct.row_dimensions[curr_dgct_r].hidden = True  # Mặc định collapse ẩn đi
                    curr_dgct_r += 1
                
                # Ghi nhận mốc dòng kết thúc của các item con
                group_obj.end_child_row = curr_dgct_r - 1

                # Nếu là nhóm Vật liệu (VL), có thêm dòng "Vật liệu phụ khác (8% VL chính)"
                if g_key == "VL":
                    ws_dgct.append([
                        "", "VL_KHAC", len(group_obj.items) + 1, "",
                        " - Vật liệu phụ khác (8% VL chính)", "%", 
                        "='Hệ số'!$C$11", "", 1.0, 
                        f"=ROUND(SUM(J{group_obj.start_child_row}:J{group_obj.end_child_row})*G{curr_dgct_r}, 0)"
                    ])
                    ws_dgct.row_dimensions[curr_dgct_r].outlineLevel = 2
                    ws_dgct.row_dimensions[curr_dgct_r].hidden = True
                    curr_dgct_r += 1

            # Gọi phương thức lấy dữ liệu dòng Subtotal của nhóm (tự động có hàm =SUM(...))
            # Cập nhật lại dải dòng subtotal trước khi xuất
            sub_row_data = group_obj.to_row_data()
            
            # Nếu nhóm có item, ta ghi đè công thức SUM chuẩn vào cột Thành tiền (cột J, index 9)
            if group_obj.items:
                sum_range_end = curr_dgct_r - 1
                sub_row_data[9] = f"=ROUND(SUM(J{group_obj.start_child_row}:J{sum_range_end}), 0)"

            ws_dgct.append(sub_row_data)
            ws_dgct.row_dimensions[curr_dgct_r].outlineLevel = 1
            
            # Lưu lại vị trí dòng subtotal của nhóm này để tính tổng chi phí trực tiếp (T)
            group_subtotal_rows[g_key] = curr_dgct_r
            curr_dgct_r += 1

        # 3. Khối tổng hợp chi phí trực tiếp và các khoản gián tiếp cho 1 mẫu
        vl_sub_r = group_subtotal_rows.get("VL", curr_dgct_r)
        nc_sub_r = group_subtotal_rows.get("NC", curr_dgct_r)
        dc_sub_r = group_subtotal_rows.get("DC", curr_dgct_r)
        m_sub_r  = group_subtotal_rows.get("M",  curr_dgct_r)

        t_row = curr_dgct_r
        ws_dgct.append(["", "", "", "Chi phi truc tiep (VL + NC + DC + M)", "T", "", "", "", "", f"=ROUND(J{vl_sub_r}+J{nc_sub_r}+J{dc_sub_r}+J{m_sub_r}, 0)"])
        ws_dgct.row_dimensions[curr_dgct_r].outlineLevel = 0
        curr_dgct_r += 1

        # Các dòng chi phí gián tiếp, VAT, Thuế dự thầu tiếp theo...
        gt_row = curr_dgct_r
        c_row = curr_dgct_r + 1
        tt_row = curr_dgct_r + 2
        tl_row = curr_dgct_r + 3
        g_row = curr_dgct_r + 4
        gtgt_row = curr_dgct_r + 5
        gxd_row = curr_dgct_r + 6
        lt_row = curr_dgct_r + 7
        total_row = curr_dgct_r + 8

        ws_dgct.append(["", "", "", "Chi phí gián tiếp (C + TT)", "GT", "", "", "", "", f"=J{c_row}+J{tt_row}"])
        curr_dgct_r += 1
        ws_dgct.append(["", "", "", "Chi phí chung (T x 20%)", "C", "", "='Hệ số'!$C$4", "", "", f"=ROUND(J{t_row}*G{c_row}, 0)"])
        curr_dgct_r += 1
        ws_dgct.append(["", "", "", "Chi phí công việc không xác định từ thiết kế", "TT", "", "='Hệ số'!$C$9", "", "", f"=ROUND(J{t_row}*G{tt_row}, 0)"])
        curr_dgct_r += 1
        ws_dgct.append(["", "", "", "Thu nhập chịu thuế tính trước", "TL", "", "='Hệ số'!$C$8", "", "", f"=ROUND((J{t_row}+J{gt_row})*G{tl_row}, 0)"])
        curr_dgct_r += 1
        ws_dgct.append(["", "", "", "Chi phí trước thuế", "G", "", "", "", "", f"=ROUND(J{t_row}+J{gt_row}+J{tl_row}, 0)"])
        curr_dgct_r += 1
        ws_dgct.append(["", "", "", "Thuế giá trị gia tăng (VAT 8%)", "GTGT", "", "='Hệ số'!$C$10", "", "", f"=ROUND(J{g_row}*G{gtgt_row}, 0)"])
        curr_dgct_r += 1
        ws_dgct.append(["", "", "", "CHI PHÍ SAU THUẾ", "Gxd", "", "", "", "", f"=ROUND(J{g_row}+J{gtgt_row}, 0)"])
        curr_dgct_r += 1
        ws_dgct.append(["", "", "", "Chi phí nhà tạm để ở và điều hành", "LT", "", "='Hệ số'!$C$6", "", "", f"=ROUND(J{g_row}*G{lt_row}*(1+'Hệ số'!$C$10), 0)"])
        curr_dgct_r += 1
        ws_dgct.append(["", "", "", "Tổng cộng đơn giá dự thầu 1 mẫu", "VNĐ", "", "", "", "", f"=ROUND(J{gxd_row}+J{lt_row}, 0)"])
        curr_dgct_r += 1

        ws_dgct.append([])
        curr_dgct_r += 1

        # Lưu lại map tọa độ phục vụ cho sheet 'Công trình' link sang
        map_dgct[job.stt] = {
            'row_vl': vl_sub_r,
            'row_nc': nc_sub_r,
            'row_dc': dc_sub_r,
            'row_m': m_sub_r,
            'row_t': t_row,
            'row_total': total_row
        }

    return ws_dgct, map_dgct


# ============================================================
#  BLOCK TEST — chạy trực tiếp: python backend/exporters/hieu_exporter.py
# ============================================================
if __name__ == "__main__":
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter

    print("=== BẮT ĐẦU TEST hieu_exporter.py ===")

    # --- Dữ liệu giả lập dùng mã thông số thực từ JSON TT20 ---
    pakt_items = [
        {
            # Thông số thực: 1KK1a = Nhiệt độ (Ngoại nghiệp, II.1)
            "ma_gop":      "II.1",
            "ma_thong_so": "1KK1a",   # key tra cứu trong dinh_muc_row_map
            "thong_so":    "Nhiệt độ",
            "dvt":         "mẫu",
            "code":        "KK_001",
            "tt20_data": {
                "field": {
                    "dinh_muc_cong": 0.22,
                    "dinh_bien": "1QTVTNMT hạng IV.2",
                    "materials": [
                        {"name": "Pin chuyên dụng",   "norm": 0.03,  "unit": "cục"},
                        {"name": "Băng giấy in",       "norm": 0.02,  "unit": "gram"},
                        {"name": "Mực máy in",         "norm": 0.002, "unit": "hộp"},
                        {"name": "Sổ công tác",        "norm": 0.005, "unit": "cuốn"},
                        {"name": "Bản đồ địa hình",    "norm": 0.02,  "unit": "tờ"},
                        {"name": "Bút ghi kính",       "norm": 0.05,  "unit": "cái"},
                    ],
                    "tools": [
                        {"name": "Đầu đo",             "unit": "cái", "lifespan_months": "cái",  "norm": 6.0},
                        {"name": "Quần áo BHLĐ",       "unit": "bộ",  "lifespan_months": "bộ",   "norm": 6.0},
                        {"name": "Giầy BHLĐ",          "unit": "đôi", "lifespan_months": "đôi",  "norm": 12.0},
                        {"name": "Mũ cứng",            "unit": "cái", "lifespan_months": "cái",  "norm": 3.0},
                        {"name": "Ô che mưa, che nắng","unit": "cái", "lifespan_months": "cái",  "norm": 24.0},
                    ],
                    "equipment": [
                        {"name": "Thiết bị đo hiện số", "unit": "bộ", "norm": 0.08},
                        {"name": "Nhiệt ẩm kế Asman",   "unit": "cái","norm": 0.08},
                        {"name": "Máy định vị GPS cầm tay","unit":"bộ","norm": 0.04},
                    ]
                }
            }
        },
        {
            # Thông số thực: 2KK4a = TSP (Nội nghiệp, II.1)
            "ma_gop":      "II.1",
            "ma_thong_so": "2KK4a",
            "thong_so":    "TSP - Tổng bụi lơ lửng",
            "dvt":         "mẫu",
            "code":        "KK_002",
            "tt20_data": {
                "lab": {
                    "dinh_muc_cong": 0.20,
                    "dinh_bien": "1QTVTNMT hạng III.1",
                    "materials": [],
                    "tools": [
                        {"name": "Nhíp",   "unit": "cái", "lifespan_months": "cái", "norm": 36.0},
                        {"name": "Đĩa cân","unit": "cái", "lifespan_months": "cái", "norm": 60.0},
                    ],
                    "equipment": []
                }
            }
        }
    ]


    mat_items  = [
        {"name": "Ống lấy mẫu"},
        {"name": "Dung dịch hấp thụ"},
        {"name": "Hóa chất phân tích"},
        {"name": "Chai lấy mẫu nước"},
        {"name": "Pin chuyên dụng"},
        {"name": "Băng giấy in"},
    ]
    tools_items  = [
        {"name": "Đầu đo"},
        {"name": "Quần áo BHLĐ"},
        {"name": "Giầy BHLĐ"},
    ]
    equip_items  = [
        {"name": "Thiết bị đo hiện số"},
        {"name": "Nhiệt ẩm kế Asman"},
    ]
    mats_map     = {}
    tools_map    = {}
    eq_map       = {}

    # --- Tạo styles giả lập (đơn giản) ---
    def make_font(**kw):  return Font(**kw)
    def make_fill(color): return PatternFill("solid", fgColor=color)
    def make_side():      return Side(style="thin")
    def make_border():
        s = make_side()
        return Border(left=s, right=s, top=s, bottom=s)

    font_title_15b  = make_font(size=15, bold=True)
    font_sub_11i    = make_font(size=11, italic=True)
    font_header_11b = make_font(size=11, bold=True)
    font_sec_12b    = make_font(size=12, bold=True)
    font_data_11r   = make_font(size=11)
    font_data_11b   = make_font(size=11, bold=True)
    fill_header_gray = make_fill("CCCCCC")
    fill_sub_gray    = make_fill("EEEEEE")
    fill_total_pale  = make_fill("FFF2CC")
    border_cell      = make_border()
    border_total     = make_border()
    FMT_CURRENCY = '#,##0'
    FMT_NORM     = '0.000'
    FMT_PCT      = '0%'

    # --- Tạo workbook ---
    wb = openpyxl.Workbook()
    # Sheet placeholder
    for sname in ['Công trình', 'Hệ số', 'Vật liệu', 'Nhân công', 'Công cụ dụng cụ', 'Máy thi công']:
        ws_tmp = wb.create_sheet(title=sname)
        ws_tmp.append(["placeholder"])

    # --- BƯỚC 1: Build sheet Dữ liệu định mức từ JSON TT20 ---
    DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'tt20_sections')
    print(f"[1] Đang load định mức từ: {os.path.abspath(DATA_DIR)}")
    dinh_muc_row_map = build_dinh_muc_sheet(wb, DATA_DIR)
    print(f"    → Đã load {len(dinh_muc_row_map)} thông số định mức")
    # Kiểm tra một vài mã
    for check_ma in ['1KK1a', '1KK1b', '2KK4a']:
        dto = dinh_muc_row_map.get(check_ma)
        if dto:
            print(f"    Mã {check_ma}: NC dòng {dto.nc_row_index}, {len(dto.hao_phi)} hao phí")
        else:
            print(f"    Mã {check_ma}: KHÔNG TÌM THẤY trong row_map")

    # --- BƯỚC 2: Build sheet Đơn giá chi tiết với link định mức ---
    print("[2] Đang xây dựng sheet Đơn giá chi tiết...")
    ws_result, map_result = build_sheet_12_with_dto(
        wb=wb,
        pakt_items=pakt_items,
        mats_map=mats_map,
        tools_map=tools_map,
        eq_map=eq_map,
        mat_items=mat_items,
        tools_items=tools_items,
        equip_items=equip_items,
        font_title_15b=font_title_15b,
        font_sub_11i=font_sub_11i,
        font_header_11b=font_header_11b,
        font_sec_12b=font_sec_12b,
        font_data_11r=font_data_11r,
        font_data_11b=font_data_11b,
        fill_header_gray=fill_header_gray,
        fill_sub_gray=fill_sub_gray,
        fill_total_pale=fill_total_pale,
        border_cell=border_cell,
        border_total=border_total,
        FMT_CURRENCY=FMT_CURRENCY,
        FMT_NORM=FMT_NORM,
        FMT_PCT=FMT_PCT,
        dinh_muc_row_map=dinh_muc_row_map,
    )

    # --- Lưu output ---
    out_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'output')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'hieu_test_output.xlsx')
    wb.save(out_path)

    # Lấy sheet định mức để kiểm tra
    ws_dm = wb["Dữ liệu định mức"]
    print(f"\n[3] Kết quả:")
    print(f"    Sheet 'Dữ liệu định mức': {ws_dm.max_row} dòng, {len(dinh_muc_row_map)} thông số")
    print(f"    Sheet 'Đơn giá chi tiết': {ws_result.max_row} dòng")

    # Kiểm tra một vài ô trong sheet ĐGCT xem có formula link không
    print(f"\n    Kiểm tra formula link trong sheet ĐGCT:")
    for row_idx in range(7, min(ws_result.max_row + 1, 30)):
        cell_g = ws_result.cell(row=row_idx, column=7)
        cell_d = ws_result.cell(row=row_idx, column=4)
        if cell_g.value and str(cell_g.value).startswith("='Dữ liệu định mức'"):
            print(f"      Dòng {row_idx:3d} | [{cell_d.value}] | Cột G (norm) = {cell_g.value}")

    print(f"\n    map_dgct keys: {list(map_result.keys())}")
    for k, v in map_result.items():
        print(f"      Job {k}: row_vl={v.get('row_vl')}, row_nc={v.get('row_nc')}, "
              f"row_dc={v.get('row_dc')}, row_m={v.get('row_m')}, total={v.get('row_total')}")

    print(f"\n✅ Xuất file thành công: {os.path.abspath(out_path)}")
    print("=== KẾT THÚC TEST ===")

