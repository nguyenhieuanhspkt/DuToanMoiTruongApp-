# backend/exporters/hieu_exporter.py
import sys, os, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import openpyxl
from backend.models.hieu_models_dto import (
    ExcelStyleManager, JobMappingManager, DinhMucRegistry
)

# Import các module con chuyên trách từng sheet
from backend.exporters.cong_trinh_exporter import build_cong_trinh_sheet
from backend.exporters.dinh_muc_exporter import build_dinh_muc_sheet
from backend.exporters.don_gia_ct_exporter import build_sheet_12_with_dto
from backend.exporters.hao_phi_vt_exporter import build_hao_phi_vt_sheet
from backend.exporters.vat_lieu_exporter import build_vat_lieu_sheet
from backend.exporters.nhan_cong_exporter import build_nhan_cong_sheet
from backend.exporters.cong_cu_exporter import build_cong_cu_sheet
from backend.exporters.may_thi_cong_exporter import build_may_thi_cong_sheet


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
    style_mgr = ExcelStyleManager()
    
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

    ws_ct, item_ct_rows = build_cong_trinh_sheet(
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

    print("===== ITEM CT ROWS =====")
    for k, v in list(item_ct_rows.items())[:10]:
        print(k, "->", v)

    # Gán lại row thực tế từ sheet Công trình
    for idx, job in enumerate(jobs_dtos, start=1):

        row = item_ct_rows.get(idx)

        job.cong_trinh_row = row

        if row is None:
            print(
                f"[WARNING] "
                f"idx={idx} "
                f"stt={job.stt} "
                f"code={job.code} "
                f"row=None"
            )

    print("===== JOB ROW MAP =====")
    for job in jobs_dtos[:10]:
        print(
            f"stt={job.stt} "
            f"code={job.code} "
            f"row={job.cong_trinh_row}"
        )

    # 5. Xây dựng sheet 'Đơn giá chi tiết' (Sử dụng job.cong_trinh_row đã được gán sẵn để link về Công trình)
    print("[4] Đang xây dựng sheet Đơn giá chi tiết...")
    ws_dgct, map_dgct = build_sheet_12_with_dto(
        wb=wb,
        jobs_dtos=jobs_dtos,
        style_mgr=style_mgr
        )

    # (Tùy chọn nâng cao): Nếu cần cập nhật lại đơn giá vào sheet Công trình từ map_dgct thật, 
    # ta có thể duyệt lại ws_ct tại đây hoặc tận dụng cơ chế cell update. Tuy nhiên với pre-calculate, các mỏ neo dòng đã hoàn toàn khớp lệnh!

    # 6. Xây dựng sheet 'Hao phí VT'
    print("[5] Đang xây dựng sheet Hao phí VT...")
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
        jobs_dtos=jobs_dtos
    )

    # 7. Xây dựng sheet 'Nhân công'
    print("[6] Đang xây dựng sheet Nhân công...")
    ws_nc, total_nc_row = build_nhan_cong_sheet(
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

    # 8. Xây dựng sheet 'Vật liệu'
    print("[7] Đang xây dựng sheet Vật liệu...")
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

    # 9. Xây dựng sheet 'Công cụ dụng cụ'
    print("[8] Đang xây dựng sheet Công cụ dụng cụ...")
    ws_dc, total_dc_row = build_cong_cu_sheet(
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

    # 10. Xây dựng sheet 'Máy thi công'
    print("[9] Đang xây dựng sheet Máy thi công...")
    ws_m, total_m_row = build_may_thi_cong_sheet(
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
    
    # 11. Hoàn thiện các sheet hệ thống phụ trợ
    print("[10] Đang hoàn thiện các sheet hệ thống phụ trợ...")
    for sname in ['Hệ số', 'Nhân công', 'Công cụ dụng cụ', 'Máy thi công', 'Khoản 4.5 TT20', 'THDT hạng mục']:
        if sname not in wb.sheetnames:
            ws_tmp = wb.create_sheet(title=sname)
            ws_tmp.append(["placeholder"])

    print("✅ Hoàn tất điều phối toàn bộ các sheet thành công!")
    return wb, ws_dgct