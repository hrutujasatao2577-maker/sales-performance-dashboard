"""
data_generator.py — Generates 55,000 rows of realistic sales transaction data.

Simulates a multi-region, multi-category B2B sales dataset with:
- Seasonal patterns (Q4 peak, summer dip)
- Regional growth trends
- Intentional underperformance in Furniture category (for insight generation)
- ~1% missing values to demonstrate data cleaning
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_sales_data(num_rows: int = 55000, output_file: str = 'raw_sales_data.csv') -> pd.DataFrame:
    print(f"Generating {num_rows} rows of realistic sales data...")
    rng = np.random.default_rng(seed=42)

    # ── Date range: Jan 2022 – Dec 2023 ────────────────────────────────────
    start_date = datetime(2022, 1, 1)
    end_date   = datetime(2023, 12, 31)
    total_days = (end_date - start_date).days

    # Seasonal weight per day-of-year (Q4 spike, summer dip)
    doy_weights = np.ones(366)
    doy_weights[274:365] *= 2.2   # Oct–Dec peak
    doy_weights[152:243] *= 0.75  # Jun–Aug summer dip
    doy_weights = doy_weights / doy_weights.sum()

    sampled_days = rng.choice(total_days + 1, size=num_rows,
                               p=np.tile(doy_weights[:total_days+1],1)[:total_days+1] /
                                 doy_weights[:total_days+1].sum())
    dates = [start_date + timedelta(days=int(d)) for d in sampled_days]

    # ── Geography ─────────────────────────────────────────────────────────
    regions  = ['North America', 'Europe', 'Asia Pacific', 'Latin America', 'Middle East & Africa']
    reg_wts  = [0.32, 0.28, 0.22, 0.10, 0.08]   # realistic share
    cities   = {
        'North America':        ['New York', 'Los Angeles', 'Chicago', 'Toronto', 'Dallas'],
        'Europe':               ['London', 'Paris', 'Berlin', 'Amsterdam', 'Madrid'],
        'Asia Pacific':         ['Singapore', 'Tokyo', 'Sydney', 'Mumbai', 'Seoul'],
        'Latin America':        ['São Paulo', 'Mexico City', 'Buenos Aires', 'Bogotá'],
        'Middle East & Africa': ['Dubai', 'Riyadh', 'Nairobi', 'Cape Town'],
    }

    region_col = rng.choice(regions, size=num_rows, p=reg_wts)
    city_col   = [rng.choice(cities[r]) for r in region_col]

    # ── Product catalogue ──────────────────────────────────────────────────
    catalogue = {
        'Electronics':    {
            'products': ['Laptops', 'Smartphones', 'Tablets', 'Monitors', 'Headphones', 'Webcams'],
            'weight': 0.38,
            'price_range': (299, 1799),
            'cost_pct': (0.48, 0.65),
            'discount_range': (0.00, 0.12),
            'units_range': (1, 8),
        },
        'Office Supplies': {
            'products': ['Chairs', 'Keyboards', 'Mouse', 'Paper', 'Pens', 'Binders', 'Staplers'],
            'weight': 0.30,
            'price_range': (8, 149),
            'cost_pct': (0.38, 0.55),
            'discount_range': (0.00, 0.08),
            'units_range': (5, 50),
        },
        'Furniture':      {
            'products': ['Sofas', 'Executive Desks', 'Boardroom Tables', 'Filing Cabinets', 'Shelving Units'],
            'weight': 0.12,   # intentionally under-represented
            'price_range': (199, 1299),
            'cost_pct': (0.72, 0.91),   # HIGH cost ratio → thin margins
            'discount_range': (0.10, 0.35),  # high discounts to move stock
            'units_range': (1, 4),
        },
        'Accessories':    {
            'products': ['Laptop Bags', 'Phone Cases', 'Chargers', 'USB Hubs', 'Screen Protectors'],
            'weight': 0.20,
            'price_range': (12, 89),
            'cost_pct': (0.35, 0.50),
            'discount_range': (0.00, 0.10),
            'units_range': (2, 30),
        },
    }

    cat_names = list(catalogue.keys())
    cat_wts   = [catalogue[c]['weight'] for c in cat_names]
    cat_wts   = [w / sum(cat_wts) for w in cat_wts]

    # ── Sales reps ─────────────────────────────────────────────────────────
    reps = [
        'Alice Monroe', 'Bob Patel', 'Carlos Vega', 'Diana Chen',
        'Ethan Brooks', 'Fatima Al-Rashid', 'George Kim', 'Hannah Schmidt',
        'Ivan Petrov', 'Jaya Nair',
    ]

    # ── Channels ───────────────────────────────────────────────────────────
    channels     = ['Direct', 'Online', 'Partner', 'Reseller']
    channel_wts  = [0.35, 0.30, 0.20, 0.15]

    # ── Build rows ─────────────────────────────────────────────────────────
    rows = []
    order_id_start = 100_000

    cat_col   = rng.choice(cat_names, size=num_rows, p=cat_wts)
    chan_col   = rng.choice(channels,  size=num_rows, p=channel_wts)
    rep_col    = rng.choice(reps,      size=num_rows)

    for i in range(num_rows):
        cat  = cat_col[i]
        cfg  = catalogue[cat]
        prod = rng.choice(cfg['products'])

        units = int(rng.integers(cfg['units_range'][0], cfg['units_range'][1] + 1))
        price = round(float(rng.uniform(*cfg['price_range'])), 2)
        cost  = round(price * float(rng.uniform(*cfg['cost_pct'])), 2)
        disc  = round(float(rng.uniform(*cfg['discount_range'])), 3)

        rows.append({
            'Order_ID':    order_id_start + i,
            'Date':        dates[i].strftime('%Y-%m-%d'),
            'Region':      region_col[i],
            'City':        city_col[i],
            'Category':    cat,
            'Product':     prod,
            'Channel':     chan_col[i],
            'Sales_Rep':   rep_col[i],
            'Units_Sold':  units,
            'Unit_Price':  price,
            'Unit_Cost':   cost,
            'Discount':    disc,
        })

    df = pd.DataFrame(rows)

    # ── Inject ~1% missing values (realistic dirty data) ──────────────────
    n_missing = int(num_rows * 0.010)
    df.loc[rng.choice(df.index, n_missing // 2, replace=False), 'Region'] = np.nan
    df.loc[rng.choice(df.index, n_missing // 2, replace=False), 'Sales_Rep'] = np.nan

    # ── Inject ~0.3% duplicate rows ───────────────────────────────────────
    n_dupes = int(num_rows * 0.003)
    dup_idx  = rng.choice(df.index, n_dupes, replace=False)
    df = pd.concat([df, df.loc[dup_idx]], ignore_index=True)

    df.to_csv(output_file, index=False)
    print(f"  ✓ {len(df):,} rows written to '{output_file}'  "
          f"({n_missing} missing values, {n_dupes} duplicates injected)")
    return df


if __name__ == '__main__':
    generate_sales_data()
