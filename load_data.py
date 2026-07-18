"""
load_data.py
------------
Loads the generated CSVs into a SQLite database using the schema
defined in schema.sql. This is the "L" (Load) step of the pipeline.
"""

import sqlite3
import pandas as pd

DB_PATH = "credit_pipeline.db"


def main():
    conn = sqlite3.connect(DB_PATH)

    with open("schema.sql", "r") as f:
        conn.executescript(f.read())

    customers_df = pd.read_csv("data/customers.csv")
    loans_df = pd.read_csv("data/loans.csv")
    repayments_df = pd.read_csv("data/repayments.csv")

    customers_df.to_sql("customers", conn, if_exists="append", index=False)
    loans_df.to_sql("loans", conn, if_exists="append", index=False)
    repayments_df.to_sql("repayments", conn, if_exists="append", index=False)

    conn.commit()

    counts = conn.execute(
        "SELECT (SELECT COUNT(*) FROM customers), (SELECT COUNT(*) FROM loans), (SELECT COUNT(*) FROM repayments)"
    ).fetchone()
    print(f"Loaded -> customers: {counts[0]}, loans: {counts[1]}, repayments: {counts[2]}")

    conn.close()


if __name__ == "__main__":
    main()
