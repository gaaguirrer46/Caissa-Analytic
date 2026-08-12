# Calendario Scrumban — Frontend (Interfaz Visual)

> **Capa de presentación — fuera del hexágono.** Contiene la interfaz visual de la plataforma web de Se Caissa Analytics para el **entrenador** (gestión completa) y el **atleta** (consulta y registro de ejecuciones/objetivos), con roles y permisos (RF-01).
> Consume la **Web API** de `adaptadores/primarios/web/`. No contiene reglas de negocio: solo presenta datos y envía acciones.

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
| **Revisión / QA** | Code review + pruebas de interfaz | **2** |
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

- [ ] La pantalla consume la **Web API** real (no datos mockeados), salvo indicación contraria.
- [ ] Respeta los **roles**: el atleta no ve ni modifica datos ajenos (RF-01.6).
- [ ] Usa el **design system** común (colores, tipografía, componentes) y los **semáforos** (verde/amarillo/rojo, RNF-03.3).
- [ ] Responsive (móvil y escritorio) y accesible (navegación por teclado, contraste).
- [ ] Estados de carga/error/vacío manejados.
- [ ] Sin errores en consola ni vulnerabilidades básicas (XSS, tokens en local en memoria segura).

---

## 5. Calendarización — 12 semanas (2026)

> Cada semana es un **sprint scrumban** con objetivo, entregable y criterios de aceptación.
> **Nota de sincronización:** cada pantalla consume la API correspondiente de `adaptadores/primarios/` (módulo listo en su semana del calendario primario). Si la API de un módulo aún no está, se desarrolla contra el **contrato OpenAPI** acordado.

| Sem. | Sprint | Objetivo | Entregable semanal | Criterios de aceptación |
|:---:|---|---|---|---|
| **1** | S1 · Fundación visual | Preparar la base de la interfaz | Setup del proyecto SPA (estructura, routing, HTTP client), **design system** (paleta, tipografía, componentes base: tablas, formularios, botones, semáforos), layout maestro (sidebar, header) | Layout navegable; componentes base reutilizables; paleta y semáforos definidos según RNF-03.3 |
| **2** | S2 · Identidad y sesión | Autenticación en la UI | Pantallas de **login** y registro, gestión de sesión/token, **guardas de ruta por rol** (ENTRENADOR/ATLETA/INVITADO) | Login válido entra; token inválido redirige a login; atleta no accede a rutas de entrenador (RF-01.6) |
| **3** | S3 · Atletas | Expediente deportivo en pantalla | Listado de atletas (búsqueda/filtros), **perfil** con edad calculada, formulario de alta/edición, visualización de ratings y categorías | Alta valida campos obligatorios (RF-02.2); perfil muestra edad automática; filtro por entrenador/categoría |
| **4** | S4 · Objetivos SMART | Seguimiento visual | CRUD de objetivos, **semáforo** de estado (RF-03.4), flujo de propuesta → aprobación por entrenador, barra de porcentaje de avance | Objetivo propuesto queda PENDIENTE_APROBACION; solo entrenador aprueba (RF-03.7); semáforo refleja estado |
| **5** | S5 · Entrenamientos | Planificación y registro | Vista **por semana** (RF-04.5): plan con sesiones, registro de ejecución (atleta), aprobación de horas (entrenador), **registro de asistencia**, % de cumplimiento | Detalle siempre por semana; atleta reporta horas; entrenador aprueba; cumplimiento = ejecutadas aprobadas / planificadas |
| **6** | S6 · Partidas y análisis | Gestión competitiva | Registro de partidas, **análisis técnico** (accuracy, ACPL, blunders…), clasificación visual (botada/excelente/buena/libro), **importación de PGN** (subir archivo) | Datos obligatorios validados (RF-05.1); clasificación visible; PGN importado crea la partida |
| **7** | S7 · Aperturas y patrones | Repertorio y tendencias | Gestión del repertorio de aperturas (ECO, color, estado, efectividad), **visualización de patrones** de error por periodo con frecuencias | Apertura por color independiente (RF-08.2); patrones solo con mínimos de partidas (RF-06.9) |
| **8** | S8 · Dashboards | KPIs y alertas | **Dashboard del entrenador** (estado del equipo, alertas, cumplimiento, evolución de rating grupal) y **dashboard del atleta** (KPIs con semáforos, comparación mensual), gráficos interactivos (RNF-03.4) | Alertas visibles y destacadas; comparación mes actual vs anterior; gráficos interactivos (RF-09.7) |
| **9** | S9 · Reportes | Exportación e informes | Botones de **exportación PDF/Excel**, vista del Informe Integral del Atleta (8 secciones, RF-11.10), informes individual/grupal/institucional | Exportación descarga el archivo desde la API; informe integral muestra las 8 secciones |
| **10** | S10 · Evaluación y auditoría | Zona de administración | Pantallas de **evaluaciones** (entrenador obligatoria, autoevaluación opcional, escala 1–10), historial de **auditoría** con filtros | Calificación validada 1–10 (RF-10.4); historial exige al menos un filtro (RF-12) |
| **11** | S11 · Calidad integral | Blindar la interfaz | Responsive completo, accesibilidad (navegación por teclado, contraste, ARIA), **pruebas E2E** de los flujos principales, revisión de estados de carga/error | Flujos E2E en verde (login→atleta→objetivo→entrenamiento→partida→reporte); uso en móvil sin roturas |
| **12** | S12 · Release visual | Entrega pulida | Pulido visual (micro-interacciones, consistencia), optimización de rendimiento (carga inicial, lazy loading), **release candidate**, demo final, retro y métricas scrumban | RC navegable en los 3 roles; carga inicial < 2 s; sin errores de consola; métricas del tablero reportadas |

---

## 6. Backlog priorizado por Epic (referencia para el tablero)

1. **EPIC-BASE-UI** (S1): setup, design system, layout.
2. **EPIC-SESION** (S2): login, roles, guardas.
3. **EPIC-EXPEDIENTE-UI** (S3): atletas.
4. **EPIC-SEGUIMIENTO-UI** (S4–S5): objetivos y entrenamientos.
5. **EPIC-COMPETICION-UI** (S6–S7): partidas, aperturas, patrones.
6. **EPIC-ANALITICA-UI** (S8–S9): dashboards y reportes.
7. **EPIC-ADMIN-UI** (S10): evaluaciones y auditoría.
8. **EPIC-CALIDAD-UI** (S11–S12): responsive, E2E, release.

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
- Al terminar la semana, lo no completado regresa al backlog priorizado y se reprioriza en el refinamiento del lunes.
