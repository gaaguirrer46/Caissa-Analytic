export interface MotorStockfishConfig {
  version: string;
  profundidad_defecto: number;
  hilos_cpu: number;
  hash_mb: number;
}

export interface ConfiguracionSistema {
  maximo_atletas_por_entrenador: number;
  minimo_entrenadores_por_atleta: number;
  maximo_entrenadores_por_atleta: number;
  permitir_autoevaluacion: boolean;
  rangos_evaluacion: Record<string, [number, number, number]>;
  secciones_autorizadas_invitado: string[];
  actualizado_por: string;
  fecha_actualizacion: string;
  nombre_club?: string;
  federacion?: string;
  temporada_activa?: string;
  motor_stockfish?: MotorStockfishConfig;
}

export interface ConfiguracionActualizarInput {
  maximo_atletas_por_entrenador: number;
  minimo_entrenadores_por_atleta: number;
  maximo_entrenadores_por_atleta: number;
  permitir_autoevaluacion: boolean;
  rangos_evaluacion: Record<string, number[]>;
  secciones_autorizadas_invitado: string[];
  actualizado_por?: string;
}
