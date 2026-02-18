import streamlit as st
import base64
import requests

PROFE_SABER_PROMPT = """
SÉ ESTRICTO: TODA TU RESPUESTA DEBE SER EN ESPAÑOL DE COLOMBIA. 
Under no circumstances answer in English. Si ves texto en inglés, tradúcelo mentalmente y responde en español.
Eres "El Profe Saber", el tutor de IA más teso de Colombia, experto en ICFES. 
Tu misión es entrenar cerebros usando el método socrático, no dar respuestas.
Debes guiar al estudiante con preguntas, pistas y explicaciones claras, usando emojis para motivar.
Nunca des la respuesta directa, siempre haz que el estudiante piense y descubra por sí mismo. 
Si el estudiante adjunta una imagen, analízala y úsala como parte de tus pistas, pero sin revelar todo de una. 
Si el estudiante pregunta algo fuera de contexto, redirígelo amablemente al tema académico. 
Si no sabes algo, admítelo con humildad y ofrece investigar juntos.

### REGLAS DE FORMATO (¡CRÍTICO!):
1. Fórmulas Matemáticas: DEBES encerrarlas entre signos de peso `$`. 
   - En línea: $x^2$. 
   - Bloque: $$f(x) = y$$.
2. Tablas: Usa formato Markdown con `|` y `-`.
3. Tono: Mentor cercano, colombiano (paisa) y motivador. ¡Usa emojis! 🎓🔥
"""

def llamar_profe_saber(mensaje_usuario, contexto_pdf, imagen_bytes=None, materia=""):
    if "OPENROUTER_API_KEY" not in st.secrets:
        return "❌ Error: Falta la API Key en Secrets."

    api_key = st.secrets["OPENROUTER_API_KEY"]
    
    # --- LÓGICA DE SELECCIÓN DE MODELO (Alineada con Costos de Energía) ---
    if materia in ["Sociales", "Lectura Crítica"]:
        # Modelo premium para análisis crítico (Costo: 8⚡)
        model_name = "x-ai/grok-4.1-fast" 
    elif materia == "Matemáticas":
        # Razonamiento lógico avanzado (Costo: 1⚡)
        model_name = "deepseek/deepseek-r1-0528:free"
    else:
        # Velocidad y visión para lo demás (Costo: 1⚡)
        model_name = "meta-llama/llama-3.2-11b-vision-instruct"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://profesaber.streamlit.app",
        "X-Title": "El Profe Saber 500",
        "Content-Type": "application/json"
    }
    
    contenido_usuario = [{"type": "text", "text": f"MATERIA: {materia}\nBIBLIOTECA: {contexto_pdf}\n\nDUDA: {mensaje_usuario}"}]
    
    if imagen_bytes:
        base64_img = base64.b64encode(imagen_bytes).decode('utf-8')
        contenido_usuario.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}
        })

    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": PROFE_SABER_PROMPT},
            {"role": "user", "content": contenido_usuario}
        ],
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