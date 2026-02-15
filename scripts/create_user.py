import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv() # Carga las llaves del archivo .env

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

def crear_estudiante(email, pin, plan):
    """
    plan: 'basico' o 'avanzado'
    """
    nuevo_usuario = {
        "email": email,
        "pin": pin,
        "plan": plan,
        "preguntas_usadas": 0,
        "imagenes_usadas": 0,
        "ultima_fecha": "2000-01-01" # Para forzar el primer reset
    }
    
    try:
        supabase.table("perfiles").insert(nuevo_usuario).execute()
        print(f"✅ Estudiante {email} creado con éxito en el plan {plan}.")
    except Exception as e:
        print(f"❌ Error: {e}")

# Ejemplo de uso:
if __name__ == "__main__":
    correo = input("Email del estudiante: ")
    pass_pin = input("PIN de 4 dígitos: ")
    tipo_plan = input("Plan (basico/avanzado): ").lower()
    crear_estudiante(correo, pass_pin, tipo_plan)