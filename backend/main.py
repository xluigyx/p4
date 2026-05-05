from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocket
import os
import shutil
import redis
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

INGEST_DIR_RRV = "/app/ingest/rrv"
redis_client = redis.Redis(host='redis_queue', port=6379, db=0)

# Connect to both clusters
DB_OFICIAL_URL = os.environ.get("DB_OFICIAL", "postgresql://postgres:bolivia_vota@db_oficial:5432/oficial_db")
DB_RAPIDO_URL = os.environ.get("DB_RAPIDO", "postgresql://postgres:bolivia_vota@db_rapido:5432/rrv_db")

engine_oficial = create_engine(DB_OFICIAL_URL)
SessionLocalOficial = sessionmaker(autocommit=False, autoflush=False, bind=engine_oficial)

engine_rapido = create_engine(DB_RAPIDO_URL)
SessionLocalRapido = sessionmaker(autocommit=False, autoflush=False, bind=engine_rapido)

@app.on_event("startup")
async def startup_event():
    os.makedirs(INGEST_DIR_RRV, exist_ok=True)
    # Ping both databases to ensure connectivity
    try:
        with engine_oficial.connect() as conn:
            print("Conectado exitosamente a DB_OFICIAL")
        with engine_rapido.connect() as conn:
            print("Conectado exitosamente a DB_RAPIDO")
    except Exception as e:
        print(f"Error conectando a las BD: {e}")

@app.get("/api/health")
async def health_check():
    health = {"db_oficial": "OFFLINE", "db_rapido": "OFFLINE"}
    try:
        with engine_oficial.connect() as conn:
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
