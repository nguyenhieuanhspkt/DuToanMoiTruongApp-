# backend/exporters/he_so_exporter.py
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border
from typing import Dict, Any

def _init_he_so_sheet(wb) -> openpyxl.worksheet.worksheet.Worksheet:
    """Khởi tạo hoặc lấy sẵn sheet 'Hệ số' và thiết lập hiển thị lưới."""
    if "Hệ số" in wb.sheetnames:
        ws_hs = wb["Hệ số"]
    else:
        ws_hs = wb.create_sheet(title="Hệ số")
    ws_hs.views.sheetView[0].showGridLines = True
    return ws_hs


def _write_he_so_header(ws_hs, font_title_15b: Font, font_header_11b: Font, fill_header_gray: PatternFill, border_cell: Border):
    """Ghi tiêu đề và định dạng header bảng hệ số."""
    ws_hs.append(["BẢNG TỔNG HỢP VÀ QUẢN LÝ HỆ SỐ ĐIỀU CHỈNH DỰ TOÁN"])
    ws_hs.append(["='Công trình'!A3"])
    ws_hs.append(["='Công trình'!A4"])
    ws_hs.append([]) # Dòng 4 trống

    # Tiêu đề cột
    headers = [
        "STT", "Mã hệ số", "Nội dung / Tên hệ số điều chỉnh", "Ký hiệu", 
        "Giá trị hệ số", "Phạm vi áp dụng", "Căn cứ pháp lý / Ghi chú"
    ]
    ws_hs.append(headers)
    ws_hs.row_dimensions[5].height = 25

    # Định dạng header (Dòng 5)
    for c in range(1, len(headers) + 1):
        cell = ws_hs.cell(5, c)
        cell.font = font_header_11b
        cell.fill = fill_header_gray
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = border_cell


def _write_he_so_data(ws_hs, he_so_items: list, font_data_11r: Font, border_cell: Border, FMT_NORM: str) -> tuple:
    """Ghi danh sách các hệ số kỹ thuật / chi phí vào sheet và trả về (last_row, he_so_rows)."""
    start_row = 6
    curr_row = start_row
    he_so_rows = {}

    # Dữ liệu chỉ giữ lại Chi phí quản lý chung và Thu nhập chịu thuế tính trước
    default_items = he_so_items if he_so_items else [
        {"ma": "CP_QLC", "ten": "Chi phí quản lý chung", "ky_hieu": "Tỷ lệ chung", "val": 0.20, "pham_vi": "Chi phí trực tiếp (I)", "ghi_chu": "Thông tư 02/2017/TT-BTC (Phụ lục 03/04)"},
        {"ma": "TN_TT", "ten": "Thu nhập chịu thuế tính trước", "ky_hieu": "TL", "val": 0.055, "pham_vi": "Giao trực tiếp", "ghi_chu": "Lợi nhuận định mức tính trước thuế"}
    ]

    for idx, item in enumerate(default_items, 1):
        ma = item.get("ma", "")
        if ma:
            he_so_rows[ma] = curr_row

        ws_hs.append([
            idx,
            ma,
            item.get("ten", ""),
            item.get("ky_hieu", ""),
            item.get("val", 1.0),
            item.get("pham_vi", ""),
            item.get("ghi_chu", "")
        ])

        # Định dạng dòng dữ liệu
        for c in range(1, 8):
            cell = ws_hs.cell(curr_row, c)
            cell.font = font_data_11r
            cell.border = border_cell
            if c in (1, 2, 4, 6):
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif c == 5:
                cell.alignment = Alignment(horizontal="right", vertical="center")
                cell.number_format = FMT_NORM

        curr_row += 1

    return curr_row - 1, he_so_rows


def _apply_he_so_column_widths(ws_hs):
    """Thiết lập độ rộng chuẩn cho các cột trong sheet Hệ số."""
    col_widths = {
        'A': 8, 'B': 16, 'C': 40, 'D': 12, 'E': 16, 'F': 22, 'G': 38
    }
    for col_letter, width in col_widths.items():
        ws_hs.column_dimensions[col_letter].width = width


def build_he_so_sheet(
    wb, 
    he_so_items: list = None,
    font_title_15b: Font = None, 
    font_header_11b: Font = None, 
    font_data_11r: Font = None, 
    fill_header_gray: PatternFill = None, 
    border_cell: Border = None, 
    FMT_NORM: str = "#,##0.0000"
):
    """
    Hàm điều phối chính: Khởi tạo, viết tiêu đề, điền dữ liệu hệ số và trả về (ws_hs, he_so_rows).
    """
    ws_hs = _init_he_so_sheet(wb)
    _write_he_so_header(ws_hs, font_title_15b, font_header_11b, fill_header_gray, border_cell)
    last_row, he_so_rows = _write_he_so_data(ws_hs, he_so_items, font_data_11r, border_cell, FMT_NORM)
    _apply_he_so_column_widths(ws_hs)

    return ws_hs, he_so_rows