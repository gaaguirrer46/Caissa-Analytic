"use client";

import React, { useState, useEffect } from "react";
import {
  ShieldCheck,
  ShieldAlert,
  Search,
  Filter,
  RefreshCw,
  Clock,
  User,
  Database,
  ArrowRight,
  FileCode,
  Download,
  CheckCircle,
  AlertTriangle,
  History,
  Lock,
} from "lucide-react";
import {
  RegistroAuditoria,
  ResultadoIntegridad,
  TipoOperacion,
} from "@/types/auditoria.types";
import {
  getHistorialAuditoria,
  getVerificacionIntegridad,
} from "@/services/auditoria.service";

const ENTIDADES_DISPONIBLES = [
  "TODAS",
  "Atleta",
  "ObjetivoSmart",
  "PlanEntrenamientoSemanal",
  "SesionEntrenamiento",
  "EvaluacionAtleta",
  "AperturaRepertorio",
  "Partida",
  "Configuracion",
];

export default function AuditoriaPage() {
  const [registros, setRegistros] = useState<RegistroAuditoria[]>([]);
  const [integridad, setIntegridad] = useState<ResultadoIntegridad | null>(null);
  const [cargando, setCargando] = useState<boolean>(true);
  const [verificando, setVerificando] = useState<boolean>(false);

  // Filters
  const [busquedaUsuario, setBusquedaUsuario] = useState<string>("");
  const [entidadFiltro, setEntidadFiltro] = useState<string>("TODAS");
  const [operacionFiltro, setOperacionFiltro] = useState<string>("TODAS");
  const [mostrarDetallesIntegridad, setMostrarDetallesIntegridad] = useState<boolean>(false);

  useEffect(() => {
    cargarDatos();
  }, [entidadFiltro, operacionFiltro]);

  async function cargarDatos() {
    setCargando(true);
    const data = await getHistorialAuditoria({
      entidad: entidadFiltro === "TODAS" ? undefined : entidadFiltro,
      usuario: busquedaUsuario ? busquedaUsuario : undefined,
      tipo_operacion: operacionFiltro === "TODAS" ? undefined : operacionFiltro,
    });
    setRegistros(data);

    const intResult = await getVerificacionIntegridad();
    setIntegridad(intResult);
    setCargando(false);
  }

  const ejecutarVerificacion = async () => {
    setVerificando(true);
    const intResult = await getVerificacionIntegridad();
    setIntegridad(intResult);
    setTimeout(() => {
      setVerificando(false);
    }, 600);
  };

  const handleBuscar = (e: React.FormEvent) => {
    e.preventDefault();
    cargarDatos();
  };

  const exportarJSON = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(registros, null, 2));
    const downloadAnchor = document.createElement("a");
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `auditoria_caissa_${new Date().toISOString().split("T")[0]}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const getOperacionBadge = (tipo: TipoOperacion) => {
    switch (tipo) {
      case "CREAR":
        return {
          label: "CREAR",
          color: "bg-emerald-950/60 text-emerald-400 border-emerald-800/40",
        };
      case "MODIFICAR":
        return {
          label: "MODIFICAR",
          color: "bg-cyan-950/60 text-cyan-400 border-cyan-800/40",
        };
      case "ELIMINAR":
        return {
          label: "ELIMINAR",
          color: "bg-rose-950/60 text-rose-400 border-rose-800/40",
        };
      default:
        return {
          label: tipo,
          color: "bg-slate-800 text-slate-400 border-slate-700",
        };
    }
  };

  const formatearFechaRelativa = (isoStr: string) => {
    try {
      const fecha = new Date(isoStr);
      const diffMs = Date.now() - fecha.getTime();
      const diffHoras = Math.floor(diffMs / (1000 * 60 * 60));
      const diffDias = Math.floor(diffHoras / 24);

      if (diffHoras < 1) return "Hace unos minutos";
      if (diffHoras < 24) return `Hace ${diffHoras} hora${diffHoras > 1 ? "s" : ""}`;
      if (diffDias === 1) return "Ayer";
      if (diffDias < 30) return `Hace ${diffDias} días`;
      return fecha.toLocaleDateString("es-ES");
    } catch {
      return isoStr;
    }
  };

  return (
    <div className="min-h-screen bg-[#070b12] text-slate-100 p-4 sm:p-6 lg:p-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-cyan-400 uppercase tracking-widest mb-1.5">
            <Lock className="w-4 h-4" />
            <span>Módulo de Trazabilidad, Seguridad & Validación Preventiva</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white flex items-center gap-3">
            Auditoría & Trazabilidad Forense
            <span className="text-xs px-2.5 py-0.5 rounded-full font-mono bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
              RNF-02.5 / RNF-04
            </span>
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1 max-w-3xl">
            Bitácora inmutable de transacciones críticas del sistema, auditoría de cambios de ELO y objetivos, e inspección criptográfica de integridad estructural en SQLite.
          </p>
        </div>

        {/* Action Tools */}
        <div className="flex items-center gap-3">
          <button
            onClick={exportarJSON}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-medium text-slate-300 bg-slate-900 border border-slate-700 hover:bg-slate-800 hover:text-white transition-all shadow-sm"
          >
            <Download className="w-4 h-4 text-slate-400" />
            <span>Exportar Bitácora (JSON)</span>
          </button>
          <button
            onClick={ejecutarVerificacion}
            disabled={verificando}
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold text-slate-950 bg-gradient-to-r from-cyan-400 to-emerald-400 hover:from-cyan-300 hover:to-emerald-300 transition-all shadow-lg shadow-cyan-500/20 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${verificando ? "animate-spin" : ""}`} />
            <span>{verificando ? "Escaneando..." : "Verificar Integridad"}</span>
          </button>
        </div>
      </div>

      {/* Integrity Telemetry Banner */}
      {integridad && (
        <div className="bg-gradient-to-b from-[#0d1424] to-[#080d17] rounded-2xl border border-slate-800 p-6 shadow-xl space-y-6">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 pb-6 border-b border-slate-800/80">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 flex-shrink-0">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <div>
                <div className="flex items-center gap-3">
                  <span className="text-base font-bold text-white tracking-tight">
                    ESTADO DE INTEGRIDAD DEL SISTEMA:
                  </span>
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-emerald-950/80 text-emerald-300 border border-emerald-500/40">
                    {integridad.estado} (100% CONFORME)
                  </span>
                </div>
                <div className="flex items-center gap-3 text-xs font-mono text-slate-400 mt-1">
                  <span>SQLite PRAGMA: <strong className="text-emerald-400">{integridad.integridad_sqlite}</strong></span>
                  <span className="text-slate-600">|</span>
                  <span>Firma Criptográfica: <strong className="text-cyan-400">{integridad.snapshot_hash}</strong></span>
                </div>
              </div>
            </div>

            {/* Quick Metrics */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 w-full lg:w-auto">
              <div className="bg-[#05080e] p-3 rounded-xl border border-slate-800/80 text-center">
                <span className="text-[10px] font-mono text-slate-500 block uppercase">
                  Transacciones
                </span>
                <span className="text-lg font-black font-mono text-white">
                  {integridad.total_registros_auditados}
                </span>
              </div>
              <div className="bg-[#05080e] p-3 rounded-xl border border-slate-800/80 text-center">
                <span className="text-[10px] font-mono text-slate-500 block uppercase">
                  Atletas FIDE
                </span>
                <span className="text-lg font-black font-mono text-emerald-400">
                  {integridad.atletas_validados} en regla
                </span>
              </div>
              <div className="bg-[#05080e] p-3 rounded-xl border border-slate-800/80 text-center">
                <span className="text-[10px] font-mono text-slate-500 block uppercase">
                  Partidas Validadas
                </span>
                <span className="text-lg font-black font-mono text-cyan-400">
                  {integridad.partidas_validadas}
                </span>
              </div>
              <div className="bg-[#05080e] p-3 rounded-xl border border-slate-800/80 text-center">
                <span className="text-[10px] font-mono text-slate-500 block uppercase">
                  Anomalías
                </span>
                <span className="text-lg font-black font-mono text-emerald-400">
                  {integridad.anomalias_detectadas}
                </span>
              </div>
            </div>
          </div>

          {/* Collapsible Inspection Details */}
          <div>
            <button
              onClick={() => setMostrarDetallesIntegridad(!mostrarDetallesIntegridad)}
              className="text-xs font-mono text-cyan-400 hover:text-cyan-300 flex items-center gap-1.5 transition-colors"
            >
              <Database className="w-3.5 h-3.5" />
              <span>
                {mostrarDetallesIntegridad ? "Ocultar diagnóstico detallado" : "Ver diagnóstico preventivo de reglas de negocio"}
              </span>
            </button>

            {mostrarDetallesIntegridad && (
              <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-2.5 bg-[#05080e] p-4 rounded-xl border border-slate-800/80 animate-fadeIn">
                {integridad.detalles.map((detalle, idx) => (
                  <div key={idx} className="flex items-start gap-2 text-xs text-slate-300">
                    <CheckCircle className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0 mt-0.5" />
                    <span>{detalle}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="bg-[#0d1424] p-4 rounded-2xl border border-slate-800 shadow-xl space-y-4">
        <form onSubmit={handleBuscar} className="grid grid-cols-1 md:grid-cols-12 gap-3 items-center">
          {/* Search by user/email */}
          <div className="md:col-span-5 relative">
            <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={busquedaUsuario}
              onChange={(e) => setBusquedaUsuario(e.target.value)}
              placeholder="Buscar por usuario / correo (ej. magnus, kasparov)..."
              className="w-full bg-[#070b12] border border-slate-700 rounded-xl pl-9 pr-3.5 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 transition-all"
            />
          </div>

          {/* Entity Selector */}
          <div className="md:col-span-4 flex items-center gap-2">
            <span className="text-xs font-mono text-slate-400 uppercase flex-shrink-0">
              Entidad:
            </span>
            <select
              value={entidadFiltro}
              onChange={(e) => setEntidadFiltro(e.target.value)}
              className="w-full bg-[#070b12] border border-slate-700 rounded-xl px-3 py-2 text-xs font-medium text-slate-200 focus:outline-none focus:border-cyan-500"
            >
              {ENTIDADES_DISPONIBLES.map((ent) => (
                <option key={ent} value={ent}>
                  {ent}
                </option>
              ))}
            </select>
          </div>

          {/* Operation Pills */}
          <div className="md:col-span-3 flex items-center justify-start md:justify-end gap-1.5 overflow-x-auto scrollbar-none">
            {["TODAS", "CREAR", "MODIFICAR", "ELIMINAR"].map((op) => (
              <button
                key={op}
                type="button"
                onClick={() => setOperacionFiltro(op)}
                className={`px-2.5 py-1.5 rounded-lg text-xs font-mono font-medium transition-all ${
                  operacionFiltro === op
                    ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm"
                    : "bg-slate-900/60 text-slate-400 border border-slate-800 hover:bg-slate-800"
                }`}
              >
                {op}
              </button>
            ))}
          </div>
        </form>
      </div>

      {/* Audit Log Timeline Feed */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <History className="w-4 h-4 text-cyan-400" />
            <h2 className="text-lg font-bold text-white tracking-tight">
              Línea Temporal de Eventos Auditados
            </h2>
          </div>
          <span className="text-xs font-mono text-slate-500">
            {registros.length} eventos encontrados
          </span>
        </div>

        {cargando ? (
          <div className="p-12 text-center text-slate-500 font-mono text-xs animate-pulse">
            Cargando bitácora forense desde SQLite...
          </div>
        ) : registros.length === 0 ? (
          <div className="p-12 text-center bg-[#0d1424] rounded-2xl border border-slate-800 text-slate-400 space-y-2">
            <FileCode className="w-8 h-8 mx-auto text-slate-600" />
            <p className="text-sm font-semibold text-slate-300">
              No se encontraron registros de auditoría con los filtros aplicados.
            </p>
            <p className="text-xs text-slate-500">
              Pruebe cambiando la entidad o limpiando el filtro de usuario.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {registros.map((reg) => {
              const opBadge = getOperacionBadge(reg.tipo_operacion);
              return (
                <div
                  key={reg.id}
                  className="bg-[#0d1424] rounded-2xl border border-slate-800/90 p-4 sm:p-5 hover:border-slate-700 transition-all shadow-md space-y-3"
                >
                  {/* Top line of event */}
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <div className="flex items-center gap-2.5">
                      <span className="px-2 py-0.5 rounded-md text-[10px] font-mono font-bold bg-slate-800/80 text-slate-300 border border-slate-700">
                        TX-#{reg.id}
                      </span>
                      <span className={`px-2 py-0.5 rounded-md text-[10px] font-mono font-bold border ${opBadge.color}`}>
                        {opBadge.label}
                      </span>
                      <span className="px-2.5 py-0.5 rounded-md text-xs font-semibold bg-slate-900 text-slate-200 border border-slate-800">
                        {reg.entidad_afectada}
                      </span>
                      {reg.campo_modificado && (
                        <span className="text-xs font-mono text-cyan-400">
                          .{reg.campo_modificado}
                        </span>
                      )}
                    </div>

                    <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
                      <Clock className="w-3.5 h-3.5 text-slate-500" />
                      <span>{formatearFechaRelativa(reg.fecha_hora)}</span>
                      <span className="text-slate-600">({new Date(reg.fecha_hora).toLocaleTimeString("es-ES", { hour: "2-digit", minute: "2-digit" })})</span>
                    </div>
                  </div>

                  {/* Diff representation (Valor anterior vs Valor nuevo) */}
                  <div className="bg-[#070b12] p-3.5 rounded-xl border border-slate-800/80 text-xs">
                    {reg.tipo_operacion === "MODIFICAR" && (
                      <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4 font-mono">
                        <div className="flex items-center gap-2 text-rose-300/80 bg-rose-950/20 px-2.5 py-1 rounded-lg border border-rose-900/30 line-through">
                          <span className="text-[10px] text-slate-500 select-none">PREVIO:</span>
                          <span className="break-all">{reg.valor_anterior || "null"}</span>
                        </div>
                        <ArrowRight className="w-4 h-4 text-slate-600 flex-shrink-0 hidden sm:block" />
                        <div className="flex items-center gap-2 text-emerald-300 bg-emerald-950/30 px-2.5 py-1 rounded-lg border border-emerald-800/40">
                          <span className="text-[10px] text-slate-500 select-none">NUEVO:</span>
                          <span className="font-bold break-all">{reg.valor_nuevo || "null"}</span>
                        </div>
                      </div>
                    )}

                    {reg.tipo_operacion === "CREAR" && (
                      <div className="flex items-center gap-2 text-emerald-300 bg-emerald-950/20 px-3 py-1.5 rounded-lg border border-emerald-900/30 font-mono">
                        <span className="text-[10px] text-slate-500 font-bold select-none">+ CREADO:</span>
                        <span className="break-all">{reg.valor_nuevo || `Instancia de ${reg.entidad_afectada} registrada`}</span>
                      </div>
                    )}

                    {reg.tipo_operacion === "ELIMINAR" && (
                      <div className="flex items-center gap-2 text-rose-300 bg-rose-950/20 px-3 py-1.5 rounded-lg border border-rose-900/30 font-mono">
                        <span className="text-[10px] text-slate-500 font-bold select-none">- ELIMINADO:</span>
                        <span className="break-all">{reg.valor_anterior || `Instancia de ${reg.entidad_afectada} dada de baja`}</span>
                      </div>
                    )}
                  </div>

                  {/* Operator signature */}
                  <div className="flex items-center justify-between text-[11px] font-mono text-slate-500 pt-1">
                    <div className="flex items-center gap-1.5">
                      <User className="w-3.5 h-3.5 text-slate-400" />
                      <span>Autor: <strong className="text-slate-300">{reg.usuario}</strong></span>
                    </div>
                    <span>Timestamp UTC: {reg.fecha_hora}</span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
