"use client";

import { useState, useEffect } from "react";
import {
  Target,
  Plus,
  Clock,
  TrendingUp,
  Award,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  HelpCircle,
  Sparkles,
  BarChart3,
  Calendar,
  User,
  Shield,
  Zap,
} from "lucide-react";
import { getObjetivos, crearObjetivo, OBJETIVOS_MOCK } from "@/services/objetivos.service";
import { ObjetivoSmart, TipoIndicadorAvance } from "@/types/objetivo.types";
import { ATLETAS_MOCK } from "@/services/atletas.service";

export default function ObjetivosPage() {
  const [objetivos, setObjetivos] = useState<ObjetivoSmart[]>(OBJETIVOS_MOCK);
  const [filtroEstado, setFiltroEstado] = useState<string>("TODOS");
  const [filtroAtleta, setFiltroAtleta] = useState<string>("TODOS");
  const [modalAbierto, setModalAbierto] = useState(false);
  const [cargando, setCargando] = useState(false);

  // Formulario nuevo objetivo
  const [nuevoAtletaId, setNuevoAtletaId] = useState<number>(2);
  const [nuevaDescripcion, setNuevaDescripcion] = useState("");
  const [nuevoIndicador, setNuevoIndicador] = useState<TipoIndicadorAvance>("RATING");
  const [nuevoValorMeta, setNuevoValorMeta] = useState<number>(2100);
  const [nuevoRatingActual, setNuevoRatingActual] = useState<number>(2045);
  const [nuevaFechaLimite, setNuevaFechaLimite] = useState("2026-12-31");

  useEffect(() => {
    cargarDatos();
  }, []);

  async function cargarDatos() {
    setCargando(true);
    try {
      const data = await getObjetivos();
      if (data && data.length > 0) {
        setObjetivos(data);
      }
    } finally {
      setCargando(false);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!nuevaDescripcion.trim()) return;

    const res = await crearObjetivo({
      id_atleta: nuevoAtletaId,
      descripcion: nuevaDescripcion,
      indicador_meta: nuevoIndicador,
      valor_meta: Number(nuevoValorMeta),
      rating_actual: Number(nuevoRatingActual),
      rating_meta: Number(nuevoValorMeta),
      fecha_limite: nuevaFechaLimite,
    });

    if (res) {
      setObjetivos((prev) => [res, ...prev]);
    } else {
      // Agregado local optimista
      const atletaObj = ATLETAS_MOCK.find((a) => a.id === nuevoAtletaId);
      const localNuevo: ObjetivoSmart = {
        id: Date.now(),
        id_atleta: nuevoAtletaId,
        nombre_atleta: atletaObj ? atletaObj.nombre : "Atleta Federado",
        descripcion: nuevaDescripcion,
        indicador_meta: nuevoIndicador,
        valor_meta: Number(nuevoValorMeta),
        rating_actual: Number(nuevoRatingActual),
        rating_meta: Number(nuevoValorMeta),
        fecha_inicio: new Date().toISOString().split("T")[0],
        fecha_limite: nuevaFechaLimite,
        porcentaje_avance: 0.0,
        estado: "EN_PROCESO",
        color_semaforo: "AMARILLO",
        supera_umbral_temporal: true,
      };
      setObjetivos((prev) => [localNuevo, ...prev]);
    }

    setNuevaDescripcion("");
    setModalAbierto(false);
  }

  // Filtrado
  const filtrados = objetivos.filter((obj) => {
    const coincideEstado = filtroEstado === "TODOS" || obj.estado === filtroEstado;
    const coincideAtleta =
      filtroAtleta === "TODOS" || String(obj.id_atleta) === filtroAtleta;
    return coincideEstado && coincideAtleta;
  });

  // Métricas agregadas
  const totalActivos = objetivos.filter((o) => o.estado === "EN_PROCESO").length;
  const totalFinalizados = objetivos.filter((o) => o.estado === "FINALIZADO").length;
  const totalRetrasados = objetivos.filter((o) => o.estado === "RETRASADO").length;
  const promedioAvance = Math.round(
    objetivos.reduce((acc, o) => acc + o.porcentaje_avance, 0) / (objetivos.length || 1)
  );

  function obtenerColorSemaforo(color: string) {
    switch (color) {
      case "VERDE":
        return "bg-emerald-500/15 text-emerald-400 border-emerald-500/30";
      case "AMARILLO":
        return "bg-amber-500/15 text-amber-400 border-amber-500/30";
      case "ROJO":
        return "bg-rose-500/15 text-rose-400 border-rose-500/30";
      default:
        return "bg-slate-800 text-slate-400 border-slate-700";
    }
  }

  function obtenerIconoIndicador(indicador: TipoIndicadorAvance) {
    switch (indicador) {
      case "RATING":
        return <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />;
      case "HORAS_ENTRENADAS":
        return <Clock className="w-3.5 h-3.5 text-blue-400" />;
      case "MEDALLAS":
      case "TORNEOS":
        return <Award className="w-3.5 h-3.5 text-amber-400" />;
      case "TAREAS":
        return <Zap className="w-3.5 h-3.5 text-cyan-400" />;
      default:
        return <Target className="w-3.5 h-3.5 text-slate-400" />;
    }
  }

  return (
    <div className="min-h-screen bg-[#070b12] text-slate-100 py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-8 font-sans">
      {/* Header Banner */}
      <div className="p-6 rounded-2xl border border-slate-800/90 bg-gradient-to-r from-[#0d1424] via-[#0a101d] to-[#070b12] flex flex-col sm:flex-row sm:items-center justify-between gap-6 shadow-xl">
        <div className="space-y-2 max-w-2xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-mono font-medium">
            <Target className="w-3.5 h-3.5" /> REQUERIMIENTOS RF-03.5 & RF-03.6
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white">
            Objetivos SMART Cuantificables
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 leading-relaxed">
            Cálculo automatizado del avance deportivo mediante horas entrenadas, variación de rating ELO FIDE, resultados, ejercicios resueltos y torneos jugados.
          </p>
        </div>

        <button
          onClick={() => setModalAbierto(true)}
          className="flex items-center gap-2 px-5 py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-bold text-xs shadow-lg shadow-emerald-500/20 transition-all hover:scale-[1.02]"
        >
          <Plus className="w-4 h-4" /> Crear Objetivo SMART
        </button>
      </div>

      {/* 4 KPIs de Cumplimiento */}
      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl border border-slate-800/80 bg-[#0d1424]/70 space-y-1">
          <span className="text-[11px] text-slate-400 font-mono uppercase block">Progreso Promedio</span>
          <span className="text-3xl font-extrabold font-mono text-emerald-400">{promedioAvance}%</span>
          <p className="text-[10px] text-slate-500 pt-1 border-t border-slate-800/60">Calculado automáticamente</p>
        </div>
        <div className="p-5 rounded-2xl border border-slate-800/80 bg-[#0d1424]/70 space-y-1">
          <span className="text-[11px] text-slate-400 font-mono uppercase block">En Proceso (Al Día)</span>
          <span className="text-3xl font-extrabold font-mono text-amber-400">{totalActivos}</span>
          <p className="text-[10px] text-slate-500 pt-1 border-t border-slate-800/60">Dentro del umbral temporal</p>
        </div>
        <div className="p-5 rounded-2xl border border-slate-800/80 bg-[#0d1424]/70 space-y-1">
          <span className="text-[11px] text-slate-400 font-mono uppercase block">Metas Alcanzadas</span>
          <span className="text-3xl font-extrabold font-mono text-blue-400">{totalFinalizados}</span>
          <p className="text-[10px] text-slate-500 pt-1 border-t border-slate-800/60">Certificadas por DT</p>
        </div>
        <div className="p-5 rounded-2xl border border-slate-800/80 bg-[#0d1424]/70 space-y-1">
          <span className="text-[11px] text-slate-400 font-mono uppercase block">En Riesgo / Retrasadas</span>
          <span className="text-3xl font-extrabold font-mono text-rose-400">{totalRetrasados}</span>
          <p className="text-[10px] text-slate-500 pt-1 border-t border-slate-800/60">Superan límite de tiempo</p>
        </div>
      </section>

      {/* Barra de Filtros */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-2xl border border-slate-800/80 bg-[#0d1424]/60">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-mono text-slate-400 mr-2">Filtrar por Estado:</span>
          {["TODOS", "EN_PROCESO", "FINALIZADO", "RETRASADO"].map((est) => (
            <button
              key={est}
              onClick={() => setFiltroEstado(est)}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono font-semibold transition-all ${
                filtroEstado === est
                  ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                  : "bg-slate-900 text-slate-400 border border-slate-800 hover:text-white"
              }`}
            >
              {est === "TODOS" ? "Todos" : est.replace("_", " ")}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs font-mono text-slate-400">Atleta:</span>
          <select
            value={filtroAtleta}
            onChange={(e) => setFiltroAtleta(e.target.value)}
            className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
          >
            <option value="TODOS">Todos los atletas</option>
            {ATLETAS_MOCK.map((a) => (
              <option key={a.id} value={String(a.id)}>
                {a.nombre}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Grid de Tarjetas SMART */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {filtrados.map((obj) => {
          const atletaEncontrado = ATLETAS_MOCK.find((a) => a.id === obj.id_atleta);
          const nombreAtleta = obj.nombre_atleta || (atletaEncontrado ? atletaEncontrado.nombre : `Atleta #${obj.id_atleta}`);

          return (
            <div
              key={obj.id}
              className="p-6 rounded-2xl border border-slate-800/80 bg-[#0d1424]/70 hover:bg-[#0f1729] hover:border-slate-700 transition-all space-y-4 shadow-lg flex flex-col justify-between"
            >
              <div className="space-y-3">
                {/* Cabecera de la tarjeta */}
                <div className="flex items-start justify-between gap-3">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-emerald-400 font-mono text-[11px] font-bold">
                        {nombreAtleta}
                      </span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold border ${obtenerColorSemaforo(obj.color_semaforo)}`}>
                        {obj.estado.replace("_", " ")}
                      </span>
                    </div>
                    <h3 className="text-sm font-bold text-white mt-1 leading-snug">
                      {obj.descripcion}
                    </h3>
                  </div>

                  <div className="w-10 h-10 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center flex-shrink-0">
                    {obtenerIconoIndicador(obj.indicador_meta)}
                  </div>
                </div>

                {/* Barra de Progreso Dinámica */}
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs font-mono">
                    <span className="text-slate-400">Progreso Cuantificable:</span>
                    <span className="font-extrabold text-white text-sm">
                      {obj.porcentaje_avance}%
                    </span>
                  </div>
                  <div className="w-full bg-slate-900 h-2.5 rounded-full overflow-hidden border border-slate-800">
                    <div
                      className={`h-full rounded-full transition-all duration-700 ${
                        obj.porcentaje_avance >= 100
                          ? "bg-emerald-400 shadow-sm shadow-emerald-400/50"
                          : obj.porcentaje_avance >= 70
                          ? "bg-gradient-to-r from-emerald-500 to-teal-400"
                          : obj.porcentaje_avance >= 40
                          ? "bg-amber-400"
                          : "bg-rose-400"
                      }`}
                      style={{ width: `${Math.min(obj.porcentaje_avance, 100)}%` }}
                    />
                  </div>
                </div>

                {/* Métricas clave */}
                <div className="grid grid-cols-2 gap-2 text-xs font-mono pt-2">
                  <div className="p-2.5 rounded-xl bg-[#070b12] border border-slate-800/80">
                    <span className="text-slate-400 text-[10px] block">Métrica Objetivo:</span>
                    <span className="font-bold text-slate-200">
                      {obj.valor_meta} ({obj.indicador_meta.replace("_", " ")})
                    </span>
                  </div>
                  <div className="p-2.5 rounded-xl bg-[#070b12] border border-slate-800/80">
                    <span className="text-slate-400 text-[10px] block">Rating Meta:</span>
                    <span className="font-bold text-emerald-400">
                      {obj.rating_meta} ELO
                    </span>
                  </div>
                </div>
              </div>

              {/* Pie de tarjeta: Fechas y Estado Temporal */}
              <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-mono text-slate-400">
                <span className="flex items-center gap-1">
                  <Calendar className="w-3.5 h-3.5 text-slate-400" />
                  Límite: {obj.fecha_limite}
                </span>
                <span className={obj.supera_umbral_temporal ? "text-emerald-400" : "text-rose-400"}>
                  {obj.supera_umbral_temporal ? "Ritmo Óptimo ✓" : "Ritmo Insuficiente ⚠"}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {filtrados.length === 0 && (
        <div className="text-center py-16 border border-slate-800 rounded-2xl bg-slate-900/30">
          <Target className="w-10 h-10 text-slate-600 mx-auto mb-3" />
          <h3 className="text-base font-semibold text-white">No se encontraron objetivos</h3>
          <p className="text-sm text-slate-400 mt-1">Modifica los filtros seleccionados o crea un nuevo objetivo SMART.</p>
        </div>
      )}

      {/* Modal Crear Objetivo SMART */}
      {modalAbierto && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="w-full max-w-lg rounded-2xl border border-slate-800 bg-[#0d1424] p-6 shadow-2xl space-y-5">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <Target className="w-5 h-5 text-emerald-400" /> Registrar Nuevo Objetivo SMART
              </h2>
              <button
                onClick={() => setModalAbierto(false)}
                className="text-slate-400 hover:text-white text-sm font-bold"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4 text-xs font-mono">
              <div>
                <label className="block text-slate-400 mb-1">Atleta Asignado:</label>
                <select
                  value={nuevoAtletaId}
                  onChange={(e) => setNuevoAtletaId(Number(e.target.value))}
                  className="w-full bg-[#070b12] border border-slate-800 rounded-xl p-2.5 text-slate-200 focus:outline-none focus:border-emerald-500"
                >
                  {ATLETAS_MOCK.map((a) => (
                    <option key={a.id} value={a.id}>
                      {a.nombre} (ELO {a.rating_actual.clasicas || "—"})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Descripción del Objetivo (Específico):</label>
                <input
                  type="text"
                  placeholder="Ej: Alcanzar 2,150 ELO FIDE Clásico en el Campeonato Nacional"
                  value={nuevaDescripcion}
                  onChange={(e) => setNuevaDescripcion(e.target.value)}
                  required
                  className="w-full bg-[#070b12] border border-slate-800 rounded-xl p-2.5 text-slate-200 focus:outline-none focus:border-emerald-500 font-sans text-xs"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1">Indicador Medible:</label>
                  <select
                    value={nuevoIndicador}
                    onChange={(e) => setNuevoIndicador(e.target.value as TipoIndicadorAvance)}
                    className="w-full bg-[#070b12] border border-slate-800 rounded-xl p-2.5 text-slate-200 focus:outline-none focus:border-emerald-500"
                  >
                    <option value="RATING">Rating ELO FIDE</option>
                    <option value="HORAS_ENTRENADAS">Horas de Entrenamiento</option>
                    <option value="TAREAS">Ejercicios Tácticos</option>
                    <option value="TORNEOS">Torneos Disputados</option>
                    <option value="MEDALLAS">Medallas / Podios</option>
                  </select>
                </div>

                <div>
                  <label className="block text-slate-400 mb-1">Valor Cuantitativo Meta:</label>
                  <input
                    type="number"
                    value={nuevoValorMeta}
                    onChange={(e) => setNuevoValorMeta(Number(e.target.value))}
                    required
                    className="w-full bg-[#070b12] border border-slate-800 rounded-xl p-2.5 text-slate-200 focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1">Rating Base Actual:</label>
                  <input
                    type="number"
                    value={nuevoRatingActual}
                    onChange={(e) => setNuevoRatingActual(Number(e.target.value))}
                    required
                    className="w-full bg-[#070b12] border border-slate-800 rounded-xl p-2.5 text-slate-200 focus:outline-none focus:border-emerald-500"
                  />
                </div>

                <div>
                  <label className="block text-slate-400 mb-1">Fecha Límite (Temporal):</label>
                  <input
                    type="date"
                    value={nuevaFechaLimite}
                    onChange={(e) => setNuevaFechaLimite(e.target.value)}
                    required
                    className="w-full bg-[#070b12] border border-slate-800 rounded-xl p-2.5 text-slate-200 focus:outline-none focus:border-emerald-500"
                  />
                </div>
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
                  Guardar en Base de Datos
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

