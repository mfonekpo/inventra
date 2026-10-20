with source as (

    select * from {{ source('inventra_raw', 'raw_stock_ledger') }}

),

cleaned as (

    select
        nullif(trim(movement_id), '') as movement_id,
        nullif(trim(product_id), '') as product_id,
        nullif(trim(branch_id), '') as branch_id,
        nullif(trim(movement_type), '') as movement_type,
        toDate(movement_date) as movement_date,
        toUInt16(quantity) as quantity,
        nullif(trim(reference_type), '') as reference_type,
        nullif(trim(reference_id), '') as reference_id,
        toUInt16(running_balance) as running_balance

    from source

)

select * from cleaned