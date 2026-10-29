# Trong file excel_f1_full_replica_exporter.py

from backend.models.hieu_models_dto import JobItemDTO, SubtotalGroupDTO, DetailItemDTO

def build_sheet_12_with_dto(
    wb, pakt_items, mats_map, tools_map, eq_map, mat_items, tools_items, equip_items,
    font_title_15b, font_sub_11i, font_header_11b, font_sec_12b, font_data_11r, font_data_11b,
    fill_header_gray, fill_sub_gray, fill_total_pale, border_cell, border_total,
    FMT_CURRENCY, FMT_NORM, FMT_PCT
):
    """
    Xây dựng Sheet 'Đơn giá chi tiết' hoàn toàn bằng mô hình DTO (Data Transfer Object).
    """
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

    # Mapping tọa độ dòng sang các sheet tổng hợp
    vl_row_mapping = {str(m.get('name', '')).lower().strip(): idx_m for idx_m, m in enumerate(mat_items, start=7)}
    nc_row_mapping = {"nc_ldkt": 7, "nc_ldpt": 8}
    eq_row_mapping = {str(e.get('name', '')).lower().strip(): idx_e for idx_e, e in enumerate(equip_items, start=7)}
    tools_row_mapping = {str(t.get('name', '')).lower().strip(): idx_t for idx_t, t in enumerate(tools_items, start=7)}

    # BƯỚC 1: CHUYỂN ĐỔI DỮ LIỆU THÔ THÀNH DANH SÁCH OBJECT DTO
    jobs_dtos: List[JobItemDTO] = []
    for idx, it in enumerate(pakt_items, start=1):
        code_str = it.get("ma_gop", f"TT20_{idx:03d}")
        name_str = it.get("thong_so", "Thông số quan trắc")
        dvt_str = it.get("dvt", "mẫu")
        core_code = it.get("code", f"P_{idx}")
        tt20_data = it.get("tt20_data", {})

        job_dto = JobItemDTO(stt=idx, code=code_str, name=name_str, unit=dvt_str, quantity=1.0)

        for stage_key, stage_lbl in [('field', 'Ngoại nghiệp'), ('lab', 'Nội nghiệp'), ('single', 'Toàn phần')]:
            sub = tt20_data.get(stage_key)
            if not sub or not isinstance(sub, dict):
                continue

            # Nhân công
            nc_norm = sub.get('dinh_muc_cong')
            nc_title = sub.get('dinh_bien') or f'Quan trắc viên ({stage_lbl})'
            if nc_norm and float(nc_norm) > 0:
                is_pt = ("phổ thông" in nc_title.lower() or "phụ việc" in nc_title.lower())
                target_row_nc = nc_row_mapping.get("nc_ldpt" if is_pt else "nc_ldkt", 7)
                job_dto.add_detail("NC", DetailItemDTO(
                    code=f"NC_{core_code}", sub_code="1", name=f"{nc_title}", unit="công",
                    norm=float(nc_norm), price_formula=f"='Nhân công'!$F${target_row_nc}", stage=stage_lbl
                ))

            # Vật liệu
            for m_idx, m in enumerate(sub.get('materials', []), 1):
                m_name = m.get('name', '').strip()
                m_norm = float(m.get('norm') or 0.0)
                if m_norm > 0:
                    target_row_vl = vl_row_mapping.get(m_name.lower().strip(), 7)
                    job_dto.add_detail("VL", DetailItemDTO(
                        code=f"VL_{core_code}", sub_code=str(m_idx), name=m_name, unit=m.get('unit', '').strip(),
                        norm=m_norm, price_formula=f"='Vật liệu'!$F${target_row_vl}", stage=stage_lbl
                    ))

            # Máy & CCDC (gộp vào nhóm M)
            for t_idx, t in enumerate(sub.get('tools', []), 1):
                t_norm = float(t.get('norm') or 0.0)
                t_name = t.get('name') or t.get('unit') or 'cái'
                if t_norm > 0:
                    target_row_t = tools_row_mapping.get(str(t_name).lower().strip(), 7)
                    job_dto.add_detail("M", DetailItemDTO(
                        code=f"M_{core_code}", sub_code=f"DC_{t_idx}", name=f"DC: {t_name}", unit=t.get('unit', 'cái'),
                        norm=t_norm, price_formula=f"='Công cụ dụng cụ'!$F${target_row_t}", stage=stage_lbl
                    ))

        jobs_dtos.append(job_dto)

    curr_dgct_r = 6
    map_dgct = {}

    for job in jobs_dtos:
        job.row_index = curr_dgct_r
        
        # 1. Ghi dòng Công việc Cha (Master Row)
        ws_dgct.append(job.to_master_row())
        ws_dgct.row_dimensions[curr_dgct_r].outlineLevel = 0
        curr_dgct_r += 1

        # Lưu lại các dòng tổng hợp subtotal của từng nhóm để sau này tính Tổng trực tiếp (T)
        group_subtotal_rows = {}

        # Định nghĩa 4 nhóm chuẩn nghiệp vụ TT20: Vật liệu, Nhân công, CCDC, Máy
        group_configs = [
            ("VL", "Vật liệu"),
            ("NC", "Nhân công"),
            ("DC", "Công cụ dụng cụ"),
            ("M", "Máy thi công & Thiết bị")
        ]

        # 2. Duyệt qua từng nhóm con trong 4 nhóm
        for g_key, g_label in group_configs:
            group_obj = job.groups[g_key]
            
            # Ghi dòng tiêu đề nhóm (ví dụ: "Vật liệu", "Nhân công"...)
            ws_dgct.append(["", "", "", g_label, "", "", "", "", "", ""])
            ws_dgct.row_dimensions[curr_dgct_r].outlineLevel = 1
            curr_dgct_r += 1

            if group_obj.items:
                # Ghi nhận mốc dòng bắt đầu của các item con trong nhóm
                group_obj.start_child_row = curr_dgct_r
                
                # Bơm các dòng thành phần chi tiết (Detail Items) vào
                for item in group_obj.items:
                    ws_dgct.append(item.to_row_data(curr_dgct_r))
                    ws_dgct.row_dimensions[curr_dgct_r].outlineLevel = 2
                    ws_dgct.row_dimensions[curr_dgct_r].hidden = True  # Mặc định collapse ẩn đi
                    curr_dgct_r += 1
                
                # Ghi nhận mốc dòng kết thúc của các item con
                group_obj.end_child_row = curr_dgct_r - 1

                # Nếu là nhóm Vật liệu (VL), có thêm dòng "Vật liệu phụ khác (8% VL chính)"
                if g_key == "VL":
                    ws_dgct.append([
                        "", "VL_KHAC", len(group_obj.items) + 1, 
                        " - Vật liệu phụ khác (8% VL chính)", "%", 
                        "='Hệ số'!$C$11", "", 1.0, 
                        f"=ROUND(SUM(J{group_obj.start_child_row}:J{group_obj.end_child_row})*G{curr_dgct_r}, 0)"
                    ])
                    ws_dgct.row_dimensions[curr_dgct_r].outlineLevel = 2
                    ws_dgct.row_dimensions[curr_dgct_r].hidden = True
                    curr_dgct_r += 1

            # Gọi phương thức lấy dữ liệu dòng Subtotal của nhóm (tự động có hàm =SUM(...))
            # Cập nhật lại dải dòng subtotal trước khi xuất
            sub_row_data = group_obj.to_row_data()
            
            # Nếu nhóm có item, ta ghi đè công thức SUM chuẩn vào cột Thành tiền (cột J, index 9)
            if group_obj.items:
                sum_range_end = curr_dgct_r - 1
                sub_row_data[9] = f"=ROUND(SUM(J{group_obj.start_child_row}:{sum_range_end}), 0)"

            ws_dgct.append(sub_row_data)
            ws_dgct.row_dimensions[curr_dgct_r].outlineLevel = 1
            
            # Lưu lại vị trí dòng subtotal của nhóm này để tính tổng chi phí trực tiếp (T)
            group_subtotal_rows[g_key] = curr_dgct_r
            curr_dgct_r += 1

        # 3. Khối tổng hợp chi phí trực tiếp và các khoản gián tiếp cho 1 mẫu
        vl_sub_r = group_subtotal_rows.get("VL", curr_dgct_r)
        nc_sub_r = group_subtotal_rows.get("NC", curr_dgct_r)
        dc_sub_r = group_subtotal_rows.get("DC", curr_dgct_r)
        m_sub_r  = group_subtotal_rows.get("M", curr_dgct_r)

        t_row = curr_dgct_r
        ws_dgct.append(["", "", "", "Chi phí trực tiếp (VL + NC + DC + M)", "T", "", "", "", "", f"=ROUND(J{vl_sub_r}+J{nc_sub_r}+J{dc_sub_r}+J{m_sub_r}, 0)"])
        ws_dgct.row_dimensions[curr_dgct_r].outlineLevel = 0
        curr_dgct_r += 1

        # Các dòng chi phí gián tiếp, VAT, Thuế dự thầu tiếp theo...
        gt_row = curr_dgct_r
        c_row = curr_dgct_r + 1
        tt_row = curr_dgct_r + 2
        tl_row = curr_dgct_r + 3
        g_row = curr_dgct_r + 4
        gtgt_row = curr_dgct_r + 5
        gxd_row = curr_dgct_r + 6
        lt_row = curr_dgct_r + 7
        total_row = curr_dgct_r + 8

        ws_dgct.append(["", "", "", "Chi phí gián tiếp (C + TT)", "GT", "", "", "", "", f"=J{c_row}+J{tt_row}"])
        curr_dgct_r += 1
        ws_dgct.append(["", "", "", "Chi phí chung (T x 20%)", "C", "='Hệ số'!$C$4", "", "", "", f"=ROUND(J{t_row}*G{c_row}, 0)"])
        curr_dgct_r += 1
        ws_dgct.append(["", "", "", "Chi phí công việc không xác định từ thiết kế", "TT", "='Hệ số'!$C$9", "", "", "", f"=ROUND(J{t_row}*G{tt_row}, 0)"])
        curr_dgct_r += 1
        ws_dgct.append(["", "", "", "Thu nhập chịu thuế tính trước", "TL", "='Hệ số'!$C$8", "", "", "", f"=ROUND((J{t_row}+J{gt_row})*G{tl_row}, 0)"])
        curr_dgct_r += 1
        ws_dgct.append(["", "", "", "Chi phí trước thuế", "G", "", "", "", "", f"=ROUND(J{t_row}+J{gt_row}+J{tl_row}, 0)"])
        curr_dgct_r += 1
        ws_dgct.append(["", "", "", "Thuế giá trị gia tăng (VAT 8%)", "GTGT", "='Hệ số'!$C$10", "", "", "", f"=ROUND(J{g_row}*G{gtgt_row}, 0)"])
        curr_dgct_r += 1
        ws_dgct.append(["", "", "", "CHI PHÍ SAU THUẾ", "Gxd", "", "", "", "", f"=ROUND(J{g_row}+J{gtgt_row}, 0)"])
        curr_dgct_r += 1
        ws_dgct.append(["", "", "", "Chi phí nhà tạm để ở và điều hành", "LT", "='Hệ số'!$C$6", "", "", "", f"=ROUND(J{g_row}*G{lt_row}*(1+'Hệ số'!$C$10), 0)"])
        curr_dgct_r += 1
        ws_dgct.append(["", "", "", "Tổng cộng đơn giá dự thầu 1 mẫu", "VNĐ", "", "", "", "", f"=ROUND(J{gxd_row}+J{lt_row}, 0)"])
        curr_dgct_r += 1

        ws_dgct.append([])
        curr_dgct_r += 1

        # Lưu lại map tọa độ phục vụ cho sheet 'Công trình' link sang
        map_dgct[job.stt] = {
            'row_vl': vl_sub_r,
            'row_nc': nc_sub_r,
            'row_dc': dc_sub_r,
            'row_m': m_sub_r,
            'row_t': t_row,
            'row_total': total_row
        }