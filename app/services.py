from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (Producto, MovimientoStock, SolicitudReabastecimiento,
                        TipoMovimiento, EstadoSolicitud)


# Errores propios del negocio. No dependen de FastAPI ni de HTTP.
class NoEncontradoError(Exception):
    pass


class ConflictoError(Exception):
    pass


def calcular_estado(stock: int, minimo: int) -> str:
    if stock == 0:
        return "AGOTADO"
    if stock < minimo:
        return "STOCK BAJO"
    return "OK"


# La función de tu mini-reto: pedir hasta llegar al doble del mínimo
def cantidad_a_pedir(stock: int, minimo: int) -> int:
    if stock >= minimo:
        return 0
    return minimo * 2 - stock


def registrar_movimiento(db: Session, producto_id: int, tipo: TipoMovimiento,
                         cantidad: int, motivo: str | None):
    # with_for_update: bloquea la fila del producto hasta el commit.
    # Si llegan dos salidas al mismo tiempo, la segunda espera a la primera.
    producto = db.get(Producto, producto_id, with_for_update=True)
    if producto is None:
        raise NoEncontradoError("Producto no encontrado")

    if tipo == TipoMovimiento.SALIDA:
        if cantidad > producto.stock:
            raise ConflictoError(f"Stock insuficiente: hay {producto.stock}, se pidieron {cantidad}")
        producto.stock -= cantidad
    else:
        producto.stock += cantidad

    movimiento = MovimientoStock(producto_id=producto.id, tipo=tipo,
                                 cantidad=cantidad, motivo=motivo)
    db.add(movimiento)
    solicitud = _generar_solicitud_si_hace_falta(db, producto)

    db.commit()   # stock + movimiento + solicitud: todo o nada
    db.refresh(movimiento)
    if solicitud:
        db.refresh(solicitud)
    return producto, movimiento, solicitud


# El guion bajo inicial indica que es una función "interna" del módulo
def _generar_solicitud_si_hace_falta(db: Session, producto: Producto):
    pedir = cantidad_a_pedir(producto.stock, producto.minimo)
    if pedir == 0:
        return None

    # Evita duplicados: ¿ya hay una solicitud pendiente para este producto?
    pendiente = db.scalar(
        select(SolicitudReabastecimiento).where(
            SolicitudReabastecimiento.producto_id == producto.id,
            SolicitudReabastecimiento.estado == EstadoSolicitud.PENDIENTE,
        )
    )
    if pendiente:
        return None

    solicitud = SolicitudReabastecimiento(producto_id=producto.id, cantidad=pedir)
    db.add(solicitud)
    return solicitud


def resolver_solicitud(db: Session, solicitud_id: int, aprobar: bool,
                       comentario: str | None):
    solicitud = db.get(SolicitudReabastecimiento, solicitud_id, with_for_update=True)
    if solicitud is None:
        raise NoEncontradoError("Solicitud no encontrada")

    # Máquina de estados: solo PENDIENTE puede cambiar
    if solicitud.estado != EstadoSolicitud.PENDIENTE:
        raise ConflictoError(f"La solicitud ya fue {solicitud.estado.value}")

    solicitud.estado = EstadoSolicitud.APROBADA if aprobar else EstadoSolicitud.RECHAZADA
    solicitud.comentario = comentario
    solicitud.resuelta_en = datetime.now(timezone.utc)
    db.commit()
    db.refresh(solicitud)
    return solicitud

def generar_solicitudes_pendientes(db: Session) -> list[SolicitudReabastecimiento]:
    productos = db.scalars(select(Producto)).all()   # 1. todos los productos

    creadas = []
    for producto in productos:                        # 2. revisa cada uno
        solicitud = _generar_solicitud_si_hace_falta(db, producto)
        if solicitud is not None:                     # 3. solo las nuevas
            creadas.append(solicitud)

    db.commit()                                       # 4. una sola transacción
    for solicitud in creadas:
        db.refresh(solicitud)                         # carga id y creada_en
    return creadas                                    # 5.