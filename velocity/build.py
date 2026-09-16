"""Run the SQL models in order and write the outputs.

    python -m velocity.build --data data --as-of 2026-09-14 --out out
"""
from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

import duckdb

SQL_DIR = Path(__file__).resolve().parents[1] / "sql"
OUTPUT_TABLES = ["sku_velocity", "region_velocity", "weekly_trend",
                 "new_door_ramp", "store_reorder_health", "sku_whitespace"]


def build(data_dir: Path, as_of: date, db_path: str = ":memory:") -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(db_path)
    params = {"data": str(Path(data_dir).resolve()).replace("'", "''"), "as_of": as_of.isoformat()}
    for path in sorted(SQL_DIR.glob("*.sql")):
        sql = path.read_text()
        for key, value in params.items():
            sql = sql.replace("{" + key + "}", value)
        try:
            con.execute(sql)
        except duckdb.Error as exc:
            raise RuntimeError(f"{path.name}: {exc}") from exc
    return con


def export(con: duckdb.DuckDBPyConnection, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for t in OUTPUT_TABLES:
        con.table(t).df().to_csv(out_dir / f"{t}.csv", index=False)


def main(argv: list[str] | None = None) -> int:
    from .report import write_report

    ap = argparse.ArgumentParser(description="Build velocity, reorder and whitespace tables.")
    ap.add_argument("--data", type=Path, default=Path("data"))
    ap.add_argument("--as-of", type=date.fromisoformat, default=date.today())
    ap.add_argument("--out", type=Path, default=Path("out"))
    ap.add_argument("--db", default=":memory:", help="path to keep a .duckdb file for ad-hoc queries")
    args = ap.parse_args(argv)

    con = build(args.data, args.as_of, args.db)
    export(con, args.out)
    path = write_report(con, args.out, args.as_of)
    print(f"wrote {len(OUTPUT_TABLES)} tables and {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
