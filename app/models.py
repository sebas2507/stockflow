from sqlalchemy import String, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum
from datetime import datetime
from sqlalchemy import DateTime, func


class Familia(Base):
    __tablename__ = "familias"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(50), unique=True)

    # Relación: desde una familia se puede acceder a sus productos
    productos: Mapped[list["Producto"]] = relationship(back_populates="familia")


class Producto(Base):
    __tablename__ = "productos"
    __table_args__ = (
        CheckConstraint("stock >= 0", name="ck_stock_no_negativo"),
        CheckConstraint("minimo >= 0", name="ck_minimo_no_negativo"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str | None] = mapped_column(String(20))   # opcional -> permite NULL
    nombre: Mapped[str] = mapped_column(String(100))         # obligatorio -> NOT NULL
    subcategoria: Mapped[str] = mapped_column(String(50))
    stock: Mapped[int]
    minimo: Mapped[int]
    familia_id: Mapped[int] = mapped_column(ForeignKey("familias.id"))

    # Relación: producto.familia devuelve el objeto Familia completo
    familia: Mapped["Familia"] = relationship(back_populates="productos")

# Enum: un conjunto cerrado de valores permitidos.
# Hereda de str para que se convierta a JSON como texto ("ENTRADA").
class TipoMovimiento(str, enum.Enum):
    ENTRADA = "ENTRADA"
    SALIDA = "SALIDA"


class EstadoSolicitud(str, enum.Enum):
    PENDIENTE = "PENDIENTE"
    APROBADA = "APROBADA"
    RECHAZADA = "RECHAZADA"


# Historial de cada cambio de stock (auditoría)
class MovimientoStock(Base):
    __tablename__ = "movimientos_stock"
    __table_args__ = (CheckConstraint("cantidad > 0", name="ck_mov_cantidad_positiva"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"))
    tipo: Mapped[TipoMovimiento]
    cantidad: Mapped[int]
    motivo: Mapped[str | None] = mapped_column(String(200))
    # server_default: la fecha la pone PostgreSQL al insertar la fila
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SolicitudReabastecimiento(Base):
    __tablename__ = "solicitudes_reabastecimiento"

    id: Mapped[int] = mapped_column(primary_key=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"))
    cantidad: Mapped[int]
    estado: Mapped[EstadoSolicitud] = mapped_column(default=EstadoSolicitud.PENDIENTE)
    comentario: Mapped[str | None] = mapped_column(String(300))
    creada_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    resuelta_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))