
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select default_rate_pct
from "credit_pipeline"."public"."default_rate_by_region"
where default_rate_pct is null



  
  
      
    ) dbt_internal_test