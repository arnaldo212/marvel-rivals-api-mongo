from fastapi import APIRouter
from database.db import jogadores


router = APIRouter(prefix="/jogadores", tags=["jogadores"])

@router.get("/")
def get_jogadores():

    try:
        # Busca todos os jogadores
        todos_jogadores = list(jogadores.find())
        
        # Converte ObjectId para string
        for jogador in todos_jogadores:
            if "_id" in jogador:
                jogador["_id"] = str(jogador["_id"])
        
        return {
            "total": len(todos_jogadores),
            "jogadores": todos_jogadores
        }
    except Exception as e:
        return {"erro": f"Erro ao buscar jogadores: {str(e)}"}

@router.get("/jogador/{jogador_nome}")
def get_jogador_por_nome(jogador_nome: str):

    try:
        # Busca com regex para case insensitive
        jogador_doc = jogadores.find_one({
            "nome": {"$regex": jogador_nome, "$options": "i"}
        })
        
        # Converte ObjectId para string
        if "_id" in jogador_doc:
            jogador_doc["_id"] = str(jogador_doc["_id"])
        
        return jogador_doc
        
    except Exception as e:
        return {"erro": f"Erro ao buscar jogador: {str(e)}"}

@router.get("/vitorias/{jogador_nome}")
def get_vitorias_jogador_personagem(jogador_nome: str):

    try:
        # usar aggregation para simular a view
        pipeline = [
            # Filtra pelo nome do jogador (case insensitive)
            {"$match": {
                "nome_jogador": {"$regex": f"^{jogador_nome}$", "$options": "i"}
            }},
            
            # Se não encontrar, tenta busca parcial
            {"$match": {
                "nome_jogador": {"$regex": jogador_nome, "$options": "i"}
            }},
            
            # Formata o resultado
            {"$project": {
                "_id": 0,  # Remove _id
                "nome_jogador": 1,
                "nome_personagem": 1,
                "total_vitorias": 1,
                "total_partidas": 1,
                "taxa_vitoria": {
                    "$cond": {
                        "if": {"$gt": ["$total_partidas", 0]},
                        "then": {
                            "$multiply": [
                                {"$divide": ["$total_vitorias", "$total_partidas"]},
                                100
                            ]
                        },
                        "else": 0
                    }
                }
            }}
        ]
        
        resultados = list(jogadores.aggregate(pipeline))
        
        if not resultados:
            # Se não encontrar na coleção principal, talvez tenha coleção separada
            from database.db import db
            colecoes = db.list_collection_names()
            
            if "vitorias_jogadores_personagens" in colecoes:
                colecao_vitorias = db["vitorias_jogadores_personagens"]
                resultados = list(colecao_vitorias.find({
                    "nome_jogador": {"$regex": jogador_nome, "$options": "i"}
                }))
            
        
        # Converte ObjectId para string se existir
        for resultado in resultados:
            if "_id" in resultado:
                resultado["_id"] = str(resultado["_id"])
        
        return {
            "jogador": jogador_nome,
            "total_resultados": len(resultados),
            "estatisticas": resultados
        }
        
    except Exception as e:
        return {"erro": f"Erro ao buscar vitórias: {str(e)}"}
