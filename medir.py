"""
Instrumento de medición para la Parte C.

Lanza N peticiones a cada endpoint con una concurrencia dada, mide la latencia
de cada una y escribe MEDICIONES.csv con las ocho columnas que pide el enunciado.

    # arranca el servicio en otra terminal, y luego:
    python medir.py

    # o midiendo solo un endpoint, para probar:
    python medir.py --endpoints /ping --concurrencias 1 20 --peticiones 20

Lo que este script NO hace, y es lo que se califica: clasificar cada endpoint
como IO-bound o CPU-bound, decidir cómo debe declararse el handler, y explicar
los números que salgan. Las columnas `clasificacion` y `decision` las rellenan
ustedes; si las dejan vacías, el archivo no vale.

Pueden modificarlo. Si lo hacen, dígan­lo en HALLAZGOS.md.
"""
import argparse
import csv
import statistics
import time
from concurrent.futures import ThreadPoolExecutor

import httpx

ENDPOINTS = ["/ping", "/consulta-archivo", "/servicio-externo", "/calculo-pesado"]
COLUMNAS = ["endpoint", "clasificacion", "decision", "concurrencia",
            "peticiones", "tiempo_total_s", "p50_ms", "p95_ms"]


def percentil(muestras, q):
    """Percentil q (0-100) por interpolación lineal, sobre una lista ya ordenada."""
    if not muestras:
        return float("nan")
    xs = sorted(muestras)
    if len(xs) == 1:
        return xs[0]
    pos = (len(xs) - 1) * q / 100
    bajo, alto = int(pos), min(int(pos) + 1, len(xs) - 1)
    return xs[bajo] + (xs[alto] - xs[bajo]) * (pos - bajo)


def una_peticion(cliente, ruta):
    """Devuelve (milisegundos, ok). Un fallo NO se cuenta como medición."""
    t0 = time.perf_counter()
    try:
        r = cliente.get(ruta)
        ok = r.status_code < 500
    except Exception:
        ok = False
    return (time.perf_counter() - t0) * 1000, ok


def esperar_servicio(base, segundos=30):
    """Sin esto, una medición contra un servicio caído da tiempos preciosos y falsos."""
    limite = time.time() + segundos
    with httpx.Client(base_url=base, timeout=3) as c:
        while time.time() < limite:
            try:
                c.get("/openapi.json")
                return True
            except Exception:
                time.sleep(0.3)
    return False


def medir(base, ruta, concurrencia, peticiones, calentamiento=3):
    with httpx.Client(base_url=base, timeout=120) as cliente:
        for _ in range(calentamiento):          # descarta el arranque en frío
            una_peticion(cliente, ruta)
        t0 = time.perf_counter()
        with ThreadPoolExecutor(max_workers=concurrencia) as ex:
            resultados = list(ex.map(lambda _: una_peticion(cliente, ruta), range(peticiones)))
        total = time.perf_counter() - t0
    latencias = [ms for ms, ok in resultados if ok]
    fallidas = len(resultados) - len(latencias)
    if fallidas:
        raise RuntimeError(
            f"{fallidas} de {peticiones} peticiones a {ruta} fallaron. "
            "No se escribe el CSV: una medición sobre peticiones fallidas da "
            "tiempos rapidísimos y completamente falsos.")
    return {
        "endpoint": ruta, "clasificacion": "", "decision": "",
        "concurrencia": concurrencia, "peticiones": peticiones,
        "tiempo_total_s": round(total, 3),
        "p50_ms": round(statistics.median(latencias), 1),
        "p95_ms": round(percentil(latencias, 95), 1),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", default="http://localhost:8000")
    ap.add_argument("--endpoints", nargs="+", default=ENDPOINTS)
    ap.add_argument("--concurrencias", nargs="+", type=int, default=[1, 20])
    ap.add_argument("--peticiones", type=int, default=50)
    ap.add_argument("--salida", default="MEDICIONES.csv")
    a = ap.parse_args()

    if not esperar_servicio(a.base):
        print(f"ERROR: no hay ningún servicio respondiendo en {a.base}.")
        print("Arránquelo en otra terminal antes de medir.")
        raise SystemExit(1)

    filas = []
    for ruta in a.endpoints:
        for c in a.concurrencias:
            print(f"midiendo {ruta:<20} concurrencia {c:>3} … ", end="", flush=True)
            fila = medir(a.base, ruta, c, a.peticiones)
            filas.append(fila)
            print(f"{fila['tiempo_total_s']:>7.3f} s   p50 {fila['p50_ms']:>8.1f} ms   "
                  f"p95 {fila['p95_ms']:>8.1f} ms")

    with open(a.salida, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNAS)
        w.writeheader()
        w.writerows(filas)
    print(f"\n{a.salida} escrito con {len(filas)} filas.")
    print("Falta lo suyo: rellenar `clasificacion` y `decision` en cada fila.")


if __name__ == "__main__":
    main()
