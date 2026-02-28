#database.py
import streamlit as st
from supabase import create_client
from datetime import datetime, date
import pytz

# Conexión segura con Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

def registrar_intento_fallido(email):
    """Suma un intento fallido y bloquea si llega a 5"""
    res = supabase.table("perfiles")\
        .select("intentos_fallidos")\
        .eq("email", email).single().execute()
    
    if not res.data:
        return None
    
    nuevos_intentos = res.data['intentos_fallidos'] + 1
    update = {"intentos_fallidos": nuevos_intentos}
    
    if nuevos_intentos >= 5:
        from datetime import datetime, timedelta
        import pytz
        bloqueado_hasta = datetime.now(pytz.utc) + timedelta(minutes=2)
        update["bloqueado_hasta"] = bloqueado_hasta.isoformat()
    
    supabase.table("perfiles").update(update).eq("email", email).execute()
    return nuevos_intentos

def resetear_intentos(email):
    """Limpia el contador al hacer login exitoso"""
    supabase.table("perfiles").update({
        "intentos_fallidos": 0,
        "bloqueado_hasta": None
    }).eq("email", email).execute()

# Configuración de créditos diarios por plan
CREDITOS_DIARIOS = {
    "basico": 50,      # 50 créditos diarios para plan básico
    "avanzado": 150    # 150 créditos diarios para plan avanzado
}

def verificar_y_recargar_creditos(email):
    """
    Verifica si es un nuevo día y recarga créditos según el plan.
    Retorna los datos actualizados del usuario.
    """
    try:
        # Obtener datos del usuario
        res = supabase.table("perfiles").select("*").eq("email", email).single().execute()
        if not res.data:
            return None
        
        usuario = res.data
        plan = usuario.get('plan', 'basico')
        ultima_fecha_str = usuario.get('ultima_fecha', '2000-01-01')
        creditos_actuales = usuario.get('creditos_totales', 0)
        
        # Convertir string a date
        if isinstance(ultima_fecha_str, str):
            ultima_fecha = datetime.strptime(ultima_fecha_str, '%Y-%m-%d').date()
        else:
            ultima_fecha = ultima_fecha_str
        
        # Fecha actual en Colombia
        hoy = datetime.now(pytz.timezone('America/Bogota')).date()
        
        # Verificar si es un nuevo día
        if hoy > ultima_fecha:
            # Calcular créditos a agregar
            creditos_diarios = CREDITOS_DIARIOS.get(plan, 50)
            nuevos_creditos = creditos_actuales + creditos_diarios
            
            # Actualizar en la base de datos
            supabase.table("perfiles").update({
                "creditos_totales": nuevos_creditos,
                "ultima_fecha": hoy.strftime('%Y-%m-%d')
            }).eq("email", email).execute()
            
            print(f"✅ Recarga diaria: +{creditos_diarios}⚡ para {email} (Plan: {plan})")
            
            # Retornar datos actualizados
            usuario['creditos_totales'] = nuevos_creditos
            usuario['ultima_fecha'] = hoy.strftime('%Y-%m-%d')
        
        return usuario
        
    except Exception as e:
        print(f"❌ Error en recarga diaria: {e}")
        return None

def obtener_datos_usuario(email):
    """Obtiene datos del usuario y verifica recarga diaria."""
    # Primero verificar y recargar si es necesario
    usuario = verificar_y_recargar_creditos(email)
    return usuario

def descontar_energia(email, cantidad=1):
    """Descuenta créditos atómicamente en Supabase para evitar race conditions."""
    return supabase.rpc(
        "descontar_creditos", 
        {"user_email": email, "cantidad": cantidad}
    ).execute()

def guardar_o_actualizar_chat(chat_id, email, titulo, materia, mensajes):
    data = {
        "email_usuario": email,
        "materia": materia,
        "mensajes": mensajes,
        "actualizado_el": datetime.now(pytz.timezone('America/Bogota')).isoformat()
    }
    if not chat_id: data["titulo"] = titulo
    
    if chat_id:
        return supabase.table("historial_chats").update(data).eq("id", chat_id).execute()
    else:
        return supabase.table("historial_chats").insert(data).execute()

def listar_chats_usuario(email):
    return supabase.table("historial_chats") \
        .select("id, titulo, materia, actualizado_el") \
        .eq("email_usuario", email) \
        .order("actualizado_el", desc=True).execute()

def cargar_chat_completo(chat_id):
    res = supabase.table("historial_chats").select("*").eq("id", chat_id).single().execute()
    return res.data

# Cliente con service role para operaciones de registro (bypasa RLS)
service_key = st.secrets["SUPABASE_SERVICE_KEY"]
supabase_admin = create_client(url, service_key)