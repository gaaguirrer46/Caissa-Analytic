# Calendario Scrumban — Infraestructura

> **Capa de composición (composition root) — fuera del hexágono.** Contiene todo lo necesario para **cablear** el sistema: configuración (settings, variables de entorno), **contenedor de inyección de dependencias** (une puertos de `dominio/` con adaptadores concretos), fábrica de sesiones de base de datos, `main.py` (punto de arranque), logging, despliegue (Docker/CI) y monitoreo.
> Esta capa **no contiene reglas de negocio**: solo pega las piezas y las configura.

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

- [ ] El sistema arranca desde `main.py` con **todas** las dependencias cableadas (puerto → adaptador).
- [ ] La configuración se lee de variables de entorno con valores por defecto seguros.
- [ ] `python -m compileall -q dominio adaptadores infraestructura` compila sin errores.
- [ ] La suite de tests pasa con la configuración de prueba.
- [ ] Sin secretos en el código (solo en `.env` / variables de entorno).
- [ ] Documentado: cómo arrancar, configurar y desplegar.

---

## 5. Calendarización — 12 semanas (2026)

> Cada semana es un **sprint scrumban** con objetivo, entregable y criterios de aceptación.
> **Nota de sincronización:** esta capa **habilita** a los adaptadores: el contenedor de dependencias (S2) y la integración de migraciones (S4) deben estar listos antes de que primarios/secundarios necesiten probar integración (desde S2–S6).

| Sem. | Sprint | Objetivo | Entregable semanal | Criterios de aceptación |
|:---:|---|---|---|---|
| **1** | S1 · Fundación | Montar la base de configuración y el arranque | `configuracion/` con settings (pydantic-settings/dotenv), logging estructurado, declaración de dependencias (pyproject/requirements), estructura del composition root, **CI básico** (lint + compileall + pytest) | La app lee configuración desde `.env`; logs con niveles y formato definidos; CI verde en cada push |
| **2** | S2 · Composición | Cablear puertos ↔ adaptadores | **Contenedor de dependencias** en `dependencias/` (fábrica que inyecta los adaptadores en los casos de uso), fábrica de sesiones SQLAlchemy en `base_de_datos/`, `main.py` arranca la API con `/health` | Inyectar `RepositorioAtletas` de SQLAlchemy en `RegistrarAtleta` sin tocar el dominio; `/health` responde 200; arranque reproducible |
| **3** | S3 · Entornos y secretos | Configuración por entorno | Perfiles **dev / test / prod**, carga de secretos por entorno (BD, JWT, API keys), validación de configuración al arrancar | La misma app corre en los 3 entornos con distinta configuración; falla al arrancar si faltan secretos críticos; `.env.example` documentado |
| **4** | S4 · Migraciones y seed | Integrar Alembic con el proyecto | Configuración de Alembic (`env.py` leyendo settings), script de **migración inicial** (esquema completo de la BD del dominio), comando/script de **seed** de datos de prueba | `alembic upgrade head` crea la BD desde cero; `seed` puebla datos de prueba; reversible (`downgrade`) |
| **5** | S5 · Seguridad de la app | Endurecer la entrada HTTP | CORS configurado, **rate limiting**, headers de seguridad, configuración JWT (secreto, expiración) centralizada, logging de auditoría de peticiones | Endpoints protegidos usan la config JWT; respuestas con headers seguros; límites de peticiones aplicados |
| **6** | S6 · Contenedores | Entorno reproducible | `Dockerfile` multi-etapa, `docker-compose.yml` (app + BD), volúmenes, redes, **healthchecks** | `docker compose up` levanta app + BD y `/health` responde desde el contenedor; datos de BD persistentes |
| **7** | S7 · CI/CD | Automatizar calidad y despliegue | Pipeline completo: lint → compileall → pytest → build de imagen → **deploy a staging**; badges/estado visible | Un push a `main` dispara el pipeline; staging actualizado automáticamente; tests bloquean el merge si fallan |
| **8** | S8 · Observabilidad | Ver y diagnosticar | Manejo global de errores y excepciones no capturadas, logging estructurado en producción, endpoint `/health` detallado (BD, dependencias), métricas básicas | Un error no capturado queda registrado con trace completo; `/health` refleja el estado real de BD y dependencias |
| **9** | S9 · Respaldo y recuperación | Proteger los datos | Scripts de **respaldo** y **restauración** de la BD, programación (cron/scheduler), verificación de integridad del respaldo | Respaldo programado genera archivo verificable; restauración probada en entorno de prueba; procedimiento documentado |
| **10** | S10 · Rendimiento | Puesta a punto | Pooling de conexiones configurado, caché de lecturas frecuentes (ej. catálogos), tuneo de sesiones, carga diferida de relaciones | Dashboard con 40 atletas responde < 3 s (RNF-01.4); sin conexiones agotadas bajo carga; métricas de pool visibles |
| **11** | S11 · Despliegue y runbooks | Preparar producción | Despliegue a **producción** (Postgres), runbooks (arranque, respaldo, rollback), documentación técnica del composition root, checklist de release | Producción desplegada desde CI; runbooks verificados por otro miembro del equipo; checklist completado |
| **12** | S12 · Cierre y hardening | Entrega final estable | Revisión de secretos (rotación), hardening final, **release candidate**, demo final, acta de retro y métricas scrumban | RC desplegable y estable; sin secretos expuestos; métricas del tablero reportadas |

---

## 6. Backlog priorizado por Epic (referencia para el tablero)

1. **EPIC-BASE** (S1–S2): settings, logging, DI container, sesiones, main.
2. **EPIC-CONFIG** (S3): entornos, secretos, validación.
3. **EPIC-DATOS** (S4): Alembic, migración inicial, seed.
4. **EPIC-SEGURIDAD** (S5): CORS, rate limit, JWT, headers.
5. **EPIC-OPS** (S6–S7): Docker, CI/CD.
6. **EPIC-CALIDAD-OPS** (S8–S10): observabilidad, respaldos, rendimiento.
7. **EPIC-RELEASE** (S11–S12): despliegue, runbooks, hardening.

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
