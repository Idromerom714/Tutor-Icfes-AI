#auth.py
import bcrypt

def hashear_pin(pin: str) -> str:
    """Convierte el PIN en un hash seguro antes de guardarlo en Supabase"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pin.encode('utf-8'), salt).decode('utf-8')

def verificar_pin(pin_ingresado: str, hash_guardado: str) -> bool:
    """Compara el PIN ingresado contra el hash en BD, sin exponer el original"""
    return bcrypt.checkpw(pin_ingresado.encode('utf-8'), hash_guardado.encode('utf-8'))