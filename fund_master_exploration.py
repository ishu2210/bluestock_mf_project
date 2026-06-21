import pandas as pd
import numpy as np
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# FUND MASTER EXPLORATION & AMFI VALIDATION SCRIPT
# ============================================================================

def load_fund_master(file_path):
    """Load fund master CSV"""
    try:
        df = pd.read_csv(file_path)
        print(f"✅ Fund Master loaded successfully!")
        print(f"   Shape: {df.shape[0]} rows × {df.shape[1]} columns\n")
        return df
    except FileNotFoundError:
        print(f"❌ Error: File not found at {file_path}")
        return None

def explore_unique_houses(df):
    """Explore unique fund houses"""
    print("=" * 70)
    print("1️⃣  UNIQUE FUND HOUSES")
    print("=" * 70)
    
    # Identify potential house columns
    house_cols = [col for col in df.columns if 'house' in col.lower() or 'fund' in col.lower()]
    
    if not house_cols:
        print("⚠️  No 'house' or 'fund' column found. Checking all columns...")
        print(f"Available columns: {list(df.columns)}\n")
        return
    
    for col in house_cols:
        if col in df.columns:
            unique_houses = df[col].nunique()
            houses_list = df[col].value_counts()
            
            print(f"\nColumn: '{col}'")
            print(f"  • Unique Houses: {unique_houses}")
            print(f"  • Top 10 Houses:")
            for idx, (house, count) in enumerate(houses_list.head(10).items(), 1):
                print(f"      {idx:2d}. {house:35s} → {count:4d} funds")
            
            # Check for nulls
            null_count = df[col].isna().sum()
            if null_count > 0:
                print(f"  • Missing Values: {null_count} ({null_count/len(df)*100:.2f}%)")

def explore_categories(df):
    """Explore fund categories"""
    print("\n" + "=" * 70)
    print("2️⃣  FUND CATEGORIES")
    print("=" * 70)
    
    # Identify category column
    category_cols = [col for col in df.columns if 'category' in col.lower() or 'type' in col.lower()]
    
    if not category_cols:
        print("⚠️  No 'category' column found.")
        return
    
    for col in category_cols:
        if col in df.columns:
            unique_cats = df[col].nunique()
            cats_list = df[col].value_counts()
            
            print(f"\nColumn: '{col}'")
            print(f"  • Unique Categories: {unique_cats}")
            print(f"  • Distribution:")
            for idx, (cat, count) in enumerate(cats_list.items(), 1):
                pct = count / len(df) * 100
                print(f"      {idx:2d}. {str(cat):30s} → {count:4d} funds ({pct:6.2f}%)")
            
            # Check for nulls
            null_count = df[col].isna().sum()
            if null_count > 0:
                print(f"  • Missing Values: {null_count} ({null_count/len(df)*100:.2f}%)")

def explore_risk_grades(df):
    """Explore risk grades/ratings"""
    print("\n" + "=" * 70)
    print("3️⃣  RISK GRADES/RATINGS")
    print("=" * 70)
    
    # Identify risk-related columns
    risk_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['risk', 'grade', 'rating', 'star'])]
    
    if not risk_cols:
        print("⚠️  No risk/grade/rating columns found.")
        return
    
    for col in risk_cols:
        if col in df.columns:
            unique_risks = df[col].nunique()
            risks_list = df[col].value_counts().sort_index()
            
            print(f"\nColumn: '{col}'")
            print(f"  • Unique Values: {unique_risks}")
            print(f"  • Distribution:")
            for idx, (risk, count) in enumerate(risks_list.items(), 1):
                pct = count / len(df) * 100
                print(f"      {idx}. {str(risk):15s} → {count:4d} funds ({pct:6.2f}%)")
            
            # Check for nulls
            null_count = df[col].isna().sum()
            if null_count > 0:
                print(f"  • Missing Values: {null_count} ({null_count/len(df)*100:.2f}%)")

def validate_amfi_codes(df):
    """Validate AMFI codes"""
    print("\n" + "=" * 70)
    print("4️⃣  AMFI CODE VALIDATION")
    print("=" * 70)
    
    # Identify AMFI code column
    amfi_cols = [col for col in df.columns if 'amfi' in col.lower() or 'code' in col.lower()]
    
    if not amfi_cols:
        print("⚠️  No AMFI code column found. Checking all columns...")
        print(f"Available columns: {list(df.columns)}\n")
        return
    
    for col in amfi_cols:
        if col in df.columns:
            print(f"\nColumn: '{col}'")
            
            # Total count
            total = len(df)
            print(f"  • Total Records: {total}")
            
            # Null/Missing
            null_count = df[col].isna().sum()
            null_pct = null_count / total * 100
            print(f"  • Missing Values: {null_count} ({null_pct:.2f}%)")
            
            # Duplicates
            non_null = df[col].dropna()
            dup_count = len(non_null) - non_null.nunique()
            print(f"  • Duplicate Codes: {dup_count}")
            if dup_count > 0:
                dups = non_null[non_null.duplicated(keep=False)].value_counts()
                print(f"    Top duplicates:")
                for code, count in dups.head(5).items():
                    print(f"      → {code}: appears {count} times")
            
            # Format validation (typically 6 digits)
            valid_format = 0
            invalid_format = 0
            
            for code in non_null:
                code_str = str(code).strip()
                # AMFI codes are typically 6-digit numbers
                if code_str.isdigit() and len(code_str) == 6:
                    valid_format += 1
                else:
                    invalid_format += 1
            
            print(f"  • Format Check (6-digit numeric):")
            print(f"    ✅ Valid Format: {valid_format} ({valid_format/len(non_null)*100:.2f}%)")
            print(f"    ❌ Invalid Format: {invalid_format} ({invalid_format/len(non_null)*100:.2f}%)")
            
            if invalid_format > 0:
                print(f"    Sample invalid codes:")
                invalid_samples = []
                for code in non_null:
                    code_str = str(code).strip()
                    if not (code_str.isdigit() and len(code_str) == 6):
                        invalid_samples.append(code_str)
                for sample in invalid_samples[:5]:
                    print(f"      → {sample}")
            
            # Uniqueness check
            unique_codes = non_null.nunique()
            print(f"  • Uniqueness: {unique_codes} unique codes out of {len(non_null)} non-null records")

def data_quality_summary(df):
    """Generate comprehensive data quality summary"""
    print("\n" + "=" * 70)
    print("5️⃣  DATA QUALITY SUMMARY")
    print("=" * 70)
    
    print(f"\n📊 DATASET OVERVIEW")
    print(f"  • Total Records: {len(df)}")
    print(f"  • Total Columns: {len(df.columns)}")
    print(f"  • Memory Usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    print(f"\n🔍 MISSING DATA ANALYSIS")
    missing_data = df.isna().sum()
    if missing_data.sum() == 0:
        print("  ✅ No missing values detected!")
    else:
        print(f"  Total Missing Values: {missing_data.sum()}")
        print("\n  Columns with Missing Data:")
        for col, count in missing_data[missing_data > 0].items():
            pct = count / len(df) * 100
            print(f"    • {col:30s}: {count:4d} ({pct:6.2f}%)")
    
    print(f"\n📈 DATA TYPE DISTRIBUTION")
    dtype_counts = df.dtypes.value_counts()
    for dtype, count in dtype_counts.items():
        print(f"  • {str(dtype):15s}: {count} columns")
    
    print(f"\n✔️  DATA INTEGRITY")
    # Check for duplicate rows
    dup_rows = df.duplicated().sum()
    print(f"  • Duplicate Rows: {dup_rows}")
    
    # Check numeric columns for outliers/anomalies
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        print(f"  • Numeric Columns: {len(numeric_cols)}")
        for col in numeric_cols[:5]:  # Show first 5
            print(f"    ✓ {col:30s}: min={df[col].min():.2f}, max={df[col].max():.2f}, mean={df[col].mean():.2f}")
    
    print(f"\n📋 COLUMN-WISE SUMMARY")
    print(f"  Total Columns: {len(df.columns)}")
    for col in df.columns:
        null_pct = df[col].isna().sum() / len(df) * 100
        unique = df[col].nunique()
        status = "✅" if null_pct == 0 else "⚠️ "
        print(f"  {status} {col:30s}: {unique:4d} unique, {null_pct:5.2f}% missing")

def main():
    """Main execution"""
    print("\n" + "🎯" * 35)
    print("BLUESTOCK FINTECH - FUND MASTER EXPLORATION & VALIDATION")
    print("🎯" * 35 + "\n")
    
    # Define file path - modify this to your actual file location
    file_path = input("Enter the path to your fund master CSV (or press Enter for default): ").strip()
    if not file_path:
        file_path = "fund_master.csv"  # Default filename
    
    # Load data
    df = load_fund_master(file_path)
    if df is None:
        return
    
    # Display column names for reference
    print("📌 Available Columns:")
    for idx, col in enumerate(df.columns, 1):
        print(f"   {idx:2d}. {col}")
    print()
    
    # Run all explorations
    explore_unique_houses(df)
    explore_categories(df)
    explore_risk_grades(df)
    validate_amfi_codes(df)
    data_quality_summary(df)
    
    print("\n" + "=" * 70)
    print("✅ ANALYSIS COMPLETE!")
    print("=" * 70 + "\n")
    
    # Optional: Export summary to CSV
    export = input("Do you want to export the data quality summary to CSV? (y/n): ").strip().lower()
    if export == 'y':
        summary_data = {
            'Metric': ['Total Records', 'Total Columns', 'Missing Values'],
            'Value': [len(df), len(df.columns), df.isna().sum().sum()]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_csv('data_quality_summary.csv', index=False)
        print("✅ Summary exported to 'data_quality_summary.csv'\n")

if __name__ == "__main__":
    main()