
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with child as (
    select loan_id as from_field
    from "credit_pipeline"."public"."stg_repayments"
    where loan_id is not null
),

parent as (
    select loan_id as to_field
    from "credit_pipeline"."public"."stg_loans"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null



  
  
      
    ) dbt_internal_test