import { useState } from "react";
import type { Producto, SolicitudReabastecimiento, EstadoSolicitud } from "../types";
import { aprobarSolicitud, rechazarSolicitud } from "../api";

type Props = {
  solicitud: SolicitudReabastecimiento;
  producto: Producto | undefined;   // puede no encontrarse
  onResuelta: (mensaje: string) => void;
};

const CLASE_ESTADO: Record<EstadoSolicitud, string> = {
  PENDIENTE: "badge bajo",
  APROBADA: "badge ok",
  RECHAZADA: "badge agotado",
};

// La API envía fechas en formato ISO (2026-11-06T15:41:00Z); aquí las mostramos legibles
function formatearFecha(iso: string) {
  return new Date(iso).toLocaleString("es-CR", { dateStyle: "medium", timeStyle: "short" });
}

export function SolicitudFila({ solicitud, producto, onResuelta }: Props) {
  // Cada fila tiene su propio comentario y su propio estado de envío
  const [comentario, setComentario] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // ?. evita un error si producto es undefined; ?? da un valor por defecto
  const nombre = producto?.nombre ?? `Producto #${solicitud.producto_id}`;

  async function resolver(aprobar: boolean) {
    // Misma regla que el backend: rechazar exige explicar el motivo
    if (!aprobar && comentario.trim().length < 3) {
      setError("Para rechazar, explica el motivo (mínimo 3 caracteres).");
      return;
    }
    setEnviando(true);
    setError(null);
    try {
      if (aprobar) await aprobarSolicitud(solicitud.id, comentario);
      else await rechazarSolicitud(solicitud.id, comentario);
      onResuelta(`Solicitud #${solicitud.id} (${nombre}) ${aprobar ? "aprobada" : "rechazada"}.`);
    } catch (err) {
      setError((err as Error).message);   // ej.: 409 si otra persona ya la resolvió
    } finally {
      setEnviando(false);
    }
  }

  return (
    <article className="panel solicitud">
      <div className="solicitud-cabecera">
        <div>
          <h3>{nombre}</h3>
          <p className="secundario">
            Solicitud #{solicitud.id} · creada {formatearFecha(solicitud.creada_en)}
          </p>
        </div>
        <span className={CLASE_ESTADO[solicitud.estado]}>{solicitud.estado}</span>
      </div>

      <p>
        Pedir <strong>{solicitud.cantidad}</strong> unidades
        {producto && <> · stock actual {producto.stock} (mínimo {producto.minimo})</>}
      </p>

      {solicitud.estado === "PENDIENTE" ? (
        <>
          <input
            type="text"
            className="comentario"
            placeholder="Comentario (obligatorio para rechazar)"
            value={comentario}
            onChange={(e) => setComentario(e.target.value)}
          />
          {error && <p className="error">{error}</p>}
          <div className="acciones">
            <button className="peligro-btn" disabled={enviando} onClick={() => resolver(false)}>
              Rechazar
            </button>
            <button disabled={enviando} onClick={() => resolver(true)}>
              Aprobar
            </button>
          </div>
        </>
      ) : (
        <p className="secundario">
          {solicitud.comentario && <>“{solicitud.comentario}” · </>}
          Resuelta {solicitud.resuelta_en && formatearFecha(solicitud.resuelta_en)}
        </p>
      )}
    </article>
  );
}