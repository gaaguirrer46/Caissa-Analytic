"use client";

import { use } from "react";
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

  if (!atleta) {
    notFound();
  }

  const edad = calcularEdad(atleta.fecha_nacimiento);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-8">
      {/* Top back navigation */}
      <div>
        <Link
          href="/atletas"
          className="inline-flex items-center gap-2 text-xs font-medium text-slate-400 hover:text-emerald-400 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Volver al catálogo de atletas
        </Link>
      </div>

      {/* Profile Header Hero */}
      <div className="p-6 sm:p-8 rounded-3xl border border-slate-800 bg-gradient-to-br from-slate-900 via-slate-900/60 to-slate-950 shadow-xl space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6">
          <div className="flex items-center gap-5">
            <div className="w-20 h-20 rounded-3xl bg-gradient-to-br from-emerald-500 to-teal-700 p-0.5 shadow-lg shadow-emerald-500/20">
              <div className="w-full h-full bg-slate-950 rounded-[22px] flex items-center justify-center font-black text-2xl text-emerald-400">
                {atleta.nombre
                  .split(" ")
                  .map((n) => n[0])
                  .slice(0, 2)
                  .join("")}
              </div>
            </div>

            <div>
              <div className="flex items-center gap-3">
                <h1 className="text-2xl sm:text-3xl font-bold text-white">{atleta.nombre}</h1>
                <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-xs font-semibold flex items-center gap-1">
                  <UserCheck className="w-3.5 h-3.5" /> Activo
                </span>
              </div>
              <p className="text-sm text-slate-400 mt-1">
                {edad} años ({atleta.sexo === "M" ? "Masculino" : "Femenino"}) • Nacimiento: {atleta.fecha_nacimiento}
              </p>
              {atleta.federacion && (
                <p className="text-xs text-slate-500 mt-0.5">{atleta.federacion}</p>
              )}
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <Link
              href={`/partidas?atleta=${atleta.id}`}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold text-xs shadow-md transition-colors"
            >
              <Trophy className="w-4 h-4" /> Ver Partidas PGN
            </Link>
          </div>
        </div>

        {/* Badges / Chips */}
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 pt-4 border-t border-slate-800/80">
          <div className="p-3 rounded-2xl bg-slate-950/80 border border-slate-800 text-center">
            <span className="text-[10px] uppercase font-bold text-slate-400 block">FIDE Clásico</span>
            <span className="text-xl font-extrabold text-emerald-400">
              {atleta.rating_actual.clasicas || "S/R"}
            </span>
          </div>
          <div className="p-3 rounded-2xl bg-slate-950/80 border border-slate-800 text-center">
            <span className="text-[10px] uppercase font-bold text-slate-400 block">FIDE Rápido</span>
            <span className="text-xl font-extrabold text-blue-400">
              {atleta.rating_actual.rapidas || "S/R"}
            </span>
          </div>
          <div className="p-3 rounded-2xl bg-slate-950/80 border border-slate-800 text-center">
            <span className="text-[10px] uppercase font-bold text-slate-400 block">FIDE Blitz</span>
            <span className="text-xl font-extrabold text-amber-400">
              {atleta.rating_actual.blitz || "S/R"}
            </span>
          </div>
          <div className="p-3 rounded-2xl bg-slate-950/80 border border-slate-800 text-center">
            <span className="text-[10px] uppercase font-bold text-slate-400 block">Chess.com</span>
            <span className="text-xl font-extrabold text-teal-400">
              {atleta.rating_actual.chess_com || "—"}
            </span>
          </div>
          <div className="p-3 rounded-2xl bg-slate-950/80 border border-slate-800 text-center col-span-2 sm:col-span-1">
            <span className="text-[10px] uppercase font-bold text-slate-400 block">Lichess</span>
            <span className="text-xl font-extrabold text-purple-400">
              {atleta.rating_actual.lichess || "—"}
            </span>
          </div>
        </div>
      </div>

      {/* Two columns: Details & History */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Expediente Académico y Club */}
        <div className="space-y-6">
          <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/40 space-y-4">
            <h2 className="font-bold text-base text-white flex items-center gap-2">
              <FileText className="w-4 h-4 text-emerald-400" /> Ficha Técnica
            </h2>

            <dl className="space-y-3 text-xs">
              <div>
                <dt className="text-slate-500">Documento de Identidad:</dt>
                <dd className="font-semibold text-slate-200 mt-0.5">
                  {atleta.identidad_opcional || "No especificado"}
                </dd>
              </div>
              <div>
                <dt className="text-slate-500">Institución / Universidad:</dt>
                <dd className="font-semibold text-slate-200 mt-0.5">
                  {atleta.universidad || "No asignada"}
                </dd>
              </div>
              {atleta.carrera && (
                <div>
                  <dt className="text-slate-500">Carrera Profesional:</dt>
                  <dd className="font-semibold text-slate-200 mt-0.5">{atleta.carrera}</dd>
                </div>
              )}
              <div>
                <dt className="text-slate-500">Clubs Afiliados:</dt>
                <dd className="font-semibold text-slate-200 mt-0.5">
                  {atleta.clubs.length > 0 ? atleta.clubs.join(", ") : "Sin club"}
                </dd>
              </div>
              <div>
                <dt className="text-slate-500">Última Actualización ELO:</dt>
                <dd className="font-semibold text-slate-200 mt-0.5">
                  {atleta.rating_actual.fecha_actualizacion || "Reciente"}
                </dd>
              </div>
            </dl>
          </div>
        </div>

        {/* Right Column: Historical Tournaments Table */}
        <div className="lg:col-span-2 space-y-4">
          <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/40 space-y-4">
            <h2 className="font-bold text-base text-white flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-emerald-400" /> Historial de Torneos y Evolución
            </h2>

            {atleta.historial.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider text-[10px]">
                      <th className="py-2.5 px-3">Año</th>
                      <th className="py-2.5 px-3">Torneo / Evento</th>
                      <th className="py-2.5 px-3">Clásicas</th>
                      <th className="py-2.5 px-3">Rápidas</th>
                      <th className="py-2.5 px-3">Observaciones</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {atleta.historial.map((snap) => (
                      <tr key={snap.id} className="hover:bg-slate-800/30 transition-colors">
                        <td className="py-3 px-3 font-semibold text-white">{snap.anio}</td>
                        <td className="py-3 px-3 text-slate-300 font-medium">
                          {snap.torneo || "Torneo Oficial"}
                        </td>
                        <td className="py-3 px-3 font-bold text-emerald-400">
                          {snap.rating.clasicas || "—"}
                        </td>
                        <td className="py-3 px-3 font-bold text-blue-400">
                          {snap.rating.rapidas || "—"}
                        </td>
                        <td className="py-3 px-3 text-slate-400 italic">
                          {snap.observaciones || "Completado"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-10 text-slate-500 text-xs">
                No hay registros históricos previos para este atleta.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
