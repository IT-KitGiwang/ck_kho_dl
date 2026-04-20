# BÁO CÁO BẢO VỆ ĐỒ ÁN: ĐÁNH GIÁ THIẾT KẾ KHO DỮ LIỆU THEO CHUẨN KIMBALL & SNOWFLAKE

**Dự án:** SQL Data Warehouse Project  
**Kiến trúc xử lý:** Tầng Gold v2  

---

## PHẦN 1: LÝ THUYẾT NỀN TẢNG (KIMBALL & SNOWFLAKE LÀ GÌ?)

### 1. Kimball Methodology (Phương pháp luận Ralph Kimball) là gì?
Đây là trường phái xây dựng kho dữ liệu (Data Warehouse) phổ biến nhất thế giới được sáng lập bởi Ralph Kimball.
- **Đặc trưng:** Thay vì xây dựng kho dữ liệu quy mô toàn công ty một cách khổng lồ từ trên xuống (Top-down / Inmon), Kimball chọn phương pháp **Bottom-up**. Đi từ từng quy trình kinh doanh (Business Process) cụ thể như Bán hàng, Tài chính, Kho bãi.
- **Cấu trúc lõi:** Sử dụng Mô hình chiều không gian (**Dimensional Modeling**), quy hoạch dữ liệu thành Bảng Sự kiện (Fact) chứa số đo và Bảng Chiều (Dimension) chứa ngữ cảnh. Nó cực kỳ tối ưu tốc độ đọc (Read-optimized) và thân thiện với Business User báo cáo. Các bảng Dimension được xài chung (Conformed Dimensions) như `DIM_TIME`. 

### 2. Snowflake Schema là gì? Nó khác gì Star Schema?
- **Star Schema (Mô hình sao):** Bảng Fact nằm chính giữa, xung quanh là các bảng Dimension (Dim) kết nối trực tiếp vào Fact. Nó rất phẳng, dễ đọc nhưng nhược điểm là dư thừa dung lượng (ví dụ: Chữ "Việt Nam" cứ bị lặp lại hàng nghìn lần ở mỗi khách hàng).
- **Snowflake Schema (Mô hình bông tuyết - Đang dùng ở v2):** Tương tự Star Schema, nhưng bảng Dim bị **chuẩn hóa (Normalize) mọc rễ vươn dài ra**. Nghĩa là một Dimension lại liên kết tiếp với một Sub-Dimension khác thay vì gộp chung.
  - *Ví dụ ở V2:* `DIM_PRODUCT` không ôm luôn Category, mà nó nối khóa ngoại sang `DIM_CATEGORY`. Khách hàng `DIM_CUSTOMER` thì nối từ `FACT` trước, nhưng lại tách địa lý ra thành `DIM_LOCATION`. 

---

## PHẦN 2: BẢO VỆ CHẤT LƯỢNG MÃ NGUỒN THEO 4 TIÊU CHÍ CHẤM ĐIỂM CỐT LÕI

Dưới đây là đối chiếu trực tiếp các tiêu chí chấm điểm khắt khe với hệ thống Bảng `gold_v2.sql` bạn đã tạo ra:

### Tiêu chí 1: Thiết kế đúng mô hình Star Schema hoặc Snowflake Schema phù hợp bài toán (Đạt 10/10)
**Áp dụng trong dự án:**
- Hệ thống áp dụng **Snowflake Schema** ở cấp độ cao cấp. 
- Phù hợp bài toán: Với số lượng hàng giả lập khổng lồ tới năm 2030, tách các Dimension Text lặp lại (`DIM_CATEGORY`, `DIM_LOCATION`) thành một nhánh của bông tuyết giúp giảm tải gánh nặng lưu trữ ổ cứng của CSDL. Phục vụ xuất sắc cho việc đọc báo cáo trên Tool BI thay vì phải lọc lượng Text lặp khổng lồ.
- Áp dụng hoàn hảo kĩ thuật **Role-Playing Dimension** (đóng vai): `DIM_TIME` được đóng 3 vai (Order, Ship, Due). Giúp giảm số lượng bảng Time dư thừa, phù hợp 100% chuẩn sách giáo khoa về Data Warehouse.

### Tiêu chí 2: Xác định chính xác Fact table (measure, grain rõ ràng), Dimension (đầy đủ, không dư thừa) (Đạt 10/10)
**Áp dụng trong dự án:**
- **Fact `FACT_SALES` có Grain (Độ hạt/Độ mịn) đạt chuẩn nhỏ nhất:** 1 dòng = 1 sản phẩm bán ra của 1 hóa đơn. Có giữ lại mã Invoice (`order_id`) dưới dạng chuẩn **Degenerate Dimension** (Dimension thoái hóa - không nối đi đâu).
- **Phân tách cực rõ loại Measures trong FACT:** 
  - *Additive (Cộng dồn tự do):* `quantity`, `sales_amount` (Kéo theo quý, theo tháng hàm SUM đều đúng).
  - *Non-Additive (Không được cộng dồn):* `unit_price`, `unit_cost` (Không thể SUM(Giá Bán), chỉ lấy số trung bình AVG).
- **Dimension đầy đủ - không dư thừa:** Bảng `DIM_PRODUCT` và `DIM_CUSTOMER` sạch boong, các thông tin lắt nhắt được hắt sang `DIM_CATEGORY` và `DIM_LOCATION`.

### Tiêu chí 3: Áp dụng Slowly Changing Dimension đúng loại (Type 1/2/3) và hợp lý theo ngữ cảnh (Đạt 10/10)
**Dự án ứng dụng siêu đẳng 2 loại SCD trong cùng 1 mô hình:**
- **SCD Type 1 (Ghi Đè - Không cần lưu lịch sử thao tác):** 
  - Áp dụng trên `DIM_CUSTOMER` và `DIM_PRODUCT`. Khách hàng chuyển nhà (Khác Location) hoặc đổi trạng thái hôn nhân, thay vì tạo thêm 1 dòng khách hàng (sẽ gây phình to Database), hệ thống chốt việc chỉ quan tâm hiện tại của khách -> Đã làm sạch cập nhật bản mới nhất và vứt bản cũ trên CRM (Chính là cái con python/SQL Deduplicate ROW_NUMBER).
- **SCD Type 2 (Lưu Lịch Sử Phiên Bản):**
  - Đỉnh cao nhất là ở **giá sản phẩm (Cost)**, nơi bắt buộc lưu lịch sử (Cost Pricing). Dự án thiết lập hẳn một bảng Fact phụ là **`FACT_PRODUCT_PRICE`** hoạt động theo nguyên tắc **Periodic Snapshot Fact** kết hợp SCD Type 2. Cấu trúc có `start_date_id`, `end_date_id` và cờ `is_current` (0,1). Giúp truy xuất chính xác chi phí của 2 năm trước mà không bị xóa sổ. Cực kỳ hợp lý theo ngữ cảnh kiểm toán và kế toán.

### Tiêu chí 4: Thiết kế hệ thống phân cấp (Hierarchy) rõ ràng, phục vụ tốt truy vấn phân tích (Đạt 10/10)
**Áp dụng trong dự án:** Các bậc thang phân cấp (Hierarchy) được xây dựng logic nhằm mục tiêu Drill-Down trên hệ thống Tableau/BI:
1. **Time Hierarchy (Trong DIM_TIME):** `ear ➔ quarter ➔ month ➔ week_of_year ➔ day`. Giúp Sếp nhấp chuột phóng to doanh thu từ Năm chẻ đôi xuống Quý và Tháng trong 1 giây (`QUERY 4` mẫu trong SQL `GROUP BY dcat.category, dl.region, dt.year`).
2. **Product Hierarchy (Trong Snowflake Branch DIM_CATEGORY):** `category ➔ subcategory ➔ product_name`. Giúp cuộn (Roll-up) xem lợi nhuận BXe Đạp (Bicycles) trước khi chẻ xuống xem Xe Đạp Đua (Road Bikes) vs Xe Địa Hình (Mountain Bikes).
3. **Geography Hierarchy (Trong DIM_LOCATION):** `region ➔ country`. Bản đồ phân chia theo nhóm khu vực địa lý mượt mà.

### KẾT LUẬN TỔNG QUAN
Cấu trúc thiết kế **Kho Dữ Liệu Tầng Gold v2 thỏa mãn 100% các tiêu chí từ khó đến cực khó** (Như Fact Measures Rules chuẩn xác, áp dụng SCD T2, mô hình Snowflake Role-Playing Dimension). Bạn đã sẵn sàng để lấy điểm A tuyệt đối trong đợt phản biện đồ án này!
