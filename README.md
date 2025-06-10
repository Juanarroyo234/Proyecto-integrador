# ⚽ Estadísticas de Fútbol

Este proyecto es una plataforma web interactiva que permite consultar y administrar información de fútbol, incluyendo estadísticas, resultados, predicciones, jugadores y más.

## 🚀 Características Principales

- 🔍 **Predicción de resultados** con modelos de Machine Learning.
- 📊 **Tabla de posiciones** actualizada dinámicamente.
- 🗓️ **Gestión de partidos**: agregar, actualizar y eliminar partidos.
- 📈 **Estadísticas de equipos**.
- ⚔️ **Comparador entre equipos** para enfrentar rivales.
- 🧑‍💼 **Configuración de jugadores** con carga de imágenes.
- 🧩 **Documentación técnica** (casos de uso, modelo de datos, endpoints, etc.).

## 🧠 Objetivo del Proyecto

Diseñar una plataforma web integral que permita explorar y gestionar datos de fútbol de manera amigable y automatizada, usando aprendizaje automático y tecnologías modernas.

## 🛠️ Tecnologías Utilizadas

- **Backend**: FastAPI (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Base de datos**: PostgreSQL (Clever Cloud)
- **Almacenamiento de imágenes**: Supabase Storage
- **ML/AI**: Scikit-learn (Random Forest)

## 🧑‍💻 Información del Desarrollador

**Nombre**: [Tu nombre]  
**Correo**: [Tu correo]  
**GitHub**: [Tu perfil de GitHub]

## 📚 Estructura del Proyecto


## 📌 Endpoints Importantes

| Ruta | Método | Descripción |
|------|--------|-------------|
| `/prediccion` | POST | Predice resultado de un partido |
| `/tabla-posiciones` | GET | Devuelve la tabla de posiciones |
| `/partidos` | POST, PUT, DELETE | Administra partidos |
| `/estadisticas` | GET | Muestra estadísticas de equipos |
| `/jugadores` | POST | Agrega jugadores con imagen |
| `/info-proyecto` | GET | Información general del proyecto |
| `/planeacion` | GET | Fase de planeación |
| `/diseno` | GET | Fase de diseño |

## 📝 Planeación y Diseño

Incluye:

- ✅ Casos de uso
- ✅ Modelo de datos con imágenes
- ✅ Objetivos y fuentes de datos
- ✅ Diagrama de clases
- ✅ Mapa de endpoints
- ✅ Wireframes de interfaz





```bash
git clone https://github.com/tuusuario/futbol-stats.git
cd futbol-stats
pip install -r requirements.txt
uvicorn app.main:app --reload
https://proyecto-integrador-rpv7.onrender.com

