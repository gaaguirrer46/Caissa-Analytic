import { ObjetivoSmart, ObjetivoCrearInput } from "@/types/objetivo.types";

export const OBJETIVOS_MOCK: ObjetivoSmart[] = [
  {
    id: 1,
    id_atleta: 2,
    nombre_atleta: "Carlos Daniel Morales",
    descripcion: "Superar barrera de 2,100 ELO FIDE Clásico",
    indicador_meta: "RATING",
    valor_meta: 2100,
    rating_actual: 2045,
    rating_meta: 2100,
    fecha_inicio: "2026-08-01",
    fecha_limite: "2026-11-30",
    porcentaje_avance: 81.0,
    estado: "EN_PROCESO",
    color_semaforo: "AMARILLO",
    supera_umbral_temporal: true,
  },
  {
    id: 2,
    id_atleta: 3,
    nombre_atleta: "Sofía Valentina Castro",
    descripcion: "40 Horas de Entrenamiento Táctico Mensual",
    indicador_meta: "HORAS_ENTRENADAS",
    valor_meta: 40,
    rating_actual: 1920,
    rating_meta: 1920,
    fecha_inicio: "2026-10-01",
    fecha_limite: "2026-10-31",
    porcentaje_avance: 85.0,
    estado: "EN_PROCESO",
    color_semaforo: "AMARILLO",
    supera_umbral_temporal: true,
  },
  {
    id: 3,
    id_atleta: 4,
    nombre_atleta: "Alejandro José Rivas",
    descripcion: "Consolidar 1ra Norma de Maestro Nacional",
    indicador_meta: "TORNEOS",
    valor_meta: 1,
    rating_actual: 2180,
    rating_meta: 2200,
    fecha_inicio: "2026-01-01",
    fecha_limite: "2026-10-25",
    porcentaje_avance: 100.0,
    estado: "FINALIZADO",
    color_semaforo: "VERDE",
    supera_umbral_temporal: true,
  },
  {
    id: 4,
    id_atleta: 1,
    nombre_atleta: "Garry Kasparov Jr.",
    descripcion: "Resolver 300 problemas de finales de peones y torres",
    indicador_meta: "TAREAS",
    valor_meta: 300,
    rating_actual: 2150,
    rating_meta: 2200,
    fecha_inicio: "2026-09-01",
    fecha_limite: "2026-12-15",
    porcentaje_avance: 45.0,
    estado: "RETRASADO",
    color_semaforo: "ROJO",
    supera_umbral_temporal: false,
  },
];

export async function getObjetivos(idAtleta?: number): Promise<ObjetivoSmart[]> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
  try {
    const url = idAtleta ? `${apiUrl}/objetivos?id_atleta=${idAtleta}` : `${apiUrl}/objetivos`;
    const res = await fetch(url, { cache: "no-store" });
    if (res.ok) {
      const data = await res.json();
      return data;
    }
  } catch {
    // Fallback a mock si la API no está levantada en desarrollo
  }
  return idAtleta
    ? OBJETIVOS_MOCK.filter((o) => o.id_atleta === idAtleta)
    : OBJETIVOS_MOCK;
}

export async function crearObjetivo(input: ObjetivoCrearInput): Promise<ObjetivoSmart | null> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
  try {
    const res = await fetch(`${apiUrl}/objetivos`, {
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

