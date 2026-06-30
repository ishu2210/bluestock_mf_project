-- Mutual Fund Analytics: 10 Key Queries
-- Generated: 2026-06-24T04:03:39.971824

-- Q1: Top 5 Funds by Latest AUM

SELECT 
    df.scheme_name,
    df.amfi_code,
    MAX(fn.aum_crores) as latest_aum_crores,
    COUNT(fn.nav_id) as num_nav_records
FROM fact_nav fn
JOIN dim_fund df ON fn.fund_id = df.fund_id
GROUP BY fn.fund_id
ORDER BY latest_aum_crores DESC
LIMIT 5;


-- Q2: Average NAV per Month (2024)

SELECT 
    df.scheme_name,
    dd.year,
    dd.month,
    ROUND(AVG(fn.nav_value), 2) as avg_nav,
    COUNT(fn.nav_id) as num_observations
FROM fact_nav fn
JOIN dim_fund df ON fn.fund_id = df.fund_id
JOIN dim_date dd ON fn.date_id = dd.date_id
WHERE dd.year = 2024
GROUP BY fn.fund_id, dd.year, dd.month
ORDER BY dd.year, dd.month, df.scheme_name;


-- Q3: Transaction Type Analysis

SELECT 
    ft.transaction_type,
    COUNT(ft.transaction_id) as transaction_count,
    SUM(ft.amount) as total_amount,
    ROUND(AVG(ft.amount), 2) as avg_transaction_amount,
    COUNT(DISTINCT ft.investor_id_fk) as unique_investors
FROM fact_transaction ft
GROUP BY ft.transaction_type
ORDER BY transaction_count DESC;


-- Q4: SIP Growth YoY

SELECT 
    dd.year,
    COUNT(ft.transaction_id) as sip_count,
    SUM(ft.amount) as total_sip_amount,
    COUNT(DISTINCT ft.investor_id_fk) as unique_sip_investors
FROM fact_transaction ft
JOIN dim_date dd ON ft.date_id = dd.date_id
WHERE ft.transaction_type = 'SIP'
GROUP BY dd.year
ORDER BY dd.year;


-- Q5: Top States by Investment

SELECT 
    di.state,
    COUNT(ft.transaction_id) as transaction_count,
    SUM(ft.amount) as total_investment,
    COUNT(DISTINCT ft.investor_id_fk) as unique_investors,
    ROUND(AVG(ft.amount), 2) as avg_investment
FROM fact_transaction ft
JOIN dim_investor di ON ft.investor_id_fk = di.investor_id_pkey
GROUP BY di.state
ORDER BY total_investment DESC
LIMIT 10;


-- Q6: Low-Cost Funds (< 1%)

SELECT 
    df.scheme_name,
    df.amfi_code,
    fp.fund_year,
    ROUND(fp.expense_ratio_pct, 2) as expense_ratio,
    ROUND(fp.return_1y_pct, 2) as return_1y,
    ROUND(fp.return_3y_pct, 2) as return_3y,
    ROUND(fp.aum_crores, 0) as aum_crores
FROM fact_performance fp
JOIN dim_fund df ON fp.fund_id = df.fund_id
WHERE fp.expense_ratio_pct < 1.0
ORDER BY fp.expense_ratio_pct ASC, fp.fund_year DESC;


-- Q7: Fund Performance Ranking

SELECT 
    df.scheme_name,
    fp.fund_year,
    ROUND(fp.return_1y_pct, 2) as return_1y_pct,
    ROUND(fp.return_3y_pct, 2) as return_3y_pct,
    ROUND(fp.return_5y_pct, 2) as return_5y_pct,
    ROUND(fp.expense_ratio_pct, 2) as expense_ratio,
    RANK() OVER (PARTITION BY fp.fund_year ORDER BY fp.return_1y_pct DESC) as rank_1y
FROM fact_performance fp
JOIN dim_fund df ON fp.fund_id = df.fund_id
WHERE fp.fund_year = 2024
ORDER BY rank_1y;


-- Q8: KYC Status Distribution

SELECT 
    di.kyc_status,
    COUNT(DISTINCT di.investor_id_pkey) as investor_count,
    COUNT(ft.transaction_id) as transaction_count,
    SUM(ft.amount) as total_investment,
    ROUND(AVG(ft.amount), 2) as avg_investment
FROM dim_investor di
LEFT JOIN fact_transaction ft ON di.investor_id_pkey = ft.investor_id_fk
GROUP BY di.kyc_status
ORDER BY investor_count DESC;


-- Q9: Monthly Transaction Trends

SELECT 
    dd.year,
    dd.month,
    ft.transaction_type,
    COUNT(ft.transaction_id) as transaction_count,
    SUM(ft.amount) as total_amount,
    COUNT(DISTINCT ft.investor_id_fk) as unique_investors
FROM fact_transaction ft
JOIN dim_date dd ON ft.date_id = dd.date_id
WHERE dd.year >= 2023
GROUP BY dd.year, dd.month, ft.transaction_type
ORDER BY dd.year DESC, dd.month DESC, ft.transaction_type;


-- Q10: Top 10 Investors

SELECT 
    di.investor_id,
    COUNT(DISTINCT ft.fund_id) as num_funds,
    COUNT(ft.transaction_id) as num_transactions,
    SUM(ft.amount) as total_invested,
    SUM(ft.units) as total_units,
    ROUND(AVG(ft.amount), 2) as avg_transaction_size
FROM dim_investor di
JOIN fact_transaction ft ON di.investor_id_pkey = ft.investor_id_fk
GROUP BY di.investor_id
ORDER BY total_invested DESC
LIMIT 10;


