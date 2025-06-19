import csv
import sqlite3
from database import get_db_connection
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS instituicoes (
            co_instituicao INTEGER PRIMARY KEY,
            no_instituicao TEXT NOT NULL,
            id_municipio INTEGER,
            id_estado INTEGER,
            id_mesorregiao INTEGER,
            id_microrregiao INTEGER,
            dependencia_administrativa TEXT,
            ano_censo INTEGER,
            latitude REAL,
            longitude REAL,
            FOREIGN KEY (id_municipio) REFERENCES municipios(id_municipio),
            FOREIGN KEY (id_estado) REFERENCES estados(id_estado),
            FOREIGN KEY (id_mesorregiao) REFERENCES mesorregioes(id_mesorregiao),
            FOREIGN KEY (id_microrregiao) REFERENCES microrregioes(id_microrregiao)
        )
    """)
    conn.commit()
    conn.close()
    logger.info("Tabela 'instituicoes' criada ou verificada")

def get_municipio_info(cidade, uf):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.id_municipio, m.id_estado, m.id_mesorregiao, m.id_microrregiao
        FROM municipios m
        JOIN estados e ON m.id_estado = e.id_estado
        WHERE m.nome = ? AND e.sigla = ?
    """, (cidade, uf))
    result = cursor.fetchone()
    conn.close()
    return result

def extract_instituicoes(csv_path, ano_censo):
    logger.info(f"Extraindo dados de {csv_path} para o ano {ano_censo}")
    instituicoes = []
    with open(csv_path, encoding="latin1") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            municipio_info = get_municipio_info(row["NO_MUNICIPIO"], row["SG_UF"])
            if municipio_info:
                id_municipio, id_estado, id_mesorregiao, id_microrregiao = municipio_info
                latitude = float(row["NU_LATITUDE"]) if "NU_LATITUDE" in row and row["NU_LATITUDE"] else None
                longitude = float(row["NU_LONGITUDE"]) if "NU_LONGITUDE" in row and row["NU_LONGITUDE"] else None
                instituicao = (
                    int(row["CO_ENTIDADE"]),
                    row["NO_ENTIDADE"],
                    id_municipio,
                    id_estado,
                    id_mesorregiao,
                    id_microrregiao,
                    row["TP_DEPENDENCIA"],
                    ano_censo,
                    latitude,
                    longitude
                )
                instituicoes.append(instituicao)
    return instituicoes

def load_instituicoes(instituicoes):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.executemany("""
        INSERT OR REPLACE INTO instituicoes (
            co_instituicao, no_instituicao, id_municipio, id_estado, id_mesorregiao, id_microrregiao,
            dependencia_administrativa, ano_censo, latitude, longitude
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, instituicoes)
    conn.commit()
    conn.close()
    logger.info(f"{len(instituicoes)} instituições inseridas no banco")

def main():
    create_table()
    csv_files = [
        ("microdados_ed_basica_2023.csv", 2023),
        ("microdados_ed_basica_2024.csv", 2024)
    ]
    for csv_path, ano_censo in csv_files:
        try:
            instituicoes = extract_instituicoes(csv_path, ano_censo)
            load_instituicoes(instituicoes)
        except FileNotFoundError:
            logger.warning(f"Arquivo {csv_path} não encontrado")
        except Exception as e:
            logger.error(f"Erro ao processar {csv_path}: {e}")

if __name__ == "__main__":
    main()