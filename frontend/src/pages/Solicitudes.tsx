import { useEffect, useState } from "react";
import type { Producto, SolicitudReabastecimiento, EstadoSolicitud } from "../types";
import { obtenerProductos, obtenerSolicitudes, generarSolicitudes } from "../api";
import { SolicitudFila } from "../components/SolicitudFila";

export function Solicitudes() {
  const [solicitudes, setSolicitudes] = useState<SolicitudReabastecimiento[]>([]);
  // Map: búsqueda rápida de un producto por su id
  const [productos, setProductos] = useState<Map<number, Producto>>(new Map());
  const [filtro, setFiltro] = useState<EstadoSolicitud>("PENDIENTE");
  const [cargando, setCargando] = useState(true);
  const [generando, setGenerando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [recargar, setRecargar] = useState(0);

  useEffect(() => {
    let ignorar = false;

    // Promise.all: las dos peticiones viajan EN PARALELO
    Promise.all([obtenerSolicitudes(filtro), obtenerProductos("", "")])
      .then(([listaSolicitudes, listaProductos]) => {
        if (ignorar) return;
        setSolicitudes(listaSolicitudes);
        setProductos(new Map(listaProductos.map((p) => [p.id, p])));
        setError(null);
      })
      .catch((err: Error) => {
        if (!ignorar) setError(err.message);
      })
      .finally(() => {
        if (!ignorar) setCargando(false);
      });

    return () => {
      ignorar = true;
    };
  }, [filtro, recargar]);

  function actualizar(texto: string) {
    setMensaje(texto);
    setRecargar((n) => n + 1);
  }

  // Llama al endpoint batch que hiciste con TDD
  async function revisarInventario() {
    setGenerando(true);
    setError(null);
    try {
      const creadas = await generarSolicitudes();
      actualizar(
        creadas.length === 0
          ? "Inventario revisado: no hacía falta crear solicitudes nuevas."
          : `Inventario revisado: se crearon ${creadas.length} solicitudes nuevas.`,
      );
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setGenerando(false);
    }
  }

  return (
    <>
      <div className="barra">
        <label>
          Estado
          <select value={filtro} onChange={(e) => setFiltro(e.target.value as EstadoSolicitud)}>
            <option value="PENDIENTE">Pendientes</option>
            <option value="APROBADA">Aprobadas</option>
            <option value="RECHAZADA">Rechazadas</option>
          </select>
        </label>
        <button onClick={revisarInventario} disabled={generando}>
          {generando ? "Revisando..." : "Revisar inventario"}
        </button>
      </div>

      {mensaje && <p className="exito">{mensaje}</p>}
      {error && <p className="error">{error}</p>}

      {cargando ? (
        <p>Cargando solicitudes...</p>
      ) : solicitudes.length === 0 ? (
        <p className="vacio">No hay solicitudes {filtro.toLowerCase()}s.</p>
      ) : (
        <div className="lista">
          {solicitudes.map((s) => (
            <SolicitudFila
              key={s.id}
              solicitud={s}
              producto={productos.get(s.producto_id)}
              onResuelta={actualizar}
            />
          ))}
        </div>
      )}
    </>
  );
}