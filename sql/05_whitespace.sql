-- Expansion list: stores in good standing that are missing a SKU which
-- sells well in similar stores. Estimated upside uses the SKU's velocity
-- in the same store type, 4.3 weeks a month.

create or replace table sku_whitespace as
with carried as (
    select distinct store_id, sku from stg_orders
),
type_velocity as (
    select s.store_type, p.sku, sum(p.units) / count(*) as upsw
    from stg_pos p join stg_stores s using (store_id)
    group by all
),
healthy as (
    select store_id, store_name, region, store_type
    from store_reorder_health
    where status = 'on rhythm'
),
gaps as (
    select h.*, k.sku, k.sku_name, k.unit_price
    from healthy h
    cross join stg_skus k
    where not exists (select 1 from carried c where c.store_id = h.store_id and c.sku = k.sku)
)
select
    g.store_id, g.store_name, g.region, g.store_type,
    g.sku, g.sku_name,
    round(tv.upsw, 2)                                           as peer_units_per_week,
    round(tv.upsw * 4.3 * g.unit_price, 2)                      as est_monthly_wholesale
from gaps g
join type_velocity tv on tv.store_type = g.store_type and tv.sku = g.sku
order by est_monthly_wholesale desc;
