import os
import sys
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

file_path = r'D:\TaskApp_kiet\DuToanMoiTruongApp\backend\exporters\excel_f1_full_replica_exporter.py'

# Read original exporter
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

# Let's inspect where sheet 6, 8, 9 and 10 are defined
sheet6_marker = "# SHEET 6: 'Vật liệu'"
sheet10_marker = "# SHEET 10: 'THDT hạng mục'"

idx6 = code.find(sheet6_marker)
idx10 = code.find(sheet10_marker)

print(f"Sheet 6 at {idx6}, Sheet 10 at {idx10}")
