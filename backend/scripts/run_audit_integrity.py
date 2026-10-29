import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Load PAKT items
with open(r'D:\TaskApp_kiet\DuToanMoiTruongApp\backend\data\pakt_253_items.json', 'r', encoding='utf-8') as f:
    pakt = json.load(f)

audit_report = {
    "total_work_items": len(pakt),
    "unique_norm_codes": 0,
    "code_breakdown": {},
    "total_expected_resource_records": 0,
    "distinct_materials_count": 0,
    "distinct_tools_count": 0,
    "distinct_equipment_count": 0
}

all_materials = {}
all_tools = {}
all_equipment = {}
unique_codes = {}

for it in pakt:
    tt = it.get('tt20_data')
    if not tt:
        continue
    code = tt.get('coreCode') or it.get('thong_so')
    if code not in unique_codes:
        unique_codes[code] = {
            "name": it.get('thong_so'),
            "labor_count": 0,
            "materials_count": 0,
            "tools_count": 0,
            "equipment_count": 0,
            "total_records": 0
        }
        for stage_key in ['field', 'lab', 'single']:
            sub = tt.get(stage_key)
            if not sub:
                continue
            if sub.get('dinh_muc_cong') is not None or sub.get('labor'):
                unique_codes[code]["labor_count"] += 1
            mats = sub.get('materials') or []
            unique_codes[code]["materials_count"] += len(mats)
            for m in mats:
                m_name = m.get('name', '').strip()
                all_materials[m_name] = all_materials.get(m_name, 0) + 1
            tools = sub.get('tools') or []
            unique_codes[code]["tools_count"] += len(tools)
            for t in tools:
                t_name = t.get('name', '').strip()
                all_tools[t_name] = all_tools.get(t_name, 0) + 1
            eqs = sub.get('equipment') or []
            unique_codes[code]["equipment_count"] += len(eqs)
            for e in eqs:
                e_name = e.get('name', '').strip()
                all_equipment[e_name] = all_equipment.get(e_name, 0) + 1
                
        unique_codes[code]["total_records"] = (
            unique_codes[code]["labor_count"] +
            unique_codes[code]["materials_count"] +
            unique_codes[code]["tools_count"] +
            unique_codes[code]["equipment_count"]
        )

total_res = sum(c["total_records"] for c in unique_codes.values())

print(f"=== KẾT QUẢ TỰ KIỂM TRA ĐỐI SOÁT DỮ LIỆU ĐỊNH MỨC ===")
print(f"1. Tổng số dòng công việc (PAKT): {len(pakt)} dòng")
print(f"2. Số mã định mức TT20 độc lập được áp dụng: {len(unique_codes)} mã")
print(f"3. Tổng số record hao phí định mức chuẩn: {total_res} records")
print(f"   - Số loại vật liệu/hóa chất duy nhất cần có ở Sheet Vật liệu: {len(all_materials)} loại")
print(f"   - Số loại CCDC duy nhất cần có ở Sheet Công cụ dụng cụ: {len(all_tools)} loại")
print(f"   - Số loại Thiết bị duy nhất cần có ở Sheet Máy thi công: {len(all_equipment)} loại")
print(f"\n--- MẪU ĐỐI SOÁT 5 MÃ ĐỊNH MỨC TIÊU BIỂU ---")
for k in list(unique_codes.keys())[:5]:
    c = unique_codes[k]
    print(f"Mã [{k}] {c['name']}: {c['total_records']} record hao phí ({c['labor_count']} NC + {c['materials_count']} VL + {c['tools_count']} CCDC + {c['equipment_count']} Máy)")
