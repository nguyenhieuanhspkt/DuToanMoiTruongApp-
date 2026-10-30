# scripts/test_hieu_exporter.py
import os
import sys

# Đưa thư mục gốc của project vào sys.path để import nội bộ
root_dir = r"D:\TaskApp_kiet\DuToanMoiTruongApp"
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.storage.onedrive_adapter import OneDriveAdapter
from backend.exporters.hieu_exporter import export_full_du_toan

def inspect_real_pakt_items(pakt_items):
    """Hàm phụ giúp in cấu trúc chi tiết của 3 item đầu tiên để kiểm tra key dữ liệu thật."""
    print(f"\n🔍 Tổng số công tác quan trắc (pakt_items): {len(pakt_items)}")
    for idx, item in enumerate(pakt_items[:3], start=1):
        print(f"\n--- [PAKT Item #{idx}] ---")
        if isinstance(item, dict):
            for k, v in item.items():
                print(f"  Key: '{k}' -> Type: {type(v).__name__} | Sample: {str(v)[:100]}")
        else:
            print(f"  Item type: {type(item).__name__} | Value: {item}")

def run_test():
    print("=== BẮT ĐẦU CHẠY SCRIPT TEST EXPORTER ===")

    # 1. Tải dữ liệu từ OneDrive Adapter
    adapter = OneDriveAdapter(root_dir)
    pakt_items = adapter.load_pakt_items()
    # inspect_real_pakt_items(pakt_items)
    
    mats = adapter.load_material_pricing()
    tools = adapter.load_msc_tools()
    eq = adapter.load_msc_equipment()
    
    mat_items = mats if isinstance(mats, list) else list(mats.values()) if isinstance(mats, dict) else []
    tools_items = tools if isinstance(tools, list) else list(tools.values()) if isinstance(tools, dict) else []
    equip_items = eq if isinstance(eq, list) else list(eq.values()) if isinstance(eq, dict) else []

    # 2. Gọi hàm điều phối trung tâm để xây dựng toàn bộ Workbook hoàn chỉnh
    wb, ws_result = export_full_du_toan(
        root_dir=root_dir,
        pakt_items=pakt_items,
        mat_items=mat_items,
        tools_items=tools_items,
        equip_items=equip_items
    )
    
    # 3. Lưu file kết quả ra thư mục output
    out_dir = os.path.join(root_dir, 'output')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'hieu_test_output.xlsx')
    wb.save(out_path)
    print(f"✅ Xuất file thành công tại: {os.path.abspath(out_path)}")

if __name__ == "__main__":
    run_test()