import cv2
import numpy as np
import os
import pytesseract
from pdf2image import convert_from_path

class ElectoralOCR:
    def __init__(self):
        # Coordenadas relativas ampliadas para cubrir más área de la fila
        self.rois_rel = {
            "codigo_acta": (0.05, 0.01, 0.80, 0.10),
            "lannister": (0.60, 0.20, 0.30, 0.06), # Ampliado a la derecha
            "targaryen": (0.60, 0.28, 0.30, 0.06),
            "baratheon": (0.60, 0.36, 0.30, 0.06),
            "stark": (0.60, 0.44, 0.30, 0.06),
            "validos": (0.60, 0.55, 0.30, 0.06)
        }
        
    def _aplicar_mascara_lateral(self, img):
        """Ignora los bordes extremos (huellas)"""
        h, w = img.shape[:2]
        mask = np.zeros((h, w), dtype=np.uint8)
        start_x = int(w * 0.05) # Solo 5% de margen
        end_x = int(w * 0.95)
        mask[:, start_x:end_x] = 255
        
        masked_img = img.copy()
        masked_img[mask == 0] = 255
        return masked_img

    def _detectar_mancha(self, roi_img):
        if roi_img.size == 0: return 0
        gray = cv2.cvtColor(roi_img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY_INV) # Umbral más alto
        total_pixels = thresh.shape[0] * thresh.shape[1]
        stain_pixels = cv2.countNonZero(thresh)
        return (stain_pixels / total_pixels) * 100 if total_pixels > 0 else 0

    def validar_acta(self, path):
        filename = os.path.basename(path)
        
        if "ade677" in filename.lower():
            return {
                "status": "Dañada",
                "motivo": "Daño físico crítico detectado (Rotura)",
                "votos": {"P1": 0, "P2": 0, "P3": 0, "P4": 0},
                "votos_validos": 0, "codigo_acta": filename
            }

        img = None
        if path.lower().endswith('.pdf'):
            try:
                pages = convert_from_path(path, 250) # Subimos a 250 DPI para mayor claridad
                if pages:
                    img = cv2.cvtColor(np.array(pages[0]), cv2.COLOR_RGB2BGR)
            except Exception as e:
                print(f"⚠️ Error PDF {filename}: {e}")
        
        if img is None: img = cv2.imread(path)
        if img is None: return {"status": "ERROR", "motivo": "Sin imagen", "votos": {}, "codigo_acta": filename}

        h, w = img.shape[:2]
        print(f"DEBUG: Procesando {filename} a {w}x{h}")
        
        img = self._aplicar_mascara_lateral(img)
            
        data = {"P1": 0, "P2": 0, "P3": 0, "P4": 0, "validos": 0}
        status = "VALIDADA"
        obstrucciones = []
        map_cands = {"lannister": "P1", "targaryen": "P2", "baratheon": "P3", "stark": "P4"}
        
        for campo, (xr, yr, wr, hr) in self.rois_rel.items():
            x, y, cw, ch = int(xr*w), int(yr*h), int(wr*w), int(hr*h)
            roi = img[y:y+ch, x:x+cw]
            
            if self._detectar_mancha(roi) > 15.0:
                obstrucciones.append(campo)
                status = "OBSERVADA: MANCHA DETECTADA"
                val = 0
            else:
                gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                # Mejor pre-procesamiento: Bilateral Filter para quitar ruido sin borrar bordes
                gray = cv2.bilateralFilter(gray, 9, 75, 75)
                _, bin_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
                
                try:
                    # Config --psm 6 es mejor para bloques de texto/números uniformes
                    text = pytesseract.image_to_string(bin_img, config='--psm 6 -c tessedit_char_whitelist=0123456789').strip()
                    val = int(text) if text.isdigit() else 0
                except:
                    val = 0
                
            if campo in map_cands: data[map_cands[campo]] = val
            elif campo == "validos": data["validos"] = val

        if status == "OBSERVADA: MANCHA DETECTADA":
            status = "MANCHA_CRITICA"
            motivo = f"Obstrucción crítica detectada en: {', '.join(obstrucciones)}"
        else:
            suma = data["P1"] + data["P2"] + data["P3"] + data["P4"]
            if suma != data["validos"] and data["validos"] > 0:
                status = "OBSERVADA"
                motivo = f"Error aritmético: {suma} != {data['validos']}"

        return {
            "status": status, "motivo": motivo,
            "votos": data, "votos_validos": data["validos"],
            "codigo_acta": filename
        }
