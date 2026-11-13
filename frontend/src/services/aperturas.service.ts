import { AperturaRepertorio, AperturaCrearInput } from "@/types/apertura.types";

export const APERTURAS_MOCK: AperturaRepertorio[] = [
  {
    id: 2,
    id_atleta: 2,
    codigo_eco: "B90",
    nombre: "Defensa Siciliana",
    variante: "Variante Najdorf (6.Be3)",
    color: "NEGRAS",
    estado: "ACTIVA",
    nivel_dominio: "AVANZADO",
    clasificacion_uso: "PRINCIPAL",
    fuente_estudio: "Modern Chess Openings & ChessBase",
    observaciones: "Arma principal contra 1.e4",
    partidas_jugadas: 28,
    victorias: 18,
    empates: 7,
    derrotas: 3,
    rendimiento_pct: 76.8,
    accuracy_promedio: 93.5,
    acpl_promedio: 18.2,
    errores_frecuentes: 1,
    evaluacion_motor: 0.4,
    efectividad: "MUY_EFECTIVA",
    jugadas_clave: "1. e4 c5 2. Nf3 d6 3. d4 cxd4 4. Nxd4 Nf6 5. Nc3 a6",
  },
  {
    id: 3,
    id_atleta: 2,
    codigo_eco: "C50",
    nombre: "Apertura Italiana",
    variante: "Giuoco Piano (d3 sólido)",
    color: "BLANCAS",
    estado: "ACTIVA",
    nivel_dominio: "AVANZADO",
    clasificacion_uso: "PRINCIPAL",
    fuente_estudio: "ChessBase Magazine #210",
    observaciones: "Repertorio de élite con blancas",
    partidas_jugadas: 22,
    victorias: 16,
    empates: 4,
    derrotas: 2,
    rendimiento_pct: 81.8,
    accuracy_promedio: 94.2,
    acpl_promedio: 16.8,
    errores_frecuentes: 0,
    evaluacion_motor: 0.7,
    efectividad: "MUY_EFECTIVA",
    jugadas_clave: "1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. O-O Nf6 5. d3",
  },
  {
    id: 4,
    id_atleta: 3,
    codigo_eco: "E60",
    nombre: "Defensa India de Rey",
    variante: "Variante Clásica",
    color: "NEGRAS",
    estado: "ACTIVA",
    nivel_dominio: "INTERMEDIO",
    clasificacion_uso: "PRINCIPAL",
    fuente_estudio: "Mastering the King's Indian",
    observaciones: "Líneas de contraataque táctico",
    partidas_jugadas: 19,
    victorias: 11,
    empates: 5,
    derrotas: 3,
    rendimiento_pct: 71.1,
    accuracy_promedio: 88.6,
    acpl_promedio: 26.4,
    errores_frecuentes: 2,
    evaluacion_motor: -0.2,
    efectividad: "MUY_EFECTIVA",
    jugadas_clave: "1. d4 Nf6 2. c4 g6 3. Nc3 Bg7 4. e4 d6 5. Nf3 O-O",
  },
  {
    id: 5,
    id_atleta: 4,
    codigo_eco: "D35",
    nombre: "Gambito de Dama Declinado",
    variante: "Variante del Cambio",
    color: "BLANCAS",
    estado: "EN_ESTUDIO",
    nivel_dominio: "INTERMEDIO",
    clasificacion_uso: "SECUNDARIA",
    fuente_estudio: "Repertoire 1.d4 Boris Avrukh",
    observaciones: "Preparación para torneos cerrados",
    partidas_jugadas: 14,
    victorias: 9,
    empates: 3,
    derrotas: 2,
    rendimiento_pct: 75.0,
    accuracy_promedio: 90.1,
    acpl_promedio: 21.0,
    errores_frecuentes: 1,
    evaluacion_motor: 0.5,
    efectividad: "MUY_EFECTIVA",
    jugadas_clave: "1. d4 d5 2. c4 e6 3. Nc3 Nf6 4. cxd5 exd5",
  },
  {
    id: 6,
    id_atleta: 2,
    codigo_eco: "B12",
    nombre: "Defensa Caro-Kann",
    variante: "Variante Avanzada",
    color: "NEGRAS",
    estado: "EN_REVISION",
    nivel_dominio: "INTERMEDIO",
    clasificacion_uso: "SECUNDARIA",
    fuente_estudio: "Estudio Lichess",
    observaciones: "Agujero teórico detectado en jugada 12",
    partidas_jugadas: 9,
    victorias: 3,
    empates: 2,
    derrotas: 4,
    rendimiento_pct: 44.4,
    accuracy_promedio: 82.4,
    acpl_promedio: 38.5,
    errores_frecuentes: 3,
    evaluacion_motor: -0.8,
    efectividad: "REQUIERE_REVISION",
    jugadas_clave: "1. e4 c6 2. d4 d5 3. e5 Bf5 4. Nf3 e6",
  },
  {
    id: 7,
    id_atleta: 3,
    codigo_eco: "C00",
    nombre: "Defensa Francesa",
    variante: "Variante Tarrasch (3.Nd2)",
    color: "BLANCAS",
    estado: "ACTIVA",
    nivel_dominio: "AVANZADO",
    clasificacion_uso: "PRINCIPAL",
    fuente_estudio: "Grandmaster Repertoire",
    observaciones: "Gran control de peones centrales",
    partidas_jugadas: 16,
    victorias: 12,
    empates: 3,
    derrotas: 1,
    rendimiento_pct: 84.4,
    accuracy_promedio: 92.8,
    acpl_promedio: 19.4,
    errores_frecuentes: 0,
    evaluacion_motor: 0.6,
    efectividad: "MUY_EFECTIVA",
    jugadas_clave: "1. e4 e6 2. d4 d5 3. Nd2 Nf6 4. e5 Nfd7",
  },
];

export async function getAperturas(idAtleta?: number, color?: string): Promise<AperturaRepertorio[]> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
  try {
    const params = new URLSearchParams();
    if (idAtleta) params.append("id_atleta", String(idAtleta));
    if (color && color !== "TODOS") params.append("color", color);

    const qs = params.toString() ? `?${params.toString()}` : "";
    const res = await fetch(`${apiUrl}/aperturas${qs}`, { cache: "no-store" });
    if (res.ok) {
      return await res.json();
    }
  } catch {
    // Fallback a datos mock si el backend no está corriendo
  }
  return APERTURAS_MOCK.filter((a) => {
    const coincideAtleta = !idAtleta || a.id_atleta === idAtleta;
    const coincideColor = !color || color === "TODOS" || a.color === color;
    return coincideAtleta && coincideColor;
  });
}

export async function crearApertura(input: AperturaCrearInput): Promise<AperturaRepertorio | null> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
  try {
    const res = await fetch(`${apiUrl}/aperturas`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(input),
    });
    if (res.ok) {
      return await res.json();
    }
  } catch {
    // Fallback
  }
  return null;
}

