import os
import requests
import psycopg2
from dotenv import load_dotenv
from datetime import datetime, timezone

# 1. Configuração e Conexão
load_dotenv()

def get_db_connection():
    """Cria a conexão com o banco usando as variáveis do .env"""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            port=os.getenv("DB_PORT", "6543") # Padrão 6543 se não tiver no env
        )
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar no banco: {e}")
        raise e

def obter_ultima_data_banco(cursor):
    """Consulta via SQL qual a data mais recente salva."""
    try:
        # Query SQL direta
        query = "SELECT updated_at FROM bronze_bitcoin ORDER BY updated_at DESC LIMIT 1;"
        cursor.execute(query)
        result = cursor.fetchone()
        
        if result:
            dt = result[0] # Pega o primeiro campo da tupla
            
            # Se vier sem fuso (naive), força UTC
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        return None 
    except Exception as e:
        print(f"⚠️ Erro ao verificar data no banco: {e}")
        return None

def ingestao_bronze():
    print("🧠 Iniciando Ingestão (Via SQL/Pooler)...")
    
    # Conecta no banco
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 1. Verifica estado atual
        ultima_data = obter_ultima_data_banco(cursor)
        
        dias_para_buscar = "365"
        if ultima_data:
            print(f"📅 Última data no banco: {ultima_data.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        else:
            print("📅 Banco vazio ou sem dados. Buscaremos os últimos 365 dias.")

        # 2. Chamada na API (CoinGecko)
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
        
        # 3. Processamento e Filtragem
        novos_dados = []
        
        for registro in precos:
            timestamp_ms = registro[0]
            valor_usd = registro[1]
            
            # Converte timestamp ms para datetime UTC
            data_registro = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
            
            # Filtra apenas o que for mais novo que o banco
            if ultima_data is None or data_registro > ultima_data:
                # Prepara a tupla para o insert SQL
                novos_dados.append((
                    "bitcoin", 
                    valor_usd, 
                    data_registro, 
                    datetime.now(timezone.utc)
                ))

        # 4. Inserção em Lote (Batch Insert)
        total_novos = len(novos_dados)
        
        if total_novos > 0:
            print(f"🚀 Inserindo {total_novos} novos registros...")
            
            query_insert = """
            INSERT INTO bronze_bitcoin (coin_id, price_usd, updated_at, ingestion_at)
            VALUES (%s, %s, %s, %s)
            """
            
            # Executemany é muito mais rápido que loop for
            cursor.executemany(query_insert, novos_dados)
            conn.commit() # Importante: Salvar a transação!
            
            print("✅ SUCESSO! Carga concluída.")
        else:
            print("✅ Banco já atualizado. Nenhum dado novo para inserir.")

    except Exception as e:
        conn.rollback() # Desfaz se der erro
        print(f"❌ Erro Crítico: {e}")
    finally:
        cursor.close()
        conn.close()
        print("🔌 Conexão encerrada.")

if __name__ == "__main__":
    ingestao_bronze()