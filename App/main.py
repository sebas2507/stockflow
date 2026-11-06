from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session, contains_eager

from app.database import get_db
from app.models import (Producto, Familia, MovimientoStock,
                        SolicitudReabastecimiento, EstadoSolicitud)
from app.schemas import (ProductoCrear, ProductoRespuesta, MovimientoCrear,
                         MovimientoRespuesta, MovimientoResultado,
                         SolicitudRespuesta, Aprobacion, Rechazo)
from app.services import (calcular_estado, registrar_movimiento, resolver_solicitud,
                          generar_solicitudes_pendientes,
                          NoEncontradoError, ConflictoError)

app = FastAPI(title="StockFlow API")

# Traducen los errores del negocio a códigos HTTP, en un solo lugar
@app.exception_handler(NoEncontradoError)
def manejar_no_encontrado(request: Request, exc: NoEncontradoError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(ConflictoError)
def manejar_conflicto(request: Request, exc: ConflictoError):
    return JSONResponse(status_code=409, content={"detail": str(exc)})

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

    # ---------- Movimientos ----------

@app.post("/products/{product_id}/movements", response_model=MovimientoResultado,
          status_code=201)
def crear_movimiento(product_id: int, datos: MovimientoCrear,
                     db: Session = Depends(get_db)):
    producto, movimiento, solicitud = registrar_movimiento(
        db, product_id, datos.tipo, datos.cantidad, datos.motivo)
    return MovimientoResultado(
        movimiento=MovimientoRespuesta.model_validate(movimiento),
        stock_actual=producto.stock,
        solicitud_generada=SolicitudRespuesta.model_validate(solicitud) if solicitud else None,
    )


@app.get("/products/{product_id}/movements", response_model=list[MovimientoRespuesta])
def listar_movimientos(product_id: int, db: Session = Depends(get_db)):
    if db.get(Producto, product_id) is None:
        raise NoEncontradoError("Producto no encontrado")
    consulta = (select(MovimientoStock)
                .where(MovimientoStock.producto_id == product_id)
                .order_by(MovimientoStock.creado_en.desc()))   # los más recientes primero
    return db.scalars(consulta).all()


# ---------- Solicitudes de reabastecimiento ----------

@app.get("/restock-requests", response_model=list[SolicitudRespuesta])
def listar_solicitudes(estado: EstadoSolicitud | None = None,
                       db: Session = Depends(get_db)):
    consulta = select(SolicitudReabastecimiento).order_by(
        SolicitudReabastecimiento.creada_en.desc())
    if estado:
        consulta = consulta.where(SolicitudReabastecimiento.estado == estado)
    return db.scalars(consulta).all()

# Revisa todo el inventario y crea las solicitudes que falten.
# Pensado para ejecutarse automáticamente (por ejemplo, cada mañana).
@app.post("/restock-requests/generate", response_model=list[SolicitudRespuesta])
def generar_solicitudes(db: Session = Depends(get_db)):
    return generar_solicitudes_pendientes(db)


@app.post("/restock-requests/{solicitud_id}/approve", response_model=SolicitudRespuesta)
def aprobar_solicitud(solicitud_id: int, datos: Aprobacion | None = None,
                      db: Session = Depends(get_db)):
    comentario = datos.comentario if datos else None
    return resolver_solicitud(db, solicitud_id, aprobar=True, comentario=comentario)


@app.post("/restock-requests/{solicitud_id}/reject", response_model=SolicitudRespuesta)
def rechazar_solicitud(solicitud_id: int, datos: Rechazo,
                       db: Session = Depends(get_db)):
    return resolver_solicitud(db, solicitud_id, aprobar=False, comentario=datos.comentario)

