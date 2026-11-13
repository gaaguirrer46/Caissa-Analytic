"use client";

import { use, useState } from "react";
import Link from "next/link";
import { notFound } from "next/navigation";
import {
  ArrowLeft,
  Calendar,
  GraduationCap,
  Shield,
  Trophy,
  Activity,
  Award,
  Globe,
  TrendingUp,
  FileText,
  UserCheck,
  Target,
  Clock,
  Sparkles,
  ChevronRight,
} from "lucide-react";
import { ATLETAS_MOCK } from "@/services/atletas.service";
import { calcularEdad } from "@/types/atleta.types";

interface Props {
  params: Promise<{ id: string }>;
}

export default function AtletaDetallePage({ params }: Props) {
  const resolvedParams = use(params);
  const atletaId = parseInt(resolvedParams.id, 10);
  const atleta = ATLETAS_MOCK.find((a) => a.id === atletaId);

  const [pestanaActiva, setPestanaActiva] = useState<"torneos" | "objetivos" | "ficha">("torneos");

  if (!atleta) {
    notFound();
  }

  const edad = calcularEdad(atleta.fecha_nacimiento);

  return (
    <div className="min-h-screen bg-[#070b12] text-slate-100 py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-6 font-sans">
      {/* Top back navigation */}
      <div>
        <Link
          href="/atletas"
          className="inline-flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-emerald-400 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Volver al catálogo de atletas
        </Link>
      </div>

      {/* Profile Master Hero Banner */}
      <div className="p-6 sm:p-8 rounded-3xl border border-slate-800/90 bg-gradient-to-br from-[#0d1424] via-[#0a101d] to-[#070b12] shadow-2xl space-y-6">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="flex items-center gap-5">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-emerald-500 via-teal-600 to-emerald-800 p-0.5 shadow-xl shadow-emerald-500/20 flex-shrink-0">
              <div className="w-full h-full bg-[#070b12] rounded-[14px] flex items-center justify-center font-black text-2xl text-emerald-400">
                {atleta.nombre
                  .split(" ")
                  .map((n) => n[0])
                  .slice(0, 2)
                  .join("")}
              </div>
            </div>

            <div>
              <div className="flex flex-wrap items-center gap-3">
                <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
                  {atleta.nombre}
                </h1>
                <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-xs font-mono font-bold flex items-center gap-1">
                  <UserCheck className="w-3.5 h-3.5" /> ATLETA FEDERADO
                </span>
              </div>
              <p className="text-xs sm:text-sm text-slate-400 mt-1">
                {edad} años ({atleta.sexo === "M" ? "Masculino" : "Femenino"}) • Nacimiento: {atleta.fecha_nacimiento} • {atleta.federacion}
              </p>
              {atleta.universidad && (
                <p className="text-xs text-slate-500 mt-0.5">
                  {atleta.universidad} {atleta.carrera && `• ${atleta.carrera}`}
                </p>
              )}
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Link
              href={`/partidas?atleta=${atleta.id}`}
              className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-bold text-xs shadow-lg shadow-emerald-500/20 transition-all"
            >
              <Trophy className="w-4 h-4" /> Ver Partidas en Suite PGN
            </Link>
          </div>
        </div>

        {/* 5 ELO Modality Cards (TradingView / Aimchess style) */}
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 pt-4 border-t border-slate-800/80 font-mono">
          <div className="p-3.5 rounded-2xl bg-[#070b12] border border-slate-800 text-center space-y-1">
            <span className="text-[10px] uppercase font-bold text-slate-400 block">FIDE Clásico</span>
            <span className="text-2xl font-black text-emerald-400">
              {atleta.rating_actual.clasicas || "S/R"}
            </span>
            <span className="text-[10px] text-emerald-500/80 block">+15 este ciclo</span>
          </div>
          <div className="p-3.5 rounded-2xl bg-[#070b12] border border-slate-800 text-center space-y-1">
            <span className="text-[10px] uppercase font-bold text-slate-400 block">FIDE Rápido</span>
            <span className="text-2xl font-black text-blue-400">
              {atleta.rating_actual.rapidas || "S/R"}
            </span>
            <span className="text-[10px] text-blue-500/80 block">+8 este ciclo</span>
          </div>
          <div className="p-3.5 rounded-2xl bg-[#070b12] border border-slate-800 text-center space-y-1">
            <span className="text-[10px] uppercase font-bold text-slate-400 block">FIDE Blitz</span>
            <span className="text-2xl font-black text-amber-400">
              {atleta.rating_actual.blitz || "S/R"}
            </span>
            <span className="text-[10px] text-amber-500/80 block">+22 este ciclo</span>
          </div>
          <div className="p-3.5 rounded-2xl bg-[#070b12] border border-slate-800 text-center space-y-1">
            <span className="text-[10px] uppercase font-bold text-slate-400 block">Chess.com</span>
            <span className="text-2xl font-black text-teal-400">
              {atleta.rating_actual.chess_com || "—"}
            </span>
            <span className="text-[10px] text-slate-500 block">Digital Blitz</span>
          </div>
          <div className="p-3.5 rounded-2xl bg-[#070b12] border border-slate-800 text-center space-y-1 col-span-2 sm:col-span-1">
            <span className="text-[10px] uppercase font-bold text-slate-400 block">Lichess</span>
            <span className="text-2xl font-black text-purple-400">
              {atleta.rating_actual.lichess || "—"}
            </span>
            <span className="text-[10px] text-slate-500 block">Digital Rapid</span>
          </div>
        </div>
      </div>

      {/* Tabs navigation row */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-2 text-xs font-semibold">
        <button
          onClick={() => setPestanaActiva("torneos")}
          className={`px-4 py-2 rounded-xl transition-all ${
            pestanaActiva === "torneos"
              ? "bg-emerald-500/15 text-emerald-300 border border-emerald-500/30"
              : "text-slate-400 hover:text-white"
          }`}
        >
          Historial de Torneos ({atleta.historial.length})
        </button>
        <button
          onClick={() => setPestanaActiva("objetivos")}
          className={`px-4 py-2 rounded-xl transition-all ${
            pestanaActiva === "objetivos"
              ? "bg-emerald-500/15 text-emerald-300 border border-emerald-500/30"
              : "text-slate-400 hover:text-white"
          }`}
        >
          Objetivos SMART (RF-03.5/6)
        </button>
        <button
          onClick={() => setPestanaActiva("ficha")}
          className={`px-4 py-2 rounded-xl transition-all ${
            pestanaActiva === "ficha"
              ? "bg-emerald-500/15 text-emerald-300 border border-emerald-500/30"
              : "text-slate-400 hover:text-white"
          }`}
        >
          Ficha Técnica & Clubes
        </button>
      </div>

      {/* Tab 1: Tournaments History */}
      {pestanaActiva === "torneos" && (
        <div className="p-6 rounded-2xl border border-slate-800/90 bg-[#0d1424]/70 space-y-4">
          <h2 className="font-bold text-sm text-white uppercase tracking-wider flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-emerald-400" /> Registro Oficial de Torneos y Evolución ELO
          </h2>

          {atleta.historial.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 text-[10px] uppercase font-mono tracking-wider">
                    <th className="py-2.5 px-3">Año</th>
                    <th className="py-2.5 px-3">Torneo / Evento Oficial</th>
                    <th className="py-2.5 px-3 font-mono">FIDE Clásicas</th>
                    <th className="py-2.5 px-3 font-mono">FIDE Rápidas</th>
                    <th className="py-2.5 px-3">Observaciones del Entrenador</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-sans">
                  {atleta.historial.map((snap) => (
                    <tr key={snap.id} className="hover:bg-slate-800/30 transition-colors">
                      <td className="py-3 px-3 font-mono font-bold text-white">{snap.anio}</td>
                      <td className="py-3 px-3 text-slate-200 font-semibold">{snap.torneo}</td>
                      <td className="py-3 px-3 font-mono font-bold text-emerald-400">
                        {snap.rating.clasicas || "—"}
                      </td>
                      <td className="py-3 px-3 font-mono font-bold text-blue-400">
                        {snap.rating.rapidas || "—"}
                      </td>
                      <td className="py-3 px-3 text-slate-300 italic text-[11px]">
                        {snap.observaciones || "Completado"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-10 text-slate-500 text-xs font-mono">
              Sin historial de torneos previos registrado.
            </div>
          )}
        </div>
      )}

      {/* Tab 2: SMART Goals */}
      {pestanaActiva === "objetivos" && (
        <div className="p-6 rounded-2xl border border-slate-800/90 bg-[#0d1424]/70 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
            <h2 className="font-bold text-sm text-white uppercase tracking-wider flex items-center gap-2">
              <Target className="w-4 h-4 text-amber-400" /> Metas y Objetivos SMART (RF-03.5 / RF-03.6)
            </h2>
            <span className="text-xs font-mono text-emerald-400">
              Cálculo Automatizado Activo
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-3">
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-[10px] font-mono text-emerald-400 uppercase font-bold">Meta Principal ELO</span>
                  <h3 className="text-sm font-bold text-white mt-0.5">Alcanzar 2,100 ELO FIDE Clásico</h3>
                </div>
                <span className="text-xs font-mono font-bold text-white">81%</span>
              </div>
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div className="bg-gradient-to-r from-emerald-500 to-teal-400 h-full rounded-full" style={{ width: "81%" }} />
              </div>
              <div className="flex justify-between text-[11px] font-mono text-slate-400">
                <span>Actual: {atleta.rating_actual.clasicas || 0} pts</span>
                <span>Objetivo: 2,100 pts (Faltan {2100 - (atleta.rating_actual.clasicas || 0)} pts)</span>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-3">
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-[10px] font-mono text-blue-400 uppercase font-bold">Volumen Táctico</span>
                  <h3 className="text-sm font-bold text-white mt-0.5">500 Problemas de Táctica Mensuales</h3>
                </div>
                <span className="text-xs font-mono font-bold text-white">92%</span>
              </div>
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div className="bg-gradient-to-r from-blue-500 to-cyan-400 h-full rounded-full" style={{ width: "92%" }} />
              </div>
              <div className="flex justify-between text-[11px] font-mono text-slate-400">
                <span>Resueltos: 460 / 500</span>
                <span>Precisión: 89.4%</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 3: Technical Dossier */}
      {pestanaActiva === "ficha" && (
        <div className="p-6 rounded-2xl border border-slate-800/90 bg-[#0d1424]/70 space-y-4">
          <h2 className="font-bold text-sm text-white uppercase tracking-wider flex items-center gap-2">
            <FileText className="w-4 h-4 text-emerald-400" /> Datos Federativos y Académicos
          </h2>

          <dl className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 text-xs font-mono">
            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
              <dt className="text-slate-400 text-[10px] uppercase font-bold">Identificación Oficial</dt>
              <dd className="font-bold text-white mt-1">{atleta.identidad_opcional || "001-140503-1002A"}</dd>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
              <dt className="text-slate-400 text-[10px] uppercase font-bold">Universidad / Institución</dt>
              <dd className="font-bold text-white mt-1">{atleta.universidad || "No asignada"}</dd>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
              <dt className="text-slate-400 text-[10px] uppercase font-bold">Clubes Afiliados</dt>
              <dd className="font-bold text-white mt-1">{atleta.clubs.join(", ") || "Sin club"}</dd>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
              <dt className="text-slate-400 text-[10px] uppercase font-bold">Categorías Registradas</dt>
              <dd className="font-bold text-emerald-400 mt-1">Sub-20 • Categoría A • ELO &gt; 2000</dd>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
              <dt className="text-slate-400 text-[10px] uppercase font-bold">Entrenador Responsable</dt>
              <dd className="font-bold text-white mt-1">ID #101 (Maestro Nacional)</dd>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
              <dt className="text-slate-400 text-[10px] uppercase font-bold">Última Actualización</dt>
              <dd className="font-bold text-slate-300 mt-1">{atleta.rating_actual.fecha_actualizacion || "Reciente"}</dd>
            </div>
          </dl>
        </div>
      )}
    </div>
  );
}
