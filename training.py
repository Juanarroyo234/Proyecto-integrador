import sqlite3
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import pickle

# Leer desde DB limpia
conn = sqlite3.connect("futbol.db")
df = pd.read_sql("SELECT * FROM partidos", con=conn)
conn.close()

if df.empty:
    print("⚠️ La tabla 'partidos' está vacía.")
    exit()

# Filtrar por equipos que están realmente en la base (opcional, solo por seguridad extra)
equipos_validos = set(df["equipo_local"]).union(set(df["equipo_visitante"]))
df = df[df["equipo_local"].isin(equipos_validos) & df["equipo_visitante"].isin(equipos_validos)]

# Codificación
le = LabelEncoder()
todos_equipos = pd.concat([df["equipo_local"], df["equipo_visitante"]])
le.fit(todos_equipos)

df["equipo_local_encoded"] = le.transform(df["equipo_local"])
df["equipo_visitante_encoded"] = le.transform(df["equipo_visitante"])

# Features y target
X = df[["equipo_local_encoded", "equipo_visitante_encoded"]]
y = df["resultado"]

# Entrenamiento
modelo = RandomForestClassifier()
modelo.fit(X, y)

# Guardar todo limpio
with open("modelo_rf.pkl", "wb") as f:
    pickle.dump(modelo, f)

with open("label_encoder.pkl", "wb") as f:
    pickle.dump(le, f)

print("✅ Modelo y encoder regenerados desde datos válidos.")

