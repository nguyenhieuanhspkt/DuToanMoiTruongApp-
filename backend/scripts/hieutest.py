# hieutest.py
import sys
import os
root_dir = r"D:\TaskApp_kiet\DuToanMoiTruongApp"
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# 1. Gọi DTO Models từ file hieu_models_dto
from backend.models.hieu_models_dto import JobItemDTO, SubtotalGroupDTO, DetailItemDTO

# 2. Gọi Exporter từ file hieu_exporter
from backend.exporters.excel_f1_full_replica_exporter import ExcelF1FullReplicaExporter
from backend.storage.onedrive_adapter import OneDriveAdapter

def run_test():
    # Dữ liệu giả lập PAKT items
    adapter = OneDriveAdapter(root_dir)
    items = adapter.load_pakt_items()
    pakt_items = items

    # Gọi Exporter xuất file
    output_path = "output/hieu_test_output.xlsx"
    ExcelF1FullReplicaExporter.export_workbook(
        pakt_items=pakt_items,
        pricing_config={},
        materials_db={},
        tools_db={},
        equipment_db={},
        overhead_config={},
        output_path=output_path
    )
    print(f"Xuất file thành công tại: {output_path}")

if __name__ == "__main__":
    run_test()