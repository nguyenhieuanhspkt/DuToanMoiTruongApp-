import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border
from openpyxl.worksheet.worksheet import Worksheet
from typing import List, Dict, Any, Tuple
from backend.exporters.cong_cu_exporter import _collect_cong_cu_items
from backend.exporters.may_thi_cong_exporter import _collect_may_items
from backend.storage.onedrive_adapter import OneDriveAdapter


def _init_tinh_gia_ca_may_sheet(wb: openpyxl.Workbook) -> Worksheet:
    """Khởi tạo hoặc làm mới sheet 'Tính giá ca máy' và thiết lập hiển thị lưới."""
    name = "Tính giá ca máy"
    if name in wb.sheetnames:
        ws = wb[name]
        ws.delete_rows(1, ws.max_row)
    else:
        ws = wb.create_sheet(name)
    ws.views.sheetView[0].showGridLines = True
    return ws


def _write_tinh_gia_ca_may_header(ws: Worksheet):
    """Ghi tiêu đề chính và tiêu đề 16 cột theo phương pháp BXD (Dòng 1 đến 5)."""
    ws.append(["BẢNG TÍNH ĐƠN GIÁ CA MÁY, THIẾT BỊ VÀ DỤNG CỤ QUAN TRẮC MÔI TRƯỜNG"])
    ws.append(["(Xác định theo phương pháp tính giá ca máy Thông tư 13/2021/TT-BXD của Bộ Xây dựng)"])
    ws.append(["='Công trình'!A3"])
    ws.append(["='Công trình'!A4"])
    ws.append([])  # Dòng 4 trống
    ws.append([
        "STT",                              # A (1)
        "Mã hiệu",                          # B (2)
        "Tên loại máy, thiết bị, dụng cụ",  # C (3)
        "ĐVT",                              # D (4)
        "Nguyên giá (VNĐ)",                 # E (5)
        "Số ca năm (Nca)",                  # F (6)
        "Tỷ lệ KH (%)",                     # G (7)
        "Khấu hao (đ/ca)",                  # H (8)
        "Tỷ lệ SC (%)",                     # I (9)
        "Sửa chữa (đ/ca)",                  # J (10)
        "Tỷ lệ CPK (%)",                    # K (11)
        "CP khác (đ/ca)",                   # L (12)
        "Nhiên liệu (đ/ca)",                # M (13)
        "Nhân công ĐK (đ/ca)",              # N (14)
        "ĐƠN GIÁ CA MÁY (VNĐ)",             # O (15) ⭐ Cột lấy link
        "Căn cứ tính toán / Ghi chú"        # P (16)
    ])


def _write_section_banner(ws: Worksheet, title: str, font_sec_12b: Font, fill_header_gray: PatternFill, border_cell: Border):
    """Ghi dòng banner phân đoạn lớn (Phần I / Phần II)."""
    ws.append([title] + [""] * 15)
    r = ws.max_row
    ws.row_dimensions[r].height = 24
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=16)
    for c in range(1, 17):
        cell = ws.cell(r, c)
        cell.font = font_sec_12b
        cell.fill = fill_header_gray
        cell.border = border_cell
        cell.alignment = Alignment(horizontal="left", vertical="center")


def _write_items_block(
    ws: Worksheet,
    items: List[Dict[str, Any]],
    prefix_type: str,
    default_nca: int,
    default_kh: float,
    default_sc: float,
    default_cpk: float,
    border_cell: Border,
    font_data_11r: Font,
    font_data_11b: Font,
    FMT_CURRENCY: str,
    lookup_db: Dict[str, Any] = None
) -> Dict[str, int]:
    """Ghi danh sách máy hoặc dụng cụ kèm công thức chuẩn BXD, trả về từ điển tọa độ."""
    row_map = {}

    for idx, it in enumerate(items, 1):
        item_id = str(it.get('id', f"{prefix_type}_{idx:03d}")).strip()
        item_name = str(it.get('name', '')).strip()
        item_unit = "ca"

        matched = lookup_db.get(item_name.lower().strip(), {}) if lookup_db else {}
        orig_price = float(matched.get('msc_original_price') or it.get('original_price') or (50000000.0 if prefix_type == 'M' else 500000.0))
        tbmt = str(matched.get('msc_tbmt_code') or '')
        contractor = str(matched.get('msc_contractor') or '')
        appr_date = str(matched.get('msc_approval_date') or '')

        if tbmt:
            basis_text = f"TBMT: {tbmt} - {contractor} ({appr_date})"
        else:
            basis_text = "Thông tư 13/2021/TT-BXD"

        r = ws.max_row + 1

        # Đăng ký cả mã ID và tên vào row_map để tra cứu linh hoạt
        row_map[item_id] = r
        row_map[item_id.lower()] = r
        row_map[item_name.lower()] = r

        is_electric = item_name.lower().strip() in ['điện', 'điện năng'] or str(it.get('unit', '')).lower().strip() in ['kw', 'kwh']
        if is_electric:
            item_unit = "kWh"
            orig_price = 0.0
            nca_val = 1
            kh_val = 0.0
            sc_val = 0.0
            cpk_val = 0.0
            f_kh = 0
            f_sc = 0
            f_cpk = 0
            fuel_cost = 2100  # Đơn giá điện sản xuất EVN
            f_total = "=M" + str(r)
            basis_text = "QĐ 2699/QĐ-BCT giá điện bán lẻ EVN"
        else:
            item_unit = "ca"
            nca_val = default_nca
            kh_val = default_kh
            sc_val = default_sc
            cpk_val = default_cpk
            f_kh = f"=ROUND(E{r}*G{r}/100/F{r}, 0)"
            f_sc = f"=ROUND(E{r}*I{r}/100/F{r}, 0)"
            f_cpk = f"=ROUND(E{r}*K{r}/100/F{r}, 0)"
            fuel_cost = 0
            f_total = f"=H{r}+J{r}+L{r}+M{r}+N{r}"

        ws.append([
            idx,
            item_id,
            item_name,
            item_unit,
            orig_price,            # E: Nguyên giá tra cứu từ MSC
            nca_val,               # F: Số ca làm việc năm
            kh_val,                # G: Tỷ lệ Khấu hao %
            f_kh,                  # H: Chi phí Khấu hao
            sc_val,                # I: Tỷ lệ Sửa chữa %
            f_sc,                  # J: Chi phí Sửa chữa
            cpk_val,               # K: Tỷ lệ CP khác %
            f_cpk,                 # L: Chi phí khác
            fuel_cost,             # M: Chi phí Nhiên liệu/Năng lượng
            0,                     # N: Chi phí Nhân công điều khiển
            f_total,               # O: Đơn giá ca máy tổng cộng
            basis_text             # P: Căn cứ pháp lý & Cơ sở giá
        ])

        for c in range(1, 17):
            cell = ws.cell(r, c)
            cell.font = font_data_11r
            cell.border = border_cell
            if c in (1, 2, 4):
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif c in (3, 16):
                cell.alignment = Alignment(horizontal="left", vertical="center")
            elif c in (6, 7, 9, 11):
                cell.alignment = Alignment(horizontal="right", vertical="center")
                cell.number_format = "#,##0.0"
            elif c in (5, 8, 10, 12, 13, 14, 15):
                cell.alignment = Alignment(horizontal="right", vertical="center")
                cell.number_format = FMT_CURRENCY
                if c == 15:
                    cell.font = font_data_11b

    return row_map


def _apply_tinh_gia_ca_may_styling(
    ws: Worksheet,
    font_title_15b: Font,
    font_sub_11i: Font,
    font_header_11b: Font,
    fill_header_gray: PatternFill,
    border_cell: Border
):
    """Căn chỉnh độ rộng cột và format tiêu đề bảng tính giá ca máy."""
    ws.merge_cells("A1:P1")
    ws["A1"].font = font_title_15b
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")

    ws["A2"].font = font_sub_11i
    ws["A3"].font = font_sub_11i
    ws["A4"].font = font_sub_11i

    # Header dòng 6
    header_row = 6
    ws.row_dimensions[header_row].height = 28
    for c in range(1, 17):
        cell = ws.cell(header_row, c)
        cell.font = font_header_11b
        cell.fill = fill_header_gray
        cell.border = border_cell
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    col_widths = {
        'A': 8,   # STT
        'B': 14,  # Mã hiệu
        'C': 38,  # Tên loại máy/thiết bị
        'D': 10,  # ĐVT
        'E': 18,  # Nguyên giá
        'F': 14,  # Số ca năm
        'G': 14,  # Tỷ lệ KH
        'H': 18,  # Khấu hao/ca
        'I': 14,  # Tỷ lệ SC
        'J': 18,  # Sửa chữa/ca
        'K': 14,  # Tỷ lệ CPK
        'L': 18,  # CP khác/ca
        'M': 18,  # Nhiên liệu/ca
        'N': 18,  # Nhân công/ca
        'O': 22,  # ĐƠN GIÁ CA MÁY (VNĐ)
        'P': 42   # Căn cứ pháp lý & Cơ sở giá MSC
    }
    for col_letter, width in col_widths.items():
        ws.column_dimensions[col_letter].width = width

    ws.freeze_panes = "A7"


def build_tinh_gia_ca_may_sheet(
    wb: openpyxl.Workbook,
    jobs_dtos: List[Any],
    font_title_15b: Font,
    font_sub_11i: Font,
    font_header_11b: Font,
    font_data_11r: Font,
    font_data_11b: Font,
    fill_header_gray: PatternFill,
    border_cell: Border,
    border_total: Border,
    FMT_CURRENCY: str,
    root_dir: str = None
) -> Tuple[Worksheet, Dict[str, Dict[str, int]]]:
    """
    Hàm điều phối chính: Khởi tạo và ghi đầy đủ bảng tính giá ca máy & thiết bị theo chuẩn BXD.
    Trả về worksheet và từ điển ánh xạ tọa độ dòng:
    ca_may_rows = {
        'm_rows': {m_id: row, m_name_lower: row},
        'dc_rows': {dc_id: row, dc_name_lower: row}
    }
    """
    ws = _init_tinh_gia_ca_may_sheet(wb)
    _write_tinh_gia_ca_may_header(ws)

    # 1. Bóc tách danh mục duy nhất từ jobs_dtos
    m_items = _collect_may_items(jobs_dtos)
    dc_items = _collect_cong_cu_items(jobs_dtos)

    eq_lookup = {}
    tools_lookup = {}
    if root_dir:
        try:
            adapter = OneDriveAdapter(root_dir)
            eq_lookup = {it.get("name", "").lower().strip(): it for it in adapter.load_msc_equipment().get("items", [])}
            tools_lookup = {it.get("name", "").lower().strip(): it for it in adapter.load_msc_tools().get("items", [])}
        except Exception as e:
            print(f"Warning: could not load MSC lookup in tinh_gia_ca_may_exporter: {e}")

    font_sec_12b = Font(name="Times New Roman", size=12, bold=True)

    # 2. PHẦN I: MÁY VÀ THIẾT BỊ QUAN TRẮC (59 mục)
    _write_section_banner(ws, "I. BẢNG TÍNH ĐƠN GIÁ CA MÁY VÀ THIẾT BỊ QUAN TRẮC MÔI TRƯỜNG", font_sec_12b, fill_header_gray, border_cell)

    m_rows = _write_items_block(
        ws=ws,
        items=m_items,
        prefix_type="M",
        default_nca=250,
        default_kh=15.0,
        default_sc=5.0,
        default_cpk=3.0,
        border_cell=border_cell,
        font_data_11r=font_data_11r,
        font_data_11b=font_data_11b,
        FMT_CURRENCY=FMT_CURRENCY,
        lookup_db=eq_lookup
    )

    # Dòng trống ngăn cách
    ws.append([])

    # 3. PHẦN II: CÔNG CỤ DỤNG CỤ QUAN TRẮC (118 mục)
    _write_section_banner(ws, "II. BẢNG TÍNH ĐƠN GIÁ CA DỤNG CỤ QUAN TRẮC MÔI TRƯỜNG", font_sec_12b, fill_header_gray, border_cell)

    dc_rows = _write_items_block(
        ws=ws,
        items=dc_items,
        prefix_type="DC",
        default_nca=250,
        default_kh=20.0,
        default_sc=8.0,
        default_cpk=5.0,
        border_cell=border_cell,
        font_data_11r=font_data_11r,
        font_data_11b=font_data_11b,
        FMT_CURRENCY=FMT_CURRENCY,
        lookup_db=tools_lookup
    )

    # 4. Áp dụng định dạng và freeze panes
    _apply_tinh_gia_ca_may_styling(
        ws=ws,
        font_title_15b=font_title_15b,
        font_sub_11i=font_sub_11i,
        font_header_11b=font_header_11b,
        fill_header_gray=fill_header_gray,
        border_cell=border_cell
    )

    ca_may_rows = {
        "m_rows": m_rows,
        "dc_rows": dc_rows
    }

    return ws, ca_may_rows
