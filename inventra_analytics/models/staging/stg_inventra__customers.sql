with source as (

    select * from {{ source('inventra_raw', 'raw_customers')}}

),

cleaned as (

    select
        nullif(TRIM(customer_id), '') as customer_id,
        nullif(TRIM(customer_type), '') as customer_type,
        nullif(TRIM(industry_segment), '') as industry_segment,
        nullif(TRIM(city), '') as city,
        nullif(TRIM(state), '') as state,
        nullif(TRIM(pincode), '') as pincode,
        nullif(TRIM(region), '') as region,
        nullif(TRIM(branch_id), '') as branch_id,

        toUInt32(credit_limit) as credit_limit,
        toUInt32(current_balance) as current_balance,
        payment_terms,
        customer_since,
        last_purchase_date,
        toUInt32(total_purchase_value) as total_purchase_value,
        customer_rating

    from source

),


select * from cleaned