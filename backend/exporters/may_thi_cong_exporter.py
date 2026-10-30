import os
import json
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from typing import Dict, Any, List, Tuple, Optional


def _init_may_thi_cong_sheet(wb) -> Worksheet:
    """Khởi tạo hoặc làm mới sheet 'Máy thi công' và kích hoạt hiển thị đường lưới."""
    if "Máy thi công" in wb.sheetnames:
        ws_m = wb["Máy thi công"]
        wb.remove(ws_m)
    
    ws_m = wb.create_sheet(title="Máy thi công")
    ws_m.views.sheetView[0].showGridLines = True
    return ws_m


def _write_may_thi_cong_header(ws_m):
    """Ghi khối tiêu đề dự án và tiêu đề cột bảng Máy thi công (Dòng 1 đến 6)."""
    ws_m.append(["BẢNG TỔNG HỢP MÁY THI CÔNG VÀ CHÊNH LỆCH GIÁ"])
    ws_m.append(["(Căn cứ theo Thông tư 20/2017/TT-BTNMT và định giá ca máy hiện hành)"])
    ws_m.append(["='Công trình'!A3"])
    ws_m.append(["='Công trình'!A4"])
    ws_m.append([])
    ws_m.cell(5, 17, "Đơn vị: đồng")

    headers = [""] * 17
    headers[0] = "STT"           # Cột A
    headers[1] = "Mã hiệu"       # Cột B
    headers[4] = "Tên vật tư"    # Cột E (Hiển thị tên máy thi công)
    headers[7] = "Đơn vị"        # Cột H
    headers[9] = "Khối lượng"    # Cột J
    headers[10] = "Giá gốc"      # Cột K
    headers[11] = "Giá thông báo"# Cột L
    headers[12] = "Bù giá"       # Cột M
    headers[13] = "Giá hiện tại" # Cột N
    headers[14] = "Chênh lệch"   # Cột O
    headers[15] = "Tổng chênh"   # Cột P
    headers[16] = "Thành tiền"   # Cột Q
    ws_m.append(headers)


def _collect_may_items(jobs_dtos: List[Any]) -> List[Dict[str, Any]]:
    """Tự động bóc tách danh mục máy móc/thiết bị duy nhất từ jobs_dtos (loại bỏ dòng tiêu đề phân mục)."""
    equip_map = {}
    for job in jobs_dtos:
        raw_stt = getattr(job, 'stt', None)
        if not raw_stt or not str(raw_stt).strip().isdigit():
            continue

        m_group = job.groups.get("M")
        if m_group and hasattr(m_group, 'items'):
            for detail_item in m_group.items:
                eq_name = detail_item.name.strip()
                eq_unit = detail_item.unit.strip() if detail_item.unit else "ca"
                if eq_name not in equip_map:
                    equip_map[eq_name] = {
                        "id": f"M_{len(equip_map)+1:03d}",
                        "name": eq_name,
                        "unit": eq_unit,
                        "price": 0.0,
                        "basis": "Đơn giá ca máy"
                    }
    return list(equip_map.values())


def _find_usage_jobs_for_machine(jobs_dtos: List[Any], m_name: str) -> List[Dict[str, Any]]:
    """Tìm danh sách các công tác sử dụng máy thi công tương ứng kèm theo mỏ neo dòng sheet Công trình."""
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

        m_group = job.groups.get("M")
        if m_group and hasattr(m_group, 'items'):
            for detail_item in m_group.items:
                detail_name_clean = detail_item.name.strip().lower()
                m_name_clean = m_name.strip().lower()
                if detail_name_clean == m_name_clean or detail_name_clean in m_name_clean or m_name_clean in detail_name_clean:
                    usage_jobs.append({
                        "job": job,
                        "detail_item": detail_item,
                        "cong_trinh_row": c_row
                    })
    return usage_jobs


def _write_machine_parent_row(
    ws_m, 
    idx: int, 
    curr_row: int, 
    it: Dict[str, Any], 
    num_children: int,
    font_data_11b: Font
) -> int:
    """Ghi dòng Cha tổng hợp máy thi công (Cột J tính SUM dòng con, Cột Q tính thành tiền)."""
    child_start_row = curr_row + 1
    child_end_row = curr_row + num_children if num_children > 0 else curr_row

    f_sum_qty = f"=ROUND(SUM(J{child_start_row}:J{child_end_row}), 4)" if num_children > 0 else 0.0

    m_id = it.get('id', f'M_{idx:03d}')
    m_name = it.get('name', '').strip()
    m_unit = str(it.get('unit', '')).strip()
    price = float(it.get('price') or 0.0)

    parent_row = curr_row
    row_data = [""] * 17
    row_data[0] = idx
    row_data[1] = m_id
    row_data[4] = m_name
    row_data[7] = m_unit
    row_data[9] = f_sum_qty
    row_data[10] = 0
    row_data[11] = 0
    row_data[12] = 0
    row_data[13] = price
    row_data[14] = f"=N{parent_row}-K{parent_row}"
    row_data[15] = f"=ROUND(J{parent_row}*O{parent_row}, 0)"
    row_data[16] = f"=ROUND(J{parent_row}*N{parent_row}, 0)"

    ws_m.append(row_data)
    ws_m.cell(parent_row, 5).font = font_data_11b
    return parent_row


def _write_machine_child_rows(
    ws_m, 
    curr_row: int, 
    usage_jobs: List[Dict[str, Any]], 
    parent_row: int
) -> int:
    """
    Ghi các dòng Con truy vết công tác:
    - Cột B: Link số thứ tự công tác từ sheet Công trình ('Công trình'!A{c_row})
    - Cột E: Link tên công tác từ sheet Công trình ('Công trình'!D{c_row})
    - Cột J: Link trực tiếp khối lượng hao phí từ Cột P của sheet 'Hao phí VT' ('Hao phí VT'!$P${hp_row})
    - Cột P, Q: Thành tiền chênh lệch và thành tiền theo đơn giá dòng Cha
    """
    child_start_row = curr_row
    for item_data in usage_jobs:
        detail_item = item_data["detail_item"]
        c_row = item_data["cong_trinh_row"]

        j_stt_formula = f"='Công trình'!A{c_row}" if c_row else ""
        j_name_formula = f"='Công trình'!D{c_row}" if c_row else ""

        # Link trực tiếp sang cột P (Khối lượng hao phí Máy thi công đã nhân Q) của sheet 'Hao phí VT'
        hp_row = getattr(detail_item, 'hp_row', None)
        if hp_row:
            j_qty = f"='Hao phí VT'!$P${hp_row}"
        else:
            j_qty = 0

        child_row = [""] * 17
        child_row[1] = j_stt_formula
        child_row[4] = j_name_formula
        child_row[9] = j_qty
        child_row[15] = f"=ROUND(J{curr_row}*$O${parent_row}, 0)"
        child_row[16] = f"=ROUND(J{curr_row}*$N${parent_row}, 0)"

        ws_m.append(child_row)
        blue_font = Font(name="Times New Roman", size=11, bold=False, color="0000FF")
        for c_idx in range(1, 18):
            ws_m.cell(curr_row, c_idx).font = blue_font
        curr_row += 1

    child_end_row = curr_row - 1
    if child_start_row <= child_end_row:
        ws_m.row_dimensions.group(child_start_row, child_end_row, outline_level=1, hidden=True)

    return curr_row


def _write_machine_total_row(
    ws_m, 
    curr_row: int, 
    m_start_row: int, 
    last_m_item_row: int
) -> int:
    """Ghi dòng Cộng tổng chi phí máy thi công ở cuối bảng."""
    total_row = [""] * 17
    total_row[2] = "Cộng Máy:"
    total_row[15] = f"=SUM(P{m_start_row}:P{last_m_item_row})"
    total_row[16] = f"=SUM(Q{m_start_row}:Q{last_m_item_row})"
    ws_m.append(total_row)
    return curr_row


def _apply_may_thi_cong_styling(
    ws_m,
    m_start_row: int,
    total_m_row: int,
    font_title_15b: Font,
    font_sub_11i: Font,
    font_header_11b: Font,
    font_data_11r: Font,
    font_data_11b: Font,
    fill_header_gray: PatternFill,
    fill_sub_gray: PatternFill,
    border_cell: Border,
    border_total: Border,
    FMT_CURRENCY: str,
    FMT_NORM: str
):
    """Định dạng phông chữ, màu sắc, viền và độ rộng cột cho sheet Máy thi công."""
    ws_m.cell(1, 1).font = font_title_15b
    ws_m.cell(2, 1).font = font_sub_11i
    ws_m.cell(3, 1).font = font_sub_11i
    ws_m.cell(4, 1).font = font_sub_11i

    for c in range(1, 18):
        cell = ws_m.cell(6, c)
        cell.font = font_header_11b
        cell.fill = fill_header_gray
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    for r in range(m_start_row, total_m_row + 1):
        is_total = (r == total_m_row)
        for c in range(1, 18):
            cell = ws_m.cell(r, c)
            if r != total_m_row and cell.font.color and cell.font.color.rgb == "0000FF":
                pass 
            else:
                cell.font = font_data_11b if is_total else font_data_11r
            cell.border = border_total if is_total else border_cell
            if is_total:
                cell.fill = fill_sub_gray
                if c in (16, 17):
                    cell.font = Font(name="Times New Roman", size=11, bold=True, color="0000FF")
            if c in (11, 12, 13, 14, 15, 16, 17):
                cell.number_format = FMT_CURRENCY
            if c == 10:
                cell.number_format = FMT_NORM

    col_widths = {
        'A': 8, 'B': 14, 'C': 10, 'D': 10, 'E': 45, 'F': 10, 'G': 10,
        'H': 10, 'I': 10, 'J': 14, 'K': 14, 'L': 10, 'M': 10,
        'N': 14, 'O': 14, 'P': 16, 'Q': 18
    }
    for col_letter, width in col_widths.items():
        ws_m.column_dimensions[col_letter].width = width


def build_may_thi_cong_sheet(
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
    FMT_NORM: str
) -> Tuple[Worksheet, int]:
    """
    Xây dựng sheet 'Máy thi công' chuẩn mẫu F1 điều phối qua các module chức năng chuyên biệt:
    - Dòng cha: Tính tổng từ các dòng con theo từng loại máy móc/thiết bị.
    - Dòng con: Link trực tiếp khối lượng sang cột P của sheet 'Hao phí VT'.
    """
    ws_m = _init_may_thi_cong_sheet(wb)
    _write_may_thi_cong_header(ws_m)

    equip_items = _collect_may_items(jobs_dtos)

    m_start_row = 7
    curr_row = m_start_row

    for idx, it in enumerate(equip_items, 1):
        m_name = it.get('name', '').strip()
        usage_jobs = _find_usage_jobs_for_machine(jobs_dtos, m_name)
        num_children = len(usage_jobs)

        parent_row = _write_machine_parent_row(
            ws_m=ws_m,
            idx=idx,
            curr_row=curr_row,
            it=it,
            num_children=num_children,
            font_data_11b=font_data_11b
        )
        curr_row += 1

        if num_children > 0:
            curr_row = _write_machine_child_rows(
                ws_m=ws_m,
                curr_row=curr_row,
                usage_jobs=usage_jobs,
                parent_row=parent_row
            )

    last_m_item_row = curr_row - 1
    total_m_row = _write_machine_total_row(
        ws_m=ws_m,
        curr_row=curr_row,
        m_start_row=m_start_row,
        last_m_item_row=last_m_item_row
    )

    _apply_may_thi_cong_styling(
        ws_m=ws_m,
        m_start_row=m_start_row,
        total_m_row=total_m_row,
        font_title_15b=font_title_15b,
        font_sub_11i=font_sub_11i,
        font_header_11b=font_header_11b,
        font_data_11r=font_data_11r,
        font_data_11b=font_data_11b,
        fill_header_gray=fill_header_gray,
        fill_sub_gray=fill_sub_gray,
        border_cell=border_cell,
        border_total=border_total,
        FMT_CURRENCY=FMT_CURRENCY,
        FMT_NORM=FMT_NORM
    )

    return ws_m, total_m_row
