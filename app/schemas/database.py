from motor.motor_asyncio import AsyncIOMotorClient

# Dados do MongoDB
MONGO_USER = "admin"
MONGO_PASS = "secret"
MONGO_HOST = "db"          # nome do serviço do MongoDB no docker-compose
MONGO_PORT = 27017
DB_NAME = "mydatabase"

# String de conexão
MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/{DB_NAME}?authSource=admin"

# Variáveis globais
client = None
db = None

# Conectar ao Mongo
async def connect_to_mongo():
    global client, db
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    print("✅ Conectado ao MongoDB!")

# Fechar conexão
async def close_mongo_connection():
    global client
    if client:
        client.close()
        print("❌ Conexão encerrada")
