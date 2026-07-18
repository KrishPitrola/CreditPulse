
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select loan_status
from "credit_pipeline"."public"."late_payment_vs_default"
where loan_status is null



  
  
      
    ) dbt_internal_test