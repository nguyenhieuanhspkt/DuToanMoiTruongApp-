import os
import json
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from typing import Dict, Any, List, Tuple, Optional


def _init_vat_lieu_sheet(wb) -> Worksheet:
    """Khởi tạo hoặc làm mới sheet 'Vật liệu' và kích hoạt hiển thị đường lưới."""
    if "Vật liệu" in wb.sheetnames:
        ws_vl = wb["Vật liệu"]
        wb.remove(ws_vl)
    
    ws_vl = wb.create_sheet(title="Vật liệu")
    ws_vl.views.sheetView[0].showGridLines = True
    return ws_vl


def _write_vat_lieu_header(ws_vl):
    """Ghi khối tiêu đề dự án và tiêu đề cột bảng Vật liệu (Dòng 1 đến 6) - Bổ sung cột Giai đoạn."""
    ws_vl.append(["BẢNG TỔNG HỢP VẬT LIỆU VÀ CHÊNH LỆCH GIÁ"])
    ws_vl.append(["(Theo giá thông báo và định mức Thông tư 20/2017/TT-BTNMT)"])
    ws_vl.append(["='Công trình'!A3"])
    ws_vl.append(["='Công trình'!A4"])
    ws_vl.append([])
    ws_vl.append([
        "STT", "Mã hiệu", "Tên vật tư, hóa chất, dung môi", "Đơn vị tính",
        "Giai đoạn", "Khối lượng tổng cộng", "Đơn giá chưa VAT", "Thành tiền vật liệu (VNĐ)", "Ghi chú nguồn giá"
    ])

def _collect_vat_lieu_items(jobs_dtos: List[Any]) -> List[Dict[str, Any]]:
    """Tự động bóc tách danh mục vật liệu duy nhất từ jobs_dtos (loại bỏ dòng tiêu đề phân mục)."""
    mat_map = {}
    for job in jobs_dtos:
        raw_stt = getattr(job, 'stt', None)
        if not raw_stt or not str(raw_stt).strip().isdigit():
            continue

        vl_group = job.groups.get("VL")
        if vl_group and hasattr(vl_group, 'items'):
            for detail_item in vl_group.items:
                vl_name = detail_item.name.strip()
                vl_unit = detail_item.unit.strip() if detail_item.unit else "kg"
                if vl_name not in mat_map:
                    mat_map[vl_name] = {
                        "id": f"VL_{len(mat_map)+1:03d}",
                        "name": vl_name,
                        "unit": vl_unit,
                        "price": 0.0,
                        "basis": "Chưa có giá"
                    }
    return list(mat_map.values())


def _find_usage_jobs_for_mat(jobs_dtos: List[Any], mat_name: str) -> List[Dict[str, Any]]:
    """Tìm danh sách các công tác sử dụng vật tư tương ứng kèm theo mỏ neo dòng sheet Công trình."""
    usage_jobs = []
    for job in jobs_dtos:
        raw_stt = getattr(job, 'stt', None)
        if not raw_stt or not str(raw_stt).strip().isdigit():
            continue

        c_row = getattr(job, 'cong_trinh_row', None)
        if not c_row:
            try:
                stt_int = int(raw_stt)
            except (ValueError, TypeError):
                stt_int = 1
            c_row = getattr(job, 'row_index_in_cong_trinh', 6 + stt_int - 1)

        vl_group = job.groups.get("VL")
        if vl_group and hasattr(vl_group, 'items'):
            for detail_item in vl_group.items:
                detail_vl_name = str(detail_item.name).strip()
                if detail_vl_name.lower() == mat_name.lower():
                    usage_jobs.append({
                        "job": job,
                        "detail_item": detail_item,
                        "cong_trinh_row": c_row
                    })
    return usage_jobs


def _write_mat_parent_row(
    ws_vl, 
    idx: int, 
    curr_row: int, 
    it: Dict[str, Any], 
    num_children: int,
    font_data_11b: Font
) -> int:
    """Ghi dòng Cha tổng hợp vật liệu tương ứng với cấu trúc cột mới (Cột F tổng khối lượng, Cột H thành tiền)."""
    child_start_row = curr_row + 1
    child_end_row = curr_row + num_children if num_children > 0 else curr_row

    # Cột F chứa khối lượng của các dòng con từ child_start_row đến child_end_row
    f_sum_qty = f"=ROUND(SUM(F{child_start_row}:F{child_end_row}), 4)" if num_children > 0 else 0.0
    
    # Cột F (Khối lượng tổng cộng) nhân với Cột G (Đơn giá chưa VAT) ra Cột H (Thành tiền)
    parent_row = curr_row
    f_thanhtien = f"=ROUND(F{parent_row}*G{parent_row}, 0)"

    mat_id = it.get('id', f'VL_{idx:03d}')
    mat_name = it.get('name', '').strip()
    mat_unit = str(it.get('unit', '')).strip().lower()
    price = float(it.get('price') or it.get('approved_price') or it.get('msc_unit_price') or 0.0)
    tbmt = str(it.get('msc_tbmt_code') or '')
    contractor = str(it.get('msc_contractor') or '')
    if tbmt:
        basis = f"TBMT: {tbmt} - {contractor}"
    else:
        basis = str(it.get('basis') or it.get('approval_basis') or it.get('note') or 'Giá trúng thầu MSC')

    # Thứ tự các cột: [STT (A), Mã hiệu (B), Tên vật tư (C), Đơn vị (D), Giai đoạn (E), Khối lượng (F), Đơn giá (G), Thành tiền (H), Ghi chú (I)]
    ws_vl.append([
        idx, mat_id, mat_name, mat_unit, "",
        f_sum_qty, price, f_thanhtien, basis
    ])
    ws_vl.cell(parent_row, 3).font = font_data_11b
    return parent_row


def _write_mat_child_rows(
    ws_vl, 
    curr_row: int, 
    usage_jobs: List[Dict[str, Any]], 
    parent_row: int
) -> int:
    """
    Ghi các dòng Con truy vết công tác kèm theo Giai đoạn (Nội nghiệp / Ngoại nghiệp):
    - Cột B: Link STT công tác từ sheet Công trình ('Công trình'!A{c_row})
    - Cột C: Link tên công tác từ sheet Công trình ('Công trình'!D{c_row})
    - Cột D: Đơn vị tính
    - Cột E: Giai đoạn (Ngoại nghiệp / Nội nghiệp) từ detail_item.stage
    - Cột F: Link trực tiếp khối lượng hao phí từ Cột M của sheet 'Hao phí VT' ('Hao phí VT'!$M${hp_row})
    - Cột H: Thành tiền theo đơn giá dòng Cha (=ROUND(F{curr_row}*$G${parent_row}, 0))
    """
    child_start_row = curr_row
    for item_data in usage_jobs:
        detail_item = item_data["detail_item"]
        c_row = item_data["cong_trinh_row"]

        j_stt_formula = f"='Công trình'!A{c_row}" if c_row else ""
        j_name_formula = f"='Công trình'!D{c_row}" if c_row else ""
        j_unit = getattr(detail_item, 'unit', '') or ''
        j_stage = getattr(detail_item, 'stage', '') or 'Toàn phần' # Lấy trực tiếp thông tin Nội/Ngoại nghiệp

        # Link trực tiếp sang cột M (Khối lượng hao phí VL đã nhân Q) của sheet 'Hao phí VT'
        hp_row = getattr(detail_item, 'hp_row', None)
        j_qty = f"='Hao phí VT'!$M${hp_row}" if hp_row else 0

        child_row = [
            "",             # Cột A: STT trống
            j_stt_formula,  # Cột B: STT công trình
            j_name_formula, # Cột C: Tên công việc
            j_unit,         # Cột D: Đơn vị
            j_stage,        # Cột E: Giai đoạn (Ngoại nghiệp / Nội nghiệp) [MỚI BỔ SUNG]
            j_qty,          # Cột F: Khối lượng hao phí
            "",             # Cột G: Đơn giá trống
            f"=ROUND(F{curr_row}*$G${parent_row}, 0)", # Cột H: Thành tiền
            ""              # Cột I: Ghi chú trống
        ]

        ws_vl.append(child_row)
        blue_font = Font(name="Times New Roman", size=11, bold=False, color="0000FF")
        for c_idx in range(1, 10):
            ws_vl.cell(curr_row, c_idx).font = blue_font
        curr_row += 1

    child_end_row = curr_row - 1
    if child_start_row <= child_end_row:
        ws_vl.row_dimensions.group(child_start_row, child_end_row, outline_level=1, hidden=True)

    return curr_row


def _write_mat_extra_and_total_rows(
    ws_vl, 
    curr_row: int, 
    vl_start_row: int, 
    last_mat_item_row: int, 
    num_mat_items: int
) -> Tuple[int, int]:
    """Ghi dòng Vật liệu phụ khác (8% theo Khoản 4.4 TT20) và dòng Cộng chi phí vật liệu."""
    # 1. Dòng Vật liệu phụ khác (8%)
    ws_vl.append([
        num_mat_items + 1, "VL_KHAC", "Vật liệu phụ khác (8% vật liệu chính theo Khoản 4.4 TT20)", "%",
        "8.0%", "", f"=ROUND(SUM(G{vl_start_row}:G{last_mat_item_row})*'Hệ số'!$C$11, 0)", "Hệ số 8% theo Khoản 4.4 TT20"
    ])
    vl_khac_row = curr_row
    curr_row += 1

    # 2. Dòng Cộng tổng chi phí vật liệu
    ws_vl.append([
        "", "", "CỘNG CHI PHÍ VẬT LIỆU:", "", "", "", 
        f"=SUM(G{vl_start_row}:G{vl_khac_row})", "Tổng chi phí vật liệu (VL)"
    ])
    total_vl_row = curr_row

    return vl_khac_row, total_vl_row


def _apply_vat_lieu_styling(
    ws_vl,
    vl_start_row: int,
    total_vl_row: int,
    font_title_15b: Font,
    font_sub_11i: Font,
    font_header_11b: Font,
    font_data_11r: Font,
    font_data_11b: Font,
    fill_header_gray: PatternFill,
    border_cell: Border,
    border_total: Border,
    FMT_CURRENCY: str,
    FMT_NORM: str
):
    """Định dạng phông chữ, màu sắc, viền và độ rộng cột cho sheet Vật liệu."""
    ws_vl.cell(1, 1).font = font_title_15b
    ws_vl.cell(2, 1).font = font_sub_11i
    ws_vl.cell(3, 1).font = font_sub_11i
    ws_vl.cell(4, 1).font = font_sub_11i

    for c in range(1, 9):
        cell = ws_vl.cell(6, c)
        cell.font = font_header_11b
        cell.fill = fill_header_gray
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    for r in range(vl_start_row, total_vl_row + 1):
        is_total = (r == total_vl_row)
        for c in range(1, 9):
            cell = ws_vl.cell(r, c)
            if r != total_vl_row and cell.font.color and cell.font.color.rgb == "0000FF":
                pass 
            else:
                cell.font = font_data_11b if is_total else font_data_11r
                
            cell.border = border_total if is_total else border_cell
            if is_total:
                cell.fill = fill_header_gray
            if c in (6, 7):
                cell.number_format = FMT_CURRENCY
            if c == 5:
                cell.number_format = FMT_NORM
            if c in (1, 2, 4):
                cell.alignment = Alignment(horizontal="center", vertical="center")

    col_widths = {
        'A': 8, 'B': 12, 'C': 44, 'D': 10, 'E': 16, 'F': 20, 'G': 20, 'H': 24, 'I': 32
    }
    for col_letter, width in col_widths.items():
        ws_vl.column_dimensions[col_letter].width = width


def build_vat_lieu_sheet(
    wb, 
    last_hp_row: int,
    jobs_dtos: List[Any],
    font_title_15b: Font,
    font_sub_11i: Font,
    font_header_11b: Font,
    font_data_11r: Font,
    font_data_11b: Font,
    fill_header_gray: PatternFill,
    fill_sub_gray: PatternFill,
    fill_total_pale: PatternFill,
    border_cell: Border,
    border_total: Border,
    FMT_CURRENCY: str,
    FMT_NORM: str,
    root_dir: Optional[str] = None,
    mat_lookup_items: Optional[List[Dict[str, Any]]] = None
) -> Tuple[Worksheet, int]:
    """
    Xây dựng sheet 'Vật liệu' chuẩn F1 điều phối qua các module chức năng chuyên biệt:
    - Dòng cha: Tính tổng từ các dòng con theo từng loại vật liệu.
    - Dòng con: Link trực tiếp khối lượng sang cột M của sheet 'Hao phí VT'.
    """
    ws_vl = _init_vat_lieu_sheet(wb)
    _write_vat_lieu_header(ws_vl)

    mat_items = _collect_vat_lieu_items(jobs_dtos)

    mat_lookup = {}
    if mat_lookup_items:
        mat_lookup = {str(it.get("name", "")).strip().lower(): it for it in mat_lookup_items}
    elif root_dir:
        try:
            from backend.storage.onedrive_adapter import OneDriveAdapter
            adapter = OneDriveAdapter(root_dir)
            raw = adapter.load_msc_materials()
            items = raw.get("items", []) if isinstance(raw, dict) else (raw if isinstance(raw, list) else [])
            mat_lookup = {str(it.get("name", "")).strip().lower(): it for it in items}
        except Exception as e:
            print(f"Warning: could not load MSC materials lookup: {e}")

    if mat_lookup:
        for it in mat_items:
            m_key = it.get("name", "").strip().lower()
            if m_key in mat_lookup:
                src = mat_lookup[m_key]
                it["price"] = src.get("msc_unit_price") or src.get("price") or 0.0
                it["msc_tbmt_code"] = src.get("msc_tbmt_code", "")
                it["msc_contractor"] = src.get("msc_contractor", "")
                it["msc_approval_date"] = src.get("msc_approval_date", "")

    vl_start_row = 7
    curr_row = vl_start_row

    for idx, it in enumerate(mat_items, 1):
        mat_name = it.get('name', '').strip()
        usage_jobs = _find_usage_jobs_for_mat(jobs_dtos, mat_name)
        num_children = len(usage_jobs)

        parent_row = _write_mat_parent_row(
            ws_vl=ws_vl,
            idx=idx,
            curr_row=curr_row,
            it=it,
            num_children=num_children,
            font_data_11b=font_data_11b
        )
        curr_row += 1

        if num_children > 0:
            curr_row = _write_mat_child_rows(
                ws_vl=ws_vl,
                curr_row=curr_row,
                usage_jobs=usage_jobs,
                parent_row=parent_row
            )

    last_mat_item_row = curr_row - 1
    vl_khac_row, total_vl_row = _write_mat_extra_and_total_rows(
        ws_vl=ws_vl,
        curr_row=curr_row,
        vl_start_row=vl_start_row,
        last_mat_item_row=last_mat_item_row,
        num_mat_items=len(mat_items)
    )

    _apply_vat_lieu_styling(
        ws_vl=ws_vl,
        vl_start_row=vl_start_row,
        total_vl_row=total_vl_row,
        font_title_15b=font_title_15b,
        font_sub_11i=font_sub_11i,
        font_header_11b=font_header_11b,
        font_data_11r=font_data_11r,
        font_data_11b=font_data_11b,
        fill_header_gray=fill_header_gray,
        border_cell=border_cell,
        border_total=border_total,
        FMT_CURRENCY=FMT_CURRENCY,
        FMT_NORM=FMT_NORM
    )

    return ws_vl, total_vl_row
