class ElectoralOCR:
    def validar_acta(self, path):
        # Simulación de extracción (Aquí integrarías Tesseract/EasyOCR)
        # Datos extraídos del acta 9050305335016.pdf[cite: 1]
        data = {
            "p1": 140, "p2": 39, "p3": 124, "p4": 345, 
            "validos": 648, "estado_fisico": "bueno"
        }
        
        # 1. Validación Física
        if data["estado_fisico"] in ["roto", "manchado"]:
            return {"status": "OBSERVADA", "motivo": "Acta dañada físicamente"}
            
        # 2. Validación Aritmética Requerida[cite: 1, 2]
        suma = data["p1"] + data["p2"] + data["p3"] + data["p4"]
        if suma != data["validos"]:
            return {"status": "OBSERVADA", "motivo": f"Error de suma: {suma} != {data['validos']}"}
            
        return {"status": "VALIDADA", "data": data}
