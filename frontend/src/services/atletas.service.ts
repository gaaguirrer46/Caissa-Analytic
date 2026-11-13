import { Atleta } from "@/types/atleta.types";

export const ATLETAS_MOCK: Atleta[] = [
  {
    id: 1,
    nombre: "Carlos Daniel Morales",
    fecha_nacimiento: "2003-05-14",
    sexo: "M",
    identidad_opcional: "001-140503-1002A",
    federacion: "Federación Nacional de Ajedrez",
    universidad: "Universidad Nacional de Ingeniería (UNI)",
    institucion: "Facultad de Ciencias de la Computación",
    carrera: "Ingeniería de Sistemas",
    categorias: [1, 3],
    clubs: ["Club Alfil de Oro", "Selección Universitaria"],
    entrenadores_asignados: [101],
    rating_actual: {
      clasicas: 2045,
      rapidas: 2110,
      blitz: 2185,
      chess_com: 2240,
      lichess: 2290,
      fecha_actualizacion: "2026-10-15",
    },
    historial: [
      {
        id: 1,
        id_atleta: 1,
        anio: 2025,
        torneo: "Torneo Nacional Universitario",
        rating: { clasicas: 1980, rapidas: 2050, blitz: 2120 },
        observaciones: "Campeón invicto 7/7 tableros.",
      },
      {
        id: 2,
        id_atleta: 1,
        anio: 2026,
        torneo: "Campeonato Abierto Centroamericano",
        rating: { clasicas: 2045, rapidas: 2110, blitz: 2185 },
        observaciones: "Subida de +65 puntos ELO FIDE.",
      },
    ],
    activo: true,
  },
  {
    id: 2,
    nombre: "Sofía Valentina Castro",
    fecha_nacimiento: "2005-09-22",
    sexo: "F",
    identidad_opcional: "001-220905-1044B",
    federacion: "Federación Nacional de Ajedrez",
    universidad: "Universidad Americana (UAM)",
    carrera: "Medicina",
    categorias: [1, 2],
    clubs: ["Club Lasker", "Selección Femenina"],
    entrenadores_asignados: [102],
    rating_actual: {
      clasicas: 1920,
      rapidas: 1985,
      blitz: 2050,
      chess_com: 2095,
      lichess: 2140,
      fecha_actualizacion: "2026-10-20",
    },
    historial: [
      {
        id: 3,
        id_atleta: 2,
        anio: 2026,
        torneo: "Nacional Femenino Sub-20",
        rating: { clasicas: 1920, rapidas: 1985, blitz: 2050 },
        observaciones: "Medalla de oro categoría Sub-20.",
      },
    ],
    activo: true,
  },
  {
    id: 3,
    nombre: "Alejandro José Rivas",
    fecha_nacimiento: "2001-11-03",
    sexo: "M",
    identidad_opcional: "001-031101-1008C",
    federacion: "Federación Nacional de Ajedrez",
    universidad: "UNAN-Managua",
    carrera: "Licenciatura en Educación Física",
    categorias: [2],
    clubs: ["Club Capablanca"],
    entrenadores_asignados: [101],
    rating_actual: {
      clasicas: 2180,
      rapidas: 2230,
      blitz: 2310,
      chess_com: 2380,
      lichess: 2420,
      fecha_actualizacion: "2026-10-25",
    },
    historial: [
      {
        id: 4,
        id_atleta: 3,
        anio: 2026,
        torneo: "Gran Torneo Magistral de Apertura",
        rating: { clasicas: 2180, rapidas: 2230, blitz: 2310 },
        observaciones: "Norma de Maestro Nacional lograda.",
      },
    ],
    activo: true,
  },
  {
    id: 4,
    nombre: "Mariana Elena Flores",
    fecha_nacimiento: "2006-03-18",
    sexo: "F",
    identidad_opcional: "001-180306-1033D",
    federacion: "Federación Nacional de Ajedrez",
    universidad: "Colegio Calasanz",
    categorias: [3],
    clubs: ["Academia Juvenil de Ajedrez"],
    entrenadores_asignados: [103],
    rating_actual: {
      clasicas: 1750,
      rapidas: 1810,
      blitz: 1880,
      chess_com: 1920,
      lichess: 1960,
      fecha_actualizacion: "2026-10-18",
    },
    historial: [],
    activo: true,
  },
];

export async function getAtletas(): Promise<Atleta[]> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL;
  if (apiUrl) {
    try {
      const res = await fetch(`${apiUrl}/atletas`, { next: { revalidate: 30 } });
      if (res.ok) {
        return await res.json();
      }
    } catch {
      // Si el backend aún no está levantado, usa el mock de dominio
    }
  }
  return ATLETAS_MOCK;
}

export async function getAtletaById(id: number): Promise<Atleta | null> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL;
  if (apiUrl) {
    try {
      const res = await fetch(`${apiUrl}/atletas/${id}`, { next: { revalidate: 30 } });
      if (res.ok) {
        return await res.json();
      }
    } catch {
      // Fallback
    }
  }
  return ATLETAS_MOCK.find((a) => a.id === id) || null;
}

