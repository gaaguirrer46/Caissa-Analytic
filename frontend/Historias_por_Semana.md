# Historias por Semana — Frontend (Interfaz Visual)

> Historias de usuario de la capa de **presentación**, organizadas por semana según el `Calendario_Scrumban.md` de esta carpeta.
> **Formato:** `H-F-XX | Historia | Prioridad | Criterios de aceptación`.

---

## Semana 1 · Fundación visual

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-F-01 | Como desarrollador, quiero el **setup de la SPA** (estructura, routing, HTTP client) para empezar a construir. | Alta | Proyecto arranca; ruteo base funcional. |
| H-F-02 | Como usuario, quiero un **design system** consistente (paleta, tipografía, componentes base, semáforos). | Alta | Componentes reutilizables; semáforos verde/amarillo/rojo (RNF-03.3). |
| H-F-03 | Como usuario, quiero un **layout maestro** (sidebar + header) navegable. | Alta | Navegación por módulos; responsive base. |

## Semana 2 · Identidad y sesión

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-F-04 | Como usuario, quiero **iniciar sesión** y **registrarme** desde la UI. | Alta | Login/registro funcionales contra la API; errores visibles. |
| H-F-05 | Como usuario, quiero que mi **sesión se mantenga** con token y se cierre al expirar. | Alta | Token gestionado de forma segura; redirección a login al expirar. |
| H-F-06 | Como sistema, quiero **guardas de ruta por rol** (ENTRENADOR/ATLETA/INVITADO). | Alta | Atleta no accede a rutas de entrenador (RF-01.6). |

## Semana 3 · Atletas

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-F-07 | Como entrenador, quiero **listar atletas** con búsqueda y filtros. | Alta | Listado con filtros por categoría/entrenador; paginación. |
| H-F-08 | Como entrenador, quiero ver el **perfil completo** con edad calculada y ratings. | Alta | Edad automática visible (RF-02.3); ratings por plataforma. |
| H-F-09 | Como entrenador, quiero **formularios de alta/edición** con validaciones. | Alta | Obligatorios validados (RF-02.2); errores del servidor mostrados. |

## Semana 4 · Objetivos SMART

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-F-10 | Como atleta/entrenador, quiero **crear y listar objetivos** SMART. | Alta | CRUD; fechas obligatorias (RF-03.3). |
| H-F-11 | Como usuario, quiero ver el **semáforo** y el **porcentaje de avance** de cada objetivo. | Alta | Estados verde/amarillo/rojo correctos (RF-03.4). |
| H-F-12 | Como entrenador, quiero **aprobar** objetivos y **validar cumplimiento**. | Alta | Flujo de aprobación; solo entrenador valida (RF-03.7). |

## Semana 5 · Entrenamientos

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-F-13 | Como entrenador, quiero **planificar la semana** con sesiones y horas. | Alta | Vista por semana (RF-04.5); edición de sesiones. |
| H-F-14 | Como atleta, quiero **registrar horas ejecutadas**; como entrenador **aprobarlas**. | Alta | Reporte y aprobación; horas no aprobadas no cuentan. |
| H-F-15 | Como entrenador, quiero **registrar asistencia** y ver el **% de cumplimiento** semanal. | Alta | Asistencia post-sesión; % visible (RF-04.8). |

## Semana 6 · Partidas y análisis

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-F-16 | Como entrenador, quiero **registrar partidas** con sus datos. | Alta | Obligatorios validados (RF-05.1). |
| H-F-17 | Como entrenador, quiero **completar el análisis técnico** y ver la **clasificación** de la partida. | Alta | Métricas de RF-05.5; clasificación visual (botada/excelente/buena/libro). |
| H-F-18 | Como entrenador, quiero **importar PGN** desde la interfaz. | Media | Subida de archivo; resultado informado; errores claros. |

## Semana 7 · Aperturas y patrones

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-F-19 | Como entrenador, quiero **gestionar el repertorio de aperturas** (ECO, color, estado, efectividad). | Alta | Registro por color independiente (RF-08.2); niveles de efectividad. |
| H-F-20 | Como entrenador, quiero **visualizar patrones de error** por periodo con frecuencias. | Media | Patrones con mínimos de partidas (RF-06.9); solo estadísticas (RF-06.10). |

## Semana 8 · Dashboards

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-F-21 | Como entrenador, quiero el **dashboard del equipo** (estado, alertas, cumplimiento, rating grupal). | Alta | Alertas destacadas (RF-11.1); datos en tiempo real. |
| H-F-22 | Como atleta, quiero mi **dashboard personal** con KPIs, semáforos y comparación mensual. | Alta | KPIs de RF-11.2; comparación mes actual vs anterior. |
| H-F-23 | Como usuario, quiero **gráficos interactivos** de tendencias. | Alta | Gráficos de evolución de rating, accuracy, horas de entrenamiento, rendimiento por torneo, distribución de resultados, comparación entre atletas e Índice Global de Rendimiento (RF-11.8). |

## Semana 9 · Reportes

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-F-24 | Como entrenador, quiero **exportar reportes** en PDF y Excel desde la UI. | Alta | Descarga de archivos generados por la API (RF-11.5–11.7). |
| H-F-25 | Como entrenador, quiero ver el **Informe Integral del Atleta** con sus 8 secciones. | Alta | 8 secciones visibles (RF-11.10). |

## Semana 10 · Evaluación y auditoría

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-F-26 | Como entrenador, quiero **crear evaluaciones** (1–10) con fortalezas, mejoras y recomendaciones. | Media | Escala validada (RF-10.4); autoevaluación opcional (RF-10.3). |
| H-F-27 | Como entrenador, quiero consultar el **historial de auditoría** con filtros. | Media | Al menos un filtro obligatorio (RF-12). |

## Semana 11 · Calidad integral

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-F-28 | Como usuario, quiero una interfaz **responsive y accesible** (teclado, contraste). | Alta | Uso correcto en móvil/escritorio; navegación por teclado. |
| H-F-29 | Como equipo, quiero **pruebas E2E** de los flujos principales. | Alta | Flujos en verde (login→atleta→objetivo→entrenamiento→partida→reporte). |

## Semana 12 · Release visual

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-F-30 | Como usuario, quiero una interfaz **pulida** con micro-interacciones y rendimiento optimizado. | Alta | Carga inicial < 2 s; sin errores de consola. |
| H-F-31 | Como equipo, quiero una **release candidate** navegable en los 3 roles y la retro con métricas. | Alta | RC estable; demo final; métricas reportadas. |
