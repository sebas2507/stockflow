// Describe la forma de un producto, igual que ProductoRespuesta en schemas.py.
// Si el backend cambia, TypeScript marca en rojo cada lugar del frontend que se rompe.
export interface Producto {
  id: number;
  codigo: string | null;   // en Python era: str | None
  nombre: string;
  familia: string;
  subcategoria: string;
  stock: number;
  minimo: number;
  estado: "OK" | "STOCK BAJO" | "AGOTADO";   // solo acepta estos tres valores
}