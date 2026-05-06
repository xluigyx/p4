from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocket
import os
import shutil
import redis
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import pymongo

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

INGEST_DIR_RRV = "/app/ingest/rrv"
redis_client = redis.Redis(host='redis_queue', port=6379, db=0)

# Connect to both clusters
DB_OFICIAL_URL = os.environ.get("DB_OFICIAL", "mongodb://db_oficial:27017/oficial_db")
DB_RAPIDO_URL = os.environ.get("DB_RAPIDO", "postgresql://postgres:bolivia_vota@db_rapido:5432/rrv_db")

# MongoDB
client_oficial = pymongo.MongoClient(DB_OFICIAL_URL)
db_oficial = client_oficial.get_database()

engine_rapido = create_engine(DB_RAPIDO_URL)
SessionLocalRapido = sessionmaker(autocommit=False, autoflush=False, bind=engine_rapido)

@app.on_event("startup")
async def startup_event():
    os.makedirs(INGEST_DIR_RRV, exist_ok=True)
    
    # 1. Bucle de espera para Postgres (Resiliencia)
    max_retries = 10
    connected = False
    
    print("⏳ Aguardando conexión con clústers de base de datos...", flush=True)
    for i in range(max_retries):
        try:
            # Ping MongoDB
            client_oficial.admin.command('ping')
            
            # Ping Postgres y verificar integridad
            import psycopg2
            conn = psycopg2.connect(DB_RAPIDO_URL)
            cur = conn.cursor()
            cur.execute("ALTER TABLE transcripciones DROP CONSTRAINT IF EXISTS unique_voto")
            cur.execute("ALTER TABLE transcripciones ADD CONSTRAINT unique_voto UNIQUE (codigo_acta, candidato)")
            conn.commit()
            cur.close()
            conn.close()
            
            print("✅ Conectado exitosamente y base de datos verificada.", flush=True)
            connected = True
            break
        except Exception as e:
            print(f"⚠️ Intento {i+1}/{max_retries}: Base de datos no lista. Reintentando en 5s... ({e})", flush=True)
            await asyncio.sleep(5)
            
    if not connected:
        print("❌ CRITICAL: No se pudo establecer conexión tras varios intentos.", flush=True)

@app.get("/api/health")
async def health_check():
    health = {"db_oficial": "OFFLINE", "db_rapido": "OFFLINE"}
    try:
        client_oficial.admin.command('ping')
        health["db_oficial"] = "ONLINE"
    except: pass
    try:
        with engine_rapido.connect() as conn:
            health["db_rapido"] = "ONLINE"
    except: pass
    return health

@app.post("/api/upload")
async def upload_acta(file: UploadFile = File(...)):
    """ Endpoint para la app móvil """
    file_path = os.path.join(INGEST_DIR_RRV, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"message": "Acta encolada exitosamente", "filename": file.filename}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    pubsub = redis_client.pubsub()
    pubsub.subscribe('dashboard_updates')
    
    try:
        while True:
            # Poll redis messages and send via websocket
            message = pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                data = message['data'].decode('utf-8')
                await websocket.send_text(data)
            await asyncio.sleep(0.1)
    except Exception as e:
        print(f"WebSocket closed: {e}")
        pubsub.unsubscribe()
