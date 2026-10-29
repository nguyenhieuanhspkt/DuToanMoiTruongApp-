import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r"D:\TaskApp_kiet\DuToanMoiTruongApp\backend\data\msc_lookup_materials.json", "r", encoding="utf-8") as f:
    d = json.load(f)

for i, it in enumerate(d["items"]):
    print(f"{i+1:>3}. {it['name']:<50} | {it['unit']:<8} | Hiện tại: {it['msc_unit_price']:>10,.0f} đ | {it['msc_tbmt_code']}")
