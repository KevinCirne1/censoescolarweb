import requests
import pandas as pd
from sqlalchemy import create_engine
from typing import Optional

def fetch_mesorregioes_data(db_connection: object, destination_table: str) -> None:
    """
    Busca dados de mesorregiões do IBGE e os carrega em uma tabela SQLite.
    """
    api_endpoint = "https://servicodados.ibge.gov.br/api/v1/localidades/mesorregioes?orderBy=nome"
    print(f"\n🌍 Acessando API do IBGE para mesorregiões: {api_endpoint}")

    try:
        # Requisição à API
        response = requests.get(api_endpoint, timeout=10)
        response.raise_for_status()
        data = response.json()
        print(f"✅ Encontradas {len(data)} mesorregiões.")

        # Processamento dos dados
        df = pd.json_normalize(data)
        df.columns = [col.replace(".", "_") for col in df.columns]
        
        print("\n📋 Colunas processadas:")
        print("\n".join([f"  • {col}" for col in df.columns]))

        # Carregamento no banco
        print(f"\n🚚 Gravando dados na tabela '{destination_table}'...")
        df.to_sql(
            destination_table,
            db_connection,
            if_exists="replace",
            index=False,
            chunksize=1000
        )
        print(f"🎯 Tabela '{destination_table}' atualizada com sucesso!")
        
    except requests.exceptions.RequestException as err:
        print(f"🚫 Erro de rede ao acessar a API: {err}")
    except Exception as err:
        print(f"❌ Erro inesperado: {err}")

def main():
    print("=============================================================")
    print("🔄 Iniciando carga de dados de mesorregiões (IBGE)")
    print("=============================================================")
    
    database_path = "DadosBR.db"
    target_table = "mesorregioes"
    engine = create_engine(f"sqlite:///{database_path}")
    
    fetch_mesorregioes_data(engine, target_table)
    
    print("\n🏁 Carga de mesorregiões concluída!")

if __name__ == "__main__":
    main()