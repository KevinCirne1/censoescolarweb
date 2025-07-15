```sql
  -- Tabela para instituições do Censo Escolar
  CREATE TABLE IF NOT EXISTS instituicoes (
      NO_REGIAO TEXT,
      CO_REGIAO INTEGER,
      NO_UF TEXT,
      SG_UF TEXT,
      CO_UF INTEGER,
      NO_MUNICIPIO TEXT,
      CO_MUNICIPIO INTEGER,
      NO_MESORREGIAO TEXT,
      NO_MICRORREGIAO TEXT,
      NO_ENTIDADE TEXT,
      CO_ENTIDADE INTEGER,
      QT_MAT_BAS INTEGER,
      QT_MAT_INF INTEGER,
      QT_MAT_FUND INTEGER,
      QT_MAT_MED INTEGER,
      QT_MAT_EJA INTEGER,
      QT_MAT_EJA_FUND INTEGER,
      QT_MAT_ESP INTEGER,
      QT_MAT_BAS_EAD INTEGER,
      QT_MAT_FUND_INT INTEGER,
      QT_MAT_MED_INT INTEGER,
      ano_censo INTEGER
  );

  -- Tabela para mesorregiões
  CREATE TABLE IF NOT EXISTS mesorregioes (
      id INTEGER PRIMARY KEY,
      nome TEXT,
      UF_id INTEGER,
      UF_sigla TEXT,
      UF_nome TEXT,
      UF_regiao_id INTEGER,
      UF_regiao_sigla TEXT,
      UF_regiao_nome TEXT
  );

  -- Tabela para microrregiões
  CREATE TABLE IF NOT EXISTS microrregioes (
      id INTEGER PRIMARY KEY,
      nome TEXT,
      mesorregiao_id INTEGER,
      mesorregiao_nome TEXT,
      mesorregiao_UF_id INTEGER,
      mesorregiao_UF_sigla TEXT,
      mesorregiao_UF_nome TEXT,
      mesorregiao_UF_regiao_id INTEGER,
      mesorregiao_UF_regiao_sigla TEXT,
      mesorregiao_UF_regiao_nome TEXT
  );

  -- Tabela para municípios
  CREATE TABLE IF NOT EXISTS municipios (
      id INTEGER PRIMARY KEY,
      nome TEXT,
      microrregiao_id INTEGER,
      microrregiao_nome TEXT,
      mesorregiao_id INTEGER,
      mesorregiao_nome TEXT,
      uf_id INTEGER,
      uf_sigla TEXT,
      uf_nome TEXT,
      regiao_id INTEGER,
      regiao_sigla TEXT,
      regiao_nome TEXT
  );

  -- Tabela para UFs
  CREATE TABLE IF NOT EXISTS ufs (
      id INTEGER PRIMARY KEY,
      sigla TEXT,
      nome TEXT,
      regiao_id INTEGER,
      regiao_sigla TEXT,
      regiao_nome TEXT
  );
  ```