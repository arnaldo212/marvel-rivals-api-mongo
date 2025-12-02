from pymongo import MongoClient
from dotenv import load_dotenv
import os
import certifi

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME", "MarvelRivals")


#cria a conexao
client = MongoClient(MONGODB_URL,
    tlsCAFile=certifi.where()
    )
db = client[DATABASE_NAME]


#colecoes
personagem = db.personagem
habilidade_colab = db.habilidade_colab
jogadores = db.jogadores
partidas = db.partidas
classe = db.classe
cosmeticos = db.cosmeticos


def get_db():
    return db