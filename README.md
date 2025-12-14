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
git clone [https://github.com/tu-usuario/phash-image-processor.git](https://github.com/tu-usuario/phash-image-processor.git)
cd phash-image-processor