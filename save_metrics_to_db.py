"""
Day 3: Save Performance Metrics to SQLite Database
This connects the performance analytics to your existing database schema
"""

import pandas as pd
import numpy as np
import sqlite3
from pathlib import Path

# Database path
DB_PATH = r'C:\Users\vasanth\OneDrive\Desktop\bluestock_mf_project\bluestock_mf.db'

print("=" * 70)
print("CONNECTING TO SQLite DATABASE")
print("=" * 70)
print()

# Connect to database
try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    print(f"✅ Connected to: {DB_PATH}")
    print()
except Exception as e:
    print(f"❌ Error connecting to database: {e}")
    exit()

# Check existing tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
existing_tables = cursor.fetchall()
print("📋 Existing tables in database:")
for table in existing_tables:
    print(f"   - {table[0]}")
print()

# =====================================================================
# CREATE PERFORMANCE METRICS TABLE (if not exists)
# =====================================================================

create_perf_table = """
CREATE TABLE IF NOT EXISTS fund_performance (
    performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_id INTEGER NOT NULL,
    fund_name TEXT NOT NULL,
    calculation_date DATE DEFAULT CURRENT_DATE,
    cagr REAL,
    volatility REAL,
    sharpe_ratio REAL,
    sortino_ratio REAL,
    max_drawdown REAL,
    alpha REAL,
    beta REAL,
    composite_score REAL,
    overall_rank INTEGER,
    FOREIGN KEY(fund_id) REFERENCES funds(fund_id)
);
"""

try:
    cursor.execute(create_perf_table)
    conn.commit()
    print("✅ Performance metrics table created/verified")
    print()
except Exception as e:
    print(f"❌ Error creating table: {e}")
    print()

# =====================================================================
# GET FUND IDs FROM DATABASE
# =====================================================================

cursor.execute("SELECT fund_id, fund_name FROM funds;")
fund_mapping = cursor.fetchall()

if not fund_mapping:
    print("⚠️  No funds found in database. Please run Day 2 setup first.")
    conn.close()
    exit()

print(f"📌 Found {len(fund_mapping)} funds in database")
print()

# Create mapping of fund names to IDs
fund_name_to_id = {name: fund_id for fund_id, name in fund_mapping}

# =====================================================================
# SAMPLE PERFORMANCE DATA (Replace with your actual calculations)
# =====================================================================

print("📊 Generating sample performance metrics...")
print()

# Recreate the metrics from the previous script
np.random.seed(2024)

FUNDS = [
    ("HDFC Mid-Cap Opportunities", 0.175, 0.18, 1.62),
    ("Axis Bluechip Fund", 0.145, 0.14, 1.35),
    ("Kotak Standard Multicap Fund", 0.160, 0.16, 1.20),
    ("ICICI Pru Bluechip Fund", 0.138, 0.13, 1.40),
    ("Mirae Asset Large Cap Fund", 0.155, 0.15, 0.95),
    ("SBI Bluechip Fund", 0.142, 0.14, 0.89),
    ("Nippon India Small Cap Fund", 0.210, 0.25, 1.75),
    ("Axis Midcap Fund", 0.180, 0.19, 1.55),
    ("Franklin India Smallcap Fund", 0.205, 0.24, 1.85),
    ("Motilal Oswal Multicap 35 Fund", 0.168, 0.17, 1.10),
    ("HDFC Hybrid Debt Fund", 0.095, 0.08, 1.05),
    ("ICICI Pru Conservative Hybrid Fund", 0.085, 0.07, 0.85),
    ("Axis Equity Hybrid Fund", 0.125, 0.12, 1.20),
    ("Kotak Equity Hybrid Fund", 0.130, 0.13, 1.15),
    ("SBI Equity Hybrid Fund", 0.115, 0.11, 0.95),
    ("Aditya Birla SL Equity Hybrid Fund", 0.120, 0.11, 1.10),
    ("HDFC Liquid Fund", 0.055, 0.02, 0.40),
    ("ICICI Pru Liquid Fund", 0.060, 0.02, 0.35),
    ("Axis Liquid Fund", 0.058, 0.02, 0.38),
    ("Kotak Liquid Fund", 0.062, 0.02, 0.36),
    ("SBI Liquid Fund", 0.056, 0.02, 0.32),
    ("Motilal Oswal Liquid Fund", 0.061, 0.02, 0.34),
    ("HDFC Balanced Advantage Fund", 0.135, 0.13, 1.25),
    ("Nippon India Growth Fund", 0.192, 0.21, 1.78),
    ("Franklin India Value Fund", 0.178, 0.19, 1.58),
    ("Kotak Emerging Opportunities Fund", 0.195, 0.22, 1.68),
    ("ICICI Pru Emerging Bluechip Fund", 0.188, 0.20, 1.62),
    ("Axis Focused 25 Fund", 0.172, 0.17, 1.40),
    ("SBI Growth Fund", 0.165, 0.16, 1.30),
    ("Motilal Oswal Large Cap Fund", 0.150, 0.145, 0.98),
    ("Aditya Birla SL Growth Fund", 0.168, 0.175, 1.30),
    ("ICICI Pru Smallcap Fund", 0.198, 0.22, 1.90),
]

dates = pd.bdate_range(end='2026-06-27', periods=1304)

# Performance metrics calculation functions
def calculate_cagr(nav_series):
    start_nav = nav_series.iloc[0]
    end_nav = nav_series.iloc[-1]
    num_years = len(nav_series) / 252
    return (end_nav / start_nav) ** (1 / num_years) - 1

def calculate_volatility(nav_series):
    returns = nav_series.pct_change().dropna()
    return returns.std() * np.sqrt(252)

def calculate_sharpe_ratio(nav_series, risk_free_rate=0.05):
    returns = nav_series.pct_change().dropna()
    excess_returns = returns - risk_free_rate / 252
    return excess_returns.mean() / excess_returns.std() * np.sqrt(252)

def calculate_sortino_ratio(nav_series, risk_free_rate=0.05):
    returns = nav_series.pct_change().dropna()
    excess_returns = returns - risk_free_rate / 252
    downside_returns = excess_returns[excess_returns < 0]
    downside_vol = downside_returns.std() * np.sqrt(252)
    return excess_returns.mean() * np.sqrt(252) / downside_vol

def calculate_max_drawdown(nav_series):
    cummax = nav_series.expanding().max()
    drawdown = (nav_series - cummax) / cummax
    return drawdown.min()

def calculate_alpha_beta(nav_series, benchmark_series, risk_free_rate=0.05):
    fund_returns = nav_series.pct_change().dropna()
    bench_returns = benchmark_series.pct_change().dropna()
    common_dates = fund_returns.index.intersection(bench_returns.index)
    fund_ret = fund_returns[common_dates]
    bench_ret = bench_returns[common_dates]
    covariance = np.cov(fund_ret, bench_ret)[0][1]
    bench_variance = np.var(bench_ret)
    beta = covariance / bench_variance
    fund_annual_return = fund_ret.mean() * 252
    bench_annual_return = bench_ret.mean() * 252
    alpha = fund_annual_return - (risk_free_rate + beta * (bench_annual_return - risk_free_rate))
    return alpha, beta

# Generate benchmark
benchmark_return = 0.12
benchmark_vol = 0.14
bench_returns = np.random.normal(benchmark_return / 252, benchmark_vol / np.sqrt(252), len(dates))
benchmark_nav = 100 * np.exp(np.cumsum(bench_returns))
benchmark_series = pd.Series(benchmark_nav, index=dates)

# Calculate metrics for all funds
print("⏳ Computing performance metrics for all funds...")
print()

metrics_data = []

for fund_name, annual_return, volatility, expense_ratio in FUNDS:
    # Generate NAV
    daily_return = annual_return / 252
    daily_vol = volatility / np.sqrt(252)
    returns = np.random.normal(daily_return, daily_vol, len(dates))
    nav_values = 100 * np.exp(np.cumsum(returns))
    nav_series = pd.Series(nav_values, index=dates)
    
    # Calculate metrics
    cagr = calculate_cagr(nav_series)
    vol = calculate_volatility(nav_series)
    sharpe = calculate_sharpe_ratio(nav_series)
    sortino = calculate_sortino_ratio(nav_series)
    max_dd = calculate_max_drawdown(nav_series)
    alpha, beta = calculate_alpha_beta(nav_series, benchmark_series)
    
    metrics_data.append({
        'fund_name': fund_name,
        'cagr': cagr,
        'volatility': vol,
        'sharpe_ratio': sharpe,
        'sortino_ratio': sortino,
        'max_drawdown': max_dd,
        'alpha': alpha,
        'beta': beta
    })

metrics_df = pd.DataFrame(metrics_data)

# Calculate composite score
metrics_df['cagr_rank'] = metrics_df['cagr'].rank(ascending=False)
metrics_df['vol_rank'] = metrics_df['volatility'].rank(ascending=True)
metrics_df['sharpe_rank'] = metrics_df['sharpe_ratio'].rank(ascending=False)
metrics_df['sortino_rank'] = metrics_df['sortino_ratio'].rank(ascending=False)
metrics_df['dd_rank'] = metrics_df['max_drawdown'].rank(ascending=True)

rank_cols = ['cagr_rank', 'vol_rank', 'sharpe_rank', 'sortino_rank', 'dd_rank']
metrics_df['composite_score'] = metrics_df[rank_cols].mean(axis=1)
metrics_df['overall_rank'] = metrics_df['composite_score'].rank(ascending=True)

print(f"✅ Metrics calculated for {len(metrics_df)} funds")
print()

# =====================================================================
# INSERT INTO DATABASE
# =====================================================================

print("💾 Inserting performance metrics into database...")
print()

inserted_count = 0
skipped_count = 0

for _, row in metrics_df.iterrows():
    fund_name = row['fund_name']
    
    # Check if fund exists in database
    if fund_name not in fund_name_to_id:
        print(f"⚠️  Skipped '{fund_name}' (not in database)")
        skipped_count += 1
        continue
    
    fund_id = fund_name_to_id[fund_name]
    
    try:
        insert_query = """
        INSERT INTO fund_performance 
        (fund_id, fund_name, cagr, volatility, sharpe_ratio, sortino_ratio, 
         max_drawdown, alpha, beta, composite_score, overall_rank)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        cursor.execute(insert_query, (
            fund_id,
            fund_name,
            row['cagr'],
            row['volatility'],
            row['sharpe_ratio'],
            row['sortino_ratio'],
            row['max_drawdown'],
            row['alpha'],
            row['beta'],
            row['composite_score'],
            int(row['overall_rank'])
        ))
        
        inserted_count += 1
        
    except Exception as e:
        print(f"❌ Error inserting {fund_name}: {e}")
        skipped_count += 1

conn.commit()

print(f"✅ Inserted: {inserted_count} records")
print(f"⏭️  Skipped: {skipped_count} records")
print()

# =====================================================================
# VERIFY DATA IN DATABASE
# =====================================================================

print("=" * 70)
print("VERIFYING DATA IN DATABASE")
print("=" * 70)
print()

query = """
SELECT fund_name, cagr, volatility, sharpe_ratio, overall_rank
FROM fund_performance
ORDER BY overall_rank
LIMIT 10;
"""

result = cursor.execute(query).fetchall()

print("🏆 Top 10 Funds by Composite Score:\n")
print(f"{'Fund Name':<35} {'CAGR':<10} {'Volatility':<12} {'Sharpe':<10} {'Rank':<5}")
print("-" * 75)

for row in result:
    fund_name, cagr, vol, sharpe, rank = row
    print(f"{fund_name:<35} {cagr:>8.2f}% {vol:>10.2f}% {sharpe:>8.2f} {rank:>4.0f}")

print()

# Get summary stats
summary = cursor.execute("""
SELECT 
    COUNT(*) as total_funds,
    AVG(cagr) as avg_cagr,
    AVG(volatility) as avg_volatility,
    AVG(sharpe_ratio) as avg_sharpe,
    MIN(max_drawdown) as min_drawdown,
    MAX(max_drawdown) as max_drawdown
FROM fund_performance;
""").fetchone()

print("=" * 70)
print("SUMMARY STATISTICS")
print("=" * 70)
print()
print(f"Total Funds Analyzed: {summary[0]}")
print(f"Average CAGR: {summary[1]:.2f}%")
print(f"Average Volatility: {summary[2]:.2f}%")
print(f"Average Sharpe Ratio: {summary[3]:.2f}")
print(f"Best Drawdown: {summary[4]:.2f}%")
print(f"Worst Drawdown: {summary[5]:.2f}%")
print()

# Close connection
conn.close()

print("✅ Database updated successfully!")
print()
print("📁 Your fund performance data is now saved in SQLite database")
print(f"   Location: {DB_PATH}")
print()
print("🎯 Day 3 Complete! Ready for Day 4? 🚀")
