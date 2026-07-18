with scored_customers as (
    select
        customer_id,
        credit_score,
        case
            when credit_score >= 750 then 'Excellent'
            when credit_score >= 650 then 'Good'
            when credit_score >= 550 then 'Fair'
            else 'Poor'
        end as credit_tier
    from {{ ref('stg_customers') }}
)

select
    sc.credit_tier,
    count(distinct l.loan_id) as total_loans,
    round(avg(l.loan_amount), 2) as avg_loan_amount,
    sum(case when l.loan_status = 'Default' then 1 else 0 end) as defaults
from scored_customers sc
join {{ ref('stg_loans') }} l on sc.customer_id = l.customer_id
group by sc.credit_tier
order by defaults desc
