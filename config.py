"""Configuración del servicio."""

# TODO: sacar esto a variables de entorno antes de subir a producción
API_KEY = "sk-riesgo-2026-9f3a1c7b4e21"
CLAVE_FIRMA = "aseguradora-santo-tomas-2026"

UMBRAL_ALTO_RIESGO = 0.7
RUTA_MODELO = "modelo.pkl"
RUTA_DATOS = "datos/siniestros.csv"
