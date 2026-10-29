import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

p = r'D:\TaskApp_kiet\DuToanMoiTruongApp\backend\scripts\generate_f1_100pct.py'
with open(p, 'r', encoding='utf-8') as f:
    text = f.read()

old_code = '''    shutil.copy2(out_file, onedrive_file)
    print(f"Copied to OneDrive: {onedrive_file}")'''

new_code = '''    try:
        shutil.copy2(out_file, onedrive_file)
        print(f"Copied to OneDrive: {onedrive_file}")
    except Exception as e:
        alt_file = onedrive_file.replace('.xlsx', '_CapNhatMoi.xlsx')
        try:
            shutil.copy2(out_file, alt_file)
            print(f"File chính đang mở trong Excel, đã lưu bản mới tại: {alt_file}")
        except Exception:
            print(f"Warning OneDrive: {e}")'''

if old_code in text:
    text = text.replace(old_code, new_code)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(text)
    print('Updated generate_f1_100pct.py successfully!')
else:
    print('Target not found in generate_f1_100pct.py')
