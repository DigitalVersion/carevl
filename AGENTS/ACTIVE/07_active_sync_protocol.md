# Active Sync Protocol: The Encrypted SQLite Blob

## Status
**[Active - Sprint 4 Source of Truth]**

## Context
Dự án CareVL cần đồng bộ dữ liệu từ Trạm (Site) về Tỉnh một cách an toàn và bảo toàn toàn vẹn dữ liệu. Các phương án sử dụng JSON Sync hoặc Git Push thông thường dễ gây ra đụng độ (conflict) hoặc thiếu hụt dữ liệu khi hợp nhất.

## Decision
Sử dụng **The Encrypted SQLite Blob Protocol** qua GitHub Releases với chiến lược **"Một Nhánh - Vạn Release"**.

### Chiến lược Repository: "Một Nhánh - Vạn Release" (Single Branch, Multi-Releases)

**Repository Structure:**
- **Branch `main`**: Chỉ chứa file `README.md` (có thể trống rỗng)
- **Releases**: Mỗi Site có một Release riêng biệt
- **Assets**: Mỗi Release chứa các snapshot theo ngày của Site đó

**Release Naming Convention:**
- Format: `Site_{SiteID}` (ví dụ: `Site_LongHo_01`, `Site_BinhMinh_02`)
- Mỗi Site có duy nhất 1 Release
- Assets trong Release: Các file snapshot theo thời gian

**Asset Naming Convention:**
- Format: `FINAL_{SITE_ID}_{YYYY-MM-DD}T{HH-mm-ss}.db.enc`
- Ví dụ: `FINAL_LongHo_01_2026-04-25T14-30-00.db.enc`
- Sử dụng dấu `-` thay cho dấu `:` để tương thích Windows

**Ưu điểm:**
- ✅ **Cực kỳ sạch sẽ**: Mỗi Site có không gian riêng, dễ theo dõi lịch sử
- ✅ **Không conflict**: Mỗi Site push vào Release riêng, không đụng độ
- ✅ **Dễ audit**: Xem được Site đó khám bao nhiêu đợt, mỗi đợt bao nhiêu người
- ✅ **Scalable**: Có thể có hàng trăm Sites mà không ảnh hưởng performance
- ✅ **Tự động hóa Hub**: Dùng GitHub API để liệt kê và tải tất cả Assets

**Nhược điểm:**
- ⚠️ Hub Admin cực thân nếu làm thủ công (phải vào từng Release)
- ✅ **Giải pháp**: Dùng DuckDB Script tự động (xem phần Hub Aggregation)

### Quy trình Site Push (Edge → Hub)

**Quy trình chuẩn:**
1. **Trigger**: Người dùng nhấn nút "Gửi về Hub" trên giao diện Admin/Operator.
2. **Background Task**: Quá trình này bắt buộc chạy ngầm qua `fastapi.BackgroundTasks`. Giao diện không bị treo và phải hiển thị ngay thông báo: *"Đang đóng gói và gửi..."*.
3. **Metadata Injection**: Hệ thống ghi trực tiếp `SITE_ID` và `Timestamp` vào một bảng metadata (ví dụ: `schema_meta` hoặc bảng riêng) ngay bên trong file SQLite, để Hub có thể verify nội tại.
4. **Optimize**: Thực thi câu lệnh SQL `VACUUM` và `ANALYZE` lên file DB để tối ưu hóa và giảm dung lượng.
5. **Snapshot & Encrypt**: Tạo bản sao an toàn (sử dụng API backup của SQLite để cover WAL), sau đó mã hóa file này bằng chuẩn **AES-256** (sử dụng `ENCRYPTION_KEY` từ `.env`).
6. **Naming Convention**: Tên file đầu ra bắt buộc tuân theo định dạng: `FINAL_{SITE_ID}_YYYY-MM-DDTHH-mm-ss.db.enc`.
7. **Transport**: 
   - Kiểm tra Release `Site_{SITE_ID}` đã tồn tại chưa
   - Nếu chưa: Tạo Release mới với tag `Site_{SITE_ID}`
   - Upload file `.db.enc` vào Release đó qua GitHub API (sử dụng `GITHUB_TOKEN`)

### Hub Aggregation (Hub ← Edge)

**DuckDB Script tự động:**

Hub không cần vào từng Release thủ công. Script `scripts/hub_aggregate.py` sẽ:

1. **List All Assets**: Dùng GitHub API để liệt kê toàn bộ Assets của Repo
   ```python
   GET /repos/{owner}/{repo}/releases
   # Lấy tất cả releases và assets
   ```

2. **Filter by Date**: Lọc ra những file có ngày mới nhất (ví dụ: `20260425`)
   ```python
   # Lọc assets theo pattern: FINAL_*_2026-04-25T*.db.enc
   latest_assets = filter_by_date(all_assets, target_date="2026-04-25")
   ```

3. **Download & Decrypt**: Tải về và giải mã từng file
   ```python
   for asset in latest_assets:
       download(asset.url)
       decrypt(asset.file, encryption_key)
   ```

4. **Import to DuckDB**: Gộp tất cả vào DuckDB để phân tích
   ```python
   import duckdb
   con = duckdb.connect('hub_analytics.duckdb')
   
   for db_file in decrypted_files:
       con.execute(f"ATTACH '{db_file}' AS site_{site_id}")
       con.execute(f"INSERT INTO patients SELECT * FROM site_{site_id}.patients")
       # ... import các bảng khác
   ```

5. **Analytics**: Chạy các query phân tích tổng hợp
   ```sql
   -- Tổng số bệnh nhân theo Site
   SELECT site_id, COUNT(*) FROM patients GROUP BY site_id;
   
   -- Tổng số lượt khám theo ngày
   SELECT DATE(encounter_date), COUNT(*) FROM encounters GROUP BY 1;
   ```

**Script Features:**
- ✅ Tự động phát hiện Sites mới
- ✅ Chỉ tải Assets mới nhất (theo ngày)
- ✅ Parallel download (tải nhiều file cùng lúc)
- ✅ Retry mechanism (tự động thử lại nếu lỗi)
- ✅ Progress bar (hiển thị tiến trình)
- ✅ Audit log (ghi lại quá trình aggregate)

## Rationale
- **Tránh Git Conflict**: Thay vì push lên repository gốc làm phình to lịch sử, GitHub Releases phục vụ như một File Server an toàn, lưu trữ các blob nhị phân riêng biệt.
- **Tính toàn vẹn**: Ghi metadata vào thẳng DB trước khi đóng gói giúp hệ thống tại Hub không bao giờ nhầm lẫn file này thuộc về trạm nào, ngay cả khi tên file bị đổi.
- **Tối ưu trải nghiệm**: Cơ chế Background Task đảm bảo UI không bị kẹt trong quá trình chờ mạng upload file hàng MB.
- **Scalability**: Chiến lược "Một Nhánh - Vạn Release" cho phép hệ thống mở rộng lên hàng trăm Sites mà không ảnh hưởng performance.
- **Automation**: Hub Admin không cần làm thủ công, mọi thứ tự động qua DuckDB Script.

## Related Documents
- [02. SQLite Security & Snapshots](02_SQLite_Security.md)
- [QR Code Provisioning](../FEATURES/qr_provisioning.md)
