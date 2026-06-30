"""
Day 3: Fund Performance Analytics EDA
Bluestock Fintech Capstone Project
Standalone script (run via PowerShell)
"""

import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns

print("✅ All imports loaded successfully!")
print()

# Set random seed for reproducibility
np.random.seed(2024)

# Sample funds data (for testing - we'll connect to your SQLite DB later)
FUNDS = [
    # (name, annual_return, volatility, expense_ratio)
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
    ("HDFC Mid-Cap Opportunities", 0.175, 0.18, 1.62),
    ("Axis Midcap Fund", 0.180, 0.19, 1.55),
    ("Franklin India Smallcap Fund", 0.205, 0.24, 1.85),
    ("HDFC Hybrid Debt Fund", 0.095, 0.08, 1.05),
    ("ICICI Pru Conservative Hybrid Fund", 0.085, 0.07, 0.85),
    ("Kotak Liquid Fund", 0.062, 0.02, 0.36),
    ("HDFC Balanced Advantage Fund", 0.135, 0.13, 1.25),
    ("Nippon India Growth Fund", 0.192, 0.21, 1.78),
    ("Kotak Standard Multicap Fund", 0.160, 0.16, 1.20),
    ("Axis Equity Hybrid Fund", 0.125, 0.12, 1.20),
    ("SBI Blue Chip Fund", 0.142, 0.14, 0.89),
    ("Motilal Oswal Large Cap Fund", 0.150, 0.145, 0.98),
    ("Aditya Birla SL Growth Fund", 0.168, 0.175, 1.30),
    ("ICICI Pru Multicap Fund", 0.165, 0.17, 1.45),
    ("Axis Growth Fund", 0.172, 0.18, 1.42),
    ("Franklin India Growth Fund", 0.188, 0.20, 1.65),
    ("Kotak Growth Fund", 0.158, 0.16, 1.18),
    ("ICICI Pru Smallcap Fund", 0.198, 0.22, 1.90),
]

# Generate date range (5 years of business days)
dates = pd.bdate_range(end='2026-06-27', periods=1304)

print(f"📅 Date range: {dates[0].date()} to {dates[-1].date()}")
print(f"📊 Total trading days: {len(dates)}")
print(f"💰 Number of funds: {len(FUNDS)}")
print()

# Simulate NAV data for each fund
print("🔄 Generating simulated NAV data for funds...")

nav_data = {}
for fund_name, annual_return, volatility, expense_ratio in FUNDS:
    # Generate random daily returns based on annual metrics
    daily_return = annual_return / 252  # Convert to daily
    daily_vol = volatility / np.sqrt(252)
    
    # Generate returns using GBM (Geometric Brownian Motion)
    returns = np.random.normal(daily_return, daily_vol, len(dates))
    
    # Calculate NAV starting from 100
    nav_values = 100 * np.exp(np.cumsum(returns))
    
    nav_data[fund_name] = nav_values

# Create DataFrame
nav_df = pd.DataFrame(nav_data, index=dates)

print(f"✅ Generated NAV data shape: {nav_df.shape}")
print()
print("📈 First 5 rows of NAV data:")
print(nav_df.head())
print()
print("📊 Last 5 rows of NAV data:")
print(nav_df.tail())
print()

# =====================================================================
# PERFORMANCE METRICS CALCULATION
# =====================================================================

print("=" * 70)
print("CALCULATING PERFORMANCE METRICS")
print("=" * 70)
print()

# 1. CAGR (Compound Annual Growth Rate)
def calculate_cagr(nav_series):
    """Calculate CAGR from NAV series"""
    start_nav = nav_series.iloc[0]
    end_nav = nav_series.iloc[-1]
    num_years = len(nav_series) / 252  # 252 trading days per year
    
    cagr = (end_nav / start_nav) ** (1 / num_years) - 1
    return cagr

# 2. VOLATILITY (Annual standard deviation of returns)
def calculate_volatility(nav_series):
    """Calculate annualized volatility"""
    returns = nav_series.pct_change().dropna()
    volatility = returns.std() * np.sqrt(252)
    return volatility

# 3. SHARPE RATIO (Return per unit of risk)
def calculate_sharpe_ratio(nav_series, risk_free_rate=0.05):
    """Calculate Sharpe Ratio"""
    returns = nav_series.pct_change().dropna()
    excess_returns = returns - risk_free_rate / 252
    sharpe = excess_returns.mean() / excess_returns.std() * np.sqrt(252)
    return sharpe

# 4. SORTINO RATIO (Return per unit of downside risk)
def calculate_sortino_ratio(nav_series, risk_free_rate=0.05):
    """Calculate Sortino Ratio"""
    returns = nav_series.pct_change().dropna()
    excess_returns = returns - risk_free_rate / 252
    
    # Only consider downside deviations (negative returns)
    downside_returns = excess_returns[excess_returns < 0]
    downside_vol = downside_returns.std() * np.sqrt(252)
    
    sortino = excess_returns.mean() * np.sqrt(252) / downside_vol
    return sortino

# 5. MAXIMUM DRAWDOWN
def calculate_max_drawdown(nav_series):
    """Calculate maximum drawdown"""
    cummax = nav_series.expanding().max()
    drawdown = (nav_series - cummax) / cummax
    max_dd = drawdown.min()
    return max_dd

# 6. ALPHA & BETA (vs benchmark)
def calculate_alpha_beta(nav_series, benchmark_series, risk_free_rate=0.05):
    """Calculate Alpha and Beta"""
    fund_returns = nav_series.pct_change().dropna()
    bench_returns = benchmark_series.pct_change().dropna()
    
    # Align returns
    common_dates = fund_returns.index.intersection(bench_returns.index)
    fund_ret = fund_returns[common_dates]
    bench_ret = bench_returns[common_dates]
    
    # Calculate beta
    covariance = np.cov(fund_ret, bench_ret)[0][1]
    bench_variance = np.var(bench_ret)
    beta = covariance / bench_variance
    
    # Calculate alpha
    fund_annual_return = fund_ret.mean() * 252
    bench_annual_return = bench_ret.mean() * 252
    alpha = fund_annual_return - (risk_free_rate + beta * (bench_annual_return - risk_free_rate))
    
    return alpha, beta

# Create synthetic benchmark (Nifty 50 proxy)
benchmark_return = 0.12
benchmark_vol = 0.14
bench_returns = np.random.normal(benchmark_return / 252, benchmark_vol / np.sqrt(252), len(dates))
benchmark_nav = 100 * np.exp(np.cumsum(bench_returns))
benchmark_series = pd.Series(benchmark_nav, index=dates)

print("📊 Computing metrics for all funds...\n")

metrics_data = []

for fund_name in nav_df.columns:
    nav_series = nav_df[fund_name]
    
    cagr = calculate_cagr(nav_series)
    volatility = calculate_volatility(nav_series)
    sharpe = calculate_sharpe_ratio(nav_series)
    sortino = calculate_sortino_ratio(nav_series)
    max_dd = calculate_max_drawdown(nav_series)
    alpha, beta = calculate_alpha_beta(nav_series, benchmark_series)
    
    metrics_data.append({
        'Fund Name': fund_name,
        'CAGR (%)': cagr * 100,
        'Volatility (%)': volatility * 100,
        'Sharpe Ratio': sharpe,
        'Sortino Ratio': sortino,
        'Max Drawdown (%)': max_dd * 100,
        'Alpha (%)': alpha * 100,
        'Beta': beta
    })

metrics_df = pd.DataFrame(metrics_data)

print("✅ Metrics calculated!")
print()
print(metrics_df.to_string(index=False))
print()

# =====================================================================
# COMPOSITE FUND SCORECARD
# =====================================================================

print("=" * 70)
print("COMPOSITE FUND SCORECARD")
print("=" * 70)
print()

# Rank each metric (lower is better for volatility & max drawdown)
metrics_df['CAGR_Rank'] = metrics_df['CAGR (%)'].rank(ascending=False)
metrics_df['Volatility_Rank'] = metrics_df['Volatility (%)'].rank(ascending=True)  # Lower is better
metrics_df['Sharpe_Rank'] = metrics_df['Sharpe Ratio'].rank(ascending=False)
metrics_df['Sortino_Rank'] = metrics_df['Sortino Ratio'].rank(ascending=False)
metrics_df['MaxDD_Rank'] = metrics_df['Max Drawdown (%)'].rank(ascending=True)  # Lower is better

# Calculate composite score (average of ranks)
rank_cols = ['CAGR_Rank', 'Volatility_Rank', 'Sharpe_Rank', 'Sortino_Rank', 'MaxDD_Rank']
metrics_df['Composite_Score'] = metrics_df[rank_cols].mean(axis=1)
metrics_df['Overall_Rank'] = metrics_df['Composite_Score'].rank(ascending=True)

scorecard = metrics_df[['Fund Name', 'CAGR (%)', 'Sharpe Ratio', 'Sortino Ratio', 
                        'Max Drawdown (%)', 'Composite_Score', 'Overall_Rank']].copy()
scorecard = scorecard.sort_values('Overall_Rank')

print("🏆 TOP 10 FUNDS BY COMPOSITE SCORE:")
print()
print(scorecard.head(10).to_string(index=False))
print()

# =====================================================================
# VISUALIZATIONS
# =====================================================================

print("=" * 70)
print("GENERATING VISUALIZATIONS")
print("=" * 70)
print()

# Create figure with subplots
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 1. CAGR vs Volatility (Risk-Return Scatter)
ax1 = axes[0, 0]
ax1.scatter(metrics_df['Volatility (%)'], metrics_df['CAGR (%)'], s=100, alpha=0.6, color='steelblue')
ax1.set_xlabel('Volatility (%)', fontsize=10)
ax1.set_ylabel('CAGR (%)', fontsize=10)
ax1.set_title('Risk-Return Profile', fontsize=12, fontweight='bold')
ax1.grid(True, alpha=0.3)

# 2. Top 10 Funds by CAGR
ax2 = axes[0, 1]
top_10_cagr = metrics_df.nlargest(10, 'CAGR (%)')
ax2.barh(range(len(top_10_cagr)), top_10_cagr['CAGR (%)'], color='green', alpha=0.7)
ax2.set_yticks(range(len(top_10_cagr)))
ax2.set_yticklabels([name[:25] for name in top_10_cagr['Fund Name']], fontsize=8)
ax2.set_xlabel('CAGR (%)', fontsize=10)
ax2.set_title('Top 10 Funds by CAGR', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3, axis='x')

# 3. Sharpe Ratio Distribution
ax3 = axes[1, 0]
ax3.hist(metrics_df['Sharpe Ratio'], bins=15, color='coral', alpha=0.7, edgecolor='black')
ax3.set_xlabel('Sharpe Ratio', fontsize=10)
ax3.set_ylabel('Number of Funds', fontsize=10)
ax3.set_title('Sharpe Ratio Distribution', fontsize=12, fontweight='bold')
ax3.grid(True, alpha=0.3, axis='y')

# 4. NAV Trend (Top 5 performers)
ax4 = axes[1, 1]
top_5_funds = metrics_df.nlargest(5, 'Sharpe Ratio')['Fund Name'].values
for fund in top_5_funds:
    ax4.plot(dates, nav_df[fund], label=fund[:20], linewidth=2, alpha=0.8)
ax4.set_xlabel('Date', fontsize=10)
ax4.set_ylabel('NAV', fontsize=10)
ax4.set_title('NAV Trend - Top 5 by Sharpe Ratio', fontsize=12, fontweight='bold')
ax4.legend(fontsize=8, loc='best')
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('performance_analytics_day3.png', dpi=150, bbox_inches='tight')
print("✅ Chart saved as: performance_analytics_day3.png")
print()

# Summary statistics
print("=" * 70)
print("SUMMARY STATISTICS")
print("=" * 70)
print()
print(metrics_df[['CAGR (%)', 'Volatility (%)', 'Sharpe Ratio', 'Sortino Ratio', 'Max Drawdown (%)']].describe())
print()

print("✅ Performance analytics complete!")
print()
print("📁 Next steps:")
print("   1. Save metrics to CSV: metrics_df.to_csv('performance_metrics.csv', index=False)")
print("   2. Save to SQLite database for integration with your schema")
print("   3. Review visualizations in performance_analytics_day3.png")
