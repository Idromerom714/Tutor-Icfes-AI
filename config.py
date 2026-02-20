# config.py
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

# Validación: si falta alguna variable, el servidor no arranca
if not all([SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_JWT_SECRET]):
    raise ValueError("Faltan variables de entorno críticas. Revisa tu .env")