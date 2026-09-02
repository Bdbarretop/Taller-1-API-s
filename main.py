"""
riesgo-api-v0 — Servicio de puntuación de siniestros.
Aseguradora Santo Tomás · prototipo interno.
"""
import asyncio
import multiprocessing
import pickle
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

import config
from dominio import EvaluadorRiesgo, RepositorioHistorial, RepositorioSiniestros

BASE = Path(__file__).parent

# Cargamos el modelo al importar (arranque del servicio), no dentro del handler.
# Patrón enseñado en M5 · 3 «El servidor web y WSGI». Cubre restricción B6.
with open(BASE / config.RUTA_MODELO, "rb") as fh:
    MODELO = pickle.load(fh)

HISTORIAL = RepositorioHistorial()
SINIESTROS = RepositorioSiniestros(BASE / config.RUTA_DATOS)


def _calculo_pesado_cpu() -> float:
    """Cómputo CPU-bound aislado; vive a nivel de módulo para que
    ProcessPoolExecutor pueda serializarla (Windows usa spawn)."""
    total = 0.0
    for i in range(3_000_000):
        total += (i % 7) ** 0.5
    return round(total, 2)


# ProcessPoolExecutor para tareas CPU-bound (M5 · 6.4.5 «Advertencia: async
# no es magia para todo»). Se crea solo en el proceso principal; los hijos
# spawneados re-importan este módulo y saltan la creación para evitar
# recursión.
CPU_EXECUTOR: ProcessPoolExecutor | None = None
if multiprocessing.current_process().name == "MainProcess":
    CPU_EXECUTOR = ProcessPoolExecutor(max_workers=4)

app = FastAPI(title="Riesgo API", version="0.1.0")


# --- Modelos de request/response (M4 · Pydantic, cubre B5) ----------------

class SolicitudScore(BaseModel):
    """Datos que llegan al endpoint /score."""

    poliza: str = Field(min_length=1, max_length=32)
    monto: float = Field(gt=0)
    antiguedad: int = Field(ge=0, le=60)
    siniestros_previos: int = Field(ge=0)

    @field_validator("poliza")
    @classmethod
    def poliza_no_vacia(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("la póliza no puede ser solo espacios")
        return v


class RespuestaScore(BaseModel):
    """Salida del endpoint /score. Validada también en la salida."""

    poliza: str
    puntaje: float = Field(ge=0.0, le=1.0)
    alto_riesgo: bool


# --- Endpoints de negocio -------------------------------------------------

@app.post("/score", response_model=RespuestaScore)
async def score(payload: SolicitudScore) -> RespuestaScore:
    evaluador = EvaluadorRiesgo(payload.poliza, modelo=MODELO, historial=HISTORIAL)
    puntaje = evaluador.puntuar(payload.model_dump())
    evaluador.anotar(puntaje)
    return RespuestaScore(
        poliza=payload.poliza,
        puntaje=puntaje,
        alto_riesgo=evaluador.es_alto_riesgo(puntaje),
    )


@app.get("/historial")
async def historial():
    return {"evaluaciones": HISTORIAL.todo()}


@app.get("/siniestros/{id_siniestro}")
async def siniestro(id_siniestro: int):
    fila = SINIESTROS.buscar(id_siniestro)
    if fila is None:
        raise HTTPException(status_code=404, detail=f"no existe el siniestro {id_siniestro}")
    return fila


@app.get("/exportar")
async def exportar():
    return {"siniestros": SINIESTROS.todos()}


@app.get("/health")
def health():
    """Sonda de vida (liveness). Responde 200 sin consultar dependencias."""
    return {"status": "ok"}


# --- Endpoints de perfil de carga -----------------------------------------

@app.get("/ping")
async def ping():
    return {"pong": True}


@app.get("/consulta-archivo")
def consulta_archivo():
    # IO-bound con archivo pequeño (~50 KB). `def` deja que FastAPI lo ejecute
    # en el thread pool sin bloquear el event loop (M5 · 6).
    contenido = (BASE / config.RUTA_DATOS).read_text(encoding="utf-8")
    return {"lineas": len(contenido.splitlines())}


@app.get("/servicio-externo")
async def servicio_externo():
    # IO-bound de red. `await asyncio.sleep` cede control al event loop;
    # 20 corrutinas concurrentes esperan sus 0.3 s en paralelo (M5 · 6).
    await asyncio.sleep(0.3)
    return {"tarifa_referencia": 1.18}


@app.get("/calculo-pesado")
async def calculo_pesado():
    # CPU-bound. Se delega al ProcessPoolExecutor: proceso separado, fuera
    # del GIL, paralelismo real (M5 · 6.4.5 «async no es magia para todo»).
    loop = asyncio.get_running_loop()
    total = await loop.run_in_executor(CPU_EXECUTOR, _calculo_pesado_cpu)
    return {"total": total}
