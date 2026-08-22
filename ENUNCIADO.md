# Taller del Corte I — «Riesgo API v0»

**Python para Desarrollo de APIs e IA** · USTA · Estadística · 2026-II · Código 28549
**Cubre:** módulos 1 a 5 · **Peso:** 60 % del Corte I (18 % de la nota definitiva)
**Grupos:** máximo 3 personas · **Publicado:** sáb 22 ago 2026
**Congelado del repositorio:** vie 4 sep 2026, 23:59 · **Sustentación:** sesión de la primera semana de septiembre

---

## 1. De qué se trata

Reciben un servicio web que **funciona pero está mal hecho**: `riesgo-api-v0`, un
microservicio mínimo de puntuación de siniestros. Arranca, responde y hace lo que dice el
README. También arrastra una colección de decisiones equivocadas, todas del tipo que este
curso lleva cinco semanas enseñando a no tomar.

El trabajo tiene cinco partes: **diagnosticar** lo que está mal, **arreglarlo** bajo
restricciones, **decidir y medir** un punto donde la intuición falla, **auditar una propuesta
de código escrita por IA**, y **defender** lo que hicieron.

### Lo que se evalúa, y lo que no

| Sí se evalúa | No se evalúa |
|---|---|
| Que sepan nombrar lo que ven y por qué está mal | Que el código sea largo |
| Que la decisión técnica esté justificada y medida | Que hayan añadido funcionalidades extra |
| Que sepan comprobar si algo funciona | Que el servicio tenga interfaz gráfica |
| Que cada integrante responda por el repositorio | La elegancia del formateo |

Cualquier cosa que añadan más allá de lo pedido no suma puntos y sí ocupa el tiempo de la
defensa. La consigna es **hacer lo pedido y saber por qué**.

---

## 2. Reglas del juego

### 2.1 La IA está permitida — y es parte de lo evaluado

Pueden usar cualquier asistente de IA, sin restricción y para cualquier parte. A cambio, dos
obligaciones:

1. **Bitácora obligatoria** (`BITACORA_IA.md`). Registran los prompts relevantes, qué
   aceptaron y —esto es lo que se califica— **qué rechazaron y con qué argumento**. Una
   bitácora que solo lista prompts aceptados vale la mitad.
2. **La Parte D audita a la IA.** Se les entrega código generado por IA que parece correcto y
   no lo es. Encontrarlo es el ejercicio.

Bitácora ausente o falsificada: **−15 puntos**.

El taller está diseñado sabiendo que van a usar IA. Las partes A y B las van a resolver más
rápido con ayuda, y está bien: ese tiempo es para las partes C, D y E, donde la IA no puede
medir en su máquina, no audita bien su propio código, y no se sienta en la sustentación.

### 2.2 Entrega

- **Un repositorio en GitHub por grupo**, con historia real de commits. No se reciben `.zip`:
  el criterio C2 califica `git log` por autor.
- El enlace se entrega por Moodle antes del **vie 4 sep, 23:59**. Se registra el SHA del
  último commit a esa hora; **lo que se califica es ese commit**, no lo que haya después.
- Entrega fuera de plazo: no se recibe.
- El repositorio debe arrancar siguiendo **su propio README**, en una máquina limpia. Si no
  arranca, la nota tiene tope de 60.

### 2.3 Grupos y responsabilidad individual

Máximo 3. Son 32 estudiantes: habrá diez grupos de tres y uno de dos. Esta agrupación **es
independiente de los equipos de dos del proyecto integrador** y no crea equipo de proyecto.

Repartan el trabajo como quieran, pero **cualquier integrante puede ser preguntado por
cualquier línea del repositorio**. El 30 % de la nota es individual, y se mide dos veces:

**Control presencial — segunda sesión de la última semana de agosto, 10 minutos, individual, sin IA y sin
consultar a los compañeros.** Papel y lápiz; no hace falta computador.

A cada estudiante se le entrega **un endpoint que no ha visto**, de cinco a diez líneas, y
escribe:

1. **Clasificación:** `IO-bound`, `CPU-bound` o `trivial`.
2. **Decisión:** `def`, `async def` o `async def + executor`.
3. **Justificación**, dos o tres frases: *por qué*.
4. **Predicción:** qué esperaría ver al medirlo con concurrencia 1 y con 20, y por qué.

No se pide reproducir nada de lo que entregaron: se pide **llevar el criterio de la Parte C a
un caso nuevo**. Los tres integrantes de un grupo reciben endpoints distintos.

Lo que se califica es la justificación y la predicción. Acertar la etiqueta sin saber
justificarla vale poco; equivocarse de etiqueta con un razonamiento que revela comprensión
vale bastante. Si hicieron la Parte C ustedes, esto les sale en cinco minutos.

No se evalúa que el número coincida al decimal, sino que sepan producirlo y leerlo.

**La nota individual acota la grupal.** La nota final de cada estudiante es:

> `nota = min( 0,70 × grupal + 0,30 × individual ,  individual + 15 )`

Es decir: un buen repositorio no compensa no entender lo que hay dentro. Si su nota
individual es 40, la final no pasa de 55 por bueno que sea el trabajo del grupo. Si ambas van
parejas, la cota no se activa y no cambia nada.

---

## 3. El artefacto

```bash
git clone <url-del-semilla> riesgo-api
cd riesgo-api
cat README.md          # léanlo: forma parte del problema
```

Contiene un servicio de puntuación de siniestros con **ocho endpoints** —cuatro de negocio
(`/score`, `/historial`, `/siniestros/{id}`, `/exportar`) y cuatro de perfil de carga, que
usarán en la Parte C—, un modelo serializado de juguete (`modelo.pkl`), un dataset sintético
y un README. **Arranca.**
Ninguno de los defectos impide que corra: por eso hay que buscarlos.

No se dice cuántos defectos hay.

---

## 4. Las cinco partes

### Parte A — Diagnóstico

Encuentren los defectos y documéntenlos en **`HALLAZGOS.md`**, una fila por defecto, con
este formato exacto:

```markdown
| ID | Síntoma observable | Causa | Módulo · Sección | SHA donde se observa | Comando de evidencia | Salida obtenida | Corrección aplicada |
|----|--------------------|-------|------------------|----------------------|----------------------|-----------------|---------------------|
| H1 | *(ejemplo de FORMATO, no un defecto de este repositorio)* `GET /ping` responde sin cabecera `Cache-Control` | El handler no declara política de caché | M2 · 2. El protocolo HTTP y la autenticación | `v0-semilla` | `curl -sI localhost:8000/ping \| grep -ci cache-control` | `0` | Se añade la cabecera en la respuesta |
```

Reglas:

- **`Módulo · Sección` debe citar una sección que exista** en el material de los módulos 1 a
  5, con su título tal como aparece en el menú lateral. El calificador lo verifica contra los
  archivos del curso; una cita inventada anula la fila.
- **`SHA donde se observa`.** Aquí está el punto: el síntoma se observa en el repositorio
  **roto**, y la Parte B lo repara. Si el calificador ejecutara su comando sobre el commit
  final no vería nada. Declaren el commit donde el defecto todavía vive —normalmente
  `v0-semilla`, la etiqueta del repositorio tal como se lo entregamos— y el calificador hace
  *checkout* ahí para reproducirlo.
- **`Comando de evidencia` debe ser ejecutable y reproducible.** El calificador lo corre sobre
  ese commit. Escríbanlo contra `localhost:8000`: el puerto lo sustituye el calificador.
- **`Salida obtenida` es literal**, copiada de su terminal. No parafraseada. **Se compara con
  la salida real**, normalizando solo puertos, fechas y rutas absolutas. Una salida inventada
  se detecta.
- **Entre 6 y 12 hallazgos.** Una fila que no corresponda a un defecto real **resta la mitad**
  de lo que suma una correcta. El máximo se alcanza con precisión, no con volumen.
- **Si el comando lleva `|`, escríbanlo `\|`.** Sin escapar, Markdown lo lee como
  separador de columna y la fila queda con ocho campos: el parser la rechaza.
- Un hallazgo sin evidencia ejecutable no cuenta.

### Parte B — Refactor con restricciones

Arreglen el servicio. Las restricciones no son sugerencias; el calificador las comprueba:

| # | Restricción | Módulo |
|---|---|---|
| B1 | El entorno es reproducible: `requirements.txt` con versiones fijadas, sin secretos versionados, `.gitignore` correcto | M1 |
| B2 | Los códigos de estado HTTP son correctos y **el error viaja en el estado, no en el cuerpo con 200** | M2 |
| B3 | Nada se serializa con `pickle` hacia el cliente | M2 |
| B4 | El dominio vive en **clases**, no en funciones sueltas con estado global | M3 |
| B5 | **Todas** las entradas y salidas se declaran con `BaseModel`; restricciones con `Field`; al menos un validador de campo; `ValidationError` → **422** | M4 |
| B6 | El modelo se carga **al iniciar el servicio**, no dentro del handler | M5 |
| B7 | Existe un endpoint `/health` que responde 200 | M5 |
| B8 | El arranque documentado es de producción: `uvicorn` **sin `--reload`** y con `--workers`. Un servidor con recarga en caliente no es apto para producción | M5 |
| B9 | Ningún decorador propio oculta la identidad de la función que envuelve, ni captura excepciones para devolver `None` | M1 |

**El contrato de rutas no se cambia.** Estas son las rutas y los verbos que el calificador
va a golpear; renombrarlas o cambiarles el verbo hace fallar los checks:

| Verbo | Ruta | Devuelve |
|---|---|---|
| POST | `/score` | 200 con la puntuación · 422 si la entrada es inválida |
| GET | `/historial` | 200 |
| GET | `/siniestros/{id}` | 200 · **404** si no existe |
| GET | `/exportar` | 200 en **JSON** |
| GET | `/health` | 200 · **hay que crearlo** |
| GET | `/ping`, `/consulta-archivo`, `/servicio-externo`, `/calculo-pesado` | 200 |

Pueden añadir rutas si lo justifican; no pueden quitar ni renombrar estas.

**El contrato de dominio tampoco.** La batería construye objetos directamente, así que dos
nombres quedan fijados:

- `dominio.EvaluadorRiesgo` debe poder construirse **solo con la póliza**:
  `EvaluadorRiesgo("POL-2026-0413")`. Cualquier colaborador que necesiten —el modelo, un
  repositorio— va como argumento **opcional**.
- El método que registra una evaluación se sigue llamando `anotar(puntaje)`.

Dentro de esos dos límites el modelado es suyo: dónde vive el historial, qué clases hay y
qué colabora con qué es justo lo que califica C5.

En `tests/test_contrato.py` hay una batería de once tests. Diez están **en rojo** sobre el
repositorio tal como se entrega y **todos deben pasar al terminar**. Que pasen es el mínimo,
no la meta: hay criterios de rúbrica que los tests no ven. **No modifiquen ni borren esos
tests**: se comprueba que el archivo llega intacto.

### Parte C — Decisión sync/async, medida

El servicio expone cuatro endpoints con perfiles distintos:

| Endpoint | Qué hace |
|---|---|
| `/consulta-archivo` | Lee un archivo del disco |
| `/calculo-pesado` | Cálculo numérico intensivo en CPU |
| `/servicio-externo` | Llama a otro servicio HTTP (simulado con latencia) |
| `/ping` | Devuelve una constante |

Para cada uno: clasifíquenlo, decidan cómo debe declararse el handler, y **demuéstrenlo
midiendo**.

Los dos vocabularios son cerrados —se parsean, escríbanlos exactamente así:

| Columna | Valores admitidos |
|---|---|
| `clasificacion` | `IO-bound` · `CPU-bound` · `trivial` |
| `decision` | `def` · `async def` · `async def + executor` |

Entregan **`MEDICIONES.csv`** con estas columnas exactas:

```csv
endpoint,clasificacion,decision,concurrencia,peticiones,tiempo_total_s,p50_ms,p95_ms
/ejemplo,IO-bound,async def,1,50,10.42,206.1,214.8
/ejemplo,IO-bound,async def,20,50,0.63,240.7,268.3
```

`/ejemplo` no existe: la fila muestra el **formato**, no una respuesta.

Cada endpoint con **dos condiciones**: concurrencia 1 y concurrencia 20.

**El semilla trae `medir.py` funcionando**: lanza las peticiones, calienta la caché, calcula
los percentiles y escribe el CSV con las ocho columnas. Lo que no hace —y es lo que se
califica— es rellenar `clasificacion` y `decision`, ni explicar los números. Pueden
modificarlo; si lo hacen, dígan­lo en `HALLAZGOS.md`.

Y un párrafo por endpoint en **`HALLAZGOS.md`** (sección «Parte C») que explique **los
tiempos que obtuvieron ustedes**. Se califica la coherencia entre la clasificación, la
decisión que quedó en el código y la explicación de los números. No se califica el número.

> Aviso: la regla «I/O va con `async`» falla en más de un caso, y de dos maneras distintas.
> En uno, seguirla da peor rendimiento. En otro, el código incumple la regla y **la medición
> dice que da exactamente igual**. Los dos cuentan, y el segundo solo se responde bien
> midiendo primero y decidiendo después. Midan antes de decidir.

### Parte D — Auditoría de la propuesta de IA

En el repositorio hay un archivo **`ia_propuesta.py`**: código generado por un asistente de
IA para resolver parte de este mismo taller. Importa y ejecuta sin errores de sintaxis. Está
comentado, es legible y **tiene tres defectos de comportamiento**.

Entregan **`DICTAMEN_IA.md`**:

```markdown
## Defecto 1
- **Qué está mal:**
- **Por qué es un defecto** (citando módulo · sección):
- **Cómo lo comprobamos:** (código o comando que lo demuestra, con su salida)
- **Corrección:**
```

Más `ia_propuesta_corregida.py` con las tres correcciones aplicadas.

El peso está en **«cómo lo comprobamos»**. Afirmar que algo está mal no vale; demostrarlo, sí.

### Parte E — Bitácora y sustentación

**`BITACORA_IA.md`**, con estas secciones obligatorias: `## Prompts`, `## Aceptado`,
`## Rechazado`. En `## Rechazado` va lo que se califica: qué les propuso la IA que no
aceptaron, y por qué. Es el único apartado de la bitácora con peso propio.

**Sustentación: 12 minutos.**

- **4 min — demo en vivo.** Levantan el servicio delante del curso y le pegan con `curl`:
  un caso válido, uno inválido que debe dar 422, y `/health`. Sin diapositivas.
- **8 min — preguntas dirigidas.** Se pregunta a **un integrante concreto** por **una línea
  concreta** de su repositorio. Todos deben poder responder por todo.

---

## 5. Qué se entrega — lista de verificación

En la raíz del repositorio:

- [ ] El servicio corregido, que arranca siguiendo su propio README
- [ ] `HALLAZGOS.md` — tabla de la Parte A + sección «Parte C»
- [ ] `MEDICIONES.csv` — Parte C, 4 endpoints × 2 condiciones = 8 filas
- [ ] El script de medición
- [ ] `DICTAMEN_IA.md` — Parte D
- [ ] `ia_propuesta_corregida.py` — Parte D
- [ ] `BITACORA_IA.md` — Parte E
- [ ] `requirements.txt` con versiones fijadas
- [ ] `README.md` actualizado con el arranque real

Las cuatro plantillas vienen en `plantillas/` **dentro del repositorio semilla**. Cópienlas a
la raíz y rellénenlas; no las reescriban desde cero: traen resueltos detalles de formato que
el parser exige.

---

## 6. Rúbrica — 100 puntos

**Nota del taller = min( 0,70 × grupal + 0,30 × individual , individual + 15 )**, con la
nota individual repartida así:

| # | Componente individual | Pts |
|---|---|---:|
| I1 | Sustentación dirigida, sesión de la primera semana de septiembre | 50 |
| I2 | Control presencial, segunda sesión de la última semana de agosto: un endpoint nuevo, sin IA | 30 |
| I3 | Contribución trazable al repositorio (`git log` propio) | 20 |

Escala por criterio: **4 Excelente (100 %) · 3 Competente (75 %) · 2 En desarrollo (50 %) ·
1 Insuficiente (25 %) · 0 Ausente o no verificable.**

| # | Criterio | Pts | Nivel 4 se ve así |
|---|---|---:|---|
| C1 | Entorno reproducible (M1) | 8 | Versiones fijadas; `pip install` limpio en venv nuevo; sin secretos versionados; `.gitignore` correcto |
| C2 | Higiene de Git y trazabilidad (M1) | 7 | Un autor por integrante con ≥ 2 commits sustantivos cada uno; mensajes que describen el cambio |
| C3 | Diagnóstico (Parte A) | 15 | Todos los defectos hallados, cada uno con síntoma, causa, cita real al material y evidencia reproducible |
| C4 | Contratos HTTP (M2 + M4) | 12 | Verbos correctos; 200/404/422; el error viaja en el estado; respuesta JSON, nunca `pickle` |
| C5 | Modelado del dominio con POO (M3) | 12 | Dominio en clases con responsabilidad clara; sin estado mutable de clase; herencia donde aporta |
| C6 | Validación declarativa (M4) | 12 | Entradas y salidas en `BaseModel`; restricciones en `Field`; ≥ 1 validador; `ValidationError` → 422 |
| C7 | Arquitectura del servicio (M5) | 10 | Modelo cargado al inicio, no por petición; `/health`; arranque de producción documentado, sin `--reload` |
| C8 | Decisión sync/async con evidencia (Parte C) | 10 | Los 4 clasificados bien; `MEDICIONES.csv` completo y reproducible; la interpretación explica **sus** tiempos |
| C9 | Auditoría de la propuesta de IA (Parte D) | 10 | Los 3 defectos identificados; comprobación descrita y ejecutable; corrección que funciona |
| C10 | Bitácora de IA (Parte E) | 4 | Rechazos argumentados y localizables, no solo prompts aceptados |
| | **Total** | **100** | |

**Penalizaciones:** bitácora ausente o falsificada −15 · repositorio que no arranca siguiendo
su propio README, tope de 60 · entrega fuera del congelado, no se recibe.

---

## 7. Cómo se califica

68 de los 100 puntos los resuelve un **calificador automático** que se corre sobre su
repositorio: crea un entorno limpio, instala sus dependencias, corre una batería de tests que
ustedes no ven, levanta su servicio y le pega, analiza la estructura de su código y ejecuta
los comandos de evidencia que declararon. Los 32 restantes —la calidad del diagnóstico, del
modelado, de la interpretación y del dictamen— los lee el docente.

Reciben `reporte_<grupo>.md` con **la nota de cada criterio y la evidencia que la sustenta**:
el comando ejecutado y su salida literal. Es auditable: si creen que un check está mal, se
revisa contra esa evidencia.

Dos consecuencias prácticas:

- **Los formatos son rígidos porque se parsean.** Una tabla torcida en `HALLAZGOS.md` no se
  «entiende igual»: se rechaza indicando la línea. Usen las plantillas.
- **Que el calificador no pueda medir algo no es un aprobado.** Sale marcado como no
  verificable, que en la escala es 0.
