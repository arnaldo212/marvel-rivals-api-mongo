from fastapi import APIRouter
from database.db import jogadores
from database.db import partidas
from database.db import db


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
        
        return todos_jogadores
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

