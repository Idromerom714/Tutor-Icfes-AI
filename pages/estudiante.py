import streamlit as st
from datetime import datetime
import pytz

from core.auth import verificar_pin
from core.database import (
    obtener_datos_usuario,
    guardar_o_actualizar_chat,
    listar_chats_usuario,
    cargar_chat_completo,
    descontar_energia,
    registrar_consumo_energia,
    listar_estudiantes,
    obtener_ultimo_diagnostico,
    guardar_diagnostico_estudiante,
    listar_diagnosticos_estudiante,
)
from core.rag_search import buscar_contexto_icfes
from core.ai_engine import llamar_profe_saber, generar_titulo_chat
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

st.set_page_config(page_title="Entrada Estudiantes - El Profe Saber", page_icon="🎓")

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


def init_state():
    defaults = {
        "est_autenticado": False,
        "est_user_email": None,
        "est_estudiante_id": None,
        "est_chat_id_actual": None,
        "est_mensajes_actuales": [],
        "est_materia_anterior": None,
        "est_materia_activa": "Matemáticas",
        "est_diagnostico_completado": False,
        "est_diagnostico_resultado": None,
        "est_diagnostico_preguntas": [],
        "est_perfil_aprendizaje": None,
        "est_diagnostico_creado_el": None,
        "est_diagnostico_anterior": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def logout_estudiante():
    keys = [
        "est_autenticado",
        "est_user_email",
        "est_estudiante_id",
        "est_chat_id_actual",
        "est_mensajes_actuales",
        "est_materia_anterior",
        "est_materia_activa",
        "est_diagnostico_completado",
        "est_diagnostico_resultado",
        "est_diagnostico_preguntas",
        "est_perfil_aprendizaje",
        "est_diagnostico_creado_el",
        "est_diagnostico_anterior",
    ]
    for key in keys:
        st.session_state.pop(key, None)
    init_state()


def cargar_contexto_estudiante(estudiante):
    st.session_state.est_estudiante_id = estudiante["id"]
    st.session_state.est_chat_id_actual = None
    st.session_state.est_mensajes_actuales = []
    st.session_state.est_materia_anterior = None

    ultimo_diagnostico = obtener_ultimo_diagnostico(estudiante["id"])

    if ultimo_diagnostico and ultimo_diagnostico.get("resultado") and not diagnostico_requiere_renovacion(ultimo_diagnostico.get("creado_el")):
        resultado_diag = ultimo_diagnostico["resultado"]
        st.session_state.est_diagnostico_resultado = resultado_diag
        st.session_state.est_diagnostico_completado = True
        st.session_state.est_diagnostico_preguntas = []
        st.session_state.est_perfil_aprendizaje = resultado_diag
        st.session_state.est_diagnostico_creado_el = ultimo_diagnostico.get("creado_el")
        st.session_state.est_diagnostico_anterior = None

        materia_prioritaria = obtener_materia_prioritaria(resultado_diag, default="Matemáticas")
        st.session_state.est_materia_activa = materia_prioritaria
        st.session_state.est_materia_anterior = materia_prioritaria
    else:
        if ultimo_diagnostico and ultimo_diagnostico.get("resultado"):
            st.session_state.est_diagnostico_anterior = ultimo_diagnostico["resultado"]
        else:
            st.session_state.est_diagnostico_anterior = None

        st.session_state.est_diagnostico_resultado = None
        st.session_state.est_diagnostico_completado = False
        st.session_state.est_diagnostico_preguntas = construir_preguntas_diagnostico(
            estudiante["id"], st.session_state.get("est_diagnostico_anterior")
        )
        st.session_state.est_perfil_aprendizaje = None
        st.session_state.est_diagnostico_creado_el = None


def render_login_estudiante():
    st.title("🎓 Entrada de estudiantes")
    st.caption("Ingresa con correo del padre + seleccion de hijo + PIN del hijo.")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("👨‍👩‍👧 Ir a Panel Padre", use_container_width=True):
            st.switch_page("app.py")
    with c2:
        if st.button("📝 Ir a Registro", use_container_width=True):
            st.switch_page("pages/registro.py")

    email_input = st.text_input("Correo del padre")
    user = obtener_datos_usuario(email_input) if email_input else None

    estudiantes = []
    opciones = {}

    if user and user.get("estado") == "activo":
        estudiantes = listar_estudiantes(user["id"])
        opciones = {f"{e['nombre']} ({e['grado']})": e["id"] for e in estudiantes}
    elif email_input:
        st.caption("Cuenta no activa o no encontrada.")

    with st.form("form_login_estudiante"):
        if opciones:
            etiqueta = st.selectbox("Selecciona estudiante", options=list(opciones.keys()))
        else:
            etiqueta = None
            st.caption("Primero ingresa un correo valido con hijos activos.")

        pin_hijo = st.text_input("PIN del estudiante", type="password")
        entrar = st.form_submit_button("Entrar al entorno", use_container_width=True)

    if not entrar:
        return

    if not user or user.get("estado") != "activo":
        st.error("No se puede ingresar con esta cuenta.")
        return

    if not opciones:
        st.error("Esta cuenta no tiene hijos activos.")
        return

    estudiante_id = opciones[etiqueta]
    estudiante = next((e for e in estudiantes if e["id"] == estudiante_id), None)
    if not estudiante:
        st.error("No fue posible cargar el estudiante.")
        return

    pin_hash = estudiante.get("pin_hash")
    if not pin_hash:
        st.error("Este estudiante no tiene PIN configurado. Pide al padre configurarlo en el panel.")
        return

    if not verificar_pin(pin_hijo, pin_hash):
        st.error("PIN del estudiante incorrecto.")
        return

    st.session_state.est_autenticado = True
    st.session_state.est_user_email = user["email"]
    cargar_contexto_estudiante(estudiante)
    st.rerun()


def render_app_estudiante():
    user = obtener_datos_usuario(st.session_state.est_user_email)
    if not user:
        st.error("No fue posible cargar la cuenta padre.")
        logout_estudiante()
        st.stop()

    estudiantes = listar_estudiantes(user["id"])
    estudiante = next((e for e in estudiantes if e["id"] == st.session_state.est_estudiante_id), None)

    if not estudiante:
        st.error("El estudiante ya no esta disponible.")
        logout_estudiante()
        st.stop()

    nombre_estudiante = estudiante["nombre"]
    historial_progreso = listar_diagnosticos_estudiante(estudiante["id"], limite=4)

    if st.session_state.est_diagnostico_completado and diagnostico_requiere_renovacion(st.session_state.get("est_diagnostico_creado_el")):
        st.session_state.est_diagnostico_anterior = st.session_state.get("est_diagnostico_resultado")
        st.session_state.est_diagnostico_resultado = None
        st.session_state.est_diagnostico_completado = False
        st.session_state.est_diagnostico_preguntas = construir_preguntas_diagnostico(
            estudiante["id"],
            st.session_state.get("est_diagnostico_anterior"),
        )
        st.session_state.est_perfil_aprendizaje = None
        st.session_state.est_diagnostico_creado_el = None
        st.rerun()

    if not st.session_state.est_diagnostico_completado:
        if not st.session_state.est_diagnostico_preguntas:
            st.session_state.est_diagnostico_preguntas = construir_preguntas_diagnostico(
                estudiante["id"],
                st.session_state.get("est_diagnostico_anterior"),
            )

        titulo_diag = "🧭 Diagnóstico Semanal ICFES" if st.session_state.get("est_diagnostico_anterior") else "🧭 Diagnóstico Inicial ICFES"
        st.title(titulo_diag)
        st.caption(f"Responde estas {DIAGNOSTICO_CANTIDAD} preguntas para estimar tu punto de partida y crear tu plan.")

        with st.form("diagnostico_estudiante_form"):
            for i, pregunta in enumerate(st.session_state.est_diagnostico_preguntas, start=1):
                st.markdown(f"**{i}. [{pregunta['materia']}] {pregunta['enunciado']}**")
                st.radio(
                    "Selecciona una opcion:",
                    options=pregunta["opciones"],
                    key=f"est_diag_{pregunta['id']}",
                    index=None,
                )

            enviar = st.form_submit_button("Calificar diagnostico", use_container_width=True)

            if enviar:
                respuestas = {}
                faltantes = []

                for pregunta in st.session_state.est_diagnostico_preguntas:
                    respuesta = st.session_state.get(f"est_diag_{pregunta['id']}")
                    if respuesta is None:
                        faltantes.append(pregunta["id"])
                    else:
                        respuestas[pregunta["id"]] = respuesta

                if faltantes:
                    st.error("Debes responder todas las preguntas.")
                else:
                    resultado = evaluar_diagnostico(respuestas, st.session_state.est_diagnostico_preguntas)
                    st.session_state.est_diagnostico_resultado = resultado
                    st.session_state.est_diagnostico_completado = True
                    st.session_state.est_perfil_aprendizaje = resultado
                    st.session_state.est_diagnostico_creado_el = datetime.now(pytz.timezone("America/Bogota")).isoformat()

                    materia_prioritaria = obtener_materia_prioritaria(resultado, default="Matemáticas")
                    st.session_state.est_materia_activa = materia_prioritaria
                    st.session_state.est_materia_anterior = materia_prioritaria

                    guardar_diagnostico_estudiante(estudiante["id"], user["email"], resultado)
                    st.success("Diagnostico completado.")
                    st.rerun()

        st.stop()

    with st.sidebar:
        st.header(f"¡Ey, {nombre_estudiante}! 👋")
        st.caption(f"Cuenta padre: {user['email']}")

        resultado_diag = st.session_state.get("est_diagnostico_resultado")
        if resultado_diag:
            porcentaje_diag = resultado_diag.get("porcentaje_total", 0)
            st.caption(f"🧭 Diagnostico: {porcentaje_diag}%")

            preguntas_recomendadas = generar_preguntas_recomendadas(
                resultado_diag,
                st.session_state.get("est_materia_activa", "Matemáticas"),
                max_preguntas=3,
            )
            with st.expander("💬 Preguntas recomendadas"):
                for sugerencia in preguntas_recomendadas:
                    st.write(f"- {sugerencia}")

            plan_semanal = generar_plan_semanal(resultado_diag)
            with st.expander("🗓️ Plan semanal"):
                for bloque in plan_semanal:
                    st.write(f"**{bloque['dia']} · {bloque['materia']}**")
                    st.caption(f"Objetivo: {bloque['objetivo']}")

            with st.expander("📈 Progreso (ultimas 4 semanas)"):
                if historial_progreso:
                    historial_asc = list(reversed(historial_progreso))
                    puntajes = [float(item.get("puntaje", 0)) for item in historial_asc]
                    st.line_chart({"Puntaje": puntajes})
                else:
                    st.caption("Aun no hay historial suficiente.")

        creditos = user.get("creditos_totales", 0)
        st.markdown(f"### ⚡ Energia: {creditos}")

        if st.button("➕ Nueva conversacion", use_container_width=True):
            st.session_state.est_chat_id_actual = None
            st.session_state.est_mensajes_actuales = []
            st.session_state.est_materia_anterior = None
            st.rerun()

        if st.button("🔁 Cambiar estudiante", use_container_width=True):
            st.session_state.est_autenticado = False
            st.session_state.est_estudiante_id = None
            st.rerun()

        if st.button("👨‍👩‍👧 Ir a Panel Padre", use_container_width=True):
            st.switch_page("app.py")

        st.divider()
        st.subheader("📚 Historial")
        chats_response = listar_chats_usuario(user["email"], estudiante_id=estudiante["id"])
        if chats_response.data:
            for chat in chats_response.data[:10]:
                if st.button(f"💬 {chat['titulo'][:25]}", key=f"est_chat_{chat['id']}", use_container_width=True):
                    chat_completo = cargar_chat_completo(chat["id"])
                    st.session_state.est_chat_id_actual = chat["id"]
                    st.session_state.est_mensajes_actuales = chat_completo["mensajes"]
                    st.session_state.est_materia_activa = chat_completo["materia"]
                    st.session_state.est_materia_anterior = chat_completo["materia"]
                    st.rerun()
        else:
            st.caption("Sin conversaciones aun.")

        st.divider()
        materias = ["Matemáticas", "Lectura Crítica", "Sociales", "Ciencias Naturales", "Física", "Inglés"]
        try:
            idx = materias.index(st.session_state.est_materia_activa)
        except ValueError:
            idx = 0

        materia_sel = st.selectbox("Materia actual", materias, index=idx)
        if materia_sel != st.session_state.est_materia_anterior:
            st.session_state.est_materia_activa = materia_sel
            st.session_state.est_materia_anterior = materia_sel
            st.session_state.est_chat_id_actual = None
            st.session_state.est_mensajes_actuales = []
            st.rerun()

    for msg in st.session_state.est_mensajes_actuales:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    st.divider()
    foto = st.file_uploader("📸 Añadir imagen (opcional)", type=["jpg", "jpeg", "png"])
    pregunta_input = st.chat_input("Escribe tu duda...")

    if not pregunta_input:
        return

    costo_base = 8 if st.session_state.est_materia_activa in ["Sociales", "Lectura Crítica"] else 1
    plus_foto = 5 if foto else 0
    total_a_pagar = costo_base + plus_foto

    if user.get("creditos_totales", 0) < total_a_pagar:
        st.error(f"Sin energia suficiente. Necesitas {total_a_pagar}⚡")
        return

    with st.chat_message("user"):
        st.markdown(pregunta_input)

    with st.spinner(f"El Profe analiza ({total_a_pagar}⚡)..."):
        img_bytes = foto.read() if foto else None
        contexto = buscar_contexto_icfes(pregunta_input, st.session_state.est_materia_activa)
        respuesta = llamar_profe_saber(
            pregunta_input,
            contexto,
            img_bytes,
            materia=st.session_state.est_materia_activa,
            historial_mensajes=st.session_state.est_mensajes_actuales,
            diagnostico_resultado=st.session_state.get("est_perfil_aprendizaje"),
            nivel_recomendado=dificultad_objetivo_por_materia(
                st.session_state.get("est_perfil_aprendizaje"),
                st.session_state.est_materia_activa,
            ),
        )

    if "⚠️" in respuesta:
        st.error(respuesta)
        return

    st.session_state.est_mensajes_actuales.append({"role": "user", "content": pregunta_input})
    st.session_state.est_mensajes_actuales.append({"role": "assistant", "content": respuesta})

    titulo = generar_titulo_chat(pregunta_input) if not st.session_state.est_chat_id_actual else "Actualizando..."
    res_db = guardar_o_actualizar_chat(
        st.session_state.est_chat_id_actual,
        user["email"],
        titulo,
        st.session_state.est_materia_activa,
        st.session_state.est_mensajes_actuales,
        estudiante_id=estudiante["id"],
    )

    if not st.session_state.est_chat_id_actual:
        st.session_state.est_chat_id_actual = res_db.data[0]["id"]

    descontar_energia(user["email"], total_a_pagar)
    registrar_consumo_energia(
        email_padre=user["email"],
        estudiante_id=estudiante["id"],
        cantidad=total_a_pagar,
        materia=st.session_state.est_materia_activa,
        metadata={"costo_base": costo_base, "plus_foto": plus_foto},
    )
    st.rerun()


init_state()

if st.session_state.est_autenticado:
    render_app_estudiante()
else:
    render_login_estudiante()
