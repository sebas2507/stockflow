const FAMILIAS = ["ferreteria", "cristaleria", "mascotas", "accesorios"];
const ESTADOS = ["OK", "STOCK BAJO", "AGOTADO"];

type Props = {
  familia: string;
  estado: string;
  // Funciones que el padre (App) le pasa para enterarse de los cambios
  onFamiliaChange: (valor: string) => void;
  onEstadoChange: (valor: string) => void;
};

export function Filtros({ familia, estado, onFamiliaChange, onEstadoChange }: Props) {
  return (
    <div className="filtros">
      <label>
        Familia
        {/* Componente controlado: el valor viene del estado de React */}
        <select value={familia} onChange={(e) => onFamiliaChange(e.target.value)}>
          <option value="">Todas</option>
          {FAMILIAS.map((f) => (
            <option key={f} value={f}>{f}</option>
          ))}
        </select>
      </label>

      <label>
        Estado
        <select value={estado} onChange={(e) => onEstadoChange(e.target.value)}>
          <option value="">Todos</option>
          {ESTADOS.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </label>
    </div>
  );
}