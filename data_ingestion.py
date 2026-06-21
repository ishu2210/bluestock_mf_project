import pandas as pd
import os

DATA_PATH = "data/raw/drive-download-20260622T054554Z-3-001/"

csv_files = [
    "01_fund_master.csv",
    "02_nav_history.csv",
    "03_aum_by_fund_house.csv",
    "04_monthly_sip_inflows.csv",
    "05_category_inflows.csv",
    "06_industry_folio_count.csv",
    "07_scheme_performance.csv",
    "08_investor_transactions.csv",
    "09_portfolio_holdings.csv",
    "10_benchmark_indices.csv"
]

print("=" * 80)
print("DATA INGESTION: Loading All Datasets")
print("=" * 80)

for file in csv_files:
    file_path = os.path.join(DATA_PATH, file)
    try:
        df = pd.read_csv(file_path)
        print(f"\n📊 {file}")
        print(f"Shape: {df.shape}")
        print(f"Data Types:\n{df.dtypes}")
        print(f"First 5 Rows:\n{df.head()}")
        print(f"Missing Values:\n{df.isnull().sum()}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

print("\n✅ DATA INGESTION COMPLETE")