from pydantic import BaseModel, Field


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