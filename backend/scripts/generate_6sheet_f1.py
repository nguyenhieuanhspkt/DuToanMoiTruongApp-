import os
import sys
import shutil

sys.stdout.reconfigure(encoding='utf-8')

root_dir = r"D:\TaskApp_kiet\DuToanMoiTruongApp"
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.storage.onedrive_adapter import OneDriveAdapter
from backend.exporters.excel_6sheet_f1_exporter import Excel6SheetF1Exporter

adapter = OneDriveAdapter(root_dir)
items = adapter.load_pakt_items()
pricing = adapter.load_pricing_config()
mats = adapter.load_material_pricing()
tools = adapter.load_msc_tools()
eq = adapter.load_msc_equipment()
overhead = adapter.load_overhead_config()

out_file = os.path.join(root_dir, "backend", "data", "DU_TOAN_QUAN_TRAC_MOI_TRUONG_CHUAN_6_SHEET_F1.xlsx")
pub_file = os.path.join(root_dir, "frontend", "public", "DU_TOAN_QUAN_TRAC_MOI_TRUONG_CHUAN_6_SHEET_F1.xlsx")
onedrive_file = r"D:\onedrive_hieuna\OneDrive - EVN\Tổ Thẩm định\Hiếu\2026_DuToanMoiTruongApp\exports\DU_TOAN_QUAN_TRAC_MOI_TRUONG_CHUAN_6_SHEET_F1.xlsx"

print(f"Generating 6-Sheet F1 Replacement Workbook with {len(items)} items...")
Excel6SheetF1Exporter.export_workbook(
    pakt_items=items,
    pricing_config=pricing,
    materials_db=mats,
    tools_db=tools,
    equipment_db=eq,
    overhead_config=overhead,
    output_path=out_file
)

shutil.copy2(out_file, pub_file)
if os.path.exists(os.path.dirname(onedrive_file)):
    shutil.copy2(out_file, onedrive_file)

print(f"Generated successfully: {out_file} (Size: {os.path.getsize(out_file):,} bytes)")
print(f"Copied to public: {pub_file}")
print(f"Copied to OneDrive: {onedrive_file}")
