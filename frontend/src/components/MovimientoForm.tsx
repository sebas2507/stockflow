import { useState } from "react";
import type { FormEvent } from "react";
import type { Producto, TipoMovimiento } from "../types";
import { registrarMovimiento } from "../api";

type Props = {
  producto: Producto;
  onCancelar: () => void;
  onRegistrado: (mensaje: string) => void;
};

export function MovimientoForm({ producto, onCancelar, onRegistrado }: Props) {
  // Estado local del formulario: solo le importa a este componente
  const [tipo, setTipo] = useState<TipoMovimiento>("SALIDA");
  const [cantidad, setCantidad] = useState("");     // texto: así se maneja un input vacío
  const [motivo, setMotivo] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function manejarEnvio(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();   // evita que el navegador recargue la página

    // Validación en el cliente: respuesta inmediata, sin ir al servidor
    const numero = Number(cantidad);
    if (!Number.isInteger(numero) || numero <= 0) {
      setError("La cantidad debe ser un número entero mayor que 0.");
      return;
    }

    setEnviando(true);
    setError(null);
    try {
      const resultado = await registrarMovimiento(producto.id, tipo, numero, motivo);

      let mensaje = `${tipo === "ENTRADA" ? "Entrada" : "Salida"} registrada. ` +
                    `Stock actual de ${producto.nombre}: ${resultado.stock_actual}.`;
      if (resultado.solicitud_generada) {
        mensaje += ` Se generó la solicitud #${resultado.solicitud_generada.id} ` +
                   `por ${resultado.solicitud_generada.cantidad} unidades.`;
      }
      onRegistrado(mensaje);   // avisa al padre: él cierra el formulario y recarga la lista
    } catch (err) {
      setError((err as Error).message);   // por ejemplo, el 409 de stock insuficiente
    } finally {
      setEnviando(false);
    }
  }

  return (
    <form className="panel" onSubmit={manejarEnvio}>
      <h2>Registrar movimiento</h2>
      <p className="secundario">
        {producto.nombre} · stock actual: {producto.stock} · mínimo: {producto.minimo}
      </p>

      <div className="campos">
        <label>
          Tipo
          <select value={tipo} onChange={(e) => setTipo(e.target.value as TipoMovimiento)}>
            <option value="SALIDA">Salida</option>
            <option value="ENTRADA">Entrada</option>
          </select>
        </label>

        <label>
          Cantidad
          <input type="number" min="1" value={cantidad}
                 onChange={(e) => setCantidad(e.target.value)} />
        </label>

        <label className="ancho">
          Motivo (opcional)
          <input type="text" value={motivo} placeholder="Ej: Pedido supermercado"
                 onChange={(e) => setMotivo(e.target.value)} />
        </label>
      </div>

      {error && <p className="error">{error}</p>}

      <div className="acciones">
        <button type="button" className="secundario-btn" onClick={onCancelar}>Cancelar</button>
        {/* Deshabilitado mientras se envía: evita registrar el movimiento dos veces */}
        <button type="submit" disabled={enviando}>
          {enviando ? "Guardando..." : "Registrar"}
        </button>
      </div>
    </form>
  );
}