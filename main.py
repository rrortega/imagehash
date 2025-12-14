import requests
import imagehash
from PIL import Image
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import tempfile
import os
from typing import Tuple # Necesario para la pista de tipo de la función de ayuda

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
app = FastAPI(title="pHash Image Processor", version="1.0.0")

# ----------------------------------------------------
# Función de Ayuda para Descargar y Calcular pHash
# ----------------------------------------------------
async def calculate_phash_from_url(image_url: str) -> Tuple[str, str]:
    """
    Descarga una imagen, calcula su pHash, y devuelve el pHash y la ruta temporal.
    Lanza HTTPException en caso de error.
    """
    temp_filepath = None
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()

        # Usar archivo temporal
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_filepath = temp_file.name
        for chunk in response.iter_content(chunk_size=8192):
            temp_file.write(chunk)
        temp_file.close()

        img = Image.open(temp_filepath)
        phash_value = str(imagehash.phash(img))
        
        return phash_value, temp_filepath

    except requests.exceptions.RequestException as e:
        if temp_filepath and os.path.exists(temp_filepath):
            os.remove(temp_filepath)
        raise HTTPException(
            status_code=400, 
            detail=f"Error al descargar la imagen de la URL ({image_url}): {e}"
        )
    except Exception as e:
        if temp_filepath and os.path.exists(temp_filepath):
            os.remove(temp_filepath)
        raise HTTPException(
            status_code=500, 
            detail=f"Error al procesar la imagen ({image_url}): {e}"
        )

# ----------------------------------------------------
# Endpoint Existente: Calcular un solo pHash
# ----------------------------------------------------
@app.post("/process-image/")
async def calculate_phash(payload: ImageURL):
    """
    Descarga una imagen remota y calcula su pHash (Perceptual Hash).
    """
    phash_value, temp_filepath = None, None
    try:
        phash_value, temp_filepath = await calculate_phash_from_url(payload.url)
        return {"phash": phash_value }
    finally:
        # Eliminar el archivo temporal
        if temp_filepath and os.path.exists(temp_filepath):
            os.remove(temp_filepath)
            print(f"-> Archivo temporal eliminado: {temp_filepath}")


# ----------------------------------------------------
# NUEVO Endpoint: Comparar dos imágenes
# ----------------------------------------------------
@app.post("/compare-images/")
async def compare_images(payload: ImageComparisonPayload):
    """
    Descarga dos imágenes remotas, calcula sus pHashes y la Distancia de Hamming.
    """
    url_a = payload.url_a
    url_b = payload.url_b
    
    # Variables para limpiar los archivos temporales en caso de éxito o fallo
    temp_path_a, temp_path_b = None, None
    
    try:
        # 1. Calcular pHash A
        print(f"-> Calculando pHash para A: {url_a}")
        phash_a_str, temp_path_a = await calculate_phash_from_url(url_a)
        
        # 2. Calcular pHash B
        print(f"-> Calculando pHash para B: {url_b}")
        phash_b_str, temp_path_b = await calculate_phash_from_url(url_b)

        # Convertir los strings de hash a objetos Hash para la comparación
        phash_a = imagehash.hex_to_hash(phash_a_str)
        phash_b = imagehash.hex_to_hash(phash_b_str)

        # 3. Calcular la Distancia de Hamming
        # La distancia es el número de bits diferentes. 0 significa idénticos.
        distance = phash_a - phash_b 

        # 4. Determinar si son similares (Umbral típico es < 5)
        # Esto es un ejemplo, el umbral real depende del caso de uso.
        is_similar = distance <= 5

        print(f"-> Distancia de Hamming calculada: {distance}. Similares: {is_similar}")

        return { 
            "phash_a": phash_a_str,
            "phash_b": phash_b_str,
            "hamming_distance": distance,
            "is_similar": is_similar,
            "note": "Una distancia de Hamming cercana a 0 indica alta similitud."
        }

    finally:
        # 5. Limpieza de archivos temporales (Asegurar que se ejecute siempre)
        if temp_path_a and os.path.exists(temp_path_a):
            os.remove(temp_path_a)
            print(f"-> Archivo temporal A eliminado: {temp_path_a}")
            
        if temp_path_b and os.path.exists(temp_path_b):
            os.remove(temp_path_b)
            print(f"-> Archivo temporal B eliminado: {temp_path_b}")

# ----------------------------------------------------
# Endpoint de prueba
# ----------------------------------------------------
@app.get("/")
def health_check():
    return {"status": "ok", "service": "pHash Calculator API"}