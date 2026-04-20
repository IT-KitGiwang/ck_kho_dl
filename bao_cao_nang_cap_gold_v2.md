# BÁO CÁO PHÂN TÍCH NÂNG CẤP KIẾN TRÚC TẦNG GOLD (V1 vs V2)

**Dự án:** SQL Data Warehouse Project  
**Phiên bản phân tích:** `ddl_gold.sql` (V1) so với `gold_v2.sql` (V2)

Bản nâng cấp V2 là một sự lột xác hoàn toàn về mặt kiến trúc dữ liệu và khả năng tối ưu hóa truy vấn cho kho dữ liệu hiện tại. Dưới đây là phân tích chi tiết sự khác biệt và đánh giá về mức độ ảnh hưởng đến hạ tầng làm sạch dữ liệu.

---

## 1. Sự Khác Biệt Giữa Thiết Kế V1 và V2

### 1.1. Physical Tables vs Logical Views
- **V1 (`ddl_gold.sql`):** Sử dụng **VIEWs** (`CREATE VIEW`). Dữ liệu ở tầng Gold được tạo "ảo" bằng lệnh SELECT trực tiếp từ tầng Silver. Nghĩa là lúc chạy Query, CSDL sẽ lấy dữ liệu từ Silver. Không tốn dung lượng bộ nhớ phụ nhưng hiệu năng sẽ chậm đi đối với kho dữ liệu lớn.
- **V2 (`gold_v2.sql`):** Sử dụng **TABLEs** (`CREATE TABLE`). Dữ liệu được tính toán và lưu trữ thật sự xuống đĩa dưới dạng các bảng độc lập biệt lập với Silver. Có đánh Index hỗ trợ tăng tốc độ truy vấn (Performance Indexing).

### 1.2. Star Schema vs Snowflake Schema
- **V1:** Kiến trúc **Star Schema** cơ bản. Thông tin Quốc gia/Khu vực (Location) vẫn nằm chung trong bảng Khách hàng. Thông tin Loại hàng (Category) nằm chung trong bảng Sản phẩm. Không có bảng chuyên cho lịch sử ngày tháng.
- **V2:** Cấu trúc **Snowflake Schema** toàn diện:
  - Tách Category khỏi Product (`DIM_CATEGORY`).
  - Tách Location khỏi Customer (`DIM_LOCATION`).
  - Lập sẵn bảng lịch sử thời gian chuyên dụng `DIM_TIME` từ năm 2003 -> 2030 (Date Dimension).

### 1.3. Cải Tiến Cột Tính Toán Sẵn (Pre-Calculated Measures)
Việc chuyển từ View sang Table trong V2 giúp hệ thống có thể lưu lại "Snapshot" thực tế của dự án. 
- **V1:** Mỗi khi muốn lấy thông tin Doanh thu / Biên lợi nhuận hay xem Giao hàng trễ, hệ thống tự động chạy lại phép trừ (`DATEDIFF`) gây cồng kềnh máy chủ.
- **V2:** 3 trường dữ liệu vô cùng quan trọng đã được khởi tạo để lưu vào Fact:
  - `unit_cost`: Lưu Lại chụp Giá vốn tại thời điểm mua (Tránh lỗi làm sai sổ sách khi giá vốn nhập hàng thay đổi vào tháng sau).
  - `days_to_ship` & `days_to_due`: Tính sẵn số ngày chờ để giao hàng và ngày deadline giao hàng.

---

## 2. V2 Có Gây Ảnh Hưởng Đến Hệ Thống Làm Sạch Dữ Liệu (Cleansing) Tầng Silver Không?

**TRẢ LỜI: KHÔNG SAO CẢ. HỆ THỐNG LÀM SẠCH VẪN CHẠY BÌNH THƯỜNG 100%.**

**Giải thích nguyên lý:** 
Theo chuẩn kiến trúc Medallion, dòng chảy dữ liệu lưu thông một chiều như thác nước: `Nguồn → Bronze → Silver → Gold`.
Quá trình làm sạch dữ liệu diễn ra hoàn toàn bên trong Stored Procedure `proc_load_silver.sql` (đẩy dữ liệu từ Bronze sang Silver). Tầng Bronze và Silver không quan tâm hay phụ thuộc vào việc tầng Gold lưu trữ cái gì. 
Do đó, dù bạn sử dụng `ddl_gold.sql` hay chạy script `gold_v2.sql` đè vào hệ thống máy chủ, **quá trình làm sạch vẫn hoàn thiện mỹ mãn và không sinh ra bất kỳ lỗi gãy khóa ngoại (Foreign key) nào.** 

---

## 3. Hệ Quả & Hành Động Cần Làm Để V2 Chạy Được
Dù V2 KHÔNG LÀM GÃY TẦNG SILVER CŨ, nhưng để V2 thật sự hoạt động được (có dữ liệu bên trong các bảng v2 để query), bạn bắt buộc phải có một sự chuyển mình về Code:

Trong V1, dữ liệu "tự động hiển thị" vì dùng VIEWs nối với Silver. Nhưng V2 sử dụng **TABLE**, bảng khi chạy Code `gold_v2.sql` chỉ là "vỏ bọc rỗng" (ngoại trừ bảng thời gian `DIM_TIME` đã được sinh dữ liệu mồi).
⚠️ **Việc cần làm tiếp theo:**
Đội ngũ Data Engineer cần phải viết bổ sung một Stored Procedure mới (Ví dụ: `scripts/gold/proc_load_gold.sql`) chứa lệnh `INSERT INTO ... SELECT ... FROM silver...` để rót dữ liệu đã làm sạch từ tầng Silver, đổ vật lý sang các bảng `FACT_` và `DIM_` mới của kiến trúc V2 này.
