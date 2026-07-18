-- Singular test: a dbt test passes if this query returns ZERO rows.
-- Here, it fails if any region's default rate falls outside a valid
-- percentage range -- catching a calculation bug that a generic
-- not_null/unique test wouldn't.

select *
from {{ ref('default_rate_by_region') }}
where default_rate_pct < 0 or default_rate_pct > 100
