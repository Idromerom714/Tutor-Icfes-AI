import streamlit as st
from datetime import datetime
from core.database import (
    obtener_datos_usuario, 
    descontar_energia, 
    guardar_o_actualizar_chat, 
    listar_chats_usuario, 
    cargar_chat_completo,
    registrar_intento_fallido,
    resetear_intentos,
    obtener_estudiante,
    obtener_ultimo_diagnostico,
    guardar_diagnostico_estudiante,
    listar_diagnosticos_estudiante,
)
from core.rag_search import buscar_contexto_icfes
from core.ai_engine import llamar_profe_saber, generar_titulo_chat
from core.pdf_generator import generar_pdf_estudio
from core.auth import verificar_pin
from core.diagnostic import (
    obtener_preguntas_diagnostico,
    obtener_preguntas_diagnostico_adaptativo,
    evaluar_diagnostico,
    generar_semilla_diagnostico_semanal,
    diagnostico_requiere_renovacion,
    obtener_materia_prioritaria,
    dificultad_objetivo_por_materia,
    generar_preguntas_recomendadas,
    generar_plan_semanal,
)
import pytz

st.set_page_config(page_title="El Profe Saber", page_icon="🎓")

DIAGNOSTICO_CANTIDAD = 10


def construir_preguntas_diagnostico(estudiante_id, diagnostico_anterior=None):
    semilla = generar_semilla_diagnostico_semanal(str(estudiante_id) if estudiante_id else None)
    if diagnostico_anterior:
        return obtener_preguntas_diagnostico_adaptativo(
            cantidad=DIAGNOSTICO_CANTIDAD,
            diagnostico_anterior=diagnostico_anterior,
            semilla=semilla,
        )
    return obtener_preguntas_diagnostico(cantidad=DIAGNOSTICO_CANTIDAD, semilla=semilla)

# --- ESTADO DE SESIÓN ---
if "autenticado" not in st.session_state: st.session_state.autenticado = False
if "chat_id_actual" not in st.session_state: st.session_state.chat_id_actual = None
if "mensajes_actuales" not in st.session_state: st.session_state.mensajes_actuales = []
if "materia_anterior" not in st.session_state: st.session_state.materia_anterior = None
if "materia_activa" not in st.session_state: st.session_state.materia_activa = "Matemáticas"
if "estudiante" not in st.session_state: st.session_state.estudiante = None
if "diagnostico_completado" not in st.session_state: st.session_state.diagnostico_completado = False
if "diagnostico_resultado" not in st.session_state: st.session_state.diagnostico_resultado = None
if "diagnostico_preguntas" not in st.session_state: st.session_state.diagnostico_preguntas = []
if "perfil_aprendizaje" not in st.session_state: st.session_state.perfil_aprendizaje = None
if "diagnostico_creado_el" not in st.session_state: st.session_state.diagnostico_creado_el = None
if "diagnostico_anterior" not in st.session_state: st.session_state.diagnostico_anterior = None

if not st.session_state.autenticado:
    st.title("🎓 El Profe Saber")
    
    col1, col2 = st.columns([1, 1])
    with col2:
        if st.button("¿No tienes cuenta? Regístrate →", use_container_width=True):
            st.switch_page("pages/registro.py")
    
    with st.form("login_form"):
        email_input = st.text_input("Correo electrónico")
        pin_input = st.text_input("PIN de acceso", type="password")
        if st.form_submit_button("Entrar a estudiar", use_container_width=True):
            user = obtener_datos_usuario(email_input)

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

            if user and verificar_pin(pin_input, user['pin']):
                estado = user.get('estado')
                
                if estado == 'pendiente':
                    st.warning("""
                        ⏳ Tu cuenta está pendiente de activación.
                        Te contactaremos pronto para completar el pago.
                        ¿Dudas? Escríbenos a ivanromero714@gmail.com
                    """)
                elif estado == 'pendiente_renovacion':
                    st.warning("""
                        📅 Tu plan ha vencido. Para renovar escríbenos a
                        ivanromero714@gmail.com y seguirás estudiando sin interrupciones.
                    """)
                elif estado == 'suspendido':
                    st.error("🚫 Cuenta suspendida. Contacta al administrador.")
                elif estado == 'activo':
                    resetear_intentos(email_input)
                    st.session_state.user = user
                    st.session_state.autenticado = True
                    estudiante = obtener_estudiante(user['id'])
                    st.session_state.estudiante = estudiante

                    ultimo_diagnostico = None
                    if estudiante:
                        ultimo_diagnostico = obtener_ultimo_diagnostico(estudiante['id'])

                    if ultimo_diagnostico and ultimo_diagnostico.get("resultado") and not diagnostico_requiere_renovacion(ultimo_diagnostico.get("creado_el")):
                        resultado_diag = ultimo_diagnostico["resultado"]
                        st.session_state.diagnostico_resultado = resultado_diag
                        st.session_state.diagnostico_completado = True
                        st.session_state.diagnostico_preguntas = []
                        st.session_state.perfil_aprendizaje = resultado_diag
                        st.session_state.diagnostico_creado_el = ultimo_diagnostico.get("creado_el")

                        materia_prioritaria = obtener_materia_prioritaria(resultado_diag, default="Matemáticas")
                        st.session_state.materia_activa = materia_prioritaria
                        st.session_state.materia_anterior = materia_prioritaria
                    else:
                        if ultimo_diagnostico and ultimo_diagnostico.get("resultado"):
                            st.session_state.diagnostico_anterior = ultimo_diagnostico["resultado"]
                        st.session_state.diagnostico_resultado = None
                        st.session_state.diagnostico_completado = False
                        st.session_state.diagnostico_preguntas = construir_preguntas_diagnostico(
                            estudiante['id'] if estudiante else None,
                            st.session_state.get("diagnostico_anterior"),
                        )
                        st.session_state.perfil_aprendizaje = None
                        st.session_state.diagnostico_creado_el = None

                    st.rerun()
                else:
                    st.error("Estado de cuenta desconocido. Contacta al administrador.")
            else:
                if user:
                    intentos = registrar_intento_fallido(email_input)
                    restantes = max(0, 5 - intentos)
                    if restantes == 0:
                        st.error("🔒 Cuenta bloqueada por 2 minutos.")
                    else:
                        st.error(f"PIN o correo incorrectos. {restantes} intentos restantes.")
                else:
                    st.error("PIN o correo incorrectos.")

else:
    user = obtener_datos_usuario(st.session_state.user['email'])
    estudiante = st.session_state.estudiante
    nombre_estudiante = estudiante['nombre'] if estudiante else user['email'].split('@')[0].capitalize()
    historial_progreso = listar_diagnosticos_estudiante(estudiante['id'], limite=4) if estudiante else []

    if st.session_state.diagnostico_completado and diagnostico_requiere_renovacion(st.session_state.get("diagnostico_creado_el")):
        st.session_state.diagnostico_anterior = st.session_state.get("diagnostico_resultado")
        st.session_state.diagnostico_resultado = None
        st.session_state.diagnostico_completado = False
        st.session_state.diagnostico_preguntas = construir_preguntas_diagnostico(
            estudiante['id'] if estudiante else None,
            st.session_state.get("diagnostico_anterior"),
        )
        st.session_state.perfil_aprendizaje = None
        st.session_state.diagnostico_creado_el = None
        st.rerun()

    if not st.session_state.diagnostico_completado:
        if not st.session_state.diagnostico_preguntas:
            st.session_state.diagnostico_preguntas = construir_preguntas_diagnostico(
                estudiante['id'] if estudiante else None,
                st.session_state.get("diagnostico_anterior"),
            )

        titulo_diag = "🧭 Diagnóstico Semanal ICFES" if st.session_state.get("diagnostico_anterior") else "🧭 Diagnóstico Inicial ICFES"
        st.title(titulo_diag)
        st.caption(f"Responde estas {DIAGNOSTICO_CANTIDAD} preguntas para estimar tu punto de partida y crear tu plan de refuerzo semanal.")

        if st.session_state.get("diagnostico_anterior"):
            puntaje_prev = st.session_state["diagnostico_anterior"].get("porcentaje_total", 0)
            st.info(f"Seguimiento semanal: tu último puntaje fue {puntaje_prev}%. Compara tu progreso al finalizar este test.")

        with st.form("diagnostico_inicial_form"):
            for i, pregunta in enumerate(st.session_state.diagnostico_preguntas, start=1):
                st.markdown(f"**{i}. [{pregunta['materia']}] {pregunta['enunciado']}**")
                st.radio(
                    "Selecciona una opción:",
                    options=pregunta["opciones"],
                    key=f"diag_{pregunta['id']}",
                    index=None,
                )

            enviar = st.form_submit_button("Calificar diagnóstico", use_container_width=True)

            if enviar:
                respuestas = {}
                preguntas_incompletas = []

                for pregunta in st.session_state.diagnostico_preguntas:
                    respuesta = st.session_state.get(f"diag_{pregunta['id']}")
                    if respuesta is None:
                        preguntas_incompletas.append(pregunta["id"])
                    else:
                        respuestas[pregunta["id"]] = respuesta

                if preguntas_incompletas:
                    st.error("Debes responder todas las preguntas antes de calificar.")
                else:
                    resultado = evaluar_diagnostico(respuestas, st.session_state.diagnostico_preguntas)
                    st.session_state.diagnostico_resultado = resultado
                    st.session_state.diagnostico_completado = True
                    st.session_state.perfil_aprendizaje = resultado
                    st.session_state.diagnostico_creado_el = datetime.now(pytz.timezone('America/Bogota')).isoformat()

                    materia_prioritaria = obtener_materia_prioritaria(resultado, default="Matemáticas")
                    st.session_state.materia_activa = materia_prioritaria
                    st.session_state.materia_anterior = materia_prioritaria

                    if estudiante:
                        guardar_diagnostico_estudiante(estudiante['id'], user['email'], resultado)

                    if st.session_state.get("diagnostico_anterior"):
                        puntaje_prev = st.session_state["diagnostico_anterior"].get("porcentaje_total", 0)
                        delta = round(resultado.get("porcentaje_total", 0) - puntaje_prev, 2)
                        st.success(f"Diagnóstico semanal completado. Variación frente a la semana pasada: {delta:+} puntos.")
                    else:
                        st.success("Diagnóstico completado. Ya puedes empezar a estudiar con un plan personalizado.")
                    st.rerun()

        st.stop()

    # --- SIDEBAR ---
    with st.sidebar:
        st.header(f"¡Ey, {nombre_estudiante}! 👋")

        resultado_diag = st.session_state.get("diagnostico_resultado")
        if resultado_diag:
            porcentaje_diag = resultado_diag.get("porcentaje_total", 0)
            st.caption(f"🧭 Diagnóstico inicial: {porcentaje_diag}%")
            with st.expander("Ver plan de refuerzo"):
                for recomendacion in resultado_diag.get("recomendaciones", []):
                    st.write(f"- {recomendacion}")

            preguntas_recomendadas = generar_preguntas_recomendadas(
                resultado_diag,
                st.session_state.get("materia_activa", "Matemáticas"),
                max_preguntas=3,
            )
            with st.expander("💬 Preguntas recomendadas para hoy"):
                for sugerencia in preguntas_recomendadas:
                    st.write(f"- {sugerencia}")

            plan_semanal = generar_plan_semanal(resultado_diag)
            with st.expander("🗓️ Plan semanal sugerido"):
                for bloque in plan_semanal:
                    st.write(f"**{bloque['dia']} · {bloque['materia']}**")
                    st.caption(f"Objetivo: {bloque['objetivo']}")
                    st.caption(f"Actividad: {bloque['actividad']}")

            with st.expander("🎚️ Nivel recomendado por materia"):
                iconos_dificultad = {
                    "basico": "🟢 Básico",
                    "intermedio": "🟡 Intermedio",
                    "avanzado": "🔴 Avanzado",
                }
                for item in resultado_diag.get("resultados_por_materia", []):
                    materia = item.get("materia", "General")
                    nivel = dificultad_objetivo_por_materia(resultado_diag, materia)
                    st.write(f"- {materia}: {iconos_dificultad.get(nivel, nivel)}")

            with st.expander("📈 Progreso semanal (últimas 4 semanas)"):
                if historial_progreso:
                    historial_asc = list(reversed(historial_progreso))
                    puntajes = [float(item.get("puntaje", 0)) for item in historial_asc]
                    labels = []
                    for item in historial_asc:
                        creado = item.get("creado_el", "")
                        try:
                            fecha = datetime.fromisoformat(creado.replace("Z", "+00:00")).strftime("%d/%m")
                        except Exception:
                            fecha = "s/f"
                        labels.append(fecha)

                    st.line_chart({"Puntaje": puntajes})

                    tendencia = "estable"
                    if len(puntajes) >= 2:
                        delta = round(puntajes[-1] - puntajes[0], 2)
                        if delta > 0:
                            tendencia = f"en alza (+{delta} pts)"
                        elif delta < 0:
                            tendencia = f"a la baja ({delta} pts)"
                        else:
                            tendencia = "estable (0 pts)"
                    st.caption(f"Tendencia general: {tendencia}")

                    for i, score in enumerate(puntajes):
                        st.write(f"Semana {i + 1} ({labels[i]}): {score}%")
                else:
                    st.caption("Aún no hay suficiente historial semanal.")
        else:
            st.caption("🧭 Diagnóstico inicial pendiente")
        
        creditos = user.get('creditos_totales', 0)
        fecha_venc = user.get('fecha_vencimiento', '')
        color_bat = "green" if creditos > 500 else "orange" if creditos > 100 else "red"
        st.markdown(f"### 🔋 Energía: :{color_bat}[{creditos} ⚡]")
        
        plan = user.get('plan', 'basico').capitalize()
        st.caption(f"📦 Plan {plan} | Vence: {fecha_venc}")
        
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
                    st.error("❌ No se pudo generar el PDF.")
                elif not isinstance(pdf_bytes, (bytes, bytearray)):
                    st.error(f"❌ Error: formato de PDF inválido.")
                else:
                    st.download_button(
                        label="📄 Descargar Resumen PDF",
                        data=pdf_bytes,
                        file_name=f"Estudio_{m_pdf}_{datetime.now().strftime('%m%d')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
            except Exception as e:
                st.error(f"❌ Error al generar PDF: {str(e)}")

        st.divider()
        
        # --- HISTORIAL ---
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
                    historial_mensajes=st.session_state.mensajes_actuales,
                    diagnostico_resultado=st.session_state.get("perfil_aprendizaje"),
                    nivel_recomendado=dificultad_objetivo_por_materia(
                        st.session_state.get("perfil_aprendizaje"),
                        st.session_state.materia_activa,
                    ),
                )
                
                if "⚠️" in respuesta:
                    st.error(respuesta)
                else:
                    st.session_state.mensajes_actuales.append({"role": "user", "content": pregunta_input})
                    st.session_state.mensajes_actuales.append({"role": "assistant", "content": respuesta})
                    
                    titulo = generar_titulo_chat(pregunta_input) if not st.session_state.chat_id_actual else "Actualizando..."
                    res_db = guardar_o_actualizar_chat(
                        st.session_state.chat_id_actual, 
                        user['email'], 
                        titulo, 
                        st.session_state.materia_activa, 
                        st.session_state.mensajes_actuales,
                        estudiante_id=st.session_state.estudiante['id'] if st.session_state.estudiante else None
                            )
                    if not st.session_state.chat_id_actual:
                        st.session_state.chat_id_actual = res_db.data[0]['id']
                    
                    descontar_energia(user['email'], total_a_pagar)
                    st.rerun()
        else:
            st.error(f"Sin energía suficiente. Necesitas {total_a_pagar}⚡ | Tienes {creditos}⚡")