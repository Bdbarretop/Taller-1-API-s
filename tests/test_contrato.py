"""
Contrato que el servicio debe cumplir al terminar el taller.

Estos tests están ROJOS sobre el repositorio tal como se entrega. Todos deben
pasar cuando terminen la Parte B. Que pasen es el mínimo, no la meta: hay
criterios de la rúbrica que estos tests no ven.

    pytest -v
"""
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app  # noqa: E402

cliente = TestClient(app)

VALIDO = {
    "poliza": "POL-2026-0413",
    "monto": 4_200_000,
    "antiguedad": 3,
    "siniestros_previos": 1,
}


# --- M5 · arquitectura del servicio ---------------------------------------

def test_health_responde_200():
    assert cliente.get("/health").status_code == 200


# --- M2 · contratos HTTP ---------------------------------------------------

def test_falta_un_campo_obligatorio_da_422():
    r = cliente.post("/score", json={"monto": 1000})
    assert r.status_code == 422, f"devolvió {r.status_code}"


def test_monto_negativo_da_422_y_no_500():
    r = cliente.post("/score", json={**VALIDO, "monto": -5})
    assert r.status_code == 422, f"devolvió {r.status_code}"


def test_antiguedad_negativa_da_422():
    r = cliente.post("/score", json={**VALIDO, "antiguedad": -1})
    assert r.status_code == 422, f"devolvió {r.status_code}"


def test_ningun_error_viaja_con_200():
    for cuerpo in ({}, {"monto": -1}, {**VALIDO, "antiguedad": -3}):
        r = cliente.post("/score", json=cuerpo)
        assert not (r.status_code == 200 and "error" in r.text.lower()), (
            f"error devuelto con 200 para {cuerpo}"
        )


def test_siniestro_inexistente_da_404():
    assert cliente.get("/siniestros/999999").status_code == 404


# --- M2 · serialización ----------------------------------------------------

def test_exportar_devuelve_json_no_pickle():
    r = cliente.get("/exportar")
    assert r.headers["content-type"].startswith("application/json"), (
        f"content-type: {r.headers['content-type']}"
    )
    r.json()


# --- M3 · POO --------------------------------------------------------------

def test_el_historial_no_se_comparte_entre_instancias():
    from dominio import EvaluadorRiesgo

    a, b = EvaluadorRiesgo("POL-A"), EvaluadorRiesgo("POL-B")
    a.anotar(0.5)
    # getattr con defecto: vale tanto mover el historial a la instancia como
    # sacarlo del evaluador a un colaborador. Lo que no vale es compartirlo.
    ajeno = getattr(b, "historial", [])
    assert len(ajeno) == 0, f"la instancia B ve {len(ajeno)} anotaciones que no hizo"


# --- M1 · decoradores ------------------------------------------------------

def test_el_decorador_conserva_la_identidad_de_la_funcion():
    from dominio import EvaluadorRiesgo

    assert EvaluadorRiesgo.puntuar.__name__ == "puntuar", (
        f"la función dice llamarse {EvaluadorRiesgo.puntuar.__name__!r}"
    )


def test_un_fallo_al_puntuar_no_se_traga_en_silencio():
    r = cliente.post("/score", json={**VALIDO, "siniestros_previos": "muchos"})
    assert r.status_code != 200 or r.json().get("puntaje") is not None, (
        "devolvió 200 con puntaje nulo: el fallo se tragó"
    )


# --- M4 · validación declarativa ------------------------------------------

def test_el_caso_valido_sigue_funcionando():
    r = cliente.post("/score", json=VALIDO)
    assert r.status_code == 200
    cuerpo = r.json()
    assert 0.0 <= cuerpo["puntaje"] <= 1.0
