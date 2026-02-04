import os
import google.generativeai as genai
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import urllib.parse 

# 1. Carregar variáveis
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

# --- CONEXÃO COM O SUPABASE ---
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

if not all([db_user, db_pass, db_host, db_port, db_name]):
    raise ValueError("ERRO: Faltam variáveis no .env")

# Trata a senha
safe_password = urllib.parse.quote_plus(db_pass)
DB_URL = f"postgresql://{db_user}:{safe_password}@{db_host}:{db_port}/{db_name}"

genai.configure(api_key=API_KEY)

def get_market_data():
    print(f">>> [1/2] Acessando Supabase: Tabela 'public_gold.mart_bitcoin_indicadores'...")
    engine = create_engine(DB_URL)
    
    try:
        # Busca os dados calculados pelo dbt
        query = """
            SELECT 
                updated_at, 
                price_usd, 
                mms_7d, 
                variacao_pct 
            FROM public_gold.mart_bitcoin_indicadores 
            ORDER BY updated_at DESC 
            LIMIT 7
        """
        
        df = pd.read_sql(query, engine)
        
        if df.empty:
            print("⚠️ A tabela existe, mas está vazia.")
            return pd.DataFrame()
            
        return df.sort_values(by='updated_at', ascending=True)
        
    except Exception as e:
        print("\n❌ ERRO SQL.")
        print(f"Erro detalhado: {e}")
        return pd.DataFrame()

def run_analysis(df):
    print(">>> [2/2] O Gemini 2.5 está analisando seus indicadores...")
    
    # --- ATUALIZADO: Usando o modelo disponível na sua lista ---
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    last_row = df.iloc[-1]
    data_str = df.to_string(index=False)
    
    prompt = f"""
    Aja como um Estrategista de Criptoativos Sênior.
    Analise esta tabela vinda da nossa camada Gold de Engenharia:
    
    {data_str}
    
    RESUMO TÉCNICO DE HOJE:
    - Preço Atual: ${last_row['price_usd']:.2f}
    - Média Móvel (7 dias): ${last_row['mms_7d']:.2f}
    - Variação Diária: {last_row['variacao_pct']:.2f}%
    
    Com base nisso, responda de forma executiva:
    1. **Sinal Técnico:** O preço cruzou a média móvel? O que isso significa?
    2. **Momentum:** A variação recente indica força ou fraqueza?
    3. **Veredito:** (COMPRA / VENDA / AGUARDAR)
    """
    
    response = model.generate_content(prompt)
    return response.text

if __name__ == "__main__":
    df = get_market_data()
    
    if not df.empty:
        print("\n" + "="*50)
        print("🚀 RELATÓRIO DE INTELIGÊNCIA - BITCOIN")
        print("="*50)
        print(run_analysis(df))
        print("="*50 + "\n")