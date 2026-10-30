import os
import json
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from typing import Dict, Any, List, Tuple

def build_nhan_cong_sheet(
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
    Xây dựng sheet 'Nhân công' chuẩn mẫu F1:
    - Truy vết trực tiếp sang sheet 'Công trình' thông qua mỏ neo job.cong_trinh_row đã được đăng ký sẵn.
    """
    if "Nhân công" in wb.sheetnames:
        ws_nc = wb["Nhân công"]
        wb.remove(ws_nc)
    
    ws_nc = wb.create_sheet(title="Nhân công")
    ws_nc.views.sheetView[0].showGridLines = True

    # 1. Tiêu đề
    ws_nc.append(["BẢNG TỔNG HỢP NHÂN CÔNG VÀ CHÊNH LỆCH GIÁ"])
    ws_nc.append(["(Căn cứ theo 5898/SXD-QLXD ngày 02/7/2026 của SXD tỉnh Lâm Đồng)"])
    ws_nc.append(["CÔNG TRÌNH: Quan trắc môi trường cho NMNĐ Vĩnh Tân 4"])
    ws_nc.append(["HẠNG MỤC: Toàn bộ khối lượng quan trắc môi trường"])
    ws_nc.append([])
    ws_nc.cell(5, 17, "Đơn vị: đồng")

    headers = [""] * 17
    headers[0] = "STT"
    headers[1] = "Mã hiệu"
    headers[4] = "Tên vật tư"
    headers[7] = "Đơn vị"
    headers[9] = "Khối lượng"
    headers[10] = "Giá gốc"
    headers[13] = "Giá hiện tại"
    headers[14] = "Chênh lệch"
    headers[15] = "Tổng chênh"
    headers[16] = "Thành tiền"
    ws_nc.append(headers)

    valid_jobs = [j for j in jobs_dtos if getattr(j, 'stt', None) is not None and str(j.stt).strip() != ""]

    nc_map = {}
    for job in valid_jobs:
        nc_group = job.groups.get("NC")
        if nc_group and hasattr(nc_group, 'items'):
            for detail_item in nc_group.items:
                nc_name = detail_item.name.strip()
                nc_unit = detail_item.unit.strip() if detail_item.unit else "công"
                nc_code = getattr(detail_item, 'code', f"NC_{job.code}")
                if nc_name not in nc_map:
                    nc_map[nc_name] = {
                        "id": nc_code,
                        "name": nc_name,
                        "unit": nc_unit,
                        "price": 268124.0,
                        "basis": "Đơn giá công bố"
                    }

    nc_items = list(nc_map.values())
    nc_start_row = 7
    curr_row = nc_start_row

    for idx, it in enumerate(nc_items, 1):
        nc_id = it.get('id')
        nc_name = it.get('name')
        nc_unit = it.get('unit')
        price = float(it.get('price', 0.0))

        usage_jobs = []
        for job in valid_jobs:
            # Lấy trực tiếp tọa độ dòng thực tế trên sheet Công trình đã được lưu vào DTO
            c_row = getattr(job, 'cong_trinh_row', None)

            nc_group = job.groups.get("NC")
            if nc_group and hasattr(nc_group, 'items'):
                for detail_item in nc_group.items:
                    if detail_item.name.strip().lower() == nc_name.strip().lower():
                        usage_jobs.append({
                            "job": job,
                            "detail_item": detail_item,
                            "cong_trinh_row": c_row
                        })

        num_children = len(usage_jobs)
        child_start_row = curr_row + 1
        child_end_row = curr_row + num_children if num_children > 0 else curr_row

        f_sum_qty = f"=ROUND(SUM(J{child_start_row}:J{child_end_row}), 4)" if num_children > 0 else 0.0

        parent_row = curr_row
        row_data = [""] * 17
        row_data[0] = idx
        row_data[1] = nc_id
        row_data[4] = nc_name
        row_data[7] = nc_unit
        row_data[9] = f_sum_qty
        row_data[10] = 0
        row_data[13] = price
        row_data[14] = f"=N{parent_row}-K{parent_row}"
        row_data[15] = f"=ROUND(J{parent_row}*O{parent_row}, 0)"
        row_data[16] = f"=ROUND(J{parent_row}*N{parent_row}, 0)"

        ws_nc.append(row_data)
        ws_nc.cell(parent_row, 5).font = font_data_11b
        curr_row += 1

        # --- DÒNG CON: Link trực tiếp sang sheet Công trình theo cong_trinh_row chuẩn xác ---
        for item_data in usage_jobs:
            detail_item = item_data["detail_item"]
            c_row = item_data["cong_trinh_row"]

            j_stt_formula = f"='Công trình'!A{c_row}" if c_row else ""
            j_name_formula = f"='Công trình'!D{c_row}" if c_row else ""
            j_qty = f"={detail_item.norm}" if hasattr(detail_item, 'norm') else "=0"

            child_row = [""] * 17
            child_row[1] = j_stt_formula
            child_row[4] = j_name_formula
            child_row[9] = j_qty
            child_row[15] = f"=ROUND(J{curr_row}*O{curr_row}, 0)"
            child_row[16] = f"=ROUND(J{curr_row}*N{curr_row}, 0)"

            ws_nc.append(child_row)
            for c_idx in range(1, 18):
                ws_nc.cell(curr_row, c_idx).font = Font(name="Times New Roman", size=11, color="0000FF")
            curr_row += 1

        if child_start_row <= child_end_row and num_children > 0:
            ws_nc.row_dimensions.group(child_start_row, child_end_row, outline_level=1, hidden=True)

    last_nc_item_row = curr_row - 1

    total_row = [""] * 17
    total_row[2] = "Cộng nhân công:"
    total_row[15] = f"=SUM(P{nc_start_row}:P{last_nc_item_row})"
    total_row[16] = f"=SUM(Q{nc_start_row}:Q{last_nc_item_row})"
    ws_nc.append(total_row)
    total_nc_row = curr_row

    # Style tổng thể (giữ nguyên quy chuẩn F1 cũ)
    ws_nc.cell(1, 1).font = font_title_15b
    ws_nc.cell(2, 1).font = font_sub_11i
    ws_nc.cell(3, 1).font = font_sub_11i
    ws_nc.cell(4, 1).font = font_sub_11i

    for c in range(1, 18):
        cell = ws_nc.cell(6, c)
        cell.font = font_header_11b
        cell.fill = fill_header_gray
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    for r in range(nc_start_row, total_nc_row + 1):
        is_total = (r == total_nc_row)
        for c in range(1, 18):
            cell = ws_nc.cell(r, c)
            if r != total_nc_row and cell.font.color and cell.font.color.rgb == "0000FF":
                pass 
            else:
                cell.font = font_data_11b if is_total else font_data_11r
            cell.border = border_total if is_total else border_cell
            if is_total:
                cell.fill = fill_sub_gray
                if c in (16, 17):
                    cell.font = Font(name="Times New Roman", size=11, bold=True, color="0000FF")
            if c in (11, 14, 15, 16, 17):
                cell.number_format = FMT_CURRENCY
            if c == 10:
                cell.number_format = FMT_NORM

    return ws_nc, total_nc_row