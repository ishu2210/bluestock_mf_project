# Mutual Fund Analytics Database - Data Dictionary

**Generated:** 2026-06-24  
**Database:** bluestock_mf.db  
**Version:** 1.0

---

## Table of Contents

1. [Overview](#overview)
2. [Dimension Tables](#dimension-tables)
3. [Fact Tables](#fact-tables)
4. [Data Quality Standards](#data-quality-standards)
5. [Business Definitions](#business-definitions)

---

## Overview

This SQLite database implements a **star schema** for mutual fund analytics. It consolidates data from three source datasets:
- **nav_history.csv** → `fact_nav` + `dim_fund` + `dim_date`
- **investor_transactions.csv** → `fact_transaction` + `dim_investor` + `dim_date`
- **scheme_performance.csv** → `fact_performance` + `dim_fund`

### Schema Diagram
```
dim_fund ───┬─── fact_nav
            ├─── fact_transaction
            └─── fact_performance

dim_date ───┬─── fact_nav
            └─── fact_transaction

dim_investor ────── fact_transaction
```

---

## Dimension Tables

### dim_fund
**Purpose:** Master dimension for mutual fund schemes  
**Primary Key:** `fund_id` (auto-increment)  
**Business Key:** `amfi_code` (AMFI registration code)

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| fund_id | INTEGER | NO | Unique fund identifier (PK) |
| amfi_code | STRING(50) | NO | AMFI scheme registration code (UNIQUE, INDEX) |
| scheme_name | STRING(255) | NO | Official mutual fund scheme name |
| created_at | DATETIME | NO | Record creation timestamp |

**Sample Data:**
```
fund_id | amfi_code        | scheme_name
--------|------------------|-------------------------------------
1       | INF090K01CH7     | Axis Bluechip Fund
2       | INF129G01CH8     | HDFC Top 100 Fund
3       | INF740U01CH9     | ICICI Prudential Growth Fund
```

**Business Rules:**
- One fund per AMFI code
- Scheme names are immutable (reference data)
- AMFI codes are the authoritative identifier

---

### dim_date
**Purpose:** Conformed date dimension for time-based analytics  
**Primary Key:** `date_id` (auto-increment)  
**Business Key:** `date` (calendar date)

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| date_id | INTEGER | NO | Unique date identifier (PK) |
| date | DATETIME | NO | Calendar date (UNIQUE, INDEX) |
| year | INTEGER | NO | Calendar year (e.g., 2024) |
| month | INTEGER | NO | Month of year (1-12) |
| day | INTEGER | NO | Day of month (1-31) |
| quarter | INTEGER | NO | Quarter (1-4) |
| day_of_week | INTEGER | NO | Day of week (0=Monday, 6=Sunday) |
| day_name | STRING(10) | NO | Day name (Monday, Tuesday, etc.) |
| is_weekend | BOOLEAN | NO | Weekend flag (TRUE if Saturday/Sunday) |

**Sample Data:**
```
date_id | date       | year | month | day | quarter | day_of_week | day_name | is_weekend
--------|------------|------|-------|-----|---------|-------------|----------|----------
1       | 2023-01-02 | 2023 | 1     | 2   | 1       | 0           | Monday   | FALSE
2       | 2023-01-03 | 2023 | 1     | 3   | 1       | 1           | Tuesday  | FALSE
```

**Business Rules:**
- Only trading days (Mon-Fri) for Indian markets
- Weekends flagged but included for completeness
- Facilitates month/quarter/year rollups

---

### dim_investor
**Purpose:** Investor master dimension with compliance metadata  
**Primary Key:** `investor_id_pkey` (auto-increment)  
**Business Key:** `investor_id` (client ID)

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| investor_id_pkey | INTEGER | NO | Unique investor identifier (PK) |
| investor_id | STRING(50) | NO | Client investor ID (UNIQUE, INDEX) |
| state | STRING(100) | YES | Investor's state (e.g., TamilNadu) |
| kyc_status | STRING(50) | YES | KYC approval status |
| created_at | DATETIME | NO | Record creation timestamp |

**Sample Data:**
```
investor_id_pkey | investor_id | state      | kyc_status
-----------------|-------------|------------|---------------
1                | INV000001   | TamilNadu  | KYC_Approved
2                | INV000002   | Karnataka  | KYC_Pending
```

**Valid kyc_status Values:**
- `KYC_Approved` — Investor cleared for transactions
- `KYC_Pending` — Awaiting KYC verification

**Business Rules:**
- One investor per client ID
- KYC status affects transaction eligibility
- State used for regional analytics

---

## Fact Tables

### fact_nav
**Purpose:** Net Asset Value (NAV) time series for funds  
**Primary Key:** `nav_id` (auto-increment)  
**Unique Key:** `(fund_id, date_id)`  
**Grain:** One row per fund per trading day

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| nav_id | INTEGER | NO | Unique NAV record (PK) |
| fund_id | INTEGER | NO | Foreign key to dim_fund (INDEX) |
| date_id | INTEGER | NO | Foreign key to dim_date (INDEX) |
| nav_value | FLOAT | NO | Net Asset Value per unit (₹) |
| aum_crores | FLOAT | YES | Assets Under Management (₹ crores) |

**Sample Data:**
```
nav_id | fund_id | date_id | nav_value | aum_crores
-------|---------|---------|-----------|----------
1      | 1       | 100     | 28.45     | 2500.50
2      | 1       | 101     | 28.67     | 2510.25
```

**Source:** nav_history.csv (cleaned)

**Data Quality Standards:**
- NAV values validated > 0
- NAV rounded to 4 decimal places
- Missing NAV forward-filled (for weekends/holidays)
- No duplicates: unique per (fund, date)
- Dates parsed to DATETIME type

**Business Rules:**
- NAV fluctuates daily based on portfolio valuation
- Forward-filled values represent holiday closures
- AUM represents total fund size at NAV date

---

### fact_transaction
**Purpose:** Investor transactions (purchases, SIPs, redemptions)  
**Primary Key:** `transaction_id` (auto-increment)  
**Grain:** One row per investor transaction

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| transaction_id | INTEGER | NO | Unique transaction (PK) |
| fund_id | INTEGER | NO | Foreign key to dim_fund (INDEX) |
| investor_id_fk | INTEGER | NO | Foreign key to dim_investor (INDEX) |
| date_id | INTEGER | NO | Foreign key to dim_date (INDEX) |
| transaction_type | STRING(50) | NO | Type: SIP, Lumpsum, Redemption |
| amount | FLOAT | NO | Transaction amount (₹, >0) |
| units | FLOAT | NO | Number of units transacted |

**Sample Data:**
```
transaction_id | fund_id | investor_id_fk | date_id | transaction_type | amount   | units
---------------|---------|----------------|---------|------------------|----------|-------
1              | 1       | 5              | 150     | SIP              | 10000.00 | 350.25
2              | 2       | 5              | 150     | Lumpsum          | 50000.00 | 1750.00
```

**Source:** investor_transactions.csv (cleaned)

**Valid transaction_type Values:**
- `SIP` — Systematic Investment Plan (recurring)
- `Lumpsum` — One-time investment
- `Redemption` — Withdrawal/redemption

**Data Quality Standards:**
- Amount validated > 0
- Transaction types standardized and trimmed
- Dates parsed to DATETIME
- Units rounded to 2 decimal places
- Only KYC_Approved investors included in final dataset
- ⚠ ~544 rows removed for failing validation (invalid amounts, kyc status)

**Business Rules:**
- SIPs are recurring monthly contributions
- Lumpsums are one-time investments
- Redemptions represent exit from fund
- Amount must match NAV × units at transaction date

---

### fact_performance
**Purpose:** Annual fund performance metrics and risk statistics  
**Primary Key:** `performance_id` (auto-increment)  
**Unique Key:** `(fund_id, fund_year)`  
**Grain:** One row per fund per year

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| performance_id | INTEGER | NO | Unique performance record (PK) |
| fund_id | INTEGER | NO | Foreign key to dim_fund (INDEX) |
| fund_year | INTEGER | NO | Calendar year (e.g., 2024) |
| return_1y_pct | FLOAT | YES | 1-year annualized return (%) |
| return_3y_pct | FLOAT | YES | 3-year annualized return (%) |
| return_5y_pct | FLOAT | YES | 5-year annualized return (%) |
| expense_ratio_pct | FLOAT | YES | Annual expense ratio (%) |
| expense_ratio_valid | BOOLEAN | NO | TRUE if expense_ratio in [0.1%, 2.5%] |
| aum_crores | FLOAT | YES | Assets Under Management (₹ crores) |

**Sample Data:**
```
performance_id | fund_id | fund_year | return_1y_pct | return_3y_pct | expense_ratio_pct | expense_ratio_valid
---------------|---------|-----------|---------------|---------------|-------------------|-------------------
1              | 1       | 2023      | 21.37         | 15.45         | 0.27              | TRUE
2              | 1       | 2024      | 6.86          | 14.23         | 0.28              | TRUE
```

**Source:** scheme_performance.csv (cleaned)

**Data Quality Standards:**
- Returns validated as numeric (-∞ to +∞, but flagged if >±50%)
- Expense ratio range: **0.1% – 2.5%** (SEBI guidelines)
  - Values outside range flagged in `expense_ratio_valid = FALSE`
  - Outliers retained for analysis; not removed
- All percentages rounded to 2 decimal places
- Numeric conversion errors removed (2 rows)
- Final count: 22 rows (from 24 source)

**Business Rules:**
- Returns are annualized percentages
- Expense ratio is annual cost as % of AUM
- Lower expense ratio = better for investors (lower fees)
- ⚠ Some funds flagged as having unusual returns (>50% or <-50%)

---

## Data Quality Standards

### Validation Rules Applied During Cleaning

**nav_history.csv → fact_nav:**
- ✓ Dates parsed to DATETIME (3,100 → 3,100 rows)
- ✓ NAV values forward-filled for missing holidays (2,888 missing → 0 missing)
- ✓ Negative/zero NAV removed (814 rows removed)
- ✓ Duplicates removed by (amfi_code, nav_date) (17 duplicates removed)
- ✓ **Final: 2,269 valid rows**

**investor_transactions.csv → fact_transaction:**
- ✓ Dates parsed to DATETIME (2,000 → 2,000 rows)
- ✓ Transaction types standardized (SIP, Lumpsum, Redemption)
- ✓ Invalid amounts ≤ 0 removed (104 rows)
- ✓ KYC status standardized & validated
- ✓ **Final: 1,896 rows passed validation; 1,352 loaded** 
  - (Some investors have no valid transactions)

**scheme_performance.csv → fact_performance:**
- ✓ Return values validated as numeric (2 non-numeric removed)
- ✓ Expense ratio range validated (0.1% – 2.5%)
  - 0 rows removed; 0 rows flagged as out-of-range
- ✓ Anomalies detected (returns >±50%) but retained with flag
- ✓ **Final: 22 valid rows**

### Missing Data Handling
- **NAV:** Forward-filled (market closure, holidays)
- **AUM:** Retained as-is if missing; nullable in schema
- **Performance Returns:** Nullable (some funds have incomplete history)
- **KYC Status:** Standardized; blanks converted to enum value

---

## Business Definitions

### Key Metrics

**Net Asset Value (NAV)**  
- Price per unit of a mutual fund
- Calculated as: Total Fund Value / Total Units Outstanding
- Unit: Indian Rupees (₹)
- Updated daily by AMC (Asset Management Company)

**Assets Under Management (AUM)**  
- Total market value of assets managed by fund
- Unit: Crores of Rupees (₹ crores = ₹10 million)
- Indicator of fund size and investor confidence

**Expense Ratio**  
- Annual cost of operating the fund
- Unit: Percentage of AUM (e.g., 0.75% = 75 basis points)
- SEBI guideline: 0.1% – 2.5% for equity mutual funds
- Lower is better (more of investor money stays invested)

**Annualized Return**  
- Compound annual growth rate (CAGR) over period
- Unit: Percentage (%)
- Periods: 1-year, 3-year, 5-year
- Comparison basis: benchmark indices (Nifty 50, Sensex, etc.)

**SIP (Systematic Investment Plan)**  
- Recurring investment (typically monthly)
- Amount fixed; units purchased at monthly NAV
- Benefits from rupee-cost averaging
- Lower entry barrier for retail investors

**Lumpsum Investment**  
- One-time, large investment
- All amount invested at single NAV
- Higher risk but can yield returns if NAV appreciates

**Redemption**  
- Withdrawal / sale of units
- Units converted back to cash at redemption NAV
- May incur exit load (fee) if within lock-in period

**KYC (Know Your Customer)**  
- Regulatory compliance: investor verification
- Statuses: `KYC_Approved`, `KYC_Pending`
- Required before trading; protects against financial crime

---

## Relationships & Constraints

### Foreign Keys
1. `fact_nav.fund_id` → `dim_fund.fund_id`
2. `fact_nav.date_id` → `dim_date.date_id`
3. `fact_transaction.fund_id` → `dim_fund.fund_id`
4. `fact_transaction.investor_id_fk` → `dim_investor.investor_id_pkey`
5. `fact_transaction.date_id` → `dim_date.date_id`
6. `fact_performance.fund_id` → `dim_fund.fund_id`

### Unique Constraints
1. `fact_nav(fund_id, date_id)` — One NAV per fund per day
2. `fact_performance(fund_id, fund_year)` — One performance record per fund per year
3. `dim_fund(amfi_code)` — One fund per AMFI code
4. `dim_date(date)` — One date per calendar day
5. `dim_investor(investor_id)` — One investor per client ID

---

## Sample Analytical Queries

See `queries.sql` for 10 production-ready queries:

1. **Top 5 Funds by AUM** — Identify largest funds
2. **Average NAV per Month** — Track monthly performance
3. **Transaction Type Analysis** — SIP vs Lumpsum vs Redemption breakdown
4. **SIP YoY Growth** — Year-over-year recurring investment trends
5. **Top States by Investment** — Geographic revenue concentration
6. **Low-Cost Funds** — Funds with expense_ratio < 1%
7. **Fund Performance Ranking** — 1-year return rankings
8. **KYC Status Distribution** — Compliance analysis
9. **Monthly Transaction Trends** — Time series of transaction volumes
10. **Top Investors** — High-value investor portfolio analysis

---

## Dataset Statistics

| Metric | Value |
|--------|-------|
| Date Range | 2023-01-02 to 2024-06-23 |
| Number of Funds | 8 |
| Number of Investors | 100 |
| Number of Trading Days | 385 |
| Total NAV Records | 2,269 |
| Total Transactions | 1,352 |
| Total Investment (₹) | ₹285.4 crores |
| Avg Transaction Size (₹) | ₹211,000 |
| Data Freshness | 2026-06-24 |

---

## Related Files

- **schema.sql** — Complete CREATE TABLE statements
- **queries.sql** — 10 analytical SQL queries
- **data_cleaning.log** — Detailed cleaning audit trail
- **data_cleaning_report.txt** — Validation summary

---

**Prepared by:** Bluestock Fintech Analytics Team  
**Database Version:** 1.0  
**Last Updated:** 2026-06-24
