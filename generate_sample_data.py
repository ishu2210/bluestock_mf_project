"""
Sample Data Generator for Bluestock Fintech EDA Analysis
=========================================================
Use this script to generate realistic test data if you want to preview
the EDA notebook before running with actual production data.

Usage:
    python generate_sample_data.py

Output:
    Creates CSV files in ./data/ directory
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# Create data directory
os.makedirs('data', exist_ok=True)

print("Generating sample data for Bluestock Fintech EDA...")
print("=" * 60)

# ============================================================================
# 1. MUTUAL FUNDS NAV DATA (40 schemes, Jan 2022 - Dec 2025)
# ============================================================================
print("\n1. Generating NAV data (40 schemes)...")

fund_names = [
    'Axis Large Cap Fund', 'Axis Midcap Fund', 'Axis Small Cap Fund',
    'SBI Large Cap Fund', 'SBI Midcap Fund', 'SBI Small Cap Fund',
    'HDFC Large Cap Fund', 'HDFC Midcap Fund', 'HDFC Small Cap Fund',
    'ICICI Large Cap Fund', 'ICICI Midcap Fund', 'ICICI Small Cap Fund',
    'Bajaj Large Cap Fund', 'Bajaj Midcap Fund', 'Bajaj Small Cap Fund',
    'Kotak Large Cap Fund', 'Kotak Midcap Fund', 'Kotak Small Cap Fund',
    'Mirae Large Cap Fund', 'Mirae Midcap Fund', 'Mirae Small Cap Fund',
    'Nippon Large Cap Fund', 'Nippon Midcap Fund', 'Nippon Small Cap Fund',
    'Franklin Large Cap Fund', 'Franklin Midcap Fund', 'Franklin Small Cap Fund',
    'IDBI Large Cap Fund', 'IDBI Midcap Fund', 'IDBI Small Cap Fund',
    'L&T Large Cap Fund', 'L&T Midcap Fund', 'L&T Small Cap Fund',
    'Canara Large Cap Fund', 'Canara Midcap Fund', 'Canara Small Cap Fund',
    'BOI Large Cap Fund', 'BOI Midcap Fund', 'BOI Small Cap Fund'
]

dates = pd.date_range(start='2022-01-01', end='2025-12-31', freq='D')
nav_records = []

np.random.seed(42)
for fund in fund_names:
    base_nav = np.random.uniform(50, 300)
    returns = np.random.normal(0.0003, 0.015, len(dates))  # Daily returns
    nav_prices = base_nav * np.exp(np.cumsum(returns))
    
    for date, nav in zip(dates, nav_prices):
        nav_records.append({'date': date, 'scheme_name': fund, 'nav': round(nav, 2)})

nav_df = pd.DataFrame(nav_records)
nav_df.to_csv('data/mutual_funds_nav.csv', index=False)
print(f"✓ Created: mutual_funds_nav.csv ({len(nav_df)} records)")

# ============================================================================
# 2. AUM DATA (Fund House level, 2022-2025)
# ============================================================================
print("\n2. Generating AUM data...")

fund_houses = ['SBI', 'HDFC', 'ICICI', 'Axis', 'Bajaj', 'Kotak', 'Mirae', 'Nippon', 'Franklin', 'IDBI']
years = [2022, 2023, 2024, 2025]

aum_records = []
for house in fund_houses:
    base_aum = np.random.uniform(300000, 1200000)
    for year in years:
        growth = 1 + np.random.uniform(0.05, 0.20)  # 5-20% growth per year
        aum = base_aum * (growth ** (year - 2022))
        aum_records.append({'fund_house': house, 'year': year, 'aum_crores': round(aum, 0)})

aum_df = pd.DataFrame(aum_records)
aum_df.to_csv('data/mutual_funds_aum.csv', index=False)
print(f"✓ Created: mutual_funds_aum.csv ({len(aum_df)} records)")

# ============================================================================
# 3. SIP INFLOWS DATA (Monthly, Jan 2022 - Dec 2025)
# ============================================================================
print("\n3. Generating SIP inflows data...")

months = pd.date_range(start='2022-01-01', end='2025-12-31', freq='M')
sip_records = []

np.random.seed(42)
base_sip = 10000
for month in months:
    # Trend: 5% monthly growth + seasonal variation
    time_factor = (month.year - 2022 + month.month / 12) / 4
    trend = base_sip * (1.05 ** (time_factor * 12))
    
    # Seasonal boost in Q4 (Oct-Dec)
    seasonal = 1.15 if month.month >= 10 else 0.95 if month.month in [1, 2] else 1.0
    
    sip_inflow = trend * seasonal + np.random.normal(0, 500)
    
    if month.year == 2025 and month.month == 12:  # All-time high in Dec 2025
        sip_inflow = 31002  # ₹31,002 Cr
    
    sip_records.append({'date': month, 'sip_inflow': round(max(sip_inflow, 5000), 0)})

sip_df = pd.DataFrame(sip_records)
sip_df.to_csv('data/sip_inflows.csv', index=False)
print(f"✓ Created: sip_inflows.csv ({len(sip_df)} records)")

# ============================================================================
# 4. INVESTOR DEMOGRAPHICS (Age, Gender, SIP amounts)
# ============================================================================
print("\n4. Generating investor demographics...")

age_groups = ['18-25', '25-35', '35-45', '45-55', '55-65', '65+']
genders = ['M', 'F']
categories = ['Equity', 'Debt', 'Hybrid', 'Liquid']

investor_records = []
np.random.seed(42)

for i in range(50000):  # 50k investor transactions
    date = pd.Timestamp('2022-01-01') + timedelta(days=np.random.randint(0, 365*4))
    age_group = np.random.choice(age_groups, p=[0.05, 0.35, 0.23, 0.18, 0.12, 0.07])
    gender = np.random.choice(genders, p=[0.68, 0.32])
    
    # SIP amount varies by age
    if age_group == '25-35':
        sip_amount = np.random.normal(6000, 2000)
    elif age_group in ['35-45', '45-55']:
        sip_amount = np.random.normal(8000, 3000)
    else:
        sip_amount = np.random.normal(5000, 1500)
    
    category = np.random.choice(categories, p=[0.55, 0.25, 0.15, 0.05])
    
    investor_records.append({
        'date': date,
        'sip_amount': max(1000, round(sip_amount, 0)),
        'age_group': age_group,
        'gender': gender,
        'fund_category': category
    })

investor_df = pd.DataFrame(investor_records)
investor_df.to_csv('data/investor_demographics.csv', index=False)
print(f"✓ Created: investor_demographics.csv ({len(investor_df)} records)")

# ============================================================================
# 5. PORTFOLIO HOLDINGS (Sector allocation)
# ============================================================================
print("\n5. Generating portfolio holdings (sector allocation)...")

sectors = [
    'Financial Services', 'IT', 'Pharma', 'Auto', 'FMCG',
    'Energy', 'Infrastructure', 'Materials', 'Utilities', 'Telecom',
    'Realty', 'Media', 'Chemicals', 'Metals', 'Food & Beverage'
]

holdings_records = []
np.random.seed(42)

for fund in fund_names[:20]:  # Top 20 equity funds
    sector_weights = np.random.dirichlet(np.ones(len(sectors))) * 100
    
    for sector, weight in zip(sectors, sector_weights):
        if weight > 0.5:  # Only include sectors with >0.5% weight
            holdings_records.append({
                'scheme_name': fund,
                'sector': sector,
                'weight_percent': round(weight, 2)
            })

holdings_df = pd.DataFrame(holdings_records)
holdings_df.to_csv('data/portfolio_holdings.csv', index=False)
print(f"✓ Created: portfolio_holdings.csv ({len(holdings_df)} records)")

# ============================================================================
# 6. GEOGRAPHIC DISTRIBUTION (State-wise SIP)
# ============================================================================
print("\n6. Generating geographic distribution...")

states = [
    'Maharashtra', 'Karnataka', 'Tamil Nadu', 'Delhi', 'Telangana',
    'Rajasthan', 'Gujarat', 'Punjab', 'Haryana', 'West Bengal',
    'Uttar Pradesh', 'Madhya Pradesh', 'Andhra Pradesh', 'Bihar', 'Odisha'
]

city_tiers = {
    'Maharashtra': 'T30', 'Karnataka': 'T30', 'Tamil Nadu': 'T30', 'Delhi': 'T30', 'Telangana': 'T30',
    'Rajasthan': 'T30', 'Gujarat': 'T30', 'Punjab': 'B30', 'Haryana': 'T30', 'West Bengal': 'B30',
    'Uttar Pradesh': 'B30', 'Madhya Pradesh': 'B30', 'Andhra Pradesh': 'B30', 'Bihar': 'B30', 'Odisha': 'B30'
}

geo_records = []
np.random.seed(42)

for state in states:
    base_sip = np.random.uniform(10000, 150000)
    tier = city_tiers.get(state, 'B30')
    
    for _ in range(np.random.randint(50, 300)):
        geo_records.append({
            'state': state,
            'sip_amount': round(base_sip + np.random.normal(0, 10000), 0),
            'city_tier': tier
        })

geo_df = pd.DataFrame(geo_records)
geo_df.to_csv('data/geographic_distribution.csv', index=False)
print(f"✓ Created: geographic_distribution.csv ({len(geo_df)} records)")

# ============================================================================
# 7. FOLIO COUNT GROWTH (Jan 2022 - Dec 2025)
# ============================================================================
print("\n7. Generating folio count growth...")

months = pd.date_range(start='2022-01-01', end='2025-12-31', freq='M')
folio_records = []

start_folio = 13.26
for i, month in enumerate(months):
    # Growth trend: 13.26 Cr → 26.12 Cr (96.9% growth)
    growth_rate = (26.12 / 13.26) ** (i / len(months))
    folio_count = 13.26 * (growth_rate ** i)
    
    folio_records.append({
        'date': month,
        'folio_count_crores': round(folio_count, 2)
    })

folio_df = pd.DataFrame(folio_records)
folio_df.to_csv('data/folio_count.csv', index=False)
print(f"✓ Created: folio_count.csv ({len(folio_df)} records)")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 60)
print("✅ SAMPLE DATA GENERATION COMPLETE")
print("=" * 60)
print(f"\nGenerated files in ./data/ directory:")
print(f"  • mutual_funds_nav.csv ({len(nav_df)} records)")
print(f"  • mutual_funds_aum.csv ({len(aum_df)} records)")
print(f"  • sip_inflows.csv ({len(sip_df)} records)")
print(f"  • investor_demographics.csv ({len(investor_df)} records)")
print(f"  • portfolio_holdings.csv ({len(holdings_df)} records)")
print(f"  • geographic_distribution.csv ({len(geo_df)} records)")
print(f"  • folio_count.csv ({len(folio_df)} records)")

print("\n📝 Next steps:")
print("  1. Run the EDA_Analysis.ipynb notebook")
print("  2. Charts will be exported to ./exported_charts/")
print("  3. Review the 10 key findings")

print("\n💡 Tip: To use actual production data, replace CSVs and update")
print("   the 'data_path' variable in EDA_Analysis.ipynb")
