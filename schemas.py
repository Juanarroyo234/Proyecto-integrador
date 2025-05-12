from pydantic import BaseModel
from typing import Optional

class PartidoSchema(BaseModel):
    equipo_local: str
    equipo_visitante: str
    goles_local: Optional[int] = 0  # Asignar 0 como valor predeterminado si es None
    goles_visitante: Optional[int] = 0  # Asignar 0 como valor predeterminado si es None
    resultado: str

    class Config:
        orm_mode = True


class EquipoSchema(BaseModel):
    nombre: str
    partidos_jugados: int
    goles_a_favor: int
    goles_en_contra: int
    victorias: int
    empates: int
    derrotas: int

    class Config:
        orm_mode = True