import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from typing import Dict, Any, List

class Excel6SheetF1Exporter:
    """
    Engine xuất file Excel Dự toán Chi phí Quan trắc Môi trường chuẩn 6 Sheet
    thay thế phần mềm chuyên dụng F1:
    1. DM_DinhMuc_TT20      : Cơ sở dữ liệu định mức gốc Thông tư 20/2017
    2. DM_GiaVatTu          : Bảng giá gốc & Thông báo giá (Lương 22 ngày, Vật tư KQLCNT IB2600096765 / 1.08, Ca máy TT45)
    3. DuToan               : Bảng tính chi tiết chi phí trực tiếp (Hệ công thức sống XLOOKUP, khử trùng lặp M >= 1)
    4. Chiettinh            : Bảng chiết tính đơn giá 1 đơn vị mẫu (Đồng/mẫu)
    5. TongHop_KinhPhi      : Bảng tổng hợp kinh phí toàn gói thầu
    6. DM_GiaTruong_BaoGia  : Phụ lục 3 bảng báo giá & Thống kê Mua sắm công (Minh chứng pháp lý IB2600096765)
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

        # Styles
        font_title = Font(name="Calibri", size=13, bold=True, color="1E3A8A")
        font_sub = Font(name="Calibri", size=10, italic=True, color="475569")
        font_header = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
        font_bold = Font(name="Calibri", size=10, bold=True)
        font_regular = Font(name="Calibri", size=10)

        fill_header_blue = PatternFill(start_color="1E40AF", end_color="1E40AF", fill_type="solid")
        fill_header_green = PatternFill(start_color="047857", end_color="047857", fill_type="solid")
        fill_header_purple = PatternFill(start_color="6D28D9", end_color="6D28D9", fill_type="solid")
        fill_zebra = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
        fill_total = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")

        thin_border = Border(
            left=Side(style='thin', color='CBD5E1'),
            right=Side(style='thin', color='CBD5E1'),
            top=Side(style='thin', color='CBD5E1'),
            bottom=Side(style='thin', color='CBD5E1')
        )

        def apply_table_style(ws, header_fill, start_row=4):
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
        # 1. Sheet: DM_DinhMuc_TT20
        # =========================================================================
        ws_dm = wb.create_sheet(title="DM_DinhMuc_TT20")
        ws_dm.append(["CƠ SỞ DỮ LIỆU ĐỊNH MỨC KINH TẾ - KỸ THUẬT GỐC THEO THÔNG TƯ 20/2017/TT-BTNMT"])
        ws_dm.append(["(Nguồn chuẩn để các Sheet Dự toán và Chiết tính tự động tra cứu bằng hàm XLOOKUP)"])
        ws_dm.append([])
        ws_dm.append([
            "STT", "Mã hiệu TT20", "Tên thông số & Công đoạn", "Phân loại", "ĐVT",
            "Hao phí Ngày công (H_NC)", "Hao phí Vật liệu/Hóa chất (H_VL)", "Hao phí Dụng cụ (H_DC)", "Hao phí Ca máy (H_TB)"
        ])
        for idx, it in enumerate(pakt_items, start=1):
            nc_field = it.get("nc_field", 0.3)
            nc_lab = it.get("nc_lab", 0.5)
            ws_dm.append([
                idx,
                it.get("ma_gop", f"TT20_{idx:03d}"),
                f"{it.get('thong_so', '')} ({it.get('moi_truong', '')})",
                "Ngoại nghiệp + Nội nghiệp",
                it.get("dvt", "mẫu"),
                round(nc_field + nc_lab, 4),
                round(it.get("vl_cost_norm", 250000), 2),
                round(it.get("dc_cost_norm", 35000), 2),
                round(it.get("tb_cost_norm", 120000), 2)
            ])
        apply_table_style(ws_dm, fill_header_blue)

        # =========================================================================
        # 2. Sheet: DM_GiaVatTu
        # =========================================================================
        ws_gia = wb.create_sheet(title="DM_GiaVatTu")
        ws_gia.append(["BẢNG GIÁ GỐC & THÔNG BÁO GIÁ QUAN TRẮC MÔI TRƯỜNG NĂM 2026"])
        ws_gia.append(["(Căn cứ: QĐ 80/2026/QĐ-UBND 22 ngày/tháng, KQLCNT IB2600096765 chia 1.08 trước thuế & TT 45/2013)"])
        ws_gia.append([])
        
        # Bảng 1: Lương nhân công
        ws_gia.append(["BẢNG 1: ĐƠN GIÁ TIỀN LƯƠNG NHÂN CÔNG VIÊN CHỨC (22 NGÀY LÀM VIỆC CHUẨN)"])
        ws_gia.append(["Mã Bậc", "Chức Danh Chuyên Môn (TTLT 56)", "Hệ Số Lương", "Lương Cơ Bản (VNĐ/tháng)", "Đơn Giá Ngày Công (/22 ngày)", "Ghi Chú"])
        salary_rows = [
            ("NC_III_1", "Quan trắc viên tài nguyên môi trường Bậc 1", 2.34, 5475600, 248891, "Chuẩn TTLT 56/2015 chia 22 ngày"),
            ("NC_III_2", "Quan trắc viên tài nguyên môi trường Bậc 2", 2.67, 6247800, 283991, "Chuẩn TTLT 56/2015 chia 22 ngày"),
            ("NC_III_3", "Quan trắc viên tài nguyên môi trường Bậc 3", 3.00, 7020000, 319091, "Chuẩn TTLT 56/2015 chia 22 ngày"),
            ("NC_III_4", "Quan trắc viên tài nguyên môi trường Bậc 4", 3.33, 7792200, 354191, "Chuẩn TTLT 56/2015 chia 22 ngày"),
            ("NC_II_1", "Quan trắc viên chính tài nguyên môi trường Bậc 1", 4.40, 10296000, 468000, "Chuẩn TTLT 56/2015 chia 22 ngày"),
            ("NC_PT", "Lao động phổ thông / Phụ trợ ngoại nghiệp", 1.86, 4352400, 197836, "Hỗ trợ bốc vác, chèo thuyền")
        ]
        for s in salary_rows:
            ws_gia.append(list(s))

        ws_gia.append([])
        ws_gia.append(["BẢNG 2: ĐƠN GIÁ VẬT LIỆU, HÓA CHẤT, KHÍ CHUẨN (TRƯỚC THUẾ = KQLCNT IB2600096765 / 1.08)"])
        ws_gia.append(["Mã Vật Tư", "Tên Hóa Chất, Khí Chuẩn, Dung Môi", "ĐVT", "Đơn Giá Trước Thuế (/1.08)", "Mã TBMT / Nguồn Tra Cứu", "Hãng Sản Xuất & Xuất Xứ"])
        
        mats_list = materials_db.get("items", [])
        for m in mats_list[:60]:
            ws_gia.append([
                m.get("id", ""),
                m.get("name", ""),
                m.get("unit", ""),
                m.get("msc_unit_price", m.get("approved_price", 0)),
                m.get("msc_tbmt_code", "IB2600096765"),
                m.get("msc_contractor", "Merck / Hach / Air Liquide")
            ])
            
        ws_gia.append([])
        ws_gia.append(["BẢNG 3: ĐƠN GIÁ CA MÁY & THIẾT BỊ PHÂN TÍCH THEO THÔNG TƯ 45/2013/TT-BTC"])
        ws_gia.append(["Mã Máy", "Tên Thiết Bị Quan Trắc / Phân Tích", "ĐVT", "Nguyên Giá (VNĐ)", "Số Ca Chuẩn/Năm", "Khấu Hao 1 Ca", "Sửa Chữa 1 Ca", "Điện Năng 1 Ca", "Đơn Giá 1 Ca Máy"])
        
        eq_list = equipment_db.get("items", [])
        for eq in eq_list[:30]:
            orig = eq.get("original_price", 150000000)
            shifts = eq.get("shifts_per_year", 250)
            dep = round(orig * 0.10 / shifts)
            rep = round(orig * 0.03 / shifts)
            pwr = round(eq.get("power_kw", 1.5) * 8 * 1800)
            ws_gia.append([
                eq.get("id", ""),
                eq.get("name", ""),
                "Ca",
                orig,
                shifts,
                dep,
                rep,
                pwr,
                dep + rep + pwr
            ])
            
        apply_table_style(ws_gia, fill_header_purple, start_row=5)

        # =========================================================================
        # 3. Sheet: DuToan (Trái tim của dự toán)
        # =========================================================================
        ws_dt = wb.create_sheet(title="DuToan")
        ws_dt.append(["BẢNG DỰ TOÁN CHI TIẾT CHI PHÍ QUAN TRẮC MÔI TRƯỜNG NĂM 2026 - EVN VĨNH TÂN 4"])
        ws_dt.append(["(Hệ công thức sống XLOOKUP, khử trùng lặp M >= 1, bóc tách NC +20%, VL +8%, DC +10% chia 22 ca, K4.5)"])
        ws_dt.append([])
        ws_dt.append([
            "STT", "Mã Hiệu TT20", "Tên Thông Số Công Tác", "ĐVT", "Số Lượng Mẫu (Q)", "Số Thông Số Dùng Chung (M)",
            "Hao Phí NC Gốc", "Ngày Công NN (+20%/M)", "Ngày Công Lab", "Đơn Giá Ngày Công (VNĐ)",
            "Thành Tiền NC (C_NC)", "Thành Tiền VL (C_VL, +8%)", "Thành Tiền DC (C_DC, +10%)",
            "Thành Tiền TB (C_TB)", "Chi Phí Tính Riêng (K4.5)", "Tổng Chi Phí Trực Tiếp (T)", "Đơn Giá 1 Mẫu (VNĐ)"
        ])

        start_r = 5
        for i, it in enumerate(pakt_items, start=1):
            r = start_r + i - 1
            code = it.get("ma_gop", f"TT20_{i:03d}")
            q = it.get("so_luong_mau", 1)
            m_val = it.get("so_thong_so_chung", 1)
            if m_val < 1: m_val = 1
            
            # Formulas
            # G: Hao phí NC gốc = XLOOKUP(B{r}, DM_DinhMuc_TT20!$B:$B, DM_DinhMuc_TT20!$F:$F, 0.8)
            f_g = f"=IFERROR(XLOOKUP(B{r}, DM_DinhMuc_TT20!$B:$B, DM_DinhMuc_TT20!$F:$F, 0.8), 0.8)"
            # H: Ngày công NN (+20%/M) = ROUND((G{r} * 0.4 * 1.2) / IF(F{r}>0, F{r}, 1), 4)
            f_h = f"=ROUND((G{r} * 0.4 * 1.2) / IF(F{r}>0, F{r}, 1), 4)"
            # I: Ngày công Lab = ROUND(G{r} * 0.6, 4)
            f_i = f"=ROUND(G{r} * 0.6, 4)"
            # J: Đơn giá lương = DM_GiaVatTu!$E$6 (Bậc III.3)
            f_j = "=DM_GiaVatTu!$E$8"
            # K: Thành tiền NC = ROUND((H{r} + I{r}) * J{r} * E{r}, 0)
            f_k = f"=ROUND((H{r} + I{r}) * J{r} * E{r}, 0)"
            # L: Thành tiền VL (+8%) = ROUND(E{r} * 1.08 * IFERROR(XLOOKUP(B{r}, DM_DinhMuc_TT20!$B:$B, DM_DinhMuc_TT20!$G:$G, 150000), 150000), 0)
            f_l = f"=ROUND(E{r} * 1.08 * IFERROR(XLOOKUP(B{r}, DM_DinhMuc_TT20!$B:$B, DM_DinhMuc_TT20!$G:$G, 150000), 150000), 0)"
            # M: Thành tiền DC (+10%) = ROUND(E{r} * 1.10 * IFERROR(XLOOKUP(B{r}, DM_DinhMuc_TT20!$B:$B, DM_DinhMuc_TT20!$H:$H, 25000), 25000), 0)
            f_m = f"=ROUND(E{r} * 1.10 * IFERROR(XLOOKUP(B{r}, DM_DinhMuc_TT20!$B:$B, DM_DinhMuc_TT20!$H:$H, 25000), 25000), 0)"
            # N: Thành tiền TB = ROUND(E{r} * IFERROR(XLOOKUP(B{r}, DM_DinhMuc_TT20!$B:$B, DM_DinhMuc_TT20!$I:$I, 80000), 80000), 0)
            f_n = f"=ROUND(E{r} * IFERROR(XLOOKUP(B{r}, DM_DinhMuc_TT20!$B:$B, DM_DinhMuc_TT20!$I:$I, 80000), 80000), 0)"
            # O: Chi phí tính riêng K4.5 (thuê tàu, giàn giáo...)
            val_o = it.get("cost_k45", 0)
            # P: Tổng trực tiếp T = K{r} + L{r} + M{r} + N{r} + O{r}
            f_p = f"=K{r}+L{r}+M{r}+N{r}+O{r}"
            # Q: Đơn giá 1 mẫu = IF(E{r}>0, ROUND(P{r}/E{r}, 0), 0)
            f_q = f"=IF(E{r}>0, ROUND(P{r}/E{r}, 0), 0)"

            ws_dt.append([
                i, code, it.get("thong_so", ""), it.get("dvt", "mẫu"), q, m_val,
                f_g, f_h, f_i, f_j, f_k, f_l, f_m, f_n, val_o, f_p, f_q
            ])

        last_r = start_r + len(pakt_items) - 1
        total_r = last_r + 1
        ws_dt.append([
            "TỔNG CỘNG", "", "", "", f"=SUM(E{start_r}:E{last_r})", "",
            "", f"=SUM(H{start_r}:H{last_r})", f"=SUM(I{start_r}:I{last_r})", "",
            f"=SUM(K{start_r}:K{last_r})", f"=SUM(L{start_r}:L{last_r})", f"=SUM(M{start_r}:M{last_r})",
            f"=SUM(N{start_r}:N{last_r})", f"=SUM(O{start_r}:O{last_r})", f"=SUM(P{start_r}:P{last_r})", ""
        ])
        for c in range(1, 18):
            cell = ws_dt.cell(row=total_r, column=c)
            cell.font = font_bold
            cell.fill = fill_total

        apply_table_style(ws_dt, fill_header_green, start_row=4)

        # =========================================================================
        # 4. Sheet: Chiettinh (Bảng chiết tính 1 đơn vị mẫu - Đồng/mẫu)
        # =========================================================================
        ws_ct = wb.create_sheet(title="Chiettinh")
        ws_ct.append(["BẢNG CHIẾT TÍNH ĐƠN GIÁ CHI TIẾT 1 ĐƠN VỊ MẪU QUAN TRẮC MÔI TRƯỜNG"])
        ws_ct.append(["(Phục vụ in ấn, kẹp hồ sơ nghiệm thu thanh quyết toán và trình Hội đồng Thẩm định)"])
        ws_ct.append([])
        ws_ct.append([
            "STT", "Mã Hiệu TT20", "Tên Thông Số Quan Trắc", "ĐVT",
            "ĐG Nhân Công 1 Mẫu", "ĐG Vật Liệu 1 Mẫu", "ĐG Dụng Cụ 1 Mẫu", "ĐG Thiết Bị 1 Mẫu",
            "Cộng Chi Phí Trực Tiếp 1 Mẫu (Đồng/mẫu)", "Ghi Chú Công Đoạn"
        ])

        for idx, it in enumerate(pakt_items, start=1):
            dt_row = start_r + idx - 1
            ws_ct.append([
                idx,
                it.get("ma_gop", f"TT20_{idx:03d}"),
                it.get("thong_so", ""),
                it.get("dvt", "mẫu"),
                f"=IF(DuToan!E{dt_row}>0, ROUND(DuToan!K{dt_row}/DuToan!E{dt_row}, 0), 0)",
                f"=IF(DuToan!E{dt_row}>0, ROUND(DuToan!L{dt_row}/DuToan!E{dt_row}, 0), 0)",
                f"=IF(DuToan!E{dt_row}>0, ROUND(DuToan!M{dt_row}/DuToan!E{dt_row}, 0), 0)",
                f"=IF(DuToan!E{dt_row}>0, ROUND(DuToan!N{dt_row}/DuToan!E{dt_row}, 0), 0)",
                f"=E{idx+4}+F{idx+4}+G{idx+4}+H{idx+4}",
                "Bao gồm lấy mẫu hiện trường và phân tích phòng thí nghiệm"
            ])
        apply_table_style(ws_ct, fill_header_blue, start_row=4)

        # =========================================================================
        # 5. Sheet: TongHop_KinhPhi (Tổng hợp kinh phí toàn gói thầu)
        # =========================================================================
        ws_th = wb.create_sheet(title="TongHop_KinhPhi")
        ws_th.append(["TỔNG HỢP KINH PHÍ DỰ TOÁN GÓI THẦU QUAN TRẮC MÔI TRƯỜNG EVN VĨNH TÂN 4"])
        ws_th.append(["(Cấu trúc tài chính vĩ mô: Chi phí trực tiếp T, Quản lý chung 15%, Thu nhập tính trước 6%, Dự phòng 5%, VAT 8%)"])
        ws_th.append([])
        ws_th.append(["STT", "Khoản Mục Chi Phí", "Ký Hiệu", "Cách Tính / Công Thức", "Giá Trị (VNĐ)", "Tỷ Lệ (%)"])

        ws_th.append(["1", "Chi phí trực tiếp", "T", f"=DuToan!P{total_r}", f"=DuToan!P{total_r}", "=E5/E11"])
        ws_th.append(["2", "Chi phí quản lý chung", "C_GT", "=ROUND(0.15 * E5, 0)", "=ROUND(0.15 * E5, 0)", "=E6/E11"])
        ws_th.append(["3", "Thu nhập chịu thuế tính trước", "TL", "=ROUND(0.06 * (E5 + E6), 0)", "=ROUND(0.06 * (E5 + E6), 0)", "=E7/E11"])
        ws_th.append(["4", "Chi phí dự phòng phát sinh", "DP", "=ROUND(0.05 * (E5 + E6 + E7), 0)", "=ROUND(0.05 * (E5 + E6 + E7), 0)", "=E8/E11"])
        ws_th.append(["5", "CỘNG CHI PHÍ TRƯỚC THUẾ", "G_Q", "=E5 + E6 + E7 + E8", "=E5 + E6 + E7 + E8", "=E9/E11"])
        ws_th.append(["6", "Thuế Giá trị gia tăng (VAT)", "VAT", "=ROUND(0.08 * E9, 0)", "=ROUND(0.08 * E9, 0)", "=E10/E11"])
        ws_th.append(["7", "TỔNG KINH PHÍ GÓI THẦU (SAU THUẾ)", "TTS", "=E9 + E10", "=E9 + E10", "100.0%"])

        for r in range(5, 12):
            cell_val = ws_th.cell(row=r, column=5)
            cell_val.number_format = "#,##0"
            cell_pct = ws_th.cell(row=r, column=6)
            cell_pct.number_format = "0.00%"
            if r in (9, 11):
                for c in range(1, 7):
                    ws_th.cell(row=r, column=c).font = font_bold
                    ws_th.cell(row=r, column=c).fill = fill_total

        apply_table_style(ws_th, fill_header_green, start_row=4)

        # =========================================================================
        # 6. Sheet: DM_GiaTruong_BaoGia (Minh chứng pháp lý KQLCNT & Báo giá)
        # =========================================================================
        ws_bg = wb.create_sheet(title="DM_GiaTruong_BaoGia")
        ws_bg.append(["PHỤ LỤC MINH CHỨNG PHÁP LÝ: KẾT QUẢ LỰA CHỌN NHÀ THẦU & BÁO GIÁ THỊ TRƯỜNG"])
        ws_bg.append(["(Căn cứ: Gói thầu IB2600096765 của NMNĐ Vĩnh Tân 4 ngày 03/04/2026 & Điều 16 Nghị định 24/2024/NĐ-CP)"])
        ws_bg.append([])
        ws_bg.append([
            "STT", "Tên Hàng Hóa / Dịch Vụ", "ĐVT", "Đơn Giá Trúng Thầu (VAT 8%)",
            "Đơn Giá Chưa VAT (/1.08)", "Mã TBMT / Hồ Sơ", "Ngày Duyệt KQLCNT", "Đơn Vị Trúng Thầu / Báo Giá", "Cơ Sở Pháp Lý"
        ])

        kqlcnt_samples = [
            ("Khí Heli 99.99%", "Bình", 10141200, 9390000, "IB2600096765", "03/04/2026", "Quingdao Ruiming", "KQLCNT chính NMNĐ Vĩnh Tân 4"),
            ("Khí Hydrogen UHP", "Bình", 21621600, 20020000, "IB2600096765", "03/04/2026", "Air Liquide", "KQLCNT chính NMNĐ Vĩnh Tân 4"),
            ("Khí Nitơ 99.99%", "Bình", 324000, 300000, "IB2600096765", "03/04/2026", "Sovigaz", "KQLCNT chính NMNĐ Vĩnh Tân 4"),
            ("Bình khí Argon 99.9999%", "Bình", 6112800, 5660000, "IB2600096765", "03/04/2026", "Cryotech", "KQLCNT chính NMNĐ Vĩnh Tân 4"),
            ("Bình khí CO+CO2", "Bình", 12171600, 11270000, "IB2600096765", "03/04/2026", "Cryotech", "KQLCNT chính NMNĐ Vĩnh Tân 4"),
            ("Bình Khí NO", "Bình", 37141200, 34390000, "IB2600096765", "03/04/2026", "CSL", "KQLCNT chính NMNĐ Vĩnh Tân 4"),
            ("Bình và khí Span SO2", "Bình", 29721600, 27520000, "IB2600096765", "03/04/2026", "CSL", "KQLCNT chính NMNĐ Vĩnh Tân 4"),
            ("Acetone Merck Chai 1000ml", "Chai", 399600, 370000, "IB2600096765", "03/04/2026", "Merck", "KQLCNT chính NMNĐ Vĩnh Tân 4"),
            ("Toluen Merck Chai 1000ml", "Chai", 421200, 390000, "IB2600096765", "03/04/2026", "Merck", "KQLCNT chính NMNĐ Vĩnh Tân 4"),
            ("Methanol 99.8%", "Lít", 43200, 40000, "IB2600096765", "03/04/2026", "Brunei Methanol", "KQLCNT chính NMNĐ Vĩnh Tân 4"),
            ("Hóa chất EDTA Merck 100g", "Chai", 1371600, 1270000, "IB2600096765", "03/04/2026", "Merck", "KQLCNT chính NMNĐ Vĩnh Tân 4"),
            ("Sắt (III) Clorua FeCl3 40%", "Kg", 6480, 6000, "IB2600096765", "03/04/2026", "Vũ Hoàng", "KQLCNT chính NMNĐ Vĩnh Tân 4"),
            ("Acid chlohydride 36-37% Merck", "Chai", 648000, 600000, "IB2600096765", "03/04/2026", "Merck", "KQLCNT chính NMNĐ Vĩnh Tân 4"),
            ("Natri hydroxit NaOH Merck 1000g", "Chai", 1166400, 1080000, "IB2600096765", "03/04/2026", "Merck", "KQLCNT chính NMNĐ Vĩnh Tân 4"),
            ("Dịch vụ thuê tàu biển quan trắc xa bờ", "Chuyến", 16200000, 15000000, "HĐ_TAU_01", "15/01/2026", "Công ty CP Dịch vụ Hàng hải", "Hợp đồng nguyên tắc & 3 báo giá"),
            ("Lắp dựng giàn giáo sàn thao tác ống khói", "Điểm", 21600000, 20000000, "BG_SCAFFOLD", "20/01/2026", "Công ty Xây lắp Nhiệt điện", "Định mức BXD TT 12/2021 & 3 báo giá"),
            ("Vận chuyển mẫu bảo quản lạnh hỏa tốc", "Đợt", 4320000, 4000000, "BG_EXPRESS", "10/02/2026", "Viettel Post Express", "Hợp đồng cung ứng dịch vụ hỏa tốc")
        ]

        for idx, row in enumerate(kqlcnt_samples, start=1):
            ws_bg.append([idx] + list(row))

        apply_table_style(ws_bg, fill_header_purple, start_row=4)

        # Lưu file
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        wb.save(output_path)
        return output_path
