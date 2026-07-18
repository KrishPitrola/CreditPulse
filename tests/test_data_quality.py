"""
test_data_quality.py
---------------------
Tests the validation functions in load_data.py directly, using small
hand-built DataFrames -- some valid, some deliberately broken -- to
prove each check actually catches the problem it claims to, not just
that it passes on already-clean data.
"""

import os
import sys
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from load_data import (
    validate_customers,
    validate_loans,
    validate_repayments,
    DataQualityError,
)


def make_customers_df(**overrides):
    base = {
        "customer_id": [1, 2],
        "name": ["Alice", "Bob"],
        "age": [30, 25],
        "monthly_income": [50000, 40000],
        "credit_score": [700, 650],
        "region": ["Mumbai", "Pune"],
        "employment_type": ["Salaried", "Self-Employed"],
        "signup_date": ["2024-01-01", "2024-01-02"],
    }
    base.update(overrides)
    return pd.DataFrame(base)


def make_loans_df(**overrides):
    base = {
        "loan_id": [1, 2],
        "customer_id": [1, 2],
        "loan_amount": [100000, 200000],
        "term_months": [12, 24],
        "interest_rate": [8.5, 9.0],
        "purpose": ["Personal", "Home"],
        "loan_status": ["Current", "Paid Off"],
        "disbursed_date": ["2024-01-01", "2024-01-02"],
    }
    base.update(overrides)
    return pd.DataFrame(base)


def make_repayments_df(**overrides):
    base = {
        "repayment_id": [1, 2],
        "loan_id": [1, 2],
        "payment_date": ["2024-02-01", "2024-02-02"],
        "amount_paid": [5000.0, 8000.0],
        "days_late": [0, 3],
    }
    base.update(overrides)
    return pd.DataFrame(base)


# --- customers ---

def test_valid_customers_passes():
    validate_customers(make_customers_df())  # should not raise


def test_customers_null_name_rejected():
    df = make_customers_df(name=["Alice", None])
    with pytest.raises(DataQualityError):
        validate_customers(df)


def test_customers_duplicate_pk_rejected():
    df = make_customers_df(customer_id=[1, 1])
    with pytest.raises(DataQualityError):
        validate_customers(df)


def test_customers_credit_score_out_of_range_rejected():
    df = make_customers_df(credit_score=[700, 1200])  # 1200 is out of the 300-900 range
    with pytest.raises(DataQualityError):
        validate_customers(df)


def test_customers_negative_income_rejected():
    df = make_customers_df(monthly_income=[50000, -1000])
    with pytest.raises(DataQualityError):
        validate_customers(df)


# --- loans ---

def test_valid_loans_passes():
    validate_loans(make_loans_df())  # should not raise


def test_loans_negative_amount_rejected():
    df = make_loans_df(loan_amount=[100000, -500])
    with pytest.raises(DataQualityError):
        validate_loans(df)


def test_loans_duplicate_pk_rejected():
    df = make_loans_df(loan_id=[1, 1])
    with pytest.raises(DataQualityError):
        validate_loans(df)


# --- repayments ---

def test_valid_repayments_passes():
    validate_repayments(make_repayments_df())  # should not raise


def test_repayments_negative_days_late_rejected():
    df = make_repayments_df(days_late=[0, -5])
    with pytest.raises(DataQualityError):
        validate_repayments(df)