import pandas as pd
import numpy as np
import datetime
import os

# Define paths
base_dir = r"e:\JOURNEY DATA ENGINEERING\Kho dữ liệu cuối kỳ\example\sql-data-warehouse-project\datasets"
crm_cust_path = os.path.join(base_dir, r"source_crm\cust_info.csv")
crm_prd_path = os.path.join(base_dir, r"source_crm\prd_info.csv")
crm_sales_path = os.path.join(base_dir, r"source_crm\sales_details.csv")
erp_cust_path = os.path.join(base_dir, r"source_erp\CUST_AZ12.csv")
erp_loc_path = os.path.join(base_dir, r"source_erp\LOC_A101.csv")

def main():
    print("="*80)
    print("BÁO CÁO KIỂM TRA CHẤT LƯỢNG DỮ LIỆU (DATA QUALITY ASSESSMENT)")
    print("="*80)

    try:
        # Load datasets
        crm_cust = pd.read_csv(crm_cust_path)
        crm_prd = pd.read_csv(crm_prd_path)
        crm_sales = pd.read_csv(crm_sales_path)
        erp_cust = pd.read_csv(erp_cust_path)
        erp_loc = pd.read_csv(erp_loc_path)
        
        # Normalize column names to lowercase to avoid KeyError
        for df in [crm_cust, crm_prd, crm_sales, erp_cust, erp_loc]:
            df.columns = df.columns.str.strip().str.lower()
            
    except Exception as e:
        print(f"Error loading files: {e}")
        return

    # -------------------------------------------------------------------------
    # 3.2.2.1. Sai lệch cấu trúc Key và thiếu hụt Key-Mapping
    # -------------------------------------------------------------------------
    print("\n[1] SAI LỆCH CẤU TRÚC KEY VÀ KEY-MAPPING")
    print("-" * 50)
    
    # Prefix 'NAS' in ERP customer ID
    nas_prefix_count = erp_cust['cid'].astype(str).str.startswith('NAS').sum()
    print(f"-> Số mã khách hàng trong ERP chứa tiền tố 'NAS': {nas_prefix_count} / {len(erp_cust)} bản ghi")
    if nas_prefix_count > 0:
        print(f"   (Ví dụ: {erp_cust[erp_cust['cid'].astype(str).str.startswith('NAS')]['cid'].iloc[0]})")

    # Delimiters in ERP loc
    dash_loc_count = erp_loc['cid'].astype(str).str.contains('-').sum()
    print(f"\n-> Số mã định danh trong LOC_A101 chứa dấu gạch ngang '-': {dash_loc_count} / {len(erp_loc)} bản ghi")
    if dash_loc_count > 0:
         print(f" (Ví dụ: {erp_loc[erp_loc['cid'].astype(str).str.contains('-')]['cid'].iloc[0]})")

    # Complex product Key in CRM
    dash_prd_count = crm_prd['prd_key'].astype(str).str.contains('-').sum()
    print(f"\n-> Số mã sản phẩm trong CRM chứa ký tự phân tách nhánh '-': {dash_prd_count} / {len(crm_prd)} bản ghi")
    if dash_prd_count > 0:
         print(f"   (Ví dụ: {crm_prd[crm_prd['prd_key'].astype(str).str.contains('-')]['prd_key'].iloc[0]})")

    # -------------------------------------------------------------------------
    # 3.2.2.2. Dữ liệu trùng lặp (Duplicates)
    # -------------------------------------------------------------------------
    print("\n[2] DỮ LIỆU TRÙNG LẶP (DUPLICATES)")
    print("-" * 50)
    
    # CRM Customer Duplicates based on ID
    total_crm_cust = len(crm_cust)
    unique_crm_cust = crm_cust['cst_id'].nunique()
    duplicated_ids = total_crm_cust - unique_crm_cust
    print(f"-> Tổng số bản ghi crm_cust_info   : {total_crm_cust}")
    print(f"-> Số ID khách hàng duy nhất       : {unique_crm_cust}")
    print(f"-> Số bản ghi trùng lặp (lịch sử)  : {duplicated_ids} (Cần dùng ROW_NUMBER để lọc)")
    
    if duplicated_ids > 0:
        dup_example_id = crm_cust[crm_cust['cst_id'].duplicated()]['cst_id'].iloc[0]
        dup_count = len(crm_cust[crm_cust['cst_id'] == dup_example_id])
        print(f"   (Ví dụ: ID '{dup_example_id}' xuất hiện {dup_count} lần)")

    # -------------------------------------------------------------------------
    # 3.2.2.3. Dữ liệu dị thường (Anomalies) và sai lệch định dạng
    # -------------------------------------------------------------------------
    print("\n[3] DỮ LIỆU DỊ THƯỜNG (ANOMALIES)")
    print("-" * 50)

    # Future dates in ERP Birthdate
    try:
        current_date = datetime.datetime.now()
        erp_cust['bdate_dt'] = pd.to_datetime(erp_cust['bdate'], errors='coerce')
        future_bdate_count = len(erp_cust[erp_cust['bdate_dt'] > current_date])
        print(f"-> Số khách hàng có ngày sinh trong tương lai (ERP) : {future_bdate_count} bản ghi")
    except Exception as e:
        print(f"-> KHÔNG THỂ KIỂM TRA NGÀY SINH TƯƠNG LAI do lỗi format: {e}")

    # Sales anomaly: Quantity * Price != Sales
    # First, handle potential nulls or wrong types
    crm_sales['calc_sales'] = crm_sales['sls_quantity'] * crm_sales['sls_price'].abs()
    # Allowing a small floating point tolerance
    sales_anomaly = crm_sales[
       (crm_sales['sls_sales'].notnull()) & 
       (crm_sales['sls_quantity'].notnull()) & 
       (crm_sales['sls_price'].notnull()) &
       (abs(crm_sales['sls_sales'] - crm_sales['calc_sales']) > 0.01)
    ]
    print(f"\n-> Số đơn hàng tính sai tổng tiền (Sales != Qty * Price): {len(sales_anomaly)} / {len(crm_sales)} bản ghi")
    if len(sales_anomaly) > 0:
        sample = sales_anomaly.iloc[0]
        print(f"   (Ví dụ Hóa đơn {sample['sls_ord_num']}: Qty={sample['sls_quantity']}, Price={sample['sls_price']} => Lẽ ra phải là {sample['calc_sales']} nhưng lại ghi {sample['sls_sales']})")

    # Inconsistent categories (Gender in CRM)
    unique_genders = crm_cust['cst_gndr'].dropna().unique()
    print(f"\n-> Các format giới tính lộn xộn trong CRM (cst_gndr): {list(unique_genders)}")
    
    unique_genders_erp = erp_cust['gen'].dropna().unique()
    print(f"-> Các format giới tính lộn xộn trong ERP (gen)     : {list(unique_genders_erp)}")

    # -------------------------------------------------------------------------
    # 3.2.2.4. Dữ liệu bị khuyết thiếu (Null/Missing values)
    # -------------------------------------------------------------------------
    print("\n[4] DỮ LIỆU KHUYẾT THIẾU (MISSING VALUES)")
    print("-" * 50)

    # Missing Cost in Products
    missing_cost = crm_prd['prd_cost'].isnull().sum()
    print(f"-> Số sản phẩm không có Giá vốn (prd_cost = NULL) : {missing_cost} / {len(crm_prd)} bản ghi")

    # Missing Country in ERP
    missing_country = erp_loc['cntry'].isnull().sum()
    empty_country = (erp_loc['cntry'].astype(str).str.strip() == '').sum()
    print(f"-> Số bản ghi khuyết thiếu Quốc gia (NULL/Empty)  : {missing_country + empty_country} / {len(erp_loc)} bản ghi")

    print("\n" + "="*80)

if __name__ == "__main__":
    main()
