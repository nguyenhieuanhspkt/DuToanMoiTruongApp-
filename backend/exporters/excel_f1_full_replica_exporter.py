import json
import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from typing import Dict, Any, List

class ExcelF1FullReplicaExporter:
    """
    Engine xuất file Excel Dự toán Chi phí Quan trắc Môi trường
    áp dụng 100% chuẩn mực Format, Typography (Times New Roman),
    Danh pháp Sheet và Chuỗi liên kết ô (Cell Linking) kế thừa từ tệp F1:
    'Cong trinh moi.xlsm' (Gói thầu Quan trắc môi trường NMNĐ Vĩnh Tân 4).

    Danh sách Sheet:
    1. 'Công trình'        : Tiên lượng khối lượng (253 dòng PAKT, vị trí, phép nhân Q)
    2. 'Hao phí VT'        : Bung định mức TT20 (Master-Detail, 4 nhóm tài nguyên)
    3. 'Hệ số'             : Bảng tham số vĩ mô (hsC, hsTL, hsGTGT, hsTT...) - Ô vàng kem FFFFFFB4
    4. 'Lương nhân công'   : Lương ngày công viên chức 22 ngày (QĐ 80/2026 & TTLT 56)
    5. 'Tính giá ca máy'   : Tính giá ca máy & điện năng TT 45/2013
    6. 'Vật liệu'          : Tổng hợp vật liệu qua SUMIF ('Hao phí VT') + 8% phụ
    7. 'Nhân công'         : Tổng hợp ngày công qua SUMIF ('Hao phí VT')
    8. 'Công cụ dụng cụ'   : Tổng hợp CCDC qua SUMIF ('Hao phí VT') + 10% phụ
    9. 'Máy thi công'      : Tổng hợp ca máy & điện năng qua SUMIF + 5% phụ
    10. 'THDT hạng mục'    : Tổng hợp kinh phí vĩ mô (T, C, TT, TL, G, GTGT, Làm tròn -3)
    11. 'Đơn giá chi tiết' : Chiết tính đơn giá 1 đơn vị mẫu
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
        wb.remove(wb.active) # Xóa sheet rỗng ban đầu

        # -------------------------------------------------------------
        # 1. BẢNG MÀU & ĐỊNH DẠNG TYPOGRAPHY 100% TIMES NEW ROMAN
        # -------------------------------------------------------------
        fn_name = "Times New Roman"
        font_title_15b = Font(name=fn_name, size=15, bold=True, color="000000")
        font_sub_11i = Font(name=fn_name, size=11, italic=True, color="000000")
        font_header_11b = Font(name=fn_name, size=11, bold=True, color="000000")
        font_sec_12b = Font(name=fn_name, size=12, bold=True, color="000000")
        font_data_11r = Font(name=fn_name, size=11, bold=False, color="000000")
        font_data_11b = Font(name=fn_name, size=11, bold=True, color="000000")
        font_input_11b = Font(name=fn_name, size=11, bold=True, color="0000FF") # Chữ xanh cho ô input

        # Fill màu chuẩn F1
        fill_header_gray = PatternFill(start_color="FFEFEFF2", end_color="FFEFEFF2", fill_type="solid")
        fill_sub_gray = PatternFill(start_color="FFF2F2F2", end_color="FFF2F2F2", fill_type="solid")
        fill_input_yellow = PatternFill(start_color="FFFFFFB4", end_color="FFFFFFB4", fill_type="solid") # Vàng kem F1
        fill_total_pale = PatternFill(start_color="FFEFEFF2", end_color="FFEFEFF2", fill_type="solid")

        # Viền kẻ chuẩn F1
        thin_side = Side(style='thin', color='A6A6A6')
        double_side = Side(style='double', color='000000')
        border_cell = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)
        border_total = Border(top=thin_side, bottom=double_side, left=thin_side, right=thin_side)

        # Number formats
        FMT_CURRENCY = "#,##0"
        FMT_NORM = "#,##0.0000"
        FMT_QTY = "#,##0.000"
        FMT_INT = "#,##0"
        FMT_PCT = "0.0%"
        FMT_PCT2 = "0.00%"

        # =============================================================
        # SHEET 1: 'Hệ số' (Bảng tham số điều hành vĩ mô)
        # =============================================================
        ws_hs = wb.create_sheet(title="Hệ số")
        ws_hs.views.sheetView[0].showGridLines = True
        ws_hs.append(["Hạng mục 1", "", "", ""])
        ws_hs.append(["HS điều chỉnh máy thi công", "hsBM", 1.0, 1.0])
        ws_hs.append(["HS điều chỉnh nhân công", "hsBNC", 1.0, 1.0])
        ws_hs.append(["Chi phí chung theo chi phí trực tiếp", "hsC", 0.20, 0.20])
        ws_hs.append(["Hệ số đảm bảo an toàn giao thông", "hsDBATGT", 0.010, 0.010])
        ws_hs.append(["Hệ số lán trại, nhà tạm", "hsGxdnt", 0.011, 0.011])
        ws_hs.append(["Hệ số riêng vật liệu", "hsRVL", 1.0, 1.0])
        ws_hs.append(["Thu nhập chịu thuế tính trước", "hsTL", 0.055, 0.055])
        ws_hs.append(["Hệ số trực tiếp phí khác", "hsTT", 0.025, 0.025])
        ws_hs.append(["Thuế VAT", "hsGTGT", 0.08, 0.08])
        ws_hs.append(["Hệ số vật liệu phụ (Khoản 4.4 TT20)", "hsVLP", 0.08, 0.08])
        ws_hs.append(["Hệ số CCDC phụ (Khoản 4.2 TT20)", "hsCCDCP", 0.10, 0.10])
        ws_hs.append(["Hệ số thiết bị phụ", "hsTBP", 0.05, 0.05])

        for r in range(1, 14):
            for c in range(1, 5):
                cell = ws_hs.cell(r, c)
                cell.font = font_data_11r
                cell.border = border_cell
                if c == 3: # Ô tham số input F1
                    cell.fill = fill_input_yellow
                    cell.font = font_input_11b
                    if isinstance(cell.value, (int, float)):
                        cell.number_format = FMT_PCT if cell.value < 1.0 else FMT_INT
        ws_hs.column_dimensions['A'].width = 38
        ws_hs.column_dimensions['B'].width = 14
        ws_hs.column_dimensions['C'].width = 14
        ws_hs.column_dimensions['D'].width = 14

        # =============================================================
        # SHEET 2: 'Lương nhân công' (Tính lương ngày công chuẩn 22 ngày)
        # =============================================================
        ws_lnc = wb.create_sheet(title="Lương nhân công")
        ws_lnc.views.sheetView[0].showGridLines = True
        ws_lnc.append(["BẢNG TÍNH LƯƠNG NHÂN CÔNG QUAN TRẮC MÔI TRƯỜNG"])
        ws_lnc.append(["(Căn cứ theo QĐ số 80/2026/QĐ-UBND & TTLT 56/2015/TTLT-BTNMT-BNV chia 22 ngày làm việc chuẩn)"])
        ws_lnc.append([])
        ws_lnc.append(["", "Vùng/Khu vực:", "Vùng IV (Tuy Phong - Bình Thuận)", ""])
        ws_lnc.append(["", "Hệ số điều chỉnh:", 1.0, ""])
        ws_lnc.append([])
        ws_lnc.append(["Mã nhân công", "Tên nhóm / Chức danh nhân công", "Mức lương cơ sở / tháng", "Hệ số điều chỉnh", "Đơn giá ngày công (/22 ngày)"])

        salary_table = [
            ("NC_LDKT", "Lao động kỹ thuật (Kỹ sư/QTVTNMT - Bậc 4-5/7)", 7020000, "=C5", "=ROUND(C8/22*D8, 0)"),
            ("NC_LDPT", "Lao động phổ thông (Phụ việc hiện trường/vận chuyển)", 4352400, "=C5", "=ROUND(C9/22*D9, 0)"),
            ("NC_III_1", "Quan trắc viên tài nguyên môi trường Bậc 1", 5475600, "=C5", "=ROUND(C10/22*D10, 0)"),
            ("NC_III_2", "Quan trắc viên tài nguyên môi trường Bậc 2", 6247800, "=C5", "=ROUND(C11/22*D11, 0)"),
            ("NC_III_3", "Quan trắc viên tài nguyên môi trường Bậc 3", 7020000, "=C5", "=ROUND(C12/22*D12, 0)"),
            ("NC_III_4", "Quan trắc viên tài nguyên môi trường Bậc 4", 7792200, "=C5", "=ROUND(C13/22*D13, 0)"),
            ("NC_II_1", "Quan trắc viên chính tài nguyên môi trường Bậc 1", 10296000, "=C5", "=ROUND(C14/22*D14, 0)")
        ]
        for row in salary_table:
            ws_lnc.append(list(row))

        # Format Sheet Lương nhân công
        ws_lnc.cell(1, 1).font = font_title_15b
        ws_lnc.cell(2, 1).font = font_sub_11i
        for c in range(1, 6):
            cell = ws_lnc.cell(7, c)
            cell.font = font_header_11b
            cell.fill = fill_header_gray
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        for r in range(8, 8 + len(salary_table)):
            for c in range(1, 6):
                cell = ws_lnc.cell(r, c)
                cell.font = font_data_11r
                cell.border = border_cell
                if c == 3:
                    cell.number_format = FMT_CURRENCY
                    cell.fill = fill_input_yellow
                    cell.font = font_input_11b
                elif c == 5:
                    cell.number_format = FMT_CURRENCY
                    cell.font = font_data_11b

        ws_lnc.column_dimensions['A'].width = 16
        ws_lnc.column_dimensions['B'].width = 50
        ws_lnc.column_dimensions['C'].width = 24
        ws_lnc.column_dimensions['D'].width = 18
        ws_lnc.column_dimensions['E'].width = 28

        # =============================================================
        # SHEET 3: 'Tính giá ca máy' (Giá ca máy & Điện năng EVN)
        # =============================================================
        ws_cm = wb.create_sheet(title="Tính giá ca máy")
        ws_cm.views.sheetView[0].showGridLines = True
        ws_cm.append(["BẢNG TÍNH GIÁ CA MÁY & THIẾT BỊ QUAN TRẮC MÔI TRƯỜNG"])
        ws_cm.append(["(Căn cứ theo Thông tư số 45/2013/TT-BTC & Thông tư số 20/2017/TT-BTNMT)"])
        ws_cm.append([])
        ws_cm.append(["Xăng RON 92:", "", 22791, "đồng/lít", "", "", "", "", "", "", "Vùng/Khu vực:", "Vùng IV"])
        ws_cm.append(["Dầu Diezel 0,05S:", "", 22591, "đồng/lít"])
        ws_cm.append(["Dầu Mazut 3,5S:", "", 13548, "đồng/lít"])
        ws_cm.append(["Điện năng EVN:", "", 1920.37, "đồng/kWh"])
        ws_cm.append([])
        ws_cm.append([
            "Mã máy", "Loại máy và thiết bị", "Số ca/năm", "Nguyên giá (MSC)",
            "ĐM Khấu hao (%)", "ĐM Sửa chữa (%)", "ĐM Chi phí khác (%)",
            "Chi phí Khấu hao 1 ca", "Chi phí Sửa chữa 1 ca", "Chi phí Khác 1 ca", "Điện năng (kWh/ca)", "Tiền điện 1 ca", "ĐƠN GIÁ 1 CA MÁY"
        ])

        eq_samples = [
            ("M_KHTSCD", "Khấu hao thiết bị quan trắc chuyên dụng (Máy đo khí, ồn, bụi, quang phổ)", 250, 450000000, 0.10, 0.03, 0.02, "=ROUND(D9*E9/C9, 0)", "=ROUND(D9*F9/C9, 0)", "=ROUND(D9*G9/C9, 0)", 0, 0, "=H9+I9+J9+L9"),
            ("M_NANGLUONG", "Điện năng vận hành thiết bị PTN, tủ sấy, lò nung mẫu", 250, 0, 0, 0, 0, 0, 0, 0, 8, "=ROUND(K10*$C$7, 0)", "=L10"),
            ("M_FLUEGAS", "Máy phân tích khí phát thải tự động Flue Gas Analyzer", 200, 850000000, 0.10, 0.03, 0.02, "=ROUND(D11*E11/C11, 0)", "=ROUND(D11*F11/C11, 0)", "=ROUND(D11*G11/C11, 0)", 12, "=ROUND(K11*$C$7, 0)", "=H11+I11+J11+L11"),
            ("M_ISOKINETIC", "Hệ thống lấy mẫu bụi Isokinetic ống khói (Method 5)", 200, 620000000, 0.10, 0.03, 0.02, "=ROUND(D12*E12/C12, 0)", "=ROUND(D12*F12/C12, 0)", "=ROUND(D12*G12/C12, 0)", 16, "=ROUND(K12*$C$7, 0)", "=H12+I12+J12+L12"),
            ("M_NOISE", "Máy đo độ ồn và độ rung tích hợp Rion NL-52", 250, 160000000, 0.10, 0.03, 0.02, "=ROUND(D13*E13/C13, 0)", "=ROUND(D13*F13/C13, 0)", "=ROUND(D13*G13/C13, 0)", 2, "=ROUND(K13*$C$7, 0)", "=H13+I13+J13+L13"),
            ("M_AAS", "Hệ thống quang phổ hấp thu nguyên tử AAS", 250, 1850000000, 0.10, 0.03, 0.02, "=ROUND(D14*E14/C14, 0)", "=ROUND(D14*F14/C14, 0)", "=ROUND(D14*G14/C14, 0)", 24, "=ROUND(K14*$C$7, 0)", "=H14+I14+J14+L14"),
            ("M_GCMS", "Hệ thống sắc ký khí khối phổ GC/MS", 250, 2400000000, 0.10, 0.03, 0.02, "=ROUND(D15*E15/C15, 0)", "=ROUND(D15*F15/C15, 0)", "=ROUND(D15*G15/C15, 0)", 32, "=ROUND(K15*$C$7, 0)", "=H15+I15+J15+L15")
        ]
        for eq in eq_samples:
            ws_cm.append(list(eq))

        # Format Sheet Tính giá ca máy
        ws_cm.cell(1, 1).font = font_title_15b
        ws_cm.cell(2, 1).font = font_sub_11i
        ws_cm.cell(4, 3).fill = fill_input_yellow
        ws_cm.cell(5, 3).fill = fill_input_yellow
        ws_cm.cell(6, 3).fill = fill_input_yellow
        ws_cm.cell(7, 3).fill = fill_input_yellow # Điện năng ô input F1

        for c in range(1, 14):
            cell = ws_cm.cell(8, c)
            cell.font = font_header_11b
            cell.fill = fill_header_gray
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        for r in range(9, 9 + len(eq_samples)):
            for c in range(1, 14):
                cell = ws_cm.cell(r, c)
                cell.font = font_data_11r
                cell.border = border_cell
                if c in (3, 4, 8, 9, 10, 12, 13):
                    cell.number_format = FMT_CURRENCY
                if c in (5, 6, 7):
                    cell.number_format = FMT_PCT
                if c == 13:
                    cell.font = font_data_11b
                    cell.fill = fill_sub_gray

        ws_cm.column_dimensions['A'].width = 16
        ws_cm.column_dimensions['B'].width = 46
        ws_cm.column_dimensions['C'].width = 12
        ws_cm.column_dimensions['D'].width = 20
        ws_cm.column_dimensions['M'].width = 24

        # =============================================================
                # =============================================================
        # SHEET 12: 'Đơn giá chi tiết' (Chiết tính 2 tầng Micro & Macro cho toàn bộ 253 công tác)
        # =============================================================
        ws_dgct = wb.create_sheet(title="Đơn giá chi tiết")
        ws_dgct.views.sheetView[0].showGridLines = True
        ws_dgct.append(["BẢNG ĐƠN GIÁ CHI TIẾT 1 ĐƠN VỊ CÔNG TÁC QUAN TRẮC MÔI TRƯỜNG"])
        ws_dgct.append(["='Công trình'!A3"])
        ws_dgct.append(["='Công trình'!A4"])
        ws_dgct.append([])
        ws_dgct.append([
            "STT", "Mã hiệu đơn giá", "TT Vật tư", "Mã hiệu VL, NC, M",
            "Tên công tác / Thành phần hao phí chi tiết", "Đơn vị", "Định mức", "Đơn giá (VNĐ)", "Hệ số", "Thành tiền (VNĐ)"
        ])

        # Pre-build lookup dictionaries for fast mapping
        mats_map = {}
        for m in (materials_db.get('items', []) if isinstance(materials_db, dict) else materials_db):
            mats_map[m.get('name', '').lower().strip()] = float(m.get('approved_price') or m.get('price_ktat') or 85000)

        tools_map = {}
        for t in (tools_db.get('items', []) if isinstance(tools_db, dict) else tools_db):
            tools_map[t.get('name', '').lower().strip()] = float(t.get('shift_unit_price') or 1458)

        eq_map = {}
        for e in (equipment_db.get('items', []) if isinstance(equipment_db, dict) else equipment_db):
            eq_map[e.get('name', '').lower().strip()] = float(e.get('shift_unit_rate') or 88800)

        curr_dgct_r = 6
        map_dgct = {}

        for idx, it in enumerate(pakt_items, start=1):
            code_str = it.get("ma_gop", f"TT20_{idx:03d}")
            name_str = it.get("thong_so", "Thông số quan trắc")
            dvt_str = it.get("dvt", "mẫu")
            core_code = it.get("code", f"P_{idx}")
            tt20_data = it.get("tt20_data", {})

            # 1. Master row of the công tác
            master_dgct_r = curr_dgct_r
            ws_dgct.append([idx, code_str, "", "", name_str, dvt_str, "", "", "", ""])
            curr_dgct_r += 1

            # Extract norms from field, lab, single
            mat_list = []
            labor_list = []
            tool_list = []
            eq_list = []

            for stage_key, stage_lbl in [('field', 'Ngoại nghiệp'), ('lab', 'Nội nghiệp'), ('single', 'Toàn phần')]:
                sub = tt20_data.get(stage_key)
                if not sub or not isinstance(sub, dict):
                    continue
                nc_norm = sub.get('dinh_muc_cong')
                nc_title = sub.get('dinh_bien') or f'Quan trắc viên ({stage_lbl})'
                if nc_norm and float(nc_norm) > 0:
                    labor_list.append((nc_title, float(nc_norm), stage_lbl))
                for m in sub.get('materials', []):
                    m_name = m.get('name', '').strip()
                    m_unit = m.get('unit', '').strip()
                    m_norm = float(m.get('norm') or 0.0)
                    if m_norm > 0:
                        mat_list.append((m_name, m_unit, m_norm, stage_lbl))
                for t in sub.get('tools', []):
                    raw_name = str(t.get('name') or '').strip()
                    raw_unit = str(t.get('unit') or '').strip()
                    raw_life = str(t.get('lifespan_months') or '').strip().lower()
                    t_norm = float(t.get('norm') or 0.0)
                    if raw_name.isdigit() or raw_name == "":
                        t_name = raw_unit
                        valid_units = ['cái', 'bộ', 'đôi', 'hộp', 'chiếc', 'dây', 'tấm', 'cuốn', 'bình', 'kw']
                        t_unit = raw_life if raw_life in valid_units else 'cái'
                    else:
                        t_name = raw_name
                        t_unit = raw_unit or 'cái'
                    if t_norm > 0 and t_name:
                        tool_list.append((t_name, t_unit, t_norm, stage_lbl))
                for e in sub.get('equipment', []):
                    e_name = e.get('name', '').strip()
                    e_unit = e.get('unit', '').strip()
                    e_norm = float(e.get('norm') or 0.0)
                    if e_norm > 0:
                        eq_list.append((e_name, e_unit, e_norm, stage_lbl))

            # 2. Section Vật liệu
            vl_row = curr_dgct_r
            if mat_list:
                vl_start = curr_dgct_r + 1
                ws_dgct.append(["", "", "", "", "Vật liệu", "", "", "", "", ""])
                curr_dgct_r += 1
                for m_idx, (m_name, m_unit, m_norm, stage_lbl) in enumerate(mat_list, 1):
                    price = mats_map.get(m_name.lower().strip(), 85000)
                    ws_dgct.append([
                        "", f"VL_{core_code}", m_idx, f"VL_{m_idx:03d}", f" - {m_name} ({stage_lbl})", m_unit,
                        m_norm, price, 1.0, f"=ROUND(G{curr_dgct_r}*H{curr_dgct_r}*I{curr_dgct_r}, 0)"
                    ])
                    curr_dgct_r += 1
                vl_end_main = curr_dgct_r - 1
                # 8% Vật liệu phụ khác theo Khoản 4.4 TT20
                ws_dgct.append([
                    "", "VL_KHAC", len(mat_list)+1, "VL_KHAC", " - Vật liệu phụ khác (8% VL chính theo Khoản 4.4 TT20)", "%",
                    "='Hệ số'!$C$11", "", 1.0, f"=ROUND(SUM(J{vl_start}:J{vl_end_main})*G{curr_dgct_r}, 0)"
                ])
                vl_end = curr_dgct_r
                curr_dgct_r += 1
                ws_dgct.cell(vl_row, 10).value = f"=ROUND(SUM(J{vl_start}:J{vl_end}), 0)"
            else:
                ws_dgct.append(["", "", "", "", "Vật liệu", "", "", "", "", 0])
                curr_dgct_r += 1

            # 3. Section Nhân công
            nc_row = curr_dgct_r
            if labor_list:
                nc_start = curr_dgct_r + 1
                ws_dgct.append(["", "", "", "", "Nhân công", "", "", "", "", ""])
                curr_dgct_r += 1
                for l_idx, (nc_title, nc_norm, stage_lbl) in enumerate(labor_list, 1):
                    price_formula = "='Lương nhân công'!$E$9" if ("phổ thông" in nc_title.lower() or "phụ việc" in nc_title.lower()) else "='Lương nhân công'!$E$8"
                    ws_dgct.append([
                        "", f"NC_{core_code}", l_idx, f"NC_{l_idx:02d}", f" - {nc_title} ({stage_lbl})", "công",
                        nc_norm, price_formula, 1.0, f"=ROUND(G{curr_dgct_r}*H{curr_dgct_r}*I{curr_dgct_r}, 0)"
                    ])
                    curr_dgct_r += 1
                nc_end = curr_dgct_r - 1
                ws_dgct.cell(nc_row, 10).value = f"=ROUND(SUM(J{nc_start}:J{nc_end}), 0)"
            else:
                ws_dgct.append(["", "", "", "", "Nhân công", "", "", "", "", 0])
                curr_dgct_r += 1

            # 4. Section CCDC & Máy thi công
            m_row = curr_dgct_r
            all_machinery = []
            for t_name, t_unit, t_norm, stage_lbl in tool_list:
                price = tools_map.get(t_name.lower().strip(), 1458)
                all_machinery.append((f"DC: {t_name}", t_unit, t_norm, price, stage_lbl))
            for e_name, e_unit, e_norm, stage_lbl in eq_list:
                price = eq_map.get(e_name.lower().strip(), 85000)
                all_machinery.append((f"M: {e_name}", e_unit, e_norm, price, stage_lbl))

            if all_machinery:
                m_start = curr_dgct_r + 1
                ws_dgct.append(["", "", "", "", "Máy thi công & CCDC", "", "", "", "", ""])
                curr_dgct_r += 1
                for m_idx, (m_name, m_unit, m_norm, price, stage_lbl) in enumerate(all_machinery, 1):
                    ws_dgct.append([
                        "", f"M_{core_code}", m_idx, f"M_{m_idx:02d}", f" - {m_name} ({stage_lbl})", m_unit,
                        m_norm, price, 1.0, f"=ROUND(G{curr_dgct_r}*H{curr_dgct_r}*I{curr_dgct_r}, 0)"
                    ])
                    curr_dgct_r += 1
                m_end = curr_dgct_r - 1
                ws_dgct.cell(m_row, 10).value = f"=ROUND(SUM(J{m_start}:J{m_end}), 0)"
            else:
                ws_dgct.append(["", "", "", "", "Máy thi công & CCDC", "", "", "", "", 0])
                curr_dgct_r += 1

            # 5. Khối chi phí vĩ mô 1 mẫu (Tier 2 Macro Costs)
            t_row = curr_dgct_r
            ws_dgct.append(["", "", "", "", "Chi phí trực tiếp (VL + NC + M)", "T", "", "", "", f"=ROUND(J{vl_row}+J{nc_row}+J{m_row}, 0)"])
            curr_dgct_r += 1

            gt_row = curr_dgct_r
            c_row = curr_dgct_r + 1
            tt_row = curr_dgct_r + 2
            tl_row = curr_dgct_r + 3
            g_row = curr_dgct_r + 4
            gtgt_row = curr_dgct_r + 5
            gxd_row = curr_dgct_r + 6
            lt_row = curr_dgct_r + 7
            total_row = curr_dgct_r + 8

            ws_dgct.append(["", "", "", "", "Chi phí gián tiếp (C + TT)", "GT", "", "", "", f"=J{c_row}+J{tt_row}"])
            curr_dgct_r += 1

            ws_dgct.append(["", "", "", "", "Chi phí chung (T x 20%)", "C", "='Hệ số'!$C$4", "", "", f"=ROUND(J{t_row}*G{c_row}, 0)"])
            curr_dgct_r += 1

            ws_dgct.append(["", "", "", "", "Chi phí một số công việc không xác định (T x 2,5%)", "TT", "='Hệ số'!$C$9", "", "", f"=ROUND(J{t_row}*G{tt_row}, 0)"])
            curr_dgct_r += 1

            ws_dgct.append(["", "", "", "", "Thu nhập chịu thuế tính trước ((T + GT) x 5,5%)", "TL", "='Hệ số'!$C$8", "", "", f"=ROUND((J{t_row}+J{gt_row})*G{tl_row}, 0)"])
            curr_dgct_r += 1

            ws_dgct.append(["", "", "", "", "Chi phí xây dựng trước thuế (T + GT + TL)", "G", "", "", "", f"=ROUND(J{t_row}+J{gt_row}+J{tl_row}, 0)"])
            curr_dgct_r += 1

            ws_dgct.append(["", "", "", "", "Thuế giá trị gia tăng (G x 8%)", "GTGT", "='Hệ số'!$C$10", "", "", f"=ROUND(J{g_row}*G{gtgt_row}, 0)"])
            curr_dgct_r += 1

            ws_dgct.append(["", "", "", "", "CHI PHÍ SAU THUẾ (G + GTGT)", "Gxd", "", "", "", f"=ROUND(J{g_row}+J{gtgt_row}, 0)"])
            curr_dgct_r += 1

            ws_dgct.append(["", "", "", "", "Chi phí nhà tạm để ở và điều hành (G x 1,1% x (1 + 8%))", "LT", "='Hệ số'!$C$6", "", "", f"=ROUND(J{g_row}*G{lt_row}*(1+'Hệ số'!$C$10), 0)"])
            curr_dgct_r += 1

            ws_dgct.append(["", "", "", "", "Tổng cộng đơn giá dự thầu 1 mẫu (Gxd + LT)", "VNĐ", "", "", "", f"=ROUND(J{gxd_row}+J{lt_row}, 0)"])
            curr_dgct_r += 1

            # Dòng phân cách giữa các công tác
            ws_dgct.append([])
            curr_dgct_r += 1

            map_dgct[idx] = {
                'row_vl': vl_row,
                'row_nc': nc_row,
                'row_m': m_row,
                'row_t': t_row,
                'row_total': total_row
            }

        # Format Sheet Đơn giá chi tiết
        ws_dgct.cell(1, 1).font = font_title_15b
        ws_dgct.cell(2, 1).font = font_sub_11i
        ws_dgct.cell(3, 1).font = font_sub_11i
        for c in range(1, 11):
            ws_dgct.cell(5, c).font = font_header_11b
            ws_dgct.cell(5, c).fill = fill_header_gray
            ws_dgct.cell(5, c).alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        for r in range(6, curr_dgct_r):
            col_e_val = str(ws_dgct.cell(r, 5).value or "")
            col_a_val = ws_dgct.cell(r, 1).value
            is_master = isinstance(col_a_val, int)
            is_sub = col_e_val in ("Vật liệu", "Nhân công", "Máy thi công & CCDC", "Chi phí trực tiếp (VL + NC + M)")
            is_total = "Tổng cộng đơn giá dự thầu" in col_e_val

            for c in range(1, 11):
                cell = ws_dgct.cell(r, c)
                cell.font = font_data_11r
                if cell.value is not None and str(cell.value) != "":
                    cell.border = border_cell

                if is_master:
                    cell.font = font_data_11b
                    cell.fill = fill_header_gray
                elif is_sub:
                    cell.font = font_data_11b
                    if col_e_val == "Chi phí trực tiếp (VL + NC + M)":
                        cell.fill = fill_sub_gray
                elif is_total:
                    cell.font = font_data_11b
                    cell.fill = fill_total_pale

                if c in (7, 8, 10):
                    if c == 7 and isinstance(cell.value, float) and cell.value < 1.0:
                        cell.number_format = FMT_PCT2
                    elif c == 7:
                        cell.number_format = FMT_NORM
                    else:
                        cell.number_format = FMT_CURRENCY
                if c in (1, 6, 9):
                    cell.alignment = Alignment(horizontal="center", vertical="center")

        ws_dgct.column_dimensions['A'].width = 8
        ws_dgct.column_dimensions['B'].width = 16
        ws_dgct.column_dimensions['C'].width = 8
        ws_dgct.column_dimensions['D'].width = 14
        ws_dgct.column_dimensions['E'].width = 46
        ws_dgct.column_dimensions['F'].width = 10
        ws_dgct.column_dimensions['G'].width = 14
        ws_dgct.column_dimensions['H'].width = 16
        ws_dgct.column_dimensions['I'].width = 8
        ws_dgct.column_dimensions['J'].width = 20

        # =============================================================
        # SHEET 4: 'Công trình' (Bảng tiên lượng khối lượng 253 dòng PAKT)
        # =============================================================
        ws_ct = wb.create_sheet(title="Công trình")
        ws_ct.views.sheetView[0].showGridLines = True
        ws_ct.append(["BẢNG CHI TIẾT KHỐI LƯỢNG CÔNG TRÌNH QUAN TRẮC MÔI TRƯỜNG"])
        ws_ct.append(["(Ban hành kèm theo Quyết định số 1155/QĐ-NĐVT4 và Thông tư số 20/2017/TT-BTNMT)"])
        ws_ct.append(["CÔNG TRÌNH: QUAN TRẮC MÔI TRƯỜNG CHO NMNĐ VĨNH TÂN 4 VÀ VĨNH TÂN 4 MỞ RỘNG NĂM 2026"])
        ws_ct.append(["HẠNG MỤC: TOÀN BỘ KHỐI LƯỢNG QUAN TRẮC MÔI TRƯỜNG THEO ĐỊNH MỨC THÔNG TƯ 20/2017/TT-BTNMT"])
        ws_ct.append([])
        ws_ct.append([
            "STT", "Ký hiệu vị trí (Bản vẽ)", "Mã hiệu công tác (TT20)", "Danh mục công tác quan trắc", "Đơn vị",
            "Số vị trí quan trắc", "Số đợt / Tần suất (lần/năm)", "Số mẫu song song", "Hệ số chung mẫu (M)",
            "Kích thước phụ", "Ghi chú phương pháp", "KHỐI LƯỢNG THỰC HIỆN (Q)",
            "Đơn giá Vật liệu", "Đơn giá Nhân công", "Đơn giá Dụng cụ", "Đơn giá Máy thi công",
            "CỘNG ĐƠN GIÁ TRỰC TIẾP (Đ/mẫu)", "THÀNH TIỀN TRỰC TIẾP (VNĐ)",
            "ĐƠN GIÁ DỰ THẦU TRỌN GÓI (Đ/mẫu)", "THÀNH TIỀN DỰ THẦU TRỌN GÓI (VNĐ)"
        ])

        start_ct_row = 7
        curr_section = ""
        row_offset = 0
        item_ct_rows = {}

        for idx, it in enumerate(pakt_items, start=1):
            r = start_ct_row + row_offset
            moi_truong = it.get("moi_truong", "KHÔNG KHÍ XUNG QUANH")

            if moi_truong != curr_section:
                curr_section = moi_truong
                ws_ct.append(["", "", "", f"PHẦN: GIÁM SÁT {curr_section.upper()}", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""])
                sec_cell = ws_ct.cell(r, 4)
                sec_cell.font = font_sec_12b
                for c in range(1, 21):
                    ws_ct.cell(r, c).fill = fill_header_gray
                row_offset += 1
                r = start_ct_row + row_offset

            item_ct_rows[idx] = r

            so_vt = it.get("so_vi_tri", 1) or 1
            so_lan = it.get("so_lan", 1) or 1
            vi_tri_str = it.get("vi_tri", f"VT_{idx}")
            code_str = it.get("ma_gop", f"TT20_{idx:03d}")
            name_str = it.get("thong_so", "Thông số quan trắc")
            dvt_str = it.get("dvt", "mẫu")
            m_val = it.get("so_thong_so_chung", 1) or 1

            # Khối lượng Q = Số vị trí * Số lần
            f_q = f"=F{r}*G{r}"

            # Tọa độ link động từ Sheet 'Đơn giá chi tiết'
            dgct_info = map_dgct.get(idx, {'row_vl': 6, 'row_nc': 7, 'row_m': 8, 'row_total': 18})

            f_vl = f"='Đơn giá chi tiết'!$J${dgct_info['row_vl']}"
            f_nc = f"='Đơn giá chi tiết'!$J${dgct_info['row_nc']}"
            f_dc = 0
            f_m = f"='Đơn giá chi tiết'!$J${dgct_info['row_m']}"

            # Cộng đơn giá trực tiếp = M + N + O + P
            f_unit = f"=M{r}+N{r}+O{r}+P{r}"
            # Thành tiền trực tiếp = Q * Cộng đơn giá
            f_total = f"=ROUND(L{r}*Q{r}, 0)"

            # Đơn giá dự thầu trọn gói 1 mẫu (All-in Rate)
            f_all_in = f"='Đơn giá chi tiết'!$J${dgct_info['row_total']}"
            # Thành tiền dự thầu trọn gói
            f_total_all_in = f"=ROUND(L{r}*S{r}, 0)"

            ws_ct.append([
                idx, vi_tri_str, code_str, name_str, dvt_str,
                so_vt, so_lan, 1, m_val,
                "", it.get("sec_id", "TT20"), f_q,
                f_vl, f_nc, f_dc, f_m,
                f_unit, f_total,
                f_all_in, f_total_all_in
            ])
            row_offset += 1

        last_ct_row = start_ct_row + row_offset - 1

        # Dòng tổng cộng Sheet Công trình
        tot_ct_row = last_ct_row + 1
        ws_ct.append([
            "", "", "", "CỘNG TOÀN BỘ CÔNG TRÌNH QUAN TRẮC MÔI TRƯỜNG (253 CÔNG TÁC)", "",
            "", "", "", "", "", "", "",
            "", "", "", "", "",
            f"=SUM(R{start_ct_row}:R{last_ct_row})",
            "",
            f"=SUM(T{start_ct_row}:T{last_ct_row})"
        ])

        # Format Sheet Công trình
        ws_ct.cell(1, 1).font = font_title_15b
        ws_ct.cell(2, 1).font = font_sub_11i
        ws_ct.cell(3, 1).font = font_data_11b
        ws_ct.cell(4, 1).font = font_data_11b

        for c in range(1, 21):
            cell = ws_ct.cell(6, c)
            cell.font = font_header_11b
            cell.fill = fill_header_gray
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        for r in range(start_ct_row, last_ct_row + 1):
            for c in range(1, 21):
                cell = ws_ct.cell(r, c)
                if cell.font != font_sec_12b:
                    cell.font = font_data_11r
                    cell.border = border_cell
                if c in (1, 5, 6, 7, 8, 9):
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                if c in (12, 13, 14, 15, 16, 17, 18, 19, 20):
                    cell.number_format = FMT_CURRENCY
                if c == 12:
                    cell.font = font_data_11b
                if c in (18, 20):
                    cell.font = font_data_11b
                    cell.fill = fill_sub_gray

        # Format dòng tổng cộng
        for c in range(1, 21):
            cell = ws_ct.cell(tot_ct_row, c)
            cell.font = font_data_11b
            cell.border = border_total
            if c in (18, 20):
                cell.fill = fill_total_pale
                cell.number_format = FMT_CURRENCY

        ws_ct.column_dimensions['A'].width = 8
        ws_ct.column_dimensions['B'].width = 18
        ws_ct.column_dimensions['C'].width = 16
        ws_ct.column_dimensions['D'].width = 45
        ws_ct.column_dimensions['L'].width = 16
        ws_ct.column_dimensions['M'].width = 16
        ws_ct.column_dimensions['N'].width = 16
        ws_ct.column_dimensions['O'].width = 12
        ws_ct.column_dimensions['P'].width = 16
        ws_ct.column_dimensions['Q'].width = 18
        ws_ct.column_dimensions['R'].width = 22
        ws_ct.column_dimensions['S'].width = 20
        ws_ct.column_dimensions['T'].width = 24

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
                        "", ("NC_LDPT" if ("phổ thông" in nc_title.lower() or "phụ việc" in nc_title.lower()) else "NC_LDKT"), "NHÂN CÔNG", f" - {nc_title} ({stage_lbl})", "công", "",
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
                    raw_name = str(t.get('name') or '').strip()
                    raw_unit = str(t.get('unit') or '').strip()
                    raw_life = str(t.get('lifespan_months') or '').strip().lower()
                    t_norm = float(t.get('norm') or 0.0)

                    # Tự động nhận diện và hoán đổi trường nếu bị lệch cột (name chứa STT 1, 2, 3...)
                    if raw_name.isdigit() or raw_name == "":
                        t_name = raw_unit
                        valid_units = ['cái', 'bộ', 'đôi', 'hộp', 'chiếc', 'dây', 'tấm', 'cuốn', 'bình', 'kw']
                        t_unit = raw_life if raw_life in valid_units else (t.get('real_unit') or 'cái')
                    else:
                        t_name = raw_name
                        t_unit = raw_unit or 'cái'
                    
                    if t_norm > 0 and t_name:
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
                # =============================================================
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

        ws_thdt.append(["I", "Chi phí trực tiếp (T = VL + DC + NC + M + C_TR)", "=\"VL + DC + NC + M + C_TR\"", "=ROUND(D8+D10+D12+D14+D16, 0)", "T"])
        ws_thdt.append(["1", "Chi phí vật liệu", "=\"VLHT\"", "=ROUND(D9, 0)", "VL"])
        ws_thdt.append(["", " - Đơn giá vật liệu", "Theo bảng tổng hợp vật liệu", f"='Vật liệu'!$G${total_vl_row}", "VLHT"])
        ws_thdt.append(["2", "Chi phí công cụ dụng cụ", "=\"DCHT\"", "=ROUND(D11, 0)", "DC"])
        ws_thdt.append(["", " - Đơn giá công cụ dụng cụ", "Theo bảng tổng hợp dụng cụ", f"='Công cụ dụng cụ'!$G${total_dc_row}", "DCHT"])
        ws_thdt.append(["3", "Chi phí nhân công", "=\"NCHT\"", "=ROUND(D13, 0)", "NC"])
        ws_thdt.append(["", " - Đơn giá nhân công", "Theo bảng tổng hợp nhân công", "='Nhân công'!$G$9", "NCHT"])
        ws_thdt.append(["4", "Chi phí máy và thiết bị thi công", "=\"MHT\"", "=ROUND(D15, 0)", "M"])
        ws_thdt.append(["", " - Đơn giá máy thi công", "Theo bảng tổng hợp máy thi công", f"='Máy thi công'!$G${total_m_row}", "MHT"])
        ws_thdt.append(["5", "Chi phí tính riêng ngoài định mức (Khoản 4.5 TT20)", "=\"C_TR\"", "='Khoản 4.5 TT20'!$J$24", "C_TR"])
        ws_thdt.append(["II", "Chi phí gián tiếp", "=\"C + TT\"", "=D18+D19", "GT"])
        ws_thdt.append(["1", "Chi phí chung", "=\"T x 20%\"", "=ROUND(D7*'Hệ số'!$C$4, 0)", "C"])
        ws_thdt.append(["2", "Chi phí một số công việc không xác định từ thiết kế", "=\"T x 2,5%\"", "=ROUND(D7*'Hệ số'!$C$9, 0)", "TT"])
        ws_thdt.append(["III", "Thu nhập chịu thuế tính trước", "=\"(T + GT) x 5,5%\"", "=ROUND((D7+D17)*'Hệ số'!$C$8, 0)", "TL"])
        ws_thdt.append(["", "Chi phí trước thuế", "=\"T + GT + TL\"", "=ROUND(D7+D17+D20, 0)", "G"])
        ws_thdt.append(["IV", "Thuế giá trị gia tăng", "=\"G x 8%\"", "=ROUND(D21*'Hệ số'!$C$10, 0)", "GTGT"])
        ws_thdt.append(["", "CHI PHÍ SAU THUẾ", "=\"G + GTGT\"", "=ROUND(D21+D22, 0)", "Gxd"])
        ws_thdt.append(["V", "Chi phí nhà tạm để ở và điều hành", "=\"G x 1,1% x (1 + 8%)\"", "=ROUND(D21*'Hệ số'!$C$6*(1+'Hệ số'!$C$10), 0)", "LT"])
        ws_thdt.append(["", "TỔNG CỘNG KINH PHÍ GÓI THẦU", "=\"Gxd + LT\"", "=ROUND(D23+D24, 0)", "TTS"])
        ws_thdt.append(["", "LÀM TRÒN (ĐẾN HÀNG NGHÌN ĐỒNG)", "=\"ROUND(D23, -3)\"", "=ROUND(D25, -3)", "LTR"])

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

                # =============================================================
        # SẮP XẾP LẠI THỨ TỰ CÁC TAB SHEET CHUẨN F1 TRƯỚC KHI LƯU
        # =============================================================
        wb._sheets = [ws_hs, ws_lnc, ws_cm, ws_ct, ws_hp, ws_vl, ws_nc, ws_dc, ws_m, ws_45, ws_thdt, ws_dgct]

        # Đảm bảo 100% font chữ là Times New Roman
        for ws in wb.worksheets:
            for row in ws.iter_rows():
                for cell in row:
                    if cell.font:
                        if cell.font.name != 'Times New Roman':
                            cell.font = Font(name='Times New Roman', size=cell.font.size or 11, bold=cell.font.bold, italic=cell.font.italic, color=cell.font.color)
                    else:
                        cell.font = Font(name='Times New Roman', size=11)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        wb.save(output_path)
        return output_path
