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
from core.ai_engine import llamar_profe_saber, generar_titulo_chat

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
                # Truncar título para que quepa en el botón
                titulo_corto = f"{chat['materia']}: {chat['titulo'][:15]}..."
                if st.button(titulo_corto, key=chat['id'], use_container_width=True):
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
        """)
    else:
        for msg in st.session_state.mensajes_actuales:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # 3. ENTRADA DE DUDAS (Centro de Comando)
    st.divider()
    with st.container():
        pregunta_txt = st.chat_input("Escribe tu duda aquí...")
        foto = st.file_uploader("📸 Sube una foto (opcional)", type=['jpg', 'jpeg', 'png'])
        
        col_btn1, col_btn2 = st.columns([0.7, 0.3])
        with col_btn1:
            enviar = st.button("🚀 Enviar al Profe Saber", use_container_width=True, type="primary")
        with col_btn2:
            # Botón agregado sin consulta: permite limpiar la imagen rápidamente
            if st.button("🗑️ Limpiar", use_container_width=True):
                st.rerun()

    if enviar:
        if pregunta_txt or foto:
            usando_foto = bool(foto)
            # Validación de energía
            p_ok = user['preguntas_usadas'] < limite_p
            i_ok = user['imagenes_usadas'] < limite_i

            if (usando_foto and i_ok) or (not usando_foto and p_ok):
                texto_usuario = pregunta_txt if pregunta_txt else "Profe, analice esta imagen."
                
                # Pre-visualización inmediata
                st.chat_message("user").write(texto_usuario)
                
                with st.spinner("El Profe está analizando..."):
                    img_bytes = foto.read() if usando_foto else None
                    contexto = buscar_contexto_icfes(texto_usuario, materia_seleccionada)
                    
                    # Llamada a la IA
                    respuesta = llamar_profe_saber(pregunta_txt, contexto, img_bytes, materia=materia_seleccionada)
                    
                    # --- FILTRO DE ERROR: NO COBRAR SI FALLA ---
                    if "⚠️ El Profe tuvo un problema" in respuesta or "❌ Error" in respuesta:
                        st.error(respuesta)
                        st.stop() # Aquí evitamos que el código siga y descuente el crédito

                    # Si llegamos aquí, la respuesta fue exitosa
                    with st.chat_message("assistant"):
                        st.markdown(respuesta)
                    
                    st.session_state.mensajes_actuales.append({"role": "user", "content": texto_usuario})
                    st.session_state.mensajes_actuales.append({"role": "assistant", "content": respuesta})
                    
                    # Persistencia y Título
                    if not st.session_state.chat_id_actual:
                        with st.spinner("Poniéndole nombre..."):
                            titulo_chat = generar_titulo_chat(pregunta_txt if pregunta_txt else "Análisis visual")
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

                    # --- COBRO SEGURO POST-RESPUESTA ---
                    if usando_foto:
                        descontar_credito(user['email'], es_imagen=True)
                        user['imagenes_usadas'] += 1
                    else:
                        descontar_credito(user['email'], es_imagen=False)
                        user['preguntas_usadas'] += 1
                    
                    st.rerun()
            else:
                st.error("⚠️ Energía insuficiente.")
        else:
            st.warning("Escribe algo o sube una foto antes de enviar.")