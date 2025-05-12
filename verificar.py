from sqlalchemy.orm import Session
from data_base import SessionLocal
from models import Partido

def verificar_partidos():
    db: Session = SessionLocal()
    partidos = db.query(Partido).all()
    if not partidos:
        print("⚠️ La tabla 'partidos' está vacía.")
    else:
        print(f"✅ Total de partidos en la base de datos: {len(partidos)}")
        for p in partidos:
            print(f"{p.equipo_local} {p.goles_local} - {p.goles_visitante} {p.equipo_visitante} | Resultado: {p.resultado}")
    db.close()

if __name__ == "__main__":
    verificar_partidos()
