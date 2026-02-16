import streamlit as st
import random
from core.database import obtener_datos_usuario, descontar_credito
from core.rag_search import buscar_contexto_icfes
from core.ai_engine import llamar_profe_saber

# Configuración de página (Medellín Vibes)
st.set_page_config(page_title="El Profe Saber - Prepárate para la U", page_icon="🎓")

# --- ESTADO DE SESIÓN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# --- LÓGICA DE LOGIN ---
if not st.session_state.autenticado:
    st.title("🎓 El Profe Saber")
    
    # Usar un formulario evita que el botón sea "perezoso"
    with st.form("login_form"):
        email_input = st.text_input("Correo electrónico")
        pin_input = st.text_input("PIN de acceso", type="password")
        submit = st.form_submit_button("Entrar a estudiar", use_container_width=True)
        
        if submit:
            user = obtener_datos_usuario(email_input)
            if user and str(user['pin']) == pin_input:
                st.session_state.user = user
                st.session_state.autenticado = True
                st.rerun() # Esto ahora funcionará al primer toque
            else:
                st.error("PIN o correo incorrectos.")

# --- APP PRINCIPAL ---
else:
    user = st.session_state.user
    nombre = user['email'].split('@')[0].capitalize()
    
    # 1. BARRA LATERAL (SIDEBAR)
    with st.sidebar:
        st.header(f"¡Ey, {nombre}! 👋")
        st.caption(f"Plan: {user['plan'].upper()}")
        
        # Selección de Materia (Namespaces en Pinecone)
        st.subheader("📚 ¿Qué vamos a estudiar?")
        materia_seleccionada = st.selectbox(
            "Selecciona el área:",
            ["Matemáticas", "Lectura Crítica", "Sociales", "Ciencias Naturales", "Inglés"]
        )
        
        st.divider()
        
        # Control de Energía (Créditos)
        limite_p = 10 if user['plan'] == 'basico' else 50
        limite_i = 5 if user['plan'] == 'basico' else 12
        
        st.subheader("⚡ Tu Energía Hoy")
        st.progress(user['preguntas_usadas'] / limite_p, text=f"Preguntas: {user['preguntas_usadas']}/{limite_p}")
        st.progress(user['imagenes_usadas'] / limite_i, text=f"Fotos: {user['imagenes_usadas']}/{limite_i}")
        
        st.divider()
        
        # Tips dinámicos
        tip = random.choice([
            "En Matemáticas, descarta las opciones que no tengan sentido antes de operar.",
            "En Sociales, fíjate siempre en quién escribe el texto y cuál es su intención.",
            "Para Inglés, el contexto de las imágenes te da media respuesta."
        ])
        st.info(tip)
        
        if st.button("Cerrar Sesión"):
            st.session_state.autenticado = False
            st.rerun()

    # 2. ÁREA DE CHAT
    # 1. Inicializar el historial como un diccionario si no existe
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}

# 2. Si la materia actual no tiene historial, creárselo
if materia_seleccionada not in st.session_state.chat_history:
    st.session_state.chat_history[materia_seleccionada] = []

# 3. Usar el historial específico de la materia
mensajes_actuales = st.session_state.chat_history[materia_seleccionada]

for msg in mensajes_actuales:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ... (cuando guardes la respuesta del Profe, hazlo así:)
st.session_state.chat_history[materia_seleccionada].append({"role": "assistant", "content": respuesta})

    # 3. ENTRADA DE DUDAS (Texto y Foto)
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        pregunta_txt = st.chat_input("Escribe tu duda o sube una foto...")
    with col2:
        foto = st.file_uploader("📸", type=['jpg', 'jpeg', 'png'], label_visibility="collapsed")

    if pregunta_txt or foto:
        # Validar si tiene créditos suficientes
        p_ok = user['preguntas_usadas'] < limite_p
        i_ok = (not foto) or (user['imagenes_usadas'] < limite_i)

        if p_ok and i_ok:
            # Mostramos pregunta del usuario
            st.chat_message("user").write(pregunta_txt if pregunta_txt else "Te envío esta foto, profe.")
            
            with st.spinner(f"Buscando en la biblioteca de {materia_seleccionada}..."):
                # A. Buscar contexto específico en el NAMESPACE de la materia
                contexto = buscar_contexto_icfes(
                    query=pregunta_txt if pregunta_txt else "Analiza esta imagen de examen",
                    materia=materia_seleccionada
                )
                
                # B. Llamar a la IA con Visión si hay foto
                img_bytes = foto.read() if foto else None
                respuesta = llamar_profe_saber(pregunta_txt, contexto, img_bytes)
                
                # C. Mostrar respuesta
                with st.chat_message("assistant"):
                    st.markdown(respuesta)
                
                # D. Guardar historial y descontar créditos
                st.session_state.messages.append({"role": "user", "content": pregunta_txt if pregunta_txt else "Foto enviada"})
                st.session_state.messages.append({"role": "assistant", "content": respuesta})
                
                descontar_credito(user['email'], es_imagen=bool(foto))
                # Actualizamos el estado local para que las barras de progreso se muevan de una
                user['preguntas_usadas'] += 1
                if foto: user['imagenes_usadas'] += 1
                
        else:
            st.error("⚠️ Se te acabó la energía por hoy. ¡Mañana amaneces con el tanque lleno!")