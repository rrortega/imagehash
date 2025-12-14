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
    """Modelo para el payload JSON de entrada para dos URLs (comparación entre URLs)."""
    url_a: str
    url_b: str
    
class ImageHashComparisonPayload(BaseModel):
    """Modelo para el payload JSON de entrada: 1 URL y 1 pHash string (comparación contra hash fijo)."""
    url: str
    phash_target: str

# ----------------------------------------------------
# Inicialización de FastAPI
# ----------------------------------------------------
app = FastAPI(title="pHash Image Processor", version="2.0.0 - Optimized")

# ----------------------------------------------------
# Función de Ayuda Optimizado: Descargar y Calcular pHash SIN DISCO
# ----------------------------------------------------
async def calculate_phash_from_url_optimized(image_url: str) -> str:
    """
    Descarga una imagen, calcula su pHash, manejando todo en memoria (BytesIO).
    Devuelve solo el pHash como string. Lanza HTTPException en caso de error.
    """
    print(f"-> Descargando imagen: {image_url}")
    try:
        # 1. Descargar la imagen
        # Nota: requests.get puede ser bloqueante. En producción, considera usar httpx
        # si se esperan muchas peticiones concurrentes y no quieres usar threads.
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
# Endpoint 1: Calcular un solo pHash
# ----------------------------------------------------
@app.post("/process-image/")
async def calculate_phash(payload: ImageURL):
    """
    Descarga una imagen remota y calcula su pHash.
    """
    phash_value = await calculate_phash_from_url_optimized(payload.url)
    
    return {"phash": phash_value }

# ----------------------------------------------------
# Endpoint 2: Comparar URL contra pHash Objetivo
# ----------------------------------------------------
@app.post("/compare-hash/")
async def compare_hash(payload: ImageHashComparisonPayload):
    """
    Descarga una imagen (URL), calcula su pHash y lo compara con un pHash objetivo.
    """
    url = payload.url
    phash_target_str = payload.phash_target
    
    try:
        # 1. Calcular pHash de la nueva imagen (Optimizado en memoria)
        phash_new_str = await calculate_phash_from_url_optimized(url)
        
        # 2. Convertir los strings de hash a objetos Hash para la comparación
        phash_new = imagehash.hex_to_hash(phash_new_str)
        
        try:
            # Intentar convertir el pHash objetivo.
            phash_target = imagehash.hex_to_hash(phash_target_str)
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail="El pHash objetivo ('phash_target') no es un valor hexadecimal válido."
            )

        # 3. Calcular la Distancia de Hamming
        distance = phash_new - phash_target 

        # Corregir error de serialización: Convertir a int nativo
        distance_int = int(distance)
        
        # 4. Determinar si son similares
        is_similar = distance_int <= 5

        print(f"-> pHash Nuevo: {phash_new_str} | pHash Objetivo: {phash_target_str}")
        print(f"-> Distancia de Hamming calculada: {distance_int}. Similares: {is_similar}")

        return { 
            "phash_calculated": phash_new_str,
            "phash_target": phash_target_str,
            "hamming_distance": distance_int,
            "is_similar": is_similar,
            "note": "Una distancia de Hamming cercana a 0 (≤5) indica alta similitud."
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error inesperado al comparar el hash: {e}"
        )


# ----------------------------------------------------
# Endpoint 3: Comparar dos URLs de Imágenes
# ----------------------------------------------------
@app.post("/compare-images/")
async def compare_images(payload: ImageComparisonPayload):
    """
    Descarga dos imágenes remotas, calcula sus pHashes y la Distancia de Hamming.
    """
    url_a = payload.url_a
    url_b = payload.url_b
    
    try:
        # 1. Calcular pHash A
        phash_a_str = await calculate_phash_from_url_optimized(url_a)
        
        # 2. Calcular pHash B
        phash_b_str = await calculate_phash_from_url_optimized(url_b)

        # Convertir los strings de hash a objetos Hash
        phash_a = imagehash.hex_to_hash(phash_a_str)
        phash_b = imagehash.hex_to_hash(phash_b_str)

        # 3. Calcular la Distancia de Hamming
        distance = phash_a - phash_b 

        # Corregir error de serialización: Convertir a int nativo
        distance_int = int(distance)
        
        # 4. Determinar si son similares
        is_similar = distance_int <= 5

        print(f"-> Distancia de Hamming calculada: {distance_int}. Similares: {is_similar}")

        return { 
            "phash_a": phash_a_str,
            "phash_b": phash_b_str,
            "hamming_distance": distance_int,
            "is_similar": is_similar,
            "note": "Una distancia de Hamming cercana a 0 (≤5) indica alta similitud."
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error inesperado al comparar imágenes: {e}"
        )


# ----------------------------------------------------
# Endpoint de prueba (Health Check)
# ----------------------------------------------------
@app.get("/")
def health_check():
    return {"status": "ok", "service": "pHash Calculator API"}