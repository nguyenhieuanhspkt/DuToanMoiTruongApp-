import os
import json
from backend.models.hieu_models_dto import DinhMucRowDTO, DinhMucRegistry

def build_dinh_muc_sheet(wb, data_dir: str):
    """
    Đọc file JSON định mức từ thư mục TT20, ghi ra sheet 'Dữ liệu định mức' 
    và đăng ký Unique ID cho từng thành phần hao phí.
    """
    registry = DinhMucRegistry()
    
    # Kiểm tra xem sheet đã tồn tại chưa, nếu có thì dùng lại, chưa thì tạo mới
    if "Dữ liệu định mức" in wb.sheetnames:
        ws = wb["Dữ liệu định mức"]
    else:
        ws = wb.create_sheet(title="Dữ liệu định mức")
        
    ws.views.sheetView[0].showGridLines = True
    
    # Ghi tiêu đề cột nếu sheet còn trống
    if ws.max_row <= 1:
        ws.append(["Mã TT", "Tên thông số", "Phân loại", "Định biên",
                   "Loại hao phí", "Đơn vị", "Định mức", "Tên VT / Tiêu chuẩn"])
        ws.row_dimensions[1].height = 20

    row_map = {}
    curr_row = 2

    # Lấy danh sách file JSON định mức
    if not os.path.exists(data_dir):
        return row_map, registry

    json_files = sorted([f for f in os.listdir(data_dir) if f.endswith('.json')])

    for fn in json_files:
        fpath = os.path.join(data_dir, fn)
        with open(fpath, encoding='utf-8') as f:
            section_data = json.load(f)

        section_id    = section_data.get('section_id', '')
        section_title = section_data.get('section_title', '')
        parameters    = section_data.get('parameters', {})

        ws.append([f"=== {section_id}: {section_title} ==="])
        curr_row += 1

        for ma, param in parameters.items():
            dm_dto = DinhMucRowDTO(
                ma            = ma,
                ten           = param.get('ten_thong_so', ''),
                phan_loai     = param.get('phan_loai', ''),
                dinh_bien     = param.get('dinh_bien', ''),
                dinh_muc_cong = float(param.get('dinh_muc_cong') or 0.0),
                tieu_chuan    = param.get('tieu_chuan', ''),
            )

            for m in param.get('materials', []):
                m_norm = float(m.get('norm') or 0.0)
                m_name = str(m.get('name') or '').strip()
                raw_unit = str(m.get('unit') or '').strip()
                m_unit = raw_unit.lower() if raw_unit else ''
                
                if m_norm > 0 and m_name:
                    dm_dto.add_hao_phi('VL', m_name, m_unit, m_norm)
            for t in param.get('tools', []):
                t_norm = float(t.get('norm') or 0.0)
                # JSON gốc bị lệch: Tên dụng cụ nằm ở 'unit', Đơn vị tính nằm ở 'lifespan_months'
                t_name = str(t.get('unit') or '').strip()
                raw_unit = str(t.get('lifespan_months') or '').strip()
                
                # Giữ nguyên đơn vị gốc, chỉ lower() để đồng bộ
                t_unit = raw_unit.lower() if raw_unit else 'cái'
                
                if t_norm > 0 and t_name:
                    dm_dto.add_hao_phi('DC', t_name, t_unit, t_norm)

            for e in param.get('equipment', []):
                e_norm = float(e.get('norm') or 0.0)
                e_name = str(e.get('name') or '').strip()
                raw_unit = str(e.get('unit') or '').strip()
                e_unit = raw_unit.lower() if raw_unit else ''
                
                if e_norm > 0 and e_name:
                    dm_dto.add_hao_phi('M', e_name, e_unit, e_norm)

            # 1. Ghi dòng Nhân công (NC - index 1)
            dm_dto.block_start  = curr_row
            dm_dto.nc_row_index = curr_row
            ws.append(dm_dto.to_nc_row(curr_row))
            
            uid_nc = registry.generate_unique_id(ma, 'NC', 1)
            registry.register_by_id(uid_nc, curr_row)
            curr_row += 1

            # 2. Ghi các dòng hao phí VL / DC / M
            vl_idx, dc_idx, m_idx = 1, 1, 1
            for hp in dm_dto.hao_phi:
                hp.row_index = curr_row
                ws.append(dm_dto.to_haophi_row(hp))
                
                if hp.loai == 'VL':
                    cur_id = registry.generate_unique_id(ma, 'VL', vl_idx)
                    vl_idx += 1
                elif hp.loai == 'DC':
                    cur_id = registry.generate_unique_id(ma, 'DC', dc_idx)
                    dc_idx += 1
                else:
                    cur_id = registry.generate_unique_id(ma, 'M', m_idx)
                    m_idx += 1

                registry.register_by_id(cur_id, curr_row)
                curr_row += 1

            dm_dto.block_end = curr_row - 1
            row_map[ma] = dm_dto

        ws.append([])
        curr_row += 1

    ws.freeze_panes = "A2"
    return row_map, registry