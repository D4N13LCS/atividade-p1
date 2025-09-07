# 🚀 FastAPI + MongoDB com Docker

Este projeto utiliza **FastAPI** (Python 3.12) como API e **MongoDB 6.0** como banco de dados, orquestrados via **Docker Compose**.  
Abaixo estão explicações detalhadas de cada arquivo (`Dockerfile` e `docker-compose.yaml`) para facilitar a compreensão.

---

# 📂 Estrutura Básica
```bash
├── app/ # Código da aplicação FastAPI
| └── routers/
|   ├── health.py # arquivo de teste para checar a inicialização do projeto
| └── schemas/
|   ├── database.py # conexão com o mongodb
| └── static/ # arquivos estáticos
|   ├── home.html
|   ├── style.css
│ ├── main.py # Ponto de entrada da aplicação
├── requirements.txt # Dependências Python
├── Dockerfile # Imagem da API FastAPI
└── docker-compose.yaml # Orquestração dos serviços (API + DB)

```
---

## 🛠️ app/routers/health.py

```python
from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["healt"])

@router.get("")
def healthcheck():
    return {"status": "ok"}

```

- Define uma rota simples de saúde (/health) para checar se a API está em funcionamento.

- Retorna {"status": "ok"}.

- Útil para monitoramento.

## 🗄️ app/schemas/database.py

```python
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_USER = "admin"
MONGO_PASS = "secret"
MONGO_HOST = "db"
MONGO_PORT = 27017
DB_NAME = "mydatabase"

MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/{DB_NAME}?authSource=admin"

client = None
db = None

async def connect_to_mongo():
    global client, db
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    print("✅ Conectado ao MongoDB!")

async def close_mongo_connection():
    global client
    if client:
        client.close()
        print("❌ Conexão encerrada")

```

- Faz a conexão com o MongoDB usando motor (driver assíncrono para Python), biblioteca construída com base na biblioteca pymongo.

- Configurações (usuário, senha, host e porta) estão alinhadas com o docker-compose.yaml.

- Expõe duas funções principais:

    - connect_to_mongo(): conecta ao banco e inicializa a variável db.

    - close_mongo_connection(): encerra a conexão de forma segura.

## 🚀 app/main.py

```python

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import app.schemas.database as database
import os

app = FastAPI(title="FastAPI + Docker Start Initial", version="0.1.0")

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Arquivos estáticos (HTML + CSS)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Eventos de conexão ao Mongo
@app.on_event("startup")
async def startup_event():
    await database.connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_event():
    await database.close_mongo_connection()

# Rota inicial (interface HTML)
@app.get("/")
async def root():
    return FileResponse(os.path.join("app", "static", "home.html"))

# CRUD Usuários
@app.get("/show")      # Listar usuários
@app.get("/user")      # Buscar usuário por ID
@app.post("/create")   # Criar usuário
@app.put("/edit")      # Editar usuário
@app.delete("/delete") # Deletar usuário


```

- Configuração da API com título e versão.

- Middleware CORS liberado para qualquer origem (útil em desenvolvimento).

- Eventos do ciclo de vida:

    - startup: conecta ao Mongo.

    - shutdown: fecha a conexão.

- Rotas:

    - <code>/</code> → Retorna a interface HTML (home.html).

    - <code>/show</code> → Lista todos os usuários do MongoDB.

    - <code>/user?id={id}</code> → Busca um usuário específico.

    - <code>/create</code> → Cria um novo usuário.

    - <code>/edit</code> → Atualiza o nome de um usuário.

    - <code>/delete</code> → Remove um usuário.

## 🖼️ app/static/home.html

<img width="1600" height="529" alt="image" src="https://github.com/user-attachments/assets/2276dda1-bb66-412a-b4ba-75db4914e9e9" />


Página simples que serve como UI para a API.

Contém:

Formulário para criar usuários.

Listagem dinâmica de usuários consumindo a API (/show).

Botões Editar e Deletar, que fazem requisições PUT e DELETE respectivamente.

Scripts JavaScript integrados fazem as chamadas à API com fetch().

## 🎨 app/static/style.css

Define tema escuro com cores base (bg, card, accent, etc.).

Estiliza cards, botões (create, edit, delete) e layout responsivo.

Usa flexbox e grid para organizar o conteúdo.

Responsividade garantida com @media (max-width:880px).

## 🐳 Dockerfile (API)

```docker 
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN python -m pip install --upgrade pip

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main", "--host", "0.0.0.0", "--port", "8000", "--reload"]

```

### 🔎 Explicação

- Base: Usa a imagem leve python:3.12-slim.

- ENV:

    - PYTHONDONTWRITEBYTECODE=1: evita criação de arquivos .pyc.

    - PYTHONUNBUFFERED=1: garante que logs apareçam em tempo real no terminal.

    - PIP_NO_CACHE_DIR=1: evita cache do pip (reduz tamanho da imagem).

- WORKDIR /app: Define a pasta /app como diretório de trabalho.

- requirements.txt: Copiado e instalado antes do código (melhora cache da build).

- COPY app ./app: Copia a aplicação FastAPI.

- EXPOSE 8000: Expõe a porta 8000 (onde o Uvicorn rodará).

- CMD: Comando para iniciar a API com Uvicorn em modo reload (hot-reload para desenvolvimento).

## 🐙 docker-compose.yaml (Orquestração)

```yaml
services:
  api:
    container_name: fastapi-dev
    restart: always
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./app:/app/app:rw
    environment:
      - PYTHONPATH=/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    depends_on:
      - db

  db:
    image: mongo:6.0
    container_name: mongo-dev
    restart: always
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=secret
      - MONGO_INITDB_DATABASE=mydatabase
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

volumes:
  mongo_data:

```

### 🔎 Explicação
- Serviço API (FastAPI)

    - container_name: Nome do container → fastapi-dev.

    - build: Cria a imagem da API com base no Dockerfile.

    - ports: Expõe a API em http://localhost:8000.

    - volumes: Monta o código local (./app) dentro do container, permitindo hot-reload.

    - environment: Define PYTHONPATH=/app para facilitar importações.

    - command: Roda a aplicação FastAPI com Uvicorn.

    - depends_on: Garante que o MongoDB suba antes da API.

- Serviço DB (MongoDB)

    - image: Usa mongo:6.0.

    - container_name: Nome do container → mongo-dev.

    - environment:

    - Usuário root: admin

    - Senha root: secret

    - Database inicial: mydatabase

    - ports: Expõe o MongoDB em localhost:27017.

    - volumes: Usa volume mongo_data para persistir dados do banco.

## ▶️ Como Rodar o Projeto

1. Build e subida dos containers

abra no terminal e execute o seguinte comando: <code>docker-compose up --build</code>

2. Acessar a API

Acesse http://localhost:8000 no navegador
