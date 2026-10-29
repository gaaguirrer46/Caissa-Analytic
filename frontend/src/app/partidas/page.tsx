"use client";

import { useState, useEffect, useTransition } from "react";
import dynamic from "next/dynamic";
import { Chess } from "chess.js";
import {
  Trophy,
  RotateCcw,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  Upload,
  Play,
  CheckCircle2,
  AlertCircle,
  FileText,
} from "lucide-react";

// Dynamic import for react-chessboard to prevent SSR mismatch on window/canvas
const Chessboard = dynamic(
  () => import("react-chessboard").then((mod) => mod.Chessboard),
  { ssr: false }
);

interface PartidaMuestra {
  id: number;
  evento: string;
  blancas: string;
  negras: string;
  resultado: string;
  eco: string;
  apertura: string;
  pgn: string;
}

const PARTIDAS_MUESTRA: PartidaMuestra[] = [
  {
    id: 1,
    evento: "Campeonato Nacional Universitario 2026",
    blancas: "Carlos Daniel Morales (2045)",
    negras: "Rival Federado (1980)",
    resultado: "1-0",
    eco: "B90",
    apertura: "Defensa Siciliana: Variante Najdorf",
    pgn: "1. e4 c5 2. Nf3 d6 3. d4 cxd4 4. Nxd4 Nf6 5. Nc3 a6 6. Be3 e5 7. Nb3 Be6 8. Qd2 Nbd7 9. f3 b5 10. O-O-O Be7 11. g4 O-O 12. g5 b4 13. Ne2 Ne8 14. h4 a5 15. Kb1 a4 16. Nbc1 Nb6 17. Ng3 d5 18. Bxb6 Qxb6 19. exd5 Rd8 20. Bc4 Nc7 21. Qe2 Nxd5 22. Qxe5 Bd6 23. Qe1 Ne3 24. Bxe6 Nxd1 25. Bc4 Bxg3 26. Qxg3 Ne3 27. Bd3 b3 28. cxb3 axb3 29. a3 Qc5 30. Be4 Rd2 31. Re1 Nc4 32. Nd3 Qd4 1-0",
  },
  {
    id: 2,
    evento: "Nacional Femenino Sub-20 2026",
    blancas: "Sofía Valentina Castro (1920)",
    negras: "Oponente Departamental (1840)",
    resultado: "1-0",
    eco: "C50",
    apertura: "Apertura Italiana: Giuoco Piano",
    pgn: "1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. O-O Nf6 5. d3 d6 6. c3 a6 7. Bb3 Ba7 8. Nbd2 O-O 9. h3 h6 10. Re1 Re8 11. Nf1 Be6 12. Bc2 d5 13. Qe2 Qd7 14. Ng3 Rad8 15. Nh4 dxe4 16. dxe4 Ne7 17. Qf3 Nh7 18. Nhf5 Ng6 19. Nh5 Bxf5 20. exf5 Nh4 21. Qg4 g5 22. Qxh4 gxh4 23. Bxh6 Qd6 24. Bg7 Qd2 1-0",
  },
  {
    id: 3,
    evento: "Gran Torneo Magistral 2026",
    blancas: "Alejandro José Rivas (2180)",
    negras: "Maestro FIDE (2250)",
    resultado: "1/2-1/2",
    eco: "E60",
    apertura: "Defensa India de Rey: Sistema Clásico",
    pgn: "1. d4 Nf6 2. c4 g6 3. Nc3 Bg7 4. e4 d6 5. Nf3 O-O 6. Be2 e5 7. O-O Nc6 8. d5 Ne7 9. Ne1 Nd7 10. Be3 f5 11. f3 f4 12. Bf2 g5 13. Nd3 Ng6 14. c5 Nf6 15. Rc1 Rf7 16. Kh1 h5 17. cxd6 cxd6 18. Nb5 a6 19. Na3 g4 20. Nc4 g3 21. Bg1 gxh2 22. Bf2 h4 23. Nb6 Rb8 24. Nxc8 Rxc8 25. Rxc8 Qxc8 26. Kxh2 Nh5 1/2-1/2",
  },
];

export default function PartidasPage() {
  const [partidaSeleccionada, setPartidaSeleccionada] = useState<PartidaMuestra>(PARTIDAS_MUESTRA[0]);
  const [game, setGame] = useState(() => new Chess());
  const [history, setHistory] = useState<string[]>([]);
  const [currentMoveIndex, setCurrentMoveIndex] = useState(-1);
  const [boardOrientation, setBoardOrientation] = useState<"white" | "black">("white");
  const [pgnInput, setPgnInput] = useState("");
  const [pgnError, setPgnError] = useState("");
  const [, startTransition] = useTransition();

  // Load selected game PGN
  useEffect(() => {
    cargarPgn(partidaSeleccionada.pgn);
  }, [partidaSeleccionada]);

  function cargarPgn(pgnString: string) {
    try {
      const newGame = new Chess();
      newGame.loadPgn(pgnString);
      const moves = newGame.history();

      // Reset to beginning
      const starterGame = new Chess();
      setGame(starterGame);
      setHistory(moves);
      setCurrentMoveIndex(-1);
      setPgnError("");
    } catch {
      setPgnError("Formato PGN inválido. Revisa las jugadas.");
    }
  }

  function irAJugada(index: number) {
    const newGame = new Chess();
    for (let i = 0; i <= index && i < history.length; i++) {
      newGame.move(history[i]);
    }
    setGame(newGame);
    setCurrentMoveIndex(index);
  }

  function siguienteJugada() {
    if (currentMoveIndex < history.length - 1) {
      irAJugada(currentMoveIndex + 1);
    }
  }

  function jugadaAnterior() {
    if (currentMoveIndex > -1) {
      irAJugada(currentMoveIndex - 1);
    }
  }

  function irAlInicio() {
    irAJugada(-1);
  }

  function irAlFinal() {
    irAJugada(history.length - 1);
  }

  function rotarTablero() {
    setBoardOrientation((prev) => (prev === "white" ? "black" : "white"));
  }

  // Handle manual piece drop on board
  function onDrop({
    sourceSquare,
    targetSquare,
  }: {
    piece: unknown;
    sourceSquare: string;
    targetSquare: string | null;
  }): boolean {
    if (!targetSquare) return false;
    try {
      const copy = new Chess(game.fen());
      const move = copy.move({
        from: sourceSquare,
        to: targetSquare,
        promotion: "q",
      });

      if (move === null) return false;

      setGame(copy);
      setHistory((prev) => [...prev.slice(0, currentMoveIndex + 1), move.san]);
      setCurrentMoveIndex((prev) => prev + 1);
      return true;
    } catch {
      return false;
    }
  }

  function handleCustomPgnSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!pgnInput.trim()) return;
    cargarPgn(pgnInput);
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium mb-2">
            <Trophy className="w-3.5 h-3.5" /> Visor Interactivo PGN
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white">
            Partidas & Análisis de Tablero
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Reproducción paso a paso de partidas, evaluación de variantes y análisis por fases de juego.
          </p>
        </div>

        {/* Game Info Chip */}
        <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs">
          <span className="text-slate-400">ECO:</span>
          <span className="font-bold text-emerald-400">{partidaSeleccionada.eco}</span>
          <span className="text-slate-600">|</span>
          <span className="text-slate-300 font-medium">{partidaSeleccionada.resultado}</span>
        </div>
      </div>

      {/* Main Layout: Board + Controls + Move List */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Interactive Chessboard */}
        <div className="lg:col-span-7 flex flex-col items-center space-y-4">
          <div className="w-full max-w-[500px] aspect-square rounded-2xl overflow-hidden border-2 border-slate-800 bg-slate-900 shadow-2xl relative">
            <Chessboard
              options={{
                position: game.fen(),
                boardOrientation: boardOrientation,
                onPieceDrop: onDrop,
                darkSquareStyle: { backgroundColor: "#1e293b" },
                lightSquareStyle: { backgroundColor: "#cbd5e1" },
                animationDurationInMs: 200,
              }}
            />
          </div>

          {/* Navigation Controls Bar */}
          <div className="flex items-center justify-center gap-2 p-2 rounded-2xl bg-slate-900/80 border border-slate-800 w-full max-w-[500px]">
            <button
              onClick={irAlInicio}
              disabled={currentMoveIndex === -1}
              title="Ir al inicio"
              className="p-2.5 rounded-xl text-slate-300 hover:text-white hover:bg-slate-800 disabled:opacity-30 disabled:hover:bg-transparent transition-colors"
            >
              <ChevronsLeft className="w-5 h-5" />
            </button>
            <button
              onClick={jugadaAnterior}
              disabled={currentMoveIndex === -1}
              title="Jugada anterior"
              className="p-2.5 rounded-xl text-slate-300 hover:text-white hover:bg-slate-800 disabled:opacity-30 disabled:hover:bg-transparent transition-colors"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <button
              onClick={rotarTablero}
              title="Rotar tablero"
              className="p-2.5 rounded-xl text-emerald-400 hover:bg-slate-800 transition-colors flex items-center gap-1.5 text-xs font-semibold px-3"
            >
              <RotateCcw className="w-4 h-4" /> Rotar ({boardOrientation === "white" ? "B" : "N"})
            </button>
            <button
              onClick={siguienteJugada}
              disabled={currentMoveIndex >= history.length - 1}
              title="Siguiente jugada"
              className="p-2.5 rounded-xl text-slate-300 hover:text-white hover:bg-slate-800 disabled:opacity-30 disabled:hover:bg-transparent transition-colors"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
            <button
              onClick={irAlFinal}
              disabled={currentMoveIndex >= history.length - 1}
              title="Ir al final"
              className="p-2.5 rounded-xl text-slate-300 hover:text-white hover:bg-slate-800 disabled:opacity-30 disabled:hover:bg-transparent transition-colors"
            >
              <ChevronsRight className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Right Column: Move List & Metadata */}
        <div className="lg:col-span-5 space-y-6">
          {/* Active Game Card */}
          <div className="p-5 rounded-2xl border border-slate-800 bg-slate-900/60 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-emerald-400">
                {partidaSeleccionada.apertura}
              </span>
              <span className="text-xs px-2 py-0.5 rounded-md bg-slate-800 text-slate-300 font-bold">
                {partidaSeleccionada.resultado}
              </span>
            </div>

            <div className="space-y-1 text-xs">
              <div className="flex items-center justify-between">
                <span className="text-slate-400 flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-slate-200 inline-block" /> Blancas:
                </span>
                <span className="font-semibold text-slate-200">{partidaSeleccionada.blancas}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-400 flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-slate-800 border border-slate-600 inline-block" /> Negras:
                </span>
                <span className="font-semibold text-slate-200">{partidaSeleccionada.negras}</span>
              </div>
            </div>

            <p className="text-[11px] text-slate-500 pt-1 border-t border-slate-800/80">
              {partidaSeleccionada.evento}
            </p>
          </div>

          {/* Algebraic Move List */}
          <div className="p-5 rounded-2xl border border-slate-800 bg-slate-900/40 space-y-3">
            <div className="flex items-center justify-between text-xs font-bold text-slate-300 border-b border-slate-800 pb-2">
              <span>Registro de Jugadas</span>
              <span className="text-slate-500">
                {history.length} jugadas ({Math.ceil(history.length / 2)} tiempos)
              </span>
            </div>

            <div className="max-h-60 overflow-y-auto pr-2 grid grid-cols-2 gap-x-2 gap-y-1 text-xs font-mono">
              {history.map((movimiento, idx) => {
                const moveNumber = Math.floor(idx / 2) + 1;
                const isWhite = idx % 2 === 0;
                const isCurrent = idx === currentMoveIndex;

                return (
                  <button
                    key={idx}
                    onClick={() => irAJugada(idx)}
                    className={`text-left px-2 py-1 rounded transition-colors flex items-center gap-1.5 ${
                      isCurrent
                        ? "bg-emerald-500/20 text-emerald-300 font-bold border border-emerald-500/30"
                        : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
                    }`}
                  >
                    {isWhite && <span className="text-slate-600 font-sans text-[10px] w-6">{moveNumber}.</span>}
                    {!isWhite && <span className="w-6" />}
                    <span>{movimiento}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Sample Games Switcher */}
          <div className="p-5 rounded-2xl border border-slate-800 bg-slate-900/40 space-y-3">
            <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
              Seleccionar Partida de Ejemplo
            </h3>
            <div className="space-y-2">
              {PARTIDAS_MUESTRA.map((p) => (
                <button
                  key={p.id}
                  onClick={() => setPartidaSeleccionada(p)}
                  className={`w-full text-left p-3 rounded-xl border text-xs transition-all ${
                    p.id === partidaSeleccionada.id
                      ? "bg-emerald-500/10 border-emerald-500/40 text-emerald-300 font-medium"
                      : "bg-slate-950 border-slate-800/80 text-slate-400 hover:text-slate-200 hover:border-slate-700"
                  }`}
                >
                  <div className="font-semibold text-white">{p.apertura}</div>
                  <div className="text-[11px] text-slate-400 mt-0.5 truncate">
                    {p.blancas} vs {p.negras} ({p.resultado})
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Custom PGN Importer */}
          <form onSubmit={handleCustomPgnSubmit} className="p-5 rounded-2xl border border-slate-800 bg-slate-900/40 space-y-3">
            <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <Upload className="w-3.5 h-3.5 text-emerald-400" /> Cargar tu propio PGN
            </h3>
            <textarea
              rows={3}
              placeholder="Pega aquí el código PGN de una partida (ej: 1. e4 e5 2. Nf3...)"
              value={pgnInput}
              onChange={(e) => setPgnInput(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-emerald-500 font-mono"
            />
            {pgnError && (
              <p className="text-xs text-rose-400 flex items-center gap-1.5">
                <AlertCircle className="w-3.5 h-3.5" /> {pgnError}
              </p>
            )}
            <button
              type="submit"
              className="w-full py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-white transition-colors"
            >
              Cargar y Analizar Partida
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
