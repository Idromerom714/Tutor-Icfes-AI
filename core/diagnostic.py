# diagnostico.py
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
import hashlib

# El cliente Supabase se importa desde database.py para no duplicar inicialización
from core.database import supabase_admin as sb


# ─────────────────────────────────────────────────────────────────────────────
# CONSULTAS AL BANCO DE PREGUNTAS (Supabase)
# ─────────────────────────────────────────────────────────────────────────────

def _filas_a_dicts(filas: list) -> List[Dict]:
    """Convierte filas de Supabase a lista de dicts con opciones como lista."""
    resultado = []
    for f in filas:
        resultado.append({
            "id":                 str(f["id"]),
            "materia":            f["materia"],
            "tema":               f["tema"],
            "subtema":            f["subtema"],
            "competencia":        f["competencia"],
            "dificultad":         f["dificultad"],
            "enunciado":          f["enunciado"],
            "opciones":           [f["opcion_a"], f["opcion_b"], f["opcion_c"], f["opcion_d"]],
            "respuesta_correcta": f["respuesta_correcta"],
            "explicacion":        f.get("explicacion", ""),
        })
    return resultado


def _sin_respuesta(preguntas: List[Dict]) -> List[Dict]:
    """Elimina respuesta_correcta y explicacion antes de enviar al frontend."""
    return [
        {k: v for k, v in p.items() if k not in ("respuesta_correcta", "explicacion")}
        for p in preguntas
    ]


def obtener_preguntas_diagnostico(
    cantidad: int = 12,
    estudiante_id: Optional[str] = None,
    incluir_respuestas: bool = False,
) -> List[Dict]:
    """
    Diagnóstico inicial: selecciona preguntas del banco con cobertura balanceada
    por materia y nivel intermedio. Excluye preguntas ya vistas por el estudiante.
    """
    if not (10 <= cantidad <= 15):
        raise ValueError("La cantidad debe estar entre 10 y 15.")

    ids_vistos = _obtener_ids_vistos(estudiante_id) if estudiante_id else set()

    materias = [
        "Matemáticas",
        "Lectura Crítica",
        "Sociales y Ciudadanas",
        "Ciencias Naturales",
        "Inglés",
    ]

    seleccionadas: List[Dict] = []
    por_materia = cantidad // len(materias)
    resto = cantidad % len(materias)

    for i, materia in enumerate(materias):
        cupo = por_materia + (1 if i < resto else 0)
        query = (
            sb.table("banco_preguntas")
            .select("*")
            .eq("materia", materia)
            .eq("dificultad", "intermedio")
        )
        if ids_vistos:
            query = query.not_.in_("id", list(ids_vistos))

        filas = query.limit(cupo * 5).execute().data  # traer más y samplear
        import random
        sample = random.sample(filas, min(cupo, len(filas))) if filas else []
        seleccionadas.extend(_filas_a_dicts(sample))

    import random
    random.shuffle(seleccionadas)
    preguntas = seleccionadas[:cantidad]
    return preguntas if incluir_respuestas else _sin_respuesta(preguntas)


def obtener_preguntas_diagnostico_adaptativo(
    cantidad: int = 10,
    estudiante_id: Optional[str] = None,
    diagnostico_anterior_id: Optional[str] = None,
    incluir_respuestas: bool = False,
) -> List[Dict]:
    """
    Diagnóstico adaptativo:
    - 60% preguntas de subtemas donde el estudiante falló antes (refuerzo)
    - 40% preguntas de subtemas nuevos (exploración)
    - Nunca repite preguntas ya vistas
    """
    if not estudiante_id or not diagnostico_anterior_id:
        return obtener_preguntas_diagnostico(
            cantidad=cantidad,
            estudiante_id=estudiante_id,
            incluir_respuestas=incluir_respuestas,
        )

    import random

    ids_vistos = _obtener_ids_vistos(estudiante_id)
    subtemas_fallados = _obtener_subtemas_fallados(estudiante_id)
    dificultad_obj = _calcular_dificultad_objetivo(estudiante_id, diagnostico_anterior_id)

    cupo_refuerzo   = max(1, int(cantidad * 0.6))
    cupo_exploracion = max(1, int(cantidad * 0.4))
    seleccionadas: List[Dict] = []

    # ── Refuerzo: subtemas donde falló ───────────────────────────────────────
    if subtemas_fallados:
        query = (
            sb.table("banco_preguntas")
            .select("*")
            .in_("subtema", list(subtemas_fallados))
            .eq("dificultad", dificultad_obj)
        )
        if ids_vistos:
            query = query.not_.in_("id", list(ids_vistos))

        filas = query.limit(cupo_refuerzo * 5).execute().data or []
        sample = random.sample(filas, min(cupo_refuerzo, len(filas)))
        seleccionadas.extend(_filas_a_dicts(sample))

    ids_seleccionados = {p["id"] for p in seleccionadas}

    # ── Exploración: subtemas no fallados y no vistos ─────────────────────────
    query_exp = (
        sb.table("banco_preguntas")
        .select("*")
        .eq("dificultad", dificultad_obj)
        .not_.in_("subtema", list(subtemas_fallados) if subtemas_fallados else ["__none__"])
        .not_.in_("id", list(ids_vistos | ids_seleccionados))
    )
    filas_exp = query_exp.limit(cupo_exploracion * 5).execute().data or []
    sample_exp = random.sample(filas_exp, min(cupo_exploracion, len(filas_exp)))
    seleccionadas.extend(_filas_a_dicts(sample_exp))

    # ── Relleno si no alcanzó ────────────────────────────────────────────────
    faltantes = cantidad - len(seleccionadas)
    if faltantes > 0:
        ids_usados = {p["id"] for p in seleccionadas}
        filas_extra = (
            sb.table("banco_preguntas")
            .select("*")
            .not_.in_("id", list(ids_vistos | ids_usados))
            .limit(faltantes * 3)
            .execute()
            .data or []
        )
        sample_extra = random.sample(filas_extra, min(faltantes, len(filas_extra)))
        seleccionadas.extend(_filas_a_dicts(sample_extra))

    random.shuffle(seleccionadas)
    preguntas = seleccionadas[:cantidad]
    return preguntas if incluir_respuestas else _sin_respuesta(preguntas)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS DE CONSULTA
# ─────────────────────────────────────────────────────────────────────────────

def _obtener_ids_vistos(estudiante_id: str) -> set[str]:
    """IDs de preguntas que el estudiante ya respondió en cualquier diagnóstico."""
    filas = (
        sb.table("respuestas_diagnostico")
        .select("pregunta_id")
        .eq("estudiante_id", estudiante_id)
        .execute()
        .data or []
    )
    return {str(f["pregunta_id"]) for f in filas}


def _obtener_subtemas_fallados(estudiante_id: str) -> set[str]:
    """
    Subtemas donde el estudiante falló en diagnósticos anteriores.
    Hace join manual: respuestas_diagnostico → banco_preguntas.
    """
    filas = (
        sb.table("respuestas_diagnostico")
        .select("pregunta_id")
        .eq("estudiante_id", estudiante_id)
        .eq("es_correcta", False)
        .execute()
        .data or []
    )
    if not filas:
        return set()

    ids_fallados = [str(f["pregunta_id"]) for f in filas]
    preguntas = (
        sb.table("banco_preguntas")
        .select("subtema")
        .in_("id", ids_fallados)
        .execute()
        .data or []
    )
    return {p["subtema"] for p in preguntas}


def _calcular_dificultad_objetivo(
    estudiante_id: str,
    diagnostico_id: str,
) -> str:
    """Determina la dificultad para el siguiente diagnóstico según el puntaje anterior."""
    diag = (
        sb.table("diagnosticos")
        .select("porcentaje_total")
        .eq("id", diagnostico_id)
        .eq("estudiante_id", estudiante_id)
        .single()
        .execute()
        .data
    )
    if not diag:
        return "intermedio"
    puntaje = float(diag.get("porcentaje_total", 50))
    if puntaje < 45:
        return "basico"
    if puntaje < 75:
        return "intermedio"
    return "avanzado"


# ─────────────────────────────────────────────────────────────────────────────
# EVALUACIÓN Y PERSISTENCIA
# ─────────────────────────────────────────────────────────────────────────────

def evaluar_diagnostico(
    respuestas_usuario: Dict[str, str],
    preguntas_presentadas: List[Dict],
) -> Dict:
    """
    Evalúa las respuestas del estudiante.

    `preguntas_presentadas` debe incluir 'respuesta_correcta' —
    se obtiene llamando a _filas_a_dicts() internamente antes de _sin_respuesta().
    En la práctica, app.py guarda las preguntas completas en session_state
    y las pasa aquí para evaluación.
    """
    aciertos = 0
    total = len(preguntas_presentadas)
    por_materia: Dict[str, Dict] = {}
    por_dificultad: Dict[str, Dict] = {}
    temas_evaluados = set()

    for p in preguntas_presentadas:
        pid           = str(p["id"])
        correcta      = p["respuesta_correcta"]
        respuesta     = respuestas_usuario.get(pid, "")
        es_correcta   = respuesta == correcta
        materia       = p["materia"]
        subtema       = p["subtema"]
        dificultad    = p.get("dificultad", "intermedio")

        if es_correcta:
            aciertos += 1

        temas_evaluados.add((materia, subtema))

        if materia not in por_materia:
            por_materia[materia] = {"aciertos": 0, "total": 0, "subtemas_reforzar": []}
        por_materia[materia]["total"] += 1
        if es_correcta:
            por_materia[materia]["aciertos"] += 1
        else:
            por_materia[materia]["subtemas_reforzar"].append(subtema)

        if dificultad not in por_dificultad:
            por_dificultad[dificultad] = {"aciertos": 0, "total": 0}
        por_dificultad[dificultad]["total"] += 1
        if es_correcta:
            por_dificultad[dificultad]["aciertos"] += 1

    porcentaje = round((aciertos / total) * 100, 2) if total else 0

    resultados_por_materia = []
    for materia, datos in por_materia.items():
        t = datos["total"]
        a = datos["aciertos"]
        resultados_por_materia.append({
            "materia":           materia,
            "aciertos":          a,
            "total":             t,
            "porcentaje":        round((a / t) * 100, 2) if t else 0,
            "subtemas_reforzar": sorted(set(datos["subtemas_reforzar"])),
        })

    return {
        "aciertos_totales":      aciertos,
        "total_preguntas":       total,
        "porcentaje_total":      porcentaje,
        "resultados_por_materia": sorted(resultados_por_materia, key=lambda x: x["materia"]),
        "resultados_por_dificultad": por_dificultad,
        "temas_evaluados": [
            {"materia": m, "subtema": s}
            for (m, s) in sorted(temas_evaluados)
        ],
        "recomendaciones": generar_recomendaciones_refuerzo(resultados_por_materia),
    }


def guardar_diagnostico(
    estudiante_id: str,
    preguntas_ids: List[str],
    resultado: Dict,
) -> Optional[str]:
    """
    Persiste el diagnóstico en Supabase y retorna el ID generado.
    Llamar DESPUÉS de evaluar_diagnostico().
    """
    fila = {
        "estudiante_id":        estudiante_id,
        "preguntas_ids":        preguntas_ids,
        "porcentaje_total":     resultado["porcentaje_total"],
        "resultados_por_materia": resultado["resultados_por_materia"],
    }
    resp = sb.table("diagnosticos").insert(fila).execute()
    if resp.data:
        return str(resp.data[0]["id"])
    return None


def guardar_respuestas(
    diagnostico_id: str,
    estudiante_id: str,
    preguntas_presentadas: List[Dict],
    respuestas_usuario: Dict[str, str],
) -> None:
    """
    Persiste cada respuesta individual en respuestas_diagnostico.
    Permite reconstruir qué preguntas vio el estudiante y en cuáles falló.
    """
    filas = []
    for p in preguntas_presentadas:
        pid       = str(p["id"])
        correcta  = p["respuesta_correcta"]
        respuesta = respuestas_usuario.get(pid, "")
        filas.append({
            "diagnostico_id": diagnostico_id,
            "estudiante_id":  estudiante_id,
            "pregunta_id":    pid,
            "respuesta_dada": respuesta,
            "es_correcta":    respuesta == correcta,
        })
    if filas:
        sb.table("respuestas_diagnostico").insert(filas).execute()


def obtener_ultimo_diagnostico(estudiante_id: str) -> Optional[Dict]:
    """Retorna el diagnóstico más reciente del estudiante o None."""
    filas = (
        sb.table("diagnosticos")
        .select("*")
        .eq("estudiante_id", estudiante_id)
        .order("fecha", desc=True)
        .limit(1)
        .execute()
        .data
    )
    return filas[0] if filas else None


# ─────────────────────────────────────────────────────────────────────────────
# LÓGICA DE NEGOCIO (sin cambios respecto al original)
# ─────────────────────────────────────────────────────────────────────────────

def generar_recomendaciones_refuerzo(resultados_por_materia: List[Dict]) -> List[str]:
    recomendaciones = []
    for item in resultados_por_materia:
        materia    = item["materia"]
        porcentaje = float(item["porcentaje"])
        subtemas   = item.get("subtemas_reforzar", [])

        if porcentaje >= 80:
            recomendaciones.append(
                f"{materia}: buen nivel. Sube dificultad con preguntas tipo caso."
            )
        elif porcentaje >= 50:
            recomendaciones.append(
                f"{materia}: nivel intermedio. Refuerza {', '.join(subtemas[:2])} con práctica guiada."
            )
        else:
            recomendaciones.append(
                f"{materia}: prioridad alta. Trabaja base conceptual en {', '.join(subtemas[:2])}."
            )
    return recomendaciones or ["No se generaron recomendaciones. Repite el diagnóstico."]


def obtener_materia_prioritaria(
    diagnostico_resultado: Optional[Dict],
    default: str = "Matemáticas",
) -> str:
    if not diagnostico_resultado:
        return default
    resultados = diagnostico_resultado.get("resultados_por_materia", [])
    if not resultados:
        return default
    ordenadas = sorted(
        resultados,
        key=lambda x: (float(x.get("porcentaje", 0)), -int(x.get("total", 0)))
    )
    return ordenadas[0].get("materia", default)


def generar_preguntas_recomendadas(
    diagnostico_resultado: Optional[Dict],
    materia_actual: str,
    max_preguntas: int = 3,
) -> List[str]:
    if not diagnostico_resultado:
        return [
            "Explícame cómo identificar el tema central de una pregunta tipo ICFES.",
            "Hazme una pregunta diagnóstica de nivel intermedio para empezar.",
            "Quiero practicar con una pregunta guiada paso a paso.",
        ][:max_preguntas]

    resultados = diagnostico_resultado.get("resultados_por_materia", [])
    datos = next((m for m in resultados if m.get("materia") == materia_actual), None)

    if not datos:
        return [
            f"Hazme una pregunta tipo ICFES de {materia_actual} y guíame con método socrático.",
            f"Evalúa mi nivel actual en {materia_actual} con un ejercicio breve.",
        ][:max_preguntas]

    subtemas = datos.get("subtemas_reforzar", [])
    if not subtemas:
        return [
            f"Quiero un reto de mayor nivel en {materia_actual}.",
            f"Propón una pregunta tipo caso en {materia_actual}.",
        ][:max_preguntas]

    return [
        f"Ayúdame a reforzar '{s}' en {materia_actual} con una pregunta tipo ICFES."
        for s in subtemas[:max_preguntas]
    ]


def generar_plan_semanal(diagnostico_resultado: Optional[Dict]) -> List[Dict[str, str]]:
    hoy  = datetime.now().date()
    dias = [(hoy + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

    if not diagnostico_resultado:
        return [
            {"dia": dias[0], "materia": "General",
             "objetivo": "Realizar diagnóstico inicial",
             "actividad": "Completar test para personalizar el plan."},
            {"dia": dias[1], "materia": "General",
             "objetivo": "Sesión base",
             "actividad": "Resolver 2 preguntas guiadas por el tutor."},
        ]

    resultados = sorted(
        diagnostico_resultado.get("resultados_por_materia", []),
        key=lambda x: float(x.get("porcentaje", 0)),
    )
    if not resultados:
        return []

    materias_ciclo = [r.get("materia", "General") for r in resultados]
    plan = []
    for i, dia in enumerate(dias):
        materia = materias_ciclo[i % len(materias_ciclo)]
        datos   = next((r for r in resultados if r.get("materia") == materia), {})
        subtemas = datos.get("subtemas_reforzar", [])
        objetivo = subtemas[0] if subtemas else "resolución de preguntas tipo caso"
        plan.append({
            "dia":       dia,
            "materia":   materia,
            "objetivo":  f"Fortalecer {objetivo}",
            "actividad": f"Resolver 3 preguntas guiadas de {materia} y cerrar con autoexplicación.",
        })
    return plan


def diagnostico_requiere_renovacion(
    creado_el_iso: Optional[str],
    ahora: Optional[datetime] = None,
    dias_vigencia: int = 7,
) -> bool:
    if not creado_el_iso:
        return True
    try:
        fecha = datetime.fromisoformat(creado_el_iso.replace("Z", "+00:00"))
    except ValueError:
        return True
    if fecha.tzinfo is None:
        fecha = fecha.replace(tzinfo=timezone.utc)
    ref = ahora or datetime.now(timezone.utc)
    return ref >= (fecha + timedelta(days=dias_vigencia))