with source as (

    select * from {{ source('inventra_raw', 'raw_inventory_master') }}

),

cleaned as (

    select
        nullif(trim(product_id), '') as product_id,
        nullif(TRIM(branch_id), '') as branch_id,
        toUInt32(opening_stock) as opening_stock,
        toUInt32(reorder_level) as reorder_level,
        toUInt32(safety_stock) as safety_stock,
        toUInt32(max_stock) as max_stock,
        toUInt64(current_stock) as current_stock,
        nullif(TRIM(warehouse_bin), '') as warehouse_bin

    from source

)

select 
    *
from cleaned