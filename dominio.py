"""Lógica de dominio: evaluación de riesgo de pólizas."""
import csv
from pathlib import Path

import config
from utilidades import con_registro

BASE = Path(__file__).parent


class EvaluadorRiesgo:
    """Evalúa el riesgo de una póliza y guarda lo que ha evaluado."""

    historial = []
    umbral = config.UMBRAL_ALTO_RIESGO

    def __init__(self, poliza):
        self.poliza = poliza

    @con_registro
    def puntuar(self, modelo, payload):
        rasgos = [[
            payload["monto"],
            payload["antiguedad"],
            payload["siniestros_previos"],
        ]]
        return float(modelo.predict_proba(rasgos)[0][1])

    def anotar(self, puntaje):
        self.historial.append({"poliza": self.poliza, "puntaje": puntaje})

    def es_alto_riesgo(self, puntaje):
        return puntaje is not None and puntaje > self.umbral


def cargar_siniestros():
    with open(BASE / config.RUTA_DATOS, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def buscar_siniestro(id_siniestro):
    for fila in cargar_siniestros():
        if fila["id"] == str(id_siniestro):
            return fila
    return None
