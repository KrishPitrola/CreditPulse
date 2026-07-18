select
    loan_id,
    customer_id,
    loan_amount,
    term_months,
    interest_rate,
    purpose,
    loan_status,
    disbursed_date
from {{ source('raw', 'loans') }}
