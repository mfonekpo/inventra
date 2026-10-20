with source as (

    select * from {{ source('inventra_raw', 'raw_purchase_orders_lines') }}

),

cleaned as (

    select
        nullif(trim(po_id), '') as po_id,
        toUInt8(line_number) as line_number,
        nullif(trim(product_id), '') as product_id,
        toUInt8(quantity) as quantity,
        toDecimal64(round(toFloat64(unit_cost), 2), 2) as unit_cost,
        toUInt8(gst_rate) as gst_rate,
        toDecimal64(round(toFloat64(line_total), 2), 2) as line_total,
        toDecimal64(round(toFloat64(gst_amount), 2), 2) as gst_amount,
        toDecimal64(round(toFloat64(line_grand_total), 2), 2) as line_grand_total

    from source

)

select * from cleaned