"""
conftest.py
-----------
Shared pytest fixtures. `db_conn` builds a brand-new, isolated
in-memory SQLite database from the real schema.sql for every test
that uses it -- no dependency on credit_pipeline.db, and no risk of
one test's data leaking into another.
"""

import os
import sqlite3
import pytest

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "schema.sql")


@pytest.fixture
def db_conn():
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON;")
    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())
    yield conn
    conn.close()