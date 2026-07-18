
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select credit_score
from "credit_pipeline"."public"."stg_customers"
where credit_score is null



  
  
      
    ) dbt_internal_test