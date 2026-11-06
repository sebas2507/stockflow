import { useState } from "react";
import { Inventario } from "./pages/Inventario";
import { Solicitudes } from "./pages/Solicitudes";

type Vista = "inventario" | "solicitudes";

function App() {
  const [vista, setVista] = useState<Vista>("inventario");

  return (
    <main>
      <header className="encabezado">
        <div>
          <h1>StockFlow</h1>
          <p className="subtitulo">Inventario y reabastecimiento</p>
        </div>
        <nav className="pestanas">
          <button
            className={vista === "inventario" ? "activa" : ""}
            onClick={() => setVista("inventario")}
          >
            Inventario
          </button>
          <button
            className={vista === "solicitudes" ? "activa" : ""}
            onClick={() => setVista("solicitudes")}
          >
            Solicitudes
          </button>
        </nav>
      </header>

      {/* Renderizado condicional: solo existe la pantalla activa */}
      {vista === "inventario" ? <Inventario /> : <Solicitudes />}
    </main>
  );
}

export default App;
