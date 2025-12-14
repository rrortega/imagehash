import requests
import imagehash
from PIL import Image
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from io import BytesIO
from typing import Tuple

# ----------------------------------------------------
# Pydantic Models
# ----------------------------------------------------
class ImageURL(BaseModel):
    """Modelo para el payload JSON de entrada para una sola URL."""
    url: str

class ImageComparisonPayload(BaseModel):
    """Nuevo modelo para el payload JSON de entrada para dos URLs."""
    url_a: str
    url_b: str

# ----------------------------------------------------
# Inicialización de FastAPI
# ----------------------------------------------------
app = FastAPI(title="pHash Image Processor", version="2.0.0 - Optimized")

# ----------------------------------------------------
# Función de Ayuda Optimizado: Descargar y Calcular pHash SIN DISCO
# ----------------------------------------------------
async def calculate_phash_from_url_optimized(image_url: str) -> str:
    """
    Descarga una imagen y calcula su pHash, manejando todo en memoria (BytesIO).
    Devuelve solo el pHash como string. Lanza HTTPException en caso de error.
    """
    print(f"-> Descargando imagen: {image_url}")
    try:
        # 1. Descargar la imagen
        response = requests.get(image_url)
        response.raise_for_status()  # Lanza excepción para códigos 4xx/5xx

        # 2. Manejar en memoria con BytesIO (EVITA I/O DE DISCO)
        image_data = BytesIO(response.content)
        
        # 3. Abrir y calcular el pHash
        img = Image.open(image_data)
        phash_value = str(imagehash.phash(img))
        
        return phash_value

    except requests.exceptions.RequestException as e:
        # Errores de red, URL no válida, o HTTP (404, 500, etc.)
        raise HTTPException(
            status_code=400, 
            detail=f"Error al descargar la imagen de la URL proporcionada ({image_url}): {e}"
        )
    except Exception as e:
        # Otros errores (ej. el archivo no es una imagen válida)
        raise HTTPException(
            status_code=500, 
            detail=f"Error interno al procesar la imagen ({image_url}): {e}. Asegúrese de que el archivo es una imagen válida."
        )

# ----------------------------------------------------
# Endpoint Existente: Calcular un solo pHash
# ----------------------------------------------------
@app.post("/process-image/")
async def calculate_phash(payload: ImageURL):
    """
    Descarga una imagen remota y calcula su pHash (Perceptual Hash) usando manejo de memoria.
    """
    phash_value = await calculate_phash_from_url_optimized(payload.url)
    
    # Nota: Ya no se requiere limpieza manual ya que no hay archivos temporales.
    
    return {"phash": phash_value, "url": payload.url}


# ----------------------------------------------------
# Endpoint Corregido y Optimizado: Comparar dos imágenes
# ----------------------------------------------------
@app.post("/compare-images/")
async def compare_images(payload: ImageComparisonPayload):
    """
    Descarga dos imágenes remotas, calcula sus pHashes y la Distancia de Hamming.
    """
    url_a = payload.url_a
    url_b = payload.url_b
    
    try:
        # 1. Calcular pHash A (Optimizado en memoria)
        phash_a_str = await calculate_phash_from_url_optimized(url_a)
        
        # 2. Calcular pHash B (Optimizado en memoria)
        phash_b_str = await calculate_phash_from_url_optimized(url_b)

        # Convertir los strings de hash a objetos Hash para la comparación
        phash_a = imagehash.hex_to_hash(phash_a_str)
        phash_b = imagehash.hex_to_hash(phash_b_str)

        # 3. Calcular la Distancia de Hamming (Resultado es numpy.int64)
        distance = phash_a - phash_b 

        # *** CORRECCIÓN CRÍTICA: Convertir a int nativo para JSON serialización ***
        distance_int = int(distance)
        
        # 4. Determinar si son similares (Umbral típico es <= 5)
        is_similar = distance_int <= 5

        print(f"-> Distancia de Hamming calculada: {distance_int}. Similares: {is_similar}")

        return {
            "url_a": url_a,
            "url_b": url_b,
            "phash_a": phash_a_str,
            "phash_b": phash_b_str,
            "hamming_distance": distance_int,
            "is_similar": is_similar,
            "note": "Una distancia de Hamming cercana a 0 (≤5) indica alta similitud."
        }
        
    except HTTPException as e:
        # Re-lanzar la excepción HTTP generada por calculate_phash_from_url_optimized
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error inesperado al comparar imágenes: {e}"
        )


# ----------------------------------------------------
# Endpoint de prueba
# ----------------------------------------------------
@app.get("/")
def health_check():
    return {"status": "ok", "service": "pHash Calculator API"}