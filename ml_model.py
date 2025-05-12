import pickle

# Cargar modelo
with open("modelo_rf.pkl", "rb") as f:
    modelo = pickle.load(f)

# Cargar codificador
with open("label_encoder.pkl", "rb") as f:
    le = pickle.load(f)

# Obtener los equipos conocidos
equipos_disponibles = set(le.classes_)

def predecir_resultado(equipo_local: str, equipo_visitante: str) -> str:
    if equipo_local not in equipos_disponibles or equipo_visitante not in equipos_disponibles:
        return f"❌ Uno o ambos equipos no están en el dataset original."

    local_encoded = le.transform([equipo_local])[0]
    visita_encoded = le.transform([equipo_visitante])[0]

    X_nuevo = [[local_encoded, visita_encoded]]
    prediccion = modelo.predict(X_nuevo)[0]
    return prediccion



