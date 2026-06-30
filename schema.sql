-- SQLite Schema: Mutual Fund Analytics Database
-- Generated: 2026-06-24T04:03:15.411241

CREATE TABLE dim_fund (
	fund_id INTEGER NOT NULL, 
	amfi_code VARCHAR(50) NOT NULL, 
	scheme_name VARCHAR(255) NOT NULL, 
	created_at DATETIME, 
	PRIMARY KEY (fund_id)
);

CREATE TABLE dim_date (
	date_id INTEGER NOT NULL, 
	date DATETIME NOT NULL, 
	year INTEGER NOT NULL, 
	month INTEGER NOT NULL, 
	day INTEGER NOT NULL, 
	quarter INTEGER NOT NULL, 
	day_of_week INTEGER NOT NULL, 
	day_name VARCHAR(10) NOT NULL, 
	is_weekend BOOLEAN NOT NULL, 
	PRIMARY KEY (date_id)
);

CREATE TABLE dim_investor (
	investor_id_pkey INTEGER NOT NULL, 
	investor_id VARCHAR(50) NOT NULL, 
	state VARCHAR(100), 
	kyc_status VARCHAR(50), 
	created_at DATETIME, 
	PRIMARY KEY (investor_id_pkey)
);

CREATE TABLE fact_nav (
	nav_id INTEGER NOT NULL, 
	fund_id INTEGER NOT NULL, 
	date_id INTEGER NOT NULL, 
	nav_value FLOAT NOT NULL, 
	aum_crores FLOAT, 
	PRIMARY KEY (nav_id), 
	CONSTRAINT uq_nav_fund_date UNIQUE (fund_id, date_id), 
	FOREIGN KEY(fund_id) REFERENCES dim_fund (fund_id), 
	FOREIGN KEY(date_id) REFERENCES dim_date (date_id)
);

CREATE TABLE fact_transaction (
	transaction_id INTEGER NOT NULL, 
	fund_id INTEGER NOT NULL, 
	investor_id_fk INTEGER NOT NULL, 
	date_id INTEGER NOT NULL, 
	transaction_type VARCHAR(50) NOT NULL, 
	amount FLOAT NOT NULL, 
	units FLOAT NOT NULL, 
	PRIMARY KEY (transaction_id), 
	FOREIGN KEY(fund_id) REFERENCES dim_fund (fund_id), 
	FOREIGN KEY(investor_id_fk) REFERENCES dim_investor (investor_id_pkey), 
	FOREIGN KEY(date_id) REFERENCES dim_date (date_id)
);

CREATE TABLE fact_performance (
	performance_id INTEGER NOT NULL, 
	fund_id INTEGER NOT NULL, 
	fund_year INTEGER NOT NULL, 
	return_1y_pct FLOAT, 
	return_3y_pct FLOAT, 
	return_5y_pct FLOAT, 
	expense_ratio_pct FLOAT, 
	expense_ratio_valid BOOLEAN, 
	aum_crores FLOAT, 
	PRIMARY KEY (performance_id), 
	CONSTRAINT uq_performance_fund_year UNIQUE (fund_id, fund_year), 
	FOREIGN KEY(fund_id) REFERENCES dim_fund (fund_id)
);

