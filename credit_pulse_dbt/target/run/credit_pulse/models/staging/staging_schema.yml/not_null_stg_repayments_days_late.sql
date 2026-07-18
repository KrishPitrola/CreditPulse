
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select days_late
from "credit_pipeline"."public"."stg_repayments"
where days_late is null



  
  
      
    ) dbt_internal_test