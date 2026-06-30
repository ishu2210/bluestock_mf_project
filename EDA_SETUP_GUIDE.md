# EDA Analysis Setup Guide
## Bluestock Fintech Capstone — Quick Start for Windows

---

## Step 1: Prepare Your Data Folder

Your project structure should look like this:
```
C:\Users\vasanth\OneDrive\Desktop\bluestock_mf_project\
├── data/
│   ├── mutual_funds_nav.csv          ← Daily NAV data (40 schemes)
│   ├── mutual_funds_aum.csv          ← AUM by fund house & year
│   ├── sip_inflows.csv               ← Monthly SIP trends
│   ├── investor_demographics.csv     ← Age, gender, SIP amounts
│   ├── portfolio_holdings.csv        ← Sector allocation
│   ├── geographic_distribution.csv   ← State-wise SIP data
│   └── folio_count.csv               ← Folio count by month
├── EDA_Analysis.ipynb                ← This notebook
└── exported_charts/                  ← Charts will be saved here (auto-created)
```

---

## Step 2: Install Required Libraries

Open PowerShell/Command Prompt and run:

```powershell
pip install pandas numpy matplotlib seaborn jupyter
```

**Verify installation:**
```powershell
python -c "import pandas; import seaborn; print('✓ Libraries OK')"
```

---

## Step 3: Update Data Path in Notebook

In the **"Data Loading"** cell (around line 50), change this line:

```python
data_path = r'C:\Users\vasanth\OneDrive\Desktop\bluestock_mf_project\data\'
```

**To match your actual folder.** Examples:

| Scenario | Path |
|----------|------|
| OneDrive Desktop | `r'C:\Users\vasanth\OneDrive\Desktop\bluestock_mf_project\data\'` |
| Local Desktop | `r'C:\Users\vasanth\Desktop\bluestock_mf_project\data\'` |
| Custom folder | `r'C:\path\to\your\data\'` |

---

## Step 4: Prepare CSV Files

Each CSV file must have **specific columns**:

### **mutual_funds_nav.csv**
```
date, scheme_name, nav
2022-01-01, Axis Large Cap Fund, 234.50
2022-01-02, Axis Large Cap Fund, 235.10
...
```

### **mutual_funds_aum.csv**
```
fund_house, year, aum_crores
SBI, 2022, 950000
SBI, 2023, 1025000
...
```

### **sip_inflows.csv**
```
date, sip_inflow
2022-01-01, 8500
2022-02-01, 9200
...
```

### **investor_demographics.csv**
```
date, sip_amount, age_group, gender, fund_category
2022-01-01, 5000, 25-35, M, Equity
2022-01-02, 7500, 35-45, F, Debt
...
```

### **portfolio_holdings.csv**
```
scheme_name, sector, weight_percent
Axis Equity Fund, Financial Services, 28.5
Axis Equity Fund, IT, 18.2
...
```

### **geographic_distribution.csv**
```
state, sip_amount, city_tier
Maharashtra, 125000, T30
Karnataka, 98000, T30
...
```

### **folio_count.csv**
```
date, folio_count_crores
2022-01-01, 13.26
2022-02-01, 13.35
...
```

---

## Step 5: Run the Notebook

### **Option A: Jupyter Notebook (Interactive)**
```powershell
cd C:\Users\vasanth\OneDrive\Desktop\bluestock_mf_project
jupyter notebook EDA_Analysis.ipynb
```

Then:
- Browser opens automatically
- Run cells top-to-bottom (Shift + Enter)
- Charts display inline
- PNG files auto-save to `exported_charts/` folder

### **Option B: VSCode or PyCharm**
- Open the `.ipynb` file directly
- Run cells with built-in notebook support
- Output appears in the interface

---

## Step 6: Export Charts

The notebook **automatically exports** all charts as PNG files to:
```
C:\Users\vasanth\OneDrive\Desktop\bluestock_mf_project\exported_charts\
```

**Chart filenames:**
```
01_nav_trends_2022_2026.png
02_aum_by_fund_house.png
03_sip_inflows_timeseries.png
04_category_inflow_heatmap.png
05_investor_demographics.png
06_geographic_distribution.png
07_folio_count_growth.png
08_nav_correlation_matrix.png
09_sector_allocation_donut.png
```

---

## Step 7: Git Commit & Push

After running successfully:

```powershell
cd C:\Users\vasanth\OneDrive\Desktop\bluestock_mf_project

git add EDA_Analysis.ipynb exported_charts/
git commit -m "Add: Complete EDA analysis with 10 key insights and Seaborn visualizations"
git push origin main
```

---

## Troubleshooting

### ❌ "FileNotFoundError: No such file or directory"
**Solution**: Check your CSV file names and the `data_path` variable. Ensure files are in the exact folder you specified.

### ❌ "ModuleNotFoundError: No module named 'seaborn'"
**Solution**: Install missing library:
```powershell
pip install seaborn
```

### ❌ Charts not displaying
**Solution**: Ensure you're running cells sequentially from top. Try restarting the kernel:
- Jupyter: **Kernel → Restart**
- VSCode: **Ctrl + Shift + P** → "Restart Kernel"

### ❌ "SettingWithCopyWarning" in Pandas
**Ignore it** — it's just a warning, not an error. Charts will still export correctly.

### ❌ Low resolution PNGs
**Solution**: DPI is set to 300 by default. If you need higher:
```python
plt.savefig(..., dpi=600, bbox_inches='tight')
```

---

## Common Customizations

### Change Colors
Replace this line:
```python
sns.set_palette('husl')
```
With:
```python
sns.set_palette('Set2')  # or 'Dark2', 'muted', 'pastel', etc.
```

### Adjust Figure Size
In any cell:
```python
plt.rcParams['figure.figsize'] = (18, 8)  # Change width, height
```

### Add Your Findings
In the **"Key Findings"** section, add/edit Markdown cells with your own insights.

---

## Expected Runtime

**Total execution time**: ~2-3 minutes (depends on data size)
- Data loading: 10 seconds
- NAV analysis: 15 seconds
- Demographics: 20 seconds
- Charts export: 30 seconds
- Total: ~2 minutes

---

## Next Steps After EDA

1. ✅ Run this notebook and export charts
2. ✅ Validate findings against raw data
3. ✅ Create final presentation/PDF report with charts
4. ✅ Push to GitHub: `https://github.com/ishu2210/bluestock_mf_project`
5. ✅ Share findings in team sync meeting

---

## Questions?

**For data path issues**: Use `os.listdir()` to verify folder contents:
```python
import os
print(os.listdir(r'C:\Users\vasanth\OneDrive\Desktop\bluestock_mf_project\data'))
```

**For chart customization**: Refer to [Seaborn documentation](https://seaborn.pydata.org/)

---

**Good luck with your EDA, miss pretty!** 🎯📊
