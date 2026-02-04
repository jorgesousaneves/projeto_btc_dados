# 🪙 Bitcoin Data Pipeline | End-to-End Engineering + AI Analytics

![Status](https://img.shields.io/badge/Status-Production-green)
![Python](https://img.shields.io/badge/Python-3.10-blue)
![dbt](https://img.shields.io/badge/dbt-Core-orange)
![GenAI](https://img.shields.io/badge/GenAI-Gemini%202.5-magenta)
![CI/CD](https://img.shields.io/badge/GitHub-Actions-black)

##  Sobre o Projeto

Este projeto consiste em um pipeline de Engenharia de Dados completo (**End-to-End**) desenvolvido para ingerir, armazenar e transformar dados históricos do mercado de criptomoedas (Bitcoin), finalizando com uma camada de **Inteligência Artificial** para análise técnica automatizada.

O objetivo principal foi construir uma arquitetura resiliente, segura e automatizada, simulando um ambiente corporativo real que vai desde a coleta do dado bruto até a geração de insights via LLM (Large Language Model).

---

##  Arquitetura e Design

O projeto expande a **Arquitetura Medalhão** (Medallion Architecture), adicionando uma camada de inteligência analítica ao final do fluxo:

### 1. Ingestão (Bronze)
* **Fonte:** API CoinGecko.
* **Tecnologia:** Python (Script customizado com `requests` e `psycopg2`).
* **Estratégia:** Carga Incremental (Stateful Loading). O script verifica a última data no banco (`max_date`) e busca apenas os novos registros (D-1), evitando duplicidade e consumo desnecessário da API.
* **Armazenamento:** PostgreSQL (Raw Data).

### 2. Transformação (Silver)
* **Tecnologia:** dbt (Data Build Tool).
* **Processos:** Limpeza de dados, tipagem forte (casting), deduplicação e tratamento de nulos.
* **Qualidade:** Testes automatizados (`schema tests`) para garantir unicidade e integridade referencial.

### 3. Modelagem (Gold)
* **Tecnologia:** dbt.
* **Foco:** Tabela agregada e otimizada para Business Intelligence (BI) e consumo da IA.
* **KPIs Calculados:** Médias Móveis (7 e 30 dias), volatilidade e variação percentual diária.

### 4. Inteligência (AI Analytics) 
* **Tecnologia:** Google Gemini 2.5 (Via Python SDK).
* **Processo:** Um agente de IA lê os indicadores calculados na camada Gold e atua como um "Estrategista Sênior de Cripto".
* **Output:** A IA analisa cruzamento de médias e momentum para gerar um veredito textual (Compra/Venda/Neutro) e uma explicação técnica do cenário atual.

---

## Tech Stack

| Categoria | Tecnologia | Detalhes |
| :--- | :--- | :--- |
| **Linguagem** | **Python 3.10** | Scripts de ingestão e orquestração do módulo de IA. |
| **Generative AI** | **Google Gemini 2.5** | Modelo Flash para análise de indicadores financeiros (Prompt Engineering). |
| **Banco de Dados** | **PostgreSQL 15** | Hospedado na nuvem (Supabase) via Pooler (Port 6543). |
| **Transformação** | **dbt Core** | Orquestração de SQL, testes e documentação de linhagem. |
| **Automação (CI/CD)** | **GitHub Actions** | Pipeline YAML configurado para execução diária (CRON). |
| **Infraestrutura** | **Cloud Native** | Ambiente Serverless e execução em containers Ubuntu. |
| **Segurança** | **GitHub Secrets** | Credenciais gerenciadas via variáveis de ambiente (`.env`). |

---

## CI/CD e Automação

O projeto conta com um workflow de **Integração e Entrega Contínua** configurado no GitHub Actions, garantindo que o dado e a análise estejam sempre atualizados:

* **Trigger:** Execução programada (Schedule) todos os dias às 09:00 UTC e gatilho manual (`workflow_dispatch`).
* **Steps do Pipeline:**
    1.  Provisionamento de ambiente Linux (Ubuntu Latest).
    2.  Instalação de dependências (`requirements.txt`).
    3.  Injeção segura de credenciais (Secrets).
    4.  **Ingestão:** Execução do script Python (API -> Bronze).
    5.  **Transformação:** Execução do dbt (Bronze -> Silver -> Gold).
    6.  **Inteligência:** Execução do Agente de IA (Leitura da Gold -> Relatório Gemini).