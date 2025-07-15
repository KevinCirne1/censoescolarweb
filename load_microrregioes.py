import requests
import pandas as pd
from sqlalchemy import create_engine

def load_microrregioes(db_engine: object, table: str) -> None:
    """
    Carrega dados de microrregiões do IBGE em uma tabela SQLite.
    """
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/microrregioes?orderBy=nome"
    print(f"\n🌎 Conectando à API do IBGE: {url}")

    try:
        # Requisição com timeout
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        json_data = resp.json()
        print(f"✅ Total de microrregiões: {len(json_data)}")

        # Normalizar e renomear colunas
        df = pd.json_normalize(json_data)
        df.columns = df.columns.str.replace(".", "_", regex=False)
        
        print("\n📑 Colunas disponíveis:")
        for col in df.columns:
            print(f"  - {col}")

        # Salvar no banco
        print(f"\n📥 Salvando na tabela '{table}'...")
        df.to_sql(
            table,
            db_engine,
            if_exists="replace",
            index=False,
            chunksize=2000
        )
        print(f"🎉 Dados de microrregiões salvos com sucesso!")
        
    except requests.exceptions.HTTPError as http_err:
        print(f"🚫 Erro HTTP: {http_err}")
    except Exception as err:
        print(f"❌ Falha geral: {err}")

def main():
    print("=============================================================")
    print("🔄 Carregando dados de microrregiões (IBGE)")
    print("=============================================================")
    
    db_path = "DadosBR.db"
    table_name = "microrregioes"
    engine = create_engine(f"sqlite:///{db_path}")
    
    load_microrregioes(engine, table_name)
    
    print("\n🏁 Processo de microrregiões concluído!")

if __name__ == "__main__":
    main()