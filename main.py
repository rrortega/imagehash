import requests
import imagehash
from PIL import Image
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from io import BytesIO
import tempfile
import os

# ----------------------------------------------------
# Pydantic Model para la entrada del request
# ----------------------------------------------------
class ImageURL(BaseModel):
    """Modelo para el payload JSON de entrada."""
    url: str

# ----------------------------------------------------
# Inicialización de FastAPI
# ----------------------------------------------------
app = FastAPI(title="pHash Image Processor", version="1.0.0")


@app.post("/process-image/")
async def calculate_phash(payload: ImageURL):
    """
    Descarga una imagen remota, calcula su pHash (Perceptual Hash) 
    y devuelve el resultado.
    """
    image_url = payload.url
    temp_filepath = None # Inicializamos para el bloque 'finally'

    print(f"-> Solicitud recibida para URL: {image_url}")

    try:
        # 1. Descargar la imagen
        response = requests.get(image_url, stream=True)
        response.raise_for_status()  # Lanza excepción para códigos 4xx/5xx
        
        # Usar BytesIO para procesar la imagen sin guardarla en disco (más eficiente)
        # Aunque el requisito pide "eliminar el temporal", una solución más limpia
        # es usar BytesIO. Si estrictamente necesitas un archivo temporal:
        
        # Solución con archivo temporal (siguiendo el requisito)
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_filepath = temp_file.name
        for chunk in response.iter_content(chunk_size=8192):
            temp_file.write(chunk)
        temp_file.close()

        # 2. Abrir y calcular el pHash
        img = Image.open(temp_filepath)
        # Calculamos el pHash. El resultado se convierte automáticamente a string.
        phash_value = str(imagehash.phash(img))
        
        print(f"-> pHash calculado: {phash_value}")

        # 3. Devolver el pHash
        return {"phash": phash_value}

    except requests.exceptions.RequestException as e:
        # Errores de red, URL no válida, o HTTP (404, 500, etc.)
        raise HTTPException(
            status_code=400, 
            detail=f"Error al descargar la imagen de la URL proporcionada: {e}"
        )
    except Exception as e:
        # Otros errores (ej. el archivo no es una imagen válida)
        raise HTTPException(
            status_code=500, 
            detail=f"Error interno al procesar la imagen: {e}"
        )
    finally:
        # 4. Eliminar el archivo temporal
        if temp_filepath and os.path.exists(temp_filepath):
            os.remove(temp_filepath)
            print(f"-> Archivo temporal eliminado: {temp_filepath}")

# ----------------------------------------------------
# Endpoint de prueba para verificar que el servicio está activo
# ----------------------------------------------------
@app.get("/")
def health_check():
    return {"status": "ok", "service": "pHash Calculator API"}