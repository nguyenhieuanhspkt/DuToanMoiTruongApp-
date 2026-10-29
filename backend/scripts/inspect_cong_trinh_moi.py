import openpyxl
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

path = r"D:\onedrive_hieuna\OneDrive - EVN\Tổ Thẩm định\Năm 2026\Thẩm định 345_hieuna\Cong trinh moi.xlsm"
wb = openpyxl.load_workbook(path, data_only=False)

sheets_to_inspect = [
    'Công trình', 'Hao phí VT', 'Vật liệu', 'Nhân công', 
    'Công cụ dụng cụ', 'Máy thi công', 'Đơn giá chi tiết', 
    'THDT hạng mục', 'Lương nhân công', 'Tính giá ca máy'
]

print("="*100)
print(f"PHÂN TÍCH FORMAT, ĐỊNH DẠNG SỐ & TRÌNH BÀY FILE: {os.path.basename(path)}")
print("="*100)

for sname in sheets_to_inspect:
    if sname not in wb.sheetnames:
        continue
    ws = wb[sname]
    print(f"\n--- SHEET: [{sname}] (Max Row: {ws.max_row}, Max Col: {ws.max_column}) ---")
    
    # Check sheet views / gridlines
    try:
        gridlines = ws.views.sheetView[0].showGridLines
    except:
        gridlines = "Default"
    print(f"Show Gridlines: {gridlines}")
    
    # Analyze row heights & first 15 rows
    row_formats = []
    num_formats_seen = set()
    fonts_seen = set()
    fills_seen = set()
    
    for r in range(1, min(25, ws.max_row + 1)):
        row_vals = []
        for c in range(1, min(15, ws.max_column + 1)):
            cell = ws.cell(r, c)
            val = cell.value
            nf = cell.number_format
            num_formats_seen.add(nf)
            
            f = cell.font
            if f:
                f_desc = f"{f.name} {f.size}pt {'B' if f.bold else ''} {'I' if f.italic else ''} {f.color.rgb if f.color and hasattr(f.color, 'rgb') else ''}".strip()
                fonts_seen.add(f_desc)
                
            fill = cell.fill
            if fill and fill.fill_type:
                fill_color = fill.start_color.rgb if fill.start_color and hasattr(fill.start_color, 'rgb') else fill.fill_type
                fills_seen.add(str(fill_color))
                
            if val is not None:
                row_vals.append(f"C{c}[{nf}]: {str(val)[:30]}")
        if row_vals:
            print(f"Row {r:>2} (h={ws.row_dimensions[r].height}): " + " | ".join(row_vals[:6]))
            
    print(f"\n>> Number formats detected in [{sname}]: {num_formats_seen}")
    print(f">> Distinct Fonts: {list(fonts_seen)[:6]}")
    print(f">> Fill Colors: {fills_seen}")
