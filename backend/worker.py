import os
import time
import json
import logging
from multiprocessing import Process
import psycopg2
import redis
from ocr_engine import ElectoralOCR
import csv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(processName)s] - %(message)s')

INGEST_DIR = "/app/ingest"
redis_client = redis.Redis(host='redis', port=6379, db=0)

def get_db_connection(cluster_type="B"):
    # Cluster A para CSV (Oficial), Cluster B para OCR (Rápido)
    host_env = "DB_HOST_A" if cluster_type == "A" else "DB_HOST_B"
    # Fallback to db-primary si no está definido (por ej., en dev)
    host = os.environ.get(host_env, "db-primary")
    
    return psycopg2.connect(
        host=host,
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASS", "admin"),
        dbname=os.environ.get("DB_NAME", "elections_db")
    )

def process_csv(file_path):
    # Lógica de lectura CSV (Oficial)
    try:
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Retornar la primera fila como dict por simplicidad
            return next(reader, None)
    except Exception as e:
        return None

def bot_worker(worker_id):
    logger = logging.getLogger(f"Bot-{worker_id}")
    logger.info(f"Worker {worker_id} started, watching {INGEST_DIR}")
    ocr = ElectoralOCR()
    
    while True:
        try:
            if not os.path.exists(INGEST_DIR):
                os.makedirs(INGEST_DIR, exist_ok=True)
                
            files = [f for f in os.listdir(INGEST_DIR) if f.endswith(('.jpg', '.png', '.pdf', '.csv'))]
            for filename in files:
                file_path = os.path.join(INGEST_DIR, filename)
                
                if os.path.getsize(file_path) == 0:
                    continue
                    
                logger.info(f"Processing {filename}")
                
                is_csv = filename.endswith('.csv')
                cluster_target = "A" if is_csv else "B"
                
                if is_csv:
                    data = process_csv(file_path)
                    if not data:
                        logger.warning(f"Failed to read CSV: {filename}")
                        os.remove(file_path)
                        continue
                    status = "VALIDADA"
                    errors = []
                    codigo_mesa = data.get('codigo_mesa', 'DESCONOCIDA')
                else:
                    data = ocr.process_acta(file_path)
                    if not data:
                        logger.warning(f"Failed to read OCR: {filename}")
                        os.remove(file_path)
                        continue
                    
                    status = data.get("estado_validacion", "VALIDADA")
                    errors = []
                    if status == "OBSERVADA":
                        errors.append(data.get("mensaje_error", "Error desconocido"))
                    
                    if data.get('validos', 0) + data.get('blancos', 0) + data.get('nulos', 0) != data.get('papeletas_anfora', 0):
                        errors.append(f"Mesa {data['codigo_mesa']} observada por discrepancia en ánfora")
                        status = "OBSERVADA"
                    
                    if not data.get('firmas_detectadas', False):
                        errors.append(f"Mesa {data['codigo_mesa']} observada por falta de firmas")
                        status = "OBSERVADA"
                    
                    codigo_mesa = data['codigo_mesa']

                for err in errors:
                    logger.warning(err)
                
                redis_client.publish('dashboard_updates', json.dumps({
                    "type": "ocr_log",
                    "mesa": codigo_mesa,
                    "status": status,
                    "errors": errors,
                    "worker": worker_id,
                    "source": "CSV" if is_csv else "OCR",
                    "cluster": cluster_target
                }))
                
                # Escribir en la base de datos correspondiente (Cluster A o B)
                try:
                    conn = get_db_connection(cluster_type=cluster_target)
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO acta_events (acta_id, event_type, payload) VALUES (%s, %s, %s)",
                        (codigo_mesa, f"{status}_{'OFICIAL' if is_csv else 'RRV'}", json.dumps(data))
                    )
                    conn.commit()
                    cursor.close()
                    conn.close()
                    logger.info(f"Saved {filename} to Cluster {cluster_target}")
                except Exception as db_err:
                    logger.error(f"DB Error (Cluster {cluster_target}): {db_err}")

                os.remove(file_path)
                
        except Exception as e:
            logger.error(f"Worker Error: {e}")
            
        time.sleep(2)

if __name__ == "__main__":
    NUM_BOTS = 4
    processes = []
    
    for i in range(NUM_BOTS):
        p = Process(target=bot_worker, args=(i,), name=f"Bot-{i}")
        p.start()
        processes.append(p)
        
    for p in processes:
        p.join()
