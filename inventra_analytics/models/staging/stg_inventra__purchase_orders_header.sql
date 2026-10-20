with source as (

    select * from {{ source('inventra_raw', 'raw_purchase_orders_header') }}

),

cleaned as (

    select
        nullif(trim(po_id), '') as po_id,
        nullif(trim(supplier_id), '') as supplier_id,
        nullif(trim(branch_id), '') as branch_id,
        toDate(order_date) as order_date,
        toDate(expected_delivery_date) as expected_delivery_date,
        toDateOrNull(received_date) as received_date,
        nullif(trim(po_status), '') as po_status,
        toDecimal64(round(toFloat64(total_cost), 2), 2) as total_cost,
        toDecimal64(round(toFloat64(total_gst_amount), 2), 2) as total_gst_amount,
        toDecimal64(round(toFloat64(grand_total), 2), 2) as grand_total

    from source

)

select * from cleaned