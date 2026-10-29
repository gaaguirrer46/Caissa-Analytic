import {
  Trophy,
  Users,
  Target,
  BarChart3,
  BookOpen,
  ShieldCheck,
  Zap,
  Activity,
  ArrowRight,
  Database,
  Sliders,
  CheckCircle2,
} from "lucide-react";

export default function HomePage() {
  const modulos = [
    {
      titulo: "Gestión de Atletas",
      descripcion: "Fichas técnicas, categorías, clubes, historial federativo y seguimiento de rating ELO.",
      icono: Users,
      color: "from-blue-500/20 to-blue-600/5 text-blue-400 border-blue-500/30",
      href: "/atletas",
      badge: "Dominio Activo",
    },
    {
      titulo: "Partidas & Visor PGN",
      descripcion: "Carga de partidas, visualizador interactivo de tablero, análisis de fases y detección de jugadas.",
      icono: Trophy,
      color: "from-emerald-500/20 to-emerald-600/5 text-emerald-400 border-emerald-500/30",
      href: "/partidas",
      badge: "PGN Parser",
    },
    {
      titulo: "Repertorio de Aperturas",
      descripcion: "Árbol de variantes, códigos ECO y estadísticas de rendimiento con piezas blancas y negras.",
      icono: BookOpen,
      color: "from-purple-500/20 to-purple-600/5 text-purple-400 border-purple-500/30",
      href: "/aperturas",
      badge: "Estadísticas",
    },
    {
      titulo: "Objetivos SMART",
      descripcion: "Cálculo automático de avance por horas de entrenamiento, rating, medallas y torneos.",
      icono: Target,
      color: "from-amber-500/20 to-amber-600/5 text-amber-400 border-amber-500/30",
      href: "/objetivos",
      badge: "RF-03.5 / RF-03.6",
    },
    {
      titulo: "Indicadores & Rendimiento",
      descripcion: "Evolución histórica de ELO, precisión posicional, táctica y radar de fortalezas.",
      icono: BarChart3,
      color: "from-cyan-500/20 to-cyan-600/5 text-cyan-400 border-cyan-500/30",
      href: "/indicadores",
      badge: "Analítica",
    },
    {
      titulo: "Auditoría & Trazabilidad",
      descripcion: "Registro inmutable de acciones, control de acceso, roles y configuración de rangos.",
      icono: ShieldCheck,
      color: "from-rose-500/20 to-rose-600/5 text-rose-400 border-rose-500/30",
      href: "/auditoria",
      badge: "Control Interno",
    },
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* Top Navigation Bar */}
      <header className="border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center font-black text-slate-950 shadow-lg shadow-emerald-500/20">
              ♞
            </div>
            <div>
              <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
                Caissa Analytic
              </span>
              <span className="ml-2 text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                v1.0 Ready
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3 text-sm">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300">
              <Database className="w-4 h-4 text-emerald-400" />
              <span className="text-xs">Backend: SQLite / Hexagonal</span>
            </div>
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-xs font-medium">Vercel Ready</span>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-12">
        <div className="relative overflow-hidden rounded-3xl border border-slate-800 bg-gradient-to-b from-slate-900/80 to-slate-950 p-8 sm:p-12 shadow-2xl">
          <div className="absolute top-0 right-0 -mt-12 -mr-12 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
          <div className="max-w-3xl space-y-4">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium">
              <Zap className="w-3.5 h-3.5" /> Frontend Next.js Inicializado con Éxito
            </div>
            <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white">
              Plataforma Analítica de <br />
              <span className="bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 bg-clip-text text-transparent">
                Rendimiento Ajedrecístico
              </span>
            </h1>
            <p className="text-slate-400 text-base sm:text-lg leading-relaxed">
              Monitoreo integral de atletas, evaluación táctica de partidas, gestión de aperturas y cumplimiento de objetivos de entrenamiento en conexión directa con la arquitectura limpia del backend.
            </p>

            <div className="pt-2 flex flex-wrap gap-4 items-center">
              <div className="flex items-center gap-2 text-xs text-slate-400">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Next.js 16 + React 19
              </div>
              <div className="flex items-center gap-2 text-xs text-slate-400">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Tailwind CSS v4
              </div>
              <div className="flex items-center gap-2 text-xs text-slate-400">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" /> TypeScript Estricto
              </div>
              <div className="flex items-center gap-2 text-xs text-slate-400">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Compatible con Vercel
              </div>
            </div>
          </div>
        </div>

        {/* Quick Stats Overview */}
        <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-5 rounded-2xl border border-slate-800 bg-slate-900/50 space-y-1">
            <span className="text-xs text-slate-400 flex items-center gap-1.5">
              <Users className="w-3.5 h-3.5 text-blue-400" /> Módulos Dominio
            </span>
            <p className="text-2xl font-bold text-white">12</p>
            <p className="text-[11px] text-emerald-400">Implementados en Python</p>
          </div>
          <div className="p-5 rounded-2xl border border-slate-800 bg-slate-900/50 space-y-1">
            <span className="text-xs text-slate-400 flex items-center gap-1.5">
              <Trophy className="w-3.5 h-3.5 text-emerald-400" /> Partidas & PGN
            </span>
            <p className="text-2xl font-bold text-white">SQLite</p>
            <p className="text-[11px] text-slate-400">caissa.db persistente</p>
          </div>
          <div className="p-5 rounded-2xl border border-slate-800 bg-slate-900/50 space-y-1">
            <span className="text-xs text-slate-400 flex items-center gap-1.5">
              <Target className="w-3.5 h-3.5 text-amber-400" /> Objetivos SMART
            </span>
            <p className="text-2xl font-bold text-white">RF-03.5/6</p>
            <p className="text-[11px] text-amber-400">Cálculo automatizado</p>
          </div>
          <div className="p-5 rounded-2xl border border-slate-800 bg-slate-900/50 space-y-1">
            <span className="text-xs text-slate-400 flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5 text-cyan-400" /> Estado Frontend
            </span>
            <p className="text-2xl font-bold text-emerald-400">Compilado</p>
            <p className="text-[11px] text-slate-400">0 errores de build</p>
          </div>
        </section>

        {/* Modules Grid */}
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-white">Módulos del Sistema</h2>
              <p className="text-sm text-slate-400">Acceso a las áreas analíticas del entrenamiento</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {modulos.map((modulo) => {
              const Icon = modulo.icono;
              return (
                <div
                  key={modulo.titulo}
                  className="group relative rounded-2xl border border-slate-800/80 bg-slate-900/40 p-6 hover:border-slate-700 hover:bg-slate-900/80 transition-all duration-200 flex flex-col justify-between"
                >
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className={`w-12 h-12 rounded-xl bg-gradient-to-b border flex items-center justify-center ${modulo.color}`}>
                        <Icon className="w-6 h-6" />
                      </div>
                      <span className="text-[11px] font-medium px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                        {modulo.badge}
                      </span>
                    </div>

                    <div>
                      <h3 className="font-semibold text-lg text-white group-hover:text-emerald-400 transition-colors">
                        {modulo.titulo}
                      </h3>
                      <p className="text-sm text-slate-400 mt-1 leading-relaxed">
                        {modulo.descripcion}
                      </p>
                    </div>
                  </div>

                  <div className="pt-6 mt-4 border-t border-slate-800/60 flex items-center justify-between text-xs font-medium text-slate-400 group-hover:text-emerald-400">
                    <span>Ver especificación</span>
                    <ArrowRight className="w-4 h-4 transform group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 py-6 text-center text-xs text-slate-500">
        <p>Caissa Analytic &copy; 2026 — Plataforma de Rendimiento Ajedrecístico (Monorepo Backend Python + Frontend Next.js)</p>
      </footer>
    </div>
  );
}
