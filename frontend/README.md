# Caissa Analytic — Frontend (Next.js)

Este directorio contendrá la aplicación frontend para **Caissa Analytic**, la plataforma analítica de ajedrez para el seguimiento de atletas, análisis de partidas, repertorio de aperturas, planes de entrenamiento y métricas de rendimiento.

---

## 📌 Estado Actual

> [!NOTE]
> Siguiendo la planificación de arquitectura, **aún no se ha generado código fuente** en esta carpeta. Primero se han establecido las especificaciones, la arquitectura recomendada, el plan de fases y los contratos de integración con el backend.

---

## 🛠️ Stack Tecnológico Seleccionado

| Herramienta / Librería | Propósito |
| :--- | :--- |
| **Next.js (App Router)** | Framework full-stack / frontend de React optimizado para Vercel. |
| **TypeScript** | Tipado estático estricto para garantizar consistencia con los modelos del dominio. |
| **Tailwind CSS** | Estilos utilitarios modernos, responsivos y de alto rendimiento. |
| **shadcn/ui** | Componentes de UI accesibles, personalizables y de estándar profesional. |
| **Lucide React** | Iconografía limpia y coherente para dashboards deportivos/analíticos. |
| **Recharts / Tremor** | Gráficos analíticos interactivos (curvas de ELO, distribución de aperturas, precisión táctica). |
| **react-chessboard + chess.js** | Visualizador y reproductor interactivo de tableros de ajedrez y parseo de PGN/FEN. |
| **TanStack Query (React Query)** | Gestión eficiente del caché de llamadas API al backend en Python. |
| **Zustand** | Gestión de estado global ligero (sesión activa, filtros globales, configuración de tablero). |

---

## 📚 Documentos de Planificación y Guías

Antes de escribir la primera línea de código en Next.js, consulta los siguientes documentos detallados:

1. [**ARQUITECTURA_Y_ESTRUCTURA.md**](./ARQUITECTURA_Y_ESTRUCTURA.md):
   * Organización modular orientada a características (*Feature-driven Architecture*).
   * Separación clara entre Server Components y Client Components.
   * Convenciones de nombres, tipado y componentes UI.

2. [**PLAN_DE_DESARROLLO.md**](./PLAN_DE_DESARROLLO.md):
   * Hoja de ruta dividida en 6 fases de implementación paso a paso.
   * Definición de prioridades, entregables y criterios de aceptación por módulo.

3. [**INTEGRACION_BACKEND.md**](./INTEGRACION_BACKEND.md):
   * Guía de conexión con el backend de Python (`backend/adaptadores/primarios/web`).
   * Configuración de variables de entorno, cliente HTTP, CORS y autenticación JWT.

---

## 🚀 Próximo Paso (Cuando se decida inicializar)

Cuando estés listo para inicializar el proyecto Next.js en esta carpeta, se ejecutará:

```bash
npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"
```

*(Consulta [PLAN_DE_DESARROLLO.md](./PLAN_DE_DESARROLLO.md) para ver la guía paso a paso de la Fase 0).*

