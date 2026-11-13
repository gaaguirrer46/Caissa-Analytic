import { Partida } from "@/types/partida.types";

export const PARTIDAS_MOCK: Partida[] = [
  {
    id: 1,
    id_atleta: 2,
    evento: "Campeonato Nacional Universitario 2026",
    fecha: "2026-10-24",
    ronda: "Ronda 5 • Mesa 1",
    blancas: "Carlos Daniel Morales",
    negras: "Rival Federado Universitario",
    rating_blancas: 2045,
    rating_negras: 1980,
    resultado: "1-0",
    color_atleta: "BLANCAS",
    eco: "B90",
    apertura: "Defensa Siciliana: Variante Najdorf (Ataque Inglés)",
    pgn: "1. e4 c5 2. Nf3 d6 3. d4 cxd4 4. Nxd4 Nf6 5. Nc3 a6 6. Be3 e5 7. Nb3 Be6 8. Qd2 Nbd7 9. f3 b5 10. O-O-O Be7 11. g4 O-O 12. g5 b4 13. Ne2 Ne8 14. h4 a5 15. Kb1 a4 16. Nbc1 Nb6 17. Ng3 d5 18. Bxb6 Qxb6 19. exd5 Rd8 20. Bc4 Nc7 21. Qe2 Nxd5 22. Qxe5 Bd6 23. Qe1 Ne3 24. Bxe6 Nxd1 25. Bc4 Bxg3 26. Qxg3 Ne3 27. Bd3 b3 28. cxb3 axb3 29. a3 Qc5 30. Be4 Rd2 31. Re1 Nc4 32. Nd3 Qd4 1-0",
    precision_atleta: 94.6,
    errores_graves: 0,
    fuente: "PGN",
  },
  {
    id: 2,
    id_atleta: 3,
    evento: "Nacional Femenino Sub-20 2026",
    fecha: "2026-10-18",
    ronda: "Final Oro",
    blancas: "Sofía Valentina Castro",
    negras: "Oponente Departamental",
    rating_blancas: 1920,
    rating_negras: 1840,
    resultado: "1-0",
    color_atleta: "BLANCAS",
    eco: "C50",
    apertura: "Apertura Italiana: Giuoco Piano",
    pgn: "1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. O-O Nf6 5. d3 d6 6. c3 a6 7. Bb3 Ba7 8. Nbd2 O-O 9. h3 h6 10. Re1 Re8 11. Nf1 Be6 12. Bc2 d5 13. Qe2 Qd7 14. Ng3 Rad8 15. Nh4 dxe4 16. dxe4 Ne7 17. Qf3 Nh7 18. Nhf5 Ng6 19. Nh5 Bxf5 20. exf5 Nh4 21. Qg4 g5 22. Qxh4 gxh4 23. Bxh6 Qd6 24. Bg7 Qd2 1-0",
    precision_atleta: 91.2,
    errores_graves: 0,
    fuente: "PGN",
  },
  {
    id: 3,
    id_atleta: 4,
    evento: "Gran Torneo Magistral 2026",
    fecha: "2026-10-12",
    ronda: "Ronda 7",
    blancas: "Alejandro José Rivas",
    negras: "Maestro FIDE Internacional",
    rating_blancas: 2180,
    rating_negras: 2250,
    resultado: "1/2-1/2",
    color_atleta: "BLANCAS",
    eco: "E60",
    apertura: "Defensa India de Rey: Variante Clásica",
    pgn: "1. d4 Nf6 2. c4 g6 3. Nc3 Bg7 4. e4 d6 5. Nf3 O-O 6. Be2 e5 7. O-O Nc6 8. d5 Ne7 9. Ne1 Nd7 10. Be3 f5 11. f3 f4 12. Bf2 g5 13. Nd3 Ng6 14. c5 Nf6 15. Rc1 Rf7 16. Kh1 h5 17. cxd6 cxd6 18. Nb5 a6 19. Na3 g4 20. Nc4 g3 21. Bg1 gxh2 22. Bf2 h4 23. Nb6 Rb8 24. Nxc8 Rxc8 25. Rxc8 Qxc8 26. Kxh2 Nh5 1/2-1/2",
    precision_atleta: 88.4,
    errores_graves: 1,
    fuente: "PGN",
  },
];

export async function getPartidas(idAtleta?: number, eco?: string): Promise<Partida[]> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
  try {
    const params = new URLSearchParams();
    if (idAtleta) params.append("id_atleta", String(idAtleta));
    if (eco) params.append("eco", eco);

    const qs = params.toString() ? `?${params.toString()}` : "";
    const res = await fetch(`${apiUrl}/partidas${qs}`, { cache: "no-store" });
    if (res.ok) {
      const data = await res.json();
      return data.map((d: any) => ({
        id: d.id,
        id_atleta: d.id_atleta,
        evento: d.evento,
        fecha: d.fecha,
        blancas: d.blancas,
        negras: d.negras,
        rating_blancas: d.rating_blancas,
        rating_negras: d.rating_negras,
        resultado: d.resultado,
        color_atleta: d.color_atleta,
        eco: d.apertura_eco,
        apertura: d.apertura || `Apertura ECO ${d.apertura_eco}`,
        pgn: d.pgn,
        precision_atleta: d.accuracy,
        errores_graves: d.blunders,
        fuente: "PGN",
      }));
    }
  } catch {
    // Fallback
  }
  return PARTIDAS_MOCK;
}

export async function importarPartidaPgn(idAtleta: number, pgnRaw: string): Promise<Partida | null> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
  try {
    const res = await fetch(`${apiUrl}/partidas/importar-pgn`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id_atleta: idAtleta, pgn_raw: pgnRaw }),
    });
    if (res.ok) {
      const d = await res.json();
      return {
        id: d.id,
        id_atleta: d.id_atleta,
        evento: d.evento,
        fecha: d.fecha,
        blancas: d.blancas,
        negras: d.negras,
        rating_blancas: d.rating_blancas,
        rating_negras: d.rating_negras,
        resultado: d.resultado,
        color_atleta: d.color_atleta,
        eco: d.apertura_eco,
        apertura: d.apertura || `Apertura ECO ${d.apertura_eco}`,
        pgn: d.pgn,
        precision_atleta: d.accuracy,
        errores_graves: d.blunders,
        fuente: "PGN",
      };
    }
  } catch {
    // Fallback
  }
  return null;
}

