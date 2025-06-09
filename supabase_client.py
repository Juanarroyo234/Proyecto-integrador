from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()  # Cargar las variables del .env

# Obtener las variables por su NOMBRE, no por su valor
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET")

# Validar que no estén vacías
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("❌ SUPABASE_URL o SUPABASE_KEY no están definidos.")

# Crear cliente Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)