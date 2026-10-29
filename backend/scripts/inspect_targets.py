import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r"D:\TaskApp_kiet\DuToanMoiTruongApp\backend\data\msc_lookup_materials.json", "r", encoding="utf-8") as f:
    msc_data = json.load(f)
msc_items = msc_data["items"]

with open(r"D:\TaskApp_kiet\DuToanMoiTruongApp\backend\data\kqlcnt_ib2600096765.json", "r", encoding="utf-8") as f:
    ib_data = json.load(f)
ib_items = ib_data["items"]

# Find which items in msc_lookup_materials correspond to our chemicals
keywords = [
    "Aceton", "EDTA", "FeCl3", "clohydric", "NaOH", "NaCl", "KCl", 
    "pH", "COD", "Cồn", "Ethanol", "Methanol", "Heli", "Hydro", 
    "Nitơ", "argon", "Acetylen", "CO", "NO", "Oxy", "SO2", "Span", "Zero", 
    "Amoni", "DO", "Clo", "Sulfua", "độ đục", "độ dẫn điện", "ORP", 
    "Silica", "sắt", "kẽm", "đồng", "Nitrat", "Amoniac", "Citric", 
    "ascorbic", "formic", "PAC", "Javen", "Na2CO3", "điện cực"
]

print("Checking items in msc_lookup_materials matching target chemicals:")
matched_indices = []
for idx, it in enumerate(msc_items):
    name = it["name"]
    for kw in keywords:
        if re.search(r'\b' + re.escape(kw), name, re.IGNORECASE):
            matched_indices.append((idx, it, kw))
            break

print(f"Total target items found in project: {len(matched_indices)}")
for idx, it, kw in matched_indices[:30]:
    print(f"Idx {idx:>3} | STT {it['stt']:>3} | {it['name']:<40} | ĐVT: {it['unit']:<6} | Giá hiện tại: {it['msc_unit_price']:>10,.0f} đ | Ghi chú: {it.get('note','')}")
