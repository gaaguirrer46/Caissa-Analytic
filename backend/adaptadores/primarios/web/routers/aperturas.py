"""Endpoints de Repertorio de Aperturas para Caissa Analytic."""
from __future__ import annotations

from typing import Any, Dict, List
from fastapi import APIRouter

from infraestructura.dependencias.contenedor import Contenedor

router = APIRouter(prefix="/api/v1/aperturas", tags=["Aperturas"])
contenedor = Contenedor()

@router.get("", response_model=List[Dict[str, Any]])
def listar_aperturas():
    """Retorna las aperturas del repertorio con estadísticas de efectividad."""
    return [
        {
            "id": 1,
            "eco": "B90",
            "nombre": "Defensa Siciliana: Variante Najdorf",
            "jugadas": "1. e4 c5 2. Nf3 d6 3. d4 cxd4 4. Nxd4 Nf6 5. Nc3 a6",
            "color": "NEGRAS",
            "partidas_jugadas": 24,
            "win_rate": 66.7,
            "rendimiento": "ALTO",
        },
        {
            "id": 2,
            "eco": "C50",
            "nombre": "Apertura Italiana: Giuoco Piano",
            "jugadas": "1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5",
            "color": "BLANCAS",
            "partidas_jugadas": 18,
            "win_rate": 72.2,
            "rendimiento": "OPTIMO",
        },
        {
            "id": 3,
            "eco": "E60",
            "nombre": "Defensa India de Rey: Variante Clásica",
            "jugadas": "1. d4 Nf6 2. c4 g6 3. Nc3 Bg7 4. e4 d6",
            "color": "NEGRAS",
            "partidas_jugadas": 15,
            "win_rate": 60.0,
            "rendimiento": "SOLIDO",
        },
        {
            "id": 4,
            "eco": "D35",
            "nombre": "Gambito de Dama Declinado: Cambio",
            "jugadas": "1. d4 d5 2. c4 e6 3. Nc3 Nf6 4. cxd5",
            "color": "BLANCAS",
            "partidas_jugadas": 12,
            "win_rate": 75.0,
            "rendimiento": "OPTIMO",
        },
    ]

