# Hallazgos — Parte A

**Grupo:** <número> · **Integrantes:** Brayan David Barreto, Edwing Navarrete

> No borren la fila de ejemplo hasta haber comprobado que su tabla se parsea.
> El formato es rígido: siete columnas, en este orden. Una tabla torcida se
> rechaza indicando la línea, no se «entiende igual».
>
> **Tuberías dentro de una celda:** si su comando lleva `|` —y varios lo llevarán,
> por `grep`, `head` o `jq`— escríbanlo `\|`. Sin escapar, Markdown lo lee como
> separador de columna y su fila pasa a tener ocho.

| ID | Síntoma observable | Causa | Módulo · Sección | SHA donde se observa | Comando de evidencia | Salida obtenida | Corrección aplicada |
|----|--------------------|-------|------------------|----------------------|----------------------|-----------------|---------------------|
| H1 | *(ejemplo de FORMATO, no un defecto de este repositorio)* `GET /ping` responde sin cabecera `Cache-Control` | El handler no declara política de caché | M2 · 2. El protocolo HTTP y la autenticación | `v0-semilla` | `curl -sI localhost:8000/ping \| grep -ci cache-control` | `0` | Se añade la cabecera en la respuesta |
| H2 | `requirements.txt` no fija versiones; un `pip install` mañana puede traer una versión de sklearn incompatible con `modelo.pkl` | Dependencias declaradas sin `==` | M2 · 5. requirements.txt y la reproducibilidad | `v0-semilla` | `grep -cE "==" requirements.txt` | `0` | `pip freeze > requirements.txt` fijando versiones, en particular scikit-learn a la del entrenamiento |
| H3 | Higiene de git rota: `.gitignore` solo ignora `*.pyc` (no cubre `.venv/`, `__pycache__/`, `.env`, `.pytest_cache/`) y `config.py` versiona dos claves con formato de credencial (`API_KEY`, `CLAVE_FIRMA`) — el propio `# TODO` reconoce el defecto | El semilla trae reglas mínimas de `.gitignore` y secretos hardcodeados en un archivo comiteado al repo público | M1 · 5. Git y GitHub para investigadores | `v0-semilla` | `cat .gitignore; grep -nE "^(API_KEY\|CLAVE_FIRMA)" config.py` | `*.pyc`, `4:API_KEY = "sk-riesgo-2026-9f3a1c7b4e21"`, `5:CLAVE_FIRMA = "aseguradora-santo-tomas-2026"` | Ampliar `.gitignore` con rutas estándar de Python (venv, cache, pytest, egg-info, dotenv) y mover las claves a `os.environ` con valor por defecto seguro; `.env` ignorado |
| H4 | `EvaluadorRiesgo.historial = []` es atributo de clase mutable; todas las instancias comparten la misma lista, así que la evaluación que hace la póliza A aparece en el historial de la póliza B | El semilla declara `historial` en el cuerpo de la clase (`dominio.py:14`) en vez de en `__init__` o en un colaborador inyectable | M3 · 3. Componentes: atributos de clase | `v0-semilla` | `python -c "from dominio import EvaluadorRiesgo as E; a=E('POL-A'); b=E('POL-B'); a.anotar(0.5); print(len(b.historial))"` | `1` | Mover `historial` a atributo de instancia (`self.historial = []` en `__init__`) o sacarlo a un colaborador inyectable (`RepositorioHistorial`) — el test acepta ambas soluciones (B4) |
| H5 | `/score` sin campos devuelve status 200 con `{"error":"..."}` en el cuerpo; el cliente no puede distinguir éxito de error por el código HTTP | El handler no usa BaseModel y devuelve dict de error en la rama `if "poliza" not in payload` (`main.py:20-21`) | M2 · 2. El protocolo HTTP y la autenticación | `v0-semilla` | `curl -s -o /dev/null -w "%{http_code}" -X POST localhost:8000/score -H "content-type: application/json" -d "{}"` | `200` | Declarar request con `BaseModel` (B5); FastAPI responde 422 automáticamente cuando faltan campos |
| H6 | `/score` con `monto: -5` devuelve 500 (Internal Server Error) en vez de 422; el 500 confunde al cliente y a monitoreo, dispara alertas de oncall en producción por un error del cliente | Validación con `assert payload["monto"] > 0` (`main.py:23`) lanza `AssertionError` → 500; además se desactiva con `python -O` | M4 · 7. Del ValidationError al error HTTP 422 | `v0-semilla` | `curl -s -o /dev/null -w "%{http_code}" -X POST localhost:8000/score -H "content-type: application/json" -d '{"poliza":"POL-2026-0413","monto":-5,"antiguedad":3,"siniestros_previos":1}'` | `500` | En el `BaseModel` de request: `monto: float = Field(gt=0)`; Pydantic responde 422 automáticamente |
| H7 | `/siniestros/{id}` con id inexistente devuelve 200 con `{"error": "..."}` en vez de 404; el cliente no puede distinguir "existe" de "no existe" por el código HTTP | El handler retorna dict de error en vez de lanzar `HTTPException(404)` (`main.py:50-51`) | M2 · 2. El protocolo HTTP y la autenticación | `v0-semilla` | `curl -s -o /dev/null -w "%{http_code}" localhost:8000/siniestros/999999` | `200` | `raise HTTPException(status_code=404, detail=f"no existe el siniestro {id_siniestro}")` en la rama `if fila is None` |
| H8 | `/exportar` responde con pickle binario (`Content-Type: application/octet-stream`); serializar pickle hacia el cliente es un riesgo de seguridad — cualquier deserialización maliciosa puede ejecutar código arbitrario | El handler envuelve `pickle.dumps(datos)` en un `Response` con `media_type="application/octet-stream"` (`main.py:58`) | M2 · 3. JSON frente a Pickle | `v0-semilla` | `curl -s -D - -o /dev/null localhost:8000/exportar \| grep -i "^content-type"` | `content-type: application/octet-stream` | Retornar `{"siniestros": cargar_siniestros()}` directamente; FastAPI serializa a JSON |
| H9 | Cada petición POST a `/score` abre `modelo.pkl` del disco y lo deserializa con `pickle.load()`; suma I/O y CPU de deserialización por petición, y si el archivo se corrompe en runtime cada petición estalla | El semilla mete `with open(...) as fh: modelo = pickle.load(fh)` dentro del handler en vez de cargarlo al inicio (`main.py:28-29`) | M5 · 3. El servidor web y WSGI | `v0-semilla` | `grep -n "pickle.load\|open.*RUTA_MODELO" main.py` | `28:    with open(BASE / config.RUTA_MODELO, "rb") as fh:` y `29:        modelo = pickle.load(fh)` | Cargar el modelo una vez en el `lifespan` de FastAPI y exponerlo vía `app.state.modelo`; el handler lo consume sin abrir el archivo |
| H10 | Tres handlers declarados `async def` hacen operaciones bloqueantes en el cuerpo: `/consulta-archivo` lee disco con `.read_text()`, `/servicio-externo` usa `time.sleep(0.3)`, `/calculo-pesado` corre un loop CPU-intensivo. Bajo carga concurrente congelan el event loop y todas las demás peticiones esperan en fila | El semilla usa `async def` en todos los handlers por convención, sin distinguir el tipo de operación real dentro | M5 · 6. Síncrono frente a asíncrono | `v0-semilla` | `grep -nE "^async def\|time\.sleep\|read_text\|range\(3_000_000\)" main.py` | 11 líneas, incluyendo `70:    contenido = (BASE / config.RUTA_DATOS).read_text(...)`, `76:    time.sleep(0.3)`, `83:    for i in range(3_000_000):` | Parte C mide cada endpoint con concurrencia 1 y 20; se decide `def` (CPU-bound / IO disco) o `async def` + `await asyncio.sleep` (I/O red simulada) según los números |
| H11 | El servicio no expone `GET /health`; sin sonda de vida, cualquier orquestador (kubelet, systemd, ALB) no puede saber si el proceso está sano y podría no reiniciarlo cuando cuelga | El semilla nunca declaró el endpoint | M5 · 3. El servidor web y WSGI | `v0-semilla` | `curl -s -o /dev/null -w "%{http_code}" localhost:8000/health` | `404` | Añadir `@app.get("/health") def health(): return {"status": "ok"}` sin dependencias (liveness pura, no readiness) |
| H12 | El decorador `con_registro` (`utilidades.py`) reemplaza el `__name__` de las funciones envueltas por `envoltura` y captura todas las excepciones devolviendo `None`, convirtiendo cualquier error dentro del dominio en un `puntaje: null` silencioso | `envoltura` no usa `functools.wraps` y su `except Exception: return None` traga fallos en vez de dejarlos subir (`utilidades.py:6-11`) | M1 · 6. Decoradores como guardianes | `v0-semilla` | `python -c "from dominio import EvaluadorRiesgo as E; print(E.puntuar.__name__)"; curl -s -X POST localhost:8000/score -H "content-type: application/json" -d '{"poliza":"POL-2026-0413","monto":4200000,"antiguedad":3,"siniestros_previos":"muchos"}'` | `envoltura` seguido de `{"poliza":"POL-2026-0413","puntaje":null,"alto_riesgo":false}` | Añadir `@wraps(func)` y eliminar el `try/except: return None` para que los errores suban y se manejen donde corresponde |
| H13 | El README instruye arrancar en producción con `uvicorn ... --reload`, y `main.py` hace `uvicorn.run(..., reload=True)`; `--reload` monta un watcher del sistema de archivos incompatible con `--workers`, es para desarrollo. Un servicio en prod con `--reload` no escala y gasta recursos vigilando archivos que nunca cambian | El semilla documenta como "producción" el mismo comando de desarrollo | M5 · 5. Flask frente a frameworks modernos | `v0-semilla` | `grep -nE "reload" README.md main.py` | `README.md:18:uvicorn main:app --reload --host 0.0.0.0 --port 8000` y `main.py:90:    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)` (3 líneas en total) | README documenta `uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4`; se elimina el bloque `if __name__ == "__main__"` de `main.py` o se quita `reload=True` |


**Reglas que se verifican automáticamente:**

- `Módulo · Sección` debe citar una lección que exista en los módulos 1 a 5, con el
  título tal como aparece en el menú lateral del material.
- **`SHA donde se observa`** es el commit donde el defecto todavía está: normalmente
  `v0-semilla`, la etiqueta del repositorio tal como se lo entregamos. El calificador hace
  *checkout* de ese commit para reproducir la evidencia. Si lo dejan en el commit final —donde
  ya está corregido— el comando no reproducirá nada y la fila no cuenta.
- `Comando de evidencia` se ejecuta ahí. Escríbanlo contra `localhost:8000`; el calificador
  sustituye el puerto por el que use.
- `Salida obtenida` es literal, copiada de su terminal. **Se compara con lo que salga de
  verdad**, así que una salida inventada se detecta.
- Entre 6 y 12 hallazgos. Una fila que no corresponda a un defecto real resta la mitad de lo
  que suma una correcta: el máximo se alcanza con precisión, no con volumen.

---

# Parte C — Interpretación de las mediciones

> Un párrafo por endpoint. Expliquen **los tiempos que ustedes obtuvieron**, no la
> teoría general. Si un resultado los sorprendió, dígan­lo: eso se premia.

## `/ping`

**trivial · `async def`.** El handler solo retorna un dict literal, sin I/O ni cómputo real. Con concurrencia 1 el p50 es 2.2 ms — ida y vuelta HTTP más el overhead de FastAPI/uvicorn. Con concurrencia 20 el p50 apenas sube a 4.0 ms; el p95 de 2076 ms **no** es tiempo del servidor sino la cola del cliente: `medir.py` usa un `ThreadPoolExecutor` que lanza las 50 peticiones en tandas del tamaño de la concurrencia, y las últimas peticiones esperan en cola hasta que se libera un worker. Dejar el handler como `async def` o cambiarlo a `def` mide igual porque no hay operación bloqueante que reclame el thread pool.

## `/consulta-archivo`

**IO-bound · `def`.** Lee un CSV de ~50 KB con `read_text()`. Por la regla del material («I/O va con async»), tocaría `async def` con `aiofiles`; sin embargo la medición con `async def` del semilla (p50 4.1 ms con c=20) y con `def` (p50 3.7 ms con c=20) es indistinguible. Esta es una de las dos trampas que avisa el PDF: el archivo es tan pequeño que la latencia de I/O queda por debajo del ruido del ida y vuelta HTTP, así que aplicar o incumplir la regla da lo mismo. Nos quedamos con `def` porque no requiere `aiofiles` y deja que FastAPI mueva el handler al thread pool sin bloquear el event loop.

## `/servicio-externo`

**IO-bound · `async def`.** Simula una llamada de red con un sleep de 0.3 s. Con el declarador del semilla (`async def` + `time.sleep`) la medición con concurrencia 20 fue **catastrófica: p50 3628 ms, p95 14382 ms** — porque `time.sleep` es bloqueante y `async def` lo mete dentro del event loop, así que las 20 peticiones se serializaron. Cambiando a `await asyncio.sleep(0.3)` el event loop pudo despachar las 20 corrutinas en paralelo: p50 pasó a **333 ms** con c=20 (≈10× mejor) y el total del tramo de 15 s a 3 s. Es la trampa 1 del PDF: seguir la regla «I/O va con async» sin quitar la operación bloqueante da peor rendimiento; corregirla en serio requiere `await` sobre una primitiva async.

## `/calculo-pesado`

**CPU-bound · `async def + executor`.** Loop de 3 millones de raíces cuadradas. Con `async def` del semilla, c=20 dio p50 4938 ms — el cálculo bloquea el event loop y las 20 peticiones corren en serie. Intentamos pasarlo a `def` (que va al thread pool por defecto de FastAPI) esperando mejora, pero medimos **peor: p50 9778 ms**. Motivo: el GIL de Python serializa igual las 20 tareas CPU-bound, y añade overhead de context switching entre hilos. Aplicamos entonces la corrección canónica del material (M5 · 6.4.5 «async no es magia para todo»): `async def` en el handler + `run_in_executor` sobre un `ProcessPoolExecutor(max_workers=4)` a nivel de módulo. Con procesos separados fuera del GIL, c=20 bajó a p50 **2569 ms** — ~2× mejor que el semilla y ~4× mejor que el intento con `def`.
