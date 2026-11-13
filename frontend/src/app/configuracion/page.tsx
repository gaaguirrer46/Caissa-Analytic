"use client";

import React, { useState, useEffect } from "react";
import {
  Settings,
  Sliders,
  Gauge,
  UserCheck,
  Cpu,
  Save,
  CheckCircle2,
  AlertCircle,
  Database,
  Building,
  Shield,
  Layers,
  Sparkles,
  Zap,
} from "lucide-react";
import {
  ConfiguracionSistema,
  ConfiguracionActualizarInput,
} from "@/types/configuracion.types";
import {
  getConfiguracion,
  actualizarConfiguracion,
  configurarAccesoInvitado,
} from "@/services/configuracion.service";

const NOMBRES_RANGOS: Record<string, { label: string; unidad: string; menorEsMejor?: boolean }> = {
  ACCURACY: { label: "Precisión de Jugadas (Accuracy)", unidad: "%" },
  CUMPLIMIENTO_ENTRENAMIENTO: { label: "Cumplimiento del Plan Semanal", unidad: "%" },
  CUMPLIMIENTO_OBJETIVOS: { label: "Avance de Metas SMART", unidad: "%" },
  ACPL: { label: "Pérdida Promedio de Centipeones (ACPL)", unidad: "cp", menorEsMejor: true },
  ASISTENCIA: { label: "Asistencia a Sesiones Oficiales", unidad: "%" },
  RENDIMIENTO_POR_APERTURA: { label: "Efectividad en Aperturas Clave", unidad: "%" },
  GESTION_DEL_TIEMPO: { label: "Eficiencia en Control de Reloj", unidad: "%" },
};

export default function ConfiguracionPage() {
  const [tabActiva, setTabActiva] = useState<"LIMITES" | "RANGOS" | "INVITADOS" | "MOTOR">("LIMITES");
  const [config, setConfig] = useState<ConfiguracionSistema | null>(null);
  const [cargando, setCargando] = useState<boolean>(true);
  const [guardando, setGuardando] = useState<boolean>(false);
  const [mensajeExito, setMensajeExito] = useState<string | null>(null);

  // Form states
  const [maxAtletas, setMaxAtletas] = useState<number>(40);
  const [minEntrenadores, setMinEntrenadores] = useState<number>(1);
  const [maxEntrenadores, setMaxEntrenadores] = useState<number>(3);
  const [permitirAutoevaluacion, setPermitirAutoevaluacion] = useState<boolean>(true);
  const [rangos, setRangos] = useState<Record<string, [number, number, number]>>({});
  const [seccionesInvitado, setSeccionesInvitado] = useState<string[]>([]);

  useEffect(() => {
    cargarConfiguracion();
  }, []);

  async function cargarConfiguracion() {
    setCargando(true);
    const data = await getConfiguracion();
    setConfig(data);
    setMaxAtletas(data.maximo_atletas_por_entrenador);
    setMinEntrenadores(data.minimo_entrenadores_por_atleta);
    setMaxEntrenadores(data.maximo_entrenadores_por_atleta);
    setPermitirAutoevaluacion(data.permitir_autoevaluacion);
    setRangos(data.rangos_evaluacion);
    setSeccionesInvitado(data.secciones_autorizadas_invitado);
    setCargando(false);
  }

  const handleRangoChange = (clave: string, index: number, valor: number) => {
    setRangos((prev) => {
      const actual = prev[clave] ? [...prev[clave]] : [90, 75, 60];
      actual[index] = valor;
      return {
        ...prev,
        [clave]: actual as [number, number, number],
      };
    });
  };

  const toggleSeccionInvitado = (seccion: string) => {
    setSeccionesInvitado((prev) =>
      prev.includes(seccion)
        ? prev.filter((s) => s !== seccion)
        : [...prev, seccion]
    );
  };

  const handleGuardarTodo = async (e: React.FormEvent) => {
    e.preventDefault();
    setGuardando(true);

    const input: ConfiguracionActualizarInput = {
      maximo_atletas_por_entrenador: maxAtletas,
      minimo_entrenadores_por_atleta: minEntrenadores,
      maximo_entrenadores_por_atleta: maxEntrenadores,
      permitir_autoevaluacion: permitirAutoevaluacion,
      rangos_evaluacion: rangos,
      secciones_autorizadas_invitado: seccionesInvitado,
      actualizado_por: "entrenador.magnus@caissa.org",
    };

    const exito = await actualizarConfiguracion(input);
    setGuardando(false);

    if (exito) {
      setMensajeExito("¡Parámetros y límites operativos guardados exitosamente en SQLite!");
      cargarConfiguracion();
      setTimeout(() => setMensajeExito(null), 4000);
    }
  };

  if (cargando) {
    return (
      <div className="min-h-screen bg-[#070b12] text-slate-100 flex items-center justify-center p-8">
        <div className="text-center space-y-3 font-mono text-xs text-slate-400 animate-pulse">
          <Settings className="w-8 h-8 mx-auto text-emerald-400 animate-spin" />
          <p>Cargando parámetros del sistema desde SQLite...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#070b12] text-slate-100 p-4 sm:p-6 lg:p-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-emerald-400 uppercase tracking-widest mb-1.5">
            <Settings className="w-4 h-4" />
            <span>Módulo de Administración & Personalización Dinámica</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white flex items-center gap-3">
            Configuración del Club & Parámetros
            <span className="text-xs px-2.5 py-0.5 rounded-full font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
              RNF-07.1 / RNF-07.2
            </span>
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1 max-w-3xl">
            Ajuste de límites deportivos, umbrales paramétricos de semáforos analíticos, accesibilidad pública para invitados y calibración del motor Stockfish.
          </p>
        </div>

        {/* Global Save Button */}
        <div>
          <button
            onClick={handleGuardarTodo}
            disabled={guardando}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold text-slate-950 bg-gradient-to-r from-emerald-400 to-teal-400 hover:from-emerald-300 hover:to-teal-300 transition-all shadow-lg shadow-emerald-500/20 disabled:opacity-50"
          >
            <Save className="w-4 h-4" />
            <span>{guardando ? "Guardando..." : "Guardar Configuración Oficial"}</span>
          </button>
        </div>
      </div>

      {/* Alert toast */}
      {mensajeExito && (
        <div className="p-4 rounded-xl bg-emerald-950/70 border border-emerald-500/50 text-emerald-300 text-xs flex items-center justify-between animate-fadeIn shadow-lg shadow-emerald-950/50">
          <div className="flex items-center gap-2.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
            <span className="font-semibold">{mensajeExito}</span>
          </div>
          <button onClick={() => setMensajeExito(null)} className="text-emerald-400 hover:text-white">
            ×
          </button>
        </div>
      )}

      {/* Tabs navigation */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-2 overflow-x-auto scrollbar-none">
        <button
          onClick={() => setTabActiva("LIMITES")}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
            tabActiva === "LIMITES"
              ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-sm"
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-900"
          }`}
        >
          <Sliders className="w-4 h-4" />
          <span>Límites Operativos & Club</span>
        </button>

        <button
          onClick={() => setTabActiva("RANGOS")}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
            tabActiva === "RANGOS"
              ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-sm"
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-900"
          }`}
        >
          <Gauge className="w-4 h-4" />
          <span>Rangos & Semáforos ELO</span>
        </button>

        <button
          onClick={() => setTabActiva("INVITADOS")}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
            tabActiva === "INVITADOS"
              ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-sm"
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-900"
          }`}
        >
          <UserCheck className="w-4 h-4" />
          <span>Seguridad & Modo Invitado</span>
        </button>

        <button
          onClick={() => setTabActiva("MOTOR")}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
            tabActiva === "MOTOR"
              ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-sm"
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-900"
          }`}
        >
          <Cpu className="w-4 h-4" />
          <span>Motor Stockfish & SQLite</span>
        </button>
      </div>

      {/* TAB 1: Límites Operativos & Club */}
      {tabActiva === "LIMITES" && (
        <div className="space-y-6 animate-fadeIn">
          {/* Institutional Dossier */}
          <div className="bg-[#0d1424] p-6 rounded-2xl border border-slate-800 shadow-xl space-y-4">
            <div className="flex items-center gap-2 text-xs font-mono text-emerald-400 uppercase tracking-wider">
              <Building className="w-4 h-4" />
              <span>Identidad Institucional de la Academia</span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-[#070b12] p-4 rounded-xl border border-slate-800">
                <span className="text-[10px] font-mono text-slate-500 block uppercase">
                  Organización Oficial
                </span>
                <span className="text-sm font-bold text-white block mt-0.5">
                  {config?.nombre_club || "Caissa Analytic Club"}
                </span>
              </div>

              <div className="bg-[#070b12] p-4 rounded-xl border border-slate-800">
                <span className="text-[10px] font-mono text-slate-500 block uppercase">
                  Federación de Adscripción
                </span>
                <span className="text-sm font-bold text-emerald-400 block mt-0.5">
                  {config?.federacion || "FIDE Internacional"}
                </span>
              </div>

              <div className="bg-[#070b12] p-4 rounded-xl border border-slate-800">
                <span className="text-[10px] font-mono text-slate-500 block uppercase">
                  Temporada Deportiva Activa
                </span>
                <span className="text-sm font-bold text-cyan-400 block mt-0.5">
                  {config?.temporada_activa || "Ciclo 2026-I"}
                </span>
              </div>
            </div>
          </div>

          {/* Operational Limits */}
          <div className="bg-[#0d1424] p-6 rounded-2xl border border-slate-800 shadow-xl space-y-6">
            <div className="flex items-center gap-2 text-xs font-mono text-emerald-400 uppercase tracking-wider">
              <Layers className="w-4 h-4" />
              <span>Capacidad Operativa del Cuerpo Técnico (RNF-07.1)</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="space-y-1.5">
                <label className="text-xs font-mono text-slate-300 block">
                  Máximo de Atletas por Entrenador:
                </label>
                <input
                  type="number"
                  min="1"
                  max="1000"
                  value={maxAtletas}
                  onChange={(e) => setMaxAtletas(Number(e.target.value))}
                  className="w-full bg-[#070b12] border border-slate-700 rounded-xl px-3.5 py-2.5 text-xs font-mono text-white focus:outline-none focus:border-emerald-500"
                />
                <span className="text-[11px] text-slate-500 block">
                  Límite máximo de expedientes asignables a un solo DT.
                </span>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-mono text-slate-300 block">
                  Mínimo de Entrenadores por Atleta:
                </label>
                <input
                  type="number"
                  min="1"
                  max="5"
                  value={minEntrenadores}
                  onChange={(e) => setMinEntrenadores(Number(e.target.value))}
                  className="w-full bg-[#070b12] border border-slate-700 rounded-xl px-3.5 py-2.5 text-xs font-mono text-white focus:outline-none focus:border-emerald-500"
                />
                <span className="text-[11px] text-slate-500 block">
                  Todo atleta debe tener al menos 1 DT responsable asignado.
                </span>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-mono text-slate-300 block">
                  Máximo de Entrenadores por Atleta:
                </label>
                <input
                  type="number"
                  min="1"
                  max="10"
                  value={maxEntrenadores}
                  onChange={(e) => setMaxEntrenadores(Number(e.target.value))}
                  className="w-full bg-[#070b12] border border-slate-700 rounded-xl px-3.5 py-2.5 text-xs font-mono text-white focus:outline-none focus:border-emerald-500"
                />
                <span className="text-[11px] text-slate-500 block">
                  Límite de entrenadores co-asignados (ej. DT Principal + Táctico).
                </span>
              </div>
            </div>

            {/* Toggle Autoevaluacion */}
            <div className="pt-4 border-t border-slate-800 flex items-center justify-between">
              <div>
                <span className="text-xs font-bold text-white block">
                  Permitir Autoevaluaciones a los Atletas
                </span>
                <span className="text-xs text-slate-400 block mt-0.5">
                  Habilita a los ajedrecistas registrar impresiones personales tras torneos sin mezclarse con la evaluación oficial del DT.
                </span>
              </div>

              <button
                type="button"
                onClick={() => setPermitirAutoevaluacion(!permitirAutoevaluacion)}
                className={`w-12 h-6 flex items-center rounded-full p-1 transition-colors duration-300 ${
                  permitirAutoevaluacion ? "bg-emerald-500" : "bg-slate-700"
                }`}
              >
                <div
                  className={`bg-white w-4 h-4 rounded-full shadow-md transform transition-transform duration-300 ${
                    permitirAutoevaluacion ? "translate-x-6" : "translate-x-0"
                  }`}
                />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: Rangos y Semáforos ELO (RNF-07.2) */}
      {tabActiva === "RANGOS" && (
        <div className="space-y-6 animate-fadeIn">
          <div className="bg-gradient-to-r from-emerald-950/40 via-teal-950/20 to-transparent p-4 rounded-2xl border border-emerald-800/40 flex items-start gap-3">
            <Gauge className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
            <div className="text-xs leading-relaxed text-slate-300">
              <strong className="text-white">Parametrización Dinámica sin Código (RNF-07.2): </strong>
              Los semáforos analíticos del Command Center, apertura de partidas y cumplimiento de metas SMART se rigen por estos 3 umbrales:
              <span className="text-emerald-400 font-bold ml-1">Verde (Excelente)</span>,
              <span className="text-teal-400 font-bold ml-1">Verde Claro (Bueno)</span> y
              <span className="text-amber-400 font-bold ml-1">Amarillo (Aceptable)</span>. Valores inferiores disparan el semáforo
              <span className="text-rose-400 font-bold ml-1">Rojo (Requiere Intervención)</span>.
            </div>
          </div>

          <div className="bg-[#0d1424] rounded-2xl border border-slate-800 shadow-xl overflow-hidden">
            <div className="p-4 sm:p-5 border-b border-slate-800 flex items-center justify-between">
              <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">
                Indicadores y Umbrales Oficiales
              </span>
              <span className="text-xs font-mono text-emerald-400">
                Escala Paramétrica FIDE
              </span>
            </div>

            <div className="divide-y divide-slate-800/80">
              {Object.entries(rangos).map(([clave, valores]) => {
                const info = NOMBRES_RANGOS[clave] || { label: clave, unidad: "pts" };
                return (
                  <div key={clave} className="p-4 sm:p-5 flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                    <div className="lg:w-1/3">
                      <span className="font-bold text-white text-sm block">
                        {info.label}
                      </span>
                      <span className="text-xs font-mono text-slate-500">
                        Código: {clave} {info.menorEsMejor && "(Menor valor es mejor)"}
                      </span>
                    </div>

                    <div className="grid grid-cols-3 gap-3 lg:w-2/3">
                      {/* Excelente */}
                      <div className="bg-[#070b12] p-2.5 rounded-xl border border-emerald-900/40">
                        <span className="text-[10px] font-mono text-emerald-400 block uppercase font-bold">
                          Excelente (Verde)
                        </span>
                        <div className="flex items-center gap-1 mt-1">
                          <input
                            type="number"
                            step="0.5"
                            value={valores[0]}
                            onChange={(e) => handleRangoChange(clave, 0, Number(e.target.value))}
                            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-2 py-1 text-xs font-mono text-white focus:outline-none focus:border-emerald-500"
                          />
                          <span className="text-xs font-mono text-slate-400">{info.unidad}</span>
                        </div>
                      </div>

                      {/* Bueno */}
                      <div className="bg-[#070b12] p-2.5 rounded-xl border border-teal-900/40">
                        <span className="text-[10px] font-mono text-teal-400 block uppercase font-bold">
                          Bueno (Verde Claro)
                        </span>
                        <div className="flex items-center gap-1 mt-1">
                          <input
                            type="number"
                            step="0.5"
                            value={valores[1]}
                            onChange={(e) => handleRangoChange(clave, 1, Number(e.target.value))}
                            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-2 py-1 text-xs font-mono text-white focus:outline-none focus:border-teal-500"
                          />
                          <span className="text-xs font-mono text-slate-400">{info.unidad}</span>
                        </div>
                      </div>

                      {/* Aceptable */}
                      <div className="bg-[#070b12] p-2.5 rounded-xl border border-amber-900/40">
                        <span className="text-[10px] font-mono text-amber-400 block uppercase font-bold">
                          Aceptable (Amarillo)
                        </span>
                        <div className="flex items-center gap-1 mt-1">
                          <input
                            type="number"
                            step="0.5"
                            value={valores[2]}
                            onChange={(e) => handleRangoChange(clave, 2, Number(e.target.value))}
                            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-2 py-1 text-xs font-mono text-white focus:outline-none focus:border-amber-500"
                          />
                          <span className="text-xs font-mono text-slate-400">{info.unidad}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: Seguridad & Modo Invitado */}
      {tabActiva === "INVITADOS" && (
        <div className="space-y-6 animate-fadeIn">
          <div className="bg-[#0d1424] p-6 rounded-2xl border border-slate-800 shadow-xl space-y-6">
            <div className="flex items-center gap-2 text-xs font-mono text-cyan-400 uppercase tracking-wider">
              <Shield className="w-4 h-4" />
              <span>Privacidad & Concesión de Secciones para Rol Invitado</span>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed max-w-3xl">
              El rol <strong className="text-white">Invitado</strong> está pensado para visores de prensa, federativos o patrocinadores externos. Configure qué vistas del club están autorizadas para acceso público sin credenciales de entrenador o atleta.
            </p>

            <div className="space-y-3">
              {[
                {
                  id: "perfil_publico",
                  titulo: "Expediente Deportivo Público (perfil_publico)",
                  desc: "Permite ver nombres de atletas, ratings FIDE oficiales y títulos federativos (sin notas confidenciales del DT).",
                },
                {
                  id: "ranking",
                  titulo: "Tabla de Posiciones & Ranking Interno (ranking)",
                  desc: "Muestra el escalafón del club ordenado por ELO clásico, rápido y blitz.",
                },
                {
                  id: "resumen_equipo",
                  titulo: "Métricas Consolidadas del Equipo (resumen_equipo)",
                  desc: "Exhibe estadísticas agregadas del club (número de victorias, torneos disputados y ELO promedio colectivo).",
                },
              ].map((item) => {
                const activo = seccionesInvitado.includes(item.id);
                return (
                  <div
                    key={item.id}
                    onClick={() => toggleSeccionInvitado(item.id)}
                    className={`p-4 rounded-xl border cursor-pointer transition-all flex items-start justify-between gap-4 ${
                      activo
                        ? "bg-emerald-950/20 border-emerald-500/40 text-slate-200"
                        : "bg-[#070b12] border-slate-800 text-slate-400 hover:border-slate-700"
                    }`}
                  >
                    <div>
                      <span className="text-sm font-bold text-white block">
                        {item.titulo}
                      </span>
                      <span className="text-xs text-slate-400 block mt-1">
                        {item.desc}
                      </span>
                    </div>

                    <div
                      className={`w-5 h-5 rounded-md border flex items-center justify-center flex-shrink-0 mt-1 transition-colors ${
                        activo
                          ? "bg-emerald-500 border-emerald-400 text-slate-950"
                          : "border-slate-600 bg-slate-900"
                      }`}
                    >
                      {activo && <CheckCircle2 className="w-4 h-4 stroke-[3]" />}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* TAB 4: Motor Stockfish & SQLite */}
      {tabActiva === "MOTOR" && (
        <div className="space-y-6 animate-fadeIn">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Stockfish Engine */}
            <div className="bg-[#0d1424] p-6 rounded-2xl border border-slate-800 shadow-xl space-y-4">
              <div className="flex items-center gap-2 text-xs font-mono text-emerald-400 uppercase tracking-wider">
                <Zap className="w-4 h-4" />
                <span>Motor de Análisis Táctico Stockfish</span>
              </div>

              <div className="space-y-3 font-mono text-xs">
                <div className="flex justify-between p-3 rounded-xl bg-[#070b12] border border-slate-800">
                  <span className="text-slate-400">Versión:</span>
                  <span className="text-emerald-400 font-bold">
                    {config?.motor_stockfish?.version || "Stockfish 16.1 NNUE"}
                  </span>
                </div>

                <div className="flex justify-between p-3 rounded-xl bg-[#070b12] border border-slate-800">
                  <span className="text-slate-400">Profundidad por Defecto:</span>
                  <span className="text-white font-bold">
                    {config?.motor_stockfish?.profundidad_defecto || 18} plies
                  </span>
                </div>

                <div className="flex justify-between p-3 rounded-xl bg-[#070b12] border border-slate-800">
                  <span className="text-slate-400">Hilos CPU Asignados:</span>
                  <span className="text-white font-bold">
                    {config?.motor_stockfish?.hilos_cpu || 4} Cores
                  </span>
                </div>

                <div className="flex justify-between p-3 rounded-xl bg-[#070b12] border border-slate-800">
                  <span className="text-slate-400">Memoria Hash (RAM):</span>
                  <span className="text-white font-bold">
                    {config?.motor_stockfish?.hash_mb || 256} MB
                  </span>
                </div>
              </div>
            </div>

            {/* SQLite & Persistence */}
            <div className="bg-[#0d1424] p-6 rounded-2xl border border-slate-800 shadow-xl space-y-4">
              <div className="flex items-center gap-2 text-xs font-mono text-cyan-400 uppercase tracking-wider">
                <Database className="w-4 h-4" />
                <span>Almacenamiento Local & SQLite</span>
              </div>

              <div className="space-y-3 font-mono text-xs">
                <div className="flex justify-between p-3 rounded-xl bg-[#070b12] border border-slate-800">
                  <span className="text-slate-400">Base de Datos:</span>
                  <span className="text-cyan-400 font-bold">caissa.db</span>
                </div>

                <div className="flex justify-between p-3 rounded-xl bg-[#070b12] border border-slate-800">
                  <span className="text-slate-400">Modo de Hilos:</span>
                  <span className="text-white font-bold">check_same_thread=False</span>
                </div>

                <div className="flex justify-between p-3 rounded-xl bg-[#070b12] border border-slate-800">
                  <span className="text-slate-400">Última Actualización:</span>
                  <span className="text-slate-300 font-medium">
                    {config?.fecha_actualizacion ? new Date(config.fecha_actualizacion).toLocaleString("es-ES") : "Hoy"}
                  </span>
                </div>

                <div className="flex justify-between p-3 rounded-xl bg-[#070b12] border border-slate-800">
                  <span className="text-slate-400">Modificado por:</span>
                  <span className="text-slate-300 font-medium truncate max-w-[180px]">
                    {config?.actualizado_por || "sistema"}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
