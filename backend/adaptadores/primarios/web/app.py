"""Aplicación principal FastAPI para Caissa Analytic."""
from __future__ import annotations

import sys
from pathlib import Path

# Asegurar que backend está en sys.path para resolver imports
RAIZ_BACKEND = Path(__file__).resolve().parent.parent.parent
if str(RAIZ_BACKEND) not in sys.path:
    sys.path.insert(0, str(RAIZ_BACKEND))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from adaptadores.primarios.web.routers import atletas, partidas, objetivos, indicadores, aperturas

app = FastAPI(
    title="Caissa Analytic API",
    description="API REST de alto rendimiento para el análisis deportivo, táctico y estratégico en ajedrez.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configuración de CORS para permitir peticiones desde el frontend en desarrollo y producción
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://caissa-analytic.vercel.app",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de routers modulares
app.include_router(atletas.router)
app.include_router(partidas.router)
app.include_router(objetivos.router)
app.include_router(indicadores.router)
app.include_router(aperturas.router)


@app.get("/", tags=["Estado"])
def root():
    return {
        "sistema": "Caissa Analytic API",
        "version": "1.0.0",
        "estado": "operativo",
        "docs": "/docs",
        "database": "caissa.db (SQLite)",
    }


@app.get("/api/health", tags=["Estado"])
def health():
    return {"status": "ok", "engine": "FastAPI + Clean Architecture"}

