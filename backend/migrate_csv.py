import os
import pandas as pd
import pymongo

def migrate_csv_to_mongo():
    print("🚀 Iniciando migración de CSV a MongoDB (Clúster Oficial)...")
    
    # Rutas
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # El archivo de la práctica
    csv_path = os.path.join(base_dir, "data", "ingest", "Recursos Practica 4 - Transcripciones.csv")
    
    if not os.path.exists(csv_path):
        # Fallback to the known excel file if CSV doesn't exist, just in case
        excel_path = os.path.join(base_dir, "data", "ingest", "_Recursos Practica 4.xlsx")
        if os.path.exists(excel_path):
            print(f"⚠️ No se encontró {csv_path}. Usando {excel_path} (Pestaña Transcripciones)...")
            df = pd.read_excel(excel_path, sheet_name="Transcripciones")
        else:
            print(f"❌ Error: No se encontró el archivo CSV en {csv_path}")
            return
    else:
        df = pd.read_csv(csv_path)

    # Conexión a MongoDB Oficial (Puerto 27017)
    db_url = os.environ.get("DB_OFICIAL", "mongodb://db_oficial:27017/oficial_db")
    
    try:
        client = pymongo.MongoClient(db_url)
        db_mongo = client.get_database()
        coleccion = db_mongo["actas_oficiales"]
        
        # Limpiar colección previa
        coleccion.delete_many({})
        print("🧹 Colección 'actas_oficiales' limpiada.")
        
        docs_to_insert = []
        for index, row in df.iterrows():
            # Validación: Valores negativos se normalizan a 0 (P4 detectado)
            # Adaptamos para soportar cabeceras tipo 'P1' o 'lannister'
            lannister_raw = int(row.get('lannister', row.get('P1', 0)))
            targaryen_raw = int(row.get('targaryen', row.get('P2', 0)))
            baratheon_raw = int(row.get('baratheon', row.get('P3', 0)))
            stark_raw = int(row.get('stark', row.get('P4', 0)))
            
            lannister = max(0, lannister_raw)
            targaryen = max(0, targaryen_raw)
            baratheon = max(0, baratheon_raw)
            stark = max(0, stark_raw)
            
            if stark_raw < 0:
                print(f"⚠️ [P4] Voto negativo detectado en Acta {row.get('codigo_acta', index)} para Stark ({stark_raw}). Normalizado a 0.")
                status = "OBSERVADO"
                reason = "Valor negativo en P4"
            else:
                status = "EXITO"
                reason = "-"
                
            # 3. Mapeo al Esquema Anidado Exigido
            doc = {
                "id_acta": str(row.get('id_acta', row.get('codigo_acta', str(index)))),
                "departamento": str(row.get('departamento', row.get('desc_dep', 'Desconocido'))),
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
            coleccion.insert_many(docs_to_insert)
            print(f"✅ Migración completada: {len(docs_to_insert)} actas insertadas en MongoDB.")
        else:
            print("⚠️ No hay datos para insertar.")
            
    except Exception as e:
        print(f"❌ Error conectando a MongoDB o procesando datos: {e}")

if __name__ == "__main__":
    migrate_csv_to_mongo()
