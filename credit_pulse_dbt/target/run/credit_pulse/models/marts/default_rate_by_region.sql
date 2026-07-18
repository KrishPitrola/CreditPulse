
  
    

  create  table "credit_pipeline"."public"."default_rate_by_region__dbt_tmp"
  
  
    as
  
  (
    select
    c.region,
    count(*) as total_loans,
    sum(case when l.loan_status = 'Default' then 1 else 0 end) as defaults,
    round(
        100.0 * sum(case when l.loan_status = 'Default' then 1 else 0 end) / count(*),
        2
    ) as default_rate_pct
from "credit_pipeline"."public"."stg_loans" l
join "credit_pipeline"."public"."stg_customers" c on l.customer_id = c.customer_id
group by c.region
order by default_rate_pct desc
  );
  