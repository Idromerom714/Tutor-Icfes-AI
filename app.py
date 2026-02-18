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

st.set_page_config(page_title="El Profe Saber", page_icon="🎓")

if "autenticado" not in st.session_state: st.session_state.autenticado = False
if "chat_id_actual" not in st.session_state: st.session_state.chat_id_actual = None
if "mensajes_actuales" not in st.session_state: st.session_state.mensajes_actuales = []

if not st.session_state.autenticado:
    # ... (Mismo login que tienes)
    pass
else:
    # Recargar datos frescos del usuario
    user = obtener_datos_usuario(st.session_state.user['email'])
    nombre = user['email'].split('@')[0].capitalize()
    
    with st.sidebar:
        st.header(f"¡Ey, {nombre}! 👋")
        
        # --- MEJORA ESTÉTICA: Batería de Energía ---
        creditos = user['creditos_totales']
        color_bat = "green" if creditos > 50 else "orange" if creditos > 15 else "red"
        st.markdown(f"### 🔋 Energía: :{color_bat}[{creditos} ⚡]")
        
        if st.button("➕ Nueva Conversación", use_container_width=True):
            st.session_state.chat_id_actual = None
            st.session_state.mensajes_actuales = []
            st.rerun()

        st.divider()
        
        if st.session_state.mensajes_actuales:
            st.subheader("📥 Exportar")
            m_pdf = st.session_state.get('materia_activa', 'General')
            pdf_bytes = generar_pdf_estudio(st.session_state.mensajes_actuales, m_pdf)
            st.download_button("Descargar PDF", data=pdf_bytes, file_name=f"Estudio_{m_pdf}.pdf", use_container_width=True)

        st.divider()
        materia_seleccionada = st.selectbox("Materia actual:", ["Matemáticas", "Lectura Crítica", "Sociales", "Ciencias Naturales", "Inglés"])
        st.session_state.materia_activa = materia_seleccionada

    # 3. ENTRADA DE DUDAS
    pregunta_input = st.chat_input("Escribe tu duda...")
    foto = st.file_uploader("📸 Añadir imagen (opcional)", type=['jpg', 'jpeg', 'png'])
    enviar = st.button("🚀 Consultar al Profe", type="primary")

    if enviar or pregunta_input:
        texto_final = pregunta_input if pregunta_input else "Analice la imagen adjunta, Profe."
        
        # Lógica de costos
        costo_base = 8 if materia_seleccionada in ["Sociales", "Lectura Crítica"] else 1
        plus_foto = 5 if foto else 0
        total_a_pagar = costo_base + plus_foto

        if creditos >= total_a_pagar:
            with st.spinner(f"El Profe analiza ({total_a_pagar}⚡)..."):
                img_bytes = foto.read() if foto else None
                contexto = buscar_contexto_icfes(texto_final, materia_seleccionada)
                respuesta = llamar_profe_saber(texto_final, contexto, img_bytes, materia=materia_seleccionada)
                
                if "⚠️" in respuesta:
                    st.error(respuesta)
                else:
                    st.session_state.mensajes_actuales.append({"role": "user", "content": texto_final})
                    st.session_state.mensajes_actuales.append({"role": "assistant", "content": respuesta})
                    
                    # Persistencia
                    if not st.session_state.chat_id_actual:
                        titulo = generar_titulo_chat(texto_final)
                    else: titulo = "Actualizando..."
                    
                    res_db = guardar_o_actualizar_chat(st.session_state.chat_id_actual, user['email'], titulo, materia_seleccionada, st.session_state.mensajes_actuales)
                    if not st.session_state.chat_id_actual: st.session_state.chat_id_actual = res_db.data[0]['id']
                    
                    descontar_energia(user['email'], total_a_pagar)
                    st.rerun()
        else:
            st.error("No tienes suficiente energía para esta consulta.")