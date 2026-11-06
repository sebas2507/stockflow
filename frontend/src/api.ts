import type { Producto, TipoMovimiento, MovimientoResultado } from "./types";

export const API_URL = "http://127.0.0.1:8000";

// async/await: otra forma de escribir promesas, más fácil de leer que .then()
export async function obtenerProductos(familia: string, estado: string): Promise<Producto[]> {
  // URLSearchParams arma el query string: ?familia=mascotas&estado=AGOTADO
  const params = new URLSearchParams();
  if (familia) params.append("familia", familia);
  if (estado) params.append("estado", estado);

  const res = await fetch(`${API_URL}/products?${params}`);
  if (!res.ok) throw new Error(`Error ${res.status}`);
  return res.json();
}

// Convierte el error de FastAPI en un mensaje legible.
// 409/404 traen detail como texto; 422 trae una lista de errores de validación.
function mensajeDeError(data: unknown, status: number): string {
  if (data && typeof data === "object" && "detail" in data) {
    const detail = (data as { detail: unknown }).detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) return detail.map((d) => d.msg).join(", ");
  }
  return `Error ${status}`;
}

export async function registrarMovimiento(
  productoId: number,
  tipo: TipoMovimiento,
  cantidad: number,
  motivo: string,
): Promise<MovimientoResultado> {
  const res = await fetch(`${API_URL}/products/${productoId}/movements`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },   // le dice a la API que enviamos JSON
    body: JSON.stringify({ tipo, cantidad, motivo: motivo || null }),
  });

  if (!res.ok) {
    const data = await res.json().catch(() => null);  // si el error no trae JSON, no se cae
    throw new Error(mensajeDeError(data, res.status));
  }
  return res.json();
}

