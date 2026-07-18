
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with all_values as (

    select
        loan_status as value_field,
        count(*) as n_records

    from "credit_pipeline"."public"."stg_loans"
    group by loan_status

)

select *
from all_values
where value_field not in (
    'Current','Paid Off','Default'
)



  
  
      
    ) dbt_internal_test