export type ColorApertura = "BLANCAS" | "NEGRAS";
export type EstadoApertura = "EN_ESTUDIO" | "ACTIVA" | "EN_REVISION" | "DESCARTADA";
export type NivelDominio = "INICIAL" | "INTERMEDIO" | "AVANZADO";
export type ClasificacionUso = "PRINCIPAL" | "SECUNDARIA";
export type EfectividadApertura = "MUY_EFECTIVA" | "EFECTIVA" | "REQUIERE_REVISION";

export interface AperturaRepertorio {
  id: number;
  id_atleta: number;
  codigo_eco: string;
  nombre: string;
  variante?: string;
  color: ColorApertura;
  estado: EstadoApertura;
  nivel_dominio: NivelDominio;
  clasificacion_uso: ClasificacionUso;
  fuente_estudio?: string;
  observaciones?: string;
  partidas_jugadas: number;
  victorias: number;
  empates: number;
  derrotas: number;
  rendimiento_pct: number;
  accuracy_promedio: number;
  acpl_promedio: number;
  errores_frecuentes: number;
  evaluacion_motor: number;
  efectividad: EfectividadApertura;
  jugadas_clave?: string;
}

export interface AperturaCrearInput {
  id_atleta: number;
  codigo_eco: string;
  nombre: string;
  variante?: string;
  color: ColorApertura;
  estado?: EstadoApertura;
  nivel_dominio?: NivelDominio;
  fuente_estudio?: string;
  observaciones?: string;
  clasificacion_uso?: ClasificacionUso;
}

