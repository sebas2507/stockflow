from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from app.models import TipoMovimiento, EstadoSolicitud


# Lo que entra: datos para crear un producto
class ProductoCrear(BaseModel):
    codigo: str | None = None
    nombre: str = Field(min_length=1)
    familia: str
    subcategoria: str
    stock: int = Field(ge=0)
    minimo: int = Field(ge=0)


# Lo que sale: lo que la API devuelve
class ProductoRespuesta(BaseModel):
    id: int
    codigo: str | None
    nombre: str
    familia: str          # el nombre, no el id interno
    subcategoria: str
    stock: int
    minimo: int
    estado: str           # calculado, no se guarda

class MovimientoCrear(BaseModel):
    tipo: TipoMovimiento               # solo acepta "ENTRADA" o "SALIDA"
    cantidad: int = Field(gt=0)        # gt = "greater than": mayor que 0
    motivo: str | None = None


class MovimientoRespuesta(BaseModel):
    # from_attributes: permite crear el schema leyendo los atributos
    # de un objeto SQLAlchemy directamente
    model_config = ConfigDict(from_attributes=True)

    id: int
    producto_id: int
    tipo: TipoMovimiento
    cantidad: int
    motivo: str | None
    creado_en: datetime


class SolicitudRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    producto_id: int
    cantidad: int
    estado: EstadoSolicitud
    comentario: str | None
    creada_en: datetime
    resuelta_en: datetime | None


# Respuesta al registrar un movimiento: qué pasó y si se generó una solicitud
class MovimientoResultado(BaseModel):
    movimiento: MovimientoRespuesta
    stock_actual: int
    solicitud_generada: SolicitudRespuesta | None


class Aprobacion(BaseModel):
    comentario: str | None = None


class Rechazo(BaseModel):
    comentario: str = Field(min_length=3)   # rechazar exige explicar el motivo