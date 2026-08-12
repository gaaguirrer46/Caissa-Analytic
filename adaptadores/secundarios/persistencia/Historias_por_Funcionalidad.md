# Historias por Funcionalidad — Base de Datos

> Base de datos de Se Caissa Analytics dividida en **11 funcionalidades (F0–F10)**, una por módulo del dominio.
> Cada funcionalidad es un **paquete de trabajo asignable a un grupo de trabajo**. Las historias se reparten **por funcionalidad** y se ejecutan en paralelo dentro del calendario urgente de 2 semanas (`Calendario_Scrumban.md` de esta carpeta).
> **Formato:** `H-DB-FF-NN | Historia | Semana | Prioridad | Criterios de aceptación`.

---

## Tabla de asignación para el coordinador

| Grupo | Funcionalidad | Alcance (tablas) | Semana 1 | Semana 2 |
|:---:|---|---|:---:|:---:|
| G1 | **F0 · Núcleo y catálogos** | Configuración, catálogos, migraciones base | X | X |
| G2 | **F1 · Usuarios y Permisos** | `usuarios`, roles, permisos | X | X |
| G3 | **F2 · Atletas y Categorías** | `atletas`, `ratings`, `categorias`, `clubs`, `perfil_historico` | X | X |
| G4 | **F3 · Objetivos SMART** | `objetivos`, `indicadores_avance` | X | X |
| G5 | **F4 · Entrenamientos y Asistencia** | `planes_semanales`, `sesiones`, `ejecuciones`, `asistencias` | X | X |
| G6 | **F5 · Partidas y Análisis** | `partidas`, `analisis_tecnico`, `estadisticas_fase` | X | X |
| G7 | **F6 · Aperturas** | `aperturas_repertorio`, `estadisticas_apertura`, `estadisticas_torneo` | X | X |
| G8 | **F7 · Patrones de Error** | `analisis_patrones`, `patrones_detectados` | X | X |
| G9 | **F8 · Indicadores y Dashboards** | `indicadores`, `alertas`, vistas de dashboards | X | X |
| G10 | **F9 · Evaluaciones** | `evaluaciones_atleta` | X | X |
| G11 | **F10 · Auditoría** | `registros_auditoria` | X | X |

> **Semana 1** = esquema + constraints + migración + seed de datos de prueba. **Semana 2** = vistas + filtros + índices.

---

## F0 · Núcleo y Catálogos (transversal — Grupo 1)

| ID | Historia | Sem. | Prio. | Criterios de aceptación |
|---|---|---|---|---|
| H-DB-00-01 | Como coordinador, quiero la **base de datos creada** (motor dev: SQLite; prod: PostgreSQL) con configuración y charset definidos. | 1 | Alta | BD accesible; parámetros documentados. |
| H-DB-00-02 | Como desarrollador, quiero el **sistema de migraciones (Alembic)** configurado y la **migración base**. | 1 | Alta | `alembic upgrade head` / `downgrade` funcionan. |
| H-DB-00-03 | Como sistema, quiero los **catálogos configurables**: categorías (EDAD/NIVEL/ELO con rangos, RF-02.5) y **rangos de evaluación** (RNF-07.2). | 1 | Alta | Catálogos poblados con valores por defecto del dominio; editables por admin. |
| H-DB-00-04 | Como administrador, quiero **datos maestros** (seed global): 1 entrenador, atletas, datos base comunes. | 1 | Alta | Seed reproducible; coherente con los seeds de los demás grupos. |
| H-DB-00-05 | Como backend, quiero **convenciones y utilidades compartidas** (nombres de tablas `snake_case`, PK `id`, FK `*_id`, timestamps). | 1 | Alta | Convenciones documentadas y usadas por todos los grupos. |

## F1 · Usuarios y Permisos (RF-01 — Grupo 2)

| ID | Historia | Sem. | Prio. | Criterios de aceptación |
|---|---|---|---|---|
| H-DB-01-01 | Como sistema, quiero la tabla **`usuarios`** (id, correo, hash_contrasena, rol, fecha_creacion) para persistir identidades. | 1 | Alta | Campos y tipos correctos; **correo único**. |
| H-DB-01-02 | Como sistema, quiero **constraints** de usuarios: correo con formato válido, rol ∈ (ENTRENADOR, ATLETA, INVITADO), contraseña ≥ 8 caracteres. | 1 | Alta | Inserciones inválidas rechazadas por la BD. |
| H-DB-01-03 | Como entrenador, quiero una **vista de usuarios** (perfil y listado por rol) para la gestión. | 2 | Alta | Vista devuelve datos legibles; filtro por rol. |
| H-DB-01-04 | Como backend, quiero **consultas/filtros** de usuarios: buscar por correo, por id, listar todos, verificar existencia. | 2 | Alta | Consultas implementadas para `RepositorioUsuarios`. |
| H-DB-01-05 | Como sistema, quiero **seed de usuarios de prueba** (1 entrenador admin, ≥ 2 atletas, 1 invitado). | 1 | Alta | Seed coherente con F2 (atletas) y F0. |

## F2 · Atletas y Categorías (RF-02 — Grupo 3)

| ID | Historia | Sem. | Prio. | Criterios de aceptación |
|---|---|---|---|---|
| H-DB-02-01 | Como sistema, quiero la tabla **`atletas`** con campos del RF-02.1 (nombre, fecha_nacimiento, sexo, identidad, fotografia, federacion, universidad, carrera, activo). | 1 | Alta | Obligatorios NOT NULL (nombre, fecha_nacimiento, sexo); edad **calculada**, no almacenada. |
| H-DB-02-02 | Como sistema, quiero la tabla **`ratings`** 1:1 con atletas (clasicas, rapidas, blitz, chess_com, lichess, fecha_actualizacion). | 1 | Alta | Ratings obligatorios (RF-02.2); **≥ 0**; FK a `atletas`. |
| H-DB-02-03 | Como sistema, quiero la tabla **`categorias`** con relación **N:M atleta–categoría** y la tabla **`clubs`** con relación **N:M atleta–club**. | 1 | Alta | Categorías predefinidas + personalizadas; múltiples categorías y clubs por atleta (RF-02.4). |
| H-DB-02-04 | Como sistema, quiero la tabla **`perfil_historico`** (anio, torneo, snapshot de rating) **inmutable** por año/torneo (RF-02.7). | 1 | Alta | Sin UPDATE/DELETE sobre históricos; único por (id_atleta, anio, torneo). |
| H-DB-02-05 | Como backend, quiero **vistas**: expediente completo con edad, historial de ratings, atletas por categoría. | 2 | Alta | Vista con `edad` calculada; historial ordenado por año. |
| H-DB-02-06 | Como entrenador, quiero **filtros/consultas**: atletas por entrenador, por categoría, por rango de rating, activos/inactivos. | 2 | Alta | Consultas listas para `RepositorioAtletas`. |
| H-DB-02-07 | Como sistema, quiero **seed de atletas de prueba** con ratings, categorías e historial. | 1 | Alta | ≥ 5 atletas coherentes con F1, F3–F8. |

## F3 · Objetivos SMART (RF-03 — Grupo 4)

| ID | Historia | Sem. | Prio. | Criterios de aceptación |
|---|---|---|---|---|
| H-DB-03-01 | Como sistema, quiero la tabla **`objetivos`** (id_atleta, descripcion, indicador_meta, valor_meta, rating_actual, rating_meta, fecha_inicio, fecha_limite, porcentaje_avance, estado, aprobado_por_entrenador). | 1 | Alta | Fechas **obligatorias** (RF-03.3); FK a `atletas`; estado ∈ PENDIENTE_APROBACION/EN_PROCESO/RETRASADO/FINALIZADO. |
| H-DB-03-02 | Como sistema, quiero la tabla **`indicadores_avance`** (tipo, valor_actual, valor_esperado) por objetivo. | 1 | Alta | Tipo ∈ HORAS_ENTRENADAS/RATING/TAREAS/TORNEOS/MEDALLAS. |
| H-DB-03-03 | Como backend, quiero **vistas**: semáforo de objetivos por atleta, objetivos pendientes de aprobación, retrasados. | 2 | Alta | Vista calcula el semáforo según reglas del dominio (RF-03.4/03.8). |
| H-DB-03-04 | Como usuario, quiero **filtros**: objetivos por atleta, por estado, por rango de fechas. | 2 | Alta | Consultas para `RepositorioObjetivos`. |
| H-DB-03-05 | Como sistema, quiero **seed de objetivos de prueba** (todos los estados). | 1 | Alta | Objetivos coherentes con atletas de F2. |

## F4 · Entrenamientos y Asistencia (RF-04 — Grupo 5)

| ID | Historia | Sem. | Prio. | Criterios de aceptación |
|---|---|---|---|---|
| H-DB-04-01 | Como sistema, quiero la tabla **`planes_semanales`** (id_atleta, semana, anio) con unicidad por (id_atleta, semana, anio). | 1 | Alta | Un plan por atleta/semana; FK a `atletas`. |
| H-DB-04-02 | Como sistema, quiero la tabla **`sesiones`** (id_plan, tipo, dia_semana, horas_planificadas, estado, observaciones). | 1 | Alta | Tipo ∈ 12 tipos (RF-04.1); estado ∈ PROGRAMADA/REPROGRAMADA/CANCELADA/EJECUTADA; horas > 0. |
| H-DB-04-03 | Como sistema, quiero la tabla **`ejecuciones`** (id_sesion, horas_ejecutadas, fecha_registro, registrado_por_atleta, aprobado_por_entrenador, incidencias, tareas). | 1 | Alta | Una ejecución por sesión; FK; historial conservado (RF-04.6); registro rápido diario con incidencias y tareas (RNF-01.1). |
| H-DB-04-04 | Como sistema, quiero la tabla **`asistencias`** (id_atleta, id_sesion, fecha, estado). | 1 | Alta | Estado ∈ PRESENTE/AUSENTE/JUSTIFICADO; único por (id_atleta, id_sesion). |
| H-DB-04-05 | Como backend, quiero **vistas**: cumplimiento semanal (planificado vs ejecutado aprobado + %), asistencia por sesión. | 2 | Alta | % = ejecutadas aprobadas / planificadas × 100 (RF-04.4). |
| H-DB-04-06 | Como usuario, quiero **filtros**: planes por semana/año, sesiones por tipo/estado, historial por atleta. | 2 | Alta | Consultas para `RepositorioEntrenamientos` y `RepositorioAsistencia`. |
| H-DB-04-07 | Como sistema, quiero **seed** de planes, sesiones, ejecuciones y asistencias. | 1 | Alta | 3–4 semanas de datos coherentes con F2. |

## F5 · Partidas y Análisis Técnico (RF-05 / RF-07 — Grupo 6)

| ID | Historia | Sem. | Prio. | Criterios de aceptación |
|---|---|---|---|---|
| H-DB-05-01 | Como sistema, quiero la tabla **`partidas`** (id_atleta, evento, fecha, jugador_blancas, jugador_negras, rating_blancas, rating_negras, resultado, apertura_eco, control_tiempo, color_atleta, fuente). | 1 | Alta | Obligatorios del RF-05.1; resultado ∈ victoria/derrota/tablas; FK a `atletas`. |
| H-DB-05-02 | Como sistema, quiero la tabla **`analisis_tecnico`** 1:1 (accuracy, acpl, blunders, errores, imprecisiones, brilliant_moves, excelente, buena, libro, tiempo_promedio_jugada, perdidas_tiempo). | 1 | Alta | Métricas del RF-05.5; accuracy 0–100; **solo resumen** (RF-05.4). |
| H-DB-05-03 | Como sistema, quiero la tabla **`estadisticas_fase`** (apertura: exito/errores/tiempo; medio_juego: precision/errores; finales: conversion/tablas_salvadas/errores). | 1 | Alta | Estructura por fases del RF-07. |
| H-DB-05-04 | Como backend, quiero **vistas**: estadísticas por fase, distribución por clasificación (botada/excelente/buena/libro), resultados por color. | 2 | Alta | Vistas agregadas listas para dashboards. |
| H-DB-05-05 | Como usuario, quiero **filtros**: partidas por torneo/evento, por periodo, por color, por resultado. | 2 | Alta | Consultas para `RepositorioPartidas` y `RepositorioAnalisisTecnico`. |
| H-DB-05-06 | Como sistema, quiero **seed** de partidas con análisis y estadísticas por fase. | 1 | Alta | ≥ 10 partidas coherentes con F2 y F6. |

## F6 · Aperturas (RF-08 — Grupo 7)

| ID | Historia | Sem. | Prio. | Criterios de aceptación |
|---|---|---|---|---|
| H-DB-06-01 | Como sistema, quiero la tabla **`aperturas_repertorio`** (id_atleta, codigo_eco, nombre, variante, color, estado, nivel_dominio, fuente_estudio, observaciones, clasificacion_uso). | 1 | Alta | Color ∈ BLANCAS/NEGRAS/AMBOS; estado ∈ EN_ESTUDIO/ACTIVA/EN_REVISION/DESCARTADA; único por (id_atleta, codigo_eco, color, variante). |
| H-DB-06-02 | Como sistema, quiero la tabla **`estadisticas_apertura`** (partidas_jugadas, victorias, empates, derrotas, accuracy_promedio, acpl_promedio, errores_frecuentes, evaluacion_motor, tiempo_promedio). | 1 | Alta | FK a apertura; consistentes (suma resultados = partidas); incluye evaluación con motor y tiempo promedio (RF-08.4). |
| H-DB-06-03 | Como sistema, quiero la tabla **`estadisticas_apertura_torneo`** (anio, control_tiempo, color, nivel_rival, rival_especifico). | 2 | Alta | Filtros del RF-08.5; FK a apertura. |
| H-DB-06-04 | Como backend, quiero **vistas**: efectividad por apertura (MUY_EFECTIVA…REQUIERE_REVISION), mejores/peores aperturas del atleta. | 2 | Alta | Nivel calculado según desempeño del atleta (RF-08.6). |
| H-DB-06-05 | Como usuario, quiero **filtros**: aperturas por color, por estado, estadísticas por torneo. | 2 | Alta | Consultas para `RepositorioAperturas`. |
| H-DB-06-06 | Como sistema, quiero **seed** de aperturas con estadísticas. | 1 | Alta | Coherente con partidas de F5. |

## F7 · Patrones de Error (RF-06 — Grupo 8)

| ID | Historia | Sem. | Prio. | Criterios de aceptación |
|---|---|---|---|---|
| H-DB-07-01 | Como sistema, quiero la tabla **`analisis_patrones`** (id_atleta, fecha_inicio, fecha_fin, total_partidas_analizadas). | 1 | Alta | FK a `atletas`; periodo válido. |
| H-DB-07-02 | Como sistema, quiero la tabla **`patrones_detectados`** (id_analisis, tipo, descripcion, frecuencia_absoluta, frecuencia_relativa, nivel_confianza). | 1 | Alta | Tipo ∈ 7 tipos (RF-06.1–06.7); sin sugerencias automáticas (RF-06.10). |
| H-DB-07-03 | Como backend, quiero **vistas**: patrones por atleta/periodo, frecuencia relativa, partidas afectadas. | 2 | Alta | Vistas agregan frecuencias para el dashboard. |
| H-DB-07-04 | Como usuario, quiero **filtros**: patrones por tipo, por nivel de confianza, por periodo. | 2 | Alta | Consultas para `RepositorioPatrones`. |
| H-DB-07-05 | Como sistema, quiero **seed** de análisis y patrones de prueba. | 1 | Alta | Coherente con partidas de F5. |

## F8 · Indicadores y Dashboards (RF-09 / RF-11 — Grupo 9)

| ID | Historia | Sem. | Prio. | Criterios de aceptación |
|---|---|---|---|---|
| H-DB-08-01 | Como sistema, quiero la tabla **`indicadores`** (id_atleta, tipo, valor, rango_evaluacion, periodo). | 1 | Alta | Tipo ∈ 15 indicadores (RF-09); rango ∈ EXCELENTE/BUENO/ACEPTABLE/REQUIERE_INTERVENCION. |
| H-DB-08-02 | Como sistema, quiero la tabla **`alertas`** (tipo, id_atleta, fecha_generacion, atendida). | 1 | Alta | Tipo ∈ BAJA_ASISTENCIA/OBJETIVO_VENCIDO/DISMINUCION_RENDIMIENTO; FK a `atletas`. |
| H-DB-08-03 | Como backend, quiero **vistas de dashboards**: KPIs del atleta siempre visibles, evolución de rating grupal, cumplimiento del plan, objetivos pendientes, alertas activas, comparación con el grupo. | 2 | Alta | Vistas agregadas (RF-11.1/11.2/11.3) listas para consulta < 3 s (RNF-01.4); comparación con promedio del grupo y ranking (RF-09.5). |
| H-DB-08-04 | Como usuario, quiero **filtros**: indicadores por periodo, por tipo, por rango de evaluación. | 2 | Alta | Consultas para `RepositorioIndicadores` y `ProveedorDatosRendimiento`. |
| H-DB-08-05 | Como sistema, quiero **seed** de indicadores y alertas. | 1 | Alta | Coherente con los datos de F2–F7. |

## F9 · Evaluaciones (RF-10 — Grupo 10)

| ID | Historia | Sem. | Prio. | Criterios de aceptación |
|---|---|---|---|---|
| H-DB-09-01 | Como sistema, quiero la tabla **`evaluaciones_atleta`** (id_atleta, fecha, periodo_tipo, periodo_nombre, calificaciones de los 8 indicadores, fortalezas, aspectos_mejorar, recomendaciones, es_autoevaluacion, completa). | 1 | Alta | FK a `atletas`; periodo_tipo ∈ TORNEO/MES/MESOCICLO/ANIO; 8 indicadores del RF-10.2. |
| H-DB-09-02 | Como sistema, quiero **constraints**: calificaciones entre **1 y 10** (RF-10.4); entrenador obligatoria, autoevaluación opcional (RF-10.3). | 1 | Alta | Inserciones fuera de rango rechazadas. |
| H-DB-09-03 | Como backend, quiero **vistas**: historial de evaluaciones por atleta, promedio de calificaciones. | 2 | Alta | Promedio calculado por periodo. |
| H-DB-09-04 | Como usuario, quiero **filtros**: evaluaciones por atleta, por periodo_tipo, por rango de fechas. | 2 | Alta | Consultas para `RepositorioEvaluaciones`. |
| H-DB-09-05 | Como sistema, quiero **seed** de evaluaciones de prueba. | 1 | Alta | Coherente con F2. |

## F10 · Auditoría (RF-12 — Grupo 11)

| ID | Historia | Sem. | Prio. | Criterios de aceptación |
|---|---|---|---|---|
| H-DB-10-01 | Como sistema, quiero la tabla **`registros_auditoria`** (usuario, fecha_hora, entidad_afectada, campo_modificado, valor_anterior, valor_nuevo, tipo_operacion). | 1 | Alta | Tipo ∈ CREAR/MODIFICAR/ELIMINAR; **inmutable**. |
| H-DB-10-02 | Como sistema, quiero **reglas de inmutabilidad**: sin UPDATE/DELETE sobre registros de auditoría ni históricos (RF-12, RNF-04.2). | 1 | Alta | Intentos de modificación rechazados por la BD (triggers/permisos). |
| H-DB-10-03 | Como backend, quiero **vistas**: trail de auditoría por entidad, por usuario, por fecha. | 2 | Alta | Vista de historial con al menos un filtro obligatorio (RF-12). |
| H-DB-10-04 | Como usuario, quiero **filtros**: auditoría por entidad_afectada, por usuario, por rango de fechas, por tipo_operacion. | 2 | Alta | Consultas para `RepositorioAuditoria`. |
| H-DB-10-05 | Como sistema, quiero **seed** de registros de auditoría de prueba. | 1 | Alta | Registros que reflejen las operaciones de los demás seeds. |

---

## Orden recomendado de integración (dependencias entre grupos)

1. **F0 (G1)** primero: motor, migraciones base y catálogos — todos dependen de sus convenciones.
2. **F1 (G2)** y **F2 (G3)** en paralelo: identidad y expediente (F2 es FK de casi todo).
3. **F3–F8 (G4–G9)** en paralelo después de F1/F2: objetivos, entrenamientos, partidas, aperturas, patrones, indicadores.
4. **F9 (G10)** y **F10 (G11)** pueden ir en paralelo desde el inicio; F10 registra operaciones de todos.
5. **Integración diaria** al esquema común; los conflictos de FK se resuelven en el daily con el coordinador.
