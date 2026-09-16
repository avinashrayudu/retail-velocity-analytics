"""Fake data for a small snack and chocolate brand selling to independent retail.

Four files, shaped like what a brand actually has on hand:
  stores.csv       one row per retail door
  skus.csv         the product list with case size and wholesale price
  orders.csv       wholesale order lines (what the store bought from us)
  pos_weekly.csv   weekly units sold at the register, for the doors that share scan data

Everything is invented. A few stories are planted so the models have something to find:
  - a batch of doors opened in April where a handful sell far below their peers
  - stores that used to reorder every few weeks and then went quiet
  - stores carrying only the dark bar, even though the milk bar sells faster
"""
from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(21)
OUT = Path(__file__).resolve().parents[1] / "data"
AS_OF = date(2026, 9, 14)            # a Monday
START = date(2026, 1, 5)

SKUS = [
    # sku, name, case_units, wholesale_price_per_unit, base weekly units per store
    ("BAR-DARK-12", "Dark 72% 12-pack", 12, 2.60, 3.0),
    ("BAR-MILK-12", "Creamy Milk 12-pack", 12, 2.60, 5.0),
    ("BAR-SALT-12", "Sea Salt 12-pack", 12, 2.80, 2.0),
    ("BAR-MATCHA-12", "Matcha White 12-pack", 12, 2.90, 2.4),
]
REGIONS = {"Brooklyn": 1.1, "Manhattan": 1.25, "Queens": 0.9, "Bronx": 0.8, "New Jersey": 0.85, "Westchester": 1.0}
TYPES = {"grocery": 1.2, "specialty": 1.0, "cafe": 0.6, "gift": 0.5}

stores = []
for i in range(1, 161):
    region = random.choice(list(REGIONS))
    stype = random.choices(list(TYPES), [4, 3, 2, 1])[0]
    if i <= 110:
        opened = START + timedelta(weeks=random.randint(0, 10))
    elif i <= 140:
        opened = date(2026, 4, 6) + timedelta(days=random.randint(0, 20))   # spring expansion cohort
    else:
        opened = date(2026, 6, 1) + timedelta(weeks=random.randint(0, 8))
    stores.append({
        "store_id": f"S{i:03d}",
        "store_name": f"{random.choice(['Corner','Union','Park','Hudson','Garden','Maple','Olive','Harbor'])} "
                      f"{random.choice(['Market','Grocer','Pantry','Cafe','Provisions','Foods'])} #{i}",
        "region": region, "store_type": stype, "first_order_date": opened.isoformat(),
        "shares_pos": "true" if random.random() < 0.6 else "false",
    })

laggards = set(random.sample([s["store_id"] for s in stores[110:140]], 6))
churned = set(random.sample([s["store_id"] for s in stores[:110]], 12))
dark_only = set(random.sample([s["store_id"] for s in stores[:110]], 18))

orders, pos = [], []
oid = 0
for s in stores:
    opened = date.fromisoformat(s["first_order_date"])
    carried = [k for k in SKUS if not (s["store_id"] in dark_only and k[0] != "BAR-DARK-12")]
    if s["store_id"] not in dark_only:
        carried = [k for k in carried if k[0] in ("BAR-DARK-12", "BAR-MILK-12") or random.random() < 0.5]
    mult = REGIONS[s["region"]] * TYPES[s["store_type"]]
    if s["store_id"] in laggards:
        mult *= 0.25
    interval = random.choice([3, 4, 4, 5, 6])  # weeks between orders
    stop = AS_OF - timedelta(weeks=random.randint(8, 14)) if s["store_id"] in churned else AS_OF

    week = opened - timedelta(days=opened.weekday())
    w = 0
    while week <= AS_OF - timedelta(days=7):
        if s["shares_pos"] == "true" and week <= stop:
            for sku, name, case, price, base in carried:
                ramp = min(1.0, 0.5 + w * 0.1)
                units = max(0, round(random.gauss(base * mult * ramp, 1.0)))
                pos.append({"week_start": week.isoformat(), "store_id": s["store_id"], "sku": sku, "units": units})
        if w % interval == 0 and week <= stop:
            oid += 1
            order_date = week + timedelta(days=random.randint(0, 4))
            for sku, name, case, price, base in carried:
                cases = max(1, round(base * mult * interval / case + random.uniform(-0.4, 0.4)))
                orders.append({"order_id": f"O{oid:05d}", "order_date": order_date.isoformat(),
                               "store_id": s["store_id"], "sku": sku, "cases": cases,
                               "units": cases * case, "net_revenue": round(cases * case * price, 2)})
        week += timedelta(weeks=1)
        w += 1

OUT.mkdir(exist_ok=True)
for fname, rows in (("stores.csv", stores), ("orders.csv", orders), ("pos_weekly.csv", pos)):
    with open(OUT / fname, "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0]))
        wr.writeheader()
        wr.writerows(rows)
with open(OUT / "skus.csv", "w", newline="") as fh:
    wr = csv.writer(fh)
    wr.writerow(["sku", "sku_name", "case_units", "unit_price"])
    for sku, name, case, price, _ in SKUS:
        wr.writerow([sku, name, case, price])
print(f"{len(stores)} stores, {len(orders)} order lines, {len(pos)} POS rows")
