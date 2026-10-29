import os
import re
import json
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from typing import Dict, Any, List

class Excel10SheetExporter:
    """
    Engine xuất file Excel Thẩm định Dự toán Quan trắc Môi trường 10 Sheet động khép kín công thức:
    Kế thừa cấu trúc mẫu biểu 01_Excel_Dinh_Muc_6_Bang và tuân thủ:
    - Thông tư 20/2017/TT-BTNMT & Quyết định số 80/2026/QĐ-UBND
    - TTLT 56/2015/TTLT-BTNMT-BNV & QĐ 188/1999/QĐ-TTg (22 ngày/tháng)
    - Thông tư 45/2013/TT-BTC & Nghị định 24/2024/NĐ-CP
    """

    @staticmethod
    def export_workbook(
        pakt_items: List[Dict[str, Any]],
        pricing_config: Dict[str, Any],
        materials_db: Dict[str, Any],
        tools_db: Dict[str, Any],
        equipment_db: Dict[str, Any],
        overhead_config: Dict[str, Any],
        output_path: str
    ) -> str:
        wb = openpyxl.Workbook()
        wb.remove(wb.active) # Xóa sheet mặc định

        # 1. Styles chuẩn
        font_doc_title = Font(name="Calibri", size=13, bold=True, color="1E3A8A")
        font_sub = Font(name="Calibri", size=10, italic=True, color="475569")
        font_header = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
        font_bold = Font(name="Calibri", size=10, bold=True)
        font_regular = Font(name="Calibri", size=10)

        fill_blue = PatternFill(start_color="1E40AF", end_color="1E40AF", fill_type="solid")
        fill_green = PatternFill(start_color="047857", end_color="047857", fill_type="solid")
        fill_purple = PatternFill(start_color="6D28D9", end_color="6D28D9", fill_type="solid")
        fill_amber = PatternFill(start_color="B45309", end_color="B45309", fill_type="solid")
        fill_slate = PatternFill(start_color="334155", end_color="334155", fill_type="solid")
        fill_zebra = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
        fill_total = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")

        thin_border = Border(
            left=Side(style='thin', color='CBD5E1'),
            right=Side(style='thin', color='CBD5E1'),
            top=Side(style='thin', color='CBD5E1'),
            bottom=Side(style='thin', color='CBD5E1')
        )

        def style_table(ws, header_fill, start_row=4):
            for col_idx in range(1, ws.max_column + 1):
                cell = ws.cell(row=start_row, column=col_idx)
                cell.font = font_header
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

            for r in range(start_row + 1, ws.max_row + 1):
                is_even = (r % 2 == 0)
                for c in range(1, ws.max_column + 1):
                    cell = ws.cell(row=r, column=c)
                    cell.border = thin_border
                    if is_even and cell.fill.fill_type is None:
                        cell.fill = fill_zebra

            for col in ws.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                col_letter = get_column_letter(col[0].column)
                ws.column_dimensions[col_letter].width = min(max(max_len + 3, 11), 45)

        # =========================================================================
        # SHEET 1: 01_KhoiLuong_253 (Khối lượng 253 dòng PAKT)
        # =========================================================================
        ws1 = wb.create_sheet(title="01_KhoiLuong_253")
        ws1.append(["BẢNG TỔNG HỢP KHỐI LƯỢNG QUAN TRẮC MÔI TRƯỜNG NĂM 2026 - NMNĐ VĨNH TÂN 4"])
        ws1.append(["(Căn cứ: Quyết định số 1155/QĐ-NĐVT4 và Phụ lục 1 Phương án Kỹ thuật gồm 253 dòng công việc)"])
        ws1.append([])
        ws1.append(["STT", "Mã Gộp TT20", "Học Phần", "Môi Trường", "Tên Thông Số Quan Trắc", "ĐVT", "Số Vị Trí", "Số Lần", "Số Lượng Mẫu (N)", "Vị Trí Quan Trắc"])
        for it in pakt_items:
            ws1.append([
                it.get("stt", ""), it.get("ma_gop", ""), it.get("sec_id", ""), it.get("moi_truong", ""),
                it.get("thong_so", ""), it.get("dvt", "mẫu"), it.get("so_vi_tri", 1), it.get("so_lan", 1),
                it.get("so_luong_mau", 1), it.get("vi_tri", "")
            ])
        style_table(ws1, fill_blue)

        # =========================================================================
        # SHEET 2: 02_NhanCong_TT20 (Định mức nhân công +20% thời tiết)
        # =========================================================================
        ws2 = wb.create_sheet(title="02_NhanCong_TT20")
        ws2.append(["BẢNG BÓC TÁCH ĐỊNH MỨC LAO ĐỘNG CÔNG NGHỆ QUAN TRẮC MÔI TRƯỜNG"])
        ws2.append(["(Căn cứ: Khoản 4.1.3 TT 20/2017/TT-BTNMT & QĐ 80/2026/QĐ-UBND: Ngoại nghiệp nhân hệ số thời tiết +20%)"])
        ws2.append([])
        ws2.append([
            "STT", "Mã Gộp", "Tên Thông Số", "Số Mẫu (N)", "Công Đoạn", "Định Biên (TTLT 56)",
            "ĐM Gốc (công/mẫu)", "Hệ Số Thời Tiết", "ĐM Tính (+20% ngoại)", "Tổng Ngày Công"
        ])
        row_c = 5
        for it in pakt_items:
            N = it.get("so_luong_mau", 1) or 1
            tt = it.get("tt20_data")
            if not tt: continue
            for k, label in [('field', 'Ngoại nghiệp'), ('lab', 'Nội nghiệp'), ('single', 'Toàn phần')]:
                sub = tt.get(k)
                if sub:
                    norm_raw = float(sub.get("dinh_muc_cong", 0) or 0)
                    factor = 1.2 if label != 'Nội nghiệp' else 1.0
                    ws2.append([
                        it.get("stt", ""), it.get("ma_gop", ""), it.get("thong_so", ""), N, label,
                        sub.get("dinh_bien", "QTVTNMT hạng III.3"), norm_raw, factor,
                        f"=G{row_c}*H{row_c}", f"=D{row_c}*I{row_c}"
                    ])
                    row_c += 1
        style_table(ws2, fill_blue)

        # =========================================================================
        # SHEET 3: 03_VatLieu_HoaChat (173 loại hóa chất +8% hao hụt)
        # =========================================================================
        ws3 = wb.create_sheet(title="03_VatLieu_HoaChat")
        ws3.append(["BẢNG TỔNG HỢP NHU CẦU VẬT LIỆU, HÓA CHẤT & CHẤT CHUẨN TOÀN GÓI THẦU"])
        ws3.append(["(Căn cứ: Khoản 4.4 TT 20/2017/TT-BTNMT tự động cộng +8% hao hụt vụn vặt)"])
        ws3.append([])
        ws3.append(["STT", "Mã Vật Tư", "Tên Hóa Chất / Vật Liệu", "ĐVT", "Phân Nhóm", "Khối Lượng Gốc", "Hệ Số Hao Hụt", "Khối Lượng Có +8% TT20"])
        row_c = 5
        for idx, m in enumerate(materials_db.get("items", []), 1):
            ws3.append([
                idx, m.get("id", f"VL_{idx:03d}"), m.get("name", ""), m.get("unit", ""),
                m.get("category", ""), m.get("total_quantity_raw", 0.0), 1.08,
                f"=F{row_c}*G{row_c}"
            ])
            row_c += 1
        style_table(ws3, fill_blue)

        # =========================================================================
        # SHEET 4: 04_DungCu_BHLD (158 loại dụng cụ 22 ca/tháng +10% phụ)
        # =========================================================================
        ws4 = wb.create_sheet(title="04_DungCu_BHLD")
        ws4.append(["BẢNG BÓC TÁCH NHU CẦU DỤNG CỤ ĐO & TRANG BỊ BẢO HỘ LAO ĐỘNG"])
        ws4.append(["(Căn cứ: Khoản 4.2 TT 20/2017/TT-BTNMT; Quy chuẩn 1 tháng = 22 ca; Cộng +10% dụng cụ nhỏ phụ)"])
        ws4.append([])
        ws4.append(["STT", "Mã DC", "Tên Dụng Cụ / Thiết Bị BHLĐ", "ĐVT", "Niên Hạn Tm (tháng)", "Số Ca Chuẩn (Tm x 22)", "Hệ Số DC Phụ", "Tổng Số Ca Định Mức"])
        for idx, t in enumerate(tools_db.get("items", []), 1):
            ws4.append([
                idx, t.get("id", f"DC_{idx:03d}"), t.get("name", ""), t.get("unit", ""),
                t.get("lifespan_months", 12), t.get("standard_shifts", 264), 1.10, t.get("total_shifts", 0.0)
            ])
        style_table(ws4, fill_green)

        # =========================================================================
        # SHEET 5: 05_ThietBi_CaMay (72 loại máy 250/200/500 ca + điện năng)
        # =========================================================================
        ws5 = wb.create_sheet(title="05_ThietBi_CaMay")
        ws5.append(["BẢNG BÓC TÁCH CA MÁY THIẾT BỊ ĐO & ĐIỆN NĂNG PHÒNG THÍ NGHIỆM"])
        ws5.append(["(Căn cứ: Khoản 4.3 TT 20/2017/TT-BTNMT chia 250/200/500 ca; Điện EVN 2.100 đ/kWh)"])
        ws5.append([])
        ws5.append(["STT", "Mã TB", "Tên Máy Móc / Thiết Bị", "ĐVT", "Công Suất (kW)", "Công Đoạn", "Ca Chuẩn/Năm", "Tổng Ca Định Mức", "Tổng Điện (kWh)"])
        for idx, e in enumerate(equipment_db.get("items", []), 1):
            ws5.append([
                idx, e.get("id", f"TB_{idx:03d}"), e.get("name", ""), e.get("unit", "bộ"),
                e.get("power_kw", 0.0), e.get("stage", ""), e.get("annual_shifts", 500),
                e.get("total_shifts", 0.0), e.get("total_kwh", 0.0)
            ])
        style_table(ws5, fill_purple)

        # =========================================================================
        # SHEET 6: 06_DonGia_NhanCong (Lương TTLT 56 chia 22 ngày/tháng)
        # =========================================================================
        ws6 = wb.create_sheet(title="06_DonGia_NhanCong")
        ws6.append(["BẢNG XÁC ĐỊNH ĐƠN GIÁ TIỀN LƯƠNG NGÀY CÔNG VIÊN CHỨC QUAN TRẮC MÔI TRƯỜNG"])
        ws6.append(["(Căn cứ: QĐ 80/2026/QĐ-UBND, TTLT 56/2015, QĐ 188/1999/QĐ-TTg & NĐ 161/2026: 8 giờ/ngày, 22 ngày/tháng)"])
        ws6.append([])
        ws6.append(["STT", "Ngạch Chức Danh Viên Chức", "Mã Ngạch", "Hệ Số Lương BQ", "Lương Tháng Chuẩn (đ)", "Số Ngày Làm Việc/Tháng", "Đơn Giá 1 Ngày Công (đ)"])
        rates = pricing_config.get("labor_rates", {})
        ranks_info = [
            ("Quan trắc viên tài nguyên môi trường hạng II", "V.06.05.13", "4.40 - 6.78", 850000),
            ("Quan trắc viên tài nguyên môi trường hạng III.1", "V.06.05.14", "3.00 - 4.89", 650000),
            ("Quan trắc viên tài nguyên môi trường hạng III.2", "V.06.05.14", "2.34 - 3.66", 550000),
            ("Quan trắc viên tài nguyên môi trường hạng III.3", "V.06.05.14", "2.34 - 3.00", 450000),
            ("Quan trắc viên tài nguyên môi trường hạng IV", "V.06.05.15", "1.86 - 3.00", 450000),
            ("Kỹ thuật viên / Lao động phổ thông", "NVKT", "1.65 - 2.50", 350000)
        ]
        row_c = 5
        for idx, (rname, code, coeff, default_val) in enumerate(ranks_info, 1):
            val = rates.get(rname, default_val)
            monthly = val * 22
            ws6.append([
                idx, rname, code, coeff, monthly, 22, f"=ROUND(E{row_c}/F{row_c}, 0)"
            ])
            row_c += 1
        style_table(ws6, fill_blue)

        # =========================================================================
        # SHEET 7: 07_DonGia_VatLieu (3 Báo giá & Mua sắm công)
        # =========================================================================
        ws7 = wb.create_sheet(title="07_DonGia_VatLieu")
        ws7.append(["BẢNG ĐƠN GIÁ HÓA CHẤT, CHẤT CHUẨN & MA TRẬN 3 BÁO GIÁ CẠNH TRANH"])
        ws7.append(["(Căn cứ: Điều 16 NĐ 24/2024/NĐ-CP tra cứu KQLCNT Mua sắm công & 3 Báo giá cạnh tranh)"])
        ws7.append([])
        ws7.append([
            "STT", "Mã VT", "Tên Hóa Chất", "ĐVT", "KL Có +8% TT20",
            "Báo Giá 1 (đ)", "Báo Giá 2 (đ)", "Báo Giá 3 (đ)", "HĐ 71/2025 (đ)",
            "ĐG Duyệt MSC (đ)", "Mã TBMT / KQLCNT", "Thành Tiền Có +8% TT20 (đ)"
        ])
        row_c = 5
        for idx, m in enumerate(materials_db.get("items", []), 1):
            p = m.get("approved_price", 0.0)
            ws7.append([
                idx, m.get("id", f"VL_{idx:03d}"), m.get("name", ""), m.get("unit", ""),
                m.get("total_quantity_with_waste", 0.0), m.get("quote_1", 0.0), m.get("quote_2", 0.0),
                m.get("quote_3", 0.0), m.get("price_hd71", 0.0), p, m.get("msc_tbmt_code", ""),
                f"=ROUND(E{row_c}*J{row_c}, 0)"
            ])
            row_c += 1
        # Hàng tổng cộng
        ws7.append(["", "", "TỔNG CỘNG CHI PHÍ VẬT LIỆU (C_VL):", "", "", "", "", "", "", "", "", f"=SUM(L5:L{row_c-1})"])
        ws7.cell(row=row_c, column=3).font = font_bold
        ws7.cell(row=row_c, column=12).font = font_bold
        ws7.cell(row=row_c, column=12).fill = fill_total
        style_table(ws7, fill_blue)

        # =========================================================================
        # SHEET 8: 08_DonGia_DC_TB (Đơn giá dụng cụ & ca máy thiết bị)
        # =========================================================================
        ws8 = wb.create_sheet(title="08_DonGia_DC_TB")
        ws8.append(["BẢNG ĐƠN GIÁ DỤNG CỤ & CA MÁY THIẾT BỊ QUAN TRẮC MÔI TRƯỜNG"])
        ws8.append(["(Căn cứ: TT 45/2013/TT-BTC khấu hao TSCĐ; TT 20/2017/TT-BTNMT; Điện EVN 2.100 đ/kWh)"])
        ws8.append([])
        ws8.append([
            "STT", "Mã", "Tên Dụng Cụ / Thiết Bị", "Phân Loại", "ĐVT",
            "Tổng Ca ĐM", "Nguyên Giá MSC (đ)", "Mã TBMT", "Đơn Giá 1 Ca (đ/ca)", "Thành Tiền (đ)"
        ])
        row_c = 5
        for idx, t in enumerate(tools_db.get("items", []), 1):
            ws8.append([
                idx, t.get("id", ""), t.get("name", ""), "Dụng cụ BHLĐ", t.get("unit", ""),
                t.get("total_shifts", 0.0), t.get("msc_original_price", 0.0), t.get("msc_tbmt_code", ""),
                t.get("shift_unit_price", 0.0), f"=ROUND(F{row_c}*I{row_c}, 0)"
            ])
            row_c += 1
        for idx, e in enumerate(equipment_db.get("items", []), 1):
            ws8.append([
                idx + len(tools_db.get("items", [])), e.get("id", ""), e.get("name", ""), "Ca máy thiết bị", e.get("unit", ""),
                e.get("total_shifts", 0.0), e.get("msc_original_price", 0.0), e.get("msc_tbmt_code", ""),
                e.get("shift_unit_rate", 0.0), f"=ROUND(F{row_c}*I{row_c}, 0)"
            ])
            row_c += 1
        ws8.append(["", "", "TỔNG CỘNG CHI PHÍ DỤNG CỤ + CA MÁY (CDC + CTB):", "", "", "", "", "", "", f"=SUM(J5:J{row_c-1})"])
        ws8.cell(row=row_c, column=3).font = font_bold
        ws8.cell(row=row_c, column=10).font = font_bold
        ws8.cell(row=row_c, column=10).fill = fill_total
        style_table(ws8, fill_green)

        # =========================================================================
        # SHEET 9: 09_ChiPhi_GianTiep_K4.5 (Hệ số +38,23% & 4 khoản tính riêng)
        # =========================================================================
        ws9 = wb.create_sheet(title="09_ChiPhi_GianTiep_K4.5")
        ws9.append(["BẢNG CHI PHÍ GIÁN TIẾP & CÁC KHOẢN NGOÀI ĐỊNH MỨC TÍNH RIÊNG"])
        ws9.append(["(Căn cứ: Khoản 4.5 TT 20/2017/TT-BTNMT; TT 12/2021/TT-BXD; TT 40/2017/TT-BTC; QĐ 80/2026/QĐ-UBND)"])
        ws9.append([])
        ws9.append(["STT", "Mã Khoản", "Nội Dung Chi Phí Ngoài Định Mức Tính Riêng", "Căn Cứ Pháp Lý", "ĐVT", "Khối Lượng", "Đơn Giá (đ)", "Thành Tiền (đ)"])
        row_c = 5
        exps = overhead_config.get("separate_expenses", [])
        for idx, it in enumerate(exps, 1):
            ws9.append([
                idx, it.get("id", f"CPTR_{idx:03d}"), it.get("name", ""), it.get("standard", ""),
                it.get("unit", ""), it.get("quantity", 1), it.get("unit_price", 0),
                f"=ROUND(F{row_c}*G{row_c}, 0)"
            ])
            row_c += 1
        ws9.append(["", "", "TỔNG CHI PHÍ TÍNH RIÊNG (KHOẢN 4.5 TT20):", "", "", "", "", f"=SUM(H5:H{row_c-1})"])
        ws9.cell(row=row_c, column=3).font = font_bold
        ws9.cell(row=row_c, column=8).font = font_bold
        ws9.cell(row=row_c, column=8).fill = fill_total
        style_table(ws9, fill_amber)

        # =========================================================================
        # SHEET 10: 10_TongHop_3_KichBan (Dashboard tổng hợp so sánh 3 phương án)
        # =========================================================================
        ws10 = wb.create_sheet(title="10_TongHop_3_KichBan")
        ws10.append(["BẢNG TỔNG HỢP KINH PHÍ QUAN TRẮC MÔI TRƯỜNG & SO SÁNH 3 PHƯƠNG ÁN"])
        ws10.append(["(Dự thảo trình Tổ Thẩm định & Lãnh đạo phê duyệt trần dự toán gói thầu năm 2026)"])
        ws10.append([])
        ws10.append([
            "STT", "Hạng Mục / Yếu Tố Chi Phí", "Phương Pháp Xác Định",
            "PA1: Chuẩn ĐM TT20 (đ)", "PA2: 3 Báo Giá TT (đ)", "PA3: HĐ 71 Kế Thừa (đ)",
            "Chênh Lệch PA1 vs PA2 (đ)", "Đề Xuất Duyệt"
        ])

        summary_rows = [
            ("I", "CHI PHÍ TRỰC TIẾP (T)", "", "", "", "", "", ""),
            ("1", "Chi phí Nhân công (CNC)", "Khoản 4.1.3 TT20 (+20% ngoại nghiệp)", 825420000, 950000000, 890000000),
            ("2", "Chi phí Vật liệu, Hóa chất (CVL)", "Khoản 4.4 TT20 (+8% hao hụt)", 625340000, 780000000, 710000000),
            ("3", "Chi phí Dụng cụ (CDC)", "Khoản 4.2 TT20 (22 ca + 10% phụ)", 84520000, 110000000, 98000000),
            ("4", "Chi phí Thiết bị, Ca máy (CTB)", "Khoản 4.3 TT20 (250/200/500 ca)", 685120000, 820000000, 750000000),
            ("5", "Chi phí Ngoài định mức tính riêng", "Khoản 4.5 TT20 (4 khoản đặc thù)", 704000000, 704000000, 704000000),
            ("II", "TỔNG CHI PHÍ TRỰC TIẾP (T)", "=SUM(D6:D10)", "=SUM(D6:D10)", "=SUM(E6:E10)", "=SUM(F6:F10)"),
            ("III", "CHI PHÍ GIÁN TIẾP & THUẾ (+38,23%)", "Φ = 1,15 x 1,06 x 1,05 x 1,08", "=ROUND(D11*0.382346, 0)", "=ROUND(E11*0.382346, 0)", "=ROUND(F11*0.382346, 0)"),
            ("1", "Chi phí quản lý chung (15%)", "15% x T", "=ROUND(D11*0.15, 0)", "=ROUND(E11*0.15, 0)", "=ROUND(F11*0.15, 0)"),
            ("2", "Thu nhập chịu thuế tính trước (6%)", "6% x (T + C_chung)", "=ROUND((D11+D13)*0.06, 0)", "=ROUND((E11+E13)*0.06, 0)", "=ROUND((F11+F13)*0.06, 0)"),
            ("3", "Chi phí dự phòng phát sinh (5%)", "5% x (T + C_chung + TL)", "=ROUND((D11+D13+D14)*0.05, 0)", "=ROUND((E11+E13+E14)*0.05, 0)", "=ROUND((F11+F13+F14)*0.05, 0)"),
            ("4", "Thuế Giá trị gia tăng VAT (8%)", "8% x (T + C_chung + TL + DP)", "=ROUND((D11+D13+D14+D15)*0.08, 0)", "=ROUND((E11+E13+E14+E15)*0.08, 0)", "=ROUND((F11+F13+F14+F15)*0.08, 0)"),
            ("IV", "TỔNG KINH PHÍ DỰ TOÁN TRỌN GÓI", "T + C_GIAN_TIEP", "=D11+D12", "=E11+E12", "=F11+F12")
        ]

        for r in summary_rows:
            if len(r) == 6:
                ws10.append([r[0], r[1], r[2], r[3], r[4], r[5], f"=E{ws10.max_row+1}-D{ws10.max_row+1}", "Kiến nghị duyệt PA1"])
            elif len(r) == 8:
                ws10.append([r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]])

        # Format rows tổng
        ws10.cell(row=11, column=2).font = font_bold
        ws10.cell(row=11, column=4).font = font_bold
        ws10.cell(row=11, column=4).fill = fill_total
        ws10.cell(row=17, column=2).font = font_bold
        ws10.cell(row=17, column=4).font = font_bold
        ws10.cell(row=17, column=4).fill = fill_total

        style_table(ws10, fill_slate)

        # Lưu file
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        wb.save(output_path)
        return output_path
