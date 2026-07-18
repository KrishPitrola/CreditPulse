-- schema.sql
-- Relational schema for the Credit Risk Analytics Pipeline.
-- Deliberately normalized into 3 tables so real joins are required
-- to answer any interesting business question.

DROP TABLE IF EXISTS repayments;
DROP TABLE IF EXISTS loans;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id     INTEGER PRIMARY KEY,
    name            TEXT NOT NULL,
    age             INTEGER NOT NULL,
    monthly_income  INTEGER NOT NULL,
    credit_score    INTEGER NOT NULL,
    region          TEXT NOT NULL,
    employment_type TEXT NOT NULL,
    signup_date     TEXT NOT NULL
);

CREATE TABLE loans (
    loan_id         INTEGER PRIMARY KEY,
    customer_id     INTEGER NOT NULL,
    loan_amount     INTEGER NOT NULL,
    term_months     INTEGER NOT NULL,
    interest_rate   REAL NOT NULL,
    purpose         TEXT NOT NULL,
    loan_status     TEXT NOT NULL CHECK (loan_status IN ('Current', 'Paid Off', 'Default')),
    disbursed_date  TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE repayments (
    repayment_id    INTEGER PRIMARY KEY,
    loan_id         INTEGER NOT NULL,
    payment_date    TEXT NOT NULL,
    amount_paid     REAL NOT NULL,
    days_late       INTEGER NOT NULL,
    FOREIGN KEY (loan_id) REFERENCES loans(loan_id)
);

CREATE INDEX idx_loans_customer_id ON loans(customer_id);
CREATE INDEX idx_repayments_loan_id ON repayments(loan_id);
