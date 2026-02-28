#app.py
import streamlit as st
from datetime import datetime
from core.database import (
    obtener_datos_usuario, 
    descontar_energia, 
    guardar_o_actualizar_chat, 
    listar_chats_usuario, 
    cargar_chat_completo,
    registrar_intento_fallido,
    resetear_intentos
)
from core.rag_search import buscar_contexto_icfes
from core.ai_engine import llamar_profe_saber, generar_titulo_chat
from core.pdf_generator import generar_pdf_estudio
from core.auth import verificar_pin
import pytz

# Configuración de página
st.set_page_config(page_title="El Profe Saber", page_icon="🎓")

# --- ESTADO DE SESIÓN ---
if "autenticado" not in st.session_state: st.session_state.autenticado = False
if "chat_id_actual" not in st.session_state: st.session_state.chat_id_actual = None
if "mensajes_actuales" not in st.session_state: st.session_state.mensajes_actuales = []
if "materia_anterior" not in st.session_state: st.session_state.materia_anterior = None
if "materia_activa" not in st.session_state: st.session_state.materia_activa = "Matemáticas"
if "creditos_anteriores" not in st.session_state: st.session_state.creditos_anteriores = 0
if "recarga_notificada" not in st.session_state: st.session_state.recarga_notificada = False

if not st.session_state.autenticado:
    # --- LOGIN ---
    st.title("🎓 El Profe Saber")
    with st.form("login_form"):
        email_input = st.text_input("Correo electrónico")
        pin_input = st.text_input("PIN de acceso", type="password")
        if st.form_submit_button("Entrar a estudiar", use_container_width=True):
            user = obtener_datos_usuario(email_input)

            # Verificar bloqueo (solo si el usuario existe, sin revelar si existe)
            if user:
                bloqueado_hasta = user.get('bloqueado_hasta')
                if bloqueado_hasta:
                    ahora = datetime.now(pytz.utc)
                    bloqueo_dt = datetime.fromisoformat(bloqueado_hasta)
                    if ahora < bloqueo_dt:
                        segundos = int((bloqueo_dt - ahora).total_seconds())
                        st.error(f"🔒 Cuenta bloqueada. Espera {segundos} segundos.")
                        st.stop()
                    else:
                        resetear_intentos(email_input)
                        user = obtener_datos_usuario(email_input)

            # Verificar PIN — mensaje siempre igual sin importar si el email existe o no
            if user and verificar_pin(pin_input, user['pin']):
                resetear_intentos(email_input)
                st.session_state.user = user
                st.session_state.autenticado = True
                st.rerun()
            else:
                if user:  # Registrar intento solo si el email existe
                    intentos = registrar_intento_fallido(email_input)
                    restantes = max(0, 5 - intentos)
                    if restantes == 0:
                        st.error("🔒 Cuenta bloqueada por 2 minutos.")
                    else:
                        st.error(f"PIN o correo incorrectos. {restantes} intentos restantes.")
                else:
                    st.error("PIN o correo incorrectos.")  # Mismo mensaje, no revela si el email existe

else:
    # Recargar datos del usuario para energía en tiempo real
    user = obtener_datos_usuario(st.session_state.user['email'])
    nombre = user['email'].split('@')[0].capitalize()
    
    # Detectar si hubo recarga diaria
    creditos_actuales = user.get('creditos_totales', 0)
    if st.session_state.creditos_anteriores > 0 and creditos_actuales > st.session_state.creditos_anteriores:
        if not st.session_state.recarga_notificada:
            diferencia = creditos_actuales - st.session_state.creditos_anteriores
            st.success(f"🎉 ¡Recarga diaria! +{diferencia}⚡ créditos agregados. Total: {creditos_actuales}⚡")
            st.session_state.recarga_notificada = True
    
    # Actualizar créditos anteriores
    if creditos_actuales != st.session_state.creditos_anteriores:
        st.session_state.creditos_anteriores = creditos_actuales
    
    # --- SIDEBAR ---
    with st.sidebar:
        st.header(f"¡Ey, {nombre}! 👋")
        
        # Visualización de Energía
        creditos = user.get('creditos_totales', 0)
        color_bat = "green" if creditos > 50 else "orange" if creditos > 15 else "red"
        st.markdown(f"### 🔋 Energía: :{color_bat}[{creditos} ⚡]")
        
        # Info del plan
        plan = user.get('plan', 'básico').capitalize()
        creditos_diarios = 50 if user.get('plan') == 'basico' else 150
        st.caption(f"📦 Plan {plan} - Recarga diaria: {creditos_diarios}⚡")
        
        if st.button("➕ Nueva Conversación", use_container_width=True):
            st.session_state.chat_id_actual = None
            st.session_state.mensajes_actuales = []
            st.session_state.materia_anterior = None
            st.rerun()

        st.divider()
        
        # --- EXPORTAR PDF ---
        if st.session_state.mensajes_actuales:
            st.subheader("📥 Exportar")
            
            num_msgs = len(st.session_state.mensajes_actuales)
            st.caption(f"📊 {num_msgs} mensaje(s) en conversación")
            
            with st.expander("🔍 Ver mensajes en conversación"):
                for idx, msg in enumerate(st.session_state.mensajes_actuales):
                    rol = "👤 ESTUDIANTE" if msg.get("role") == "user" else "🤖 PROFE"
                    contenido = msg.get("content", "")
                    contenido_preview = (contenido[:150] + "...") if len(contenido) > 150 else contenido
                    st.text(f"\n{rol}:\n{contenido_preview}")
            
            try:
                m_pdf = st.session_state.get('materia_activa', 'General')
                with st.spinner("🔄 Generando PDF..."):
                    pdf_bytes = generar_pdf_estudio(st.session_state.mensajes_actuales, m_pdf)
                
                if pdf_bytes is None:
                    st.error("❌ No se pudo generar el PDF. Revisa los logs del servidor.")
                elif not isinstance(pdf_bytes, (bytes, bytearray)):
                    st.error(f"❌ Error: formato de PDF inválido. Tipo: {type(pdf_bytes)}")
                else:
                    st.download_button(
                        label="📄 Descargar Resumen PDF",
                        data=pdf_bytes,
                        file_name=f"Estudio_{m_pdf}_{datetime.now().strftime('%m%d')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    st.success(f"✅ PDF listo ({len(pdf_bytes)} bytes)")
            except Exception as e:
                st.error(f"❌ Error al generar PDF: {str(e)}")
                import traceback
                with st.expander("📋 Detalles del error"):
                    st.code(traceback.format_exc())

        st.divider()
        
        # --- HISTORIAL DE CONVERSACIONES ---
        st.subheader("📚 Historial")
        try:
            chats_response = listar_chats_usuario(st.session_state.user['email'])
            if chats_response.data:
                for chat in chats_response.data[:10]:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        if st.button(f"💬 {chat['titulo'][:25]}", key=f"chat_{chat['id']}", use_container_width=True):
                            chat_completo = cargar_chat_completo(chat['id'])
                            st.session_state.chat_id_actual = chat['id']
                            st.session_state.mensajes_actuales = chat_completo['mensajes']
                            st.session_state.materia_activa = chat_completo['materia']
                            st.session_state.materia_anterior = chat_completo['materia']
                            st.rerun()
                    with col2:
                        st.caption(f"({chat['materia'][:3]})")
            else:
                st.caption("Sin conversaciones aún.")
        except Exception:
            st.caption("No hay historial disponible.")
        
        st.divider()
        
        materias_disponibles = ["Matemáticas", "Lectura Crítica", "Sociales", "Ciencias Naturales", "Física", "Inglés"]
        try:
            materia_index = materias_disponibles.index(st.session_state.materia_activa)
        except ValueError:
            materia_index = 0
        
        materia_seleccionada = st.selectbox(
            "Materia actual:", 
            materias_disponibles,
            index=materia_index
        )
        
        # Detectar cambio de materia y limpiar conversación
        if materia_seleccionada != st.session_state.materia_anterior:
            st.session_state.materia_activa = materia_seleccionada
            st.session_state.materia_anterior = materia_seleccionada
            st.session_state.chat_id_actual = None
            st.session_state.mensajes_actuales = []
            st.rerun()

    # --- ÁREA DE CHAT ---
    for msg in st.session_state.mensajes_actuales:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # --- ENTRADA DE DUDAS ---
    st.divider()
    foto = st.file_uploader("📸 Añadir imagen (opcional)", type=['jpg', 'jpeg', 'png'])
    pregunta_input = st.chat_input("Escribe tu duda...")
    
    if pregunta_input:
        costo_base = 8 if st.session_state.materia_activa in ["Sociales", "Lectura Crítica"] else 1
        plus_foto = 5 if foto else 0
        total_a_pagar = costo_base + plus_foto

        if creditos >= total_a_pagar:
            with st.chat_message("user"):
                st.markdown(pregunta_input)
            
            with st.spinner(f"El Profe analiza ({total_a_pagar}⚡)..."):
                img_bytes = foto.read() if foto else None
                contexto = buscar_contexto_icfes(pregunta_input, st.session_state.materia_activa)
                respuesta = llamar_profe_saber(
                    pregunta_input, 
                    contexto, 
                    img_bytes, 
                    materia=st.session_state.materia_activa,
                    historial_mensajes=st.session_state.mensajes_actuales
                )
                
                if "⚠️" in respuesta:
                    st.error(respuesta)
                else:
                    st.session_state.mensajes_actuales.append({"role": "user", "content": pregunta_input})
                    st.session_state.mensajes_actuales.append({"role": "assistant", "content": respuesta})
                    
                    titulo = generar_titulo_chat(pregunta_input) if not st.session_state.chat_id_actual else "Actualizando..."
                    res_db = guardar_o_actualizar_chat(st.session_state.chat_id_actual, user['email'], titulo, st.session_state.materia_activa, st.session_state.mensajes_actuales)
                    
                    if not st.session_state.chat_id_actual:
                        st.session_state.chat_id_actual = res_db.data[0]['id']
                    
                    descontar_energia(user['email'], total_a_pagar)
                    st.rerun()
        else:
            st.error(f"Necesitas {total_a_pagar}⚡ de energía. ¡Recarga para seguir!")