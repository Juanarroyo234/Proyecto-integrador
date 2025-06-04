from fastapi import FastAPI, Depends, HTTPException, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List
import logging
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from collections import defaultdict

from operations import (
    get_partidos_ganados_por_local,
    calcular_tabla_puntos,
    agregar_partido,
    eliminar_partido,
    actualizar_partido
)
from data_base import get_db, Base, engine
from models import Partido
from schemas import PartidoSchema

# Inicializar app FastAPI
app = FastAPI()




# Montar carpeta estática para CSS, JS, escudos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurar templates Jinja2
templates = Jinja2Templates(directory="templates")

# Crear las tablas en la base de datos si no existen
Base.metadata.create_all(bind=engine)

# Configurar logging
logging.basicConfig(level=logging.INFO)

# Página principal
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Obtener todos los equipos disponibles
@app.get("/equipos")
def get_equipos(db: Session = Depends(get_db)):
    try:
        partidos = db.query(Partido).all()
        if not partidos:
            return {"equipos": []}

        equipos_local = set(p.equipo_local for p in partidos)
        equipos_visita = set(p.equipo_visitante for p in partidos)
        equipos = sorted(list(equipos_local.union(equipos_visita)))
        return {"equipos": equipos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener equipos: {str(e)}")

# Endpoint para predecir resultados
@app.get("/predecir/")
def predecir(equipo_local: str, equipo_visitante: str, db: Session = Depends(get_db)):
    try:
        partidos = db.query(Partido).all()
        if not partidos:
            raise HTTPException(status_code=404, detail="No hay datos suficientes para el entrenamiento.")

        data = {
            "equipo_local": [p.equipo_local for p in partidos],
            "equipo_visitante": [p.equipo_visitante for p in partidos],
            "resultado": [p.resultado for p in partidos]
        }
        df = pd.DataFrame(data)

        le = LabelEncoder()
        todos_equipos = pd.concat([df["equipo_local"], df["equipo_visitante"]])
        le.fit(todos_equipos)

        df["equipo_local_encoded"] = le.transform(df["equipo_local"])
        df["equipo_visitante_encoded"] = le.transform(df["equipo_visitante"])

        X = df[["equipo_local_encoded", "equipo_visitante_encoded"]]
        y = df["resultado"]

        modelo = RandomForestClassifier()
        modelo.fit(X, y)

        equipos_disponibles = set(le.classes_)
        if equipo_local not in equipos_disponibles or equipo_visitante not in equipos_disponibles:
            return {"error": "Uno o ambos equipos no están en el dataset original."}

        local_encoded = le.transform([equipo_local])[0]
        visita_encoded = le.transform([equipo_visitante])[0]
        X_nuevo = pd.DataFrame([[local_encoded, visita_encoded]], columns=["equipo_local_encoded", "equipo_visitante_encoded"])

        prediccion = modelo.predict(X_nuevo)[0]

        return {
            "equipo_local": equipo_local,
            "equipo_visitante": equipo_visitante,
            "prediccion": prediccion
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al predecir el resultado: {str(e)}")

# Obtener todos los partidos
@app.get("/partidos", response_model=List[PartidoSchema])
def get_partidos(db: Session = Depends(get_db)):
    try:
        partidos = db.query(Partido).all()
        if not partidos:
            raise HTTPException(status_code=404, detail="No hay partidos disponibles")

        for partido in partidos:
            if partido.goles_local is None:
                partido.goles_local = 0
            if partido.goles_visitante is None:
                partido.goles_visitante = 0

        return partidos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

# Verificar cuántos partidos hay en la base
@app.get("/verificar_partidos")
def verificar_partidos(db: Session = Depends(get_db)):
    try:
        partidos = db.query(Partido).all()
        if not partidos:
            raise HTTPException(status_code=404, detail="No hay partidos en PostgreSQL")
        return {"message": f"Hay {len(partidos)} partidos en la base de datos"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al verificar los partidos: {str(e)}")

# Obtener partidos ganados por locales
@app.get("/ganados-local", response_model=List[PartidoSchema])
def ganados_local(db: Session = Depends(get_db)):
    return get_partidos_ganados_por_local(db)

# Calcular tabla de puntos
@app.get("/tabla")
def tabla_liga(db: Session = Depends(get_db)):
    return calcular_tabla_puntos(db)

# Agregar nuevo partido
@app.post("/partidos/")
def agregar_partido_endpoint(equipo_local: str, equipo_visitante: str, goles_local: int, goles_visitante: int, resultado: str, db: Session = Depends(get_db)):
    return agregar_partido(db, equipo_local, equipo_visitante, goles_local, goles_visitante, resultado)

# Eliminar partido
@app.delete("/partidos/")
def eliminar_partido_endpoint(equipo_local: str, equipo_visitante: str, db: Session = Depends(get_db)):
    return eliminar_partido(db, equipo_local, equipo_visitante)

# Actualizar partido
@app.put("/partidos/")
def actualizar_partido_endpoint(equipo_local: str, equipo_visitante: str, goles_local: int, goles_visitante: int, resultado: str, db: Session = Depends(get_db)):
    return actualizar_partido(db, equipo_local, equipo_visitante, goles_local, goles_visitante, resultado)

# Consultar un solo partido
@app.get("/partido")
def get_partido(equipo_local: str, equipo_visitante: str, db: Session = Depends(get_db)):
    try:
        partido = db.query(Partido).filter_by(
            equipo_local=equipo_local,
            equipo_visitante=equipo_visitante
        ).first()

        if not partido:
            raise HTTPException(status_code=404, detail="Partido no encontrado")

        return partido
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
@app.get("/tabla_posiciones")
def tabla_posiciones_json(db: Session = Depends(get_db)):
    partidos = db.query(Partido).all()
    if not partidos:
        raise HTTPException(status_code=404, detail="No hay partidos en la base de datos")

    tabla = defaultdict(lambda: {"equipo": "", "jugados": 0, "ganados": 0, "empatados": 0, "perdidos": 0, "puntos": 0})

    for p in partidos:
        local = p.equipo_local
        visita = p.equipo_visitante
        resultado = p.resultado

        tabla[local]["equipo"] = local
        tabla[visita]["equipo"] = visita

        tabla[local]["jugados"] += 1
        tabla[visita]["jugados"] += 1

        if resultado == "L":
            tabla[local]["ganados"] += 1
            tabla[local]["puntos"] += 3
            tabla[visita]["perdidos"] += 1
        elif resultado == "V":
            tabla[visita]["ganados"] += 1
            tabla[visita]["puntos"] += 3
            tabla[local]["perdidos"] += 1
        elif resultado == "E":
            tabla[local]["empatados"] += 1
            tabla[visita]["empatados"] += 1
            tabla[local]["puntos"] += 1
            tabla[visita]["puntos"] += 1

    # Convertir a lista y ordenar por puntos descendente
    tabla_ordenada = sorted(tabla.values(), key=lambda x: x["puntos"], reverse=True)

    return JSONResponse(content=tabla_ordenada)

@app.get("/estadisticas/{nombre}")
def estadisticas(nombre: str, db: Session = Depends(get_db)):
    partidos = db.query(Partido).filter(
        (Partido.equipo_local == nombre) | (Partido.equipo_visitante == nombre)
    ).all()

    victorias = 0
    empates = 0
    derrotas = 0

    for partido in partidos:
        if partido.resultado == "empate":
            empates += 1
        elif partido.resultado == "local":
            if partido.equipo_local == nombre:
                victorias += 1
            else:
                derrotas += 1
        elif partido.resultado == "visitante":
            if partido.equipo_visitante == nombre:
                victorias += 1
            else:
                derrotas += 1

    puntos = victorias * 3 + empates

    return {
        "victorias": victorias,
        "empates": empates,
        "derrotas": derrotas,
        "puntos": puntos
    }

@app.get("/partidos/filtrar")
def filtrar_partidos(equipo: str = Query(...), db: Session = Depends(get_db)):
    partidos = db.query(Partido).filter(
        (Partido.equipo_local == equipo) | (Partido.equipo_visitante == equipo)
    ).all()
    # Serializar la respuesta, por ejemplo:
    return [
        {
            "equipo_local": p.equipo_local,
            "equipo_visitante": p.equipo_visitante,
            "goles_local": p.goles_local,
            "goles_visitante": p.goles_visitante,
            "resultado": p.resultado
        } for p in partidos
    ]