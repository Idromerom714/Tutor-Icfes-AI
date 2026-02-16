import streamlit as st
import random
from core.database import (
    obtener_datos_usuario, 
    descontar_credito, 
    guardar_o_actualizar_chat, 
    listar_chats_usuario, 
    cargar_chat_completo
)
from core.rag_search import buscar_contexto_icfes
from core.ai_engine import llamar_profe_saber, generar_titulo_chat # Importamos la nueva función

# Configuración de página (Medellín Vibes)
st.set_page_config(page_title="El Profe Saber - Prepárate para la U", page_icon="🎓")

# --- ESTADO DE SESIÓN INICIAL ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "chat_id_actual" not in st.session_state:
    st.session_state.chat_id_actual = None
if "mensajes_actuales" not in st.session_state:
    st.session_state.mensajes_actuales = []

# --- LÓGICA DE LOGIN ---
if not st.session_state.autenticado:
    st.title("🎓 El Profe Saber")
    with st.form("login_form"):
        email_input = st.text_input("Correo electrónico")
        pin_input = st.text_input("PIN de acceso", type="password")
        submit = st.form_submit_button("Entrar a estudiar", use_container_width=True)
        
        if submit:
            user = obtener_datos_usuario(email_input)
            if user and str(user['pin']) == pin_input:
                st.session_state.mensajes_actuales = []
                st.session_state.chat_id_actual = None
                st.session_state.user = user
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("PIN o correo incorrectos.")

# --- APP PRINCIPAL ---
else:
    user = st.session_state.user
    nombre = user['email'].split('@')[0].capitalize()
    
    # 1. BARRA LATERAL (SIDEBAR)
    with st.sidebar:
        st.header(f"¡Ey, {nombre}! 👋")
        
        if st.button("➕ Nueva Conversación", use_container_width=True):
            st.session_state.chat_id_actual = None
            st.session_state.mensajes_actuales = []
            st.rerun()

        st.divider()
        
        st.subheader("📜 Tus Estudios Recientes")
        res_historial = listar_chats_usuario(user['email'])
        if res_historial.data:
            for chat in res_historial.data:
                if st.button(f"{chat['materia']}: {chat['titulo']}", key=chat['id'], use_container_width=True):
                    datos_chat = cargar_chat_completo(chat['id'])
                    st.session_state.chat_id_actual = chat['id']
                    st.session_state.mensajes_actuales = datos_chat['mensajes']
                    st.rerun()
        else:
            st.caption("Aún no tienes chats guardados.")

        st.divider()
        
        materia_seleccionada = st.selectbox(
            "Materia actual:",
            ["Matemáticas", "Lectura Crítica", "Sociales", "Ciencias Naturales", "Inglés"],
            disabled=(st.session_state.chat_id_actual is not None)
        )
        
        limite_p = 10 if user['plan'] == 'basico' else 50
        limite_i = 5 if user['plan'] == 'basico' else 12
        st.progress(user['preguntas_usadas'] / limite_p, text=f"Preguntas: {user['preguntas_usadas']}/{limite_p}")
        st.progress(user['imagenes_usadas'] / limite_i, text=f"Fotos: {user['imagenes_usadas']}/{limite_i}")
        
        if st.button("Cerrar Sesión"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # 2. ÁREA DE PANTALLA
    if not st.session_state.mensajes_actuales:
        st.title(f"¡Qué más, {nombre}! 🦾")
        st.markdown(f"""
        ### 🚀 ¡Hoy es un buen día para darle duro al estudio!
        Faltan pocos meses para que las pruebas **Saber 11°** pongan a prueba tu talento. Aquí en la capital de la montaña no nos rendimos, ¡así que vamos por ese puntaje global de 500!
        
        **¿Cómo quieres empezar hoy?**
        1. Selecciona el área de **{materia_seleccionada}** o cambia de materia en el menú lateral.
        2. Escribe una duda o sube una foto de ese ejercicio que te está sacando canas.
        
        *¡Hágale pues, que el examen no se gana solo!* 🎓🔥
        """)
    else:
        for msg in st.session_state.mensajes_actuales:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # 3. ENTRADA DE DUDAS
    pregunta_txt = st.chat_input("Escribe tu duda...")
    foto = st.file_uploader("📸 Sube una foto", type=['jpg', 'jpeg', 'png'], label_visibility="collapsed")

    if pregunta_txt or foto:
        usando_foto = bool(foto)
        if (usando_foto and user['imagenes_usadas'] < limite_i) or (not usando_foto and user['preguntas_usadas'] < limite_p):
            
            texto_usuario = pregunta_txt if pregunta_txt else "Analiza esta imagen, profe."
            st.session_state.mensajes_actuales.append({"role": "user", "content": texto_usuario})
            st.chat_message("user").write(texto_usuario)
            
            with st.spinner("El Profe está pensando..."):
                img_bytes = foto.read() if usando_foto else None
                contexto = buscar_contexto_icfes(texto_usuario, materia_seleccionada)
                respuesta = llamar_profe_saber(pregunta_txt, contexto, img_bytes, materia=materia_seleccionada)
                
                with st.chat_message("assistant"):
                    st.markdown(respuesta)
                
                st.session_state.mensajes_actuales.append({"role": "assistant", "content": respuesta})
                
                # --- Lógica de Título Inteligente y Persistencia ---
                if not st.session_state.chat_id_actual:
                    with st.spinner("Poniéndole nombre a tu estudio..."):
                        resumen_input = pregunta_txt if pregunta_txt else "Análisis visual"
                        titulo_chat = generar_titulo_chat(resumen_input)
                else:
                    titulo_chat = "Actualizando..." # No afectará gracias al cambio en database.py

                res_db = guardar_o_actualizar_chat(
                    chat_id=st.session_state.chat_id_actual,
                    email=user['email'],
                    titulo=titulo_chat,
                    materia=materia_seleccionada,
                    mensajes=st.session_state.mensajes_actuales
                )
                
                if not st.session_state.chat_id_actual:
                    st.session_state.chat_id_actual = res_db.data[0]['id']

                # Descuento de créditos
                if usando_foto:
                    descontar_credito(user['email'], es_imagen=True)
                    user['imagenes_usadas'] += 1
                else:
                    descontar_credito(user['email'], es_imagen=False)
                    user['preguntas_usadas'] += 1
                
                st.rerun()
        else:
            st.error("⚠️ Sin energía suficiente.")