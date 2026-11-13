"use client";

import React, { useState, useEffect } from "react";
import {
  Award,
  TrendingUp,
  FileText,
  AlertTriangle,
  CheckCircle2,
  Plus,
  Printer,
  ChevronRight,
  Shield,
  Sparkles,
  BarChart3,
  Calendar,
  X,
  Target,
} from "lucide-react";
import {
  EvaluacionAtleta,
  ResumenEvaluacionAtleta,
  EvaluacionCrearInput,
  PeriodoEvaluacion,
} from "@/types/evaluacion.types";
import {
  getEvaluaciones,
  getResumenEvaluaciones,
  crearEvaluacion,
} from "@/services/evaluaciones.service";

const NOMBRES_INDICADORES: Record<string, string> = {
  CUMPLIMIENTO_PLAN: "Cumplimiento del Plan",
  DESARROLLO_TECNICO_TACTICO: "Técnica, Táctica y Cálculo",
  PROGRESO_RATING: "Evolución y Progresión ELO",
  CUMPLIMIENTO_OBJETIVOS_SMART: "Logro de Objetivos SMART",
  ORGANIZACION: "Organización y Disciplina",
  GESTION_COMPETENCIAS: "Gestión Emocional & Tiempo",
  DESARROLLO_APERTURAS: "Dominio de Aperturas",
  SEGUIMIENTO_INDIVIDUAL: "Compromiso y Bitácora",
};

const ATLETAS_CLUB = [
  { id: 0, nombre: "Todos los Atletas" },
  { id: 1, nombre: "Garry Kasparov Jr." },
  { id: 2, nombre: "Carlos Daniel Morales" },
  { id: 3, nombre: "Sofía Valentina Castro" },
  { id: 4, nombre: "Alejandro José Rivas" },
];

export default function EvaluacionesPage() {
  const [evaluaciones, setEvaluaciones] = useState<EvaluacionAtleta[]>([]);
  const [resumen, setResumen] = useState<ResumenEvaluacionAtleta | null>(null);
  const [atletaSeleccionado, setAtletaSeleccionado] = useState<number>(1);
  const [periodoFiltro, setPeriodoFiltro] = useState<string>("TODOS");
  const [cargando, setCargando] = useState<boolean>(true);
  const [modalAbierto, setModalAbierto] = useState<boolean>(false);
  const [guardando, setGuardando] = useState<boolean>(false);
  const [mensajeExito, setMensajeExito] = useState<string | null>(null);

  // Form State for new evaluation
  const [nuevoAtletaId, setNuevoAtletaId] = useState<number>(1);
  const [nuevoPeriodo, setNuevoPeriodo] = useState<PeriodoEvaluacion>("MES");
  const [nuevaReferencia, setNuevaReferencia] = useState<string>("");
  const [nuevasCalificaciones, setNuevasCalificaciones] = useState<Record<string, number>>({
    CUMPLIMIENTO_PLAN: 9,
    DESARROLLO_TECNICO_TACTICO: 8,
    PROGRESO_RATING: 8,
    CUMPLIMIENTO_OBJETIVOS_SMART: 9,
    ORGANIZACION: 9,
    GESTION_COMPETENCIAS: 8,
    DESARROLLO_APERTURAS: 8,
    SEGUIMIENTO_INDIVIDUAL: 9,
  });
  const [nuevasFortalezas, setNuevasFortalezas] = useState<string>("");
  const [nuevosAspectos, setNuevosAspectos] = useState<string>("");
  const [nuevasRecomendaciones, setNuevasRecomendaciones] = useState<string>("");

  useEffect(() => {
    cargarDatos();
  }, [atletaSeleccionado, periodoFiltro]);

  async function cargarDatos() {
    setCargando(true);
    const idAtleta = atletaSeleccionado === 0 ? undefined : atletaSeleccionado;
    const periodo = periodoFiltro === "TODOS" ? undefined : periodoFiltro;

    const data = await getEvaluaciones(idAtleta, periodo);
    setEvaluaciones(data);

    if (atletaSeleccionado > 0) {
      const res = await getResumenEvaluaciones(atletaSeleccionado);
      setResumen(res);
    } else {
      setResumen(null);
    }
    setCargando(false);
  }

  const handleSliderChange = (indicador: string, valor: number) => {
    setNuevasCalificaciones((prev) => ({
      ...prev,
      [indicador]: valor,
    }));
  };

  const handleSubmitEvaluacion = async (e: React.FormEvent) => {
    e.preventDefault();
    setGuardando(true);

    const payload: EvaluacionCrearInput = {
      id_atleta: nuevoAtletaId,
      id_entrenador: 1,
      periodo: nuevoPeriodo,
      referencia_periodo: nuevaReferencia || `Evaluación ${nuevoPeriodo} - ${new Date().toLocaleDateString("es-ES")}`,
      fecha_realizacion: new Date().toISOString().split("T")[0],
      calificaciones: nuevasCalificaciones,
      fortalezas: nuevasFortalezas || "Excelente disciplina y compromiso competitivo.",
      aspectos_por_mejorar: nuevosAspectos || "Optimizar el manejo del reloj en apuros de tiempo.",
      recomendaciones: nuevasRecomendaciones || "Continuar con el bloque de cálculo intensivo programado.",
      es_autoevaluacion: false,
    };

    const exito = await crearEvaluacion(payload);
    setGuardando(false);

    if (exito) {
      setMensajeExito("¡Evaluación técnica del DT guardada exitosamente en el sistema!");
      setModalAbierto(false);
      // Limpiar formulario
      setNuevaReferencia("");
      setNuevasFortalezas("");
      setNuevosAspectos("");
      setNuevasRecomendaciones("");
      cargarDatos();
      setTimeout(() => setMensajeExito(null), 4000);
    }
  };

  // Helper calculation for Tier Badge
  const getTierLabel = (promedio: number) => {
    if (promedio >= 9.0) return { label: "SOBRESALIENTE (ALTO RENDIMIENTO)", color: "text-emerald-400 bg-emerald-950/60 border-emerald-500/40" };
    if (promedio >= 8.0) return { label: "NOTABLE (COMPETITIVO)", color: "text-blue-400 bg-blue-950/60 border-blue-500/40" };
    if (promedio >= 7.0) return { label: "ACEPTABLE (EN DESARROLLO)", color: "text-amber-400 bg-amber-950/60 border-amber-500/40" };
    return { label: "REQUIERE ATENCIÓN TÉCNICA", color: "text-rose-400 bg-rose-950/60 border-rose-500/40" };
  };

  // Render SVG Radar Chart for 8 indicators
  const renderRadarChart = (califs: Record<string, number>) => {
    const keys = Object.keys(NOMBRES_INDICADORES);
    const totalPoints = keys.length;
    const center = 150;
    const radius = 100;
    const angleStep = (2 * Math.PI) / totalPoints;

    // Build concentric web levels
    const levels = [2, 4, 6, 8, 10];

    // Build data polygon points
    const polygonPoints = keys
      .map((k, i) => {
        const val = califs[k] || 5;
        const normalizedRadius = (val / 10) * radius;
        const angle = i * angleStep - Math.PI / 2;
        const x = center + normalizedRadius * Math.cos(angle);
        const y = center + normalizedRadius * Math.sin(angle);
        return `${x},${y}`;
      })
      .join(" ");

    return (
      <svg className="w-full max-w-[340px] h-[300px] mx-auto select-none overflow-visible" viewBox="0 0 300 300">
        {/* Background web levels */}
        {levels.map((lvl) => {
          const r = (lvl / 10) * radius;
          return (
            <circle
              key={lvl}
              cx={center}
              cy={center}
              r={r}
              fill="none"
              stroke="#1e293b"
              strokeDasharray={lvl === 10 ? "none" : "3,3"}
              strokeWidth="1"
            />
          );
        })}

        {/* Axis spokes */}
        {keys.map((_, i) => {
          const angle = i * angleStep - Math.PI / 2;
          const x2 = center + radius * Math.cos(angle);
          const y2 = center + radius * Math.sin(angle);
          return (
            <line
              key={i}
              x1={center}
              y1={center}
              x2={x2}
              y2={y2}
              stroke="#1e293b"
              strokeWidth="1"
            />
          );
        })}

        {/* Data polygon */}
        <polygon
          points={polygonPoints}
          fill="rgba(16, 185, 129, 0.25)"
          stroke="#10b981"
          strokeWidth="2.5"
          className="transition-all duration-500 ease-out"
        />

        {/* Vertex points and labels */}
        {keys.map((k, i) => {
          const val = califs[k] || 5;
          const normalizedRadius = (val / 10) * radius;
          const angle = i * angleStep - Math.PI / 2;
          const px = center + normalizedRadius * Math.cos(angle);
          const py = center + normalizedRadius * Math.sin(angle);

          // Label placement slightly further than radius
          const lx = center + (radius + 24) * Math.cos(angle);
          const ly = center + (radius + 24) * Math.sin(angle);

          return (
            <g key={k}>
              <circle cx={px} cy={py} r="4" fill="#34d399" stroke="#059669" strokeWidth="1.5" />
              <text
                x={lx}
                y={ly + 3}
                fill="#94a3b8"
                fontSize="8.5"
                fontWeight="600"
                textAnchor={Math.abs(Math.cos(angle)) < 0.1 ? "middle" : Math.cos(angle) > 0 ? "start" : "end"}
                className="font-mono tracking-tighter"
              >
                {val}/10
              </text>
            </g>
          );
        })}
      </svg>
    );
  };

  const evaluacionDestacada = evaluaciones[0];

  return (
    <div className="min-h-screen bg-[#070b12] text-slate-100 p-4 sm:p-6 lg:p-8 space-y-8">
      {/* Print-only CSS rules */}
      <style jsx global>{`
        @media print {
          header, nav, button, .no-print {
            display: none !important;
          }
          body, .min-h-screen {
            background: white !important;
            color: black !important;
            padding: 0 !important;
          }
          .print-card {
            background: white !important;
            border: 1px solid #cbd5e1 !important;
            color: black !important;
            box-shadow: none !important;
          }
        }
      `}</style>

      {/* Header & Breadcrumb */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-emerald-400 uppercase tracking-widest mb-1.5">
            <Award className="w-4 h-4" />
            <span>Módulo de Supervisión Técnica & Evaluación del Entrenador</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white flex items-center gap-3">
            Evaluaciones Técnicas del DT
            <span className="text-xs px-2.5 py-0.5 rounded-full font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
              RF-05 Oficial
            </span>
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1 max-w-3xl">
            Rúbrica cuantitativa en 8 dimensiones táctico-estratégicas (escala 1-10) y diagnóstico cualitativo continuo para el seguimiento de mesociclos y emisión de informes técnicos federativos.
          </p>
        </div>

        {/* Actions bar */}
        <div className="flex items-center gap-3 no-print">
          <button
            onClick={() => window.print()}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-medium text-slate-300 bg-slate-900 border border-slate-700/80 hover:bg-slate-800 hover:text-white transition-all shadow-sm"
          >
            <Printer className="w-4 h-4 text-slate-400" />
            <span>Imprimir Dossier Oficial</span>
          </button>
          <button
            onClick={() => setModalAbierto(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold text-slate-950 bg-gradient-to-r from-emerald-400 to-teal-400 hover:from-emerald-300 hover:to-teal-300 transition-all shadow-lg shadow-emerald-500/20"
          >
            <Plus className="w-4 h-4" />
            <span>Nueva Evaluación DT</span>
          </button>
        </div>
      </div>

      {/* Alert toast on action */}
      {mensajeExito && (
        <div className="p-4 rounded-xl bg-emerald-950/70 border border-emerald-500/50 text-emerald-300 text-xs flex items-center justify-between animate-fadeIn shadow-lg shadow-emerald-950/50">
          <div className="flex items-center gap-2.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
            <span className="font-semibold">{mensajeExito}</span>
          </div>
          <button onClick={() => setMensajeExito(null)} className="text-emerald-400 hover:text-white">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Filter bar: Atleta selector & Period Tabs */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-4 items-center bg-[#0d1424] p-4 rounded-2xl border border-slate-800 shadow-xl no-print">
        <div className="md:col-span-5 flex items-center gap-3">
          <span className="text-xs font-mono text-slate-400 uppercase tracking-wider flex-shrink-0">
            Atleta Evaluado:
          </span>
          <select
            value={atletaSeleccionado}
            onChange={(e) => setAtletaSeleccionado(Number(e.target.value))}
            className="w-full bg-[#070b12] border border-slate-700 rounded-xl px-3.5 py-2 text-xs font-semibold text-slate-200 focus:outline-none focus:border-emerald-500 transition-all"
          >
            {ATLETAS_CLUB.map((at) => (
              <option key={at.id} value={at.id}>
                {at.nombre}
              </option>
            ))}
          </select>
        </div>

        <div className="md:col-span-7 flex items-center justify-start md:justify-end gap-2 overflow-x-auto scrollbar-none">
          <span className="text-xs font-mono text-slate-400 uppercase tracking-wider mr-2 hidden sm:inline">
            Ciclo:
          </span>
          {["TODOS", "MES", "MESOCICLO", "TORNEO", "ANIO"].map((p) => (
            <button
              key={p}
              onClick={() => setPeriodoFiltro(p)}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition-all ${
                periodoFiltro === p
                  ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-sm"
                  : "bg-slate-900/60 text-slate-400 border border-slate-800 hover:bg-slate-800"
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {/* Main KPI & Radar section (if an athlete is selected and has data) */}
      {resumen && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
          {/* Executive Score & Synthesis Card */}
          <div className="lg:col-span-5 bg-gradient-to-b from-[#0f172a] to-[#090d16] p-6 rounded-2xl border border-slate-800 shadow-xl flex flex-col justify-between space-y-6">
            <div>
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">
                  Índice Global de Rendimiento Técnico
                </span>
                <span className={`text-[10px] font-mono px-2.5 py-1 rounded-full border ${getTierLabel(resumen.promedio_general).color}`}>
                  {getTierLabel(resumen.promedio_general).label}
                </span>
              </div>

              <div className="flex items-baseline gap-3 my-2">
                <span className="text-5xl font-black font-mono text-white tracking-tight">
                  {resumen.promedio_general.toFixed(2)}
                </span>
                <span className="text-slate-500 font-mono text-base">/ 10.0</span>
                <div className="ml-auto flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-emerald-950/50 border border-emerald-800/40 text-emerald-400 text-xs font-mono font-semibold">
                  <TrendingUp className="w-3.5 h-3.5" />
                  <span>+{resumen.variacion_ultimo_ciclo.toFixed(2)} pts</span>
                </div>
              </div>

              <p className="text-xs text-slate-400 leading-relaxed mt-3">
                Calificación consolidada del Director Técnico para{" "}
                <span className="text-slate-200 font-semibold">{resumen.nombre_atleta}</span> tras{" "}
                <span className="text-emerald-400 font-bold">{resumen.cantidad_evaluaciones}</span> ciclos evaluativos oficiales registrados en la base de datos.
              </p>
            </div>

            {/* Areas of improvement & Top strengths */}
            <div className="space-y-4 pt-4 border-t border-slate-800/80">
              <div>
                <span className="text-[11px] font-mono text-amber-400 font-bold uppercase tracking-wider flex items-center gap-1.5 mb-2">
                  <AlertTriangle className="w-3.5 h-3.5" />
                  Áreas Prioritarias de Intervención (Bajas Calificaciones)
                </span>
                <div className="flex flex-wrap gap-2">
                  {resumen.areas_de_mejora.map((area) => (
                    <span
                      key={area}
                      className="px-2.5 py-1 rounded-lg bg-amber-950/40 border border-amber-800/40 text-amber-300 text-xs font-medium"
                    >
                      {NOMBRES_INDICADORES[area] || area} (
                      {resumen.promedio_por_indicador[area]?.toFixed(1) || "N/A"})
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider block mb-1.5">
                  Última Fecha de Examen Oficial:
                </span>
                <span className="text-xs font-mono text-slate-200 font-medium">
                  {resumen.ultima_evaluacion || "Sin registro"}
                </span>
              </div>
            </div>
          </div>

          {/* Radar Chart & 8 Rubric Progress Bars */}
          <div className="lg:col-span-7 bg-[#0d1424] p-6 rounded-2xl border border-slate-800 shadow-xl flex flex-col md:flex-row items-center gap-6">
            {/* SVG Spider/Radar Visualization */}
            <div className="w-full md:w-1/2 flex flex-col items-center">
              <span className="text-xs font-mono text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <BarChart3 className="w-3.5 h-3.5 text-emerald-400" />
                Matriz Radial de 8 Ejes
              </span>
              {renderRadarChart(resumen.promedio_por_indicador)}
            </div>

            {/* Numerical breakdown bars */}
            <div className="w-full md:w-1/2 space-y-2.5">
              <span className="text-xs font-mono text-slate-400 uppercase tracking-wider block mb-2">
                Desglose Cuantitativo por Eje
              </span>
              {Object.entries(NOMBRES_INDICADORES).map(([key, label]) => {
                const score = resumen.promedio_por_indicador[key] || 0;
                const pct = (score / 10) * 100;
                return (
                  <div key={key} className="space-y-1">
                    <div className="flex justify-between text-[11px] font-mono">
                      <span className="text-slate-300 truncate max-w-[170px]">{label}</span>
                      <span className="text-emerald-400 font-bold">{score.toFixed(1)} / 10</span>
                    </div>
                    <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-emerald-500 to-teal-400 rounded-full transition-all duration-500"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Historical Evaluations Dossier Feed */}
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4 text-emerald-400" />
            <h2 className="text-lg font-bold text-white tracking-tight">
              Expediente Histórico de Informes Técnicos
            </h2>
          </div>
          <span className="text-xs font-mono text-slate-500">
            {evaluaciones.length} informes encontrados
          </span>
        </div>

        {cargando ? (
          <div className="p-12 text-center text-slate-500 font-mono text-xs animate-pulse">
            Cargando evaluaciones desde SQLite...
          </div>
        ) : evaluaciones.length === 0 ? (
          <div className="p-12 text-center bg-[#0d1424] rounded-2xl border border-slate-800 text-slate-400 space-y-3">
            <Award className="w-8 h-8 mx-auto text-slate-600" />
            <p className="text-sm font-semibold text-slate-300">
              No hay evaluaciones registradas con los filtros seleccionados.
            </p>
            <p className="text-xs text-slate-500">
              Haga clic en "+ Nueva Evaluación DT" para emitir el primer informe técnico.
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            {evaluaciones.map((ev) => (
              <div
                key={ev.id}
                className="print-card bg-[#0d1424] rounded-2xl border border-slate-800/90 shadow-xl overflow-hidden hover:border-slate-700 transition-all"
              >
                {/* Dossier Card Header */}
                <div className="bg-[#090d16] p-4 sm:p-5 border-b border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500/20 to-teal-500/10 border border-emerald-500/30 flex items-center justify-center font-bold text-emerald-400 font-mono text-sm">
                      #{ev.id}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-extrabold text-white text-base">
                          {ev.nombre_atleta}
                        </span>
                        <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-slate-800 text-slate-300 border border-slate-700">
                          {ev.periodo}
                        </span>
                      </div>
                      <span className="text-xs text-slate-400 font-medium">
                        {ev.referencia_periodo}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <span className="text-[10px] font-mono text-slate-500 block uppercase">
                        Fecha Dictamen
                      </span>
                      <span className="text-xs font-mono text-slate-300">
                        {ev.fecha_realizacion}
                      </span>
                    </div>

                    <div className="flex items-center gap-2 pl-4 border-l border-slate-800">
                      <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex flex-col items-center justify-center">
                        <span className="text-base font-black font-mono text-emerald-400 leading-none">
                          {ev.promedio.toFixed(1)}
                        </span>
                        <span className="text-[9px] font-mono text-emerald-500/80">/10</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Dossier Card Content */}
                <div className="p-5 sm:p-6 space-y-6">
                  {/* Calificaciones Pills Grid */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2 bg-[#070b12]/60 p-3.5 rounded-xl border border-slate-800/60">
                    {Object.entries(ev.calificaciones).map(([k, score]) => (
                      <div key={k} className="text-center p-2 rounded-lg bg-slate-900/40 border border-slate-800/50">
                        <span className="text-[10px] text-slate-400 truncate block">
                          {NOMBRES_INDICADORES[k]?.split(" ")[0] || k}
                        </span>
                        <span className="text-sm font-black font-mono text-emerald-400">
                          {score}
                        </span>
                      </div>
                    ))}
                  </div>

                  {/* Qualitative Technical Diagnosis 3-Column Grid */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {/* Fortalezas */}
                    <div className="p-4 rounded-xl bg-[#0a0f1d] border border-emerald-900/30 space-y-2">
                      <span className="text-xs font-mono font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        Fortalezas Observadas
                      </span>
                      <p className="text-xs text-slate-300 leading-relaxed">
                        {ev.fortalezas || "Sin observaciones específicas registradas."}
                      </p>
                    </div>

                    {/* Aspectos por Mejorar */}
                    <div className="p-4 rounded-xl bg-[#0a0f1d] border border-amber-900/30 space-y-2">
                      <span className="text-xs font-mono font-bold text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
                        <AlertTriangle className="w-3.5 h-3.5" />
                        Puntos de Corrección Técnica
                      </span>
                      <p className="text-xs text-slate-300 leading-relaxed">
                        {ev.aspectos_por_mejorar || "Sin aspectos críticos señalados."}
                      </p>
                    </div>

                    {/* Recomendaciones / Plan */}
                    <div className="p-4 rounded-xl bg-[#0a0f1d] border border-cyan-900/30 space-y-2">
                      <span className="text-xs font-mono font-bold text-cyan-400 uppercase tracking-wider flex items-center gap-1.5">
                        <Target className="w-3.5 h-3.5" />
                        Plan de Acción & Recomendación DT
                      </span>
                      <p className="text-xs text-slate-300 leading-relaxed">
                        {ev.recomendaciones || "Continuar plan regular de mesociclo."}
                      </p>
                    </div>
                  </div>

                  {/* Sign-off badge */}
                  <div className="flex items-center justify-between text-[11px] font-mono text-slate-500 pt-2 border-t border-slate-800/40">
                    <div className="flex items-center gap-1.5">
                      <Shield className="w-3.5 h-3.5 text-slate-400" />
                      <span>Dictamen Técnico Oficial - Caissa Analytic Integrity System</span>
                    </div>
                    <span>ID Entrenador: #{ev.id_entrenador} (GM Magnus Principal)</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Modal: Registrar Nueva Evaluación DT */}
      {modalAbierto && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto no-print">
          <div className="bg-[#0d1424] border border-slate-700 rounded-2xl max-w-2xl w-full p-6 shadow-2xl space-y-6 my-8 animate-fadeIn">
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400">
                  <Award className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white">
                    Registrar Evaluación Técnica del DT
                  </h3>
                  <p className="text-xs text-slate-400">
                    Califique las 8 dimensiones oficiales del atleta (escala 1 a 10).
                  </p>
                </div>
              </div>
              <button
                onClick={() => setModalAbierto(false)}
                className="text-slate-400 hover:text-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Form */}
            <form onSubmit={handleSubmitEvaluacion} className="space-y-6">
              {/* Basic Details */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-mono text-slate-300 block mb-1">
                    Atleta a Evaluar *
                  </label>
                  <select
                    value={nuevoAtletaId}
                    onChange={(e) => setNuevoAtletaId(Number(e.target.value))}
                    className="w-full bg-[#070b12] border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
                    required
                  >
                    {ATLETAS_CLUB.filter((a) => a.id > 0).map((a) => (
                      <option key={a.id} value={a.id}>
                        {a.nombre}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="text-xs font-mono text-slate-300 block mb-1">
                    Tipo de Período *
                  </label>
                  <select
                    value={nuevoPeriodo}
                    onChange={(e) => setNuevoPeriodo(e.target.value as PeriodoEvaluacion)}
                    className="w-full bg-[#070b12] border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
                    required
                  >
                    <option value="MES">Mes Regular</option>
                    <option value="MESOCICLO">Mesociclo de Preparación</option>
                    <option value="TORNEO">Post-Torneo Oficial</option>
                    <option value="ANIO">Balance Anual</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="text-xs font-mono text-slate-300 block mb-1">
                  Referencia / Título del Período *
                </label>
                <input
                  type="text"
                  value={nuevaReferencia}
                  onChange={(e) => setNuevaReferencia(e.target.value)}
                  placeholder="Ej: Evaluación Post-Torneo Magistral Noviembre 2026"
                  className="w-full bg-[#070b12] border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
                  required
                />
              </div>

              {/* 8 Indicators Sliders */}
              <div className="space-y-4 bg-[#070b12] p-4 rounded-xl border border-slate-800">
                <span className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider block">
                  Rúbrica Cuantitativa de los 8 Ejes (1 al 10)
                </span>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-3">
                  {Object.entries(NOMBRES_INDICADORES).map(([key, label]) => {
                    const val = nuevasCalificaciones[key] || 8;
                    return (
                      <div key={key} className="space-y-1">
                        <div className="flex justify-between text-xs font-mono">
                          <span className="text-slate-400">{label}</span>
                          <span className="text-emerald-400 font-bold">{val}</span>
                        </div>
                        <input
                          type="range"
                          min="1"
                          max="10"
                          step="1"
                          value={val}
                          onChange={(e) => handleSliderChange(key, Number(e.target.value))}
                          className="w-full accent-emerald-500 cursor-pointer h-1.5 bg-slate-800 rounded-lg"
                        />
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Qualitative Fields */}
              <div className="space-y-3">
                <div>
                  <label className="text-xs font-mono text-slate-300 block mb-1">
                    Fortalezas Detectadas
                  </label>
                  <textarea
                    rows={2}
                    value={nuevasFortalezas}
                    onChange={(e) => setNuevasFortalezas(e.target.value)}
                    placeholder="Describa el progreso táctico, apertura o tenacidad demostrada..."
                    className="w-full bg-[#070b12] border border-slate-700 rounded-xl p-2.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
                  />
                </div>

                <div>
                  <label className="text-xs font-mono text-slate-300 block mb-1">
                    Aspectos por Mejorar
                  </label>
                  <textarea
                    rows={2}
                    value={nuevosAspectos}
                    onChange={(e) => setNuevosAspectos(e.target.value)}
                    placeholder="Señale debilidades específicas (ej. finales de torres, apuros de tiempo)..."
                    className="w-full bg-[#070b12] border border-slate-700 rounded-xl p-2.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
                  />
                </div>

                <div>
                  <label className="text-xs font-mono text-slate-300 block mb-1">
                    Recomendaciones & Plan de Trabajo
                  </label>
                  <textarea
                    rows={2}
                    value={nuevasRecomendaciones}
                    onChange={(e) => setNuevasRecomendaciones(e.target.value)}
                    placeholder="Prescripción concreta de horas, temas tácticos o libros clave..."
                    className="w-full bg-[#070b12] border border-slate-700 rounded-xl p-2.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>

              {/* Submit Buttons */}
              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setModalAbierto(false)}
                  className="px-4 py-2 rounded-xl text-xs font-medium text-slate-400 hover:text-white transition-colors"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={guardando}
                  className="px-5 py-2 rounded-xl text-xs font-bold text-slate-950 bg-gradient-to-r from-emerald-400 to-teal-400 hover:from-emerald-300 hover:to-teal-300 transition-all disabled:opacity-50 shadow-lg shadow-emerald-500/20"
                >
                  {guardando ? "Guardando..." : "Emitir Dictamen Oficial"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
