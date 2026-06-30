# Quick Start — Day 3 EDA Analytics
## Fix Common Issues

---

## ⚠️ ERROR: "Could not find sqlite3"

### **Solution: DON'T pip install sqlite3**

`sqlite3` is **built-in to Python**. It doesn't come from pip.

```bash
# ❌ WRONG (will fail)
pip install sqlite3

# ✅ CORRECT (no installation needed)
# sqlite3 is already included with Python 3.x
```

---

## 📦 Installation Instructions

### Option A: Standalone Script (Recommended)
```bash
# 1. Install dependencies ONLY
pip install pandas numpy scipy matplotlib seaborn

# 2. Run the script
python performance_analytics.py

# 3. Outputs in current directory:
#    - fund_scorecard.csv
#    - alpha_beta.csv
#    - risk_metrics.csv
#    - 01_daily_returns_validation.png
#    - ...07_benchmark_comparison.png
```

### Option B: Jupyter Notebook
```bash
# 1. Install dependencies + Jupyter
pip install pandas numpy scipy matplotlib seaborn jupyter

# 2. Open notebook
jupyter notebook Performance_Analytics.ipynb

# 3. Update database path in Cell 2:
db_path = r'C:\Users\vasanth\OneDrive\Desktop\bluestock_mf_project\mutual_funds.db'

# 4. Run cells sequentially (Cell → Cell → Run)
```

---

## 🚀 Quick Test

### Verify Installation
```python
# Test in Python shell
python
>>> import sqlite3
>>> print("✓ sqlite3 working!")
>>> exit()
```

### Run Standalone Script
```bash
# From your bluestock_mf_project directory
python performance_analytics.py

# Should print:
# ✓ Connected to database...
# ✓ Loaded X NAV records
# ✓ Daily returns computed...
# [STEP 2] Computing daily returns...
# ... (will run all 8 tasks)
```

---

## 📝 Expected Output Files

```
📂 Your Working Directory/
├── performance_analytics.py          (the script)
├── fund_scorecard.csv                ✓ CSV with top 40 funds ranked
├── alpha_beta.csv                    ✓ Alpha & Beta regression
├── risk_metrics.csv                  ✓ Sharpe, Sortino, Drawdown
├── performance_summary.csv           ✓ Summary statistics
├── 01_daily_returns_validation.png   ✓ Chart
├── 02_cagr_analysis.png              ✓ Chart
├── 03_sharpe_sortino_analysis.png    ✓ Chart
├── 04_alpha_beta_analysis.png        ✓ Chart
├── 05_drawdown_analysis.png          ✓ Chart
├── 06_fund_scorecard.png             ✓ Chart
└── 07_benchmark_comparison.png       ✓ Chart
```

---

## 🔧 Troubleshooting

### Issue 1: "ModuleNotFoundError: No module named 'pandas'"

**Fix:**
```bash
pip install pandas numpy scipy matplotlib seaborn
```

### Issue 2: "Database file not found"

**Fix:** Update the path in the script:
```python
# Line ~30 in performance_analytics.py
db_path = r'C:\Users\vasanth\OneDrive\Desktop\bluestock_mf_project\mutual_funds.db'

# Verify the path exists:
# - Navigate to: C:/Users/vasanth/OneDrive/Desktop/bluestock_mf_project/
# - Check that mutual_funds.db file is there
```

### Issue 3: "Data shape mismatch" or "empty DataFrame"

**Fix:**
- Make sure Day 2 created `nav_history` and `schemes` tables in SQLite
- Check database schema:
  ```python
  import sqlite3
  conn = sqlite3.connect(r'C:\Users\vasanth\OneDrive\Desktop\bluestock_mf_project\mutual_funds.db')
  cursor = conn.cursor()
  cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
  print(cursor.fetchall())  # Should show: [('schemes',), ('nav_history',), ...]
  ```

### Issue 4: "Permission denied" when saving PNG files

**Fix:** Change working directory or run with elevated permissions
```bash
# Option 1: Run from a writable directory
cd C:\Users\vasanth\Desktop
python C:\path\to\performance_analytics.py

# Option 2: Run as administrator (Windows)
# Right-click Command Prompt → Run as Administrator
```

---

## 💡 Pro Tips

### Tip 1: Redirect Output to File
```bash
python performance_analytics.py > output.log 2>&1

# Then review the log
cat output.log  # Linux/Mac
type output.log  # Windows
```

### Tip 2: Run in Background (Windows)
```bash
start pythonw performance_analytics.py
```

### Tip 3: Check Python Version
```bash
python --version  # Should be 3.7+
pip --version
```

### Tip 4: View CSV Results Quickly
```python
import pandas as pd

# Read scorecard
df = pd.read_csv('fund_scorecard.csv')
print(df.head(10))  # Top 10 funds

# Filter by score
print(df[df['composite_score'] > 80])  # Score > 80
```

---

## 📋 Checklist

- [ ] Python 3.7+ installed
- [ ] `pip install pandas numpy scipy matplotlib seaborn` (NO sqlite3!)
- [ ] Database path updated in script
- [ ] SQLite file exists: `mutual_funds.db`
- [ ] Working directory is writable
- [ ] Run: `python performance_analytics.py`
- [ ] Check for CSVs and PNGs in output folder
- [ ] Review `fund_scorecard.csv` for top funds

---

## 🎯 Next Steps

1. **Review Results:**
   ```bash
   # Open fund_scorecard.csv in Excel or Pandas
   ```

2. **Interpret Findings:**
   - Top 5 schemes by composite score
   - Schemes with positive alpha
   - Low-volatility options
   - Recovery time from drawdowns

3. **For Day 4:**
   - Sector allocation analysis
   - Fund categorization
   - Portfolio optimization

---

## 📞 Still Having Issues?

1. **Check sqlite3 import:**
   ```python
   import sqlite3
   print(sqlite3.version)  # Should print version
   ```

2. **Verify database integrity:**
   ```python
   import sqlite3
   conn = sqlite3.connect('mutual_funds.db')
   cursor = conn.cursor()
   cursor.execute("SELECT COUNT(*) FROM nav_history")
   print(f"NAV records: {cursor.fetchone()[0]}")
   ```

3. **Test with demo data:**
   - Script has fallback synthetic data
   - If database fails, uses random data for testing
   - Check console output for "✓" or "✗" markers

---

**Last Updated:** June 29, 2026
**Status:** Ready for Production ✓
