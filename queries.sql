-- queries.sql
-- Real business questions answered with real SQL, covering exactly
-- the concepts IDFC's interview doc mentions: joins, window functions,
-- CTEs, aggregates, subqueries. Rehearse explaining EACH of these
-- out loud -- what it does and why you wrote it that way.

-- ===========================================================
-- 1) INNER JOIN: loan details with the customer who took them
-- ===========================================================
SELECT l.loan_id, c.name, c.region, l.loan_amount, l.loan_status
FROM loans l
INNER JOIN customers c ON l.customer_id = c.customer_id
LIMIT 10;


-- ===========================================================
-- 2) LEFT JOIN: every customer, even those with zero loans
--    (tests your understanding of NULLs from the right table)
-- ===========================================================
SELECT c.customer_id, c.name, COUNT(l.loan_id) AS total_loans
FROM customers c
LEFT JOIN loans l ON c.customer_id = l.customer_id
GROUP BY c.customer_id, c.name
ORDER BY total_loans ASC
LIMIT 10;


-- ===========================================================
-- 3) Default rate by region (GROUP BY + aggregate + CASE)
-- ===========================================================
SELECT
    c.region,
    COUNT(*) AS total_loans,
    SUM(CASE WHEN l.loan_status = 'Default' THEN 1 ELSE 0 END) AS defaults,
    ROUND(100.0 * SUM(CASE WHEN l.loan_status = 'Default' THEN 1 ELSE 0 END) / COUNT(*), 2) AS default_rate_pct
FROM loans l
JOIN customers c ON l.customer_id = c.customer_id
GROUP BY c.region
ORDER BY default_rate_pct DESC;


-- ===========================================================
-- 4) CTE: credit-score tiers, then aggregate on top of the CTE
-- ===========================================================
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
ORDER BY defaults DESC;


-- ===========================================================
-- 5) WINDOW FUNCTION: rank customers by total loan amount
--    within their own region (PARTITION BY)
-- ===========================================================
SELECT
    c.region,
    c.name,
    SUM(l.loan_amount) AS total_borrowed,
    RANK() OVER (PARTITION BY c.region ORDER BY SUM(l.loan_amount) DESC) AS rank_in_region
FROM customers c
JOIN loans l ON c.customer_id = l.customer_id
GROUP BY c.region, c.customer_id, c.name
ORDER BY c.region, rank_in_region
LIMIT 20;


-- ===========================================================
-- 6) WINDOW FUNCTION: running total of disbursed loan amount
--    over time (classic "running totals" interview question)
-- ===========================================================
SELECT
    disbursed_date,
    loan_amount,
    SUM(loan_amount) OVER (ORDER BY disbursed_date) AS running_total_disbursed
FROM loans
ORDER BY disbursed_date
LIMIT 20;


-- ===========================================================
-- 7) Nth highest value (classic "Nth highest salary"-style question,
--    reframed as Nth highest loan amount)
-- ===========================================================
SELECT DISTINCT loan_amount
FROM loans
ORDER BY loan_amount DESC
LIMIT 1 OFFSET 2;   -- OFFSET 2 -> 3rd highest distinct loan amount


-- ===========================================================
-- 8) Correlated subquery: customers whose most recent loan
--    is currently in Default
-- ===========================================================
SELECT c.customer_id, c.name
FROM customers c
WHERE (
    SELECT l.loan_status
    FROM loans l
    WHERE l.customer_id = c.customer_id
    ORDER BY l.disbursed_date DESC
    LIMIT 1
) = 'Default';


-- ===========================================================
-- 9) Repayment behavior: average days late per loan, joined
--    back to loan status -- do late payers actually default more?
-- ===========================================================
SELECT
    l.loan_status,
    ROUND(AVG(r.days_late), 2) AS avg_days_late
FROM loans l
JOIN repayments r ON l.loan_id = r.loan_id
GROUP BY l.loan_status
ORDER BY avg_days_late DESC;
