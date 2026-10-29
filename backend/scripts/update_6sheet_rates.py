import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

p = r'D:\TaskApp_kiet\DuToanMoiTruongApp\backend\exporters\excel_6sheet_f1_exporter.py'
with open(p, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('=ROUND(0.15 * E5, 0)', '=ROUND(0.20 * E5, 0)')
text = text.replace('=ROUND(0.06 * (E5 + E6), 0)', '=ROUND(0.055 * (E5 + E6), 0)')
text = text.replace('=ROUND(0.05 * (E5 + E6 + E7), 0)', '=ROUND(0.00 * (E5 + E6 + E7), 0)')

with open(p, 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated excel_6sheet_f1_exporter.py successfully!")
