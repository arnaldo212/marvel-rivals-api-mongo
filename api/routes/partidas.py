from fastapi import APIRouter
from database.db import partidas, db
from fastapi import HTTPException

router = APIRouter(prefix="/partidas", tags=["partidas"])

@router.get("/")
def get_partidas():
    todas_partidas = list(partidas.find())
    
    for partida in todas_partidas:
        partida["_id"] = str(partida["_id"])

    return {
        "total": len(todas_partidas),
        "partidas": todas_partidas
    }


@router.get("/personagens")
def get_estatisticas_personagens():
    
    try:
        partidas_collection = db["partidas"] 
    except Exception:
        raise HTTPException(
            status_code=500, 
            detail="Erro de configuração: Conexão com o banco de dados 'db' não encontrada ou falhou."
        )

    pipeline = [
        { "$unwind": "$equipes" },
        { "$unwind": "$equipes.jogadores" },
        {
            "$project": {
                "id_personagem": "$equipes.jogadores.id_personagem",
                "abates": "$equipes.jogadores.abates",
                "venceu": { "$cond": [{ "$eq": ["$equipes.nome", "$vencedor"] }, 1, 0] }
            }
        },
        {
            "$group": {
                "_id": "$id_personagem",
                "vezes_usado": { "$sum": 1 },
                "total_vitorias": { "$sum": "$venceu" },
                "total_abates": { "$sum": "$abates" }
            }
        },
        { "$sort": { "total_vitorias": -1, "total_abates": -1 } },
        {
            "$lookup": {
                "from": "personagem", 
                "localField": "_id",
                "foreignField": "_id",
                "as": "personagem_info"
            }
        },
        { "$unwind": "$personagem_info" },
        {
            "$project": {
                "_id": 0,
                "id_personagem": "$_id",
                "nome_personagem": "$personagem_info.nome",
                "vezes_usado": 1,
                "total_vitorias": 1,
                "total_abates": 1
            }
        }
    ]

    try:
        resultados = list(partidas_collection.aggregate(pipeline))
        
        return resultados

    except Exception as e:
        print(f"ERRO CRÍTICO NA AGREGAÇÃO: {e}") 
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao executar a agregação combinada: {str(e)}"
        )


@router.get("/jogadores")
def get_estatisticas_jogadores():
    try:
        partidas_collection = db["partidas"] 
    except Exception:
        raise HTTPException(
            status_code=500, 
            detail="Erro de configuração: Conexão com o banco de dados 'db' não encontrada ou falhou."
        )

    pipeline = [
        { "$unwind": "$equipes" },
        { "$unwind": "$equipes.jogadores" },
        {
            "$project": {
                "id_jogador": "$equipes.jogadores.id_jogador",
                "abates": "$equipes.jogadores.abates",
                "venceu": { "$cond": [{ "$eq": ["$equipes.nome", "$vencedor"] }, 1, 0] }
            }
        },
        {
            "$group": {
                "_id": "$id_jogador",
                "partidas_jogadas": { "$sum": 1 },
                "partidas_vencidas": { "$sum": "$venceu" },
                "total_abates": { "$sum": "$abates" }
            }
        },
        { "$sort": { "partidas_vencidas": -1, "total_abates": -1 } },
        {
            "$lookup": {
                "from": "jogadores",
                "localField": "_id",
                "foreignField": "_id",
                "as": "jogador_info"
            }
        },
        { "$unwind": "$jogador_info" },
        {
            "$project": {
                "_id": 0,
                "id_jogador": "$_id",
                "nome_jogador": "$jogador_info.nome",
                "partidas_jogadas": 1,
                "partidas_vencidas": 1,
                "total_abates": 1
            }
        }
    ]

    try:
        resultados = list(partidas_collection.aggregate(pipeline))
        
        return resultados

    except Exception as e:
        print(f"ERRO CRÍTICO NA AGREGAÇÃO: {e}") 
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao executar a agregação combinada de jogadores: {str(e)}"
        )



@router.get("/rank_jogadores")
def get_rank_jogadores():
    try:
        partidas_collection = db["partidas"] 
    except Exception:
        raise HTTPException(
            status_code=500, 
            detail="Erro de configuração: Conexão com o banco de dados 'db' não encontrada ou falhou."
        )
    
    pipeline = [
        { "$unwind": "$equipes" },
        { "$unwind": "$equipes.jogadores" },
        {
            "$project": {
                "id_jogador": "$equipes.jogadores.id_jogador",
                "abates": "$equipes.jogadores.abates",
                "mortes": "$equipes.jogadores.mortes",
                "assistencias": "$equipes.jogadores.assistencias"
            }
        },
        {
            "$group": {
                "_id": "$id_jogador",
                "partidas_jogadas": { "$sum": 1 },
                "total_abates": { "$sum": "$abates" },
                "total_mortes": { "$sum": "$mortes" },
                "total_assistencias": { "$sum": "$assistencias" }
            }
        },
        {
            "$addFields": {
                "kda": {
                    "$divide": [
                        { "$add": ["$total_abates", "$total_assistencias"] },
                        { "$max": [1, "$total_mortes"] }
                    ]
                },
                "media_abates_por_partida": {
                    "$divide": ["$total_abates", "$partidas_jogadas"]
                }
            }
        },
        { "$sort": { "total_abates": -1 } },
        {
            "$lookup": {
                "from": "jogadores",
                "localField": "_id",
                "foreignField": "_id",
                "as": "perfil_info"
            }
        },
        { "$unwind": "$perfil_info" },
        {
            "$project": {
                "_id": 0,
                "id_jogador": "$_id",
                "nome_jogador": "$perfil_info.nome",
                "nivel": "$perfil_info.nivel",
                "ranque": "$perfil_info.ranque",
                "partidas_jogadas": 1,
                "total_abates": 1,
                "total_mortes": 1,
                "total_assistencias": 1,
                "kda": { "$round": ["$kda", 2] },
                "media_abates_por_partida": { "$round": ["$media_abates_por_partida", 2] }
            }
        }
    ]

    try:
        resultados = list(partidas_collection.aggregate(pipeline))
        
        return resultados

    except Exception as e:
        # Imprimir o erro detalhado é crucial para o debug
        print(f"ERRO CRÍTICO NA AGREGAÇÃO: {e}") 
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao executar a agregação combinada de jogadores: {str(e)}"
        )


@router.get("/personagem/{personagem_nome}")
def get_jogadores_por_personagem(personagem_nome: str):
    try:
        partidas_collection = db["partidas"] 
    except Exception:
        raise HTTPException(
            status_code=500, 
            detail="Erro de conexão com o banco de dados."
        )

    pipeline = [
        {
            "$lookup": {
                "from": "personagem",
                "let": { "personagem_nome_param": personagem_nome }, 
                "pipeline": [
                    { 
                        "$match": { 
                            "$expr": {
                                "$regexMatch": {
                                    "input": "$nome", 
                                    "regex": "$$personagem_nome_param", 
                                    "options": "i"
                                }
                            }
                        } 
                    },
                    { "$project": { "_id": 1, "nome": 1 } }
                ],
                "as": "personagem_alvo"
            }
        },
        { "$unwind": "$personagem_alvo" },
        { "$unwind": "$equipes" },
        { "$unwind": "$equipes.jogadores" },
        {
            "$match": {
                "$expr": {
                    "$eq": ["$equipes.jogadores.id_personagem", "$personagem_alvo._id"]
                }
            }
        },
        {
            "$project": {
                "id_jogador": "$equipes.jogadores.id_jogador",
                "total_abates": "$equipes.jogadores.abates",
                "id_personagem": "$personagem_alvo._id",
                "nome_personagem": "$personagem_alvo.nome"
            }
        },
        {
            "$group": {
                "_id": {
                    "id_jogador": "$id_jogador",
                    "id_personagem": "$id_personagem",
                    "nome_personagem": "$nome_personagem"
                },
                "partidas_jogadas": { "$sum": 1 },
                "total_abates": { "$sum": "$total_abates" }
            }
        },
        {
            "$addFields": {
                "media_abates": { 
                    "$divide": ["$total_abates", "$partidas_jogadas"] 
                }
            }
        },
        {
            "$lookup": {
                "from": "jogadores",
                "localField": "_id.id_jogador",
                "foreignField": "_id",
                "as": "jogador_info"
            }
        },
        { "$unwind": "$jogador_info" },
        { "$sort": { "total_abates": -1 } },
        {
            "$project": {
                "_id": 0,
                "id_personagem": "$_id.id_personagem",
                "nome_personagem": "$_id.nome_personagem",
                "id_jogador": "$_id.id_jogador",
                "nome_jogador": "$jogador_info.nome",
                "total_abates": 1,
                "partidas_jogadas": 1,
                "media_abates": { "$round": ["$media_abates", 1] }
            }
        }
    ]

    try:
        resultados = list(partidas_collection.aggregate(pipeline))
        
        if not resultados:
            raise HTTPException(
                status_code=404,
                detail=f"Nenhum jogador encontrado usando o personagem '{personagem_nome}'."
            )
            
        return resultados

    except HTTPException as h:
        raise h 
        
    except Exception as e:
        print(f"ERRO CRÍTICO NA AGREGAÇÃO POR PERSONAGEM: {e}") 
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao executar a agregação: {str(e)}"
        )










## ESSA TÁ FUNCIONANDO MAL

@router.get("/jogador/{jogador_nome}")
def get_personagens_vitorias_por_jogador(jogador_nome: str):
    try:
        partidas_collection = db["partidas"] 
    except Exception:
        raise HTTPException(
            status_code=500, 
            detail="Erro de conexão com o banco de dados."
        )
    pipeline = [
        {
            "$lookup": {
                "from": "jogadores",
                "let": { "jogador_nome_param": jogador_nome }, 
                "pipeline": [
                    { 
                        "$match": { 
                            "$expr": {
                                "$regexMatch": {
                                    "input": "$nome", 
                                    "regex": "$$jogador_nome_param", 
                                    "options": "i"
                                }
                            }
                        } 
                    },
                    { "$project": { "_id": 1, "nome": 1 } }
                ],
                "as": "jogador_alvo"
            }
        },
        { "$unwind": "$jogador_alvo" }, 
        
        { "$unwind": "$equipes" },
        { "$unwind": "$equipes.jogadores" },
        
        {
            "$match": {
                "equipes.jogadores.id_jogador": "$jogador_alvo._id",
                "$expr": { "$eq": ["$equipes.nome", "$vencedor"] }
            }
        },
        
        {
            "$group": {
                "_id": "$equipes.jogadores.id_personagem",
                "total_vitorias": { "$sum": 1 },
                "id_jogador": { "$first": "$jogador_alvo._id" }, 
                "nome_jogador": { "$first": "$jogador_alvo.nome" }
            }
        },
        
        { "$sort": { "total_vitorias": -1 } },
        
        {
            "$lookup": {
                "from": "personagem",
                "localField": "_id",
                "foreignField": "_id",
                "as": "personagem_info"
            }
        },
        { "$unwind": "$personagem_info" },
        
        {
            "$project": {
                "_id": 0,
                "id_jogador": "$id_jogador",
                "nome_jogador": "$nome_jogador",
                "id_personagem": "$_id",
                "nome_personagem": "$personagem_info.nome",
                "total_vitorias": 1
            }
        }
    ]

    try:
        resultados = list(partidas_collection.aggregate(pipeline))
        
        if not resultados:
            raise HTTPException(
                status_code=404,
                detail=f"O jogador '{jogador_nome}' não foi encontrado ou não possui vitórias registradas."
            )
            
        return resultados

    except HTTPException as h:
        raise h 
        
    except Exception as e:
        print(f"ERRO CRÍTICO NA AGREGAÇÃO DE PERSONAGENS POR JOGADOR: {e}") 
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao executar a agregação: {str(e)}"

        )
