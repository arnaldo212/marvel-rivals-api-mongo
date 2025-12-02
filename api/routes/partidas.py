from fastapi import APIRouter
from database.db import partidas, db


router = APIRouter(prefix="/partidas", tags=["partidas"])

@router.get("/")
def get_partidas():
    todas_partidas = list(partidas.find())
    

    #Converte apenas o _id principal para string
    for partida in todas_partidas:
        partida["_id"] = str(partida["_id"])

    return {
        "total": len(todas_partidas),
        "partidas": todas_partidas
    }