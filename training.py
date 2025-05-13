import pandas as pd
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import logging

# Configuración del log
logging.basicConfig(level=logging.INFO)

# Datos de conexión
DB_URL = "postgresql://{usuario}:{password}@{host}:{port}/{database}"

# Configuración de la conexión (sustituye con tus datos)
engine = create_engine(DB_URL)

# Consultar datos
logging.info("Conectando a la base de datos y obteniendo datos...")
query = "SELECT equipo_local, equipo_visitante, resultado FROM partidos"
df = pd.read_sql_query(query, engine)

# Preprocesamiento
logging.info("Preprocesando los datos...")
le = LabelEncoder()
df["equipo_local"] = le.fit_transform(df["equipo_local"])
df["equipo_visitante"] = le.transform(df["equipo_visitante"])
df["resultado"] = le.fit_transform(df["resultado"])

# Entrenamiento del modelo
logging.info("Entrenando el modelo...")
X = df[["equipo_local", "equipo_visitante"]]
y = df["resultado"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
modelo = RandomForestClassifier(n_estimators=100, random_state=42)
modelo.fit(X_train, y_train)

logging.info("Modelo entrenado exitosamente.")

# Obtener los equipos conocidos
equipos_disponibles = set(le.classes_)

def predecir_resultado(equipo_local: str, equipo_visitante: str) -> str:
    if equipo_local not in equipos_disponibles or equipo_visitante not in equipos_disponibles:
        return f"❌ Uno o ambos equipos no están en el dataset original."

    local_encoded = le.transform([equipo_local])[0]
    visita_encoded = le.transform([equipo_visitante])[0]

    X_nuevo = [[local_encoded, visita_encoded]]
    prediccion = modelo.predict(X_nuevo)[0]
    return le.inverse_transform([prediccion])[0]


