
    
    

select
    region as unique_field,
    count(*) as n_records

from "credit_pipeline"."public"."default_rate_by_region"
where region is not null
group by region
having count(*) > 1


