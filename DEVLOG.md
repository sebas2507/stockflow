# StockFlow – Devlog

## Sesión 1 
- Instalé Python 3.14 (uso `py` por conflicto con el alias de la Microsoft Store).
- Creé el repositorio con Git y un entorno virtual (`.venv`) para aislar dependencias.
- Agregué `.gitignore` para no subir el entorno ni las credenciales.
- Analicé el inventario real de Chrio: 214 productos, 7 familias, problemas de calidad de datos 
- Ajusté el modelo: código de barras, familia y subcategoría. El Excel original no se sube al repositorio.
- Fase 2: API REST con FastAPI. Endpoints GET (lista, por id) y POST con validación Pydantic.
- Filtros con query parameters (familia, estado). El estado se calcula en lugar de guardarse, a diferencia de la columna manual del Excel.

## Sesión 2 
- PostgreSQL 17 en Docker con docker-compose y volumen persistente.
- Credenciales en .env y .env.example como plantilla.

## Sesion 3
- API conectada a PostgreSQL con SQLAlchemy 2.0 (ORM) y psycopg.
- Código separado en database, models, schemas, seed y main (separación de responsabilidades).
- Relación familias → productos con llave foránea. JOIN + contains_eager para evitar N+1.
- Seed idempotente. Los datos persisten al reiniciar la API.

## Sesion 4 
- Movimientos de stock (ENTRADA/SALIDA) como historial de auditoría. El stock no se edita directo.
- Solicitudes de reabastecimiento automáticas al quedar bajo el mínimo (cantidad = doble del mínimo − stock), sin duplicados.
- Flujo human-in-the-loop: PENDIENTE → APROBADA / RECHAZADA (rechazo con comentario obligatorio).
- Capa de servicios separada de los endpoints. Excepciones propias traducidas a 404/409 con exception handlers.
- Bloqueo de fila (SELECT ... FOR UPDATE) para evitar condiciones de carrera.

## Sesion 5 
- Pruebas unitarias de las reglas de negocio con parametrize y casos límite.
- Pruebas de integración de la API con TestClient y una base de datos de prueba aislada (dependency_overrides).
- Endpoint de generación masiva de solicitudes desarrollado con TDD (rojo → verde → refactor).

## Sesion 6 – Frontend 
- Proyecto React + TypeScript con Vite en /frontend.
- CORS en FastAPI restringido al origen del frontend.
- Tipos en TypeScript que reflejan el schema de la API.
- Lista de productos con useState/useEffect y estados de carga y error.

## Sesion 7 - componentes
- Filtros enviados como query parameters a la API. El estado de los filtros vive en App (lifting state up).
- Cleanup en useEffect para descartar respuestas viejas (condición de carrera).
- Estilos con badges de color + texto (accesibilidad).

## Sesion 8
- formulario para registrar movimientos (entrada/salida).
- Validación en el cliente (UX) + mensajes de error del backend (409, 422).
- Botón deshabilitado durante el envío (evita doble registro). Recarga de datos desde la API tras cada movimiento.

## Sesion 9
- bandeja de aprobación (human-in-the-loop) con aprobar/rechazar y comentario.
- Botón "Revisar inventario" que usa el endpoint batch.
- Refactor: pantallas en pages/, App solo con navegación por pestañas.
- Helper genérico postJson<T> para todas las peticiones POST (DRY).
- Promise.all + Map para unir solicitudes con productos.

## Sesion 10
- Dockerfile de la API .
- Dockerfile multi-stage del frontend .
- docker-compose con 3 servicios, red interna , healthcheck y depends_on.
- Configuración por variables de entorno (POSTGRES_HOST, VITE_API_URL).


### Problemas encontrados
- La terminal de Windows se "congelaba" al hacer clic sobre ella (modo selección), y eso pausaba la API. Se sale con Esc.