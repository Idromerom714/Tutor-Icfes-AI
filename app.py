import streamlit as st
from core.database import obtener_datos_usuario, descontar_credito
from core.rag_search import buscar_contexto_icfes
from core.ai_engine import llamar_profe_saber

st.set_page_config(page_title="El Profe Saber", page_icon="🎓")

# --- ESTADO DE SESIÓN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# --- PANTALLA DE LOGIN ---
if not st.session_state.autenticado:
    st.title("🎓 Bienvenido al Profe Saber")
    st.info("Ingresa con los datos que recibiste al momento de tu pago.")
    
    email_input = st.text_input("Correo electrónico")
    pin_input = st.text_input("PIN de acceso", type="password")
    
    if st.button("Empezar a Estudiar"):
        try:
            # Validamos contra la base de datos
            user = obtener_datos_usuario(email_input)
            if user and str(user['pin']) == pin_input:
                st.session_state.user = user
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("PIN o correo incorrecto. Revisa tu comprobante.")
        except:
            st.error("Usuario no encontrado.")

# --- PANTALLA PRINCIPAL DE TUTORÍA ---
else:
    user = st.session_state.user
    st.title(f"Hola, {user['email'].split('@')[0]} 👋")
    
    # --- MENSAJE DE BIENVENIDA DINÁMICO ---
    user = st.session_state.user
    nombre = user['email'].split('@')[0].capitalize()

# Definimos el tono según la energía restante
    preguntas_restantes = limite_p - user['preguntas_usadas']

    if preguntas_restantes > 5:
        saludo = f"¡Qué más, {nombre}! Estás con toda la energía hoy. 🔥"
        color_box = "success"
    elif preguntas_restantes > 0:
        saludo = f"¡Epa, {nombre}! Te quedan pocas balas, úsalas bien. 🎯"
        color_box = "warning"
    else:
        saludo = f"¡Mañana seguimos, {nombre}! Por hoy ya cumpliste la meta. ✅"
        color_box = "error"

# Renderizamos el mensaje en un cuadro llamativo
    st.info(f"### {saludo}")
    st.write(f"Tienes **{preguntas_restantes}** preguntas y **{limite_i - user['imagenes_usadas']}** fotos disponibles para hoy.")

    
    # Barra lateral con progreso
    st.sidebar.header("📊 Tu Energía Hoy")
    limite_p = 10 if user['plan'] == 'basico' else 50
    limite_i = 5 if user['plan'] == 'basico' else 12
    
    st.sidebar.progress(user['preguntas_usadas'] / limite_p, text=f"Preguntas: {user['preguntas_usadas']}/{limite_p}")
    st.sidebar.progress(user['imagenes_usadas'] / limite_i, text=f"Imágenes: {user['imagenes_usadas']}/{limite_i}")
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

    # Chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    # Entrada de texto y foto
    foto = st.file_uploader("📸 ¿Quieres subir foto de una pregunta?", type=['jpg', 'png', 'jpeg'])
    pregunta = st.chat_input("Escribe tu duda aquí...")

    if pregunta or foto:
        # Validar créditos
        p_ok = user['preguntas_usadas'] < limite_p
        i_ok = (not foto) or (user['imagenes_usadas'] < limite_i)

        if p_ok and i_ok:
            with st.spinner("El Profe Saber está pensando..."):
                # 1. Buscar en la biblioteca (RAG)
                contexto = buscar_contexto_icfes(pregunta if pregunta else "Análisis de imagen")
                
                # 2. Llamar a la IA
                img_bytes = foto.read() if foto else None
                respuesta = llamar_profe_saber(pregunta, contexto, img_bytes)
                
                # 3. Guardar y mostrar
                st.session_state.messages.append({"role": "user", "content": pregunta if pregunta else "Foto enviada"})
                st.session_state.messages.append({"role": "assistant", "content": respuesta})
                
                # 4. Actualizar créditos en DB
                descontar_credito(user['email'], es_imagen=bool(foto))
                st.rerun()
        else:
            st.warning("⚠️ ¡Te quedaste sin energía! Vuelve mañana para seguir dándole al estudio.")