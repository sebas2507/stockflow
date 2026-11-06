from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="StockFlow API")

# este es el esquema  de entrada: lo que el cliente debe enviar para crear un producto.
# No incluye "id" porque lo genera el sistema, no el cliente.
class ProductoCrear(BaseModel):
    codigo: str | None = None          # opcional: hay productos sin código en el Excel
    nombre: str = Field(min_length=1)  # no puede venir vacío
    familia: str
    subcategoria: str
    stock: int = Field(ge=0)           # ge = "greater or equal": no se aceptan negativos
    minimo: int = Field(ge=0)

productos = [
    {"id": 1, "codigo": "7501206626610", "nombre": "Tape eléctrico negro", "familia": "ferreteria", "subcategoria": "Cintas", "stock": 20, "minimo": 10},
    {"id": 2, "codigo": "7501206661741", "nombre": "Regleta económica", "familia": "ferreteria", "subcategoria": "Electricidad", "stock": 7, "minimo": 10},
    {"id": 3, "codigo": "6925582176582", "nombre": "Cinta métrica 5m", "familia": "ferreteria", "subcategoria": "Herramienta", "stock": 9, "minimo": 10},
    {"id": 4, "codigo": "6928002128871", "nombre": "Jarra cervecera", "familia": "cristaleria", "subcategoria": "Vidrio", "stock": 24, "minimo": 10},
    {"id": 5, "codigo": "1711503448365", "nombre": "Plato melamina blanco", "familia": "cristaleria", "subcategoria": "Melamina", "stock": 0, "minimo": 10},
    {"id": 6, "codigo": "2589637411352", "nombre": "Arnés para gato", "familia": "mascotas", "subcategoria": "Accesorios", "stock": 40, "minimo": 90},
    {"id": 7, "codigo": "2589637410232", "nombre": "Juguete hamburguesa", "familia": "mascotas", "subcategoria": "Juguetes", "stock": 447, "minimo": 120},
    {"id": 8, "codigo": "850009206381", "nombre": "Cable tipo C de silicón", "familia": "accesorios", "subcategoria": "Cables", "stock": 2, "minimo": 25},
]

#Para saber si la API esta viva
@app.get("/health")
def health():
    return {"status": "ok"}

#Listar todos los productos
@app.get("/productos")
def listar_productos():
    return productos

# Devuelve un producto por su id. {product_id} es un "path parameter".
@app.get("/products/{product_id}")
def obtener_producto(product_id: int):
    for p in productos:
        if p["id"] == product_id:
            return p
    # Si no se encuentra, responde con el código 404 (Not Found).
    raise HTTPException(status_code=404, detail="Producto no encontrado")

# Crea un producto. status_code=201 significa "Created".
@app.post("/products", status_code=201)
def crear_producto(datos: ProductoCrear):
    nuevo_id = max(p["id"] for p in productos) + 1   # siguiente id disponible
    nuevo = {"id": nuevo_id, **datos.model_dump()}    # une el id con los datos recibidos
    productos.append(nuevo)
    return nuevo

