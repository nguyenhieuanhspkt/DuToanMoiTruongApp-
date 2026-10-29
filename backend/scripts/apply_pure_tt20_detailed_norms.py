import os
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

exporter_file = r'D:\TaskApp_kiet\DuToanMoiTruongApp\backend\exporters\excel_f1_full_replica_exporter.py'

with open(exporter_file, 'r', encoding='utf-8') as f:
    text = f.read()

# Let's inspect where sheet 5 ('Hao phí VT') starts and ends
start_hp = text.find("# SHEET 5: 'Hao phí VT'")
end_hp = text.find("# SHEET 6: 'Vật liệu'")

if start_hp == -1 or end_hp == -1:
    print(f"Error finding markers: start_hp={start_hp}, end_hp={end_hp}")
    sys.exit(1)

# Draft new Hao phí VT generator that reads real tt20_data from pakt_items
new_hp_code = '''        # =============================================================
        # SHEET 5: 'Hao phí VT' (Bung 100% ĐỊNH MỨC CHI TIẾT THÔNG TƯ 20/2017)
        # =============================================================
        ws_hp = wb.create_sheet(title="Hao phí VT")
        ws_hp.views.sheetView[0].showGridLines = True
        ws_hp.append(["HAO PHÍ VẬT LIỆU, NHÂN CÔNG, MÁY VÀ CÔNG CỤ DỤNG CỤ CHI TIẾT THEO ĐỊNH MỨC THÔNG TƯ 20/2017/TT-BTNMT"])
        ws_hp.append(["='Công trình'!A3"])
        ws_hp.append(["='Công trình'!A4"])
        ws_hp.append([])
        ws_hp.append([
            "STT", "Mã hiệu TT20", "Phân loại", "Tên công tác / Thành phần hao phí chi tiết", "Đơn vị", "Khối lượng công trình (Q)",
            "Định mức VL", "Định mức NC", "Định mức CCDC", "Định mức Máy",
            "Khối lượng VL", "Khối lượng NC", "Khối lượng CCDC", "Khối lượng Máy", "Căn cứ pháp lý định mức TT20"
        ])

        hp_row = 6
        # Duyệt qua các công việc thực tế để bung chi tiết 100% định mức
        for i, it in enumerate(pakt_items, 1):
            ct_r = start_ct_row + i - 1
            tt = it.get('tt20_data') or {}
            core_code = tt.get('coreCode') or it.get('ma_gop') or 'TT20'
            work_name = it.get('thong_so') or 'Công tác quan trắc'
            work_unit = it.get('dvt') or 'mẫu'

            # Dòng Cha (Mã công tác)
            ws_hp.append([
                i, core_code, "CÔNG TÁC", work_name, work_unit,
                f"='Công trình'!L{ct_r}", "", "", "", "", "", "", "", "", "Thông tư 20/2017/TT-BTNMT"
            ])
            master_r = hp_row
            ws_hp.cell(master_r, 4).font = font_data_11b
            for c in range(1, 16):
                ws_hp.cell(master_r, c).fill = fill_header_gray
                ws_hp.cell(master_r, c).border = border_cell
            hp_row += 1

            # Bung từng giai đoạn (Ngoại nghiệp, Nội nghiệp, Toàn phần)
            for stage_key, stage_lbl in [('field', 'Ngoại nghiệp'), ('lab', 'Nội nghiệp'), ('single', 'Toàn phần')]:
                sub = tt.get(stage_key)
                if not sub:
                    continue

                # 1. NHÂN CÔNG CHI TIẾT
                nc_norm = sub.get('dinh_muc_cong')
                nc_title = sub.get('dinh_bien') or f'Quan trắc viên ({stage_lbl})'
                if nc_norm is not None and float(nc_norm) > 0:
                    ws_hp.append([
                        "", f"NC_{core_code}_{stage_key}", "NHÂN CÔNG", f" - {nc_title} ({stage_lbl})", "công", "",
                        "", float(nc_norm), "", "", "", f"=ROUND(F{master_r}*H{hp_row}, 4)", "", "", "Bảng 1 TT20 & TTLT 56/2015"
                    ])
                    hp_row += 1

                # 2. VẬT LIỆU & HÓA CHẤT CHI TIẾT
                for m in sub.get('materials', []):
                    m_name = m.get('name', '').strip()
                    m_unit = m.get('unit', '').strip()
                    m_norm = float(m.get('norm') or 0.0)
                    if m_norm > 0:
                        ws_hp.append([
                            "", f"VL_{core_code}", "VẬT LIỆU", f" - {m_name} ({stage_lbl})", m_unit, "",
                            m_norm, "", "", "", f"=ROUND(F{master_r}*G{hp_row}, 4)", "", "", "", "Bảng 5 TT20/2017"
                        ])
                        hp_row += 1

                # 3. CÔNG CỤ DỤNG CỤ CHI TIẾT
                for t in sub.get('tools', []):
                    t_name = t.get('name', '').strip()
                    t_unit = t.get('unit', '').strip()
                    t_norm = float(t.get('norm') or 0.0)
                    if t_norm > 0:
                        ws_hp.append([
                            "", f"DC_{core_code}", "DỤNG CỤ", f" - {t_name} ({stage_lbl})", t_unit, "",
                            "", "", t_norm, "", "", "", f"=ROUND(F{master_r}*I{hp_row}, 4)", "", "Bảng 3 TT20/2017"
                        ])
                        hp_row += 1

                # 4. THIẾT BỊ & CA MÁY CHI TIẾT
                for e in sub.get('equipment', []):
                    e_name = e.get('name', '').strip()
                    e_unit = e.get('unit', '').strip()
                    e_norm = float(e.get('norm') or 0.0)
                    if e_norm > 0:
                        ws_hp.append([
                            "", f"M_{core_code}", "THIẾT BỊ", f" - {e_name} ({stage_lbl})", e_unit, "",
                            "", "", "", e_norm, "", "", "", f"=ROUND(F{master_r}*J{hp_row}, 4)", "Bảng 4 TT20 & TT 45/2013"
                        ])
                        hp_row += 1

            # Dòng cách giữa các công tác
            ws_hp.append([])
            hp_row += 1

        last_hp_row = hp_row - 1

        # Format Sheet Hao phí VT
        ws_hp.cell(1, 1).font = font_title_15b
        ws_hp.cell(2, 1).font = font_sub_11i
        ws_hp.cell(3, 1).font = font_sub_11i
        for c in range(1, 16):
            ws_hp.cell(5, c).font = font_header_11b
            ws_hp.cell(5, c).fill = fill_header_gray
            ws_hp.cell(5, c).alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        for r in range(6, last_hp_row + 1):
            for c in range(1, 16):
                cell = ws_hp.cell(r, c)
                if cell.value:
                    if cell.fill != fill_header_gray:
                        cell.font = font_data_11r
                    cell.border = border_cell
                    if c in (7, 8, 9, 10, 11, 12, 13, 14):
                        cell.number_format = FMT_NORM
                    if c in (1, 2, 3, 5):
                        cell.alignment = Alignment(horizontal="center", vertical="center")

        ws_hp.column_dimensions['A'].width = 8
        ws_hp.column_dimensions['B'].width = 16
        ws_hp.column_dimensions['C'].width = 14
        ws_hp.column_dimensions['D'].width = 50
        ws_hp.column_dimensions['E'].width = 10
        ws_hp.column_dimensions['F'].width = 16
        ws_hp.column_dimensions['G'].width = 14
        ws_hp.column_dimensions['H'].width = 14
        ws_hp.column_dimensions['I'].width = 14
        ws_hp.column_dimensions['J'].width = 14
        ws_hp.column_dimensions['K'].width = 16
        ws_hp.column_dimensions['L'].width = 16
        ws_hp.column_dimensions['M'].width = 16
        ws_hp.column_dimensions['N'].width = 16
        ws_hp.column_dimensions['O'].width = 28
'''

new_text = text[:start_hp] + new_hp_code + "\n        " + text[end_hp:]

with open(exporter_file, 'w', encoding='utf-8') as f:
    f.write(new_text)

print("Updated excel_f1_full_replica_exporter.py with 100% pure detailed TT20 norms in sheet 'Hao phí VT'!")
