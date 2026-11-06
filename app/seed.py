from sqlalchemy import select
from app.database import Base, engine, SessionLocal
from app.models import Familia, Producto

FAMILIAS = ["ferreteria", "cristaleria", "mascotas", "accesorios"]

# (codigo, nombre, familia, subcategoria, stock, minimo)
PRODUCTOS = [
    ("7501206626610", "Tape eléctrico negro", "ferreteria", "Cintas", 20, 10),
    ("7501206661741", "Regleta económica", "ferreteria", "Electricidad", 7, 10),
    ("6925582176582", "Cinta métrica 5m", "ferreteria", "Herramienta", 9, 10),
    ("6928002128871", "Jarra cervecera", "cristaleria", "Vidrio", 24, 10),
    ("1711503448365", "Plato melamina blanco", "cristaleria", "Melamina", 0, 10),
    ("2589637411352", "Arnés para gato", "mascotas", "Accesorios", 40, 90),
    ("2589637410232", "Juguete hamburguesa", "mascotas", "Juguetes", 447, 120),
    ("850009206381", "Cable tipo C de silicón", "accesorios", "Cables", 2, 25),
]


def main():
    Base.metadata.create_all(engine)   # crea las tablas que no existan

    with SessionLocal() as db:
        # Idempotente: si ya hay datos, no inserta de nuevo
        if db.scalar(select(Producto)) is not None:
            print("La base ya tiene datos; no se insertó nada.")
            return

        familias = {nombre: Familia(nombre=nombre) for nombre in FAMILIAS}
        db.add_all(familias.values())

        for codigo, nombre, fam, sub, stock, minimo in PRODUCTOS:
            db.add(Producto(codigo=codigo, nombre=nombre, familia=familias[fam],
                            subcategoria=sub, stock=stock, minimo=minimo))

        db.commit()   # guarda todo en una sola transacción
        print(f"Se insertaron {len(PRODUCTOS)} productos.")


if __name__ == "__main__":
    main()