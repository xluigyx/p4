import multiprocessing
import os
import time
from ocr_engine import ElectoralOCR

def bot_worker(bot_id, folder_path):
    ocr = ElectoralOCR()
    print(f"🤖 Bot-{bot_id} activo. Vigilando ráfagas...")
    
    while True:
        archivos = [f for f in os.listdir(folder_path) if f.endswith(('.pdf', '.png', '.jpg'))]
        for archivo in archivos:
            full_path = os.path.join(folder_path, archivo)
            print(f"📸 Bot-{bot_id} procesando acta: {archivo}")
            
            # Ejecuta OCR y Validación OEP
            resultado = ocr.validar_acta(full_path)
            
            # Mover a procesados para liberar la carpeta
            base_dir = os.path.dirname(os.path.abspath(__file__))
            processed_dir = os.path.join(base_dir, "processed", archivo)
            os.rename(full_path, processed_dir)
            
            # LOGS PARA EL FRONTEND (Aquí enviarías al WebSocket)
            if resultado["status"] == "OBSERVADA":
                print(f"❌ ALERTA: {archivo} - {resultado['motivo']}")
        
        time.sleep(2)

if __name__ == "__main__":
    # Levanta bots según tus núcleos (puedes forzar 4 o 8)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ingest_dir = os.path.join(base_dir, "ingest", "pdf_actas")
    
    for i in range(multiprocessing.cpu_count()):
        p = multiprocessing.Process(target=bot_worker, args=(i, ingest_dir))
        p.start()
