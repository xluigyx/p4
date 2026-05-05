import multiprocessing
import os
import time
import pandas as pd
from sqlalchemy import create_engine
from ocr_engine import ElectoralOCR

def load_excel_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    excel_path = os.path.join(base_dir, "data", "ingest", "_Recursos Practica 4.xlsx")
    
    if not os.path.exists(excel_path):
        print(f"⚠️ No se encontró el Excel en {excel_path}")
        return

    # Usar variables de entorno de docker-compose
    db_url = os.environ.get("DB_OFICIAL", "postgresql://postgres:bolivia_vota@localhost:5433/oficial_db")
    engine = create_engine(db_url)
    
    try:
        print("📊 Cargando datos del Excel a la BD Oficial...")
        
        # 1. Distribución
        df_dist = pd.read_excel(excel_path, sheet_name="Distribucion")
        df_dist.to_sql('distribucion', engine, if_exists='replace', index=False)
        print("✅ Distribución cargada")
        
        # 2. Recintos
        df_recintos = pd.read_excel(excel_path, sheet_name="Recintos")
        # Rename columns to match init.sql if needed, or replace table
        df_recintos.to_sql('recintos', engine, if_exists='replace', index=False)
        print("✅ Recintos cargados")
        
        # 3. Actas Impresas
        df_actas = pd.read_excel(excel_path, sheet_name="Actas Impresas")
        df_actas.to_sql('actas_impresas', engine, if_exists='replace', index=False)
        print("✅ Actas Impresas cargadas")
        
        # 4. Transcripciones (simulando ingesta rápida para el dashboard)
        # Opcionalmente se puede cargar en RRV aquí, o dejar que el OCR lo haga
        
        print("🎉 Carga inicial completada.")
    except Exception as e:
        print(f"❌ Error al cargar Excel: {e}")

def bot_worker(bot_id, folder_path):
    ocr = ElectoralOCR()
    print(f"🤖 Bot-{bot_id} activo. Vigilando ráfagas...")
    
    while True:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)
            
        archivos = [f for f in os.listdir(folder_path) if f.endswith(('.pdf', '.png', '.jpg'))]
        for archivo in archivos:
            full_path = os.path.join(folder_path, archivo)
            print(f"📸 Bot-{bot_id} procesando acta: {archivo}")
            
            # Ejecuta OCR y Validación OEP
            resultado = ocr.validar_acta(full_path)
            
            # Mover a procesados para liberar la carpeta
            base_dir = os.path.dirname(os.path.abspath(__file__))
            processed_dir = os.path.join(base_dir, "processed")
            os.makedirs(processed_dir, exist_ok=True)
            dest_path = os.path.join(processed_dir, archivo)
            try:
                os.rename(full_path, dest_path)
            except Exception as e:
                print(f"⚠️ No se pudo mover el archivo {archivo}: {e}")
            
            # LOGS PARA EL FRONTEND (Aquí enviarías al WebSocket)
            if resultado["status"] == "OBSERVADA":
                print(f"❌ ALERTA: {archivo} - {resultado['motivo']}")
        
        time.sleep(2)

if __name__ == "__main__":
    # 1. Cargar Excel inicial
    load_excel_data()

    # 2. Levanta bots
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ingest_dir = os.path.join(base_dir, "ingest", "pdf_actas")
    
    for i in range(multiprocessing.cpu_count()):
        p = multiprocessing.Process(target=bot_worker, args=(i, ingest_dir))
        p.start()
