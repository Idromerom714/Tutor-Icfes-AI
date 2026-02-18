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
st.set_page_config(page_title="El Profe Saber", page_icon="🎓")

# --- ESTADO DE SESIÓN ---
if "autenticado" not in st.session_state: st.session_state.autenticado = False
if "chat_id_actual" not in st.session_state: st.session_state.chat_id_actual = None
if "mensajes_actuales" not in st.session_state: st.session_state.mensajes_actuales = []

if not st.session_state.autenticado:
    # --- LOGIN ---
    st.title("🎓 El Profe Saber")
    with st.form("login_form"):
        email_input = st.text_input("Correo electrónico")
        pin_input = st.text_input("PIN de acceso", type="password")
        if st.form_submit_button("Entrar a estudiar", use_container_width=True):
            user = obtener_datos_usuario(email_input)
            if user and str(user['pin']) == pin_input:
                st.session_state.user = user
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("PIN o correo incorrectos.")
else:
    # Recargar datos del usuario para energía en tiempo real
    user = obtener_datos_usuario(st.session_state.user['email'])
    nombre = user['email'].split('@')[0].capitalize()
    
    # --- SIDEBAR ---
    with st.sidebar:
        st.header(f"¡Ey, {nombre}! 👋")
        
        # Visualización de Energía
        creditos = user.get('creditos_totales', 0)
        color_bat = "green" if creditos > 50 else "orange" if creditos > 15 else "red"
        st.markdown(f"### 🔋 Energía: :{color_bat}[{creditos} ⚡]")
        
        if st.button("➕ Nueva Conversación", use_container_width=True):
            st.session_state.chat_id_actual = None
            st.session_state.mensajes_actuales = []
            st.rerun()

        st.divider()
        
        # --- FIX: EXPORTAR PDF SEGURO ---
        if st.session_state.mensajes_actuales:
            st.subheader("📥 Exportar")
            try:
                m_pdf = st.session_state.get('materia_activa', 'General')
                pdf_bytes = generar_pdf_estudio(st.session_state.mensajes_actuales, m_pdf)
                
                if pdf_bytes: # Solo mostramos el botón si los bytes son válidos
                    st.download_button(
                        label="Descargar mi Resumen",
                        data=pdf_bytes,
                        file_name=f"Estudio_{m_pdf}_{datetime.now().strftime('%m%d')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                else:
                    st.caption("Generando archivo...")
            except Exception:
                st.caption("⚠️ PDF no disponible en este momento.")

        st.divider()
        materia_seleccionada = st.selectbox