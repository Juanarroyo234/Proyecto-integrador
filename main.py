from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import logging
from operations import get_partidos_ganados_por_local, calcular_tabla_puntos, agregar_partido, eliminar_partido, \
    actualizar_partido
from data_base import get_db, Base, engine
from models import Partido
from schemas import PartidoSchema
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import pandas as pd

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


logging.basicConfig(level=logging.DEBUG)


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


@app.get("/verificar_partidos")
def verificar_partidos(db: Session = Depends(get_db)):
    try:
        partidos = db.query(Partido).all()
        if not partidos:
            raise HTTPException(status_code=404, detail="No hay partidos en PostgreSQL")
        return {"message": f"Hay {len(partidos)} partidos en la base de datos"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al verificar los partidos: {str(e)}")


@app.get("/ganados-local", response_model=List[PartidoSchema])
def ganados_local(db: Session = Depends(get_db)):
    return get_partidos_ganados_por_local(db)


@app.get("/predecir/")
def predecir(equipo_local: str, equipo_visitante: str, db: Session = Depends(get_db)):
    try:
        # Leer los datos de la base de datos
        partidos = db.query(Partido).all()

        if not partidos:
            raise HTTPException(status_code=404, detail="No hay datos suficientes para el entrenamiento.")

        # Convertir a DataFrame
        data = {
            "equipo_local": [p.equipo_local for p in partidos],
            "equipo_visitante": [p.equipo_visitante for p in partidos],
            "resultado": [p.resultado for p in partidos]
        }
        df = pd.DataFrame(data)

        # Codificación
        le = LabelEncoder()
        todos_equipos = pd.concat([df["equipo_local"], df["equipo_visitante"]])
        le.fit(todos_equipos)

        df["equipo_local_encoded"] = le.transform(df["equipo_local"])
        df["equipo_visitante_encoded"] = le.transform(df["equipo_visitante"])

        # Entrenamiento del modelo
        X = df[["equipo_local_encoded", "equipo_visitante_encoded"]]
        y = df["resultado"]

        modelo = RandomForestClassifier()
        modelo.fit(X, y)

        # Validación de equipos
        equipos_disponibles = set(le.classes_)
        if equipo_local not in equipos_disponibles or equipo_visitante not in equipos_disponibles:
            return {"error": "Uno o ambos equipos no están en el dataset original."}

        # Predicción
        local_encoded = le.transform([equipo_local])[0]
        visita_encoded = le.transform([equipo_visitante])[0]
        X_nuevo = [[local_encoded, visita_encoded]]
        prediccion = modelo.predict(X_nuevo)[0]

        return {
            "equipo_local": equipo_local,
            "equipo_visitante": equipo_visitante,
            "prediccion": prediccion
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al predecir el resultado: {str(e)}")


@app.get("/tabla")
def tabla_liga(db: Session = Depends(get_db)):
    return calcular_tabla_puntos(db)


@app.post("/partidos/")
def agregar_partido_endpoint(equipo_local: str, equipo_visitante: str, goles_local: int, goles_visitante: int,
                             resultado: str, db: Session = Depends(get_db)):
    return agregar_partido(db, equipo_local, equipo_visitante, goles_local, goles_visitante, resultado)


@app.delete("/partidos/")
def eliminar_partido_endpoint(equipo_local: str, equipo_visitante: str, db: Session = Depends(get_db)):
    return eliminar_partido(db, equipo_local, equipo_visitante)


@app.put("/partidos/")
def actualizar_partido_endpoint(equipo_local: str, equipo_visitante: str, goles_local: int, goles_visitante: int,
                                resultado: str, db: Session = Depends(get_db)):
    return actualizar_partido(db, equipo_local, equipo_visitante, goles_local, goles_visitante, resultado)


@app.get("/partido")
def get_partido(equipo_local: str, equipo_visitante: str, db: Session = Depends(get_db)):
    try:
        logging.debug("Iniciando consulta para partido: %s vs %s", equipo_local, equipo_visitante)
        partido = db.query(Partido).filter_by(
            equipo_local=equipo_local,
            equipo_visitante=equipo_visitante
        ).first()

        if not partido:
            logging.warning("No se encontró el partido: %s vs %s", equipo_local, equipo_visitante)
            raise HTTPException(status_code=404, detail="Partido no encontrado")

        logging.debug("Partido encontrado: %s vs %s", equipo_local, equipo_visitante)
        return partido

    except Exception as e:
        logging.error("Error al obtener el partido: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

