export type TipoOperacion = "CREAR" | "MODIFICAR" | "ELIMINAR";

export interface RegistroAuditoria {
  id: number;
  usuario: string;
  fecha_hora: string;
  entidad_afectada: string;
  tipo_operacion: TipoOperacion;
  campo_modificado: string;
  valor_anterior: string | null;
  valor_nuevo: string | null;
}

export interface ResultadoIntegridad {
  estado: "OPTIMO" | "ADVERTENCIA" | "CRITICO";
  integridad_sqlite: string;
  snapshot_hash: string;
  total_registros_auditados: number;
  atletas_validados: number;
  partidas_validadas: number;
  anomalias_detectadas: number;
  detalles: string[];
  fecha_verificacion: string;
}

export interface FiltrosAuditoria {
  entidad?: string;
  usuario?: string;
  tipo_operacion?: string;
  limite?: number;
}
