"""Script de inicio del servidor FastAPI para Caissa Analytic."""
import sys
from pathlib import Path

# Añadir la carpeta backend al path de ejecución
RAIZ_BACKEND = Path(__file__).resolve().parent
if str(RAIZ_BACKEND) not in sys.path:
    sys.path.insert(0, str(RAIZ_BACKEND))

import uvicorn

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Iniciando Caissa Analytic API (FastAPI) en http://localhost:8000")
    print("📚 Documentación Swagger interactiva: http://localhost:8000/docs")
    print("=" * 60)
    uvicorn.run("adaptadores.primarios.web.app:app", host="0.0.0.0", port=8000, reload=True)

