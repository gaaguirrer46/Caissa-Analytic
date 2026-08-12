# Calendario Scrumban — Adaptadores Secundarios (Driven / Salida)

> **Base del hexágono — lado secundario (driven).** Contiene la salida del sistema: **persistencia (SQLite/PostgreSQL + SQLAlchemy + Alembic)**, **autenticación (JWT/OAuth/bcrypt)**, **parser PGN**, **motor de ajedrez (Stockfish)**, **generación de reportes (PDF/Excel)** y **APIs externas (Chess.com/Lichess)**.
> Estos adaptadores **implementan los puertos (interfaces `ABC`) de `dominio/`**. El dominio define el *qué*; estos definen el *cómo* tecnológico.

---

## 1. ¿Qué es Scrumban y cómo lo aplicamos aquí?

Combinamos **Scrum** (iteraciones semanales con objetivo y entregable definido) con **Kanban** (flujo continuo, límites de trabajo en progreso y sistema *pull*).

| Práctica | Cómo se aplica |
|---|---|
| **Sprint** | Cada **semana** es una iteración con un entregable verificable (tabla del §5). |
| **Tablero Kanban** | Columnas `Backlog → En Progreso → Revisión/QA → Hecho` con límites WIP (§2). |
| **Pull** | Solo se inicia una nueva historia cuando hay capacidad en `En Progreso`. |
| **Planificación** | El lunes se fija el objetivo de la semana extrayendo del backlog priorizado. |
| **Demo + Retro** | El viernes se demuestra el entregable y se ajusta el proceso. |

---

## 2. Tablero y límites WIP

| Columna | Descripción | WIP máximo |
|---|---|---|
| **Backlog** | Historias priorizadas (epics de cada semana del §5) | ∞ |
| **En Progreso** | Trabajo en curso (máx. 3 historias simultáneas) | **3** |
| **Revisión / QA** | Code review + pruebas de integración | **2** |
| **Hecho** | Cumple la Definición de Hecho (§4) | ∞ |

> Regla de oro: **no multitarea**. Una historia se termina (o se devuelve al backlog) antes de tomar otra.

---

## 3. Ceremonias semanales (duración)

| Ceremonia | Día | Duración |
|---|---|---|
| Daily (sincronización) | Lun–Vie | 15 min |
| Refinamiento del backlog | Lunes | 30 min |
| Revisión de sprint + demo | Viernes | 45 min |
| Retrospectiva | Viernes | 30 min |

---

## 4. Definición de Hecho (DoD) — aplica a toda historia

- [ ] Implementa **todas** las firmas del puerto `ABC` de `dominio/` correspondiente (sin inventar ni omitir métodos).
- [ ] No contiene reglas de negocio: toda validación vive en el dominio.
- [ ] `python -m compileall -q dominio adaptadores` compila sin errores.
- [ ] Tests de integración en verde contra el recurso real (BD SQLite/Postgres, motor, archivo PDF/Excel, API externa mockeada).
- [ ] Migración Alembic generada y aplicable desde cero (para persistencia).
- [ ] Maneja errores de infraestructura sin filtrar detalles internos al dominio.
- [ ] Sin regresiones en la suite completa.

---

## 5. Calendarización — 12 semanas (2026)

> Cada semana es un **sprint scrumban** con objetivo, entregable y criterios de aceptación.
> **Nota de sincronización:** estos sprints corren en paralelo con el calendario de `adaptadores/primarios/`. El lado primario consume cada puerto **una semana después** de que aquí esté terminado (S1–S4 de persistencia habilitan S3–S9 de la API). La demo del viernes integra ambos lados.

| Sem. | Sprint | Objetivo | Entregable semanal | Criterios de aceptación |
|:---:|---|---|---|---|
| **1** | S1 · Fundación de datos y auth | Preparar la capa de infraestructura base | Configuración de **SQLAlchemy** (SQLite dev / PostgreSQL prod) + **Alembic** (migraciones), gestión de sesiones, modelo base; selección e instalación de librerías de auth (bcrypt/argon2 + JWT) | Conexión a BD desde configuración; `alembic upgrade head` crea la BD vacía; prototipo de `hashear/verificar` responde correctamente |
| **2** | S2 · Repos de usuarios y atletas | Persistir identidad y expediente deportivo | `RepositorioUsuarios` + `RepositorioAtletas` + `RepositorioCategorias` (SQLAlchemy) con **migración inicial** | CRUD completo; `buscar_por_correo` y `buscar_por_id` funcionan; validación de límite 40 atletas se delega al dominio; migración aplicable desde cero |
| **3** | S3 · Repos de objetivos y entrenamientos | Persistir planificación y avance | `RepositorioObjetivos` + `ProveedorDatosAvance` (consulta cruzada real a horas ejecutadas/rating/torneos) + `RepositorioEntrenamientos` + `RepositorioAsistencia` | Crear/actualizar objetivos y planes semanales; `ProveedorDatosAvance` devuelve datos agregados de entrenamientos y partidas; % de asistencia calculable |
| **4** | S4 · Repos restantes (completitud) | Cubrir los 10 módulos del dominio | `RepositorioPartidas`, `RepositorioAnalisisTecnico`, `RepositorioAperturas`, `RepositorioEvaluaciones`, `RepositorioIndicadores`, `RepositorioPatrones`, `RepositorioAuditoria` + **migraciones completas** | **Todos** los `Repositorio*` del dominio implementados; auditoría inmutable (sin update/delete, RF-12); los históricos no se pueden modificar |
| **5** | S5 · Autenticación completa | Seguridad de identidad | `ServicioHashContrasenas` definitivo (bcrypt/argon2), emisión/validación de **JWT** (o sesiones), integración de `PermisosPorRol` (RBAC) como middleware/dependencia | Hash y verificación correctos; token inválido/expirado rechazado; roles ENTRENADOR/ATLETA/INVITADO resuelven permisos según matriz del dominio |
| **6** | S6 · Parser PGN | Importar partidas estructuradas | `ProveedorPGN` con **python-chess**: validación del archivo, extracción de datos (evento, fecha, jugadores, ratings, resultado, apertura ECO, control de tiempo), carga individual y masiva, errores de parseo controlados | Un PGN válido produce una `Partida` estructurada del dominio; PGN inválido lanza error controlado sin romper el lote |
| **7** | S7 · Motor de ajedrez | Análisis técnico automático | `ProveedorEvaluacionMotor` con **Stockfish**: evaluación numérica de posiciones, y a partir de PGN: cálculo de **accuracy, ACPL, blunders, errores, imprecisiones, brilliant** y tiempos por jugada | Un PGN con 40+ jugadas produce un `AnalisisTecnico` completo; umbrales de blunder/error coherentes con RF-05.5; motor arranca/apaga sin fugas de proceso |
| **8** | S8 · Reportes PDF | Generar informes individuales y grupales | `ServicioGeneracionReportes` (ReportLab): plantillas de perfil, evolución de rating, estadísticas de partidas, historial de torneos, aperturas, objetivos SMART, **Informe Integral del Atleta (8 secciones, RF-11.10)**, reporte grupal e institucional | Cada plantilla genera PDF sin errores; el Informe Integral contiene las **8 secciones** obligatorias en el orden definido por el dominio |
| **9** | S9 · Reportes Excel | Exportación tabular | `ServicioGeneracionReportes` (OpenPyXL): tablas de historial de partidas, entrenamientos, objetivos, estadísticas por apertura/torneo, ranking, asistencia, informe integral en Excel | Cada exportación genera `.xlsx` válido; encabezados y datos correctos; formatos (colores semáforo) aplicados según rango de evaluación |
| **10** | S10 · APIs externas | Sincronización con plataformas | Clientes **Chess.com** y **Lichess** (ratings y partidas del atleta) y soporte de fuente **ChessBase** (RF-05.2), normalización a estructuras del dominio, sincronización manual y programada | Traer ratings de Chess.com/Lichess actualiza el `Rating` del atleta (RF-13.6); importar partidas externas (incl. ChessBase) produce `Partida` + resumen; errores de red controlados con reintentos |
| **11** | S11 · Optimización y Postgres | Rendimiento y producción | Índices, eliminación de N+1, migración a **PostgreSQL** + Alembic de producción, respaldos, transacciones para auditoría inmutable, caché de lecturas | Consultas de dashboards < 3 s (RNF-01.4) con 40 atletas; `alembic upgrade head` en Postgres limpio; respaldo/restauración probados |
| **12** | S12 · Integración final | Cierre de la base de salida | Pruebas de integración completas (todos los puertos), **seed** de datos de prueba realistas, documentación de cada adaptador, hardening (manejo de errores, secretos), retro y métricas scrumban | 100 % de puertos probados contra recursos reales; seed reproducible; secretos fuera del código; métricas del tablero reportadas en la retro final |

---

## 6. Backlog priorizado por Epic (referencia para el tablero)

1. **EPIC-DATOS** (S1–S4): SQLAlchemy/Alembic, repos de los 10 módulos, consulta cruzada.
2. **EPIC-SEGURIDAD** (S5): hash, JWT/OAuth, RBAC.
3. **EPIC-ANÁLISIS** (S6–S7): parser PGN + motor Stockfish (accuracy, ACPL, blunders).
4. **EPIC-REPORTES** (S8–S9): PDF (ReportLab) y Excel (OpenPyXL), informe integral.
5. **EPIC-CONECTIVIDAD** (S10): Chess.com, Lichess.
6. **EPIC-PRODUCCIÓN** (S11–S12): Postgres, optimización, respaldos, integración final.

---

## 7. Métricas y reglas de flujo

| Métrica | Objetivo |
|---|---|
| Cycle time por historia | ≤ 2 días hábiles |
| Throughput semanal | 4–6 historias |
| WIP en Progreso | ≤ 3 (estricto) |
| % entregables semanales cumplidos | ≥ 90 % |

**Reglas:**
- Se trabaja en *pull*: nada entra a `En Progreso` sin capacidad.
- Los bloqueos se marcan con etiqueta roja y se escalan en el daily (máx. 1 día).
- Al terminar la semana, lo no completado regresa al backlog priorizado y se reprioriza en el refinamiento del lunes (no se arrastra a ciegas).
