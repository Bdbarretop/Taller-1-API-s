"""Configuración del servicio.

Secretos y valores dependientes del entorno se leen de variables de entorno.
Para desarrollo local, copiar `.env.example` a `.env` y rellenar. `.env` está
ignorado por `.gitignore` y no se sube al repositorio (B1 · M1 · 5).

Uvicorn puede cargarlas automáticamente con `--env-file .env`.
"""
import os

API_KEY = os.environ.get("RIESGO_API_KEY", "")
CLAVE_FIRMA = os.environ.get("RIESGO_CLAVE_FIRMA", "")

UMBRAL_ALTO_RIESGO = float(os.environ.get("RIESGO_UMBRAL_ALTO", "0.7"))
RUTA_MODELO = "modelo.pkl"
RUTA_DATOS = "datos/siniestros.csv"
