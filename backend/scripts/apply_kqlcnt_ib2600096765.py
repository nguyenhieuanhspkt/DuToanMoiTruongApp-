import json
import os
import sys
import shutil

sys.stdout.reconfigure(encoding='utf-8')

root_dir = r"D:\TaskApp_kiet\DuToanMoiTruongApp"
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
data_dir = os.path.join(root_dir, "backend", "data")
public_dir = os.path.join(root_dir, "frontend", "public")

# 1. Load IB2600096765
with open(os.path.join(data_dir, "kqlcnt_ib2600096765.json"), "r", encoding="utf-8") as f:
    ib_data = json.load(f)
ib_items = {str(it["stt"]).strip(): it for it in ib_data["items"]}

# 2. Load msc_lookup_materials.json
with open(os.path.join(data_dir, "msc_lookup_materials.json"), "r", encoding="utf-8") as f:
    msc_mat_data = json.load(f)
msc_items = msc_mat_data["items"]

# 3. Load material_pricing.json
with open(os.path.join(data_dir, "material_pricing.json"), "r", encoding="utf-8") as f:
    pricing_data = json.load(f)
pricing_items = pricing_data["items"]

# Mapping dictionary: stt in msc_lookup_materials -> (ib_stt, unit_price_pre_vat, note_text)
# Notice formula: pre_vat = vat_8_price / 1.08
updates = {
    # Aceton Lít (Chai 1000ml Merck: 399.600 -> 370.000)
    5: (88, 370000.0, "Acetone Merck tinh khiết 1000ml (Chai) trúng thầu 399.600 đ/1.08 = 370.000 đ/Lít"),
    # Aceton ml
    6: (88, 370.0, "Acetone Merck tinh khiết quy đổi 370.000 đ/1000ml = 370 đ/ml"),
    # Axit ascorbic gam (Merck 100g: 5.910.000 đ/chai -> 59.100 đ/gam)
    10: (68, 59100.0, "L(+)-Acid ascorbic Merck (Chai 100g) trúng thầu 6.382.800 đ/1.08 = 5.910.000 đ -> 59.100 đ/gam"),
    # Cồn lau dụng cụ lít (Methanol 99.8%: 43.200 đ/1.08 = 40.000 đ/lít)
    31: (32, 40000.0, "Methanol 99.8% trúng thầu 43.200 đ/1.08 = 40.000 đ/Lít"),
    32: (32, 40000.0, "Methanol 99.8% trúng thầu 43.200 đ/1.08 = 40.000 đ/Lít"),
    # Cồn lau dụng cụ / đầu đo ml
    33: (32, 40.0, "Methanol 99.8% quy đổi 40.000 đ/1000ml = 40 đ/ml"),
    34: (32, 40.0, "Methanol 99.8% quy đổi 40.000 đ/1000ml = 40 đ/ml"),
    # Dung dịch NH4+ chuẩn ml (NSI 500ml: 2.390.000 đ -> 4.780 đ/ml)
    36: (156, 4780.0, "Dung dịch chuẩn Amoni NSI (Chai 500ml) trúng thầu 2.581.200 đ/1.08 = 2.390.000 đ -> 4.780 đ/ml"),
    # Dung dịch chuẩn pH (pH=4 & pH=10) ml (Merck: (620.000+1.300.000)/2 = 960.000 đ/500ml -> 1.920 đ/ml)
    42: (119, 1920.0, "Dung dịch chuẩn pH 4 & 10 Merck trúng thầu 669.600 đ và 1.404.000 đ -> 1.920 đ/ml"),
    # Dung dịch chuẩn pH (pH=4, 7, 10) ml (Merck trung bình 853.333 đ/500ml -> 1.707 đ/ml)
    43: (118, 1707.0, "Dung dịch chuẩn pH 4, 7, 10 Merck trung bình 853.333 đ/chai 500ml -> 1.707 đ/ml"),
    # Dung dịch chuẩn pH hộp/chai (Merck trung bình 853.333 đ/chai)
    44: (118, 853333.0, "Dung dịch chuẩn pH Merck trúng thầu TB 921.600 đ/1.08 = 853.333 đ/chai"),
    # Dung dịch làm sạch điện cực ml (Toluen Merck 1000ml: 390.000 đ -> 390 đ/ml)
    45: (114, 390.0, "Toluen làm sạch hệ thống Merck trúng thầu 421.200 đ/1.08 = 390.000 đ/Lít -> 390 đ/ml"),
    # Dung dịch điện cực DO ml (Hanna 500ml: 600.000 đ -> 1.200 đ/ml)
    46: (159, 1200.0, "Dung dịch chuẩn DO Hanna trúng thầu 648.000 đ/1.08 = 600.000 đ/chai 500ml -> 1.200 đ/ml"),
    # EDTA gam (Merck 100g: 1.270.000 đ -> 12.700 đ/gam)
    48: (69, 12700.0, "Hóa chất EDTA Merck 100g trúng thầu 1.371.600 đ/1.08 = 1.270.000 đ -> 12.700 đ/gam"),
    49: (69, 1270.0, "Dung dịch EDTA quy đổi -> 1.270 đ/ml"),
    # FeCl3 gam (Vũ Hoàng 40%: 6.000 đ/kg -> 6 đ/gam)
    50: (14, 6.0, "Sắt (III) Clorua FeCl3 40% trúng thầu 6.480 đ/1.08 = 6.000 đ/kg -> 6 đ/gam"),
    51: (14, 6.0, "Sắt (III) Clorua FeCl3 40% trúng thầu 6.480 đ/1.08 = 6.000 đ/kg -> 6 đ/gam"),
    # HCl ml (Acid chlohydride 36-37% Merck 1000ml: 600.000 đ -> 600 đ/ml)
    80: (54, 600.0, "Acid chlohydride 36-37% Merck 1000ml trúng thầu 648.000 đ/1.08 = 600.000 đ -> 600 đ/ml"),
    # KCl gam (KCl 3M Merck: 620.000 đ/250ml -> 2.480 đ/gam)
    96: (53, 2480.0, "Dung dịch điện ly KCl 3M Merck trúng thầu 669.600 đ/1.08 = 620.000 đ/250ml -> 2.480 đ/gam"),
    # Khí Heli bình (99.99%: 10.141.200 đ/1.08 = 9.390.000 đ/bình)
    104: (124, 9390000.0, "Bình khí Heli 99.99% trúng thầu 10.141.200 đ/1.08 = 9.390.000 đ/bình"),
    # Khí Hydro bình (Air Liquide UHP: 21.621.600 đ/1.08 = 20.020.000 đ/bình)
    105: (130, 20020000.0, "Khí Hydrogen Ultra High Purity Air Liquide trúng thầu 21.621.600 đ/1.08 = 20.020.000 đ/bình"),
    # Khí Nitơ bình (Sovigaz 99.99%: 324.000 đ/1.08 = 300.000 đ/bình)
    106: (123, 300000.0, "Khí Nitơ 99.99% Sovigaz trúng thầu 324.000 đ/1.08 = 300.000 đ/bình"),
    # Khí Argon bình (Cryotech 99.9999%: 6.112.800 đ/1.08 = 5.660.000 đ/bình)
    107: (127, 5660000.0, "Bình khí Argon 99.9999% Cryotech trúng thầu 6.112.800 đ/1.08 = 5.660.000 đ/bình"),
    # Khí axetylen bình (Sovigaz 40 lít: 4.860.000 đ/1.08 = 4.500.000 đ/bình)
    108: (126, 4500000.0, "Bình khí Acetylen 40 lít Sovigaz trúng thầu 4.860.000 đ/1.08 = 4.500.000 đ/bình"),
    # Khí chuẩn CO bình (CO+CO2 Cryotech: 12.171.600 đ/1.08 = 11.270.000 đ/bình)
    109: (125, 11270000.0, "Bình khí CO+CO2 Cryotech trúng thầu 12.171.600 đ/1.08 = 11.270.000 đ/bình"),
    # Khí chuẩn NO bình (CSL: 37.141.200 đ/1.08 = 34.390.000 đ/bình)
    111: (141, 34390000.0, "Bình Khí NO CSL trúng thầu 37.141.200 đ/1.08 = 34.390.000 đ/bình"),
    # Khí chuẩn O2 bình (Calgaz: 9.871.200 đ/1.08 = 9.140.000 đ/bình)
    112: (133, 9140000.0, "Bình khí chuẩn Oxy Calgaz trúng thầu 9.871.200 đ/1.08 = 9.140.000 đ/bình"),
    # Khí chuẩn SO2 bình (CSL Span: 29.721.600 đ/1.08 = 27.520.000 đ/bình)
    113: (135, 27520000.0, "Bình và khí Span SO2 CSL trúng thầu 29.721.600 đ/1.08 = 27.520.000 đ/bình"),
    # NH3 ml (Amoniac 32% Merck 1000ml: 590.000 đ -> 590 đ/ml)
    121: (65, 590.0, "Dung dịch Amoniac 32% Merck trúng thầu 637.200 đ/1.08 = 590.000 đ/Lít -> 590 đ/ml"),
    # Na2CO3 gam (Soda Ash Light: 11.880 đ/1.08 = 11.000 đ/kg -> 11 đ/gam)
    125: (34, 11.0, "Sodium Carbonate Na2CO3 trúng thầu 11.880 đ/1.08 = 11.000 đ/kg -> 11 đ/gam"),
    126: (34, 11.0, "Sodium Carbonate Na2CO3 trúng thầu 11.880 đ/1.08 = 11.000 đ/kg -> 11 đ/gam"),
    # NaClO ml (Nước Javen NaClO: 8.640 đ/1.08 = 8.000 đ/kg -> 8 đ/ml)
    140: (19, 8.0, "Nước Javen NaClO Biên Hòa trúng thầu 8.640 đ/1.08 = 8.000 đ/kg -> 8 đ/ml"),
    # NaCl gam (Natri Clorua Merck 250g: 6.560.000 đ -> 26.240 đ/gam)
    141: (72, 26240.0, "Natri Clorua NaCl Merck 250g trúng thầu 7.084.800 đ/1.08 = 6.560.000 đ -> 26.240 đ/gam"),
    # NaOH gam (Natri hydroxit Merck 1000g: 1.080.000 đ -> 1.080 đ/gam)
    142: (70, 1080.0, "Natri hydroxit NaOH Merck 1000g trúng thầu 1.166.400 đ/1.08 = 1.080.000 đ -> 1.080 đ/gam"),
    143: (70, 1080.0, "Natri hydroxit NaOH Merck 1000g trúng thầu 1.166.400 đ/1.08 = 1.080.000 đ -> 1.080 đ/gam"),
    # Toluen Lít (Toluen Merck 1000ml: 390.000 đ/Lít)
    161: (114, 390000.0, "Toluen làm sạch hệ thống Merck trúng thầu 421.200 đ/1.08 = 390.000 đ/Lít"),
}

applied_count = 0
for it in msc_items:
    stt = it["stt"]
    if stt in updates:
        ib_stt, price_pre, note = updates[stt]
        ib_item = ib_items.get(str(ib_stt).strip())
        if ib_item:
            it["msc_unit_price"] = price_pre
            it["msc_tbmt_code"] = "IB2600096765"
            it["msc_approval_date"] = "03/04/2026"
            it["msc_contractor"] = f"{ib_item['brand']} ({ib_item['origin']})"
            it["msc_total_amount"] = round(it["quantity_with_waste"] * price_pre)
            it["note"] = f"KQLCNT Vĩnh Tân 4 IB2600096765 (VAT 8% -> chia 1.08): {note}"
            applied_count += 1

print(f"Applied updates to {applied_count} items in msc_lookup_materials!")

# Also update material_pricing.json
pricing_by_id = {it["id"]: it for it in pricing_items}
for it in msc_items:
    if it["stt"] in updates:
        p_item = pricing_by_id.get(it["id"])
        if p_item:
            p_item["approved_price"] = it["msc_unit_price"]
            p_item["approval_basis"] = "KQLCNT EVN Vĩnh Tân 4 IB2600096765 (Trước thuế = Giá VAT 8% / 1.08)"
            p_item["note"] = it["note"]

# Save updated JSONs
with open(os.path.join(data_dir, "msc_lookup_materials.json"), "w", encoding="utf-8") as f:
    json.dump(msc_mat_data, f, ensure_ascii=False, indent=2)

with open(os.path.join(data_dir, "material_pricing.json"), "w", encoding="utf-8") as f:
    json.dump(pricing_data, f, ensure_ascii=False, indent=2)

# Copy to frontend/public
shutil.copy2(os.path.join(data_dir, "msc_lookup_materials.json"), os.path.join(public_dir, "msc_lookup_materials.json"))
shutil.copy2(os.path.join(data_dir, "material_pricing.json"), os.path.join(public_dir, "material_pricing.json"))

print("Synchronized updated JSON files to backend/data and frontend/public.")

# Now re-generate Excel 10 Sheet
from backend.storage.onedrive_adapter import OneDriveAdapter
from backend.exporters.excel_exporter import Excel10SheetExporter

adapter = OneDriveAdapter(root_dir)
items = adapter.load_pakt_items()
pricing = adapter.load_pricing_config()
mats = adapter.load_material_pricing()
tools = adapter.load_msc_tools()
eq = adapter.load_msc_equipment()
overhead = adapter.load_overhead_config()

excel_out = os.path.join(data_dir, "DU_TOAN_QUAN_TRAC_MOI_TRUONG_2026_10_SHEET.xlsx")
excel_pub = os.path.join(public_dir, "DU_TOAN_QUAN_TRAC_MOI_TRUONG_2026_10_SHEET.xlsx")

Excel10SheetExporter.export_workbook(
    pakt_items=items,
    pricing_config=pricing,
    materials_db=mats,
    tools_db=tools,
    equipment_db=eq,
    overhead_config=overhead,
    output_path=excel_out
)

shutil.copy2(excel_out, excel_pub)
print(f"Re-exported Excel 10 Sheet successfully: {excel_out} and {excel_pub}")
