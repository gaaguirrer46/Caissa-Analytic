export type TipoIndicadorAvance =
  | "HORAS_ENTRENADAS"
  | "RATING"
  | "TAREAS"
  | "TORNEOS"
  | "MEDALLAS";

export type EstadoObjetivo =
  | "PENDIENTE_APROBACION"
  | "EN_PROCESO"
  | "RETRASADO"
  | "FINALIZADO";

export interface ObjetivoSmart {
  id: number;
  id_atleta: number;
  descripcion: string;
  indicador_meta: TipoIndicadorAvance;
  valor_meta: number;
  rating_actual: number;
  rating_meta: number;
  fecha_inicio: string;
  fecha_limite: string;
  porcentaje_avance: number;
  estado: EstadoObjetivo;
  color_semaforo: "VERDE" | "AMARILLO" | "ROJO" | "GRIS";
  supera_umbral_temporal: boolean;
  nombre_atleta?: string;
}

export interface ObjetivoCrearInput {
  id_atleta: number;
  descripcion: string;
  indicador_meta: TipoIndicadorAvance;
  valor_meta: number;
  rating_actual: number;
  rating_meta: number;
  fecha_inicio?: string;
  fecha_limite: string;
}

