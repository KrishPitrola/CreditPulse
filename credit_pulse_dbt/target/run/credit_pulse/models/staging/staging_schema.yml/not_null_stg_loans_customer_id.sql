
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select customer_id
from "credit_pipeline"."public"."stg_loans"
where customer_id is null



  
  
      
    ) dbt_internal_test