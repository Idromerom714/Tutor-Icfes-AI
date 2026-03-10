"""
Tests para lógica de diagnóstico inicial (core/diagnostic.py).
"""

import pytest
from datetime import datetime, timedelta, timezone


class TestObtenerPreguntasDiagnostico:
    """Tests para selección de preguntas."""

    def test_retorna_cantidad_solicitada(self):
        from core.diagnostic import obtener_preguntas_diagnostico

        preguntas = obtener_preguntas_diagnostico(cantidad=12, semilla=42)

        assert len(preguntas) == 12
        assert all("dificultad" in p for p in preguntas)

    def test_no_expone_respuesta_correcta(self):
        from core.diagnostic import obtener_preguntas_diagnostico

        preguntas = obtener_preguntas_diagnostico(cantidad=10, semilla=1)

        assert all("respuesta_correcta" not in p for p in preguntas)

    def test_falla_fuera_de_rango(self):
        from core.diagnostic import obtener_preguntas_diagnostico

        with pytest.raises(ValueError):
            obtener_preguntas_diagnostico(cantidad=9)

        with pytest.raises(ValueError):
            obtener_preguntas_diagnostico(cantidad=16)

    def test_banco_tiene_100_por_competencia(self):
        from core.diagnostic import (
            VARIANTES_POR_COMPETENCIA,
            PREGUNTAS_BASE,
            BANCO_PREGUNTAS,
            contar_preguntas_por_competencia,
        )

        conteo = contar_preguntas_por_competencia(BANCO_PREGUNTAS)

        assert len(conteo) == len(PREGUNTAS_BASE)
        assert all(cantidad >= VARIANTES_POR_COMPETENCIA for cantidad in conteo.values())
        assert len(BANCO_PREGUNTAS) >= len(PREGUNTAS_BASE) * VARIANTES_POR_COMPETENCIA

    def test_variantes_semanticas_matematicas(self):
        from core.diagnostic import BANCO_PREGUNTAS

        variantes_mat = [q for q in BANCO_PREGUNTAS if q.id.startswith("MAT_1_V")][:12]
        enunciados = {q.enunciado for q in variantes_mat}

        assert len(enunciados) == len(variantes_mat)
        assert all("ecuación" in q.enunciado.lower() for q in variantes_mat)

    def test_diagnostico_inicial_sin_enunciados_repetidos(self):
        from core.diagnostic import obtener_preguntas_diagnostico

        preguntas = obtener_preguntas_diagnostico(cantidad=15, semilla=20260307)
        firmas = {f"{p['materia']}::{' '.join(p['enunciado'].strip().lower().split())}" for p in preguntas}

        assert len(firmas) == len(preguntas)

    def test_diagnostico_no_muestra_sufijo_escenario(self):
        from core.diagnostic import obtener_preguntas_diagnostico

        preguntas = obtener_preguntas_diagnostico(cantidad=15, semilla=20260309)

        assert all("(Escenario:" not in p["enunciado"] for p in preguntas)


class TestEvaluarDiagnostico:
    """Tests para evaluación y recomendaciones."""

    def test_calcula_puntaje_y_recomendaciones(self):
        from core.diagnostic import obtener_preguntas_diagnostico, evaluar_diagnostico, BANCO_PREGUNTAS

        preguntas = obtener_preguntas_diagnostico(cantidad=10, semilla=7)
        indice = {q.id: q for q in BANCO_PREGUNTAS}

        # Fuerza 5 correctas y 5 incorrectas para validar porcentaje y plan de refuerzo.
        respuestas = {}
        for i, pregunta in enumerate(preguntas):
            correcta = indice[pregunta["id"]].respuesta_correcta
            if i < 5:
                respuestas[pregunta["id"]] = correcta
            else:
                respuestas[pregunta["id"]] = "respuesta_incorrecta"

        resultado = evaluar_diagnostico(respuestas, preguntas)

        assert resultado["total_preguntas"] == 10
        assert resultado["aciertos_totales"] == 5
        assert resultado["porcentaje_total"] == 50.0
        assert len(resultado["resultados_por_materia"]) > 0
        assert len(resultado["recomendaciones"]) > 0


class TestSeguimientoSemanal:
    """Tests de personalización y seguimiento semanal."""

    def test_obtener_materia_prioritaria(self):
        from core.diagnostic import obtener_materia_prioritaria

        resultado = {
            "resultados_por_materia": [
                {"materia": "Matemáticas", "porcentaje": 70, "total": 2},
                {"materia": "Lectura Crítica", "porcentaje": 40, "total": 2},
            ]
        }

        materia = obtener_materia_prioritaria(resultado)

        assert materia == "Lectura Crítica"

    def test_genera_preguntas_recomendadas_por_tema(self):
        from core.diagnostic import generar_preguntas_recomendadas

        resultado = {
            "resultados_por_materia": [
                {
                    "materia": "Matemáticas",
                    "temas_reforzar": ["Álgebra básica", "Proporcionalidad"],
                }
            ]
        }

        preguntas = generar_preguntas_recomendadas(resultado, "Matemáticas", max_preguntas=2)

        assert len(preguntas) == 2
        assert "Álgebra" in preguntas[0] or "Proporcionalidad" in preguntas[1]

    def test_genera_plan_semanal(self):
        from core.diagnostic import generar_plan_semanal

        resultado = {
            "resultados_por_materia": [
                {"materia": "Física", "porcentaje": 30, "temas_reforzar": ["Movimiento uniforme"]},
                {"materia": "Inglés", "porcentaje": 60, "temas_reforzar": ["Vocabulary in context"]},
            ]
        }

        plan = generar_plan_semanal(resultado)
    hoy = datetime.now().date()
    fechas_esperadas = [(hoy + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

        assert len(plan) == 7
        assert all("dia" in bloque and "materia" in bloque for bloque in plan)
    assert [bloque["dia"] for bloque in plan] == fechas_esperadas

    def test_diagnostico_requiere_renovacion_cada_7_dias(self):
        from core.diagnostic import diagnostico_requiere_renovacion

        ahora = datetime.now(timezone.utc)
        hace_8_dias = (ahora - timedelta(days=8)).isoformat()
        hace_2_dias = (ahora - timedelta(days=2)).isoformat()

        assert diagnostico_requiere_renovacion(hace_8_dias, ahora=ahora) is True
        assert diagnostico_requiere_renovacion(hace_2_dias, ahora=ahora) is False

    def test_semilla_semanal_es_deterministica(self):
        from core.diagnostic import generar_semilla_diagnostico_semanal

        fecha = datetime(2026, 3, 7, tzinfo=timezone.utc)
        s1 = generar_semilla_diagnostico_semanal("est-1", fecha)
        s2 = generar_semilla_diagnostico_semanal("est-1", fecha)
        s3 = generar_semilla_diagnostico_semanal("est-2", fecha)

        assert s1 == s2
        assert s1 != s3

    def test_diagnostico_adaptativo_refuerza_y_explora(self):
        from core.diagnostic import obtener_preguntas_diagnostico_adaptativo, dificultad_objetivo_por_materia

        diagnostico_anterior = {
            "resultados_por_materia": [
                {
                    "materia": "Matemáticas",
                    "porcentaje": 40,
                    "temas_reforzar": ["Álgebra básica"],
                },
                {
                    "materia": "Inglés",
                    "porcentaje": 85,
                    "temas_reforzar": [],
                },
            ],
            "temas_evaluados": [
                {"materia": "Matemáticas", "tema": "Álgebra básica"},
                {"materia": "Inglés", "tema": "Reading comprehension"},
            ],
        }

        preguntas = obtener_preguntas_diagnostico_adaptativo(
            cantidad=10,
            diagnostico_anterior=diagnostico_anterior,
            semilla=1234,
        )

        assert len(preguntas) == 10

        # Debe incluir al menos una pregunta de refuerzo.
        assert any(p["materia"] == "Matemáticas" or p["tema"] == "Álgebra básica" for p in preguntas)

        # Debe incluir al menos un tema exploratorio no evaluado previamente.
        temas_previos = {(t["materia"], t["tema"]) for t in diagnostico_anterior["temas_evaluados"]}
        assert any((p["materia"], p["tema"]) not in temas_previos for p in preguntas)

        # Dificultad objetivo por materia según rendimiento previo.
        assert dificultad_objetivo_por_materia(diagnostico_anterior, "Matemáticas") == "basico"
        assert dificultad_objetivo_por_materia(diagnostico_anterior, "Inglés") == "avanzado"

        # Al menos una pregunta de refuerzo en Matemáticas debería llegar en básico.
        assert any(
            p["materia"] == "Matemáticas" and p.get("dificultad") == "basico"
            for p in preguntas
        )

    def test_diagnostico_adaptativo_sin_enunciados_repetidos(self):
        from core.diagnostic import obtener_preguntas_diagnostico_adaptativo

        diagnostico_anterior = {
            "resultados_por_materia": [
                {"materia": "Matemáticas", "porcentaje": 35, "temas_reforzar": ["Álgebra básica", "Proporcionalidad"]},
                {"materia": "Física", "porcentaje": 42, "temas_reforzar": ["Movimiento uniforme"]},
                {"materia": "Inglés", "porcentaje": 80, "temas_reforzar": []},
            ],
            "temas_evaluados": [
                {"materia": "Matemáticas", "tema": "Álgebra básica"},
                {"materia": "Física", "tema": "Movimiento uniforme"},
            ],
        }

        preguntas = obtener_preguntas_diagnostico_adaptativo(
            cantidad=12,
            diagnostico_anterior=diagnostico_anterior,
            semilla=20260308,
        )

        firmas = {f"{p['materia']}::{' '.join(p['enunciado'].strip().lower().split())}" for p in preguntas}
        assert len(firmas) == len(preguntas)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
