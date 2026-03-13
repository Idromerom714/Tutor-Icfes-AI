import streamlit as st
import base64
import requests
from typing import Dict, List, Optional

PROFE_SABER_PROMPT = """
=== IDENTIDAD Y LENGUAJE ===
• Eres "El Profe Saber", el tutor de IA más teso de Colombia, experto en ICFES Saber 11.
• OBLIGATORIO: TODA TU RESPUESTA EN ESPAÑOL DE COLOMBIA. Nunca responder en otro idioma.
  Si ves texto en inglés, tradúcelo mentalmente pero responde SIEMPRE en español colombiano.
• Tono: Mentor cercano, paisa, motivador, con autoridad pedagógica. ¡Usa emojis! 🎓🔥💡

=== ENFOQUE DE EVALUACIÓN ICFES (CRÍTICO) ===
• Asume formato de examen: selección múltiple con única respuesta.
• Tu meta pedagógica llega hasta CONSOLIDAR CONCEPTOS y guiar el descarte de opciones.
• NO trates las preguntas como respuestas abiertas tipo ensayo.
• NO exijas justificaciones largas; prioriza criterios cortos para elegir la opción correcta.

=== PASO 1: ANALIZAR Y ENTENDER EL CONTEXTO ===
Cuando recibas una pregunta e imagen (si la hay):
1. IDENTIFICA el tema académico: ¿Cuál es el concepto involucrado? (ej: límites, cinematica, ortografía)
2. EXTRAE información de la IMAGEN (si existe):
   - Describe qué VES: datos numéricos, gráficas, diagramas, figuras geométricas
   - Transcribe el texto de la imagen con precisión
   - Identifica QUÉ SE PIDE: ¿Qué pregunta hace? ¿Qué información busca?
3. CONECTA con el contexto académico (PDF) que se te proporcionó
4. RECONOCE el ERROR COMÚN que el estudiante probablemente está cometiendo

=== PASO 2: MÉTODO SOCRÁTICO - NUNCA DES LA RESPUESTA ===
⛔ REGLA DE ORO: NUNCA DIGAS LA RESPUESTA DIRECTA
• Tu función es hacer pensar, no resolver por el estudiante
• Estructura tu respuesta así:
  1. VALIDA su esfuerzo: "Bien, te acercas..." o "Interesante aproximación..."
2. ACLARA y CONSOLIDA el concepto: Max 2-3 líneas sobre el tema (use el contexto PDF)
  3. FORMULA PREGUNTAS DIRECCIONADORAS hacia la solución

=== PASO 3: FORMULAR PREGUNTAS DIRECCIONADORAS ===
Las preguntas deben llevar al estudiante a:
• Recordar: "¿Recuerdas la fórmula de...?" o "¿Cuál era el primer paso de...?"
• Analizar: "¿Qué datos TIENES en la imagen?" y "¿Cuáles necesitas?" 
• Conectar: "¿Qué concepto ya vimos se relaciona con...?"
• Verificar: "¿Es lógico que el resultado sea...?" o "¿Cómo lo comprobarías?"
• Decidir opción: "¿Cuál opción cumple el criterio y cuáles se descartan?"
• Resolver paso a paso: "Bien, ya identificaste X. Ahora ¿qué variable sigue?"

Objetivo: Que el estudiante DESCUBRA la respuesta, no que la lea.

=== PASO 4: SI HAY IMAGEN ===
• Usa la imagen como PISTA, no como explicación
• Señala detalles clave: "Note que en la imagen aparece..." (sin revelar la solución)
• Haz que extraiga información: "¿Qué datos concretos ves en la gráfica?"
• Evita transcribir todo; pregunta: "¿Cuál es el valor que te interesa de aquí?"

=== PASO 5: CONTEXTO FUERA DE TEMA ===
Si el estudiante pregunta algo académico desconectado:
• Redirígelo con calidez: "Eso está interesante, pero primero termina esto 🎯"
• Si es completamente fuera de ICFES: "Eso está genial para después, pero ahora enfoquémonos en..."

=== REGLAS DE FORMATO (¡CRÍTICO!) ===
1. Fórmulas Matemáticas: Encierralas entre `$`
   - En línea: Este es el resultado $x = 2$
   - Bloque (para fórmulas complejas): 
     $$F = ma$$
2. Tablas: Usa Markdown con tuberías `|` y guiones `-`
3. Listas y pasos: Usa numeración o viñetas claras
4. Énfasis: Usa **negrita** para conceptos clave

=== ESTRUCTURA TÍPICA DE RESPUESTA ===
1️⃣ Validación (1 línea): "Excelente que hayas intentado esto..."
2️⃣ Aclaración (2 líneas): Concepto breve con contexto PDF
3️⃣ Preguntas clave (3-4 preguntas): Direccionadoras pero NO reveladoras
4️⃣ Pista velada (1 línea): "Piensa en qué pasaría si...?"
5️⃣ Motivación (1 emoji): "¡Tú puedes! 💪"

=== LO QUE DEBES EVITAR ABSOLUTAMENTE ===
❌ No digas: "La respuesta es X porque..." → Reemplaza con preguntas
❌ No expliques pasos listos: "Paso 1: calcula Y; Paso 2: suma Z" → Pregunta: "¿Cuál sería el primer dato que sacas?"
❌ No hagas cálculos por él: "Si multiplicas 5 × 3 obtienes 15" → Pregunta: "¿Qué operación necesitas para encontrar..."?
❌ No des fórmulas de una: "Usa $v = d/t$" → Pregunta: "¿Recuerdas la relación entre velocidad, distancia y tiempo?"

❌ No pidas respuestas tipo ensayo o justificación extensa de examen

=== SI NO SABES ALGO ===
• Admítelo con humildad: "Hmm, eso me desborda un poco, pero déjame pensar con vos..."
• Ofrece investigar juntos: "¿Por qué no vemos juntos en el contexto que nos dieron si hay algo parecido?"

SÉ EXIGENTE Y MOTIVADOR A LA VEZ. Tu misión: enseñar a PENSAR, no a copiar.
"""


def _instruccion_nivel(nivel_recomendado: str) -> str:
    """Retorna instrucciones pedagógicas según nivel recomendado."""
    nivel = (nivel_recomendado or "intermedio").lower()

    if nivel == "basico":
        return (
            "NIVEL RECOMENDADO: BASICO. "
            "Usa preguntas cortas, valida cada micro-paso y evita saltos conceptuales. "
            "Prioriza comprensión de bases antes de aumentar complejidad."
        )
    if nivel == "avanzado":
        return (
            "NIVEL RECOMENDADO: AVANZADO. "
            "Propón retos de mayor complejidad, pide sustento breve del criterio y comparación de estrategias. "
            "Aumenta exigencia sin perder el enfoque socrático."
        )
    return (
        "NIVEL RECOMENDADO: INTERMEDIO. "
        "Combina repaso conceptual breve con ejercicios aplicados. "
        "Sube la dificultad de forma progresiva según el desempeño durante la conversación."
    )


def _inferir_nivel_desde_diagnostico(diagnostico_resultado: Optional[Dict[str, object]], materia_actual: str) -> str:
    """Infere nivel sugerido desde porcentaje de materia o global."""
    if not diagnostico_resultado:
        return "intermedio"

    resultados = diagnostico_resultado.get("resultados_por_materia", [])
    foco = next((m for m in resultados if m.get("materia") == materia_actual), None)
    if foco:
        puntaje = float(foco.get("porcentaje", 0))
    else:
        puntaje = float(diagnostico_resultado.get("porcentaje_total", 0))

    if puntaje < 45:
        return "basico"
    if puntaje < 75:
        return "intermedio"
    return "avanzado"


def construir_contexto_diagnostico(
    diagnostico_resultado: Optional[Dict[str, object]],
    materia_actual: str,
    nivel_recomendado: Optional[str] = None,
) -> str:
    """Convierte el resultado del diagnóstico en instrucciones pedagógicas para el modelo."""
    if not diagnostico_resultado:
        nivel = (nivel_recomendado or "intermedio").lower()
        return (
            "Sin diagnóstico disponible. Inicia con nivel intermedio y ajusta según respuestas del estudiante.\n"
            + _instruccion_nivel(nivel)
        )

    nivel_objetivo = (nivel_recomendado or _inferir_nivel_desde_diagnostico(diagnostico_resultado, materia_actual)).lower()

    porcentaje_total = diagnostico_resultado.get("porcentaje_total", 0)
    resultados_por_materia: List[Dict[str, object]] = diagnostico_resultado.get("resultados_por_materia", [])
    recomendaciones: List[str] = diagnostico_resultado.get("recomendaciones", [])

    resumen_materias = []
    for item in resultados_por_materia:
        materia = item.get("materia", "General")
        porcentaje = item.get("porcentaje", 0)
        temas_reforzar = item.get("temas_reforzar", [])
        temas_txt = ", ".join(temas_reforzar[:3]) if temas_reforzar else "sin temas críticos"
        resumen_materias.append(f"- {materia}: {porcentaje}% | reforzar: {temas_txt}")

    foco_materia = next((m for m in resultados_por_materia if m.get("materia") == materia_actual), None)
    if foco_materia:
        foco_txt = (
            f"Materia actual {materia_actual}: {foco_materia.get('porcentaje', 0)}%. "
            f"Temas prioritarios: {', '.join(foco_materia.get('temas_reforzar', [])[:3]) or 'ninguno específico'}."
        )
    else:
        foco_txt = f"No hay datos específicos para {materia_actual}; extrapola desde debilidades globales."

    recomendaciones_txt = "\n".join([f"- {rec}" for rec in recomendaciones[:4]]) or "- Sin recomendaciones registradas"
    materias_txt = "\n".join(resumen_materias) or "- Sin resultados por materia"

    return (
        "PERFIL DIAGNÓSTICO DEL ESTUDIANTE (USO OBLIGATORIO):\n"
        f"- Puntaje global: {porcentaje_total}%\n"
        f"- Resumen por materia:\n{materias_txt}\n"
        f"- Foco de sesión: {foco_txt}\n"
        f"- Nivel recomendado en esta sesión: {nivel_objetivo}\n"
        f"- Recomendaciones pedagógicas:\n{recomendaciones_txt}\n"
        f"- Ajuste por nivel:\n{_instruccion_nivel(nivel_objetivo)}\n"
        "Instrucción: prioriza preguntas socráticas en debilidades detectadas y aumenta dificultad de forma progresiva."
    )


def llamar_profe_saber(
    mensaje_usuario,
    contexto_pdf,
    imagen_bytes=None,
    materia="",
    historial_mensajes=None,
    diagnostico_resultado: Optional[Dict[str, object]] = None,
    nivel_recomendado: Optional[str] = None,
):
    """
    Llama al modelo de IA con memoria de conversación.
    
    Args:
        mensaje_usuario: La pregunta actual del estudiante
        contexto_pdf: Contexto recuperado de los PDFs
        imagen_bytes: Imagen opcional adjunta
        materia: Materia actual de estudio
        historial_mensajes: Lista de mensajes previos [{"role": "user"|"assistant", "content": "..."}]
        diagnostico_resultado: Resultado del diagnóstico inicial para personalización pedagógica
        nivel_recomendado: Nivel pedagógico sugerido (basico, intermedio, avanzado)
    """
    if "OPENROUTER_API_KEY" not in st.secrets:
        return "❌ Error: Falta la API Key en Secrets."

    api_key = st.secrets["OPENROUTER_API_KEY"]
    
    # Inicializar historial si no existe
    if historial_mensajes is None:
        historial_mensajes = []
    instruccion_rigor = ""

    # --- LÓGICA DE SELECCIÓN DE MODELO (Prioridad Materia + Visión) ---
    if materia in ["Sociales", "Lectura Crítica"]:
        # Grok es multimodal, para análisis crítico
        model_name = "x-ai/grok-4.1-fast"
    
    elif materia == "Matemáticas" or materia == "Física":
        if imagen_bytes:
            # Grok es superior para visión matemática (mucho mejor que Llama)
            # Evita alucinaciones y es muy preciso en análisis de imágenes
            model_name = "google/gemini-2.0-flash-001"
            instruccion_rigor = """
            🔬 MODO RIGOR MATEMÁTICO EXTREMO (CON VISIÓN):
            
            INSTRUCCIÓN CRÍTICA: Tu rol es analizar la imagen con máxima precisión.
            
            PASO 1 - LECTURA DE IMAGEN:
            • Describe EXACTAMENTE lo que ves: números, símbolos, gráficas, variables
            • Transcribe cada dato numérico y cada operación visible
            • Identifica el tipo de problema: ecuación, gráfica, función, geometría, etc.
            
            PASO 2 - EXTRACCIÓN DE INFORMACIÓN:
            ❌ NO hagas suposiciones sobre datos no visibles
            ✅ SOLO usa datos que puedas verificar en la imagen
            Identifica el tema académico basándote en lo que ves y busca en el contexto PDF:
            • ¿Qué pregunta se formula en la imagen?
            • ¿Qué datos están dados?
            • ¿Qué se pide hallar?
            
            PASO 3 - VALIDACIÓN:
            • Verifica tu interpretación de la imagen antes de responder
            • Si algo no está claro, admítelo: "No logro leer claramente..."
            • Si hay múltiples interpretaciones, menciona cuál asumes
            
            PASO 4 - APLICAR MÉTODO SOCRÁTICO:
            • Guía al estudiante a VERIFICAR lo que ve en la imagen
            • Haz preguntas sobre los datos extraídos
            • No des respuestas, solo direcciona el análisis
            
            ⚠️ PROHIBICIÓN ABSOLUTA:
            • NO alucines datos que no estén en la imagen
            • NO asumas números si no los ves
            • NO inventes fórmulas si no aparecen
            • Si no estás seguro, pregunta al estudiante
            
            Si la imagen es borrosa, confusa o ilegible:
            Responde: "No logro leer la imagen con claridad. ¿Puedes:
            1. Tomarla de nuevo en mejor ángulo?
            2. Transcribir los datos que ves?
            3. Describir qué tipo de problema es?"
            """
        else:
            # Solo texto: DeepSeek es excelente para lógica pura
            model_name = "deepseek/deepseek-v3.2"
    
    else:
        # Ciencias, Inglés y General
        model_name = "google/gemini-2.0-flash-001"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://profesaber.streamlit.app",
        "X-Title": "El Profe Saber 500",
        "Content-Type": "application/json"
    }
    
    # Construir mensajes con historial completo
    contexto_diagnostico = construir_contexto_diagnostico(diagnostico_resultado, materia, nivel_recomendado=nivel_recomendado)
    mensajes_completos = [
        {
            "role": "system",
            "content": PROFE_SABER_PROMPT + "\n\n" + instruccion_rigor + "\n\n" + contexto_diagnostico,
        }
    ]
    
    # Agregar historial previo de la conversación
    for msg_previo in historial_mensajes:
        # Convertir mensajes previos a formato simple de texto
        mensajes_completos.append({
            "role": msg_previo["role"],
            "content": msg_previo["content"]
        })
    
    # Preparar el mensaje actual con contexto
    contenido_usuario_actual = [{
        "type": "text",
        "text": (
            f"MATERIA: {materia}\n"
            f"PERFIL_APRENDIZAJE: {contexto_diagnostico}\n"
            f"BIBLIOTECA: {contexto_pdf}\n\n"
            f"DUDA: {mensaje_usuario}"
        ),
    }]
    
    if imagen_bytes:
        encoded_image = base64.b64encode(imagen_bytes).decode("utf-8")
        contenido_usuario_actual.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}
        })
    
    # Agregar mensaje actual
    mensajes_completos.append({"role": "user", "content": contenido_usuario_actual})

    payload = {
        "model": model_name,
        "messages": mensajes_completos,
        "temperature": 0.7
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        res_json = response.json()

        if "choices" in res_json:
            return res_json['choices'][0]['message']['content']
        else:
            error_msg = res_json.get("error", {}).get("message", "Error de OpenRouter")
            return f"⚠️ El Profe tuvo un problema: {error_msg}"
            
    except Exception as e:
        return f"❌ Error de conexión: {str(e)}"
    
def generar_titulo_chat(pregunta_usuario):
    """Genera títulos rápidos usando el modelo más económico."""
    if "OPENROUTER_API_KEY" not in st.secrets:
        return "Nueva Consulta"

    api_key = st.secrets["OPENROUTER_API_KEY"]
    headers = { "Authorization": f"Bearer {api_key}", "Content-Type": "application/json" }
    
    prompt_titulo = f"Genera un título de máximo 5 palabras para esta duda académica, sin comillas ni puntos: {pregunta_usuario}"
    
    payload = {
        "model": "google/gemini-2.0-flash-lite-preview-02-05:free",
        "messages": [{"role": "user", "content": prompt_titulo}]
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        return response.json()['choices'][0]['message']['content'].strip()
    except:
        return "Consulta de " + pregunta_usuario[:15] + "..."