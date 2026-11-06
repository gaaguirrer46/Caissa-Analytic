"use client";

import { useState, useEffect } from "react";
import {
  CalendarCheck,
  Plus,
  Clock,
  CheckCircle2,
  AlertCircle,
  BrainCircuit,
  Filter,
  User,
  Zap,
  Target,
  Flame,
  Award,
  Layers,
  Sparkles,
} from "lucide-react";
import { getPlanes, agregarSesion, PLANES_MOCK } from "@/services/entrenamientos.service";
import { PlanEntrenamientoSemanal, TipoEntrenamiento } from "@/types/entrenamiento.types";
import { ATLETAS_MOCK } from "@/services/atletas.service";

export default function EntrenamientosPage() {
  const [planes, setPlanes] = useState<PlanEntrenamientoSemanal[]>(PLANES_MOCK);
  const [filtroAtleta, setFiltroAtleta] = useState<string>("TODOS");
  const [modalAbierto, setModalAbierto] = useState(false);
  const [planSeleccionadoId, setPlanSeleccionadoId] = useState<number>(2);
  const [cargando, setCargando] = useState(false);
  const [notificacion, setNotificacion] = useState("");

  // Formulario nueva sesión
  const [nuevoTipo, setNuevoTipo] = useState<TipoEntrenamiento>("TACTICA");
  const [nuevoDia, setNuevoDia] = useState<string>("LUNES");
  const [nuevasHoras, setNuevasHoras] = useState<number>(2.0);
  const [nuevasObs, setNuevasObs] = useState<string>("");

  useEffect(() => {
    cargarDatos();
  }, []);

  async function cargarDatos() {
    setCargando(true);
    try {
      const datos = await getPlanes();
      if (datos && datos.length > 0) {
        setPlanes(datos);
      }
    } finally {
      setCargando(false);
    }
  }

  async function handleAgregarSesionSubmit(e: React.FormEvent) {
    e.preventDefault();

    const ok = await agregarSesion({
      id_plan: planSeleccionadoId,
      tipo: nuevoTipo,
      dia_semana: nuevoDia,
      horas_planificadas: Number(nuevasHoras),
      observaciones: nuevasObs,
    });

    if (ok) {
      setNotificacion("Sesión de entrenamiento programada con éxito en SQLite.");
    } else {
      // Agregado local optimista
      setPlanes((prev) =>
        prev.map((p) => {
          if (p.id === planSeleccionadoId) {
            const nueva = {
              id: Date.now(),
              tipo: nuevoTipo,
              dia_semana: nuevoDia,
              horas_planificadas: Number(nuevasHoras),
              horas_ejecutadas: 0.0,
              estado: "PROGRAMADA" as const,
              ejecucion_aprobada: false,
              observaciones: nuevasObs,
            };
            return {
              ...p,
              total_horas_planificadas: p.total_horas_planificadas + Number(nuevasHoras),
              sesiones: [...p.sesiones, nueva],
            };
          }
          return p;
        })
      );
      setNotificacion("Sesión programada en el plan semanal (Modo local).");
    }

    setNuevasObs("");
    setModalAbierto(false);
    setTimeout(() => setNotificacion(""), 4000);
  }

  // Filtrado
  const filtrados = planes.filter((p) => {
    return filtroAtleta === "TODOS" || String(p.id_atleta) === filtroAtleta;
  });

  // Métricas agregadas
  const totalHorasPlan = Math.round(
    planes.reduce((acc, p) => acc + p.total_horas_planificadas, 0)
  );
  const totalHorasEjec = Math.round(
    planes.reduce((acc, p) => acc + p.total_horas_ejecutadas, 0)
  );
  const pctGlobal = totalHorasPlan > 0 ? Math.round((totalHorasEjec / totalHorasPlan) * 100) : 0;
  const totalSesiones = planes.reduce((acc, p) => acc + p.sesiones.length, 0);

  function obtenerColorTipo(tipo: TipoEntrenamiento) {
    switch (tipo) {
      case "TACTICA":
      case "CALCULO":
        return "bg-emerald-500/15 text-emerald-400 border-emerald-500/30";
      case "APERTURAS":
        return "bg-blue-500/15 text-blue-400 border-blue-500/30";
      case "FINALES":
        return "bg-cyan-500/15 text-cyan-400 border-cyan-500/30";
      case "ANALISIS_PARTIDAS":
        return "bg-purple-500/15 text-purple-400 border-purple-500/30";
      case "PREPARACION_COMPETITIVA":
        return "bg-amber-500/15 text-amber-400 border-amber-500/30";
      default:
        return "bg-slate-800 text-slate-300 border-slate-700";
    }
  }

  return (
    <div className="min-h-screen bg-[#070b12] text-slate-100 py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-8 font-sans">
      {/* Notificación flotante */}
      {notificacion && (
        <div className="p-3 rounded-xl bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 text-xs font-mono flex items-center gap-2 shadow-lg animate-fade-in">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <span>{notificacion}</span>
        </div>
      )}

      {/* Header Banner */}
      <div className="p-6 rounded-2xl border border-slate-800/90 bg-gradient-to-r from-[#0d1424] via-[#0a101d] to-[#070b12] flex flex-col sm:flex-row sm:items-center justify-between gap-6 shadow-xl">
        <div className="space-y-2 max-w-2xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono font-medium">
            <CalendarCheck className="w-3.5 h-3.5" /> PLANIFICACIÓN SEMANAL Y ASISTENCIA
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white">
            Planes de Entrenamiento & Tareas
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 leading-relaxed">
            Cronograma semanal por bloques temáticos (Aperturas, Táctica, Finales y Cálculo). Control y certificación de horas entrenadas para la alimentación automática de Objetivos SMART.
          </p>
        </div>

        <button
          onClick={() => setModalAbierto(true)}
          className="flex items-center gap-2 px-5 py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-bold text-xs shadow-lg shadow-emerald-500/20 transition-all hover:scale-[1.02]"
        >
          <Plus className="w-4 h-4" /> Asignar Sesión
        </button>
      </div>

      {/* 4 KPIs de Rendimiento del Entrenamiento */}
      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl border border-slate-800/80 bg-[#0d1424]/70 space-y-1">
          <span className="text-[11px] text-slate-400 font-mono uppercase block">Cumplimiento Global</span>
          <span className="text-3xl font-extrabold font-mono text-emerald-400">{pctGlobal}%</span>
          <p className="text-[10px] text-slate-500 pt-1 border-t border-slate-800/60">Horas aprobadas por DT</p>
        </div>
        <div className="p-5 rounded-2xl border border-slate-800/80 bg-[#0d1424]/70 space-y-1">
          <span className="text-[11px] text-slate-400 font-mono uppercase block">Horas Ejecutadas</span>
          <span className="text-3xl font-extrabold font-mono text-cyan-400">{totalHorasEjec} hrs</span>
          <p className="text-[10px] text-slate-500 pt-1 border-t border-slate-800/60">Registradas en el ciclo</p>
        </div>
        <div className="p-5 rounded-2xl border border-slate-800/80 bg-[#0d1424]/70 space-y-1">
          <span className="text-[11px] text-slate-400 font-mono uppercase block">Horas Planificadas</span>
          <span className="text-3xl font-extrabold font-mono text-white">{totalHorasPlan} hrs</span>
          <p className="text-[10px] text-slate-500 pt-1 border-t border-slate-800/60">Carga semanal asignada</p>
        </div>
        <div className="p-5 rounded-2xl border border-slate-800/80 bg-[#0d1424]/70 space-y-1">
          <span className="text-[11px] text-slate-400 font-mono uppercase block">Sesiones Activas</span>
          <span className="text-3xl font-extrabold font-mono text-amber-400">{totalSesiones} Bloques</span>
          <p className="text-[10px] text-slate-500 pt-1 border-t border-slate-800/60">Táctica, cálculo y teoría</p>
        </div>
      </section>

      {/* Selector de Atleta */}
      <div className="flex items-center justify-between p-4 rounded-2xl border border-slate-800/80 bg-[#0d1424]/60">
        <span className="text-xs font-mono text-slate-400">Filtrar Plan por Atleta:</span>
        <select
          value={filtroAtleta}
          onChange={(e) => setFiltroAtleta(e.target.value)}
          className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-500 font-mono"
        >
          <option value="TODOS">Todos los Atletas Federados</option>
          {ATLETAS_MOCK.map((a) => (
            <option key={a.id} value={String(a.id)}>
              {a.nombre}
            </option>
          ))}
        </select>
      </div>

      {/* Listado de Planes Semanales */}
      <div className="space-y-6">
        {filtrados.map((plan) => (
          <div
            key={plan.id}
            className="p-6 rounded-2xl border border-slate-800/80 bg-[#0d1424]/70 space-y-5 shadow-xl"
          >
            {/* Cabecera del Plan */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="px-2.5 py-0.5 rounded bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 font-mono text-xs font-bold">
                    Semana {plan.semana} • {plan.anio}
                  </span>
                  <h2 className="text-lg font-bold text-white tracking-tight">
                    {plan.nombre_atleta}
                  </h2>
                </div>
                <p className="text-xs text-slate-400">
                  {plan.sesiones.length} sesiones programadas • {plan.total_horas_ejecutadas} de {plan.total_horas_planificadas} horas cumplidas
                </p>
              </div>

              {/* Barra de Progreso del Plan */}
              <div className="flex items-center gap-4 min-w-[220px]">
                <div className="flex-1 space-y-1">
                  <div className="flex justify-between text-xs font-mono">
                    <span className="text-slate-400">Cumplimiento:</span>
                    <span className="text-emerald-400 font-bold">{plan.cumplimiento_pct}%</span>
                  </div>
                  <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden border border-slate-800">
                    <div
                      className="bg-gradient-to-r from-emerald-500 to-teal-400 h-full rounded-full transition-all"
                      style={{ width: `${Math.min(plan.cumplimiento_pct, 100)}%` }}
                    />
                  </div>
                </div>

                <span className="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-[11px] font-mono text-slate-300">
                  {plan.cumplimiento_pct >= 70 ? "Al Día ✓" : "Pendiente ⏳"}
                </span>
              </div>
            </div>

            {/* Grid de Sesiones de la Semana */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {plan.sesiones.map((sesion) => (
                <div
                  key={sesion.id}
                  className="p-4 rounded-xl bg-[#070b12] border border-slate-800/80 hover:border-slate-700 transition-all space-y-2 flex flex-col justify-between"
                >
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold border ${obtenerColorTipo(sesion.tipo)}`}>
                        {sesion.tipo.replace("_", " ")}
                      </span>
                      <span className="text-xs font-mono font-bold text-slate-300">
                        {sesion.dia_semana}
                      </span>
                    </div>

                    <p className="text-xs text-slate-300 leading-snug">
                      {sesion.observaciones || "Sesión de estudio técnico"}
                    </p>
                  </div>

                  <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between text-[11px] font-mono">
                    <span className="text-slate-400">
                      {sesion.horas_ejecutadas} / {sesion.horas_planificadas} hrs
                    </span>
                    <span
                      className={`font-semibold ${
                        sesion.estado === "EJECUTADA" ? "text-emerald-400" : "text-amber-400"
                      }`}
                    >
                      {sesion.estado === "EJECUTADA" ? "Aprobada ✓" : "Programada"}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Modal Programar Sesión */}
      {modalAbierto && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="w-full max-w-lg rounded-2xl border border-slate-800 bg-[#0d1424] p-6 shadow-2xl space-y-5">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <CalendarCheck className="w-5 h-5 text-emerald-400" /> Programar Sesión de Entrenamiento
              </h2>
              <button
                onClick={() => setModalAbierto(false)}
                className="text-slate-400 hover:text-white text-sm font-bold"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleAgregarSesionSubmit} className="space-y-4 text-xs font-mono">
              <div>
                <label className="block text-slate-400 mb-1">Plan Semanal del Atleta:</label>
                <select
                  value={planSeleccionadoId}
                  onChange={(e) => setPlanSeleccionadoId(Number(e.target.value))}
                  className="w-full bg-[#070b12] border border-slate-800 rounded-xl p-2.5 text-slate-200 focus:outline-none focus:border-emerald-500"
                >
                  {planes.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.nombre_atleta} — Semana {p.semana} ({p.anio})
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1">Bloque Temático:</label>
                  <select
                    value={nuevoTipo}
                    onChange={(e) => setNuevoTipo(e.target.value as TipoEntrenamiento)}
                    className="w-full bg-[#070b12] border border-slate-800 rounded-xl p-2.5 text-slate-200 focus:outline-none focus:border-emerald-500"
                  >
                    <option value="TACTICA">Táctica & Ejercicios</option>
                    <option value="CALCULO">Cálculo de Variantes</option>
                    <option value="APERTURAS">Aperturas & Repertorio</option>
                    <option value="FINALES">Finales Teóricos</option>
                    <option value="ANALISIS_PARTIDAS">Análisis de Partidas</option>
                    <option value="ESTRATEGIA">Estrategia & Posicional</option>
                    <option value="PREPARACION_COMPETITIVA">Simulacro Competitivo</option>
                  </select>
                </div>

                <div>
                  <label className="block text-slate-400 mb-1">Día de la Semana:</label>
                  <select
                    value={nuevoDia}
                    onChange={(e) => setNuevoDia(e.target.value)}
                    className="w-full bg-[#070b12] border border-slate-800 rounded-xl p-2.5 text-slate-200 focus:outline-none focus:border-emerald-500"
                  >
                    <option value="LUNES">Lunes</option>
                    <option value="MARTES">Martes</option>
                    <option value="MIERCOLES">Miércoles</option>
                    <option value="JUEVES">Jueves</option>
                    <option value="VIERNES">Viernes</option>
                    <option value="SABADO">Sábado</option>
                    <option value="DOMINGO">Domingo</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Horas Planificadas:</label>
                <input
                  type="number"
                  step="0.5"
                  min="0.5"
                  max="8.0"
                  value={nuevasHoras}
                  onChange={(e) => setNuevasHoras(Number(e.target.value))}
                  required
                  className="w-full bg-[#070b12] border border-slate-800 rounded-xl p-2.5 text-slate-200 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Observaciones / Tarea Específica:</label>
                <input
                  type="text"
                  placeholder="Ej: Resolución de 40 problemas de cálculo en Lichess / Chess.com"
                  value={nuevasObs}
                  onChange={(e) => setNuevasObs(e.target.value)}
                  className="w-full bg-[#070b12] border border-slate-800 rounded-xl p-2.5 text-slate-200 focus:outline-none focus:border-emerald-500 font-sans"
                />
              </div>

              <div className="pt-3 border-t border-slate-800 flex items-center justify-end gap-3 font-sans">
                <button
                  type="button"
                  onClick={() => setModalAbierto(false)}
                  className="px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 text-xs font-semibold"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-bold text-xs"
                >
                  Guardar Sesión en SQLite
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

