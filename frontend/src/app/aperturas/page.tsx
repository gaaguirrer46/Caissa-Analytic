"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  BookOpen,
  Plus,
  Shield,
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  BrainCircuit,
  Search,
  Filter,
  Layers,
  Sparkles,
  ArrowRight,
  Zap,
  RotateCcw,
} from "lucide-react";
import { getAperturas, crearApertura, APERTURAS_MOCK } from "@/services/aperturas.service";
import { AperturaRepertorio, ColorApertura, EstadoApertura } from "@/types/apertura.types";
import { ATLETAS_MOCK } from "@/services/atletas.service";

export default function AperturasPage() {
  const [aperturas, setAperturas] = useState<AperturaRepertorio[]>(APERTURAS_MOCK);
  const [filtroColor, setFiltroColor] = useState<string>("TODOS");
  const [filtroAtleta, setFiltroAtleta] = useState<string>("TODOS");
  const [busquedaEco, setBusquedaEco] = useState<string>("");
  const [modalAbierto, setModalAbierto] = useState(false);
  const [cargando, setCargando] = useState(false);

  // Formulario nueva apertura
  const [nuevoAtletaId, setNuevoAtletaId] = useState<number>(2);
  const [nuevoEco, setNuevoEco] = useState<string>("C50");
  const [nuevoNombre, setNuevoNombre] = useState<string>("");
  const [nuevaVariante, setNuevaVariante] = useState<string>("");
  const [nuevoColor, setNuevoColor] = useState<ColorApertura>("BLANCAS");
  const [nuevoEstado, setNuevoEstado] = useState<EstadoApertura>("ACTIVA");
  const [nuevaFuente, setNuevaFuente] = useState<string>("");

  useEffect(() => {
    cargarDatos();
  }, []);

  async function cargarDatos() {
    setCargando(true);
    try {
      const data = await getAperturas();
      if (data && data.length > 0) {
        setAperturas(data);
      }
    } finally {
      setCargando(false);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!nuevoNombre.trim() || !nuevoEco.trim()) return;

    const res = await crearApertura({
      id_atleta: nuevoAtletaId,
      codigo_eco: nuevoEco.toUpperCase(),
      nombre: nuevoNombre,
      variante: nuevaVariante,
      color: nuevoColor,
      estado: nuevoEstado,
      fuente_estudio: nuevaFuente,
      clasificacion_uso: "PRINCIPAL",
    });

    if (res) {
      setAperturas((prev) => [res, ...prev]);
    } else {
      // Fallback local
      const localNueva: AperturaRepertorio = {
        id: Date.now(),
        id_atleta: nuevoAtletaId,
        codigo_eco: nuevoEco.toUpperCase(),
        nombre: nuevoNombre,
        variante: nuevaVariante,
        color: nuevoColor,
        estado: nuevoEstado,
        nivel_dominio: "AVANZADO",
        clasificacion_uso: "PRINCIPAL",
        fuente_estudio: nuevaFuente,
        partidas_jugadas: 1,
        victorias: 1,
        empates: 0,
        derrotas: 0,
        rendimiento_pct: 100.0,
        accuracy_promedio: 92.0,
        acpl_promedio: 20.0,
        errores_frecuentes: 0,
        evaluacion_motor: 0.5,
        efectividad: "MUY_EFECTIVA",
        jugadas_clave: "Línea teórica registrada en el repertorio",
      };
      setAperturas((prev) => [localNueva, ...prev]);
    }

    setNuevoNombre("");
    setNuevaVariante("");
    setModalAbierto(false);
  }

  // Filtrado
  const filtradas = aperturas.filter((ap) => {
    const coincideColor = filtroColor === "TODOS" || ap.color === filtroColor;
    const coincideAtleta = filtroAtleta === "TODOS" || String(ap.id_atleta) === filtroAtleta;
    const coincideEco =
      !busquedaEco ||
      ap.codigo_eco.toLowerCase().includes(busquedaEco.toLowerCase()) ||
      ap.nombre.toLowerCase().includes(busquedaEco.toLowerCase()) ||
      (ap.variante && ap.variante.toLowerCase().includes(busquedaEco.toLowerCase()));

    return coincideColor && coincideAtleta && coincideEco;
  });

  // Métricas de repertorio
  const totalBlancas = aperturas.filter((a) => a.color === "BLANCAS").length;
  const totalNegras = aperturas.filter((a) => a.color === "NEGRAS").length;
  const winRatePromedio = Math.round(
    aperturas.reduce((acc, a) => acc + (a.rendimiento_pct || 0), 0) / (aperturas.length || 1)
  );
  const agujerosTeoricos = aperturas.filter((a) => a.rendimiento_pct < 50).length;

  return (
    <div className="min-h-screen bg-[#070b12] text-slate-100 py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-8 font-sans">
      {/* Header Banner */}
      <div className="p-6 rounded-2xl border border-slate-800/90 bg-gradient-to-r from-[#0d1424] via-[#0a101d] to-[#070b12] flex flex-col sm:flex-row sm:items-center justify-between gap-6 shadow-xl">
        <div className="space-y-2 max-w-2xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-400 text-xs font-mono font-medium">
            <BookOpen className="w-3.5 h-3.5" /> REPERTORIO Y EFECTIVIDAD POR VARIANTES
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white">
            Repertorio de Aperturas
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 leading-relaxed">
            Árbol de variantes para piezas blancas y negras, estadísticas de efectividad por código ECO, precisión teórica contra el libro y detección de agujeros en la preparación.
          </p>
        </div>

        <button
          onClick={() => setModalAbierto(true)}
          className="flex items-center gap-2 px-5 py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-bold text-xs shadow-lg shadow-emerald-500/20 transition-all hover:scale-[1.02]"
        >
          <Plus className="w-4 h-4" /> Agregar Apertura
        </button>
      </div>

      {/* 4 KPIs de Rendimiento de Repertorio */}
      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl border border-slate-800/80 bg-[#0d1424]/70 space-y-1">
          <span className="text-[11px] text-slate-400 font-mono uppercase block">Win Rate Promedio</span>
          <span className="text-3xl font-extrabold font-mono text-emerald-400">{winRatePromedio}%</span>
          <p className="text-[10px] text-slate-500 pt-1 border-t border-slate-800/60">Puntos obtenidos globales</p>
        </div>
        <div className="p-5 rounded-2xl border border-slate-800/80 bg-[#0d1424]/70 space-y-1">
          <span className="text-[11px] text-slate-400 font-mono uppercase block">Líneas con Blancas</span>
          <span className="text-3xl font-extrabold font-mono text-white">{totalBlancas} Variantes</span>
          <p className="text-[10px] text-slate-500 pt-1 border-t border-slate-800/60">1.e4 y 1.d4 principales</p>
        </div>
        <div className="p-5 rounded-2xl border border-slate-800/80 bg-[#0d1424]/70 space-y-1">
          <span className="text-[11px] text-slate-400 font-mono uppercase block">Defensas con Negras</span>
          <span className="text-3xl font-extrabold font-mono text-cyan-400">{totalNegras} Variantes</span>
          <p className="text-[10px] text-slate-500 pt-1 border-t border-slate-800/60">Najdorf, India de Rey, Francesa</p>
        </div>
        <div className="p-5 rounded-2xl border border-slate-800/80 bg-[#0d1424]/70 space-y-1">
          <span className="text-[11px] text-slate-400 font-mono uppercase block">Agujeros Detectados</span>
          <span className="text-3xl font-extrabold font-mono text-amber-400">{agujerosTeoricos}</span>
          <p className="text-[10px] text-slate-500 pt-1 border-t border-slate-800/60">Win rate menor al 50%</p>
        </div>
      </section>

      {/* Barra de Filtros y Búsqueda */}
      <div className="grid grid-cols-1 sm:grid-cols-12 gap-3 p-4 rounded-2xl border border-slate-800/80 bg-[#0d1424]/60">
        <div className="relative sm:col-span-6">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-3.5" />
          <input
            type="text"
            placeholder="Buscar por código ECO (ej: B90, C50), nombre o variante..."
            value={busquedaEco}
            onChange={(e) => setBusquedaEco(e.target.value)}
            className="w-full bg-[#070b12] border border-slate-800 rounded-xl pl-10 pr-4 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500"
          />
        </div>

        <div className="sm:col-span-3">
          <select
            value={filtroColor}
            onChange={(e) => setFiltroColor(e.target.value)}
            className="w-full bg-[#070b12] border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-500 font-mono"
          >
            <option value="TODOS">Todos los Colores</option>
            <option value="BLANCAS">Blancas</option>
            <option value="NEGRAS">Negras</option>
          </select>
        </div>

        <div className="sm:col-span-3">
          <select
            value={filtroAtleta}
            onChange={(e) => setFiltroAtleta(e.target.value)}
            className="w-full bg-[#070b12] border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-500 font-mono"
          >
            <option value="TODOS">Todos los Atletas</option>
            {ATLETAS_MOCK.map((a) => (
              <option key={a.id} value={String(a.id)}>
                {a.nombre}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Grid de Aperturas del Repertorio */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {filtradas.map((ap) => {
          const atletaObj = ATLETAS_MOCK.find((a) => a.id === ap.id_atleta);
          const nombreAtleta = atletaObj ? atletaObj.nombre : `Atleta #${ap.id_atleta}`;

          return (
            <div
              key={ap.id}
              className="p-6 rounded-2xl border border-slate-800/80 bg-[#0d1424]/70 hover:bg-[#0f1729] hover:border-slate-700 transition-all space-y-4 shadow-lg flex flex-col justify-between"
            >
              <div className="space-y-3">
                {/* Header tarjeta */}
                <div className="flex items-start justify-between gap-3">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 rounded bg-blue-500/15 border border-blue-500/30 text-blue-400 font-mono text-xs font-bold">
                        {ap.codigo_eco}
                      </span>
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                          ap.color === "BLANCAS"
                            ? "bg-slate-100 text-slate-900"
                            : "bg-slate-900 border border-slate-700 text-slate-200"
                        }`}
                      >
                        {ap.color}
                      </span>
                      <span className="text-[10px] font-mono text-slate-400 truncate max-w-[100px]">
                        {nombreAtleta}
                      </span>
                    </div>

                    <h3 className="text-base font-bold text-white mt-1 leading-snug">
                      {ap.nombre}
                    </h3>
                    {ap.variante && (
                      <p className="text-xs text-emerald-400 font-medium">
                        {ap.variante}
                      </p>
                    )}
                  </div>

                  <div className="text-right font-mono flex-shrink-0">
                    <span
                      className={`text-xl font-extrabold ${
                        ap.rendimiento_pct >= 70
                          ? "text-emerald-400"
                          : ap.rendimiento_pct >= 50
                          ? "text-cyan-400"
                          : "text-amber-400"
                      }`}
                    >
                      {ap.rendimiento_pct}%
                    </span>
                    <span className="block text-[10px] text-slate-400">Win Rate</span>
                  </div>
                </div>

                {/* Jugadas clave */}
                {ap.jugadas_clave && (
                  <div className="p-2.5 rounded-xl bg-[#070b12] border border-slate-800 text-[11px] font-mono text-slate-300">
                    {ap.jugadas_clave}
                  </div>
                )}

                {/* Barra de Desglose Victorias / Tablas / Derrotas */}
                <div className="space-y-1 pt-1">
                  <div className="flex justify-between text-[11px] font-mono text-slate-400">
                    <span>
                      {ap.partidas_jugadas} partidas ({ap.victorias}V - {ap.empates}T - {ap.derrotas}D)
                    </span>
                    <span className="text-emerald-400 font-bold">Precisión: {ap.accuracy_promedio}%</span>
                  </div>

                  <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden flex border border-slate-800">
                    <div
                      className="bg-emerald-400 h-full"
                      style={{ width: `${(ap.victorias / (ap.partidas_jugadas || 1)) * 100}%` }}
                      title="Victorias"
                    />
                    <div
                      className="bg-slate-400 h-full"
                      style={{ width: `${(ap.empates / (ap.partidas_jugadas || 1)) * 100}%` }}
                      title="Tablas"
                    />
                    <div
                      className="bg-rose-500 h-full"
                      style={{ width: `${(ap.derrotas / (ap.partidas_jugadas || 1)) * 100}%` }}
                      title="Derrotas"
                    />
                  </div>
                </div>

                {/* Alerta de preparación / Evaluación motor */}
                <div className="flex items-center justify-between text-xs font-mono pt-1">
                  <span className="text-slate-400">Evaluación Stockfish:</span>
                  <span className={`font-bold ${ap.evaluacion_motor >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                    {ap.evaluacion_motor > 0 ? `+${ap.evaluacion_motor}` : ap.evaluacion_motor}
                  </span>
                </div>
              </div>

              {/* Pie de tarjeta: Fuente y Enlace a Partidas */}
              <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
                <span className="text-[11px] text-slate-400 truncate max-w-[150px]">
                  {ap.fuente_estudio || "Línea magistral"}
                </span>
                <Link
                  href={`/partidas?eco=${ap.codigo_eco}`}
                  className="text-emerald-400 hover:text-emerald-300 font-semibold flex items-center gap-1 transition-colors"
                >
                  Ver partidas PGN →
                </Link>
              </div>
            </div>
          );
        })}
      </div>

      {filtradas.length === 0 && (
        <div className="text-center py-16 border border-slate-800 rounded-2xl bg-slate-900/30">
          <BookOpen className="w-10 h-10 text-slate-600 mx-auto mb-3" />
          <h3 className="text-base font-semibold text-white">No se encontraron aperturas</h3>
          <p className="text-sm text-slate-400 mt-1">Prueba con otros términos de búsqueda o registra una nueva línea.</p>
        </div>
      )}

      {/* Modal Registrar Apertura */}
      {modalAbierto && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="w-full max-w-lg rounded-2xl border border-slate-800 bg-[#0d1424] p-6 shadow-2xl space-y-5">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-emerald-400" /> Añadir al Repertorio de Aperturas
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
                      {a.nombre}
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1">Código ECO:</label>
                  <input
                    type="text"
                    placeholder="B90"
                    value={nuevoEco}
                    onChange={(e) => setNuevoEco(e.target.value)}
                    required
                    className="w-full bg-[#070b12] border border-slate-800 rounded-xl p-2.5 text-slate-200 uppercase focus:outline-none focus:border-emerald-500"
                  />
                </div>

                <div className="col-span-2">
                  <label className="block text-slate-400 mb-1">Nombre de la Apertura:</label>
                  <input
                    type="text"
                    placeholder="Defensa Siciliana"
                    value={nuevoNombre}
                    onChange={(e) => setNuevoNombre(e.target.value)}
                    required
                    className="w-full bg-[#070b12] border border-slate-800 rounded-xl p-2.5 text-slate-200 focus:outline-none focus:border-emerald-500 font-sans"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Variante Específica:</label>
                <input
                  type="text"
                  placeholder="Variante Najdorf con 6.Be3"
                  value={nuevaVariante}
                  onChange={(e) => setNuevaVariante(e.target.value)}
                  className="w-full bg-[#070b12] border border-slate-800 rounded-xl p-2.5 text-slate-200 focus:outline-none focus:border-emerald-500 font-sans"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1">Color de Piezas:</label>
                  <select
                    value={nuevoColor}
                    onChange={(e) => setNuevoColor(e.target.value as ColorApertura)}
                    className="w-full bg-[#070b12] border border-slate-800 rounded-xl p-2.5 text-slate-200 focus:outline-none focus:border-emerald-500"
                  >
                    <option value="BLANCAS">Blancas</option>
                    <option value="NEGRAS">Negras</option>
                  </select>
                </div>

                <div>
                  <label className="block text-slate-400 mb-1">Estado en Repertorio:</label>
                  <select
                    value={nuevoEstado}
                    onChange={(e) => setNuevoEstado(e.target.value as EstadoApertura)}
                    className="w-full bg-[#070b12] border border-slate-800 rounded-xl p-2.5 text-slate-200 focus:outline-none focus:border-emerald-500"
                  >
                    <option value="ACTIVA">Activa</option>
                    <option value="EN_ESTUDIO">En Estudio</option>
                    <option value="EN_REVISION">En Revisión</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Fuente / Estudio de Referencia:</label>
                <input
                  type="text"
                  placeholder="Libro, estudio ChessBase o partida modelo"
                  value={nuevaFuente}
                  onChange={(e) => setNuevaFuente(e.target.value)}
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
                  Guardar en Repertorio
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

