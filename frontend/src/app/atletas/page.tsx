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
    <div className="min-h-screen bg-slate-950 text-slate-100 py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-medium mb-2">
            <Users className="w-3.5 h-3.5" /> Expediente Deportivo Integral
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white">
            Catálogo de Atletas
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Gestión de perfiles, categorías federativas y seguimiento de rating FIDE y plataformas digitales.
          </p>
        </div>

        {/* Global KPI Summary */}
        <div className="flex items-center gap-3">
          <div className="px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-center">
            <span className="text-[11px] text-slate-400 block font-medium">Atletas Registrados</span>
            <span className="text-lg font-bold text-white">{ATLETAS_MOCK.length}</span>
          </div>
          <div className="px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-center">
            <span className="text-[11px] text-slate-400 block font-medium">ELO Promedio</span>
            <span className="text-lg font-bold text-emerald-400">{promedioElo}</span>
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 bg-slate-900/60 p-4 rounded-2xl border border-slate-800">
        <div className="relative sm:col-span-2">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
          <input
            type="text"
            placeholder="Buscar por nombre, club, universidad..."
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-colors"
          />
        </div>

        <div className="flex items-center gap-2">
          <select
            value={filtroSexo}
            onChange={(e) => setFiltroSexo(e.target.value)}
            className="w-1/2 bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
          >
            <option value="TODOS">Todos los géneros</option>
            <option value="M">Masculino</option>
            <option value="F">Femenino</option>
          </select>

          <select
            value={orden}
            onChange={(e) => setOrden(e.target.value)}
            className="w-1/2 bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
          >
            <option value="RATING_DESC">Mayor Rating</option>
            <option value="RATING_ASC">Menor Rating</option>
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
              className="group p-6 rounded-2xl border border-slate-800 bg-slate-900/40 hover:bg-slate-900 hover:border-slate-700 transition-all duration-200 flex flex-col justify-between"
            >
              <div className="space-y-4">
                {/* Header card */}
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 flex items-center justify-center font-bold text-slate-200 text-lg group-hover:border-emerald-500/50 transition-colors">
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
                        <span>{edad} años ({atleta.sexo === "M" ? "Masculino" : "Femenino"})</span>
                        <span>•</span>
                        <span className="flex items-center gap-1 text-emerald-400 font-medium">
                          <UserCheck className="w-3 h-3" /> Activo
                        </span>
                      </div>
                    </div>
                  </div>

                  <ChevronRight className="w-5 h-5 text-slate-500 group-hover:text-emerald-400 group-hover:translate-x-1 transition-all" />
                </div>

                {/* Rating Badges */}
                <div className="grid grid-cols-3 gap-2 pt-2">
                  <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-center">
                    <span className="text-[10px] uppercase tracking-wider text-slate-400 block font-semibold">
                      Clásicas
                    </span>
                    <span className="text-sm font-bold text-emerald-400">
                      {atleta.rating_actual.clasicas || "—"}
                    </span>
                  </div>
                  <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-center">
                    <span className="text-[10px] uppercase tracking-wider text-slate-400 block font-semibold">
                      Rápidas
                    </span>
                    <span className="text-sm font-bold text-blue-400">
                      {atleta.rating_actual.rapidas || "—"}
                    </span>
                  </div>
                  <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-center">
                    <span className="text-[10px] uppercase tracking-wider text-slate-400 block font-semibold">
                      Blitz
                    </span>
                    <span className="text-sm font-bold text-amber-400">
                      {atleta.rating_actual.blitz || "—"}
                    </span>
                  </div>
                </div>

                {/* Academic & Club Info */}
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
                <span className="text-emerald-400 group-hover:underline">Ver ficha técnica →</span>
              </div>
            </Link>
          );
        })}
      </div>

      {atletasFiltrados.length === 0 && (
        <div className="text-center py-16 border border-slate-800 rounded-2xl bg-slate-900/30">
          <Users className="w-10 h-10 text-slate-600 mx-auto mb-3" />
          <h3 className="text-base font-semibold text-white">No se encontraron atletas</h3>
          <p className="text-sm text-slate-400 mt-1">Intenta con otros términos de búsqueda o filtros.</p>
        </div>
      )}
    </div>
  );
}

