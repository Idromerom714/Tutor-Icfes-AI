import streamlit as st
import base64
import requests

PROFE_SABER_PROMPT = """
Eres "El Profe Saber", el tutor de IA más teso de Colombia, experto en ICFES. 
Tu misión es entrenar cerebros usando el método socrático, no dar respuestas.

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
    
    # --- LÓGICA DE SELECCIÓN DE MODELO (Cerebro Dinámico) ---
    # 1. Si es Matemáticas o Física (Ciencias Naturales), usamos razonamiento pesado
    if materia in ["Matemáticas", "Ciencias Naturales"]:
        # DeepSeek R1 o Qwen Thinking son los reyes del razonamiento ahora
        model_name = "deepseek/deepseek-r1-0528:free" 
    else:
        # 2. Para el resto (Sociales, Inglés, etc.), priorizamos velocidad
        model_name = "openai/gpt-oss-120b:free"

    # --- SOBRESCRITURA POR IMAGEN ---
    # Si hay una foto, necesitamos un modelo que "vea" (Vision)
    if imagen_bytes:
        # GPT-4o-mini es el mejor balance costo/visión
        model_name = "nvidia/nemotron-nano-12b-v2-vl:free"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://profesaber.streamlit.app",
        "X-Title": "El Profe Saber",
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
        ]
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        res_json = response.json()

        if "choices" in res_json:
            # Algunos modelos de razonamiento (thinking) incluyen el proceso en el contenido
            return res_json['choices'][0]['message']['content']
        else:
            error_msg = res_json.get("error", {}).get("message", "Error de OpenRouter")
            return f"⚠️ El Profe tuvo un problema con el modelo {model_name}: {error_msg}"
            
    except Exception as e:
        return f"❌ Error de conexión: {str(e)}"