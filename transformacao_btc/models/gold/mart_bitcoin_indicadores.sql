{{ config(
    materialized='table',
    schema='gold'
) }}

WITH silver_data AS (
    SELECT * FROM {{ ref('stg_bitcoin') }}
),

calculos AS (
    SELECT
        updated_at,
        price_usd,
        AVG(price_usd) OVER(ORDER BY updated_at ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as mms_7d,
        AVG(price_usd) OVER(ORDER BY updated_at ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) as mms_30d,
        LAG(price_usd) OVER(ORDER BY updated_at) as price_ontem
    FROM silver_data
)

SELECT
    updated_at,
    
    CAST(price_usd AS NUMERIC(18,2)) as price_usd,
    
    CAST(mms_7d AS NUMERIC(18,2)) as mms_7d,
    CAST(mms_30d AS NUMERIC(18,2)) as mms_30d,

    COALESCE(
        CAST(
            ((price_usd - price_ontem) / NULLIF(price_ontem, 0)) * 100 
        AS NUMERIC(18,2)), 
        0
    ) as variacao_pct

FROM calculos
ORDER BY updated_at DESC