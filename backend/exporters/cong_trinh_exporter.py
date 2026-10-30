import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from typing import List, Dict, Any, Tuple
from openpyxl.worksheet.worksheet import Worksheet


def _build_cong_trinh_header(
    ws_ct: Worksheet, 
    font_title_15b: Font, 
    font_sub_11i: Font, 
    font_data_11b: Font, 
    font_header_11b: Font, 
    fill_header_gray: PatternFill
) -> None:
    """1. Tạo phần tiêu đề công trình và hàng header 20 cột."""
    ws_ct.append(["BẢNG CHI TIẾT KHỐI LƯỢNG CÔNG TRÌNH QUAN TRẮC MÔI TRƯỜNG"])
    ws_ct.append(["(Căn cứ theo Quyết định số 1155/QĐ-NĐVT4 và Thông tư số 20/2017/TT-BTNMT)"])
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

    ws_ct.cell(1, 1).font = font_title_15b
    ws_ct.cell(2, 1).font = font_sub_11i
    ws_ct.cell(3, 1).font = font_data_11b
    ws_ct.cell(4, 1).font = font_data_11b

    for c in range(1, 21):
        cell = ws_ct.cell(6, c)
        cell.font = font_header_11b
        cell.fill = fill_header_gray
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)


def _write_cong_trinh_section(
    ws_ct: Worksheet, 
    r: int, 
    curr_section: str, 
    font_sec_12b: Font, 
    fill_header_gray: PatternFill
) -> None:
    """2. Ghi dòng tiêu đề phân đoạn (Phần: Giám sát môi trường...)."""
    ws_ct.append(["", "", "", f"PHẦN: GIÁM SÁT {curr_section.upper()}", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""])
    sec_cell = ws_ct.cell(r, 4)
    sec_cell.font = font_sec_12b
    for c in range(1, 21):
        ws_ct.cell(r, c).fill = fill_header_gray


def _write_cong_trinh_row(
    ws_ct: Worksheet, 
    idx: int, 
    r: int, 
    it: Dict[str, Any], 
    map_dgct: Dict[Any, Dict[str, Any]]
) -> None:
    """3. Ghi 1 dòng dữ liệu công tác quan trắc."""
    so_vt = it.get("so_vi_tri", 1) or 1
    so_lan = it.get("so_lan", 1) or 1
    vi_tri_str = it.get("vi_tri", f"VT_{idx}")
    code_str = it.get("ma_gop", f"TT20_{idx:03d}")
    name_str = it.get("thong_so", "Thông số quan trắc")
    dvt_str = it.get("dvt", "mẫu")
    m_val = it.get("so_thong_so_chung", 1) or 1

    f_q = f"=F{r}*G{r}"

    dgct_info = map_dgct.get(idx) or map_dgct.get(str(idx), {})
    row_vl = dgct_info.get('row_vl')
    row_nc = dgct_info.get('row_nc')
    row_dc = dgct_info.get('row_dc')
    row_m  = dgct_info.get('row_m')
    row_total = dgct_info.get('row_total')

    f_vl = f"='Đơn giá chi tiết'!$J${row_vl}" if row_vl else 0
    f_nc = f"='Đơn giá chi tiết'!$J${row_nc}" if row_nc else 0
    f_dc = f"='Đơn giá chi tiết'!$J${row_dc}" if row_dc else 0
    f_m  = f"='Đơn giá chi tiết'!$J${row_m}"  if row_m  else 0

    f_unit = f"=M{r}+N{r}+O{r}+P{r}"
    f_total = f"=ROUND(L{r}*Q{r}, 0)"

    f_all_in = f"='Đơn giá chi tiết'!$J${row_total}" if row_total else 0
    f_total_all_in = f"=ROUND(L{r}*S{r}, 0)"

    ws_ct.append([
        idx, vi_tri_str, code_str, name_str, dvt_str,
        so_vt, so_lan, 1, m_val,
        "", it.get("sec_id", "TT20"), f_q,
        f_vl, f_nc, f_dc, f_m,
        f_unit, f_total,
        f_all_in, f_total_all_in
    ])


def _write_cong_trinh_total(
    ws_ct: Worksheet, 
    tot_ct_row: int, 
    start_ct_row: int, 
    last_ct_row: int, 
    font_data_11b: Font, 
    border_total: Border, 
    fill_total_pale: PatternFill, 
    FMT_CURRENCY: str
) -> None:
    """4. Ghi dòng tổng cộng toàn bộ công trình quan trắc."""
    ws_ct.append([
        "", "", "", "CỘNG TOÀN BỘ CÔNG TRÌNH QUAN TRẮC MÔI TRƯỜNG", "",
        "", "", "", "", "", "", "", "", "", "", "", "",
        f"=SUM(R{start_ct_row}:R{last_ct_row})", "",
        f"=SUM(T{start_ct_row}:T{last_ct_row})"
    ])

    for c in range(1, 21):
        cell = ws_ct.cell(tot_ct_row, c)
        cell.font = font_data_11b
        cell.border = border_total
        if c in (18, 20):
            cell.fill = fill_total_pale
            cell.number_format = FMT_CURRENCY


def _apply_cong_trinh_styling(
    ws_ct: Worksheet, 
    start_ct_row: int, 
    last_ct_row: int, 
    font_sec_12b: Font, 
    font_data_11r: Font, 
    border_cell: Border, 
    FMT_CURRENCY: str
) -> None:
    """5. Áp dụng định dạng style cho các dòng dữ liệu công trình."""
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


def update_cong_trinh_from_dgct(
    ws_ct: Worksheet, 
    item_ct_rows: Dict[int, int], 
    map_dgct: Dict[Any, Dict[str, Any]]
) -> None:
    """
    6. Cập nhật các cột M, N, O, P, Q, R, S, T của sheet 'Công trình' 
    sau khi đã sinh xong sheet 'Đơn giá chi tiết' và có tọa độ chính xác.
    """
    for idx, r in item_ct_rows.items():
        dgct_info = map_dgct.get(idx) or map_dgct.get(str(idx), {})
        row_vl = dgct_info.get('row_vl')
        row_nc = dgct_info.get('row_nc')
        row_dc = dgct_info.get('row_dc')
        row_m  = dgct_info.get('row_m')
        row_total = dgct_info.get('row_total')

        # Cột M: Đơn giá Vật liệu
        ws_ct.cell(r, 13).value = f"='Đơn giá chi tiết'!$J${row_vl}" if row_vl else 0
        # Cột N: Đơn giá Nhân công
        ws_ct.cell(r, 14).value = f"='Đơn giá chi tiết'!$J${row_nc}" if row_nc else 0
        # Cột O: Đơn giá Dụng cụ
        ws_ct.cell(r, 15).value = f"='Đơn giá chi tiết'!$J${row_dc}" if row_dc else 0
        # Cột P: Đơn giá Máy thi công
        ws_ct.cell(r, 16).value = f"='Đơn giá chi tiết'!$J${row_m}" if row_m else 0
        # Cột Q: CỘNG ĐƠN GIÁ TRỰC TIẾP
        ws_ct.cell(r, 17).value = f"=M{r}+N{r}+O{r}+P{r}"
        # Cột R: THÀNH TIỀN TRỰC TIẾP
        ws_ct.cell(r, 18).value = f"=ROUND(L{r}*Q{r}, 0)"
        # Cột S: ĐƠN GIÁ DỰ THẦU TRỌN GÓI
        ws_ct.cell(r, 19).value = f"='Đơn giá chi tiết'!$J${row_total}" if row_total else 0
        # Cột T: THÀNH TIỀN DỰ THẦU TRỌN GÓI
        ws_ct.cell(r, 20).value = f"=ROUND(L{r}*S{r}, 0)"


def build_cong_trinh_sheet(
    wb, 
    pakt_items: List[Dict[str, Any]], 
    map_dgct: Dict[Any, Dict[str, Any]], 
    font_title_15b: Font, 
    font_sub_11i: Font, 
    font_header_11b: Font, 
    font_sec_12b: Font, 
    font_data_11r: Font, 
    font_data_11b: Font, 
    fill_header_gray: PatternFill, 
    fill_sub_gray: PatternFill, 
    fill_total_pale: PatternFill, 
    border_cell: Border, 
    border_total: Border, 
    FMT_CURRENCY: str
) -> Tuple[Worksheet, Dict[int, int]]:
    """
    7. Xây dựng Sheet 'Công trình' và trả về tuple: (worksheet, item_ct_rows).
    item_ct_rows là registry lưu tọa độ dòng Excel thực tế của từng công tác (idx -> row_excel).
    """
    if "Công trình" in wb.sheetnames:
        ws_ct = wb["Công trình"]
        wb.remove(ws_ct)
        
    ws_ct = wb.create_sheet(title="Công trình")
    ws_ct.views.sheetView[0].showGridLines = True
    
    _build_cong_trinh_header(ws_ct, font_title_15b, font_sub_11i, font_data_11b, font_header_11b, fill_header_gray)

    start_ct_row = 7
    curr_section = ""
    row_offset = 0
    item_ct_rows: Dict[int, int] = {}

    for idx, it in enumerate(pakt_items, start=1):
        r = start_ct_row + row_offset
        moi_truong = it.get("moi_truong", "KHÔNG KHÍ XUNG QUANH")

        if moi_truong != curr_section:
            curr_section = moi_truong
            _write_cong_trinh_section(ws_ct, r, curr_section, font_sec_12b, fill_header_gray)
            row_offset += 1
            r = start_ct_row + row_offset

        item_ct_rows[idx] = r
        _write_cong_trinh_row(ws_ct, idx, r, it, map_dgct)
        row_offset += 1

    last_ct_row = start_ct_row + row_offset - 1
    tot_ct_row = last_ct_row + 1
    
    _write_cong_trinh_total(ws_ct, tot_ct_row, start_ct_row, last_ct_row, font_data_11b, border_total, fill_total_pale, FMT_CURRENCY)
    _apply_cong_trinh_styling(ws_ct, start_ct_row, last_ct_row, font_sec_12b, font_data_11r, border_cell, FMT_CURRENCY)

    return ws_ct, item_ct_rows
