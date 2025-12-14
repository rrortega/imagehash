# 🖼️ pHash Image Processor API

## Visión General

Este repositorio contiene una **API RESTful** ligera y eficiente construida con **FastAPI** para calcular el **Perceptual Hash (pHash)** de imágenes alojadas remotamente. El servicio está completamente dockerizado para facilitar el despliegue y la escalabilidad.

### 💡 ¿Qué es el pHash?

El pHash es una técnica de *hashing* de imágenes que permite la identificación de imágenes duplicadas o visualmente similares, incluso si han sido redimensionadas, recortadas o ligeramente modificadas.

## 🚀 Características Principales

* **FastAPI:** Servidor Python de alto rendimiento y fácil de usar.
* **Dockerizado:** Despliegue simple y consistente en cualquier entorno.
* **Procesamiento de Imágenes:** Utiliza **Pillow** y **imagehash** para el cálculo robusto.
* **Clean-up Automático:** Descarga la imagen, calcula el hash, y elimina el archivo temporal inmediatamente.

## 📦 Tecnologías

| Componente | Tecnología | Uso |
| :--- | :--- | :--- |
| **Framework Web** | `FastAPI` | Manejo de rutas y *payloads* JSON. |
| **Servidor ASGI** | `Uvicorn` | Servidor ultrarrápido para la API. |
| **Imágenes** | `Pillow` y `imagehash` | Descarga, apertura y cálculo del pHash. |
| **Contenedor** | `Docker` | Empaquetado y orquestación del servicio. |

## 🛠️ Despliegue y Uso Local

### Requisitos

Necesitas tener instalado:
* [**Docker**](https://www.docker.com/get-started)
* [**Docker Compose**](https://docs.docker.com/compose/install/) (opcional, pero recomendado)

### 1. Clonar el Repositorio

```bash
git clone https://github.com/rrortega/imagehash.git
cd phash-image-processor
```

### 2. Construir la Imagen de Docker
Utiliza el Dockerfile provisto para construir la imagen.
```bash
docker build -t phash-service .
```

### 3. Ejecutar el Contenedor
Ejecuta la imagen, mapeando el puerto interno 80 al puerto 8000 de tu máquina local.
```bash
docker run -d --name phash-app -p 8000:80 phash-service
```

## ⚙️ Uso de la API
El servicio expone dos endpoints principales vía HTTP POST.

### Endpoint: /phash/
Calcula el pHash de una imagen remota y devuelve el valor.
| Método | Ruta |Descripción |
| :--- | :---: | ---: |
| POST | /phash/ |Procesa la URL de una imagen y devuelve su pHash. |
 
 ### Solicitud (Payload JSON)
 Debes enviar una URL de imagen válida en el cuerpo de la solicitud:
 ```json
 {
  "url": "https://images.unsplash.com/photo-1555066931-4365d14bab8c" 
}
 ```  

### Ejemplo con curl: Sustituir la URL por una imagen real 

```bash
curl -X POST "http://localhost:8000/phash/" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://images.unsplash.com/photo-1555066931-4365d14bab8c"}'
``` 
### Respuesta Exitosa (200 OK)
La respuesta JSON incluirá el pHash calculado como una cadena hexadecimal.
```bash
{
  "phash": "f006797960714c11" 
}
```

### Respuestas de Error

|Código	| Detalle |	Posible Causa |
| :--- | :---: | ---: |
|400 Bad Request|	Error al descargar la imagen...|	La URL no es válida, la imagen no existe (404), o error de red.|
|500 Internal Server Error	| Error interno al procesar...	|El archivo descargado no es una imagen válida o la librería falló al procesar.|

## Endpoint /compare/images/  
| Método | Ruta |	Descripción|
| :--- | :---: | ---: | 
| POST	| /compare-images/	| Comparar dos Imágenes (Distancia de Hamming).|


| Parámetro  | Tipo | Descripción | 
| :--- | :---: | ---: |
| url_a | string | URL de la primera  |
| url_b | string | URL de la segunda imagen.|

### Ejemplo con curl
``` bash
# Se recomienda usar dos imágenes que sean idénticas o muy similares para probar la distancia baja.
curl -X POST "http://localhost:8000/compare/images/" \
     -H "Content-Type: application/json" \
     -d '{
           "url_a": "https://url-imagen-1/original.jpg",
           "url_b": "https://url-imagen-2/modificada.jpg"
         }'
```

### Respuesta
```json
{ 
  "phash_a": "f006797960714c11",
  "phash_b": "f006797960714c15",
  "hamming_distance": 4,
  "is_similar": true,
  "note": "Una distancia de Hamming de 0 a 5 generalmente indica alta similitud visual."
}
```

## Endpoint /compare/phash-vs-image/
Descarga y procesa una imagen para compararla con un pHash conocido. Este es el método más rápido si ya tienes una base de datos de pHashes.
|Parámetro	| Tipo |	Descripción |
| :--- | :---: | ---: | 
|url|	string	 | URL de la imagen a verificar.|
|phash|	string	|pHash hexadecimal (16 caracteres) de la imagen de referencia.|

### Ejemplo con curl
```bash 
curl -X POST "http://localhost:8000/phash-vs-image/" \
     -H "Content-Type: application/json" \
     -d '{
           "url": "https://url-imagen-1/new.jpg",
           "phash": "f006797960714c11"
         }'
```
### Respuesta Exitosa (200 OK)
```json
{ 
  "phash_calculated": "f006797960714c15",
  "phash_target": "f006797960714c11",
  "hamming_distance": 4,
  "is_similar": true,
  "note": "Una distancia de Hamming cercana a 0 (≤5) indica alta similitud."
}
```

# 📁 Estructura del Proyecto
```bash 
imagehash/
  ├── Dockerfile             # Define la imagen de Docker (Python, dependencias)
  ├── entrypoint.sh          # Script de inicio que ejecuta Uvicorn   
  ├── requirements.txt       # Lista las dependencias de Python (FastAPI, imagehash, etc.)
  └── main.py                # Lógica principal de la API con FastAPI y el cálculo del pHash
```

# 📝 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo LICENSE para más detalles.

# 🧑‍💻 Contribuciones
Las contribuciones son bienvenidas. Si tienes sugerencias o reportes de errores, por favor, abre un issue o envía un Pull Request.