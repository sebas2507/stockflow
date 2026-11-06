import type { Producto } from "../types";
import { EstadoBadge } from "./EstadoBadge";

type Props = {
  productos: Producto[];
  onMovimiento: (producto: Producto) => void;
};

export function ProductTable({ productos, onMovimiento }: Props) {
  if (productos.length === 0) {
    return <p className="vacio">No hay productos con esos filtros.</p>;
  }

  return (
    <table>
      <thead>
        <tr>
          <th>Producto</th>
          <th>Familia</th>
          <th className="numero">Stock</th>
          <th className="numero">Mínimo</th>
          <th>Estado</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {productos.map((p) => (
          <tr key={p.id}>
            <td>
              <strong>{p.nombre}</strong>
              <div className="secundario">{p.subcategoria}</div>
            </td>
            <td>{p.familia}</td>
            <td className="numero">{p.stock}</td>
            <td className="numero">{p.minimo}</td>
            <td><EstadoBadge estado={p.estado} /></td>
            <td>
                    <button className="secundario-btn" onClick={() => onMovimiento(p)}>
                        Movimiento
                    </button>
                </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}