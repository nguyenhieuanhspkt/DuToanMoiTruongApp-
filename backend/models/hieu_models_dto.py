# backend/models/dutoan_dto.py
from typing import List, Dict, Any, Optional


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


class DetailItemDTO:
    """DTO đại diện cho một thành phần hao phí chi tiết (Cấp 2: Vật liệu, Nhân công, Máy...)"""
    def __init__(self, code: str, sub_code: str, name: str, unit: str, norm: float, price_formula: str, stage: str = ""):
        self.code = code          # Mã hiệu (ví dụ: VL_TT20_001)
        self.sub_code = sub_code  # STT hoặc mã phụ (ví dụ: VL_001)
        self.name = name          # Tên thành phần
        self.unit = unit          # Đơn vị tính
        self.norm = norm          # Định mức tiêu hao
        self.price_formula = price_formula  # Công thức link đơn giá (ví dụ: ='Vật liệu'!$F$7)
        self.stage = stage        # Giai đoạn (Ngoại nghiệp, Nội nghiệp...)

    def to_row_data(self, current_row: int) -> List[Any]:
        display_name = f" - {self.name} ({self.stage})" if self.stage else f" - {self.name}"
        return [
            "",                 # STT (trống cho dòng con)
            self.code,          # Mã hiệu
            self.sub_code,      # STT thành phần (Cột C)
            "",                 # Mã hiệu VL/NC/M (Cột D)
            display_name,       # Tên hao phí (Cột E)
            self.unit,          # Đơn vị
            self.norm,          # Định mức (Cột G)
            self.price_formula, # Đơn giá (Cột H)
            1.0,                # Hệ số (Cột I)
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

    def to_row_data(self) -> List[Any]:
        # Tự sinh hàm SUM dựa trên dải dòng thực tế của các item con bên trong nhóm
        formula_sum = f"=SUM(J{self.start_child_row}:J{self.end_child_row})" if self.items else "0"
        return [
            "", "", "", self.group_name, "", "", "", "", "", formula_sum
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