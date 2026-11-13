export type PeriodoEvaluacion = "TORNEO" | "MES" | "MESOCICLO" | "ANIO";

export type TipoIndicadorEvaluacion =
  | "CUMPLIMIENTO_PLAN"
  | "DESARROLLO_TECNICO_TACTICO"
  | "PROGRESO_RATING"
  | "CUMPLIMIENTO_OBJETIVOS_SMART"
  | "ORGANIZACION"
  | "GESTION_COMPETENCIAS"
  | "DESARROLLO_APERTURAS"
  | "SEGUIMIENTO_INDIVIDUAL";

export interface EvaluacionAtleta {
  id: number;
  id_atleta: number;
  nombre_atleta: string;
  id_entrenador: number;
  periodo: PeriodoEvaluacion;
  referencia_periodo: string;
  fecha_realizacion: string;
  promedio: number;
  calificaciones: Record<string, number>;
  fortalezas: string;
  aspectos_por_mejorar: string;
  recomendaciones: string;
  es_autoevaluacion: boolean;
}

export interface ResumenEvaluacionAtleta {
  id_atleta: number;
  nombre_atleta: string;
  cantidad_evaluaciones: number;
  ultima_evaluacion: string | null;
  promedio_general: number;
  promedio_por_indicador: Record<string, number>;
  areas_de_mejora: string[];
  variacion_ultimo_ciclo: number;
  variaciones_por_indicador: Record<string, number>;
  recomendaciones_consolidadas: string[];
}

export interface EvaluacionCrearInput {
  id_atleta: number;
  id_entrenador?: number;
  periodo: PeriodoEvaluacion;
  referencia_periodo: string;
  fecha_realizacion?: string;
  calificaciones: Record<string, number>;
  fortalezas?: string;
  aspectos_por_mejorar?: string;
  recomendaciones?: string;
  es_autoevaluacion?: boolean;
}
