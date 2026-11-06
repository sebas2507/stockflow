import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db, construir_url
from app.main import app
from app.models import Familia, Producto

engine_test = create_engine(construir_url("stockflow_test"))
SessionTest = sessionmaker(bind=engine_test)


# Fixture: prepara una base de datos LIMPIA para cada prueba
@pytest.fixture
def db():
    Base.metadata.drop_all(engine_test)     # borra todas las tablas
    Base.metadata.create_all(engine_test)   # las crea de nuevo, vacías

    session = SessionTest()
    ferreteria = Familia(nombre="ferreteria")
    session.add_all([
        # id 1: arriba del mínimo
        Producto(codigo="111", nombre="Tape", familia=ferreteria,
                 subcategoria="Cintas", stock=20, minimo=10),
        # id 2: ya está bajo el mínimo
        Producto(codigo="222", nombre="Regleta", familia=ferreteria,
                 subcategoria="Electricidad", stock=7, minimo=10),
    ])
    session.commit()

    yield session       # aquí se ejecuta la prueba
    session.close()     # limpieza al terminar


# Fixture: un "navegador falso" que envía peticiones a la API
@pytest.fixture
def client(db):
    def get_db_test():
        yield db

    # Reemplaza la dependencia real por la de prueba
    app.dependency_overrides[get_db] = get_db_test
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()