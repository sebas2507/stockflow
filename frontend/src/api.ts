import type { Producto } from "./types";

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