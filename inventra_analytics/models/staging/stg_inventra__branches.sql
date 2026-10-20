with source as (

    select * from {{ source('inventra_raw', 'raw_branches') }}

),

cleaned as (

    select
        nullif(TRIM(branch_id), '') as branch_id,
        nullif(TRIM(branch_name), '') as branch_name,
        nullif(TRIM(city), '') as city,
        nullif(TRIM(state), '') as state,
        nullif(TRIM(region), '') as region,
        nullif(TRIM(warehouse_type), '') as warehouse_type,
        nullif(TRIM(service_center_available), '') as service_center_available,
        
        toString(manager_id) as manager_id,

        accurateCastOrNull(
            splitByWhitespace(warehouse_capacity)[1],
            'UInt32'
        ) as warehouse_capacity_value,

        splitByWhitespace(warehouse_capacity)[2] as warehouse_capacity_unit,

        accurateCastOrNull(
            trimBoth(total_employees), 'UInt32'
        ) as total_employees,

        accurateCastOrNull(trimBoth(avg_monthly_revenue), 'Decimal(20,2)') as avg_monthly_revenue,

        accurateCastOrNull(
            trimBoth(monthly_operational_cost), 'Decimal(20,4)'
            ) as monthly_operational_cost,

        toFloat64OrNull(trimBoth(market_demand_index)) as market_demand_index

    from source

)

select * from cleaned