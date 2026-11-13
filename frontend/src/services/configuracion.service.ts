import {
  ConfiguracionSistema,
  ConfiguracionActualizarInput,
} from "@/types/configuracion.types";

export const CONFIGURACION_MOCK: ConfiguracionSistema = {
  maximo_atletas_por_entrenador: 40,
  minimo_entrenadores_por_atleta: 1,
  maximo_entrenadores_por_atleta: 3,
  permitir_autoevaluacion: true,
  rangos_evaluacion: {
    ACCURACY: [92.0, 82.0, 70.0],
    CUMPLIMIENTO_ENTRENAMIENTO: [90.0, 75.0, 60.0],
    CUMPLIMIENTO_OBJETIVOS: [85.0, 70.0, 50.0],
    ACPL: [20.0, 35.0, 50.0],
    ASISTENCIA: [95.0, 85.0, 75.0],
    RENDIMIENTO_POR_APERTURA: [70.0, 55.0, 45.0],
    GESTION_DEL_TIEMPO: [85.0, 70.0, 55.0],
  },
  secciones_autorizadas_invitado: [
    "perfil_publico",
    "ranking",
    "resumen_equipo",
  ],
  actualizado_por: "entrenador.magnus@caissa.org",
  fecha_actualizacion: new Date().toISOString(),
  nombre_club: "Caissa Analytic Club & Performance Center",
  federacion: "FIDE (Federación Internacional de Ajedrez)",
  temporada_activa: "Ciclo Federativo 2026-I",
  motor_stockfish: {
    version: "Stockfish 16.1 NNUE",
    profundidad_defecto: 18,
    hilos_cpu: 4,
    hash_mb: 256,
  },
};

export async function getConfiguracion(): Promise<ConfiguracionSistema> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
  try {
    const res = await fetch(`${apiUrl}/configuracion`, { cache: "no-store" });
    if (res.ok) {
      return await res.json();
    }
  } catch {
    // Fallback
  }
  return CONFIGURACION_MOCK;
}

export async function actualizarConfiguracion(
  input: ConfiguracionActualizarInput
): Promise<boolean> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
  try {
    const res = await fetch(`${apiUrl}/configuracion`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(input),
    });
    return res.ok;
  } catch {
    return false;
  }
}

export async function configurarAccesoInvitado(
  secciones: string[]
): Promise<boolean> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
  try {
    const res = await fetch(`${apiUrl}/configuracion/acceso-invitado`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ secciones, id_usuario: 1 }),
    });
    return res.ok;
  } catch {
    return false;
  }
}
