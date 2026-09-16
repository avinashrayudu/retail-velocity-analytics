import csv
from datetime import date
from pathlib import Path

import pytest

from velocity.build import build, export
from velocity.report import write_report

ROOT = Path(__file__).resolve().parents[1]
AS_OF = date(2026, 9, 14)


def write(path, rows):
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


@pytest.fixture(scope="session")
def sample_data():
    return ROOT / "data"


@pytest.fixture
def tiny(tmp_path):
    write(tmp_path / "skus.csv", [
        {"sku": "A", "sku_name": "Bar A", "case_units": 10, "unit_price": 2.0},
        {"sku": "B", "sku_name": "Bar B", "case_units": 10, "unit_price": 3.0},
    ])
    stores = []
    for i, (typ, first) in enumerate([("grocery", "2026-01-05")] * 6 + [("grocery", "2026-07-06")]):
        stores.append({"store_id": f"S{i}", "store_name": f"Shop {i}", "region": "Brooklyn",
                       "store_type": typ, "first_order_date": first, "shares_pos": "true"})
    write(tmp_path / "stores.csv", stores)

    orders = []
    # S0 reorders every 28 days and is current; S1 stopped in May; S2 carries only A.
    for sid, dates, skus in [
        ("S0", ["2026-06-22", "2026-07-20", "2026-08-17", "2026-09-10"], ["A", "B"]),
        ("S1", ["2026-03-02", "2026-03-30", "2026-04-27", "2026-05-25"], ["A", "B"]),
        ("S2", ["2026-07-01", "2026-08-01", "2026-09-01"], ["A"]),
        ("S3", ["2026-09-01"], ["A", "B"]),
    ]:
        for d in dates:
            for k in skus:
                orders.append({"order_id": f"{sid}-{d}", "order_date": d, "store_id": sid, "sku": k,
                               "cases": 1, "units": 10, "net_revenue": 20.0})
    write(tmp_path / "orders.csv", orders)

    pos = []
    for w in range(12):
        week = date.fromordinal(date(2026, 6, 22).toordinal() + 7 * w).isoformat()
        for sid in ["S0", "S3", "S4", "S5", "S6"]:
            pos.append({"week_start": week, "store_id": sid, "sku": "A", "units": 4})
        pos.append({"week_start": week, "store_id": "S2", "sku": "A", "units": 1})  # the laggard
        pos.append({"week_start": week, "store_id": "S0", "sku": "B", "units": 6})
    write(tmp_path / "pos_weekly.csv", pos)
    return tmp_path


def test_velocity_counts_only_weeks_on_shelf(tiny):
    con = build(tiny, AS_OF)
    v = {r[0]: r for r in con.execute("select sku, doors_selling, units_per_store_week from sku_velocity").fetchall()}
    assert v["B"][1] == 1 and v["B"][2] == 6.0      # one door, 6 a week; other doors don't dilute it
    assert v["A"][1] == 6


def test_reorder_status(tiny):
    con = build(tiny, AS_OF)
    status = dict(con.execute("select store_id, status from store_reorder_health").fetchall())
    assert status["S0"] == "on rhythm"
    assert status["S1"] == "lapsed"
    assert status["S3"] == "too new"


def test_lagging_door_is_flagged(tiny):
    con = build(tiny, AS_OF)
    lag = [r[0] for r in con.execute("select store_id from new_door_ramp where lagging").fetchall()]
    assert lag == ["S2"]


def test_whitespace_only_for_healthy_stores(tiny):
    con = build(tiny, AS_OF)
    rows = con.execute("select store_id, sku from sku_whitespace").fetchall()
    assert ("S2", "B") in rows              # S2 is healthy and missing B
    assert all(r[0] != "S1" for r in rows)  # lapsed stores are a save, not an upsell


def test_sample_build_and_report(sample_data, tmp_path):
    con = build(sample_data, AS_OF)
    export(con, tmp_path)
    report = write_report(con, tmp_path, AS_OF).read_text()
    assert "Reorder risk" in report
    assert (tmp_path / "sku_velocity.csv").exists()
    top = con.execute("select sku from sku_velocity order by units_per_store_week desc limit 1").fetchone()[0]
    assert top == "BAR-MILK-12"
    lag = con.execute("select count(*) from new_door_ramp where lagging").fetchone()[0]
    assert lag >= 1
