import streamlit as st
import random
from core.database import obtener_datos_usuario, descontar_credito
from core.rag_search import buscar_contexto_icfes
from core.ai_engine import llamar_profe_saber

# Configuración de página
st.set_page_config(page_title="El Profe Saber - Prepárate para la U", page_icon="🎓")

# --- ESTADO DE SESIÓN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

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
                st.session_state.user = user
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("PIN o correo incorrectos.")

# --- APP PRINCIPAL (Todo esto debe estar indentado bajo el 'else') ---
else:
    user = st.session_state.user
    nombre = user['email'].split('@')[0].capitalize()
    
    # 1. BARRA LATERAL (SIDEBAR)
    with st.sidebar:
        st.header(f"¡Ey, {nombre}! 👋")
        st.caption(f"Plan: {user['plan'].upper()}")
        
        st.subheader("📚 ¿Qué vamos a estudiar?")
        materia_seleccionada = st.selectbox(
            "Selecciona el área:",
            ["Matemáticas", "Lectura Crítica", "Sociales", "Ciencias Naturales", "Inglés"]
        )
        
        st.divider()
        
        limite_p = 10 if user['plan'] == 'basico' else 50
        limite_i = 5 if user['plan'] == 'basico' else 12
        
        st.subheader("⚡ Tu Energía Hoy")
        st.progress(user['preguntas_usadas'] / limite_p, text=f"Preguntas: {user['preguntas_usadas']}/{limite_p}")
        st.progress(user['imagenes_usadas'] / limite_i, text=f"Fotos: {user['imagenes_usadas']}/{limite_i}")
        
        st.divider()
        
        tip = random.choice([
            "En Matemáticas, descarta las opciones que no tengan sentido antes de operar.",
            "En Sociales, fíjate siempre en quién escribe el texto y cuál es su intención.",
            "Para Inglés, el contexto de las imágenes te da media respuesta."
        ])
        st.info(tip)
        
        if st.button("Cerrar Sesión"):
            st.session_state.autenticado = False
            st.rerun()

    # 2. INICIALIZAR HISTORIAL POR MATERIA
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = {}

    if materia_seleccionada not in st.session_state.chat_history:
        st.session_state.chat_history[materia_seleccionada] = []

    # 3. MOSTRAR CHAT EXISTENTE
    for msg in st.session_state.chat_history[materia_seleccionada]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 4. ENTRADA DE DUDAS
    # Usamos st.chat_input que es más limpio para móviles
    pregunta_txt = st.chat_input("Escribe tu duda...")
    foto = st.file_uploader("Subir foto de un ejercicio", type=['jpg', 'jpeg', 'png'])

    if pregunta_txt or foto:
        p_ok = user['preguntas_usadas'] < limite_p
        i_ok = (not foto) or (user['imagenes_usadas'] < limite_i)

        if p_ok and i_ok:
            # Mostrar mensaje del usuario
            texto_usuario = pregunta_txt if pregunta_txt else "Te envío esta foto, profe."
            st.chat_message("user").write(texto_usuario)
            st.session_state.chat_history[materia_seleccionada].append({"role": "user", "content": texto_usuario})
            
            with st.spinner(f"El Profe está analizando {materia_seleccionada}..."):
                # Leer foto si existe
                img_bytes = foto.read() if foto else None
                
                # Buscar contexto
                contexto = buscar_contexto_icfes(
                    query=pregunta_txt if pregunta_txt else "Analiza esta imagen",
                    materia=materia_seleccionada
                )
                
                # Llamar IA
                respuesta = llamar_profe_saber(pregunta_txt, contexto, img_bytes)
                
                # Mostrar y guardar respuesta
                with st.chat_message("assistant"):
                    st.markdown(respuesta)
                
                st.session_state.chat_history[materia_seleccionada].append({"role": "assistant", "content": respuesta})
                
                # Actualizar DB y local
                descontar_credito(user['email'], es_imagen=bool(foto))
                user['preguntas_usadas'] += 1
                if foto: user['imagenes_usadas'] += 1
                st.rerun() # Recarga para actualizar las barras de progreso
                
        else:
            st.error("⚠️ Se te acabó la energía por hoy. ¡Mañana amaneces con el tanque lleno!")