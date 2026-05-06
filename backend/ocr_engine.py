import cv2
import numpy as np
import os
import pytesseract

class ElectoralOCR:
    def __init__(self):
        # 1. Segmentación de Áreas (Obviar Firmas y Huellas)
        # Definimos las regiones de interés (x, y, w, h) basadas en el formato OEP
        # Estas ROIs evitan tocar el footer donde van firmas y huellas
        self.rois = {
            "codigo_acta": (100, 50, 400, 50),
            "lannister": (300, 200, 100, 40),
            "targaryen": (300, 250, 100, 40),
            "baratheon": (300, 300, 100, 40),
            "stark": (300, 350, 100, 40),
            "validos": (300, 400, 100, 40),
            "blancos": (300, 450, 100, 40),
            "nulos": (300, 500, 100, 40)
        }
        
    def _detectar_mancha(self, roi_img):
        # Convertir a escala de grises y buscar regiones oscuras persistentes
        gray = cv2.cvtColor(roi_img, cv2.COLOR_BGR2GRAY)
        
        # Umbralización para detectar ruido u obstrucciones oscuras (ej. tinta, café)
        _, thresh = cv2.threshold(gray, 90, 255, cv2.THRESH_BINARY_INV)
        
        # Calcular porcentaje del área cubierta por ruido oscuro
        total_pixels = thresh.shape[0] * thresh.shape[1]
        stain_pixels = cv2.countNonZero(thresh)
        
        if total_pixels == 0: return 0
        porcentaje = (stain_pixels / total_pixels) * 100
        return porcentaje

    def validar_acta(self, path):
        filename = os.path.basename(path)
        
        # Leemos la imagen real con OpenCV
        img = cv2.imread(path)
        if img is None:
            # Fallback en caso de que la ruta falle o se pasen PDFs sin rasterizar aún
            img = np.ones((800, 600, 3), dtype=np.uint8) * 255
            
        data = {"P1": 0, "P2": 0, "P3": 0, "P4": 0, "validos": 0}
        status = "VALIDADA"
        motivo = "-"
        
        obstrucciones = []
        map_cands = {"lannister": "P1", "targaryen": "P2", "baratheon": "P3", "stark": "P4"}
        
        # 2. Detector de Manchas y Extracción OCR
        for campo, (x, y, w, h) in self.rois.items():
            # Extraer ROI asegurando límites
            roi = img[max(0, y):min(img.shape[0], y+h), max(0, x):min(img.shape[1], x+w)]
            
            # Calcular Heatmap de error / Porcentaje de Mancha
            porcentaje_mancha = self._detectar_mancha(roi)
            
            # Tolerancia: Si la mancha cubre más del 20%
            if porcentaje_mancha > 20.0:
                obstrucciones.append(f"{campo.upper()} [X:{x}, Y:{y}]")
                status = "MANCHA_CRITICA"
                val = 0
            else:
                # Pre-procesamiento de limpieza visual para Pytesseract
                gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (3, 3), 0)
                _, bin_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
                
                # Tesseract OCR (Solo dígitos numéricos)
                try:
                    text = pytesseract.image_to_string(bin_img, config='--psm 7 -c tessedit_char_whitelist=0123456789').strip()
                    val = int(text) if text.isdigit() else 0
                except Exception:
                    val = 0
                
            if campo in map_cands:
                data[map_cands[campo]] = val
            elif campo == "validos":
                data["validos"] = val

        # 3. Validación Aritmética con Tolerancia
        if status == "MANCHA_CRITICA":
            motivo = f"OBSERVADA: DATO ILEGIBLE. Obstrucción detectada en el área de {', '.join(obstrucciones)}"
            # Si hay mancha crítica que afecta la suma, devolvemos 0 en todo
            data = {"P1": 0, "P2": 0, "P3": 0, "P4": 0, "validos": 0}
        else:
            suma = data["P1"] + data["P2"] + data["P3"] + data["P4"]
            if suma != data["validos"]:
                status = "OBSERVADA"
                motivo = f"Error aritmético: {suma} != {data['validos']}"

        return {
            "status": status,
            "motivo": motivo,
            "votos": data,
            "votos_validos": data["validos"],
            "codigo_acta": filename
        }
