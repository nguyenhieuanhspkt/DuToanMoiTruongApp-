# backend/exporters/hao_phi_vt_exporter.py
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border
from typing import List, Dict, Any

def _init_hao_phi_vt_sheet(wb) -> openpyxl.worksheet.worksheet.Worksheet:
    """Khởi tạo hoặc lấy sẵn sheet 'Hao phí VT' và thiết lập hiển thị lưới."""
    if "Hao phí VT" in wb.sheetnames:
        ws_hp = wb["Hao phí VT"]
    else:
        ws_hp = wb.create_sheet(title="Hao phí VT")
    ws_hp.views.sheetView[0].showGridLines = True
    return ws_hp


def _write_hao_phi_header(ws_hp):
    """Ghi tiêu đề chính và hệ thống Multi-level Header (Dòng 5 và 6)."""
    ws_hp.append(["HAO PHÍ VẬT LIỆU, NHÂN CÔNG, MÁY VÀ CÔNG CỤ DỤNG CỤ CHI TIẾT THEO ĐỊNH MỨC THÔNG TƯ 20/2017/TT-BTNMT"])
    ws_hp.append(["='Công trình'!A3"])
    ws_hp.append(["='Công trình'!A4"])
    ws_hp.append([]) # Dòng 4 trống

    # Multi-level Header
    ws_hp.append([
        "STT", "Mã hiệu TT20", "Phân loại", "Giai đoạn", "Tên công tác / Thành phần hao phí chi tiết", "Đơn vị", "Khối lượng công trình (Q)",
        "MỨC HAO PHÍ", "", "", "", "Hệ số", "KHỐI LƯỢNG HAO PHÍ", "", "", "", "Căn cứ pháp lý định mức TT20"
    ])
    ws_hp.append([
        "", "", "", "", "", "", "",
        "Vật liệu", "Nhân công", "Công cụ dụng cụ", "Máy thi công",
        "",
        "Vật liệu", "Nhân công", "Công cụ dụng cụ", "Máy thi công",
        ""
    ])

    # Gộp ô tiêu đề cấp lớn
    ws_hp.merge_cells("A5:A6")
    ws_hp.merge_cells("B5:B6")
    ws_hp.merge_cells("C5:C6")
    ws_hp.merge_cells("D5:D6")
    ws_hp.merge_cells("E5:E6")
    ws_hp.merge_cells("F5:F6")
    ws_hp.merge_cells("G5:G6")
    
    ws_hp.merge_cells("H5:K5")  # Mức hao phí
    ws_hp.merge_cells("L5:L6")  # Hệ số
    ws_hp.merge_cells("M5:P5")  # Khối lượng hao phí
    ws_hp.merge_cells("Q5:Q6")  # Căn cứ pháp lý


def _write_master_row(
    ws_hp, ct_r: int, core_code: str, work_unit: str, hp_row: int, 
    font_data_11b: Font, fill_header_gray: PatternFill, border_cell: Border
) -> int:
    """Quản lý và ghi dòng Cha (Mã công tác chính) có link STT, Tên và Khối lượng sang sheet Công trình."""
    ws_hp.append([
        f"='Công trình'!A{ct_r}",    # Cột A: STT (Link động sang sheet Công trình)
        core_code,                   # Cột B: Mã hiệu TT20
        "CÔNG TÁC",                  # Cột C: Phân loại
        "",                          # Cột D: Giai đoạn (Dòng cha để trống)
        f"='Công trình'!D{ct_r}",    # Cột E: Tên công tác (Link động sang sheet Công trình)
        work_unit,                   # Cột F: Đơn vị
        f"='Công trình'!L{ct_r}",    # Cột G: Khối lượng công trình (Q)
        "", "", "", "",              # Cột H, I, J, K (Mức hao phí - để trống)
        "",                          # Cột L (Hệ số)
        "", "", "", "",              # Cột M, N, O, P (Khối lượng hao phí - để trống)
        "Thông tư 20/2017/TT-BTNMT"   # Cột Q (Căn cứ pháp lý)
    ])
    master_r = hp_row
    ws_hp.cell(master_r, 5).font = font_data_11b
    for c in range(1, 18):
        ws_hp.cell(master_r, c).fill = fill_header_gray
        ws_hp.cell(master_r, c).border = border_cell
    return master_r


def _write_nhan_cong_rows(ws_hp, sub, core_code, stage_lbl, master_r, hp_row, registry, job_dto=None) -> int:
    """Quản lý và ghi các dòng Nhân công (NC) theo giai đoạn."""
    nc_norm = sub.get('dinh_muc_cong')
    nc_title = sub.get('dinh_bien') or 'Quan trắc viên'
    if nc_norm is not None and float(nc_norm) > 0:
        uid_nc = registry.generate_unique_id(core_code, 'NC', 1, stage=stage_lbl) if registry else None
        norm_val_nc = registry.get_formula_by_id(uid_nc, float(nc_norm)) if registry else float(nc_norm)
        
        ws_hp.append([
            "", ("NC_LDPT" if ("phổ thông" in nc_title.lower() or "phụ việc" in nc_title.lower()) else "NC_LDKT"), 
            "NHÂN CÔNG", stage_lbl, f" - {nc_title}", "công", "",
            "", norm_val_nc, "", "", "",    
            "", f"=ROUND(G{master_r}*I{hp_row}, 4)", "", "",  
            "Bảng 1 TT20 & TTLT 56/2015"
        ])

        # Đăng ký tọa độ hp_row cho DetailItemDTO tương ứng
        if job_dto and hasattr(job_dto, 'groups') and "NC" in job_dto.groups:
            for d_item in job_dto.groups["NC"].items:
                if getattr(d_item, 'stage', '') == stage_lbl:
                    d_item.hp_row = hp_row
                    break

        return 1
    return 0


def _write_vat_lieu_rows(ws_hp, sub, core_code, stage_lbl, master_r, hp_row, registry, job_dto=None) -> int:
    """Quản lý và ghi các dòng Vật liệu (VL) theo giai đoạn."""
    count = 0
    for m_idx, m in enumerate(sub.get('materials', []), 1):
        m_name = m.get('name', '').strip()
        m_unit = m.get('unit', '').strip()
        m_norm = float(m.get('norm') or 0.0)
        if m_norm > 0:
            uid_vl = registry.generate_unique_id(core_code, 'VL', m_idx, stage=stage_lbl) if registry else None
            norm_val_vl = registry.get_formula_by_id(uid_vl, m_norm) if registry else m_norm

            curr_row = hp_row + count
            ws_hp.append([
                "", f"VL_{core_code}", "VẬT LIỆU", stage_lbl, f" - {m_name}", m_unit, "",
                norm_val_vl, "", "", "", "",   
                f"=ROUND(G{master_r}*H{curr_row}, 4)", "", "", "",  
                "Bảng 5 TT20/2017"
            ])

            if job_dto and hasattr(job_dto, 'groups') and "VL" in job_dto.groups:
                for d_item in job_dto.groups["VL"].items:
                    if getattr(d_item, 'stage', '') == stage_lbl and str(getattr(d_item, 'sub_code', '')) == str(m_idx):
                        d_item.hp_row = curr_row
                        break

            count += 1
    return count


def _write_dung_cu_rows(ws_hp, sub, core_code, stage_lbl, master_r, hp_row, registry, job_dto=None) -> int:
    """Quản lý và ghi các dòng Công cụ dụng cụ (DC) theo giai đoạn."""
    count = 0
    for t_idx, t in enumerate(sub.get('tools', []), 1):
        raw_name = str(t.get('name') or '').strip()
        raw_unit = str(t.get('unit') or '').strip()
        raw_life = str(t.get('lifespan_months') or '').strip().lower()
        t_norm = float(t.get('norm') or 0.0)

        if raw_name.isdigit() or raw_name == "":
            t_name = raw_unit if raw_unit and not raw_unit.isdigit() else "Công cụ dụng cụ"
            t_unit = raw_life if raw_life in ['cái', 'bộ', 'đôi', 'hộp', 'chiếc', 'dây', 'tấm', 'cuốn', 'bình'] else 'cái'
        else:
            t_name = raw_name
            t_unit = raw_unit or 'cái'

        if t_norm > 0 and t_name:
            uid_dc = registry.generate_unique_id(core_code, 'DC', t_idx, stage=stage_lbl) if registry else None
            norm_val_dc = registry.get_formula_by_id(uid_dc, t_norm) if registry else t_norm

            curr_row = hp_row + count
            ws_hp.append([
                "", f"DC_{core_code}", "DỤNG CỤ", stage_lbl, f" - {t_name}", t_unit, "",
                "", "", norm_val_dc, "", "",   
                "", "", f"=ROUND(G{master_r}*J{curr_row}, 4)", "",  
                "Bảng 3 TT20/2017"
            ])

            if job_dto and hasattr(job_dto, 'groups') and "DC" in job_dto.groups:
                for d_item in job_dto.groups["DC"].items:
                    if getattr(d_item, 'stage', '') == stage_lbl and str(getattr(d_item, 'sub_code', '')) in (str(t_idx), f"DC_{t_idx}"):
                        d_item.hp_row = curr_row
                        break

            count += 1
    return count


def _write_thiet_bi_rows(ws_hp, sub, core_code, stage_lbl, master_r, hp_row, registry, job_dto=None) -> int:
    """Quản lý và ghi các dòng Thiết bị / Máy thi công (M) theo giai đoạn."""
    count = 0
    for e_idx, e in enumerate(sub.get('equipment', []), 1):
        e_name = e.get('name', '').strip()
        e_unit = e.get('unit', '').strip()
        e_norm = float(e.get('norm') or 0.0)
        if e_norm > 0:
            uid_m = registry.generate_unique_id(core_code, 'M', e_idx, stage=stage_lbl) if registry else None
            norm_val_m = registry.get_formula_by_id(uid_m, e_norm) if registry else e_norm

            curr_row = hp_row + count
            ws_hp.append([
                "", f"M_{core_code}", "THIẾT BỊ", stage_lbl, f" - {e_name}", e_unit, "",
                "", "", "", norm_val_m, "",   
                "", "", "", f"=ROUND(G{master_r}*K{curr_row}, 4)",  
                "Bảng 4 TT20 & TT 45/2013"
            ])

            if job_dto and hasattr(job_dto, 'groups') and "M" in job_dto.groups:
                for d_item in job_dto.groups["M"].items:
                    if getattr(d_item, 'stage', '') == stage_lbl and str(getattr(d_item, 'sub_code', '')) in (str(e_idx), f"M_{e_idx}"):
                        d_item.hp_row = curr_row
                        break

            count += 1
    return count


def build_hao_phi_vt_sheet(
    wb, 
    pakt_items: List[Dict[str, Any]], 
    start_ct_row: int,
    job_mapper: Any,
    font_title_15b: Font, 
    font_sub_11i: Font, 
    font_header_11b: Font, 
    font_data_11r: Font, 
    font_data_11b: Font, 
    fill_header_gray: PatternFill, 
    border_cell: Border, 
    FMT_NORM: str,
    jobs_dtos: List[Any] = None
):
    registry = job_mapper.registry if job_mapper else None
    ws_hp = _init_hao_phi_vt_sheet(wb)
    _write_hao_phi_header(ws_hp)

    hp_row = 7

    # Duyệt qua các công việc thực tế để điều phối ghi dòng cha và dòng con
    for i, it in enumerate(pakt_items, 1):
        ct_r = start_ct_row + i - 1
        tt = it.get('tt20_data') or {}
        core_code = it.get('ma_gop') or tt.get('coreCode') or it.get('code') or 'TT20'
        work_unit = it.get('dvt') or 'mẫu'
        job_dto = jobs_dtos[i - 1] if (jobs_dtos and i - 1 < len(jobs_dtos)) else None

        # 1. Ghi khung dòng Cha (Truyền đủ tham số, không dùng SUM tổng dòng con)
        master_r = _write_master_row(
            ws_hp, ct_r, core_code, work_unit, hp_row, 
            font_data_11b, fill_header_gray, border_cell
        )
        hp_row += 1

        # 2. Bung chi tiết các giai đoạn và các dòng con
        for stage_key, stage_lbl in [('field', 'Ngoại nghiệp'), ('lab', 'Nội nghiệp'), ('single', 'Toàn phần')]:
            sub = tt.get(stage_key)
            if not sub:
                continue

            hp_row += _write_nhan_cong_rows(ws_hp, sub, core_code, stage_lbl, master_r, hp_row, registry, job_dto=job_dto)
            hp_row += _write_vat_lieu_rows(ws_hp, sub, core_code, stage_lbl, master_r, hp_row, registry, job_dto=job_dto)
            hp_row += _write_dung_cu_rows(ws_hp, sub, core_code, stage_lbl, master_r, hp_row, registry, job_dto=job_dto)
            hp_row += _write_thiet_bi_rows(ws_hp, sub, core_code, stage_lbl, master_r, hp_row, registry, job_dto=job_dto)

        # Dòng trống ngăn cách các công tác
        ws_hp.append([])
        hp_row += 1

    last_hp_row = hp_row - 1

    # Format toàn bộ dữ liệu và định dạng cột
    for r in range(5, last_hp_row + 1):
        for c in range(1, 18):
            cell = ws_hp.cell(r, c)
            if r in (5, 6):
                cell.font = font_header_11b
                cell.fill = fill_header_gray
                cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                cell.border = border_cell
            else:
                if cell.value is not None and str(cell.value) != "":
                    if cell.fill.fill_type is None:
                        cell.font = font_data_11r
                    cell.border = border_cell
                    if c in (8, 9, 10, 11, 13, 14, 15, 16):
                        cell.number_format = FMT_NORM
                    if c in (1, 2, 3, 4, 6):
                        cell.alignment = Alignment(horizontal="center", vertical="center")

    col_widths = {
        'A': 8, 'B': 16, 'C': 14, 'D': 14, 'E': 40, 'F': 10, 'G': 14,
        'H': 12, 'I': 12, 'J': 12, 'K': 12, 'L': 10,
        'M': 14, 'N': 14, 'O': 14, 'P': 14, 'Q': 28
    }
    for col_letter, width in col_widths.items():
        ws_hp.column_dimensions[col_letter].width = width

    ws_hp.freeze_panes = "H7"

    return ws_hp, last_hp_row