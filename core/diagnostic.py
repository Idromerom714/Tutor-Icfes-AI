from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
from random import Random
from typing import Dict, List, Optional


@dataclass(frozen=True)
class PreguntaDiagnostico:
    """Representa una pregunta de opción múltiple para diagnóstico inicial."""

    id: str
    materia: str
    tema: str
    enunciado: str
    opciones: List[str]
    respuesta_correcta: str
    dificultad: str = "intermedio"


VARIANTES_POR_COMPETENCIA = 100


PREGUNTAS_BASE: List[PreguntaDiagnostico] = [
    PreguntaDiagnostico(
        id="MAT_1",
        materia="Matemáticas",
        tema="Álgebra básica",
        enunciado="Si 2x + 5 = 17, ¿cuál es el valor de x?",
        opciones=["4", "5", "6", "7"],
        respuesta_correcta="6",
    ),
    PreguntaDiagnostico(
        id="MAT_2",
        materia="Matemáticas",
        tema="Proporcionalidad",
        enunciado="Si 3 cuadernos cuestan $12.000, ¿cuánto cuestan 5 cuadernos al mismo precio unitario?",
        opciones=["$16.000", "$18.000", "$20.000", "$22.000"],
        respuesta_correcta="$20.000",
    ),
    PreguntaDiagnostico(
        id="LC_1",
        materia="Lectura Crítica",
        tema="Idea principal",
        enunciado="En un texto argumentativo, la tesis corresponde a:",
        opciones=[
            "El ejemplo más llamativo",
            "La postura central del autor",
            "La conclusión del lector",
            "Una cita textual aislada",
        ],
        respuesta_correcta="La postura central del autor",
    ),
    PreguntaDiagnostico(
        id="LC_2",
        materia="Lectura Crítica",
        tema="Inferencias",
        enunciado="Si un texto afirma que una medida redujo el tráfico, una inferencia válida sería:",
        opciones=[
            "Todos dejaron de usar carro",
            "Hubo cambios en la movilidad de la ciudad",
            "La medida no tuvo ningún efecto",
            "No existía tráfico antes",
        ],
        respuesta_correcta="Hubo cambios en la movilidad de la ciudad",
    ),
    PreguntaDiagnostico(
        id="SOC_1",
        materia="Sociales",
        tema="Constitución y ciudadanía",
        enunciado="La Constitución Política de Colombia de 1991 se caracteriza por:",
        opciones=[
            "Eliminar todos los derechos fundamentales",
            "Fortalecer la participación ciudadana",
            "Prohibir la descentralización",
            "Sustituir la división de poderes",
        ],
        respuesta_correcta="Fortalecer la participación ciudadana",
    ),
    PreguntaDiagnostico(
        id="SOC_2",
        materia="Sociales",
        tema="Interpretación de fuentes",
        enunciado="Al comparar dos fuentes históricas sobre un mismo hecho, lo más adecuado es:",
        opciones=[
            "Escoger la más antigua siempre",
            "Contrastar contexto, autor e intención",
            "Creer únicamente la más larga",
            "Descartar cualquier diferencia",
        ],
        respuesta_correcta="Contrastar contexto, autor e intención",
    ),
    PreguntaDiagnostico(
        id="CN_1",
        materia="Ciencias Naturales",
        tema="Método científico",
        enunciado="Después de plantear una hipótesis, el siguiente paso usual es:",
        opciones=[
            "Publicar resultados sin probar",
            "Diseñar y ejecutar un experimento",
            "Cambiar la hipótesis al azar",
            "Ignorar variables",
        ],
        respuesta_correcta="Diseñar y ejecutar un experimento",
    ),
    PreguntaDiagnostico(
        id="CN_2",
        materia="Ciencias Naturales",
        tema="Ecología",
        enunciado="En una cadena alimentaria, los productores son organismos que:",
        opciones=[
            "Obtienen energía de otros seres vivos",
            "Fabrican su alimento, por ejemplo por fotosíntesis",
            "Solo descomponen materia orgánica",
            "No intercambian energía con el entorno",
        ],
        respuesta_correcta="Fabrican su alimento, por ejemplo por fotosíntesis",
    ),
    PreguntaDiagnostico(
        id="FIS_1",
        materia="Física",
        tema="Movimiento uniforme",
        enunciado="Si un objeto recorre 120 m en 10 s, su rapidez media es:",
        opciones=["10 m/s", "12 m/s", "14 m/s", "1200 m/s"],
        respuesta_correcta="12 m/s",
    ),
    PreguntaDiagnostico(
        id="FIS_2",
        materia="Física",
        tema="Fuerza y leyes de Newton",
        enunciado="Según la segunda ley de Newton, si la masa es constante y aumenta la fuerza neta:",
        opciones=[
            "La aceleración disminuye",
            "La aceleración aumenta",
            "La velocidad siempre es cero",
            "No cambia nada",
        ],
        respuesta_correcta="La aceleración aumenta",
    ),
    PreguntaDiagnostico(
        id="ING_1",
        materia="Inglés",
        tema="Reading comprehension",
        enunciado="Choose the correct option: 'She ___ to school every day.'",
        opciones=["go", "goes", "going", "gone"],
        respuesta_correcta="goes",
    ),
    PreguntaDiagnostico(
        id="ING_2",
        materia="Inglés",
        tema="Vocabulary in context",
        enunciado="In the sentence 'The room was tiny', the word 'tiny' means:",
        opciones=["very big", "very small", "very old", "very bright"],
        respuesta_correcta="very small",
    ),
]


def _dificultad_por_indice(indice: int, total_variantes: int) -> str:
    """Segmenta variantes en tres niveles de dificultad."""
    tercio = max(1, total_variantes // 3)
    if indice <= tercio:
        return "basico"
    if indice <= (2 * tercio):
        return "intermedio"
    return "avanzado"


def _puntaje_a_dificultad(puntaje: float) -> str:
    """Mapea puntaje a dificultad objetivo para la siguiente evaluación."""
    if puntaje < 45:
        return "basico"
    if puntaje < 75:
        return "intermedio"
    return "avanzado"


def dificultad_objetivo_por_materia(
    diagnostico_anterior: Optional[Dict[str, object]],
    materia: Optional[str] = None,
) -> str:
    """Define el nivel recomendado para la próxima evaluación por materia o global."""
    if not diagnostico_anterior:
        return "intermedio"

    if materia:
        for r in diagnostico_anterior.get("resultados_por_materia", []):
            if r.get("materia") == materia:
                return _puntaje_a_dificultad(float(r.get("porcentaje", 0)))

    return _puntaje_a_dificultad(float(diagnostico_anterior.get("porcentaje_total", 0)))


def _generar_variantes_competencia(
    pregunta_base: PreguntaDiagnostico,
    total_variantes: int = VARIANTES_POR_COMPETENCIA,
) -> List[PreguntaDiagnostico]:
    """Expande una competencia en múltiples variantes con cambios semánticos reales."""

    def rng_variant(indice: int) -> Random:
        key = f"{pregunta_base.id}-{indice}".encode("utf-8")
        return Random(int(hashlib.sha256(key).hexdigest()[:8], 16))

    def mezclar_opciones(opciones: List[str], correcta: str, rnd: Random) -> tuple[List[str], str]:
        opciones_copia = list(opciones)
        rnd.shuffle(opciones_copia)
        return opciones_copia, correcta

    def generar_matematicas_algebra(indice: int) -> tuple[str, List[str], str]:
        rnd = rng_variant(indice)
        x = rnd.randint(2, 18)
        a = rnd.randint(2, 9)
        b = rnd.randint(-8, 12)
        c = a * x + b
        enunciado = (
            f"En un simulacro ICFES, resuelve la ecuación {a}x "
            f"{'+' if b >= 0 else '-'} {abs(b)} = {c}. ¿Cuál es x?"
        )
        distractores = sorted({x - 2, x - 1, x + 1, x + 2} - {x})
        opciones = [str(x)] + [str(v) for v in distractores[:3]]
        opciones, correcta = mezclar_opciones(opciones, str(x), rnd)
        return enunciado, opciones, correcta

    def generar_matematicas_proporcionalidad(indice: int) -> tuple[str, List[str], str]:
        rnd = rng_variant(indice)
        cantidad_base = rnd.randint(2, 6)
        precio_unitario = rnd.choice([1500, 2000, 2500, 3000, 4000])
        cantidad_objetivo = rnd.randint(7, 12)
        costo_base = cantidad_base * precio_unitario
        costo_objetivo = cantidad_objetivo * precio_unitario
        enunciado = (
            f"Una papelería vende {cantidad_base} cuadernos por ${costo_base:,.0f}. "
            f"Si se mantiene el mismo precio unitario, ¿cuánto valen {cantidad_objetivo} cuadernos?"
        ).replace(",", ".")
        opciones = [
            f"${costo_objetivo:,.0f}".replace(",", "."),
            f"${(costo_objetivo + precio_unitario):,.0f}".replace(",", "."),
            f"${(costo_objetivo - precio_unitario):,.0f}".replace(",", "."),
            f"${(costo_objetivo + 2 * precio_unitario):,.0f}".replace(",", "."),
        ]
        correcta = opciones[0]
        opciones, correcta = mezclar_opciones(opciones, correcta, rnd)
        return enunciado, opciones, correcta

    def generar_fisica_rapidez(indice: int) -> tuple[str, List[str], str]:
        rnd = rng_variant(indice)
        rapidez = rnd.randint(8, 22)
        tiempo = rnd.randint(5, 15)
        distancia = rapidez * tiempo
        enunciado = (
            f"Un móvil recorre {distancia} m en {tiempo} s con rapidez constante. "
            "¿Cuál es su rapidez media?"
        )
        opciones = [f"{rapidez} m/s", f"{rapidez - 2} m/s", f"{rapidez + 2} m/s", f"{rapidez * 10} m/s"]
        correcta = opciones[0]
        opciones, correcta = mezclar_opciones(opciones, correcta, rnd)
        return enunciado, opciones, correcta

    def generar_ingles_gramatica(indice: int) -> tuple[str, List[str], str]:
        rnd = rng_variant(indice)
        casos = [
            ("She", "study", "studies"),
            ("He", "play", "plays"),
            ("My brother", "watch", "watches"),
            ("The teacher", "go", "goes"),
            ("Ana", "do", "does"),
        ]
        sujeto, verbo_base, correcta = casos[indice % len(casos)]
        complemento = rnd.choice(["every day", "at night", "on Mondays", "before class", "after lunch"])
        enunciado = f"Choose the correct option: '{sujeto} ___ math {complemento}.'"
        opciones = [correcta, verbo_base, f"{verbo_base}ing", f"{verbo_base}ed"]
        opciones, correcta = mezclar_opciones(opciones, correcta, rnd)
        return enunciado, opciones, correcta

    def generar_ingles_vocabulario(indice: int) -> tuple[str, List[str], str]:
        rnd = rng_variant(indice)
        casos = [
            ("tiny", "very small", ["very big", "very old", "very bright"]),
            ("huge", "very big", ["very small", "very slow", "very noisy"]),
            ("quick", "very fast", ["very late", "very weak", "very cold"]),
            ("ancient", "very old", ["very new", "very short", "very dark"]),
            ("calm", "peaceful", ["angry", "confusing", "expensive"]),
        ]
        palabra, correcta, distractores = casos[indice % len(casos)]
        enunciado = f"In the sentence 'The room looked {palabra}', the word '{palabra}' means:"
        opciones = [correcta] + distractores
        opciones, correcta = mezclar_opciones(opciones, correcta, rnd)
        return enunciado, opciones, correcta

    def generar_contextual(indice: int) -> tuple[str, List[str], str]:
        rnd = rng_variant(indice)
        grados = ["grado 9", "grado 10", "grado 11"]
        contextos = [
            "en una guía de preparación",
            "durante un simulacro institucional",
            "en una sesión de repaso",
            "al analizar un caso aplicado",
            "en una actividad de aula",
        ]
        habilidades = [
            "identificación de idea central",
            "inferencia de información implícita",
            "análisis crítico de opciones",
            "interpretación del contexto",
            "verificación de la respuesta más sólida",
        ]

        grado = grados[indice % len(grados)]
        contexto = contextos[(indice // len(grados)) % len(contextos)]
        habilidad = habilidades[(indice // (len(grados) * len(contextos))) % len(habilidades)]
        enunciado = (
            f"{pregunta_base.enunciado} "
            f"(Escenario: {grado}, {contexto}; foco: {habilidad})."
        )
        opciones, correcta = mezclar_opciones(pregunta_base.opciones, pregunta_base.respuesta_correcta, rnd)
        return enunciado, opciones, correcta

    variantes = []
    for i in range(total_variantes):
        idx = i + 1
        dificultad = _dificultad_por_indice(idx, total_variantes)
        if pregunta_base.id == "MAT_1":
            enunciado, opciones, correcta = generar_matematicas_algebra(idx)
        elif pregunta_base.id == "MAT_2":
            enunciado, opciones, correcta = generar_matematicas_proporcionalidad(idx)
        elif pregunta_base.id == "FIS_1":
            enunciado, opciones, correcta = generar_fisica_rapidez(idx)
        elif pregunta_base.id == "ING_1":
            enunciado, opciones, correcta = generar_ingles_gramatica(idx)
        elif pregunta_base.id == "ING_2":
            enunciado, opciones, correcta = generar_ingles_vocabulario(idx)
        else:
            enunciado, opciones, correcta = generar_contextual(idx)

        variantes.append(
            PreguntaDiagnostico(
                id=f"{pregunta_base.id}_V{idx:03d}",
                materia=pregunta_base.materia,
                tema=pregunta_base.tema,
                enunciado=enunciado,
                opciones=opciones,
                respuesta_correcta=correcta,
                dificultad=dificultad,
            )
        )

    return variantes


def construir_banco_preguntas(
    preguntas_base: List[PreguntaDiagnostico] = PREGUNTAS_BASE,
    variantes_por_competencia: int = VARIANTES_POR_COMPETENCIA,
) -> List[PreguntaDiagnostico]:
    """Construye banco escalado de preguntas (100+ por competencia)."""
    banco = []
    for pregunta_base in preguntas_base:
        banco.extend(_generar_variantes_competencia(pregunta_base, variantes_por_competencia))
    return banco


def contar_preguntas_por_competencia(
    banco: Optional[List[PreguntaDiagnostico]] = None,
) -> Dict[str, int]:
    """Retorna conteo por competencia (materia+tema)."""
    objetivo = banco or BANCO_PREGUNTAS
    conteo: Dict[str, int] = {}
    for q in objetivo:
        competencia = f"{q.materia}::{q.tema}"
        conteo[competencia] = conteo.get(competencia, 0) + 1
    return conteo


BANCO_PREGUNTAS: List[PreguntaDiagnostico] = construir_banco_preguntas()


def _pregunta_a_dict(q: PreguntaDiagnostico) -> Dict[str, object]:
    return {
        "id": q.id,
        "materia": q.materia,
        "tema": q.tema,
        "dificultad": q.dificultad,
        "enunciado": q.enunciado,
        "opciones": q.opciones,
    }


def _sample_unicos(rng: Random, fuente: List[PreguntaDiagnostico], cantidad: int) -> List[PreguntaDiagnostico]:
    if cantidad <= 0 or not fuente:
        return []
    if cantidad >= len(fuente):
        return list(fuente)
    return rng.sample(fuente, cantidad)


def generar_semilla_diagnostico_semanal(estudiante_id: Optional[str], fecha_referencia: Optional[datetime] = None) -> int:
    """Genera semilla estable por estudiante y semana ISO para diagnósticos reproducibles."""
    ref = fecha_referencia or datetime.now(timezone.utc)
    iso_year, iso_week, _ = ref.isocalendar()
    identidad = str(estudiante_id or "anon")
    base = f"{identidad}-{iso_year}-{iso_week}".encode("utf-8")
    digest = hashlib.sha256(base).hexdigest()
    return int(digest[:8], 16)


def obtener_preguntas_diagnostico(cantidad: int = 12, semilla: int | None = None) -> List[Dict[str, object]]:
    """Retorna preguntas para mostrar en UI sin exponer la respuesta correcta."""
    if cantidad < 10 or cantidad > 15:
        raise ValueError("La cantidad de preguntas debe estar entre 10 y 15.")
    if cantidad > len(BANCO_PREGUNTAS):
        raise ValueError("No hay suficientes preguntas en el banco para esa cantidad.")

    rng = Random(semilla)
    materias = sorted({q.materia for q in BANCO_PREGUNTAS})
    seleccionadas: List[PreguntaDiagnostico] = []

    # Asegura cobertura mínima por materia antes de completar aleatoriamente.
    if cantidad >= len(materias):
        for materia in materias:
            pool = [q for q in BANCO_PREGUNTAS if q.materia == materia]
            seleccionadas.extend(_sample_unicos(rng, pool, 1))

    restantes = cantidad - len(seleccionadas)
    if restantes > 0:
        ids_actuales = {q.id for q in seleccionadas}
        pool_restante = [q for q in BANCO_PREGUNTAS if q.id not in ids_actuales]
        seleccionadas.extend(_sample_unicos(rng, pool_restante, restantes))

    rng.shuffle(seleccionadas)
    return [_pregunta_a_dict(q) for q in seleccionadas]


def obtener_preguntas_diagnostico_adaptativo(
    cantidad: int = 10,
    diagnostico_anterior: Optional[Dict[str, object]] = None,
    semilla: int | None = None,
) -> List[Dict[str, object]]:
    """Genera diagnóstico mixto: refuerzo de falencias + exploración de nuevos temas."""
    if not diagnostico_anterior:
        return obtener_preguntas_diagnostico(cantidad=cantidad, semilla=semilla)

    rng = Random(semilla)
    resultados = diagnostico_anterior.get("resultados_por_materia", [])

    temas_reforzar = {
        tema
        for r in resultados
        for tema in r.get("temas_reforzar", [])
    }
    materias_debiles = {
        r.get("materia")
        for r in resultados
        if float(r.get("porcentaje", 0)) < 70
    }

    temas_evaluados_raw = diagnostico_anterior.get("temas_evaluados", [])
    temas_evaluados = set()
    for item in temas_evaluados_raw:
        if isinstance(item, dict):
            temas_evaluados.add((item.get("materia"), item.get("tema")))

    refuerzo_pool = [
        q for q in BANCO_PREGUNTAS
        if q.tema in temas_reforzar or q.materia in materias_debiles
    ]

    exploracion_pool = [
        q for q in BANCO_PREGUNTAS
        if (q.materia, q.tema) not in temas_evaluados or q.tema not in temas_reforzar
    ]

    base_pool = list(BANCO_PREGUNTAS)
    seleccionadas: List[PreguntaDiagnostico] = []

    # Ajusta dificultad objetivo por materia según desempeño previo.
    objetivo_por_materia = {
        r.get("materia"): dificultad_objetivo_por_materia(diagnostico_anterior, r.get("materia"))
        for r in resultados
    }

    refuerzo_filtrado = []
    for q in refuerzo_pool:
        objetivo = objetivo_por_materia.get(q.materia, "intermedio")
        if q.dificultad == objetivo:
            refuerzo_filtrado.append(q)
    if refuerzo_filtrado:
        refuerzo_pool = refuerzo_filtrado

    exploracion_filtrada_dif = []
    for q in exploracion_pool:
        objetivo = objetivo_por_materia.get(q.materia, dificultad_objetivo_por_materia(diagnostico_anterior))
        if q.dificultad == objetivo:
            exploracion_filtrada_dif.append(q)
    if exploracion_filtrada_dif:
        exploracion_pool = exploracion_filtrada_dif

    cupo_refuerzo = max(1, int(cantidad * 0.6))
    cupo_exploracion = max(1, int(cantidad * 0.4))

    seleccionadas.extend(_sample_unicos(rng, refuerzo_pool, min(cupo_refuerzo, len(refuerzo_pool))))

    ids = {q.id for q in seleccionadas}
    exploracion_filtrada = [q for q in exploracion_pool if q.id not in ids]
    seleccionadas.extend(_sample_unicos(rng, exploracion_filtrada, min(cupo_exploracion, len(exploracion_filtrada))))

    ids = {q.id for q in seleccionadas}
    faltantes = cantidad - len(seleccionadas)
    if faltantes > 0:
        pool_faltantes = [q for q in base_pool if q.id not in ids]
        seleccionadas.extend(_sample_unicos(rng, pool_faltantes, faltantes))

    rng.shuffle(seleccionadas)
    return [_pregunta_a_dict(q) for q in seleccionadas[:cantidad]]


def evaluar_diagnostico(respuestas_usuario: Dict[str, str], preguntas_presentadas: List[Dict[str, object]]) -> Dict[str, object]:
    """Evalua respuestas y genera resumen por materia/tema para plan de refuerzo."""
    indice_correctas = {q.id: q for q in BANCO_PREGUNTAS}

    aciertos = 0
    total = len(preguntas_presentadas)
    por_materia: Dict[str, Dict[str, object]] = {}
    por_dificultad: Dict[str, Dict[str, int]] = {}
    temas_evaluados = set()

    for pregunta in preguntas_presentadas:
        qid = pregunta["id"]
        correcta = indice_correctas[qid].respuesta_correcta
        respuesta = respuestas_usuario.get(qid)
        es_correcta = respuesta == correcta

        if es_correcta:
            aciertos += 1

        materia = pregunta["materia"]
        tema = pregunta["tema"]
        dificultad = str(pregunta.get("dificultad", "intermedio"))
        temas_evaluados.add((materia, tema))

        if materia not in por_materia:
            por_materia[materia] = {"aciertos": 0, "total": 0, "temas_reforzar": []}

        if dificultad not in por_dificultad:
            por_dificultad[dificultad] = {"aciertos": 0, "total": 0}

        por_materia[materia]["total"] += 1
        if es_correcta:
            por_materia[materia]["aciertos"] += 1
            por_dificultad[dificultad]["aciertos"] += 1
        else:
            por_materia[materia]["temas_reforzar"].append(tema)
        por_dificultad[dificultad]["total"] += 1

    porcentaje = round((aciertos / total) * 100, 2) if total else 0

    resultados_por_materia = []
    for materia, datos in por_materia.items():
        total_materia = datos["total"]
        aciertos_materia = datos["aciertos"]
        porcentaje_materia = round((aciertos_materia / total_materia) * 100, 2) if total_materia else 0
        temas = sorted(set(datos["temas_reforzar"]))
        resultados_por_materia.append(
            {
                "materia": materia,
                "aciertos": aciertos_materia,
                "total": total_materia,
                "porcentaje": porcentaje_materia,
                "temas_reforzar": temas,
            }
        )

    recomendaciones = generar_recomendaciones_refuerzo(resultados_por_materia)

    return {
        "aciertos_totales": aciertos,
        "total_preguntas": total,
        "porcentaje_total": porcentaje,
        "resultados_por_materia": sorted(resultados_por_materia, key=lambda x: x["materia"]),
        "resultados_por_dificultad": por_dificultad,
        "temas_evaluados": [
            {"materia": materia, "tema": tema}
            for (materia, tema) in sorted(temas_evaluados)
        ],
        "recomendaciones": recomendaciones,
    }


def generar_recomendaciones_refuerzo(resultados_por_materia: List[Dict[str, object]]) -> List[str]:
    """Crea un plan de refuerzo breve y accionable según resultados."""
    recomendaciones = []

    for item in resultados_por_materia:
        materia = item["materia"]
        porcentaje = float(item["porcentaje"])
        temas = item["temas_reforzar"]

        if porcentaje >= 80:
            recomendaciones.append(f"{materia}: buen punto de partida. Sube dificultad con preguntas tipo caso.")
        elif porcentaje >= 50:
            recomendaciones.append(f"{materia}: nivel intermedio. Refuerza {', '.join(temas[:2])} con práctica guiada.")
        else:
            recomendaciones.append(f"{materia}: prioridad alta de refuerzo. Trabaja base conceptual en {', '.join(temas[:2])}.")

    if not recomendaciones:
        recomendaciones.append("No se generaron recomendaciones. Repite el diagnóstico.")

    return recomendaciones


def obtener_materia_prioritaria(diagnostico_resultado: Optional[Dict[str, object]], default: str = "Matemáticas") -> str:
    """Elige la materia con menor porcentaje para priorizarla al iniciar sesión."""
    if not diagnostico_resultado:
        return default

    resultados = diagnostico_resultado.get("resultados_por_materia", [])
    if not resultados:
        return default

    ordenadas = sorted(resultados, key=lambda x: (float(x.get("porcentaje", 0)), -int(x.get("total", 0))))
    return ordenadas[0].get("materia", default)


def generar_preguntas_recomendadas(
    diagnostico_resultado: Optional[Dict[str, object]],
    materia_actual: str,
    max_preguntas: int = 3,
) -> List[str]:
    """Genera preguntas sugeridas para abrir conversación enfocada en debilidades."""
    if not diagnostico_resultado:
        return [
            "Explícame cómo identificar el tema central de una pregunta tipo ICFES.",
            "Hazme una pregunta diagnóstica de nivel intermedio para empezar.",
            "Quiero practicar con una pregunta guiada paso a paso.",
        ][:max_preguntas]

    resultados = diagnostico_resultado.get("resultados_por_materia", [])
    datos_materia = next((m for m in resultados if m.get("materia") == materia_actual), None)

    if not datos_materia:
        return [
            f"Hazme una pregunta tipo ICFES de {materia_actual} y guíame con método socrático.",
            f"Evalúa mi nivel actual en {materia_actual} con un ejercicio breve.",
        ][:max_preguntas]

    temas = datos_materia.get("temas_reforzar", [])
    if not temas:
        return [
            f"Quiero un reto de mayor nivel en {materia_actual}.",
            f"Propón una pregunta tipo caso en {materia_actual}.",
        ][:max_preguntas]

    sugerencias = []
    for tema in temas[:max_preguntas]:
        sugerencias.append(f"Ayúdame a reforzar {tema} en {materia_actual} con una pregunta tipo ICFES.")

    return sugerencias


def generar_plan_semanal(diagnostico_resultado: Optional[Dict[str, object]]) -> List[Dict[str, str]]:
    """Construye un plan semanal simple orientado a los temas críticos del diagnóstico."""
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

    if not diagnostico_resultado:
        return [
            {"dia": dias[0], "materia": "General", "objetivo": "Realizar diagnóstico inicial", "actividad": "Completar test para personalizar el plan."},
            {"dia": dias[1], "materia": "General", "objetivo": "Sesión base", "actividad": "Resolver 2 preguntas guiadas por el tutor."},
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
        datos = next((r for r in resultados if r.get("materia") == materia), {})
        temas = datos.get("temas_reforzar", [])
        tema_objetivo = temas[0] if temas else "resolución de preguntas tipo caso"

        plan.append(
            {
                "dia": dia,
                "materia": materia,
                "objetivo": f"Fortalecer {tema_objetivo}",
                "actividad": f"Resolver 3 preguntas guiadas de {materia} y cerrar con autoexplicación.",
            }
        )

    return plan


def diagnostico_requiere_renovacion(
    creado_el_iso: Optional[str],
    ahora: Optional[datetime] = None,
    dias_vigencia: int = 7,
) -> bool:
    """Determina si el diagnóstico debe repetirse por vigencia semanal."""
    if not creado_el_iso:
        return True

    try:
        fecha_diag = datetime.fromisoformat(creado_el_iso.replace("Z", "+00:00"))
    except ValueError:
        return True

    if fecha_diag.tzinfo is None:
        fecha_diag = fecha_diag.replace(tzinfo=timezone.utc)

    referencia = ahora or datetime.now(timezone.utc)
    return referencia >= (fecha_diag + timedelta(days=dias_vigencia))
