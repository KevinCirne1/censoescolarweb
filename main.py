from fastapi import FastAPI, HTTPException, Request
from marshmallow import Schema, fields, validates, ValidationError, validate
from database import get_db_connection
from app_config import create_app

app = create_app()

class InstituicaoSchema(Schema):
    co_instituicao = fields.Integer(required=True, validate=validate.Range(min=1))
    no_instituicao = fields.String(required=True, validate=validate.Length(min=1))
    id_municipio = fields.Integer(required=True, validate=validate.Range(min=1))
    id_estado = fields.Integer(required=True, validate=validate.Range(min=1))
    id_mesorregiao = fields.Integer(required=True, validate=validate.Range(min=1))
    id_microrregiao = fields.Integer(required=True, validate=validate.Range(min=1))
    dependencia_administrativa = fields.String(
        required=True,
        validate=validate.OneOf(["Federal", "Estadual", "Municipal", "Privada"])
    )
    ano_censo = fields.Integer(required=True, validate=validate.OneOf([2023, 2024]))
    latitude = fields.Float(allow_none=True)
    longitude = fields.Float(allow_none=True)

    @validates("id_estado")
    def validate_id_estado(self, value):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_estado FROM estados WHERE id_estado = ?", (value,))
        if not cursor.fetchone():
            conn.close()
            raise ValidationError("ID de estado inválido.")
        conn.close()

    @validates("id_municipio")
    def validate_id_municipio(self, value):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_municipio FROM municipios WHERE id_municipio = ? AND id_estado = ?", 
                      (value, self.context.get("id_estado")))
        if not cursor.fetchone():
            conn.close()
            raise ValidationError("ID de município inválido ou não pertence ao estado informado.")
        conn.close()

    @validates("id_mesorregiao")
    def validate_id_mesorregiao(self, value):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_mesorregiao FROM mesorregioes WHERE id_mesorregiao = ? AND id_estado = ?", 
                      (value, self.context.get("id_estado")))
        if not cursor.fetchone():
            conn.close()
            raise ValidationError("ID de mesorregião inválido ou não pertence ao estado informado.")
        conn.close()

    @validates("id_microrregiao")
    def validate_id_microrregiao(self, value):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_microrregiao FROM microrregioes WHERE id_microrregiao = ? AND id_mesorregiao = ?", 
                      (value, self.context.get("id_mesorregiao")))
        if not cursor.fetchone():
            conn.close()
            raise ValidationError("ID de microrregião inválido ou não pertence à mesorregião informada.")
        conn.close()

@app.get("/instituicoesensino")
async def listar_instituicoes(request: Request):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.co_instituicao, i.no_instituicao, m.nome as cidade, e.sigla as uf, 
               mes.nome as mesorregiao, mic.nome as microrregiao, i.dependencia_administrativa,
               i.ano_censo, i.latitude, i.longitude
        FROM instituicoes i
        JOIN municipios m ON i.id_municipio = m.id_municipio
        JOIN estados e ON i.id_estado = e.id_estado
        JOIN mesorregioes mes ON i.id_mesorregiao = mes.id_mesorregiao
        JOIN microrregioes mic ON i.id_microrregiao = mic.id_microrregiao
    """)
    instituicoes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    request.state.logger.info("Listando todas as instituições")
    return instituicoes

@app.get("/instituicoesensino/{co_instituicao}")
async def recuperar_instituicao(co_instituicao: int, request: Request):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.co_instituicao, i.no_instituicao, m.nome as cidade, e.sigla as uf, 
               mes.nome as mesorregiao, mic.nome as microrregiao, i.dependencia_administrativa,
               i.ano_censo, i.latitude, i.longitude
        FROM instituicoes i
        JOIN municipios m ON i.id_municipio = m.id_municipio
        JOIN estados e ON i.id_estado = e.id_estado
        JOIN mesorregioes mes ON i.id_mesorregiao = mes.id_mesorregiao
        JOIN microrregioes mic ON i.id_microrregiao = mic.id_microrregiao
        WHERE i.co_instituicao = ?
    """, (co_instituicao,))
    instituicao = cursor.fetchone()
    conn.close()
    if instituicao:
        request.state.logger.info(f"Recuperando instituição {co_instituicao}")
        return dict(instituicao)
    request.state.logger.warning(f"Instituição {co_instituicao} não encontrada")
    raise HTTPException(status_code=404, detail="Instituição não encontrada")

@app.get("/instituicoesensino/mapa")
async def listar_instituicoes_mapa(request: Request):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.co_instituicao, i.no_instituicao, m.nome as cidade, e.sigla as uf, 
               i.dependencia_administrativa, i.ano_censo, i.latitude, i.longitude
        FROM instituicoes i
        JOIN municipios m ON i.id_municipio = m.id_municipio
        JOIN estados e ON i.id_estado = e.id_estado
        WHERE i.latitude IS NOT NULL AND i.longitude IS NOT NULL
    """)
    instituicoes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    request.state.logger.info("Listando instituições para o mapa")
    return instituicoes

@app.post("/instituicoesensino")
async def inserir_instituicao(nova_instituicao: dict, request: Request):
    schema = InstituicaoSchema()
    try:
        validated_data = schema.load(nova_instituicao, context={
            "id_estado": nova_instituicao.get("id_estado"),
            "id_mesorregiao": nova_instituicao.get("id_mesorregiao"),
            "id_microrregiao": nova_instituicao.get("id_microrregiao")
        })
    except ValidationError as err:
        request.state.logger.error(f"Erro de validação ao inserir instituição: {err.messages}")
        raise HTTPException(status_code=422, detail=err.messages)

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO instituicoes (co_instituicao, no_instituicao, id_municipio, id_estado, id_mesorregiao, id_microrregiao, 
                                     dependencia_administrativa, ano_censo, latitude, longitude)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            validated_data["co_instituicao"],
            validated_data["no_instituicao"],
            validated_data["id_municipio"],
            validated_data["id_estado"],
            validated_data["id_mesorregiao"],
            validated_data["id_microrregiao"],
            validated_data["dependencia_administrativa"],
            validated_data["ano_censo"],
            validated_data.get("latitude"),
            validated_data.get("longitude")
        ))
        conn.commit()
        request.state.logger.info(f"Instituição {validated_data['co_instituicao']} inserida")
    except sqlite3.IntegrityError:
        conn.close()
        request.state.logger.error(f"Erro ao inserir instituição: já existe ou IDs inválidos")
        raise HTTPException(status_code=400, detail="Instituição já existe ou IDs inválidos")
    finally:
        conn.close()
    return {"mensagem": "Instituição adicionada com sucesso"}

@app.put("/instituicoesensino")
async def atualizar_instituicao(inst_atualizada: dict, request: Request):
    schema = InstituicaoSchema()
    try:
        validated_data = schema.load(inst_atualizada, context={
            "id_estado": inst_atualizada.get("id_estado"),
            "id_mesorregiao": inst_atualizada.get("id_mesorregiao"),
            "id_microrregiao": inst_atualizada.get("id_microrregiao")
        })
    except ValidationError as err:
        request.state.logger.error(f"Erro de validação ao atualizar instituição: {err.messages}")
        raise HTTPException(status_code=422, detail=err.messages)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE instituicoes
        SET no_instituicao = ?, id_municipio = ?, id_estado = ?, id_mesorregiao = ?, id_microrregiao = ?, 
            dependencia_administrativa = ?, ano_censo = ?, latitude = ?, longitude = ?
        WHERE co_instituicao = ?
    """, (
        validated_data["no_instituicao"],
        validated_data["id_municipio"],
        validated_data["id_estado"],
        validated_data["id_mesorregiao"],
        validated_data["id_microrregiao"],
        validated_data["dependencia_administrativa"],
        validated_data["ano_censo"],
        validated_data.get("latitude"),
        validated_data.get("longitude"),
        validated_data["co_instituicao"]
    ))
    if cursor.rowcount == 0:
        conn.close()
        request.state.logger.warning(f"Instituição {validated_data['co_instituicao']} não encontrada")
        raise HTTPException(status_code=404, detail="Instituição não encontrada")
    conn.commit()
    conn.close()
    request.state.logger.info(f"Instituição {validated_data['co_instituicao']} atualizada")
    return {"mensagem": "Instituição atualizada com sucesso"}

@app.delete("/instituicoesensino/{co_instituicao}")
async def remover_instituicao(co_instituicao: int, request: Request):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM instituicoes WHERE co_instituicao = ?", (co_instituicao,))
    if cursor.rowcount == 0:
        conn.close()
        request.state.logger.warning(f"Instituição {co_instituicao} não encontrada")
        raise HTTPException(status_code=404, detail="Instituição não encontrada")
    conn.commit()
    conn.close()
    request.state.logger.info(f"Instituição {co_instituicao} removida")
    return {"mensagem": "Instituição removida com sucesso"}

@app.get("/estados")
async def listar_estados(request: Request):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_estado, sigla, nome FROM estados")
    estados = [dict(row) for row in cursor.fetchall()]
    conn.close()
    request.state.logger.info("Listando todos os estados")
    return estados

@app.get("/municipios")
async def listar_municipios(request: Request, id_estado: int = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    if id_estado:
        cursor.execute("SELECT id_municipio, nome, id_estado FROM municipios WHERE id_estado = ?", (id_estado,))
    else:
        cursor.execute("SELECT id_municipio, nome, id_estado FROM municipios")
    municipios = [dict(row) for row in cursor.fetchall()]
    conn.close()
    request.state.logger.info(f"Listando municípios {'do estado ' + str(id_estado) if id_estado else 'de todos os estados'}")
    return municipios

@app.get("/mesorregioes")
async def listar_mesorregioes(request: Request, id_estado: int = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    if id_estado:
        cursor.execute("SELECT id_mesorregiao, nome, id_estado FROM mesorregioes WHERE id_estado = ?", (id_estado,))
    else:
        cursor.execute("SELECT id_mesorregiao, nome, id_estado FROM mesorregioes")
    mesorregioes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    request.state.logger.info(f"Listando mesorregiões {'do estado ' + str(id_estado) if id_estado else 'de todos os estados'}")
    return mesorregioes

@app.get("/microrregioes")
async def listar_microrregioes(request: Request, id_mesorregiao: int = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    if id_mesorregiao:
        cursor.execute("SELECT id_microrregiao, nome, id_mesorregiao FROM microrregioes WHERE id_mesorregiao = ?", (id_mesorregiao,))
    else:
        cursor.execute("SELECT id_microrregiao, nome, id_mesorregiao FROM microrregioes")
    microrregioes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    request.state.logger.info(f"Listando microrregiões {'da mesorregião ' + str(id_mesorregiao) if id_mesorregiao else 'de todas as mesorregiões'}")
    return microrregioes