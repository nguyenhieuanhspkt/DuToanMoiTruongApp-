import os
import json
from openpyxl.worksheet.worksheet import Worksheet
from backend.models.hieu_models_dto import DinhMucRowDTO, DinhMucRegistry

def _init_dinh_muc_sheet(wb) -> Worksheet:
    """Khởi tạo hoặc lấy sẵn sheet 'Dữ liệu định mức' và thiết lập tiêu đề cột chuẩn."""
    if "Dữ liệu định mức" in wb.sheetnames:
        ws = wb["Dữ liệu định mức"]
    else:
        ws = wb.create_sheet(title="Dữ liệu định mức")
        
    ws.views.sheetView[0].showGridLines = True
    
    if ws.max_row <= 1:
        ws.append([
            "Mã TT", "Tên thông số", "Phân loại", "Định biên",
            "Loại hao phí", "Đơn vị", "Định mức", "Tên VT / Tiêu chuẩn"
        ])
        ws.row_dimensions[1].height = 20

    return ws


def _parse_materials(param: dict, dm_dto: DinhMucRowDTO):
    """Nạp danh sách Vật liệu (VL) vào đối tượng DTO."""
    for m in param.get('materials', []):
        m_norm = float(m.get('norm') or 0.0)
        m_name = str(m.get('name') or '').strip()
        raw_unit = str(m.get('unit') or '').strip()
        m_unit = raw_unit.lower() if raw_unit else ''
        
        if m_norm > 0 and m_name:
            dm_dto.add_hao_phi('VL', m_name, m_unit, m_norm)


def _parse_tools(param: dict, dm_dto: DinhMucRowDTO):
    """Nạp danh sách Công cụ dụng cụ (DC) vào đối tượng DTO."""
    for t in param.get('tools', []):
        t_norm = float(t.get('norm') or 0.0)
        t_name = str(t.get('unit') or '').strip()
        raw_unit = str(t.get('lifespan_months') or '').strip()
        t_unit = raw_unit.lower() if raw_unit else 'cái'
        
        if t_norm > 0 and t_name:
            dm_dto.add_hao_phi('DC', t_name, t_unit, t_norm)


def _parse_equipment(param: dict, dm_dto: DinhMucRowDTO):
    """Nạp danh sách Thiết bị / Máy thi công (M) vào đối tượng DTO."""
    for e in param.get('equipment', []):
        e_norm = float(e.get('norm') or 0.0)
        e_name = str(e.get('name') or '').strip()
        raw_unit = str(e.get('unit') or '').strip()
        e_unit = raw_unit.lower() if raw_unit else ''
        
        if e_norm > 0 and e_name:
            dm_dto.add_hao_phi('M', e_name, e_unit, e_norm)


def _write_parameter_block(
    ws: Worksheet, 
    registry: DinhMucRegistry, 
    dm_dto: DinhMucRowDTO, 
    ma: str, 
    phan_loai: str, 
    curr_row: int
) -> int:
    """Ghi dòng Nhân công và toàn bộ hao phí của thông số ra sheet, đồng thời đăng ký Registry."""
    # 1. Ghi dòng Nhân công (NC)
    dm_dto.block_start = curr_row
    dm_dto.nc_row_index = curr_row
    ws.append(dm_dto.to_nc_row(curr_row))

    uid_nc = registry.generate_unique_id(ma, 'NC', 1, stage=phan_loai)
    registry.register_by_id(uid_nc, curr_row)
    curr_row += 1

    # 2. Ghi các dòng hao phí VL / DC / M
    vl_idx, dc_idx, m_idx = 1, 1, 1
    for hp in dm_dto.hao_phi:
        hp.row_index = curr_row
        ws.append(dm_dto.to_haophi_row(hp))
        
        if hp.loai == 'VL':
            cur_id = registry.generate_unique_id(ma, 'VL', vl_idx, stage=phan_loai)
            vl_idx += 1
        elif hp.loai == 'DC':
            cur_id = registry.generate_unique_id(ma, 'DC', dc_idx, stage=phan_loai)
            dc_idx += 1
        else:
            cur_id = registry.generate_unique_id(ma, 'M', m_idx, stage=phan_loai)
            m_idx += 1

        registry.register_by_id(cur_id, curr_row)
        curr_row += 1

    dm_dto.block_end = curr_row - 1
    return curr_row


def _apply_column_widths(ws: Worksheet):
    """Tự động căn chỉnh độ rộng các cột trong sheet."""
    col_widths = [14, 30, 16, 28, 14, 12, 14, 35]
    for col_idx, width in enumerate(col_widths, start=1):
        col_letter = ws.cell(row=1, column=col_idx).column_letter
        ws.column_dimensions[col_letter].width = width


def build_dinh_muc_sheet(wb, data_dir: str):
    """
    Hàm điều phối chính: Đọc file JSON định mức từ thư mục TT20, 
    ghi ra sheet 'Dữ liệu định mức' và đăng ký Unique ID theo từng giai đoạn.
    """
    registry = DinhMucRegistry()
    ws = _init_dinh_muc_sheet(wb)

    row_map = {}
    curr_row = 2

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
            phan_loai = param.get('phan_loai', '')

            dm_dto = DinhMucRowDTO(
                ma            = ma,
                ten           = param.get('ten_thong_so', ''),
                phan_loai     = phan_loai,
                dinh_bien     = param.get('dinh_bien', ''),
                dinh_muc_cong = float(param.get('dinh_muc_cong') or 0.0),
                tieu_chuan    = param.get('tieu_chuan', ''),
            )

            # Bóc tách các thành phần hao phí qua các hàm con chuyên trách
            _parse_materials(param, dm_dto)
            _parse_tools(param, dm_dto)
            _parse_equipment(param, dm_dto)

            # Ghi ra sheet và đăng ký Registry
            curr_row = _write_parameter_block(ws, registry, dm_dto, ma, phan_loai, curr_row)

            row_map[ma] = dm_dto

        ws.append([])
        curr_row += 1

    _apply_column_widths(ws)

    return row_map, registry