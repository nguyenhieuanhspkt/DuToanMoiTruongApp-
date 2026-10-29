import os
from typing import List, Dict, Any, Optional
from backend.storage.atomic_writer import AtomicWriter
from backend.models.pakt_item import PaktItem, PricingConfig, OverheadConfig

class OneDriveAdapter:
    """
    Adapter interfacing between DuToanMoiTruongApp, Git Local Repo and EVN OneDrive storage.
    Supports smart 2-tier fallback:
    1. Primary: EVN OneDrive path if available (D:\\onedrive_hieuna\\...)
    2. Fallback: Internal Git repository storage (backend/data/)
    Guarantees 100% standalone execution when cloning or pulling on an office machine!
    """
    DEFAULT_ONEDRIVE_DATA_DIR = r"D:\onedrive_hieuna\OneDrive - EVN\Tổ Thẩm định\Hiếu\2026_DuToanMoiTruongApp\data"
    REPO_BACKEND_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

    def __init__(self, data_dir: Optional[str] = None):
        self.repo_dir = self.REPO_BACKEND_DATA_DIR
        os.makedirs(self.repo_dir, exist_ok=True)

        if data_dir and os.path.exists(data_dir):
            self.primary_dir = data_dir
        elif os.environ.get("ONEDRIVE_DATA_DIR") and os.path.exists(os.environ.get("ONEDRIVE_DATA_DIR")):
            self.primary_dir = os.environ.get("ONEDRIVE_DATA_DIR")
        elif os.path.exists(self.DEFAULT_ONEDRIVE_DATA_DIR):
            self.primary_dir = self.DEFAULT_ONEDRIVE_DATA_DIR
        else:
            self.primary_dir = self.repo_dir

        self.data_dir = self.primary_dir

    def _resolve_read_path(self, filename: str) -> str:
        """Kiểm tra tệp tại primary_dir trước, nếu không có thì fallback sang repo_dir."""
        primary_path = os.path.join(self.primary_dir, filename)
        if os.path.exists(primary_path):
            return primary_path
        repo_path = os.path.join(self.repo_dir, filename)
        if os.path.exists(repo_path):
            return repo_path
        return primary_path

    def _write_dual(self, filename: str, data: Any) -> None:
        """Ghi đồng thời vào cả repo_dir (để Git quản lý) và primary_dir (OneDrive)."""
        repo_path = os.path.join(self.repo_dir, filename)
        AtomicWriter.write_json(repo_path, data)
        if self.primary_dir != self.repo_dir and os.path.exists(self.primary_dir):
            try:
                primary_path = os.path.join(self.primary_dir, filename)
                AtomicWriter.write_json(primary_path, data)
            except Exception as e:
                print(f"Warning: Could not sync to OneDrive {self.primary_dir}: {e}")

    def load_pakt_items(self) -> List[Dict[str, Any]]:
        target_path = self._resolve_read_path("pakt_253_items.json")
        if not os.path.exists(target_path):
            return []
        return AtomicWriter.read_json(target_path)

    def save_pakt_items(self, items: List[Dict[str, Any]]) -> None:
        self._write_dual("pakt_253_items.json", items)

    def load_pricing_config(self) -> Dict[str, Any]:
        target_path = self._resolve_read_path("pricing_config.json")
        if not os.path.exists(target_path):
            default_config = {
                "labor_rates": {
                    "Quan trắc viên tài nguyên môi trường hạng II": 850000,
                    "Quan trắc viên tài nguyên môi trường hạng III.1": 650000,
                    "Quan trắc viên tài nguyên môi trường hạng III.2": 550000,
                    "Quan trắc viên tài nguyên môi trường hạng III.3": 450000,
                    "Quan trắc viên tài nguyên môi trường hạng IV": 450000,
                    "Kỹ thuật viên / Lao động phổ thông": 350000
                },
                "currency": "VND",
                "source": "Văn bản số 5691/EVN-MTPTBV ngày 06/10/2026 và Quyết định số 1155/QĐ-NĐVT4",
                "legal_bases": [
                    "Thông tư liên tịch số 56/2015/TTLT-BTNMT-BNV ngày 08/12/2015",
                    "Nghị định số 161/2026/NĐ-CP ngày 15/5/2026 (Mức lương cơ sở 2.530.000 đồng/tháng từ 01/7/2026)",
                    "Văn bản số 5691/EVN-MTPTBV ngày 06/10/2026 của Tập đoàn Điện lực Việt Nam",
                    "Quyết định số 1155/QĐ-NĐVT4 của NMNĐ Vĩnh Tân 4"
                ]
            }
            self._write_dual("pricing_config.json", default_config)
            return default_config

        data = AtomicWriter.read_json(target_path)
        # Tự động đồng bộ khóa labor_rates nếu tệp cũ chỉ có labor_rates_3072
        if "labor_rates" not in data and "labor_rates_3072" in data:
            data["labor_rates"] = data["labor_rates_3072"]
            if "Quan trắc viên tài nguyên môi trường hạng III.3" not in data["labor_rates"]:
                data["labor_rates"]["Quan trắc viên tài nguyên môi trường hạng III.3"] = 450000
            data["source"] = "Văn bản số 5691/EVN-MTPTBV ngày 06/10/2026 và Quyết định số 1155/QĐ-NĐVT4"
            data["legal_bases"] = [
                "Thông tư liên tịch số 56/2015/TTLT-BTNMT-BNV ngày 08/12/2015",
                "Nghị định số 161/2026/NĐ-CP ngày 15/5/2026 (Mức lương cơ sở 2.530.000 đồng/tháng từ 01/7/2026)",
                "Văn bản số 5691/EVN-MTPTBV ngày 06/10/2026 của Tập đoàn Điện lực Việt Nam",
                "Quyết định số 1155/QĐ-NĐVT4 của NMNĐ Vĩnh Tân 4"
            ]
            self._write_dual("pricing_config.json", data)
        return data

    def save_pricing_config(self, config: Dict[str, Any]) -> None:
        self._write_dual("pricing_config.json", config)

    def load_overhead_config(self) -> Dict[str, Any]:
        target_path = self._resolve_read_path("overhead_config.json")
        if not os.path.exists(target_path):
            return {}
        return AtomicWriter.read_json(target_path)

    def save_overhead_config(self, config: Dict[str, Any]) -> None:
        self._write_dual("overhead_config.json", config)

    def load_tt20_norm_database(self) -> Dict[str, Any]:
        target_path = self._resolve_read_path("tt20_norm_database.json")
        if not os.path.exists(target_path):
            return {}
        return AtomicWriter.read_json(target_path)

    def get_tt20_sections_summary(self) -> List[Dict[str, Any]]:
        db = self.load_tt20_norm_database()
        sections = db.get("sections", {})
        summary = []
        for sec_id, data in sections.items():
            summary.append({
                "section_id": sec_id,
                "section_title": data.get("section_title"),
                "slug": data.get("slug"),
                "total_parameters": data.get("total_parameters", 0),
                "legal_basis": data.get("legal_basis")
            })
        return summary

    def lookup_tt20_parameter(self, code: str) -> Optional[Dict[str, Any]]:
        db = self.load_tt20_norm_database()
        idx = db.get("parameter_index", {})
        param_summary = idx.get(code)
        if not param_summary:
            return None
        sec_id = param_summary.get("section_id")
        sections = db.get("sections", {})
        sec_data = sections.get(sec_id, {})
        full_param = sec_data.get("parameters", {}).get(code)
        return {
            "section_id": sec_id,
            "section_title": sec_data.get("section_title"),
            "parameter": full_param
        }

    def load_material_pricing(self) -> Dict[str, Any]:
        path = self._resolve_read_path('material_pricing.json')
        if not os.path.exists(path):
            return {'metadata': {'total_items': 0}, 'items': []}
        return AtomicWriter.read_json(path)

    def save_material_pricing(self, pricing_db: Dict[str, Any]) -> None:
        self._write_dual('material_pricing.json', pricing_db)

    def load_msc_tools(self) -> Dict[str, Any]:
        path = self._resolve_read_path('msc_lookup_tools.json')
        if not os.path.exists(path):
            return {'metadata': {'total': 0}, 'items': []}
        return AtomicWriter.read_json(path)

    def save_msc_tools(self, data: Dict[str, Any]) -> None:
        self._write_dual('msc_lookup_tools.json', data)

    def load_msc_equipment(self) -> Dict[str, Any]:
        path = self._resolve_read_path('msc_lookup_equipment.json')
        if not os.path.exists(path):
            return {'metadata': {'total': 0}, 'items': []}
        return AtomicWriter.read_json(path)

    def save_msc_equipment(self, data: Dict[str, Any]) -> None:
        self._write_dual('msc_lookup_equipment.json', data)

    def load_msc_materials(self) -> Dict[str, Any]:
        path = self._resolve_read_path('msc_lookup_materials.json')
        if not os.path.exists(path):
            return {'metadata': {'total': 0}, 'items': []}
        return AtomicWriter.read_json(path)

    def save_msc_materials(self, data: Dict[str, Any]) -> None:
        self._write_dual('msc_lookup_materials.json', data)
