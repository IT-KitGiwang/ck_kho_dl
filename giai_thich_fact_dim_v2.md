# GIẢI THÍCH VAI TRÒ CỦA CÁC BẢNG FACT VÀ DIMENSION DỰ ÁN V2

**Dự án:** SQL Data Warehouse Project  
**Kiến trúc xử lý:** Snowflake Schema (Tầng Gold v2)

Trong hệ thống kho dữ liệu (Data Warehouse), dữ liệu phải được chia thành 2 loại bảng cốt lõi là **FACT** và **DIMENSION**. Mục đích của việc chia này là để phục vụ khả năng truy vấn dữ liệu ở tốc độ cao cho các hệ thống phần mềm báo cáo (BI Tools như Tableau, PowerBI), đồng thời làm rõ ngữ cảnh kinh doanh.

Dưới đây là giải thích chi tiết chức năng của từng bảng trong kiến trúc `gold_v2.sql`.

---

## 1. FACT TABLES (BẢNG SỰ KIỆN / ĐO LƯỜNG)
Bảng Fact là trung tâm của kho dữ liệu. Nó lưu trữ các **sự kiện** (hành động sinh ra số liệu, tiền bạc, giao dịch) và chứa các con số **đo lường được (Measures)** dùng để làm toán học (Cộng, Trừ, Trung bình).

### 1.1 `FACT_SALES` (Bảng Sự kiện Giao dịch Bán Hàng)
- **Nó để làm gì?** Đây là trái tim của hệ thống bán hàng. Nó lưu trữ lịch sử của BẤT KỲ GIAO DỊCH BÁN HÀNG NÀO (Mỗi dòng là 1 món hàng nằm trong 1 hóa đơn). 
- **Nó chứa cái gì?**
  - **Khóa (Keys):** Nó chắp nối mọi chiều không gian bằng cách chứa khóa ID của Ai mua (`customer_id`), Mua cái gì (`product_id`), Mua ở đâu (`location_id`), Mua khi nào (`order_date_id`).
  - **Số đo (Measures):** Lưu số lượng bán (`quantity`), doanh thu (`sales_amount`), giá bán (`unit_price`).
  - **Chỉ số tính sẵn (Pre-Calculated - V2):** Đặc biệt ở V2, nó lưu luôn giá vốn tại lúc bán (`unit_cost`) và thời gian giao hàng (`days_to_ship`).
- **Ứng dụng BI:** Dùng để vẽ biểu đồ tổng doanh thu, tỷ suất lợi nhuận gộp (Margin), và tỷ lệ giao hàng trễ hẹn.

### 1.2 `FACT_PRODUCT_PRICE` (Bảng Sự kiện Lịch sử Giá)
- **Nó để làm gì?** Đây là bảng quản lý lịch sử (Periodic Snapshot). Trong thực tế kinh doanh, giá trị nhập hàng (giá vốn - cost) thay đổi liên tục theo từng thời kỳ làm phát sinh chênh lệch lợi nhuận. Nếu chỉ lưu giá hiện hành, kế toán sẽ tính sai sổ sách các tháng trước.
- **Nó chứa cái gì?** Nó lưu ngày bắt đầu áp dụng giá (`start_date_id`), ngày kết thúc giá đó (`end_date_id`), và cột trạng thái giá đang kích hoạt (`is_current = 1`).
- **Ứng dụng BI:** Dùng để dò lại toàn bộ lịch sử chi phí thay đổi cấu thành sản phẩm trong khoảng thời gian 10-20 năm mà không bị mất dấu.

---

## 2. DIMENSION TABLES (BẢNG CHIỀU PHÂN TÍCH / NGỮ CẢNH)
Bảng Dimension (Dim) luôn vây quanh bảng Fact. Nó mang nhiệm vụ **giải thích ngữ cảnh**. Nếu bảng Fact báo có "1 ông mã ID số 5 mua cái xe ID số 10", thì bảng Dim sẽ trả lời "Ông số 5 tên là gì, bao nhiêu tuổi?", "Xe số 10 màu gì, dòng xe nào?".
*Đặc tính của rễ các từ tiếng anh hay dùng là Who (Ai), What (Cái gì), Where (Ở đâu), When (Khi nào).*

### 2.1 `DIM_CUSTOMER` (Chiều Khách Hàng - Tiêu chí: WHO)
- **Nó để làm gì?** Lưu toàn bộ hồ sơ nhân khẩu học của khách.
- **Góc nhìn phân tích:** Giúp vẽ các biểu đồ phân tích tệp khách hàng theo độ tuổi người mua, tình trạng hôn nhân (để xem người có gia đình hay độc thân mua nhiều xe đạp hơn), giới tính nam/nữ.

### 2.2 `DIM_PRODUCT` (Chiều Sản Phẩm - Tiêu chí: WHAT)
- **Nó để làm gì?** Mổ xẻ chi tiết định danh món hàng.
- **Góc nhìn phân tích:** Vẽ biểu đồ so sánh các Dòng sản phẩm (`product_line`) như xe đua hạng nhẹ (Road) hay xe leo núi (Mountain), sản phẩm nào đang tạo ra tiền nhiều nhất.

### 2.3 `DIM_CATEGORY` (Chiều Danh Mục - Tiêu chí: WHAT - SNOWFLAKE)
- **Nó để làm gì?** Tại sao tách khỏi Product? Để tối ưu dung lượng và chống sai chính tả lặp chữ. Bảng này quản lý cây thư mục cấp cao như Nhóm ngành (Bikes, Accessories, Clothing) và Phân khúc (`subcategory`).
- **Góc nhìn phân tích:** Cho góc nhìn quản trị tầm vĩ mô. Giám đốc sẽ xem doanh thu nhóm `Bikes` trong năm so với nhóm `Clothing` chứ không rảnh đi xoi từng tên cái xe ở bảng Product.

### 2.4 `DIM_LOCATION` (Chiều Địa Lý Quốc Gia - Tiêu chí: WHERE)
- **Nó để làm gì?** Quản lý khu vực tọa độ lãnh thổ. 
- **Góc nhìn phân tích:** Phục vụ vẽ Data Maps (bản đồ). Hiển thị rực rỡ xem Thị trường Bắc Mỹ (North America) hay Châu Âu (Europe) đem lại nguồn tiền chính.

### 2.5 `DIM_TIME` (Chiều Thời Gian Đa Năng - Tiêu chí: WHEN)
- **Nó để làm gì?** Thay vì mỗi lần làm báo cáo phải yêu cầu tính lại hàm ngày tháng (Ví dụ: móc số năm, số tháng ra khỏi biến Date). Bảng này chẻ sẵn 1 ngày ra thành 10 thuộc tính riêng: thứ mấy trong tuần, tuần thứ mấy trong năm, quý (quarter).
- **Tuyệt chiêu Role-Playing (Đóng nhiều vai):** Tại bảng `FACT_SALES`, nó đóng 3 vai diễn cùng lúc là "Ngày đặt hàng", "Ngày giao", "Ngày trễ hẹn". 
- **Góc nhìn phân tích:** Cực kỳ mạnh! Nó trả lời được các câu hỏi siêu khó: "Có phải khách có thói quen mua nhiều xe đạp nhất vào sáng Thứ 2 (Monday) của Quý 3 không?". Lên BI chỉ cần nhấp kéo và thả.
