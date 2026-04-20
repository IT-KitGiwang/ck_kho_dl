# 📘 BỘ TỪ ĐIỂN CÔNG THỨC DATA CLEANSING TRÊN SSIS (DERIVED COLUMN EXPRESSIONS)

Tài liệu này tổng hợp **toàn bộ mã code (Expressions) chuẩn nhất** để dán vào cục **Derived Column** trong SSIS cho tất cả 6 bảng theo đúng yêu cầu từ `bao_cao_lam_sach_du_lieu.md`.
Bạn chỉ cần mở tài liệu này, Copy mã Expression ở cột phải, và Paste thẳng vào ô gõ công thức trên SSIS là tỉ lệ lỗi bằng 0%.

---

## 1. NẠP DIM_CATEGORY (Nguồn: `PX_CAT_G1V2.csv`)
*Nhiệm vụ: Cắt gọt lỗi khoảng trắng văn bản.*

| Tên cột đặt mới (Derived Column Name) | Công thức SSIS (Expression) để Copy |
| :--- | :--- |
| `clean_category` | `TRIM([CAT])` |
| `clean_subcategory` | `TRIM([SUBCAT])` |

*(Cột `MAINTENANCE` bạn có thể map thẳng vào SQL vì nó đã sạch sẵn).*

---

## 2. NẠP DIM_LOCATION (Nguồn: `LOC_A101.csv`)
*Nhiệm vụ: Loại bỏ dấu gạch ngang của mã khách, chuẩn hóa tên quốc gia và chia khu vực.*

| Tên cột đặt mới | Công thức SSIS (Expression) để Copy |
| :--- | :--- |
| `clean_cid` | `REPLACE([CID], "-", "")` |
| `clean_country` | (DT_WSTR,50)TRIM([CNTRY]) == "DE" ? "Germany" : ((DT_WSTR,50)TRIM([CNTRY]) == "US" || (DT_WSTR,50)TRIM([CNTRY]) == "USA" ? "United States" : (DT_WSTR,50)TRIM([CNTRY]))
| `derived_region` | [clean_country] == "United States" || [clean_country] == "Canada" ? "North America" : ([clean_country] == "Germany" || [clean_country] == "France" || [clean_country] == "United Kingdom" ? "Europe" : "Pacific")

---

## 3. NẠP DIM_CUSTOMER — TỪ NGUỒN CRM (Nguồn: `cust_info.csv`)
*Nhiệm vụ: Chuẩn hóa Trimming, Gender (M/F) và Tình trạng hôn nhân.*
*(Lưu ý: Trong Data Flow, phải dùng hộp **Sort** tích chọn "Remove rows with duplicate sort values" theo `cst_id` tăng dần và `cst_create_date` giảm dần để thỏa mãn kỹ thuật Deduplication).*

| Tên cột đặt mới | Công thức SSIS (Expression) để Copy |
| :--- | :--- |
| `clean_firstname` | `TRIM([cst_firstname])` |
| `clean_lastname` | `TRIM([cst_lastname])` |
| `clean_marital` | `TRIM([cst_marital_status]) == "S" ? "Single" : (TRIM([cst_marital_status]) == "M" ? "Married" : "n/a")` |
| `clean_gender_crm`| `UPPER(TRIM([cst_gndr])) == "M" ? "Male" : (UPPER(TRIM([cst_gndr])) == "F" ? "Female" : "n/a")` |

---

## 4. NẠP DIM_CUSTOMER — TỪ NGUỒN ERP (Nguồn: `CUST_AZ12.csv`)
*Nhiệm vụ: Bóc tách mã khách dính tạp chất "NAS" đầu chuỗi, xử lý giới tính và loại bỏ ngày sinh tương lai phi logic.*

| Tên cột đặt mới | Công thức SSIS (Expression) để Copy |
| :--- | :--- |
| `clean_erp_cid` | `LEFT([CID], 3) == "NAS" ? SUBSTRING([CID], 4, LEN([CID]) - 3) : [CID]` |
| `clean_bdate` | `ISNULL([BDATE]) ? NULL(DT_DBDATE) : ((DT_DBDATE)[BDATE] > GETDATE() ? NULL(DT_DBDATE) : (DT_DBDATE)[BDATE])` |
| `clean_gender_erp`| `UPPER(TRIM([GEN])) == "M" || UPPER(TRIM([GEN])) == "MALE" ? "Male" : (UPPER(TRIM([GEN])) == "F" || UPPER(TRIM([GEN])) == "FEMALE" ? "Female" : "n/a")` |

*(MẸO SAU KHI MERGE JOIN CRM & ERP): Bạn dùng 1 cái Derived Column ở đầu chót với công thức sau để ưu tiên lấy Giới Tính bên ERP (chuẩn hơn) đè lên CRM:*
- `final_gender` : `!ISNULL([clean_gender_erp]) && [clean_gender_erp] != "n/a" ? [clean_gender_erp] : [clean_gender_crm]`

---

## 5. NẠP DIM_PRODUCT (Nguồn: `prd_info.csv`)
*Nhiệm vụ: Cắt key phức hợp thành Category_ID và Product_ID Thực; Khôi phục cost bị khuyết, Map Product Line.*

| Tên cột đặt mới | Công thức SSIS (Expression) để Copy |
| :--- | :--- |
| `clean_prd_nm` | `TRIM([prd_nm])` |
| `clean_prd_cost` | `ISNULL([prd_cost]) ? 0 : [prd_cost]` |
| `clean_prd_line` | `TRIM([prd_line]) == "M" ? "Mountain" : (TRIM([prd_line]) == "R" ? "Road" : (TRIM([prd_line]) == "T" ? "Touring" : (TRIM([prd_line]) == "S" ? "Other Sales" : "n/a")))` |
| `cat_id` | `SUBSTRING([prd_key], 1, FINDSTRING([prd_key], "-", 1) + FINDSTRING(SUBSTRING([prd_key], FINDSTRING([prd_key], "-", 1) + 1, LEN([prd_key])), "-", 1) - 1)` |
| `clean_prd_key` | `SUBSTRING([prd_key], FINDSTRING([prd_key], "-", 1) + FINDSTRING(SUBSTRING([prd_key], FINDSTRING([prd_key], "-", 1) + 1, LEN([prd_key])), "-", 1) + 1, LEN([prd_key]))` |

---

## 6. NẠP FACT_SALES (Nguồn: `sales_details.csv`)
*Nhiệm vụ: Sửa sai số và khôi phục giá Sales / Price theo chuẩn công thức toán học (`Quantity * Price = Sales`).*

💡 **LỜI KHUYÊN KIẾN TRÚC:** 
Bảng Fact chứa logic xử lý các Ngày (Date bị độ dài khác 8 hoặc bằng 0). SSIS Expression xử lý Date String lỗi sang kiểu DateTime rất hay báo lỗi đỏ cả luồng. Tốt nhất ở bảng Fact_Sales này bạn **KHÔNG NÊN** dùng Derived Column, mà hãy nạp thẳng CSV vào bảng tạm (`stg_sales`) ròi dùng `CASE WHEN` SQL sửa nó.

Tuy nhiên, nếu bạn vẫn muốn dùng SSIS Derived Column ép dẻo để Sửa Giá/Sửa Doanh Thu, đây là công thức:

| Tên cột đặt mới | Công thức SSIS (Expression) để Copy |
| :--- | :--- |
| `clean_ord_num` | `TRIM([sls_ord_num])` |
| `clean_prd_key` | `TRIM([sls_prd_key])` |
| `calc_sales` | `ISNULL([sls_sales]) || [sls_sales] <= 0 || [sls_sales] != ([sls_quantity] * ABS([sls_price])) ? ([sls_quantity] * ABS(ISNULL([sls_price]) ? 0 : [sls_price])) : [sls_sales]` |
| `calc_price` | `ISNULL([sls_price]) || [sls_price] <= 0 ? ([sls_sales] / NULLIF([sls_quantity], 0)) : ABS([sls_price])` |
