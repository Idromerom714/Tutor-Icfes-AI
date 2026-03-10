# database.py
import streamlit as st
from supabase import create_client
from datetime import datetime
import re
import pytz

# ─────────────────────────────────────────────────────────────────────────────
# CLIENTES
# ─────────────────────────────────────────────────────────────────────────────

url          = st.secrets["SUPABASE_URL"]
key          = st.secrets["SUPABASE_KEY"]
service_key  = st.secrets["SUPABASE_SERVICE_KEY"]

supabase       = create_client(url, key)
supabase_admin = create_client(url, service_key)

CREDITOS_POR_PLAN = {
    "basico":   2000,
    "estandar": 3000,
    "familia":  7000,
}

# ─────────────────────────────────────────────────────────────────────────────
# AUTENTICACIÓN Y PADRES
# ─────────────────────────────────────────────────────────────────────────────

def registrar_intento_fallido(email):
    res = supabase_admin.table("padres") \
        .select("intentos_fallidos") \
        .eq("email", email).single().execute()
    if not res.data:
        return None
    nuevos = res.data["intentos_fallidos"] + 1
    update = {"intentos_fallidos": nuevos}
    if nuevos >= 5:
        from datetime import timedelta
        bloqueado_hasta = datetime.now(pytz.utc) + timedelta(minutes=2)
        update["bloqueado_hasta"] = bloqueado_hasta.isoformat()
    supabase_admin.table("padres").update(update).eq("email", email).execute()
    return nuevos


def resetear_intentos(email):
    supabase_admin.table("padres").update({
        "intentos_fallidos": 0,
        "bloqueado_hasta": None,
    }).eq("email", email).execute()


def obtener_datos_usuario(email):
    try:
        res = supabase_admin.table("padres") \
            .select("*").eq("email", email).single().execute()
        return res.data
    except Exception:
        return None


def descontar_energia(email, cantidad=1):
    return supabase_admin.rpc(
        "descontar_creditos",
        {"user_email": email, "cantidad": cantidad}
    ).execute()


def registrar_consumo_energia(email_padre, estudiante_id, cantidad, materia=None, metadata=None):
    data = {
        "email_padre":   email_padre,
        "estudiante_id": estudiante_id,
        "cantidad":      cantidad,
        "materia":       materia,
        "metadata":      metadata or {},
        "creado_el":     datetime.now(pytz.timezone("America/Bogota")).isoformat(),
    }
    try:
        return supabase_admin.table("consumo_energia").insert(data).execute()
    except Exception:
        return None


def listar_consumo_energia(email_padre, fecha_inicio=None, fecha_fin=None, estudiante_id=None):
    try:
        query = supabase_admin.table("consumo_energia") \
            .select("email_padre, estudiante_id, cantidad, materia, creado_el") \
            .eq("email_padre", email_padre)
        if estudiante_id:
            query = query.eq("estudiante_id", estudiante_id)
        if fecha_inicio:
            query = query.gte("creado_el", f"{fecha_inicio}T00:00:00")
        if fecha_fin:
            query = query.lte("creado_el", f"{fecha_fin}T23:59:59")
        return query.order("creado_el", desc=False).execute().data or []
    except Exception:
        return []

# ─────────────────────────────────────────────────────────────────────────────
# CHATS
# ─────────────────────────────────────────────────────────────────────────────

def guardar_o_actualizar_chat(chat_id, email, titulo, materia, mensajes, estudiante_id=None):
    data = {
        "email_usuario": email,
        "materia":       materia,
        "mensajes":      mensajes,
        "actualizado_el": datetime.now(pytz.timezone("America/Bogota")).isoformat(),
    }
    if estudiante_id:
        data["estudiante_id"] = estudiante_id
    if not chat_id:
        data["titulo"] = titulo
    if chat_id:
        return supabase_admin.table("historial_chats").update(data).eq("id", chat_id).execute()
    else:
        return supabase_admin.table("historial_chats").insert(data).execute()


def listar_chats_usuario(email, estudiante_id=None):
    query = supabase_admin.table("historial_chats") \
        .select("id, titulo, materia, actualizado_el") \
        .eq("email_usuario", email)
    if estudiante_id:
        query = query.eq("estudiante_id", estudiante_id)
    return query.order("actualizado_el", desc=True).execute()


def cargar_chat_completo(chat_id):
    res = supabase_admin.table("historial_chats") \
        .select("*").eq("id", chat_id).single().execute()
    return res.data

# ─────────────────────────────────────────────────────────────────────────────
# ESTUDIANTES
# ─────────────────────────────────────────────────────────────────────────────

def obtener_estudiante(padre_id):
    try:
        res = supabase_admin.table("estudiantes") \
            .select("*").eq("padre_id", padre_id).limit(1).single().execute()
        return res.data
    except Exception:
        return None


def listar_estudiantes(padre_id, incluir_inactivos=False):
    columnas_orden = ["fecha_registro", "creado_el", "created_at", None]
    for columna in columnas_orden:
        try:
            query = supabase_admin.table("estudiantes") \
                .select("*").eq("padre_id", padre_id)
            if not incluir_inactivos:
                query = query.eq("activo", True)
            if columna:
                query = query.order(columna, desc=False)
            return query.execute().data or []
        except Exception:
            continue
    return []


def contar_estudiantes_padre(padre_id):
    try:
        res = supabase_admin.table("estudiantes") \
            .select("id").eq("padre_id", padre_id).execute()
        return len(res.data or [])
    except Exception:
        return 0


def crear_estudiante(padre_id, nombre, grado, pin_hash=None):
    def _grado_int(valor):
        if isinstance(valor, int):
            return valor
        m = re.search(r"\d+", str(valor))
        return int(m.group(0)) if m else None

    payloads = []
    base = {"padre_id": padre_id, "nombre": nombre, "grado": grado}
    con_pin = {**base, "pin_hash": pin_hash} if pin_hash else None
    if con_pin:
        payloads.append(con_pin)
    payloads.append(base)

    grado_int = _grado_int(grado)
    if grado_int is not None and grado_int != grado:
        base_int = {"padre_id": padre_id, "nombre": nombre, "grado": grado_int}
        if pin_hash:
            payloads.append({**base_int, "pin_hash": pin_hash})
        payloads.append(base_int)

    vistos, unicos = set(), []
    for p in payloads:
        k = tuple(sorted(p.items()))
        if k not in vistos:
            vistos.add(k)
            unicos.append(p)

    ultimo_error = None
    for payload in unicos:
        try:
            return supabase_admin.table("estudiantes").insert(payload).execute()
        except Exception as exc:
            ultimo_error = exc
    raise ultimo_error


def renombrar_estudiante(estudiante_id, padre_id, nuevo_nombre):
    return supabase_admin.table("estudiantes") \
        .update({"nombre": nuevo_nombre}) \
        .eq("id", estudiante_id).eq("padre_id", padre_id).execute()


def actualizar_pin_estudiante(estudiante_id, padre_id, nuevo_pin_hash):
    return supabase_admin.table("estudiantes") \
        .update({"pin_hash": nuevo_pin_hash}) \
        .eq("id", estudiante_id).eq("padre_id", padre_id).execute()


def desactivar_estudiante(estudiante_id, padre_id):
    return supabase_admin.table("estudiantes") \
        .update({
            "activo": False,
            "desactivado_el": datetime.now(pytz.timezone("America/Bogota")).isoformat(),
        }) \
        .eq("id", estudiante_id).eq("padre_id", padre_id).execute()

# ─────────────────────────────────────────────────────────────────────────────
# DIAGNÓSTICOS  (tablas: diagnosticos + respuestas_diagnostico)
# ─────────────────────────────────────────────────────────────────────────────

def obtener_ultimo_diagnostico(estudiante_id):
    """Retorna el diagnóstico más reciente del estudiante o None."""
    try:
        filas = supabase_admin.table("diagnosticos") \
            .select("*") \
            .eq("estudiante_id", estudiante_id) \
            .order("fecha", desc=True) \
            .limit(1).execute().data
        return filas[0] if filas else None
    except Exception:
        return None


def guardar_diagnostico_estudiante(estudiante_id, email_padre, resultado):
    """
    Persiste diagnóstico en tabla `diagnosticos`.
    Retorna el ID generado o None.
    """
    data = {
        "estudiante_id":          estudiante_id,
        "preguntas_ids":          resultado.get("preguntas_ids", []),
        "porcentaje_total":       resultado.get("porcentaje_total", 0),
        "resultados_por_materia": resultado.get("resultados_por_materia", []),
    }
    try:
        res = supabase_admin.table("diagnosticos").insert(data).execute()
        return res.data[0]["id"] if res.data else None
    except Exception:
        return None


def guardar_respuestas_diagnostico(diagnostico_id, estudiante_id, preguntas, respuestas_usuario):
    """
    Persiste cada respuesta individual en `respuestas_diagnostico`.
    `preguntas` debe incluir `respuesta_correcta`.
    """
    filas = []
    for p in preguntas:
        pid      = str(p["id"])
        correcta = p["respuesta_correcta"]
        dada     = respuestas_usuario.get(pid, "")
        filas.append({
            "diagnostico_id": diagnostico_id,
            "estudiante_id":  estudiante_id,
            "pregunta_id":    pid,
            "respuesta_dada": dada,
            "es_correcta":    dada == correcta,
        })
    if filas:
        try:
            supabase_admin.table("respuestas_diagnostico").insert(filas).execute()
        except Exception:
            pass


def listar_diagnosticos_estudiante(estudiante_id, limite=4):
    """Lista diagnósticos recientes para gráfica de progreso del panel padre."""
    try:
        res = supabase_admin.table("diagnosticos") \
            .select("porcentaje_total, fecha") \
            .eq("estudiante_id", estudiante_id) \
            .order("fecha", desc=True) \
            .limit(limite).execute()
        # Normalizamos a puntaje/creado_el para compatibilidad con app.py del padre
        return [
            {"puntaje": r["porcentaje_total"], "creado_el": r["fecha"]}
            for r in (res.data or [])
        ]
    except Exception:
        return []