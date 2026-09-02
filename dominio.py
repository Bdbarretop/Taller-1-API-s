"""Lógica de dominio: evaluación de riesgo de pólizas.

Diseño (B4 · M3):
- `RepositorioHistorial` guarda las evaluaciones hechas por el servicio.
- `RepositorioSiniestros` accede al catálogo persistido en CSV.
- `EvaluadorRiesgo` puntúa una póliza usando el modelo inyectado y anota el
  resultado en el historial inyectado (o uno propio si no se inyecta).

El constructor del evaluador recibe solo la póliza (contrato del taller). Los
colaboradores son opcionales con default seguro; en producción se inyectan
desde el `lifespan` de FastAPI para que todas las peticiones compartan
historial y catálogo.
"""
import csv
from pathlib import Path

import config


class RepositorioHistorial:
    """Almacén en memoria de evaluaciones hechas por el servicio."""

    def __init__(self):
        self._registros: list[dict] = []

    def registrar(self, poliza: str, puntaje: float) -> None:
        self._registros.append({"poliza": poliza, "puntaje": puntaje})

    def todo(self) -> list[dict]:
        return list(self._registros)

    def __len__(self) -> int:
        return len(self._registros)

    def __iter__(self):
        return iter(self._registros)


class RepositorioSiniestros:
    """Acceso al catálogo de siniestros persistido en un archivo CSV."""

    def __init__(self, ruta_csv):
        self._ruta = Path(ruta_csv)

    def todos(self) -> list[dict]:
        with open(self._ruta, encoding="utf-8") as fh:
            return list(csv.DictReader(fh))

    def buscar(self, id_siniestro):
        for fila in self.todos():
            if fila["id"] == str(id_siniestro):
                return fila
        return None


class EvaluadorRiesgo:
    """Evalúa el riesgo de una póliza y anota el resultado en el historial."""

    def __init__(self, poliza, modelo=None, umbral=None, historial=None):
        self.poliza = poliza
        self.modelo = modelo
        self.umbral = umbral if umbral is not None else config.UMBRAL_ALTO_RIESGO
        self.historial = historial if historial is not None else RepositorioHistorial()

    def puntuar(self, payload):
        if self.modelo is None:
            raise RuntimeError("EvaluadorRiesgo construido sin modelo cargado")
        rasgos = [[
            payload["monto"],
            payload["antiguedad"],
            payload["siniestros_previos"],
        ]]
        return float(self.modelo.predict_proba(rasgos)[0][1])

    def anotar(self, puntaje):
        self.historial.registrar(self.poliza, puntaje)

    def es_alto_riesgo(self, puntaje):
        return puntaje is not None and puntaje > self.umbral
