import sys

sys.stdout.reconfigure(encoding='utf-8')

plan_path = r"D:\TaskApp_kiet\DuToanMoiTruongApp\PLAN_DU_AN.md"

with open(plan_path, "r", encoding="utf-8") as f:
    content = f.read()

target = "---" + "\n\n" + "## 📅 VI. LỘ TRÌNH TRIỂN KHAI DỰ ÁN CHI TIẾT"

addition = """---

## 🎯 V.B. MỤC TIÊU CẦN ĐẠT ĐƯỢC CỦA FILE EXCEL DỰ TOÁN (CHUẨN 6 SHEET THAY THẾ PHẦN MỀM F1)
*(Yêu cầu kỹ thuật then chốt giải quyết bài toán không có phần mềm chuyên dụng F1: Minh bạch, Tự động hóa 100%, Kiểm soát triệt để quy tắc chống trùng lặp)*

### 1. Kiến Trúc 6 Sheet Chuẩn Mực Trong File Excel Dự Toán:
1. **Sheet `DM_DinhMuc_TT20` (Cơ sở dữ liệu định mức gốc):**
   * Lưu trữ toàn bộ định mức kinh tế - kỹ thuật theo Thông tư 20/2017/TT-BTNMT cho từng mã hiệu thông số.
   * Cột chính: `STT` | `Mã hiệu TT20` | `Tên thông số & Công đoạn` | `Phân loại (Ngoại/Nội nghiệp)` | `ĐVT` | `Hao phí Ngày công (H_NC)` | `Hao phí Vật liệu/Hóa chất (H_VL)` | `Hao phí Dụng cụ (H_DC)` | `Hao phí Ca máy (H_TB)`.
   * Đóng vai trò Data Source bất biến để các Sheet sau tra cứu hao phí tự động bằng `XLOOKUP`.
2. **Sheet `DM_GiaVatTu` (Bảng giá gốc & Thông báo giá):**
   * **Bảng 1 (Nhân công):** Lương ngày công chuẩn 22 ngày làm việc (QĐ 80/2026/QĐ-UBND, TTLT 56/2015, QĐ 188/1999/QĐ-TTg).
   * **Bảng 2 (Vật liệu, Hóa chất):** Áp dụng đơn giá mua sắm chưa VAT từ Kết quả lựa chọn nhà thầu gói **IB2600096765** của chính EVN Vĩnh Tân 4 (chia ngược lại 1,08 trước thuế theo đúng chỉ đạo).
   * **Bảng 3 (Ca máy thiết bị):** Nguyên giá Mua sắm công theo Thông tư 45/2013/TT-BTC, chuẩn 250/200/500 ca/năm, khấu hao, sửa chữa, điện năng 1 ca (1.800 đ/kWh).
3. **Sheet `DuToan` (Bảng tính chi tiết - Trái tim của file Excel):**
   * Nhập: STT, Mã hiệu, Tên thông số, ĐVT, Khối lượng mẫu ($Q$), Số thông số dùng chung mẫu ($M \ge 1$).
   * Nhân công: Ngày công NN có hệ số thời tiết $+20\%$ (Khoản 4.1.3 TT20) chia $M$:
     $$\\text{Ngày công NN} = \\frac{\\text{Định mức H\\_NC\\_field} \\times 1{,}2}{M}$$
     Thành tiền $C_{NC} = (\\text{Ngày công NN} + \\text{Định mức H\\_NC\\_lab}) \\times \\text{Đơn giá lương bậc}$.
   * Vật liệu: Hệ số hao hụt phụ $+8\%$ (Khoản 4.4 TT20): $C_{VL} = 1{,}08 \\times \\sum (H_{VL} \\times G_{VL})$.
   * Dụng cụ: Hệ số phụ $+10\%$ (Khoản 4.2 TT20) phân bổ 22 ca/tháng: $C_{DC} = 1{,}10 \\times \\sum (H_{DC} \\times \\text{Nguyên giá} / (T_m \\times 22))$.
   * Ca máy: $C_{TB} = \\sum (H_{TB} \\times ĐG_{\\text{ca}})$.
   * Chi phí ngoài định mức tính riêng Khoản 4.5 TT20 ($C_{\\text{tính riêng}}$): Thuê tàu biển, giàn giáo ống khói, chuyển phát mẫu lạnh, lưu trú công tác.
   * Chi phí trực tiếp: $T = C_{NC} + C_{VL} + C_{DC} + C_{TB} + C_{\\text{tính riêng}}$.
4. **Sheet `Chiettinh` (Bảng chiết tính đơn giá 1 đơn vị mẫu - Đồng/mẫu):**
   * Diễn giải chi tiết cấu thành chi phí 1 đơn vị đo/mẫu cho từng mã hiệu phục vụ in ấn, hồ sơ nghiệm thu thanh quyết toán và giải trình Hội đồng Thẩm định.
5. **Sheet `TongHop_KinhPhi` (Bảng tổng hợp kinh phí toàn gói thầu):**
   * Trực tiếp $T$, Quản lý chung $C_{GT} = 15\\% \\times T$, Thu nhập tính trước $TL = 6\\% \\times (T + C_{GT})$, Dự phòng $DP = 5\\% \\times (T + C_{GT} + TL)$, Chi phí trước thuế $G_Q$, Thuế VAT (8%), Tổng kinh phí sau thuế $TTS$.
6. **Sheet `DM_GiaTruong_BaoGia` (Phụ lục 3 bảng báo giá & Thống kê Mua sắm công):**
   * Lưu vết căn cứ pháp lý: Mã KQLCNT IB2600096765 của Vĩnh Tân 4, link MSC, 3 báo giá cạnh tranh theo Điều 16 NĐ 24/2024/NĐ-CP.

### 2. Kỹ Thuật Công Thức Then Chốt (Thay Thế F1):
* Dò tìm tự động: `=IFERROR(XLOOKUP(B5, DM_DinhMuc_TT20!$B:$B, DM_DinhMuc_TT20!$F:$F, 0), 0)`
* Chống trùng lặp hệ số $M$: Ô chia sẻ $M \\ge 1$, ngày công ngoại nghiệp tự động chia $M$.
* Tính toàn vẹn: Không dùng macro/VBA nhằm tương thích tuyệt đối mọi phiên bản Excel (Office 365, Office 2021, Web Excel).

---

## 📅 VI. LỘ TRÌNH TRIỂN KHAI DỰ ÁN CHI TIẾT"""

if target in content:
    content = content.replace(target, addition)
    with open(plan_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully updated PLAN_DU_AN.md")
else:
    # Try with CRLF
    target_crlf = "---\r\n\r\n## 📅 VI. LỘ TRÌNH TRIỂN KHAI DỰ ÁN CHI TIẾT"
    if target_crlf in content:
        content = content.replace(target_crlf, addition.replace("\n", "\r\n"))
        with open(plan_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("Successfully updated PLAN_DU_AN.md (CRLF)")
    else:
        print("Target not found in PLAN_DU_AN.md")
