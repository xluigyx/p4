import multiprocessing
import os
import time
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from ocr_engine import ElectoralOCR

import pymongo

def load_excel_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    excel_path = os.path.join(base_dir, "data", "ingest", "_Recursos Practica 4.xlsx")
    
    if not os.path.exists(excel_path):
        print(f"⚠️ No se encontró el Excel en {excel_path}")
        return

    db_url_oficial = os.environ.get("DB_OFICIAL", "mongodb://db_oficial:27017/oficial_db")
    db_url_rapido = os.environ.get("DB_RAPIDO", "postgresql://postgres:bolivia_vota@db_rapido:5432/rrv_db")
    
    # MongoDB Connection for Oficial
    client = pymongo.MongoClient(db_url_oficial)
    db_mongo = client.get_database()

    # PostgreSQL Connection for RRV
    engine_rapido = create_engine(db_url_rapido)
    
    try:
        print("📊 Cargando datos del Excel a la BD Oficial (MongoDB) y RRV (PostgreSQL)...")
        
        df_dist = pd.read_excel(excel_path, sheet_name="DistribucionTerritorial")
        if not df_dist.empty:
            db_mongo["distribucionterritorial"].insert_many(df_dist.to_dict('records'))
        df_dist.to_sql('distribucionterritorial', engine_rapido, if_exists='append', index=False)
        print("✅ DistribucionTerritorial cargada")
        
        df_recintos = pd.read_excel(excel_path, sheet_name="RecintosElectorales")
        if not df_recintos.empty:
            db_mongo["recintoselectorales"].insert_many(df_recintos.to_dict('records'))
        df_recintos.to_sql('recintoselectorales', engine_rapido, if_exists='append', index=False)
        print("✅ RecintosElectorales cargados")
        
        df_actas = pd.read_excel(excel_path, sheet_name="ActasImpresas")
        if not df_actas.empty:
            db_mongo["actasimpresas"].insert_many(df_actas.to_dict('records'))
        df_actas.to_sql('actasimpresas', engine_rapido, if_exists='append', index=False)
        print(f"✅ ActasImpresas cargadas: {len(df_actas)} actas procesadas.")
        
        df_trans = pd.read_excel(excel_path, sheet_name="Transcripciones")
        if not df_trans.empty:
            db_mongo["transcripciones"].insert_many(df_trans.to_dict('records'))
        df_trans.to_sql('transcripciones', engine_rapido, if_exists='append', index=False)
        print("✅ Transcripciones cargadas")
        
        print("🎉 Carga inicial completada para ambos clústeres.")
    except Exception as e:
        print(f"❌ Error al cargar Excel: {e}")

def bot_worker(bot_id, folder_path):
    ocr = ElectoralOCR()
    print(f"🤖 Bot-{bot_id} activo. Vigilando ráfagas...")
    
    processed_files = set()
    db_url_rapido = os.environ.get("DB_RAPIDO", "postgresql://postgres:bolivia_vota@db_rapido:5432/rrv_db")
    
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
                    conn = psycopg2.connect(db_url_rapido)
                    cursor = conn.cursor()
                    codigo_acta = resultado.get("codigo_acta", archivo)
                    
                    # Inject P1 to P4
                    for cand, cand_votos in [('P1', p1), ('P2', p2), ('P3', p3), ('P4', p4)]:
                        cursor.execute(
                            "INSERT INTO Transcripciones (codigo_acta, candidato, votos) VALUES (%s, %s, %s)",
                            (codigo_acta, cand, cand_votos)
                        )
                    conn.commit()
                    cursor.close()
                    conn.close()
                else:
                    print(f"❌ Error aritmético en {archivo}: {suma} != {votos_validos}")
                    
                if resultado.get("status") == "OBSERVADA":
                    print(f"❌ ALERTA: {archivo} - {resultado.get('motivo')}")
                    
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
                    db_mongo["actas_oficiales"].insert_many(docs_to_insert)
                    print(f"✅ Catálogo {archivo} migrado a MongoDB Oficial ({len(docs_to_insert)} actas).")
            except Exception as e:
                print(f"⚠️ Error al procesar CSV {archivo}: {e}")
            
            processed_files.add(archivo)
            
        time.sleep(2)

if __name__ == "__main__":
    load_excel_data()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    ingest_dir_pdf = os.path.join(base_dir, "ingest", "pdf_actas")
    ingest_dir_csv = os.path.join(base_dir, "ingest", "csv_actas")
    
    # Un bot para CSV
    p_csv = multiprocessing.Process(target=csv_bot_worker, args=(99, ingest_dir_csv))
    p_csv.start()
    
    for i in range(multiprocessing.cpu_count()):
        p = multiprocessing.Process(target=bot_worker, args=(i, ingest_dir_pdf))
        p.start()
