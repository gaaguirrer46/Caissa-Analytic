# Calendario Scrumban — Tests (Calidad)

> **Capa transversal de calidad.** Contiene la suite de pruebas del proyecto completo: **unitarias** (entidades y casos de uso del dominio), **de integración** (adaptadores contra recursos reales), **de API** (Web API) y **E2E** (flujos completos). Según la documentación, los tests son un **adaptador primario (driving)** que ejercita el sistema desde fuera.
> Los tests son el **guardarraíl** de todos los demás calendarios: cada sprint de otra capa solo se marca como "Hecho" si sus tests pasan aquí.

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
| **Revisión / QA** | Revisión de calidad de los propios tests | **2** |
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

- [ ] Test escrito con **pytest**, nombrado y organizado por módulo (`tests/dominio/…`, `tests/adaptadores/…`, `tests/api/…`, `tests/e2e/…`).
- [ ] Cubre al menos los casos: **feliz, error/borde y negación** de la regla de negocio.
- [ ] No depende de red ni de servicios externos (se usan **fakes/mocks** para puertos).
- [ ] La suite completa pasa: `pytest` en verde.
- [ ] Sin tests frágiles (no dependen de orden ni de tiempos).

---

## 5. Calendarización — 12 semanas (2026)

> Cada semana es un **sprint scrumban** con objetivo, entregable y criterios de aceptación.
> **Nota de sincronización:** esta capa avanza **en paralelo y una semana detrás** de las capas que prueba: el dominio ya está listo (semana 1 se puede cubrir de inmediato) y cada adaptador/API se testea cuando su calendario lo entrega.

| Sem. | Sprint | Objetivo | Entregable semanal | Criterios de aceptación |
|:---:|---|---|---|---|
| **1** | S1 · Fundación de calidad | Preparar la infraestructura de tests | Configuración de **pytest** (fixtures, conftest, marcadores, cobertura con coverage.py), tests del paquete `dominio/comun/` (errores, constantes, reglas de límites, ids) y de entidades de usuarios/atletas | `pytest` corre con cobertura reportada; tests de `comun` y entidades base en verde |
| **2** | S2 · Casos de uso I | Cubrir identidad y expediente | Tests de casos de uso: **usuarios** (autenticar, crear con 1 solo ENTRENADOR, permisos, perfil) y **atletas** (registrar con obligatorios, edad, 1–3 entrenadores, ratings, historial) | Casos de error validados (RF-01.8, RF-02.2, RF-02.6); fakes de repositorios en memoria |
| **3** | S3 · Casos de uso II | Cubrir planificación | Tests de **objetivos SMART** (crear, aprobar, avance, semáforo, cumplimiento solo entrenador) y **entrenamientos** (plan semanal, reprogramar, ejecución/aprobación, cumplimiento %, asistencia) | Semáforo RETRASADO correcto (RF-03.8); % cumplimiento exacto (RF-04.4) |
| **4** | S4 · Casos de uso III | Cubrir competición y análisis | Tests de **partidas** (validación, clasificación botada/excelente/buena/libro, estadísticas por fase, importación PGN) y **aperturas + patrones** (repertorio por color, efectividad, umbrales ≥5 partidas / >40 %) | Clasificación respeta color del atleta (RF-05); umbrales de patrón verificados (RF-06.8) |
| **5** | S5 · Casos de uso IV | Cubrir analítica y trazabilidad | Tests de **indicadores** (KPIs, rangos, dashboards, tendencias, reportes), **evaluaciones** (1–10, obligatoria/opcional) y **auditoría** (registro inmutable, filtros obligatorios) | Rangos por defecto correctos; auditoría no permite modificar históricos (RF-12) |
| **6** | S6 · Integración de persistencia | Probar repos reales | Tests de integración de **todos los `Repositorio*`** de SQLAlchemy contra **SQLite**, incluidas migraciones Alembic y restricciones (unicidad, FK, inmutabilidad de históricos) | CRUD real verificado; migración aplicada desde cero en test; datos de seed disponibles |
| **7** | S7 · API | Probar la Web API | Tests de la **API** con httpx/testclient: CRUD por módulo, códigos HTTP correctos (400/401/404/500), contratos de respuesta (Pydantic) | Mapeo de errores de dominio verificado; esquemas de respuesta validados |
| **8** | S8 · Seguridad | Probar auth y RBAC | Tests de **autenticación** (login, token inválido/expirado) y **RBAC** (atleta no accede a datos ajenos, invitado limitado, entrenador total) | RF-01.4/01.6/01.7 verificados; tokens rechazados correctamente |
| **9** | S9 · Análisis externo | Probar PGN y motor | Tests del **parser PGN** (PGN válido/inválido, lote) y del **motor Stockfish** (evaluación, accuracy/ACPL/blunders con umbrales) | PGN malformado lanza error controlado; análisis con datos conocidos arroja valores esperados |
| **10** | S10 · Reportes | Probar exportaciones | Tests de generación de **PDF** (8 secciones del informe integral, RF-11.10) y **Excel** (hojas, encabezados, datos) | Archivos generados válidos y con contenido esperado |
| **11** | S11 · E2E y carga | Probar flujos completos | **E2E**: flujo integral (login → atleta → objetivo → entrenamiento → partida → reporte) con la app real levantada; **pruebas de carga** básica (< 3 s por consulta, RNF-01.4) | Flujos E2E en verde de punta a punta; p95 de consultas < 3 s |
| **12** | S12 · Cierre de calidad | Consolidar cobertura | Cobertura objetivo (≥ 80 % en dominio, ≥ 70 % global), documentación de la suite, integración final con CI, retro y métricas scrumban | Cobertura reportada y verificada; suite documentada; CI ejecuta toda la suite |

---

## 6. Backlog priorizado por Epic (referencia para el tablero)

1. **EPIC-INFRA-TESTS** (S1): setup, fixtures, cobertura, `comun`.
2. **EPIC-UNIT-DOMINIO** (S2–S5): casos de uso de los 10 módulos.
3. **EPIC-INTEGRACION** (S6): repos SQLAlchemy + Alembic.
4. **EPIC-API** (S7–S8): endpoints, auth, RBAC.
5. **EPIC-EXTERNOS** (S9–S10): PGN, motor, reportes.
6. **EPIC-E2E** (S11–S12): flujos completos, carga, cobertura.

---

## 7. Métricas y reglas de flujo

| Métrica | Objetivo |
|---|---|
| Cycle time por historia | ≤ 2 días hábiles |
| Throughput semanal | 4–6 historias |
| WIP en Progreso | ≤ 3 (estricto) |
| Cobertura del dominio | ≥ 80 % |
| Cobertura global | ≥ 70 % |

**Reglas:**
- Un test que falla se atiende el mismo día (etiqueta roja) y se escala en el daily.
- Prohibido desactivar tests para "que pasen": se corrige el código o el test con justificación.
- Al terminar la semana, lo no completado regresa al backlog priorizado y se reprioriza en el refinamiento del lunes.
