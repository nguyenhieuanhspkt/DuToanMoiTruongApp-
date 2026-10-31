# backend/scripts/inspect_du_toan_values.py
import os
import sys
import win32com.client

root_dir = r"D:\TaskApp_kiet\DuToanMoiTruongApp"
file_path = os.path.join(root_dir, "output", "hieu_test_output.xlsx")

excel = win32com.client.DispatchEx("Excel.Application")
excel.Visible = False
excel.DisplayAlerts = False

try:
    wb = excel.Workbooks.Open(os.path.abspath(file_path))
    excel.Calculate()
    
    print("=== THDT HANG MUC (TỔNG HỢP DỰ TOÁN) ===")
    ws_thdt = wb.Sheets("THDT hạng mục")
    for r in range(5, 17):
        c1 = ws_thdt.Cells(r, 1).Text
        c2 = ws_thdt.Cells(r, 2).Text
        c3 = ws_thdt.Cells(r, 3).Text
        c5 = ws_thdt.Cells(r, 5).Text
        c6 = ws_thdt.Cells(r, 6).Text
        print(f"Row {r:2d} | {c1} | {c2} | {c3} | {c5} | {c6}")

    print("\n=== BẢNG CÔNG TRÌNH TỔNG HỢP (Row 276) ===")
    ws_ct = wb.Sheets("Công trình")
    r276 = 276
    vl_val = ws_ct.Cells(r276, 18).Value
    nc_val = ws_ct.Cells(r276, 19).Value
    dc_val = ws_ct.Cells(r276, 20).Value
    m_val  = ws_ct.Cells(r276, 21).Value
    total_val = ws_ct.Cells(r276, 22).Value
    print(f"Chi phí Vật liệu (R276):    {vl_val:,.0f} VNĐ ({ws_ct.Cells(r276, 18).Text})")
    print(f"Chi phí Nhân công (S276):   {nc_val:,.0f} VNĐ ({ws_ct.Cells(r276, 19).Text})")
    print(f"Chi phí Công cụ DC (T276):  {dc_val:,.0f} VNĐ ({ws_ct.Cells(r276, 20).Text})")
    print(f"Chi phí Máy TC (U276):      {m_val:,.0f} VNĐ ({ws_ct.Cells(r276, 21).Text})")
    if total_val:
        print(f"Tổng Chi phí trực tiếp:     {total_val:,.0f} VNĐ ({ws_ct.Cells(r276, 22).Text})")

    print("\n=== TOP 10 CÔNG TÁC CÓ GIÁ TRỊ LỚN NHẤT TRONG BẢNG CÔNG TRÌNH ===")
    jobs = []
    for r in range(7, 276):
        stt = ws_ct.Cells(r, 1).Text
        code = ws_ct.Cells(r, 2).Text
        name = ws_ct.Cells(r, 4).Text
        unit = ws_ct.Cells(r, 5).Text
        qty  = ws_ct.Cells(r, 12).Value or 0.0
        unit_price = ws_ct.Cells(r, 17).Value or 0.0
        total_price = ws_ct.Cells(r, 22).Value or 0.0
        vl_sub = ws_ct.Cells(r, 18).Value or 0.0
        nc_sub = ws_ct.Cells(r, 19).Value or 0.0
        dc_sub = ws_ct.Cells(r, 20).Value or 0.0
        m_sub  = ws_ct.Cells(r, 21).Value or 0.0
        jobs.append({
            "stt": stt, "code": code, "name": name, "unit": unit,
            "qty": qty, "unit_price": unit_price, "total": total_price,
            "vl": vl_sub, "nc": nc_sub, "dc": dc_sub, "m": m_sub
        })

    jobs.sort(key=lambda x: x["total"], reverse=True)
    for idx, j in enumerate(jobs[:10], start=1):
        print(f"#{idx} [STT {j['stt']}] {j['code']} - {j['name'][:50]}")
        print(f"    KL: {j['qty']} {j['unit']} | Đơn giá: {j['unit_price']:,.0f} đ | Thành tiền: {j['total']:,.0f} VNĐ")
        print(f"    -> VL: {j['vl']:,.0f} | NC: {j['nc']:,.0f} | DC: {j['dc']:,.0f} | M: {j['m']:,.0f}")

    print("\n=== CHI TIẾT KHOẢN 4.5 TT20 (TỔNG = 1.004.575.120 VNĐ) ===")
    ws_45 = wb.Sheets("Khoản 4.5 TT20")
    for r in range(6, 25):
        c1 = ws_45.Cells(r, 1).Text
        c2 = ws_45.Cells(r, 2).Text
        c3 = ws_45.Cells(r, 3).Text
        cJ = ws_45.Cells(r, 10).Text
        cK = ws_45.Cells(r, 11).Text
        print(f"Row {r:2d} | {c1:4s} | {c2:55s} | {c3:8s} | Tiền (Col J): {cJ:>15s} | Ghi chú: {cK}")

    print("\n=== TOP VẬT LIỆU CHI PHÍ CAO NHẤT TRONG SHEET VẬT LIỆU ===")
    ws_vl = wb.Sheets("Vật liệu")
    vl_list = []
    for r in range(7, ws_vl.UsedRange.Rows.Count + 1):
        c1 = ws_vl.Cells(r, 1).Text.strip()
        if c1.isdigit():
            v_code = ws_vl.Cells(r, 2).Text
            v_name = ws_vl.Cells(r, 3).Text
            v_unit = ws_vl.Cells(r, 4).Text
            try:
                v_qty  = float(ws_vl.Cells(r, 6).Value or 0.0)
            except:
                v_qty = 0.0
            try:
                v_price = float(ws_vl.Cells(r, 7).Value or 0.0)
            except:
                v_price = 0.0
            try:
                v_total = float(ws_vl.Cells(r, 8).Value or 0.0)
            except:
                v_total = 0.0
            v_note = ws_vl.Cells(r, 9).Text
            vl_list.append({
                "code": v_code, "name": v_name, "unit": v_unit,
                "qty": v_qty, "price": v_price, "total": v_total, "note": v_note
            })
    vl_list.sort(key=lambda x: x["total"], reverse=True)
    for idx, v in enumerate(vl_list[:10], start=1):
        print(f"#{idx} {v['code']} - {v['name']} ({v['unit']}): KL={v['qty']:,.2f} x Đơn giá={v['price']:,.0f} = {v['total']:,.0f} VNĐ | {v['note'][:40]}")

    print("\n=== TOP DỤNG CỤ VÀ MÁY THI CÔNG TRONG TÍNH GIÁ CA MÁY ===")
    ws_cm = wb.Sheets("Tính giá ca máy")
    cm_list = []
    for r in range(6, ws_cm.UsedRange.Rows.Count + 1):
        c1 = ws_cm.Cells(r, 1).Text.strip()
        if c1.isdigit():
            m_code = ws_cm.Cells(r, 2).Text
            m_name = ws_cm.Cells(r, 3).Text
            m_unit = ws_cm.Cells(r, 4).Text
            try:
                m_orig = float(ws_cm.Cells(r, 5).Value or 0.0)
            except:
                m_orig = 0.0
            try:
                m_rate = float(ws_cm.Cells(r, 15).Value or 0.0)
            except:
                m_rate = 0.0
            m_note = ws_cm.Cells(r, 16).Text
            cm_list.append({
                "code": m_code, "name": m_name, "unit": m_unit,
                "orig": m_orig, "rate": m_rate, "note": m_note
            })
    cm_list.sort(key=lambda x: x["orig"], reverse=True)
    print("--- Top 5 thiết bị/máy có nguyên giá cao nhất ---")
    for idx, m in enumerate(cm_list[:5], start=1):
        print(f"#{idx} {m['code']} - {m['name']}: Nguyên giá={m['orig']:,.0f} đ -> Đơn giá ca={m['rate']:,.0f} đ/ca | {m['note'][:40]}")

    print("\n=== KIỂM TRA MỤC CÓ GIÁ = 0 HOẶC CẦN LƯU Ý ===")
    zero_vl = [v for v in vl_list if v["price"] == 0]
    print(f"Số lượng vật liệu có đơn giá = 0: {len(zero_vl)}")
    for zv in zero_vl[:5]:
        print(f"   - {zv['code']} {zv['name']}")

    wb.Close(False)
finally:
    excel.Quit()
