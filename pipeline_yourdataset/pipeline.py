"""Shop pipeline: load -> clean -> validate -> split -> enrich -> output.

Run from this folder with: python pipeline.py
Raw files are read only. Generated files are written to data/output/.
"""
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import pandera.pandas as pa

import rules

BASE = Path(__file__).parent
RAW = BASE / "data" / "raw"
OUT = BASE / "data" / "output"
LOG = BASE / "logs" / "run_log.txt"


def log(msg):
    print(msg)
    RUN_LOG.append(msg)


def write_log(status):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"=== run {datetime.now():%Y-%m-%d %H:%M:%S} - {status} ===\n")
        f.write("\n".join(RUN_LOG) + "\n\n")


def parse_mixed_date(col):
    iso = pd.to_datetime(col, format="%Y-%m-%d", errors="coerce")
    de = pd.to_datetime(col, format="%d.%m.%Y", errors="coerce")
    return iso.fillna(de)


def load_raw():
    frames = []
    for file in sorted(RAW.glob("orders_*.csv")):
        df = pd.read_csv(file, dtype=str, keep_default_na=False)
        df["source_file"] = file.name
        frames.append(df)
    if not frames:
        raise FileNotFoundError(f"No orders_*.csv files found in {RAW}")
    orders = pd.concat(frames, ignore_index=True)
    customers = pd.read_csv(RAW / "customers.csv", dtype=str, keep_default_na=False)
    log(f"Loaded {len(orders)} order rows from {len(frames)} files, {len(customers)} customers")
    return orders, customers


def clean_orders(orders):
    before = len(orders)
    df = orders.drop_duplicates().copy()
    log(f"Removed {before - len(df)} exact duplicate(s): {before} -> {len(df)} rows")
    for col in ["order_id", "customer_id", "category"]:
        df[col] = df[col].str.strip()
    df["order_date"] = parse_mixed_date(df["order_date"])
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").astype(float)
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce").astype(float)
    return df


def clean_customers(customers):
    df = customers.copy()
    for col in df.columns:
        df[col] = df[col].str.strip()

    # Explicit, documented corrections for known typos in the supplied sample.
    fixes = {
        "clara.schmidt(at)web.de": "clara.schmidt@web.de",
    }
    df["email"] = df["email"].replace(fixes)
    df["country"] = df["country"].replace({"Germny": "Germany"})
    return df


def validate(orders, customers):
    try:
        rules.clean_orders_rules.validate(orders, lazy=True)
        rules.clean_customers_rules.validate(customers, lazy=True)
    except pa.errors.SchemaErrors as err:
        log("VALIDATION FAILED - pipeline stopped, no outputs written:")
        cases = err.failure_cases[["column", "check", "failure_case", "index"]]
        log(cases.to_string(index=False))
        write_log("FAILED")
        sys.exit(1)
    log("Validation passed: all critical rules OK")


def split(orders, customers):
    df = orders.copy()
    # The March export stores prices in cents; convert them to EUR.
    df.loc[df["source_file"] == "orders_2026_03.csv", "unit_price"] /= 100

    reason = pd.Series("", index=df.index, dtype="object")
    reason[df["order_date"].isna()] = "missing order_date"
    reason[df["unit_price"].isna()] = "missing unit_price"
    reason[~df["customer_id"].isin(customers["customer_id"])] = "unknown customer"
    reason[df["quantity"] <= 0] = "quantity <= 0"
    quarantine = df[reason != ""].copy()
    quarantine["reason"] = reason[reason != ""]
    trusted = df[reason == ""].copy()
    log(f"Split: {len(trusted)} trusted, {len(quarantine)} quarantined")
    return trusted, quarantine


def enrich_orders(trusted, customers):
    df = trusted.merge(customers[["customer_id", "city"]], on="customer_id", how="left")
    df["line_total"] = (df["quantity"] * df["unit_price"]).round(2)
    return df


def output(fct, quarantine):
    OUT.mkdir(parents=True, exist_ok=True)
    fct.to_csv(OUT / "fct_orders.csv", index=False)
    quarantine.to_csv(OUT / "quarantine_orders.csv", index=False)

    by_city = (fct.groupby("city", as_index=False)["line_total"].sum().round(2)
               .sort_values("line_total", ascending=False))
    by_city.to_csv(OUT / "revenue_by_city.csv", index=False)

    by_category = (fct.groupby("category", as_index=False)["line_total"].sum().round(2)
                   .sort_values("line_total", ascending=False))
    by_category.to_csv(OUT / "revenue_by_category.csv", index=False)

    log(f"Revenue: EUR {fct['line_total'].sum():,.2f}")
    log("Wrote fct_orders.csv, quarantine_orders.csv, revenue_by_city.csv, revenue_by_category.csv")


def main():
    global RUN_LOG
    RUN_LOG = []
    raw_orders, raw_customers = load_raw()
    orders = clean_orders(raw_orders)
    customers = clean_customers(raw_customers)
    validate(orders, customers)
    trusted, quarantine = split(orders, customers)
    fct = enrich_orders(trusted, customers)
    output(fct, quarantine)
    write_log("SUCCESS")


if __name__ == "__main__":
    main()
