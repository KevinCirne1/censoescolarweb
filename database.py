import sqlite3
from pathlib import Path

def initialize_database(db_path: str, schema_file: str) -> None:
    """
    Executa o script SQL para configurar o esquema do banco de dados.
    """
    print(f"\n🛠️ Configurando banco de dados: {db_path}")
    print(f"📜 Usando script SQL: {schema_file}")

    try:
        # Verificar se o arquivo de esquema existe
        if not Path(schema_file).is_file():
            print(f"🚫 Arquivo {schema_file} não encontrado!")
            return

        # Conectar ao banco
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Ler e executar o script SQL
            with open(schema_file, 'r', encoding='utf-8') as sql_file:
                sql_script = sql_file.read()
            
            print("⏳ Executando comandos SQL...")
            cursor.executescript(sql_script)
            conn.commit()
            print("✅ Esquema do banco configurado com sucesso!")
            
    except sqlite3.Error as sql_err:
        print(f"❌ Erro no banco de dados: {sql_err}")
    except Exception as err:
        print(f"❌ Erro inesperado: {err}")

def main():
    print("=============================================================")
    print("🔄 Inicializando esquema do banco de dados")
    print("=============================================================")
    
    database = "DadosBR.db"
    schema = "schemas.sql"
    
    initialize_database(database, schema)
    
    print("\n🏁 Configuração do banco concluída!")

if __name__ == "__main__":
    main()