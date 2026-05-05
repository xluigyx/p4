import os
import time
import json
import logging
import multiprocessing
import psycopg2
import redis
from ocr_engine import ElectoralOCR
import csv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(processName)s] - %(message)s')

redis_client = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

def get_db_connection():
    # Intenta conectar al primario, si falla, va al replica (Failover manual simple)
    host = os.environ.get("DB_HOST", "db-primary")
    replica_host = os.environ.get("DB_REPLICA_HOST", "db-replica")
    user = os.environ.get("DB_USER", "postgres")
    password = os.environ.get("DB_PASS", "admin")
    dbname = os.environ.get("DB_NAME", "elections_db")
    
    try:
        return psycopg2.connect(host=host, user=user, password=password, dbname=dbname, connect_timeout=3)
    except psycopg2.OperationalError as e:
        logging.warning(f"Primary DB failed, failing over to replica {replica_host}: {e}")
        return psycopg2.connect(host=replica_host, user=user, password=password, dbname=dbname, connect_timeout=3)

def process_csv(file_path):
    try:
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return next(reader, None)
    except Exception:
        return None

def bot_worker(worker_id):
    logger = logging.getLogger(f"Bot-{worker_id}")
    logger.info(f"Bot-{worker_id} started. Monitoring Redis queues: 'queue:oficial', 'queue:rrv'")
    ocr = ElectoralOCR()
    
    while True:
        try:
            # Vigila la cola de Redis (bloqueante por 2 segundos para permitir graceful shutdown si se desea)
            task = redis_client.brpop(['queue:oficial', 'queue:rrv'], timeout=2)
            if not task:
                continue
                
            queue_name, task_data_str = task
            task_data = json.loads(task_data_str)
            file_path = task_data.get('file_path')
            
            if not file_path or not os.path.exists(file_path):
                logger.warning(f"File not found: {file_path}")
                continue
                
            logger.info(f"Processing task from {queue_name}: {file_path}")
            
            is_oficial = queue_name == 'queue:oficial'
            
            if is_oficial:
                data = process_csv(file_path)
                if not data:
                    logger.warning(f"Failed to read CSV: {file_path}")
                    continue
                status = "VALIDADA"
                errors = []
                codigo_mesa = data.get('codigo_mesa', 'DESCONOCIDA')
            else:
                data = ocr.process_acta(file_path)
                if not data:
                    logger.warning(f"Failed to read OCR: {file_path}")
                    continue
                
                status = data.get("estado_validacion", "VALIDADA")
                errors = []
                if status == "OBSERVADA":
                    errors.append(data.get("mensaje_error", "Error desconocido"))
                
                codigo_mesa = data.get('codigo_mesa', 'DESCONOCIDA')

            for err in errors:
                logger.warning(f"Mesa {codigo_mesa}: {err}")
            
            # Notifica al Dashboard por WebSockets a través de PubSub
            redis_client.publish('dashboard_updates', json.dumps({
                "type": "ocr_log",
                "mesa": codigo_mesa,
                "status": status,
                "errors": errors,
                "worker": worker_id,
                "source": "OFICIAL" if is_oficial else "RRV"
            }))
            
            # Escribir en Event Sourcing DB
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO acta_events (acta_id, event_type, payload) VALUES (%s, %s, %s)",
                    (codigo_mesa, f"{status}_{'OFICIAL' if is_oficial else 'RRV'}", json.dumps(data))
                )
                conn.commit()
                cursor.close()
                conn.close()
                logger.info(f"Saved {codigo_mesa} event to DB.")
            except Exception as db_err:
                logger.error(f"DB Insert Error: {db_err}")
                
        except Exception as e:
            logger.error(f"Worker Error: {e}")
            time.sleep(1)

def orchestrator():
    # Directorios de simulación
    os.makedirs("/app/ingest/oficial", exist_ok=True)
    os.makedirs("/app/ingest/rrv", exist_ok=True)
    
    # Orquestador simple que simula inyectar tareas a Redis leyendo directorios
    # En un caso real, otro microservicio subiría los archivos y empujaría a la cola
    while True:
        try:
            for q_type, d_path in [('queue:oficial', '/app/ingest/oficial'), ('queue:rrv', '/app/ingest/rrv')]:
                for f in os.listdir(d_path):
                    f_path = os.path.join(d_path, f)
                    if os.path.isfile(f_path):
                        # Evita procesar archivos vacíos temporalmente
                        if os.path.getsize(f_path) > 0:
                            redis_client.lpush(q_type, json.dumps({"file_path": f_path}))
                            # Renombra para no re-procesar (simulación)
                            os.rename(f_path, f_path + ".processing")
        except Exception as e:
            logging.error(f"Orchestrator error: {e}")
        time.sleep(5)

if __name__ == "__main__":
    cores = multiprocessing.cpu_count()
    logging.info(f"Arrancando Orquestador con {cores} bots...")
    
    processes = []
    
    # Arranca el thread/proceso orquestador (simulador de ingesta)
    p_orch = multiprocessing.Process(target=orchestrator, name="Orchestrator")
    p_orch.start()
    processes.append(p_orch)
    
    # Arranca bots
    for i in range(cores):
        p = multiprocessing.Process(target=bot_worker, args=(i,), name=f"Bot-{i}")
        p.start()
        processes.append(p)
        
    for p in processes:
        p.join()
