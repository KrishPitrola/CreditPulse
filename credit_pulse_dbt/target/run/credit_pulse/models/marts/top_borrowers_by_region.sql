
  
    

  create  table "credit_pipeline"."public"."top_borrowers_by_region__dbt_tmp"
  
  
    as
  
  (
    select
    c.region,
    c.name,
    sum(l.loan_amount) as total_borrowed,
    rank() over (
        partition by c.region
        order by sum(l.loan_amount) desc
    ) as rank_in_region
from "credit_pipeline"."public"."stg_customers" c
join "credit_pipeline"."public"."stg_loans" l on c.customer_id = l.customer_id
group by c.region, c.customer_id, c.name
order by c.region, rank_in_region
  );
  