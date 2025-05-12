from sqlalchemy import Column, Integer, String
from data_base import Base

class Partido(Base):
    __tablename__ = "partidos"

    equipo_local = Column(String, primary_key=True)
    equipo_visitante = Column(String, primary_key=True)
    goles_local = Column(Integer)
    goles_visitante = Column(Integer)
    resultado = Column(String)

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre_usuario = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)

    def __repr__(self):
        return f"Usuario(id={self.id}, nombre_usuario={self.nombre_usuario}, email={self.email})"
