import pytest
from app.services import calcular_estado, cantidad_a_pedir


# parametrize: ejecuta la misma prueba con varios casos (entrada, resultado esperado)
@pytest.mark.parametrize("stock, minimo, esperado", [
    (0, 10, "AGOTADO"),
    (5, 10, "STOCK BAJO"),
    (10, 10, "OK"),        # caso límite: justo en el mínimo
    (50, 10, "OK"),
])
def test_calcular_estado(stock, minimo, esperado):
    assert calcular_estado(stock, minimo) == esperado


def test_cantidad_a_pedir_bajo_minimo():
    assert cantidad_a_pedir(4, 8) == 12        # el ejemplo de tu mini-reto


def test_cantidad_a_pedir_agotado():
    assert cantidad_a_pedir(0, 10) == 20


def test_cantidad_a_pedir_en_el_minimo_es_cero():
    assert cantidad_a_pedir(10, 10) == 0       # caso límite


def test_cantidad_a_pedir_sobre_minimo_es_cero():
    assert cantidad_a_pedir(30, 10) == 0       # nunca devuelve negativos