import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\TaskApp_kiet\DuToanMoiTruongApp\backend\data\pakt_253_items.json', 'r', encoding='utf-8') as f:
    pakt = json.load(f)

# Analyze norm codes and distinct resources
all_codes = set()
total_labor_records = 0
distinct_materials = set()
total_mat_records = 0
distinct_tools = set()
total_tool_records = 0
distinct_equip = set()
total_equip_records = 0

for it in pakt:
    tt = it.get('tt20_data')
    if not tt:
        continue
    code = tt.get('coreCode') or it.get('thong_so')
    all_codes.add(code)
    
    for stage_key in ['field', 'lab', 'single']:
        sub = tt.get(stage_key)
        if not sub:
            continue
        # labor
        if sub.get('labor'):
            total_labor_records += 1
        # materials
        mats = sub.get('materials') or []
        total_mat_records += len(mats)
        for m in mats:
            distinct_materials.add(m.get('name'))
        # tools
        tools = sub.get('tools') or []
        total_tool_records += len(tools)
        for t in tools:
            distinct_tools.add(t.get('name'))
        # equip
        eqs = sub.get('equipment') or []
        total_equip_records += len(eqs)
        for e in eqs:
            distinct_equip.add(e.get('name'))

print(f"1. Tổng số dòng công tác: {len(pakt)}")
print(f"2. Số mã định mức TT20 duy nhất xuất hiện: {len(all_codes)}")
print(f"3. Tổng số lượt bóc tách hao phí theo định mức:")
print(f"   - Lượt hao phí Nhân công: {total_labor_records}")
print(f"   - Lượt hao phí Vật liệu: {total_mat_records} (Ứng với {len(distinct_materials)} loại vật liệu/hóa chất duy nhất)")
print(f"   - Lượt hao phí CCDC: {total_tool_records} (Ứng với {len(distinct_tools)} loại dụng cụ duy nhất)")
print(f"   - Lượt hao phí Thiết bị: {total_equip_records} (Ứng với {len(distinct_equip)} loại thiết bị duy nhất)")
print(f"   -> TỔNG CỘNG SỐ DÒNG BÓC TÁCH HAO PHÍ CHUẨN XÁC: {total_labor_records + total_mat_records + total_tool_records + total_equip_records} dòng")
