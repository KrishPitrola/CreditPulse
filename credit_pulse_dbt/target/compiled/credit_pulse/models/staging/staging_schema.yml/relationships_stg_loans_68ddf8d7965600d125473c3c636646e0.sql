
    
    

with child as (
    select customer_id as from_field
    from "credit_pipeline"."public"."stg_loans"
    where customer_id is not null
),

parent as (
    select customer_id as to_field
    from "credit_pipeline"."public"."stg_customers"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null


