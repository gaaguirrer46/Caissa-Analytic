import Link from "next/link";
import {
  Trophy,
  Users,
  Target,
  BarChart3,
  TrendingUp,
  Activity,
  ArrowRight,
  ShieldCheck,
  Zap,
  Clock,
  Sparkles,
  Flame,
  Award,
  ChevronRight,
  Play,
  Crosshair,
} from "lucide-react";

export default function HomePage() {
  const kpis = [
    {
      titulo: "ELO Promedio del Club",
      valor: "2,085",
      cambio: "+42 pts",
      positivo: true,
      subtexto: "Último ciclo competitivo",
      color: "emerald",
    },
    {
      titulo: "Tasa de Victorias Global",
      valor: "68.4%",
      cambio: "+5.2%",
      positivo: true,
      subtexto: "31V - 8T - 6D en torneos",
      color: "blue",
    },
    {
      titulo: "Precisión de Fases (ACPL)",
      valor: "89.2%",
      cambio: "+2.8%",
      positivo: true,
      subtexto: "Apertura 93% • Finales 86%",
      color: "cyan",
    },
    {
      titulo: "Cumplimiento SMART (RF-03.5)",
      valor: "82.5%",
      cambio: "4 Metas",
      positivo: true,
      subtexto: "Horas, ELO y torneos al día",
      color: "amber",
    },
  ];

  const ultimasPartidas = [
    {
      id: 1,
      atleta: "Carlos Daniel Morales",
      rival: "Rival Federado (1980)",
      evento: "Campeonato Nacional Universitario",
      eco: "B90",
      apertura: "Siciliana Najdorf (6.Be3)",
      resultado: "1-0",
      precision: "94.6%",
      blunders: 0,
      fecha: "Hace 2 días",
    },
    {
      id: 2,
      atleta: "Sofía Valentina Castro",
      rival: "Oponente Departamental (1840)",
      evento: "Nacional Femenino Sub-20",
      eco: "C50",
      apertura: "Italiana: Giuoco Piano",
      resultado: "1-0",
      precision: "91.2%",
      blunders: 0,
      fecha: "Hace 4 días",
    },
    {
      id: 3,
      atleta: "Alejandro José Rivas",
      rival: "Maestro FIDE (2250)",
      evento: "Gran Torneo Magistral",
      eco: "E60",
      apertura: "India de Rey (Clásica)",
      resultado: "1/2-1/2",
      precision: "88.4%",
      blunders: 1,
      fecha: "Hace 1 semana",
    },
  ];

  const objetivosSmart = [
    {
      atleta: "Carlos Morales",
      meta: "Superar barrera de 2,100 ELO FIDE",
      progreso: 81,
      actual: "2,045 pts",
      objetivo: "2,100 pts",
      tiempo: "2 semanas restantes",
      estado: "En camino",
    },
    {
      atleta: "Sofía Castro",
      meta: "40 Horas de Entrenamiento Táctico",
      progreso: 85,
      actual: "34 hrs",
      objetivo: "40 hrs",
      tiempo: "Fin de mes",
      estado: "Excelente",
    },
    {
      atleta: "Alejandro Rivas",
      meta: "Consolidar 1ra Norma de Maestro",
      progreso: 100,
      actual: "Completada",
      objetivo: "1 Norma",
      tiempo: "Alcanzado",
      estado: "Completado",
    },
  ];

  return (
    <div className="min-h-screen bg-[#070b12] text-slate-100 flex flex-col font-sans">
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Top Command Banner */}
        <div className="relative overflow-hidden rounded-2xl border border-slate-800/90 bg-gradient-to-r from-[#0d1527] via-[#0b1220] to-[#080d17] p-6 sm:p-8 shadow-2xl">
          <div className="absolute top-0 right-0 -mt-16 -mr-16 w-80 h-80 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 relative z-10">
            <div className="space-y-3 max-w-2xl">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono font-medium">
                <Sparkles className="w-3.5 h-3.5" /> CENTRO DE CONTROL ANALÍTICO EN TIEMPO REAL
              </div>
              <h1 className="text-2xl sm:text-4xl font-extrabold tracking-tight text-white leading-tight">
                Telemetría de Rendimiento &{" "}
                <span className="bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 bg-clip-text text-transparent">
                  Ajedrez de Competición
                </span>
              </h1>
              <p className="text-slate-400 text-sm leading-relaxed">
                Supervisión centralizada de expedientes de atletas, precisión de jugadas por fases con Stockfish, detección de errores graves y seguimiento automatizado de objetivos SMART.
              </p>
            </div>

            <div className="flex flex-wrap sm:flex-nowrap gap-3 items-center">
              <Link
                href="/partidas"
                className="flex items-center gap-2 px-5 py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-bold text-xs shadow-lg shadow-emerald-500/20 transition-all hover:scale-[1.02]"
              >
                <Trophy className="w-4 h-4" /> Abrir Visor PGN
              </Link>
              <Link
                href="/atletas"
                className="flex items-center gap-2 px-5 py-3 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-800 hover:border-slate-700 font-semibold text-xs transition-colors"
              >
                <Users className="w-4 h-4 text-emerald-400" /> Ver Atletas (4)
              </Link>
            </div>
          </div>
        </div>

        {/* 4 High-Density KPI Cards */}
        <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {kpis.map((kpi) => (
            <div
              key={kpi.titulo}
              className="p-5 rounded-2xl border border-slate-800/80 bg-[#0d1424]/70 backdrop-blur-sm hover:border-slate-700 transition-all space-y-2 relative overflow-hidden"
            >
              <div className="flex items-center justify-between text-xs text-slate-400 font-medium">
                <span>{kpi.titulo}</span>
                <span className="text-emerald-400 font-mono text-[11px] font-bold bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                  {kpi.cambio}
                </span>
              </div>
              <div className="flex items-baseline gap-2 pt-1">
                <span className="text-3xl font-extrabold text-white tracking-tight font-mono">
                  {kpi.valor}
                </span>
              </div>
              <p className="text-[11px] text-slate-500 pt-1 border-t border-slate-800/60 truncate">
                {kpi.subtexto}
              </p>
            </div>
          ))}
        </section>

        {/* Master Two-Column Grid: Telemetry & Radar */}
        <section className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Column (8 cols): ELO Curve + Live Games Feed */}
          <div className="lg:col-span-8 space-y-8">
            {/* Interactive ELO Evolution Chart Card */}
            <div className="p-6 rounded-2xl border border-slate-800/90 bg-[#0d1424]/60 space-y-5">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800/80 pb-4">
                <div>
                  <div className="flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-emerald-400" />
                    <h2 className="text-base font-bold text-white tracking-tight">
                      Evolución de Rendimiento ELO del Equipo
                    </h2>
                  </div>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Histórico de rating ponderado en torneos oficiales (FIDE Clásico)
                  </p>
                </div>

                <div className="flex items-center gap-1 bg-slate-900 p-1 rounded-lg border border-slate-800 text-[11px] font-mono text-slate-400">
                  <button className="px-2.5 py-1 rounded bg-emerald-500/20 text-emerald-300 font-bold border border-emerald-500/30">
                    6M
                  </button>
                  <button className="px-2.5 py-1 rounded hover:text-white transition-colors">
                    1A
                  </button>
                  <button className="px-2.5 py-1 rounded hover:text-white transition-colors">
                    TODO
                  </button>
                </div>
              </div>

              {/* High-Fidelity SVG Area Curve */}
              <div className="w-full h-56 relative pt-4">
                <svg className="w-full h-full overflow-visible" viewBox="0 0 700 200" preserveAspectRatio="none">
                  <defs>
                    <linearGradient id="eloGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#10b981" stopOpacity="0.35" />
                      <stop offset="100%" stopColor="#10b981" stopOpacity="0.0" />
                    </linearGradient>
                  </defs>

                  {/* Horizontal grid lines */}
                  <line x1="0" y1="30" x2="700" y2="30" stroke="#1e293b" strokeDasharray="3 3" />
                  <line x1="0" y1="80" x2="700" y2="80" stroke="#1e293b" strokeDasharray="3 3" />
                  <line x1="0" y1="130" x2="700" y2="130" stroke="#1e293b" strokeDasharray="3 3" />
                  <line x1="0" y1="180" x2="700" y2="180" stroke="#1e293b" />

                  {/* Filled area curve */}
                  <path
                    d="M 0 160 Q 120 150 200 120 T 400 90 T 550 50 T 700 30 L 700 180 L 0 180 Z"
                    fill="url(#eloGradient)"
                  />

                  {/* Stroke path */}
                  <path
                    d="M 0 160 Q 120 150 200 120 T 400 90 T 550 50 T 700 30"
                    fill="none"
                    stroke="#10b981"
                    strokeWidth="3"
                  />

                  {/* Data Points */}
                  <circle cx="200" cy="120" r="5" fill="#10b981" stroke="#070b12" strokeWidth="2" />
                  <circle cx="400" cy="90" r="5" fill="#10b981" stroke="#070b12" strokeWidth="2" />
                  <circle cx="550" cy="50" r="5" fill="#10b981" stroke="#070b12" strokeWidth="2" />
                  <circle cx="700" cy="30" r="6" fill="#34d399" stroke="#070b12" strokeWidth="2" />
                </svg>

                {/* X Axis month markers */}
                <div className="flex justify-between text-[11px] font-mono text-slate-400 pt-2 border-t border-slate-800">
                  <span>Mayo 2025 (1,920)</span>
                  <span>Ago 2025</span>
                  <span>Nov 2025 (1,990)</span>
                  <span>Feb 2026</span>
                  <span>Jun 2026 (2,045)</span>
                  <span className="text-emerald-400 font-bold">Oct 2026 (2,085)</span>
                </div>
              </div>
            </div>

            {/* Live Tournament Games Feed */}
            <div className="p-6 rounded-2xl border border-slate-800/90 bg-[#0d1424]/60 space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
                <div className="flex items-center gap-2">
                  <Trophy className="w-4 h-4 text-emerald-400" />
                  <h2 className="text-base font-bold text-white tracking-tight">
                    Partidas de Torneo Recientes
                  </h2>
                </div>
                <Link
                  href="/partidas"
                  className="text-xs text-emerald-400 hover:text-emerald-300 font-semibold flex items-center gap-1 transition-colors"
                >
                  Abrir suite completa →
                </Link>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400 text-[10px] uppercase font-mono tracking-wider">
                      <th className="py-2.5 px-3">Atleta</th>
                      <th className="py-2.5 px-3">Apertura & ECO</th>
                      <th className="py-2.5 px-3">Precisión</th>
                      <th className="py-2.5 px-3">Blunders</th>
                      <th className="py-2.5 px-3">Resultado</th>
                      <th className="py-2.5 px-3 text-right">Acción</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 font-sans">
                    {ultimasPartidas.map((p) => (
                      <tr key={p.id} className="hover:bg-slate-800/30 transition-colors">
                        <td className="py-3 px-3">
                          <span className="font-bold text-white block">{p.atleta}</span>
                          <span className="text-[11px] text-slate-500 truncate block max-w-[140px]">
                            vs {p.rival}
                          </span>
                        </td>
                        <td className="py-3 px-3">
                          <span className="px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 font-mono text-[10px] font-bold mr-1.5">
                            {p.eco}
                          </span>
                          <span className="text-slate-300">{p.apertura}</span>
                        </td>
                        <td className="py-3 px-3 font-mono font-bold text-emerald-400">
                          {p.precision}
                        </td>
                        <td className="py-3 px-3">
                          {p.blunders === 0 ? (
                            <span className="text-slate-400 text-[11px] font-mono">0 errores</span>
                          ) : (
                            <span className="px-1.5 py-0.5 rounded bg-rose-500/15 text-rose-400 border border-rose-500/30 text-[10px] font-bold">
                              {p.blunders} blunder
                            </span>
                          )}
                        </td>
                        <td className="py-3 px-3">
                          <span
                            className={`px-2 py-0.5 rounded text-xs font-mono font-bold ${
                              p.resultado === "1-0"
                                ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                                : "bg-slate-800 text-slate-300"
                            }`}
                          >
                            {p.resultado}
                          </span>
                        </td>
                        <td className="py-3 px-3 text-right">
                          <Link
                            href="/partidas"
                            className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-slate-900 hover:bg-emerald-500 hover:text-slate-950 text-slate-300 font-semibold text-[11px] border border-slate-700 hover:border-emerald-400 transition-colors"
                          >
                            <Play className="w-3 h-3" /> Analizar
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* Right Column (4 cols): Tactical Radar & SMART Goals */}
          <div className="lg:col-span-4 space-y-8">
            {/* Tactical Radar Widget */}
            <div className="p-6 rounded-2xl border border-slate-800/90 bg-[#0d1424]/60 space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
                <div className="flex items-center gap-2">
                  <Crosshair className="w-4 h-4 text-emerald-400" />
                  <h2 className="text-base font-bold text-white tracking-tight">
                    Radar de Habilidades
                  </h2>
                </div>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  EQUIPO A
                </span>
              </div>

              {/* Geometric SVG Radar Chart */}
              <div className="relative flex items-center justify-center py-4">
                <svg className="w-56 h-56" viewBox="0 0 200 200">
                  {/* Concentric rings */}
                  <polygon points="100,20 180,65 180,155 100,190 20,155 20,65" fill="none" stroke="#1e293b" strokeWidth="1" />
                  <polygon points="100,50 150,80 150,135 100,160 50,135 50,80" fill="none" stroke="#1e293b" strokeWidth="1" />

                  {/* Dynamic skill polygon */}
                  <polygon
                    points="100,32 165,72 145,130 100,152 45,90 35,70"
                    fill="#10b981"
                    fillOpacity="0.25"
                    stroke="#10b981"
                    strokeWidth="2"
                  />

                  {/* Axis points */}
                  <circle cx="100" cy="32" r="3.5" fill="#34d399" />
                  <circle cx="165" cy="72" r="3.5" fill="#34d399" />
                  <circle cx="145" cy="130" r="3.5" fill="#34d399" />
                  <circle cx="100" cy="152" r="3.5" fill="#34d399" />
                  <circle cx="45" cy="90" r="3.5" fill="#34d399" />
                  <circle cx="35" cy="70" r="3.5" fill="#34d399" />
                </svg>
              </div>

              {/* Radar metric breakdown */}
              <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                <div className="p-2 rounded bg-slate-900/80 border border-slate-800">
                  <span className="text-slate-400 text-[10px] block">Táctica & Cálculo</span>
                  <span className="font-bold text-emerald-400">92% • Excelente</span>
                </div>
                <div className="p-2 rounded bg-slate-900/80 border border-slate-800">
                  <span className="text-slate-400 text-[10px] block">Aperturas (Teoría)</span>
                  <span className="font-bold text-blue-400">86% • Sólido</span>
                </div>
                <div className="p-2 rounded bg-slate-900/80 border border-slate-800">
                  <span className="text-slate-400 text-[10px] block">Manejo de Reloj</span>
                  <span className="font-bold text-amber-400">79% • Mejorar</span>
                </div>
                <div className="p-2 rounded bg-slate-900/80 border border-slate-800">
                  <span className="text-slate-400 text-[10px] block">Técnica Finales</span>
                  <span className="font-bold text-cyan-400">88% • Preciso</span>
                </div>
              </div>
            </div>

            {/* Automated SMART Goals Tracker (RF-03.5 / RF-03.6) */}
            <div className="p-6 rounded-2xl border border-slate-800/90 bg-[#0d1424]/60 space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
                <div className="flex items-center gap-2">
                  <Target className="w-4 h-4 text-amber-400" />
                  <h2 className="text-base font-bold text-white tracking-tight">
                    Objetivos SMART (RF-03.5/6)
                  </h2>
                </div>
                <span className="text-[10px] font-mono text-amber-400 font-semibold">
                  3 ACTIVOS
                </span>
              </div>

              <div className="space-y-4">
                {objetivosSmart.map((obj) => (
                  <div key={obj.meta} className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
                    <div className="flex items-start justify-between">
                      <div>
                        <span className="text-[11px] font-bold text-emerald-400 block font-mono">
                          {obj.atleta}
                        </span>
                        <h3 className="text-xs font-semibold text-slate-200 mt-0.5">
                          {obj.meta}
                        </h3>
                      </div>
                      <span className="text-xs font-mono font-bold text-white">
                        {obj.progreso}%
                      </span>
                    </div>

                    {/* Progress Bar */}
                    <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${
                          obj.progreso === 100
                            ? "bg-emerald-400"
                            : obj.progreso > 80
                            ? "bg-gradient-to-r from-emerald-500 to-teal-400"
                            : "bg-amber-400"
                        }`}
                        style={{ width: `${obj.progreso}%` }}
                      />
                    </div>

                    <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono pt-1">
                      <span>Actual: {obj.actual}</span>
                      <span>Meta: {obj.objetivo}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 py-6 text-center text-xs text-slate-400 bg-[#05080e]">
        <p>Caissa Analytic &copy; 2026 — Plataforma Profesional de Alto Rendimiento para Ajedrez Competitivo</p>
      </footer>
    </div>
  );
}
