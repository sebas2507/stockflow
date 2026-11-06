import { useEffect, useState } from "react";
import type { Producto } from "./types";
import { obtenerProductos } from "./api";
import { Filtros } from "./components/Filtros";
import { ProductTable } from "./components/ProductTable";
import { MovimientoForm } from "./components/MovimientoForm";

function App() {
  const [productos, setProductos] = useState<Producto[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Estado de los filtros: vive en App porque lo usan Filtros Y la consulta
  const [familia, setFamilia] = useState("");
  const [estado, setEstado] = useState("");
  const [seleccionado, setSeleccionado] = useState<Producto | null>(null);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [recargar, setRecargar] = useState(0);   // contador: al cambiar, vuelve a consultar

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
  }, [familia, estado, recargar]);

  function manejarRegistrado(texto: string) {
  setMensaje(texto);
  setSeleccionado(null);          // cierra el formulario
  setRecargar((n) => n + 1);      // vuelve a pedir los productos a la API
}

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

            {mensaje && <p className="exito">{mensaje}</p>}
      {error && <p className="error">No se pudo conectar con la API: {error}</p>}

      {seleccionado && (
        <MovimientoForm
          key={seleccionado.id}
          producto={seleccionado}
          onCancelar={() => setSeleccionado(null)}
          onRegistrado={manejarRegistrado}
        />
      )}

      {cargando ? (
        <p>Cargando productos...</p>
      ) : (
        <ProductTable
          productos={productos}
          onMovimiento={(p) => {
            setSeleccionado(p);
            setMensaje(null);
          }}
        />
      )}
    </main>
  );
}

export default App;
