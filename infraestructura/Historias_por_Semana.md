# Historias por Semana — Infraestructura (Configuración, DI, Despliegue)

> Historias de usuario de la capa de **composición**, organizadas por semana según el `Calendario_Scrumban.md` de esta carpeta.
> **Formato:** `H-I-XX | Historia | Prioridad | Criterios de aceptación`.

---

## Semana 1 · Fundación

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-I-01 | Como desarrollador, quiero **settings centralizados** (variables de entorno con defaults) para configurar la app. | Alta | Config leída de `.env`; `.env.example` documentado. |
| H-I-02 | Como desarrollador, quiero **logging estructurado** con niveles y formato definidos. | Alta | Logs con timestamp, nivel y contexto; configurable por entorno. |
| H-I-03 | Como desarrollador, quiero la **declaración de dependencias** (pyproject/requirements) del proyecto. | Alta | Instalación reproducible. |
| H-I-04 | Como equipo, quiero un **CI básico** (lint + compileall + pytest). | Alta | Pipeline verde en cada push. |

## Semana 2 · Composición

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-I-05 | Como desarrollador, quiero un **contenedor de dependencias** que inyecte adaptadores en los casos de uso. | Alta | `RegistrarAtleta` recibe `RepositorioAtletas` real sin tocar el dominio. |
| H-I-06 | Como desarrollador, quiero una **fábrica de sesiones SQLAlchemy** centralizada. | Alta | Sesión disponible para todos los repos; cierre automático. |
| H-I-07 | Como desarrollador, quiero un **`main.py`** que arranque la API con `/health`. | Alta | Arranque limpio; `/health` 200. |

## Semana 3 · Entornos y secretos

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-I-08 | Como operador, quiero **perfiles dev/test/prod** para correr la misma app en distintos entornos. | Alta | La app arranca con la config correcta en los 3 entornos. |
| H-I-09 | Como operador, quiero **gestión de secretos** (BD, JWT, API keys) fuera del código. | Alta | Sin secretos en repositorio; fallo al arrancar si faltan críticos. |

## Semana 4 · Migraciones y seed

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-I-10 | Como desarrollador, quiero **integrar Alembic** con la configuración del proyecto. | Alta | `env.py` lee settings; comandos funcionan. |
| H-I-11 | Como desarrollador, quiero una **migración inicial** con el esquema completo del dominio. | Alta | `upgrade head` crea BD desde cero; `downgrade` reversible. |
| H-I-12 | Como operador, quiero un **seed de datos de prueba** ejecutable. | Alta | Puebla datos realistas; reproducible. |

## Semana 5 · Seguridad de la app

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-I-13 | Como operador, quiero **CORS** y **rate limiting** configurados. | Alta | Orígenes permitidos definidos; límites aplicados por endpoint. |
| H-I-14 | Como operador, quiero **headers de seguridad** y **config JWT centralizada** (secreto, expiración). | Alta | Headers presentes en respuestas; JWT usa la config. |
| H-I-15 | Como operador, quiero **logging de auditoría** de peticiones. | Media | Peticiones relevantes registradas con contexto. |

## Semana 6 · Contenedores

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-I-16 | Como operador, quiero un **Dockerfile** multi-etapa para la app. | Alta | Imagen ligera; build reproducible. |
| H-I-17 | Como operador, quiero **docker-compose** (app + BD) con volúmenes y **healthchecks**. | Alta | `docker compose up` levanta todo; datos persistentes. |

## Semana 7 · CI/CD

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-I-18 | Como equipo, quiero un **pipeline completo** (lint → compileall → pytest → build → deploy staging). | Alta | Push a `main` dispara el pipeline; staging actualizado; tests bloquean. |

## Semana 8 · Observabilidad

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-I-19 | Como operador, quiero **manejo global de errores** y logging en producción. | Alta | Errores no capturados con trace completo. |
| H-I-20 | Como operador, quiero un **`/health` detallado** (BD y dependencias) y métricas básicas. | Alta | Estado real reflejado; métricas accesibles. |

## Semana 9 · Respaldo y recuperación

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-I-21 | Como operador, quiero **scripts de respaldo y restauración** de la BD. | Alta | Respaldo verificable; restauración probada (RNF-02.3). |
| H-I-22 | Como operador, quiero la **programación** de respaldos (cron/scheduler). | Media | Respaldo automático ejecutado y verificado. |

## Semana 10 · Rendimiento

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-I-23 | Como operador, quiero **pooling de conexiones** y **caché** de lecturas frecuentes. | Alta | Sin agotamiento de conexiones; catálogos cacheados. |
| H-I-24 | Como desarrollador, quiero **carga diferida** de relaciones para evitar N+1. | Media | Consultas de listados eficientes. |

## Semana 11 · Despliegue y runbooks

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-I-25 | Como operador, quiero **desplegar a producción** (Postgres) desde CI. | Alta | Producción desplegada y estable. |
| H-I-26 | Como operador, quiero **runbooks** (arranque, respaldo, rollback) y **documentación técnica**. | Alta | Runbooks verificados por otro miembro del equipo. |

## Semana 12 · Cierre y hardening

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-I-27 | Como operador, quiero **revisión y rotación de secretos** y hardening final. | Alta | Sin secretos expuestos; checklist de seguridad. |
| H-I-28 | Como equipo, quiero una **release candidate** estable y la retro con métricas scrumban. | Alta | RC desplegable; retro realizada. |
