"""Adaptador SQLite de indicadores de rendimiento y proveedor de métricas.

``indicadores_rendimiento`` y ``alertas`` existen en el esquema oficial. Los
dashboards son vistas calculadas y no tienen tabla propia, por lo que su
persistencia es una operación nula que devuelve el objeto."""
from __future__ import annotations

import sqlite3
from datetime import date
from typing import List, Optional

from dominio.indicadores.entidades import (
    DashboardAtleta,
    DashboardEntrenador,
    IndicadorRendimiento,
    RangoEvaluacion,
    TipoIndicador,
)
from dominio.indicadores.puertos import (
    ProveedorDatosRendimiento,
    RepositorioIndicadores,
)

class RepositorioIndicadoresSqlite(RepositorioIndicadores):
    def __init__(self, conexion: sqlite3.Connection) -> None:
        self._conexion = conexion

    def guardar(self, indicador: IndicadorRendimiento) -> IndicadorRendimiento:
        cursor = self._conexion.cursor()
        cursor.execute(
            """
            INSERT INTO indicadores_rendimiento (
                id_atleta, tipo, valor, rango_evaluacion, periodo_inicio, periodo_fin
            ) VALUES (?, ?, ?, ?, ?, ?);
            """,
            (
                indicador.id_atleta,
                indicador.tipo.value,
                indicador.valor,
                indicador.rango_evaluacion.value,
                indicador.periodo_inicio.isoformat(),
                indicador.periodo_fin.isoformat(),
            ),
        )
        indicador.id = cursor.lastrowid
        self._conexion.commit()
        return indicador

    def listar_por_atleta(self, id_atleta: int) -> List[IndicadorRendimiento]:
        cursor = self._conexion.cursor()
        cursor.execute(
            "SELECT * FROM indicadores_rendimiento WHERE id_atleta = ? ORDER BY id;",
            (id_atleta,),
        )
        return [self._fila_a_indicador(f) for f in cursor.fetchall()]

    def listar_por_periodo(
        self, id_atleta: int, desde: date, hasta: date
    ) -> List[IndicadorRendimiento]:
        cursor = self._conexion.cursor()
        cursor.execute(
            """
            SELECT * FROM indicadores_rendimiento
            WHERE id_atleta = ? AND periodo_inicio >= ? AND periodo_fin <= ?
            ORDER BY id;
            """,
            (id_atleta, desde.isoformat(), hasta.isoformat()),
        )
        return [self._fila_a_indicador(f) for f in cursor.fetchall()]

    def guardar_dashboard_entrenador(
        self, dashboard: DashboardEntrenador
    ) -> DashboardEntrenador:
        return dashboard

    def guardar_dashboard_atleta(self, dashboard: DashboardAtleta) -> DashboardAtleta:
        return dashboard

    @staticmethod
    def _fila_a_indicador(fila: sqlite3.Row) -> IndicadorRendimiento:
        inicio = fila["periodo_inicio"]
        fin = fila["periodo_fin"]
        if isinstance(inicio, str):
            inicio = date.fromisoformat(inicio)
        if isinstance(fin, str):
            fin = date.fromisoformat(fin)
        return IndicadorRendimiento(
            id=fila["id"],
            id_atleta=fila["id_atleta"],
            tipo=TipoIndicador(fila["tipo"]),
            valor=float(fila["valor"]),
            rango_evaluacion=RangoEvaluacion(fila["rango_evaluacion"]),
            periodo_inicio=inicio,
            periodo_fin=fin,
        )

class ProveedorDatosRendimientoSqlite(ProveedorDatosRendimiento):
    """Agrega métricas de los módulos de atletas, entrenamientos, partidas y objetivos."""

    def __init__(self, conexion: sqlite3.Connection) -> None:
        self._conexion = conexion

    def horas_entrenadas_aprobadas(
        self, id_atleta: int, desde: date, hasta: date
    ) -> float:
        return self._suma_horas(id_atleta, desde, hasta, ejecutadas=True)

    def horas_planificadas(self, id_atleta: int, desde: date, hasta: date) -> float:
        return self._suma_horas(id_atleta, desde, hasta, ejecutadas=False)

    def _suma_horas(
        self, id_atleta: int, desde: date, hasta: date, *, ejecutadas: bool
    ) -> float:

        columna = "s.horas_ejecutadas" if ejecutadas else "s.horas_planificadas"
        filtro = "AND s.ejecucion_aprobada = 1" if ejecutadas else ""
        cursor = self._conexion.cursor()
        cursor.execute(
            f"""
            SELECT COALESCE(SUM({columna}), 0.0)
            FROM sesiones_entrenamiento s
            INNER JOIN planes_entrenamiento p ON s.id_plan = p.id
            WHERE p.id_atleta = ? AND p.anio BETWEEN ? AND ? {filtro};
            """,
            (id_atleta, desde.year, hasta.year),
        )
        return float(cursor.fetchone()[0] or 0.0)

    def _consulta_analisis(self, id_atleta: int, desde: date, hasta: date, expresion: str) -> float:
        cursor = self._conexion.cursor()
        cursor.execute(
            f"""
            SELECT {expresion}
            FROM analisis_tecnico_partidas a
            INNER JOIN partidas p ON a.id_partida = p.id
            WHERE p.id_atleta = ? AND p.fecha BETWEEN ? AND ?;
            """,
            (id_atleta, desde.isoformat(), hasta.isoformat()),
        )
        fila = cursor.fetchone()
        return float(fila[0]) if fila and fila[0] is not None else 0.0

    def accuracy_promedio(self, id_atleta: int, desde: date, hasta: date) -> float:
        return self._consulta_analisis(id_atleta, desde, hasta, "AVG(a.accuracy)")

    def acpl_promedio(self, id_atleta: int, desde: date, hasta: date) -> float:
        return self._consulta_analisis(id_atleta, desde, hasta, "AVG(a.acpl)")

    def blunders_totales(self, id_atleta: int, desde: date, hasta: date) -> int:
        return int(
            self._consulta_analisis(id_atleta, desde, hasta, "SUM(a.blunders)")
        )

    def resultados(self, id_atleta: int, desde: date, hasta: date) -> tuple[int, int, int]:
        cursor = self._conexion.cursor()
        cursor.execute(
            """
            SELECT
                SUM(CASE WHEN resultado = '1/2-1/2' THEN 1 ELSE 0 END),
                SUM(CASE
                    WHEN (color_atleta = 'BLANCAS' OR color_atleta IS NULL)
                         AND resultado = '1-0' THEN 1
                    WHEN color_atleta = 'NEGRAS' AND resultado = '0-1' THEN 1
                    ELSE 0 END),
                SUM(CASE
                    WHEN (color_atleta = 'BLANCAS' OR color_atleta IS NULL)
                         AND resultado = '0-1' THEN 1
                    WHEN color_atleta = 'NEGRAS' AND resultado = '1-0' THEN 1
                    ELSE 0 END)
            FROM partidas
            WHERE id_atleta = ? AND fecha BETWEEN ? AND ?;
            """,
            (id_atleta, desde.isoformat(), hasta.isoformat()),
        )
        fila = cursor.fetchone()
        return (int(fila[1] or 0), int(fila[0] or 0), int(fila[2] or 0))

    def partidas_analizadas(self, id_atleta: int, desde: date, hasta: date) -> int:
        return int(
            self._consulta_analisis(id_atleta, desde, hasta, "COUNT(*)")
        )

    def rendimiento_por_color(
        self, id_atleta: int, color: str, desde: date, hasta: date
    ) -> tuple[int, int, int]:
        """(victorias, tablas, derrotas) jugando con un color.

 Las partidas sin ``color_atleta`` se atribuyen a blancas, igual que
 en el método ``resultados``.
 """
        cursor = self._conexion.cursor()
        cursor.execute(
            """
            SELECT
                SUM(CASE WHEN resultado = '1/2-1/2' THEN 1 ELSE 0 END),
                SUM(CASE
                    WHEN (color_atleta = 'BLANCAS' OR color_atleta IS NULL)
                         AND resultado = '1-0' THEN 1
                    WHEN color_atleta = 'NEGRAS' AND resultado = '0-1' THEN 1
                    ELSE 0 END),
                SUM(CASE
                    WHEN (color_atleta = 'BLANCAS' OR color_atleta IS NULL)
                         AND resultado = '0-1' THEN 1
                    WHEN color_atleta = 'NEGRAS' AND resultado = '1-0' THEN 1
                    ELSE 0 END)
            FROM partidas
            WHERE id_atleta = ? AND fecha BETWEEN ? AND ?
              AND (color_atleta = ? OR (? = 'BLANCAS' AND color_atleta IS NULL));
            """,
            (id_atleta, desde.isoformat(), hasta.isoformat(), color, color),
        )
        fila = cursor.fetchone()
        return (int(fila[1] or 0), int(fila[0] or 0), int(fila[2] or 0))

    def rendimiento_por_apertura(
        self, id_atleta: int, desde: date, hasta: date
    ) -> List[tuple[str, str, float]]:
        """porcentaje de puntos por apertura (ECO) del periodo.

 El nombre sale del repertorio del atleta si existe; sin repertorio
 se expone el código ECO sin nombre (no se inventan denominaciones).
 """
        cursor = self._conexion.cursor()
        cursor.execute(
            """
            SELECT p.apertura_eco,
                   COALESCE(MAX(r.nombre), ''),
                   COUNT(*),
                   SUM(CASE
                       WHEN p.resultado = '1/2-1/2' THEN 1.0
                       WHEN (p.color_atleta = 'BLANCAS' OR p.color_atleta IS NULL)
                            AND p.resultado = '1-0' THEN 1.0
                       WHEN p.color_atleta = 'NEGRAS' AND p.resultado = '0-1' THEN 1.0
                       ELSE 0.0 END)
            FROM partidas p
            LEFT JOIN aperturas_repertorio r
                ON r.id_atleta = p.id_atleta AND r.codigo_eco = p.apertura_eco
            WHERE p.id_atleta = ? AND p.fecha BETWEEN ? AND ?
            GROUP BY p.apertura_eco;
            """,
            (id_atleta, desde.isoformat(), hasta.isoformat()),
        )
        filas = [
            (eco, nombre, (puntos / total) * 100 if total else 0.0)
            for eco, nombre, total, puntos in cursor.fetchall()
        ]
        filas.sort(key=lambda f: (-f[2], f[0]))
        return filas

    def partidas_jugadas(self, id_atleta: int, desde: date, hasta: date) -> int:
        cursor = self._conexion.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM partidas WHERE id_atleta = ? AND fecha BETWEEN ? AND ?;",
            (id_atleta, desde.isoformat(), hasta.isoformat()),
        )
        return int(cursor.fetchone()[0] or 0)

    def torneos_jugados(self, id_atleta: int, desde: date, hasta: date) -> int:
        cursor = self._conexion.cursor()
        cursor.execute(
            """
            SELECT COUNT(DISTINCT evento) FROM partidas
            WHERE id_atleta = ? AND fecha BETWEEN ? AND ?;
            """,
            (id_atleta, desde.isoformat(), hasta.isoformat()),
        )
        return int(cursor.fetchone()[0] or 0)

    def porcentaje_asistencia(self, id_atleta: int, desde: date, hasta: date) -> float:
        cursor = self._conexion.cursor()
        cursor.execute(
            """
            SELECT COUNT(*),
                   SUM(CASE WHEN estado = 'PRESENTE' THEN 1 ELSE 0 END)
            FROM asistencias
            WHERE id_atleta = ? AND fecha BETWEEN ? AND ?;
            """,
            (id_atleta, desde.isoformat(), hasta.isoformat()),
        )
        total, presentes = cursor.fetchone()
        if not total:
            return 0.0
        return (int(presentes or 0) / int(total)) * 100

    def ejercicios_tacticos_resueltos(
        self, id_atleta: int, desde: date, hasta: date
    ) -> int:

        return 0

    def cumplimiento_objetivos(self, id_atleta: int, desde: date, hasta: date) -> float:
        cursor = self._conexion.cursor()
        cursor.execute(
            """
            SELECT COUNT(*),
                   SUM(CASE WHEN cumplido_por_entrenador = 1 THEN 1 ELSE 0 END)
            FROM objetivos_smart
            WHERE id_atleta = ? AND fecha_inicio <= ? AND fecha_limite >= ?;
            """,
            (id_atleta, hasta.isoformat(), desde.isoformat()),
        )
        total, cumplidos = cursor.fetchone()
        if not total:
            return 0.0
        return (int(cumplidos or 0) / int(total)) * 100

    def rating_fide(self, id_atleta: int, tipo: str) -> int:
        columna = {
            "rapidas": "rating_rapidas",
            "blitz": "rating_blitz",
        }.get(tipo, "rating_clasicas")
        cursor = self._conexion.cursor()
        cursor.execute(f"SELECT {columna} FROM atletas WHERE id = ?;", (id_atleta,))
        fila = cursor.fetchone()
        return int(fila[0]) if fila and fila[0] is not None else 0

    def variacion_rating(
        self, id_atleta: int, desde: date, hasta: date
    ) -> float:
        """variación del rating clásicas con snapshots históricos.

 Criterio documentado: rating de cierre (último snapshot con fecha <=
 "hasta") menos el último snapshot anterior al inicio; si no hay
 snapshot anterior se toma el primero disponible como base. Los
 snapshots sin fecha se consideran al 31 de diciembre de su año. Sin
 historial suficiente la variación es 0.0 (no se inventan datos).
 """
        cursor = self._conexion.cursor()
        cursor.execute(
            """
            SELECT anio, fecha_actualizacion_rating, rating_clasicas
            FROM perfiles_historicos_atleta
            WHERE id_atleta = ? AND rating_clasicas IS NOT NULL
            ORDER BY anio, id;
            """,
            (id_atleta,),
        )
        historial: List[tuple[date, int]] = []
        for anio, fecha, rating in cursor.fetchall():
            if fecha:
                momento = (
                    date.fromisoformat(fecha) if isinstance(fecha, str) else fecha
                )
            else:
                momento = date(int(anio), 12, 31)
            historial.append((momento, int(rating)))
        if not historial:
            return 0.0
        base: Optional[int] = None
        cierre: Optional[int] = None
        for momento, rating in historial:
            if momento < desde:
                base = rating
            if momento <= hasta:
                cierre = rating
        if cierre is None:
            return 0.0
        if base is None:
            base = historial[0][1]
        return float(cierre - base)

    def atletas_por_entrenador(self, id_entrenador: int) -> list:
        cursor = self._conexion.cursor()
        cursor.execute(
            "SELECT id_atleta FROM atleta_entrenadores WHERE id_entrenador = ? ORDER BY id_atleta;",
            (id_entrenador,),
        )
        return [int(f[0]) for f in cursor.fetchall()]

    def ids_atletas(self) -> list:
        cursor = self._conexion.cursor()
        cursor.execute("SELECT id FROM atletas ORDER BY id;")
        return [int(f[0]) for f in cursor.fetchall()]

    def torneos_del_atleta(self, id_atleta: int) -> list:
        cursor = self._conexion.cursor()
        cursor.execute(
            """
            SELECT evento, MIN(fecha), MAX(fecha)
            FROM partidas
            WHERE id_atleta = ?
            GROUP BY evento
            ORDER BY MIN(fecha), MAX(fecha);
            """,
            (id_atleta,),
        )
        filas = []
        for evento, desde, hasta in cursor.fetchall():
            d = date.fromisoformat(desde) if isinstance(desde, str) else desde
            h = date.fromisoformat(hasta) if isinstance(hasta, str) else hasta
            filas.append((evento, d, h))
        return filas

    def objetivos_no_cumplidos(self, id_atleta: int) -> int:
        cursor = self._conexion.cursor()
        cursor.execute(
            """
            SELECT COUNT(*) FROM objetivos_smart
            WHERE id_atleta = ? AND cumplido_por_entrenador = 0
              AND estado <> 'FINALIZADO';
            """,
            (id_atleta,),
        )
        return int(cursor.fetchone()[0] or 0)
