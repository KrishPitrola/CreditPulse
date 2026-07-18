
    
    

select
    loan_status as unique_field,
    count(*) as n_records

from "credit_pipeline"."public"."late_payment_vs_default"
where loan_status is not null
group by loan_status
having count(*) > 1


