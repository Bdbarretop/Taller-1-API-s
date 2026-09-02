# riesgo-api-v0

Servicio de puntuación de siniestros de la Aseguradora Santo Tomás. Recibe los
datos de una póliza y devuelve la probabilidad de que el siniestro declarado
termine en un pago alto.

Este repositorio es la entrega del **Taller Corte I** del curso Python para
Desarrollo de APIs e IA (USTA 2026-II) sobre el semilla `riesgo-api-v0`.
Cumple las restricciones B1–B9 del taller; contrato de rutas y de dominio
intactos.

## Requisitos

- Python 3.11 o superior (probado en 3.13).
- `pip` reciente.

## Instalación

```bash
git clone https://github.com/Bdbarretop/Taller-1-API-s.git
cd Taller-1-API-s
python -m venv .venv
.venv\Scripts\activate            # Windows
# source .venv/bin/activate       # Linux/macOS
pip install -r requirements.txt
```

El modelo entrenado (`modelo.pkl`) y el dataset (`datos/siniestros.csv`) vienen
en el repositorio.

## Configuración

Las credenciales y umbrales dependientes de entorno se leen de variables de
entorno. Para desarrollo local, copiar la plantilla:

```bash
cp .env.example .env
# rellenar los valores en .env
```

Variables disponibles (todas opcionales, todas con default seguro):

| Variable | Default | Uso |
|---|---|---|
| `RIESGO_API_KEY` | `""` | Clave interna del servicio (reservada, no se usa aún en handlers). |
| `RIESGO_CLAVE_FIRMA` | `""` | Clave de firma. |
| `RIESGO_UMBRAL_ALTO` | `0.7` | Umbral para clasificar una póliza como alto riesgo. |

`.env` está en `.gitignore` y **no se sube al repositorio**.

## Arranque

**Producción** (comando documentado del servicio):

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

`--workers 4` levanta cuatro procesos servidores en paralelo. Si se necesita
cargar variables de entorno desde `.env`, añadir `--env-file .env`.

**No** usar `--reload` en producción: el watcher de archivos es incompatible
con `--workers` y no aporta valor cuando el código no cambia.

Para desarrollo local ocasional, arrancar con un solo worker sin recarga:

```bash
uvicorn main:app --host 127.0.0.1 --port 8000
```

## Endpoints

### Negocio

| Método | Ruta | Comportamiento |
|---|---|---|
| POST | `/score` | Puntúa una póliza. `200` con el resultado o `422` si la entrada es inválida. |
| GET | `/historial` | Lista de evaluaciones hechas por el servicio (en memoria). |
| GET | `/siniestros/{id}` | Consulta un siniestro por id. `200` con la fila o `404` si no existe. |
| GET | `/exportar` | Exporta el catálogo de siniestros en JSON. |

### Operación

| Método | Ruta | Comportamiento |
|---|---|---|
| GET | `/health` | Sonda de vida (liveness). Responde `200` sin consultar dependencias. |

### Perfil de carga (usados por la Parte C)

| Método | Ruta | Perfil |
|---|---|---|
| GET | `/ping` | trivial (`async def`) |
| GET | `/consulta-archivo` | IO-bound de disco (`def`) |
| GET | `/servicio-externo` | IO-bound de red (`async def` con `await asyncio.sleep`) |
| GET | `/calculo-pesado` | CPU-bound (`async def` + `run_in_executor` sobre `ProcessPoolExecutor`) |

### Ejemplos

Caso válido:
```bash
curl -X POST http://localhost:8000/score \
  -H "Content-Type: application/json" \
  -d '{"poliza": "POL-2026-0413", "monto": 4200000, "antiguedad": 3, "siniestros_previos": 1}'
```
Respuesta:
```json
{"poliza": "POL-2026-0413", "puntaje": 0.61, "alto_riesgo": false}
```

Entrada inválida (falta `poliza`):
```bash
curl -X POST http://localhost:8000/score \
  -H "Content-Type: application/json" \
  -d '{}'
```
Respuesta: `HTTP 422` con el detalle Pydantic de qué campos faltan.

Health check:
```bash
curl http://localhost:8000/health
# {"status": "ok"}
```

## Tests

```bash
python -m pytest tests/test_contrato.py -v
```

11 tests, todos verdes. Cubren el contrato mínimo del servicio: códigos HTTP,
validación con Pydantic, aislamiento del historial del dominio, identidad de
métodos y ausencia de errores tragados en silencio.

## Mediciones sync/async (Parte C)

Con el servicio arriba en `localhost:8000`, correr:

```bash
python medir.py
```

Escribe `MEDICIONES.csv` con 8 filas (4 endpoints × concurrencia {1, 20}).
La interpretación por endpoint está en `HALLAZGOS.md` sección «Parte C».

## Estructura del repositorio

```
.
├── main.py                     # Aplicación FastAPI y handlers
├── dominio.py                  # EvaluadorRiesgo, RepositorioHistorial, RepositorioSiniestros
├── config.py                   # Lectura de variables de entorno
├── medir.py                    # Herramienta de medición sync/async (Parte C)
├── modelo.pkl                  # Modelo entrenado (sklearn 1.7.2)
├── datos/
│   └── siniestros.csv          # Catálogo sintético de siniestros
├── tests/
│   └── test_contrato.py        # 11 tests que fija el contrato del servicio
├── plantillas/                 # Plantillas del taller (referencia)
├── ia_propuesta.py             # Código IA a auditar (Parte D)
├── ia_propuesta_corregida.py   # Corrección tras la auditoría (Parte D)
├── HALLAZGOS.md                # Diagnóstico (Parte A) + interpretación (Parte C)
├── MEDICIONES.csv              # Mediciones sync/async
├── DICTAMEN_IA.md              # Auditoría de la propuesta IA (Parte D)
├── BITACORA_IA.md              # Bitácora de uso de IA (Parte E)
├── requirements.txt            # Dependencias con versiones fijadas
├── .env.example                # Plantilla de variables de entorno
├── .gitignore                  # Reglas estándar de Python
└── README.md                   # Este archivo
```

## Grupo del taller

- Brayan David Barreto — `brayandavidbarreto@gmail.com`
- Edwing Navarrete
