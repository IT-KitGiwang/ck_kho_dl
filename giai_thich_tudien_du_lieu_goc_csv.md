# TỪ ĐIỂN Ý NGHĨA THỰC TẾ CÁC DATASET GỐC (CSV)

**Dự án:** SQL Data Warehouse Project  
**Tầng Dữ Liệu:** Raw Data (Đầu vào từ CRM và ERP)

Để làm được một kho dữ liệu đúng chuẩn, Data Engineer phải thực sự đóng vai một người làm Kinh Doanh (Business Analyst) để hiểu cặn kẽ vì sao các cột dữ liệu đó lại ra đời trong "Đời thực". Dưới đây là "Giải mã" toàn bộ ý nghĩa thực tế của 6 bảng dữ liệu nguồn.

---

## PHẦN 1: HỆ THỐNG CRM (PHẦN MỀM QUẢN LÝ QUAN HỆ KHÁCH HÀNG)
*Phần mềm này dùng cho bộ phận Sale / Marketing để chốt đơn và chăm sóc khách. Mang tính chất "tiền tuyến".*

### 1. `crm_cust_info` (Hồ sơ Khách mồi)
Bảng điền form đăng ký thành viên trên website hoặc tại quầy siêu thị.
- **`cst_id` & `cst_key`:** Một cái là ID ẩn của phần mềm máy tính (ID), một cái là Mã thẻ thành viên in cho khách xem (Key). 
- **`cst_firstname` , `cst_lastname`:** Tên khai sinh dùng để in hóa đơn và gửi Email chào mừng.
- **`cst_marital_status`:** Tình trạng Hôn nhân (Single - Độc thân / Married - Đã kết hôn).
  - *Ý nghĩa kinh doanh:* Phân tách rõ thói quen tiêu tiền. Người độc thân thường mua xe đạp thể thao đắt tiền cày phượt (Touring), người có gia đình hay mua xe chậm hơn hoặc đồ bảo hộ (Helmet) cho con cái.
- **`cst_gndr`:** Giới tính để gợi ý mẫu mã phù hợp.
- **`cst_create_date`:** Ngày lập thẻ thành viên. Dùng để xác định "Tuổi thọ" độ trung thành của khách. Hoặc để lấy hồ sơ mới nhất đem cập nhật đè lên hồ sơ gõ sai hồi xưa.

### 2. `crm_prd_info` (Kho Catalog Sản Phẩm)
Bộ Cẩm nang (Catalog) danh sách hàng đem bán cho Sale chào giá.
- **`prd_key`:** Mã vạch SKU (Stock Keeping Unit). Nhìn vào 5 chữ đầu của mã vạch nhân viên có thể biết ngay đó là Lốp xe hay là Khung xe (Chính là đoạn code cắt Substring ở tầng Silver). 
- **`prd_nm`:** Tên thương mại của sản phẩm.
- **`prd_cost`:** QUAN TRỌNG: Giá vốn ban đầu. Là số tiền công ty nhập khẩu cái xe/vật tư đó. Nó sẽ dùng để tính ngược lại Lợi nhuận sinh ra so với giá bán.
- **`prd_line`:** Dòng phân khúc (M: Mountain/Mạo hiểm, R: Road/Đua đường nhựa, T: Touring/Lượn phượt). 
- **`prd_start_dt`, `prd_end_dt`:** Ngày chào bán/Ngày ngừng kinh doanh phiên bản này trên thị trường. Quản lý vòng đời sản phẩm kiểu "Ra mắt iPhone 14, khai tử iPhone 13".

### 3. `crm_sales_details` (Máy POS Bán Hàng)
Sổ cái ghi nhận dòng thu chi của cửa hàng, là trung tâm sinh ra tiền.
- **`sls_ord_num`:** Mã số tham chiếu Hóa Đơn (Invoice Number) đưa cho khách đối chứng.
- **`sls_prd_key` & `sls_cust_id`:** Máy quét mã vạch Tít Sản phẩm và Tít Căn cước Khách hàng để biết Giao dịch này "Bán đồ gì cho ông nào".
- **`sls_order_dt`, `sls_ship_dt`, `sls_due_dt`:** Bộ tam thời gian theo dõi "Ngày khách Bấm Nút Đặt", "Ngày đóng gói Giao cho Shipper", và "Hạn chót/Deadline phải tới tay khách".
  - *Ý nghĩa kinh doanh:* Nếu Ngày Ship lố qua Hạn chót (Due Date) -> Công ty vi phạm hợp đồng, đối mặt nguy cơ khách đòi hoàn tiền hoặc đền bù thiệt hại chậm trễ.
- **`sls_quantity`, `sls_price`, `sls_sales`:** Theo thứ tự Số lượng * Đơn giá = Tiền phải thu khách. Bất kỳ sự chênh lệch nào ở đây cũng là dấu hiệu phần mềm tính tiền CRM bị lỗi hoặc Sale "ăn bớt" sửa tay tiền.

---

## PHẦN 2: HỆ THỐNG ERP (PHẦN MỀM QUẢN TRỊ TÀI NGUYÊN DOANH NGHIỆP)
*Phần mềm này dùng cho bộ phận Vận Hành (Kho bãi, Kế toán, Nhân sự). Mang tính "hậu phương", lưu trữ thông tin nội bộ quy mô lớn.*

### 4. `erp_cust_az12` (Khách hàng Hồ Sơ Mật ERP)
Có những thông tin cá nhân rất ngại nhập ở CRM (Sale không được biết), nên được phân quyền bảo mật riêng trong ERP.
- **`cid`:** Mã thẻ trùng khớp với CRM để CSDL có thông tin để ghép nối 2 hệ thống lại. Tuy nhiên, định dạng bên ERP đôi lúc đi kèm mã kho (ví dụ chữ `NAS` nhét vào đầu).
- **`bdate`:** Sinh nhật thật sự (Birth Date). 
  - *Ý nghĩa kinh doanh:* Cột sống còn cho Marketing. Móc cột này ra tính Tuổi, phân tập khách vào giỏ Millennials/GenZ/GenX để định hướng Facebook Ads, hoặc gửi Code Voucher chúc mừng sinh nhật đúng tháng.
- **`gen`:** Giới tính (Gender), một lần nữa lưu chéo để đối soát chất lượng dữ liệu với CRM. Do nhân viên hậu cần ERP nhập tay nên sinh ra rác kiểu "Male", "Female", "M", "F".

### 5. `erp_loc_a101` (Bảng Quản lý Luồng Hàng Logistics)
Quản trị địa lý vận chuyển trực thuộc ERP. Thiết yếu cho bộ phận Xuất Nhập Khẩu.
- **`cntry` (Country):** Tên quốc gia viết tắt của đơn hàng (như DE, US).
  - *Ý nghĩa kinh doanh:* Biết ông khách Mã 001 ở US thì kho tổng sẽ điều phối Container chuyển sang chi nhánh Tổng Mỹ để ship, thay vì tốn tiền ship từ tận Việt Nam. Dữ liệu này giúp Dashboard vẽ được Bản Đồ Nhiệt (Heatmap) Thị trường béo bở.

### 6. `erp_px_cat_g1v2` (Bảng Quy hoạch Ngành hàng ERP)
Phân bổ kệ hàng trong kho bãi chuyên dụng (Category Management).
- **`cat` & `subcat`:** Ngành hàng lớn (Ví dụ: Xe Đạp) chia xuống ngành hàng nhỏ (Xe Đua). Đi kèm số lượng nhãn hiệu rất lớn nên bộ phận ERP luôn phải gom nhóm chúng lại trước khi xuất Excel.
- **`maintenance`:** Cờ bảo trì (Yes/No).
  - *Ý nghĩa kinh doanh:* Một điểm nhấn cực hay. Các mặt hàng như Xe cộ, máy móc (Yes) thì cứ 6 tháng phải có nhân viên After-Sales (Chăm sóc sau bán) bốc máy alo nhắc khách mang ra tiệm thay xích/nhớt. Món nào bán đứt (Quần áo / Tất) thì gắn cờ "No" để đỡ tốn tiền gọi.
