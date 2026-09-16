-- Typed views over the raw files. Everything downstream reads these.

create or replace view stg_stores as
select
    store_id,
    store_name,
    region,
    store_type,
    cast(first_order_date as date)          as first_order_date,
    cast(shares_pos as boolean)             as shares_pos
from read_csv_auto('{data}/stores.csv', header = true, all_varchar = true);

create or replace view stg_skus as
select sku, sku_name, cast(case_units as integer) as case_units, cast(unit_price as double) as unit_price
from read_csv_auto('{data}/skus.csv', header = true, all_varchar = true);

create or replace view stg_orders as
select
    order_id,
    cast(order_date as date)                as order_date,
    store_id,
    sku,
    cast(cases as integer)                  as cases,
    cast(units as integer)                  as units,
    cast(net_revenue as double)             as net_revenue
from read_csv_auto('{data}/orders.csv', header = true, all_varchar = true);

create or replace view stg_pos as
select
    cast(week_start as date)                as week_start,
    store_id,
    sku,
    cast(units as integer)                  as units
from read_csv_auto('{data}/pos_weekly.csv', header = true, all_varchar = true);
