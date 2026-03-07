import streamlit as st
from supabase import create_client
from datetime import datetime, date
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

def listar_chats_usuario(email):
    return supabase_admin.table("historial_chats")\
        .select("id, titulo, materia, actualizado_el")\
        .eq("email_usuario", email)\
        .order("actualizado_el", desc=True).execute()

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