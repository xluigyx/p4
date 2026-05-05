from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocket
import os
import shutil
import redis
import asyncio

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

INGEST_DIR = "/app/ingest"
redis_client = redis.Redis(host='redis', port=6379, db=0)

@app.on_event("startup")
async def startup_event():
    os.makedirs(INGEST_DIR, exist_ok=True)

@app.post("/api/upload")
async def upload_acta(file: UploadFile = File(...)):
    """ Endpoint para la app móvil """
    file_path = os.path.join(INGEST_DIR, file.filename)
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
