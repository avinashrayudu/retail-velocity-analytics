# retail-velocity-analytics

![tests](https://github.com/avinashrayudu/retail-velocity-analytics/actions/workflows/tests.yml/badge.svg)

SQL models that answer the four questions a consumer brand's sales team asks every Monday:

1. **Which products actually sell once they're on the shelf?** (velocity)
2. **Which stores have gone quiet?** (reorder risk)
3. **Which new doors are underperforming stores like them?** (ramp)
4. **Where can we add a product to a healthy account?** (whitespace)

The models are written in DuckDB SQL over plain CSVs, so the whole thing runs on a laptop in about a second. They port to Snowflake or BigQuery with minor changes.

```bash
pip install -e ".[dev]"
python scripts/make_sample_data.py
python -m velocity --data data --as-of 2026-09-14 --out out
```

Full sample output: [`docs/sample_report.md`](docs/sample_report.md)

```
## Headline

- 11 stores are overdue for a reorder and 1 has lapsed, together worth $8,105 in lifetime wholesale revenue.
- 4 doors are selling at less than half the pace of similar stores in their first eight weeks.
- 178 store and SKU gaps in healthy accounts, worth about $4,521 a month at peer velocity.

## Units per store per week, by SKU

Creamy Milk 12-pack    ████████████████████████████ 4.3
Dark 72% 12-pack       █████████████████ 2.61
Matcha White 12-pack   ██████████████ 2.12
Sea Salt 12-pack       ████████████ 1.89
```

## Inputs

These are the files a small brand actually has: a store list, its own wholesale order lines, and weekly scan data from the stores that share it.

| file | grain | columns |
|---|---|---|
| `stores.csv` | one row per door | store_id, store_name, region, store_type, first_order_date, shares_pos |
| `skus.csv` | one row per SKU | sku, sku_name, case_units, unit_price |
| `orders.csv` | order line | order_id, order_date, store_id, sku, cases, units, net_revenue |
| `pos_weekly.csv` | store × SKU × week | week_start, store_id, sku, units |

## Models

| file | table | what it does |
|---|---|---|
| `sql/01_staging.sql` | `stg_*` | Typed views over the CSVs |
| `sql/02_velocity.sql` | `sku_velocity`, `region_velocity`, `weekly_trend` | Units and dollars per store per week over the last 12 weeks. It counts only the store-weeks where the SKU was on the shelf, so a product in 40 doors isn't diluted by the 120 doors that don't carry it |
| `sql/03_new_door_cohort.sql` | `new_door_ramp` | Each door's units per SKU per week in its first eight weeks, against the median for the same store type. A door below half the median is flagged |
| `sql/04_reorder_risk.sql` | `store_reorder_health` | Each store's own median gap between orders. A store is *overdue* past 1.5× that gap and *lapsed* past 3×. The gap has a floor of 21 days, so one quick reorder doesn't make a store look late forever |
| `sql/05_whitespace.sql` | `sku_whitespace` | Stores in good standing that are missing a SKU, priced at what that SKU sells in the same store type |

`python -m velocity --db velocity.duckdb` keeps the database file, so you can query it afterwards:

```sql
select store_type, status, count(*) from store_reorder_health group by all order by 1, 2;
```

## Decisions worth explaining

- **Velocity, not total units.** Total units rewards distribution. Velocity tells you whether the product earns its shelf space. In the sample, the milk chocolate bar sells well ahead of the dark bar, even though the dark bar is in more doors. That should change which SKU leads a pitch to a new buyer.
- **Per-SKU normalization for new doors.** A shop that took one SKU shouldn't look like a laggard next to a shop that took four. The first version of this model made that mistake and flagged stores that were fine.
- **Each store's own rhythm.** A café that orders every six weeks isn't late at week five. One global cutoff flags the wrong stores.
- **Only stores on rhythm show up as whitespace.** An overdue or lapsed store needs a save call first, not an upsell.
- **Laggards get a store visit, not a discount.** When a door sells at a fraction of the pace of similar stores, the product is usually in the back room or missing its shelf tag.

## Tests

```bash
pytest -q
```

The tests build a tiny handmade dataset where the right answer is known: a current store, a lapsed store, a brand-new store, and a single-SKU store that lags its peers. They check each model against it, then run the full sample end to end.

All stores and numbers in the sample data are invented.
