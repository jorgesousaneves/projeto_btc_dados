import os
import requests
import psycopg2
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

def get_db_connection():
    """Cria a conexão com o banco usando as variáveis do .env"""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            port=os.getenv("DB_PORT", "6543") 
        )
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar no banco: {e}")
        raise e

def criar_tabela_bronze(cursor):
    """Garante que a tabela existe antes de tentarmos usar."""
    query_create = """
    CREATE TABLE IF NOT EXISTS public.bronze_bitcoin (
        id SERIAL PRIMARY KEY,
        coin_id VARCHAR(50),
        price_usd NUMERIC(18,8),
        updated_at TIMESTAMP WITH TIME ZONE UNIQUE,
        ingestion_at TIMESTAMP WITH TIME ZONE
    );
    """
    cursor.execute(query_create)

def obter_ultima_data_banco(cursor):
    """Consulta via SQL qual a data mais recente salva."""
    try:
        query = "SELECT updated_at FROM public.bronze_bitcoin ORDER BY updated_at DESC LIMIT 1;"
        cursor.execute(query)
        result = cursor.fetchone()
        
        if result:
            dt = result[0] 
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        return None 
    except Exception as e:
        print(f"⚠️ Erro ao verificar data no banco: {e}")
        return None

def ingestao_bronze():
    print("🧠 Iniciando Ingestão (Via SQL/Pooler)...")
    
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        criar_tabela_bronze(cursor)
        conn.commit() 
        
        ultima_data = obter_ultima_data_banco(cursor)
        
        dias_para_buscar = "365"
        if ultima_data:
            print(f"📅 Última data no banco: {ultima_data.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        else:
            print("📅 Banco vazio ou sem dados. Buscaremos os últimos 365 dias.")

        api_url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days={dias_para_buscar}&interval=daily"
        headers = {"User-Agent": "Mozilla/5.0"}

        print(f"📡 Baixando dados da API...")
        response = requests.get(api_url, headers=headers, timeout=20)
        
        if response.status_code != 200:
            print(f"❌ Erro da API: {response.status_code}")
            return

        dados_json = response.json()
        precos = dados_json.get("prices", [])
        print(f"📦 Registros retornados pela API: {len(precos)}")
        
        novos_dados = []
        
        for registro in precos:
            timestamp_ms = registro[0]
            valor_usd = registro[1]
            
            data_registro = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
            
            if ultima_data is None or data_registro > ultima_data:
                novos_dados.append((
                    "bitcoin", 
                    valor_usd, 
                    data_registro, 
                    datetime.now(timezone.utc)
                ))

        total_novos = len(novos_dados)
        
        if total_novos > 0:
            print(f"🚀 Inserindo {total_novos} novos registros...")
            
            query_insert = """
            INSERT INTO public.bronze_bitcoin (coin_id, price_usd, updated_at, ingestion_at)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (updated_at) DO NOTHING
            """
            
            cursor.executemany(query_insert, novos_dados)
            conn.commit()
            
            print("✅ SUCESSO! Carga concluída.")
        else:
            print("✅ Banco já atualizado. Nenhum dado novo para inserir.")

    except Exception as e:
        conn.rollback() 
        print(f"❌ Erro Crítico: {e}")
    finally:
        cursor.close()
        conn.close()
        print("🔌 Conexão encerrada.")

if __name__ == "__main__":
    ingestao_bronze()