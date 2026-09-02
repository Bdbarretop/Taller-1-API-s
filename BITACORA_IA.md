# Bitácora de uso de IA

**Grupo:** <número> · **Integrantes:** Brayan David Barreto, Edwing Navarrete
**Herramientas usadas:** Claude (Anthropic), interfaz Claude Code sobre el repositorio local.

> Las tres secciones son obligatorias. **`## Rechazado` es la que se califica.**
> Una bitácora que solo lista prompts aceptados vale la mitad.

## Prompts

| # | Parte | Quién | Prompt (resumido si es largo) |
|---|-------|-------|-------------------------------|
| 1 | A | Brayan | "Analiza el semilla `riesgo-api-v0` y propón los defectos observables por eje temático (M1-M5) para llenar HALLAZGOS.md; cada uno con comando ejecutable y salida real capturada sobre `v0-semilla`." |
| 2 | A | Brayan | "Reduce el catálogo a un máximo de 12 hallazgos priorizando cobertura de los 5 módulos; agrupa defectos hermanos en una sola fila si comparten sección del material." |
| 3 | B | Brayan | "Aplica las restricciones B1-B9 en el orden que minimice retrabajo; presenta cada bloque como diff antes de aplicar." |
| 4 | B | Brayan | "Rediseña `dominio.py` respetando el contrato invariante `EvaluadorRiesgo('POL-...')` y método `anotar(puntaje)`; separa responsabilidades en clases colaboradoras (M3 · 5)." |
| 5 | B | Brayan | "Reescribe main.py con `SolicitudScore(BaseModel)` y `RespuestaScore(BaseModel)` usando `Field`, un `@field_validator` y `HTTPException` para 404 (M4 · 4/6/7, M2 · 2)." |
| 6 | C | Brayan | "Corre `medir.py` sobre el servicio arreglado con concurrencia 1 y 20, primero con el declarador del semilla y después con la decisión final por endpoint; propón la clasificación y decisión basada en las mediciones, no en teoría." |
| 7 | C | Brayan | "Con la medición de `/calculo-pesado` empeorando al cambiar de `async def` a `def`, propón la corrección canónica siguiendo el material y explica por qué la ruta anterior falló." |
| 8 | D | Edwing | "Ayúdame a leer `ia_propuesta.py` línea por línea y a identificar defectos de comportamiento verificables con comando; no me des la solución, dame pistas dirigidas." |
| 9 | D | Edwing | "Redacta las tres secciones del DICTAMEN_IA.md con las comprobaciones que ejecuté y su salida real." |
| 10 | E | Brayan | "Recopila los rechazos capturados durante el trabajo y filtra a los que tienen anclaje real al material del curso (no razones generales)." |

## Aceptado

| # | Qué propuso la IA | Por qué lo aceptamos | Qué cambiamos antes de usarlo |
|---|-------------------|----------------------|-------------------------------|
| 1 | Copiar la plantilla `plantillas/HALLAZGOS.md` a la raíz y llenarla, sin reescribirla desde cero. | El PDF pide explícitamente usar las plantillas por el detalle de formato que el parser exige. | Añadimos filas H8-H13 y las filas nuevas mantuvieron exactamente 8 columnas (validado con `awk -F'\|'`). |
| 2 | Cargar el modelo en variable de módulo (`with open(...) as f: MODELO = pickle.load(f)` a nivel de módulo) para B6. | Es el patrón canónico enseñado en M5 · 3 con el ejemplo `modelo_credito.pkl`, y funciona con `TestClient(app)` sin `with` (los tests no se pueden modificar). | Nada estructural. Se documentó en el comentario "Patrón enseñado en M5 · 3, cubre B6". |
| 3 | Usar `HTTPException(status_code=404, detail=...)` para el 404 en `/siniestros/{id}` (B2). | Es la primitiva idiomática de FastAPI para el 404 y M2 · 2 la presenta como el canal correcto. | Ninguno. |
| 4 | `RespuestaScore` como `response_model` en el decorador de `/score` (M4 · 3). | Los `BaseModel` son contrato de ida y vuelta: validan también la salida (`puntaje ∈ [0, 1]`). | Ninguno. |
| 5 | Para `/servicio-externo`, cambiar `async def + time.sleep` a `async def + await asyncio.sleep`. | La medición mostró mejora de 10× (p50 c=20 de 3628 ms a 333 ms) y es la corrección fiel al material M5 · 6. | Ninguno. |
| 6 | Para `/calculo-pesado`, aplicar `async def + run_in_executor` con `ProcessPoolExecutor(max_workers=4)`. | Es la ruta canónica del material (M5 · 6.4.5 «async no es magia para todo»); la medición confirmó mejora vs. el semilla (p50 c=20 de 4938 ms a 2569 ms). | Añadimos guarda `multiprocessing.current_process().name == "MainProcess"` para evitar recursión en el spawn de Windows. |
| 7 | Retirar `@con_registro` de `dominio.EvaluadorRiesgo.puntuar` (B4/B9). | Separa responsabilidades: el logging no es lógica de dominio (M3 · 5); el test de identidad pasa directamente sin necesidad de `functools.wraps`. | Ninguno. |
| 8 | Eliminar `utilidades.py` en vez de "curarlo" (B9). | M1 · 7 «Síntesis: de idea a análisis reproducible» pide repositorios sin código muerto; grep confirmó que ningún módulo importa `con_registro`. | Ninguno. |
| 9 | Rehacer el `.gitignore` con la lista estándar de Python (venv, cache, pytest, dotenv, IDEs). | M1 · 5 «Git y GitHub para investigadores» presenta el `.gitignore` como parte de la higiene mínima. | Redujimos el archivo a 30 líneas evitando patrones para tecnologías que no usamos (sin Django, Jupyter, Poetry, Pipenv). |

## Rechazado

| # | Qué propuso la IA | Por qué lo rechazamos | Qué hicimos en su lugar |
|---|-------------------|-----------------------|-------------------------|
| 1 | Cargar el modelo con `@asynccontextmanager` (lifespan moderno) escribiendo a `app.state.modelo`. Sería la forma "moderna" de FastAPI. | M5 · 3 no cubre `lifespan` — el material canónico enseña la variable de módulo al importar. Además `TestClient(app)` sin bloque `with` **no dispara el lifespan**, por lo que `tests/test_contrato.py` (que no se puede modificar) explota con `AttributeError: 'State' object has no attribute 'modelo'`. Dos razones curriculares para rechazarlo. | Carga del modelo al importar `main.py`, siguiendo literalmente el ejemplo de M5. |
| 2 | Para `/consulta-archivo` seguir la regla «I/O va con async» con `async def` + `aiofiles`. | Medimos primero: `async def` p50 c=20 = 4.1 ms; `def` p50 c=20 = 3.7 ms. La diferencia es ruido (el CSV tiene ~50 KB, la latencia queda por debajo del ida y vuelta HTTP). Es la trampa 2 que anuncia el PDF: "en un caso, el código incumple la regla y la medición dice que da exactamente igual". Introducir `aiofiles` sumaría dependencia y complejidad sin mejora medible. | `def` (thread pool de FastAPI). Documentado en el párrafo de `/consulta-archivo` como caso donde la regla no aporta. |
| 3 | Para `/calculo-pesado` cambiar de `async def` a `def` con la lógica "CPU-bound → def → thread pool → 20 hilos concurrentes → mejora". | Medimos: `def` p50 c=20 = 9778 ms vs 4938 ms del semilla. **Empeoró 2×**. Motivo: el GIL de Python serializa igual las 20 tareas CPU-bound y añade overhead de context switching. Además el material M5 · 6.4.5 «async no es magia para todo» dice literalmente: "async no ayuda porque el procesador está realmente ocupado. La estrategia correcta es delegar el cómputo a un proceso separado con `run_in_executor` + `ProcessPoolExecutor`". Mi propuesta con `def` no seguía la ruta canónica del material ni mejoraba la medición. | `async def` + `run_in_executor(CPU_EXECUTOR, ...)` con `ProcessPoolExecutor(max_workers=4)` a nivel de módulo. p50 c=20 bajó a 2569 ms (~2× mejor que el semilla, ~4× mejor que el intento con `def`). |
| 4 | Para `/servicio-externo` solo cambiar el declarador de `async def` a `def` (dejando `time.sleep`). En teoría, FastAPI lo mueve al thread pool y las 20 peticiones corren en paralelo. | M5 · 6 presenta `async def + await` como la forma canónica para operaciones de red (que es lo que `/servicio-externo` simula). Cambiar solo el declarador sin corregir la operación bloqueante funciona empíricamente pero enseña al lector que `def` es sinónimo de "arreglo" para `time.sleep`, cuando en un mundo real la llamada sería `await httpx.AsyncClient().get(...)` que sí exige `async`. | `async def` + `await asyncio.sleep(0.3)`. Corrección fiel al material y semilla directa para migrar a un cliente HTTP async real. p50 c=20 pasó de 3628 ms a 333 ms. |
| 5 | Partir el defecto del decorador `con_registro` (H12) en dos filas separadas en HALLAZGOS: una para "no usa `functools.wraps`" y otra para "traga excepciones a `None`", ya que técnicamente son vicios distintos y cada uno tiene su test. | Ambos vicios viven en las mismas 12 líneas de `utilidades.py`, la **restricción B9 los cubre juntos** ("ningún decorador propio oculta la identidad de la función ni captura excepciones para devolver None") y el material los presenta en la misma sección (M1 · 6 «Decoradores como guardianes»). Duplicar la fila infla el conteo sin agregar información — el PDF dice explícitamente "el máximo se alcanza con precisión, no con volumen". | Una sola fila H12 con los dos síntomas y dos comandos separados por `;`. El slot liberado se usó para otro defecto real. |
| 6 | En el plan original, hacer dos commits sintéticos para la Parte A separando "hallazgos M1-M2" y "hallazgos M3-M5" para inflar el conteo de commits sustantivos por autor. | Los 12 hallazgos se encontraron y verificaron intercalados (por eje temático, no por módulo). Forzar dos commits requeriría editar el archivo dejando solo una mitad, hacer commit, restaurar y commit — una historia falsa. **El criterio C2 califica "historia real de commits"**, no "número de commits". Además ya hay 5 commits sustantivos garantizados solo en Parte B. | Un solo commit para la Parte A con los 12 hallazgos completos y mensaje descriptivo. |
