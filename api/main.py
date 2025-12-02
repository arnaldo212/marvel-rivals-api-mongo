from fastapi import FastAPI
from database.db import personagem, db
from routes import personagens, partidas, jogadores

app = FastAPI()


#rotas
app.include_router(personagens.router)
app.include_router(partidas.router)
app.include_router(jogadores.router)

#CORS
origins = ["https://api-marvel-rivals.onrender.com", "*"]

# Adicione o middleware ao aplicativo
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,              # Lista de origens permitidas
    allow_credentials=True,             # Permite cookies de terceiros
    allow_methods=["*"],                # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"],                # Permite todos os headers
)

# so testando a conexão
@app.get("/")
def root():
    return {
        "message": "API RivalsDB",
        "status": "online"

    }

