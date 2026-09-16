from __future__ import annotations

from datetime import date
from pathlib import Path

import duckdb
import pandas as pd


def _fmt(v) -> str:
    if v is None or (not isinstance(v, str) and pd.isna(v)):
        return ""
    if isinstance(v, pd.Timestamp):
        return v.date().isoformat()
    if isinstance(v, float):
        return f"{v:,.2f}".rstrip("0").rstrip(".")
    return str(v)


def _md(df: pd.DataFrame, cols: list[str] | None = None, n: int = 10) -> str:
    d = df[cols] if cols else df
    d = d.head(n)
    head = "| " + " | ".join(d.columns) + " |"
    sep = "|" + "---|" * len(d.columns)
    rows = ["| " + " | ".join(_fmt(v) for v in r) + " |" for r in d.itertuples(index=False)]
    return "\n".join([head, sep, *rows])


def _n(count, singular: str, plural: str) -> str:
    count = int(count)
    return f"{count} {singular if count == 1 else plural}"


def _bar(values: list[float], width: int = 28) -> list[str]:
    top = max(values) if values else 1
    return ["█" * max(1, round(v / top * width)) for v in values]


def write_report(con: duckdb.DuckDBPyConnection, out_dir: Path, as_of: date) -> Path:
    sku = con.table("sku_velocity").df()
    region = con.table("region_velocity").df()
    ramp = con.table("new_door_ramp").df()
    health = con.table("store_reorder_health").df()
    white = con.table("sku_whitespace").df()

    status = health["status"].value_counts()
    at_risk = health[health["status"].isin(["overdue", "lapsed"])].sort_values("lifetime_revenue", ascending=False)
    lagging = ramp[ramp["lagging"]]

    sku_lines = [f"{r.sku_name:<22} {b} {r.units_per_store_week}"
                 for r, b in zip(sku.itertuples(), _bar(sku["units_per_store_week"].tolist()))]

    parts = [
        "# Retail velocity report",
        "",
        f"As of {as_of}. Velocity uses the last 12 weeks of scan data.",
        "",
        "## Headline",
        "",
        f"- **{_n(status.get('overdue', 0), 'store is', 'stores are')} overdue** for a reorder and "
        f"**{_n(status.get('lapsed', 0), 'has', 'have')} lapsed**, "
        f"together worth ${at_risk['lifetime_revenue'].sum():,.0f} in lifetime wholesale revenue.",
        f"- **{_n(len(lagging), 'door is', 'doors are')} selling at less than half the pace of similar stores** in their first eight weeks.",
        f"- **{len(white)} store and SKU gaps** in healthy accounts, worth about ${white['est_monthly_wholesale'].sum():,.0f} a month at peer velocity.",
        "",
        "## Units per store per week, by SKU",
        "",
        "```",
        *sku_lines,
        "```",
        "",
        _md(sku, ["sku_name", "doors_selling", "units_per_store_week", "dollars_per_store_week"]),
        "",
        "## Velocity by region and store type (top 10)",
        "",
        _md(region),
        "",
        "## Reorder risk: call these stores first",
        "",
        _md(at_risk, ["store_name", "region", "status", "days_since_order", "median_gap_days", "lifetime_revenue"]),
        "",
        "## Doors lagging similar stores in their first eight weeks",
        "",
        _md(lagging, ["store_name", "region", "store_type", "cohort_month", "units_per_sku_week", "peer_median", "vs_peers"]),
        "",
        "These are worth a store visit before a price conversation. A door selling at a fraction of",
        "stores just like it usually has the product off the shelf or out of sight.",
        "",
        "## Whitespace: SKUs missing from healthy stores (top 10)",
        "",
        _md(white, ["store_name", "store_type", "sku_name", "peer_units_per_week", "est_monthly_wholesale"]),
        "",
    ]
    path = out_dir / "report.md"
    path.write_text("\n".join(parts))
    return path
