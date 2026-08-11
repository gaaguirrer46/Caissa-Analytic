# Se Caissa Analytics — Documentación del Dominio

Sistema de medición del rendimiento deportivo en ajedrez para la toma de decisiones del entrenador.

Este documento explica cómo funciona la **capa de dominio** del proyecto: su arquitectura, los módulos que la componen, sus entidades, puertos y casos de uso, y cómo usarla y extenderla.

---

## 1. ¿Qué es el dominio?

La carpeta `dominio/` es el **núcleo de negocio** de Se Caissa Analytics. Contiene toda la lógica de la aplicación sin depender de tecnología concreta:

- **No conoce** bases de datos, frameworks web, APIs externas, autenticación concreta (JWT, OAuth) ni generadores de PDF/Excel.
- **No sabe** nada de `FastAPI`, `SQLAlchemy`, `Stockfish`, `Chess.com` o `Lichess`.

Esa separación es la base de la **arquitectura hexagonal** (puertos y adaptadores): el dominio define *qué* debe hacer el sistema (reglas de negocio) y los adaptadores definen *cómo* se hace en la práctica (persistencia, web, archivos).

```
┌─────────────────────────────────────────────────────────────┐
│  ADAPTADORES PRIMARIOS (driving)   →  Web (FastAPI), CLI     │
└──────────────────────────┬──────────────────────────────────┘
                           │ casos de uso
┌──────────────────────────▼──────────────────────────────────┐
│                    DOMINIO  (este paquete)                   │
│   entidades + puertos + casos de uso + reglas de negocio    │
└──────────────────────────┬──────────────────────────────────┘
                           │ puertos (interfaces)
┌──────────────────────────▼──────────────────────────────────┐
│  ADAPTADORES SECUNDARIOS (driven) → BD, PGN, motor, PDF...   │
└─────────────────────────────────────────────────────────────┘
```

Todo lo concreto (SQLite/PostgreSQL, endpoints REST, parser PGN, generación de reportes) se implementará **fuera** del dominio, como adaptadores que cumplen las interfaces definidas aquí.

---

## 2. Estructura de carpetas

```
dominio/
├── __init__.py              # Docstring del paquete (dominio puro)
├── comun/                   # Utilidades compartidas
│   ├── errores.py           #   Errores de dominio
│   ├── constantes.py        #   Límites operativos (RF-01.8, RF-02.6)
│   ├── reglas_limites.py    #   Validaciones de límites compartidas
│   └── ids.py               #   Generación de ids
├── usuarios/                # RF-01  Gestión de usuarios y permisos
│   ├── entidades.py         #   Usuario, Rol, Permiso
│   ├── puertos.py           #   RepositorioUsuarios, ServicioHashContrasenas, PermisosPorRol
│   └── casos_de_uso.py      #   AutenticarUsuario, CrearUsuario, ...
├── atletas/                 # RF-02  Gestión de atletas
├── objetivos/               # RF-03  Objetivos SMART
├── entrenamientos/          # RF-04  Planificación y registro de entrenamientos
├── partidas/                # RF-05, RF-07  Partidas y análisis técnico
├── patrones/                # RF-06  Detección de patrones de error
├── aperturas/               # RF-08  Repertorio de aperturas
├── indicadores/             # RF-09, RF-11  Indicadores, dashboards e informes
├── evaluaciones/            # RF-10  Evaluación del entrenador
└── auditoria/               # RF-12  Auditoría y control de cambios
```

Cada módulo sigue el mismo patrón de tres archivos:

| Archivo | Contenido |
|---|---|
| `entidades.py` | Clases que encapsulan datos y reglas invariantes (validaciones, cálculos, estados). |
| `puertos.py` | **Puertos secundarios (driven)**: interfaces abstractas (ABC) que implementarán los adaptadores de infraestructura. |
| `casos_de_uso.py` | **Puertos primarios (driving)**: clases que orquestan el flujo de negocio. |

---

## 3. Convenciones del código

### 3.1 Errores de dominio (`comun/errores.py`)

Todas las violaciones de reglas de negocio lanzan una excepción de dominio. Los adaptadores pueden capturarlas para traducirlas a respuestas HTTP u otra salida.

| Excepción | Cuándo ocurre |
|---|---|
| `ErrorDeDominio` | Base de todas las demás. |
| `ErrorValidacion` | Violación de una regla de negocio o validación. |
| `ErrorAutenticacion` | Credenciales o autorización incorrectas. |
| `EntidadNoEncontrada` | Se busca una entidad que no existe. |

### 3.2 Constantes y reglas compartidas (`comun/`)

- `constantes.py` — límites operativos: máximo **40 atletas por entrenador** (RF-01.8) y **1 a 3 entrenadores por atleta** (RF-02.6).
- `reglas_limites.py` — `validar_capacidad_entrenador(cantidad)` y `validar_entrenadores_por_atleta(cantidad)`, usadas por los módulos de Usuarios y Atletas (una sola fuente, sin duplicar lógica).
- `ids.py` — `nuevo_id(prefijo="")` genera ids UUID opcionalmente prefijados (`nuevo_id("objetivo")` → `objetivo_xxxxxxxx-...`). Todos los módulos lo usan.

### 3.3 Entidades (`entidades.py`)

- Son `@dataclass` de Python.
- Encapsulan **invariantes**: por ejemplo, `Atleta.edad()` se calcula automáticamente, `Partida.puntos_obtenidos()` devuelve los puntos según el color con el que jugó el atleta, `PlanEntrenamientoSemanal.porcentaje_cumplimiento` se calcula solo.
- Las que no deben mutarse se marcan `@dataclass(frozen=True)` (p. ej. `Usuario`, `PerfilHistorico`, `RegistroAuditoria`, `TendenciaComparada`).
- Las entidades de un módulo **referencian a otras por id, nunca por objeto completo** (un `ObjetivoSmart` conoce `id_atleta`, no la instancia de `Atleta`).

### 3.4 Puertos (`puertos.py`)

- Interfaces con métodos `@abstractmethod`, declaradas sobre `ABC`.
- Nombres en español y orientados al **qué**, no al cómo: `RepositorioAtletas.guardar(atleta)`, `ServicioHashContrasenas.verificar(...)`, `ServicioGeneracionReportes.generar(reporte, ruta)`.
- Un adaptador puede implementar **varios puertos** o un puerto puede ser implementado por **varios adaptadores** (p. ej. dos repositorios: SQLite y PostgreSQL).

### 3.5 Casos de uso (`casos_de_uso.py`)

- Son `@dataclass` con las dependencias inyectadas **por constructor**.
- Tienen un único punto de entrada: el método `ejecutar(...)`.
- **Nunca instancian adaptadores**: solo usan los puertos que reciben.
- Validan primero, modifican estado después y delegan la persistencia al repositorio.

---

## 4. Flujo típico de uso

Un caso de uso se usa igual desde cualquier adaptador (API web, script, test):

```python
from dominio.atletas.entidades import Atleta, Rating
from dominio.atletas.casos_de_uso import RegistrarAtleta

# 1. El adaptador provee una implementación concreta del puerto (aquí un fake)
class RepositorioEnMemoria(RepositorioAtletas):
    def __init__(self):
        self.datos = {}
    def guardar(self, atleta):
        self.datos[atleta.id] = atleta
        return atleta
    # ... resto de métodos del ABC

repositorio = RepositorioEnMemoria()

# 2. Se instancia el caso de uso con sus dependencias
caso = RegistrarAtleta(
    repositorio_atletas=repositorio,
    repositorio_categorias=repo_categorias,
)

# 3. Se ejecuta el flujo de negocio
atleta = Atleta(
    id="atl_1",
    nombre="Ana Torres",
    fecha_nacimiento=date(2012, 5, 10),
    sexo="F",
    entrenadores_asignados=["ent_1"],
    rating_actual=Rating(clasicas=1650, rapidas=1600, blitz=1580,
                         chess_com=1700, lichess=1680),
)
atleta_registrado = caso.ejecutar(atleta)   # valida y persiste
```

Si se viola una regla (p. ej. faltan ratings obligatorios), se lanza `ErrorValidacion`.

---

## 5. Módulos del dominio

### 5.1 Usuarios y Permisos — RF-01

**Responsabilidad:** gestionar identidad, roles y permisos del sistema.

- **Entidades:** `Usuario` (id, correo, hash_contraseña, rol, fecha_creación), `Rol` (`ENTRENADOR`, `ATLETA`, `INVITADO`), `Permiso` (10 acciones del sistema).
- **Puertos:** `RepositorioUsuarios`, `ServicioHashContrasenas` (el hashing concreto —bcrypt, argon2— es del adaptador), `PermisosPorRol` (matriz rol → permisos).
- **Casos de uso:** `AutenticarUsuario`, `CrearUsuario`, `VerificarPermiso`, `ObtenerUsuarioActual`.
- **Reglas clave:**
  - Solo puede existir **un único usuario ENTRENADOR** (RF-01.3).
  - Correo con formato válido y contraseña de al menos 8 caracteres.
  - Un entrenador tiene como máximo 40 atletas; un atleta tiene entre 1 y 3 entrenadores (reglas compartidas en `comun/reglas_limites.py`).

### 5.2 Atletas — RF-02

**Responsabilidad:** expediente deportivo integral del ajedrecista.

- **Entidades:** `Atleta` (con `edad()` automática desde la fecha de nacimiento), `Rating` (clásicas, rápidas, blitz, Chess.com, Lichess), `Categoria` (por edad, nivel o ELO), `PerfilHistorico` (snapshot inmutable por año/torneo).
- **Puertos:** `RepositorioAtletas`, `RepositorioCategorias` (categorías configurables por el administrador, RNF-07.1).
- **Casos de uso:** `RegistrarAtleta` (campos obligatorios RF-02.1/02.2 y categorías existentes), `ActualizarPerfilAtleta`, `ConsultarPerfilAtleta`, `AsignarCategoriaAAtleta`, `AsignarEntrenadorAAtleta` (valida límites), `ActualizarRating` (crea snapshot histórico inmutable con id único; permite actualizaciones periódicas, RF-13.6), `ListarAtletasPorEntrenador`.
- **Reglas clave:** el historial por año/torneo **no se modifica ni se elimina**; los snapshots previos quedan congelados.

### 5.3 Objetivos SMART — RF-03

**Responsabilidad:** definir, seguir y validar objetivos cuantificables.

- **Entidades:** `ObjetivoSmart`, `IndicadorAvance`, `EstadoObjetivo` (`PENDIENTE_APROBACION`, `EN_PROCESO`, `RETRASADO`, `FINALIZADO`), `TipoIndicadorAvance` (horas entrenadas, rating, tareas, torneos, medallas).
- **Puertos:** `RepositorioObjetivos`, `ProveedorDatosAvance` — **puerto de consulta cruzada**: el caso de uso obtiene las horas/rating/torneos actuales sin acoplarse a los repositorios de Entrenamientos o Partidas.
- **Casos de uso:** `CrearObjetivoSmart` (propuesto por entrenador o atleta), `AprobarObjetivoSmart`, `CalcularAvanceObjetivo` (automático), `EvaluarEstadoObjetivo` (semáforo), `ValidarCumplimientoObjetivo` (solo el entrenador), `ListarObjetivosPorAtleta`.
- **Reglas clave:** fecha de inicio y límite **obligatorias**; **RETRASADO** = avance real menor al porcentaje esperado según la fecha límite; el semáforo es verde (finalizado), amarillo (en proceso) o rojo (retrasado).

### 5.4 Entrenamientos — RF-04

**Responsabilidad:** planificación semanal, registro de ejecución y asistencia.

- **Entidades:** `PlanEntrenamientoSemanal` (calcula horas planificadas, ejecutadas-aprobadas y % de cumplimiento), `SesionEntrenamiento` (12 tipos de contenido; estados `PROGRAMADA`, `REPROGRAMADA`, `CANCELADA`, `EJECUTADA`), `EjecucionEntrenamiento`, `Asistencia`, `ResumenCumplimientoSemanal` (value object del contraste planificado vs ejecutado).
- **Puertos:** `RepositorioEntrenamientos` (incluye `buscar_sesion`), `RepositorioAsistencia`.
- **Casos de uso:** `PlanificarEntrenamientoSemanal` (una sola planificación por semana), `ReprogramarSesion` (solo entrenador), `RegistrarEjecucionEntrenamiento` (solo el atleta), `AprobarHorasEjecutadas` (solo el entrenador), `ConsultarCumplimientoSemanal` (devuelve el VO con el %), `RegistrarAsistencia` (solo entrenador), `ConsultarHistorialEntrenamientos`.
- **Regla clave:** % de cumplimiento = horas ejecutadas aprobadas / horas planificadas × 100.

### 5.5 Partidas y Análisis Técnico — RF-05 y RF-07

**Responsabilidad:** registrar partidas, almacenar resúmenes de análisis y clasificar la calidad del juego.

- **Entidades:** `Partida` (con `color_atleta` y `puntos_obtenidos()`), `AnalisisTecnico` (accuracy, ACPL, blunders, errores, imprecisiones, brilliant moves, etc.), `ClasificacionPartida` (`PARTIDA_BOTADA`, `EXCELENTE`, `BUENA`, `LIBRO`), `EstadisticasFaseJuego` (apertura, medio juego, finales).
- **Puertos:** `RepositorioPartidas`, `RepositorioAnalisisTecnico`, `ProveedorPGN` — **el dominio no parsea PGN**; solicita la partida ya estructurada.
- **Casos de uso:** `RegistrarPartida` y `validar_partida` (validación compartida con la importación), `RegistrarAnalisisTecnico` (solo el entrenador), `ClasificarPartida` (partida botada = ventaja > +3 con pérdida/empate por blunder; excelente = accuracy ≥ 85 sin blunders), `ConsultarEstadisticasPorFase`, `ImportarPartidaDesdePGN`.
- **Reglas clave:** solo se almacenan **resúmenes** del análisis (no movimiento a movimiento); los puntos y la clasificación respetan el color con el que jugó el atleta.

### 5.6 Patrones de Error — RF-06

**Responsabilidad:** detectar patrones recurrentes sin generar sugerencias (solo estadísticas).

- **Entidades:** `TipoPatron` (táctico, estratégico, apertura, finales, gestión del tiempo, competitivo, disciplina), `NivelMinimoPartidas` (básico 5, inicial 10, apertura 15, finales 15, color 20, rival 20, avanzado 30), `PatronDetectado`, `AnalisisPatrones`.
- **Puertos:** `ProveedorDatosPartidas` (partidas con análisis + conteos de disciplina).
- **Casos de uso:** `DetectarPatronesError`.
- **Reglas clave:** un comportamiento es patrón si se repite en **≥ 5 partidas o en > 40 %** de las analizadas (RF-06.8); detecta blunders, imprecisiones estratégicas, salidas de teoría, pérdidas por tiempo, apuros, derrotas con blunder, **disciplina** (incumplimiento del plan, baja asistencia, baja frecuencia de análisis), **rendimiento por color**, **contra rivales de mayor rating** y **por control de tiempo**.

### 5.7 Repertorio de Aperturas — RF-08

**Responsabilidad:** gestionar el repertorio del atleta con estadísticas de efectividad.

- **Entidades:** `AperturaRepertorio` (código ECO, color, estado, nivel de dominio, clasificación principal/secundaria), `EstadisticaApertura` (con `efectividad()`: muy efectiva, efectiva, en desarrollo, requiere revisión), `EstadisticaAperturaPorTorneo`.
- **Puertos:** `RepositorioAperturas`, `ProveedorEvaluacionMotor` (evaluación numérica de posiciones, p. ej. Stockfish).
- **Casos de uso:** `RegistrarAperturaRepertorio`, `ClasificarAperturaPrincipalSecundaria`, `EvaluarEfectividadApertura`, `ConsultarEstadisticasGeneralesApertura`, `ConsultarEstadisticasPorTorneo` (filtra por año, control de tiempo, color, nivel de rival y rival).
- **Regla clave:** la efectividad se mide por el **desempeño del atleta**, no por la valoración teórica de la apertura.

### 5.8 Indicadores, Dashboards e Informes — RF-09 y RF-11

**Responsabilidad:** calcular métricas de rendimiento y generar vistas consolidadas y reportes.

- **Entidades:** `IndicadorRendimiento` (15 tipos de indicador), `RangoEvaluacion` (`EXCELENTE`, `BUENO`, `ACEPTABLE`, `REQUIERE_INTERVENCION`), `Alerta`, `DashboardEntrenador`, `DashboardAtleta`, `Reporte` (individual/grupal/institucional; PDF/Excel), `TendenciaComparada` (variación absoluta y porcentual).
- **Puertos:** `RepositorioIndicadores`, `ProveedorDatosRendimiento` (consulta cruzada unificada hacia entrenamientos, partidas, objetivos y aperturas), `ProveedorRangosEvaluacion` (**RNF-07.2**: rangos configurables, con valores por defecto en el dominio), `ServicioGeneracionReportes` (el dominio define el contenido; el adaptador genera el PDF/Excel).
- **Casos de uso:** `CalcularIndicadoresPrincipales` (accuracy, ACPL, cumplimientos, resultados, blunders, rating), `CalcularIndicadoresSecundarios` (ejercicios, partidas analizadas, asistencia, torneos), `GenerarDashboardEntrenador` (alertas automáticas cuando un indicador cae en "Requiere Intervención"), `GenerarDashboardAtleta`, `CompararTendencias` (mes vs mes, torneo vs torneo, año vs año, rangos personalizados), `GenerarReporte`, `GenerarReporteIntegralAtleta` (8 secciones obligatorias, RF-11.10), `GenerarReporteGrupal`, `GenerarReporteInstitucional` (mensual/trimestral/anual).
- **Nota:** `EvaluadorRangos` aplica la configuración del proveedor o los rangos por defecto; en indicadores como ACPL y blunders un **valor menor es mejor**.

### 5.9 Evaluación del Entrenador — RF-10

**Responsabilidad:** evaluar el rendimiento del atleta tras cada torneo, mes, mesociclo o año.

- **Entidades:** `EvaluacionAtleta` (calificaciones 1-10 por cada uno de los **8 indicadores** de RF-10.2, comentarios de fortalezas/aspectos por mejorar/recomendaciones, `promedio_calificaciones`), `PeriodoEvaluacion` (`TORNEO`, `MES`, `MESOCICLO`, `ANIO`).
- **Puertos:** `RepositorioEvaluaciones`.
- **Casos de uso:** `CrearEvaluacion` (la del entrenador es **obligatoria** y debe cubrir los 8 indicadores; la autoevaluación del atleta es **opcional** y puede ser parcial), `ActualizarEvaluacion` (seguimiento entre ciclos), `ConsultarEvaluacionesPorAtleta`, y la factoría `nueva_evaluacion(...)`.
- **Regla clave:** calificación siempre entre 1 y 10.

### 5.10 Auditoría y Control de Cambios — RF-12

**Responsabilidad:** garantizar trazabilidad de todos los cambios críticos.

- **Entidades:** `RegistroAuditoria` (inmutable: usuario, fecha/hora, entidad, campo, valor anterior/nuevo, operación), `TipoOperacion` (`CREAR`, `MODIFICAR`, `ELIMINAR`).
- **Puertos:** `RepositorioAuditoria`.
- **Casos de uso:** `RegistrarCambio`, `ConsultarHistorialCambios` (exige al menos un filtro: entidad, usuario o fecha), `ValidarIntegridadDatos` (previene ratings incorrectos, resultados inválidos y eliminaciones no autorizadas de históricos).

---

## 6. Dependencias entre módulos

Los módulos se comunican sin acoplarse, siguiendo tres estrategias:

1. **Referencias por id, no por objeto.** Un `ObjetivoSmart` conoce `id_atleta`; un `PlanEntrenamientoSemanal` conoce `id_atleta`; nunca se guarda el objeto completo de otro módulo.

2. **Puertos de consulta cruzada.** Cuando un módulo necesita datos de otro, define su **propio puerto** que los adaptadores implementarán consultando los repositorios correspondientes:
   - `objetivos/ProveedorDatosAvance` → horas entrenadas, rating, tareas, torneos, medallas.
   - `indicadores/ProveedorDatosRendimiento` → agregados de entrenamientos, partidas, objetivos y aperturas.
   - `patrones/ProveedorDatosPartidas` → partidas con análisis y conteos de disciplina.
   - `aperturas/ProveedorEvaluacionMotor` → evaluación de posiciones (motor de ajedrez).

3. **Dependencias dirigidas hacia `comun/`.** Los módulos comparten errores, constantes, reglas de límites e ids desde `comun/`, y usan `usuarios/Rol` para las comprobaciones de permisos — nunca en sentido contrario.

> Los **eventos de dominio** quedaron como evolución opcional para una fase posterior. Hoy, un cambio en Entrenamientos que deba reflejarse en Indicadores se resuelve por orquestación explícita en el caso de uso.

---

## 7. Cómo añadir un módulo nuevo

1. Crea la carpeta `dominio/<modulo>/` con un `__init__.py` vacío.
2. `entidades.py` — define las clases de datos con sus invariantes (validaciones y cálculos dentro de la entidad).
3. `puertos.py` — define los `ABC` que necesitará (repositorios, proveedores externos).
4. `casos_de_uso.py` — clases `@dataclass` con `ejecutar(...)`, inyectando puertos por constructor.
5. Si el módulo necesita datos de otro, define un puerto de consulta cruzada en lugar de importar repositorios ajenos.
6. Reutiliza `comun/errores.py`, `comun/ids.py` y las constantes/reglas compartidas.
7. Verifica que compila: `python -m compileall -q dominio`.

---

## 8. Validación

```bash
# Comprueba que todo el dominio compila
python -m compileall -q dominio

# Comprueba que los 14 módulos importan correctamente
python -c "import importlib; [importlib.import_module(m) for m in [
    'dominio.comun.errores', 'dominio.comun.constantes', 'dominio.comun.reglas_limites', 'dominio.comun.ids',
    'dominio.usuarios', 'dominio.atletas', 'dominio.objetivos', 'dominio.entrenamientos',
    'dominio.partidas', 'dominio.aperturas', 'dominio.indicadores', 'dominio.patrones',
    'dominio.auditoria', 'dominio.evaluaciones']]"
```

---

## 9. Qué queda fuera del dominio (adaptadores pendientes)

Según el plan de arquitectura, todo lo tecnológico se implementará como adaptadores:

| Necesidad | Adaptador futuro |
|---|---|
| Persistencia | SQLite/PostgreSQL con SQLAlchemy y Alembic |
| Interfaz web | FastAPI (endpoints REST) que llama a los casos de uso |
| Autenticación | JWT/OAuth/sesiones (cumpliendo `ServicioHashContrasenas`) |
| Exportación PDF/Excel | ReportLab / OpenPyXL (cumpliendo `ServicioGeneracionReportes`) |
| Importación PGN | Parser de PGN (cumpliendo `ProveedorPGN`) |
| Motor de ajedrez | Stockfish / python-chess (cumpliendo `ProveedorEvaluacionMotor`) |
| APIs externas | Chess.com, Lichess, ChessBase |
