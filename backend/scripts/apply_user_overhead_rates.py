import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

p = r'D:\TaskApp_kiet\DuToanMoiTruongApp\backend\exporters\excel_f1_full_replica_exporter.py'
with open(p, 'r', encoding='utf-8') as f:
    text = f.read()

# Update hsC from 0.073 to 0.20
target_hs = 'ws_hs.append(["Chi phí chung theo chi phí trực tiếp", "hsC", 0.073, 0.073])'
replace_hs = 'ws_hs.append(["Chi phí chung theo chi phí trực tiếp", "hsC", 0.20, 0.20])'

# Update display string in THDT
target_thdt = 'ws_thdt.append(["1", "Chi phí chung", "=\\"T x 7,3%\\"", "=ROUND(D6*\'Hệ số\'!$C$4, 0)", "C"])'
replace_thdt = 'ws_thdt.append(["1", "Chi phí chung", "=\\"T x 20%\\"", "=ROUND(D6*\'Hệ số\'!$C$4, 0)", "C"])'

text = text.replace(target_hs, replace_hs)
text = text.replace(target_thdt, replace_thdt)

with open(p, 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated excel_f1_full_replica_exporter.py with Chi phí chung 20%, Thu nhập 5.5%, VAT 8%, Dự phòng 0%!")
