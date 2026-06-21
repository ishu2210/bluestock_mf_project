import pandas as pd
import numpy as np
import warnings
import os
warnings.filterwarnings('ignore')

# ============================================================================
# BLUESTOCK FINTECH - FUND MASTER EXPLORATION & AMFI VALIDATION
# ============================================================================

class FundMasterExplorer:
    """Complete fund master analysis and validation"""
    
    def __init__(self, file_path=None):
        self.df = None
        self.file_path = file_path
        self.load_data()
    
    def load_data(self):
        """Try to load fund master CSV from multiple possible locations"""
        
        # List of possible paths to check
        possible_paths = [
            self.file_path if self.file_path else None,
            "01_fund_master.csv",
            "fund_master.csv",
            "data/raw/01_fund_master.csv",
            "data/raw/drive-download-20260622T054554Z-3-001/01_fund_master.csv",
            "../data/raw/drive-download-20260622T054554Z-3-001/01_fund_master.csv",
        ]
        
        for path in possible_paths:
            if path and os.path.exists(path):
                try:
                    self.df = pd.read_csv(path)
                    print(f"✅ Fund Master loaded from: {path}")
                    print(f"   Shape: {self.df.shape[0]} rows × {self.df.shape[1]} columns\n")
                    return
                except Exception as e:
                    print(f"⚠️  Error loading from {path}: {str(e)}")
                    continue
        
        # If not found, ask user
        print("❌ Could not find fund master CSV automatically")
        user_path = input("\n📁 Enter the full path to your fund_master.csv: ").strip()
        if user_path and os.path.exists(user_path):
            try:
                self.df = pd.read_csv(user_path)
                print(f"✅ Fund Master loaded from: {user_path}")
                print(f"   Shape: {self.df.shape[0]} rows × {self.df.shape[1]} columns\n")
                return
            except Exception as e:
                print(f"❌ Error loading file: {str(e)}")
                return
        else:
            print(f"❌ File not found at: {user_path}")
    
    def print_header(self, title):
        """Print formatted section header"""
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80)
    
    def explore_unique_houses(self):
        """Explore unique fund houses"""
        self.print_header("1️⃣  UNIQUE FUND HOUSES")
        
        # Find fund house column
        house_cols = [col for col in self.df.columns 
                      if 'house' in col.lower() or 'amc' in col.lower() or 'fund' in col.lower()]
        
        if not house_cols:
            print("⚠️  No 'house' column detected. Available columns:")
            print(f"   {', '.join(self.df.columns)}\n")
            return
        
        for col in house_cols:
            houses_dist = self.df[col].value_counts()
            null_count = self.df[col].isna().sum()
            
            print(f"\n📊 Column: '{col}'")
            print(f"   Total Unique: {self.df[col].nunique()}")
            print(f"   Missing Values: {null_count} ({null_count/len(self.df)*100:.2f}%)\n")
            print("   Top 15 Fund Houses (Distribution):")
            
            for idx, (house, count) in enumerate(houses_dist.head(15).items(), 1):
                pct = count / len(self.df) * 100
                bar = "█" * int(pct / 2)
                print(f"   {idx:2d}. {str(house):35s} │ {count:4d} funds ({pct:6.2f}%) {bar}")
    
    def explore_categories(self):
        """Explore fund categories"""
        self.print_header("2️⃣  FUND CATEGORIES")
        
        # Find category column
        cat_cols = [col for col in self.df.columns 
                    if 'category' in col.lower() or 'type' in col.lower() or 'class' in col.lower()]
        
        if not cat_cols:
            print("⚠️  No 'category' column detected. Available columns:")
            print(f"   {', '.join(self.df.columns)}\n")
            return
        
        for col in cat_cols:
            cats_dist = self.df[col].value_counts()
            null_count = self.df[col].isna().sum()
            
            print(f"\n📊 Column: '{col}'")
            print(f"   Total Unique: {self.df[col].nunique()}")
            print(f"   Missing Values: {null_count} ({null_count/len(self.df)*100:.2f}%)\n")
            print("   Category Distribution:")
            
            for idx, (cat, count) in enumerate(cats_dist.items(), 1):
                pct = count / len(self.df) * 100
                bar = "█" * int(pct / 3)
                print(f"   {idx:2d}. {str(cat):40s} │ {count:4d} ({pct:6.2f}%) {bar}")
    
    def explore_risk_grades(self):
        """Explore risk grades"""
        self.print_header("3️⃣  RISK GRADES / RATINGS")
        
        # Find risk-related columns
        risk_cols = [col for col in self.df.columns 
                     if any(kw in col.lower() for kw in ['risk', 'grade', 'rating', 'star', 'level'])]
        
        if not risk_cols:
            print("⚠️  No risk/grade/rating columns detected.")
            return
        
        for col in risk_cols:
            risk_dist = self.df[col].value_counts().sort_index()
            null_count = self.df[col].isna().sum()
            
            print(f"\n📊 Column: '{col}'")
            print(f"   Total Unique: {self.df[col].nunique()}")
            print(f"   Missing Values: {null_count} ({null_count/len(self.df)*100:.2f}%)\n")
            print("   Risk Grade Distribution:")
            
            for idx, (grade, count) in enumerate(risk_dist.items(), 1):
                pct = count / len(self.df) * 100
                bar = "█" * int(pct / 2)
                print(f"   {idx}. {str(grade):20s} │ {count:4d} funds ({pct:6.2f}%) {bar}")
    
    def validate_amfi_codes(self):
        """Validate AMFI codes"""
        self.print_header("4️⃣  AMFI CODE VALIDATION")
        
        # Find AMFI code column
        amfi_cols = [col for col in self.df.columns 
                     if 'amfi' in col.lower() or 'code' in col.lower()]
        
        if not amfi_cols:
            print("⚠️  No AMFI code column detected.")
            print(f"   Available columns: {', '.join(self.df.columns)}\n")
            return
        
        for col in amfi_cols:
            total = len(self.df)
            null_count = self.df[col].isna().sum()
            non_null = self.df[col].dropna()
            
            print(f"\n📊 Column: '{col}'")
            print(f"\n   📋 BASIC METRICS:")
            print(f"      • Total Records: {total}")
            print(f"      • Non-null Records: {len(non_null)} ({len(non_null)/total*100:.2f}%)")
            print(f"      • Missing Values: {null_count} ({null_count/total*100:.2f}%)")
            
            # Uniqueness
            unique_count = non_null.nunique()
            print(f"\n   🔑 UNIQUENESS CHECK:")
            print(f"      • Unique Codes: {unique_count}")
            print(f"      • Duplicate Codes: {len(non_null) - unique_count}")
            
            if len(non_null) > unique_count:
                dups = non_null[non_null.duplicated(keep=False)].value_counts()
                print(f"      • Top 5 Duplicates:")
                for code, count in dups.head(5).items():
                    print(f"        → {code}: appears {count} times")
            
            # Format validation
            valid_format = 0
            invalid_samples = []
            
            for code in non_null:
                code_str = str(code).strip()
                if code_str.isdigit() and len(code_str) == 6:
                    valid_format += 1
                else:
                    invalid_samples.append(code_str)
            
            print(f"\n   ✅ FORMAT VALIDATION (6-digit numeric):")
            print(f"      • Valid Format: {valid_format} ({valid_format/len(non_null)*100:.2f}%)")
            print(f"      • Invalid Format: {len(invalid_samples)} ({len(invalid_samples)/len(non_null)*100:.2f}%)")
            
            if invalid_samples:
                print(f"      • Sample Invalid Codes:")
                for sample in invalid_samples[:10]:
                    print(f"        → '{sample}'")
    
    def data_quality_summary(self):
        """Generate comprehensive data quality summary"""
        self.print_header("5️⃣  DATA QUALITY SUMMARY")
        
        print(f"\n📊 DATASET OVERVIEW:")
        print(f"   • Total Records: {len(self.df):,}")
        print(f"   • Total Columns: {len(self.df.columns)}")
        print(f"   • Memory Usage: {self.df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        
        # Missing data
        missing_data = self.df.isna().sum()
        total_missing = missing_data.sum()
        
        print(f"\n🔍 MISSING DATA ANALYSIS:")
        print(f"   • Total Missing Values: {total_missing}")
        if total_missing > 0:
            print(f"   • Columns with Missing Data:")
            for col, count in missing_data[missing_data > 0].items():
                pct = count / len(self.df) * 100
                print(f"     ⚠️  {col:35s}: {count:5d} ({pct:6.2f}%)")
        else:
            print(f"   ✅ No missing values detected!")
        
        # Data types
        print(f"\n📈 DATA TYPE DISTRIBUTION:")
        dtype_counts = self.df.dtypes.value_counts()
        for dtype, count in dtype_counts.items():
            print(f"   • {str(dtype):15s}: {count} columns")
        
        # Duplicates
        dup_rows = self.df.duplicated().sum()
        print(f"\n✔️  DATA INTEGRITY:")
        print(f"   • Duplicate Rows: {dup_rows}")
        
        # Numeric columns stats
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            print(f"   • Numeric Columns: {len(numeric_cols)}")
            for col in numeric_cols[:5]:
                print(f"     • {col:30s}: min={self.df[col].min():.2f}, max={self.df[col].max():.2f}, mean={self.df[col].mean():.2f}")
        
        # Column-wise summary
        print(f"\n📋 COLUMN-WISE SUMMARY ({len(self.df.columns)} columns):")
        for col in self.df.columns:
            null_pct = self.df[col].isna().sum() / len(self.df) * 100
            unique = self.df[col].nunique()
            status = "✅" if null_pct == 0 else "⚠️ "
            dtype = str(self.df[col].dtype)
            print(f"   {status} {col:30s} | {unique:5d} unique | {null_pct:5.2f}% missing | {dtype}")
    
    def export_summary(self):
        """Export data quality summary to CSV"""
        summary_data = {
            'Metric': [
                'Total Records',
                'Total Columns',
                'Missing Values (Total)',
                'Duplicate Rows',
                'Memory Usage (MB)'
            ],
            'Value': [
                len(self.df),
                len(self.df.columns),
                self.df.isna().sum().sum(),
                self.df.duplicated().sum(),
                round(self.df.memory_usage(deep=True).sum() / 1024**2, 2)
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        output_path = 'bluestock_data_quality_summary.csv'
        summary_df.to_csv(output_path, index=False)
        print(f"\n✅ Summary exported to: {output_path}")
        return summary_df
    
    def run_all(self):
        """Run complete analysis"""
        if self.df is None:
            print("❌ Failed to load data. Exiting.")
            return
        
        print("\n" + "🎯" * 40)
        print("BLUESTOCK FINTECH - FUND MASTER ANALYSIS")
        print("🎯" * 40)
        
        # Show columns
        print(f"\n📌 AVAILABLE COLUMNS ({len(self.df.columns)}):")
        for idx, col in enumerate(self.df.columns, 1):
            print(f"   {idx:2d}. {col}")
        
        # Run all analyses
        self.explore_unique_houses()
        self.explore_categories()
        self.explore_risk_grades()
        self.validate_amfi_codes()
        self.data_quality_summary()
        
        # Export summary
        print("\n" + "=" * 80)
        summary = self.export_summary()
        print("\n" + summary.to_string(index=False))
        
        print("\n" + "=" * 80)
        print("✅ ANALYSIS COMPLETE! All tasks finished.")
        print("=" * 80 + "\n")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    explorer = FundMasterExplorer()
    if explorer.df is not None:
        explorer.run_all()