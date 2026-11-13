export interface Rating {
  clasicas?: number;
  rapidas?: number;
  blitz?: number;
  chess_com?: number;
  lichess?: number;
  fecha_actualizacion?: string;
}

export interface PerfilHistorico {
  id: number;
  id_atleta: number;
  anio: number;
  torneo?: string;
  rating: Rating;
  observaciones?: string;
}

export interface Atleta {
  id: number;
  nombre: string;
  fecha_nacimiento: string; // ISO date YYYY-MM-DD
  sexo: "M" | "F";
  identidad_opcional?: string;
  fotografia_opcional?: string;
  federacion?: string;
  universidad?: string;
  institucion?: string;
  carrera?: string;
  categorias: number[];
  clubs: string[];
  entrenadores_asignados: number[];
  rating_actual: Rating;
  historial: PerfilHistorico[];
  activo: boolean;
}

export function calcularEdad(fechaNacimiento: string): number {
  const hoy = new Date();
  const nac = new Date(fechaNacimiento);
  let edad = hoy.getFullYear() - nac.getFullYear();
  const m = hoy.getMonth() - nac.getMonth();
  if (m < 0 || (m === 0 && hoy.getDate() < nac.getDate())) {
    edad--;
  }
  return edad;
}

