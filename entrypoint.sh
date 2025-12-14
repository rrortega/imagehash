#!/bin/bash
# entrypoint.sh

# Ejecuta el servidor Uvicorn.
# --host 0.0.0.0 es necesario para que el servicio sea accesible fuera del contenedor.
# --port 80 es el puerto estándar que expondremos.
# main:app indica que debe usar la instancia 'app' del módulo 'main'.
exec uvicorn main:app --host 0.0.0.0 --port 80