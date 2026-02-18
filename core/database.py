import streamlit as st
from supabase import create_client
from datetime import datetime
import pytz

# Conexión segura con Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

def obtener_datos_usuario(email):
    """Obtiene datos y maneja el saldo de energía."""
    res = supabase.table("perfiles").select("*").eq("email", email).single().execute()
    return res.data if res.data else None

def descontar_energia(email, cantidad=1):
    """Descuenta créditos del saldo total."""
    res = supabase.table("perfiles").select("creditos_totales").eq("email", email).single().execute()
    if not res.data: return None
    
    nuevo_valor = max(0, res.data['creditos_totales'] - cantidad)
    return supabase.table("perfiles").update({"creditos_totales": nuevo_valor}).eq("email", email).execute()

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