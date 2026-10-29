# Arquitectura y Estructura del Frontend — Next.js

Este documento define la arquitectura interna, la estructura de carpetas y las buenas prácticas para el frontend de **Caissa Analytic**.

---

## 🏗️ Principios de Diseño

1. **Feature-Driven Architecture (Arquitectura por Funcionalidades)**:
   * El código no se organiza solo por tipo de archivo (`components/`, `hooks/`), sino por módulo de negocio (`features/atletas`, `features/partidas`, `features/aperturas`), replicando la claridad del dominio que existe en el backend.
2. **Server Components por Defecto**:
   * Usar Server Components de Next.js (App Router) para la carga de datos inicial y layouts estáticos.
   * Usar `"use client"` únicamente en componentes con interactividad: tableros de ajedrez arrastrables, formularios, modales y filtros dinámicos.
3. **Desacoplamiento del Backend**:
   * Todos los endpoints de la API se abstraen en servicios tipados dentro de cada *feature* o en `src/services/api/`. Si el backend cambia un endpoint, solo se modifica el cliente de servicio.

---

## 📁 Estructura de Directorios Recomendada (`src/`)

```
frontend/
├── public/                     # Assets estáticos (logos, piezas de ajedrez SVG, sonidos PGN)
├── src/
│   ├── app/                    # Next.js App Router (Páginas y Rutas)
│   │   ├── (auth)/             # Grupo de rutas de autenticación
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   └── layout.tsx
│   │   ├── (dashboard)/        # Shell principal de la aplicación (Sidebar + Topbar)
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx        # Dashboard general / resumen analítico
│   │   │   ├── atletas/
│   │   │   │   ├── page.tsx            # Lista de atletas
│   │   │   │   └── [id]/page.tsx       # Perfil del atleta y métricas
│   │   │   ├── partidas/
│   │   │   │   ├── page.tsx            # Lista de partidas con filtros
│   │   │   │   └── [id]/page.tsx       # Visor interactivo de partida
│   │   │   ├── aperturas/
│   │   │   │   └── page.tsx            # Explorador y árbol de aperturas
│   │   │   ├── entrenamientos/
│   │   │   │   └── page.tsx            # Asignación y planes de entrenamiento
│   │   │   ├── evaluaciones/
│   │   │   │   └── page.tsx            # Informes de evaluación técnica
│   │   │   ├── indicadores/
│   │   │   │   └── page.tsx            # Gráficos y analítica avanzada
│   │   │   ├── auditoria/
│   │   │   │   └── page.tsx            # Registro de auditoría y controles
│   │   │   └── configuracion/
│   │   │       └── page.tsx            # Rangos, umbrales y roles
│   │   ├── api/                # Route Handlers de Next.js (Proxy / BFF seguro opcional)
│   │   ├── layout.tsx          # Root Layout (Fuentes, Providers globales)
│   │   └── globals.css         # Directivas de Tailwind y variables CSS
│   │
│   ├── features/               # Módulos por Dominio de Negocio
│   │   ├── atletas/
│   │   │   ├── components/     # AtletaCard, AtletaForm, AtletaStats
│   │   │   ├── hooks/          # useAtleta, useAtletasList
│   │   │   ├── services/       # atletasApi.ts
│   │   │   └── types/          # atleta.types.ts
│   │   ├── partidas/
│   │   │   ├── components/     # BoardViewer, MoveList, PgnUploader, EvaluationBar
│   │   │   ├── hooks/          # useChessGame, usePgnParser
│   │   │   ├── services/       # partidasApi.ts
│   │   │   └── types/          # partida.types.ts
│   │   ├── aperturas/
│   │   │   ├── components/     # OpeningTree, WinRateBadge, RepertoireCard
│   │   │   ├── services/       # aperturasApi.ts
│   │   │   └── types/
│   │   ├── indicadores/
│   │   │   ├── components/     # EloProgressChart, AccuracyGauge, TacticalRadar
│   │   │   ├── services/       # indicadoresApi.ts
│   │   │   └── types/
│   │   └── auth/
│   │       ├── components/     # LoginForm, RoleGuard
│   │       ├── hooks/          # useAuth
│   │       └── types/          # user.types.ts
│   │
│   ├── components/             # Componentes Compartidos (Cross-feature)
│   │   ├── ui/                 # Componentes base shadcn (Button, Dialog, Card, Input, Table...)
│   │   ├── layout/             # Sidebar, Header, UserMenu, Breadcrumbs
│   │   └── chess/              # Componente base de Tablero interactivo reutilizable
│   │
│   ├── hooks/                  # Hooks utilitarios globales (useDebounce, useMediaQuery)
│   ├── lib/                    # Utilidades y configuración de librerías
│   │   ├── utils.ts            # cn() para clases de Tailwind
│   │   ├── api-client.ts       # Instancia configurada de Axios / Fetch con interceptores
│   │   └── chess-engine.ts     # Helpers para lógica de ajedrez (chess.js)
│   ├── stores/                 # Zustand Stores (authStore, uiStore, filterStore)
│   └── types/                  # Tipos globales y genéricos de API (ApiResponse<T>, etc.)
```

---

## ♟️ Componentes Clave Específicos para Ajedrez

1. **`BoardViewer`**:
   * Encapsula `react-chessboard`.
   * Permite navegación de jugadas (anterior, siguiente, saltar a posición FEN).
   * Barra de evaluación dinámica si el backend incluye análisis de motor.
2. **`MoveList`**:
   * Visualización del árbol algebraico de la partida (ej: `1. e4 e5 2. Nf3 Nc6`).
   * Clic en cualquier jugada para saltar la posición del tablero.
3. **`OpeningExplorer`**:
   * Representación jerárquica de variantes con porcentajes de victorias/tablas/derrotas.
4. **`EloProgressChart`**:
   * Gráfica temporal con Recharts que muestra la progresión del atleta y picos de rendimiento.

---

## 🎨 Sistema de Diseño y UI

* **Tokens de Color**: Paleta sobria y deportiva (Dark Slate / Zinc con acentos en esmeralda o zafiro, simulando el estilo de plataformas analíticas como Chess.com o Lichess Insights).
* **Modo Oscuro / Claro**: Integrado con `next-themes` y clases `dark:` de Tailwind.
* **Componentes UI**: Basados en **shadcn/ui** (código abierto, copiado directamente a `src/components/ui`, 100% controlable sin dependencias de cajas negras).

