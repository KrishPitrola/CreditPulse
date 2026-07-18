select
    l.loan_status,
    round(avg(r.days_late), 2) as avg_days_late
from "credit_pipeline"."public"."stg_loans" l
join "credit_pipeline"."public"."stg_repayments" r on l.loan_id = r.loan_id
group by l.loan_status
order by avg_days_late desc