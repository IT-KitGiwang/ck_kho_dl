# BÁO CÁO CÁC KỸ THUẬT LÀM SẠCH DỮ LIỆU (DATA CLEANSING)

**Dự án:** SQL Data Warehouse Project  
**Tầng áp dụng (Layer):** Silver Layer (`silver.load_silver`)

Trong quá trình chuyển đổi dữ liệu từ tầng Bronze (Dữ liệu gốc/Raw data) sang tầng Silver, dự án đã triển khai phân tích và làm sạch dữ liệu chặt chẽ nhằm giải quyết các lỗi phổ biến (data anomalies) từ các hệ thống CRM và ERP. Nhờ vậy, dữ liệu đầu ra được đảm bảo tính nhất quán (Consistency), trung thực (Integrity) và chất lượng cao.

Dưới đây là thống kê 6 kỹ thuật làm sạch dữ liệu (Data Cleansing) chủ đạo đã được thực hiện:

---

## 1. Deduplication (Loại bỏ dữ liệu trùng lặp)
Do đặc thù hệ thống CRM đôi lúc ghi nhận dư thừa bản ghi hoặc khi có biến động thông tin khách hàng, bảng `crm_cust_info` chứa các khách hàng bị lặp lặp ID (`cst_id`).
- **Kỹ thuật áp dụng:** Sử dụng Window Function `ROW_NUMBER() OVER (PARTITION BY cst_id ORDER BY cst_create_date DESC)`.
- **Kết quả:** Chỉ lấy bản ghi mới nhất (theo ngày `cst_create_date`), loại bỏ hoàn toàn các bản ghi rác/cũ để duy trì dữ liệu Unique (Duy nhất) trên mỗi khách hàng.

## 2. Text Normalization & Trimming (Chuẩn hóa chuỗi văn bản & Bỏ khoảng trắng thừa)
Dữ liệu nhập liệu bằng tay vào các hệ thống (chẳng hạn firstname, lastname) thường dính các khoảng trắng ẩn ở đầu/cuối chuỗi dẫn đến sai lệch khi join bảng.
- **Kỹ thuật áp dụng:** Xóa bỏ khoảng trắng thừa bằng hàm `TRIM(cst_firstname)` và `TRIM(cst_lastname)`.
- **Kết quả:** Chuỗi văn bản gọn gàng, tăng độ chính xác lên 100% khi tra cứu chuỗi.

## 3. Data Standardization / Value Mapping (Chuẩn hóa về cùng một bảng thuật ngữ chung)
Dữ liệu từ nhiều nguồn khác nhau có thuật ngữ lưu trữ khác nhau. Ví dụ: US, USA, thay vì United States. Hoặc M, F, Male, Female.
- **Kỹ thuật áp dụng (Mapping Rules thông qua cấu trúc `CASE WHEN`):**
  - **Tình trạng hôn nhân:** Biến các mã `'S'`, `'M'` thành `'Single'`, `'Married'`. Ngược lại các giá trị trống/không hợp lệ được gán `'n/a'`.
  - **Giới tính:** Quy hoạch đồng loạt về `'Male'`, `'Female'` hoặc `'n/a'`. Chấp nhận cả `'M', 'MALE', 'F', 'FEMALE'`.
  - **Dòng sản phẩm (Product Line):** Map logic `'M' -> 'Mountain'`, `'R' -> 'Road'`, `'S' -> 'Other Sales'`, `'T' -> 'Touring'`.
  - **Quốc gia:** Xử lý `'DE' -> 'Germany'`, `'US' / 'USA' -> 'United States'`.

## 4. String Manipulation & Key Extraction (Cắt ghép chuỗi, bóc tách khóa ngoại)
Các khóa ngoại (Primary Keys / Foreign Keys) không đồng nhất giữa CRM và ERP. Để hợp nhất được, bộ key phải được bóc tách định dạng rác đi kèm.
- **Trích xuất ID thật (ERP):** Trong bảng `erp_cust_az12`, một số ID khách hàng bị dính tiền tố `'NAS'`, dữ liệu được làm sạch bằng `SUBSTRING(cid, 4, LEN(cid))` nhằm loại bỏ tiền tố này.
- **Loại bỏ ký tự đặc biệt (Location ID):** Sử dụng hàm `REPLACE(cid, '-', '')` để xóa bỏ dấu trừ (`-`), khớp với chuẩn ID trên CRM.
- **Tách Key phức hợp (Product Key):** Khóa sản phẩm `prd_key` dài được cắt thành `cat_id` và ID thật thông qua hàm `SUBSTRING()`.

## 5. Invalid Data Handling & Type Casting (Xử lý dữ liệu không hợp lệ & Định dạng ép kiểu)
Hàng nghìn bản ghi có ngày tháng bị lệch định dạng dạng số (Integer) hoặc chứa giá trị phi logic (ví dụ `0`).
- **Lọc ngày tháng rác:** Với các cột chứa ngày sinh (`bdate`) rơi vào **tương lai** (`bdate > GETDATE()`), chu trình sẽ thiết lập ngay về NULL (Bởi vì không cá nhân nào có thể có ngày sinh ở tương lai).
- **Ép kiểu định dạng Ngày tháng an toàn (Safe Date Casting):** Nếu một trường Date trong CRM bị lỗi thiếu ký tự (`LEN(sls_order_dt) != 8`) hoặc là `0`, tự động quy về NULL, ngược lại thì thiết lập kiểu dữ liệu DATE (`CAST(... AS DATE)`).

## 6. Mathematical Derivation & Data Imputation (Phép toán sửa lỗi và khôi phục dữ liệu bị khuyết)
Đặc biệt trên bảng Fact Sales (`crm_sales_details`), một số đơn hàng có giá trị hoặc doanh thu bị trống (`NULL`), bằng 0, số âm, hoặc bị tính sai tỷ lệ toán học (`Quantity * Price != Sales`).
- **Sửa sai số (Data Validation):** 
  - Nếu trường tổng chi phí Sales (`sls_sales`) bị thiếu/âm hoặc không khớp toán học (`!= sls_quantity * ABS(sls_price)`). Hệ thống sẽ tự động tự tính lại thông qua công thức `sls_quantity * ABS(sls_price)`.
  - Nếu Giá bán (`sls_price`) bị bỏ trống hoặc <= 0, hệ thống tự động suy xuất lại dựa trên công thức `sls_sales / NULLIF(sls_quantity, 0)`.
- **Khôi phục dữ liệu khuyết:** Với các dữ liệu chi phí ban đầu (`prd_cost`) bị khuyết, sử dụng hàm `ISNULL(prd_cost, 0)`.
- **Khởi tạo dữ liệu Logic lịch sử (Type 2 SCD):** Sử dụng hàm Windows `LEAD()` để tính toán thời gian giới hạn cuối cùng (End Date) của một sản phẩm cũ bằng cách lấy `Start Date` của sản phẩm được cập nhật sau - 1 Ngày.

---

**Kết quả sau Cleansing:** Tầng Silver giờ đây chứa hệ dữ liệu sạch (sạch lỗi Typo, sạch String format, sạch logic nghiệp vụ toán học, chuẩn hóa chung mọi định dạng từ điển). Sẵn sàng cung cấp dữ liệu cho thiết kế Dimension và Fact ở tầng Gold tiếp theo. Trang thái toàn vẹn dữ liệu được đảm bảo an toàn tối đa.
