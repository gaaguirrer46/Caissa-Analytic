import {
  EvaluacionAtleta,
  ResumenEvaluacionAtleta,
  EvaluacionCrearInput,
} from "@/types/evaluacion.types";

export const EVALUACIONES_MOCK: EvaluacionAtleta[] = [
  {
    id: 2,
    id_atleta: 1,
    nombre_atleta: "Garry Kasparov Jr.",
    id_entrenador: 1,
    periodo: "MES",
    referencia_periodo: "Evaluación Mensual - Octubre 2026",
    fecha_realizacion: "2026-10-31",
    promedio: 9.25,
    calificaciones: {
      CUMPLIMIENTO_PLAN: 10,
      DESARROLLO_TECNICO_TACTICO: 9,
      PROGRESO_RATING: 9,
      CUMPLIMIENTO_OBJETIVOS_SMART: 9,
      ORGANIZACION: 9,
      GESTION_COMPETENCIAS: 9,
      DESARROLLO_APERTURAS: 9,
      SEGUIMIENTO_INDIVIDUAL: 10,
    },
    fortalezas:
      "Excelente preparación en la Defensa Siciliana (ECO B90) y cálculo preciso en complicaciones tácticas complejas. Gran recuperación psicológica tras derrotas.",
    aspectos_por_mejorar:
      "Gestión del tiempo en la jugada 30-38 previo al primer control. Apuros innecesarios que provocan descuidos tácticos.",
    recomendaciones:
      "Mantener al menos 15 minutos en el reloj antes de la jugada 35. Entrenar ejercicios de finales de damas con incremento de 30 segundos.",
    es_autoevaluacion: false,
  },
  {
    id: 1,
    id_atleta: 1,
    nombre_atleta: "Garry Kasparov Jr.",
    id_entrenador: 1,
    periodo: "MESOCICLO",
    referencia_periodo: "Mesociclo Fuerza Táctica - Sep 2026",
    fecha_realizacion: "2026-09-30",
    promedio: 8.63,
    calificaciones: {
      CUMPLIMIENTO_PLAN: 9,
      DESARROLLO_TECNICO_TACTICO: 9,
      PROGRESO_RATING: 8,
      CUMPLIMIENTO_OBJETIVOS_SMART: 8,
      ORGANIZACION: 9,
      GESTION_COMPETENCIAS: 8,
      DESARROLLO_APERTURAS: 9,
      SEGUIMIENTO_INDIVIDUAL: 9,
    },
    fortalezas:
      "Dominio agresivo de la iniciativa con piezas blancas en esquemas Siciliana Najdorf. Alta velocidad de cálculo en posiciones dinámicas.",
    aspectos_por_mejorar:
      "Paciencia en posiciones profilácticas cerradas. Tendencia a forzar simplificaciones prematuras cuando el rival se repliega.",
    recomendaciones:
      "Estudiar partidas clásicas de Petrosian y Karpov sobre profilaxis y maniobras de piezas menores sin contacto directo.",
    es_autoevaluacion: false,
  },
  {
    id: 3,
    id_atleta: 2,
    nombre_atleta: "Carlos Daniel Morales",
    id_entrenador: 1,
    periodo: "MES",
    referencia_periodo: "Evaluación Mensual - Octubre 2026",
    fecha_realizacion: "2026-10-30",
    promedio: 7.88,
    calificaciones: {
      CUMPLIMIENTO_PLAN: 8,
      DESARROLLO_TECNICO_TACTICO: 7,
      PROGRESO_RATING: 8,
      CUMPLIMIENTO_OBJETIVOS_SMART: 8,
      ORGANIZACION: 9,
      GESTION_COMPETENCIAS: 7,
      DESARROLLO_APERTURAS: 8,
      SEGUIMIENTO_INDIVIDUAL: 8,
    },
    fortalezas:
      "Sólido juego posicional en aperturas de peón dama (1.d4). Comprensión clara de estructuras Carlsbad e islas de peones.",
    aspectos_por_mejorar:
      "Agresividad táctica en momentos críticos y cálculo de líneas forzadas agudas. Dificultad para castigar jugadas pasivas del oponente.",
    recomendaciones:
      "Incrementar volumen de resolución de ejercicios tácticos de nivel 2200+ (mínimo 45 minutos diarios de cálculo forzado).",
    es_autoevaluacion: false,
  },
  {
    id: 4,
    id_atleta: 3,
    nombre_atleta: "Sofía Valentina Castro",
    id_entrenador: 1,
    periodo: "TORNEO",
    referencia_periodo: "Post-Torneo Nacional Universitario 2026",
    fecha_realizacion: "2026-10-25",
    promedio: 7.88,
    calificaciones: {
      CUMPLIMIENTO_PLAN: 8,
      DESARROLLO_TECNICO_TACTICO: 7,
      PROGRESO_RATING: 8,
      CUMPLIMIENTO_OBJETIVOS_SMART: 8,
      ORGANIZACION: 8,
      GESTION_COMPETENCIAS: 7,
      DESARROLLO_APERTURAS: 8,
      SEGUIMIENTO_INDIVIDUAL: 8,
    },
    fortalezas:
      "Gran inventiva estratégica en defensas asimétricas (Defensa Francesa variante Winawer). Tenacidad en posiciones inferiores.",
    aspectos_por_mejorar:
      "Finales teóricos de torres y peones con peón de ventaja. Necesita mecanizar el método de Lucena y puente de Philidor con total seguridad.",
    recomendaciones:
      "Simulaciones intensivas de finales de torres contra el módulo Stockfish 16 con posiciones de Dvoretsky.",
    es_autoevaluacion: false,
  },
  {
    id: 5,
    id_atleta: 4,
    nombre_atleta: "Alejandro José Rivas",
    id_entrenador: 1,
    periodo: "MES",
    referencia_periodo: "Evaluación Mensual - Octubre 2026",
    fecha_realizacion: "2026-10-29",
    promedio: 8.88,
    calificaciones: {
      CUMPLIMIENTO_PLAN: 9,
      DESARROLLO_TECNICO_TACTICO: 9,
      PROGRESO_RATING: 9,
      CUMPLIMIENTO_OBJETIVOS_SMART: 9,
      ORGANIZACION: 8,
      GESTION_COMPETENCIAS: 9,
      DESARROLLO_APERTURAS: 9,
      SEGUIMIENTO_INDIVIDUAL: 9,
    },
    fortalezas:
      "Visión combinatoria sobresaliente en el medio juego. Excelente preparación en la Apertura Española y Gambito de Dama Aceptado.",
    aspectos_por_mejorar:
      "Constancia en el registro de horas de entrenamiento personal y análisis riguroso de partidas perdidas.",
    recomendaciones:
      "Completar la bitácora semanal en Caissa Analytic antes del domingo a las 20:00 sin excepción.",
    es_autoevaluacion: false,
  },
];

export async function getEvaluaciones(
  idAtleta?: number,
  periodo?: string
): Promise<EvaluacionAtleta[]> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
  try {
    const params = new URLSearchParams();
    if (idAtleta) params.append("id_atleta", String(idAtleta));
    if (periodo) params.append("periodo", periodo);

    const qs = params.toString() ? `?${params.toString()}` : "";
    const res = await fetch(`${apiUrl}/evaluaciones${qs}`, { cache: "no-store" });
    if (res.ok) {
      return await res.json();
    }
  } catch {
    // Fallback
  }

  let filtradas = EVALUACIONES_MOCK;
  if (idAtleta) {
    filtradas = filtradas.filter((e) => e.id_atleta === idAtleta);
  }
  if (periodo) {
    filtradas = filtradas.filter((e) => e.periodo === periodo);
  }
  return filtradas;
}

export async function getResumenEvaluaciones(
  idAtleta: number
): Promise<ResumenEvaluacionAtleta | null> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
  try {
    const res = await fetch(`${apiUrl}/evaluaciones/resumen/${idAtleta}`, {
      cache: "no-store",
    });
    if (res.ok) {
      return await res.json();
    }
  } catch {
    // Fallback
  }

  const evals = EVALUACIONES_MOCK.filter((e) => e.id_atleta === idAtleta);
  if (evals.length === 0) return null;

  const ultima = evals[0];
  return {
    id_atleta: idAtleta,
    nombre_atleta: ultima.nombre_atleta,
    cantidad_evaluaciones: evals.length,
    ultima_evaluacion: ultima.fecha_realizacion,
    promedio_general: ultima.promedio,
    promedio_por_indicador: ultima.calificaciones,
    areas_de_mejora: ["DESARROLLO_TECNICO_TACTICO", "GESTION_COMPETENCIAS"],
    variacion_ultimo_ciclo: 0.62,
    variaciones_por_indicador: {
      CUMPLIMIENTO_PLAN: 1.0,
      DESARROLLO_TECNICO_TACTICO: 0.0,
      PROGRESO_RATING: 1.0,
      CUMPLIMIENTO_OBJETIVOS_SMART: 1.0,
      ORGANIZACION: 0.0,
      GESTION_COMPETENCIAS: 1.0,
      DESARROLLO_APERTURAS: 0.0,
      SEGUIMIENTO_INDIVIDUAL: 1.0,
    },
    recomendaciones_consolidadas: [
      ultima.recomendaciones,
      evals[1]?.recomendaciones || "Mantener disciplina en el plan semanal.",
    ],
  };
}

export async function crearEvaluacion(input: EvaluacionCrearInput): Promise<boolean> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
  try {
    const res = await fetch(`${apiUrl}/evaluaciones`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(input),
    });
    return res.ok;
  } catch {
    return false;
  }
}
