from fastapi import FastAPI
from database.db import personagem, db
from routes import personagens, partidas, jogadores

app = FastAPI()


#rotas
app.include_router(personagens.router)
app.include_router(partidas.router)
app.include_router(jogadores.router)

# so testando a conexão
@app.get("/")
def root():
    return {
        "message": "API RivalsDB",
        "status": "online"
    }