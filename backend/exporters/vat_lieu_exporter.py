import os
import json
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from typing import Dict, Any, List, Tuple

def build_vat_lieu_sheet(
    wb, 
    last_hp_row: int,
    jobs_dtos: List[Any], # <--- Nhận danh sách JobItemDTO đã bóc tách
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
    Xây dựng sheet 'Vật liệu' chuẩn F1:
    - Lọc bỏ triệt để các dòng tiêu đề phân mục dựa trên STT dạng số.
    - Cột B dòng con: Link công thức động trực tiếp sang STT của sheet 'Công trình' (='Công trình'!A{row}).
    - Cột C dòng con: Link tên công tác trực tiếp sang sheet 'Công trình' (='Công trình'!D{row}).
    - Dòng cha tự động dùng hàm =SUM() tổng khối lượng các dòng con.
    """
    if "Vật liệu" in wb.sheetnames:
        ws_vl = wb["Vật liệu"]
        wb.remove(ws_vl)
    
    ws_vl = wb.create_sheet(title="Vật liệu")
    ws_vl.views.sheetView[0].showGridLines = True

    # 1. Khối Tiêu đề chuẩn F1
    ws_vl.append(["BẢNG TỔNG HỢP VẬT LIỆU VÀ CHÊNH LỆCH GIÁ"])
    ws_vl.append(["(Theo giá thông báo và định mức Thông tư 20/2017/TT-BTNMT)"])
    ws_vl.append(["='Công trình'!A3"])
    ws_vl.append(["='Công trình'!A4"])
    ws_vl.append([])
    ws_vl.append([
        "STT", "Mã hiệu", "Tên vật tư, hóa chất, dung môi", "Đơn vị",
        "Khối lượng tổng cộng", "Đơn giá chưa VAT", "Thành tiền vật liệu (VNĐ)", "Ghi chú nguồn giá"
    ])

    # 2. Tự động bóc tách danh mục vật liệu từ jobs_dtos (Loại bỏ dòng tiêu đề phân mục)
    mat_map = {}
    for job in jobs_dtos:
        # Kiểm tra chuẩn: Chỉ lấy công tác có STT dạng số hợp lệ (bỏ qua dòng tiêu đề phân mục như 'PHẦN: ...')
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
                        "price": 0.0, # Giá tính toán độc lập ở bước sau
                        "basis": "Chưa có giá"
                    }
    mat_items = list(mat_map.values())

    vl_start_row = 7
    curr_row = vl_start_row

    # 3. Vòng lặp ghi danh mục vật liệu chuẩn F1
    for idx, it in enumerate(mat_items, 1):
        mat_id = it.get('id', f'VL_{idx:03d}')
        mat_name = it.get('name', '').strip()
        mat_unit = str(it.get('unit', '')).strip().lower()
        price = float(it.get('price') or 0.0)
        basis = str(it.get('basis') or 'Chưa có giá')
        
        # --- Lấy danh sách usage_jobs thông qua DTO một cách chính xác ---
        usage_jobs = []
        for job in jobs_dtos:
            # Lọc chặn các dòng tiêu đề phân mục không có STT số
            raw_stt = getattr(job, 'stt', None)
            if not raw_stt or not str(raw_stt).strip().isdigit():
                continue

            vl_group = job.groups.get("VL")
            if vl_group and hasattr(vl_group, 'items'):
                for detail_item in vl_group.items:
                    detail_vl_name = str(detail_item.name).strip()
                    if detail_vl_name.lower() == mat_name.lower():
                        usage_jobs.append({
                            "job": job,
                            "detail_item": detail_item
                        })

        # Xác định trước dải dòng con để dòng cha tính toán chính xác
        num_children = len(usage_jobs)
        child_start_row = curr_row + 1
        child_end_row = curr_row + num_children if num_children > 0 else curr_row

        # --- DÒNG CHA (VẬT LIỆU CHÍNH) ---
        if num_children > 0:
            f_sum_qty = f"=ROUND(SUM(E{child_start_row}:E{child_end_row}), 4)"
        else:
            f_sum_qty = 0.0

        f_thanhtien = f"=ROUND(E{curr_row}*F{curr_row}, 0)"

        ws_vl.append([
            idx, mat_id, mat_name, mat_unit,
            f_sum_qty, price, f_thanhtien, basis
        ])
        ws_vl.cell(curr_row, 3).font = font_data_11b
        curr_row += 1  # Dịch chuyển con trỏ xuống dòng con đầu tiên

        # --- CÁC DÒNG CON (TRUY VẾT CÔNG TÁC) ---
        for item_data in usage_jobs:
            job = item_data["job"]
            detail_item = item_data["detail_item"]

            raw_stt = getattr(job, 'stt', 1)
            try:
                stt_int = int(raw_stt)
            except (ValueError, TypeError):
                stt_int = 1
                
            cong_trinh_row = getattr(job, 'row_index_in_cong_trinh', None) 
            if not cong_trinh_row:
                cong_trinh_row = 6 + stt_int - 1

            # 1. Cột C: Link tên công tác trực tiếp sang cột D của sheet 'Công trình'
            j_name_formula = f"='Công trình'!D{cong_trinh_row}"
            
            # 2. Cột B: Link công thức động STT công tác trực tiếp từ cột A của sheet 'Công trình'
            j_stt_formula = f"='Công trình'!A{cong_trinh_row}"
            
            # 3. Cột E: Khối lượng định mức
            j_qty = f"={detail_item.norm}" if hasattr(detail_item, 'norm') else "=0"

            ws_vl.append([
                "",             # Cột A: STT (để trống cho dòng con)
                j_stt_formula,  # Cột B: Link STT từ 'Công trình'!A{row}
                j_name_formula, # Cột C: Link tên công tác từ 'Công trình'!D{row}
                "",             # Cột D: Đơn vị dòng con để trống
                j_qty,          # Cột E: Khối lượng định mức
                "",             # Cột F: Đơn giá dòng con để trống
                f"=ROUND(E{curr_row}*F{curr_row-1}, 0)", # Cột G: Thành tiền
                ""              # Cột H: Ghi chú để trống
            ])
            
            blue_font = Font(name="Times New Roman", size=11, bold=False, color="0000FF")
            for c_idx in range(1, 9):
                ws_vl.cell(curr_row, c_idx).font = blue_font
            curr_row += 1

        # --- GOM NHÓM (GROUP) ĐỂ ẨN/HIỆN DÒNG CON ---
        if child_start_row <= child_end_row and num_children > 0:
            ws_vl.row_dimensions.group(child_start_row, child_end_row, outline_level=1, hidden=True)

    # --- KẾT THÚC VÒNG LẶP FOR ---
    last_mat_item_row = curr_row - 1

    # 4. Thêm dòng Vật liệu phụ khác (8% theo Khoản 4.4 TT20)
    ws_vl.append([
        len(mat_items) + 1, "VL_KHAC", "Vật liệu phụ khác (8% vật liệu chính theo Khoản 4.4 TT20)", "%",
        "8.0%", "", f"=ROUND(SUM(G{vl_start_row}:G{last_mat_item_row})*'Hệ số'!$C$11, 0)", "Hệ số 8% theo Khoản 4.4 TT20"
    ])
    vl_khac_row = curr_row
    curr_row += 1

    # 5. Dòng CỘNG TỔNG CHI PHÍ VẬT LIỆU
    ws_vl.append(["", "", "CỘNG CHI PHÍ VẬT LIỆU:", "", "", "", f"=SUM(G{vl_start_row}:G{vl_khac_row})", "Tổng chi phí vật liệu (VL)"])
    total_vl_row = curr_row

    # 6. Thiết lập Định dạng & Kiểu chữ Times New Roman đồng bộ 100%
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

    # Tùy chỉnh độ rộng cột chuẩn hiển thị
    ws_vl.column_dimensions['A'].width = 8
    ws_vl.column_dimensions['B'].width = 14
    ws_vl.column_dimensions['C'].width = 52
    ws_vl.column_dimensions['D'].width = 12
    ws_vl.column_dimensions['E'].width = 22
    ws_vl.column_dimensions['F'].width = 22
    ws_vl.column_dimensions['G'].width = 26
    ws_vl.column_dimensions['H'].width = 38

    return ws_vl, total_vl_row