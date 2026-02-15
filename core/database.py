import streamlit as st
from supabase import create_client
from datetime import date

# Conexión (Streamlit tomará esto de 'Secrets' o '.env')
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

def obtener_datos_usuario(email):
    """Trae la info del estudiante y resetea créditos si es un nuevo día."""
    res = supabase.table("perfiles").select("*").eq("email", email).single().execute()
    user = res.data
    
    hoy = date.today().isoformat()
    if user['ultima_fecha'] != hoy:
        # Es un nuevo día: Resetear contadores en DB
        supabase.table("perfiles").update({
            "preguntas_usadas": 0,
            "imagenes_usadas": 0,
            "ultima_fecha": hoy
        }).eq("email", email).execute()
        # Actualizar objeto local
        user['preguntas_usadas'] = 0
        user['imagenes_usadas'] = 0
        user['ultima_fecha'] = hoy
        
    return user

def descontar_credito(email, es_imagen=False):
    """Resta un crédito al usuario en Supabase."""
    columna = "imagenes_usadas" if es_imagen else "preguntas_usadas"
    # Obtenemos valor actual y sumamos 1
    res = supabase.table("perfiles").select(columna).eq("email", email).single().execute()
    nuevo_valor = res.data[columna] + 1
    
    supabase.table("perfiles").update({columna: nuevo_valor}).eq("email", email).execute()