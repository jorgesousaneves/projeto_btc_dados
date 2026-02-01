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
        -- Mantemos o cálculo com precisão total aqui no CTE
        AVG(price_usd) OVER(ORDER BY updated_at ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as mms_7d,
        AVG(price_usd) OVER(ORDER BY updated_at ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) as mms_30d,
        LAG(price_usd) OVER(ORDER BY updated_at) as price_ontem
    FROM silver_data
)

SELECT
    updated_at,
    
    -- 1. Arredondar o Preço para 2 casas
    CAST(price_usd AS NUMERIC(18,2)) as price_usd,
    
    -- 2. Arredondar as Médias Móveis
    CAST(mms_7d AS NUMERIC(18,2)) as mms_7d,
    CAST(mms_30d AS NUMERIC(18,2)) as mms_30d,

    -- 3. Tratamento de NULL + Arredondamento da Variação
    -- COALESCE: Se o resultado for NULL, troca por 0
    COALESCE(
        CAST(
            ((price_usd - price_ontem) / NULLIF(price_ontem, 0)) * 100 
        AS NUMERIC(18,2)), 
        0
    ) as variacao_pct

FROM calculos
ORDER BY updated_at DESC