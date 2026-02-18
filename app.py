import streamlit as st
from datetime import datetime
from core.database import (
    obtener_datos_usuario, 
    descontar_energia, 
    guardar_o_actualizar_chat, 
    listar_chats_usuario, 
    cargar_chat_completo
)
from core.rag_search import buscar_contexto_icfes
from core.ai_engine import llamar_profe_saber, generar_titulo_chat
from core.pdf_generator import generar_pdf_estudio 

# Configuración de página
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
    # Recargar datos del usuario para ver saldo real de energía
    user = obtener_datos_usuario(st.session_state.user['email'])
    nombre = user['email'].split('@')[0].capitalize()
    
    # 1. BARRA LATERAL (SIDEBAR)
    with st.sidebar:
        st.header(f"¡Ey, {nombre}! 👋")
        
        # --- NUEVA VISUALIZACIÓN DE ENERGÍA ---
        creditos = user['creditos_totales']
        color = "green" if creditos > 50 else "orange" if creditos > 10 else "red"
        st.markdown(f"### 🔋 Energía: :{color}[{creditos} ⚡]")
        
        if st.button("➕ Nueva Conversación", use_container_width=True):
            st.session_state.chat_id_actual = None
            st.session_state.mensajes_actuales = []
            st.rerun()

        st.divider()
        
        # --- EXPORTAR PDF (Solo si hay contenido) ---
        if st.session_state.mensajes_actuales:
            st.subheader("📥 Exportar")
            try:
                # Usamos materia_seleccionada si existe, sino "General"
                m_pdf = st.session_state.get('materia_activa', 'General')
                pdf_bytes = generar_pdf_estudio(st.session_state.mensajes_actuales, m_pdf)
                st.download_button(
                    label="Descargar mi Resumen",
                    data=pdf_bytes,
                    file_name=f"Estudio_{m_pdf}_{datetime.now().strftime('%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except:
                st.caption("PDF listo para descargar.")

        st.divider()
        
        st.subheader("📜 Tus Estudios")
        res_historial = listar_chats_usuario(user['email'])
        if res_historial.data:
            for chat in res_historial.data:
                titulo_btn = f"{chat['materia']}: {chat['titulo'][:15]}..."
                if st.button(titulo_btn, key=chat['id'], use_container_width=True):
                    datos_chat = cargar_chat_completo(chat['id'])
                    st.session_state.chat_id_actual = chat['id']
                    st.session_state.mensajes_actuales = datos_chat['mensajes']
                    st.session_state.materia_activa = chat['materia']
                    st.rerun()
        
        st.divider()
        materia_seleccionada = st.selectbox(
            "Materia actual:",
            ["Matemáticas", "Lectura Crítica", "Sociales", "Ciencias Naturales", "Inglés"],
            disabled=(st.session_state.chat_id_actual is not None)
        )
        st.session_state.materia_activa = materia_seleccionada

    # 2. ÁREA DE CHAT
    if not st.session_state.mensajes_actuales:
        st.title(f"🦾 ¡Qué más, {nombre}!")
        st.markdown(f"### 🚀 Prepárate para ganar en **{materia_seleccionada}**")
    else:
        for msg in st.session_state.mensajes_actuales:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # 3. CENTRO DE COMANDO (Dudas e Imágenes)
    st.divider()
    with st.container():
        pregunta_input = st.chat_input("Escribe tu duda o pregunta...")
        foto = st.file_uploader("📸 Añadir imagen (opcional)", type=['jpg', 'jpeg', 'png'], label_visibility="collapsed")
        
        col1, col2 = st.columns([0.7, 0.3])
        with col1:
            enviar = st.button("🚀 Preguntar al Profe", use_container_width=True, type="primary")
        with col2:
            if st.button("🗑️ Limpiar", use_container_width=True):
                st.rerun()

    if enviar or pregunta_input:
        texto_final = pregunta_input if pregunta_input else "Analice la imagen adjunta, Profe."
        
        # --- CÁLCULO DE COSTO ---
        # Sociales/Lectura Crítica = 8 créditos (Grok/DeepSeek R1), Otros = 1 crédito (Gemini Flash)
        costo_base = 8 if materia_seleccionada in ["Sociales", "Lectura Crítica"] else 1
        plus_foto = 5 if foto else 0
        total_a_cobrar = costo_base + plus_foto

        if creditos >= total_a_cobrar:
            st.chat_message("user").write(texto_final)
            
            with st.spinner(f"Analizando... (Costo: {total_a_cobrar}⚡)"):
                img_bytes = foto.read() if foto else None
                contexto = buscar_contexto_icfes(texto_final, materia_seleccionada)
                respuesta = llamar_profe_saber(texto_final, contexto, img_bytes, materia=materia_seleccionada)
                
                if "⚠️" in respuesta or "❌" in respuesta:
                    st.error(respuesta)
                    st.stop()

                with st.chat_message("assistant"):
                    st.markdown(respuesta)
                
                st.session_state.mensajes_actuales.append({"role": "user", "content": texto_final})
                st.session_state.mensajes_actuales.append({"role": "assistant", "content": respuesta})
                
                # Guardar en base de datos
                if not st.session_state.chat_id_actual:
                    titulo_chat = generar_titulo_chat(texto_final)
                else:
                    titulo_chat = "Actualizando..."

                res_db = guardar_o_actualizar_chat(
                    chat_id=st.session_state.chat_id_actual,
                    email=user['email'],
                    titulo=titulo_chat,
                    materia=materia_seleccionada,
                    mensajes=st.session_state.mensajes_actuales
                )
                
                if not st.session_state.chat_id_actual:
                    st.session_state.chat_id_actual = res_db.data[0]['id']

                # --- COBRO SEGURO ---
                descontar_energia(user['email'], cantidad=total_a_cobrar)
                st.rerun()
        else:
            st.error(f"⚠️ Energía insuficiente. Necesitas {total_a_cobrar}⚡ para esta consulta.")