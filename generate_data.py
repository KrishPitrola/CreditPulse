"""
generate_data.py
----------------
Generates a synthetic (but realistic) loan/credit dataset for the
Credit Risk Analytics Pipeline project.

NOTE: This is synthetic data, generated to unblock pipeline development
quickly. Swap in a real dataset (e.g. Kaggle 'Give Me Some Credit' or
'Lending Club Loan Data') later if you want, without changing the schema
or downstream SQL.
"""

import random
import numpy as np
import pandas as pd
from datetime import date, timedelta
from faker import Faker

fake = Faker()
random.seed(42)
np.random.seed(42)

N_CUSTOMERS = 2000
N_LOANS = 3000

REGIONS = ["Mumbai", "Delhi", "Bengaluru", "Chennai", "Pune", "Hyderabad", "Kolkata", "Ahmedabad"]
EMPLOYMENT_TYPES = ["Salaried", "Self-Employed", "Business Owner", "Freelancer"]
LOAN_PURPOSES = ["Home Renovation", "Education", "Medical", "Vehicle", "Business Expansion", "Wedding", "Debt Consolidation"]
LOAN_STATUSES = ["Current", "Paid Off", "Default"]


def random_date(start_year=2022, end_year=2026):
    start = date(start_year, 1, 1)
    end = date(end_year, 6, 1)
    delta_days = (end - start).days
    return start + timedelta(days=random.randint(0, delta_days))


# ---------- CUSTOMERS ----------
customers = []
for cust_id in range(1, N_CUSTOMERS + 1):
    age = int(np.clip(np.random.normal(38, 11), 21, 70))
    income = int(np.clip(np.random.lognormal(mean=10.8, sigma=0.5), 15000, 500000))
    credit_score = int(np.clip(np.random.normal(680, 80), 300, 900))
    customers.append({
        "customer_id": cust_id,
        "name": fake.name(),
        "age": age,
        "monthly_income": income,
        "credit_score": credit_score,
        "region": random.choice(REGIONS),
        "employment_type": random.choice(EMPLOYMENT_TYPES),
        "signup_date": random_date(2021, 2025).isoformat(),
    })
customers_df = pd.DataFrame(customers)

# ---------- LOANS ----------
loans = []
for loan_id in range(1, N_LOANS + 1):
    cust = customers_df.sample(1).iloc[0]
    loan_amount = int(np.clip(np.random.lognormal(mean=10.5, sigma=0.6), 10000, 2000000))
    term_months = random.choice([6, 12, 24, 36, 48, 60])
    interest_rate = round(random.uniform(9.5, 22.0), 2)
    disbursed = random_date(2022, 2026)

    # Higher default probability for lower credit score / higher loan-to-income ratio
    loan_to_income_ratio = loan_amount / max(cust["monthly_income"] * term_months, 1)
    default_risk = (900 - cust["credit_score"]) / 600 + loan_to_income_ratio * 2
    default_risk = np.clip(default_risk, 0, 0.9)
    status = np.random.choice(
        LOAN_STATUSES,
        p=[0.45, 1 - 0.45 - default_risk, default_risk] if (1 - 0.45 - default_risk) > 0 else [0.5, 0.4, 0.1]
    )

    loans.append({
        "loan_id": loan_id,
        "customer_id": int(cust["customer_id"]),
        "loan_amount": loan_amount,
        "term_months": term_months,
        "interest_rate": interest_rate,
        "purpose": random.choice(LOAN_PURPOSES),
        "loan_status": status,
        "disbursed_date": disbursed.isoformat(),
    })
loans_df = pd.DataFrame(loans)

# ---------- REPAYMENTS ----------
repayments = []
repayment_id = 1
for _, loan in loans_df.iterrows():
    n_payments = random.randint(2, min(loan["term_months"], 18))
    disbursed = date.fromisoformat(loan["disbursed_date"])
    for i in range(n_payments):
        payment_date = disbursed + timedelta(days=30 * (i + 1))
        # Days late correlates loosely with eventual default
        late_bias = 15 if loan["loan_status"] == "Default" else 2
        days_late = max(0, int(np.random.exponential(late_bias)))
        emi = round(loan["loan_amount"] / loan["term_months"], 2)
        repayments.append({
            "repayment_id": repayment_id,
            "loan_id": int(loan["loan_id"]),
            "payment_date": payment_date.isoformat(),
            "amount_paid": emi,
            "days_late": days_late,
        })
        repayment_id += 1
repayments_df = pd.DataFrame(repayments)

# ---------- SAVE ----------
customers_df.to_csv("data/customers.csv", index=False)
loans_df.to_csv("data/loans.csv", index=False)
repayments_df.to_csv("data/repayments.csv", index=False)

print(f"Generated {len(customers_df)} customers, {len(loans_df)} loans, {len(repayments_df)} repayments")
print(loans_df["loan_status"].value_counts())
