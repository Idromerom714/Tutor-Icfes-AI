# app.py
import streamlit as st
from datetime import datetime, timedelta

from core.auth import hashear_pin, verificar_pin
from core.database import (
    obtener_datos_usuario,
    resetear_intentos,
    registrar_intento_fallido,
    listar_estudiantes,
    contar_estudiantes_padre,
    crear_estudiante,
    obtener_ultimo_diagnostico,
    listar_diagnosticos_estudiante,
    listar_chats_usuario,
    listar_consumo_energia,
)
from core.ads import render_adsense_slot_from_env

st.set_page_config(page_title="Panel Padre - El Profe Saber", page_icon="👨‍👩‍👧")


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
    --acento: #e8600a;
    --crema: #f5f0e8;
    --hueso: #ede8de;
    --tinta: #0d1f2d;
    --gris: #5a7080;
}

.stApp {
    background: radial-gradient(circle at 10% -10%, rgba(232,96,10,0.1), transparent 40%), var(--crema);
    font-family: 'DM Sans', sans-serif;
    color: var(--tinta);
}

h1, h2, h3 {
    font-family: 'Fraunces', serif !important;
    color: var(--azul) !important;
}

section[data-testid="stSidebar"] {
    display: block !important;
    visibility: visible !important;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b2743 0%, #113a5f 100%);
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] li,
[data-testid="stSidebar"] a,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
[data-testid="stSidebar"] [data-testid="stWidgetLabel"],
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] * {
    color: #f5f0e8 !important;
    opacity: 1 !important;
    visibility: visible !important;
}

[data-testid="stForm"] {
    background: #fff;
    border: 1px solid rgba(13,45,78,0.14);
    border-radius: 14px;
    padding: 1rem 1rem 1.2rem;
}

/* Evita que estilos de otras páginas dejen invisibles los labels del formulario. */
[data-testid="stForm"] label,
[data-testid="stForm"] [data-testid="stWidgetLabel"],
[data-testid="stForm"] [data-testid="stWidgetLabel"] div,
[data-testid="stForm"] [data-testid="stWidgetLabel"] p,
[data-testid="stForm"] [data-testid="stWidgetLabel"] span,
[data-testid="stForm"] .stTextInput label,
[data-testid="stForm"] .stSelectbox label,
[data-testid="stForm"] .stNumberInput label,
[data-testid="stForm"] .stTextArea label,
[data-testid="stForm"] .stCheckbox label {
    color: var(--azul) !important;
    opacity: 1 !important;
    visibility: visible !important;
}

.stButton > button,
[data-testid="stFormSubmitButton"] > button {
    background: var(--acento) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    box-shadow: 0 6px 18px rgba(232,96,10,0.28) !important;
}

.stButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 10px 24px rgba(232,96,10,0.34) !important;
}

[data-testid="stCaptionContainer"] p {
    color: var(--azul-m) !important;
}

div[data-baseweb="input"] input,
div[data-baseweb="select"] > div {
    border-radius: 10px !important;
    border: 1px solid rgba(13,45,78,0.2) !important;
}

[data-testid="stMetric"] {
    background: #fff;
    border: 1px solid rgba(13,45,78,0.12);
    border-radius: 12px;
    padding: 0.5rem 0.7rem;
}

[data-testid="stDataFrame"] {
    border: 1px solid rgba(13,45,78,0.1);
    border-radius: 10px;
    overflow: hidden;
}
</style>
        """
    )


def _init_parent_session():
    if "parent_autenticado" not in st.session_state:
        st.session_state.parent_autenticado = False
    if "parent_email" not in st.session_state:
        st.session_state.parent_email = None


def _logout_parent():
    st.session_state.parent_autenticado = False
    st.session_state.parent_email = None
    st.rerun()


def _fecha_legible(iso_str):
    try:
        return datetime.fromisoformat(iso_str.replace("Z", "+00:00")).strftime("%d/%m")
    except Exception:
        return "s/f"


def _render_login_padre():
    st.title("👨‍👩‍👧 Panel del Padre")
    st.caption("Centro de control para crear hijos, revisar progreso y monitorear consumo de energía.")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📝 Ir a Registro", use_container_width=True):
            st.switch_page("pages/presentacion.py")
    with col2:
        if st.button("🎓 Entrada Estudiantes", use_container_width=True):
            st.switch_page("pages/estudiante.py")
    with col3:
        if st.button("🚀 Ver Presentacion", use_container_width=True):
            st.switch_page("pages/presentacion.py")

    with st.form("parent_login_form"):
        email = st.text_input("Correo del padre")
        pin = st.text_input("PIN del padre", type="password")
        entrar = st.form_submit_button("Entrar al panel", use_container_width=True)

    if not entrar:
        return

    user = obtener_datos_usuario(email)
    if not user:
        st.error("Correo o PIN incorrectos.")
        return

    bloqueado_hasta = user.get("bloqueado_hasta")
    if bloqueado_hasta:
        ahora = datetime.now().astimezone()
        try:
            bloqueo_dt = datetime.fromisoformat(bloqueado_hasta)
            if ahora < bloqueo_dt:
                segundos = int((bloqueo_dt - ahora).total_seconds())
                st.error(f"🔒 Cuenta bloqueada. Espera {segundos} segundos.")
                return
            resetear_intentos(email)
            user = obtener_datos_usuario(email)
        except Exception:
            pass

    if not verificar_pin(pin, user["pin"]):
        intentos = registrar_intento_fallido(email)
        restantes = max(0, 5 - (intentos or 0))
        if restantes == 0:
            st.error("🔒 Cuenta bloqueada por 2 minutos.")
        else:
            st.error(f"Correo o PIN incorrectos. {restantes} intentos restantes.")
        return

    if user.get("estado") != "activo":
        st.warning("Tu cuenta no esta activa. Contacta al administrador.")
        return

    resetear_intentos(email)
    st.session_state.parent_autenticado = True
    st.session_state.parent_email = email
    st.rerun()


def _render_sidebar(user):
    with st.sidebar:
        st.header("Panel Padre")
        st.caption(f"👤 {user.get('nombre', user['email'])}")
        creditos = user.get("creditos_totales", 0)
        st.markdown(f"### ⚡ Energia disponible: {creditos}")
        st.caption(f"📦 Plan: {user.get('plan', 'basico').capitalize()}")

        st.divider()
        if st.button("🎓 Ir a Entrada Estudiantes", use_container_width=True):
            st.switch_page("pages/estudiante.py")
        if st.button("📝 Ir a Registro", use_container_width=True):
            st.switch_page("pages/presentacion.py")
        if st.button("🚀 Ver Presentacion", use_container_width=True):
            st.switch_page("pages/presentacion.py")

        if render_adsense_slot_from_env("ADSENSE_SLOT_APP", min_height=130):
            st.caption("Publicidad")

        if st.button("🚪 Cerrar sesion", use_container_width=True):
            _logout_parent()


def _render_crear_hijo(user):
    st.subheader("➕ Crear nuevo hijo")

    plan = str(user.get("plan", "basico") or "basico").strip().lower()
    es_plan_familiar = plan == "familia"
    max_hijos_familiar = 3
    total_actual = contar_estudiantes_padre(user["id"])

    if es_plan_familiar and total_actual >= max_hijos_familiar:
        st.info("Tu plan Familiar permite hasta 3 hijos. Ya alcanzaste el limite.")
        return

    if not es_plan_familiar and total_actual >= 1:
        st.info(
            "Tu plan actual permite 1 hijo. Para agregar varios hijos, cambia al plan Familiar."
        )
        return

    with st.form("form_nuevo_hijo_dashboard"):
        nombre = st.text_input("Nombre del hijo")
        grado = st.selectbox("Grado", ["10°", "11°"])
        pin_hijo = st.text_input("PIN del hijo (minimo 4 digitos)", type="password")
        pin_hijo_confirm = st.text_input("Confirmar PIN del hijo", type="password")
        crear = st.form_submit_button("Crear hijo", use_container_width=True)

    if not crear:
        return

    if not nombre.strip():
        st.error("El nombre del hijo es obligatorio.")
        return
    if len(pin_hijo) < 4:
        st.error("El PIN del hijo debe tener minimo 4 digitos.")
        return
    if pin_hijo != pin_hijo_confirm:
        st.error("Los PIN del hijo no coinciden.")
        return

    try:
        total_antes = contar_estudiantes_padre(user["id"])

        if es_plan_familiar and total_antes >= max_hijos_familiar:
            st.error("Tu plan Familiar permite hasta 3 hijos. Ya alcanzaste el limite.")
            return

        if not es_plan_familiar and total_antes >= 1:
            st.error(
                "Tu plan actual permite 1 hijo. Solo el plan Familiar permite crear varios hijos."
            )
            return

        pin_hash = hashear_pin(pin_hijo)
        res = crear_estudiante(user["id"], nombre.strip(), grado, pin_hash=pin_hash)
        nuevo = (res.data[0] if getattr(res, "data", None) else None)

        total_despues = contar_estudiantes_padre(user["id"])

        if total_despues <= total_antes:
            st.warning(
                "Solicitud enviada, pero no se pudo verificar el conteo en este momento. "
                "Recarga la página y revisa si aparece el hijo en el panel."
            )
            st.rerun()

        if nuevo and ("pin_hash" not in nuevo or not nuevo.get("pin_hash")):
            st.warning(
                "Hijo creado, pero sin PIN persistido en BD. Aplica migración de `pin_hash` para habilitar entrada del estudiante."
            )
        else:
            st.success("Hijo creado correctamente.")

        # No hacemos rerun inmediato para que el mensaje no desaparezca.
    except Exception as exc:
        st.error(f"No fue posible crear el hijo: {exc}")


def _render_leaderboard_y_progreso(user, estudiantes):
    st.subheader("🏆 Leaderboard de progreso")

    filas = []
    diagnosticos_por_hijo = {}

    for est in estudiantes:
        diag = obtener_ultimo_diagnostico(est["id"])
        ult_puntaje = float(diag.get("puntaje") or diag.get("resultado", {}).get("porcentaje_total", 0)) if diag else 0.0
        historial_diag = listar_diagnosticos_estudiante(est["id"], limite=24)
        diagnosticos_por_hijo[est["id"]] = historial_diag
        try:
            chats_resp = listar_chats_usuario(user["email"], estudiante_id=est["id"])
            chats_total = len(chats_resp.data or [])
        except Exception:
            chats_total = 0

        filas.append(
            {
                "Hijo": est.get("nombre", "Sin nombre"),
                "Grado": est.get("grado", "-"),
                "Ultimo puntaje": round(ult_puntaje, 2),
                "Diagnosticos": len(historial_diag),
                "Conversaciones": chats_total,
            }
        )

    if not filas:
        st.info("Aun no hay hijos para mostrar en el leaderboard.")
        return

    filas.sort(key=lambda x: x["Ultimo puntaje"], reverse=True)
    st.dataframe(filas, use_container_width=True, hide_index=True)

    st.subheader("📈 Evolucion de puntaje por hijo")
    opciones = {f"{e['nombre']} ({e['grado']})": e["id"] for e in estudiantes}
    seleccion = st.multiselect(
        "Selecciona hijos para ver su grafica",
        options=list(opciones.keys()),
        default=list(opciones.keys())[:2],
    )

    if not seleccion:
        st.caption("Selecciona al menos un hijo para ver progresos.")
        return

    for etiqueta in seleccion:
        est_id = opciones[etiqueta]
        data = list(reversed(diagnosticos_por_hijo.get(est_id, [])))
        if not data:
            st.caption(f"{etiqueta}: sin diagnosticos aun.")
            continue

        puntajes = [float(item.get("puntaje", 0)) for item in data]
        fechas = [_fecha_legible(item.get("creado_el", "")) for item in data]
        st.markdown(f"**{etiqueta}**")
        st.line_chart({"Puntaje": puntajes})
        st.caption(" - ".join(fechas))


def _render_energia_rango(user, estudiantes):
    st.subheader("⚡ Energia usada por rango")
    hoy = datetime.now().date()
    inicio_default = hoy - timedelta(days=30)

    c1, c2 = st.columns(2)
    with c1:
        fecha_inicio = st.date_input("Desde", value=inicio_default)
    with c2:
        fecha_fin = st.date_input("Hasta", value=hoy)

    if fecha_fin < fecha_inicio:
        st.error("La fecha final no puede ser anterior a la inicial.")
        return

    consumos = listar_consumo_energia(user["email"], fecha_inicio=str(fecha_inicio), fecha_fin=str(fecha_fin))

    if not consumos:
        st.caption(
            "Sin datos de consumo en este rango."
        )
        return

    nombre_por_id = {e["id"]: e.get("nombre", "Sin nombre") for e in estudiantes}
    total = 0
    por_hijo = {}
    por_fecha = {}

    for item in consumos:
        cant = int(item.get("cantidad", 0) or 0)
        total += cant

        est_id = item.get("estudiante_id")
        nombre = nombre_por_id.get(est_id, "Sin hijo")
        por_hijo[nombre] = por_hijo.get(nombre, 0) + cant

        fecha = _fecha_legible(item.get("creado_el", ""))
        por_fecha[fecha] = por_fecha.get(fecha, 0) + cant

    st.metric("Energia total consumida", f"{total} ⚡")
    st.markdown("**Consumo por hijo**")
    st.bar_chart(por_hijo)
    st.markdown("**Consumo diario**")
    st.line_chart(por_fecha)


def _render_dashboard():
    user = obtener_datos_usuario(st.session_state.parent_email)
    if not user:
        st.error("No fue posible cargar tu cuenta. Inicia sesion de nuevo.")
        _logout_parent()
        return

    _render_sidebar(user)

    st.title("👨‍👩‍👧 Panel de control del padre")
    st.caption("Gestiona hijos y supervisa rendimiento academico y consumo de energia.")

    _render_crear_hijo(user)
    st.divider()

    estudiantes = listar_estudiantes(user["id"])
    if not estudiantes:
        st.info("Aun no tienes hijos creados. Agrega el primero desde el formulario superior.")
        return

    _render_leaderboard_y_progreso(user, estudiantes)
    st.divider()
    _render_energia_rango(user, estudiantes)


_init_parent_session()
_inject_theme_styles()

if st.session_state.parent_autenticado:
    _render_dashboard()
else:
    _render_login_padre()
