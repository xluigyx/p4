import os
import pymongo

def patch_stark():
    db_url = os.environ.get("DB_OFICIAL", "mongodb://db_oficial:27017/oficial_db")
    client = pymongo.MongoClient(db_url)
    db = client.get_database()
    
    # Corregir cualquier valor negativo que haya entrado antes del filtro
    result = db["actas_oficiales"].update_many(
        {"votos.stark": {"$lt": 0}},
        {"$set": {"votos.stark": 0, "status": "NORMALIZADO", "reason": "P4 corregido por parche"}}
    )
    print(f"✅ Parche aplicado: {result.modified_count} registros Stark normalizados.")

if __name__ == "__main__":
    patch_stark()
