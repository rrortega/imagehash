# Usa una imagen base ligera de Python
FROM python:3.11-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos de requerimientos y los instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de la aplicación, incluyendo el script de la API y el entrypoint
COPY main.py .
COPY entrypoint.sh .

# Otorga permisos de ejecución al script entrypoint
RUN chmod +x entrypoint.sh

# Define el comando que se ejecutará al iniciar el contenedor
ENTRYPOINT ["./entrypoint.sh"]