export type TipoEntrenamiento =
  | "APERTURAS"
  | "MEDIO_JUEGO"
  | "FINALES"
  | "TACTICA"
  | "ESTRATEGIA"
  | "CALCULO"
  | "VISUALIZACION"
  | "ANALISIS_PARTIDAS"
  | "CLASES_TEORICAS"
  | "PREPARACION_FISICA"
  | "PSICOLOGICA_DEPORTIVA"
  | "PREPARACION_COMPETITIVA";

export type EstadoSesion =
  | "PROGRAMADA"
  | "REPROGRAMADA"
  | "CANCELADA"
  | "EJECUTADA";

export interface SesionEntrenamiento {
  id: number;
  tipo: TipoEntrenamiento;
  dia_semana: string;
  horas_planificadas: number;
  horas_ejecutadas: number;
  estado: EstadoSesion;
  ejecucion_aprobada: boolean;
  observaciones?: string;
}

export interface PlanEntrenamientoSemanal {
  id: number;
  id_atleta: number;
  nombre_atleta: string;
  semana: number;
  anio: number;
  total_horas_planificadas: number;
  total_horas_ejecutadas: number;
  cumplimiento_pct: number;
  sesiones: SesionEntrenamiento[];
}

export interface SesionCrearInput {
  id_plan: number;
  tipo: TipoEntrenamiento;
  dia_semana: string;
  horas_planificadas: number;
  observaciones?: string;
}

