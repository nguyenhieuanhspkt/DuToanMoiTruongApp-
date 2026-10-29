import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r"D:\TaskApp_kiet\DuToanMoiTruongApp\backend\data\msc_lookup_materials.json", "r", encoding="utf-8") as f:
    d = json.load(f)

for it in d["items"]:
    print(f"{it['stt']:>3}. {it['name']:<35} | {it['unit']:<6}")
