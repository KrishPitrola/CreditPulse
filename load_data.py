"""
load_data.py
------------
Loads the generated CSVs into a SQLite database using the schema
defined in schema.sql. This is the "L" (Load) step of the pipeline.

Includes data quality checks at two points:
  1. Pre-load: validate each DataFrame before it touches the database
     (nulls in required fields, duplicate primary keys, invalid ranges).
  2. Post-load: verify referential integrity (every foreign key actually
     resolves to a real row) -- SQLite doesn't enforce FK constraints by
     default, so this has to be checked explicitly.

If any check fails, the script raises an error and stops rather than
silently loading bad data.
"""

import sys
import sqlite3
import pandas as pd

DB_PATH = "credit_pipeline.db"


class DataQualityError(Exception):
    """Raised when a data quality check fails."""
    pass


# ---------------------------------------------------------
# Pre-load checks (run on the DataFrame, before writing to DB)
# ---------------------------------------------------------

def check_no_nulls(df, columns, table_name):
    for col in columns:
        null_count = df[col].isna().sum()
        if null_count > 0:
            raise DataQualityError(
                f"[{table_name}] Column '{col}' has {null_count} null value(s). "
                f"Expected no nulls."
            )


def check_unique_pk(df, pk_column, table_name):
    dup_count = df[pk_column].duplicated().sum()
    if dup_count > 0:
        raise DataQualityError(
            f"[{table_name}] Primary key '{pk_column}' has {dup_count} duplicate value(s)."
        )


def check_positive(df, columns, table_name):
    for col in columns:
        bad_count = (df[col] <= 0).sum()
        if bad_count > 0:
            raise DataQualityError(
                f"[{table_name}] Column '{col}' has {bad_count} value(s) <= 0. "
                f"Expected strictly positive values."
            )


def check_non_negative(df, columns, table_name):
    for col in columns:
        bad_count = (df[col] < 0).sum()
        if bad_count > 0:
            raise DataQualityError(
                f"[{table_name}] Column '{col}' has {bad_count} negative value(s)."
            )


def check_range(df, column, min_val, max_val, table_name):
    bad_count = (~df[column].between(min_val, max_val)).sum()
    if bad_count > 0:
        raise DataQualityError(
            f"[{table_name}] Column '{column}' has {bad_count} value(s) outside "
            f"expected range [{min_val}, {max_val}]."
        )


def validate_customers(df):
    check_no_nulls(df, ["customer_id", "name", "region"], "customers")
    check_unique_pk(df, "customer_id", "customers")
    check_positive(df, ["monthly_income"], "customers")
    check_range(df, "credit_score", 300, 900, "customers")
    check_range(df, "age", 18, 100, "customers")


def validate_loans(df):
    check_no_nulls(df, ["loan_id", "customer_id", "loan_amount"], "loans")
    check_unique_pk(df, "loan_id", "loans")
    check_positive(df, ["loan_amount", "term_months"], "loans")
    check_non_negative(df, ["interest_rate"], "loans")


def validate_repayments(df):
    check_no_nulls(df, ["repayment_id", "loan_id"], "repayments")
    check_unique_pk(df, "repayment_id", "repayments")
    check_non_negative(df, ["amount_paid", "days_late"], "repayments")


# ---------------------------------------------------------
# Post-load checks (run against the database, after writing)
# ---------------------------------------------------------

def check_foreign_keys(conn, child_table, fk_column, parent_table, parent_pk):
    """Every value in child_table.fk_column must exist in parent_table.parent_pk."""
    query = f"""
        SELECT COUNT(*) FROM {child_table}
        WHERE {fk_column} NOT IN (SELECT {parent_pk} FROM {parent_table})
    """
    orphan_count = conn.execute(query).fetchone()[0]
    if orphan_count > 0:
        raise DataQualityError(
            f"[{child_table}] {orphan_count} row(s) have '{fk_column}' values "
            f"that don't exist in {parent_table}.{parent_pk}. Referential integrity violated."
        )


def check_row_counts_match(conn, table_name, expected_count):
    actual = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    if actual != expected_count:
        raise DataQualityError(
            f"[{table_name}] Expected {expected_count} rows after load, found {actual}. "
            f"Some rows may have been dropped or duplicated during load."
        )


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():
    conn = sqlite3.connect(DB_PATH)

    with open("schema.sql", "r") as f:
        conn.executescript(f.read())

    customers_df = pd.read_csv("data/customers.csv")
    loans_df = pd.read_csv("data/loans.csv")
    repayments_df = pd.read_csv("data/repayments.csv")

    print("Running pre-load data quality checks...")
    try:
        validate_customers(customers_df)
        validate_loans(loans_df)
        validate_repayments(repayments_df)
    except DataQualityError as e:
        print(f"\nData quality check FAILED before load: {e}")
        conn.close()
        sys.exit(1)
    print("Pre-load checks passed.")

    customers_df.to_sql("customers", conn, if_exists="append", index=False)
    loans_df.to_sql("loans", conn, if_exists="append", index=False)
    repayments_df.to_sql("repayments", conn, if_exists="append", index=False)

    conn.commit()

    print("Running post-load data quality checks...")
    try:
        check_row_counts_match(conn, "customers", len(customers_df))
        check_row_counts_match(conn, "loans", len(loans_df))
        check_row_counts_match(conn, "repayments", len(repayments_df))

        check_foreign_keys(conn, "loans", "customer_id", "customers", "customer_id")
        check_foreign_keys(conn, "repayments", "loan_id", "loans", "loan_id")
    except DataQualityError as e:
        print(f"\nData quality check FAILED after load: {e}")
        conn.close()
        sys.exit(1)
    print("Post-load checks passed.")

    counts = conn.execute(
        "SELECT (SELECT COUNT(*) FROM customers), (SELECT COUNT(*) FROM loans), (SELECT COUNT(*) FROM repayments)"
    ).fetchone()
    print(f"\nLoaded -> customers: {counts[0]}, loans: {counts[1]}, repayments: {counts[2]}")

    conn.close()


if __name__ == "__main__":
    main()