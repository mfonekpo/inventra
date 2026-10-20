with source as (

    select * from {{ source('inventra_raw', 'raw_sales_orders_header') }}

),

cleaned as (

    select
        nullif(trim(so_id), '') as so_id,
        nullif(trim(customer_id), '') as customer_id,
        nullif(trim(branch_id), '') as branch_id,
        toDate(order_date) as order_date,
        toDate(delivery_date) as delivery_date,
        nullif(trim(order_status), '') as order_status,
        nullif(trim(payment_terms), '') as payment_terms,
        toUInt16(total_order_value) as total_order_value,
        toDecimal64(round(toFloat64(total_gst_amount), 2), 2) as total_gst_amount,
        toDecimal64(round(toFloat64(grand_total), 2), 2) as grand_total,
        nullif(trim(sales_channel), '') as sales_channel

    from source

)

select * from cleaned