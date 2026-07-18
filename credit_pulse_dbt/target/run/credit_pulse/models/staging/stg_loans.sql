
  create view "credit_pipeline"."public"."stg_loans__dbt_tmp"
    
    
  as (
    select
    loan_id,
    customer_id,
    loan_amount,
    term_months,
    interest_rate,
    purpose,
    loan_status,
    disbursed_date
from "credit_pipeline"."public"."loans"
  );