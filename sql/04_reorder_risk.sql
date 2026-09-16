-- Each store's normal reorder rhythm, and whether it has gone quiet.
-- A store is overdue when the days since its last order exceed 1.5x its own
-- median gap between orders (with a floor, so one early reorder does not
-- make every store look late).

create or replace table store_reorder_health as
with store_orders as (
    select store_id, order_date, sum(net_revenue) as revenue
    from stg_orders
    group by all
),
gaps as (
    select
        store_id,
        order_date,
        revenue,
        datediff('day', lag(order_date) over (partition by store_id order by order_date), order_date) as gap_days
    from store_orders
),
per_store as (
    select
        store_id,
        count(*)                                                as orders,
        max(order_date)                                         as last_order_date,
        median(gap_days)                                        as median_gap_days,
        round(sum(revenue), 2)                                  as lifetime_revenue,
        round(sum(revenue) filter (where order_date >= date '{as_of}' - interval 90 day), 2) as revenue_90d
    from gaps
    group by store_id
)
select
    s.store_id, s.store_name, s.region, s.store_type,
    p.orders,
    p.last_order_date,
    datediff('day', p.last_order_date, date '{as_of}')          as days_since_order,
    p.median_gap_days,
    greatest(coalesce(p.median_gap_days, 35), 21) * 1.5         as overdue_after_days,
    p.lifetime_revenue,
    coalesce(p.revenue_90d, 0)                                  as revenue_90d,
    case
        when p.orders < 2 then 'too new'
        when datediff('day', p.last_order_date, date '{as_of}') > 3 * greatest(coalesce(p.median_gap_days, 35), 21) then 'lapsed'
        when datediff('day', p.last_order_date, date '{as_of}') > 1.5 * greatest(coalesce(p.median_gap_days, 35), 21) then 'overdue'
        else 'on rhythm'
    end                                                         as status
from per_store p
join stg_stores s using (store_id)
order by status, lifetime_revenue desc;
