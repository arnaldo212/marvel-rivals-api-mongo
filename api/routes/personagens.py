from fastapi import APIRouter
from database.db import personagem, habilidade_colab, db

router = APIRouter(prefix="/personagens", tags=["personagens"])

@router.get("")
def listar_personagens():
    try:
        personagens = list(personagem.find())
        
        for p in personagens:
            p["_id"] = str(p["_id"])  # Converte número para string
        
        return {"total": len(personagens), "personagens": personagens}
    except Exception as e:
        return {"erro": f"Falha ao buscar personagens: {str(e)}", "total": 0, "personagens": []}

@router.get("/{personagem_id}")
def get_personagem_completo(personagem_id: str):

    try:
        
        id_num = int(personagem_id)
        
        # Pipeline de agregação
        pipeline = [
            # Encontra o personagem pelo ID numérico
            {"$match": {"_id": id_num}},
            
            # JOIN com habilidade_colab
            {"$lookup": {
                "from": "habilidade_colab",
                "localField": "id_colab",
                "foreignField": "_id",
                "as": "habilidades_colaboracao"
            }},
            
            # Formata resultado
            {"$project": {
                "_id": 1,
                "nome": 1,
                "classe": 1,
                "vida": 1,
                "dano": 1,
                "defesa": 1,
                "velocidade_movimento": 1,
                "ataque_basico": 1,
                "habilidades": 1,
                "habilidades_colaboracao": {
                    "$map": {
                        "input": "$habilidades_colaboracao",
                        "as": "hab",
                        "in": {
                            "_id": "$$hab._id",
                            "nome": "$$hab.nome",
                            "descricao": "$$hab.descricao",
                            "duracao": "$$hab.duracao",
                            "efeito_especial": "$$hab.efeito_especial",
                            "cooldown": "$$hab.cooldown",
                            "tipo": "$$hab.tipo",
                            "alcance": "$$hab.alcance",
                            "bonus_habilidade": "$$hab.bonus_habilidade"
                        }
                    }
                }
            }}
        ]
        
        resultados = list(personagem.aggregate(pipeline))
        
        if not resultados:
            return {"erro": f"Personagem com ID {id_num} não encontrado"}
        
        return resultados[0]
        
    except ValueError:
        return {"erro": f"ID '{personagem_id}' inválido. Deve ser um número."}
    except Exception as e:
        return {"erro": f"Erro ao buscar personagem: {str(e)}"}

@router.get("/{personagem_id}/ataque-basico")
def get_ataque_basico(personagem_id: str):
    try:
        id_num = int(personagem_id)
        
        personagem_doc = personagem.find_one(
            {"_id": id_num},
            {"ataque_basico": 1, "nome": 1}
        )
        
        if personagem_doc:
            personagem_doc["_id"] = str(personagem_doc["_id"])
            return {
                "personagem": personagem_doc.get("nome"),
                "ataque_basico": personagem_doc.get("ataque_basico")
            }
        
        return {"erro": "Personagem não encontrado"}
    
    except ValueError:
        return {"erro": f"ID '{personagem_id}' inválido. Deve ser um número."}

@router.get("/{personagem_id}/habilidades")
def get_habilidades(personagem_id: str):
    """
    Retorna TODAS as habilidades (normais + colaboração)
    """
    try:
        id_num = int(personagem_id)
        
        personagem_doc = personagem.find_one(
            {"_id": id_num},
            {"habilidades": 1, "nome": 1, "id_colab": 1}
        )
        
        if not personagem_doc:
            return {"erro": "Personagem não encontrado"}
        
        habilidades_colaboracao = []
        
        if "id_colab" in personagem_doc:
            habilidade_doc = habilidade_colab.find_one({
                "_id": personagem_doc["id_colab"]
            })
            
            if habilidade_doc:
                habilidades_colaboracao.append(habilidade_doc)
        
        # Monta resposta
        return {
            "personagem": personagem_doc.get("nome"),
            "habilidades_normais": personagem_doc.get("habilidades", []),
            "habilidades_colaboracao": habilidades_colaboracao,
            "total_habilidades": len(personagem_doc.get("habilidades", [])) + len(habilidades_colaboracao)
        }
    
    except ValueError:
        return {"erro": f"ID '{personagem_id}' inválido. Deve ser um número."}

@router.get("/{personagem_id}/habilidades-colaboracao")
def get_habilidades_colaboracao(personagem_id: str):

    try:
        id_num = int(personagem_id)
        
        personagem_doc = personagem.find_one(
            {"_id": id_num},
            {"nome": 1, "id_colab": 1}
        )
        
        if not personagem_doc:
            return {"erro": "Personagem não encontrado"}
        
        # Verifica se tem referência
        if "id_colab" not in personagem_doc:
            return {
                "personagem": personagem_doc.get("nome"),
                "mensagem": "Este personagem não tem habilidade de colaboração",
                "habilidades_colaboracao": []
            }
        
        # Busca a habilidade
        habilidade_doc = habilidade_colab.find_one({
            "_id": personagem_doc["id_colab"]
        })
        
        if not habilidade_doc:
            return {"erro": "Habilidade de colaboração não encontrada"}
        
        return {
            "personagem": personagem_doc.get("nome"),
            "habilidade_colaboracao": habilidade_doc
        }
    
    except ValueError:
        return {"erro": f"ID '{personagem_id}' inválido. Deve ser um número."}
    