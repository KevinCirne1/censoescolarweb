import requests
import sqlite3
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

url = "https://servicodados.ibge.gov.br/api/v1/localidades/mesorregioes"
db_path = "instituicoes.db"
json_path = "mesorregioes_brasil.json"

try:
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Erro na requisição: Status {response.status_code}")
    
    mesorregioes = response.json()
    if not mesorregioes:
        raise Exception("Nenhum dado retornado pela API")
    
    mesorregioes_db = [
        (
            m["id"],
            m["nome"],
            m["UF"]["id"]
        )
        for m in mesorregioes
    ]
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mesorregioes (
            id_mesorregiao INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            id_estado INTEGER,
            FOREIGN KEY (id_estado) REFERENCES estados(id_estado)
        )
    """)
    
    cursor.executemany("""
        INSERT OR REPLACE INTO mesorregioes (id_mesorregiao, nome, id_estado)
        VALUES (?, ?, ?)
    """, mesorregioes_db)
    
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM mesorregioes")
    count = cursor.fetchone()[0]
    conn.close()
    
    with open(json_path, "w", encoding="utf-8") as jsonfile:
        json.dump(mesorregioes, jsonfile, ensure_ascii=False, indent=2)
    
    logger.info(f"{len(mesorregioes)} mesorregiões extraídas da API")
    logger.info(f"{count} mesorregiões salvas no banco {db_path} (tabela 'mesorregioes')")
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