from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, contains_eager

from app.database import get_db
from app.models import Producto, Familia
from app.schemas import ProductoCrear, ProductoRespuesta

app = FastAPI(title="StockFlow API")


def calcular_estado(stock: int, minimo: int) -> str:
    if stock == 0:
        return "AGOTADO"
    if stock < minimo:
        return "STOCK BAJO"
    return "OK"


# Convierte un objeto de la BD (modelo) en lo que devuelve la API (schema)
def a_respuesta(p: Producto) -> ProductoRespuesta:
    return ProductoRespuesta(
        id=p.id, codigo=p.codigo, nombre=p.nombre,
        familia=p.familia.nombre, subcategoria=p.subcategoria,
        stock=p.stock, minimo=p.minimo,
        estado=calcular_estado(p.stock, p.minimo),
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/products", response_model=list[ProductoRespuesta])
def listar_productos(familia: str | None = None, estado: str | None = None,
                     db: Session = Depends(get_db)):
    # JOIN con familias + contains_eager: trae producto y familia en UNA sola consulta
    consulta = (select(Producto)
                .join(Producto.familia)
                .options(contains_eager(Producto.familia))
                .order_by(Producto.id))
    if familia:
        consulta = consulta.where(Familia.nombre == familia.lower())

    resultado = [a_respuesta(p) for p in db.scalars(consulta).all()]

    if estado:
        resultado = [r for r in resultado if r.estado == estado.upper()]
    return resultado


@app.get("/products/{product_id}", response_model=ProductoRespuesta)
def obtener_producto(product_id: int, db: Session = Depends(get_db)):
    producto = db.get(Producto, product_id)   # busca por llave primaria
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return a_respuesta(producto)


@app.post("/products", response_model=ProductoRespuesta, status_code=201)
def crear_producto(datos: ProductoCrear, db: Session = Depends(get_db)):
    fam = db.scalar(select(Familia).where(Familia.nombre == datos.familia.lower()))
    if fam is None:
        raise HTTPException(status_code=422, detail=f"La familia '{datos.familia}' no existe")

    producto = Producto(codigo=datos.codigo, nombre=datos.nombre, familia=fam,
                        subcategoria=datos.subcategoria, stock=datos.stock,
                        minimo=datos.minimo)
    db.add(producto)
    db.commit()            # guarda en PostgreSQL
    db.refresh(producto)   # recarga el objeto con el id que generó la BD
    return a_respuesta(producto)

