import pandas as pd
from sqlalchemy import create_engine
import re
import os.path
from typing import List

def import_censo_data(csv_path: str, database_engine: object, target_table: str, selected_columns: List[str]) -> None:
    """
    Importa e processa arquivos CSV do Censo Escolar, carregando-os em uma tabela SQLite.
    """
    print(f"\n📊 Iniciando importação do arquivo: {csv_path}")
    
    if not os.path.isfile(csv_path):
        print(f"🚫 Arquivo não encontrado: {csv_path}")
        return
    
    # Extrair ano do nome do arquivo
    year_match = re.match(r'.*_(\d{4})\.csv$', os.path.basename(csv_path))
    if not year_match:
        print(f"⚠️ Não foi possível extrair o ano do arquivo: {csv_path}")
        return
    
    censo_year = int(year_match.group(1))
    print(f"📅 Ano extraído: {censo_year}")
    
    try:
        # Leitura do CSV com opções otimizadas
        print("⏳ Carregando CSV...")
        data = pd.read_csv(
            csv_path,
            sep=';',
            encoding='latin-1',
            usecols=selected_columns,
            dtype_backend='numpy_nullable'
        )
        
        # Adicionar coluna de ano
        data = data.assign(ano_censo=censo_year)
        print(f"✅ Coluna 'ano_censo' adicionada com valor {censo_year}")
        
        # Carregar no banco
        print(f"📤 Enviando {len(data):,} registros para a tabela '{target_table}'...")
        data.to_sql(
            name=target_table,
            con=database_engine,
            if_exists='append',
            index=False,
            method='multi',
            chunksize=5000
        )
        print(f"🎉 Dados de {csv_path} importados com sucesso!")
        
    except Exception as error:
        print(f"❌ Erro ao processar {csv_path}: {str(error)}")
        print("   Verifique as colunas selecionadas ou o formato do arquivo.")

def main():
    print("=============================================================")
    print("🔄 Iniciando importação de dados do Censo Escolar")
    print("=============================================================")
    
    # Configurações
    database_path = "DadosBR.db"
    target_table = "instituicoes"
    censo_files = [
        "microdados_ed_basica_2023.csv",
        "microdados_ed_basica_2024.csv"
    ]
    columns_to_use = [
        "NO_REGIAO", "CO_REGIAO", "NO_UF", "SG_UF", "CO_UF", "NO_MUNICIPIO",
        "CO_MUNICIPIO", "NO_MESORREGIAO", "NO_MICRORREGIAO", "NO_ENTIDADE",
        "CO_ENTIDADE", "QT_MAT_BAS", "QT_MAT_INF", "QT_MAT_FUND", "QT_MAT_MED",
        "QT_MAT_EJA", "QT_MAT_EJA_FUND", "QT_MAT_ESP", "QT_MAT_BAS_EAD",
        "QT_MAT_FUND_INT", "QT_MAT_MED_INT"
    ]
    
    # Conexão com o banco
    engine = create_engine(f"sqlite:///{database_path}")
    
    # Processar cada arquivo
    for file in censo_files:
        import_censo_data(file, engine, target_table, columns_to_use)
    
    print("\n🏁 Importação de dados do Censo Escolar concluída!")

if __name__ == "__main__":
    main()