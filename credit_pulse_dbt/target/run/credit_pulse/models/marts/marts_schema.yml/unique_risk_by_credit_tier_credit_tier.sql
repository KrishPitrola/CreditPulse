
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    credit_tier as unique_field,
    count(*) as n_records

from "credit_pipeline"."public"."risk_by_credit_tier"
where credit_tier is not null
group by credit_tier
having count(*) > 1



  
  
      
    ) dbt_internal_test