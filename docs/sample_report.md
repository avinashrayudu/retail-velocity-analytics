# Retail velocity report

As of 2026-09-14. Velocity uses the last 12 weeks of scan data.

## Headline

- **11 stores are overdue** for a reorder and **1 has lapsed**, together worth $8,105 in lifetime wholesale revenue.
- **4 doors are selling at less than half the pace of similar stores** in their first eight weeks.
- **178 store and SKU gaps** in healthy accounts, worth about $4,521 a month at peer velocity.

## Units per store per week, by SKU

```
Creamy Milk 12-pack    ████████████████████████████ 4.3
Dark 72% 12-pack       █████████████████ 2.61
Matcha White 12-pack   ██████████████ 2.12
Sea Salt 12-pack       ████████████ 1.89
```

| sku_name | doors_selling | units_per_store_week | dollars_per_store_week |
|---|---|---|---|
| Creamy Milk 12-pack | 83 | 4.3 | 11.18 |
| Dark 72% 12-pack | 94 | 2.61 | 6.79 |
| Matcha White 12-pack | 42 | 2.12 | 6.14 |
| Sea Salt 12-pack | 39 | 1.89 | 5.3 |

## Velocity by region and store type (top 10)

| region | store_type | doors | units_per_store_week |
|---|---|---|---|
| Manhattan | grocery | 6 | 4.86 |
| Westchester | grocery | 7 | 4.04 |
| Brooklyn | grocery | 6 | 3.93 |
| Brooklyn | specialty | 2 | 3.61 |
| Manhattan | specialty | 2 | 3.51 |
| New Jersey | grocery | 6 | 3.34 |
| Westchester | specialty | 6 | 3.32 |
| Bronx | grocery | 10 | 3.22 |
| Queens | grocery | 4 | 2.67 |
| Manhattan | cafe | 4 | 2.61 |

## Reorder risk: call these stores first

| store_name | region | status | days_since_order | median_gap_days | lifetime_revenue |
|---|---|---|---|---|---|
| Garden Cafe #48 | Brooklyn | overdue | 91 | 35 | 1,101.6 |
| Union Market #30 | Westchester | overdue | 66 | 29 | 1,071.6 |
| Harbor Grocer #44 | Manhattan | overdue | 89 | 42 | 883.2 |
| Harbor Market #24 | Bronx | overdue | 68 | 28.5 | 836.4 |
| Garden Pantry #66 | Westchester | lapsed | 70 | 20 | 768 |
| Corner Pantry #21 | Bronx | overdue | 52 | 21 | 768 |
| Hudson Grocer #55 | Bronx | overdue | 101 | 35 | 747.6 |
| Park Foods #34 | Brooklyn | overdue | 105 | 40.5 | 673.2 |
| Park Foods #8 | Queens | overdue | 60 | 35 | 561.6 |
| Corner Market #33 | New Jersey | overdue | 101 | 44 | 319.2 |

## Doors lagging similar stores in their first eight weeks

| store_name | region | store_type | cohort_month | units_per_sku_week | peer_median | vs_peers |
|---|---|---|---|---|---|---|
| Union Cafe #112 | Queens | grocery | 2026-04-01 | 1 | 2.97 | 0.34 |
| Garden Pantry #132 | Queens | specialty | 2026-04-01 | 0.88 | 2.55 | 0.35 |
| Corner Grocer #139 | Bronx | cafe | 2026-04-01 | 0.75 | 1.69 | 0.44 |
| Corner Pantry #134 | Brooklyn | grocery | 2026-04-01 | 1.33 | 2.97 | 0.45 |

These are worth a store visit before a price conversation. A door selling at a fraction of
stores just like it usually has the product off the shelf or out of sight.

## Whitespace: SKUs missing from healthy stores (top 10)

| store_name | store_type | sku_name | peer_units_per_week | est_monthly_wholesale |
|---|---|---|---|---|
| Maple Provisions #78 | grocery | Creamy Milk 12-pack | 5.4 | 60.37 |
| Olive Foods #43 | grocery | Creamy Milk 12-pack | 5.4 | 60.37 |
| Maple Market #77 | grocery | Creamy Milk 12-pack | 5.4 | 60.37 |
| Olive Market #29 | grocery | Creamy Milk 12-pack | 5.4 | 60.37 |
| Park Cafe #93 | grocery | Creamy Milk 12-pack | 5.4 | 60.37 |
| Garden Grocer #102 | grocery | Creamy Milk 12-pack | 5.4 | 60.37 |
| Harbor Grocer #7 | grocery | Creamy Milk 12-pack | 5.4 | 60.37 |
| Hudson Provisions #14 | grocery | Creamy Milk 12-pack | 5.4 | 60.37 |
| Olive Grocer #22 | specialty | Creamy Milk 12-pack | 4.25 | 47.54 |
| Park Foods #84 | specialty | Creamy Milk 12-pack | 4.25 | 47.54 |
