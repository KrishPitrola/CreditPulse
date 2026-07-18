
    
    

select
    repayment_id as unique_field,
    count(*) as n_records

from "credit_pipeline"."public"."stg_repayments"
where repayment_id is not null
group by repayment_id
having count(*) > 1


