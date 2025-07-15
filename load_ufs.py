import requests
import pandas as pd
from sqlalchemy import create_engine

def import_ufs_data(db_engine: object, table: str) -> None:
    """
    Carrega dados de UFs do IBGE em uma tabela SQLite.
    """
    api = "https://servicodados.ibge.gov.br/api/v1/localidades/estados?orderBy=nome"
    print(f"\n🇧🇷 Acessando dados de UFs: {api}")

    try:
        # Requisição à API
        resp = requests.get(api, timeout=10)
        resp.raise_for_status()
        json_data = resp.json()
        print(f"✅ Total de UFs: {len(json_data)}")

        # Normalizar e mapear colunas
        df_raw = pd.json_normalize(json_data)
        columns_map = {
            'id': 'id',
            'sigla': 'sigla',
            'nome': 'nome',
            'regiao.id': 'regiao_id',
            'regiao.sigla': 'regiao_sigla',
            'regiao.nome': 'regiao_nome'
        }
        df = df_raw[list(columns_map.keys())].rename(columns=columns_map)
        
        print("\n📑 Colunas selecionadas:")
        for col in df.columns:
            print(f"  - {col}")

        # Salvar no banco
        print(f"\n💿 Salvando na tabela '{table}'...")
        df.to_sql(
            table,
            db_engine,
            if_exists="replace",
            index=False
        )
        print(f"🎉 UFs salvas com sucesso!")
        
    except requests.exceptions.RequestException as req_err:
        print(f"🚫 Erro de rede: {req_err}")
    except Exception as err:
        print(f"❌ Falha geral: {err}")

def main():
    print("=============================================================")
    print("�с Carregando dados de UFs (IBGE)")
    print("=============================================================")
    
    db_path = "DadosBR.db"
    table_name = "ufs"
    engine = create_engine(f"sqlite:///{db_path}")
    
    import_ufs_data(engine, table_name)
    
    print("\n🏁 Processo de UFs concluído!")

if __name__ == "__main__":
    main()