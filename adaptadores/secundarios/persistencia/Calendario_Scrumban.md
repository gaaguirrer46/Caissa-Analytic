# Calendario Scrumban — Base de Datos (URGENTE · 2 semanas)

> **Base de datos de Se Caissa Analytics.** Por la urgencia del proyecto, la BD **no espera a las 12 semanas**: se construye en **2 semanas** para desbloquear a todos los demás grupos (backend, API, frontend, tests).
> La BD se divide en **funcionalidades** (F0–F10) según los módulos del dominio. Cada funcionalidad es un **paquete de trabajo** que el coordinador repartirá a distintos **grupos de trabajo** (ver `Historias_por_Funcionalidad.md`).

---

## Cómo se trabaja en modo urgente (Scrumban exprés)

| Práctica | Cómo se aplica |
|---|---|
| **Sprint** | 2 sprints de 1 semana cada uno. |
| **Tablero** | `Backlog → En Progreso → Revisión/QA → Hecho` con WIP = **2 por grupo** de trabajo. |
| **Paralelismo** | Cada **funcionalidad (grupo)** trabaja en paralelo sobre su propio esquema; el coordinador integra a diario (daily de 15 min). |
| **Contrato** | Todos los grupos usan el mismo **motor y sistema de migraciones** y las mismas **convenciones de nombres** (tablas en `snake_case`, PK `id UUID/texto`, FK `*_id`). |
| **Integración continua** | Al final de cada día se integra al esquema común (`main`) para detectar conflictos temprano. |

---

## 1. Funcionalidades (paquetes de trabajo para los grupos)

| ID | Funcionalidad | Módulo del dominio | Tablas principales |
|---|---|---|---|
| **F0** | Núcleo y catálogos (transversal) | — | Configuración, migraciones base, catálogos (categorías, rangos de evaluación) |
| **F1** | Usuarios y Permisos | RF-01 | `usuarios`, roles/permisos |
| **F2** | Atletas y Categorías | RF-02 | `atletas`, `ratings`, `categorias`, `clubs`, `perfil_historico` |
| **F3** | Objetivos SMART | RF-03 | `objetivos`, `indicadores_avance` |
| **F4** | Entrenamientos y Asistencia | RF-04 | `planes_semanales`, `sesiones`, `ejecuciones`, `asistencias` |
| **F5** | Partidas y Análisis Técnico | RF-05 / RF-07 | `partidas`, `analisis_tecnico`, `estadisticas_fase` |
| **F6** | Aperturas | RF-08 | `aperturas_repertorio`, `estadisticas_apertura`, `estadisticas_torneo` |
| **F7** | Patrones de Error | RF-06 | `analisis_patrones`, `patrones_detectados` |
| **F8** | Indicadores y Dashboards | RF-09 / RF-11 | `indicadores`, `alertas`, vistas de dashboards |
| **F9** | Evaluaciones | RF-10 | `evaluaciones_atleta` |
| **F10** | Auditoría | RF-12 | `registros_auditoria` |

> Las historias detalladas de cada funcionalidad están en **`Historias_por_Funcionalidad.md`**.

---

## 2. Definición de Hecho (DoD) — aplica a cada funcionalidad

- [ ] Esquema **normalizado** (hasta 3FN cuando aplique) con PK, FK e índices básicos.
- [ ] Constraints de integridad: obligatorios, unicidad, rangos (ej. calificación 1–10, rating ≥ 0).
- [ ] **Migración** generada en `migraciones/versions/` y aplicable desde cero.
- [ ] **Seed de datos de prueba** para la funcionalidad (realista y coherente entre tablas).
- [ ] **Vistas y filtros** definidos (semana 2) tal como los consumirá el backend.
- [ ] Documentada la funcionalidad (tablas, relaciones, vistas) en el propio `Historias_por_Funcionalidad.md` o nota de entrega.

---

## 3. Calendarización — 2 semanas (URGENTE)

### Semana 1 — Esquema completo + datos de prueba

> **Objetivo:** dejar la **base de datos creada y poblada** con datos de prueba, lista para que el backend empiece a persistir.

| Entregable | Criterios de aceptación |
|---|---|
| **Esquema completo** de las 11 funcionalidades (F0–F10) en el motor elegido (SQLite para dev / PostgreSQL para prod) | Todas las tablas del §1 creadas con PK, FK, constraints y tipos correctos |
| **Migraciones** base + por funcionalidad en `migraciones/versions/` | `alembic upgrade head` crea la BD completa desde cero; `downgrade` funciona |
| **Datos de prueba (seed)** para todas las funcionalidades | Usuarios (1 entrenador, atletas, invitado), atletas con ratings, objetivos, planes y sesiones, partidas con análisis, aperturas, patrones, indicadores, evaluaciones y registros de auditoría |
| **Coherencia entre funcionalidades** | Las FK cruzadas (ej. `objetivos.id_atleta` → `atletas.id`) se cumplen; seed sin datos huérfanos |
| **Integración diaria** | Esquema común integrado al final de cada día; sin conflictos pendientes al cierre de la semana |

### Semana 2 — Vistas, filtros e índices (todo lo que el backend necesita)

> **Objetivo:** entregar las **consultas, vistas y filtros** que los repositorios del backend consumirán, optimizadas para dashboards.

| Entregable | Criterios de aceptación |
|---|---|
| **Vistas por funcionalidad** | Vistas de expediente de atleta (con edad), semáforo de objetivos, cumplimiento semanal, estadísticas por fase, efectividad de aperturas, patrones por periodo, KPIs/dashboards, alertas activas, historial de auditoría, etc. (detalle en `Historias_por_Funcionalidad.md`) |
| **Filtros/consultas del backend** | Consultas de los `Repositorio*` del dominio: por atleta, por entrenador, por periodo/fechas, por estado, por categoría, por color, por torneo, por rango de rating |
| **Índices de rendimiento** | Índices sobre FK y campos de filtro frecuentes (id_atleta, fecha, estado); consultas de dashboard < 3 s con 40 atletas (RNF-01.4) |
| **Optimizaciones** | Sin N+1 en consultas de listados; joins correctos en vistas |
| **Documentación de entrega** | Esquema + vistas documentados para el backend y el frontend |

---

## 4. Métricas del modo urgente

| Métrica | Objetivo |
|---|---|
| Funcionalidades (grupos) en paralelo | Hasta 11 (F0–F10) |
| WIP por grupo | ≤ 2 historias |
| Integraciones al esquema común | 1 diaria |
| Esquema completo + seed | Cierre de la **Semana 1** |
| Vistas + filtros + índices | Cierre de la **Semana 2** |

> **Regla de oro:** si una funcionalidad se atrasa, el coordinador **rebalancea historias entre grupos** en el daily — nada se arrastra a la siguiente semana, porque el resto del proyecto depende de esta entrega.
