# StockFlow – Devlog

## Sesión 1 
- Instalé Python 3.14 (uso `py` por conflicto con el alias de la Microsoft Store).
- Creé el repositorio con Git y un entorno virtual (`.venv`) para aislar dependencias.
- Agregué `.gitignore` para no subir el entorno ni las credenciales.
- Analicé el inventario real de Chrio: 214 productos, 7 familias, problemas de calidad de datos 
- Ajusté el modelo: código de barras, familia y subcategoría. El Excel original no se sube al repositorio.
- Fase 2: API REST con FastAPI. Endpoints GET (lista, por id) y POST con validación Pydantic.
- Filtros con query parameters (familia, estado). El estado se calcula en lugar de guardarse, a diferencia de la columna manual del Excel.