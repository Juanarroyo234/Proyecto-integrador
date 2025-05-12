import sqlite3

conn = sqlite3.connect("futbol.db")
cursor = conn.cursor()
cursor.execute("SELECT DISTINCT equipo_local FROM partidos")
equipos_locales = cursor.fetchall()

cursor.execute("SELECT DISTINCT equipo_visitante FROM partidos")
equipos_visitantes = cursor.fetchall()

equipos_unicos = set([e[0] for e in equipos_locales] + [e[0] for e in equipos_visitantes])
print("Equipos únicos:", equipos_unicos)

conn.close()
