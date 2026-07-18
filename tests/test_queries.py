"""
test_queries.py
-----------------
Loads a small, hand-built dataset (5 customers, known loan statuses)
into a fresh in-memory database and checks that the analytical SQL
returns the exact expected numbers. This validates the query logic
itself, not just that the pipeline runs without crashing.
"""


def seed_known_data(db_conn):
    """3 loans in Mumbai (2 default), 2 loans in Pune (0 default)."""
    customers = [
        (1, "Alice", 30, 50000, 700, "Mumbai", "Salaried", "2024-01-01"),
        (2, "Bob", 25, 40000, 650, "Mumbai", "Salaried", "2024-01-01"),
        (3, "Cara", 35, 60000, 720, "Mumbai", "Salaried", "2024-01-01"),
        (4, "Dan", 28, 45000, 680, "Pune", "Self-Employed", "2024-01-01"),
        (5, "Eve", 40, 70000, 750, "Pune", "Salaried", "2024-01-01"),
    ]
    db_conn.executemany(
        "INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?, ?, ?)", customers
    )

    loans = [
        (1, 1, 100000, 12, 8.5, "Personal", "Default", "2024-01-01"),
        (2, 2, 150000, 24, 9.0, "Home", "Default", "2024-01-01"),
        (3, 3, 50000, 6, 7.5, "Personal", "Paid Off", "2024-01-01"),
        (4, 4, 200000, 36, 10.0, "Business", "Current", "2024-01-01"),
        (5, 5, 80000, 12, 8.0, "Personal", "Paid Off", "2024-01-01"),
    ]
    db_conn.executemany(
        "INSERT INTO loans VALUES (?, ?, ?, ?, ?, ?, ?, ?)", loans
    )
    db_conn.commit()


def test_default_rate_by_region(db_conn):
    seed_known_data(db_conn)

    query = """
        SELECT
            c.region,
            COUNT(*) AS total_loans,
            SUM(CASE WHEN l.loan_status = 'Default' THEN 1 ELSE 0 END) AS defaults,
            ROUND(100.0 * SUM(CASE WHEN l.loan_status = 'Default' THEN 1 ELSE 0 END) / COUNT(*), 2) AS default_rate_pct
        FROM loans l
        JOIN customers c ON l.customer_id = c.customer_id
        GROUP BY c.region
        ORDER BY default_rate_pct DESC
    """
    results = {row[0]: row for row in db_conn.execute(query).fetchall()}

    # Mumbai: 3 loans, 2 defaults -> 66.67%
    assert results["Mumbai"][1] == 3
    assert results["Mumbai"][2] == 2
    assert results["Mumbai"][3] == 66.67

    # Pune: 2 loans, 0 defaults -> 0.0%
    assert results["Pune"][1] == 2
    assert results["Pune"][2] == 0
    assert results["Pune"][3] == 0.0


def test_third_highest_loan_amount(db_conn):
    seed_known_data(db_conn)

    query = """
        SELECT DISTINCT loan_amount
        FROM loans
        ORDER BY loan_amount DESC
        LIMIT 1 OFFSET 2
    """
    result = db_conn.execute(query).fetchone()

    # Loan amounts sorted desc: 200000, 150000, 100000, 80000, 50000
    # 3rd highest -> 100000
    assert result[0] == 100000