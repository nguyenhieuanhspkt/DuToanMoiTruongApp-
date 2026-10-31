import os
import re
import time
from enum import Enum
from typing import List, Dict, Optional, Tuple, Any
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.worksheet import Worksheet
from backend.models.hieu_models_dto import (
    JobItemDTO, DetailItemDTO,
    DinhMucRowDTO, ExcelStyleManager, IndirectCostSummaryDTO, 
    JobMappingManager, DinhMucRegistry
)

# ==========================================
# HẰNG SỐ CẤU HÌNH VỊ TRÍ CỘT (CHUẨN 10 CỘT F1)
# ==========================================
COL_STT = 1             # Cột A: STT (link ='Công trình'!A...)
COL_MA_HIEU_DG = 2      # Cột B: Mã hiệu đơn giá (link ='Công trình'!C...)
COL_TT_VAT_TU = 3       # Cột C: TT Vật tư (1, 2, 3...)
COL_MA_HIEU_VL_NC_M = 4 # Cột D: Mã hiệu VL, NC, M
COL_TEN_CONG_TAC = 5    # Cột E: Tên công tác / Thành phần hao phí chi tiết
COL_DON_VI = 6          # Cột F: Đơn vị / Ký hiệu chi phí
COL_DINH_MUC = 7        # Cột G: Định mức / Tỷ lệ %
COL_DON_GIA = 8         # Cột H: Đơn giá (VNĐ)
COL_HE_SO = 9           # Cột I: Hệ số (1.000)
COL_THANH_TIEN = 10     # Cột J: Thành tiền (VNĐ)

TOTAL_COLUMNS = 10

class RowType(Enum):
    MASTER = 1
    GROUP_HEADER = 2
    DETAIL = 3
    GROUP_SUBTOTAL = 4
    DIRECT_COST = 5
    INDIRECT_COST = 6
    TOTAL = 7
    OTHER = 8


def _parse_name_and_stage(raw_name: str) -> Tuple[str, str]:
    """Tách tên vật tư/hao phí sạch và phần giai đoạn (Ngoại nghiệp / Nội nghiệp)."""
    match = re.search(r'\((Ngoại nghiệp|Nội nghiệp)\)\s*$', raw_name, re.IGNORECASE)
    if match:
        stage = match.group(1)
        clean_name = raw_name[:match.start()].strip()
        return clean_name, stage
    return raw_name, ""


def _append_typed_row(
    ws_dgct: Worksheet, 
    row_data: list, 
    row_type: RowType, 
    row_types_map: Dict[int, RowType],
    curr_r: int,
    outline_level: int = 0, 
    hidden: bool = False
) -> None:
    """Helper tối ưu hiệu năng: Sử dụng trực tiếp curr_r, không gọi max_row bên trong."""
    ws_dgct.append(row_data)
    row_types_map[curr_r] = row_type
    
    if outline_level > 0:
        ws_dgct.row_dimensions[curr_r].outlineLevel = outline_level
    if hidden:
        ws_dgct.row_dimensions[curr_r].hidden = True


def _build_sheet_header(ws_dgct: Worksheet, row_types_map: Dict[int, RowType]) -> None:
    """1. Xây dựng phần tiêu đề và header (5 dòng đầu tiên chuẩn 10 cột)."""
    headers = [
        ["BẢNG ĐƠN GIÁ CHI TIẾT 1 ĐƠN VỊ CÔNG TÁC QUAN TRẮC MÔI TRƯỜNG"],
        ["='Công trình'!A3"],
        ["='Công trình'!A4"],
        [],
        [
            "STT", "Mã hiệu đơn giá", "TT Vật tư", "Mã hiệu VL, NC, M",
            "Tên công tác / Thành phần hao phí chi tiết", "Đơn vị", 
            "Định mức", "Đơn giá (VNĐ)", "Hệ số", "Thành tiền (VNĐ)"
        ]
    ]
    for idx, row_data in enumerate(headers, start=1):
        _append_typed_row(ws_dgct, row_data, RowType.OTHER, row_types_map, curr_r=idx)


def _write_master_row(
    ws_dgct: Worksheet, 
    job: JobItemDTO, 
    row_types_map: Dict[int, RowType], 
    curr_r: int
) -> int:
    """2. Ghi dòng tiêu đề công việc chính (Master row) link động sang sheet Công trình."""
    job.row_index = curr_r
    c_row = getattr(job, 'cong_trinh_row', None)
    f_stt = f"='Công trình'!A{c_row}" if c_row else job.stt
    f_mahieu = f"='Công trình'!C{c_row}" if c_row else job.code

    master_row = [
        f_stt, f_mahieu, "", "", job.name, job.unit, "", "", "", ""
    ]
    _append_typed_row(ws_dgct, master_row, RowType.MASTER, row_types_map, curr_r=curr_r, outline_level=0)
    return curr_r + 1


def _write_group_items(
    ws_dgct: Worksheet, 
    group_obj: Any, 
    g_key: str, 
    row_types_map: Dict[int, RowType], 
    start_row: int
) -> Tuple[int, int, int]:
    """3. Ghi danh mục các dòng chi tiết cấp con và vật liệu phụ khác (nếu có)."""
    curr_r = start_row
    child_start = curr_r
    
    for sub_idx, item in enumerate(group_obj.items, start=1):
        clean_name, stage = _parse_name_and_stage(item.name)
        display_name = f" - {clean_name}" + (f" ({stage})" if stage else "")
        
        item_tt = getattr(item, 'sub_code', '') or str(sub_idx)
        item_code = getattr(item, 'code', '')
        
        # Lấy tọa độ dòng bên sheet 'Hao phí VT' đã được gán trước đó
        hp_row = getattr(item, 'hp_row', None)
        
        # Nếu có hp_row, cột Định mức (G) sẽ link động sang Hao phí VT
        # Tùy theo nhóm (VL, NC, DC, M) mà cột mức hao phí bên sheet Hao phí VT nằm ở cột H, I, J hoặc K:
        # - Vật liệu (VL): Cột H
        # - Nhân công (NC): Cột I
        # - Công cụ dụng cụ (DC): Cột J
        # - Máy thi công (M): Cột K
        if hp_row:
            if g_key == "VL":
                f_norm = f"='Hao phí VT'!H{hp_row}"
            elif g_key == "NC":
                f_norm = f"='Hao phí VT'!I{hp_row}"
            elif g_key == "DC":
                f_norm = f"='Hao phí VT'!J{hp_row}"
            elif g_key == "M":
                f_norm = f"='Hao phí VT'!K{hp_row}"
            else:
                f_norm = item.norm
        else:
            f_norm = item.norm

        row_data = [
            "", "", item_tt, item_code, display_name, item.unit, 
            f_norm, item.price_formula, 1.0, 
            f"=ROUND(G{curr_r}*H{curr_r}*I{curr_r}, 0)"
        ]
        _append_typed_row(ws_dgct, row_data, RowType.DETAIL, row_types_map, curr_r=curr_r, outline_level=2, hidden=False)
        curr_r += 1
    
    # Đối với Vật liệu (VL): Thêm dòng vật liệu phụ khác
    if g_key == "VL":
        vl_khac_tt = len(group_obj.items) + 1
        items_end_r = curr_r - 1
        vl_khac_data = [
            "", "", vl_khac_tt, "VL_KHAC", 
            " - Vật liệu phụ khác (8% VL chính)", "%", 
            "='Hệ số'!$C$11", "", 1.0, 
            f"=ROUND(SUM(J{child_start}:J{items_end_r})*G{curr_r}, 0)"
        ]
        _append_typed_row(ws_dgct, vl_khac_data, RowType.DETAIL, row_types_map, curr_r=curr_r, outline_level=2, hidden=False)
        curr_r += 1

    child_end = curr_r - 1
    return child_start, child_end, curr_r


def _write_single_group(
    ws_dgct: Worksheet, 
    group_obj: Any, 
    g_key: str, 
    g_label: str, 
    row_types_map: Dict[int, RowType], 
    curr_r: int
) -> Tuple[Optional[int], int]:
    """4. Ghi 1 nhóm hao phí (VL, NC, DC, M): Bỏ qua nếu nhóm không có dữ liệu."""
    if not group_obj or not group_obj.items:
        return None, curr_r

    group_row = curr_r
    # Dòng tiêu đề nhóm có công thức tổng ở cột J: =ROUND(SUM(J{child_start}:J{child_end}), 0)
    header_row = ["", "", "", "", g_label, "", "", "", "", ""]
    _append_typed_row(ws_dgct, header_row, RowType.GROUP_HEADER, row_types_map, curr_r=curr_r, outline_level=1)
    curr_r += 1

    child_start, child_end, curr_r = _write_group_items(ws_dgct, group_obj, g_key, row_types_map, curr_r)

    # Cập nhật công thức tổng của nhóm vào dòng header
    ws_dgct.cell(group_row, COL_THANH_TIEN).value = f"=ROUND(SUM(J{child_start}:J{child_end}), 0)"

    return group_row, curr_r


def _write_direct_cost_row(
    ws_dgct: Worksheet, 
    group_subtotal_rows: Dict[str, int], 
    row_types_map: Dict[int, RowType], 
    curr_r: int
) -> Tuple[int, int]:
    """5. Ghi dòng Chi phí trực tiếp T = SUM các nhóm hao phí hiện có."""
    t_row = curr_r
    active_rows = [group_subtotal_rows[k] for k in ["VL", "NC", "DC", "M"] if k in group_subtotal_rows]
    
    if active_rows:
        f_direct = f"=ROUND({'+'.join([f'J{r}' for r in active_rows])}, 0)"
    else:
        f_direct = 0

    direct_row = ["", "", "", "", "Chi phí trực tiếp (VL + NC + M)", "T", "", "", "", f_direct]
    _append_typed_row(ws_dgct, direct_row, RowType.DIRECT_COST, row_types_map, curr_r=curr_r, outline_level=0)
    return t_row, curr_r + 1


def _write_indirect_cost_rows(
    ws_dgct: Worksheet, 
    t_row: int, 
    row_types_map: Dict[int, RowType], 
    curr_r: int
) -> Tuple[int, int]:
    """6. Ghi khối chi phí gián tiếp, VAT, và tổng giá dự thầu 1 mẫu."""
    indirect_dto = IndirectCostSummaryDTO(t_row=t_row)
    indirect_rows, total_row = indirect_dto.render_rows(start_row=curr_r)

    for row_data, r_idx in indirect_rows:
        is_grand_total = (r_idx == total_row)
        r_type = RowType.TOTAL if is_grand_total else RowType.INDIRECT_COST
        _append_typed_row(ws_dgct, row_data, r_type, row_types_map, curr_r=curr_r, outline_level=0)
        curr_r += 1

    # Dòng trống phân cách giữa các công tác
    _append_typed_row(ws_dgct, [""] * TOTAL_COLUMNS, RowType.OTHER, row_types_map, curr_r=curr_r)
    curr_r += 1

    return total_row, curr_r


def _write_job(
    ws_dgct: Worksheet, 
    job: JobItemDTO, 
    group_configs: List[Tuple[str, str]], 
    row_types_map: Dict[int, RowType], 
    start_row: int
) -> Tuple[Dict[str, Any], int]:
    """7. Điều phối ghi toàn bộ thông tin của 1 công việc quan trắc."""
    curr_r = _write_master_row(ws_dgct, job, row_types_map, start_row)

    group_subtotal_rows: Dict[str, int] = {}
    for g_key, g_label in group_configs:
        group_obj = job.groups.get(g_key)
        g_row, curr_r = _write_single_group(ws_dgct, group_obj, g_key, g_label, row_types_map, curr_r)
        if g_row is not None:
            group_subtotal_rows[g_key] = g_row

    t_row, curr_r = _write_direct_cost_row(ws_dgct, group_subtotal_rows, row_types_map, curr_r)
    total_row, curr_r = _write_indirect_cost_rows(ws_dgct, t_row, row_types_map, curr_r)

    metrics = {
        'row_vl': group_subtotal_rows.get('VL'),
        'row_nc': group_subtotal_rows.get('NC'),
        'row_dc': group_subtotal_rows.get('DC'),
        'row_m':  group_subtotal_rows.get('M'),
        'row_t':  t_row,
        'row_total': total_row
    }
    return metrics, curr_r


def _apply_styling(
    ws_dgct: Worksheet, 
    curr_dgct_r: int, 
    style_mgr: ExcelStyleManager, 
    FMT_CURRENCY: str, 
    FMT_NORM: str, 
    row_types_map: Dict[int, RowType]
) -> None:
    """8. Quản lý định dạng style dựa trên RowType chuẩn 10 cột."""
    ws_dgct.cell(1, 1).font = style_mgr.font_title_15b
    ws_dgct.cell(2, 1).font = style_mgr.font_sub_11i
    ws_dgct.cell(3, 1).font = style_mgr.font_sub_11i
    
    for c in range(1, TOTAL_COLUMNS + 1):
        cell = ws_dgct.cell(5, c)
        cell.font = style_mgr.font_header_11b
        cell.fill = style_mgr.fill_header_gray
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    font_blue_bold = Font(size=11, bold=True, color="002060")
    fill_master = PatternFill("solid", fgColor="F2F2F2")

    for r in range(6, curr_dgct_r):
        row_type = row_types_map.get(r, RowType.OTHER)
        if row_type == RowType.OTHER:
            continue

        for c in range(1, TOTAL_COLUMNS + 1):
            cell = ws_dgct.cell(r, c)
            cell.font = style_mgr.font_data_11r
            cell.border = style_mgr.border_cell

            # Định dạng theo loại dòng
            if row_type == RowType.MASTER:
                cell.font = style_mgr.font_data_11b
                cell.fill = fill_master
            elif row_type == RowType.GROUP_HEADER:
                cell.font = font_blue_bold
            elif row_type in (RowType.DIRECT_COST, RowType.INDIRECT_COST):
                if c == COL_TEN_CONG_TAC and any(kw in str(cell.value) for kw in ["trực tiếp", "trước thuế", "SAU THUẾ"]):
                    cell.font = style_mgr.font_data_11b
            elif row_type == RowType.TOTAL:
                cell.font = style_mgr.font_data_11b
                cell.fill = style_mgr.fill_total_pale

            # Định dạng số và căn lề
            if c in (COL_STT, COL_MA_HIEU_DG, COL_TT_VAT_TU, COL_MA_HIEU_VL_NC_M, COL_DON_VI, COL_HE_SO):
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif c == COL_TEN_CONG_TAC:
                cell.alignment = Alignment(horizontal="left", vertical="center")
            elif c in (COL_DINH_MUC, COL_DON_GIA, COL_THANH_TIEN):
                cell.alignment = Alignment(horizontal="right", vertical="center")

            if c == COL_DINH_MUC:
                val_str = str(cell.value or '')
                if '%' in val_str or 'Hệ số' in val_str:
                    cell.number_format = '0.0%'
                else:
                    cell.number_format = FMT_NORM
            elif c in (COL_DON_GIA, COL_THANH_TIEN):
                cell.number_format = FMT_CURRENCY

    column_widths = {
        'A': 8, 'B': 16, 'C': 10, 'D': 16, 'E': 52, 
        'F': 10, 'G': 14, 'H': 16, 'I': 10, 'J': 18
    }
    for col_letter, width in column_widths.items():
        ws_dgct.column_dimensions[col_letter].width = width


def build_sheet_12_with_dto(
    wb: Any, 
    jobs_dtos: List[JobItemDTO], 
    style_mgr: ExcelStyleManager
) -> Tuple[Worksheet, Dict[Any, Dict[str, Any]]]:
    """Hàm điều phối chính xây dựng sheet 'Đơn giá chi tiết'."""
    t_total_start = time.time()
    
    if "Đơn giá chi tiết" in wb.sheetnames:
        ws_dgct = wb["Đơn giá chi tiết"]
        wb.remove(ws_dgct)

    ws_dgct = wb.create_sheet(title="Đơn giá chi tiết")
    ws_dgct.views.sheetView[0].showGridLines = True

    row_types_map: Dict[int, RowType] = {}

    # 1. Khởi tạo header
    _build_sheet_header(ws_dgct, row_types_map)
    curr_r = ws_dgct.max_row + 1  # Bắt đầu từ dòng thứ 6

    map_dgct: Dict[Any, Dict[str, Any]] = {}
    group_configs = [
        ("VL", "Vật liệu"), 
        ("NC", "Nhân công"), 
        ("DC", "Công cụ dụng cụ"), 
        ("M", "Máy thi công")
    ]

    # 2. Vòng lặp ghi dữ liệu từng công tác
    t0 = time.time()
    for idx, job in enumerate(jobs_dtos, start=1):
        job_metrics, curr_r = _write_job(ws_dgct, job, group_configs, row_types_map, curr_r)
        map_dgct[idx] = job_metrics
        map_dgct[str(idx)] = job_metrics
        map_dgct[job.stt] = job_metrics

    print(f"   ⏱️ [Benchmark] Ghi dữ liệu Đơn giá chi tiết: {time.time() - t0:.4f}s ({len(jobs_dtos)} jobs)")

    # 3. Áp dụng định dạng style
    t0 = time.time()
    _apply_styling(ws_dgct, curr_r, style_mgr, style_mgr.FMT_CURRENCY, style_mgr.FMT_NORM, row_types_map)
    print(f"   ⏱️ [Benchmark] Áp dụng định dạng: {time.time() - t0:.4f}s")
    print(f"   🎯 [Benchmark] Tổng thời gian hoàn thành sheet Đơn giá chi tiết: {time.time() - t_total_start:.4f}s")
    
    return ws_dgct, map_dgct
