# Historias por Semana — Adaptadores Primarios (Web API + CLI)

> Historias de usuario del lado **driving** (entrada), organizadas por semana según el `Calendario_Scrumban.md` de esta carpeta.
> **Formato:** `H-P-XX | Historia | Prioridad | Criterios de aceptación`.

---

## Semana 1 · Fundación

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-P-01 | Como desarrollador, quiero un **repositorio ejecutable** con la estructura de `adaptadores/primarios/{web,cli}`, para empezar a construir la API. | Alta | Estructura creada; dependencias declaradas (FastAPI, Uvicorn, Pydantic, httpx, pytest); instala sin errores. |
| H-P-02 | Como operador, quiero un endpoint `GET /health` para verificar que la API está viva. | Alta | Responde 200 con estado `ok`. |
| H-P-03 | Como equipo, quiero un **CI** (lint + compileall + pytest) para validar cada cambio. | Alta | El pipeline pasa en cada push; bloquea merge si falla. |
| H-P-04 | Como desarrollador, quiero un **README técnico** de la carpeta para incorporar a nuevos miembros. | Media | Documenta arranque, estructura y comandos. |

## Semana 2 · Esqueleto de API + CLI

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-P-05 | Como desarrollador, quiero **routers por módulo** (usuarios, atletas, objetivos…) para organizar los endpoints. | Alta | Un router por módulo registrado en la app; visible en `/docs`. |
| H-P-06 | Como desarrollador, quiero **schemas Pydantic** (DTOs) de entrada/salida para validar el contrato de la API. | Alta | Schemas para los módulos base; errores de validación → 422/400 claros. |
| H-P-07 | Como desarrollador, quiero un **manejo global de errores** que traduzca `ErrorDeDominio` a HTTP. | Alta | `ErrorValidacion`→400, `ErrorAutenticacion`→401, `EntidadNoEncontrada`→404, resto→500. |
| H-P-08 | Como operador, quiero un **CLI base** con `--help` para preparar futuros comandos. | Media | `--help` lista subcomandos; comando de prueba funciona. |

## Semana 3 · Usuarios y sesión

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-P-09 | Como entrenador, quiero **crear usuarios** con rol asignado para dar acceso al sistema. | Alta | Correo inválido o contraseña < 8 → 400; segundo ENTRENADOR → 400 (RF-01.8). |
| H-P-10 | Como usuario, quiero **iniciar sesión** con correo y contraseña para obtener mi token. | Alta | Credenciales válidas → token; inválidas → 401. |
| H-P-11 | Como usuario, quiero consultar **mi perfil** (`/usuarios/me`) con mi token. | Alta | Devuelve perfil; sin token → 401. |
| H-P-12 | Como sistema, quiero **verificar permisos** de una acción por rol para autorizar peticiones. | Alta | INVITADO no puede `GESTIONAR_ATLETAS`; ENTRENADOR sí. |

## Semana 4 · Atletas

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-P-13 | Como entrenador, quiero **dar de alta un atleta** con su expediente completo. | Alta | Campos obligatorios validados (RF-02.2); registra con id generado. |
| H-P-14 | Como entrenador, quiero **consultar el perfil** con la **edad calculada** automáticamente. | Alta | Perfil devuelve `edad` correcta (RF-02.3). |
| H-P-15 | Como entrenador, quiero **asignar categorías** al atleta. | Media | Asigna una o varias; categoría inexistente → 404. |
| H-P-16 | Como entrenador, quiero **asignar 1–3 entrenadores** y **actualizar ratings**. | Alta | 0 o 4 entrenadores → 400 (RF-02.6); ratings actualizados con snapshot histórico (RF-02.7). |

## Semana 5 · Objetivos SMART

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-P-17 | Como entrenador/atleta, quiero **proponer un objetivo SMART** que quede pendiente de aprobación. | Alta | Sin fecha inicio/límite → 400 (RF-03.3); queda PENDIENTE_APROBACION. |
| H-P-18 | Como entrenador, quiero **aprobar objetivos** propuestos para activarlos. | Alta | Solo ENTRENADOR aprueba; atleta → 403. |
| H-P-19 | Como sistema, quiero **calcular el avance** y **evaluar el estado** (semáforo) de cada objetivo. | Alta | Avance % correcto; RETRASADO si real < esperado (RF-03.8). |
| H-P-20 | Como usuario, quiero **listar objetivos por filtros** (estado, fechas, tipo) y **validar cumplimiento**. | Alta | Filtros funcionan; solo entrenador marca cumplido (RF-03.7). |

## Semana 6 · Entrenamientos

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-P-21 | Como entrenador, quiero **planificar la semana** con sesiones y horas. | Alta | Plan por semana/año; valida tipos y horas. |
| H-P-22 | Como entrenador, quiero **reprogramar una sesión** conservando el historial. | Media | Cambio de fecha/hora; historial original conservado (RF-04.6). |
| H-P-23 | Como atleta, quiero **registrar horas ejecutadas** y como entrenador **aprobarlas**. | Alta | Atleta reporta; entrenador aprueba; sin aprobación no cuenta. |
| H-P-24 | Como usuario, quiero consultar el **% de cumplimiento semanal** y **registrar asistencia**. | Alta | % = ejecutadas aprobadas / planificadas × 100; asistencia post-sesión (PRESENTE/AUSENTE/JUSTIFICADO). |

## Semana 7 · Partidas y análisis

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-P-25 | Como entrenador, quiero **registrar una partida** con datos obligatorios. | Alta | Evento, fecha, jugadores, ratings, resultado, apertura obligatorios (RF-05.1). |
| H-P-26 | Como entrenador, quiero **completar el análisis técnico** de una partida. | Alta | Métricas de RF-05.5 almacenadas como resumen. |
| H-P-27 | Como sistema, quiero **clasificar la partida** según reglas del dominio. | Alta | Botada = ventaja > +3 + pérdida/empate por blunder; Excelente = accuracy ≥ 85 sin blunders; respeta color del atleta. |
| H-P-28 | Como entrenador, quiero **importar una partida desde PGN**. | Media | Sube PGN → crea partida (+ resumen si aplica); PGN inválido → error controlado. |

## Semana 8 · Aperturas y patrones

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-P-29 | Como entrenador, quiero **registrar aperturas** del repertorio del atleta. | Alta | Registro por color independiente (RF-08.2); campos del RF-08.1. |
| H-P-30 | Como entrenador, quiero **clasificar principal/secundaria** y ver la **efectividad** de cada apertura. | Alta | Niveles MUY_EFECTIVA/EFECTIVA/EN_DESARROLLO/REQUIERE_REVISION según desempeño del atleta. |
| H-P-31 | Como sistema, quiero **detectar patrones de error** por periodo. | Media | Patrón solo si ≥ 5 partidas o > 40 % (RF-06.8); mínimos por tipo (RF-06.9); sin sugerencias automáticas (RF-06.10). |

## Semana 9 · Analítica y reportes

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-P-32 | Como sistema, quiero **calcular indicadores** principales y secundarios. | Alta | Rating, accuracy, ACPL, cumplimientos, blunders, etc. (RF-09.1/09.2). |
| H-P-33 | Como entrenador, quiero ver el **dashboard del equipo** y como atleta mi **dashboard personal**. | Alta | Alertas automáticas (RF-09/RF-11); semáforos y comparación mensual. |
| H-P-34 | Como entrenador, quiero **comparar tendencias** y **generar reportes** PDF/Excel. | Alta | Mes/mes, torneo/torneo, año/año, rangos personalizados (RF-11.4); informes semanal, mensual y al finalizar torneo (RF-13.7); archivo generado vía `ServicioGeneracionReportes`. |
| H-P-35 | Como entrenador, quiero gestionar **evaluaciones** (1–10) y consultar **auditoría** con filtros. | Media | Calificación fuera de 1–10 → 400; historial exige al menos un filtro (RF-12). |

## Semana 10 · CLI operativo

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-P-36 | Como operador, quiero un comando de **seed** para poblar datos de prueba. | Alta | Puebla usuarios, atletas, planes, partidas; reproducible. |
| H-P-37 | Como operador, quiero **importar PGN en lote** por consola. | Media | Procesa archivos; reporta errores por archivo sin detener el lote. |
| H-P-38 | Como operador, quiero **generar reportes** y **consultas rápidas** desde el CLI. | Media | Salida legible (tablas/JSON); `--help` en cada comando. |

## Semana 11 · Calidad E2E

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-P-39 | Como equipo, quiero un **flujo E2E completo** (login→atleta→objetivo→entrenamiento→partida→reporte). | Alta | Flujo verde de punta a punta. |
| H-P-40 | Como equipo, quiero pruebas de **RBAC** que verifiquen que el atleta no ve datos ajenos. | Alta | Acceso cruzado → 403 (RF-01.6). |
| H-P-41 | Como equipo, quiero **pruebas de carga** básicas. | Media | p95 de consultas < 3 s (RNF-01.4). |

## Semana 12 · Cierre y release

| ID | Historia | Prioridad | Criterios de aceptación |
|---|---|---|---|
| H-P-42 | Como consumidor de la API, quiero un **OpenAPI pulido** y documentado. | Alta | `/docs` completo con descripciones y ejemplos. |
| H-P-43 | Como operador, quiero **hardening de entrada**: validación estricta, rate limiting, CORS. | Alta | Respuestas y config verificadas. |
| H-P-44 | Como equipo, quiero una **release candidate** desplegable y demo final. | Alta | RC estable; demo realizada; métricas scrumban reportadas. |
