import cv2
import pytesseract
import numpy as np
import logging

class ElectoralOCR:
    def __init__(self):
        self.logger = logging.getLogger("ElectoralOCR")
        # Coordenadas mockeadas para el acta boliviana
        self.coordenadas = {
            "p1": (100, 200, 50, 20),
            "p2": (100, 230, 50, 20),
            "p3": (100, 260, 50, 20),
            "p4": (100, 290, 50, 20),
            "blancos": (100, 320, 50, 20),
            "nulos": (100, 350, 50, 20),
            "validos": (100, 380, 50, 20)
        }

    def validar_acta(self, data):
        """
        Valida que la suma de los votos por partido (P1 a P4) sea igual a los votos válidos.
        """
        suma_partidos = data.get('p1', 0) + data.get('p2', 0) + data.get('p3', 0) + data.get('p4', 0)
        if suma_partidos != data.get('validos', 0):
            return "OBSERVADA", f"Discrepancia: Suma de partidos ({suma_partidos}) != Votos Válidos ({data.get('validos', 0)})"
        return "VALIDADA", "Suma correcta"

    def process_acta(self, image_path):
        """
        Simula la segmentación y extracción de OCR usando Tesseract.
        En producción: aplica Canny, findContours para aislar las tablas y extraer:
        - Código de mesa
        - Votos por candidato
        - Blancos / Nulos
        - Detección de firmas
        """
        try:
            # Leer imagen con OpenCV y usar coordenadas para extraer cada campo
            # img = cv2.imread(image_path)
            # for key, coord in self.coordenadas.items():
            #     x, y, w, h = coord
            #     roi = img[y:y+h, x:x+w]
            #     text = pytesseract.image_to_string(roi)
            
            # Simulación de datos extraídos por el OCR para la prueba
            data = {
                "codigo_mesa": "9050305335016",
                "p1": 120,
                "p2": 80,
                "p3": 10,
                "p4": 5,
                "blancos": 5,
                "nulos": 20,
                "validos": 215,
                "papeletas_anfora": 240,
                "firmas_detectadas": True,
                "is_damaged": False
            }
            
            # Validación
            estado, mensaje_error = self.validar_acta(data)
            data["estado_validacion"] = estado
            data["mensaje_error"] = mensaje_error
            
            return data
        except Exception as e:
            self.logger.error(f"Error en OCR: {str(e)}")
            return None
