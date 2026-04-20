# TỪ ĐIỂN DỮ LIỆU (DATA DICTIONARY) VÀ CẤU TRÚC LIÊN KẾT
**Dự án:** SQL Data Warehouse Project  
**Phiên bản:** Tầng Gold (V2) - Snowflake Schema  

Tài liệu này giải thích chi tiết ý nghĩa của toàn bộ 7 bảng (Tables), tóm tắt chức năng của các trường dữ liệu (Fields) và ánh xạ các Khóa liên kết (Primary Key / Foreign Key) để hiểu rõ luồng chạy dữ liệu của toàn bộ kho.

---

## PHẦN 1: CÁC BẢNG DIMENSION (BẢNG TRUY VẤN NGỮ CẢNH)
Đây là các bảng tạo ra "Bộ lọc" (Filters) trên các phần mềm báo cáo (BI Dashboard). Các Khóa Chính (PK) sinh ra ở đây được tự động tăng tự động (IDENTITY) và hoàn toàn độc lập với hệ thống gốc.

### 1. `DIM_TIME` (Chiều Thời Gian)
Bảng lịch vạn niên từ năm 2003 - 2030. Được dùng như một *Role-Playing Dimension* (Đóng nhiều vai trò ngày tháng cùng lúc).
- **`date_id` [PK - Khóa chính]:** Mã ngày định dạng `NămThángNgày` (VD: 20251008). Khóa này vô cùng nhẹ cho CSDL kết nối.
- `full_date`: Đầy đủ định dạng Ngày-Tháng-Năm chuẩn mực.
- `day`, `month`, `year`: Các cột bóc tách thông số phục vụ Drill-down báo cáo.
- `quarter`, `week_of_year`: Quý, Tuần thứ mấy.
- `day_name`, `month_name`: Tên Thứ (Monday) và Tháng (October).

### 2. `DIM_CATEGORY` (Chiều Danh Mục)
Bảng này tách rời từ Product nhằm tạo cấu trúc Snowflake, giảm thiểu dư thừa Text lặp.
- **`category_id` [PK - Khóa chính]:** Mã tự tăng quản lý danh mục.
- `category`: Tên Nhóm ngành lớn (Vd: Bikes - Xe đạp, Clothing - Quần áo).
- `subcategory`: Tên Hệ sinh thái con (Vd: Road Bikes, Mountain Bikes, Socks).
- `maintenance_flag`: Cờ đánh dấu dòng sản phẩm này có cần bảo trì định kỳ hay không (Yes/No).

### 3. `DIM_PRODUCT` (Chiều Sản Phẩm)
Bộ hồ sơ các sản phẩm mà công ty đang bán.
- **`product_id` [PK - Khóa chính mới]:** Mã tự tăng cấp bởi Data Warehouse (Surrogate Key). Dùng hệ thống mã này rất an toàn nếu CRM gốc bị hỏng khóa.
- `product_key`: Mã Business Key nguyên thủy kéo từ hệ thống CRM (Vd: CB-290). Dùng để đối chiếu rà soát lỗi nếu cần thiết.
- `product_name`: Tên kỹ thuật/thương mại của sản phẩm.
- `product_line`: Phân loại dòng xe (R: Road, M: Mountain).
- **`category_id` [FK - Khóa ngoại]:** Khóa nối ngược về bảng `DIM_CATEGORY`.
  - *Mục đích liên kết:* Trả lời câu hỏi "Sản phẩm A thuộc danh mục bự nào?". Giúp vẽ biểu đồ Cuộn/Gộp (Roll-up) từ Sản phẩm lên cấp Nhóm ngành.

### 4. `DIM_CUSTOMER` (Chiều Khách Hàng)
Bộ hồ sơ thông tin danh tính người mua.
- **`customer_id` [PK - Khóa chính mới]:** Mã tự tăng cấp bởi Data Warehouse.
- `customer_key`: Mã đối chiếu từ CRM.
- `first_name`, `last_name`: Họ tên khách hàng (Đã làm sạch khoảng trắng).
- `gender`: Giới tính (Đã chuẩn hóa Male/Female).
- `marital_status`: Hôn nhân (Single/Married).
- `birth_date`: Sinh nhật khách hàng (Đã check ngày tương lai ảo).

### 5. `DIM_LOCATION` (Chiều Địa Lý)
Cũng là nhánh Snowflake tách từ khách hàng. Quản lý bản đồ phân phối tệp người mua.
- **`location_id` [PK - Khóa chính mới]:** Mã tự tăng địa lý.
- `country`: Tên quốc gia chuẩn hóa.
- `region`: Nhóm châu lục (Vd: North America, Europe).

---

## PHẦN 2: CÁC BẢNG FACT (BẢNG SỰ KIỆN / ĐO LƯỜNG SỐ LIỆU)
Bảng Fact là trung tâm của các bản báo cáo kinh doanh, nơi chứa các phép cộng trừ nhân chia về tiền bạc và số lượng.

### 6. `FACT_SALES` (Bảng Giao Dịch Bán Hàng)
Ghi nhận từng món hàng (Line-Item) bán đi mỗi ngày. Nó đứng ở giữa và tỏa ra **6 Khóa Ngoại (FK)** để chiếu đến 5 Bảng Dimension.

**➤ CÁC TRƯỜNG ĐO LƯỜNG & DỮ LIỆU ĐỊNH DANH (Measures):**
- `order_id`: Mã Hóa đơn CRM (Degenerate Dimension). Không nối với bảng nào cả, giữ lại để phòng hờ kế toán công ty đòi kiểm tra chéo Hóa Đơn.
- `quantity`: Số lượng đã bán.
- `sales_amount`: Tổng doanh thu món đó.
- `unit_price`, `unit_cost`: Đơn giá lúc bán, và Giá vốn nhập lúc bán (Lấy giá ghim ngay lúc xuất đơn, vô cùng khó bị sai lệch).
- `days_to_ship`, `days_to_due`: Những chỉ số máy tự tính trước (Pre-calculated) để biết ngay giao mất bao ngày và có bị trễ hay không.

**➤ CÁC KHÓA NGOẠI (Foreign Keys) VÀ CHỨC NĂNG LIÊN KẾT:**
- **`customer_id` (trỏ đến DIM_CUSTOMER):** Trả lời "Biên lai này do **AI** (Ông bà nào) mua?".
- **`product_id` (trỏ đến DIM_PRODUCT):** Trả lời "Biên lai này bán **CÁI GÌ**?". Truy được luôn tới Category.
- **`location_id` (trỏ đến DIM_LOCATION):** Trả lời "Người mua cái Biên lai này sống **Ở ĐÂU**?".
- **Hệ thống khóa Ngày (Trỏ đến DIM_TIME):**
  - **`order_date_id`**: Đo lường Doanh thu sinh ra vào **Ngày Nào**.
  - **`ship_date_id`**: Áp dụng báo cáo bộ phận Logistics xem họ bắt đầu chuyển hàng vào ngày nào.
  - **`due_date_id`**: Áp dụng cho bộ phận kho theo dõi Deadline giao hàng mốc nào.

### 7. `FACT_PRODUCT_PRICE` (Bảng Sự kiện Snapshot Giá vốn Lịch sử)
Là bảng lưu vết mọi đợt biến động giá của công ty để chạy kế toán chênh lệch.
- **`product_price_id` [PK]:** Khóa theo dõi phiên bản giá.
- **`cost`:** Con số giá vốn nhập hàng vào.
- **`is_current`:** Cột quyết định. Nếu `1` tức là giá này đang còn hạn dùng hôm nay. Giá `0` là giá đồ cũ.
- **CÁC KHÓA NGOẠI (Foreign Keys):**
  - **`product_id` (trỏ đến DIM_PRODUCT):** Báo cho CSDL biết con số giá này là của Cái Xe Đạp hay Cái Mũ.
  - **`start_date_id` (trỏ đến DIM_TIME):** Ngày công ty bắt đầu áp giá mới.
  - **`end_date_id` (trỏ đến DIM_TIME):** Khóa trỏ đến ngày công ty ngừng xài mức giá này (Thường NULL nếu giá đang hiện hành).
