-- Each door's velocity in its first eight weeks on shelf, compared with the
-- median of every door of the same type over its own first eight weeks.
-- Velocity here is units per SKU per week, so a door that took one SKU is
-- not penalized next to a door that took four.
-- A door far below its peers usually has an execution problem (product in
-- the back room, missing shelf tag, bad placement), not a demand problem.

create or replace table new_door_ramp as
with doors as (
    select store_id, store_name, region, store_type,
           cast(date_trunc('month', first_order_date) as date)   as cohort_month
    from stg_stores
    where shares_pos
),
door_weeks as (
    select
        d.*,
        p.week_start,
        p.units,
        min(p.week_start) over (partition by p.store_id)        as first_week
    from doors d
    join stg_pos p using (store_id)
),
per_door as (
    select
        store_id, store_name, region, store_type, cohort_month,
        count(distinct week_start)                              as weeks_counted,
        round(sum(units) / count(*), 2)                         as units_per_sku_week
    from door_weeks
    where week_start < first_week + interval 8 week
    group by all
    having count(distinct week_start) >= 4
),
scored as (
    select
        *,
        round(median(units_per_sku_week) over (partition by store_type), 2) as peer_median,
        count(*) over (partition by store_type)                  as peer_count
    from per_door
)
select
    *,
    round(units_per_sku_week / nullif(peer_median, 0), 2)       as vs_peers,
    units_per_sku_week < 0.5 * peer_median                      as lagging
from scored
where peer_count >= 5
order by vs_peers;
