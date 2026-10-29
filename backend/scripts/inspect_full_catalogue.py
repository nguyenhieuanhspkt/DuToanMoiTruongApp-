import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 1. Load IB2600096765
with open(r"D:\TaskApp_kiet\DuToanMoiTruongApp\backend\data\kqlcnt_ib2600096765.json", "r", encoding="utf-8") as f:
    ib_data = json.load(f)

ib_items = ib_data["items"]
print(f"Total IB items: {len(ib_items)}")

# 2. Load Project Materials
with open(r"D:\TaskApp_kiet\DuToanMoiTruongApp\backend\data\material_pricing.json", "r", encoding="utf-8") as f:
    mat_data = json.load(f)
proj_materials = mat_data.get("items", [])

# 3. Load Project Tools
with open(r"D:\TaskApp_kiet\DuToanMoiTruongApp\backend\data\msc_lookup_tools.json", "r", encoding="utf-8") as f:
    tool_data = json.load(f)
proj_tools = tool_data.get("items", [])

# 4. Load Project Equipment
with open(r"D:\TaskApp_kiet\DuToanMoiTruongApp\backend\data\msc_lookup_equipment.json", "r", encoding="utf-8") as f:
    eq_data = json.load(f)
proj_eq = eq_data.get("items", [])

print(f"Project Materials: {len(proj_materials)}, Tools: {len(proj_tools)}, Equipment: {len(proj_eq)}")

def clean(s):
    if not s: return ""
    s = s.lower()
    s = re.sub(r'[\(\)\,\.\-\+\%\/\:\;]', ' ', s)
    return " ".join(s.split())

# Print all 182 IB items first so we can see the full catalogue
print("\n" + "="*80)
print("CATALOGUE OF 182 ITEMS IN IB2600096765 (NHIỆT ĐIỆN VĨNH TÂN 4):")
print("="*80)
for it in ib_items:
    print(f"STT {it['stt']:>3} | {it['name']:<35} | ĐVT: {it['dvt']:<6} | VAT 8%: {it['price_vat_8']:>12,.0f} đ | Trước thuế (/1.08): {it['price_pre_vat']:>12,.2f} đ | Hãng: {it['brand']} ({it['origin']})")
