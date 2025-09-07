from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import app.schemas.database as database
import os

app = FastAPI(title="FastAPI + Docker Start Initial", version="0.1.0")

# Middleware para CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Arquivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.on_event("startup")
async def startup_event():
    await database.connect_to_mongo()  # conecta ao Mongo

@app.on_event("shutdown")
async def shutdown_event():
    await database.close_mongo_connection()  # fecha conexão

# Rotas HTML
@app.get("/")
async def root():
    return FileResponse(os.path.join("app", "static", "home.html"))

# Buscar todos usuários
@app.get("/show")
async def show_users():
    users_cursor = database.db["usuarios"].find({}, {"_id": 0, "id": 1, "name": 1})
    users = await users_cursor.to_list(length=None)
    return {"usuarios": users} 

# Buscar usuário por ID
@app.get("/user")
async def get_user(id: int):
    users = database.db["usuarios"]
    user = await users.find_one({"id": id}, {"_id": 0, "id": 1, "name": 1})
    if not user:
        return JSONResponse(content={"error": "Usuário não encontrado"}, status_code=404)
    return user

# Criar usuário
@app.post("/create")
async def register(request: Request):
    data = await request.json()
    users = database.db["usuarios"]
    await users.insert_one({"id": data["id"], "name": data["name"]})
    return {"success_message": "User successfully registered"}

# Editar usuário
@app.put("/edit")
async def update(request: Request):
    data = await request.json()
    users = database.db["usuarios"]
    await users.update_one({"id": data["id"]}, {"$set": {"name": data["new_name"]}})
    return {"success_message": "User successfully edited"}

# Deletar usuário
@app.delete("/delete")
async def delete(request: Request):
    data = await request.json()
    users = database.db["usuarios"]
    await users.delete_one({"id": data["id"]})
    return {"success_message": "User successfully deleted"}
