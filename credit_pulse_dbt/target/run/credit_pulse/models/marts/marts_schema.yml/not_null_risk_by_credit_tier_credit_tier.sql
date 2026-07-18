
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select credit_tier
from "credit_pipeline"."public"."risk_by_credit_tier"
where credit_tier is null



  
  
      
    ) dbt_internal_test