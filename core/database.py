import streamlit as st
from supabase import create_client
from datetime import datetime
import pytz

# Conexión segura con Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

def obtener_datos_usuario(email):
    """Obtiene datos y reinicia créditos si es un nuevo día en Colombia."""
    # Configurar zona horaria de Medellín/Bogotá
    tz = pytz.timezone('America/Bogota')
    hoy = datetime.now(tz).date().isoformat()
    
    res = supabase.table("perfiles").select("*").eq("email", email).single().execute()
    user = res.data
    
    if not user:
        return None
    
    # Reinicio diario de créditos basado en hora local
    if user['ultima_fecha'] != hoy:
        supabase.table("perfiles").update({
            "preguntas_usadas": 0, 
            "imagenes_usadas": 0, 
            "ultima_fecha": hoy
        }).eq("email", email).execute()
        
        user['preguntas_usadas'] = 0
        user['imagenes_usadas'] = 0
        
    return user

def descontar_credito(email, es_imagen=False):
    """Suma 1 al contador de uso correspondiente en la base de datos."""
    columna = "imagenes_usadas" if es_imagen else "preguntas_usadas"
    
    # Primero obtenemos el valor actual
    res = supabase.table("perfiles").select(columna).eq("email", email).single().execute()
    nuevo_valor = res.data[columna] + 1
    
    # Actualizamos con el nuevo conteo
    supabase.table("perfiles").update({columna: nuevo_valor}).eq("email", email).execute()

def guardar_o_actualizar_chat(chat_id, email, titulo, materia, mensajes):
    data = {
        "email_usuario": email,
        "materia": materia,
        "mensajes": mensajes,
        "actualizado_el": datetime.now(pytz.timezone('America/Bogota')).isoformat()
    }
    
    # Solo incluimos el título si el chat es nuevo para no sobreescribir títulos personalizados
    if not chat_id:
        data["titulo"] = titulo
    
    if chat_id:
        return supabase.table("historial_chats").update(data).eq("id", chat_id).execute()
    else:
        return supabase.table("historial_chats").insert(data).execute()
 

def listar_chats_usuario(email):
    """Trae la lista de títulos de chats previos del usuario."""
    return supabase.table("historial_chats") \
        .select("id, titulo, materia, actualizado_el") \
        .eq("email_usuario", email) \
        .order("actualizado_el", desc=True) \
        .execute()

def cargar_chat_completo(chat_id):
    """Trae todos los mensajes de un chat específico."""
    res = supabase.table("historial_chats").select("*").eq("id", chat_id).single().execute()
    return res.data