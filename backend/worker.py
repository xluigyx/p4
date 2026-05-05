import multiprocessing
import os
import time
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from ocr_engine import ElectoralOCR

def load_excel_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    excel_path = os.path.join(base_dir, "data", "ingest", "_Recursos Practica 4.xlsx")
    
    if not os.path.exists(excel_path):
        print(f"⚠️ No se encontró el Excel en {excel_path}")
        return

    db_url_oficial = os.environ.get("DB_OFICIAL", "postgresql://postgres:bolivia_vota@db_oficial:5432/oficial_db")
    db_url_rapido = os.environ.get("DB_RAPIDO", "postgresql://postgres:bolivia_vota@db_rapido:5432/rrv_db")
    
    engine_oficial = create_engine(db_url_oficial)
    engine_rapido = create_engine(db_url_rapido)
    
    try:
        print("📊 Cargando datos del Excel a la BD Oficial y RRV...")
        
        df_dist = pd.read_excel(excel_path, sheet_name="DistribucionTerritorial")
        df_dist.to_sql('distribucionterritorial', engine_oficial, if_exists='append', index=False)
        df_dist.to_sql('distribucionterritorial', engine_rapido, if_exists='append', index=False)
        print("✅ DistribucionTerritorial cargada")
        
        df_recintos = pd.read_excel(excel_path, sheet_name="RecintosElectorales")
        df_recintos.to_sql('recintoselectorales', engine_oficial, if_exists='append', index=False)
        df_recintos.to_sql('recintoselectorales', engine_rapido, if_exists='append', index=False)
        print("✅ RecintosElectorales cargados")
        
        df_actas = pd.read_excel(excel_path, sheet_name="ActasImpresas")
        df_actas.to_sql('actasimpresas', engine_oficial, if_exists='append', index=False)
        df_actas.to_sql('actasimpresas', engine_rapido, if_exists='append', index=False)
        print(f"✅ ActasImpresas cargadas: {len(df_actas)} actas procesadas.")
        
        df_trans = pd.read_excel(excel_path, sheet_name="Transcripciones")
        df_trans.to_sql('transcripciones', engine_oficial, if_exists='append', index=False)
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
                    
                    cursor.execute(
                        "INSERT INTO Transcripciones (codigo_acta, candidato, votos) VALUES (%s, %s, %s)",
                        (codigo_acta, 'Total_Validos', suma)
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

if __name__ == "__main__":
    load_excel_data()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    ingest_dir = os.path.join(base_dir, "ingest", "pdf_actas")
    
    for i in range(multiprocessing.cpu_count()):
        p = multiprocessing.Process(target=bot_worker, args=(i, ingest_dir))
        p.start()
