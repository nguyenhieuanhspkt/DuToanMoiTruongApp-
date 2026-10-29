import json
import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')

with open(r"D:\TaskApp_kiet\DuToanMoiTruongApp\backend\data\kqlcnt_ib2600096765.json", "r", encoding="utf-8") as f:
    ib_data = json.load(f)
ib_items = ib_data["items"]

print("="*110)
print(f"KẾT QUẢ LỰA CHỌN NHÀ THẦU - MÃ GÓI THẦU: IB2600096765 (NHÀ MÁY NHIỆT ĐIỆN VĨNH TÂN 4)")
print(f"Thuế suất VAT: 8%  ==>  Công thức đơn giá trước thuế = Đơn giá trúng thầu / 1.08")
print("="*110)

for it in ib_items:
    stt = it['stt']
    name = it['name']
    code = it['code']
    dvt = it['dvt']
    vat = it['price_vat_8']
    pre = it['price_pre_vat']
    brand = it['brand']
    origin = it['origin']
    print(f"STT {stt:>3} | {name:<42} | ĐVT: {dvt:<6} | VAT 8%: {vat:>12,.0f} đ | Trước thuế (/1.08): {pre:>12,.2f} đ | {brand} ({origin})")
