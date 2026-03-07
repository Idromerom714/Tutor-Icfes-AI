import streamlit as st
from supabase import create_client
from datetime import datetime, date
import re
import pytz

# Conexión con Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# Cliente admin para operaciones que bypasan RLS
service_key = st.secrets["SUPABASE_SERVICE_KEY"]
supabase_admin = create_client(url, service_key)

# Créditos diarios por plan (para mostrar en UI)
CREDITOS_POR_PLAN = {
    "basico": 2000,
    "estandar": 3000,
    "familia": 7000
}

def registrar_intento_fallido(email):
    """Suma un intento fallido y bloquea si llega a 5"""
    res = supabase_admin.table("padres")\
        .select("intentos_fallidos")\
        .eq("email", email).single().execute()
    
    if not res.data:
        return None
    
    nuevos_intentos = res.data['intentos_fallidos'] + 1
    update = {"intentos_fallidos": nuevos_intentos}
    
    if nuevos_intentos >= 5:
        from datetime import timedelta
        bloqueado_hasta = datetime.now(pytz.utc) + timedelta(minutes=2)
        update["bloqueado_hasta"] = bloqueado_hasta.isoformat()
    
    supabase_admin.table("padres").update(update).eq("email", email).execute()
    return nuevos_intentos

def resetear_intentos(email):
    """Limpia el contador al hacer login exitoso"""
    supabase_admin.table("padres").update({
        "intentos_fallidos": 0,
        "bloqueado_hasta": None
    }).eq("email", email).execute()

def obtener_datos_usuario(email):
    """Obtiene datos del padre desde la tabla padres."""
    try:
        res = supabase_admin.table("padres")\
            .select("*")\
            .eq("email", email)\
            .single().execute()
        return res.data
    except Exception:
        return None

def descontar_energia(email, cantidad=1):
    """Descuenta créditos atómicamente."""
    return supabase_admin.rpc(
        "descontar_creditos",
        {"user_email": email, "cantidad": cantidad}
    ).execute()


def registrar_consumo_energia(email_padre, estudiante_id, cantidad, materia=None, metadata=None):
    """Registra consumo de energía por estudiante (fallback seguro si tabla no existe)."""
    data = {
        "email_padre": email_padre,
        "estudiante_id": estudiante_id,
        "cantidad": cantidad,
        "materia": materia,
        "metadata": metadata or {},
        "creado_el": datetime.now(pytz.timezone('America/Bogota')).isoformat(),
    }
    try:
        return supabase_admin.table("consumo_energia").insert(data).execute()
    except Exception:
        return None


def listar_consumo_energia(email_padre, fecha_inicio=None, fecha_fin=None, estudiante_id=None):
    """Lista consumo de energía del padre filtrable por rango y estudiante."""
    try:
        query = supabase_admin.table("consumo_energia")\
            .select("email_padre, estudiante_id, cantidad, materia, creado_el")\
            .eq("email_padre", email_padre)

        if estudiante_id:
            query = query.eq("estudiante_id", estudiante_id)
        if fecha_inicio:
            query = query.gte("creado_el", f"{fecha_inicio}T00:00:00")
        if fecha_fin:
            query = query.lte("creado_el", f"{fecha_fin}T23:59:59")

        res = query.order("creado_el", desc=False).execute()
        return res.data or []
    except Exception:
        return []

def guardar_o_actualizar_chat(chat_id, email, titulo, materia, mensajes, estudiante_id=None):
    data = {
        "email_usuario": email,
        "materia": materia,
        "mensajes": mensajes,
        "actualizado_el": datetime.now(pytz.timezone('America/Bogota')).isoformat()
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
    query = supabase_admin.table("historial_chats")\
        .select("id, titulo, materia, actualizado_el")\
        .eq("email_usuario", email)

    if estudiante_id:
        query = query.eq("estudiante_id", estudiante_id)

    return query.order("actualizado_el", desc=True).execute()

def cargar_chat_completo(chat_id):
    res = supabase_admin.table("historial_chats")\
        .select("*").eq("id", chat_id).single().execute()
    return res.data

def obtener_estudiante(padre_id):
    """Obtiene el primer estudiante asociado al padre."""
    try:
        res = supabase_admin.table("estudiantes")\
            .select("*")\
            .eq("padre_id", padre_id)\
            .limit(1)\
            .single().execute()
        return res.data
    except Exception:
        return None


def listar_estudiantes(padre_id, incluir_inactivos=False):
    """Lista estudiantes del padre. Por defecto, solo activos."""
    base_query = supabase_admin.table("estudiantes")\
        .select("*")\
        .eq("padre_id", padre_id)

    try:
        if incluir_inactivos:
            res = base_query.order("fecha_registro", desc=False).execute()
        else:
            # Si el esquema nuevo existe, solo muestra activos.
            res = base_query.eq("activo", True).order("fecha_registro", desc=False).execute()
        return res.data or []
    except Exception:
        # Compatibilidad temporal con esquemas antiguos sin columna `activo`.
        try:
            res = supabase_admin.table("estudiantes")\
                .select("*")\
                .eq("padre_id", padre_id)\
                .order("fecha_registro", desc=False)\
                .execute()
            return res.data or []
        except Exception:
            return []


def crear_estudiante(padre_id, nombre, grado, pin_hash=None):
    """Crea un nuevo estudiante vinculado a un padre con reintentos compatibles de esquema."""

    def _grado_a_entero(valor):
        if isinstance(valor, int):
            return valor
        if isinstance(valor, str):
            m = re.search(r"\d+", valor)
            if m:
                try:
                    return int(m.group(0))
                except Exception:
                    return None
        return None

    payloads = []

    base_payload = {
        "padre_id": padre_id,
        "nombre": nombre,
        "grado": grado,
    }

    payload_con_pin = dict(base_payload)
    if pin_hash:
        payload_con_pin["pin_hash"] = pin_hash
    payloads.append(payload_con_pin)

    if pin_hash:
        payloads.append(dict(base_payload))

    grado_int = _grado_a_entero(grado)
    if grado_int is not None and grado_int != grado:
        payload_int = {
            "padre_id": padre_id,
            "nombre": nombre,
            "grado": grado_int,
        }
        if pin_hash:
            payload_int_con_pin = dict(payload_int)
            payload_int_con_pin["pin_hash"] = pin_hash
            payloads.append(payload_int_con_pin)
        payloads.append(payload_int)

    vistos = set()
    payloads_unicos = []
    for p in payloads:
        key = tuple(sorted(p.items()))
        if key not in vistos:
            vistos.add(key)
            payloads_unicos.append(p)

    ultimo_error = None
    for payload in payloads_unicos:
        try:
            return supabase_admin.table("estudiantes").insert(payload).execute()
        except Exception as exc:
            ultimo_error = exc

    raise ultimo_error


def renombrar_estudiante(estudiante_id, padre_id, nuevo_nombre):
    """Actualiza el nombre de un estudiante del padre."""
    return supabase_admin.table("estudiantes")\
        .update({"nombre": nuevo_nombre})\
        .eq("id", estudiante_id)\
        .eq("padre_id", padre_id)\
        .execute()


def actualizar_pin_estudiante(estudiante_id, padre_id, nuevo_pin_hash):
    """Actualiza o define el PIN hash del estudiante."""
    return supabase_admin.table("estudiantes")\
        .update({"pin_hash": nuevo_pin_hash})\
        .eq("id", estudiante_id)\
        .eq("padre_id", padre_id)\
        .execute()


def desactivar_estudiante(estudiante_id, padre_id):
    """Desactiva un estudiante sin borrar su historial."""
    data = {
        "activo": False,
        "desactivado_el": datetime.now(pytz.timezone('America/Bogota')).isoformat(),
    }
    return supabase_admin.table("estudiantes")\
        .update(data)\
        .eq("id", estudiante_id)\
        .eq("padre_id", padre_id)\
        .execute()


def obtener_ultimo_diagnostico(estudiante_id):
    """Obtiene el último diagnóstico de un estudiante (si existe)."""
    try:
        res = supabase_admin.table("diagnosticos_estudiante")\
            .select("*")\
            .eq("estudiante_id", estudiante_id)\
            .order("creado_el", desc=True)\
            .limit(1)\
            .execute()
        if res.data:
            return res.data[0]
        return None
    except Exception:
        # Fallback seguro mientras la tabla se despliega en producción.
        return None


def guardar_diagnostico_estudiante(estudiante_id, email_padre, resultado):
    """Guarda el resultado del diagnóstico sin romper el flujo principal."""
    data = {
        "estudiante_id": estudiante_id,
        "email_padre": email_padre,
        "resultado": resultado,
        "puntaje": resultado.get("porcentaje_total", 0),
        "creado_el": datetime.now(pytz.timezone('America/Bogota')).isoformat(),
    }

    try:
        return supabase_admin.table("diagnosticos_estudiante").insert(data).execute()
    except Exception:
        return None


def listar_diagnosticos_estudiante(estudiante_id, limite=4):
    """Lista diagnósticos recientes para mostrar tendencia de progreso."""
    try:
        res = supabase_admin.table("diagnosticos_estudiante")\
            .select("puntaje, creado_el")\
            .eq("estudiante_id", estudiante_id)\
            .order("creado_el", desc=True)\
            .limit(limite)\
            .execute()
        return res.data or []
    except Exception:
        return []