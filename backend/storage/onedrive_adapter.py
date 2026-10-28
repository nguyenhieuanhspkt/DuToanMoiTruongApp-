import os
from typing import List, Dict, Any, Optional
from backend.storage.atomic_writer import AtomicWriter
from backend.models.pakt_item import PaktItem, PricingConfig, OverheadConfig

class OneDriveAdapter:
    """
    Adapter interfacing between DuToanMoiTruongApp and EVN OneDrive cache storage.
    Default path: D:\\onedrive_hieuna\\OneDrive - EVN\\Tổ Thẩm định\\Hiếu\\2026_DuToanMoiTruongApp\\data
    """
    DEFAULT_ONEDRIVE_DATA_DIR = r"D:\onedrive_hieuna\OneDrive - EVN\Tổ Thẩm định\Hiếu\2026_DuToanMoiTruongApp\data"

    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = data_dir or self.DEFAULT_ONEDRIVE_DATA_DIR
        self.pakt_items_path = os.path.join(self.data_dir, "pakt_253_items.json")
        self.pricing_config_path = os.path.join(self.data_dir, "pricing_config.json")
        self.overhead_config_path = os.path.join(self.data_dir, "overhead_config.json")
        os.makedirs(self.data_dir, exist_ok=True)

    def load_pakt_items(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.pakt_items_path):
            return []
        return AtomicWriter.read_json(self.pakt_items_path)

    def save_pakt_items(self, items: List[Dict[str, Any]]) -> None:
        AtomicWriter.write_json(self.pakt_items_path, items)

    def load_pricing_config(self) -> Dict[str, Any]:
        if not os.path.exists(self.pricing_config_path):
            return {
                "labor_rates_3072": {
                    "Quan trắc viên tài nguyên môi trường hạng II": 850000,
                    "Quan trắc viên tài nguyên môi trường hạng III.1": 650000,
                    "Quan trắc viên tài nguyên môi trường hạng III.2": 550000,
                    "Quan trắc viên tài nguyên môi trường hạng IV": 450000,
                    "Kỹ thuật viên / Lao động phổ thông": 350000
                },
                "currency": "VND",
                "source": "Văn bản số 3072/EVN-MTPTBV ngày 31/5/2026"
            }
        return AtomicWriter.read_json(self.pricing_config_path)

    def save_pricing_config(self, config: Dict[str, Any]) -> None:
        AtomicWriter.write_json(self.pricing_config_path, config)

    def load_overhead_config(self) -> Dict[str, Any]:
        if not os.path.exists(self.overhead_config_path):
            return {
                "indirect_cost_rate": 0.15,
                "contingency_rate": 0.05,
                "vat_rate": 0.08
            }
        return AtomicWriter.read_json(self.overhead_config_path)
