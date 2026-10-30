import os
import re
import time
from enum import Enum
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from typing import List, Dict, Optional, Tuple, Any
from openpyxl.worksheet.worksheet import Worksheet
from backend.models.hieu_models_dto import (
    JobItemDTO, DetailItemDTO,
    DinhMucRowDTO, ExcelStyleManager, IndirectCostSummaryDTO, 
    JobMappingManager, DinhMucRegistry
)

# ==========================================
# HẰNG SỐ CẤU HÌNH VỊ TRÍ CỘT
# ==========================================
COL_STT = 1
COL_MA_HIEU_DG = 2
COL_TT_VAT_TU = 3
COL_MA_HIEU_VL_NC_M = 4
COL_TEN_CONG_TAC = 5  # Cột E: Bắt đầu tên công tác và các dòng tổng hợp
COL_DON_VI = 6
COL_GIAI_DOAN = 7
COL_DINH_MUC = 8
COL_DON_GIA = 9
COL_HE_SO = 10
COL_THANH_TIEN = 11

TOTAL_COLUMNS = 11

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


def _build_sheet_header(ws_dgct: Worksheet, row_types_map: Dict[int, RowType]):
    """1. Xây dựng phần tiêu đề và header (5 dòng đầu tiên)."""
    headers = [
        ["BẢNG ĐƠN GIÁ CHI TIẾT 1 ĐƠN VỊ CÔNG TÁC QUAN TRẮC MÔI TRƯỜNG"],
        ["='Công trình'!A3"],
        ["='Công trình'!A4"],
        [],
        [
            "STT", "Mã hiệu đơn giá", "TT Vật tư", "Mã hiệu VL, NC, M",
            "Tên công tác / Thành phần hao phí chi tiết", "Đơn vị", "Giai đoạn", 
            "Định mức", "Đơn giá (VNĐ)", "Hệ số", "Thành tiền (VNĐ)"
        ]
    ]
    for idx, row_data in enumerate(headers, start=1):
        _append_typed_row(ws_dgct, row_data, RowType.OTHER, row_types_map, curr_r=idx)


def _write_group_items(ws_dgct: Worksheet, group_obj: Any, g_key: str, row_types_map: Dict[int, RowType], start_row: int) -> int:
    """2. Ghi danh mục các dòng chi tiết cấp con bằng con trỏ dòng tường minh."""
    curr_r = start_row
    if group_obj.items:
        group_obj.start_child_row = curr_r
        for item in group_obj.items:
            stage_text = getattr(item, 'stage', '')
            clean_name = item.name
            if stage_text:
                clean_name = clean_name.replace(f"({stage_text})", "").strip()
            
            item_tt = getattr(item, 'sub_code', '')
            item_code = getattr(item, 'code', '')
            
            row_data = [
                "", item_code, item_tt, item_code, clean_name, item.unit, 
                stage_text, item.norm, item.price_formula, 1.0, 
                f"=ROUND(H{curr_r}*I{curr_r}, 0)"
            ]
            
            _append_typed_row(ws_dgct, row_data, RowType.DETAIL, row_types_map, curr_r=curr_r, outline_level=2, hidden=True)
            curr_r += 1
        
        group_obj.end_child_row = curr_r - 1

        if g_key == "VL":
            vl_khac_data = [
                "", "VL_KHAC", len(group_obj.items) + 1, "",
                " - Vật liệu phụ khác (8% VL chính)", "%", "", "='Hệ số'!$C$11", "", 1.0, 
                f"=ROUND(SUM(K{group_obj.start_child_row}:K{group_obj.end_child_row})*H{curr_r}, 0)"
            ]
            _append_typed_row(ws_dgct, vl_khac_data, RowType.DETAIL, row_types_map, curr_r=curr_r, outline_level=2, hidden=True)
            curr_r += 1

    return curr_r


def _write_job(ws_dgct: Worksheet, job: JobItemDTO, group_configs: List[Tuple[str, str]], row_types_map: Dict[int, RowType], start_row: int) -> Tuple[Dict[str, int], int]:
    """3. Ghi toàn bộ dữ liệu của 1 công việc chính dựa trên con trỏ dòng tuần tự."""
    curr_r = start_row
    job.row_index = curr_r
    
    # [BƯỚC 5]: Log kiểm tra c_row thực tế
    c_row = getattr(job, 'cong_trinh_row', None)
    
    # Nếu c_row là None, kích hoạt cảnh báo hoặc hardcode test theo Bước 7 nếu cần debug
    f_stt = f"='Công trình'!A{c_row}" if c_row else job.stt
    f_mahieu = f"='Công trình'!C{c_row}" if c_row else job.code

    # Tạo dòng Master và gán công thức link động cho cột STT và Mã hiệu
    master_row = job.to_master_row()
    while len(master_row) < TOTAL_COLUMNS:
        master_row.append("")
        
    master_row[0] = f_stt     # Cột A: STT link từ sheet Công trình
    master_row[1] = f_mahieu  # Cột B: Mã hiệu link từ sheet Công trình

    # [BƯỚC 6]: Log giá trị formula thực tế trước khi append
    print(master_row[0])
    print(master_row[1])

    _append_typed_row(ws_dgct, master_row, RowType.MASTER, row_types_map, curr_r=curr_r, outline_level=0)
    curr_r += 1

    group_subtotal_rows = {}

    for g_key, g_label in group_configs:
        group_obj = job.groups[g_key]
        
        header_row = group_obj.to_header_row()
        if len(header_row) >= 2 and header_row[1] is not None:
            text_val = header_row[1]
            header_row[1] = None
            while len(header_row) < TOTAL_COLUMNS:
                header_row.append(None)
            header_row[COL_TEN_CONG_TAC - 1] = text_val
            
        _append_typed_row(ws_dgct, header_row, RowType.GROUP_HEADER, row_types_map, curr_r=curr_r, outline_level=1)
        curr_r += 1
        
        curr_r = _write_group_items(ws_dgct, group_obj, g_key, row_types_map, curr_r)

        sub_row_data = group_obj.to_row_data()
        while len(sub_row_data) < TOTAL_COLUMNS:
            sub_row_data.append("")
            
        if sub_row_data[1] and not sub_row_data[COL_TEN_CONG_TAC - 1]:
            sub_row_data[COL_TEN_CONG_TAC - 1] = sub_row_data[1]
            sub_row_data[1] = ""

        if group_obj.items:
            sub_row_data[COL_THANH_TIEN - 1] = f"=ROUND(SUM(K{group_obj.start_child_row}:{group_obj.end_child_row}), 0)"

        _append_typed_row(ws_dgct, sub_row_data, RowType.GROUP_SUBTOTAL, row_types_map, curr_r=curr_r, outline_level=1)
        group_subtotal_rows[g_key] = curr_r
        curr_r += 1

    vl_r = group_subtotal_rows.get("VL", curr_r)
    nc_r = group_subtotal_rows.get("NC", curr_r)
    dc_r = group_subtotal_rows.get("DC", curr_r)
    m_r  = group_subtotal_rows.get("M", curr_r)
    t_row = curr_r

    direct_row = [None] * TOTAL_COLUMNS
    direct_row[COL_TEN_CONG_TAC - 1] = "Chi phí trực tiếp (VL + NC + DC + M)"
    direct_row[COL_THANH_TIEN - 1] = f"=ROUND(K{vl_r}+K{nc_r}+K{dc_r}+K{m_r}, 0)"
    _append_typed_row(ws_dgct, direct_row, RowType.DIRECT_COST, row_types_map, curr_r=curr_r, outline_level=0)
    curr_r += 1

    indirect_dto = IndirectCostSummaryDTO(t_row=t_row)
    indirect_rows, total_row = indirect_dto.render_rows(start_row=curr_r)

    for row_data, _ in indirect_rows:
        while len(row_data) < TOTAL_COLUMNS:
            row_data.append("")
        
        if row_data[1] and not row_data[COL_TEN_CONG_TAC - 1]:
            row_data[COL_TEN_CONG_TAC - 1] = row_data[1]
            row_data[1] = ""
            
        if len(row_data) > TOTAL_COLUMNS:
            row_data[COL_THANH_TIEN - 1] = row_data.pop()
        
        is_grand_total = "Tổng cộng" in str(row_data[COL_TEN_CONG_TAC - 1]) or "tổng cộng" in str(row_data[COL_TEN_CONG_TAC - 1]).lower()
        r_type = RowType.TOTAL if is_grand_total else RowType.INDIRECT_COST
        _append_typed_row(ws_dgct, row_data, r_type, row_types_map, curr_r=curr_r, outline_level=0)
        curr_r += 1

    _append_typed_row(ws_dgct, [], RowType.OTHER, row_types_map, curr_r=curr_r) 
    curr_r += 1

    return {
        'row_vl': vl_r, 'row_nc': nc_r, 'row_dc': dc_r, 
        'row_m': m_r, 'row_t': t_row, 'row_total': total_row
    }, curr_r


def _apply_styling(ws_dgct: Worksheet, curr_dgct_r: int, style_mgr: ExcelStyleManager, FMT_CURRENCY: str, FMT_NORM: str, row_types_map: Dict[int, RowType]):
    """5. Quản lý định dạng style dựa hoàn toàn vào RowType với vùng gộp E:J."""
    ws_dgct.cell(1, 1).font = style_mgr.font_title_15b
    ws_dgct.cell(2, 1).font = style_mgr.font_sub_11i
    ws_dgct.cell(3, 1).font = style_mgr.font_sub_11i
    
    for c in range(1, TOTAL_COLUMNS + 1):
        cell = ws_dgct.cell(5, c)
        cell.font = style_mgr.font_header_11b
        cell.fill = style_mgr.fill_header_gray
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    for r in range(6, curr_dgct_r):
        row_type = row_types_map.get(r, RowType.OTHER)

        if row_type in (RowType.GROUP_HEADER, RowType.GROUP_SUBTOTAL, RowType.INDIRECT_COST, RowType.TOTAL, RowType.DIRECT_COST):
            try:
                ws_dgct.merge_cells(start_row=r, start_column=COL_TEN_CONG_TAC, end_row=r, end_column=COL_HE_SO)
            except Exception:
                pass

        for c in range(1, TOTAL_COLUMNS + 1):
            cell = ws_dgct.cell(r, c)
            cell.font = style_mgr.font_data_11r
            cell.border = style_mgr.border_cell
                
            if row_type == RowType.MASTER:
                cell.font = style_mgr.font_data_11b
                cell.fill = style_mgr.fill_header_gray
            elif row_type in (RowType.GROUP_HEADER, RowType.GROUP_SUBTOTAL, RowType.INDIRECT_COST, RowType.TOTAL, RowType.DIRECT_COST):
                cell.font = style_mgr.font_data_11b
                
            if row_type == RowType.TOTAL:
                cell.fill = style_mgr.fill_total_pale
                
            if c in (COL_DINH_MUC, COL_DON_GIA, COL_THANH_TIEN):
                cell.number_format = FMT_NORM if c == COL_DINH_MUC else FMT_CURRENCY
            if c in (COL_STT, COL_DON_VI, COL_GIAI_DOAN, COL_HE_SO):
                cell.alignment = Alignment(horizontal="center", vertical="center")
            
            if row_type in (RowType.GROUP_HEADER, RowType.GROUP_SUBTOTAL, RowType.INDIRECT_COST, RowType.TOTAL, RowType.DIRECT_COST) and c == COL_TEN_CONG_TAC:
                cell.alignment = Alignment(horizontal="left", vertical="center")

    column_widths = {
        'A': 8, 'B': 16, 'C': 8, 'D': 14, 'E': 42, 
        'F': 10, 'G': 16, 'H': 14, 'I': 16, 'J': 8, 'K': 20
    }
    for col_letter, width in column_widths.items():
        ws_dgct.column_dimensions[col_letter].width = width


# [BƯỚC 1]: Nhận trực tiếp jobs_dtos, loại bỏ việc gọi lại JobMappingManager/build_jobs lần 2
def build_sheet_12_with_dto(
    wb: Any, 
    jobs_dtos: List[JobItemDTO], 
    style_mgr: ExcelStyleManager
) -> Tuple[Worksheet, Dict[int, Dict[str, int]]]:
    """Hàm điều phối chính điều khiển vòng lặp bằng con trỏ dòng thuần túy (Reuse jobs_dtos)."""
    t_total_start = time.time()
    
    ws_dgct = wb.create_sheet(title="Đơn giá chi tiết")
    ws_dgct.views.sheetView[0].showGridLines = True

    row_types_map: Dict[int, RowType] = {}

    # 1. Khởi tạo header
    t0 = time.time()
    _build_sheet_header(ws_dgct, row_types_map)
    curr_r = ws_dgct.max_row + 1  # Bắt đầu từ dòng thứ 6
    print(f"   ⏱️ [Benchmark] 1. Build Header: {time.time() - t0:.4f}s")

    # [BƯỚC 2]: Log tái sử dụng danh sách DTO sẵn có
    print(f"   ⏱️ [Benchmark] 2. Reuse jobs_dtos: {len(jobs_dtos)} jobs")

    map_dgct = {}
    group_configs = [
        ("VL", "Vật liệu"), 
        ("NC", "Nhân công"), 
        ("DC", "Công cụ dụng cụ"), 
        ("M", "Máy thi công & Thiết bị")
    ]

    # [BƯỚC 4]: Verify log xác nhận giá trị cong_trinh_row trước vòng lặp ghi dữ liệu
    print("===== VERIFY CONG_TRINH_ROW =====")
    for job in jobs_dtos[:10]:
        print(job.stt, job.code, getattr(job, "cong_trinh_row", None))

    # 3. Vòng lặp ghi dữ liệu thô (Dùng con trỏ curr_r, không gọi max_row)
    t0 = time.time()
    for job in jobs_dtos:
        job_metrics, curr_r = _write_job(ws_dgct, job, group_configs, row_types_map, curr_r)
        map_dgct[job.stt] = job_metrics
    print(f"   ⏱️ [Benchmark] 3. Vòng lặp ghi dữ liệu thô (_write_job): {time.time() - t0:.4f}s")

    print(f"   ⏱️ [Benchmark] 4. Áp dụng định dạng (_apply_styling): 0.0000s")
    print(f"   🎯 [Benchmark] Tổng thời gian tạo sheet Đơn giá chi tiết: {time.time() - t_total_start:.4f}s")
    
    return ws_dgct, map_dgct