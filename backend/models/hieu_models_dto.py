import re  # <--- Thêm dòng này vào đầu file
# backend/models/dutoan_dto.py
from typing import List, Dict, Optional, Any, Union
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side




# ============================================================
# DTO: quản lý chuyên biệt (ví dụ: DinhMucRegistry hoặc tích hợp thẳng vào cấu trúc DTO định mức) để nó tự ôm trọn phần mã hóa khóa cho cả VL, NC, DC, M:
# ============================================================

class DinhMucRegistry:
    """Quản lý kho định mức chuẩn hóa dựa trên Unique ID định danh tuyệt đối có phân tách giai đoạn."""
    def __init__(self):
        self._registry_map: Dict[str, int] = {}

    @staticmethod
    def normalize_stage(stage: str, ma: str = "") -> str:
        s = str(stage).lower().strip()
        if "ngoại" in s or "field" in s:
            return "ngoai_nghiep"
        if "nội" in s or "lab" in s:
            return "noi_nghiep"
        # Nếu không truyền stage, suy luận từ tiền tố mã (1... là Ngoại, 2... là Nội)
        if str(ma).startswith("1"):
            return "ngoai_nghiep"
        if str(ma).startswith("2"):
            return "noi_nghiep"
        return "toan_phan"

    @staticmethod
    def generate_unique_id(ma: str, loai: str, index: int, stage: str = "") -> str:
        clean_ma = re.sub(r'^[12]', '', str(ma)).lower().strip()
        clean_loai = str(loai).lower().strip()
        clean_stage = DinhMucRegistry.normalize_stage(stage, ma)
        return f"{clean_ma}_{clean_stage}_{clean_loai}_{index}"

    def register_by_id(self, unique_id: str, row_index: int):
        key = unique_id.lower().strip()
        self._registry_map[key] = row_index

    def get_formula_by_id(self, unique_id: str, fallback_value: Any) -> Any:
        key = unique_id.lower().strip()
        row_idx = self._registry_map.get(key)
        if row_idx:
            return f"='Dữ liệu định mức'!$G${row_idx}"
        return fallback_value

# Chuyên gia nhận dữ liệu thô, gọi Registry để bóc tách và lắp ráp thành các danh sách DTO hoàn chỉnh.
class JobMappingManager:
    """Class chuyên trách bóc tách và ánh xạ dữ liệu công tác quan trắc thông qua Unique ID."""
    def __init__(self, mat_items: list, tools_items: list, equip_items: list, dinh_muc_registry: Optional[DinhMucRegistry] = None):
        def _normalize(items):
            return [i if isinstance(i, dict) else {"name": str(i)} for i in (items or [])]

        self.mat_items = _normalize(mat_items)
        self.tools_items = _normalize(tools_items)
        self.equip_items = _normalize(equip_items)
        
        self.registry = dinh_muc_registry or DinhMucRegistry()

        self.vl_row_mapping = {str(m.get('name', '')).lower().strip(): idx for idx, m in enumerate(self.mat_items, start=7)}
        self.nc_row_mapping = {"nc_ldkt": 7, "nc_ldpt": 8}
        self.tools_row_mapping = {str(t.get('name', '')).lower().strip(): idx for idx, t in enumerate(self.tools_items, start=7)}
        self.eq_row_mapping = {str(e.get('name', '')).lower().strip(): idx for idx, e in enumerate(self.equip_items, start=7)}

    def build_jobs(self, pakt_items: list) -> List['JobItemDTO']:
        """Bóc tách pakt_items thô thành danh sách JobItemDTO bằng Unique ID chính xác tuyệt đối."""
        jobs_dtos = []

        for idx, it in enumerate(pakt_items, start=1):
            stt_str = str(idx)
            name_str = it.get("thong_so", "Thông số quan trắc")
            dvt_str  = it.get("dvt", "mẫu")
            ma_gop   = it.get("ma_gop", f"P_{idx}")
            tt20_data = it.get("tt20_data", {})
            
            job_dto = JobItemDTO(stt=stt_str, code=ma_gop, name=name_str, unit=dvt_str, quantity=float(it.get("so_luong_mau", 1.0)))

            for stage_key, stage_lbl in [('field', 'Ngoại nghiệp'), ('lab', 'Nội nghiệp'), ('single', 'Toàn phần')]:
                sub = tt20_data.get(stage_key)
                if not sub or not isinstance(sub, dict):
                    continue

                # 1. Nhân công (NC - index 1)
                nc_norm = sub.get('dinh_muc_cong')
                nc_title = sub.get('dinh_bien') or f'Quan trắc viên ({stage_lbl})'
                if nc_norm and float(nc_norm) > 0:
                    is_pt = ("phổ thông" in nc_title.lower() or "phụ việc" in nc_title.lower())
                    target_row_nc = self.nc_row_mapping.get("nc_ldpt" if is_pt else "nc_ldkt", 7)
                    
                    uid = self.registry.generate_unique_id(ma_gop, 'NC', 1, stage=stage_lbl)
                    norm_val = self.registry.get_formula_by_id(uid, float(nc_norm))
                    
                    job_dto.add_detail("NC", DetailItemDTO(
                        code=f"NC_{ma_gop}", sub_code="1", name=nc_title, unit="công",
                        norm=norm_val, price_formula=f"='Nhân công'!$F${target_row_nc}", stage=stage_lbl
                    ))

                # 2. Vật liệu (VL)
                for m_idx, m in enumerate(sub.get('materials', []), 1):
                    m_norm = float(m.get('norm') or 0.0)
                    m_name = m.get('name', '').strip()
                    if m_norm > 0:
                        target_row_vl = self.vl_row_mapping.get(m_name.lower().strip(), 7)
                        
                        uid = self.registry.generate_unique_id(ma_gop, 'VL', m_idx, stage=stage_lbl)
                        norm_val = self.registry.get_formula_by_id(uid, m_norm)
                        
                        job_dto.add_detail("VL", DetailItemDTO(
                            code=f"VL_{ma_gop}", sub_code=str(m_idx), name=m_name, unit=m.get('unit', '').strip(),
                            norm=norm_val, price_formula=f"='Vật liệu'!$F${target_row_vl}", stage=stage_lbl
                        ))

                # 3. Công cụ dụng cụ (DC)
                for t_idx, t in enumerate(sub.get('tools', []), 1):
                    t_norm = float(t.get('norm') or 0.0)
                    t_name = t.get('name', 'Công cụ dụng cụ').strip()
                    t_unit = t.get('unit', 'cái').strip()
                    if t_norm > 0:
                        target_row_t = self.tools_row_mapping.get(t_unit.lower().strip(), 7)
                        
                        uid = self.registry.generate_unique_id(ma_gop, 'DC', t_idx, stage=stage_lbl)
                        norm_val = self.registry.get_formula_by_id(uid, t_norm)
                        
                        job_dto.add_detail("DC", DetailItemDTO(
                            code=f"DC_{ma_gop}", sub_code=f"DC_{t_idx}", name=t_name, unit=t_unit,
                            norm=norm_val, price_formula=f"='Công cụ dụng cụ'!$F${target_row_t}", stage=stage_lbl
                        ))

                # 4. Máy thi công (M)
                for e_idx, e in enumerate(sub.get('equipment', []), 1):
                    e_norm = float(e.get('norm') or 0.0)
                    e_name = e.get('name', '').strip()
                    if e_norm > 0:
                        target_row_e = self.eq_row_mapping.get(e_name.lower().strip(), 7)
                        
                        uid = self.registry.generate_unique_id(ma_gop, 'M', e_idx, stage=stage_lbl)
                        norm_val = self.registry.get_formula_by_id(uid, e_norm)
                        
                        job_dto.add_detail("M", DetailItemDTO(
                            code=f"M_{ma_gop}", sub_code=f"M_{e_idx}", name=e_name, unit=e.get('unit', ''),
                            norm=norm_val, price_formula=f"='Máy thi công'!$F${target_row_e}", stage=stage_lbl
                        ))

            jobs_dtos.append(job_dto)
        return jobs_dtos
# ============================================================
# DTO: Dữ liệu Định mức TT20 (một thông số quan trắc)
# ============================================================
class DinhMucHaoPhiDTO:
    """Một dòng hao phí chi tiết trong bảng định mức (VL / DC / M)."""
    def __init__(self, loai: str, name: str, unit: str, norm: float, row_index: int = None):
        self.loai = loai          # "VL" | "DC" | "M"
        self.name = name
        self.unit = unit
        self.norm = norm
        self.row_index: Optional[int] = row_index   # dòng trong sheet Dữ liệu định mức


class DinhMucRowDTO:
    """
    DTO đại diện cho một thông số định mức TT20.
    Mỗi thông số chiếm một BLOCK dòng trong sheet 'Dữ liệu định mức':
      - Dòng đầu  : thông tin chung + Nhân công (dinh_muc_cong) → nc_row_index
      - Tiếp theo : Vật liệu, CCDC, Máy → mỗi cái 1 dòng
    """
    def __init__(self, ma: str, ten: str, phan_loai: str,
                 dinh_bien: str, dinh_muc_cong: float, tieu_chuan: str = ""):
        self.ma = ma
        self.ten = ten
        self.phan_loai = phan_loai
        self.dinh_bien = dinh_bien
        self.dinh_muc_cong = dinh_muc_cong
        self.tieu_chuan = tieu_chuan
        self.hao_phi: List[DinhMucHaoPhiDTO] = []
        self.nc_row_index: Optional[int] = None
        self.block_start:  Optional[int] = None
        self.block_end:    Optional[int] = None

    def add_hao_phi(self, loai: str, name: str, unit: str, norm: float):
        self.hao_phi.append(DinhMucHaoPhiDTO(loai=loai, name=name, unit=unit, norm=norm))

    def to_nc_row(self, row: int) -> List[Any]:
        """A: Mã | B: Tên | C: Phân loại | D: Định biên | E: Loại | F: ĐVT | G: Định mức | H: Tiêu chuẩn"""
        return [self.ma, self.ten, self.phan_loai, self.dinh_bien,
                "Nhân công", "công", self.dinh_muc_cong, self.tieu_chuan]

    def to_haophi_row(self, hp: DinhMucHaoPhiDTO) -> List[Any]:
        return [self.ma, "", "", "", hp.loai, hp.unit, hp.norm, hp.name]
# ============================================================
# DTO: Dữ liệu Đơn giá chi tiết (một thông số quan trắc)
# ============================================================

class DetailItemDTO:
    """DTO đại diện cho một thành phần hao phí chi tiết (Cấp 2: Vật liệu, Nhân công, Máy...)"""
    def __init__(self, code: str, sub_code: str, name: str, unit: str, norm: Union[float, str], price_formula: str, stage: str = ""):
        self.code = code                # Mã hiệu (ví dụ: VL_TT20_001)
        self.sub_code = sub_code        # STT hoặc mã phụ (ví dụ: VL_001)
        self.name = name                # Tên thành phần
        self.unit = unit                # Đơn vị tính
        self.norm = norm                # Định mức tiêu hao (có thể là float hoặc chuỗi công thức)
        self.price_formula = price_formula  # Công thức link đơn giá (ví dụ: ='Vật liệu'!$F$7)
        self.stage = stage              # Giai đoạn (Ngoại nghiệp, Nội nghiệp...)
        self.hp_row: Optional[int] = None # Tọa độ dòng tương ứng trong sheet 'Hao phí VT'

    def to_row_data(self, current_row: int) -> List[Any]:
        display_name = f" - {self.name} ({self.stage})" if self.stage else f" - {self.name}"
        return [
            "",                           # STT (trống cho dòng con)
            self.code,                    # Mã hiệu
            self.sub_code,                # STT thành phần (Cột C)
            "",                           # Mã hiệu VL/NC/M (Cột D)
            display_name,                 # Tên hao phí (Cột E)
            self.unit,                    # Đơn vị
            self.norm,                    # Định mức (Cột G - nhận trực tiếp float hoặc chuỗi formula)
            self.price_formula,           # Đơn giá (Cột H)
            1.0,                          # Hệ số (Cột I)
            f"=ROUND(G{current_row}*H{current_row}*I{current_row}, 0)" # Thành tiền (Cột J)
        ]

class SubtotalGroupDTO:
    """DTO đại diện cho nhóm hao phí (Cấp 1: Vật liệu, Nhân công, Máy thi công)"""
    def __init__(self, group_name: str, prefix: str):
        self.group_name = group_name
        self.prefix = prefix
        self.items: List[DetailItemDTO] = []
        self.start_child_row = None
        self.end_child_row = None
        self.row_index = None

    def add_item(self, item: DetailItemDTO):
        self.items.append(item)

    def to_header_row(self) -> List[Any]:
        """Trả về dữ liệu dòng tiêu đề nhóm (Level 1)"""
        return [
            "", "", "", "", 
            self.group_name,  # Tên nhóm hiển thị ở cột E
            "", "", "", "", ""
        ]

    def to_row_data(self) -> List[Any]:
        # Tự sinh hàm SUM dựa trên dải dòng thực tế của các item con bên trong nhóm
        formula_sum = f"=SUM(J{self.start_child_row}:J{self.end_child_row})" if self.items else "0"
        return [
            "", "", "", "", self.group_name, "", "", "", "", formula_sum
        ]


class JobItemDTO:
    """DTO đại diện cho một công việc quan trắc chính (Cấp 0: Parent Job)"""
    def __init__(self, stt: int, code: str, name: str, unit: str, quantity: float):
        self.stt = stt
        self.code = code
        self.name = name
        self.unit = unit
        self.quantity = quantity
        self.groups: Dict[str, SubtotalGroupDTO] = {
            "VL": SubtotalGroupDTO("Vật liệu", "VL"),
            "NC": SubtotalGroupDTO("Nhân công", "NC"),
            "DC": SubtotalGroupDTO("Công cụ dụng cụ", "DC"),
            "M":  SubtotalGroupDTO("Máy thi công & Thiết bị", "M")
        }
        self.row_index = None

    def add_detail(self, group_key: str, item: DetailItemDTO):
        if group_key in self.groups:
            self.groups[group_key].add_item(item)

    def to_master_row(self) -> List[Any]:
        return [
            self.stt, self.code, "", "", self.name, self.unit, "", "", "", ""
        ]
#Tổng hợp chi phí đuôi của sheet 12 (đơn giá chi tiết)        
class IndirectCostSummaryDTO:
    """DTO chuyên quản lý khối chi phí gián tiếp, VAT, và tổng giá dự thầu từ dòng trực tiếp T."""
    def __init__(self, t_row: int):
        self.t_row = t_row  # Tọa độ dòng Chi phí trực tiếp T

    def render_rows(self, start_row: int) -> list[tuple[list, int]]:
        """
        Sinh ra danh sách các dòng dữ liệu chuẩn 10 cột (A đến J) và tính toán công thức tương ứng.
        Cấu trúc mảng: [Col A, Col B (Tên chi phí), Col C, D, E, F, Col G (Tỷ lệ %), Col H, I, Col J (Thành tiền)]
        """
        c_r  = start_row + 1
        tt_r = start_row + 2
        tl_r = start_row + 3
        g_r  = start_row + 4
        gtgt_r = start_row + 5
        gxd_r  = start_row + 6
        lt_r   = start_row + 7
        total_r = start_row + 8

        rows = [
            (["", "Chi phí gián tiếp (C + TT)", "", "", "", "", "", "", "", f"=J{c_r}+J{tt_r}"], start_row),
            (["", "Chi phí chung (T x 20%)", "", "", "", "", "='Hệ số'!$C$4", "", "", f"=ROUND(J{self.t_row}*G{start_row+1}, 0)"], c_r),
            (["", "Chi phí công việc không xác định từ thiết kế", "", "", "", "", "='Hệ số'!$C$9", "", "", f"=ROUND(J{self.t_row}*G{start_row+2}, 0)"], tt_r),
            (["", "Thu nhập chịu thuế tính trước", "", "", "", "", "='Hệ số'!$C$8", "", "", f"=ROUND((J{self.t_row}+J{start_row})*G{start_row+3}, 0)"], tl_r),
            (["", "Chi phí trước thuế", "", "", "", "", "", "", "", f"=ROUND(J{self.t_row}+J{start_row}+J{start_row+3}, 0)"], g_r),
            (["", "Thuế giá trị gia tăng (VAT 8%)", "", "", "", "", "='Hệ số'!$C$10", "", "", f"=ROUND(J{g_r}*G{gtgt_r}, 0)"], gtgt_r),
            (["", "CHI PHÍ SAU THUẾ", "", "", "", "", "", "", "", f"=ROUND(J{g_r}+J{gtgt_r}, 0)"], gxd_r),
            (["", "Chi phí nhà tạm để ở và điều hành", "", "", "", "", "='Hệ số'!$C$6", "", "", f"=ROUND(J{g_r}*G{lt_r}*(1+'Hệ số'!$C$10), 0)"], lt_r),
            (["", "Tổng cộng đơn giá dự thầu 1 mẫu", "", "", "", "", "", "", "", f"=ROUND(J{gxd_r}+J{lt_r}, 0)"], total_r),
        ]
        return rows, total_r
    
    
#class tọa đọ giá: Class này sẽ nhận dữ liệu thô từ adapter một lần, tự động lập bản đồ (mapping) tọa độ, và cung cấp các hàm tra cứu sạch sẽ:
# backend/models/hieu_models_dto.py

# class PricingMappingManager:
#     """Class trung tâm: Đóng gói toàn bộ dữ liệu nguồn, bảng ánh xạ và logic bóc tách DTO sử dụng Composite Key."""
#     def __init__(self, mat_items: list, tools_items: list, equip_items: list):
#         def _normalize(items):
#             return [i if isinstance(i, dict) else {"name": str(i)} for i in (items or [])]

#         self.mat_items = _normalize(mat_items)
#         self.tools_items = _normalize(tools_items)
#         self.equip_items = _normalize(equip_items)

#         # Tự động lập bảng ánh xạ dòng (Row Mapping)
#         self.vl_row_mapping = {str(m.get('name', '')).lower().strip(): idx for idx, m in enumerate(self.mat_items, start=7)}
#         self.nc_row_mapping = {"nc_ldkt": 7, "nc_ldpt": 8}
#         self.tools_row_mapping = {str(t.get('name', '')).lower().strip(): idx for idx, t in enumerate(self.tools_items, start=7)}
#         self.eq_row_mapping = {str(e.get('name', '')).lower().strip(): idx for idx, e in enumerate(self.equip_items, start=7)}

#     def build_jobs(self, pakt_items: list, dinh_muc_composite_map: Optional[dict] = None) -> List['JobItemDTO']:
#         """Hàm bóc tách pakt_items thô thành danh sách JobItemDTO bằng cơ chế Composite Key chuẩn xác tuyệt đối."""
#         jobs_dtos = []
#         composite_map = dinh_muc_composite_map or {}

#         for idx, it in enumerate(pakt_items, start=1):
#             stt_str = str(idx)  # Cột STT tăng tiến liên tục 1, 2, 3...
#             name_str = it.get("thong_so", "Thông số quan trắc")
#             dvt_str  = it.get("dvt", "mẫu")
#             ma_gop   = it.get("ma_gop", f"P_{idx}")
#             tt20_data = it.get("tt20_data", {})
            
#             clean_ma_gop = ma_gop.replace("1", "").lower()
#             job_dto = JobItemDTO(stt=stt_str, code=ma_gop, name=name_str, unit=dvt_str, quantity=float(it.get("so_luong_mau", 1.0)))

#             for stage_key, stage_lbl in [('field', 'Ngoại nghiệp'), ('lab', 'Nội nghiệp'), ('single', 'Toàn phần')]:
#                 sub = tt20_data.get(stage_key)
#                 if not sub or not isinstance(sub, dict):
#                     continue

#                 # 1. Nhân công (NC)
#                 nc_norm = sub.get('dinh_muc_cong')
#                 nc_title = sub.get('dinh_bien') or f'Quan trắc viên ({stage_lbl})'
#                 if nc_norm and float(nc_norm) > 0:
#                     is_pt = ("phổ thông" in nc_title.lower() or "phụ việc" in nc_title.lower())
#                     target_row_nc = self.nc_row_mapping.get("nc_ldpt" if is_pt else "nc_ldkt", 7)
                    
#                     # Tra cứu qua Composite Key cho Nhân công
#                     nc_lookup_key = f"{clean_ma_gop}_nc_{nc_title.lower().strip()}"
#                     nc_row_idx = composite_map.get(nc_lookup_key)
#                     norm_val = f"='Dữ liệu định mức'!$G${nc_row_idx}" if nc_row_idx else float(nc_norm)
                    
#                     job_dto.add_detail("NC", DetailItemDTO(
#                         code=f"NC_{ma_gop}", sub_code="1", name=nc_title, unit="công",
#                         norm=norm_val, price_formula=f"='Nhân công'!$F${target_row_nc}", stage=stage_lbl
#                     ))

#                 # 2. Vật liệu (VL)
#                 for m_idx, m in enumerate(sub.get('materials', []), 1):
#                     m_name = m.get('name', '').strip()
#                     m_norm = float(m.get('norm') or 0.0)
#                     if m_norm > 0:
#                         target_row_vl = self.vl_row_mapping.get(m_name.lower().strip(), 7)
#                         norm_val = m_norm
                        
#                         # Tra cứu qua Composite Key cho Vật liệu
#                         vl_lookup_key = f"{clean_ma_gop}_vl_{m_name.lower().strip()}"
#                         print(f"DEBUG LOOKUP -> Đang tìm key: '{vl_lookup_key}' trong composite_map (Tổng số keys: {len(composite_map)})")
#                         vl_row_idx = composite_map.get(vl_lookup_key)
#                         if vl_row_idx:
#                             norm_val = f"='Dữ liệu định mức'!$G${vl_row_idx}"
                        
#                         job_dto.add_detail("VL", DetailItemDTO(
#                             code=f"VL_{ma_gop}", sub_code=str(m_idx), name=m_name, unit=m.get('unit', '').strip(),
#                             norm=norm_val, price_formula=f"='Vật liệu'!$F${target_row_vl}", stage=stage_lbl
#                         ))

#                 # 3. Công cụ dụng cụ (DC)
#                 for t_idx, t in enumerate(sub.get('tools', []), 1):
#                     t_norm = float(t.get('norm') or 0.0)
#                     t_name = t.get('name', 'Công cụ dụng cụ').strip()
#                     t_unit = t.get('unit', 'cái').strip()
#                     if t_norm > 0:
#                         target_row_t = self.tools_row_mapping.get(t_unit.lower().strip(), 7)
#                         norm_val = t_norm
                        
#                         # Tra cứu qua Composite Key cho Công cụ dụng cụ
#                         dc_lookup_key = f"{clean_ma_gop}_dc_{t_name.lower().strip()}"
#                         dc_row_idx = composite_map.get(dc_lookup_key)
#                         if dc_row_idx:
#                             norm_val = f"='Dữ liệu định mức'!$G${dc_row_idx}"
                        
#                         job_dto.add_detail("DC", DetailItemDTO(
#                             code=f"DC_{ma_gop}", sub_code=f"DC_{t_idx}", name=t_name, unit=t_unit,
#                             norm=norm_val, price_formula=f"='Công cụ dụng cụ'!$F${target_row_t}", stage=stage_lbl
#                         ))

#                 # 4. Máy thi công (M)
#                 for e_idx, e in enumerate(sub.get('equipment', []), 1):
#                     e_norm = float(e.get('norm') or 0.0)
#                     e_name = e.get('name', '').strip()
#                     if e_norm > 0:
#                         target_row_e = self.eq_row_mapping.get(e_name.lower().strip(), 7)
#                         norm_val = e_norm
                        
#                         # Tra cứu qua Composite Key cho Máy thi công
#                         m_lookup_key = f"{clean_ma_gop}_m_{e_name.lower().strip()}"
#                         m_row_idx = composite_map.get(m_lookup_key)
#                         if m_row_idx:
#                             norm_val = f"='Dữ liệu định mức'!$G${m_row_idx}"
                        
#                         job_dto.add_detail("M", DetailItemDTO(
#                             code=f"M_{ma_gop}", sub_code=f"M_{e_idx}", name=e_name, unit=e.get('unit', ''),
#                             norm=norm_val, price_formula=f"='Máy thi công'!$F${target_row_e}", stage=stage_lbl
#                         ))

#             jobs_dtos.append(job_dto)
#         return jobs_dtos

#excel style
class ExcelStyleManager:
    """Class chuyên biệt quản lý toàn bộ Styles, Fills, Fonts, Borders và Number Formats cho Excel."""
    def __init__(self):
        # Fonts
        self.font_title_15b  = Font(size=15, bold=True)
        self.font_sub_11i    = Font(size=11, italic=True)
        self.font_header_11b = Font(size=11, bold=True)
        self.font_sec_12b    = Font(size=12, bold=True)
        self.font_data_11r   = Font(size=11)
        self.font_data_11b   = Font(size=11, bold=True)

        # Fills (Màu nền)
        self.fill_header_gray = PatternFill("solid", fgColor="CCCCCC")
        self.fill_sub_gray    = PatternFill("solid", fgColor="EEEEEE")
        self.fill_total_pale  = PatternFill("solid", fgColor="FFF2CC")

        # Borders (Đường viền)
        thin_side = Side(style="thin")
        self.border_cell  = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)
        self.border_total = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)

        # Number Formats
        self.FMT_CURRENCY = '#,##0'
        self.FMT_NORM     = '0.000'
        self.FMT_PCT      = '0%'