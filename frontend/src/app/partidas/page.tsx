"use client";

import { useState, useEffect, useRef } from "react";
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
  Pause,
  Copy,
  BrainCircuit,
  Clock,
  Plus,
  CheckCircle2,
  AlertCircle,
} from "lucide-react";
import { getPartidas, importarPartidaPgn, PARTIDAS_MOCK } from "@/services/partidas.service";
import { Partida } from "@/types/partida.types";
import { ATLETAS_MOCK } from "@/services/atletas.service";

// Dynamic import for react-chessboard
const Chessboard = dynamic(
  () => import("react-chessboard").then((mod) => mod.Chessboard),
  { ssr: false }
);

export default function PartidasPage() {
  const [partidas, setPartidas] = useState<Partida[]>(PARTIDAS_MOCK);
  const [partidaSeleccionada, setPartidaSeleccionada] = useState<Partida>(PARTIDAS_MOCK[0]);
  const [game, setGame] = useState(() => new Chess());
  const [history, setHistory] = useState<string[]>([]);
  const [currentMoveIndex, setCurrentMoveIndex] = useState(-1);
  const [boardOrientation, setBoardOrientation] = useState<"white" | "black">("white");
  const [reproduciendo, setReproduciendo] = useState(false);
  const [modalImportar, setModalImportar] = useState(false);
  const [atletaImportarId, setAtletaImportarId] = useState<number>(2);
  const [pgnInput, setPgnInput] = useState("");
  const [pgnError, setPgnError] = useState("");
  const [notificacion, setNotificacion] = useState("");
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // Cargar partidas desde la API REST
  useEffect(() => {
    async function cargar() {
      const datos = await getPartidas();
      if (datos && datos.length > 0) {
        setPartidas(datos);
        setPartidaSeleccionada(datos[0]);
      }
    }
    cargar();
  }, []);

  // Cargar PGN cuando cambia la partida seleccionada
  useEffect(() => {
    if (partidaSeleccionada && partidaSeleccionada.pgn) {
      cargarPgn(partidaSeleccionada.pgn);
    }
  }, [partidaSeleccionada]);

  // Autoplay handler
  useEffect(() => {
    if (reproduciendo) {
      intervalRef.current = setInterval(() => {
        setCurrentMoveIndex((prev) => {
          if (prev < history.length - 1) {
            irAJugada(prev + 1);
            return prev + 1;
          } else {
            setReproduciendo(false);
            return prev;
          }
        });
      }, 1000);
    } else {
      if (intervalRef.current) clearInterval(intervalRef.current);
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [reproduciendo, history]);

  function cargarPgn(pgnString: string) {
    try {
      const newGame = new Chess();
      newGame.loadPgn(pgnString);
      const moves = newGame.history();

      const starterGame = new Chess();
      setGame(starterGame);
      setHistory(moves);
      setCurrentMoveIndex(-1);
      setPgnError("");
      setReproduciendo(false);
    } catch {
      setPgnError("Formato PGN no estándar. Verifique las jugadas.");
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

  // Handle manual move on board
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

  async function handleImportarSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!pgnInput.trim()) return;

    setPgnError("");
    const guardada = await importarPartidaPgn(atletaImportarId, pgnInput);
    if (guardada) {
      setPartidas((prev) => [guardada, ...prev]);
      setPartidaSeleccionada(guardada);
      setModalImportar(false);
      setPgnInput("");
      setNotificacion("Partida importada y guardada con éxito en SQLite.");
      setTimeout(() => setNotificacion(""), 4000);
    } else {
      // Intento de carga local si la API estuviera offline
      cargarPgn(pgnInput);
      setModalImportar(false);
      setNotificacion("Partida cargada en el visor (Modo local).");
      setTimeout(() => setNotificacion(""), 4000);
    }
  }

  // Estimación de ventaja (-5 a +5)
  const evalEstimada = currentMoveIndex >= 0 ? Math.min(0.2 + currentMoveIndex * 0.15, 6.0) : 0.2;
  const alturaBlancoPct = Math.min(Math.max(50 + evalEstimada * 8, 5), 95);

  return (
    <div className="min-h-screen bg-[#070b12] text-slate-100 py-6 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-6 font-sans">
      {/* Notificación flotante de éxito */}
      {notificacion && (
        <div className="p-3 rounded-xl bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 text-xs font-mono flex items-center gap-2 shadow-lg animate-fade-in">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <span>{notificacion}</span>
        </div>
      )}

      {/* Top Match Command Header */}
      <div className="p-5 rounded-2xl border border-slate-800/90 bg-[#0d1424]/80 backdrop-blur-md flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-xl">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-700 flex items-center justify-center text-slate-950 font-black text-2xl shadow-lg shadow-emerald-500/20">
            ♞
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 rounded bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 font-mono text-xs font-bold">
                ECO {partidaSeleccionada.eco || "A00"}
              </span>
              <h1 className="font-extrabold text-lg text-white tracking-tight">
                {partidaSeleccionada.apertura || "Partida Magistral"}
              </h1>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              {partidaSeleccionada.evento} • {partidaSeleccionada.ronda || "Ronda Oficial"} • {partidaSeleccionada.fecha}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setModalImportar(true)}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-bold text-xs shadow-md transition-all hover:scale-[1.02]"
          >
            <Upload className="w-4 h-4" /> Importar PGN
          </button>
          <button
            onClick={() => navigator.clipboard.writeText(partidaSeleccionada.pgn)}
            title="Copiar PGN"
            className="p-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 hover:text-white transition-colors flex items-center gap-1.5 text-xs font-semibold"
          >
            <Copy className="w-4 h-4 text-emerald-400" /> Copiar PGN
          </button>
        </div>
      </div>

      {/* Main Suite Workspace: Board Column (Left) + Analysis & Moves (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Board + Eval Bar + Players + Controls (7 cols) */}
        <div className="lg:col-span-7 flex flex-col items-center space-y-4">
          {/* Black Player Card */}
          <div className="w-full max-w-[540px] flex items-center justify-between p-3 rounded-xl bg-[#0d1424]/90 border border-slate-800">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center font-bold text-xs text-slate-200">
                {partidaSeleccionada.negras.charAt(0)}
              </div>
              <div>
                <span className="font-bold text-sm text-white block">
                  {partidaSeleccionada.negras}
                </span>
                <span className="text-[11px] font-mono text-slate-400">
                  Rating: {partidaSeleccionada.rating_negras || 2000} FIDE
                </span>
              </div>
            </div>

            <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
              <Clock className="w-3.5 h-3.5 text-slate-400" />
              <span>15:42</span>
            </div>
          </div>

          {/* Chessboard with Vertical Evaluation Bar Container */}
          <div className="w-full max-w-[540px] flex gap-2 items-stretch">
            {/* Vertical Evaluation Bar */}
            <div className="w-7 rounded-xl overflow-hidden bg-slate-900 border border-slate-800 flex flex-col justify-end relative shadow-inner">
              <div
                className="w-full bg-slate-100 transition-all duration-300 relative flex items-center justify-center"
                style={{ height: `${alturaBlancoPct}%` }}
              >
                <span className="absolute bottom-1 font-mono font-black text-[9px] text-slate-900 select-none">
                  {evalEstimada > 0 ? `+${evalEstimada.toFixed(1)}` : evalEstimada.toFixed(1)}
                </span>
              </div>
            </div>

            {/* Chessboard Box */}
            <div className="flex-1 aspect-square rounded-2xl overflow-hidden border-2 border-slate-800 bg-[#0c121e] shadow-2xl relative">
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
          </div>

          {/* White Player Card */}
          <div className="w-full max-w-[540px] flex items-center justify-between p-3 rounded-xl bg-[#0d1424]/90 border border-slate-800">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center font-bold text-xs text-emerald-400">
                {partidaSeleccionada.blancas.charAt(0)}
              </div>
              <div>
                <span className="font-bold text-sm text-white block">
                  {partidaSeleccionada.blancas}
                </span>
                <span className="text-[11px] font-mono text-slate-400">
                  Rating: {partidaSeleccionada.rating_blancas || 2000} FIDE
                </span>
              </div>
            </div>

            <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
              <Clock className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-white font-bold">22:15</span>
            </div>
          </div>

          {/* Ergonomic Playback Controls Bar */}
          <div className="flex items-center justify-center gap-2 p-2.5 rounded-2xl bg-[#0d1424] border border-slate-800 w-full max-w-[540px] shadow-lg">
            <button
              onClick={irAlInicio}
              disabled={currentMoveIndex === -1}
              title="Ir al inicio"
              className="p-2 rounded-xl text-slate-300 hover:text-white hover:bg-slate-800 disabled:opacity-25 transition-colors"
            >
              <ChevronsLeft className="w-5 h-5" />
            </button>
            <button
              onClick={jugadaAnterior}
              disabled={currentMoveIndex === -1}
              title="Jugada anterior (←)"
              className="p-2 rounded-xl text-slate-300 hover:text-white hover:bg-slate-800 disabled:opacity-25 transition-colors"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>

            {/* Play/Pause Button */}
            <button
              onClick={() => setReproduciendo(!reproduciendo)}
              title={reproduciendo ? "Pausar" : "Reproducir automáticamente"}
              className="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs flex items-center gap-2 shadow-md transition-colors"
            >
              {reproduciendo ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4 fill-slate-950" />}
              <span>{reproduciendo ? "Pausar" : "Auto Play"}</span>
            </button>

            <button
              onClick={siguienteJugada}
              disabled={currentMoveIndex >= history.length - 1}
              title="Siguiente jugada (→)"
              className="p-2 rounded-xl text-slate-300 hover:text-white hover:bg-slate-800 disabled:opacity-25 transition-colors"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
            <button
              onClick={irAlFinal}
              disabled={currentMoveIndex >= history.length - 1}
              title="Ir al final"
              className="p-2 rounded-xl text-slate-300 hover:text-white hover:bg-slate-800 disabled:opacity-25 transition-colors"
            >
              <ChevronsRight className="w-5 h-5" />
            </button>

            <div className="w-[1px] h-6 bg-slate-800 mx-1" />

            <button
              onClick={rotarTablero}
              title="Girar tablero"
              className="px-3 py-1.5 rounded-xl text-slate-300 hover:bg-slate-800 text-xs font-mono font-semibold flex items-center gap-1.5 transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5 text-emerald-400" />
              <span>{boardOrientation === "white" ? "B" : "N"}</span>
            </button>
          </div>
        </div>

        {/* Right Column: Telemetry, Phase Breakdown & Move Sheet (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          {/* Phase Accuracy Breakdown */}
          <div className="p-5 rounded-2xl border border-slate-800/90 bg-[#0d1424]/80 space-y-3">
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
              <span className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
                <BrainCircuit className="w-4 h-4 text-emerald-400" /> Precisión Técnica Estimada
              </span>
              <span className="text-xs font-mono font-bold text-emerald-400">
                {partidaSeleccionada.precision_atleta || 92.4}%
              </span>
            </div>

            <div className="grid grid-cols-3 gap-3 pt-1">
              <div className="p-2.5 rounded-xl bg-slate-900/90 border border-slate-800 text-center">
                <span className="text-[10px] text-slate-400 uppercase font-mono block">Apertura</span>
                <span className="text-lg font-bold font-mono text-emerald-400">95%</span>
                <span className="text-[10px] text-slate-400 block">Libro ECO</span>
              </div>
              <div className="p-2.5 rounded-xl bg-slate-900/90 border border-slate-800 text-center">
                <span className="text-[10px] text-slate-400 uppercase font-mono block">Medio Juego</span>
                <span className="text-lg font-bold font-mono text-cyan-400">89%</span>
                <span className="text-[10px] text-slate-400 block">Táctica</span>
              </div>
              <div className="p-2.5 rounded-xl bg-slate-900/90 border border-slate-800 text-center">
                <span className="text-[10px] text-slate-400 uppercase font-mono block">Blunders</span>
                <span className="text-lg font-bold font-mono text-amber-400">
                  {partidaSeleccionada.errores_graves || 0}
                </span>
                <span className="text-[10px] text-slate-400 block">Errores Críticos</span>
              </div>
            </div>
          </div>

          {/* Algebraic Notation Sheet with Active Move Glow */}
          <div className="p-5 rounded-2xl border border-slate-800/90 bg-[#0d1424]/80 space-y-3">
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
              <span className="text-xs font-bold text-white uppercase tracking-wider">
                Planilla Oficial de Jugadas
              </span>
              <span className="text-xs font-mono text-slate-400">
                {history.length} jugadas ({Math.ceil(history.length / 2)} tiempos)
              </span>
            </div>

            <div className="max-h-56 overflow-y-auto pr-2 grid grid-cols-2 gap-x-2 gap-y-1 font-mono text-xs">
              {history.map((movimiento, idx) => {
                const moveNumber = Math.floor(idx / 2) + 1;
                const isWhite = idx % 2 === 0;
                const isCurrent = idx === currentMoveIndex;

                return (
                  <button
                    key={idx}
                    onClick={() => irAJugada(idx)}
                    className={`text-left px-2.5 py-1 rounded transition-colors flex items-center gap-2 ${
                      isCurrent
                        ? "bg-emerald-500/25 text-emerald-300 font-bold border border-emerald-500/40 shadow-sm"
                        : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
                    }`}
                  >
                    {isWhite && <span className="text-slate-600 text-[11px] w-6">{moveNumber}.</span>}
                    {!isWhite && <span className="w-6" />}
                    <span>{movimiento}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Saved Games Switcher */}
          <div className="p-5 rounded-2xl border border-slate-800/90 bg-[#0d1424]/80 space-y-3">
            <span className="text-xs font-bold text-slate-300 uppercase tracking-wider block">
              Partidas Guardadas en SQLite ({partidas.length})
            </span>
            <div className="space-y-2 max-h-52 overflow-y-auto pr-1">
              {partidas.map((p) => (
                <button
                  key={p.id}
                  onClick={() => setPartidaSeleccionada(p)}
                  className={`w-full text-left p-3 rounded-xl border text-xs transition-all ${
                    p.id === partidaSeleccionada.id
                      ? "bg-emerald-500/15 border-emerald-500/40 text-emerald-300"
                      : "bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700"
                  }`}
                >
                  <div className="font-bold text-white flex items-center justify-between">
                    <span className="truncate max-w-[240px]">{p.apertura}</span>
                    <span className="font-mono text-emerald-400">{p.resultado}</span>
                  </div>
                  <div className="text-[11px] text-slate-400 mt-0.5 truncate">
                    {p.blancas} vs {p.negras} • {p.evento}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Modal Importar PGN */}
      {modalImportar && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="w-full max-w-lg rounded-2xl border border-slate-800 bg-[#0d1424] p-6 shadow-2xl space-y-5">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <Upload className="w-5 h-5 text-emerald-400" /> Importar y Guardar Partida PGN
              </h2>
              <button
                onClick={() => setModalImportar(false)}
                className="text-slate-400 hover:text-white text-sm font-bold"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleImportarSubmit} className="space-y-4 text-xs font-mono">
              <div>
                <label className="block text-slate-400 mb-1">Vincular a Atleta Federado:</label>
                <select
                  value={atletaImportarId}
                  onChange={(e) => setAtletaImportarId(Number(e.target.value))}
                  className="w-full bg-[#070b12] border border-slate-800 rounded-xl p-2.5 text-slate-200 focus:outline-none focus:border-emerald-500"
                >
                  {ATLETAS_MOCK.map((a) => (
                    <option key={a.id} value={a.id}>
                      {a.nombre} (ELO {a.rating_actual.clasicas || "—"})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Texto o Archivo PGN (con etiquetas oficiales):</label>
                <textarea
                  rows={8}
                  placeholder={`[Event "Campeonato Nacional 2026"]\n[White "Carlos Morales"]\n[Black "Rival"]\n[Result "1-0"]\n[ECO "B90"]\n\n1. e4 c5 2. Nf3 d6 3. d4 cxd4 1-0`}
                  value={pgnInput}
                  onChange={(e) => setPgnInput(e.target.value)}
                  required
                  className="w-full bg-[#070b12] border border-slate-800 rounded-xl p-3 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-emerald-500 font-mono"
                />
              </div>

              {pgnError && (
                <div className="p-2.5 rounded-lg bg-rose-500/15 border border-rose-500/30 text-rose-400 text-xs flex items-center gap-1.5 font-sans">
                  <AlertCircle className="w-4 h-4 flex-shrink-0" />
                  <span>{pgnError}</span>
                </div>
              )}

              <div className="pt-3 border-t border-slate-800 flex items-center justify-end gap-3 font-sans">
                <button
                  type="button"
                  onClick={() => setModalImportar(false)}
                  className="px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 text-xs font-semibold"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-bold text-xs"
                >
                  Guardar en Base de Datos SQLite
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
