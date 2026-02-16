import streamlit as st
import base64
import requests

PROFE_SABER_PROMPT = """
Eres "El Profe Saber", experto en ICFES. Usa el método socrático. 
No des la respuesta, guía al alumno con pistas y motivación paisa.
"""

def llamar_profe_saber(mensaje_usuario, contexto_pdf, imagen_bytes=None):
    # 1. Verificar que la llave existe
    if "OPENROUTER_API_KEY" not in st.secrets:
        return "❌ Error: No configuraste la llave OPENROUTER_API_KEY en los Secrets."

    api_key = st.secrets["OPENROUTER_API_KEY"]
    # Probemos con el modelo 2.0 que es más estable y sigue siendo gratis
    model_name = "openai/gpt-oss-120b:free" 
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://profesaber.streamlit.app", # Requerido por algunos modelos free
        "Content-Type": "application/json"
    }
    
    contenido_usuario = [{"type": "text", "text": f"BIBLIOTECA: {contexto_pdf}\n\nDUDA: {mensaje_usuario}"}]
    
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

        # 2. Manejo de errores amigable
        if "choices" in res_json:
            return res_json['choices'][0]['message']['content']
        else:
            # Si falla, nos dice por qué (ej: "Insufficient credits")
            error_msg = res_json.get("error", {}).get("message", "Error desconocido del API")
            return f"⚠️ El Profe tuvo un problema: {error_msg}"
            
    except Exception as e:
        return f"❌ Error de conexión: {str(e)}"