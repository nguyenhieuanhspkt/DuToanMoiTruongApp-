import os
import sys
import shutil

sys.stdout.reconfigure(encoding='utf-8')

root_dir = r"D:\TaskApp_kiet\DuToanMoiTruongApp"
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.storage.onedrive_adapter import OneDriveAdapter
from backend.exporters.excel_f1_full_replica_exporter import ExcelF1FullReplicaExporter

adapter = OneDriveAdapter(root_dir)
items = adapter.load_pakt_items()
pricing = adapter.load_pricing_config()
mats = adapter.load_material_pricing()
tools = adapter.load_msc_tools()
eq = adapter.load_msc_equipment()
overhead = adapter.load_overhead_config()

out_file = os.path.join(root_dir, "backend", "data", "DU_TOAN_QUAN_TRAC_MOI_TRUONG_CHUAN_F1_100PCT.xlsx")
pub_file = os.path.join(root_dir, "frontend", "public", "DU_TOAN_QUAN_TRAC_MOI_TRUONG_CHUAN_F1_100PCT.xlsx")
onedrive_file = r"D:\onedrive_hieuna\OneDrive - EVN\Tổ Thẩm định\Hiếu\2026_DuToanMoiTruongApp\exports\DU_TOAN_QUAN_TRAC_MOI_TRUONG_CHUAN_F1_100PCT.xlsx"

print(f"Generating 100% F1 Replica Workbook for EVN Vinh Tan 4 ({len(items)} items)...")
ExcelF1FullReplicaExporter.export_workbook(
    pakt_items=items,
    pricing_config=pricing,
    materials_db=mats,
    tools_db=tools,
    equipment_db=eq,
    overhead_config=overhead,
    output_path=out_file
)

try:
    import win32com.client
    ex = win32com.client.DispatchEx("Excel.Application")
    ex.Visible = False
    ex.DisplayAlerts = False
    wb = ex.Workbooks.Open(os.path.abspath(out_file))
    ex.CalculateFull()
    wb.Save()
    wb.Close()
    ex.Quit()
    print("Pre-calculated all Excel formula values via Excel Engine.")
except Exception as e:
    print(f"Notice: Formula evaluation skipped ({e}).")

shutil.copy2(out_file, pub_file)
print(f"Copied to public: {pub_file}")

targets = [
    onedrive_file,
    r"D:\onedrive_hieuna\OneDrive - EVN\Tổ Thẩm định\Năm 2026\Thẩm định 345_hieuna\DU_TOAN_QUAN_TRAC_MOI_TRUONG_CHUAN_F1_100PCT.xlsx",
    r"D:\onedrive_hieuna\OneDrive - EVN\Tổ Thẩm định\Năm 2026\Thẩm định 345_hieuna\Thông tư 20\So_Hoa_Tung_Hoc_Phan\DU_TOAN_QUAN_TRAC_MOI_TRUONG_CHUAN_F1_100PCT.xlsx"
]

for target in targets:
    try:
        if os.path.exists(os.path.dirname(target)):
            shutil.copy2(out_file, target)
            print(f"Copied to: {target}")
    except PermissionError:
        alt = target.replace('.xlsx', '_CapNhatMoi.xlsx')
        try:
            shutil.copy2(out_file, alt)
            print(f"File chính đang mở trong Excel, đã lưu bản cập nhật tại: {alt}")
        except Exception as e:
            print(f"Warning: {e}")
    except Exception as e:
        print(f"Error copying to {target}: {e}")

print(f"Generated successfully: {out_file} (Size: {os.path.getsize(out_file):,} bytes)")
