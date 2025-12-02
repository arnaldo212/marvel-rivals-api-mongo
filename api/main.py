from fastapi import FastAPI
from database.db import personagem, db
from routes import personagens, partidas, jogadores

app = FastAPI()


#rotas
app.include_router(personagens.router)
app.include_router(partidas.router)
app.include_router(jogadores.router)


origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",  # Exemplo para React/Next.js
    "http://127.0.0.1:5500", # Exemplo para Live Server do VS Code
    "http://127.0.0.1",
    "http://127.0.0.1:5173",
    "https://seu-dominio-frontend.com",
]

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
