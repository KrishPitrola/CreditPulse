"""
test_schema.py
---------------
Verifies the schema itself behaves as designed: primary keys reject
duplicates, foreign keys reject orphans (with PRAGMA foreign_keys ON),
and the CHECK constraint on loan_status rejects invalid values.

These tests catch schema regressions -- e.g. if someone edits
schema.sql and accidentally drops a constraint, these fail loudly.
"""

import sqlite3
import pytest


def test_customers_table_created(db_conn):
    tables = db_conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    table_names = {t[0] for t in tables}
    assert {"customers", "loans", "repayments"}.issubset(table_names)


def test_duplicate_primary_key_rejected(db_conn):
    db_conn.execute(
        "INSERT INTO customers VALUES (1, 'Alice', 30, 50000, 700, 'Mumbai', 'Salaried', '2024-01-01')"
    )
    with pytest.raises(sqlite3.IntegrityError):
        db_conn.execute(
            "INSERT INTO customers VALUES (1, 'Bob', 25, 40000, 650, 'Pune', 'Self-Employed', '2024-01-02')"
        )


def test_orphan_foreign_key_rejected(db_conn):
    # No customer with id 999 exists -- this loan should be rejected
    with pytest.raises(sqlite3.IntegrityError):
        db_conn.execute(
            "INSERT INTO loans VALUES (1, 999, 100000, 12, 8.5, 'Personal', 'Current', '2024-01-01')"
        )


def test_valid_foreign_key_accepted(db_conn):
    db_conn.execute(
        "INSERT INTO customers VALUES (1, 'Alice', 30, 50000, 700, 'Mumbai', 'Salaried', '2024-01-01')"
    )
    db_conn.execute(
        "INSERT INTO loans VALUES (1, 1, 100000, 12, 8.5, 'Personal', 'Current', '2024-01-01')"
    )
    db_conn.commit()
    row = db_conn.execute("SELECT * FROM loans WHERE loan_id = 1").fetchone()
    assert row is not None


def test_invalid_loan_status_rejected(db_conn):
    db_conn.execute(
        "INSERT INTO customers VALUES (1, 'Alice', 30, 50000, 700, 'Mumbai', 'Salaried', '2024-01-01')"
    )
    with pytest.raises(sqlite3.IntegrityError):
        db_conn.execute(
            "INSERT INTO loans VALUES (1, 1, 100000, 12, 8.5, 'Personal', 'Overdue', '2024-01-01')"
        )