# Dictamen sobre `ia_propuesta.py` — Parte D

**Grupo:** <número> · **Integrantes:** Brayan David Barreto, Edwing Navarrete

> Tres defectos. Las cuatro secciones de cada uno son obligatorias y se parsean.
> El peso está en **«Cómo lo comprobamos»**: afirmar que algo está mal no vale;
> demostrarlo, sí.

## Defecto 1

- **Qué está mal:** El validador `redondear_monto` calcula `round(v, 2)` pero no lo retorna. En Pydantic v2 un validador de campo en modo *after* reemplaza el valor del campo por lo que retorna la función; al no retornar nada, el validador devuelve `None` y `monto` queda en `None` en toda instancia creada, pese a estar declarado `monto: float = Field(gt=0)`.
- **Por qué es un defecto** (módulo · sección): M4 · 6. Validadores de campo
- **Cómo lo comprobamos:**

```python
from ia_propuesta import SolicitudPuntuacion

s = SolicitudPuntuacion(
    poliza="POL-2026-0001",
    correo_analista="a@b.co",
    monto=100.5,
    antiguedad=3,
    siniestros_previos=1,
)
print("monto:", repr(s.monto))
```

```
monto: None
```

- **Corrección:** Retornar el valor redondeado (`return round(v, 2)`). Verificado en `ia_propuesta_corregida.py`: `monto=100.5` se conserva como `100.5` y `100.567` se redondea a `100.57`.

## Defecto 2

- **Qué está mal:** `_puntuar` es `async def` pero simula la latencia del servicio con `time.sleep(0.2)`, que es una llamada bloqueante. Dentro de una corrutina bloquea el event loop, así que `asyncio.gather` en `evaluar_lote` no consigue concurrencia: el lote corre en serie, aunque el docstring promete evaluarlo "de forma concurrente".
- **Por qué es un defecto** (módulo · sección): M5 · 6. Síncrono frente a asíncrono
- **Cómo lo comprobamos:**

```python
import asyncio, time
from ia_propuesta import SolicitudPuntuacion, evaluar_lote

solicitudes = [
    SolicitudPuntuacion(
        poliza=f"POL-2026-{i:04d}",
        correo_analista="a@b.co",
        monto=100.0,
        antiguedad=1,
        siniestros_previos=0,
    )
    for i in range(10)
]

t0 = time.time()
asyncio.run(evaluar_lote(solicitudes))
print(f"10 solicitudes: {time.time() - t0:.2f} s")
```

```
10 solicitudes: 2.00 s
```

Diez llamadas de 0.2 s tardan 2.00 s (10 × 0.2 s), la firma de la ejecución secuencial; con concurrencia real el lote completo tardaría ~0.2 s.

- **Corrección:** Sustituir la llamada bloqueante por la primitiva no bloqueante `await asyncio.sleep(0.2)`, conservando `asyncio.gather` (el defecto es la operación bloqueante, no `gather`). Verificado en `ia_propuesta_corregida.py`: el mismo lote de 10 baja a 0.20 s.

## Defecto 3

- **Qué está mal:** `RespuestaPuntuacion` se define (con `puntaje` y `alto_riesgo`) pero nunca se usa. `_puntuar` retorna un `float` crudo y `evaluar_lote` un `list` de floats, de modo que el modelo de salida queda sin aplicar y `alto_riesgo` no se calcula nunca. La respuesta no honra el contrato de salida que el propio archivo declaró (el prompt pedía los modelos de validación y una función que evaluara el lote).
- **Por qué es un defecto** (módulo · sección): M4 · 3. Profundizando en los modelos
- **Cómo lo comprobamos:**

```python
import asyncio
from ia_propuesta import RespuestaPuntuacion, SolicitudPuntuacion, evaluar_lote

sol = SolicitudPuntuacion(
    poliza="POL-2026-0001",
    correo_analista="a@b.co",
    monto=100.0,
    antiguedad=1,
    siniestros_previos=2,
)
res = asyncio.run(evaluar_lote([sol]))
print("devuelve:", res)
print("tipo:", type(res[0]).__name__)
print("es RespuestaPuntuacion:", isinstance(res[0], RespuestaPuntuacion))
```

```
devuelve: [0.75]
tipo: float
es RespuestaPuntuacion: False
```

- **Corrección:** `_puntuar` construye y retorna `RespuestaPuntuacion(poliza, puntaje, alto_riesgo=puntaje >= UMBRAL_ALTO_RIESGO)` y `evaluar_lote` se anota como `-> list[RespuestaPuntuacion]`. Verificado en `ia_propuesta_corregida.py`: la salida es `list[RespuestaPuntuacion]` con `alto_riesgo` calculado (2 siniestros previos → puntaje 0.75 → `alto_riesgo=True`).
