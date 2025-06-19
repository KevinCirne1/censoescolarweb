import sqlite3
from database import get_db_connection
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_instituicoes():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS instituicoes_new (
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

    cursor.execute("""
        INSERT INTO instituicoes_new (
            co_instituicao, no_instituicao, id_municipio, id_estado, id_mesorregiao, id_microrregiao,
            dependencia_administrativa, ano_censo, latitude, longitude
        )
        SELECT 
            i.co_instituicao,
            i.no_instituicao,
            m.id_municipio,
            e.id_estado,
            m.id_mesorregiao,
            m.id_microrregiao,
            i.dependencia_administrativa,
            i.ano_censo,
            i.latitude,
            i.longitude
        FROM instituicoes i
        JOIN municipios m ON i.cidade = m.nome AND i.uf = m.uf
        JOIN estados e ON i.uf = e.sigla
    """)

    cursor.execute("DROP TABLE IF EXISTS instituicoes")
    cursor.execute("ALTER TABLE instituicoes_new RENAME TO instituicoes")
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM instituicoes")
    count = cursor.fetchone()[0]
    conn.close()
    logger.info(f"{count} instituições migradas com sucesso")

if __name__ == "__main__":
    try:
        migrate_instituicoes()
    except sqlite3.Error as e:
        logger.error(f"Erro no banco de dados: {e}")