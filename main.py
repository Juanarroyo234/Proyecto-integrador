from fastapi import FastAPI, Depends, HTTPException, Request, Query, APIRouter, UploadFile, File, Form
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
from fastapi.responses import HTMLResponse
import matplotlib.pyplot as plt
import io
import base64
from pydantic import BaseModel
from uuid import uuid4
from supabase_client import supabase



from operations import (
    get_partidos_ganados_por_local,
    calcular_tabla_puntos,
    agregar_partido,
    eliminar_partido,
    actualizar_partido
)
from data_base import get_db, Base, engine
from models import Partido, Equipo, Jugador
from schemas import PartidoSchema, PartidoCreate, EquipoCreate, JugadorCreate, PartidoUpdate,PartidoEliminarSchema

Equipo.__table__.create(bind=engine, checkfirst=True)
# Inicializar app FastAPI
app = FastAPI()
router = APIRouter()




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
def agregar_partido_endpoint(partido: PartidoCreate, db: Session = Depends(get_db)):
    return agregar_partido(
        db,
        partido.equipo_local,
        partido.equipo_visitante,
        partido.goles_local,
        partido.goles_visitante,
        partido.resultado
    )


# Eliminar partido
@app.delete("/partidos/")
def eliminar_partido_endpoint(datos: PartidoEliminarSchema, db: Session = Depends(get_db)):
    partido = db.query(Partido).filter_by(
        equipo_local=datos.equipo_local,
        equipo_visitante=datos.equipo_visitante
    ).first()
    if not partido:
        raise HTTPException(status_code=404, detail="Partido no encontrado")
    db.delete(partido)
    db.commit()
    return {"mensaje": "Partido eliminado correctamente"}
# Actualizar partido
@app.put("/partidos/")
def actualizar_partido_endpoint(partido: PartidoUpdate, db: Session = Depends(get_db)):
    return actualizar_partido(
        db,
        partido.equipo_local,
        partido.equipo_visitante,
        partido.goles_local,
        partido.goles_visitante,
        partido.resultado
    )

@app.delete("/partidos/")
def eliminar_partido_endpoint(equipo_local: str, equipo_visitante: str, db: Session = Depends(get_db)):
    partido = db.query(Partido).filter_by(equipo_local=equipo_local, equipo_visitante=equipo_visitante).first()
    if not partido:
        raise HTTPException(status_code=404, detail="Partido no encontrado")
    db.delete(partido)
    db.commit()
    return {"mensaje": "Partido eliminado correctamente"}
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

@app.get("/enfrentar", response_class=HTMLResponse)
def enfrentar_equipos(equipo1: str, equipo2: str, db: Session = Depends(get_db)):
    if equipo1 == equipo2:
        return HTMLResponse("<p>No se puede enfrentar el mismo equipo contra sí mismo.</p>")

    # Consultar partidos entre equipo1 y equipo2 desde la base de datos
    partidos = db.query(Partido).filter(
        ((Partido.equipo_local == equipo1) & (Partido.equipo_visitante == equipo2)) |
        ((Partido.equipo_local == equipo2) & (Partido.equipo_visitante == equipo1))
    ).all()

    if not partidos:
        return HTMLResponse(f"<p>No se encontraron enfrentamientos entre {equipo1} y {equipo2}.</p>")

    # Construir DataFrame para facilitar manipulación
    data = {
        "equipo_local": [p.equipo_local for p in partidos],
        "equipo_visitante": [p.equipo_visitante for p in partidos],
        "goles_local": [p.goles_local for p in partidos],
        "goles_visitante": [p.goles_visitante for p in partidos],
    }
    df = pd.DataFrame(data)

    # Calcular resultado por partido
    def calcular_resultado(fila):
        if fila["goles_local"] == fila["goles_visitante"]:
            return "Empate"
        elif fila["goles_local"] > fila["goles_visitante"]:
            return fila["equipo_local"]
        else:
            return fila["equipo_visitante"]

    df["resultado"] = df.apply(calcular_resultado, axis=1)

    conteo_resultados = df["resultado"].value_counts()

    # Graficar resultados en pie chart
    fig, ax = plt.subplots()
    conteo_resultados.plot.pie(
        autopct="%1.1f%%",
        ax=ax,
        startangle=90,
        colors=["#4CAF50", "#F44336", "#FFC107"]  # Verde, rojo, amarillo, opcional
    )
    ax.set_ylabel("")
    ax.set_title(f"Historial de enfrentamientos: {equipo1} vs {equipo2}")

    # Convertir gráfico a imagen base64 para incrustar en HTML
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode("utf-8")

    html = f"""
    <h3>Historial de enfrentamientos</h3>
    <p>{len(df)} partidos encontrados entre <strong>{equipo1}</strong> y <strong>{equipo2}</strong>.</p>
    <img src="data:image/png;base64,{img_base64}" alt="Gráfico de enfrentamientos">
    """
    return HTMLResponse(content=html)

@app.get("/equipos/todos")
def obtener_todos_equipos(db: Session = Depends(get_db)):
    try:
        equipos = db.query(Equipo).all()
        return [{"nombre": eq.nombre, "url_escudo": eq.url_escudo} for eq in equipos]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener los equipos: {str(e)}")

@app.post("/equipos/")
def agregar_equipo(equipo: EquipoCreate, db: Session = Depends(get_db)):
    try:
        nuevo_equipo = Equipo(nombre=equipo.nombre, url_escudo=equipo.url_escudo)
        db.add(nuevo_equipo)
        db.commit()
        db.refresh(nuevo_equipo)
        return {"mensaje": "Equipo agregado correctamente", "equipo": {"nombre": nuevo_equipo.nombre, "url_escudo": nuevo_equipo.url_escudo}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al agregar equipo: {str(e)}")

@app.post("/jugadores/")
async def crear_jugador(
    nombre: str = Form(...),
    equipo: str = Form(...),
    nacionalidad: str = Form(...),
    foto: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        # Validar tipo de imagen
        if not foto.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            raise HTTPException(status_code=400, detail="Formato de imagen no soportado.")

        # Leer contenido del archivo
        contenido = await foto.read()
        print(f"📦 Tamaño del archivo: {len(contenido)} bytes")

        # Crear nombre único
        filename = f"{str(uuid4())}_{foto.filename}"

        # Subir imagen a Supabase Storage
        res = supabase.storage.from_('jugadores').upload(
            filename,
            contenido,
            {
                "content-type": foto.content_type,
                "x-upsert": "true"
            }
        )

        print("📦 Respuesta upload Supabase:", res)
        print("📦 Tipo de respuesta:", type(res))
        print("📦 Atributos:", dir(res))

        if not res or not hasattr(res, "path") or not res.path:
            print("❌ La subida a Supabase NO devolvió un path válido")
            raise HTTPException(status_code=500, detail="Fallo al subir la imagen a Supabase.")
        else:
            print("✅ Subida exitosa, path:", res.path)

        # Obtener URL pública
        imagen_url = supabase.storage.from_('jugadores').get_public_url(res.path)
        print(f"✅ Imagen subida correctamente: {imagen_url}")

        # Crear jugador en la base de datos
        nuevo_jugador = Jugador(
            nombre=nombre,
            equipo=equipo,
            nacionalidad=nacionalidad,
            imagen_url=imagen_url  # ✅ Aquí está bien el nombre del campo
        )
        db.add(nuevo_jugador)
        db.commit()
        db.refresh(nuevo_jugador)

        # Respuesta
        return {
            "id": nuevo_jugador.id,
            "nombre": nuevo_jugador.nombre,
            "equipo": nuevo_jugador.equipo,
            "nacionalidad": nuevo_jugador.nacionalidad,
            "imagen_url": nuevo_jugador.imagen_url  # ✅ Aquí también
        }

    except Exception as e:
        print(f"🛑 Excepción inesperada: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al guardar jugador: {str(e)}")

@app.get("/jugadores/")
def listar_jugadores(db: Session = Depends(get_db)):
    jugadores = db.query(Jugador).all()
    return [
        {
            "id": j.id,
            "nombre": j.nombre,
            "equipo": j.equipo,
            "nacionalidad": j.nacionalidad,
            "imagen_url": j.imagen_url
        }
        for j in jugadores
    ]

@app.delete("/jugadores/{jugador_id}")
def eliminar_jugador(jugador_id: int, db: Session = Depends(get_db)):
    jugador = db.query(Jugador).filter(Jugador.id == jugador_id).first()
    if not jugador:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")

    db.delete(jugador)
    db.commit()
    return {"mensaje": "Jugador eliminado correctamente"}

@app.get("/desarrollador")
def obtener_info_desarrollador():
    return {
        "nombre": "Juan Esteban Arroyo",
        "correo": "jearroyo27@ucatolica.edu.co",
        "github": "https://github.com/Juanarroyo234",
        "rol": "Estudiante",
        "institucion": "Universidad Catolica de Colombia"
    }

@app.get("/planeacion")
def obtener_fase_planeacion():
    return {
        "fase": "Planeación",
        "elementos": {
            "casos_de_uso": [
                "Registrar jugadores con imagen, nombre y nacionalidad.",
                "Administrar partidos y resultados.",
                "Visualizar tabla de posiciones y estadísticas.",
                "Realizar predicciones de partidos usando IA."
            ],
            "modelo_datos": "Modelo relacional con tablas de Equipos, Jugadores, Partidos y Predicciones. Incluye soporte para imágenes de jugadores y escudos de equipos.",
            "objetivos": [
                "Ofrecer una plataforma interactiva para gestión de estadísticas de fútbol.",
                "Predecir resultados usando machine learning.",
                "Brindar visualización amigable para usuarios y administradores."
            ],
            "fuente_datos": "Datos simulados o personalizados extraídos de partidos reales para pruebas del sistema."
        }
    }

@app.get("/diseno")
def obtener_fase_diseno():
    return {
        "fase": "Diseño",
        "elementos": {
            "diagrama_clases": "Incluye clases como Equipo, Jugador, Partido, Prediccion, conectadas mediante relaciones uno-a-muchos y muchos-a-uno.",
            "mapa_endpoints": [
                "/equipos [GET, POST]",
                "/jugadores [GET, POST]",
                "/partidos [GET, POST, PUT, DELETE]",
                "/prediccion [POST]",
                "/tabla-posiciones [GET]",
                "/desarrollador, /planeacion, /diseno, /objetivo [GET]"
            ],
            "mockups_wireframes": "Diseños en HTML/CSS simulando vistas principales: inicio, predicción, tabla, administrador y enfrentamiento. Estilo sencillo con carrusel informativo y navegación clara."
        }
    }

@app.get("/objetivo")
def obtener_objetivo_proyecto():
    return {
        "objetivo": (
            "Desarrollar una plataforma web para la gestión de estadísticas de fútbol que "
            "permita registrar equipos, jugadores y partidos, visualizar datos relevantes como la tabla de posiciones, "
            "y predecir resultados utilizando modelos de Machine Learning, todo desde una interfaz web amigable."
        )
    }

