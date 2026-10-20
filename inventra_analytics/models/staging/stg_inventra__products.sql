with source as (

    select * from {{ source('inventra_raw', 'raw_products') }}

),

cleaned as (

    select
        nullif(trim(product_id), '') as product_id,
        nullif(trim(product_name), '') as product_name,
        nullif(trim(category), '') as category,
        nullif(trim(machine_type), '') as machine_type,
        nullif(trim(brand), '') as brand,
        nullif(trim(model_compatibility), '') as model_compatability,
        toUInt16(unit_cost) as unit_cost,
        toUInt16(unit_price) as unit_price,
        toDecimal64(margin_percentage, 1) as margin_percentage,
        toUInt8(gst_rate) as gst_rate,
        toDecimal32(weight_kg, 2) as weight_kg,
        nullif(trim(dimensions_cm), '') as dimensions_cm,
        nullif(trim(material_type), '') as material_type,
        toUInt8(warranty_months) as warranty_months,
        toUInt8(reorder_level) as reorder_level,
        toUInt8(safety_stock) as safety_stock,
        toUInt16(max_stock_level) as max_stock_level,
        toUInt8(lead_time_days) as lead_time_days,
        nullif(trim(criticality_level), '') as criticality_level,
        nullif(trim(usage_frequency), '') as usage_frequency,
        nullif(trim(uom), '') as uom,
        toUInt16(last_purchase_price) as last_purchase_price,
        toDate(last_purchase_date) as last_purchase_date

    from source

)

select * from cleaned