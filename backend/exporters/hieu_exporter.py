import sys, os, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import openpyxl
from backend.models.hieu_models_dto import (
    ExcelStyleManager, JobMappingManager, DinhMucRegistry
)
from backend.models.project_context import ProjectContext

# Import các module con chuyên trách từng sheet
from backend.exporters.cong_trinh_exporter import build_cong_trinh_sheet, update_cong_trinh_from_dgct
from backend.exporters.dinh_muc_exporter import build_dinh_muc_sheet
from backend.exporters.don_gia_ct_exporter import build_sheet_12_with_dto
from backend.exporters.hao_phi_vt_exporter import build_hao_phi_vt_sheet
from backend.exporters.vat_lieu_exporter import build_vat_lieu_sheet
from backend.exporters.nhan_cong_exporter import build_nhan_cong_sheet
from backend.exporters.cong_cu_exporter import build_cong_cu_sheet
from backend.exporters.may_thi_cong_exporter import build_may_thi_cong_sheet
from backend.exporters.he_so_exporter import build_he_so_sheet
from backend.exporters.khoan_4_5_tt20_exporter import build_khoan_4_5_tt20_sheet
from backend.exporters.thdt_hang_muc_exporter import build_thdt_hang_muc_sheet
from backend.exporters.luong_nhan_cong_exporter import build_luong_nhan_cong_sheet
from backend.exporters.tinh_gia_ca_may_exporter import build_tinh_gia_ca_may_sheet

def _reorder_sheets_tab(wb, desired_order: list) -> None:
    """Sắp xếp lại thứ tự các sheet theo chuẩn Executive Summary First."""
    sheet_map = {ws.title: ws for ws in wb.worksheets}
    new_sheets = [sheet_map[title] for title in desired_order if title in sheet_map]
    for ws in wb.worksheets:
        if ws not in new_sheets:
            new_sheets.append(ws)
    wb._sheets = new_sheets


def _apply_all_freeze_panes(wb) -> None:
    """Cấu hình freeze_panes phù hợp cho toàn bộ các sheet."""
    freeze_map = {
        "THDT hạng mục": "A6",
        "Khoản 4.5 TT20": "A7",
        "Công trình": "A7",
        "Đơn giá chi tiết": "A6",
        "Hao phí VT": "H7",
        "Nhân công": "A7",
        "Tính lương NC": "A6",
        "Vật liệu": "A7",
        "Công cụ dụng cụ": "A7",
        "Máy thi công": "A7",
        "Tính giá ca máy": "A7",
        "Dữ liệu định mức": "A2",
        "Hệ số": "A6",
    }
    for sname, fp in freeze_map.items():
        if sname in wb.sheetnames:
            wb[sname].freeze_panes = fp


def export_full_du_toan(
    root_dir: str, 
    pakt_items: list, 
    mat_items: list, 
    tools_items: list, 
    equip_items: list
):
    """
    Hàm điều phối trung tâm (Main Orchestrator): 
    Đưa sheet Công trình lên trước tiên theo đúng logic trực quan của bảng F1.
    """
    wb = openpyxl.Workbook()
    # 🧹 Xóa bỏ sheet mặc định ("Sheet") do openpyxl tự động tạo ra
    if "Sheet" in wb.sheetnames:
        wb.remove(wb["Sheet"])
    style_mgr = ExcelStyleManager()
    ctx = ProjectContext() # ⭐ Trung tâm quản lý tọa độ dòng liên sheet
    
    FMT_CURRENCY = style_mgr.FMT_CURRENCY
    FMT_NORM = style_mgr.FMT_NORM

    # 1. Xây dựng sheet 'Dữ liệu định mức' & đăng ký Unique ID trước
    print("[1] Đang xây dựng sheet Dữ liệu định mức...")
    DATA_DIR = os.path.join(root_dir, 'backend', 'data', 'tt20_sections')
    row_map, registry = build_dinh_muc_sheet(wb, DATA_DIR)

    # 2. Khởi tạo JobMappingManager và bóc tách danh sách jobs_dtos
    print("[2] Đang khởi tạo JobMappingManager...")
    job_mapper = JobMappingManager(
        mat_items=mat_items, 
        tools_items=tools_items, 
        equip_items=equip_items, 
        dinh_muc_registry=registry
    )
    jobs_dtos = job_mapper.build_jobs(pakt_items)

    # 3. Build sheet Công trình trước
    print("[3] Đang xây dựng sheet Công trình...")
    ws_ct, item_ct_rows, tot_ct_row = build_cong_trinh_sheet(
        wb=wb,
        pakt_items=pakt_items,
        map_dgct={},
        font_title_15b=style_mgr.font_title_15b,
        font_sub_11i=style_mgr.font_sub_11i,
        font_header_11b=style_mgr.font_header_11b,
        font_sec_12b=style_mgr.font_sec_12b,
        font_data_11r=style_mgr.font_data_11r,
        font_data_11b=style_mgr.font_data_11b,
        fill_header_gray=style_mgr.fill_header_gray,
        fill_sub_gray=style_mgr.fill_sub_gray,
        fill_total_pale=style_mgr.fill_total_pale,
        border_cell=style_mgr.border_cell,
        border_total=style_mgr.border_total,
        FMT_CURRENCY=style_mgr.FMT_CURRENCY
    )
    ctx.register_cong_trinh(item_ct_rows, tot_ct_row)

    # Gán lại row thực tế từ sheet Công trình
    for idx, job in enumerate(jobs_dtos, start=1):
        row = item_ct_rows.get(idx)
        job.cong_trinh_row = row

    # 4. Xây dựng sheet 'Hao phí VT'
    print("[4] Đang xây dựng sheet Hao phí VT...")
    ws_hp, last_hp_row = build_hao_phi_vt_sheet(
        wb=wb,
        pakt_items=pakt_items,
        start_ct_row=7,
        job_mapper=job_mapper,
        font_title_15b=style_mgr.font_title_15b,
        font_sub_11i=style_mgr.font_sub_11i,
        font_header_11b=style_mgr.font_header_11b,
        font_data_11r=style_mgr.font_data_11r,
        font_data_11b=style_mgr.font_data_11b,
        fill_header_gray=style_mgr.fill_header_gray,
        border_cell=style_mgr.border_cell,
        FMT_NORM=style_mgr.FMT_NORM,
        jobs_dtos=jobs_dtos,
        item_ct_rows=item_ct_rows
    )
    ctx.register_hao_phi(last_hp_row)

    # 5. Xây dựng sheet 'Đơn giá chi tiết'
    print("[5] Đang xây dựng sheet Đơn giá chi tiết...")
    ws_dgct, map_dgct = build_sheet_12_with_dto(
        wb=wb,
        jobs_dtos=jobs_dtos,
        style_mgr=style_mgr
    )

    # 5.1 Cập nhật sheet 'Công trình' link chính xác sang 'Đơn giá chi tiết'
    print("[5.1] Đang cập nhật đơn giá và thành tiền sang sheet Công trình...")
    update_cong_trinh_from_dgct(ws_ct, item_ct_rows, map_dgct)

    # 6. Xây dựng sheet 'Tính lương NC' (Lương nhân công theo TTLT 56/2015)
    print("[6] Đang xây dựng sheet Tính lương nhân công...")
    ws_luong_nc, total_luong_nc_row, nc_rows = build_luong_nhan_cong_sheet(
        wb=wb,
        font_title_15b=style_mgr.font_title_15b,
        font_sub_11i=style_mgr.font_sub_11i,
        font_header_11b=style_mgr.font_header_11b,
        font_data_11r=style_mgr.font_data_11r,
        font_data_11b=style_mgr.font_data_11b,
        fill_header_gray=style_mgr.fill_header_gray,
        border_cell=style_mgr.border_cell,
        border_total=style_mgr.border_total,
        luong_co_so=2_530_000
    )

    # 7. Xây dựng sheet 'Nhân công' (Đơn giá nhân công tổng hợp)
    print("[7] Đang xây dựng sheet Nhân công...")
    ws_nc, total_nc_row = build_nhan_cong_sheet(
        wb=wb,
        last_hp_row=last_hp_row,
        jobs_dtos=jobs_dtos,
        nc_rows=nc_rows, # <--- Truyền bản đồ tọa độ dòng sang đây
        font_title_15b=style_mgr.font_title_15b,
        font_sub_11i=style_mgr.font_sub_11i,
        font_header_11b=style_mgr.font_header_11b,
        font_data_11r=style_mgr.font_data_11r,
        font_data_11b=style_mgr.font_data_11b,
        fill_header_gray=style_mgr.fill_header_gray,
        fill_sub_gray=style_mgr.fill_sub_gray,
        fill_total_pale=style_mgr.fill_total_pale,
        border_cell=style_mgr.border_cell,
        border_total=style_mgr.border_total,
        FMT_CURRENCY=style_mgr.FMT_CURRENCY,
        FMT_NORM=style_mgr.FMT_NORM
    )

    # 8. Xây dựng sheet 'Vật liệu'
    print("[8] Đang xây dựng sheet Vật liệu...")
    ws_vl, total_vl_row = build_vat_lieu_sheet(
        wb=wb,
        last_hp_row=last_hp_row,
        jobs_dtos=jobs_dtos,
        font_title_15b=style_mgr.font_title_15b,
        font_sub_11i=style_mgr.font_sub_11i,
        font_header_11b=style_mgr.font_header_11b,
        font_data_11r=style_mgr.font_data_11r,
        font_data_11b=style_mgr.font_data_11b,
        fill_header_gray=style_mgr.fill_header_gray,
        fill_sub_gray=style_mgr.fill_sub_gray,
        fill_total_pale=style_mgr.fill_total_pale,
        border_cell=style_mgr.border_cell,
        border_total=style_mgr.border_total,
        FMT_CURRENCY=style_mgr.FMT_CURRENCY,
        FMT_NORM=style_mgr.FMT_NORM
    )

    # 9. Xây dựng sheet 'Tính giá ca máy' (Xác định theo phương pháp chuẩn BXD)
    print("[9] Đang xây dựng sheet Tính giá ca máy...")
    ws_camay, ca_may_rows = build_tinh_gia_ca_may_sheet(
        wb=wb,
        jobs_dtos=jobs_dtos,
        font_title_15b=style_mgr.font_title_15b,
        font_sub_11i=style_mgr.font_sub_11i,
        font_header_11b=style_mgr.font_header_11b,
        font_data_11r=style_mgr.font_data_11r,
        font_data_11b=style_mgr.font_data_11b,
        fill_header_gray=style_mgr.fill_header_gray,
        border_cell=style_mgr.border_cell,
        border_total=style_mgr.border_total,
        FMT_CURRENCY=style_mgr.FMT_CURRENCY
    )

    # 10. Xây dựng sheet 'Công cụ dụng cụ'
    print("[10] Đang xây dựng sheet Công cụ dụng cụ...")
    ws_dc, total_dc_row = build_cong_cu_sheet(
        wb=wb,
        last_hp_row=last_hp_row,
        jobs_dtos=jobs_dtos,
        ca_may_rows=ca_may_rows,
        font_title_15b=style_mgr.font_title_15b,
        font_sub_11i=style_mgr.font_sub_11i,
        font_header_11b=style_mgr.font_header_11b,
        font_data_11r=style_mgr.font_data_11r,
        font_data_11b=style_mgr.font_data_11b,
        fill_header_gray=style_mgr.fill_header_gray,
        fill_sub_gray=style_mgr.fill_sub_gray,
        fill_total_pale=style_mgr.fill_total_pale,
        border_cell=style_mgr.border_cell,
        border_total=style_mgr.border_total,
        FMT_CURRENCY=style_mgr.FMT_CURRENCY,
        FMT_NORM=style_mgr.FMT_NORM
    )

    # 11. Xây dựng sheet 'Máy thi công'
    print("[11] Đang xây dựng sheet Máy thi công...")
    ws_m, total_m_row = build_may_thi_cong_sheet(
        wb=wb,
        last_hp_row=last_hp_row,
        jobs_dtos=jobs_dtos,
        ca_may_rows=ca_may_rows,
        font_title_15b=style_mgr.font_title_15b,
        font_sub_11i=style_mgr.font_sub_11i,
        font_header_11b=style_mgr.font_header_11b,
        font_data_11r=style_mgr.font_data_11r,
        font_data_11b=style_mgr.font_data_11b,
        fill_header_gray=style_mgr.fill_header_gray,
        fill_sub_gray=style_mgr.fill_sub_gray,
        fill_total_pale=style_mgr.fill_total_pale,
        border_cell=style_mgr.border_cell,
        border_total=style_mgr.border_total,
        FMT_CURRENCY=style_mgr.FMT_CURRENCY,
        FMT_NORM=style_mgr.FMT_NORM
    )

    # 11. Xây dựng sheet 'Hệ số'
    print("[11] Đang xây dựng sheet Hệ số...")
    ws_hs, he_so_rows = build_he_so_sheet(
        wb=wb,
        font_title_15b=style_mgr.font_title_15b,
        font_header_11b=style_mgr.font_header_11b,
        font_data_11r=style_mgr.font_data_11r,
        fill_header_gray=style_mgr.fill_header_gray,
        border_cell=style_mgr.border_cell,
        FMT_NORM=style_mgr.FMT_NORM,
        fill_input_yellow=style_mgr.fill_input_yellow,
        font_input_11b=style_mgr.font_input_11b
    )
    ctx.register_he_so(he_so_rows)

    # 12. Xây dựng sheet 'Khoản 4.5 TT20'
    print("[12] Đang xây dựng sheet Khoản 4.5 TT20...")
    ws_45, tot_45_row = build_khoan_4_5_tt20_sheet(
        wb=wb,
        font_title_15b=style_mgr.font_title_15b,
        font_header_11b=style_mgr.font_header_11b,
        font_data_11r=style_mgr.font_data_11r,
        font_data_11b=style_mgr.font_data_11b,
        fill_header_gray=style_mgr.fill_header_gray,
        fill_sub_gray=style_mgr.fill_sub_gray,
        border_cell=style_mgr.border_cell,
        border_total=style_mgr.border_total,
        FMT_MONEY=style_mgr.FMT_CURRENCY
    )
    ctx.register_khoan_4_5(tot_45_row)

    # 13. Xây dựng sheet 'THDT hạng mục' (Sử dụng ProjectContext Hub để liên kết động)
    print("[13] Đang xây dựng sheet THDT hạng mục...")
    build_thdt_hang_muc_sheet(
        wb=wb,
        ctx=ctx,
        tot_ct_row=tot_ct_row,
        last_hp_row=last_hp_row,
        font_title_15b=style_mgr.font_title_15b,
        font_header_11b=style_mgr.font_header_11b,
        font_data_11r=style_mgr.font_data_11r,
        font_data_11b=style_mgr.font_data_11b,
        fill_header_gray=style_mgr.fill_header_gray,
        border_cell=style_mgr.border_cell,
        border_total=style_mgr.border_total,
        FMT_MONEY=style_mgr.FMT_CURRENCY
    )

    # 14. Thiết lập Freeze Panes chuẩn xác cho toàn bộ các sheet
    _apply_all_freeze_panes(wb)

    # 15. Sắp xếp lại thứ tự Tab hiển thị chuẩn Executive Summary First (Đã loại bỏ tab lặp)
    desired_tab_order = [
        "THDT hạng mục",
        "Khoản 4.5 TT20",
        "Công trình",
        "Đơn giá chi tiết",
        "Hao phí VT",
        "Vật liệu",
        "Nhân công",
        "Tính lương NC",
        "Công cụ dụng cụ",
        "Máy thi công",
        "Tính giá ca máy",
        "Dữ liệu định mức",
        "Hệ số"
    ]
    _reorder_sheets_tab(wb, desired_tab_order)

    # 16. Thiết lập Sheet mặc định khi mở file là 'THDT hạng mục'
    if "THDT hạng mục" in wb.sheetnames:
        ws_thdt = wb["THDT hạng mục"]
        wb.active = ws_thdt
        for ws in wb.worksheets:
            ws.sheet_view.tabSelected = (ws == ws_thdt)

    print("✅ Hoàn tất điều phối toàn bộ các sheet thành công!")
    return wb, ws_dgct