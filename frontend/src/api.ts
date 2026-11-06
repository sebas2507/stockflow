import type {
  Producto, TipoMovimiento, MovimientoResultado,
  SolicitudReabastecimiento, EstadoSolicitud,
} from "./types";

export const API_URL = "http://127.0.0.1:8000";

function mensajeDeError(data: unknown, status: number): string {
  if (data && typeof data === "object" && "detail" in data) {
    const detail = (data as { detail: unknown }).detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) return detail.map((d) => d.msg).join(", ");
  }
  return `Error ${status}`;
}

// Helper genérico: TODAS las peticiones POST pasan por aquí.
// <T> es el tipo de la respuesta; lo decide quien llama a la función.
async function postJson<T>(ruta: string, body?: unknown): Promise<T> {
  const res = await fetch(`${API_URL}${ruta}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => null);
    throw new Error(mensajeDeError(data, res.status));
  }
  return res.json();
}

// ---------- Productos ----------

export async function obtenerProductos(familia: string, estado: string): Promise<Producto[]> {
  const params = new URLSearchParams();
  if (familia) params.append("familia", familia);
  if (estado) params.append("estado", estado);
  const res = await fetch(`${API_URL}/products?${params}`);
  if (!res.ok) throw new Error(`Error ${res.status}`);
  return res.json();
}

export function registrarMovimiento(
  productoId: number, tipo: TipoMovimiento, cantidad: number, motivo: string,
) {
  return postJson<MovimientoResultado>(`/products/${productoId}/movements`, {
    tipo, cantidad, motivo: motivo || null,
  });
}

// ---------- Solicitudes de reabastecimiento ----------

export async function obtenerSolicitudes(estado: EstadoSolicitud): Promise<SolicitudReabastecimiento[]> {
  const res = await fetch(`${API_URL}/restock-requests?estado=${estado}`);
  if (!res.ok) throw new Error(`Error ${res.status}`);
  return res.json();
}

export function aprobarSolicitud(id: number, comentario: string) {
  return postJson<SolicitudReabastecimiento>(`/restock-requests/${id}/approve`, {
    comentario: comentario || null,
  });
}

export function rechazarSolicitud(id: number, comentario: string) {
  return postJson<SolicitudReabastecimiento>(`/restock-requests/${id}/reject`, { comentario });
}

export function generarSolicitudes() {
  return postJson<SolicitudReabastecimiento[]>("/restock-requests/generate");
}

