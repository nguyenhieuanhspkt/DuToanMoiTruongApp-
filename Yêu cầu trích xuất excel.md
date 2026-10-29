# 🎯 BẢN ĐẶC TẢ NGHIỆP VỤ & MỤC ĐÍCH CẦN ĐẠT ĐƯỢC CỦA FILE EXCEL DỰ TOÁN
**THẨM ĐỊNH DỰ TOÁN QUAN TRẮC MÔI TRƯỜNG EVN VĨNH TÂN 4 - THAY THẾ PHẦN MỀM F1**  
**Căn cứ pháp lý & Kỹ thuật:** Thông tư 20/2017/TT-BTNMT, Quyết định số 80/2026/QĐ-UBND, Văn bản 5691/EVN-MTPTBV, Nghị định 24/2024/NĐ-CP & KQLCNT IB2600096765

---

### 🌟 I. MỤC TIÊU CỐT LÕI (CORE OBJECTIVES)
1. **Thay thế hoàn toàn phần mềm chuyên dụng F1**:
   Lập một tệp Excel dự toán chi phí quan trắc môi trường **chuẩn chỉnh, minh bạch, tự động hóa 100% và kiểm soát triệt để quy tắc chống trùng lặp** mà không cần cài đặt hoặc phụ thuộc vào bản quyền phần mềm dự toán đóng kín (F1/G8/Eta).
2. **Hệ công thức sống khép kín (Living Dynamic Formulas)**:
   Sử dụng hoàn toàn các hàm tra cứu và tính toán động thế hệ mới của Excel (`XLOOKUP`, `SUMIFS`, `INDEX/MATCH`), bọc bẫy lỗi `#N/A` bằng `IFERROR(...)` để bảo đảm tính thẩm mỹ và độ tin cậy tuyệt đối khi trình Hội đồng Thẩm định EVN Vĩnh Tân 4.
3. **Minh bạch hóa & Truy nguyên nguồn gốc (Audit Traceability)**:
   Bất kỳ ô chi phí nào trong bảng tổng hợp đều có thể nhấp chuột truy vết ngược lại:
   - Định mức gốc Nhà nước (Thông tư 20/2017/TT-BTNMT).
   - Đơn giá nhân công viên chức (22 ngày chuẩn, TTLT 56/2015 & QĐ 80/2026/QĐ-UBND).
   - Đơn giá vật tư/hóa chất trúng thầu thực tế của EVN Vĩnh Tân 4 (TBMT IB2600096765 chia 1,08 trước thuế).
   - Đơn giá ca máy theo Thông tư 45/2013/TT-BTC.
4. **Kiểm soát quy tắc chống trùng lặp hiện trường ($M \ge 1$)**:
   Đối với các phép đo lấy mẫu ngoại nghiệp dùng chung vị trí/đợt quan trắc (nước biển, khí thải), ngày công ngoại nghiệp tự động chia đều cho số thông số $M$, chấm dứt triệt để tình trạng tính trùng chi phí theo đúng tinh thần chỉ đạo tại Văn bản 5691/EVN-MTPTBV.

---

### 📂 II. CẤU TRÚC 6 SHEET CHÍNH TRONG FILE EXCEL DỰ TOÁN

```
DU_TOAN_QUAN_TRAC_MOI_TRUONG_CHUAN_6_SHEET_F1.xlsx
├── 1. DM_DinhMuc_TT20      : Cơ sở dữ liệu định mức gốc Thông tư 20/2017
├── 2. DM_GiaVatTu          : Bảng giá gốc & Thông báo giá (Lương 22 ngày, Vật tư KQLCNT, Ca máy TT45)
├── 3. DuToan               : Bảng tính chi tiết chi phí trực tiếp (Trái tim của dự toán)
├── 4. Chiettinh            : Bảng chiết tính đơn giá 1 đơn vị mẫu (Đồng/mẫu)
├── 5. TongHop_KinhPhi      : Bảng tổng hợp kinh phí toàn gói thầu & Kịch bản phê duyệt
└── 6. DM_GiaTruong_BaoGia  : Phụ lục 3 bảng báo giá & Thống kê Mua sắm công (KQLCNT IB2600096765)
```

---

#### 1. Sheet `DM_DinhMuc_TT20` (Cơ sở dữ liệu định mức gốc)
Lưu trữ toàn bộ định mức kinh tế - kỹ thuật theo Thông tư 20/2017/TT-BTNMT cho từng mã thông số công việc.
* **Các cột chính:**
  `STT` | `Mã hiệu TT20` | `Tên thông số & Công đoạn` | `Phân loại (Ngoại/Nội nghiệp)` | `ĐVT` | `Hao phí Ngày công (H_NC)` | `Hao phí Vật liệu/Hóa chất (H_VL)` | `Hao phí Dụng cụ (H_DC)` | `Hao phí Ca máy (H_TB)`
* **Cách dùng:** Cung cấp dữ liệu nguồn cố định để Sheet `DuToan` và Sheet `Chiettinh` tự động tra cứu hao phí khi nhập mã hiệu bằng hàm `XLOOKUP`.

#### 2. Sheet `DM_GiaVatTu` (Bảng giá gốc & Thông báo giá)
Lưu trữ đơn giá cập nhật cho vật liệu, hóa chất, dụng cụ, ca máy và lương nhân công theo ngạch bậc.
* **Bảng 1: Đơn giá Nhân công ($L_{\text{bậc}}$):**
  - Cột: `Bậc lương`, `Chức danh theo TTLT 56/2015`, `Hệ số lương`, `Mức lương ngày công chuẩn 22 ngày (VNĐ/công)`.
  - Tuân thủ Quyết định 80/2026/QĐ-UBND và QĐ 188/1999/QĐ-TTg (Nghỉ Thứ Bảy, CN, chia cho 22 ngày làm việc).
* **Bảng 2: Đơn giá Vật liệu & Hóa chất ($G_{VL}$):**
  - Cột: `Mã vật tư`, `Tên hóa chất/vật liệu`, `ĐVT`, `Đơn giá mua sắm chưa VAT`, `Mã TBMT/Nguồn báo giá`.
  - Áp dụng nguyên tắc: Lấy từ Kết quả lựa chọn nhà thầu gói thầu **IB2600096765** của chính Nhà máy Nhiệt điện Vĩnh Tân 4 (chia ngược lại $1{,}08$ để lấy đơn giá trước thuế theo đúng chỉ đạo).
* **Bảng 3: Danh mục & Đơn giá Ca máy ($ĐG_{\text{ca}}$):**
  - Áp dụng công thức tính ca máy từ Nguyên giá Mua sắm công theo Thông tư 45/2013/TT-BTC.
  - Cột: `Mã máy`, `Tên máy`, `Công suất (kW)`, `Nguyên giá (MSC)`, `Số ca chuẩn/năm (250/200/500)`, `Khấu hao 1 ca`, `Sửa chữa 1 ca`, `Điện năng 1 ca (1.800 đ/kWh)`, `Tổng đơn giá 1 ca`.

#### 3. Sheet `DuToan` (Bảng tính chi tiết - Trái tim của file)
Sheet này thể hiện chi tiết khối lượng, chi phí trực tiếp thành phần và thành tiền cho từng thông số quan trắc:
* **Các cột nhận diện:** `STT`, `Mã hiệu TT20`, `Tên thông số công tác`, `ĐVT`, `Số lượng mẫu (Q)`, `Số thông số dùng chung mẫu (M)`.
* **Hao phí & Thành tiền Nhân công ($C_{NC}$):**
  - Công thức tính ngày công ngoại nghiệp có kể đến hệ số thời tiết $+20\%$ (Khoản 4.1.3 TT20) và chống trùng lặp $M$:
    $$\text{Ngày công NN} = \frac{\text{Định mức } H_{NC\_field} \times 1{,}2}{M}$$
  - Thành tiền: $C_{NC} = (\text{Ngày công NN} + \text{Định mức } H_{NC\_lab}) \times \text{Đơn giá lương bậc tương ứng}$.
* **Thành tiền Vật liệu ($C_{VL}$):**
  - Áp dụng hệ số hao hụt vật liệu phụ $+8\%$ (Khoản 4.4 TT20):
    $$C_{VL} = 1{,}08 \times \sum (\text{Hao phí VL} \times \text{Đơn giá VL chưa VAT})$$
* **Thành tiền Dụng cụ ($C_{DC}$):**
  - Áp dụng hệ số dụng cụ phụ $+10\%$ (Khoản 4.2 TT20) và phân bổ theo ca làm việc chuẩn ($T_m \times 22$):
    $$C_{DC} = 1{,}10 \times \sum \left( \frac{\text{Hao phí DC} \times \text{Nguyên giá}}{T_m \times 22} \right)$$
* **Thành tiền Ca máy ($C_{TB}$):**
  $$C_{TB} = \sum (\text{Hao phí ca máy} \times ĐG_{\text{ca máy tra cứu}})$$
* **Chi phí Ngoài định mức / Tính riêng (Khoản 4.5 TT20):**
  - Cột nhập chi phí thực tế cho thuê tàu biển chuyên dụng, giàn giáo đo khí thải ống khói, vận chuyển mẫu bảo quản lạnh hỏa tốc, lưu trú công tác phí.
* **Cộng Chi phí Trực tiếp ($T$):**
  $$T = C_{NC} + C_{VL} + C_{DC} + C_{TB} + C_{\text{tính riêng}}$$

#### 4. Sheet `Chiettinh` (Bảng chiết tính đơn giá 1 đơn vị mẫu)
* Dùng để diễn giải chi tiết cấu thành đơn giá **Đồng/mẫu** cho từng mã hiệu khi cần in ấn kèm theo hồ sơ thanh quyết toán hoặc trình Hội đồng Thẩm định EVN Vĩnh Tân 4.
* Liên kết trực tiếp số liệu từ sheet `DuToan` và `DM_DinhMuc_TT20`:
  $$\text{Đơn giá 1 mẫu} = \text{ĐG Nhân công} + \text{ĐG Vật liệu} + \text{ĐG Dụng cụ} + \text{ĐG Thiết bị}$$

#### 5. Sheet `TongHop_KinhPhi` (Bảng tổng hợp kinh phí toàn gói thầu)
Tổng hợp toàn bộ chi phí xây dựng/quan trắc và áp dụng các hệ số gián tiếp, thuế theo đúng cấu trúc tài chính vĩ mô:
* **Chi phí trực tiếp ($T$):** Lấy tổng cộng `=DuToan!Total_T`.
* **Chi phí Quản lý chung ($C_{GT}$):** $15\% \times T$ (hoặc tỷ lệ theo định mức hiện hành).
* **Thu nhập chịu thuế tính trước ($TL$):** $6\% \times (T + C_{GT})$.
* **Chi phí Dự phòng phát sinh ($DP$):** $5\% \times (T + C_{GT} + TL)$.
* **Cộng chi phí trước thuế ($G_Q$):** $G_Q = T + C_{GT} + TL + DP$.
* **Thuế Giá trị gia tăng ($\text{VAT}$):** $8\%$ hoặc $10\% \times G_Q$.
* **Tổng kinh phí sau thuế (Giá trị gói thầu VNĐ):** $\text{TTS} = G_Q \times (1 + \text{VAT})$.

#### 6. Sheet `DM_GiaTruong_BaoGia` (Phụ lục 3 bảng báo giá & Thống kê Mua sắm công)
* Lưu trữ minh chứng pháp lý cho các mục chi phí "Ngoài định mức":
  - Mã KQLCNT `IB2600096765` của chính Nhà máy Nhiệt điện Vĩnh Tân 4 (ngày duyệt 03/04/2026).
  - Kết quả tra cứu Hệ thống mạng đấu thầu quốc gia cho máy móc thiết bị phân tích.
  - 3 bảng báo giá hóa chất và dịch vụ thuê tàu/vận chuyển hỏa tốc để Tổ Thẩm định kiểm tra đối chiếu nhanh.

---

### 🛠️ III. KỸ THUẬT LẬP CÔNG THỨC EXCEL THEN CHỐT (THAY THẾ F1)

1. **Tra cứu tự động Định mức bằng XLOOKUP:**
   ```excel
   =IFERROR(XLOOKUP(B5, DM_DinhMuc_TT20!$B:$B, DM_DinhMuc_TT20!$F:$F, 0), 0)
   ```
2. **Xử lý bẫy lỗi trống mã hiệu (`#N/A`):**
   Bọc toàn bộ hàm dò tìm bằng `IFERROR(...)` để bảng tính luôn sạch sẽ, chuyên nghiệp khi chưa điền dữ liệu.
3. **Chống trùng lặp hệ số dùng chung mẫu ($M$):**
   Tại ô chia sẻ mẫu chung, đặt điều kiện bắt buộc $M \ge 1$:
   ```excel
   =IF(OR(ISBLANK(F5), F5<=0), 1, F5)
   ```
   Công thức ngày công ngoại nghiệp thực tế:
   ```excel
   =(Định_Mức_Gốc * 1.2) / Ô_Chứa_M
   ```

---

### 💡 IV. GIÁ TRỊ VÀ Ý NGHĨA KHI ÁP DỤNG VÀO HỆ THỐNG
* **Minh bạch tuyệt đối**: Tổ Thẩm định EVN Vĩnh Tân 4 có thể nhấp chuột vào bất kỳ ô đơn giá nào để truy nguyên ngược lại nguồn gốc định mức gốc (Thông tư 20) hoặc hóa đơn/báo giá thị trường.
* **Linh hoạt thay đổi chính sách**: Khi nhà nước thay đổi mức lương cơ sở, tỷ lệ VAT (từ 8% lên 10%) hoặc biểu giá điện EVN, chỉ cần cập nhật tại sheet `DM_GiaVatTu`, toàn bộ bảng dự toán và tổng mức đầu tư sẽ tự động nhảy số chính xác mà không cần sửa thủ công từng dòng.
* **Độc lập, bền vững**: Không bị khóa định dạng bởi bất kỳ phần mềm thương mại nào.
