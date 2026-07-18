
    
    

with all_values as (

    select
        credit_tier as value_field,
        count(*) as n_records

    from "credit_pipeline"."public"."risk_by_credit_tier"
    group by credit_tier

)

select *
from all_values
where value_field not in (
    'Excellent','Good','Fair','Poor'
)


