{{ config(
    materialized='view',
    schema='silver'
) }}

WITH source_data AS (
    SELECT
        coin_id,
        price_usd,
        updated_at,
        ingestion_at,
        
        ROW_NUMBER() OVER(
            PARTITION BY CAST(updated_at AS DATE) 
            ORDER BY ingestion_at DESC
        ) as row_num

    FROM {{ source('supabase_bronze', 'bronze_bitcoin') }}
)

SELECT
    coin_id,
    price_usd,
    updated_at,
    ingestion_at
FROM source_data
WHERE row_num = 1