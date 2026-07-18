
  create view "credit_pipeline"."public"."stg_repayments__dbt_tmp"
    
    
  as (
    select
    repayment_id,
    loan_id,
    payment_date,
    amount_paid,
    days_late
from "credit_pipeline"."public"."repayments"
  );