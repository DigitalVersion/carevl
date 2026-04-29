# Phạm vi thu thập dữ liệu nghiệp vụ (Người nghiệp vụ trước, kỹ thuật sau)

## Trạng thái
[Active]

---

## Bản cho mọi người — **đọc từ đây trước**

### Tài liệu này để làm gì? (ba câu)

1. **Trước khi làm CSDL:** cả Sở và trạm cần **cùng hiểu** sẽ thu **những thông tin gì** khi dân đến khám.  
2. File này **không** bàn tên bảng SQL — chỉ bàn **nghĩa** (cái gì bắt buộc, cái gì còn hỏi Sở).  
3. Sau khi thống nhất xong phần «dễ đọ» bên dưới, lập trình mới chi tiết vào [tài liệu 09 — lược đồ giai đoạn 2](09_Phase2_Schema_Spec.md).

### Hai từ hay gặp trong file này

- **Lượt khám** = một người đến khám **một lần** trong ngày làm việc (có thể qua nhiều bước: tiếp nhận → khám → xét nghiệm…).  
- **Mô-đun** = một **phần hỏi thêm hoặc khám thêm** chỉ áp dụng cho **một nhóm** người (ví dụ riêng trẻ em). Chưa nói đến tên màn hình hay tên bảng trong máy.

---

### Phần 1 — Khi dân đến khám, **luôn** cần những gì?

*(Đây là phần **ổn định nhất**. Nếu chỉ đọc một mục thì đọc mục này.)*

- **Căn cước (CCCD):** quét mã trên thẻ hoặc đọc chip là chính; chỉ nhập tay khi máy hỏng. Trên thẻ thường đã có họ tên, ngày sinh, giới tính, địa chỉ thường trú…  
- **Một mã (tem / mã vạch) cho đúng lần khám đó:** in ở tiếp nhận, dán cho người bệnh, để suốt quá trình **không nhầm người** (cùng một mã từ lúc vào đến khi có kết quả).

**Thiếu gì thì ghi thêm** vào cuối file, mục «Còn phải hỏi thêm».

---

### Phần 2 — **Chưa chốt**, cần Sở / chuyên môn **trả lời rõ**

*(Đây **không phải** quyết định cuối — là **câu hỏi** để họp.)*

1. **Trẻ em:** có bắt buộc phần sàng lọc liên quan **tự kỷ** không? Từ **bao nhiêu tuổi**? Theo **văn bản nào** của ngành?  
2. **Người cao tuổi:** «Cao tuổi» tính theo **tuổi** hay theo **nhóm đối tượng** chương trình? Có bắt buộc phần **tâm lý / trầm cảm** không?  
3. **Người lao động và các nhóm khác:** có **mấy gói** khám chính thức? Ai được xếp vào gói nào theo **quy định địa phương**?

Khi đã có câu trả lời bằng văn bản (biên bản họp, công văn…) thì lập trình mới gắn vào phần mềm và tài liệu kỹ thuật 09.

---

### Phần 3 — Phiếu hỏi trên máy / giấy: **sao cho dễ**

- **Ưu tiên:** câu hỏi kiểu **chọn sẵn** (một đáp án / nhiều đáp án / Có–Không–Chưa rõ / mức độ nhẹ–nặng…). Người dân **bấm chọn** nhanh, ít sai, sau này **đếm báo cáo** cũng dễ.  
- **Hạn chế:** ô **tự viết dài**. Chỉ dùng khi thật sự không gói được vào lựa chọn; nếu có thì **ít câu**, hoặc để **sau bước khám**, không nhồi hết ở quầy đông.

**Ví dụ:**  
*«Trẻ có nhìn mặt người lớn khi được gọi tên không?»* → Trả lời: **Luôn / Đôi khi / Hiếm / Không đánh giá** — **không** lấy câu *«Hãy mô tả chi tiết hành vi trẻ»* làm câu chính.

*(Cách đặt câu khi **họp thiết kế CSDL** — tên cột, kiểu dữ liệu — nằm ở [09](09_Phase2_Schema_Spec.md), mục về câu hỏi khi xây schema.)*

---

### Việc tiếp theo (thứ tự gợi ý)

1. Họp, **chốt hoặc ghi nhận ý** về Phần 1 và Phần 2.  
2. Lập trình cập nhật [09](09_Phase2_Schema_Spec.md) (bảng, cột) cho khớp.  
3. Nếu luồng quầy thay đổi nhiều, xem thêm [26](26_Visualization.md) và [Tiếp nhận mới](../FEATURES/1_tiep_nhan_moi.md).

---

### Còn phải hỏi thêm (ghi dần khi có họp)

- Danh sách chính thức các **nhóm đối tượng** và cách xếp nhóm (theo tuổi? theo chương trình?).  
- Gói khám có **đổi theo năm / theo mùa** không.  
- Mô-đun nào **bắt buộc** hay **tự chọn**; ai chịu trách nhiệm ký duyệt.  
- Giới hạn: tối đa bao nhiêu câu **tự viết** trên một lượt khám (nếu Sở muốn quy chuẩn).

---

## Ghi chép kỹ thuật (ADR — cho đội dự án)

### Bối cảnh
Cần tách **lớp nghiệp vụ** (tiếng Việt, phạm vi thu thập) và **lớp CSDL** (bảng, cột, migration) để tránh làm phần mềm rồi bị yêu cầu sửa vì chưa thống nhất với Sở. Định danh chính qua **CCCD**; nhóm đối tượng và mô-đun bổ sung **chưa khóa hết**.

### Quyết định

1. **Lớp A** = tài liệu này (mục «Bản cho mọi người»). **Lớp B** = [09](09_Phase2_Schema_Spec.md). Lớp B cập nhật sau khi Lớp A được đồng ý hoặc ghi rõ phạm vi giai đoạn 1.  
2. Định danh: **quét CCCD** là chính; thông tin thường có trên thẻ do kỹ thuật ánh xạ theo 09.  
3. Không giả định một gói khám cho mọi người; nhóm đối tượng dùng để chọn mô-đun — chi tiết câu hỏi Sở nằm ở **Phần 2** phía trên.  
4. Biểu mẫu: ưu tiên đáp án có cấu trúc; tự luận hạn chế (đồng mục **Phần 3** và [09](09_Phase2_Schema_Spec.md) phần elicitation schema).

### Cơ sở
Giảm rủi ro hiểu nhầm giữa nghiệp vụ và code. Đáp án chọn sẵn giúp vận hành quầy và tổng hợp Hub nhất quán.

### Tài liệu liên quan
- [09. Đặc tả lược đồ CareVL giai đoạn 2](09_Phase2_Schema_Spec.md)  
- [12. Luồng dữ liệu giao diện: từ tiếp nhận đến kết quả trễ](12_ui_ux_flow.md)  
- [26. Thư mục trực quan hóa](26_Visualization.md)  
- [1. Tiếp nhận mới](../FEATURES/1_tiep_nhan_moi.md)  
- [19. Hướng dẫn migration giai đoạn 2](19_Phase2_Migration_Guide.md)
