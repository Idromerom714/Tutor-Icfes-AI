import streamlit as st
from supabase import create_client
from datetime import datetime
import pytz # Debes añadir 'pytz' a tu requirements.txt

def obtener_datos_usuario(email):
    # Forzar hora de Colombia
    tz = pytz.timezone('America/Bogota')
    hoy = datetime.now(tz).date().isoformat()
    
    res = supabase.table("perfiles").select("*").eq("email", email).single().execute()
    user = res.data
    
    if user['ultima_fecha'] != hoy:
        # Si la fecha guardada es distinta a HOY en Colombia, reiniciamos
        supabase.table("perfiles").update({
            "preguntas_usadas": 0, 
            "imagenes_usadas": 0, 
            "ultima_fecha": hoy
        }).eq("email", email).execute()
        
        # Actualizamos el objeto local para la sesión actual
        user['preguntas_usadas'] = 0
        user['imagenes_usadas'] = 0
        
    return user