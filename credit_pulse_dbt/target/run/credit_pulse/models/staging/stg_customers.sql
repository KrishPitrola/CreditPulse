
  create view "credit_pipeline"."public"."stg_customers__dbt_tmp"
    
    
  as (
    -- Thin pass-through view over the raw customers table. Staging
-- models exist so downstream marts never reference raw sources
-- directly -- if the raw schema changes, only this file needs to
-- change, not every mart built on top of it.

select
    customer_id,
    name,
    age,
    monthly_income,
    credit_score,
    region,
    employment_type,
    signup_date
from "credit_pipeline"."public"."customers"
  );