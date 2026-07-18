# Credit Risk Analytics Pipeline

[![CI](https://github.com/KrishPitrola/CreditPulse/actions/workflows/ci.yml/badge.svg)](https://github.com/KrishPitrola/CreditPulse/actions/workflows/ci.yml)

An end-to-end data engineering pipeline that models loan and repayment
behavior for a retail lending business — from raw data ingestion
through relational modeling, SQL analytics, distributed processing,
API delivery, containerized deployment, and cloud storage.

## Purpose

Lending institutions need to answer operational questions continuously:
Which regions carry the highest default risk? Which customers are the
largest borrowers? Does late payment history predict default? This
project builds the infrastructure to answer those questions — a
reproducible pipeline that takes raw transactional data and turns it
into queryable, servable insight.

It's intentionally built end-to-end rather than deep in only one
layer: schema design, SQL analytics, a processing engine, an API, a
container, and cloud storage all have to work together and agree with
each other. That integration is the point — a correct SQL query is
easy in isolation; a query that's correct, served over an API, wrapped
in a container, and backed by validated data is a different (and more
realistic) problem.

## Architecture

```
CSVs (raw ingestion)
  → SQLite (normalized relational schema)
  → SQL analytics (joins, CTEs, window functions, subqueries)
      → served via FastAPI (HTTP endpoints)
      → containerized via Docker
  → PySpark (DataFrame-based reimplementation of key analyses)
  → raw CSVs also archived to AWS S3 (raw zone pattern)
```

## Data

The dataset is synthetically generated (via Faker + numpy) to model
realistic loan/repayment behavior: 2,000 customers, 3,000 loans, and
~25,000 repayment records, with relationships and distributions
designed to resemble real lending data (regional variation in default
rates, credit-tier risk gradients, late-payment correlation with
default).

## Schema

Three normalized tables, linked by foreign key:

```
customers (customer_id PK, name, age, monthly_income, credit_score, region, employment_type, signup_date)
loans (loan_id PK, customer_id FK, loan_amount, term_months, interest_rate, purpose, loan_status, disbursed_date)
repayments (repayment_id PK, loan_id FK, payment_date, amount_paid, days_late)
```

## Components

| File | Role |
|---|---|
| `generate_data.py` | Generates synthetic customers/loans/repayments CSVs |
| `schema.sql` | Normalized 3-table relational schema with PK/FK constraints |
| `load_data.py` | Loads CSVs into a SQLite database |
| `queries.sql` | 9 analytical SQL queries (see below) |
| `api.py` | FastAPI service exposing key queries as HTTP endpoints |
| `pyspark_transform.py` | Reimplements two analyses using PySpark's DataFrame API |
| `Dockerfile` | Containerizes the FastAPI service |
| `s3_upload.py` | Uploads raw CSVs to an S3 bucket (raw data zone) |

## SQL queries and what they demonstrate

| # | Query | Concept |
|---|-------|---|
| 1 | Loan + customer details | INNER JOIN |
| 2 | Customers with loan counts, incl. zero | LEFT JOIN + NULL handling |
| 3 | Default rate by region | GROUP BY + conditional aggregate (CASE) |
| 4 | Risk by credit tier | CTE |
| 5 | Top borrowers per region | Window function (RANK, PARTITION BY) |
| 6 | Running total of disbursed loans | Window function (SUM OVER) |
| 7 | 3rd highest loan amount | Nth-highest pattern |
| 8 | Customers whose latest loan defaulted | Correlated subquery |
| 9 | Late payments vs. default status | 3-table JOIN + aggregate |

## How to run

```bash
pip install -r requirements.txt

# Generate and load data
python generate_data.py      # creates data/*.csv
python load_data.py          # loads CSVs into credit_pipeline.db

# Explore the SQL directly
sqlite3 credit_pipeline.db < queries.sql

# Serve over an API
uvicorn api:app --reload
# open http://127.0.0.1:8000/docs

# Run the PySpark version of two of the analyses
python pyspark_transform.py

# Upload raw CSVs to S3 (edit bucket name in s3_upload.py first)
python s3_upload.py

# Build and run the containerized API
docker build -t creditpulse-api .
docker run -p 8000:8000 creditpulse-api
```

## Design decisions

- **SQLite over Postgres/MySQL**: kept the project runnable with zero
  external setup — no server to install or credentials to manage.
  The schema and queries are standard SQL and would port to Postgres
  with minimal change.
- **Synthetic data over Kaggle datasets**: generating the data means
  full control over relationships (e.g. engineered regional default
  variation, credit-tier risk gradients) and no licensing ambiguity.
- **Local PySpark over a managed cluster (EMR/Glue)**: demonstrates
  the DataFrame API and distributed-processing mental model without
  the cost, setup complexity, and operational risk of a live cluster
  for a project this size.
- **S3 for raw storage, without Athena/Glue/Terraform on top**: S3
  models the "raw zone" of a real data lake. Athena/Glue/Terraform
  were deliberately left out — they'd add infrastructure surface
  area disproportionate to what this project needs to demonstrate.

## Possible extensions

- Migrate from SQLite to PostgreSQL (via Docker) for a more
  production-realistic setup
- Add a scheduler (cron or Python `schedule`) to simulate periodic
  ingestion
- Add a Streamlit dashboard on top of the API
- Add data quality checks in `load_data.py` (orphan FK detection,
  range validation on amounts/rates)
- Add unit tests against the SQLite database (row counts, aggregate
  sanity checks)