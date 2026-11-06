import { useEffect, useState } from "react";
import type { Producto } from "./types";
import { obtenerProductos } from "./api";
import { Filtros } from "./components/Filtros";
import { ProductTable } from "./components/ProductTable";

function App() {
  const [productos, setProductos] = useState<Producto[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Estado de los filtros: vive en App porque lo usan Filtros Y la consulta
  const [familia, setFamilia] = useState("");
  const [estado, setEstado] = useState("");

  // Se ejecuta al inicio Y cada vez que cambia familia o estado
  useEffect(() => {
    let ignorar = false;   // evita que una respuesta vieja pise a una nueva

    obtenerProductos(familia, estado)
      .then((data) => {
        if (!ignorar) {
          setProductos(data);
          setError(null);
        }
      })
      .catch((err: Error) => {
        if (!ignorar) setError(err.message);
      })
      .finally(() => {
        if (!ignorar) setCargando(false);
      });

    // Limpieza: React la ejecuta antes de repetir el efecto
    return () => {
      ignorar = true;
    };
  }, [familia, estado]);

  return (
    <main>
      <h1>StockFlow</h1>
      <p className="subtitulo">Inventario y reabastecimiento</p>

      <Filtros
        familia={familia}
        estado={estado}
        onFamiliaChange={setFamilia}
        onEstadoChange={setEstado}
      />

      {error && <p className="error">No se pudo conectar con la API: {error}</p>}
      {cargando ? <p>Cargando productos...</p> : <ProductTable productos={productos} />}
    </main>
  );
}

export default App;
