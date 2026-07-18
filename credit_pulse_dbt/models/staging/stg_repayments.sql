select
    repayment_id,
    loan_id,
    payment_date,
    amount_paid,
    days_late
from {{ source('raw', 'repayments') }}
