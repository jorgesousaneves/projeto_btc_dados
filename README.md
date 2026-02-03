# 🪙 Bitcoin Data Pipeline | End-to-End Engineering

![Status](https://img.shields.io/badge/Status-Production-green)
![Python](https://img.shields.io/badge/Python-3.10-blue)
![dbt](https://img.shields.io/badge/dbt-Core-orange)
![CI/CD](https://img.shields.io/badge/GitHub-Actions-black)

##  Sobre o Projeto

Este projeto consiste em um pipeline de Engenharia de Dados completo (**End-to-End**) desenvolvido para ingerir, armazenar e transformar dados históricos do mercado de criptomoedas (Bitcoin).

O objetivo principal foi construir uma arquitetura resiliente, segura e automatizada, simulando um ambiente corporativo real com separação de ambientes e governança de dados.

---

## Arquitetura e Design

O projeto segue a **Arquitetura Medalhão** (Medallion Architecture), garantindo a qualidade e rastreabilidade do dado em cada etapa:

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
* **Foco:** Tabela agregada e otimizada para Business Intelligence (BI).
* **KPIs:** Variação diária, médias móveis (7 e 30 dias) e volatilidade.

---

## Tech Stack

| Categoria | Tecnologia | Detalhes |
| :--- | :--- | :--- |
| **Linguagem** | **Python 3.10** | Script de ingestão robusto com tratamento de exceções. |
| **Banco de Dados** | **PostgreSQL 15** | Hospedado na nuvem (Supabase) via Pooler (Port 6543). |
| **Transformação** | **dbt Core** | Orquestração de SQL, testes e documentação de linhagem. |
| **Automação (CI/CD)** | **GitHub Actions** | Pipeline YAML configurado para execução diária (CRON). |
| **Infraestrutura** | **Cloud Native** | Ambiente Serverless e execução em containers Ubuntu. |
| **Segurança** | **GitHub Secrets** | Credenciais gerenciadas via variáveis de ambiente (`.env`). |

---

## CI/CD e Automação

O projeto conta com um workflow de **Integração e Entrega Contínua** configurado no GitHub Actions:

* **Trigger:** Execução programada (Schedule) todos os dias às 09:00 UTC e gatilho manual (`workflow_dispatch`).
* **Steps do Pipeline:**
    1.  Provisionamento de ambiente Linux.
    2.  Instalação de dependências (`requirements.txt`).
    3.  Injeção segura de credenciais (Secrets).
    4.  Execução do Script Python (Ingestão).
    5.  Execução do dbt (Transformação Silver/Gold).
