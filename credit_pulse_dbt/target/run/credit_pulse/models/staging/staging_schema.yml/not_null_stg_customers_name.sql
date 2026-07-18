
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select name
from "credit_pipeline"."public"."stg_customers"
where name is null



  
  
      
    ) dbt_internal_test