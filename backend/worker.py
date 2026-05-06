import multiprocessing, os, time, pandas as pd, psycopg2, pymongo
from ocr_engine import ElectoralOCR

def load_master_data():
    db_url = os.environ.get("DB_RAPIDO", "postgresql://postgres:bolivia_vota@db_rapido:5432/rrv_db")
    print("📊 [MASTER] Verificando integridad RRV...", flush=True)
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute("ALTER TABLE transcripciones DROP CONSTRAINT IF EXISTS unique_voto")
        cur.execute("ALTER TABLE transcripciones ADD CONSTRAINT unique_voto UNIQUE (codigo_acta, candidato)")
        conn.commit()
        cur.close(); conn.close()
        print("✅ [MASTER] Base de datos verificada y lista.", flush=True)
    except Exception as e: print(f"⚠️ [MASTER] Error DB: {e}", flush=True)

def bot_worker(bot_id, folder_path):
    print(f"🤖 Bot-{bot_id}: Iniciando vigilancia en {folder_path}", flush=True)
    try:
        ocr = ElectoralOCR()
        db_url_pg = os.environ.get("DB_RAPIDO", "postgresql://postgres:bolivia_vota@db_rapido:5432/rrv_db")
        db_url_mg = os.environ.get("DB_OFICIAL", "mongodb://db_oficial:27017/oficial_db")
        processed = set()
        
        while True:
            try:
                if not os.path.exists(folder_path):
                    print(f"⚠️ Bot-{bot_id}: Carpeta no encontrada {folder_path}. Reintentando...", flush=True)
                    os.makedirs(folder_path, exist_ok=True)
                
                # Obtener archivos NO procesados en esta sesión
                archivos = [f for f in os.listdir(folder_path) if f.lower().endswith(('.pdf','.png','.jpg')) and f not in processed]
                
                if archivos:
                    print(f"📸 Bot-{bot_id}: Encontrados {len(archivos)} archivos nuevos.", flush=True)
                
                for f in archivos:
                    cid = f.lower().replace(".pdf","").replace(".png","").replace(".jpg","").replace("acta_","")
                    print(f"🔍 Bot-{bot_id}: Procesando Acta {cid}...", flush=True)
                    
                    full_path = os.path.join(folder_path, f)
                    res = ocr.validar_acta(full_path)
                    v = res.get("votos", {})
                    
                    # Persistencia Postgres
                    try:
                        conn = psycopg2.connect(db_url_pg); cur = conn.cursor()
                        for cand, val in [('Lannister',v.get('P1',0)), ('Targaryen',v.get('P2',0)), ('Baratheon',v.get('P3',0)), ('Stark',v.get('P4',0))]:
                            cur.execute("INSERT INTO transcripciones (codigo_acta, candidato, votos) VALUES (%s,%s,%s) ON CONFLICT (codigo_acta, candidato) DO UPDATE SET votos=EXCLUDED.votos", (cid, cand, val))
                        
                        cur.execute("INSERT INTO logs_auditoria (bot_id, accion, detalles) VALUES (%s,%s,%s)", (f"Bot-{bot_id}", "PROCESO_OK", f"Acta {cid} procesada exitosamente."))
                        conn.commit(); cur.close(); conn.close()
                    except Exception as e: 
                        print(f"❌ Bot-{bot_id} DB Error en {cid}: {e}", flush=True)
                    
                    # Persistencia Mongo
                    if res.get("status") in ["MANCHA_DETECTADA", "OBSERVADA"]:
                        try:
                            m = pymongo.MongoClient(db_url_mg, serverSelectionTimeoutMS=2000)
                            m.get_database()["actas_oficiales"].update_one({"id_acta": cid}, {"$set": {"status": res.get("status"), "reason": res.get("motivo"), "source": "PDF"}}, upsert=True)
                            m.close()
                        except: pass
                        
                    processed.add(f)
                
                time.sleep(3) # Pausa amigable
            except Exception as e: 
                print(f"⚠️ Bot-{bot_id}: Error en bucle: {e}", flush=True)
                time.sleep(2)
    except Exception as e: 
        print(f"❌ Bot-{bot_id}: Error CRÍTICO al iniciar: {e}", flush=True)

if __name__ == "__main__":
    # Forzar rutas absolutas para Docker
    pdf_dir = "/app/ingest/pdf_actas"
    csv_dir = "/app/ingest/csv_oficial"
    
    print(f"🚀 Iniciando Orquestador de Poniente...", flush=True)
    load_master_data()
    
    # Iniciar Bots de Actas PDF
    n_bots = multiprocessing.cpu_count()
    print(f"⚙️ Desplegando {n_bots} bots de procesamiento...", flush=True)
    for i in range(n_bots):
        p = multiprocessing.Process(target=bot_worker, args=(i, pdf_dir))
        p.start()
    
    # Mantener proceso principal vivo
    try:
        while True: time.sleep(60)
    except KeyboardInterrupt:
        print("🛑 Apagando sistema...", flush=True)
