"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Trophy,
  Users,
  LayoutDashboard,
  BrainCircuit,
  Search,
  Bell,
  SlidersHorizontal,
  ChevronDown,
} from "lucide-react";

export function Navbar() {
  const pathname = usePathname();

  const navLinks = [
    { href: "/", label: "Command Center", icon: LayoutDashboard },
    { href: "/atletas", label: "Expediente Atletas", icon: Users },
    { href: "/partidas", label: "Suite de Análisis PGN", icon: Trophy },
  ];

  return (
    <header className="border-b border-slate-800/90 bg-[#070b12]/95 backdrop-blur-xl sticky top-0 z-50">
      {/* Top micro ticker bar */}
      <div className="bg-[#05080e] border-b border-slate-800/50 px-4 sm:px-8 py-1 flex items-center justify-between text-[11px] text-slate-400">
        <div className="flex items-center gap-4 overflow-x-auto scrollbar-none">
          <div className="flex items-center gap-1.5 font-mono">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-slate-300 font-semibold">MOTOR CAISSA:</span>
            <span className="text-emerald-400">EN LÍNEA (Stockfish + SQLite)</span>
          </div>
          <span className="text-slate-700 hidden sm:inline">|</span>
          <div className="hidden sm:flex items-center gap-1.5">
            <span className="text-slate-400">ELO PROMEDIO CLUB:</span>
            <span className="text-white font-mono font-bold">2,085</span>
            <span className="text-emerald-400 font-mono text-[10px]">(+42 pts)</span>
          </div>
          <span className="text-slate-700 hidden md:inline">|</span>
          <div className="hidden md:flex items-center gap-1.5">
            <span className="text-slate-400">TEMPORADA:</span>
            <span className="text-slate-200 font-medium">Ciclo Federativo 2026-I</span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <span className="px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-400 border border-emerald-800/40 text-[10px] font-mono">
            VERCEL READY
          </span>
          <span className="text-slate-500 font-mono text-[10px]">v1.4.0-pro</span>
        </div>
      </div>

      {/* Main navigation row */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        {/* Brand logo & identity */}
        <Link href="/" className="flex items-center gap-3 group flex-shrink-0">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-400 via-teal-500 to-emerald-700 flex items-center justify-center font-black text-slate-950 shadow-lg shadow-emerald-500/20 group-hover:scale-105 transition-all">
            <span className="text-2xl leading-none select-none">♞</span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-300 bg-clip-text text-transparent">
                CAISSA
              </span>
              <span className="font-light text-lg tracking-wider text-emerald-400">
                ANALYTIC
              </span>
            </div>
            <p className="text-[10px] font-mono tracking-widest text-slate-400 uppercase">
              High Performance Chess Suite
            </p>
          </div>
        </Link>

        {/* Navigation tabs */}
        <nav className="hidden md:flex items-center gap-1.5 bg-slate-900/60 p-1 rounded-xl border border-slate-800/80">
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive =
              pathname === link.href || (link.href !== "/" && pathname.startsWith(link.href));
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
                  isActive
                    ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-sm shadow-emerald-500/10"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? "text-emerald-400" : "text-slate-400"}`} />
                <span>{link.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Right tools / Profile */}
        <div className="flex items-center gap-3">
          {/* Quick search shortcut trigger */}
          <button className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900/90 border border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700 text-xs transition-colors">
            <Search className="w-3.5 h-3.5 text-slate-400" />
            <span className="text-[11px]">Buscar partida, ECO o atleta...</span>
            <kbd className="px-1.5 py-0.5 rounded bg-slate-800 text-[10px] font-mono text-slate-400 border border-slate-700">
              ⌘K
            </kbd>
          </button>

          {/* User profile capsule */}
          <div className="flex items-center gap-2.5 pl-2 border-l border-slate-800">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-slate-800 to-slate-700 border border-slate-600 flex items-center justify-center text-xs font-bold text-white shadow-inner">
              EA
            </div>
            <div className="hidden lg:block text-left">
              <span className="block text-xs font-bold text-slate-200 leading-tight">
                Entrenador Principal
              </span>
              <span className="block text-[10px] text-emerald-400 font-mono">
                Rol: DT / Club Master
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile navigation bar */}
      <div className="md:hidden flex items-center justify-around border-t border-slate-800/80 px-2 py-2 bg-[#06090f]">
        {navLinks.map((link) => {
          const Icon = link.icon;
          const isActive =
            pathname === link.href || (link.href !== "/" && pathname.startsWith(link.href));
          return (
            <Link
              key={link.href}
              href={link.href}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold ${
                isActive
                  ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                  : "text-slate-400"
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{link.label}</span>
            </Link>
          );
        })}
      </div>
    </header>
  );
}
