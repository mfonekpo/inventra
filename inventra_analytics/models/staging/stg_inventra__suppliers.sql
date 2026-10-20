with source as (

    select * from {{ source('inventra_raw', 'raw_suppliers') }}

),

cleaned as (

    select
        nullif(trim(supplier_id), '') as supplier_id,
        nullif(trim(supplier_name), '') as supplier_name,
        nullif(trim(supplier_type), '') as supplier_type,
        nullif(trim(product_category), '') as product_category,
        nullif(trim(city), '') as city,
        nullif(trim(province), '') as province,
        nullif(trim(region), '') as region,
        nullif(trim(pincode), '') as pincode,
        toUInt8(lead_time_days) as lead_time_days,
        toUInt8(reliability_score) as reliability_score,
        toUInt8(import_duty_rate) as import_duty_rate,
        nullif(trim(china_tax_id), '') as china_tax_id

    from source

)

select * from cleaned