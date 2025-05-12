import pandas as pd
import sqlite3

# Cargar el CSV
df = pd.read_csv("full_data.csv")

# Crear columna 'resultado'
def calcular_resultado(row):
    if row["H_Score"] > row["A_Score"]:
        return "local"
    elif row["H_Score"] < row["A_Score"]:
        return "visita"
    else:
        return "empate"

df["resultado"] = df.apply(calcular_resultado, axis=1)

# Seleccionar columnas útiles y renombrarlas
df_filtrado = df[["Home", "Away", "H_Score", "A_Score", "resultado"]]
df_filtrado.columns = ["equipo_local", "equipo_visitante", "goles_local", "goles_visitante", "resultado"]

# Añadir columna id manualmente
df_filtrado.insert(0, "id", range(1, len(df_filtrado) + 1))

# Crear base de datos
conn = sqlite3.connect("futbol.db")
df_filtrado.to_sql("partidos", conn, if_exists="replace", index=False)
conn.close()

print("✅ Base de datos 'futbol.db' con ID creada con éxito.")

