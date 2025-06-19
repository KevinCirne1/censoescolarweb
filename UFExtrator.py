import requests
import sqlite3
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

url = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"
db_path = "instituicoes.db"
json_path = "estados_brasil.json"

try:
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Erro na requisição: Status {response.status_code}")
    
    estados = response.json()
    if not estados:
        raise Exception("Nenhum dado retornado pela API")
    
    estados_db = [(e["id"], e["sigla"], e["nome"]) for e in estados]
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estados (
            id_estado INTEGER PRIMARY KEY,
            sigla TEXT NOT NULL,
            nome TEXT NOT NULL
        )
    """)
    
    cursor.executemany("""
        INSERT OR REPLACE INTO estados (id_estado, sigla, nome)
        VALUES (?, ?, ?)
    """, estados_db)
    
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM estados")
    count = cursor.fetchone()[0]
    conn.close()
    
    with open(json_path, "w", encoding="utf-8") as jsonfile:
        json.dump(estados, jsonfile, ensure_ascii=False, indent=2)
    
    logger.info(f"{len(estados)} estados extraídos da API")
    logger.info(f"{count} estados salvos no banco {db_path} (tabela 'estados')")
    logger.info(f"Dados também salvos em {json_path}")
    
except requests.RequestException as e:
    logger.error(f"Erro na conexão com a API: {e}")
except sqlite3.Error as e:
    logger.error(f"Erro no banco de dados: {e}")
except json.JSONDecodeError as e:
    logger.error(f"Erro ao processar o JSON: {e}")
except KeyError as e:
    logger.error(f"Erro na estrutura do JSON: Campo {e} não encontrado")
except Exception as e:
    logger.error(f"Erro: {e}")