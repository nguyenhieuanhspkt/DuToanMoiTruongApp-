import openpyxl
import sys
import os
import re

sys.stdout.reconfigure(encoding='utf-8')

path = r"D:\onedrive_hieuna\OneDrive - EVN\Tổ Thẩm định\Năm 2026\Thẩm định 345_hieuna\Cong trinh moi.xlsm"
wb = openpyxl.load_workbook(path, data_only=False)

print("="*100)
print("PHÂN TÍCH TOÀN DIỆN KIẾN TRÚC SHEET & CƠ CHẾ LIÊN KẾT Ô TRONG 'Cong trinh moi.xlsm'")
print("="*100)

print(f"Tổng số sheet: {len(wb.sheetnames)}")
print("Danh sách sheet:", wb.sheetnames)

# Inspect links across sheets
sheet_links = {}

for sname in wb.sheetnames:
    ws = wb[sname]
    formula_count = 0
    ref_sheets = set()
    sample_formulas = []
    
    for r in range(1, min(100, ws.max_row + 1)):
        for c in range(1, min(25, ws.max_column + 1)):
            v = ws.cell(r, c).value
            if isinstance(v, str) and v.startswith('='):
                formula_count += 1
                # Find referenced sheet names
                # e.g., 'Công trình'!A1 or Vật liệu!B2
                matches = re.findall(r"'([^']+)'!|[A-Za-z0-9_À-ỹ]+!", v)
                for m in matches:
                    cleaned_m = m.replace("!", "").strip()
                    if cleaned_m and cleaned_m != sname and cleaned_m in wb.sheetnames:
                        ref_sheets.add(cleaned_m)
                if len(sample_formulas) < 5:
                    sample_formulas.append(f"{ws.cell(r, c).coordinate}: {v}")
                    
    sheet_links[sname] = {
        "formula_count": formula_count,
        "ref_sheets": list(ref_sheets),
        "samples": sample_formulas
    }

print("\n" + "="*100)
print("MA TRẬN LIÊN KẾT GIỮA CÁC SHEET:")
print("="*100)
for sname, info in sheet_links.items():
    if info["formula_count"] > 0:
        print(f"\nSheet [{sname}] (Chứa {info['formula_count']} công thức):")
        print(f"  -> Nhận dữ liệu từ: {info['ref_sheets']}")
        print(f"  -> Mẫu công thức tiêu biểu:")
        for sm in info["samples"]:
            print(f"     * {sm}")
