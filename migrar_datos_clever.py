from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Partido, Base
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde el .env
load_dotenv()

# Construir la URL de PostgreSQL
POSTGRES_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@" \
               f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

# Verificar la URL generada
print(f"Conectando a PostgreSQL en: {POSTGRES_URL}")

# 1. Conexión a SQLite (origen)
SQLITE_URL = "sqlite:///./futbol.db"
sqlite_engine = create_engine(SQLITE_URL)
SQLiteSession = sessionmaker(bind=sqlite_engine)
sqlite_db = SQLiteSession()

# 2. Conexión a PostgreSQL (destino)
postgres_engine = create_engine(POSTGRES_URL)
PostgresSession = sessionmaker(bind=postgres_engine)
postgres_db = PostgresSession()

# 3. Asegurarse de que las tablas existen en PostgreSQL
Base.metadata.create_all(bind=postgres_engine)

# 4. Leer los partidos desde SQLite
partidos = sqlite_db.query(Partido).all()

# Crear una lista de objetos para insertar en PostgreSQL
partidos_a_insertar = []

for partido in partidos:
    # Se podría optimizar más, por ejemplo, si tuvieras una lista de IDs existentes en PostgreSQL
    nuevo = Partido(
        equipo_local=partido.equipo_local,
        equipo_visitante=partido.equipo_visitante,
        goles_local=partido.goles_local,
        goles_visitante=partido.goles_visitante,
        resultado=partido.resultado
    )
    partidos_a_insertar.append(nuevo)

# 5. Insertar en PostgreSQL en bloque
postgres_db.bulk_save_objects(partidos_a_insertar)

# Confirmar los cambios
postgres_db.commit()

# 6. Cerrar sesiones
sqlite_db.close()
postgres_db.close()

print("Migración completada con éxito.")
