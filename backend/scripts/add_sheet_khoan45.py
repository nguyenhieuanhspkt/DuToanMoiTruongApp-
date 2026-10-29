import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

exporter_file = r'D:\TaskApp_kiet\DuToanMoiTruongApp\backend\exporters\excel_f1_full_replica_exporter.py'

with open(exporter_file, 'r', encoding='utf-8') as f:
    text = f.read()

# Check if 'Khoản 4.5 TT20' already in exporter
if "SHEET: 'Khoản 4.5 TT20'" in text:
    print("Sheet 4.5 already exists in exporter")
    sys.exit(0)

# We will insert Sheet 'Khoản 4.5 TT20' right before Sheet 10 ('THDT hạng mục')
thdt_marker = "# SHEET 10: 'THDT hạng mục'"
idx_thdt = text.find(thdt_marker)

if idx_thdt == -1:
    print("Error: THDT marker not found")
    sys.exit(1)

sheet_45_code = '''        # =============================================================
        # SHEET 10: 'Khoản 4.5 TT20' (Chi phí tính riêng Mục 2.1.2 PAKT KTAT)
        # =============================================================
        ws_45 = wb.create_sheet(title="Khoản 4.5 TT20")
        ws_45.views.sheetView[0].showGridLines = True
        ws_45.append(["2.1.2 DỰ KIẾN KHỐI LƯỢNG NỘI DUNG CÔNG VIỆC PHỤC VỤ LẤY MẪU TẠI HIỆN TRƯỜNG (KHOẢN 4.5 TT20)"])
        ws_45.append(["(Căn cứ theo Mục 2.1.2 Báo cáo PAKT gửi ngày 28/10/2026 của KTAT NMNĐ Vĩnh Tân 4 và Khoản 4.5 TT 20/2017)"])
        ws_45.append(["='Công trình'!A3"])
        ws_45.append(["='Công trình'!A4"])
        ws_45.append([])
        ws_45.append([
            "STT", "Nội dung công việc / Chức danh / Phương tiện", "Đơn vị",
            "Đợt 1", "Đợt 2", "Đợt 3", "Đợt 4", "Tổng cộng", "Đơn giá (VNĐ)", "Thành tiền (VNĐ)", "Ghi chú nghiệp vụ KTAT"
        ])

        ws_45.append(["A", "ĐỐI VỚI QUAN TRẮC MÔI TRƯỜNG ĐỊNH KỲ THEO GIẤY PHÉP MÔI TRƯỜNG", "", "", "", "", "", "", "", "", ""])
        ws_45.append(["I", "Nhân sự thực hiện hiện trường", "Người", 7, 12, 7, 14, "=SUM(D8:G8)", "", "", "QTV hạng IV không quá 30% đội ngũ"])
        ws_45.append(["II", "Số chuyến xe phương tiện di chuyển", "Chuyến", 2, 4, 2, 4, "=SUM(D9:G9)", 15000000, "=ROUND(H9*I9, 0)", "Bảo quản hỏa tốc Coliform, BOD5, CrVI (24h-48h)"])
        ws_45.append(["IV", "Số ngày đi/về của mỗi đợt", "Ngày", 4, 4, 4, 4, "=SUM(D10:G10)", "", "", "Hà Nội - Bình Thuận khứ hồi (2.800 km)"])
        ws_45.append(["VI", "Số công di chuyển (Số người × Số ngày đi/về)", "Công", 28, 48, 28, 48, "=SUM(D11:G11)", 319090, "=ROUND(H11*I11, 0)", "Tính lương theo chuẩn 22 ngày QĐ 80/2026"])
        ws_45.append(["VII", "Khối lượng lưu trú tại hiện trường", "Đêm", 0, 25, 0, 25, "=SUM(D12:G12)", 450000, "=ROUND(H12*I12, 0)", "Nhóm KKXQ 5 người x 5 ngày (TT 40/2017/TT-BTC)"])
        ws_45.append(["VIII", "Khối lượng văn phòng phẩm, in ấn kết quả", "đồng", 500000, 500000, 500000, 500000, "=SUM(D13:G13)", 1, "=ROUND(H13*I13, 0)", "Trọn gói in ấn kết quả phân tích từng đợt"])

        ws_45.append(["B", "CHƯƠNG TRÌNH QUAN TRẮC MÔI TRƯỜNG ĐỐI CHỨNG", "", "", "", "", "", "", "", "", ""])
        ws_45.append(["I", "Nhân sự thực hiện hiện trường", "Người", 15, 14, 15, 14, "=SUM(D15:G15)", "", "", "QTV hạng IV không quá 30% đội ngũ"])
        ws_45.append(["II", "Số chuyến xe phương tiện di chuyển", "Chuyến", 4, 4, 4, 4, "=SUM(D16:G16)", 15000000, "=ROUND(H16*I16, 0)", "Vận chuyển mẫu nước thải, khí thải, nước biển"])
        ws_45.append(["IV", "Số ngày đi/về của mỗi đợt", "Ngày", 4, 4, 4, 4, "=SUM(D17:G17)", "", "", "Hà Nội - Bình Thuận khứ hồi (2.800 km)"])
        ws_45.append(["VI", "Số công di chuyển (Số người × Số ngày đi/về)", "Công", 60, 48, 60, 48, "=SUM(D18:G18)", 319090, "=ROUND(H18*I18, 0)", "Đợt 1: 15 người x 4 ngày; Đợt 2: 12 người x 4 ngày..."])
        ws_45.append(["VII", "Khối lượng lưu trú tại hiện trường", "Đêm", 6, 25, 6, 25, "=SUM(D19:G19)", 450000, "=ROUND(H19*I19, 0)", "Lưu trú Tuy Phong theo Thông tư 40/2017/TT-BTC"])
        ws_45.append(["VIII", "Khối lượng văn phòng phẩm, in ấn kết quả", "đồng", 500000, 500000, 500000, 500000, "=SUM(D20:G20)", 1, "=ROUND(H20*I20, 0)", "Trọn gói in ấn kết quả phân tích đối chứng"])

        ws_45.append(["C", "CHI PHÍ KỸ THUẬT NGOÀI ĐỊNH MỨC KHÁC THEO KHOẢN 4.5 TT20", "", "", "", "", "", "", "", "", ""])
        ws_45.append(["1", "Sàn thao tác, giàn giáo, lỗ lấy mẫu khí thải ống khói lò hơi", "trọn gói", 1, 0, 0, 0, 1, 280000000, 280000000, "Định mức Xây dựng TT 12/2021/TT-BXD"])
        ws_45.append(["2", "Thuê tàu biển chuyên dụng khảo sát nước biển xa bờ bãi xỉ", "ngày tàu", 3, 3, 3, 3, 12, 12000000, "=ROUND(H23*I23, 0)", "Tối thiểu 3 báo giá cạnh tranh NĐ 24/2024"])

        ws_45.append(["", "CỘNG CHI PHÍ TÍNH RIÊNG NGOÀI ĐỊNH MỨC (KHOẢN 4.5 TT20):", "", "", "", "", "", "", "", "=J9+J11+J12+J13+J16+J18+J19+J20+J22+J23", "Tổng chi phí tính riêng đưa vào THDT"])

        # Format Sheet Khoản 4.5 TT20
        ws_45.cell(1, 1).font = font_title_15b
        ws_45.cell(2, 1).font = font_sub_11i
        ws_45.cell(3, 1).font = font_sub_11i
        ws_45.cell(4, 1).font = font_sub_11i
        for c in range(1, 12):
            ws_45.cell(6, c).font = font_header_11b
            ws_45.cell(6, c).fill = fill_header_gray
            ws_45.cell(6, c).alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        for r in range(7, 25):
            is_bold = (r in (7, 14, 21, 24))
            for c in range(1, 12):
                cell = ws_45.cell(r, c)
                cell.font = font_data_11b if is_bold else font_data_11r
                cell.border = border_total if r == 24 else border_cell
                if is_bold:
                    cell.fill = fill_header_gray if r == 24 else fill_total_pale
                if c in (9, 10):
                    cell.number_format = FMT_CURRENCY
                if c in (4, 5, 6, 7, 8):
                    cell.alignment = Alignment(horizontal="center", vertical="center")

        ws_45.column_dimensions['A'].width = 8
        ws_45.column_dimensions['B'].width = 46
        ws_45.column_dimensions['C'].width = 12
        ws_45.column_dimensions['D'].width = 10
        ws_45.column_dimensions['E'].width = 10
        ws_45.column_dimensions['F'].width = 10
        ws_45.column_dimensions['G'].width = 10
        ws_45.column_dimensions['H'].width = 12
        ws_45.column_dimensions['I'].width = 20
        ws_45.column_dimensions['J'].width = 22
        ws_45.column_dimensions['K'].width = 38

'''

new_text = text[:idx_thdt] + sheet_45_code + "\n        " + text[idx_thdt:]

# In THDT, we also add the row for Khoản 4.5 TT20
# Let's inspect where Chi phí trực tiếp T is calculated
old_thdt_direct = '''ws_thdt.append(["I", "Chi phí trực tiếp (T = VL + DC + NC + M)", "=\\"VL + DC + NC + M\\"", "=ROUND(D8+D10+D12+D14, 0)", "T"])
        ws_thdt.append(["1", "Chi phí vật liệu", "=\\"VLHT\\"", "=ROUND(D8, 0)", "VL"])
        ws_thdt.append(["", " - Đơn giá vật liệu", "Theo bảng tổng hợp vật liệu", f"=\'Vật liệu\'!$G${total_vl_row}", "VLHT"])
        ws_thdt.append(["2", "Chi phí công cụ dụng cụ", "=\\"DCHT\\"", "=ROUND(D10, 0)", "DC"])
        ws_thdt.append(["", " - Đơn giá công cụ dụng cụ", "Theo bảng tổng hợp dụng cụ", f"=\'Công cụ dụng cụ\'!$G${total_dc_row}", "DCHT"])
        ws_thdt.append(["3", "Chi phí nhân công", "=\\"NCHT\\"", "=ROUND(D12, 0)", "NC"])
        ws_thdt.append(["", " - Đơn giá nhân công", "Theo bảng tổng hợp nhân công", "=\'Nhân công\'!$G$9", "NCHT"])
        ws_thdt.append(["4", "Chi phí máy và thiết bị thi công", "=\\"MHT\\"", "=ROUND(D14, 0)", "M"])
        ws_thdt.append(["", " - Đơn giá máy thi công", "Theo bảng tổng hợp máy thi công", f"=\'Máy thi công\'!$G${total_m_row}", "MHT"])'''

new_thdt_direct = '''ws_thdt.append(["I", "Chi phí trực tiếp (T = VL + DC + NC + M + C_TR)", "=\\"VL + DC + NC + M + C_TR\\"", "=ROUND(D8+D10+D12+D14+D16, 0)", "T"])
        ws_thdt.append(["1", "Chi phí vật liệu", "=\\"VLHT\\"", "=ROUND(D8, 0)", "VL"])
        ws_thdt.append(["", " - Đơn giá vật liệu", "Theo bảng tổng hợp vật liệu", f"=\'Vật liệu\'!$G${total_vl_row}", "VLHT"])
        ws_thdt.append(["2", "Chi phí công cụ dụng cụ", "=\\"DCHT\\"", "=ROUND(D10, 0)", "DC"])
        ws_thdt.append(["", " - Đơn giá công cụ dụng cụ", "Theo bảng tổng hợp dụng cụ", f"=\'Công cụ dụng cụ\'!$G${total_dc_row}", "DCHT"])
        ws_thdt.append(["3", "Chi phí nhân công", "=\\"NCHT\\"", "=ROUND(D12, 0)", "NC"])
        ws_thdt.append(["", " - Đơn giá nhân công", "Theo bảng tổng hợp nhân công", "=\'Nhân công\'!$G$9", "NCHT"])
        ws_thdt.append(["4", "Chi phí máy và thiết bị thi công", "=\\"MHT\\"", "=ROUND(D14, 0)", "M"])
        ws_thdt.append(["", " - Đơn giá máy thi công", "Theo bảng tổng hợp máy thi công", f"=\'Máy thi công\'!$G${total_m_row}", "MHT"])
        ws_thdt.append(["5", "Chi phí tính riêng ngoài định mức (Khoản 4.5 TT20)", "=\\"C_TR\\"", "=\'Khoản 4.5 TT20\'!$J$24", "C_TR"])'''

if old_thdt_direct in new_text:
    new_text = new_text.replace(old_thdt_direct, new_thdt_direct)
    print("Updated THDT direct cost formula to include Khoản 4.5 TT20!")
else:
    print("Notice: old_thdt_direct not exact match, check text.")

with open(exporter_file, 'w', encoding='utf-8') as f:
    f.write(new_text)

print("Added Sheet 'Khoản 4.5 TT20' to exporter successfully!")
