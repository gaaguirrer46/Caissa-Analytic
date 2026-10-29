export type ResultadoPartida = "1-0" | "0-1" | "1/2-1/2";
export type ColorPartida = "BLANCAS" | "NEGRAS";
export type FuentePartida = "PGN" | "CHESS_COM" | "LICHESS" | "MANUAL" | "CHESSBASE";

export interface Partida {
  id: number;
  id_atleta: number;
  evento: string;
  sitio?: string;
  fecha: string;
  ronda?: string;
  blancas: string;
  negras: string;
  resultado: ResultadoPartida;
  color_atleta: ColorPartida;
  eco?: string;
  apertura?: string;
  elo_blancas?: number;
  elo_negras?: number;
  pgn: string;
  precision_atleta?: number;
  errores_graves?: number;
  fuente: FuentePartida;
}

