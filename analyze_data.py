"""
analyze_data.py — Cleans, enriches, and analyses the raw sales dataset.

Steps:
  1. Load raw CSV
  2. Drop exact duplicates
  3. Fill / flag missing values
  4. Compute derived financial metrics
  5. Print analysis summary (top products, regions, uplift calc)
  6. Save cleaned_sales_data.csv
"""

import pandas as pd
import numpy as np

def analyze_and_clean_data(
    input_file:  str = 'raw_sales_data.csv',
    output_file: str = 'cleaned_sales_data.csv',
) -> pd.DataFrame:

    print(f"\n{'='*55}")
    print("  SALES DATA — CLEANING & ANALYSIS PIPELINE")
    print(f"{'='*55}")

    # ── 1. Load ────────────────────────────────────────────────────────────
    df = pd.read_csv(input_file)
    print(f"\n[1] Loaded  : {len(df):>8,} rows  |  {df.shape[1]} columns")

    # ── 2. De-duplicate ────────────────────────────────────────────────────
    before = len(df)
    df.drop_duplicates(inplace=True)
    df.reset_index(drop=True, inplace=True)
    print(f"[2] Dupes removed : {before - len(df):>5,}  →  {len(df):,} rows remain")

    # ── 3. Missing value treatment ─────────────────────────────────────────
    df['Region'].fillna('Unknown', inplace=True)
    df['Sales_Rep'].fillna('Unassigned', inplace=True)
    print(f"[3] Missing values imputed (Region → 'Unknown', Sales_Rep → 'Unassigned')")

    # ── 4. Date engineering ────────────────────────────────────────────────
    df['Date']      = pd.to_datetime(df['Date'])
    df['Year']      = df['Date'].dt.year
    df['Month']     = df['Date'].dt.month
    df['Quarter']   = df['Date'].dt.quarter
    df['YearMonth'] = df['Date'].dt.to_period('M').astype(str)
    df['YearQ']     = df['Date'].dt.to_period('Q').astype(str)
    df['DayOfWeek'] = df['Date'].dt.day_name()

    # ── 5. Financial metrics ───────────────────────────────────────────────
    df['Gross_Sales']     = (df['Units_Sold'] * df['Unit_Price']).round(2)
    df['Discount_Amount'] = (df['Gross_Sales'] * df['Discount']).round(2)
    df['Net_Sales']       = (df['Gross_Sales'] - df['Discount_Amount']).round(2)
    df['Total_Cost']      = (df['Units_Sold'] * df['Unit_Cost']).round(2)
    df['Profit']          = (df['Net_Sales'] - df['Total_Cost']).round(2)
    df['Profit_Margin']   = np.where(
        df['Net_Sales'] > 0,
        (df['Profit'] / df['Net_Sales']).round(4),
        0.0
    )

    print(f"[4] Derived metrics computed: Gross/Net Sales, Profit, Profit_Margin")

    # ── 6. Analysis ────────────────────────────────────────────────────────
    print(f"\n{'─'*55}")
    print("  TOP-LINE KPIs")
    print(f"{'─'*55}")
    total_rev    = df['Net_Sales'].sum()
    total_profit = df['Profit'].sum()
    avg_margin   = df['Profit_Margin'].mean()
    total_units  = df['Units_Sold'].sum()

    print(f"  Total Revenue : ${total_rev:>14,.2f}")
    print(f"  Total Profit  : ${total_profit:>14,.2f}")
    print(f"  Avg Margin    : {avg_margin:>13.2%}")
    print(f"  Total Units   : {total_units:>14,}")

    print(f"\n{'─'*55}")
    print("  PERFORMANCE BY CATEGORY")
    print(f"{'─'*55}")
    cat_metrics = df.groupby('Category').agg(
        Revenue     = ('Net_Sales',     'sum'),
        Profit      = ('Profit',        'sum'),
        Avg_Margin  = ('Profit_Margin', 'mean'),
        Transactions= ('Order_ID',      'count'),
    ).sort_values('Revenue', ascending=False)
    cat_metrics['Revenue_Share'] = (cat_metrics['Revenue'] / total_rev * 100).round(1)
    print(cat_metrics.to_string())

    print(f"\n{'─'*55}")
    print("  TOP 5 REGIONS BY REVENUE")
    print(f"{'─'*55}")
    reg = df.groupby('Region')['Net_Sales'].sum().sort_values(ascending=False).head(5)
    for r, v in reg.items():
        print(f"  {r:<28}: ${v:>12,.0f}")

    print(f"\n{'─'*55}")
    print("  UPLIFT ANALYSIS — FURNITURE CATEGORY")
    print(f"{'─'*55}")
    furn_rev    = df[df['Category'] == 'Furniture']['Net_Sales'].sum()
    furn_margin = df[df['Category'] == 'Furniture']['Profit_Margin'].mean()
    elec_margin = df[df['Category'] == 'Electronics']['Profit_Margin'].mean()
    uplift_rev  = furn_rev * 0.15
    margin_gap  = elec_margin - furn_margin

    print(f"  Furniture Revenue      : ${furn_rev:>12,.0f}")
    print(f"  Furniture Avg Margin   : {furn_margin:>12.2%}")
    print(f"  Electronics Avg Margin : {elec_margin:>12.2%}")
    print(f"  Margin Gap             : {margin_gap:>12.2%}")
    print(f"  ▶ 15% Potential Uplift : ${uplift_rev:>12,.0f}")
    print(f"\n  Strategy: Reduce average discount (currently {df[df['Category']=='Furniture']['Discount'].mean():.0%})")
    print(f"  from ~{df[df['Category']=='Furniture']['Discount'].mean():.0%} to <10% and renegotiate supplier costs.")

    # ── 7. Save ────────────────────────────────────────────────────────────
    df.to_csv(output_file, index=False)
    print(f"\n{'='*55}")
    print(f"  ✓ Cleaned data saved → '{output_file}'  ({len(df):,} rows)")
    print(f"{'='*55}\n")
    return df


if __name__ == '__main__':
    analyze_and_clean_data()
