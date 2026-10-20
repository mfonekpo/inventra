with source as (

    select * from {{ source('inventra_raw', 'raw_invoices') }}

),

cleaned as (

    select
        nullif(TRIM(invoice_id), '') as invoice_id,
        nullif(TRIM(so_id), '') as so_id,
        nullif(TRIM(customer_id), '') as customer_id,
        nullif(TRIM(branch_id), '') as branch_id,
        toDate(invoice_date) as invoice_date,
        toDate(due_date) as due_date,
        toDecimal64(total_order_value, 2) as total_order_value,
        toDecimal64(total_gst_amount, 2) as total_gst_amount,
        toDecimal64(grand_total, 2) as grand_total,
        nullif(TRIM(payment_status), '') as payment_status

    from source
)

select * from cleaned