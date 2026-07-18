"""
api.py
------
Minimal FastAPI layer serving the analytics pipeline's SQL queries
as HTTP endpoints -- this is the "final output" step: raw data ->
cleaned -> loaded -> queried -> served.

Run with:
    uvicorn api:app --reload
Then open:
    http://127.0.0.1:8000/docs
"""

import sqlite3
from fastapi import FastAPI

app = FastAPI(title="Credit Risk Analytics Pipeline")

DB_PATH = "credit_pipeline.db"


def query_db(sql: str, params: tuple = ()):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.execute(sql, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


@app.get("/")
def root():
    return {"message": "Credit Risk Analytics Pipeline API. See /docs for endpoints."}


@app.get("/default-rate-by-region")
def default_rate_by_region():
    """Default rate % per region -- GROUP BY + conditional aggregate."""
    sql = """
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
    return query_db(sql)


@app.get("/risk-by-credit-tier")
def risk_by_credit_tier():
    """Default counts + avg loan amount bucketed by credit-score tier -- CTE."""
    sql = """
        WITH scored_customers AS (
            SELECT
                customer_id,
                credit_score,
                CASE
                    WHEN credit_score >= 750 THEN 'Excellent'
                    WHEN credit_score >= 650 THEN 'Good'
                    WHEN credit_score >= 550 THEN 'Fair'
                    ELSE 'Poor'
                END AS credit_tier
            FROM customers
        )
        SELECT
            sc.credit_tier,
            COUNT(DISTINCT l.loan_id) AS total_loans,
            ROUND(AVG(l.loan_amount), 2) AS avg_loan_amount,
            SUM(CASE WHEN l.loan_status = 'Default' THEN 1 ELSE 0 END) AS defaults
        FROM scored_customers sc
        JOIN loans l ON sc.customer_id = l.customer_id
        GROUP BY sc.credit_tier
        ORDER BY defaults DESC
    """
    return query_db(sql)


@app.get("/top-borrowers-by-region")
def top_borrowers_by_region(limit: int = 20):
    """Rank customers by total borrowed amount within their region -- window function."""
    sql = """
        SELECT
            c.region,
            c.name,
            SUM(l.loan_amount) AS total_borrowed,
            RANK() OVER (PARTITION BY c.region ORDER BY SUM(l.loan_amount) DESC) AS rank_in_region
        FROM customers c
        JOIN loans l ON c.customer_id = l.customer_id
        GROUP BY c.region, c.customer_id, c.name
        ORDER BY c.region, rank_in_region
        LIMIT ?
    """
    return query_db(sql, (limit,))


@app.get("/late-payment-vs-default")
def late_payment_vs_default():
    """Average days late per loan status -- does late payment predict default?"""
    sql = """
        SELECT
            l.loan_status,
            ROUND(AVG(r.days_late), 2) AS avg_days_late
        FROM loans l
        JOIN repayments r ON l.loan_id = r.loan_id
        GROUP BY l.loan_status
        ORDER BY avg_days_late DESC
    """
    return query_db(sql)
