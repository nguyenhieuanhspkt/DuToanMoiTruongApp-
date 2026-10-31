import os
import json
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from typing import Dict, Any, List, Tuple, Optional


def _init_cong_cu_sheet(wb) -> Worksheet:
    """Khởi tạo hoặc làm mới sheet 'Công cụ dụng cụ' và kích hoạt hiển thị đường lưới."""
    if "Công cụ dụng cụ" in wb.sheetnames:
        ws_dc = wb["Công cụ dụng cụ"]
        wb.remove(ws_dc)
    
    ws_dc = wb.create_sheet(title="Công cụ dụng cụ")
    ws_dc.views.sheetView[0].showGridLines = True
    return ws_dc


def _write_cong_cu_header(ws_dc):
    """Ghi khối tiêu đề dự án và tiêu đề cột bảng Công cụ dụng cụ (Dòng 1 đến 6)."""
    ws_dc.append(["BẢNG TỔNG HỢP CÔNG CỤ DỤNG CỤ VÀ THIẾT BỊ THI CÔNG"])
    ws_dc.append(["(Theo định mức Thông tư 20/2017/TT-BTNMT)"])
    ws_dc.append(["='Công trình'!A3"])
    ws_dc.append(["='Công trình'!A4"])
    ws_dc.append([])
    ws_dc.append([
        "STT", "Mã hiệu", "Tên công cụ, dụng cụ", "Đơn vị",
        "Khối lượng tổng cộng", "Đơn giá chưa VAT", "Thành tiền (VNĐ)", "Ghi chú nguồn giá"
    ])


def _collect_cong_cu_items(jobs_dtos: List[Any]) -> List[Dict[str, Any]]:
    """Tự động bóc tách danh mục công cụ dụng cụ duy nhất từ jobs_dtos (loại bỏ dòng tiêu đề phân mục)."""
    tools_map = {}
    for job in jobs_dtos:
        raw_stt = getattr(job, 'stt', None)
        if not raw_stt or not str(raw_stt).strip().isdigit():
            continue

        dc_group = job.groups.get("DC")
        if dc_group and hasattr(dc_group, 'items'):
            for detail_item in dc_group.items:
                dc_name = detail_item.name.strip()
                dc_unit = detail_item.unit.strip() if detail_item.unit else "bộ"
                if dc_name not in tools_map:
                    tools_map[dc_name] = {
                        "id": f"DC_{len(tools_map)+1:03d}",
                        "name": dc_name,
                        "unit": dc_unit,
                        "price": 0.0,
                        "basis": "Đơn giá công bố"
                    }
    return list(tools_map.values())


def _find_usage_jobs_for_tool(jobs_dtos: List[Any], dc_name: str) -> List[Dict[str, Any]]:
    """Tìm danh sách các công tác sử dụng CCDC tương ứng kèm theo mỏ neo dòng sheet Công trình."""
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

        dc_group = job.groups.get("DC")
        if dc_group and hasattr(dc_group, 'items'):
            for detail_item in dc_group.items:
                detail_name_clean = detail_item.name.strip().lower()
                dc_name_clean = dc_name.strip().lower()
                if detail_name_clean == dc_name_clean or detail_name_clean in dc_name_clean or dc_name_clean in detail_name_clean:
                    usage_jobs.append({
                        "job": job,
                        "detail_item": detail_item,
                        "cong_trinh_row": c_row
                    })
    return usage_jobs


def _write_tool_parent_row(
    ws_dc, 
    idx: int, 
    curr_row: int, 
    it: Dict[str, Any], 
    num_children: int,
    font_data_11b: Font,
    ca_may_rows: Dict[str, Any] = None
) -> int:
    """Ghi dòng Cha tổng hợp CCDC, tự động liên kết đơn giá sang sheet 'Tính giá ca máy'."""
    child_start_row = curr_row + 1
    child_end_row = curr_row + num_children if num_children > 0 else curr_row

    f_sum_qty = f"=ROUND(SUM(E{child_start_row}:E{child_end_row}), 4)" if num_children > 0 else 0.0
    f_thanhtien = f"=ROUND(E{curr_row}*F{curr_row}, 0)"

    dc_id = str(it.get('id', f'DC_{idx:03d}')).strip()
    dc_name = str(it.get('name', '')).strip()
    dc_unit = str(it.get('unit', '')).strip()
    price = float(it.get('price') or 0.0)
    basis = str(it.get('basis') or 'Đơn giá công bố')

    # Tự động sinh công thức link sang Cột O của sheet 'Tính giá ca máy'
    price_formula = price
    if ca_may_rows and "dc_rows" in ca_may_rows:
        dc_map = ca_may_rows["dc_rows"]
        row_cadc = dc_map.get(dc_id) or dc_map.get(dc_id.lower()) or dc_map.get(dc_name.lower())
        if row_cadc:
            price_formula = f"='Tính giá ca máy'!$O${row_cadc}"
            basis = "Tính theo TT 13/2021/TT-BXD"

    parent_row = curr_row
    ws_dc.append([
        idx, dc_id, dc_name, dc_unit,
        f_sum_qty, price_formula, f_thanhtien, basis
    ])
    ws_dc.cell(parent_row, 3).font = font_data_11b
    return parent_row


def _write_tool_child_rows(
    ws_dc, 
    curr_row: int, 
    usage_jobs: List[Dict[str, Any]], 
    parent_row: int
) -> int:
    """
    Ghi các dòng Con truy vết công tác:
    - Cột B: Link số thứ tự công tác từ sheet Công trình ('Công trình'!A{c_row})
    - Cột C: Link tên công tác từ sheet Công trình ('Công trình'!D{c_row})
    - Cột E: Link trực tiếp khối lượng hao phí từ Cột O của sheet 'Hao phí VT' ('Hao phí VT'!$O${hp_row})
    - Cột G: Thành tiền theo đơn giá dòng Cha (=ROUND(E{curr_row}*$F${parent_row}, 0))
    """
    child_start_row = curr_row
    for item_data in usage_jobs:
        detail_item = item_data["detail_item"]
        c_row = item_data["cong_trinh_row"]

        j_stt_formula = f"='Công trình'!A{c_row}" if c_row else ""
        j_name_formula = f"='Công trình'!D{c_row}" if c_row else ""

        # Link trực tiếp sang cột O (Khối lượng hao phí DC đã nhân Q) của sheet 'Hao phí VT'
        hp_row = getattr(detail_item, 'hp_row', None)
        if hp_row:
            j_qty = f"='Hao phí VT'!$O${hp_row}"
        else:
            j_qty = 0

        child_row = [
            "",             # Cột A: STT để trống
            j_stt_formula,  # Cột B: Link STT từ 'Công trình'!A{row}
            j_name_formula, # Cột C: Link tên công tác từ 'Công trình'!D{row}
            "",             # Cột D: Đơn vị để trống
            j_qty,          # Cột E: Khối lượng hao phí
            "",             # Cột F: Đơn giá để trống
            f"=ROUND(E{curr_row}*$F${parent_row}, 0)", # Cột G: Thành tiền
            ""              # Cột H: Ghi chú để trống
        ]

        ws_dc.append(child_row)
        blue_font = Font(name="Times New Roman", size=11, bold=False, color="0000FF")
        for c_idx in range(1, 9):
            ws_dc.cell(curr_row, c_idx).font = blue_font
        curr_row += 1

    child_end_row = curr_row - 1
    if child_start_row <= child_end_row:
        ws_dc.row_dimensions.group(child_start_row, child_end_row, outline_level=1, hidden=True)

    return curr_row


def _write_tool_total_row(
    ws_dc, 
    curr_row: int, 
    dc_start_row: int, 
    last_dc_item_row: int
) -> int:
    """Ghi dòng Cộng tổng chi phí công cụ dụng cụ ở cuối bảng."""
    ws_dc.append([
        "", "", "CỘNG CHI PHÍ CÔNG CỤ DỤNG CỤ:", "", "", "", 
        f"=SUM(G{dc_start_row}:G{last_dc_item_row})", "Tổng chi phí CCDC"
    ])
    return curr_row


def _apply_cong_cu_styling(
    ws_dc,
    dc_start_row: int,
    total_dc_row: int,
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
    """Định dạng phông chữ, màu sắc, viền và độ rộng cột cho sheet Công cụ dụng cụ."""
    ws_dc.cell(1, 1).font = font_title_15b
    ws_dc.cell(2, 1).font = font_sub_11i
    ws_dc.cell(3, 1).font = font_sub_11i
    ws_dc.cell(4, 1).font = font_sub_11i

    for c in range(1, 9):
        cell = ws_dc.cell(6, c)
        cell.font = font_header_11b
        cell.fill = fill_header_gray
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    for r in range(dc_start_row, total_dc_row + 1):
        is_total = (r == total_dc_row)
        for c in range(1, 9):
            cell = ws_dc.cell(r, c)
            if r != total_dc_row and cell.font.color and cell.font.color.rgb == "0000FF":
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
        'A': 8, 'B': 14, 'C': 52, 'D': 12, 'E': 22, 'F': 22, 'G': 26, 'H': 38
    }
    for col_letter, width in col_widths.items():
        ws_dc.column_dimensions[col_letter].width = width


def build_cong_cu_sheet(
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
    ca_may_rows: Dict[str, Any] = None
) -> Tuple[Worksheet, int]:
    """
    Xây dựng sheet 'Công cụ dụng cụ' chuẩn F1 điều phối qua các module chức năng chuyên biệt:
    - Dòng cha: Tính tổng từ các dòng con theo từng loại CCDC, link đơn giá sang 'Tính giá ca máy'.
    - Dòng con: Link trực tiếp khối lượng sang cột O của sheet 'Hao phí VT'.
    """
    ws_dc = _init_cong_cu_sheet(wb)
    _write_cong_cu_header(ws_dc)

    tools_items = _collect_cong_cu_items(jobs_dtos)

    dc_start_row = 7
    curr_row = dc_start_row

    for idx, it in enumerate(tools_items, 1):
        dc_name = it.get('name', '').strip()
        usage_jobs = _find_usage_jobs_for_tool(jobs_dtos, dc_name)
        num_children = len(usage_jobs)

        parent_row = _write_tool_parent_row(
            ws_dc=ws_dc,
            idx=idx,
            curr_row=curr_row,
            it=it,
            num_children=num_children,
            font_data_11b=font_data_11b,
            ca_may_rows=ca_may_rows
        )
        curr_row += 1

        if num_children > 0:
            curr_row = _write_tool_child_rows(
                ws_dc=ws_dc,
                curr_row=curr_row,
                usage_jobs=usage_jobs,
                parent_row=parent_row
            )

    last_dc_item_row = curr_row - 1
    total_dc_row = _write_tool_total_row(
        ws_dc=ws_dc,
        curr_row=curr_row,
        dc_start_row=dc_start_row,
        last_dc_item_row=last_dc_item_row
    )

    _apply_cong_cu_styling(
        ws_dc=ws_dc,
        dc_start_row=dc_start_row,
        total_dc_row=total_dc_row,
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

    return ws_dc, total_dc_row
