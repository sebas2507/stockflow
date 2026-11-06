import { useEffect, useState } from "react";
import type { Producto } from "./types";

const API_URL = "http://127.0.0.1:8000";

// Un componente es una función que devuelve lo que se muestra en pantalla (JSX)
function App() {
  // Estado: datos que cambian y que, al cambiar, actualizan la pantalla
  const [productos, setProductos] = useState<Producto[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Efecto: se ejecuta UNA vez cuando el componente aparece ([] = sin dependencias)
  useEffect(() => {
    fetch(`${API_URL}/products`)
      .then((res) => {
        if (!res.ok) throw new Error(`Error ${res.status}`);
        return res.json();
      })
      .then((data: Producto[]) => setProductos(data))
      .catch((err: Error) => setError(err.message))
      .finally(() => setCargando(false));
  }, []);

  // Estados de la pantalla: cargando, error o datos
  if (cargando) return <p>Cargando productos...</p>;
  if (error) return <p>No se pudo conectar con la API: {error}</p>;

  return (
    <main>
      <h1>StockFlow</h1>
      <p>{productos.length} productos</p>

      <table>
        <thead>
          <tr>
            <th>Producto</th>
            <th>Familia</th>
            <th>Stock</th>
            <th>Mínimo</th>
            <th>Estado</th>
          </tr>
        </thead>
        <tbody>
          {/* map convierte cada producto en una fila de la tabla */}
          {productos.map((p) => (
            <tr key={p.id}>
              <td>{p.nombre}</td>
              <td>{p.familia}</td>
              <td>{p.stock}</td>
              <td>{p.minimo}</td>
              <td>{p.estado}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}

export default App;
