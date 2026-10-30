import os
import json
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from typing import Dict, Any, List, Tuple

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
    FMT_NORM: str
) -> Tuple[Worksheet, int]:
    """
    Xây dựng sheet 'Công cụ dụng cụ' chuẩn F1:
    - Lọc bỏ triệt để các dòng tiêu đề phân mục dựa trên STT dạng số.
    - Cột B dòng con: Link công thức động trực tiếp sang STT của sheet 'Công trình' (='Công trình'!A{row}).
    - Cột C dòng con: Link tên công tác trực tiếp từ sheet 'Công trình' (='Công trình'!D{row}).
    - Dòng cha tự động dùng hàm =SUM() tổng khối lượng các dòng con.
    """
    # Xử lý dọn dẹp nếu sheet đã tồn tại trước đó để tránh xung đột
    if "Công cụ dụng cụ" in wb.sheetnames:
        ws_dc = wb["Công cụ dụng cụ"]
        wb.remove(ws_dc)
    
    ws_dc = wb.create_sheet(title="Công cụ dụng cụ")
    ws_dc.views.sheetView[0].showGridLines = True

    # 1. KHỐI TIÊU ĐỀ CHUẨN F1
    ws_dc.append(["BẢNG TỔNG HỢP CÔNG CỤ DỤNG CỤ VÀ THIẾT BỊ THI CÔNG"])
    ws_dc.append(["(Theo định mức Thông tư 20/2017/TT-BTNMT)"])
    ws_dc.append(["='Công trình'!A3"])  # Link tên công trình động
    ws_dc.append(["='Công trình'!A4"])  # Link tên hạng mục động
    ws_dc.append([])
    ws_dc.append([
        "STT", "Mã hiệu", "Tên công cụ, dụng cụ", "Đơn vị",
        "Khối lượng tổng cộng", "Đơn giá chưa VAT", "Thành tiền (VNĐ)", "Ghi chú nguồn giá"
    ])

    # 2. TỰ ĐỘNG BÓC TÁCH DANH MỤC CÔNG CỤ DỤNG CỤ TỪ JOBS_DTOS (Loại bỏ dòng tiêu đề phân mục)
    tools_map = {}
    for job in jobs_dtos:
        # Kiểm tra chuẩn: Chỉ lấy công tác có STT dạng số hợp lệ (bỏ qua dòng tiêu đề phân mục như 'PHẦN: ...')
        raw_stt = getattr(job, 'stt', None)
        if not raw_stt or not str(raw_stt).strip().isdigit():
            continue

        dc_group = job.groups.get("DC")
        if dc_group and hasattr(dc_group, 'items'):
            for detail_item in dc_group.items:
                dc_name = detail_item.name.strip()
                dc_unit = detail_item.unit.strip() if detail_item.unit else "bộ"
                # Gom nhóm các dụng cụ trùng tên để tạo danh mục cha độc lập duy nhất
                if dc_name not in tools_map:
                    tools_map[dc_name] = {
                        "id": f"DC_{len(tools_map)+1:03d}",
                        "name": dc_name,
                        "unit": dc_unit,
                        "price": 0.0
                    }
    tools_items = list(tools_map.values())

    dc_start_row = 7
    curr_row = dc_start_row

    # 3. VÒNG LẶP DUYỆT QUA TỪNG CÔNG CỤ / DỤNG CỤ CHÍNH (DÒNG CHA)
    for idx, it in enumerate(tools_items, 1):
        dc_id = it.get('id')
        dc_name = it.get('name')
        dc_unit = it.get('unit')
        price = float(it.get('price', 0.0))

        # Thu thập danh sách các công tác sử dụng CCDC này để làm dòng con truy vết
        usage_jobs = []
        for job in jobs_dtos:
            # Lọc chặn các dòng tiêu đề phân mục không có STT số
            raw_stt = getattr(job, 'stt', None)
            if not raw_stt or not str(raw_stt).strip().isdigit():
                continue

            dc_group = job.groups.get("DC")
            if dc_group and hasattr(dc_group, 'items'):
                for detail_item in dc_group.items:
                    detail_name_clean = detail_item.name.strip().lower()
                    dc_name_clean = dc_name.strip().lower()
                    if detail_name_clean in dc_name_clean or dc_name_clean in detail_name_clean:
                        usage_jobs.append({
                            "job": job,
                            "detail_item": detail_item
                        })

        parent_row = curr_row

        # --- A. GHI DÒNG CHA (CÔNG CỤ DỤNG CỤ CHÍNH) ---
        # Cột E (Khối lượng) ban đầu truyền 0, lát sau sẽ được gán hàm SUM tổng các dòng con
        row_data = [
            idx, dc_id, dc_name, dc_unit,
            0, price, f"=ROUND(E{parent_row}*F{parent_row}, 0)", "Đơn giá công bố"
        ]

        ws_dc.append(row_data)
        ws_dc.cell(parent_row, 3).font = font_data_11b  # Định dạng in đậm tên vật tư chính
        curr_row += 1

        # --- B. GHI CÁC DÒNG CON (TRUY VẾT CÔNG TÁC CHI TIẾT) ---
        child_start_row = curr_row
        for item_data in usage_jobs:
            job = item_data["job"]
            detail_item = item_data["detail_item"]

            # Lấy vị trí dòng của công việc bên sheet 'Công trình' để tạo công thức link động
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
            
            # 3. Cột E: Khối lượng định mức thành phần lấy chuẩn từ DTO
            j_qty = f"={detail_item.norm}" if hasattr(detail_item, 'norm') else "=0"

            child_row = [
                "",                 # Cột A: STT để trống đối với dòng con (Chuẩn F1)
                j_stt_formula,      # Cột B: Link STT từ 'Công trình'!A{row}
                j_name_formula,     # Cột C: Công thức trỏ động sang tên công tác bên sheet Công trình
                "",                 # Cột D: Đơn vị dòng con để trống
                j_qty,              # Cột E: Khối lượng định mức
                "",                 # Cột F: Đơn giá dòng con để trống
                f"=ROUND(E{curr_row}*F{parent_row}, 0)", # Cột G: Thành tiền theo đơn giá dòng cha
                ""                  # Cột H: Ghi chú để trống
            ]

            ws_dc.append(child_row)
            
            # Thiết lập định dạng màu xanh chuyên biệt cho các dòng con truy vết
            blue_font = Font(name="Times New Roman", size=11, bold=False, color="0000FF")
            for c_idx in range(1, 9):
                ws_dc.cell(curr_row, c_idx).font = blue_font
            curr_row += 1
            
        child_end_row = curr_row - 1

        # --- C. GỘP NHÓM (GROUP) VÀ GÁN HÀM SUM CHO DÒNG CHA ---
        if child_start_row <= child_end_row:
            # Thu gọn/mở rộng dòng con theo chuẩn outline grouping của Excel
            ws_dc.row_dimensions.group(child_start_row, child_end_row, outline_level=1, hidden=True)
            # Gán hàm SUM tổng khối lượng các dòng con vào cột E của dòng cha
            ws_dc.cell(parent_row, 5).value = f"=SUM(E{child_start_row}:E{child_end_row})"

    last_dc_item_row = curr_row - 1

    # 4. GHI DÒNG CỘNG TỔNG CHI PHÍ CÔNG CỤ DỤNG CỤ Ở CUỐI BẢNG
    ws_dc.append(["", "", "CỘNG CHI PHÍ CÔNG CỤ DỤNG CỤ:", "", "", "", f"=SUM(G{dc_start_row}:G{last_dc_item_row})", "Tổng chi phí CCDC"])
    total_dc_row = curr_row

    # 5. THIẾT LẬP ĐỊNH DẠNG & KIỂU CHỮ TOÀN SHEET
    ws_dc.cell(1, 1).font = font_title_15b
    ws_dc.cell(2, 1).font = font_sub_11i
    ws_dc.cell(3, 1).font = font_sub_11i
    ws_dc.cell(4, 1).font = font_sub_11i

    # Định dạng vùng Header bảng (Dòng 6)
    for c in range(1, 9):
        cell = ws_dc.cell(6, c)
        cell.font = font_header_11b
        cell.fill = fill_header_gray
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    # Vòng lặp áp dụng style chi tiết cho từng ô dữ liệu và tổng kết
    for r in range(dc_start_row, total_dc_row + 1):
        is_total = (r == total_dc_row)
        for c in range(1, 9):
            cell = ws_dc.cell(r, c)
            # Giữ nguyên font chữ màu xanh đối với các dòng con truy vết
            if r != total_dc_row and cell.font.color and cell.font.color.rgb == "0000FF":
                pass 
            else:
                cell.font = font_data_11b if is_total else font_data_11r
                
            cell.border = border_total if is_total else border_cell
            if is_total:
                cell.fill = fill_header_gray
            # Định dạng kiểu số tiền (currency) và định dạng chuẩn (norm)
            if c in (6, 7):
                cell.number_format = FMT_CURRENCY
            if c == 5:
                cell.number_format = FMT_NORM
            if c in (1, 2, 4):
                cell.alignment = Alignment(horizontal="center", vertical="center")

    # Thiết lập độ rộng các cột hiển thị cân đối
    ws_dc.column_dimensions['A'].width = 8
    ws_dc.column_dimensions['B'].width = 14
    ws_dc.column_dimensions['C'].width = 52
    ws_dc.column_dimensions['D'].width = 12
    ws_dc.column_dimensions['E'].width = 22
    ws_dc.column_dimensions['F'].width = 22
    ws_dc.column_dimensions['G'].width = 26
    ws_dc.column_dimensions['H'].width = 38

    return ws_dc, total_dc_row