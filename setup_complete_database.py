"""
Complete Database Setup for Bluestock Fintech Capstone
Creates entire star schema: Facts + Dimensions
"""

import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = r'C:\Users\vasanth\OneDrive\Desktop\bluestock_mf_project\bluestock_mf.db'

print("=" * 70)
print("BUILDING BLUESTOCK FINTECH DATABASE")
print("=" * 70)
print()

# Connect to database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print(f"📁 Database: {DB_PATH}")
print()

# =====================================================================
# DIMENSION TABLES
# =====================================================================

print("🔨 Creating dimension tables...")
print()

# 1. FUND DIMENSION
create_funds_table = """
CREATE TABLE IF NOT EXISTS funds (
    fund_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_name TEXT UNIQUE NOT NULL,
    fund_category TEXT,
    asset_class TEXT,
    fund_manager TEXT,
    aum REAL,
    launch_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
cursor.execute(create_funds_table)
print("   ✅ funds table created")

# 2. DATE DIMENSION
create_date_table = """
CREATE TABLE IF NOT EXISTS dates (
    date_id INTEGER PRIMARY KEY,
    date DATE UNIQUE NOT NULL,
    year INTEGER,
    month INTEGER,
    day INTEGER,
    quarter INTEGER,
    day_of_week TEXT,
    is_trading_day BOOLEAN
);
"""
cursor.execute(create_date_table)
print("   ✅ dates table created")

# 3. FUND CATEGORY DIMENSION
create_category_table = """
CREATE TABLE IF NOT EXISTS fund_categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT UNIQUE NOT NULL,
    risk_level TEXT,
    description TEXT
);
"""
cursor.execute(create_category_table)
print("   ✅ fund_categories table created")

# 4. ASSET CLASS DIMENSION
create_asset_table = """
CREATE TABLE IF NOT EXISTS asset_classes (
    asset_class_id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_class_name TEXT UNIQUE NOT NULL,
    description TEXT
);
"""
cursor.execute(create_asset_table)
print("   ✅ asset_classes table created")

# =====================================================================
# FACT TABLES
# =====================================================================

print()
print("🔨 Creating fact tables...")
print()

# 1. NAV FACT TABLE (Daily NAV values)
create_nav_table = """
CREATE TABLE IF NOT EXISTS fund_nav (
    nav_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_id INTEGER NOT NULL,
    date_id INTEGER NOT NULL,
    nav_value REAL NOT NULL,
    nav_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(fund_id) REFERENCES funds(fund_id),
    FOREIGN KEY(date_id) REFERENCES dates(date_id),
    UNIQUE(fund_id, nav_date)
);
"""
cursor.execute(create_nav_table)
print("   ✅ fund_nav (fact) table created")

# 2. PERFORMANCE METRICS FACT TABLE
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(fund_id) REFERENCES funds(fund_id)
);
"""
cursor.execute(create_perf_table)
print("   ✅ fund_performance (fact) table created")

# 3. RETURN METRICS FACT TABLE
create_returns_table = """
CREATE TABLE IF NOT EXISTS fund_returns (
    return_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_id INTEGER NOT NULL,
    date_id INTEGER NOT NULL,
    return_date DATE NOT NULL,
    daily_return REAL,
    weekly_return REAL,
    monthly_return REAL,
    ytd_return REAL,
    one_year_return REAL,
    three_year_return REAL,
    five_year_return REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(fund_id) REFERENCES funds(fund_id),
    FOREIGN KEY(date_id) REFERENCES dates(date_id),
    UNIQUE(fund_id, return_date)
);
"""
cursor.execute(create_returns_table)
print("   ✅ fund_returns (fact) table created")

# 4. HOLDINGS FACT TABLE
create_holdings_table = """
CREATE TABLE IF NOT EXISTS fund_holdings (
    holding_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_id INTEGER NOT NULL,
    holding_date DATE NOT NULL,
    instrument_name TEXT,
    instrument_type TEXT,
    quantity REAL,
    market_value REAL,
    percentage_of_aum REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(fund_id) REFERENCES funds(fund_id),
    UNIQUE(fund_id, holding_date, instrument_name)
);
"""
cursor.execute(create_holdings_table)
print("   ✅ fund_holdings (fact) table created")

conn.commit()

# =====================================================================
# INSERT SAMPLE DATA
# =====================================================================

print()
print("📊 Inserting sample data...")
print()

# Sample funds
funds_data = [
    ("HDFC Mid-Cap Opportunities", "Mid-Cap", "Equity", "HDFC", 5000.0),
    ("Axis Bluechip Fund", "Large-Cap", "Equity", "Axis", 4500.0),
    ("Kotak Standard Multicap Fund", "Multi-Cap", "Equity", "Kotak", 3800.0),
    ("ICICI Pru Bluechip Fund", "Large-Cap", "Equity", "ICICI Prudential", 4200.0),
    ("Mirae Asset Large Cap Fund", "Large-Cap", "Equity", "Mirae Asset", 3200.0),
    ("SBI Bluechip Fund", "Large-Cap", "Equity", "SBI", 4800.0),
    ("Nippon India Small Cap Fund", "Small-Cap", "Equity", "Nippon India", 2500.0),
    ("Axis Midcap Fund", "Mid-Cap", "Equity", "Axis", 3100.0),
    ("Franklin India Smallcap Fund", "Small-Cap", "Equity", "Franklin Templeton", 2800.0),
    ("Motilal Oswal Multicap 35 Fund", "Multi-Cap", "Equity", "Motilal Oswal", 1500.0),
    ("HDFC Hybrid Debt Fund", "Hybrid", "Mixed", "HDFC", 2200.0),
    ("ICICI Pru Conservative Hybrid Fund", "Hybrid", "Mixed", "ICICI Prudential", 1800.0),
    ("Axis Equity Hybrid Fund", "Hybrid", "Mixed", "Axis", 1600.0),
    ("Kotak Equity Hybrid Fund", "Hybrid", "Mixed", "Kotak", 1400.0),
    ("SBI Equity Hybrid Fund", "Hybrid", "Mixed", "SBI", 1300.0),
    ("Aditya Birla SL Equity Hybrid Fund", "Hybrid", "Mixed", "Aditya Birla", 1100.0),
    ("HDFC Liquid Fund", "Liquid", "Debt", "HDFC", 8000.0),
    ("ICICI Pru Liquid Fund", "Liquid", "Debt", "ICICI Prudential", 7500.0),
    ("Axis Liquid Fund", "Liquid", "Debt", "Axis", 6800.0),
    ("Kotak Liquid Fund", "Liquid", "Debt", "Kotak", 7200.0),
    ("SBI Liquid Fund", "Liquid", "Debt", "SBI", 6500.0),
    ("Motilal Oswal Liquid Fund", "Liquid", "Debt", "Motilal Oswal", 5800.0),
    ("HDFC Balanced Advantage Fund", "Balanced", "Mixed", "HDFC", 3500.0),
    ("Nippon India Growth Fund", "Growth", "Equity", "Nippon India", 2100.0),
    ("Franklin India Value Fund", "Value", "Equity", "Franklin Templeton", 1900.0),
    ("Kotak Emerging Opportunities Fund", "Emerging", "Equity", "Kotak", 1700.0),
    ("ICICI Pru Emerging Bluechip Fund", "Emerging", "Equity", "ICICI Prudential", 2000.0),
    ("Axis Focused 25 Fund", "Focused", "Equity", "Axis", 1400.0),
    ("SBI Growth Fund", "Growth", "Equity", "SBI", 1200.0),
    ("Motilal Oswal Large Cap Fund", "Large-Cap", "Equity", "Motilal Oswal", 2800.0),
    ("Aditya Birla SL Growth Fund", "Growth", "Equity", "Aditya Birla", 1600.0),
    ("ICICI Pru Smallcap Fund", "Small-Cap", "Equity", "ICICI Prudential", 2300.0),
]

insert_fund_query = """
INSERT OR IGNORE INTO funds (fund_name, fund_category, asset_class, fund_manager, aum)
VALUES (?, ?, ?, ?, ?)
"""

for fund in funds_data:
    cursor.execute(insert_fund_query, fund)

conn.commit()
print(f"   ✅ Inserted {len(funds_data)} funds")

# =====================================================================
# VERIFY DATA
# =====================================================================

print()
print("=" * 70)
print("DATABASE VERIFICATION")
print("=" * 70)
print()

tables = [
    'funds', 'dates', 'fund_categories', 'asset_classes',
    'fund_nav', 'fund_performance', 'fund_returns', 'fund_holdings'
]

for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"   {table:<25} {count:>5} records")

print()

# Show sample funds
print("🏦 Sample Funds in Database:")
print()

result = cursor.execute("""
SELECT fund_id, fund_name, fund_category, asset_class, aum
FROM funds
LIMIT 10
""").fetchall()

print(f"{'ID':<5} {'Fund Name':<35} {'Category':<12} {'Asset':<8} {'AUM':<10}")
print("-" * 75)

for row in result:
    fund_id, name, category, asset, aum = row
    print(f"{fund_id:<5} {name:<35} {category:<12} {asset:<8} {aum:>8.0f}Cr")

print()

conn.close()

print("=" * 70)
print("✅ DATABASE SETUP COMPLETE!")
print("=" * 70)
print()
print("📋 Ready for next steps:")
print("   1. Run performance analytics script")
print("   2. Populate fund_nav with historical data")
print("   3. Calculate performance metrics")
print()
print("💾 Database location:")
print(f"   {DB_PATH}")
print()
