
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  -- Singular test: a dbt test passes if this query returns ZERO rows.
-- Here, it fails if any region's default rate falls outside a valid
-- percentage range -- catching a calculation bug that a generic
-- not_null/unique test wouldn't.

select *
from "credit_pipeline"."public"."default_rate_by_region"
where default_rate_pct < 0 or default_rate_pct > 100
  
  
      
    ) dbt_internal_test