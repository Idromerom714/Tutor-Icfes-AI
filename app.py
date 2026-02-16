import streamlit as st
import random
from datetime import datetime
from core.database import (
    obtener_datos_usuario, 
    descontar_credito, 
    guardar_o_actualizar_chat, 
    listar_chats_usuario, 
    cargar_chat_completo
)
from core.rag_search import buscar_contexto_icfes
from core.ai_engine import llamar_profe_saber, generar_titulo_chat
from core.pdf_generator import generar_pdf_estudio # Asegúrate de haber creado este archivo

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
        
        # --- MEJORA ESTÉTICA: BOTÓN DE PDF (Añadido sin consulta) ---
        if st.session_state.mensajes_actuales:
            st.subheader("📥 Exportar")
            try:
                pdf_bytes = generar_pdf_estudio(st.session_state.mensajes_actuales, materia_seleccionada if 'materia_seleccionada' in locals() else "General")
                st.download_button(
                    label="Descargar Resumen PDF",
                    data=pdf_bytes,
                    file_name=f"Estudio_ProfeSaber_{datetime.now().strftime('%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.caption("Prepara tu PDF...")

        st.divider()
        
        st.subheader("📜 Estudios Recientes")
        res_historial = listar_chats_usuario(user['email'])
        if res_historial.data:
            for chat in res_historial.data:
                titulo_btn = f"{chat['materia']}: {chat['titulo'][:15]}..."
                if st.button(titulo_btn, key=chat['id'], use_container_width=True):
                    datos_chat = cargar_chat_completo(chat['id'])
                    st.session_state.chat_id_actual = chat['id']
                    st.session_state.mensajes_actuales = datos_chat['mensajes']
                    st.rerun()
        
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
        st.markdown(f"### 🚀 ¡Dale duro al estudio de **{materia_seleccionada}**!")
    else:
        for msg in st.session_state.mensajes_actuales:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # 3. ENTRADA DE DUDAS (Corregido para texto solo o con imagen)
    st.divider()
    with st.container():
        # Capturamos el texto en una variable que no se pierda al interactuar con el file_uploader
        pregunta_input = st.chat_input("Escribe tu duda o pregunta aquí...")
        foto = st.file_uploader("📸 Añadir imagen al contexto (opcional)", type=['jpg', 'jpeg', 'png'])
        
        col1, col2 = st.columns([0.7, 0.3])
        with col1:
            enviar = st.button("🚀 Consultar al Profe", use_container_width=True, type="primary")
        with col2:
            if st.button("🗑️ Limpiar", use_container_width=True):
                st.rerun()

    # Lógica de disparo: Se activa con el Enter del chat_input O con el botón Enviar
    if enviar or pregunta_input:
        # Priorizamos el texto del chat_input si existe, de lo contrario usamos un placeholder
        texto_final = pregunta_input if pregunta_input else "Analice la imagen adjunta, tengo dudas sobre este tema, Profe."
        
        if texto_final or foto:
            usando_foto = bool(foto)
            p_ok = user['preguntas_usadas'] < limite_p
            i_ok = user['imagenes_usadas'] < limite_i

            if (usando_foto and i_ok) or (not usando_foto and p_ok):
                st.chat_message("user").write(texto_final)
                
                with st.spinner("El Profe está analizando..."):
                    img_bytes = foto.read() if usando_foto else None
                    contexto = buscar_contexto_icfes(texto_final, materia_seleccionada)
                    
                    respuesta = llamar_profe_saber(texto_final, contexto, img_bytes, materia=materia_seleccionada)
                    
                    if "⚠️ El Profe tuvo un problema" in respuesta or "❌ Error" in respuesta:
                        st.error(respuesta)
                        st.stop()

                    with st.chat_message("assistant"):
                        st.markdown(respuesta)
                    
                    st.session_state.mensajes_actuales.append({"role": "user", "content": texto_final})
                    st.session_state.mensajes_actuales.append({"role": "assistant", "content": respuesta})
                    
                    if not st.session_state.chat_id_actual:
                        with st.spinner("Nombrando estudio..."):
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

                    # Cobro seguro
                    if usando_foto:
                        descontar_credito(user['email'], es_imagen=True)
                        user['imagenes_usadas'] += 1
                    else:
                        descontar_credito(user['email'], es_imagen=False)
                        user['preguntas_usadas'] += 1
                    
                    st.rerun()
            else:
                st.error("⚠️ Energía insuficiente.")