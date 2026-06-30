#!/usr/bin/env python3
# ============================================================================
# BLUESTOCK FINTECH — DAY 3 EDA
# Fund Performance Analytics (Standalone Script)
# ============================================================================
# Run with: python performance_analytics.py
# ============================================================================

import pandas as pd
import numpy as np
import sqlite3  # Built-in: NO pip install!
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from scipy.stats import linregress, skew, kurtosis
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10

print("\n" + "="*70)
print("BLUESTOCK FINTECH — DAY 3 EDA: FUND PERFORMANCE ANALYTICS")
print("="*70)

# ============================================================================
# STEP 1: LOAD DATA FROM SQLITE
# ============================================================================
print("\n[STEP 1] Loading data from SQLite database...")

db_path = r'C:\Users\vasanth\OneDrive\Desktop\bluestock_mf_project\mutual_funds.db'

try:
    conn = sqlite3.connect(db_path)
    print(f"✓ Connected to database: {db_path}")
    
    # Load NAV data
    query = """
        SELECT scheme_id, scheme_name, nav_date, nav_value
        FROM nav_history
        ORDER BY scheme_id, nav_date
    """
    nav_df = pd.read_sql_query(query, conn)
    nav_df['nav_date'] = pd.to_datetime(nav_df['nav_date'])
    
    print(f"✓ Loaded {len(nav_df):,} NAV records")
    print(f"✓ {nav_df['scheme_id'].nunique()} unique schemes")
    print(f"✓ Date range: {nav_df['nav_date'].min().date()} to {nav_df['nav_date'].max().date()}")
    
    # Load scheme details
    scheme_df = pd.read_sql_query("SELECT * FROM schemes", conn)
    print(f"✓ Loaded {len(scheme_df)} scheme details")
    
    conn.close()
    
except Exception as e:
    print(f"✗ Database error: {e}")
    print("\n[FALLBACK] Using demo data instead...")
    # Create demo data (if DB fails)
    nav_df = pd.DataFrame({
        'scheme_id': [1]*100 + [2]*100,
        'scheme_name': ['Fund A']*100 + ['Fund B']*100,
        'nav_date': pd.date_range('2021-01-01', periods=200, freq='D'),
        'nav_value': np.concatenate([
            100 + np.cumsum(np.random.randn(100) * 0.5),
            100 + np.cumsum(np.random.randn(100) * 0.4)
        ])
    })
    scheme_df = pd.DataFrame({
        'scheme_id': [1, 2],
        'scheme_name': ['Fund A', 'Fund B'],
        'expense_ratio': [0.75, 0.65]
    })

# ============================================================================
# STEP 2: TASK 1 - DAILY RETURNS VALIDATION
# ============================================================================
print("\n[STEP 2] Computing daily returns...")

nav_pivot = nav_df.pivot_table(
    index='nav_date',
    columns='scheme_id',
    values='nav_value'
)

daily_returns = nav_pivot.pct_change()
all_returns = daily_returns.values.flatten()
all_returns = all_returns[~np.isnan(all_returns)]

print(f"✓ Daily returns computed: {daily_returns.shape}")
print(f"  Mean: {all_returns.mean()*100:.4f}%")
print(f"  Std Dev: {all_returns.std()*100:.4f}%")
print(f"  Skewness: {skew(all_returns):.4f}")
print(f"  Kurtosis: {kurtosis(all_returns):.4f}")

# Plot 1: Daily returns distribution
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

ax1 = axes[0, 0]
ax1.hist(all_returns, bins=100, edgecolor='black', alpha=0.7, color='steelblue')
ax1.axvline(all_returns.mean(), color='red', linestyle='--', label=f'Mean: {all_returns.mean():.4f}')
ax1.set_xlabel('Daily Return')
ax1.set_ylabel('Frequency')
ax1.set_title('Distribution of Daily Returns (All Schemes)')
ax1.legend()

ax2 = axes[0, 1]
sample_schemes = daily_returns.columns[:min(5, len(daily_returns.columns))]
for scheme in sample_schemes:
    ax2.plot(daily_returns.index, daily_returns[scheme] * 100, label=f'Scheme {scheme}', alpha=0.7)
ax2.set_xlabel('Date')
ax2.set_ylabel('Daily Return (%)')
ax2.set_title('Daily Returns Time Series (Sample)')
ax2.legend(fontsize=8)

ax3 = axes[1, 0]
ax3.boxplot([daily_returns[col].dropna() * 100 for col in daily_returns.columns[:10]])
ax3.set_ylabel('Daily Return (%)')
ax3.set_title('Daily Return Distribution (First 10 Schemes)')

ax4 = axes[1, 1]
skewness = daily_returns.skew()
kurt = daily_returns.kurtosis()
ax4.scatter(skewness, kurt, alpha=0.6, s=100, color='darkblue')
ax4.axhline(0, color='red', linestyle='--', alpha=0.5)
ax4.axvline(0, color='red', linestyle='--', alpha=0.5)
ax4.set_xlabel('Skewness')
ax4.set_ylabel('Kurtosis')
ax4.set_title('Return Distribution Shape')

plt.tight_layout()
plt.savefig('01_daily_returns_validation.png', dpi=300, bbox_inches='tight')
print("✓ Saved: 01_daily_returns_validation.png")
plt.close()

# ============================================================================
# STEP 3: TASK 2 - CAGR COMPUTATION
# ============================================================================
print("\n[STEP 3] Computing CAGR (1yr, 3yr, 5yr)...")

def compute_cagr(nav_series, years=1):
    nav_series = nav_series.dropna()
    if len(nav_series) < 2:
        return np.nan
    nav_start = nav_series.iloc[0]
    nav_end = nav_series.iloc[-1]
    if nav_start <= 0:
        return np.nan
    return ((nav_end / nav_start) ** (1 / years) - 1) * 100

cagr_data = []
for scheme_id in nav_pivot.columns:
    nav_series = nav_pivot[scheme_id]
    scheme_name = scheme_df[scheme_df['scheme_id'] == scheme_id]['scheme_name'].values
    scheme_name = scheme_name[0] if len(scheme_name) > 0 else f"Scheme {scheme_id}"
    
    cagr_1yr = compute_cagr(nav_series.tail(252), years=1)
    cagr_3yr = compute_cagr(nav_series.tail(756), years=3)
    cagr_5yr = compute_cagr(nav_series.tail(1260), years=5)
    total_days = len(nav_series) - 1
    total_years = total_days / 252
    cagr_all = compute_cagr(nav_series, years=total_years) if total_years > 0 else np.nan
    
    cagr_data.append({
        'scheme_id': scheme_id,
        'scheme_name': scheme_name,
        'cagr_1yr': cagr_1yr,
        'cagr_3yr': cagr_3yr,
        'cagr_5yr': cagr_5yr,
        'cagr_all': cagr_all,
        'nav_start': nav_series.iloc[0],
        'nav_end': nav_series.iloc[-1]
    })

cagr_df = pd.DataFrame(cagr_data).sort_values('cagr_3yr', ascending=False, na_position='last')
print(f"✓ CAGR computed for {len(cagr_df)} schemes")
print("\nTop 5 by 3Y CAGR:")
print(cagr_df[['scheme_name', 'cagr_1yr', 'cagr_3yr', 'cagr_5yr']].head(5).to_string(index=False))

# Plot: CAGR comparison
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

ax1 = axes[0, 0]
top_schemes = cagr_df.head(10)
x_pos = np.arange(len(top_schemes))
width = 0.2
ax1.bar(x_pos - 1.5*width, top_schemes['cagr_1yr'], width, label='1Y', alpha=0.8)
ax1.bar(x_pos - 0.5*width, top_schemes['cagr_3yr'], width, label='3Y', alpha=0.8)
ax1.bar(x_pos + 0.5*width, top_schemes['cagr_5yr'], width, label='5Y', alpha=0.8)
ax1.bar(x_pos + 1.5*width, top_schemes['cagr_all'], width, label='All', alpha=0.8)
ax1.set_ylabel('CAGR (%)')
ax1.set_title('CAGR Comparison (Top 10 Schemes)')
ax1.set_xticks(x_pos)
ax1.set_xticklabels([s[:12] for s in top_schemes['scheme_name']], rotation=45, ha='right', fontsize=8)
ax1.legend()

ax2 = axes[0, 1]
valid = cagr_df.dropna(subset=['cagr_3yr', 'cagr_5yr'])
ax2.scatter(valid['cagr_3yr'], valid['cagr_5yr'], alpha=0.6, s=100)
ax2.set_xlabel('3Y CAGR (%)')
ax2.set_ylabel('5Y CAGR (%)')
ax2.set_title('3Y vs 5Y CAGR')

ax3 = axes[1, 0]
cagr_1yr_valid = cagr_df['cagr_1yr'].dropna()
cagr_3yr_valid = cagr_df['cagr_3yr'].dropna()
cagr_5yr_valid = cagr_df['cagr_5yr'].dropna()
ax3.boxplot([cagr_1yr_valid, cagr_3yr_valid, cagr_5yr_valid], labels=['1Y', '3Y', '5Y'])
ax3.set_ylabel('CAGR (%)')
ax3.set_title('CAGR Distribution')

ax4 = axes[1, 1]
ax4.axis('off')
stats_text = f"""
CAGR Statistics
1Y Mean:  {cagr_1yr_valid.mean():.2f}%
3Y Mean:  {cagr_3yr_valid.mean():.2f}%
5Y Mean:  {cagr_5yr_valid.mean():.2f}%

1Y Median: {cagr_1yr_valid.median():.2f}%
3Y Median: {cagr_3yr_valid.median():.2f}%
5Y Median: {cagr_5yr_valid.median():.2f}%
"""
ax4.text(0.1, 0.5, stats_text, fontsize=11, family='monospace', verticalalignment='center')

plt.tight_layout()
plt.savefig('02_cagr_analysis.png', dpi=300, bbox_inches='tight')
print("✓ Saved: 02_cagr_analysis.png")
plt.close()

# ============================================================================
# STEP 4: TASK 3 & 4 - SHARPE & SORTINO RATIOS
# ============================================================================
print("\n[STEP 4] Computing Sharpe & Sortino ratios...")

Rf = 0.065  # 6.5% annual
rf_daily = Rf / 252

def compute_sharpe_ratio(returns_series, rf_daily=rf_daily, periods=252):
    returns_series = returns_series.dropna()
    if len(returns_series) < 2:
        return np.nan
    excess_return = returns_series.mean() - rf_daily
    volatility = returns_series.std()
    if volatility == 0:
        return np.nan
    return (excess_return / volatility) * np.sqrt(periods)

def compute_sortino_ratio(returns_series, rf_daily=rf_daily, periods=252):
    returns_series = returns_series.dropna()
    if len(returns_series) < 2:
        return np.nan
    excess_return = returns_series.mean() - rf_daily
    downside_returns = returns_series[returns_series < 0]
    if len(downside_returns) == 0:
        return np.nan
    downside_volatility = downside_returns.std()
    if downside_volatility == 0:
        return np.nan
    return (excess_return / downside_volatility) * np.sqrt(periods)

risk_metrics = []
lookback_days = 756

for scheme_id in daily_returns.columns:
    returns_series = daily_returns[scheme_id].tail(lookback_days)
    scheme_name = scheme_df[scheme_df['scheme_id'] == scheme_id]['scheme_name'].values
    scheme_name = scheme_name[0] if len(scheme_name) > 0 else f"Scheme {scheme_id}"
    
    sharpe = compute_sharpe_ratio(returns_series)
    sortino = compute_sortino_ratio(returns_series)
    volatility = returns_series.std() * np.sqrt(252)
    avg_return = returns_series.mean() * 252 * 100
    
    risk_metrics.append({
        'scheme_id': scheme_id,
        'scheme_name': scheme_name,
        'sharpe_ratio': sharpe,
        'sortino_ratio': sortino,
        'volatility': volatility * 100,
        'avg_annual_return': avg_return
    })

risk_df = pd.DataFrame(risk_metrics).sort_values('sharpe_ratio', ascending=False, na_position='last')
print(f"✓ Risk metrics computed for {len(risk_df)} schemes")
print("\nTop 5 by Sharpe Ratio:")
print(risk_df[['scheme_name', 'sharpe_ratio', 'sortino_ratio', 'volatility']].head(5).to_string(index=False))

# Plot: Sharpe & Sortino
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

ax1 = axes[0, 0]
top_sharpe = risk_df.head(10)
colors = ['green' if x > 1 else 'orange' if x > 0.5 else 'red' for x in top_sharpe['sharpe_ratio']]
ax1.barh(range(len(top_sharpe)), top_sharpe['sharpe_ratio'], color=colors, alpha=0.7)
ax1.set_yticks(range(len(top_sharpe)))
ax1.set_yticklabels([s[:20] for s in top_sharpe['scheme_name']], fontsize=8)
ax1.set_xlabel('Sharpe Ratio')
ax1.set_title('Sharpe Ratio Rankings (Top 10)')

ax2 = axes[0, 1]
valid_ratios = risk_df.dropna(subset=['sharpe_ratio', 'sortino_ratio'])
ax2.scatter(valid_ratios['sharpe_ratio'], valid_ratios['sortino_ratio'], alpha=0.6, s=100)
ax2.set_xlabel('Sharpe Ratio')
ax2.set_ylabel('Sortino Ratio')
ax2.set_title('Sharpe vs Sortino')

ax3 = axes[1, 0]
ax3.scatter(risk_df['volatility'], risk_df['avg_annual_return'], alpha=0.6, s=100)
ax3.set_xlabel('Volatility (%)')
ax3.set_ylabel('Average Annual Return (%)')
ax3.set_title('Risk-Return Profile')

ax4 = axes[1, 1]
ax4.hist(risk_df['sharpe_ratio'].dropna(), bins=15, alpha=0.7, edgecolor='black')
ax4.set_xlabel('Sharpe Ratio')
ax4.set_ylabel('Frequency')
ax4.set_title('Distribution of Sharpe Ratios')

plt.tight_layout()
plt.savefig('03_sharpe_sortino_analysis.png', dpi=300, bbox_inches='tight')
print("✓ Saved: 03_sharpe_sortino_analysis.png")
plt.close()

# ============================================================================
# STEP 5: TASK 5 - ALPHA & BETA
# ============================================================================
print("\n[STEP 5] Computing Alpha & Beta via OLS regression...")

# Create synthetic Nifty 100 returns (replace with real data in production)
np.random.seed(42)
nifty_returns = pd.Series(
    np.random.normal(0.0003, 0.012, len(daily_returns)),
    index=daily_returns.index,
    name='Nifty100'
)
nifty_returns = nifty_returns.rolling(20).mean().fillna(nifty_returns)

print(f"  Nifty 100 Annual Return: {nifty_returns.mean() * 252 * 100:.2f}%")
print(f"  Nifty 100 Annual Volatility: {nifty_returns.std() * np.sqrt(252) * 100:.2f}%")

alpha_beta_data = []

for scheme_id in daily_returns.columns:
    fund_returns = daily_returns[scheme_id].dropna()
    common_dates = fund_returns.index.intersection(nifty_returns.index)
    fund_ret_aligned = fund_returns[common_dates]
    nifty_ret_aligned = nifty_returns[common_dates]
    
    if len(fund_ret_aligned) < 30:
        continue
    
    slope, intercept, r_value, p_value, std_err = linregress(nifty_ret_aligned, fund_ret_aligned)
    
    scheme_name = scheme_df[scheme_df['scheme_id'] == scheme_id]['scheme_name'].values
    scheme_name = scheme_name[0] if len(scheme_name) > 0 else f"Scheme {scheme_id}"
    
    alpha_beta_data.append({
        'scheme_id': scheme_id,
        'scheme_name': scheme_name,
        'alpha': intercept * 252 * 100,
        'beta': slope,
        'r_squared': r_value ** 2,
        'p_value': p_value,
        'observations': len(fund_ret_aligned)
    })

alpha_beta_df = pd.DataFrame(alpha_beta_data).sort_values('alpha', ascending=False)
print(f"✓ Alpha & Beta computed for {len(alpha_beta_df)} schemes")
print("\nTop 5 by Alpha:")
print(alpha_beta_df[['scheme_name', 'alpha', 'beta', 'r_squared']].head(5).to_string(index=False))

# Plot: Alpha & Beta
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

ax1 = axes[0, 0]
top_alpha = alpha_beta_df.nlargest(10, 'alpha')
colors = ['green' if x > 0 else 'red' for x in top_alpha['alpha']]
ax1.barh(range(len(top_alpha)), top_alpha['alpha'], color=colors, alpha=0.7)
ax1.set_yticks(range(len(top_alpha)))
ax1.set_yticklabels([s[:20] for s in top_alpha['scheme_name']], fontsize=8)
ax1.set_xlabel('Alpha (%)')
ax1.set_title('Top 10 Schemes by Alpha')
ax1.axvline(0, color='black', linestyle='-', linewidth=0.8)

ax2 = axes[0, 1]
ax2.scatter(alpha_beta_df['beta'], alpha_beta_df['alpha'], s=100, alpha=0.6, 
           c=alpha_beta_df['r_squared'], cmap='RdYlGn', edgecolors='black', linewidth=0.5)
ax2.axhline(0, color='red', linestyle='--', alpha=0.5)
ax2.axvline(1, color='blue', linestyle='--', alpha=0.5)
ax2.set_xlabel('Beta')
ax2.set_ylabel('Alpha (%)')
ax2.set_title('Alpha vs Beta')
plt.colorbar(ax2.collections[0], ax=ax2, label='R²')

ax3 = axes[1, 0]
ax3.hist(alpha_beta_df['beta'], bins=15, edgecolor='black', alpha=0.7)
ax3.axvline(1.0, color='red', linestyle='--', linewidth=2, label='Beta = 1.0')
ax3.set_xlabel('Beta')
ax3.set_ylabel('Frequency')
ax3.set_title('Distribution of Beta')
ax3.legend()

ax4 = axes[1, 1]
ax4.hist(alpha_beta_df['r_squared'], bins=15, edgecolor='black', alpha=0.7)
ax4.set_xlabel('R² (Model Fit)')
ax4.set_ylabel('Frequency')
ax4.set_title('Distribution of R²')

plt.tight_layout()
plt.savefig('04_alpha_beta_analysis.png', dpi=300, bbox_inches='tight')
print("✓ Saved: 04_alpha_beta_analysis.png")
plt.close()

# ============================================================================
# STEP 6: TASK 6 - MAXIMUM DRAWDOWN
# ============================================================================
print("\n[STEP 6] Computing Maximum Drawdown...")

def compute_max_drawdown(nav_series):
    nav_series = nav_series.dropna()
    if len(nav_series) < 2:
        return np.nan, np.nan, np.nan, np.nan
    running_max = nav_series.expanding().max()
    drawdown = (nav_series / running_max) - 1
    max_dd_idx = drawdown.idxmin()
    max_dd_value = drawdown[max_dd_idx]
    peak_value = running_max[max_dd_idx]
    peak_date = nav_series[nav_series == peak_value].index[-1]
    recovery_date = np.nan
    if max_dd_idx < nav_series.index[-1]:
        post_trough = nav_series[max_dd_idx:]
        recovery_mask = post_trough >= peak_value
        if recovery_mask.any():
            recovery_date = post_trough[recovery_mask].index[0]
    return max_dd_value * 100, peak_date, max_dd_idx, recovery_date

drawdown_data = []

for scheme_id in nav_pivot.columns:
    nav_series = nav_pivot[scheme_id]
    scheme_name = scheme_df[scheme_df['scheme_id'] == scheme_id]['scheme_name'].values
    scheme_name = scheme_name[0] if len(scheme_name) > 0 else f"Scheme {scheme_id}"
    
    max_dd, peak_date, trough_date, recovery_date = compute_max_drawdown(nav_series)
    
    if pd.notna(peak_date) and pd.notna(recovery_date):
        recovery_days = (recovery_date - peak_date).days
    else:
        recovery_days = np.nan
    
    drawdown_data.append({
        'scheme_id': scheme_id,
        'scheme_name': scheme_name,
        'max_drawdown': max_dd,
        'peak_date': peak_date,
        'trough_date': trough_date,
        'recovery_date': recovery_date,
        'recovery_days': recovery_days
    })

drawdown_df = pd.DataFrame(drawdown_data).sort_values('max_drawdown', ascending=False)
print(f"✓ Drawdown computed for {len(drawdown_df)} schemes")
print("\nWorst 5 Drawdowns:")
print(drawdown_df[['scheme_name', 'max_drawdown', 'recovery_days']].head(5).to_string(index=False))

# Plot: Drawdown
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

ax1 = axes[0, 0]
worst_dd = drawdown_df.nlargest(10, 'max_drawdown')
ax1.barh(range(len(worst_dd)), worst_dd['max_drawdown'], color='darkred', alpha=0.7)
ax1.set_yticks(range(len(worst_dd)))
ax1.set_yticklabels([s[:20] for s in worst_dd['scheme_name']], fontsize=8)
ax1.set_xlabel('Maximum Drawdown (%)')
ax1.set_title('Worst 10 Schemes by Drawdown')

ax2 = axes[0, 1]
ax2.hist(drawdown_df['max_drawdown'].dropna(), bins=15, edgecolor='black', alpha=0.7)
ax2.set_xlabel('Maximum Drawdown (%)')
ax2.set_ylabel('Frequency')
ax2.set_title('Distribution of Drawdown')

ax3 = axes[1, 0]
recovery_days = drawdown_df['recovery_days'].dropna()
ax3.hist(recovery_days, bins=15, edgecolor='black', alpha=0.7)
ax3.set_xlabel('Recovery Days')
ax3.set_ylabel('Frequency')
ax3.set_title('Distribution of Recovery Periods')

ax4 = axes[1, 1]
valid_recovery = drawdown_df.dropna(subset=['max_drawdown', 'recovery_days'])
ax4.scatter(abs(valid_recovery['max_drawdown']), valid_recovery['recovery_days'], alpha=0.6, s=100)
ax4.set_xlabel('Max Drawdown Magnitude (%)')
ax4.set_ylabel('Recovery Days')
ax4.set_title('Drawdown vs Recovery Time')

plt.tight_layout()
plt.savefig('05_drawdown_analysis.png', dpi=300, bbox_inches='tight')
print("✓ Saved: 05_drawdown_analysis.png")
plt.close()

# ============================================================================
# STEP 7: TASK 7 - FUND SCORECARD
# ============================================================================
print("\n[STEP 7] Building Fund Scorecard (0-100)...")

# Merge all metrics
scorecard_base = cagr_df[['scheme_id', 'scheme_name', 'cagr_3yr']].copy()
scorecard_base = scorecard_base.merge(risk_df[['scheme_id', 'sharpe_ratio']], on='scheme_id', how='left')
scorecard_base = scorecard_base.merge(alpha_beta_df[['scheme_id', 'alpha']], on='scheme_id', how='left')
scorecard_base = scorecard_base.merge(
    scheme_df[['scheme_id', 'expense_ratio']], on='scheme_id', how='left'
)
scorecard_base = scorecard_base.merge(drawdown_df[['scheme_id', 'max_drawdown']], on='scheme_id', how='left')
scorecard_base = scorecard_base.drop_duplicates(subset=['scheme_id'])

# Percentile rankings
def percentile_rank(series, higher_is_better=True):
    valid = series.dropna()
    if len(valid) == 0:
        return pd.Series(np.nan, index=series.index)
    if higher_is_better:
        return series.rank(pct=True, method='average') * 100
    else:
        return (1 - series.rank(pct=True, method='average')) * 100

scorecard_base['rank_cagr_3yr'] = percentile_rank(scorecard_base['cagr_3yr'], higher_is_better=True)
scorecard_base['rank_sharpe'] = percentile_rank(scorecard_base['sharpe_ratio'], higher_is_better=True)
scorecard_base['rank_alpha'] = percentile_rank(scorecard_base['alpha'], higher_is_better=True)
scorecard_base['rank_expense_ratio'] = percentile_rank(scorecard_base['expense_ratio'], higher_is_better=False)
scorecard_base['rank_drawdown'] = percentile_rank(scorecard_base['max_drawdown'], higher_is_better=False)

# Composite score
scorecard_base['composite_score'] = (
    0.30 * scorecard_base['rank_cagr_3yr'].fillna(50) +
    0.25 * scorecard_base['rank_sharpe'].fillna(50) +
    0.20 * scorecard_base['rank_alpha'].fillna(50) +
    0.15 * scorecard_base['rank_expense_ratio'].fillna(50) +
    0.10 * scorecard_base['rank_drawdown'].fillna(50)
)

scorecard_final = scorecard_base.sort_values('composite_score', ascending=False)
print(f"✓ Scorecard created for {len(scorecard_final)} schemes")
print("\nTop 10 Schemes by Fund Score:")
print(scorecard_final[['scheme_name', 'composite_score', 'cagr_3yr', 'sharpe_ratio', 'alpha']].head(10).to_string(index=False))

# Plot: Scorecard
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

ax1 = axes[0, 0]
top_15 = scorecard_final.head(15)
colors_score = plt.cm.RdYlGn(top_15['composite_score'] / 100)
bars = ax1.barh(range(len(top_15)), top_15['composite_score'], color=colors_score, edgecolor='black', linewidth=0.5)
ax1.set_yticks(range(len(top_15)))
ax1.set_yticklabels([s[:20] for s in top_15['scheme_name']], fontsize=8)
ax1.set_xlabel('Composite Score (0-100)')
ax1.set_xlim(0, 100)
ax1.set_title('Top 15 Funds by Composite Score')

ax2 = axes[0, 1]
ax2.axis('off')
score_dist = scorecard_final['composite_score'].describe()
stats_text = f"""
Scorecard Statistics
Mean:     {scorecard_final['composite_score'].mean():.1f}
Median:   {scorecard_final['composite_score'].median():.1f}
Std Dev:  {scorecard_final['composite_score'].std():.1f}
Min:      {scorecard_final['composite_score'].min():.1f}
Max:      {scorecard_final['composite_score'].max():.1f}

Top 25%:  > {scorecard_final['composite_score'].quantile(0.75):.1f}
Bottom 25%: < {scorecard_final['composite_score'].quantile(0.25):.1f}
"""
ax2.text(0.1, 0.5, stats_text, fontsize=11, family='monospace', verticalalignment='center')

ax3 = axes[1, 0]
ax3.hist(scorecard_final['composite_score'].dropna(), bins=20, edgecolor='black', alpha=0.7, color='steelblue')
ax3.axvline(scorecard_final['composite_score'].mean(), color='red', linestyle='--', linewidth=2)
ax3.set_xlabel('Fund Score (0-100)')
ax3.set_ylabel('Frequency')
ax3.set_title('Distribution of Fund Scores')

ax4 = axes[1, 1]
weights_text = """
Weighting:
30% - 3Y CAGR
25% - Sharpe Ratio
20% - Alpha
15% - Expense Ratio
10% - Max Drawdown

(All converted to 
0-100 percentile rank)
"""
ax4.axis('off')
ax4.text(0.1, 0.5, weights_text, fontsize=10, family='monospace', verticalalignment='center')

plt.tight_layout()
plt.savefig('06_fund_scorecard.png', dpi=300, bbox_inches='tight')
print("✓ Saved: 06_fund_scorecard.png")
plt.close()

# ============================================================================
# STEP 8: TASK 8 - BENCHMARK COMPARISON
# ============================================================================
print("\n[STEP 8] Benchmark comparison (Top 5 vs Nifty 50/100)...")

top_5_schemes = scorecard_final.head(5)['scheme_id'].values

# Synthetic Nifty 50
nifty_50_returns = pd.Series(
    np.random.normal(0.00025, 0.011, len(daily_returns)),
    index=daily_returns.index
)
nifty_50_returns = nifty_50_returns.rolling(20).mean().fillna(nifty_50_returns)

nifty_50_cumulative = (1 + nifty_50_returns).cumprod()
nifty_100_cumulative = (1 + nifty_returns).cumprod()

# Compute tracking error
tracking_error_data = []

for scheme_id in top_5_schemes:
    scheme_name = scorecard_final[scorecard_final['scheme_id'] == scheme_id]['scheme_name'].values[0]
    fund_returns = daily_returns[scheme_id]
    
    common_dates = fund_returns.index.intersection(nifty_returns.index)
    fund_ret_aligned = fund_returns[common_dates]
    nifty_ret_aligned = nifty_returns[common_dates]
    
    tracking_diff = fund_ret_aligned - nifty_ret_aligned
    te_annual = tracking_diff.std() * np.sqrt(252) * 100
    cumulative_outperformance = tracking_diff.sum() * 252 * 100
    ir = cumulative_outperformance / te_annual if te_annual > 0 else np.nan
    
    tracking_error_data.append({
        'scheme_id': scheme_id,
        'scheme_name': scheme_name,
        'tracking_error': te_annual,
        'information_ratio': ir,
        'outperformance': cumulative_outperformance
    })

tracking_error_df = pd.DataFrame(tracking_error_data)

# Plot: Benchmark
fig, axes = plt.subplots(2, 1, figsize=(14, 10))

ax1 = axes[0]
lookback = 756
ax1.plot(nifty_50_cumulative.index[-lookback:], nifty_50_cumulative.values[-lookback:], 
        label='Nifty 50', linewidth=2.5, color='darkred', linestyle='--')
ax1.plot(nifty_100_cumulative.index[-lookback:], nifty_100_cumulative.values[-lookback:],
        label='Nifty 100', linewidth=2.5, color='darkblue', linestyle='--')

colors = plt.cm.Set1(np.linspace(0, 1, min(5, len(top_5_schemes))))
for idx, scheme_id in enumerate(top_5_schemes):
    fund_ret = daily_returns[scheme_id]
    cumulative = (1 + fund_ret).cumprod()
    scheme_name = scorecard_final[scorecard_final['scheme_id'] == scheme_id]['scheme_name'].values[0]
    relevant = cumulative[cumulative.index >= cumulative.index[-lookback]]
    ax1.plot(relevant.index, relevant.values, label=scheme_name[:25], linewidth=2, color=colors[idx])

ax1.set_xlabel('Date')
ax1.set_ylabel('Cumulative Returns')
ax1.set_title('Top 5 Funds vs Benchmarks (3-Year)')
ax1.legend(fontsize=9)
ax1.grid(True, alpha=0.3)

ax2 = axes[1]
x_pos = np.arange(len(tracking_error_df))
width = 0.35

bar1 = ax2.bar(x_pos - width/2, tracking_error_df['tracking_error'], width,
              label='Tracking Error (%)', alpha=0.7, color='steelblue')
ax2_twin = ax2.twinx()
bar2 = ax2_twin.bar(x_pos + width/2, tracking_error_df['information_ratio'], width,
                   label='Information Ratio', alpha=0.7, color='coral')

ax2.set_xlabel('Fund')
ax2.set_ylabel('Tracking Error (%)', color='steelblue')
ax2_twin.set_ylabel('Information Ratio', color='coral')
ax2.set_title('Tracking Error vs Information Ratio (Top 5)')
ax2.set_xticks(x_pos)
ax2.set_xticklabels([s[:20] for s in tracking_error_df['scheme_name']], rotation=45, ha='right', fontsize=9)
ax2.tick_params(axis='y', labelcolor='steelblue')
ax2_twin.tick_params(axis='y', labelcolor='coral')

plt.tight_layout()
plt.savefig('07_benchmark_comparison.png', dpi=300, bbox_inches='tight')
print("✓ Saved: 07_benchmark_comparison.png")
plt.close()

# ============================================================================
# STEP 9: EXPORT RESULTS TO CSV
# ============================================================================
print("\n[STEP 9] Exporting results to CSV...")

# Fund Scorecard
scorecard_export = scorecard_final[[
    'scheme_id', 'scheme_name', 'composite_score',
    'cagr_1yr', 'cagr_3yr', 'cagr_5yr',
    'sharpe_ratio', 'alpha', 'max_drawdown', 'expense_ratio'
]].copy()
scorecard_export.insert(0, 'rank', range(1, len(scorecard_export) + 1))
scorecard_export.to_csv('fund_scorecard.csv', index=False)
print(f"✓ Exported: fund_scorecard.csv ({len(scorecard_export)} schemes)")

# Alpha & Beta
alpha_beta_export = alpha_beta_df[[
    'scheme_id', 'scheme_name', 'alpha', 'beta', 'r_squared', 'observations'
]].copy()
alpha_beta_export.insert(0, 'alpha_rank', range(1, len(alpha_beta_export) + 1))
alpha_beta_export.to_csv('alpha_beta.csv', index=False)
print(f"✓ Exported: alpha_beta.csv ({len(alpha_beta_export)} schemes)")

# Risk Metrics
risk_export = risk_df[['scheme_id', 'scheme_name', 'sharpe_ratio', 'sortino_ratio',
                        'volatility', 'avg_annual_return']].copy()
risk_export = risk_export.merge(drawdown_df[['scheme_id', 'max_drawdown', 'recovery_days']], on='scheme_id', how='left')
risk_export.insert(0, 'sharpe_rank', range(1, len(risk_export) + 1))
risk_export.to_csv('risk_metrics.csv', index=False)
print(f"✓ Exported: risk_metrics.csv ({len(risk_export)} schemes)")

# Summary Statistics
summary_stats = pd.DataFrame({
    'Metric': [
        'Number of Schemes',
        'Avg 3Y CAGR (%)',
        'Avg Sharpe Ratio',
        'Avg Sortino Ratio',
        'Avg Alpha (%)',
        'Avg Beta',
        'Avg Volatility (%)',
        'Avg Max Drawdown (%)',
        'Avg Fund Score'
    ],
    'Value': [
        len(scorecard_export),
        f"{cagr_df['cagr_3yr'].mean():.2f}",
        f"{risk_df['sharpe_ratio'].mean():.3f}",
        f"{risk_df['sortino_ratio'].mean():.3f}",
        f"{alpha_beta_df['alpha'].mean():.2f}",
        f"{alpha_beta_df['beta'].mean():.3f}",
        f"{risk_df['volatility'].mean():.2f}",
        f"{drawdown_df['max_drawdown'].mean():.2f}",
        f"{scorecard_final['composite_score'].mean():.1f}"
    ]
})
summary_stats.to_csv('performance_summary.csv', index=False)
print(f"✓ Exported: performance_summary.csv")

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "="*70)
print("ALL ANALYTICS COMPLETE ✓")
print("="*70)
print(f"""
DELIVERABLES GENERATED:
  ✓ fund_scorecard.csv (ranked by composite score)
  ✓ alpha_beta.csv (OLS regression results)
  ✓ risk_metrics.csv (Sharpe, Sortino, Drawdown)
  ✓ performance_summary.csv (aggregate statistics)
  ✓ 7 PNG charts (01-07_*.png)

TOP 3 FUNDS BY COMPOSITE SCORE:
""")
for i, (_, row) in enumerate(scorecard_final.head(3).iterrows(), 1):
    print(f"  {i}. {row['scheme_name'][:40]:<40} Score: {row['composite_score']:>6.1f}")

print(f"""
QUICK STATS:
  • Average 3Y CAGR: {cagr_df['cagr_3yr'].mean():.2f}%
  • Average Sharpe Ratio: {risk_df['sharpe_ratio'].mean():.3f}
  • Average Max Drawdown: {drawdown_df['max_drawdown'].mean():.2f}%
  • Average Fund Score: {scorecard_final['composite_score'].mean():.1f}/100
  
NEXT: Review CSVs in Excel or Pandas, check PNG visualizations
""")
print("="*70)
