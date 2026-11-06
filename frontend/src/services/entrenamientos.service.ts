import { PlanEntrenamientoSemanal, SesionCrearInput } from "@/types/entrenamiento.types";

export const PLANES_MOCK: PlanEntrenamientoSemanal[] = [
  {
    id: 2,
    id_atleta: 2,
    nombre_atleta: "Carlos Daniel Morales",
    semana: 44,
    anio: 2026,
    total_horas_planificadas: 11.0,
    total_horas_ejecutadas: 8.0,
    cumplimiento_pct: 72.7,
    sesiones: [
      {
        id: 3,
        tipo: "APERTURAS",
        dia_semana: "LUNES",
        horas_planificadas: 2.5,
        horas_ejecutadas: 2.5,
        estado: "EJECUTADA",
        ejecucion_aprobada: true,
        observaciones: "Profundización en Siciliana Najdorf con 6.Be3",
      },
      {
        id: 4,
        tipo: "CALCULO",
        dia_semana: "MARTES",
        horas_planificadas: 2.0,
        horas_ejecutadas: 2.0,
        estado: "EJECUTADA",
        ejecucion_aprobada: true,
        observaciones: "Cálculo de variantes forzadas y sacrificios posicionales",
      },
      {
        id: 5,
        tipo: "FINALES",
        dia_semana: "JUEVES",
        horas_planificadas: 1.5,
        horas_ejecutadas: 1.5,
        estado: "EJECUTADA",
        ejecucion_aprobada: true,
        observaciones: "Técnica de finales de peones y casillas clave",
      },
      {
        id: 6,
        tipo: "ANALISIS_PARTIDAS",
        dia_semana: "VIERNES",
        horas_planificadas: 2.0,
        horas_ejecutadas: 2.0,
        estado: "EJECUTADA",
        ejecucion_aprobada: true,
        observaciones: "Revisión técnica de la partida contra el Maestro FIDE",
      },
      {
        id: 7,
        tipo: "PREPARACION_COMPETITIVA",
        dia_semana: "SABADO",
        horas_planificadas: 3.0,
        horas_ejecutadas: 0.0,
        estado: "PROGRAMADA",
        ejecucion_aprobada: false,
        observaciones: "Simulacro de torneo a 90+30 con reloj oficial",
      },
    ],
  },
  {
    id: 3,
    id_atleta: 3,
    nombre_atleta: "Sofía Valentina Castro",
    semana: 44,
    anio: 2026,
    total_horas_planificadas: 7.5,
    total_horas_ejecutadas: 5.5,
    cumplimiento_pct: 73.3,
    sesiones: [
      {
        id: 8,
        tipo: "TACTICA",
        dia_semana: "LUNES",
        horas_planificadas: 2.0,
        horas_ejecutadas: 2.0,
        estado: "EJECUTADA",
        ejecucion_aprobada: true,
        observaciones: "Ejercicios de clavadas y ataques dobles",
      },
      {
        id: 9,
        tipo: "APERTURAS",
        dia_semana: "MIERCOLES",
        horas_planificadas: 2.0,
        horas_ejecutadas: 2.0,
        estado: "EJECUTADA",
        ejecucion_aprobada: true,
        observaciones: "Líneas sólidas de la Apertura Italiana",
      },
      {
        id: 10,
        tipo: "CLASES_TEORICAS",
        dia_semana: "JUEVES",
        horas_planificadas: 1.5,
        horas_ejecutadas: 1.5,
        estado: "EJECUTADA",
        ejecucion_aprobada: true,
        observaciones: "Estructuras Carlsbad y cadenas de peones",
      },
      {
        id: 11,
        tipo: "CALCULO",
        dia_semana: "VIERNES",
        horas_planificadas: 2.0,
        horas_ejecutadas: 0.0,
        estado: "PROGRAMADA",
        ejecucion_aprobada: false,
        observaciones: "Entrenamiento en visualización a ciegas",
      },
    ],
  },
];

export async function getPlanes(idAtleta?: number, semana?: number): Promise<PlanEntrenamientoSemanal[]> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
  try {
    const params = new URLSearchParams();
    if (idAtleta) params.append("id_atleta", String(idAtleta));
    if (semana) params.append("semana", String(semana));

    const qs = params.toString() ? `?${params.toString()}` : "";
    const res = await fetch(`${apiUrl}/entrenamientos${qs}`, { cache: "no-store" });
    if (res.ok) {
      return await res.json();
    }
  } catch {
    // Fallback
  }
  return PLANES_MOCK;
}

export async function agregarSesion(input: SesionCrearInput): Promise<boolean> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
  try {
    const res = await fetch(`${apiUrl}/entrenamientos/sesion`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(input),
    });
    return res.ok;
  } catch {
    return false;
  }
}

