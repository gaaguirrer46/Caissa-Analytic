"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Users,
  Search,
  Trophy,
  GraduationCap,
  Award,
  ChevronRight,
  TrendingUp,
  UserCheck,
  Shield,
  Filter,
  Sparkles,
  ArrowUpRight,
  Flame,
} from "lucide-react";
import { ATLETAS_MOCK } from "@/services/atletas.service";
import { calcularEdad } from "@/types/atleta.types";

export default function AtletasPage() {
  const [busqueda, setBusqueda] = useState("");
  const [filtroSexo, setFiltroSexo] = useState<string>("TODOS");
  const [orden, setOrden] = useState<string>("RATING_DESC");

  const atletasFiltrados = ATLETAS_MOCK.filter((atleta) => {
    const coincideTexto =
      atleta.nombre.toLowerCase().includes(busqueda.toLowerCase()) ||
      (atleta.universidad && atleta.universidad.toLowerCase().includes(busqueda.toLowerCase())) ||
      atleta.clubs.some((c) => c.toLowerCase().includes(busqueda.toLowerCase()));

    const coincideSexo = filtroSexo === "TODOS" || atleta.sexo === filtroSexo;

    return coincideTexto && coincideSexo;
  }).sort((a, b) => {
    const ratingA = a.rating_actual.clasicas || 0;
    const ratingB = b.rating_actual.clasicas || 0;
    if (orden === "RATING_DESC") return ratingB - ratingA;
    if (orden === "RATING_ASC") return ratingA - ratingB;
    if (orden === "NOMBRE") return a.nombre.localeCompare(b.nombre);
    return 0;
  });

  const promedioElo = Math.round(
    ATLETAS_MOCK.reduce((acc, a) => acc + (a.rating_actual.clasicas || 0), 0) / ATLETAS_MOCK.length
  );

  return (
    <div className="min-h-screen bg-[#070b12] text-slate-100 py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-8 font-sans">
      {/* Header Banner */}
      <div className="p-6 rounded-2xl border border-slate-800/90 bg-gradient-to-r from-[#0d1424] via-[#0a101d] to-[#070b12] flex flex-col sm:flex-row sm:items-center justify-between gap-6 shadow-xl">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-400 text-xs font-mono font-medium">
            <Users className="w-3.5 h-3.5" /> EXPEDIENTE DEPORTIVO FEDERATIVO
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white">
            Catálogo & Expediente de Atletas
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 max-w-2xl">
            Seguimiento de perfiles competitivos, categorías de edad/nivel, ratings oficiales FIDE (Clásicas, Rápidas, Blitz) y vinculaciones universitarias.
          </p>
        </div>

        {/* Global Stats */}
        <div className="flex items-center gap-3">
          <div className="px-4 py-2.5 rounded-xl bg-slate-900/90 border border-slate-800 text-center">
            <span className="text-[10px] text-slate-400 font-mono uppercase block">Plantel Oficial</span>
            <span className="text-xl font-bold font-mono text-white">{ATLETAS_MOCK.length} Atletas</span>
          </div>
          <div className="px-4 py-2.5 rounded-xl bg-slate-900/90 border border-slate-800 text-center">
            <span className="text-[10px] text-slate-400 font-mono uppercase block">ELO Promedio</span>
            <span className="text-xl font-bold font-mono text-emerald-400">{promedioElo}</span>
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 bg-[#0d1424]/80 p-4 rounded-2xl border border-slate-800/80">
        <div className="relative sm:col-span-2">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-3.5" />
          <input
            type="text"
            placeholder="Buscar por nombre de atleta, club, carrera o universidad..."
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
            className="w-full bg-[#070b12] border border-slate-800 rounded-xl pl-10 pr-4 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-colors"
          />
        </div>

        <div className="flex items-center gap-2">
          <select
            value={filtroSexo}
            onChange={(e) => setFiltroSexo(e.target.value)}
            className="w-1/2 bg-[#070b12] border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
          >
            <option value="TODOS">Todos los géneros</option>
            <option value="M">Masculino</option>
            <option value="F">Femenino</option>
          </select>

          <select
            value={orden}
            onChange={(e) => setOrden(e.target.value)}
            className="w-1/2 bg-[#070b12] border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
          >
            <option value="RATING_DESC">Mayor Rating ELO</option>
            <option value="RATING_ASC">Menor Rating ELO</option>
            <option value="NOMBRE">Nombre (A-Z)</option>
          </select>
        </div>
      </div>

      {/* Athletes Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {atletasFiltrados.map((atleta) => {
          const edad = calcularEdad(atleta.fecha_nacimiento);
          return (
            <Link
              key={atleta.id}
              href={`/atletas/${atleta.id}`}
              className="group p-6 rounded-2xl border border-slate-800/80 bg-[#0d1424]/70 hover:bg-[#0f1729] hover:border-slate-700 transition-all duration-200 flex flex-col justify-between shadow-lg"
            >
              <div className="space-y-4">
                {/* Header card */}
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3.5">
                    <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 flex items-center justify-center font-bold text-slate-100 text-base group-hover:border-emerald-500/50 transition-colors">
                      {atleta.nombre
                        .split(" ")
                        .map((n) => n[0])
                        .slice(0, 2)
                        .join("")}
                    </div>
                    <div>
                      <h3 className="font-bold text-base text-white group-hover:text-emerald-400 transition-colors">
                        {atleta.nombre}
                      </h3>
                      <div className="flex items-center gap-2 text-xs text-slate-400 mt-0.5">
                        <span>{edad} años ({atleta.sexo === "M" ? "Masc" : "Fem"})</span>
                        <span>•</span>
                        <span className="flex items-center gap-1 text-emerald-400 font-medium">
                          <UserCheck className="w-3 h-3" /> Federado
                        </span>
                      </div>
                    </div>
                  </div>

                  <ArrowUpRight className="w-5 h-5 text-slate-500 group-hover:text-emerald-400 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-all" />
                </div>

                {/* Rating Badges (TradingView Style) */}
                <div className="grid grid-cols-3 gap-2 pt-1 font-mono">
                  <div className="p-2.5 rounded-xl bg-[#070b12] border border-slate-800 text-center">
                    <span className="text-[10px] uppercase tracking-wider text-slate-400 block font-semibold">
                      FIDE Clásico
                    </span>
                    <span className="text-base font-bold text-emerald-400">
                      {atleta.rating_actual.clasicas || "—"}
                    </span>
                  </div>
                  <div className="p-2.5 rounded-xl bg-[#070b12] border border-slate-800 text-center">
                    <span className="text-[10px] uppercase tracking-wider text-slate-400 block font-semibold">
                      Rápidas
                    </span>
                    <span className="text-base font-bold text-blue-400">
                      {atleta.rating_actual.rapidas || "—"}
                    </span>
                  </div>
                  <div className="p-2.5 rounded-xl bg-[#070b12] border border-slate-800 text-center">
                    <span className="text-[10px] uppercase tracking-wider text-slate-400 block font-semibold">
                      Blitz
                    </span>
                    <span className="text-base font-bold text-amber-400">
                      {atleta.rating_actual.blitz || "—"}
                    </span>
                  </div>
                </div>

                {/* University and Clubs */}
                <div className="space-y-1.5 text-xs text-slate-400 pt-1">
                  {atleta.universidad && (
                    <div className="flex items-center gap-2">
                      <GraduationCap className="w-3.5 h-3.5 text-slate-500 flex-shrink-0" />
                      <span className="truncate">{atleta.universidad} {atleta.carrera && `• ${atleta.carrera}`}</span>
                    </div>
                  )}
                  {atleta.clubs.length > 0 && (
                    <div className="flex items-center gap-2">
                      <Shield className="w-3.5 h-3.5 text-slate-500 flex-shrink-0" />
                      <span className="truncate">{atleta.clubs.join(", ")}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Card Footer */}
              <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-500">
                <span>Historial: {atleta.historial.length} torneos registrados</span>
                <span className="text-emerald-400 font-semibold group-hover:underline">
                  Abrir expediente completo →
                </span>
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
