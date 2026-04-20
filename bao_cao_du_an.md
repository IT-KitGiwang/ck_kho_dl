# BÁO CÁO TỔNG KẾT DỰ ÁN: SQL DATA WAREHOUSE & ANALYTICS

**Dự án:** SQL Data Warehouse Project  
**Mục tiêu:** Xây dựng một Kho dữ liệu (Data Warehouse) hiện đại dựa trên nền tảng cơ sở dữ liệu (SQL Server/Snowflake) để tích hợp và chuẩn hóa dữ liệu bán hàng từ nhiều nguồn khác nhau (CRM và ERP). Từ đó, cung cấp nguồn dữ liệu đã làm sạch và được mô hình hóa cho các mục tiêu phân tích (Customer Behavior, Product Performance, Sales Trends).  

---

## 1. Kiến Trúc Hệ Thống Đã Triển Khai
Dự án được ứng dụng chuẩn kiến trúc dữ liệu **Medallion Architecture** phổ biến hiện nay, bao gồm 3 tầng: **Bronze**, **Silver** và **Gold**.

- **Bronze Layer (Raw Data):** Nơi lưu trữ dữ liệu thô (raw data) gốc được nhập từ các file CSV (CRMs và ERPs), không có sự thay đổi về bản chất dữ liệu so với nguồn.
- **Silver Layer (Cleaned & Normalized Data):** Tầng làm sạch, chuẩn hóa và xử lý các vấn đề về Data Quality. Dữ liệu từ các nguồn khác nhau được đồng nhất kiểu dữ liệu, định dạng văn bản và kết nối với nhau.
- **Gold Layer (Business Ready Data):** Tầng cung cấp dữ liệu sẵn sàng cho hoạt động Business Intelligence (BI). Áp dụng mô hình thiết kế **Star Schema** bao gồm các bảng Fact (Sự kiện) và Dimension (Chiều phân tích).

---

## 2. Chi Tiết Các Công Việc Đã Hoàn Thành

### 2.1. Thiết Kế & Tài Liệu (Docs & Design)
- Hoàn thiện sơ đồ luồng dữ liệu (Data Flow) và kiến trúc hệ thống (Data Architecture).
- Hoàn thiện sơ đồ mô hình hóa dữ liệu (Data Model) áp dụng Star Schema.
- Thiết lập tài liệu **Data Catalog** (danh mục dữ liệu chi tiết) và **Naming Conventions** (quy chuẩn đặt tên bảng, cột, file).

### 2.2. Khởi Tạo Cơ Sở Dữ Liệu
- Đã tạo script `init_database.sql` để tạo mới database và các schema cần thiết (`bronze`, `silver`, `gold`).

### 2.3. Tầng Bronze (Extract & Load)
- **Data Definition (DDL):** Tạo script `ddl_bronze.sql` chứa cấu trúc các bảng chuyên dụng cho dữ liệu thô.
- **Data Load Procedure:** Xây dựng Stored Procedure `proc_load_bronze.sql` để thực thi chu trình BULK INSERT đưa dữ liệu gốc từ định dạng CSV của hệ thống CRM và ERP vào thẳng các bảng Bronze.

### 2.4. Tầng Silver (Data Transformation & Cleansing)
- **Data Definition (DDL):** Xây dựng `ddl_silver.sql` chuẩn hóa cấu trúc dữ liệu theo đúng chuẩn.
- **Data Load Procedure:** Hoàn thiện `proc_load_silver.sql`. Khối code này giải quyết triệt để các vấn đề:
  - Làm sạch dữ liệu, loại bỏ giá trị null không hợp lệ.
  - Xử lý mâu thuẫn hệ thống lưu trữ (ví dụ: gộp thông tin User từ ERP và CRM lại với nhau).
  - Chuẩn hóa chuỗi (string formatting) và ép kiểu dữ liệu ngày tháng/số (Data type casting).

### 2.5. Tầng Gold (Data Modeling for Analytics)
- Dự án đã khởi tạo cấu trúc Star Schema sử dụng các View thông qua `ddl_gold.sql`, bao gồm:
  - **`gold.dim_customers` (Dimension View):** Bảng chiều Quản lý Khách Hàng. Trích xuất, kết hợp logic dữ liệu nhân khẩu học hiệu quả nhất giữa hệ thống CRM (thông tin chính) và ERP (thông tin bổ sung fallback) để tạo ra list khách hàng chuẩn với Surrogate Key (`customer_key`).
  - **`gold.dim_products` (Dimension View):** Bảng chiều Quản lý Sản Phẩm. Lọc ra các sản phẩm khả dụng hiện tại (loại bỏ historical data lỗi thời) kèm thông tin phân mục (category/subcategory) bằng Surrogate Key (`product_key`).
  - **`gold.fact_sales` (Fact View):** Bảng sự kiện Bán Hàng trung tâm. Dễ dàng map và tính toán được doanh thu (`sales_amount`), giá bán (`price`), số lượng (`quantity`) vào từng khách hàng (`customer_key`) và từng sản phẩm (`product_key`) với các thông tin ngày tháng giao nhận cụ thể (`order_date`, `shipping_date`).

### 2.6. Quality Assurance (Kiểm Thử)
- Cấu trúc thư mục chứa các scripts chuyên phục vụ việc testing (trong folder `/tests/`) để review đầu ra và phát hiện bug rò rỉ dữ liệu trước khi ra mắt báo cáo.

---

## 3. Kết Luận
Toàn bộ dự án Data Warehouse cơ bản cấu trúc đã **HOÀN CHỈNH TẦNG DỮ LIỆU (DATA ENGINEERING)**. Đường ống ETL (Extract - Transform - Load) từ khâu đọc file thô cho tới khâu chuyển đổi, tổng hợp ra được bộ Data Model (Star Schema) cuối cùng đáp ứng rất tốt để đẩy vào các hệ thống BI Tools như Tableau, PowerBI hoặc truy vấn SQL trực tiếp phục vụ phân tích nghiệp vụ chuyên sâu.
