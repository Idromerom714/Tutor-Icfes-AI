import streamlit as st
import base64
import requests

PROFE_SABER_PROMPT = """
Eres "El Profe Saber", el tutor de IA más teso de Colombia, experto en las pruebas ICFES Saber 11. 
Tu misión no es solo dar respuestas, sino entrenar cerebros para que conquisten el examen.

REGLAS DE ORO:
1. Tono: Eres un mentor cercano y motivador, con chispa (ej: "¡Ey, genio!", "¡Vamos por ese cupo!").
2. Método Socrático: NUNCA des la respuesta de inmediato. Da pistas y analiza el enunciado con el alumno.
3. Uso del Contexto: Prioriza la información de la "Biblioteca" (RAG) que se te proporciona abajo.
4. Fórmulas: Usa LaTeX para matemáticas, ej: $E = mc^2$.
"""

def llamar_profe_saber(mensaje_usuario, contexto_pdf, imagen_bytes=None):
    api_key = st.secrets["OPENROUTER_API_KEY"]
    # Usamos Gemini Flash 1.5 Free para ahorrar o Kimi k2 para razonamiento
    model_name = "google/gemini-flash-1.5-exp:free" 
    
    headers = {"Authorization": f"Bearer {api_key}"}
    
    # Construcción del contenido
    contenido = [{"type": "text", "text": f"Contexto de estudio: {contexto_pdf}\n\nPregunta del alumno: {mensaje_usuario}"}]
    
    if imagen_bytes:
        base64_img = base64.b64encode(imagen_bytes).decode('utf-8')
        contenido.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}
        })

    payload = {
        "model": model_name,
        "messages": [
            # AQUÍ SE AÑADE EL SYSTEM PROMPT
            {"role": "system", "content": PROFE_SABER_PROMPT},
            # Y aquí la duda específica con su contexto
            {"role": "user", "content": contenido_usuario}
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    return response.json()['choices'][0]['message']['content']