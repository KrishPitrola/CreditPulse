
    
    

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


