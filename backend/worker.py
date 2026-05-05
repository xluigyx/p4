import os
import time
import json
import logging
from multiprocessing import Process
import psycopg2
import redis
from ocr_engine import ElectoralOCR

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(processName)s] - %(message)s')

INGEST_DIR = "/app/ingest"
redis_client = redis.Redis(host='redis', port=6379, db=0)

def get_db_connection():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "db-primary"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASS", "admin"),
        dbname=os.environ.get("DB_NAME", "elections_db")
    )

def bot_worker(worker_id):
    logger = logging.getLogger(f"Bot-{worker_id}")
    logger.info(f"Worker {worker_id} started, watching {INGEST_DIR}")
    ocr = ElectoralOCR()
    
    while True:
        try:
            # Simple directory polling for simulation
            if not os.path.exists(INGEST_DIR):
                os.makedirs(INGEST_DIR, exist_ok=True)
                
            files = [f for f in os.listdir(INGEST_DIR) if f.endswith(('.jpg', '.png', '.pdf'))]
            for filename in files:
                file_path = os.path.join(INGEST_DIR, filename)
                
                # Check if file is still being written
                if os.path.getsize(file_path) == 0:
                    continue
                    
                # Process the file
                logger.info(f"Processing {filename}")
                
                data = ocr.process_acta(file_path)
                
                # Validations
                errors = []
                if data['p1'] + data['p2'] + data['p3'] + data['p4'] != data['validos']:
                    errors.append(f"Mesa {data['codigo_mesa']} observada por discrepancia en suma de candidatos")
                
                if data['validos'] + data['blancos'] + data['nulos'] != data['papeletas_anfora']:
                    errors.append(f"Mesa {data['codigo_mesa']} observada por discrepancia en ánfora")
                
                if not data['firmas_detectadas']:
                    errors.append(f"Mesa {data['codigo_mesa']} observada por falta de firmas")
                
                status = "VALIDADA" if not errors else "OBSERVADA"
                
                # Log detailed error
                for err in errors:
                    logger.warning(err)
                
                # Send WebSocket notification via Redis PubSub
                redis_client.publish('dashboard_updates', json.dumps({
                    "type": "ocr_log",
                    "mesa": data['codigo_mesa'],
                    "status": status,
                    "errors": errors,
                    "worker": worker_id
                }))
                
                # CQRS: Write to DB
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO acta_events (acta_id, event_type, payload) VALUES (%s, %s, %s)",
                        (data['codigo_mesa'], status, json.dumps(data))
                    )
                    conn.commit()
                    cursor.close()
                    conn.close()
                except Exception as db_err:
                    logger.error(f"DB Error: {db_err}")

                # Remove file after processing
                os.remove(file_path)
                
        except Exception as e:
            logger.error(f"Worker Error: {e}")
            
        time.sleep(2) # Polling interval

if __name__ == "__main__":
    NUM_BOTS = 3
    processes = []
    
    for i in range(NUM_BOTS):
        p = Process(target=bot_worker, args=(i,), name=f"Bot-{i}")
        p.start()
        processes.append(p)
        
    for p in processes:
        p.join()
