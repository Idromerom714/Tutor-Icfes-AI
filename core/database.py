import streamlit as st
from supabase import create_client
from datetime import date

# Conexión segura
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

def obtener_datos_usuario(email):
    res = supabase.table("perfiles").select("*").eq("email", email).single().execute()
    user = res.data
    if not user: return None
    
    hoy = date.today().isoformat()
    if user['ultima_fecha'] != hoy:
        supabase.table("perfiles").update({
            "preguntas_usadas": 0, "imagenes_usadas": 0, "ultima_fecha": hoy
        }).eq("email", email).execute()
        user['preguntas_usadas'] = 0
        user['imagenes_usadas'] = 0
    return user

def descontar_credito(email, es_imagen=False):
    columna = "imagenes_usadas" if es_imagen else "preguntas_usadas"
    res = supabase.table("perfiles").select(columna).eq("email", email).single().execute()
    nuevo_valor = res.data[columna] + 1
    supabase.table("perfiles").update({columna: nuevo_valor}).eq("email", email).execute()