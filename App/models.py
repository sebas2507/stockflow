from sqlalchemy import String, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


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