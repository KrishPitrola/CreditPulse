select
    c.region,
    c.name,
    sum(l.loan_amount) as total_borrowed,
    rank() over (
        partition by c.region
        order by sum(l.loan_amount) desc
    ) as rank_in_region
from {{ ref('stg_customers') }} c
join {{ ref('stg_loans') }} l on c.customer_id = l.customer_id
group by c.region, c.customer_id, c.name
order by c.region, rank_in_region
