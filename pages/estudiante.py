# pages/estudiante.py
import streamlit as st
from datetime import datetime
import pytz

from core.auth import verificar_pin, hashear_pin
from core.database import (
    obtener_datos_usuario,
    obtener_estudiante,
    listar_estudiantes,
    descontar_energia,
    registrar_consumo_energia,
    guardar_o_actualizar_chat,
    listar_chats_usuario,
    cargar_chat_completo,
    registrar_intento_fallido,
    resetear_intentos,
)
from core.rag_search import buscar_contexto_icfes
from core.ai_engine import llamar_profe_saber, generar_titulo_chat
from core.pdf_generator import generar_pdf_estudio
from core.diagnostic import (
    obtener_preguntas_diagnostico,
    obtener_preguntas_diagnostico_adaptativo,
    evaluar_diagnostico,
    obtener_ultimo_diagnostico,
    guardar_diagnostico,
    guardar_respuestas,
    generar_plan_semanal,
    obtener_materia_prioritaria,
    generar_preguntas_recomendadas,
    diagnostico_requiere_renovacion,
)
from core.ads import render_adsense_slot_from_env

st.set_page_config(page_title="El Profe Saber — Estudiante", page_icon="🎓")


def _render_html(content: str) -> None:
    if hasattr(st, "html"):
        st.html(content)
    else:
        st.markdown(content, unsafe_allow_html=True)


def _inject_theme_styles() -> None:
    _render_html(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,700;9..144,900&family=DM+Sans:wght@400;500;700&display=swap');

:root {
    --azul: #0d2d4e;
    --azul-m: #1a5080;
    --naranja: #e8600a;
    --acento: #1a5080;
    --crema: #f5f0e8;
    --hueso: #ede8de;
    --tinta: #0d1f2d;
    --gris: #5a7080;
}

.stApp {
    background: radial-gradient(circle at 100% 0%, rgba(26,80,128,0.09), transparent 32%), var(--crema);
    font-family: 'DM Sans', sans-serif;
    color: var(--tinta);
}

h1, h2, h3 {
    font-family: 'Fraunces', serif !important;
    color: var(--azul) !important;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b2743 0%, #113a5f 100%);
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
    color: #f5f0e8 !important;
}

[data-testid="stChatMessage"] {
    border-radius: 12px;
    border: 1px solid rgba(13,45,78,0.11);
    background: #fff;
}

[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"],
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] span {
    color: #0d1f2d !important;
}

[data-testid="stChatMessage"] a {
    color: #0b4f87 !important;
    text-decoration: underline;
}

[data-testid="stChatMessage"] code {
    color: #0b2844 !important;
    background: #ecf3fa;
    border-radius: 4px;
    padding: 0.1rem 0.28rem;
}

[data-testid="stChatMessage"] pre code {
    color: #0d1f2d !important;
    background: #f2f7fc;
}

[data-testid="stChatMessage"][aria-label="Chat message from assistant"] {
    border-left: 4px solid var(--acento);
}

[data-testid="stForm"] {
    background: #fff;
    border: 1px solid rgba(13,45,78,0.14);
    border-radius: 14px;
    padding: 1rem 1rem 1.2rem;
}

.stButton > button,
[data-testid="stFormSubmitButton"] > button,
[data-testid="stDownloadButton"] > button {
    background: var(--acento) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    box-shadow: 0 6px 18px rgba(26,80,128,0.30) !important;
}

.stButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover,
[data-testid="stDownloadButton"] > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 10px 24px rgba(26,80,128,0.38) !important;
}

div[data-baseweb="input"] input,
div[data-baseweb="select"] > div,
div[data-baseweb="textarea"] textarea {
    border-radius: 10px !important;
    border: 1px solid rgba(13,45,78,0.2) !important;
}

[data-testid="stFileUploader"] {
    background: #fff;
    border: 1px dashed rgba(13,45,78,0.35);
    border-radius: 12px;
    padding: 0.4rem;
}

[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"] {
    background: #fdfbf8;
    border: 1px dashed rgba(13,45,78,0.4);
}

[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInstructions"] > div {
    display: none;
}

[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInstructions"]::before {
    content: "Arrastra y suelta tu imagen aquí";
    display: block;
    color: var(--azul);
    font-weight: 700;
    text-align: center;
    margin-bottom: 0.2rem;
}

[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInstructions"]::after {
    content: "o usa el botón para elegir un archivo";
    display: block;
    color: #1f3f5e;
    font-size: 0.92rem;
    text-align: center;
}

[data-testid="stFileUploader"] button[kind="secondary"] p {
    font-size: 0;
}

[data-testid="stFileUploader"] button[kind="secondary"] p::after {
    content: "Elegir imagen";
    font-size: 0.95rem;
    color: #0d2d4e;
    font-weight: 700;
}
</style>
        """
    )

# ─────────────────────────────────────────────────────────────────────────────
# ESTADO DE SESIÓN
# ─────────────────────────────────────────────────────────────────────────────

def _init_session():
    defaults = {
        "autenticado":          False,
        "user":                 None,
        "estudiante":           None,
        "chat_id_actual":       None,
        "mensajes_actuales":    [],
        "materia_activa":       "Matemáticas",
        "materia_anterior":     None,
        "uploader_nonce":       0,
        # Diagnóstico
        "modo_diagnostico":     False,
        "preguntas_diag":       [],      # sin respuesta_correcta (para mostrar)
        "preguntas_diag_full":  [],      # con respuesta_correcta (para evaluar)
        "respuestas_diag":      {},      # {pregunta_id: opcion_elegida}
        "resultado_diag":       None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_session()
_inject_theme_styles()

# ─────────────────────────────────────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────────────────────────────────────

def _logout():
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()


def _render_login():
    st.title("🎓 El Profe Saber")
    st.caption("Inicia sesión con el correo del padre y tu PIN de estudiante.")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("¿No tienes cuenta? Regístrate →", use_container_width=True):
            st.switch_page("pages/presentacion.py")
    with col2:
        if st.button("Panel del padre →", use_container_width=True):
            st.switch_page("app.py")
    with col3:
        if st.button("Ver presentación →", use_container_width=True):
            st.switch_page("pages/presentacion.py")

    with st.form("login_estudiante"):
        email_padre = st.text_input("Correo del padre")
        pin_input   = st.text_input("Tu PIN", type="password")
        entrar      = st.form_submit_button("Entrar a estudiar", use_container_width=True)

    if not entrar:
        return

    user = obtener_datos_usuario(email_padre)
    if not user:
        st.error("Correo o PIN incorrectos.")
        return

    # Bloqueo por intentos
    bloqueado_hasta = user.get("bloqueado_hasta")
    if bloqueado_hasta:
        ahora = datetime.now(pytz.utc)
        try:
            bloqueo_dt = datetime.fromisoformat(bloqueado_hasta)
            if ahora < bloqueo_dt:
                segundos = int((bloqueo_dt - ahora).total_seconds())
                st.error(f"🔒 Cuenta bloqueada. Espera {segundos} segundos.")
                return
            resetear_intentos(email_padre)
            user = obtener_datos_usuario(email_padre)
        except Exception:
            pass

    # Verificar estado de la cuenta padre
    estado = user.get("estado")
    if estado == "pendiente":
        st.warning("⏳ Cuenta pendiente de activación. Contacta al administrador.")
        return
    if estado == "pendiente_renovacion":
        st.warning("📅 Plan vencido. Escríbenos para renovar.")
        return
    if estado == "suspendido":
        st.error("🚫 Cuenta suspendida.")
        return
    if estado != "activo":
        st.error("Estado de cuenta desconocido.")
        return

    # Buscar estudiante por PIN
    estudiantes = listar_estudiantes(user["id"])
    estudiante_encontrado = None
    for est in estudiantes:
        pin_hash = est.get("pin_hash") or est.get("pin")
        if pin_hash and verificar_pin(pin_input, pin_hash):
            estudiante_encontrado = est
            break

    # Fallback: el padre puede entrar con su propio PIN
    if not estudiante_encontrado:
        if verificar_pin(pin_input, user["pin"]):
            estudiante_encontrado = obtener_estudiante(user["id"])

    if not estudiante_encontrado:
        intentos = registrar_intento_fallido(email_padre)
        restantes = max(0, 5 - (intentos or 0))
        if restantes == 0:
            st.error("🔒 Cuenta bloqueada por 2 minutos.")
        else:
            st.error(f"PIN incorrecto. {restantes} intentos restantes.")
        return

    resetear_intentos(email_padre)
    st.session_state.autenticado = True
    st.session_state.user        = user
    st.session_state.estudiante  = estudiante_encontrado
    st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# DIAGNÓSTICO
# ─────────────────────────────────────────────────────────────────────────────

def _debe_hacer_diagnostico() -> bool:
    """True si el estudiante nunca ha hecho diagnóstico o ya venció."""
    est = st.session_state.estudiante
    if not est:
        return False
    diag = obtener_ultimo_diagnostico(est["id"])
    if not diag:
        return True
    return diagnostico_requiere_renovacion(diag.get("fecha") or diag.get("creado_el"))


def _iniciar_diagnostico():
    """Carga las preguntas y activa el modo diagnóstico."""
    est       = st.session_state.estudiante
    diag_ant  = obtener_ultimo_diagnostico(est["id"]) if est else None

    if diag_ant:
        preguntas_full = obtener_preguntas_diagnostico_adaptativo(
            cantidad=12,
            estudiante_id=str(est["id"]),
            diagnostico_anterior_id=str(diag_ant["id"]),
            incluir_respuestas=True,
        )
    else:
        preguntas_full = obtener_preguntas_diagnostico(
            cantidad=12,
            estudiante_id=str(est["id"]),
            incluir_respuestas=True,
        )

    # Separar versión completa (para evaluar) de la versión limpia (para mostrar)
    st.session_state.preguntas_diag_full = preguntas_full
    st.session_state.preguntas_diag      = [
        {k: v for k, v in p.items() if k not in ("respuesta_correcta", "explicacion")}
        for p in preguntas_full
    ]
    st.session_state.respuestas_diag  = {}
    st.session_state.resultado_diag   = None
    st.session_state.modo_diagnostico = True
    st.rerun()


def _render_diagnostico():
    """Muestra el formulario de preguntas diagnósticas."""
    preguntas = st.session_state.preguntas_diag
    respuestas = st.session_state.respuestas_diag

    st.title("📋 Diagnóstico inicial")
    st.caption(
        "Responde estas preguntas para que el tutor conozca tu nivel. "
        "No afectan tus créditos."
    )
    st.progress(
        len(respuestas) / len(preguntas) if preguntas else 0,
        text=f"{len(respuestas)}/{len(preguntas)} respondidas",
    )
    st.divider()

    for i, p in enumerate(preguntas):
        pid = str(p["id"])
        st.markdown(f"**{i+1}. {p['enunciado']}**")
        st.caption(f"_{p['materia']} · {p.get('subtema', p.get('tema', ''))} · {p.get('dificultad','').capitalize()}_")

        opciones = p["opciones"]
        letras   = ["A", "B", "C", "D"]
        opciones_display = [f"{letras[j]}) {opciones[j]}" for j in range(len(opciones))]

        seleccion = st.radio(
            label=f"Pregunta {i+1}",
            options=opciones_display,
            index=None,
            key=f"diag_{pid}",
            label_visibility="collapsed",
        )

        if seleccion:
            letra_elegida = seleccion[0]  # "A", "B", "C" o "D"
            respuestas[pid] = letra_elegida
            st.session_state.respuestas_diag = respuestas

        st.divider()

    todas_respondidas = len(respuestas) == len(preguntas)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⏭ Omitir diagnóstico", use_container_width=True):
            st.session_state.modo_diagnostico = False
            st.rerun()
    with col2:
        enviar = st.button(
            "✅ Enviar respuestas",
            use_container_width=True,
            disabled=not todas_respondidas,
        )

    if enviar and todas_respondidas:
        _procesar_diagnostico()


def _procesar_diagnostico():
    """Evalúa, guarda y muestra resultados del diagnóstico."""
    preguntas_full = st.session_state.preguntas_diag_full
    respuestas     = st.session_state.respuestas_diag
    est            = st.session_state.estudiante

    resultado = evaluar_diagnostico(respuestas, preguntas_full)
    resultado["preguntas_ids"] = [str(p["id"]) for p in preguntas_full]

    # Guardar en Supabase
    diag_id = guardar_diagnostico(
        estudiante_id=str(est["id"]),
        preguntas_ids=resultado["preguntas_ids"],
        resultado=resultado,
    )
    if diag_id:
        guardar_respuestas(diag_id, str(est["id"]), preguntas_full, respuestas)

    st.session_state.resultado_diag   = resultado
    st.session_state.modo_diagnostico = False

    # Materia prioritaria para iniciar el chat
    materia_prio = obtener_materia_prioritaria(resultado)
    st.session_state.materia_activa   = materia_prio
    st.session_state.materia_anterior = materia_prio
    st.rerun()


def _render_resultado_diagnostico():
    """Muestra el resumen del diagnóstico justo terminado."""
    resultado = st.session_state.resultado_diag

    st.success("✅ ¡Diagnóstico completado!")
    st.metric("Puntaje global", f"{resultado['porcentaje_total']}%")

    st.subheader("Resultados por materia")
    for r in resultado["resultados_por_materia"]:
        emoji = "🟢" if r["porcentaje"] >= 75 else "🟡" if r["porcentaje"] >= 45 else "🔴"
        st.markdown(
            f"{emoji} **{r['materia']}**: {r['porcentaje']}%  "
            f"({r['aciertos']}/{r['total']})"
        )
        if r.get("subtemas_reforzar"):
            st.caption(f"   Reforzar: {', '.join(r['subtemas_reforzar'][:3])}")

    st.subheader("📅 Plan semanal sugerido")
    plan = generar_plan_semanal(resultado)
    for dia in plan[:4]:
        st.markdown(f"**{dia['dia']}** · {dia['materia']}: {dia['objetivo']}")

    if st.button("🚀 Ir al chat a estudiar", use_container_width=True):
        st.session_state.resultado_diag = None
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# CHAT
# ─────────────────────────────────────────────────────────────────────────────

def _render_sidebar(user, estudiante):
    nombre = estudiante["nombre"] if estudiante else user["email"].split("@")[0].capitalize()

    with st.sidebar:
        st.header(f"¡Ey, {nombre}! 👋")

        creditos    = user.get("creditos_totales", 0)
        fecha_venc  = user.get("fecha_vencimiento", "")
        color_bat   = "green" if creditos > 500 else "orange" if creditos > 100 else "red"
        st.markdown(f"### 🔋 Energía: :{color_bat}[{creditos} ⚡]")
        st.caption(f"📦 Plan {user.get('plan','basico').capitalize()} | Vence: {fecha_venc}")

        # Diagnóstico
        st.divider()
        diag = obtener_ultimo_diagnostico(estudiante["id"]) if estudiante else None
        if diag:
            puntaje = diag.get("porcentaje_total", 0)
            st.caption(f"📊 Último diagnóstico: **{puntaje}%**")
        if st.button("📋 Hacer diagnóstico", use_container_width=True):
            _iniciar_diagnostico()

        st.divider()

        # Nueva conversación
        if st.button("➕ Nueva conversación", use_container_width=True):
            st.session_state.chat_id_actual  = None
            st.session_state.mensajes_actuales = []
            st.session_state.materia_anterior  = None
            st.rerun()

        # Exportar PDF
        if st.session_state.mensajes_actuales:
            st.subheader("📥 Exportar")
            try:
                m_pdf = st.session_state.materia_activa
                with st.spinner("Generando PDF..."):
                    pdf_bytes = generar_pdf_estudio(st.session_state.mensajes_actuales, m_pdf)
                if pdf_bytes and isinstance(pdf_bytes, (bytes, bytearray)):
                    st.download_button(
                        label="📄 Descargar PDF",
                        data=pdf_bytes,
                        file_name=f"Estudio_{m_pdf}_{datetime.now().strftime('%m%d')}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
            except Exception as e:
                st.error(f"Error al generar PDF: {e}")

        st.divider()

        # Historial
        st.subheader("📚 Historial")
        try:
            chats = listar_chats_usuario(
                user["email"],
                estudiante_id=estudiante["id"] if estudiante else None,
            )
            if chats.data:
                for chat in chats.data[:10]:
                    c1, c2 = st.columns([4, 1])
                    with c1:
                        if st.button(f"💬 {chat['titulo'][:25]}", key=f"chat_{chat['id']}", use_container_width=True):
                            completo = cargar_chat_completo(chat["id"])
                            st.session_state.chat_id_actual    = chat["id"]
                            st.session_state.mensajes_actuales = completo["mensajes"]
                            st.session_state.materia_activa    = completo["materia"]
                            st.session_state.materia_anterior  = completo["materia"]
                            st.rerun()
                    with c2:
                        st.caption(f"({chat['materia'][:3]})")
            else:
                st.caption("Sin conversaciones aún.")
        except Exception:
            st.caption("No hay historial disponible.")

        st.divider()

        # Selector de materia
        materias = ["Matemáticas", "Lectura Crítica", "Sociales y Ciudadanas", "Ciencias Naturales", "Inglés"]
        try:
            idx = materias.index(st.session_state.materia_activa)
        except ValueError:
            idx = 0

        materia_sel = st.selectbox("Materia:", materias, index=idx)
        if materia_sel != st.session_state.materia_anterior:
            st.session_state.materia_activa   = materia_sel
            st.session_state.materia_anterior = materia_sel
            st.session_state.chat_id_actual   = None
            st.session_state.mensajes_actuales = []
            st.rerun()

        st.divider()
        if render_adsense_slot_from_env("ADSENSE_SLOT_ESTUDIANTE", min_height=130):
            st.caption("Publicidad")

        st.divider()
        if st.button("🚪 Cerrar sesión", use_container_width=True):
            _logout()

    return user.get("creditos_totales", 0)


def _render_chat(user, estudiante, creditos):
    st.title("🎓 El Profe Saber")

    # Sugerencias del diagnóstico si es primera vez
    resultado_diag = obtener_ultimo_diagnostico(
        estudiante["id"] if estudiante else None
    ) if estudiante else None

    if resultado_diag and not st.session_state.mensajes_actuales:
        sugerencias = generar_preguntas_recomendadas(
            resultado_diag.get("resultados_por_materia") and resultado_diag,
            st.session_state.materia_activa,
        )
        if sugerencias:
            st.caption("💡 Sugerencias basadas en tu diagnóstico:")
            for s in sugerencias:
                if st.button(s, use_container_width=True):
                    st.session_state._sugerencia_elegida = s
                    st.rerun()

    # Mensajes previos
    for msg in st.session_state.mensajes_actuales:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    st.divider()
    st.markdown("**📸 Carga una imagen (opcional)**")
    st.caption("Formatos permitidos: JPG, JPEG y PNG.")
    foto          = st.file_uploader(
        "Carga una imagen para acompañar tu pregunta",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed",
        key=f"foto_chat_{st.session_state.uploader_nonce}",
    )
    pregunta_input = st.chat_input("Escribe tu duda...")

    # Sugerencia clickeada
    if hasattr(st.session_state, "_sugerencia_elegida"):
        pregunta_input = st.session_state._sugerencia_elegida
        del st.session_state._sugerencia_elegida

    if not pregunta_input:
        return

    materia      = st.session_state.materia_activa
    costo_base   = 8 if materia in ["Sociales y Ciudadanas", "Lectura Crítica"] else 1
    plus_foto    = 5 if foto else 0
    total_costo  = costo_base + plus_foto

    if creditos < total_costo:
        st.error(f"Sin energía suficiente. Necesitas {total_costo}⚡ | Tienes {creditos}⚡")
        return

    with st.chat_message("user"):
        st.markdown(pregunta_input)

    with st.spinner(f"El Profe analiza ({total_costo}⚡)..."):
        img_bytes = foto.read() if foto else None
        contexto  = buscar_contexto_icfes(pregunta_input, materia)
        respuesta = llamar_profe_saber(
            pregunta_input,
            contexto,
            img_bytes,
            materia=materia,
            historial_mensajes=st.session_state.mensajes_actuales,
        )

    if "⚠️" in respuesta:
        st.error(respuesta)
        return

    st.session_state.mensajes_actuales.append({"role": "user",      "content": pregunta_input})
    st.session_state.mensajes_actuales.append({"role": "assistant", "content": respuesta})

    if foto:
        st.session_state.uploader_nonce += 1

    titulo = generar_titulo_chat(pregunta_input) if not st.session_state.chat_id_actual else None
    res_db = guardar_o_actualizar_chat(
        st.session_state.chat_id_actual,
        user["email"],
        titulo,
        materia,
        st.session_state.mensajes_actuales,
        estudiante_id=estudiante["id"] if estudiante else None,
    )
    if not st.session_state.chat_id_actual and res_db.data:
        st.session_state.chat_id_actual = res_db.data[0]["id"]

    descontar_energia(user["email"], total_costo)
    registrar_consumo_energia(
        user["email"],
        estudiante["id"] if estudiante else None,
        total_costo,
        materia=materia,
    )
    st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

if not st.session_state.autenticado:
    _render_login()
else:
    user       = obtener_datos_usuario(st.session_state.user["email"])
    estudiante = st.session_state.estudiante

    # Diagnóstico pendiente (primera vez o venció la semana)
    if _debe_hacer_diagnostico() and not st.session_state.modo_diagnostico:
        st.info("📋 Antes de estudiar, hagamos un diagnóstico rápido para personalizar tu plan.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 Hacer diagnóstico ahora", use_container_width=True):
                _iniciar_diagnostico()
        with col2:
            if st.button("Omitir por ahora", use_container_width=True):
                pass  # Continúa al chat

    elif st.session_state.modo_diagnostico:
        _render_diagnostico()

    elif st.session_state.resultado_diag:
        _render_resultado_diagnostico()

    else:
        creditos = _render_sidebar(user, estudiante)
        _render_chat(user, estudiante, creditos)