import requests
import pandas as pd
import os
from datetime import datetime

# API endpoint
API_BASE = "https://api.mfapi.in/mf/"

# Scheme codes to fetch
schemes = {
    "125497": "HDFC Top 100 Direct",
    "119551": "SBI Bluechip",
    "120503": "ICICI Bluechip",
    "118632": "Nippon Large Cap",
    "119092": "Axis Bluechip",
    "120841": "Kotak Bluechip"
}

print("=" * 80)
print("LIVE NAV FETCHING FROM MFAPI.IN")
print("=" * 80)

nav_data = []

for code, name in schemes.items():
    url = f"{API_BASE}{code}"
    
    try:
        print(f"\n📊 Fetching: {name} (Code: {code})")
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Extract latest NAV
        if "data" in data and len(data["data"]) > 0:
            latest = data["data"][0]
            nav_data.append({
                "Scheme Code": code,
                "Scheme Name": name,
                "NAV": latest.get("nav"),
                "Date": latest.get("date"),
                "Status": "✅ Success"
            })
            print(f"   NAV: {latest.get('nav')}")
            print(f"   Date: {latest.get('date')}")
        else:
            nav_data.append({
                "Scheme Code": code,
                "Scheme Name": name,
                "NAV": None,
                "Date": None,
                "Status": "⚠️ No data"
            })
            print("   ⚠️ No NAV data available")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error: {str(e)}")
        nav_data.append({
            "Scheme Code": code,
            "Scheme Name": name,
            "NAV": None,
            "Date": None,
            "Status": f"❌ Error: {str(e)}"
        })

# Save to CSV
output_path = "data/raw/live_nav.csv"
df = pd.DataFrame(nav_data)
df.to_csv(output_path, index=False)

print("\n" + "=" * 80)
print(f"✅ Live NAV saved to: {output_path}")
print("=" * 80)
print(df.to_string(index=False))