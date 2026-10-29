import json
import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')

def remove_accents(input_str):
    if not input_str: return ""
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def clean(s):
    if not s: return ""
    s = s.lower()
    s = remove_accents(s)
    s = re.sub(r'[^a-z0-9\s]', ' ', s)
    return " ".join(s.split())

# 1. Load IB2600096765
with open(r"D:\TaskApp_kiet\DuToanMoiTruongApp\backend\data\kqlcnt_ib2600096765.json", "r", encoding="utf-8") as f:
    ib_data = json.load(f)
ib_items = ib_data["items"]

# 2. Load Project Materials
with open(r"D:\TaskApp_kiet\DuToanMoiTruongApp\backend\data\material_pricing.json", "r", encoding="utf-8") as f:
    mat_data = json.load(f)
proj_materials = mat_data.get("items", [])

print(f"Loaded {len(ib_items)} IB items and {len(proj_materials)} project materials.")

matches = []
for p in proj_materials:
    p_name = p.get("name", "")
    p_code = p.get("code", "")
    p_unit = p.get("unit", "")
    p_price = p.get("unit_price", 0)
    p_norm = clean(p_name)
    p_words = set(p_norm.split()) - {"va", "trong", "cua", "cho", "dung", "dich", "chuan", "hoa", "chat"}
    
    best_candidate = None
    best_score = 0
    
    for ib in ib_items:
        ib_name = ib.get("name", "")
        ib_code = ib.get("code", "")
        ib_tech = ib.get("tech", "")
        full_ib_text = f"{ib_name} {ib_code} {ib_tech}"
        ib_norm = clean(full_ib_text)
        ib_words = set(ib_norm.split())
        
        # Word overlap
        common = p_words.intersection(ib_words)
        score = len(common)
        
        # Exact chemical match keywords
        # e.g., axit clohydric / hcl, natri hydroxit / naoh, axit sunfuric / h2so4, amoni / nh4, do, clo, sulfua, pac...
        if p_norm in clean(ib_name) or clean(ib_name) in p_norm:
            score += 5
            
        if score > best_score and score >= 2:
            best_score = score
            best_candidate = ib
            
    if best_candidate and best_score >= 2:
        matches.append({
            "project_code": p_code,
            "project_name": p_name,
            "project_unit": p_unit,
            "current_price": p_price,
            "ib_stt": best_candidate["stt"],
            "ib_name": best_candidate["name"],
            "ib_code": best_candidate["code"],
            "ib_brand": best_candidate["brand"],
            "ib_origin": best_candidate["origin"],
            "ib_dvt": best_candidate["dvt"],
            "ib_price_vat": best_candidate["price_vat_8"],
            "ib_price_pre_vat": best_candidate["price_pre_vat"],
            "score": best_score
        })

print(f"\nFound {len(matches)} matched items with project materials!")
print("="*100)
for m in matches[:35]:
    print(f"[{m['project_code']}] {m['project_name']} ({m['project_unit']}) - Đơn giá cũ: {m['current_price']:,.0f}")
    print(f"  --> MATCH: STT {m['ib_stt']} - {m['ib_name']} [{m['ib_code']}] ({m['ib_dvt']})")
    print(f"      Hãng/Xuất xứ: {m['ib_brand']} ({m['ib_origin']})")
    print(f"      Giá trúng thầu VAT 8%: {m['ib_price_vat']:,.0f} đ  ==>  Giá trước thuế (/1.08): {m['ib_price_pre_vat']:,.2f} đ\n")
