-- Velocity = units sold per store, per SKU, per week, counting only
-- store-weeks where the SKU was actually on the shelf (had a POS row).
-- Distribution = how many doors carried the SKU in the window.

create or replace table sku_velocity as
with window_pos as (
    select *
    from stg_pos
    where week_start >= date '{as_of}' - interval 12 week
      and week_start <  date '{as_of}'
)
select
    p.sku,
    k.sku_name,
    count(distinct p.store_id)                                  as doors_selling,
    count(*)                                                    as store_weeks,
    sum(p.units)                                                as units,
    round(sum(p.units) / count(*), 2)                           as units_per_store_week,
    round(sum(p.units * k.unit_price) / count(*), 2)            as dollars_per_store_week
from window_pos p
join stg_skus k using (sku)
group by all
order by units_per_store_week desc;

create or replace table region_velocity as
select
    s.region,
    s.store_type,
    count(distinct p.store_id)                                  as doors,
    round(sum(p.units) / count(*), 2)                           as units_per_store_week
from stg_pos p
join stg_stores s using (store_id)
where p.week_start >= date '{as_of}' - interval 12 week
  and p.week_start <  date '{as_of}'
group by all
order by units_per_store_week desc;

create or replace table weekly_trend as
select
    week_start,
    count(distinct store_id)                                    as doors_reporting,
    sum(units)                                                  as units,
    round(sum(units) / count(distinct store_id), 2)             as units_per_door
from stg_pos
group by all
order by week_start;
