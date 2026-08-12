# Historias por Semana — Tests (Calidad)

> Historias de usuario de la capa de **calidad**, organizadas por semana según el `Calendario_Scrumban.md` de esta carpeta.
> **Formato:** `H-T-XX | Historia | Prioridad | Criterios de aceptación`.

---

## Semana 1 · Fundación de calidad

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-T-01 | Como desarrollador, quiero **configurar pytest** (fixtures, conftest, cobertura) para la suite. | Alta | `pytest` con cobertura reportada; marcadores definidos. |
| H-T-02 | Como equipo, quiero tests del paquete **`comun/`** (errores, constantes, límites, ids). | Alta | Errores se lanzan según reglas; límites verificados. |
| H-T-03 | Como equipo, quiero tests de las **entidades** de usuarios y atletas (edad, ratings, inmutabilidad). | Alta | Edad calculada correcta; `PerfilHistorico` inmutable. |

## Semana 2 · Casos de uso I

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-T-04 | Como equipo, quiero tests de **usuarios**: autenticar, crear (1 solo ENTRENADOR), permisos, perfil. | Alta | RF-01.8 verificado; credenciales inválidas → error; matriz de permisos correcta. |
| H-T-05 | Como equipo, quiero tests de **atletas**: registrar (obligatorios), asignar entrenadores (1–3), ratings, historial. | Alta | RF-02.2 y RF-02.6 verificados; snapshot histórico no modificable. |

## Semana 3 · Casos de uso II

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-T-06 | Como equipo, quiero tests de **objetivos SMART**: crear, aprobar, avance, semáforo, cumplimiento. | Alta | RETRASADO cuando real < esperado (RF-03.8); solo entrenador valida (RF-03.7). |
| H-T-07 | Como equipo, quiero tests de **entrenamientos**: plan, reprogramar, ejecución/aprobación, cumplimiento, asistencia. | Alta | % de cumplimiento exacto (RF-04.4); historial conservado. |

## Semana 4 · Casos de uso III

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-T-08 | Como equipo, quiero tests de **partidas**: validación, clasificación, estadísticas por fase, importación PGN. | Alta | Clasificación respeta color del atleta; botada = ventaja > +3 + blunder. |
| H-T-09 | Como equipo, quiero tests de **aperturas y patrones**: repertorio por color, efectividad, umbrales. | Alta | Patrón solo ≥ 5 partidas o > 40 % (RF-06.8); mínimos por tipo (RF-06.9). |

## Semana 5 · Casos de uso IV

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-T-10 | Como equipo, quiero tests de **indicadores**: KPIs, rangos, dashboards, tendencias, reportes. | Alta | Rangos por defecto correctos (RF-09.3); ACPL/blunders: menor es mejor. |
| H-T-11 | Como equipo, quiero tests de **evaluaciones y auditoría**: escala 1–10, inmutabilidad, filtros. | Alta | Auditoría sin modificar históricos (RF-12); evaluación obligatoria/opcional (RF-10.3). |

## Semana 6 · Integración de persistencia

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-T-12 | Como equipo, quiero **tests de integración de repositorios** contra SQLite real. | Alta | CRUD real; FK y unicidad verificadas. |
| H-T-13 | Como equipo, quiero tests de **migraciones Alembic** (aplicar desde cero, reversa) y de inmutabilidad de históricos. | Alta | `upgrade`/`downgrade` correctos; históricos protegidos. |

## Semana 7 · API

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-T-14 | Como equipo, quiero tests de la **API** por módulo (CRUD y códigos HTTP). | Alta | 400/401/404/500 correctos según el error de dominio. |
| H-T-15 | Como equipo, quiero tests de **contratos** (schemas Pydantic de respuesta). | Alta | Respuestas validan contra el esquema acordado. |

## Semana 8 · Seguridad

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-T-16 | Como equipo, quiero tests de **autenticación** (login, token inválido/expirado). | Alta | Tokens rechazados correctamente (401). |
| H-T-17 | Como equipo, quiero tests de **RBAC**: atleta no ve datos ajenos, invitado limitado. | Alta | RF-01.4/01.6/01.7 verificados (403 en accesos prohibidos). |

## Semana 9 · Análisis externo

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-T-18 | Como equipo, quiero tests del **parser PGN** (válido, inválido, lote). | Alta | PGN malformado → error controlado; lote procesa sin detenerse. |
| H-T-19 | Como equipo, quiero tests del **motor Stockfish** (evaluación y métricas con datos conocidos). | Media | Accuracy/ACPL/blunders con valores esperados. |

## Semana 10 · Reportes

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-T-20 | Como equipo, quiero tests de **generación PDF** (informe integral con 8 secciones). | Alta | Archivo válido; 8 secciones en orden (RF-11.10). |
| H-T-21 | Como equipo, quiero tests de **generación Excel** (hojas, encabezados, datos). | Alta | `.xlsx` con contenido esperado. |

## Semana 11 · E2E y carga

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-T-22 | Como equipo, quiero **tests E2E** del flujo integral con la app real. | Alta | Flujo completo en verde (login→atleta→objetivo→entrenamiento→partida→reporte). |
| H-T-23 | Como equipo, quiero **pruebas de carga** básica. | Media | p95 de consultas < 3 s (RNF-01.4). |

## Semana 12 · Cierre de calidad

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-T-24 | Como equipo, quiero alcanzar la **cobertura objetivo** (≥ 80 % dominio, ≥ 70 % global). | Alta | Cobertura verificada y reportada. |
| H-T-25 | Como equipo, quiero **documentación de la suite** y su integración final con CI. | Media | Suite documentada; CI ejecuta todos los tests; retro con métricas. |
