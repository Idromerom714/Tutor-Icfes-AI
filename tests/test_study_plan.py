"""Tests para plan de estudio personalizado basado en diagnóstico."""


def test_plan_estudio_personalizado_prioriza_materias_debiles():
    from core.diagnostic import generar_plan_estudio_personalizado

    diagnostico = {
        "porcentaje_total": 52.0,
        "resultados_por_materia": [
            {
                "materia": "Matemáticas",
                "porcentaje": 35.0,
                "subtemas_reforzar": ["Álgebra básica", "Proporcionalidad"],
            },
            {
                "materia": "Inglés",
                "porcentaje": 78.0,
                "subtemas_reforzar": [],
            },
        ],
    }

    plan = generar_plan_estudio_personalizado(diagnostico, semanas=4)

    assert plan["duracion_semanas"] == 4
    assert len(plan["modulos"]) == 2

    primer_modulo = plan["modulos"][0]
    assert primer_modulo["materia"] == "Matemáticas"
    assert primer_modulo["prioridad"] == "alta"
    assert "Álgebra básica" in primer_modulo["falencias"]
    assert len(primer_modulo["plan_semana"]) == 4


def test_plan_estudio_personalizado_acepta_esquema_antiguo_temas_reforzar():
    from core.diagnostic import generar_plan_estudio_personalizado

    diagnostico = {
        "porcentaje_total": 60.0,
        "resultados_por_materia": [
            {
                "materia": "Lectura Crítica",
                "porcentaje": 48.0,
                "temas_reforzar": ["Inferencias", "Propósito comunicativo"],
            }
        ],
    }

    plan = generar_plan_estudio_personalizado(diagnostico, semanas=3)

    modulo = plan["modulos"][0]
    assert modulo["prioridad"] == "media"
    assert modulo["falencias"][0] == "Inferencias"
    assert len(modulo["plan_semana"]) == 3


def test_funciones_existentes_soportan_temas_reforzar_en_compatibilidad():
    from core.diagnostic import generar_plan_semanal, generar_preguntas_recomendadas

    diagnostico = {
        "resultados_por_materia": [
            {
                "materia": "Ciencias Naturales",
                "porcentaje": 42.0,
                "temas_reforzar": ["Reacciones químicas"],
            }
        ]
    }

    plan_semanal = generar_plan_semanal(diagnostico)
    sugerencias = generar_preguntas_recomendadas(diagnostico, "Ciencias Naturales", max_preguntas=1)

    assert len(plan_semanal) == 7
    assert "Reacciones químicas" in plan_semanal[0]["objetivo"]
    assert len(sugerencias) == 1
    assert "Reacciones químicas" in sugerencias[0]
