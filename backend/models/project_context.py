# backend/models/project_context.py
from typing import Dict, Any

class ProjectContext:
    """
    Trung tâm quản lý tọa độ dòng và liên kết động toàn cục (Hub).
    Loại bỏ triệt để việc truyền tham số rời rạc và hard-code tọa độ ô trong Excel.
    """
    def __init__(self):
        self.he_so_rows: Dict[str, int] = {}      # Bảng tra tọa độ dòng Sheet Hệ số {"CP_QLC": 9, ...}
        self.item_ct_rows: Dict[int, int] = {}    # Bảng tra tọa độ công tác Sheet Công trình {idx: row}
        self.tot_ct_row: int = 276                # Dòng tổng cộng Sheet Công trình
        self.last_hp_row: int = 100               # Biên độ dòng Sheet Hao phí VT
        self.nc_parent_rows = {}     # NEW
        self.total_nc_row = 0        # NEW
        self.total_salary_row = 0    # NEW

    def register_he_so(self, rows: Dict[str, int]) -> None:
        """Đăng ký bảng tra tọa độ dòng từ Sheet Hệ số."""
        self.he_so_rows = rows

    def register_cong_trinh(self, rows: Dict[int, int], tot_row: int) -> None:
        """Đăng ký bảng tra dòng công tác và dòng tổng cộng từ Sheet Công trình."""
        self.item_ct_rows = rows
        self.tot_ct_row = tot_row

    def register_hao_phi(self, last_row: int) -> None:
        """Đăng ký biên độ dòng thực tế từ Sheet Hao phí VT."""
        self.last_hp_row = last_row

    def get_he_so_row(self, ma: str, fallback: int = 9) -> int:
        """Lấy chính xác tọa độ dòng Excel của mã hệ số tương ứng."""
        return self.he_so_rows.get(ma, fallback)
    