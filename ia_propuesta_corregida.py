"""
Propuesta generada por un asistente de IA para riesgo-api-v0 — VERSIÓN CORREGIDA (Parte D).

Prompt original:
    «Escribe con Pydantic v2 los modelos de validación de una solicitud de
     puntuación de siniestros, y una función asíncrona que evalúe un lote de
     solicitudes concurrentemente. Aplica buenas prácticas.»

Correcciones aplicadas sobre `ia_propuesta.py`:
    1. `redondear_monto` ahora retorna el valor (antes devolvía None y anulaba el monto).
    2. `_puntuar` usa `await asyncio.sleep(...)` no bloqueante, de modo que `asyncio.gather`
       sí ejecuta el lote de forma concurrente (antes `time.sleep` congelaba el event loop).
    3. `_puntuar` y `evaluar_lote` honran el contrato de salida: devuelven `RespuestaPuntuacion`
       (con `alto_riesgo` calculado) en lugar de `float` crudo; el modelo definido ya no queda sin uso.
"""
import asyncio
from typing import Optional

from pydantic import BaseModel, Field, field_validator

# Umbral de política para marcar una póliza como de alto riesgo (parámetro de negocio).
UMBRAL_ALTO_RIESGO = 0.7


class SolicitudPuntuacion(BaseModel):
    """Datos de entrada para puntuar una póliza."""

    poliza: str = Field(min_length=8, max_length=20)
    correo_analista: str = Field(
        pattern=r"^[A-Za-z0-9_.+-]+@[A-Za-z0-9-]+\.[A-Za-z]{2,3}$"
    )
    monto: float = Field(gt=0)
    antiguedad: int = Field(ge=0, le=60)
    siniestros_previos: int = Field(ge=0)
    observaciones: Optional[str] = Field(default=None, max_length=200)

    @field_validator("monto")
    @classmethod
    def redondear_monto(cls, v: float) -> float:
        """Redondea el monto a dos decimales para evitar ruido de coma flotante."""
        return round(v, 2)  # CORRECCIÓN 1: se retorna el valor redondeado


class RespuestaPuntuacion(BaseModel):
    """Resultado de la evaluación."""

    poliza: str
    puntaje: float = Field(ge=0.0, le=1.0)
    alto_riesgo: bool


async def _puntuar(solicitud: SolicitudPuntuacion) -> RespuestaPuntuacion:
    """Consulta el servicio externo de scoring y devuelve la respuesta puntuada."""
    await asyncio.sleep(0.2)  # CORRECCIÓN 2: latencia no bloqueante (antes time.sleep)
    base = 0.18 * solicitud.siniestros_previos - 0.01 * solicitud.antiguedad
    puntaje = max(0.0, min(1.0, 0.4 + base))
    # CORRECCIÓN 3: se honra el contrato de salida envolviendo en RespuestaPuntuacion
    return RespuestaPuntuacion(
        poliza=solicitud.poliza,
        puntaje=puntaje,
        alto_riesgo=puntaje >= UMBRAL_ALTO_RIESGO,
    )


async def evaluar_lote(
    solicitudes: list[SolicitudPuntuacion],
) -> list[RespuestaPuntuacion]:
    """Evalúa un lote de solicitudes de forma concurrente."""
    return await asyncio.gather(*[_puntuar(s) for s in solicitudes])
