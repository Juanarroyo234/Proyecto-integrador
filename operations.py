# operations.py

from sqlalchemy.orm import Session
from models import Partido
from collections import defaultdict
from fastapi import HTTPException

def get_partidos_ganados_por_local(db: Session):
    return db.query(Partido).filter(Partido.goles_local > Partido.goles_visitante).all()


def calcular_tabla_puntos(db: Session):
    # Obtener todos los equipos únicos que aparecen como local o visitante
    equipos_locales = db.query(Partido.equipo_local).distinct().all()
    equipos_visitantes = db.query(Partido.equipo_visitante).distinct().all()

    # Convertir resultados a un set plano de strings
    equipos_validos = set([eq[0] for eq in equipos_locales] + [eq[0] for eq in equipos_visitantes])

    # Obtener todos los partidos
    partidos = db.query(Partido).all()

    tabla = defaultdict(int)

    for partido in partidos:
        local = partido.equipo_local
        visitante = partido.equipo_visitante
        resultado = partido.resultado

        # Filtrar solo si los equipos están entre los originales
        if local in equipos_validos and visitante in equipos_validos:
            if resultado == "local":
                tabla[local] += 3
            elif resultado == "visita":
                tabla[visitante] += 3
            else:  # empate
                tabla[local] += 1
                tabla[visitante] += 1

    # Ordenar tabla
    tabla_ordenada = sorted(
        [{"equipo": equipo, "puntos": puntos} for equipo, puntos in tabla.items()],
        key=lambda x: x["puntos"],
        reverse=True
    )

    return tabla_ordenada


def agregar_partido(db: Session, equipo_local: str, equipo_visitante: str, goles_local: int, goles_visitante: int,
                    resultado: str):
    db_partido = Partido(
        equipo_local=equipo_local,
        equipo_visitante=equipo_visitante,
        goles_local=goles_local,
        goles_visitante=goles_visitante,
        resultado=resultado
    )
    db.add(db_partido)
    db.commit()
    db.refresh(db_partido)
    return db_partido


# Función para eliminar un partido
def eliminar_partido(db: Session, equipo_local: str, equipo_visitante: str):
    db_partido = db.query(Partido).filter(Partido.equipo_local == equipo_local,
                                          Partido.equipo_visitante == equipo_visitante).first()
    if db_partido is None:
        raise HTTPException(status_code=404, detail="Partido no encontrado")
    db.delete(db_partido)
    db.commit()
    return {"message": f"Partido {equipo_local} vs {equipo_visitante} eliminado exitosamente."}


# Función para actualizar un partido
def actualizar_partido(db: Session, equipo_local: str, equipo_visitante: str, goles_local: int, goles_visitante: int,
                       resultado: str):
    db_partido = db.query(Partido).filter(Partido.equipo_local == equipo_local,
                                          Partido.equipo_visitante == equipo_visitante).first()
    if db_partido is None:
        raise HTTPException(status_code=404, detail="Partido no encontrado")

    db_partido.goles_local = goles_local
    db_partido.goles_visitante = goles_visitante
    db_partido.resultado = resultado

    db.commit()
    db.refresh(db_partido)
    return db_partido