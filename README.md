# Caissa Analytic — Plataforma Integral de Rendimiento Ajedrecístico

**Caissa Analytic** es una plataforma orientada al seguimiento, análisis y optimización del rendimiento de atletas de ajedrez, integrando análisis de partidas (PGN), repertorio de aperturas, planes de entrenamiento, evaluaciones periódicas e indicadores tácticos y estratégicos.

---

## 🗂️ Estructura del Proyecto

El repositorio está organizado bajo un esquema monorepo modular:

```
Caissa Analytic/
├── backend/                    # Núcleo del sistema en Python (Arquitectura Hexagonal)
│   ├── dominio/                # Lógica pura de negocio (Entidades, Casos de Uso, Puertos)
│   ├── adaptadores/            # Adaptadores primarios (web, cli) y secundarios (persistencia, pgn...)
│   ├── infraestructura/        # Conexión DB, dependencias e inyección
│   └── caissa.db               # Base de datos SQLite
│
├── frontend/                   # Interfaz de usuario en Next.js (React + Tailwind + Vercel)
│   ├── README.md               # Resumen del frontend y stack tecnológico
│   ├── ARQUITECTURA_Y_ESTRUCTURA.md # Organización por módulos y convenciones
│   ├── PLAN_DE_DESARROLLO.md   # Hoja de ruta en 6 fases de implementación
│   └── INTEGRACION_BACKEND.md  # Contratos y endpoints previstos con el backend
│
├── Documentación base/         # Documentos de auditoría, requerimientos y especificaciones
├── .gitignore                  # Reglas de exclusión para Python y Next.js
└── README.md                   # Este archivo
```

---

## 🧭 Estado de las Capas

1. **Backend (`/backend`)**:
   * Implementado con **Arquitectura Limpia / Hexagonal**.
   * Módulos funcionales de dominio: `atletas`, `partidas`, `aperturas`, `entrenamientos`, `evaluaciones`, `indicadores`, `patrones`, `auditoria`, `usuarios`, `configuracion` y `comun`.
   * Adaptadores de persistencia SQLite y lectura de PGN operativos.

2. **Frontend (`/frontend`)**:
   * Arquitectura seleccionada: **Next.js (App Router)** + **Tailwind CSS** + **shadcn/ui**.
   * Planificado y documentado para despliegue nativo en **Vercel**.
   * Documentación técnica y plan de fases listo en [frontend/README.md](frontend/README.md).

