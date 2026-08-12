# Calendario Scrumban — Adaptadores Primarios (Driving / Entrada)

> **Base del hexágono — lado primario (driving).** Contiene la entrada al sistema: **Web API (FastAPI)**, **CLI / Scripts** y la suite de **Tests** que ejercitan los casos de uso del dominio.
> Estos adaptadores reciben la petición del usuario, la traducen a una llamada a un caso de uso de `dominio/` y devuelven la respuesta. **Nunca contienen reglas de negocio.**

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
| **Revisión / QA** | Code review + pruebas de aceptación | **2** |
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

- [ ] El código implementa el caso de uso de `dominio/` correspondiente **sin duplicar reglas de negocio**.
- [ ] `python -m compileall -q dominio adaptadores` compila sin errores.
- [ ] Los 14 módulos del dominio siguen importando (validación de `Documentacion_del_Dominio.md` §10).
- [ ] Endpoint/CLI documentado en **OpenAPI** (para web) o `--help` (para CLI).
- [ ] Tests de aceptación (HTTP/CLI) en verde: `pytest`.
- [ ] Errores de dominio mapeados a respuestas HTTP correctas (`ErrorValidacion`→400, `ErrorAutenticacion`→401, `EntidadNoEncontrada`→404, resto→500).
- [ ] Sin regresiones en la suite completa.

---

## 5. Calendarización — 12 semanas (2026)

> Cada semana es un **sprint scrumban** con objetivo, entregable y criterios de aceptación.
> **Nota de sincronización:** estos sprints corren en paralelo con el calendario de `adaptadores/secundarios/` (persistencia, autenticación, motor, etc.). La semana **N** del primario consume los puertos que el secundario ya implementó en semanas **N‑1 y anteriores**. La demo del viernes integra ambos lados.

| Sem. | Sprint | Objetivo | Entregable semanal | Criterios de aceptación |
|:---:|---|---|---|---|
| **1** | S1 · Fundación | Montar el proyecto de adaptadores y el pipeline | Repositorio ejecutable: estructura `adaptadores/primarios/{web,cli}`, dependencias (FastAPI, Uvicorn, Pydantic, httpx, pytest), entorno virtual y **CI verde** (lint + compileall + pytest) | Endpoint de salud `GET /health` responde 200; CI pasa en cada push; README técnico breve |
| **2** | S2 · Esqueleto de API + CLI | Definir el contrato de la API y el CLI base | Esqueleto FastAPI: routers por módulo, **schemas Pydantic** (DTOs), manejo global de errores (mapeo `ErrorDeDominio` → HTTP), middleware de logging; CLI base con `--help` | `GET /docs` (OpenAPI) muestra todos los routers; un error `ErrorValidacion` se traduce a 400 en un endpoint de prueba; CLI responde `--help` |
| **3** | S3 · Usuarios y sesión | Exponer autenticación y gestión de usuarios | Endpoints: `POST /usuarios` (crear, valida 1 solo ENTRENADOR), `POST /auth/login`, `GET /usuarios/me`, `POST /auth/verificar-permiso` | Login con credenciales válidas devuelve token; rol INVITADO no accede a `GESTIONAR_ATLETAS`; intento de 2º ENTRENADOR → 400 (RF-01.8) |
| **4** | S4 · Atletas | CRUD del expediente deportivo | Endpoints: alta/actualización/consulta de atleta (con edad calculada), asignación de categorías, asignación de 1–3 entrenadores (RF-02.6), actualización de rating | Registro sin ratings obligatorios → 400 (RF-02.2); `GET /atletas/{id}` devuelve `edad` calculada; asignar 4º entrenador → 400 |
| **5** | S5 · Objetivos SMART | Seguimiento de objetivos por la API | Endpoints: crear objetivo (queda PENDIENTE_APROBACION), aprobar, calcular avance, evaluar estado (semáforo), listar por filtros, validar cumplimiento | Objetivo sin fecha límite → 400 (RF-03.3); atleta no puede aprobar su propio objetivo (403); semáforo RETRASADO cuando aplica (RF-03.8) |
| **6** | S6 · Entrenamientos | Planificación semanal y asistencia | Endpoints: plan semanal, reprogramar sesión, registrar ejecución (atleta), aprobar horas (entrenador), cumplimiento semanal (%), registrar asistencia, historial | Plan de la semana con sesiones; % cumplimiento = ejecutadas aprobadas / planificadas; sesión cancelada conserva historial (RF-04.6); asistencia post-sesión |
| **7** | S7 · Partidas y análisis | Registro competitivo y análisis técnico | Endpoints: registrar partida, registrar análisis técnico, clasificar partida (PARTIDA_BOTADA/EXCELENTE/BUENA/LIBRO), estadísticas por fase, **importar partida desde PGN** (vía puerto `ProveedorPGN`) | Partida sin datos obligatorios → 400 (RF-05.1); clasificación automática correcta (ej. ventaja > +3 + blunder → botada); importación PGN crea partida + resumen |
| **8** | S8 · Aperturas y patrones | Repertorio y detección de patrones | Endpoints: registrar apertura del repertorio, clasificar principal/secundaria, efectividad (motor), estadísticas generales y por torneo; detección de patrones por periodo | Apertura registrada por color independiente (RF-08.2); estadísticas por torneo filtradas (año, color, rival); patrón solo si ≥5 partidas o >40% (RF-06.8) |
| **9** | S9 · Analítica y reportes | Dashboards, tendencias, evaluaciones y auditoría | Endpoints: indicadores principales/secundarios, dashboard entrenador y atleta, comparar tendencias, generar reporte (PDF/Excel vía puerto), evaluaciones (RF-10), consulta de auditoría | Dashboard del entrenador con alertas automáticas; reporte genera archivo a través de `ServicioGeneracionReportes`; evaluación sin calificación 1–10 → 400; historial de auditoría exige filtro (RF-12) |
| **10** | S10 · CLI operativo | Automatizar operaciones del entrenador | CLI: seed de datos de prueba, importación masiva PGN, sincronización de ratings, generación de reportes por consola, consultas rápidas (cumplimiento, patrones) | Cada comando documentado en `--help`; un flujo completo seed→consulta funciona por consola; salidas legibles (tablas/formato JSON) |
| **11** | S11 · Calidad E2E | Blindar la API y el CLI | Suite **E2E**: flujo integral (login → atleta → objetivo → entrenamiento → partida → reporte), pruebas de RBAC (atleta no ve datos ajenos, RF-01.6), pruebas de carga básica (< 3 s por consulta, RNF-01.4), fuzzing de entradas | 100 % de flujos E2E en verde; intento de acceso cruzado entre atletas → 403; p95 de consultas < 3 s; sin endpoints sin probar |
| **12** | S12 · Cierre y release | Entregar la base de entrada lista para producción | OpenAPI pulido, hardening de entrada (validación estricta, rate limiting, CORS), **release candidate**, demo final, acta de retro y métricas scrumban (cycle time, throughput) | RC desplegable; documentación de la API completa; métricas del tablero reportadas en la retro final |

---

## 6. Backlog priorizado por Epic (referencia para el tablero)

1. **EPIC-FUNDACIÓN** (S1–S2): estructura, CI, esqueleto API/CLI, manejo de errores.
2. **EPIC-IDENTIDAD** (S3): usuarios, login, RBAC por API.
3. **EPIC-EXPEDIENTE** (S4): atletas, categorías, ratings.
4. **EPIC-PLANIFICACIÓN** (S5–S6): objetivos SMART y entrenamientos.
5. **EPIC-COMPETICIÓN** (S7–S8): partidas, análisis, aperturas, patrones.
6. **EPIC-ANALÍTICA** (S9): dashboards, tendencias, reportes, evaluaciones, auditoría.
7. **EPIC-OPS** (S10): CLI, seeds, automatización.
8. **EPIC-CALIDAD** (S11–S12): E2E, seguridad, release.

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
