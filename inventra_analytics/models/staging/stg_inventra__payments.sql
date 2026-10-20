with source as (

    select * from {{ source('inventra_raw', 'raw_payments') }}

),

cleaned as (

    select
        nullif(TRIM(payment_id), '') as payment_id,
        nullif(TRIM(invoice_id), '') as invoice_id,
        toDate(payment_date) as payment_date,
        toDecimal64(payment_amount, 2) as payment_amount,
        nullif(TRIM(payment_method), '') as payment_method

    from source

)

select * from cleaned