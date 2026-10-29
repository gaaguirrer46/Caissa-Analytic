# Caissa Analytic — Backend (Python Hexagonal Architecture)

Núcleo del sistema **Caissa Analytic** desarrollado en Python bajo los principios de **Arquitectura Hexagonal (Puertos y Adaptadores / Clean Architecture)**.

---

## 🏛️ Estructura del Backend

```
backend/
├── dominio/                          # Capa de Dominio (Reglas de Negocio Puras)
│   ├── aperturas/                    # Gestión y análisis de aperturas
│   ├── atletas/                      # Fichas técnicas, categorías y seguimiento
│   ├── auditoria/                    # Trazabilidad de operaciones críticas
│   ├── comun/                        # Validaciones, errores, límites y constantes
│   ├── configuracion/                # Rangos y parámetros del sistema
│   ├── entrenamientos/               # Asignación y control de entrenamientos
│   ├── evaluaciones/                 # Evaluaciones técnicas y fichas periódicas
│   ├── indicadores/                  # Métricas de rendimiento, ELO y precisión
│   ├── objetivos/                    # Metas y objetivos SMART
│   ├── partidas/                     # Procesamiento PGN y estadísticas por fase
│   ├── patrones/                     # Detección de patrones tácticos
│   └── usuarios/                     # Gestión de usuarios, credenciales y roles
│
├── adaptadores/                      # Capa de Adaptadores
│   ├── primarios/                    # Puntos de entrada (driving adapters)
│   │   ├── cli/                      # Interfaz de línea de comandos
│   │   └── web/                      # API REST / Web para conectar con el frontend
│   └── secundarios/                  # Adaptadores de salida (driven adapters)
│       ├── apis_externas/            # Conexión a servicios externos (FIDE, Lichess, etc.)
│       ├── autenticacion/            # Hashing de contraseñas y seguridad
│       ├── motor/                    # Integración con motor de análisis (Stockfish)
│       ├── persistencia/             # Repositorios SQLite para cada módulo de dominio
│       ├── pgn/                      # Lector y parser de archivos PGN
│       └── reportes/                 # Generación de reportes y exportaciones
│
├── infraestructura/                  # Capa de Infraestructura
│   ├── base_de_datos/                # Conexión transaccional SQLite (`conexion.py`)
│   └── dependencias/                 # Contenedor de inyección de dependencias
│
└── caissa.db                         # Base de datos SQLite del sistema
```

---

## 🗄️ Base de Datos

* **Ubicación**: `backend/caissa.db`
* **Gestor**: SQLite con soporte para *foreign keys* y transacciones seguras configurado en `infraestructura/base_de_datos/conexion.py`.
* La ruta se resuelve dinámicamente relativa a la raíz de `backend/` o mediante la variable de entorno `CAISSA_DB_PATH`.

