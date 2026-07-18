
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    repayment_id as unique_field,
    count(*) as n_records

from "credit_pipeline"."public"."stg_repayments"
where repayment_id is not null
group by repayment_id
having count(*) > 1



  
  
      
    ) dbt_internal_test