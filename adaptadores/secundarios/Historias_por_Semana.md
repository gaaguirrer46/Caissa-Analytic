# Historias por Semana — Adaptadores Secundarios (Persistencia, Auth, PGN, Motor, Reportes, APIs)

> Historias de usuario del lado **driven** (salida), organizadas por semana según el `Calendario_Scrumban.md` de esta carpeta.
> **Formato:** `H-S-XX | Historia | Prioridad | Criterios de aceptación`.
> *Nota: la base de datos (esquema, vistas, seed) tiene su propio calendario urgente de 2 semanas en `persistencia/`.*

---

## Semana 1 · Fundación de datos y auth

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-S-01 | Como desarrollador, quiero **configurar SQLAlchemy** (SQLite dev / PostgreSQL prod) y **Alembic** para gestionar el esquema. | Alta | Conexión desde configuración; `alembic upgrade head` funciona. |
| H-S-02 | Como desarrollador, quiero una **fábrica de sesiones** segura para usar en los repositorios. | Alta | Sesiones con scope por petición; cierre correcto de conexiones. |
| H-S-03 | Como desarrollador, quiero **elegir e instalar** las librerías de autenticación (bcrypt/argon2 + JWT). | Media | Dependencias declaradas; prototipo hashea/verifica. |

## Semana 2 · Repos de usuarios y atletas

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-S-04 | Como desarrollador, quiero implementar **`RepositorioUsuarios`** (CRUD + búsquedas). | Alta | Guardar, buscar por correo/id, listar, existe — contra BD real. |
| H-S-05 | Como desarrollador, quiero implementar **`RepositorioAtletas`** (expediente + ratings + historial). | Alta | CRUD; ratings vinculados; historial por año/torneo persistido. |
| H-S-06 | Como desarrollador, quiero implementar **`RepositorioCategorias`** y la **migración inicial**. | Alta | Categorías predefinidas (RF-02.5) y personalizadas; migración aplicable desde cero. |

## Semana 3 · Repos de objetivos y entrenamientos

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-S-07 | Como desarrollador, quiero implementar **`RepositorioObjetivos`** (CRUD + filtros). | Alta | Crear/actualizar; listar por atleta y estado. |
| H-S-08 | Como desarrollador, quiero implementar **`ProveedorDatosAvance`** (consulta cruzada real: horas, rating, torneos). | Alta | Agrega datos de entrenamientos y partidas sin acoplar módulos. |
| H-S-09 | Como desarrollador, quiero implementar **`RepositorioEntrenamientos`** (planes, sesiones, ejecuciones). | Alta | Plan por semana/año; sesiones con estados; historial conservado. |
| H-S-10 | Como desarrollador, quiero implementar **`RepositorioAsistencia`** (registro + porcentaje). | Alta | Registrar y listar por sesión/atleta; % calculable. |

## Semana 4 · Repos restantes (completitud)

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-S-11 | Como desarrollador, quiero implementar **`RepositorioPartidas`** y **`RepositorioAnalisisTecnico`**. | Alta | Partidas con análisis vinculado; listados por atleta/torneo/periodo. |
| H-S-12 | Como desarrollador, quiero implementar **`RepositorioAperturas`** y **`RepositorioEvaluaciones`**. | Alta | Repertorio por atleta/color; evaluaciones con calificaciones 1–10. |
| H-S-13 | Como desarrollador, quiero implementar **`RepositorioIndicadores`**, **`RepositorioPatrones`** y **`RepositorioAuditoria`**. | Alta | Auditoría **inmutable** (sin update/delete, RF-12); históricos no modificables. |

## Semana 5 · Autenticación completa

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-S-14 | Como usuario, quiero que mi contraseña se guarde **hasheada** con bcrypt/argon2. | Alta | `hashear`/`verificar` correctos; nunca texto plano. |
| H-S-15 | Como usuario, quiero recibir y validar un **JWT** con expiración. | Alta | Token válido aceptado; inválido/expirado rechazado. |
| H-S-16 | Como sistema, quiero resolver **permisos por rol** (RBAC) integrando `PermisosPorRol`. | Alta | Matriz del dominio aplicada en la autenticación de peticiones. |

## Semana 6 · Parser PGN

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-S-17 | Como entrenador, quiero **importar una partida desde PGN** con datos estructurados. | Alta | PGN válido → `Partida` del dominio (evento, fecha, jugadores, ratings, resultado, ECO). |
| H-S-18 | Como operador, quiero **carga masiva de PGN** con manejo de errores por archivo. | Media | Lote procesa válidos y reporta inválidos sin detenerse (RF-05.2). |

## Semana 7 · Motor de ajedrez

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-S-19 | Como desarrollador, quiero integrar **Stockfish** vía `ProveedorEvaluacionMotor`. | Alta | Evaluación numérica de posiciones; arranque/cierre del motor sin fugas. |
| H-S-20 | Como sistema, quiero **calcular accuracy, ACPL, blunders, errores, imprecisiones y brilliant** desde un PGN. | Alta | Métricas de RF-05.5 consistentes con umbrales conocidos. |

## Semana 8 · Reportes PDF

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-S-21 | Como entrenador, quiero **generar PDFs** individuales (perfil, rating, partidas, torneos, aperturas, objetivos). | Alta | Cada plantilla genera PDF válido (RF-11.5). |
| H-S-22 | Como entrenador, quiero el **Informe Integral del Atleta** (8 secciones) y reportes grupal/institucional en PDF. | Alta | 8 secciones en orden estricto (RF-11.10); grupal e institucional generan archivo (RF-11.6/11.7). |

## Semana 9 · Reportes Excel

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-S-23 | Como entrenador, quiero **exportar a Excel** tablas (partidas, entrenamientos, objetivos, aperturas, ranking, asistencia, informe integral). | Alta | `.xlsx` válido con encabezados y datos; formato semáforo en celdas evaluadas. |

## Semana 10 · APIs externas

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-S-24 | Como entrenador, quiero **sincronizar ratings y partidas desde Chess.com**. | Media | Cliente normaliza datos → estructuras del dominio; actualización de ratings post-publicación (RF-13.6); errores de red con reintentos. |
| H-S-25 | Como entrenador, quiero **sincronizar ratings y partidas desde Lichess** y soportar **ChessBase** como fuente de partidas (RF-05.2). | Media | Idem; sincronización manual y programada (RNF-05.2). |

## Semana 11 · Optimización y Postgres

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-S-26 | Como desarrollador, quiero **optimizar consultas** (índices, evitar N+1). | Alta | Dashboards < 3 s con 40 atletas (RNF-01.4). |
| H-S-27 | Como operador, quiero migrar a **PostgreSQL** en producción con Alembic. | Alta | `alembic upgrade head` en Postgres limpio; rollback probado. |
| H-S-28 | Como operador, quiero **respaldos y restauración** de la BD. | Alta | Respaldo verificable; restauración probada (RNF-02.3). |

## Semana 12 · Integración final

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-S-29 | Como equipo, quiero **pruebas de integración** de todos los puertos contra recursos reales. | Alta | 100 % de puertos probados. |
| H-S-30 | Como equipo, quiero un **seed** de datos realistas y reproducible. | Media | Seed documentado y repetible. |
| H-S-31 | Como equipo, quiero **documentación** de cada adaptador y métricas scrumban. | Media | Docs por adaptador; retro con métricas. |
