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
        ws_hs.append(["Chi phí chung theo chi phí trực tiếp", "hsC", 0.073, 0.073])
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
            "Đơn giá Vật liệu", "Đơn giá Nhân công", "Đơn giá Dụng cụ", "Đơn giá Máy thi công", "CỘNG ĐƠN GIÁ (Đ/mẫu)", "THÀNH TIỀN (VNĐ)"
        ])

        start_ct_row = 7
        curr_section = ""
        row_offset = 0

        for idx, it in enumerate(pakt_items, start=1):
            r = start_ct_row + row_offset
            moi_truong = it.get("moi_truong", "KHÔNG KHÍ XUNG QUANH")
            
            # Nếu đổi môi trường -> Chèn 1 dòng Header phân nhóm lớn F1
            if moi_truong != curr_section:
                curr_section = moi_truong
                ws_ct.append(["", "", "", f"PHẦN: GIÁM SÁT {curr_section.upper()}", "", "", "", "", "", "", "", "", "", "", "", "", "", ""])
                sec_cell = ws_ct.cell(r, 4)
                sec_cell.font = font_sec_12b
                for c in range(1, 19):
                    ws_ct.cell(r, c).fill = fill_header_gray
                row_offset += 1
                r = start_ct_row + row_offset

            so_vt = it.get("so_vi_tri", 1) or 1
            so_lan = it.get("so_lan", 1) or 1
            vi_tri_str = it.get("vi_tri", f"VT_{idx}")
            code_str = it.get("ma_gop", f"TT20_{idx:03d}")
            name_str = it.get("thong_so", "Thông số quan trắc")
            dvt_str = it.get("dvt", "mẫu")
            m_val = it.get("so_thong_so_chung", 1) or 1

            # Công thức Khối lượng Q = Số vị trí * Số lần (Cột L = F * G)
            f_q = f"=F{r}*G{r}"
            # Thành tiền = Khối lượng Q * Cộng Đơn giá (Cột R = L * Q)
            f_total = f"=ROUND(L{r}*Q{r}, 0)"
            # Đơn giá cộng = M + N + O + P
            f_unit = f"=M{r}+N{r}+O{r}+P{r}"

            ws_ct.append([
                idx, vi_tri_str, code_str, name_str, dvt_str,
                so_vt, so_lan, 1, m_val,
                "", it.get("sec_id", "TT20"), f_q,
                round(it.get("vl_cost_norm", 185000), 0),
                round(it.get("nc_cost_norm", 320000), 0),
                round(it.get("dc_cost_norm", 35000), 0),
                round(it.get("tb_cost_norm", 120000), 0),
                f_unit, f_total
            ])
            row_offset += 1

        last_ct_row = start_ct_row + row_offset - 1
        # Format Sheet Công trình
        ws_ct.cell(1, 1).font = font_title_15b
        ws_ct.cell(2, 1).font = font_sub_11i
        ws_ct.cell(3, 1).font = font_data_11b
        ws_ct.cell(4, 1).font = font_data_11b

        for c in range(1, 19):
            cell = ws_ct.cell(6, c)
            cell.font = font_header_11b
            cell.fill = fill_header_gray
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        for r in range(start_ct_row, last_ct_row + 1):
            for c in range(1, 19):
                cell = ws_ct.cell(r, c)
                if cell.font != font_sec_12b:
                    cell.font = font_data_11r
                    cell.border = border_cell
                if c in (1, 5, 6, 7, 8, 9):
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                if c in (12, 13, 14, 15, 16, 17, 18):
                    cell.number_format = FMT_CURRENCY
                if c == 12: # Cột Khối lượng Q in đậm
                    cell.font = font_data_11b
                if c == 18:
                    cell.font = font_data_11b
                    cell.fill = fill_sub_gray

        ws_ct.column_dimensions['A'].width = 8
        ws_ct.column_dimensions['B'].width = 18
        ws_ct.column_dimensions['C'].width = 16
        ws_ct.column_dimensions['D'].width = 45
        ws_ct.column_dimensions['L'].width = 16
        ws_ct.column_dimensions['Q'].width = 18
        ws_ct.column_dimensions['R'].width = 22

        # =============================================================
        # SHEET 5: 'Hao phí VT' (Bung định mức TT20 chi tiết Master-Detail)
        # =============================================================
        ws_hp = wb.create_sheet(title="Hao phí VT")
        ws_hp.views.sheetView[0].showGridLines = True
        ws_hp.append(["HAO PHÍ VẬT LIỆU, NHÂN CÔNG, MÁY VÀ CÔNG CỤ DỤNG CỤ"])
        ws_hp.append(["='Công trình'!A3"])
        ws_hp.append(["='Công trình'!A4"])
        ws_hp.append([])
        ws_hp.append([
            "STT", "Mã hiệu", "TT Vật tư", "Tên công tác / Thành phần hao phí", "Đơn vị", "Khối lượng công trình (Q)",
            "Định mức VL", "Định mức NC", "Định mức CCDC", "Định mức Máy",
            "Khối lượng VL", "Khối lượng NC", "Khối lượng CCDC", "Khối lượng Máy", "Ghi chú bóc tách"
        ])

        # Bung đại diện cho toàn bộ các công việc
        hp_row = 6
        for i in range(1, min(60, len(pakt_items) + 1)):
            ct_r = start_ct_row + i - 1
            # Dòng Cha
            ws_hp.append([
                f"='Công trình'!A{ct_r}", f"='Công trình'!C{ct_r}", "", f"='Công trình'!D{ct_r}", f"='Công trình'!E{ct_r}",
                f"='Công trình'!L{ct_r}", "", "", "", "", "", "", "", "", "PAKT & Định mức TT20"
            ])
            master_r = hp_row
            ws_hp.cell(master_r, 4).font = font_data_11b
            for c in range(1, 16):
                ws_hp.cell(master_r, c).fill = fill_header_gray
                ws_hp.cell(master_r, c).border = border_cell
            hp_row += 1

            # Dòng Con 1: Nhân công kỹ thuật (NC_LDKT)
            ws_hp.append([
                "", "NC_LDKT", "LĐKT", " - Kỹ sư / Kiểm định viên / Quan trắc viên", "công", "",
                "", 0.1760, "", "", "", f"=ROUND(F{master_r}*H{hp_row}, 4)", "", "", "TTLT 56/2015"
            ])
            hp_row += 1

            # Dòng Con 2: Lao động phổ thông (NC_LDPT)
            ws_hp.append([
                "", "NC_LDPT", "LĐPT", " - Lao động phổ thông phụ việc hiện trường", "công", "",
                "", 0.0440, "", "", "", f"=ROUND(F{master_r}*H{hp_row}, 4)", "", "", "Hỗ trợ ngoại nghiệp"
            ])
            hp_row += 1

            # Dòng Con 3: Ca CCDC (CCDC_01)
            ws_hp.append([
                "", "CCDC_01", "CCDC", " - Ca dụng cụ, thiết bị nhỏ đo đạc/lấy mẫu", "ca", "",
                "", "", 0.1000, "", "", "", f"=ROUND(F{master_r}*I{hp_row}, 4)", "", "Khoản 4.2 TT20"
            ])
            hp_row += 1

            # Dòng Con 4: CCDC phụ 10% (CCDC_PHU)
            ws_hp.append([
                "", "CCDC_PHU", "CCDC_PHỤ", " - Dụng cụ phụ khác (10% CCDC chính)", "%", "",
                "", "", 0.1000, "", "", "", f"=ROUND(M{hp_row-1}*I{hp_row}, 4)", "", "10% Khoản 4.2 TT20"
            ])
            hp_row += 1

            # Dòng Con 5: Khấu hao máy chính (M_KHTSCD)
            ws_hp.append([
                "", "M_KHTSCD", "MÁY", " - Khấu hao thiết bị quan trắc chuyên dụng", "ca", "",
                "", "", "", 0.0800, "", "", "", f"=ROUND(F{master_r}*J{hp_row}, 4)", "TT 45/2013"
            ])
            hp_row += 1

            # Dòng Con 6: Điện năng tiêu thụ (M_NANGLUONG)
            ws_hp.append([
                "", "M_NANGLUONG", "ĐIỆN", " - Năng lượng điện vận hành thiết bị PTN", "kWh", "",
                "", "", "", 0.5000, "", "", "", f"=ROUND(F{master_r}*J{hp_row}, 4)", "Điện năng PTN"
            ])
            hp_row += 1

            # Dòng Con 7: Vật liệu hóa chất (VL_01)
            ws_hp.append([
                "", "VL_01", "VL", " - Hóa chất phân tích tinh khiết, màng lọc, chuẩn", "bộ", "",
                0.0400, "", "", "", f"=ROUND(F{master_r}*G{hp_row}, 4)", "", "", "", "Khoản 4.4 TT20"
            ])
            hp_row += 1

            # Dòng Con 8: Vật liệu phụ khác 8% (VL_KHAC)
            ws_hp.append([
                "", "VL_KHAC", "VL_PHỤ", " - Vật liệu phụ khác (8% vật liệu chính)", "%", "",
                0.0800, "", "", "", f"=ROUND(K{hp_row-1}*G{hp_row}, 4)", "", "", "", "8% Khoản 4.4 TT20"
            ])
            hp_row += 1

        last_hp_row = hp_row - 1
        # Format Sheet Hao phí VT
        ws_hp.cell(1, 1).font = font_title_15b
        ws_hp.cell(2, 1).font = font_sub_11i
        ws_hp.cell(3, 1).font = font_sub_11i
        for c in range(1, 16):
            cell = ws_hp.cell(5, c)
            cell.font = font_header_11b
            cell.fill = fill_header_gray
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        for r in range(6, last_hp_row + 1):
            for c in range(1, 16):
                cell = ws_hp.cell(r, c)
                if cell.fill != fill_header_gray:
                    cell.font = font_data_11r
                    cell.border = border_cell
                if c in (7, 8, 9, 10, 11, 12, 13, 14):
                    cell.number_format = FMT_NORM

        ws_hp.column_dimensions['A'].width = 8
        ws_hp.column_dimensions['B'].width = 16
        ws_hp.column_dimensions['C'].width = 12
        ws_hp.column_dimensions['D'].width = 46
        ws_hp.column_dimensions['K'].width = 16
        ws_hp.column_dimensions['L'].width = 16
        ws_hp.column_dimensions['M'].width = 16
        ws_hp.column_dimensions['N'].width = 16

        # =============================================================
                # =============================================================
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

        ws_thdt.append(["I", "Chi phí trực tiếp (T = VL + DC + NC + M)", "=\"VL + DC + NC + M\"", "=ROUND(D8+D10+D12+D14, 0)", "T"])
        ws_thdt.append(["1", "Chi phí vật liệu", "=\"VLHT\"", "=ROUND(D8, 0)", "VL"])
        ws_thdt.append(["", " - Đơn giá vật liệu", "Theo bảng tổng hợp vật liệu", f"='Vật liệu'!$G${total_vl_row}", "VLHT"])
        ws_thdt.append(["2", "Chi phí công cụ dụng cụ", "=\"DCHT\"", "=ROUND(D10, 0)", "DC"])
        ws_thdt.append(["", " - Đơn giá công cụ dụng cụ", "Theo bảng tổng hợp dụng cụ", f"='Công cụ dụng cụ'!$G${total_dc_row}", "DCHT"])
        ws_thdt.append(["3", "Chi phí nhân công", "=\"NCHT\"", "=ROUND(D12, 0)", "NC"])
        ws_thdt.append(["", " - Đơn giá nhân công", "Theo bảng tổng hợp nhân công", "='Nhân công'!$G$9", "NCHT"])
        ws_thdt.append(["4", "Chi phí máy và thiết bị thi công", "=\"MHT\"", "=ROUND(D14, 0)", "M"])
        ws_thdt.append(["", " - Đơn giá máy thi công", "Theo bảng tổng hợp máy thi công", f"='Máy thi công'!$G${total_m_row}", "MHT"])
        ws_thdt.append(["II", "Chi phí gián tiếp", "=\"C + TT\"", "=D16+D17", "GT"])
        ws_thdt.append(["1", "Chi phí chung", "=\"T x 7,3%\"", "=ROUND(D6*'Hệ số'!$C$4, 0)", "C"])
        ws_thdt.append(["2", "Chi phí một số công việc không xác định từ thiết kế", "=\"T x 2,5%\"", "=ROUND(D6*'Hệ số'!$C$9, 0)", "TT"])
        ws_thdt.append(["III", "Thu nhập chịu thuế tính trước", "=\"(T + GT) x 5,5%\"", "=ROUND((D6+D15)*'Hệ số'!$C$8, 0)", "TL"])
        ws_thdt.append(["", "Chi phí trước thuế", "=\"T + GT + TL\"", "=ROUND(D6+D15+D18, 0)", "G"])
        ws_thdt.append(["IV", "Thuế giá trị gia tăng", "=\"G x 8%\"", "=ROUND(D19*'Hệ số'!$C$10, 0)", "GTGT"])
        ws_thdt.append(["", "CHI PHÍ SAU THUẾ", "=\"G + GTGT\"", "=ROUND(D19+D20, 0)", "Gxd"])
        ws_thdt.append(["V", "Chi phí nhà tạm để ở và điều hành", "=\"G x 1,1% x (1 + 8%)\"", "=ROUND(D19*'Hệ số'!$C$6*(1+'Hệ số'!$C$10), 0)", "LT"])
        ws_thdt.append(["", "TỔNG CỘNG KINH PHÍ GÓI THẦU", "=\"Gxd + LT\"", "=ROUND(D21+D22, 0)", "TTS"])
        ws_thdt.append(["", "LÀM TRÒN (ĐẾN HÀNG NGHÌN ĐỒNG)", "=\"ROUND(D23, -3)\"", "=ROUND(D23, -3)", "LTR"])

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

        # SHEET 11: 'Đơn giá chi tiết' (Chiết tính đơn giá 1 đơn vị mẫu)
        # =============================================================
        ws_dgct = wb.create_sheet(title="Đơn giá chi tiết")
        ws_dgct.views.sheetView[0].showGridLines = True
        ws_dgct.append(["BẢNG ĐƠN GIÁ CHI TIẾT 1 ĐƠN VỊ CÔNG TÁC QUAN TRẮC MÔI TRƯỜNG"])
        ws_dgct.append(["='Công trình'!A3"])
        ws_dgct.append(["='Công trình'!A4"])
        ws_dgct.append([])
        ws_dgct.append([
            "STT", "Mã hiệu đơn giá", "Tên công tác quan trắc", "Đơn vị",
            "ĐG Vật liệu (Đ/mẫu)", "ĐG Nhân công (Đ/mẫu)", "ĐG CCDC (Đ/mẫu)", "ĐG Máy thi công (Đ/mẫu)",
            "CỘNG CHI PHÍ TRỰC TIẾP 1 MẪU (T)", "Ghi chú quy chuẩn TT20"
        ])

        for idx, it in enumerate(pakt_items[:60], start=1):
            ct_r = start_ct_row + idx - 1
            ws_dgct.append([
                idx,
                f"='Công trình'!C{ct_r}",
                f"='Công trình'!D{ct_r}",
                f"='Công trình'!E{ct_r}",
                f"='Công trình'!M{ct_r}",
                f"='Công trình'!N{ct_r}",
                f"='Công trình'!O{ct_r}",
                f"='Công trình'!P{ct_r}",
                f"=E{idx+4}+F{idx+4}+G{idx+4}+H{idx+4}",
                "Bao gồm lấy mẫu hiện trường và phân tích PTN"
            ])

        for c in range(1, 11):
            ws_dgct.cell(4, c).font = font_header_11b
            ws_dgct.cell(4, c).fill = fill_header_gray
            ws_dgct.cell(4, c).alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        for r in range(5, 5 + min(60, len(pakt_items))):
            for c in range(1, 11):
                cell = ws_dgct.cell(r, c)
                cell.font = font_data_11r
                cell.border = border_cell
                if c in (5, 6, 7, 8, 9):
                    cell.number_format = FMT_CURRENCY
                if c == 9:
                    cell.font = font_data_11b
                    cell.fill = fill_sub_gray

        ws_dgct.column_dimensions['B'].width = 16
        ws_dgct.column_dimensions['C'].width = 45
        ws_dgct.column_dimensions['E'].width = 18
        ws_dgct.column_dimensions['F'].width = 18
        ws_dgct.column_dimensions['G'].width = 18
        ws_dgct.column_dimensions['H'].width = 18
        ws_dgct.column_dimensions['I'].width = 24

        # Lưu file workbook
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        # Enforce 100% Times New Roman across every single cell in all worksheets
        for ws in wb.worksheets:
            for row in ws.iter_rows():
                for cell in row:
                    if cell.font:
                        if cell.font.name != 'Times New Roman':
                            cell.font = Font(name='Times New Roman', size=cell.font.size or 11, bold=cell.font.bold, italic=cell.font.italic, color=cell.font.color)
                    else:
                        cell.font = Font(name='Times New Roman', size=11)

        wb.save(output_path)
        return output_path
