# Integración con el Backend — Caissa Analytic

Este documento especifica cómo el frontend de Next.js se conectará y comunicará con el backend de Python alojado en `backend/`.

---

## 🔌 Arquitectura de Comunicación

```
[ Navegador del Usuario ] 
       │
       ▼ (HTTPS / JSON)
[ Frontend Next.js (Vercel) ]
       │
       │  (Llamadas de Servidor o Cliente)
       ▼ 
[ API Web Python (FastAPI / Flask) ] ──▶ [ backend/dominio ] ──▶ [ SQLite caissa.db ]
```

---

## ⚙️ Variables de Entorno en el Frontend

Crea un archivo `.env.local` en `frontend/` (este archivo no se sube a Git):

```env
# URL base de la API del backend
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Tiempo de espera para peticiones en milisegundos
NEXT_PUBLIC_API_TIMEOUT=15000

# Entorno de ejecución
NEXT_PUBLIC_APP_ENV=development
```

En **Vercel**, la variable `NEXT_PUBLIC_API_URL` se configurará en la sección **Settings > Environment Variables** con la URL pública de producción del backend (por ejemplo, en Railway, Render o VPS).

---

## 📡 Cliente HTTP Base (`src/lib/api-client.ts`)

Cuando se implemente el código, se usará un cliente centralizado basado en `fetch` o `axios` que incluya:

1. **Inyección automática del Token**:
   * Si existe un token de sesión en cookies o almacenamiento local, se inyecta en el encabezado `Authorization: Bearer <token>`.
2. **Manejo estandarizado de Errores**:
   * Captura de códigos HTTP (401 para expiración de sesión, 403 para permisos insuficientes, 422 para errores de validación de dominio).
3. **Tipado fuerte**:
   * Cada función del API devolverá un tipo de TypeScript que corresponda a las entidades del dominio de Python.

---

## 🗺️ Mapeo de Endpoints Previstos vs Módulos del Backend

Los endpoints que el frontend consumirá corresponden directamente a los casos de uso implementados en `backend/dominio/`:

| Módulo Backend | Casos de Uso del Dominio | Endpoint API Estimado |
| :--- | :--- | :--- |
| `dominio/usuarios` | Iniciar sesión, validar permisos, perfil | `POST /api/v1/auth/login`, `GET /api/v1/auth/me` |
| `dominio/atletas` | Listar atletas, detalle, actualizar datos | `GET /api/v1/atletas`, `GET /api/v1/atletas/{id}`, `POST /api/v1/atletas` |
| `dominio/partidas` | Cargar PGN, filtrar partidas, ver jugadas | `GET /api/v1/partidas`, `POST /api/v1/partidas/pgn`, `GET /api/v1/partidas/{id}` |
| `dominio/aperturas` | Consultar repertorio, efectividad por variante | `GET /api/v1/aperturas`, `GET /api/v1/aperturas/arbol` |
| `dominio/indicadores`| Calcular métricas, historial ELO, estadísticas | `GET /api/v1/indicadores/atleta/{id}` |
| `dominio/entrenamientos` | Crear planes, tareas tácticas, seguimiento | `GET /api/v1/entrenamientos`, `POST /api/v1/entrenamientos` |
| `dominio/evaluaciones`| Fichas técnicas, evaluación periódica | `GET /api/v1/evaluaciones`, `POST /api/v1/evaluaciones` |
| `dominio/auditoria` | Registro de trazabilidad y eventos | `GET /api/v1/auditoria/eventos` |
| `dominio/configuracion` | Configuración de rangos, umbrales y roles | `GET /api/v1/configuracion`, `PUT /api/v1/configuracion` |

---

## 🛡️ Consideraciones de CORS y Seguridad

* **CORS en el Backend**: El backend en Python debe tener habilitado CORS para permitir solicitudes desde el origen del frontend (en desarrollo: `http://localhost:3000`, en producción: `https://tu-proyecto.vercel.app`).
* **Seguridad de Tokens**: Si se usan cookies `httpOnly`, se garantiza protección contra ataques XSS.

