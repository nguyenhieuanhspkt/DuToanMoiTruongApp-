import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\TaskApp_kiet\DuToanMoiTruongApp\backend\data\pakt_253_items.json', 'r', encoding='utf-8') as f:
    pakt = json.load(f)

print(f"Total items in PAKT: {len(pakt)}")

# Let's see how many items have tt20_data
with_tt = [it for it in pakt if it.get('tt20_data')]
print(f"Items with tt20_data: {len(with_tt)}")

# Inspect first 5 items
for i in range(5):
    it = pakt[i]
    tt = it.get('tt20_data') or {}
    ts = it.get('thong_so')
    cc = tt.get('coreCode')
    fld = tt.get('field') or {}
    lab = tt.get('lab') or {}
    print(f"Item {i+1}: {ts} (Code: {cc})")
    print(f"  Field: labor={fld.get('labor')}, mats={len(fld.get('materials', []))}, tools={len(fld.get('tools', []))}, equip={len(fld.get('equipment', []))}")
    print(f"  Lab:   labor={lab.get('labor')}, mats={len(lab.get('materials', []))}, tools={len(lab.get('tools', []))}, equip={len(lab.get('equipment', []))}")
