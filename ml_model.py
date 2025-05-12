import psycopg2
import pickle
from sklearn.preprocessing import LabelEncoder

# Configuración de la conexión a la base de datos PostgreSQL en Clever Cloud
# Aquí debes usar las credenciales de tu base de datos en Clever Cloud
conn = psycopg2.connect(
    host="bvlz8acs4nqffk3wiyl6-postgresql.services.clever-cloud.com",
    port="5432",
    dbname="bvlz8acs4nqffk3wiyl6",
    user="ua1toi4gask0co1lfu3b",
    password="V4P8UFLejtyier9xDiC8nkm8sxJUgs"
)

# Crear un cursor para ejecutar consultas SQL
cursor = conn.cursor()

# Obtener los equipos disponibles desde la base de datos (puedes ajustar esta consulta según tu estructura)
cursor.execute("SELECT DISTINCT equipo_local FROM partidos UNION SELECT DISTINCT equipo_visitante FROM partidos;")
equipos_disponibles = set(row[0] for row in cursor.fetchall())

# Aquí deberías obtener el modelo de la base de datos, si lo tienes almacenado en algún lugar.
# Suponiendo que ya tienes el modelo entrenado en memoria o en algún archivo:
with open("modelo_rf.pkl", "rb") as f:
    modelo = pickle.load(f)

# El codificador de etiquetas (LabelEncoder) debe estar en memoria también, si lo tienes en un archivo o base de datos
# Si lo tienes en la base de datos, puedes obtener las clases y reconstruir el codificador
le = LabelEncoder()
le.fit(list(equipos_disponibles))


def predecir_resultado(equipo_local: str, equipo_visitante: str) -> str:
    if equipo_local not in equipos_disponibles or equipo_visitante not in equipos_disponibles:
        return f"❌ Uno o ambos equipos no están en el dataset original."

    # Codificar los equipos usando el LabelEncoder
    local_encoded = le.transform([equipo_local])[0]
    visita_encoded = le.transform([equipo_visitante])[0]

    X_nuevo = [[local_encoded, visita_encoded]]
    prediccion = modelo.predict(X_nuevo)[0]

    return f"El resultado predicho para el partido {equipo_local} vs {equipo_visitante} es: {prediccion}"


# No olvides cerrar la conexión a la base de datos
cursor.close()
conn.close()
