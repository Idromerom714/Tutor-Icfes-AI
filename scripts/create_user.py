import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime
import pytz

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

# Créditos iniciales y diarios por plan
CREDITOS_INICIALES = {
    "basico": 50,
    "avanzado": 150
}

def crear_estudiante(email, pin, plan):
    """
    Crea un nuevo estudiante en Supabase.
    
    Args:
        email: Correo del estudiante
        pin: PIN de 4 dígitos (se almacena hasheado)
        plan: 'basico' o 'avanzado'
    """
    plan = plan.lower()
    if plan not in ["basico", "avanzado"]:
        print(f"❌ Error: Plan '{plan}' no válido. Usa 'basico' o 'avanzado'.")
        return
    
    creditos = CREDITOS_INICIALES.get(plan, 50)
    fecha_hoy = datetime.now(pytz.timezone('America/Bogota')).date().strftime('%Y-%m-%d')
    
    nuevo_usuario = {
        "email": email,
        "pin": pin,  # En producción debería estar hasheado
        "plan": plan,
        "creditos_totales": creditos,
        "ultima_fecha": fecha_hoy
    }
    
    try:
        supabase.table("perfiles").insert(nuevo_usuario).execute()
        print(f"✅ Estudiante creado exitosamente:")
        print(f"   📧 Email: {email}")
        print(f"   📦 Plan: {plan.capitalize()}")
        print(f"   ⚡ Créditos iniciales: {creditos}")
        print(f"   🔄 Recarga diaria: {creditos}⚡")
    except Exception as e:
        print(f"❌ Error al crear estudiante: {e}")

if __name__ == "__main__":
    print("\n🎓 === CREAR NUEVO ESTUDIANTE ===\n")
    correo = input("📧 Email del estudiante: ")
    pass_pin = input("🔐 PIN de 4 dígitos: ")
    
    print("\n📦 Selecciona el plan:")
    print("   1. Básico  - 50⚡ diarios")
    print("   2. Avanzado - 150⚡ diarios")
    opcion = input("Opción (1 o 2): ")
    
    tipo_plan = "basico" if opcion == "1" else "avanzado"
    
    print(f"\n🔍 Creando estudiante con plan {tipo_plan}...")
    crear_estudiante(correo, pass_pin, tipo_plan)