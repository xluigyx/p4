import multiprocessing
import os
import time
import pandas as pd
import psycopg2
import psycopg2.errors
from sqlalchemy import create_engine
from ocr_engine import ElectoralOCR

import pymongo

def load_master_data():
    """Carga datos maestros exclusivamente en MongoDB Oficial (si aplica)"""
    db_url_rapido = os.environ.get("DB_RAPIDO", "postgresql://postgres:bolivia_vota@db_rapido:5432/rrv_db")
    
    print("📊 Verificando integridad de la base de datos RRV...", flush=True)
    
    try:
        # Solo garantizamos la restricción de unicidad en la tabla de actas
        conn_pg = psycopg2.connect(db_url_rapido)
        cur_pg = conn_pg.cursor()
        cur_pg.execute("ALTER TABLE transcripciones DROP CONSTRAINT IF EXISTS unique_voto")
        cur_pg.execute("ALTER TABLE transcripciones ADD CONSTRAINT unique_voto UNIQUE (codigo_acta, candidato)")
        conn_pg.commit()
        cur_pg.close()
        conn_pg.close()
        print("✅ Restricción 'unique_voto' verificada en Postgres.")

    except Exception as e:
        print(f"⚠️ Error en inicialización RRV: {e}")

def bot_worker(bot_id, folder_path):
    try:
        ocr = ElectoralOCR()
        print(f"🤖 Bot-{bot_id} activo. Vigilando ráfagas...", flush=True)
        
        processed_files = set()
        db_url_rapido = os.environ.get("DB_RAPIDO", "postgresql://postgres:bolivia_vota@db_rapido:5432/rrv_db")
        
        # Sincronización eliminada: RRV procesa actas de forma inmediata
        print(f"✅ Bot-{bot_id}: Iniciando procesamiento OCR directo.", flush=True)
    
    while True:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)
            
        archivos = [f for f in os.listdir(folder_path) if f.endswith(('.pdf', '.png', '.jpg')) and f not in processed_files]
        for archivo in archivos:
            full_path = os.path.join(folder_path, archivo)
            print(f"📸 Bot-{bot_id} procesando acta: {archivo}", flush=True)
            
            try:
                resultado = ocr.validar_acta(full_path)
                
                # Validation: P1 + P2 + P3 + P4 == valid_votes
                votos = resultado.get("votos", {})
                p1 = votos.get("P1", 0)
                p2 = votos.get("P2", 0)
                p3 = votos.get("P3", 0)
                p4 = votos.get("P4", 0)
                votos_validos = resultado.get("votos_validos", p1+p2+p3+p4)
                
                suma = p1 + p2 + p3 + p4
                if suma == votos_validos:
                    print(f"✅ Acta {archivo} validada aritméticamente ({suma} votos).")
                    
                    # Transfer data to RRV cluster using psycopg2
                    # Transfer data to RRV cluster using psycopg2
                    raw_codigo = resultado.get("codigo_acta", archivo)
                    
                    # Limpieza de ID Robusta (ej. 'acta_123.pdf' -> '123')
                    codigo_acta = raw_codigo.lower()
                    for ext in [".pdf", ".png", ".jpg", ".jpeg"]:
                        codigo_acta = codigo_acta.replace(ext, "")
                    codigo_acta = codigo_acta.replace("acta_", "")
                    
                    max_retries = 2 
                    
                    for attempt in range(max_retries):
                        conn = None
                        try:
                            conn = psycopg2.connect(db_url_rapido)
                            cursor = conn.cursor()
                            
                            # Inject Lannister to Stark
                            for cand, cand_votos in [('Lannister', p1), ('Targaryen', p2), ('Baratheon', p3), ('Stark', p4)]:
                                cursor.execute(
                                    """INSERT INTO transcripciones (codigo_acta, candidato, votos) 
                                       VALUES (%s, %s, %s) 
                                       ON CONFLICT (codigo_acta, candidato) 
                                       DO UPDATE SET votos = EXCLUDED.votos, creado_at = CURRENT_TIMESTAMP""",
                                    (codigo_acta, cand, cand_votos)
                                )
                                
                            # Registrar en logs de auditoría SQL
                            cursor.execute(
                                "INSERT INTO logs_auditoria (bot_id, accion, detalles) VALUES (%s, %s, %s)",
                                (f"Bot-{bot_id}", "PROCESAMIENTO_ACTA", f"Acta {codigo_acta} procesada con {suma} votos totales.")
                            )
                                
                            conn.commit()
                            cursor.close()
                            break 
                            
                        except psycopg2.errors.DeadlockDetected:
                            if conn is not None:
                                conn.rollback()
                            print(f"⚠️ Deadlock detectado en {archivo}. Reintentando ({attempt+1}/{max_retries})...")
                            time.sleep(0.5)
                            
                        except Exception as e:
                            if conn is not None:
                                conn.rollback()
                            print(f"❌ Error DB en {archivo}: {e}")
                            break
                            
                        finally:
                            if conn is not None:
                                conn.close()
                else:
                    print(f"❌ Error aritmético en {archivo}: {suma} != {votos_validos}")
                    
                if resultado.get("status") in ["OBSERVADA", "ANULABLE", "MANCHA_CRITICA"]:
                    print(f"❌ ALERTA OCR: {archivo} - {resultado.get('motivo')}")
                    # Enviar estado a la Bitácora de Svelte (MongoDB)
                    db_url_oficial = os.environ.get("DB_OFICIAL", "mongodb://db_oficial:27017/oficial_db")
                    client = pymongo.MongoClient(db_url_oficial)
                    db_mongo = client.get_database()
                    
                    db_mongo["actas_oficiales"].update_one(
                        {"id_acta": codigo_acta},
                        {"$set": {
                            "status": resultado.get("status"), 
                            "reason": resultado.get("motivo"),
                            "source": "PDF"
                        }},
                        upsert=True
                    )
            except Exception as e:
                print(f"⚠️ Error al procesar o insertar el archivo {archivo}: {e}", flush=True)
                
            # Keep track without moving files (avoids Cross-Device Link error)
            processed_files.add(archivo)
        
        time.sleep(2)
    except Exception as e:
        print(f"CRITICAL: Bot-{bot_id} murió por error: {e}", flush=True)

def csv_bot_worker(bot_id, folder_path):
    print(f"🤖 CSV-Bot-{bot_id} activo. Vigilando ráfagas CSV Oficiales...")
    processed_files = set()
    db_url_oficial = os.environ.get("DB_OFICIAL", "mongodb://db_oficial:27017/oficial_db")
    client = pymongo.MongoClient(db_url_oficial)
    db_mongo = client.get_database()
    
    db_mongo["actas_oficiales"].create_index("id_acta", unique=True)
    
    while True:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)
            
        archivos = [f for f in os.listdir(folder_path) if f.endswith('.csv') and f not in processed_files]
        for archivo in archivos:
            full_path = os.path.join(folder_path, archivo)
            print(f"📄 CSV-Bot-{bot_id} procesando catálogo maestro: {archivo}")
            try:
                df = pd.read_csv(full_path)
                # Validar y normalizar
                docs_to_insert = []
                for _, row in df.iterrows():
                    lannister = max(0, int(row.get('lannister', row.get('P1', 0))))
                    targaryen = max(0, int(row.get('targaryen', row.get('P2', 0))))
                    baratheon = max(0, int(row.get('baratheon', row.get('P3', 0))))
                    stark_raw = int(row.get('stark', row.get('P4', 0)))
                    stark = max(0, stark_raw)
                    
                    if stark_raw < 0:
                        status = "OBSERVADO"
                        reason = "Valor negativo en P4"
                    else:
                        status = "EXITO"
                        reason = "-"

                    doc = {
                        "id_acta": str(row.get('id_acta', row.get('codigo_acta', ''))),
                        "departamento": str(row.get('departamento', row.get('desc_dep', ''))),
                        "votos": {
                            "lannister": lannister,
                            "targaryen": targaryen,
                            "baratheon": baratheon,
                            "stark": stark
                        },
                        "status": status,
                        "reason": reason
                    }
                    docs_to_insert.append(doc)
                
                if docs_to_insert:
                    # Insertar ignorando duplicados
                    try:
                        db_mongo["actas_oficiales"].insert_many(docs_to_insert, ordered=False)
                    except pymongo.errors.BulkWriteError:
                        pass # Ignore duplicate key errors
                    print(f"✅ CSV-Bot: {archivo} migrado exclusivamente a MongoDB Oficial.")
                
                
            except Exception as e:
                print(f"⚠️ Error al procesar CSV {archivo}: {e}")
            
            processed_files.add(archivo)
            
        time.sleep(2)

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ingest_dir_pdf = os.path.join(base_dir, "ingest", "pdf_actas")
    ingest_dir_csv = os.path.join(base_dir, "ingest", "csv_oficial")
    
    # 1. ARRANCAR BOTS PRIMERO (No bloqueante)
    print("🚀 Iniciando escuadrón de bots...", flush=True)
    
    # Un bot para CSV
    p_csv = multiprocessing.Process(target=csv_bot_worker, args=(99, ingest_dir_csv))
    p_csv.start()
    
    for i in range(multiprocessing.cpu_count()):
        p = multiprocessing.Process(target=bot_worker, args=(i, ingest_dir_pdf))
        p.start()
        
    print(f"✅ {multiprocessing.cpu_count()} bots desplegados y trabajando.", flush=True)
    
    # 2. VERIFICACIÓN DE INTEGRIDAD (Después de arrancar)
    load_master_data()
    
    # Mantener el proceso padre vivo
    try:
        while True:
            time.sleep(30)
    except KeyboardInterrupt:
        print("Stopping worker...", flush=True)
