import pandas as pd
import numpy as np

def clean_complex_crm_data(customers_df, products_df):
    """
    Script Python xử lý 2 nghiệp vụ khó/cồng kềnh nhất đối với SSIS thuần:
    1. Lọc Deduplication (ROW_NUMBER)
    2. Hàm Tương lai LEAD() để đẩy SCD End Date
    """
    print("Bắt đầu xử lý dữ liệu phức tạp bằng Pandas...")

    # ---------------------------------------------------------
    # 1. TRƯỜNG HỢP 1: DEDUPLICATION khách hàng bằng (ROW_NUMBER)
    # ---------------------------------------------------------
    # Tương đương SQL: ROW_NUMBER() OVER (PARTITION BY cst_id ORDER BY cst_create_date DESC)
    # Lấy bản ghi khách hàng mới nhất khi bị lặp ID
    
    # Ép kiểu ngày tháng
    customers_df['cst_create_date'] = pd.to_datetime(customers_df['cst_create_date'], errors='coerce')
    
    # Sắp xếp khách hàng theo ID và ngày tạo (mới nhất đẩy lên đầu)
    customers_df = customers_df.sort_values(by=['cst_id', 'cst_create_date'], ascending=[True, False])
    
    # Giữ lại bản ghi đầu tiên (mới nhất), drop các bản ghi cũ của khách đó
    cleaned_customers_df = customers_df.drop_duplicates(subset=['cst_id'], keep='first').copy()
    print("Đã làm sạch trùng lặp khách hàng.")


    # ---------------------------------------------------------
    # 2. TRƯỜNG HỢP 2: TÍNH TOÁN SCD DATE bằng Lệnh LEAD()
    # ---------------------------------------------------------
    # Tương đương SQL: LEAD(prd_start_dt) OVER (PARTITION BY prd_key ORDER BY prd_start_dt) - 1
    # Để tính ngày End Date của một Product dựa trên Start Date của dòng tiếp theo
    
    # Đảm bảo Dataframe được sắp xếp thứ tự thời gian phân bổ theo từng nhóm sản phẩm
    products_df['prd_start_dt'] = pd.to_datetime(products_df['prd_start_dt'], errors='coerce')
    products_df = products_df.sort_values(by=['prd_key', 'prd_start_dt'])
    
    # Dùng hàm .shift(-1) tương đương với LEAD() trong SQL
    # Lấy lùi lên 1 dòng (của cùng Nhóm prd_key) trừ đi 1 ngày
    products_df['prd_end_dt'] = products_df.groupby('prd_key')['prd_start_dt'].shift(-1) - pd.Timedelta(days=1)
    
    # Nếu dòng cuối cùng không có tiếp theo (Sản phẩm hiện hành), gán NaT hoặc xử lý thành NULL
    
    print("Đã tính toán xong Lead Function cho Date sản phẩm.")

    return cleaned_customers_df, products_df

if __name__ == "__main__":
    # Ví dụ Data Mẫu (Mock) để bạn hình dung
    sample_customers = pd.DataFrame({
        'cst_id': [1, 1, 2],
        'cst_name': ['Baraa', 'Baraa Updated', 'Anna'],
        'cst_create_date': ['2020-01-01', '2023-01-01', '2022-05-05']
    })
    
    sample_products = pd.DataFrame({
        'prd_key': ['P01', 'P01', 'P02'],
        'prd_name': ['Bike v1', 'Bike v2', 'Helmet'],
        'prd_start_dt': ['2015-01-01', '2019-01-01', '2020-01-01']
    })
    
    # Chạy hàm
    clean_cust, clean_prod = clean_complex_crm_data(sample_customers, sample_products)
    
    print("\n--- Khách hàng sau khi Deduplicate (Chỉ lấy bản update 2023) ---")
    print(clean_cust)
    
    print("\n--- Sản phẩm sau khi tính hàm Lead (prd_end_dt của Bike v1 sẽ là 2018-12-31) ---")
    print(clean_prod)
