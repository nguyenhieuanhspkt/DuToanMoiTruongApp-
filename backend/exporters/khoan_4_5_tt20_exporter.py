# backend/exporters/khoan_4_5_tt20_exporter.py
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border
from openpyxl.worksheet.worksheet import Worksheet
from typing import Tuple, Any

def _init_khoan_4_5_sheet(wb: openpyxl.Workbook) -> Worksheet:
    """Khởi tạo hoặc làm mới sheet 'Khoản 4.5 TT20' và thiết lập hiển thị lưới."""
    sheet_name = "Khoản 4.5 TT20"
    if sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        ws.delete_rows(1, ws.max_row)
    else:
        ws = wb.create_sheet(title=sheet_name)
    ws.views.sheetView[0].showGridLines = True
    return ws


def _write_khoan_4_5_header(
    ws: Worksheet,
    font_title_15b: Font,
    font_sub_11i: Font,
    font_header_11b: Font,
    fill_header_gray: PatternFill,
    border_cell: Border
) -> None:
    """Ghi khối tiêu đề dự án và tiêu đề cột ma trận 4 đợt quan trắc (Dòng 1 đến 6)."""
    ws.append(["2.1.2 DỰ KIẾN KHỐI LƯỢNG NỘI DUNG CÔNG VIỆC PHỤC VỤ LẤY MẪU TẠI HIỆN TRƯỜNG (KHOẢN 4.5 TT20)"])
    ws.append(["(Căn cứ theo Mục 2.1.2 Báo cáo PAKT gửi ngày 28/10/2026 của KTAT NMNĐ Vĩnh Tân 4 và Khoản 4.5 TT 20/2017)"])
    ws.append(["='Công trình'!A3"])
    ws.append(["='Công trình'!A4"])
    ws.append([]) # Dòng 5 trống

    # Tiêu đề 11 cột ma trận 4 đợt quan trắc chuẩn Replica F1
    headers = [
        "STT",                                          # A (1)
        "Nội dung công việc / Chức danh / Phương tiện", # B (2)
        "Đơn vị",                                       # C (3)
        "Đợt 1",                                        # D (4)
        "Đợt 2",                                        # E (5)
        "Đợt 3",                                        # F (6)
        "Đợt 4",                                        # G (7)
        "Tổng cộng",                                    # H (8)
        "Đơn giá (VNĐ)",                                # I (9)
        "Thành tiền (VNĐ)",                             # J (10) ⭐ Cột lấy link sang THDT
        "Ghi chú nghiệp vụ KTAT"                        # K (11)
    ]
    ws.append(headers)

    # Format tiêu đề
    ws.cell(1, 1).font = font_title_15b
    ws.cell(2, 1).font = font_sub_11i
    ws.cell(3, 1).font = font_sub_11i
    ws.cell(4, 1).font = font_sub_11i

    ws.row_dimensions[6].height = 28
    for c in range(1, 12):
        cell = ws.cell(6, c)
        cell.font = font_header_11b
        cell.fill = fill_header_gray
        cell.border = border_cell
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)


def _write_khoan_4_5_data(
    ws: Worksheet,
    font_data_11r: Font,
    font_data_11b: Font,
    fill_header_gray: PatternFill,
    fill_sub_gray: PatternFill,
    border_cell: Border,
    border_total: Border,
    FMT_CURRENCY: str
) -> int:
    """
    Ghi dữ liệu chi phí phụ trợ phân kỳ 4 đợt quan trắc bám sát Mục 2.1.2 PAKT KTAT NMNĐ Vĩnh Tân 4:
    - Mục A: Chi phí hiện trường định kỳ theo GPMT
    - Mục B: Chương trình quan trắc đối chứng
    - Mục C: Chi phí kỹ thuật ngoài định mức khác (Sàn thao tác, Thuê tàu biển)
    - Dòng tổng cộng: Liên kết sang Sheet THDT hạng mục
    """
    rows_def = [
        # Dòng 7: Section A
        {"type": "section", "stt": "A", "name": "ĐỐI VỚI QUAN TRẮC MÔI TRƯỜNG ĐỊNH KỲ THEO GIẤY PHÉP MÔI TRƯỜNG"},
        {"type": "item", "stt": "I", "name": "Nhân sự thực hiện hiện trường", "dvt": "Người", "d1": 7, "d2": 12, "d3": 7, "d4": 14, "price": None, "formula_amt": None, "note": "QTV hạng IV không quá 30% đội ngũ"},
        {"type": "item", "stt": "II", "name": "Số chuyến xe phương tiện di chuyển", "dvt": "Chuyến", "d1": 2, "d2": 4, "d3": 2, "d4": 4, "price": 15000000, "formula_amt": "=ROUND(H9*I9, 0)", "note": "Bảo quản hỏa tốc Coliform, BOD5, CrVI (24h-48h)"},
        {"type": "item", "stt": "IV", "name": "Số ngày đi/về của mỗi đợt", "dvt": "Ngày", "d1": 4, "d2": 4, "d3": 4, "d4": 4, "price": None, "formula_amt": None, "note": "Hà Nội - Bình Thuận khứ hồi (2.800 km)"},
        {"type": "item", "stt": "VI", "name": "Số công di chuyển (Số người × Số ngày đi/về)", "dvt": "Công", "d1": 28, "d2": 48, "d3": 28, "d4": 48, "price": 319090, "formula_amt": "=ROUND(H11*I11, 0)", "note": "Tính lương theo chuẩn 22 ngày QĐ 80/2026"},
        {"type": "item", "stt": "VII", "name": "Khối lượng lưu trú tại hiện trường", "dvt": "Đêm", "d1": 0, "d2": 25, "d3": 0, "d4": 25, "price": 450000, "formula_amt": "=ROUND(H12*I12, 0)", "note": "Nhóm KKXQ 5 người x 5 ngày (TT 40/2017/TT-BTC)"},
        {"type": "item", "stt": "VIII", "name": "Khối lượng văn phòng phẩm, in ấn kết quả", "dvt": "đồng", "d1": 500000, "d2": 500000, "d3": 500000, "d4": 500000, "price": 1, "formula_amt": "=ROUND(H13*I13, 0)", "note": "Trọn gói in ấn kết quả phân tích từng đợt"},

        # Dòng 14: Section B
        {"type": "section", "stt": "B", "name": "CHƯƠNG TRÌNH QUAN TRẮC MÔI TRƯỜNG ĐỐI CHỨNG"},
        {"type": "item", "stt": "I", "name": "Nhân sự thực hiện hiện trường", "dvt": "Người", "d1": 15, "d2": 14, "d3": 15, "d4": 14, "price": None, "formula_amt": None, "note": "QTV hạng IV không quá 30% đội ngũ"},
        {"type": "item", "stt": "II", "name": "Số chuyến xe phương tiện di chuyển", "dvt": "Chuyến", "d1": 4, "d2": 4, "d3": 4, "d4": 4, "price": 15000000, "formula_amt": "=ROUND(H16*I16, 0)", "note": "Vận chuyển mẫu nước thải, khí thải, nước biển"},
        {"type": "item", "stt": "IV", "name": "Số ngày đi/về của mỗi đợt", "dvt": "Ngày", "d1": 4, "d2": 4, "d3": 4, "d4": 4, "price": None, "formula_amt": None, "note": "Hà Nội - Bình Thuận khứ hồi (2.800 km)"},
        {"type": "item", "stt": "VI", "name": "Số công di chuyển (Số người × Số ngày đi/về)", "dvt": "Công", "d1": 60, "d2": 48, "d3": 60, "d4": 48, "price": 319090, "formula_amt": "=ROUND(H18*I18, 0)", "note": "Đợt 1: 15 người x 4 ngày; Đợt 2: 12 người x 4 ngày..."},
        {"type": "item", "stt": "VII", "name": "Khối lượng lưu trú tại hiện trường", "dvt": "Đêm", "d1": 6, "d2": 25, "d3": 6, "d2": 25, "price": 450000, "formula_amt": "=ROUND(H19*I19, 0)", "note": "Lưu trú Tuy Phong theo Thông tư 40/2017/TT-BTC"},
        {"type": "item", "stt": "VIII", "name": "Khối lượng văn phòng phẩm, in ấn kết quả", "dvt": "đồng", "d1": 500000, "d2": 500000, "d3": 500000, "d4": 500000, "price": 1, "formula_amt": "=ROUND(H20*I20, 0)", "note": "Trọn gói in ấn kết quả phân tích đối chứng"},

        # Dòng 21: Section C
        {"type": "section", "stt": "C", "name": "CHI PHÍ KỸ THUẬT NGOÀI ĐỊNH MỨC KHÁC THEO KHOẢN 4.5 TT20"},
        {"type": "item", "stt": "1", "name": "Sàn thao tác, giàn giáo, lỗ lấy mẫu khí thải ống khói lò hơi", "dvt": "trọn gói", "d1": 1, "d2": 0, "d3": 0, "d4": 0, "total": 1, "price": 280000000, "amount": 280000000, "note": "Định mức Xây dựng TT 12/2021/TT-BXD"},
        {"type": "item", "stt": "2", "name": "Thuê tàu biển chuyên dụng khảo sát nước biển xa bờ bãi xỉ", "dvt": "ngày tàu", "d1": 3, "d2": 3, "d3": 3, "d4": 3, "total": 12, "price": 12000000, "formula_amt": "=ROUND(H23*I23, 0)", "note": "Tối thiểu 3 báo giá cạnh tranh NĐ 24/2024"},

        # Dòng 24: Total
        {"type": "total", "stt": "", "name": "CỘNG CHI PHÍ TÍNH RIÊNG NGOÀI ĐỊNH MỨC (KHOẢN 4.5 TT20):", "formula": "=J9+J11+J12+J13+J16+J18+J19+J20+J22+J23", "note": "Tổng chi phí tính riêng đưa vào THDT"}
    ]

    for item in rows_def:
        itype = item["type"]
        r = ws.max_row + 1

        if itype == "section":
            ws.append([item["stt"], item["name"]] + [""] * 9)
            ws.row_dimensions[r].height = 24
            for c in range(1, 12):
                cell = ws.cell(r, c)
                cell.font = font_data_11b
                cell.fill = fill_sub_gray
                cell.border = border_cell
                if c == 1:
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                elif c == 2:
                    cell.alignment = Alignment(horizontal="left", vertical="center")

        elif itype == "item":
            f_sum = item.get("total", f"=SUM(D{r}:G{r})")
            amt = item.get("formula_amt", item.get("amount", ""))
            price_val = item.get("price", "")
            
            ws.append([
                item["stt"],
                item["name"],
                item.get("dvt", ""),
                item.get("d1", 0),
                item.get("d2", 0),
                item.get("d3", 0),
                item.get("d4", 0),
                f_sum,
                price_val if price_val is not None else "",
                amt if amt is not None else "",
                item.get("note", "")
            ])
            ws.row_dimensions[r].height = 20
            for c in range(1, 12):
                cell = ws.cell(r, c)
                cell.font = font_data_11r
                cell.border = border_cell
                if c in (1, 3, 4, 5, 6, 7, 8):
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                elif c in (2, 11):
                    cell.alignment = Alignment(horizontal="left", vertical="center")
                elif c in (9, 10):
                    cell.alignment = Alignment(horizontal="right", vertical="center")
                    if cell.value != "":
                        cell.number_format = FMT_CURRENCY

        elif itype == "total":
            ws.append([
                item["stt"],
                item["name"],
                "", "", "", "", "", "", "",
                item["formula"],
                item["note"]
            ])
            ws.row_dimensions[r].height = 24
            for c in range(1, 12):
                cell = ws.cell(r, c)
                cell.font = font_data_11b
                cell.fill = fill_header_gray
                cell.border = border_total
                if c == 2:
                    cell.alignment = Alignment(horizontal="left", vertical="center")
                elif c == 10:
                    cell.alignment = Alignment(horizontal="right", vertical="center")
                    cell.number_format = FMT_CURRENCY
                elif c == 11:
                    cell.alignment = Alignment(horizontal="left", vertical="center")

    total_row = ws.max_row
    return total_row


def _apply_khoan_4_5_styling(ws: Worksheet) -> None:
    """Căn chỉnh độ rộng cột và freeze panes cho sheet Khoản 4.5 TT20."""
    col_widths = {
        'A': 8,   # STT
        'B': 46,  # Nội dung công việc
        'C': 12,  # ĐVT
        'D': 10,  # Đợt 1
        'E': 10,  # Đợt 2
        'F': 10,  # Đợt 3
        'G': 10,  # Đợt 4
        'H': 14,  # Tổng cộng
        'I': 20,  # Đơn giá
        'J': 22,  # Thành tiền
        'K': 38   # Ghi chú
    }
    for col_letter, width in col_widths.items():
        ws.column_dimensions[col_letter].width = width

    ws.freeze_panes = "A7"


def build_khoan_4_5_tt20_sheet(
    wb: openpyxl.Workbook,
    font_title_15b: Font,
    font_header_11b: Font,
    font_data_11r: Font,
    font_data_11b: Font = None,
    fill_header_gray: PatternFill = None,
    fill_sub_gray: PatternFill = None,
    border_cell: Border = None,
    border_total: Border = None,
    FMT_MONEY: str = "#,##0",
    **kwargs
) -> Tuple[Worksheet, int]:
    """
    Hàm điều phối chính: Xây dựng hoàn chỉnh sheet 'Khoản 4.5 TT20' bám sát ma trận 4 đợt của PAKT.
    Trả về (ws, total_45_row) để đăng ký vào ProjectContext liên kết sang THDT hạng mục.
    """
    fn_name = "Times New Roman"
    font_sub_11i = Font(name=fn_name, size=11, italic=True)
    if font_data_11b is None:
        font_data_11b = Font(name=fn_name, size=11, bold=True)
    if fill_sub_gray is None:
        fill_sub_gray = PatternFill(start_color="FFF2F2F2", end_color="FFF2F2F2", fill_type="solid")
    if border_total is None:
        border_total = border_cell

    ws = _init_khoan_4_5_sheet(wb)
    _write_khoan_4_5_header(ws, font_title_15b, font_sub_11i, font_header_11b, fill_header_gray, border_cell)
    total_row = _write_khoan_4_5_data(
        ws=ws,
        font_data_11r=font_data_11r,
        font_data_11b=font_data_11b,
        fill_header_gray=fill_header_gray,
        fill_sub_gray=fill_sub_gray,
        border_cell=border_cell,
        border_total=border_total,
        FMT_CURRENCY=FMT_MONEY
    )
    _apply_khoan_4_5_styling(ws)

    return ws, total_row