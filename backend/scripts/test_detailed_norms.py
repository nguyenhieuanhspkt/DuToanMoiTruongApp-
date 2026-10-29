import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\TaskApp_kiet\DuToanMoiTruongApp\backend\data\pakt_253_items.json', 'r', encoding='utf-8') as f:
    pakt = json.load(f)

# Inspect COD (NB16a) and TSS (NB17a)
for it in pakt:
    ts = it.get('thong_so', '')
    if ts in ['COD', 'TSS', 'Nhiệt độ', 'Tiếng ồn']:
        tt = it.get('tt20_data') or {}
        print(f"\n==================================================")
        print(f"CÔNG TÁC: {ts} | MÃ HIỆU: {tt.get('coreCode')} | ĐVT: {it.get('dvt')}")
        print(f"==================================================")
        for stage_key, stage_lbl in [('field', 'NGOẠI NGHIỆP'), ('lab', 'NỘI NGHIỆP'), ('single', 'TOÀN PHẦN')]:
            sub = tt.get(stage_key)
            if not sub:
                continue
            print(f"--- Giai đoạn: {stage_lbl} ---")
            if sub.get('dinh_muc_cong'):
                print(f"  [NC] {sub.get('dinh_bien', 'Quan trắc viên')} | Định mức: {sub.get('dinh_muc_cong')} công")
            for m in sub.get('materials', []):
                print(f"  [VL] {m.get('name')} | ĐVT: {m.get('unit')} | Định mức: {m.get('norm')}")
            for t in sub.get('tools', []):
                print(f"  [DC] {t.get('name')} | ĐVT: {t.get('unit')} | Định mức: {t.get('norm')}")
            for e in sub.get('equipment', []):
                print(f"  [MÁY] {e.get('name')} | ĐVT: {e.get('unit')} | Định mức: {e.get('norm')}")
