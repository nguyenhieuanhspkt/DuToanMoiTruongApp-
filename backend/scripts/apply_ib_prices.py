import json
import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')

# Load files
with open(r"D:\TaskApp_kiet\DuToanMoiTruongApp\backend\data\kqlcnt_ib2600096765.json", "r", encoding="utf-8") as f:
    ib_data = json.load(f)
ib_items = ib_data["items"]

with open(r"D:\TaskApp_kiet\DuToanMoiTruongApp\backend\data\msc_lookup_materials.json", "r", encoding="utf-8") as f:
    msc_mat_data = json.load(f)
msc_materials = msc_mat_data.get("items", [])

with open(r"D:\TaskApp_kiet\DuToanMoiTruongApp\backend\data\material_pricing.json", "r", encoding="utf-8") as f:
    mat_pricing_data = json.load(f)
mat_pricing_items = mat_pricing_data.get("items", [])

print(f"Loaded {len(ib_items)} items from IB2600096765.")
print(f"Loaded {len(msc_materials)} items from msc_lookup_materials.json.")

# Let's create high-confidence direct mappings between project materials and IB2600096765 items
# We examine each project material name and find the exact or closest chemical counterpart in IB2600096765
mapping_rules = [
    # (regex or keyword pattern in project material name, ib_stt, unit_conversion_factor_if_needed, note)
    # Note: unit in project might be ml, gam, lít, chai, bình...
    ("Aceton", 88, 1.0, "Acetone Merck tinh khiết phân tích 1000ml (Chai) -> Đơn giá chai: 370.000 đ"),
    ("EDTA", 69, 1.0, "Hóa chất EDTA Merck 100g (Chai) -> Đơn giá chai: 1.270.000 đ"),
    ("FeCl3", 14, 1.0, "Sắt (III) Clorua FeCl3 40% (Kg) -> 6.000 đ/kg"),
    ("Axit clohydric|Axit clorhydric|HCl", 54, 1.0, "Acid chlohydride 36-37% Merck (Chai) -> 600.000 đ/chai; công nghiệp: 2.500 đ/kg"),
    ("Natri hydroxit|NaOH", 70, 1.0, "Natri hydroxit NaOH Merck 1kg (Chai) -> 1.080.000 đ/chai"),
    ("Natri Clorua|NaCl", 72, 1.0, "Natri Clorua NaCl Merck 250g (Chai) -> 6.560.000 đ/chai"),
    ("Kali Clorua|KCl", 53, 1.0, "Dung dịch điện ly KCl 3M Merck 250ml (Chai) -> 620.000 đ/chai"),
    ("Dung dịch chuẩn pH ở giá trị pH = 4|chuẩn pH 4", 119, 1.0, "Dung dịch chuẩn pH 4.00 Merck (Chai) -> 620.000 đ/chai"),
    ("Dung dịch chuẩn pH.*7|chuẩn pH 7", 118, 1.0, "Dung dịch chuẩn pH 7.00 Merck (Chai) -> 640.000 đ/chai"),
    ("Dung dịch chuẩn pH.*10|chuẩn pH 10", 120, 1.0, "Dung dịch chuẩn pH 10.00 Merck (Chai) -> 1.300.000 đ/chai"),
    ("Dung dịch chuẩn pH", 118, 1.0, "Dung dịch chuẩn pH Merck (Chai) -> 640.000 đ/chai"),
    ("COD.*nước biển|COD.*thang đo", 115, 1.0, "Thuốc thử COD Hach (Hộp) -> 3.500.000 đ/hộp"),
    ("Dung dịch chuẩn COD|COD Standard", 102, 1.0, "COD Standard Solution Merck 100mg/l (Chai) -> 1.250.000 đ/chai"),
    ("Cồn|Ethanol", 93, 1.0, "Ethanol C2H5OH Merck 1000ml (Chai) -> 670.000 đ/chai"),
    ("Methanol", 32, 1.0, "Methanol 99.8% (Lít) -> 40.000 đ/lít"),
    ("Khí Heli", 124, 1.0, "Bình khí Heli 99.99% -> 9.390.000 đ/bình"),
    ("Khí Hydro|Hydrogen", 130, 1.0, "Khí Hydrogen Ultra High Purity Air Liquide -> 20.020.000 đ/bình"),
    ("Khí Nitơ", 123, 1.0, "Khí Nitơ 99.99% Sovigaz -> 300.000 đ/bình"),
    ("Khí argon", 127, 1.0, "Bình khí Argon 99.9999% Cryotech -> 5.660.000 đ/bình"),
    ("Khí Acetylen", 126, 1.0, "Bình khí Acetylen 40 lít Sovigaz -> 4.500.000 đ/bình"),
    ("Khí chuẩn CO|CO\+CO2", 125, 1.0, "Bình khí CO+CO2 Cryotech -> 11.270.000 đ/bình"),
    ("Khí chuẩn NO", 141, 1.0, "Bình khí NO CSL -> 34.390.000 đ/bình"),
    ("Khí Oxy|chuẩn Oxy", 121, 1.0, "Khí Oxy Sovigaz -> 214.500 đ/bình"),
    ("Khí chuẩn SO2|khí Span", 135, 1.0, "Bình và khí Span CSL -> 27.520.000 đ/bình"),
    ("Khí Zero", 139, 1.0, "Bình và khí Zero trộn CSL -> 16.890.000 đ/bình"),
    ("Dung dịch chuẩn Amoni", 156, 1.0, "Dung dịch chuẩn Amoni NSI (Mỹ) -> 2.390.000 đ/chai"),
    ("Dung dịch chuẩn DO", 159, 1.0, "Dung dịch chuẩn DO Hanna -> 600.000 đ/chai"),
    ("Dung dịch chuẩn.*Clo|tổng Clo", 160, 1.0, "Dung dịch chuẩn Clo dư NSI -> 4.390.000 đ/hộp"),
    ("Dung dịch chuẩn Sulfua", 162, 1.0, "Dung dịch chuẩn Sulfua VKN -> 7.600.000 đ/chai"),
    ("Dung dịch chuẩn độ đục", 169, 1.0, "Dung dịch chuẩn độ đục NSI -> 4.580.000 đ/chai"),
    ("Dung dịch chuẩn độ dẫn điện", 171, 1.0, "Dung dịch chuẩn độ dẫn điện Inorganic Ventures -> 3.140.000 đ/chai"),
    ("Dung dịch chuẩn ORP", 176, 1.0, "Dung dịch chuẩn ORP Hanna -> 930.000 đ/chai"),
    ("Dung dịch chuẩn Silica", 62, 1.0, "Dung dịch chuẩn Silica Hach -> 2.000.000 đ/chai"),
    ("Dung dịch chuẩn sắt", 58, 1.0, "Dung dịch chuẩn sắt Hach -> 1.470.000 đ/chai"),
    ("Dung dịch chuẩn kẽm", 59, 1.0, "Dung dịch chuẩn kẽm Hach -> 1.230.000 đ/chai"),
    ("Dung dịch chuẩn đồng", 60, 1.0, "Dung dịch chuẩn đồng Hach -> 1.240.000 đ/chai"),
    ("Dung dịch chuẩn Nitơ", 57, 1.0, "Dung dịch chuẩn Nitơ Hach -> 1.140.000 đ/chai"),
    ("Dung dịch Amoniac", 65, 1.0, "Dung dịch Amoniac 32% Merck -> 590.000 đ/chai"),
    ("Citric acid|Citric axit", 66, 1.0, "Hóa chất Citric axit monohydrate Merck -> 2.460.000 đ/chai"),
    ("Acid ascorbic|Axit ascorbic", 68, 1.0, "Dung dịch L(+)-Acid ascorbic Merck -> 5.910.000 đ/chai"),
    ("Acid formic|Axit formic", 71, 1.0, "Hóa chất Acid formic 90% Merck -> 2.890.000 đ/chai"),
    ("PAC", 15, 1.0, "Hóa chất PAC 10% Long An Phát -> 6.100 đ/kg"),
    ("Javen|Javel", 19, 1.0, "Nước Javen NaClO Biên Hòa -> 8.000 đ/kg"),
    ("Sodium Carbonate|Na2CO3", 34, 1.0, "Sodium Carbonate Na2CO3 -> 11.000 đ/kg"),
    ("Dung dịch làm sạch điện cực", 114, 1.0, "Hóa chất làm sạch Toluen Merck -> 390.000 đ/chai"),
]

# Find matches in project materials
applied_count = 0
updated_items = []

ib_by_stt = {it["stt"]: it for it in ib_items}

for p in msc_materials:
    p_name = p.get("name", "")
    p_unit = p.get("unit", "")
    matched = False
    for pat, ib_stt, factor, note in mapping_rules:
        if re.search(pat, p_name, re.IGNORECASE):
            ib_item = ib_by_stt.get(ib_stt)
            if ib_item:
                p["msc_source"] = "KQLCNT EVN Vĩnh Tân 4 (IB2600096765)"
                p["tbmt_code"] = "IB2600096765"
                p["approval_date"] = "03/04/2026"
                p["winning_bidder"] = f"{ib_item['brand']} ({ib_item['origin']})"
                p["winning_price_vat_8"] = ib_item["price_vat_8"]
                p["unit_price_pre_vat"] = ib_item["price_pre_vat"]
                p["unit_price"] = ib_item["price_pre_vat"]
                p["note"] = f"{note} (Quy đổi trước thuế: {ib_item['price_vat_8']:,.0f}/1.08)"
                applied_count += 1
                matched = True
                updated_items.append({
                    "material_name": p_name,
                    "unit": p_unit,
                    "ib_item_name": ib_item["name"],
                    "brand": ib_item["brand"],
                    "origin": ib_item["origin"],
                    "price_vat_8": ib_item["price_vat_8"],
                    "price_pre_vat": ib_item["price_pre_vat"]
                })
                break

print(f"\nSuccessfully mapped and updated {applied_count} materials with IB2600096765!")
for u in updated_items[:20]:
    print(f"- {u['material_name']} ({u['unit']})")
    print(f"  -> IB2600096765: {u['ib_item_name']} | Hãng: {u['brand']} ({u['origin']})")
    print(f"  -> Giá trúng thầu (VAT 8%): {u['price_vat_8']:,.0f} đ | Đơn giá trước thuế (/1.08): {u['price_pre_vat']:,.2f} đ\n")
