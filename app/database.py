import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

load_dotenv()  # carga las variables de .env en el entorno

# URL de conexión: driver://usuario:contraseña@host:puerto/base
def construir_url(nombre_db: str) -> str:
    # Si no se define POSTGRES_HOST, usa localhost (desarrollo local y pruebas)
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    return (
        f"postgresql+psycopg://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
        f"@{host}:{port}/{nombre_db}"
    )

DATABASE_URL = construir_url(os.getenv("POSTGRES_DB"))

engine = create_engine(DATABASE_URL)        # administra las conexiones (pool)
SessionLocal = sessionmaker(bind=engine)    # "fábrica" de sesiones

class Base(DeclarativeBase):                # clase padre de todos los modelos
    pass

# Dependencia: abre una sesión por cada request y SIEMPRE la cierra.
def get_db():
    db = SessionLocal()
    try:
        yield db          # entrega la sesión al endpoint
    finally:
        db.close()        # se ejecuta aunque haya un error