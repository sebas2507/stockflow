import type { Producto } from "../types";

// Props: los datos que este componente recibe de su padre
type Props = {
  estado: Producto["estado"];   // el mismo tipo del campo estado: "OK" | "STOCK BAJO" | "AGOTADO"
};

// Record obliga a definir una clase para CADA estado posible.
// Si mañana el backend agrega un estado nuevo, TypeScript avisa aquí.
const CLASES: Record<Producto["estado"], string> = {
  "OK": "badge ok",
  "STOCK BAJO": "badge bajo",
  "AGOTADO": "badge agotado",
};

export function EstadoBadge({ estado }: Props) {
  return <span className={CLASES[estado]}>{estado}</span>;
}