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

export type TipoMovimiento = "ENTRADA" | "SALIDA";
export type EstadoSolicitud = "PENDIENTE" | "APROBADA" | "RECHAZADA";

export interface SolicitudReabastecimiento {
  id: number;
  producto_id: number;
  cantidad: number;
  estado: EstadoSolicitud;
  comentario: string | null;
  creada_en: string;          // las fechas llegan en JSON como texto (ISO 8601)
  resuelta_en: string | null;
}

// Lo que responde POST /products/{id}/movements (MovimientoResultado en schemas.py)
export interface MovimientoResultado {
  stock_actual: number;
  solicitud_generada: SolicitudReabastecimiento | null;
}