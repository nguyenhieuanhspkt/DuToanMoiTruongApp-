import os
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

exporter_file = r'D:\TaskApp_kiet\DuToanMoiTruongApp\backend\exporters\excel_f1_full_replica_exporter.py'

# Let's inspect the exact lines between Sheet 6 and Sheet 10
with open(exporter_file, 'r', encoding='utf-8') as f:
    text = f.read()

# Replacement block for Sheet 6, 7, 8, 9, 10
replacement_code = '''        # =============================================================
        # SHEET 6: 'Vật liệu' (Đầy đủ 173 danh mục hóa chất & vật tư theo TT20)
        # =============================================================
        ws_vl = wb.create_sheet(title="Vật liệu")
        ws_vl.views.sheetView[0].showGridLines = True
        ws_vl.append(["BẢNG TỔNG HỢP VẬT LIỆU VÀ CHÊNH LỆCH GIÁ"])
        ws_vl.append(["(Căn cứ theo Thông tư 20/2017/TT-BTNMT - Bảng 5 & Mục 4.4; KQLCNT IB2600096765 chia 1.08)"])
        ws_vl.append(["='Công trình'!A3"])
        ws_vl.append(["='Công trình'!A4"])
        ws_vl.append([])
        ws_vl.append([
            "STT", "Mã hiệu", "Tên vật tư, hóa chất, dung môi", "Đơn vị",
            "Khối lượng tổng cộng", "Đơn giá chưa VAT (KQLCNT IB2600096765)", "Thành tiền vật liệu (VNĐ)", "Ghi chú nguồn giá"
        ])

        # Load 173 materials
        mat_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "material_pricing.json")
        mat_items = []
        if os.path.exists(mat_path):
            with open(mat_path, "r", encoding="utf-8") as f:
                mat_items = json.load(f).get("items", [])

        vl_start_row = 7
        curr_row = vl_start_row
        for idx, it in enumerate(mat_items, 1):
            qty = float(it.get('total_quantity_raw') or 0.0)
            price = float(it.get('approved_price') or 0.0)
            basis = str(it.get('approval_basis') or '')
            ws_vl.append([
                idx, it.get('id', f'VL_{idx:03d}'), it.get('name', ''), it.get('unit', ''),
                qty, price, f"=ROUND(E{curr_row}*F{curr_row}, 0)", basis
            ])
            curr_row += 1

        last_mat_item_row = curr_row - 1
        # Vật liệu phụ khác 8%
        ws_vl.append([
            len(mat_items) + 1, "VL_KHAC", "Vật liệu phụ khác (8% vật liệu chính theo Khoản 4.4 TT20)", "%",
            "8.0%", "", f"=ROUND(SUM(G{vl_start_row}:G{last_mat_item_row})*'Hệ số'!$C$11, 0)", "Hệ số 8% theo Khoản 4.4 TT20"
        ])
        vl_khac_row = curr_row
        curr_row += 1

        # Dòng CỘNG TỔNG CHI PHÍ VẬT LIỆU
        ws_vl.append(["", "", "CỘNG CHI PHÍ VẬT LIỆU:", "", "", "", f"=SUM(G{vl_start_row}:G{vl_khac_row})", "Tổng chi phí vật liệu (VL)"])
        total_vl_row = curr_row

        # Format Sheet Vật liệu
        ws_vl.cell(1, 1).font = font_title_15b
        ws_vl.cell(2, 1).font = font_sub_11i
        for c in range(1, 9):
            ws_vl.cell(6, c).font = font_header_11b
            ws_vl.cell(6, c).fill = fill_header_gray
            ws_vl.cell(6, c).alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        for r in range(vl_start_row, total_vl_row + 1):
            is_total = (r == total_vl_row)
            for c in range(1, 9):
                cell = ws_vl.cell(r, c)
                cell.font = font_data_11b if is_total else font_data_11r
                cell.border = border_total if is_total else border_cell
                if is_total:
                    cell.fill = fill_header_gray
                if c in (6, 7):
                    cell.number_format = FMT_CURRENCY
                if c == 5 and r <= last_mat_item_row:
                    cell.number_format = FMT_NORM

        ws_vl.column_dimensions['B'].width = 14
        ws_vl.column_dimensions['C'].width = 55
        ws_vl.column_dimensions['E'].width = 24
        ws_vl.column_dimensions['F'].width = 24
        ws_vl.column_dimensions['G'].width = 26
        ws_vl.column_dimensions['H'].width = 40

        # =============================================================
        # SHEET 7: 'Nhân công' (Tổng hợp ngày công qua SUMIF)
        # =============================================================
        ws_nc = wb.create_sheet(title="Nhân công")
        ws_nc.views.sheetView[0].showGridLines = True
        ws_nc.append(["BẢNG TỔNG HỢP NHÂN CÔNG VÀ CHÊNH LỆCH GIÁ"])
        ws_nc.append(["(Căn cứ theo TT 20/2017/TT-BTNMT và QĐ 80/2026/QĐ-UBND 22 ngày/tháng)"])
        ws_nc.append(["='Công trình'!A3"])
        ws_nc.append(["='Công trình'!A4"])
        ws_nc.append([])
        ws_nc.append([
            "STT", "Mã hiệu", "Tên nhóm chức danh lao động", "Đơn vị",
            "Tổng số ngày công (SUMIF)", "Đơn giá ngày công (/22 ngày)", "Thành tiền nhân công (VNĐ)", "Căn cứ pháp lý lương"
        ])

        ws_nc.append([
            1, "NC_LDKT", "Lao động kỹ thuật (Kỹ sư/QTVTNMT - Bậc 4-5/7)", "công",
            f"=ROUND(SUMIF('Hao phí VT'!$B$6:$B${last_hp_row}, B7, 'Hao phí VT'!$L$6:$L${last_hp_row}), 4)",
            "='Lương nhân công'!$E$8", "=ROUND(E7*F7, 0)", "TTLT 56/2015 & QĐ 80/2026 chia 22 ngày"
        ])
        ws_nc.append([
            2, "NC_LDPT", "Lao động phổ thông (Phụ việc hiện trường / vận chuyển)", "công",
            f"=ROUND(SUMIF('Hao phí VT'!$B$6:$B${last_hp_row}, B8, 'Hao phí VT'!$L$6:$L${last_hp_row}), 4)",
            "='Lương nhân công'!$E$9", "=ROUND(E8*F8, 0)", "TTLT 56/2015 & QĐ 80/2026 chia 22 ngày"
        ])
        ws_nc.append(["", "", "CỘNG CHI PHÍ NHÂN CÔNG:", "", "=ROUND(E7+E8, 4)", "", "=G7+G8", "Tổng chi phí nhân công (NC)"])

        # Format Sheet Nhân công
        ws_nc.cell(1, 1).font = font_title_15b
        ws_nc.cell(2, 1).font = font_sub_11i
        for c in range(1, 9):
            ws_nc.cell(6, c).font = font_header_11b
            ws_nc.cell(6, c).fill = fill_header_gray
            ws_nc.cell(6, c).alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        for r in (7, 8, 9):
            for c in range(1, 9):
                cell = ws_nc.cell(r, c)
                cell.font = font_data_11r if r < 9 else font_data_11b
                cell.border = border_cell if r < 9 else border_total
                if r == 9:
                    cell.fill = fill_header_gray
                if c in (6, 7):
                    cell.number_format = FMT_CURRENCY
                if c == 5:
                    cell.number_format = FMT_NORM

        ws_nc.column_dimensions['B'].width = 14
        ws_nc.column_dimensions['C'].width = 50
        ws_nc.column_dimensions['E'].width = 24
        ws_nc.column_dimensions['F'].width = 24
        ws_nc.column_dimensions['G'].width = 26

        # =============================================================
        # SHEET 8: 'Công cụ dụng cụ' (Đầy đủ 158 danh mục CCDC theo TT20)
        # =============================================================
        ws_dc = wb.create_sheet(title="Công cụ dụng cụ")
        ws_dc.views.sheetView[0].showGridLines = True
        ws_dc.append(["BẢNG TỔNG HỢP VÀ CHÊNH LỆCH CÔNG CỤ DỤNG CỤ"])
        ws_dc.append(["(Căn cứ theo Thông tư 20/2017/TT-BTNMT - Bảng 3 & Mục 4.2: 22 ca/tháng + 10% CCDC phụ)"])
        ws_dc.append(["='Công trình'!A3"])
        ws_dc.append(["='Công trình'!A4"])
        ws_dc.append([])
        ws_dc.append([
            "STT", "Mã hiệu", "Tên công cụ dụng cụ", "Đơn vị",
            "Tổng số ca sử dụng", "Đơn giá 1 ca CCDC (22 ca/tháng)", "Thành tiền CCDC (VNĐ)", "Ghi chú định mức"
        ])

        # Load 158 tools
        tools_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "msc_lookup_tools.json")
        tools_items = []
        if os.path.exists(tools_path):
            with open(tools_path, "r", encoding="utf-8") as f:
                tools_items = json.load(f).get("items", [])

        dc_start_row = 7
        curr_row = dc_start_row
        for idx, it in enumerate(tools_items, 1):
            shifts = float(it.get('total_shifts') or 0.0)
            rate = float(it.get('shift_unit_price') or 0.0)
            note = str(it.get('note') or '')
            ws_dc.append([
                idx, it.get('id', f'DC_{idx:03d}'), it.get('name', ''), it.get('unit', ''),
                shifts, rate, f"=ROUND(E{curr_row}*F{curr_row}, 0)", note
            ])
            curr_row += 1

        last_dc_item_row = curr_row - 1
        # CCDC phụ 10%
        ws_dc.append([
            len(tools_items) + 1, "CCDC_PHU", "Dụng cụ phụ khác (10% CCDC chính)", "%",
            "10.0%", "", f"=ROUND(SUM(G{dc_start_row}:G{last_dc_item_row})*'Hệ số'!$C$12, 0)", "10% theo Khoản 4.2 Thông tư 20"
        ])
        dc_phu_row = curr_row
        curr_row += 1

        # CỘNG TỔNG CHI PHÍ CÔNG CỤ DỤNG CỤ
        ws_dc.append(["", "", "CỘNG CHI PHÍ CÔNG CỤ DỤNG CỤ:", "", "", "", f"=SUM(G{dc_start_row}:G{dc_phu_row})", "Tổng chi phí CCDC (DC)"])
        total_dc_row = curr_row

        # Format Sheet CCDC
        ws_dc.cell(1, 1).font = font_title_15b
        ws_dc.cell(2, 1).font = font_sub_11i
        for c in range(1, 9):
            ws_dc.cell(6, c).font = font_header_11b
            ws_dc.cell(6, c).fill = fill_header_gray
            ws_dc.cell(6, c).alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        for r in range(dc_start_row, total_dc_row + 1):
            is_total = (r == total_dc_row)
            for c in range(1, 9):
                cell = ws_dc.cell(r, c)
                cell.font = font_data_11b if is_total else font_data_11r
                cell.border = border_total if is_total else border_cell
                if is_total:
                    cell.fill = fill_header_gray
                if c in (6, 7):
                    cell.number_format = FMT_CURRENCY
                if c == 5 and r <= last_dc_item_row:
                    cell.number_format = FMT_NORM

        ws_dc.column_dimensions['B'].width = 14
        ws_dc.column_dimensions['C'].width = 50
        ws_dc.column_dimensions['E'].width = 24
        ws_dc.column_dimensions['F'].width = 24
        ws_dc.column_dimensions['G'].width = 26
        ws_dc.column_dimensions['H'].width = 35

        # =============================================================
        # SHEET 9: 'Máy thi công' (Đầy đủ 71 thiết bị quan trắc & Năng lượng)
        # =============================================================
        ws_m = wb.create_sheet(title="Máy thi công")
        ws_m.views.sheetView[0].showGridLines = True
        ws_m.append(["BẢNG TỔNG HỢP MÁY THI CÔNG VÀ CHÊNH LỆCH GIÁ"])
        ws_m.append(["(Căn cứ theo Thông tư số 45/2013/TT-BTC & Thông tư 20/2017/TT-BTNMT)"])
        ws_m.append(["='Công trình'!A3"])
        ws_m.append(["='Công trình'!A4"])
        ws_m.append([])
        ws_m.append([
            "STT", "Mã hiệu", "Tên thiết bị đo chuyên dụng / Năng lượng", "Đơn vị",
            "Khối lượng tổng (ca / kWh)", "Đơn giá 1 ca máy / 1 kWh", "Thành tiền máy (VNĐ)", "Cơ sở xác định đơn giá"
        ])

        # Load 71 equipment
        equip_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "msc_lookup_equipment.json")
        equip_items = []
        if os.path.exists(equip_path):
            with open(equip_path, "r", encoding="utf-8") as f:
                equip_items = json.load(f).get("items", [])

        m_start_row = 7
        curr_row = m_start_row
        for idx, it in enumerate(equip_items, 1):
            shifts = float(it.get('total_shifts') or 0.0)
            rate = float(it.get('shift_unit_rate') or 0.0)
            note = str(it.get('note') or '')
            ws_m.append([
                idx, it.get('id', f'TB_{idx:03d}'), it.get('name', ''), it.get('unit', ''),
                shifts, rate, f"=ROUND(E{curr_row}*F{curr_row}, 0)", note
            ])
            curr_row += 1

        last_m_item_row = curr_row - 1
        # Thiết bị phụ khác 5%
        ws_m.append([
            len(equip_items) + 1, "M_KHAC", "Chi phí thiết bị phụ khác (5% máy chính)", "%",
            "5.0%", "", f"=ROUND(SUM(G{m_start_row}:G{last_m_item_row})*'Hệ số'!$C$13, 0)", "5% chi phí thiết bị phụ"
        ])
        m_phu_row = curr_row
        curr_row += 1

        # CỘNG TỔNG CHI PHÍ MÁY THI CÔNG
        ws_m.append(["", "", "CỘNG CHI PHÍ MÁY THI CÔNG:", "", "", "", f"=SUM(G{m_start_row}:G{m_phu_row})", "Tổng chi phí máy (M)"])
        total_m_row = curr_row

        # Format Sheet Máy thi công
        ws_m.cell(1, 1).font = font_title_15b
        ws_m.cell(2, 1).font = font_sub_11i
        for c in range(1, 9):
            ws_m.cell(6, c).font = font_header_11b
            ws_m.cell(6, c).fill = fill_header_gray
            ws_m.cell(6, c).alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        for r in range(m_start_row, total_m_row + 1):
            is_total = (r == total_m_row)
            for c in range(1, 9):
                cell = ws_m.cell(r, c)
                cell.font = font_data_11b if is_total else font_data_11r
                cell.border = border_total if is_total else border_cell
                if is_total:
                    cell.fill = fill_header_gray
                if c in (6, 7):
                    cell.number_format = FMT_CURRENCY
                if c == 5 and r <= last_m_item_row:
                    cell.number_format = FMT_NORM

        ws_m.column_dimensions['B'].width = 14
        ws_m.column_dimensions['C'].width = 50
        ws_m.column_dimensions['E'].width = 24
        ws_m.column_dimensions['F'].width = 24
        ws_m.column_dimensions['G'].width = 26
        ws_m.column_dimensions['H'].width = 35

        # =============================================================
        # SHEET 10: 'THDT hạng mục' (Tổng hợp dự toán chi phí vĩ mô)
        # =============================================================
        ws_thdt = wb.create_sheet(title="THDT hạng mục")
        ws_thdt.views.sheetView[0].showGridLines = True
        ws_thdt.append(["BẢNG TỔNG HỢP DỰ TOÁN CHI PHÍ QUAN TRẮC MÔI TRƯỜNG"])
        ws_thdt.append(["='Công trình'!A3"])
        ws_thdt.append(["='Công trình'!A4"])
        ws_thdt.append(["Đơn vị tính: đồng", "", "", "", ""])
        ws_thdt.append([])
        ws_thdt.append(["STT", "NỘI DUNG CHI PHÍ", "CÁCH TÍNH / DIỄN GIẢI", "GIÁ TRỊ (VNĐ)", "KÝ HIỆU"])

        ws_thdt.append(["I", "Chi phí trực tiếp (T = VL + DC + NC + M)", "=\\"VL + DC + NC + M\\"", "=ROUND(D8+D10+D12+D14, 0)", "T"])
        ws_thdt.append(["1", "Chi phí vật liệu", "=\\"VLHT\\"", "=ROUND(D8, 0)", "VL"])
        ws_thdt.append(["", " - Đơn giá vật liệu", "Theo bảng tổng hợp vật liệu", f"='Vật liệu'!$G${total_vl_row}", "VLHT"])
        ws_thdt.append(["2", "Chi phí công cụ dụng cụ", "=\\"DCHT\\"", "=ROUND(D10, 0)", "DC"])
        ws_thdt.append(["", " - Đơn giá công cụ dụng cụ", "Theo bảng tổng hợp dụng cụ", f"='Công cụ dụng cụ'!$G${total_dc_row}", "DCHT"])
        ws_thdt.append(["3", "Chi phí nhân công", "=\\"NCHT\\"", "=ROUND(D12, 0)", "NC"])
        ws_thdt.append(["", " - Đơn giá nhân công", "Theo bảng tổng hợp nhân công", "='Nhân công'!$G$9", "NCHT"])
        ws_thdt.append(["4", "Chi phí máy và thiết bị thi công", "=\\"MHT\\"", "=ROUND(D14, 0)", "M"])
        ws_thdt.append(["", " - Đơn giá máy thi công", "Theo bảng tổng hợp máy thi công", f"='Máy thi công'!$G${total_m_row}", "MHT"])
        ws_thdt.append(["II", "Chi phí gián tiếp", "=\\"C + TT\\"", "=D16+D17", "GT"])
        ws_thdt.append(["1", "Chi phí chung", "=\\"T x 7,3%\\"", "=ROUND(D6*'Hệ số'!$C$4, 0)", "C"])
        ws_thdt.append(["2", "Chi phí một số công việc không xác định từ thiết kế", "=\\"T x 2,5%\\"", "=ROUND(D6*'Hệ số'!$C$9, 0)", "TT"])
        ws_thdt.append(["III", "Thu nhập chịu thuế tính trước", "=\\"(T + GT) x 5,5%\\"", "=ROUND((D6+D15)*'Hệ số'!$C$8, 0)", "TL"])
        ws_thdt.append(["", "Chi phí trước thuế", "=\\"T + GT + TL\\"", "=ROUND(D6+D15+D18, 0)", "G"])
        ws_thdt.append(["IV", "Thuế giá trị gia tăng", "=\\"G x 8%\\"", "=ROUND(D19*'Hệ số'!$C$10, 0)", "GTGT"])
        ws_thdt.append(["", "CHI PHÍ SAU THUẾ", "=\\"G + GTGT\\"", "=ROUND(D19+D20, 0)", "Gxd"])
        ws_thdt.append(["V", "Chi phí nhà tạm để ở và điều hành", "=\\"G x 1,1% x (1 + 8%)\\"", "=ROUND(D19*'Hệ số'!$C$6*(1+'Hệ số'!$C$10), 0)", "LT"])
        ws_thdt.append(["", "TỔNG CỘNG KINH PHÍ GÓI THẦU", "=\\"Gxd + LT\\"", "=ROUND(D21+D22, 0)", "TTS"])
        ws_thdt.append(["", "LÀM TRÒN (ĐẾN HÀNG NGHÌN ĐỒNG)", "=\\"ROUND(D23, -3)\\"", "=ROUND(D23, -3)", "LTR"])

        # Format Sheet THDT hạng mục
        ws_thdt.cell(1, 1).font = font_title_15b
        ws_thdt.cell(2, 1).font = font_sub_11i
        ws_thdt.cell(3, 1).font = font_sub_11i

        for c in range(1, 6):
            cell = ws_thdt.cell(5, c)
            cell.font = font_header_11b
            cell.fill = fill_header_gray
            cell.alignment = Alignment(horizontal="center", vertical="center")

        for r in range(6, 25):
            is_bold_row = r in (6, 15, 18, 19, 21, 23, 24)
            for c in range(1, 6):
                cell = ws_thdt.cell(r, c)
                cell.font = font_data_11b if is_bold_row else font_data_11r
                cell.border = border_cell if r < 24 else border_total
                if is_bold_row and r in (6, 19, 21, 23, 24):
                    cell.fill = fill_total_pale
                if c == 4:
                    cell.number_format = FMT_CURRENCY
                if c in (1, 5):
                    cell.alignment = Alignment(horizontal="center", vertical="center")

        ws_thdt.column_dimensions['A'].width = 8
        ws_thdt.column_dimensions['B'].width = 46
        ws_thdt.column_dimensions['C'].width = 32
        ws_thdt.column_dimensions['D'].width = 24
        ws_thdt.column_dimensions['E'].width = 10
'''

# Now let's find the start of Sheet 6 to the start of Sheet 11
start_marker = "# SHEET 6: 'Vật liệu'"
end_marker = "# SHEET 11: 'Đơn giá chi tiết'"

idx_start = text.find(start_marker)
idx_end = text.find(end_marker)

if idx_start != -1 and idx_end != -1:
    new_text = text[:idx_start] + replacement_code + "\n        " + text[idx_end:]
    with open(exporter_file, 'w', encoding='utf-8') as f:
        f.write(new_text)
    print("Upgraded excel_f1_full_replica_exporter.py successfully!")
else:
    print(f"Error finding markers: start={idx_start}, end={idx_end}")
