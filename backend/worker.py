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
    base_dir = os.path.dirname(os.path.abspath(__file__))
    excel_path = os.path.join(base_dir, "_Recursos Practica 4.xlsx")
    csv_dir = os.path.join(base_dir, "ingest", "csv_oficial")
    
    db_url_oficial = os.environ.get("DB_OFICIAL", "mongodb://db_oficial:27017/oficial_db")
    db_url_rapido = os.environ.get("DB_RAPIDO", "postgresql://postgres:bolivia_vota@db_rapido:5432/rrv_db")
    
    client = pymongo.MongoClient(db_url_oficial)
    db_mongo = client.get_database()
    engine_rapido = create_engine(db_url_rapido)

    print("📊 Iniciando carga de Catálogo Maestro...")
    
    try:
        # Intentar cargar desde CSVs si el Excel no existe
        if not os.path.exists(excel_path):
            print(f"ℹ️ Excel no detectado. Buscando CSVs de infraestructura en {csv_dir}...")
            
            # 1. DistribucionTerritorial
            dt_path = os.path.join(csv_dir, "Recursos Practica 4 - DistribucionTerritorial.csv")
            if os.path.exists(dt_path):
                df = pd.read_csv(dt_path)
                df.to_sql('distribucionterritorial', engine_rapido, if_exists='append', index=False)
                print("✅ DistribucionTerritorial (CSV) -> Postgres")

            # 2. RecintosElectorales
            re_path = os.path.join(csv_dir, "Recursos Practica 4 - RecintosElectorales.csv")
            if os.path.exists(re_path):
                df = pd.read_csv(re_path)
                df.to_sql('recintoselectorales', engine_rapido, if_exists='append', index=False)
                print("✅ RecintosElectorales (CSV) -> Postgres")

            # 3. ActasImpresas
            ai_path = os.path.join(csv_dir, "Recursos Practica 4 - ActasImpresas.csv")
            if os.path.exists(ai_path):
                df = pd.read_csv(ai_path)
                df.to_sql('actasimpresas', engine_rapido, if_exists='append', index=False)
                print(f"✅ ActasImpresas (CSV) -> Postgres ({len(df)} actas)")
        else:
            # Lógica original de Excel (abreviada)
            df_dist = pd.read_excel(excel_path, sheet_name="DistribucionTerritorial")
            df_dist.to_sql('distribucionterritorial', engine_rapido, if_exists='append', index=False)
            df_recintos = pd.read_excel(excel_path, sheet_name="RecintosElectorales")
            df_recintos.to_sql('recintoselectorales', engine_rapido, if_exists='append', index=False)
            df_actas = pd.read_excel(excel_path, sheet_name="ActasImpresas")
            df_actas.to_sql('actasimpresas', engine_rapido, if_exists='append', index=False)
            print("✅ Catálogo maestro cargado desde Excel.")

        # Garantizar Constraint Única
        conn_pg = psycopg2.connect(db_url_rapido)
        cur_pg = conn_pg.cursor()
        cur_pg.execute("ALTER TABLE transcripciones DROP CONSTRAINT IF EXISTS unique_voto")
        cur_pg.execute("ALTER TABLE transcripciones ADD CONSTRAINT unique_voto UNIQUE (codigo_acta, candidato)")
        conn_pg.commit()
        cur_pg.close()
        conn_pg.close()
        print("✅ Restricción 'unique_voto' verificada en Postgres.")

    except Exception as e:
        print(f"⚠️ Error en carga maestra: {e}")

def bot_worker(bot_id, folder_path):
    ocr = ElectoralOCR()
    print(f"🤖 Bot-{bot_id} activo. Vigilando ráfagas...")
    
    processed_files = set()
    db_url_rapido = os.environ.get("DB_RAPIDO", "postgresql://postgres:bolivia_vota@db_rapido:5432/rrv_db")
    
    # 1. Sincronización: Esperar a que el catálogo maestro esté listo
    while True:
        try:
            conn_sync = psycopg2.connect(db_url_rapido)
            cursor_sync = conn_sync.cursor()
            cursor_sync.execute("SELECT COUNT(*) FROM actasimpresas")
            count = cursor_sync.fetchone()[0]
            cursor_sync.close()
            conn_sync.close()
            if count >= 5396:
                print(f"✅ Bot-{bot_id}: Catálogo maestro detectado ({count} actas). Iniciando procesamiento OCR.")
                break
            else:
                print(f"⏳ Bot-{bot_id}: Esperando poblamiento del catálogo maestro (actasimpresas)...")
                time.sleep(5)
        except Exception as e:
            print(f"⏳ Bot-{bot_id}: Esperando base de datos RRV... {e}")
            time.sleep(5)
    
    while True:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)
            
        archivos = [f for f in os.listdir(folder_path) if f.endswith(('.pdf', '.png', '.jpg')) and f not in processed_files]
        for archivo in archivos:
            full_path = os.path.join(folder_path, archivo)
            print(f"📸 Bot-{bot_id} procesando acta: {archivo}")
            
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
                    raw_codigo = resultado.get("codigo_acta", archivo)
                    # Limpieza de ID
                    codigo_acta = raw_codigo.lower().replace("acta_", "").replace(".pdf", "").replace(".png", "").replace(".jpg", "")
                    
                    max_retries = 2 # Intentar una vez extra
                    
                    for attempt in range(max_retries):
                        conn = None
                        try:
                            conn = psycopg2.connect(db_url_rapido)
                            cursor = conn.cursor()
                            
                            # Inject Lannister to Stark
                            for cand, cand_votos in [('Lannister', p1), ('Targaryen', p2), ('Baratheon', p3), ('Stark', p4)]:
                                cursor.execute(
                                    "INSERT INTO transcripciones (codigo_acta, candidato, votos) VALUES (%s, %s, %s) ON CONFLICT (codigo_acta, candidato) DO NOTHING",
                                    (codigo_acta, cand, cand_votos)
                                )
                                time.sleep(0.1) # Reducir la presión sobre la base de datos
                                
                            conn.commit()
                            cursor.close()
                            break # Exito, salir del bucle de reintentos
                            
                        except psycopg2.errors.DeadlockDetected:
                            if conn is not None:
                                conn.rollback()
                            print(f"⚠️ Deadlock detectado en {archivo}. Esperando 0.5 segundos para reintentar ({attempt+1}/{max_retries})...")
                            time.sleep(0.5)
                            
                        except psycopg2.errors.ForeignKeyViolation as fk_err:
                            if conn is not None:
                                conn.rollback()
                            print(f"⚠️ Ignorando acta no oficial (Llave Foránea) - {codigo_acta}: {fk_err.pgerror}")
                            break # Continuar sin reintentar ni fallar por completo
                            
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
                print(f"⚠️ Error al procesar o insertar el archivo {archivo}: {e}")
                
            # Keep track without moving files (avoids Cross-Device Link error)
            processed_files.add(archivo)
        
        time.sleep(2)

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
    load_master_data()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    ingest_dir_pdf = os.path.join(base_dir, "ingest", "pdf_actas")
    ingest_dir_csv = os.path.join(base_dir, "ingest", "csv_oficial")
    
    # Un bot para CSV
    p_csv = multiprocessing.Process(target=csv_bot_worker, args=(99, ingest_dir_csv))
    p_csv.start()
    
    for i in range(multiprocessing.cpu_count()):
        p = multiprocessing.Process(target=bot_worker, args=(i, ingest_dir_pdf))
        p.start()
