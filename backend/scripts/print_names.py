import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r"D:\TaskApp_kiet\DuToanMoiTruongApp\backend\data\msc_lookup_materials.json", "r", encoding="utf-8") as f:
    d = json.load(f)

for i, it in enumerate(d["items"][:20]):
    print(f"{i+1:>2}. {it['name']} ({it['unit']})")
