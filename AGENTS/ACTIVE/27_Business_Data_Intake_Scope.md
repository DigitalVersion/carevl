# Phạm vi thu thập dữ liệu nghiệp vụ (Người nghiệp vụ trước, kỹ thuật sau)

## Trạng thái
[Active]

## Bối cảnh
Đội ngoài (Sở Y tế, trạm) và đội trong (lập trình) cần **cùng một sự thật** nhưng **khác ngôn ngữ**: người nghiệp vụ cần biết *thu thập những thông tin gì, với ai*; lập trình cần *bảng, cột, kiểu dữ liệu có cấu trúc*. Nếu nhảy thẳng vào sơ đồ thực thể (ERD) hoặc SQL mà chưa thống nhất phạm vi nghiệp vụ, tài liệu sẽ mơ hồ và mã nguồn dễ bị yêu cầu sửa vòng.

Nhóm đã thống nhất hướng: **định danh qua căn cước công dân (CCCD)** (mã QR / chip — dữ liệu cơ bản đã được mã hóa trên thẻ). Vấn đề **gói khám / đối tượng** (trẻ em so với người cao tuổi so với lao động) **chưa khóa hết** nhưng đã có hướng: **mô-đun khảo sát / phần bổ sung khác nhau theo nhóm** (ví dụ gợi ý: trẻ em — bộ câu hỏi liên quan tự kỷ; người cao tuổi — bộ câu hỏi liên quan tâm lý / trầm cảm).

## Quyết định

1. **Hai lớp tài liệu song song, không thay thế nhau**
   - **Lớp A (tài liệu này):** bảng mô tả **ý nghĩa nghiệp vụ**, tiếng Việt, không bắt buộc cú pháp SQL. Dùng để **xác nhận phạm vi** với Sở / trạm trước khi khóa chi tiết lược đồ dữ liệu (schema).
   - **Lớp B:** [09. Đặc tả lược đồ CareVL giai đoạn 2](09_Phase2_Schema_Spec.md) — mô hình lưu trữ, bảng, migration. Cập nhật Lớp B **sau** khi Lớp A được đồng ý (hoặc ghi rõ phạm vi “giai đoạn 1”).

2. **Định danh người đến khám (đã thống nhất hướng)**
   - Nguồn chính: **quét CCCD** (QR / chip), không phụ thuộc nhập tay đầy đủ cho các trường đã có sẵn trên thẻ.
   - Các thông tin cơ bản thường có trên CCCD (số định danh, họ tên, ngày sinh, giới tính, địa chỉ thường trú, ngày cấp, …) — ánh xạ kỹ thuật sang `Patient` / định danh (identifier) xem tài liệu giai đoạn 2.

3. **Đối tượng và mô-đun bổ sung (chưa khóa đủ — ghi rõ *chưa quyết*)**
   - Hệ thống **không** giả định “một gói khám một kiểu cho tất cả mọi người”.
   - **Nhóm đối tượng** (cohort) dùng để **chọn / hiển thị** các **mô-đun khảo sát hoặc mục khám bổ sung** (gợi ý nghiệp vụ: trẻ em / người cao tuổi khác nhau).
   - Chưa quyết định cuối: danh sách đủ các nhóm, tên gọi chính thức, và tiêu chí tự động (tuổi) so với chọn tay. Mục **Mớ mở cần làm rõ** bên dưới là chỗ ghi thêm khi có quyết định.

4. **Thứ tự làm việc gợi ý (tránh kẹt suy nghĩ)**
   - Bước 1: Hoàn thiện / ký duyệt **bảng Lớp A** trong tài liệu này (với Sở hoặc nhóm nghiệp vụ).
   - Bước 2: Chuyển quyết định sang **Lớp B** (tài liệu 09 + SQL / migration + hợp đồng API).
   - Bước 3: Cập nhật **sơ đồ E2E / tính năng** ([26. Thư mục trực quan hóa](26_Visualization.md), [1. Tiếp nhận mới](../FEATURES/1_tiep_nhan_moi.md)) nếu bước 4 (vận hành hằng ngày) đổi màn hình hoặc luồng.
   - **Wireframe** (nếu cần): chỉ bắt buộc khi luồng tiếp nhận / chọn mô-đun phức tạp; không bắt buộc trước bước 1.

## Cơ sở
Tách “con người” và “máy” giảm rủi ro: Sở ký phạm vi thu thập trước, lập trình không phải đoán. `questionnaire` / biểu mẫu động trong giai đoạn 2 **khớp** với ý tưởng mô-đun theo đối tượng mà **chưa cần** biết hết SQL ngay hôm nay.

## Phụ lục A — Định danh (lớp người nghiệp vụ)

| Mục | Bắt buộc / Ghi chú | Ghi chú vận hành |
|-----|-------------------|------------------|
| Định danh pháp lý (CCCD) | Bắt buộc cho luồng chuẩn | Ưu tiên quét QR / chip; nhập tay chỉ dùng khi thiết bị lỗi |
| Họ tên, ngày sinh, giới tính | Thường lấy từ CCCD | Trùng lặp nếu cần đối chiếu thủ công |
| Địa chỉ thường trú | Thường lấy từ CCCD | |
| Sticker / mã vạch lượt khám | Bắt buộc trong luồng CareVL | Gắn xuyên suốt luồng trạm — xem [12. Luồng dữ liệu giao diện](12_ui_ux_flow.md) |

## Phụ lục B — Đối tượng và mô-đun bổ sung (gợi ý, còn *chưa quyết*)

| Nhóm đối tượng (gợi ý) | Mô-đun / khảo sát bổ sung (gợi ý nghiệp vụ) | Trạng thái |
|------------------------|---------------------------------------------|------------|
| Trẻ em | Bộ câu hỏi / mục khám liên quan **tự kỷ** (ví dụ sàng lọc) | **Chưa quyết** — cần tài liệu chuyên môn và phê duyệt |
| Người cao tuổi | Bộ câu hỏi / mục khám liên quan **tâm lý / trầm cảm** (ví dụ) | **Chưa quyết** |
| Người lao động / khác | Gói hoặc mức độ khám theo quy định địa phương | **Chưa quyết** |

**Quy tắc thiết kế (trước khi có SQL):** một `Encounter` có thể **gắn** một hoặc nhiều “mô-đun” nghiệp vụ; cách lưu trữ (`questionnaire`, siêu dữ liệu lượt khám, …) do **Lớp B** quyết định sau khi các bảng trên được đồng ý.

## Mớ mở cần làm rõ (ghi thêm dần)

- Danh sách chính thức **các nhóm đối tượng** và tiêu chí vào nhóm (tuổi? loại khám?).
- Gói khám theo **quy định địa phương / năm** có thay đổi theo mùa không.
- Mô-đun nào **bắt buộc** so với **tự chọn**; ai ký (bác sĩ / tiếp nhận / hệ thống tự động).

## Tài liệu liên quan
- [09. Đặc tả lược đồ CareVL giai đoạn 2](09_Phase2_Schema_Spec.md)
- [12. Luồng dữ liệu giao diện: từ tiếp nhận đến kết quả trễ](12_ui_ux_flow.md)
- [26. Thư mục trực quan hóa: SVG, Mermaid và bảng](26_Visualization.md)
- [1. Tiếp nhận mới](../FEATURES/1_tiep_nhan_moi.md)
- [19. Hướng dẫn migration giai đoạn 2](19_Phase2_Migration_Guide.md)
