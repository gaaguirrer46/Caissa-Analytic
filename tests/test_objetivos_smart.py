"""Suite de pruebas automatizadas para Objetivos SMART (RF-03.3).

Verifica exhaustivamente la obligatoriedad y coherencia temporal de las fechas
de acuerdo con el requerimiento RF-03.3.
"""
import os
import sys
import sqlite3
from datetime import date, datetime
import pytest

# Asegurar que el directorio raíz del proyecto esté en sys.path al ejecutar directamente
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dominio.comun.errores import EntidadNoEncontrada, ErrorValidacion
from dominio.objetivos.entidades import ObjetivoSMART, EstadoObjetivo, TipoIndicadorAvance
from dominio.objetivos.validador import ObjetivoSMARTValidator
from dominio.objetivos.casos_de_uso import (
    CrearObjetivoSmart,
    ModificarObjetivoSmart,
    AprobarObjetivoSmart,
    ListarObjetivosPorAtleta,
)
from dominio.usuarios.entidades import Rol
from adaptadores.secundarios.persistencia.repositorio_objetivos_sqlite import RepositorioObjetivosSQLite


@pytest.fixture
def db_conn():
    """Crea una base de datos SQLite en memoria con el esquema canónico oficial."""
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON;")
    
    # Cargar DDL desde schema.sql
    schema_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "infraestructura",
        "base_de_datos",
        "schema.sql"
    )
    with open(schema_path, "r", encoding="utf-8") as f:
        ddl = f.read()
    
    conn.executescript(ddl)
    yield conn
    conn.close()


@pytest.fixture
def repo(db_conn):
    """Instancia del repositorio SQLite para Objetivos SMART."""
    return RepositorioObjetivosSQLite(db_conn)


def test_crear_objetivo_valido(repo):
    """Prueba 1 (Nominal): Inserción exitosa de un objetivo con fechas de inicio y límite válidas."""
    f_inicio = date(2026, 8, 1)
    f_limite = date(2026, 12, 31)

    nuevo_obj = ObjetivoSMART(
        id_atleta=1,
        titulo="Maestría FIDE",
        descripcion="Alcanzar ELO 2300 y norma de Maestro FIDE",
        fecha_inicio=f_inicio,
        fecha_limite=f_limite,
        indicador_meta=TipoIndicadorAvance.RATING,
        valor_meta=2300.0,
        creado_por="entrenador.magnus@caissa.org"
    )

    guardado = repo.guardar(nuevo_obj)

    assert guardado.id is not None
    assert guardado.fecha_inicio == f_inicio
    assert guardado.fecha_limite == f_limite
    assert guardado.estado == EstadoObjetivo.PENDIENTE_APROBACION

    # Verificación directa en base de datos SQLite
    recuperado = repo.buscar_por_id(guardado.id)
    assert recuperado is not None
    assert recuperado.descripcion == "Alcanzar ELO 2300 y norma de Maestro FIDE"
    assert recuperado.fecha_inicio == f_inicio
    assert recuperado.fecha_limite == f_limite


def test_error_fecha_inicio_nula(repo):
    """Prueba 2 (Regla a): Falla al omitir o pasar None/vacía la fecha de inicio."""
    with pytest.raises(ErrorValidacion) as exc_info:
        ObjetivoSMARTValidator.validar_fechas(None, date(2026, 12, 31))
    assert "La fecha de inicio es estrictamente obligatoria." in str(exc_info.value)

    with pytest.raises(ErrorValidacion) as exc_info_vacio:
        ObjetivoSMARTValidator.validar_fechas("", date(2026, 12, 31))
    assert "La fecha de inicio es estrictamente obligatoria." in str(exc_info_vacio.value)

    with pytest.raises(ErrorValidacion) as exc_info_entidad:
        ObjetivoSMART(
            id_atleta=1,
            descripcion="Objetivo sin fecha inicio",
            fecha_inicio=None,  # type: ignore
            fecha_limite=date(2026, 12, 31)
        )
    assert "La fecha de inicio es estrictamente obligatoria." in str(exc_info_entidad.value)


def test_error_fecha_limite_nula(repo):
    """Prueba 3 (Regla b): Falla al omitir o pasar None/vacía la fecha límite."""
    with pytest.raises(ErrorValidacion) as exc_info:
        ObjetivoSMARTValidator.validar_fechas(date(2026, 8, 1), None)
    assert "La fecha límite es estrictamente obligatoria." in str(exc_info.value)

    with pytest.raises(ErrorValidacion) as exc_info_vacio:
        ObjetivoSMARTValidator.validar_fechas(date(2026, 8, 1), "   ")
    assert "La fecha límite es estrictamente obligatoria." in str(exc_info_vacio.value)

    with pytest.raises(ErrorValidacion) as exc_info_entidad:
        ObjetivoSMART(
            id_atleta=1,
            descripcion="Objetivo sin fecha limite",
            fecha_inicio=date(2026, 8, 1),
            fecha_limite=None  # type: ignore
        )
    assert "La fecha límite es estrictamente obligatoria." in str(exc_info_entidad.value)


def test_error_fecha_limite_menor_que_inicio(repo):
    """Prueba 4 (Regla c): Falla si fecha_limite < fecha_inicio (coherencia temporal)."""
    f_inicio = date(2026, 12, 31)
    f_limite = date(2026, 8, 1)

    with pytest.raises(ErrorValidacion) as exc_info:
        ObjetivoSMARTValidator.validar_fechas(f_inicio, f_limite)
    assert "La fecha límite no puede ser anterior a la fecha de inicio." in str(exc_info.value)

    with pytest.raises(ErrorValidacion) as exc_info_entidad:
        ObjetivoSMART(
            id_atleta=1,
            descripcion="Fechas invertidas",
            fecha_inicio=f_inicio,
            fecha_limite=f_limite
        )
    assert "La fecha límite no puede ser anterior a la fecha de inicio." in str(exc_info_entidad.value)


def test_fechas_mismo_dia_es_valido():
    """Prueba 5: Un objetivo de un solo día (inicio == limite) es válido cronológicamente."""
    mismo_dia = date(2026, 10, 15)
    d_ini, d_lim = ObjetivoSMARTValidator.validar_fechas(mismo_dia, mismo_dia)
    assert d_ini == mismo_dia
    assert d_lim == mismo_dia


def test_parseo_fechas_iso_y_datetime():
    """Prueba 6: Normaliza transparentemente cadenas ISO YYYY-MM-DD y objetos datetime."""
    d_ini, d_lim = ObjetivoSMARTValidator.validar_fechas("2026-09-01", "2026-11-30")
    assert d_ini == date(2026, 9, 1)
    assert d_lim == date(2026, 11, 30)

    dt_ini = datetime(2026, 9, 1, 10, 30)
    dt_lim = datetime(2026, 11, 30, 18, 0)
    d_ini2, d_lim2 = ObjetivoSMARTValidator.validar_fechas(dt_ini, dt_lim)
    assert d_ini2 == date(2026, 9, 1)
    assert d_lim2 == date(2026, 11, 30)


def test_error_formato_fecha_invalido():
    """Prueba 7: Rechaza formatos de fecha no conformes con ISO (ej. DD/MM/YYYY)."""
    with pytest.raises(ErrorValidacion) as exc_info:
        ObjetivoSMARTValidator.parsear_fecha("01/09/2026", "fecha de inicio")
    assert "Formato de fecha de inicio inválido" in str(exc_info.value)


def test_caso_de_uso_crear_objetivo(repo):
    """Prueba 8: El caso de uso CrearObjetivoSmart valida fechas y persiste correctamente."""
    caso = CrearObjetivoSmart(repo)
    obj = caso.ejecutar(
        id_atleta=1,
        descripcion="Incrementar ELO rápido en 150 puntos",
        indicador_meta=TipoIndicadorAvance.RATING,
        valor_meta=150.0,
        fecha_inicio="2026-09-01",
        fecha_limite="2026-12-15",
        rol_proponente=Rol.ENTRENADOR,
    )
    assert obj.id is not None
    assert obj.fecha_inicio == date(2026, 9, 1)
    assert obj.fecha_limite == date(2026, 12, 15)


def test_caso_de_uso_crear_falla_si_falta_fecha(repo):
    """Prueba 9: CrearObjetivoSmart falla preventivamente si falta fecha_limite."""
    caso = CrearObjetivoSmart(repo)
    with pytest.raises(ErrorValidacion) as exc_info:
        caso.ejecutar(
            id_atleta=1,
            descripcion="Sin fecha limite",
            fecha_inicio="2026-09-01",
            fecha_limite=None,
        )
    assert "La fecha límite es estrictamente obligatoria." in str(exc_info.value)


def test_caso_de_uso_modificar_objetivo(repo):
    """Prueba 10: ModificarObjetivoSmart permite prorrogar fecha límite válidamente."""
    caso_crear = CrearObjetivoSmart(repo)
    obj = caso_crear.ejecutar(
        id_atleta=1,
        descripcion="Original",
        fecha_inicio="2026-09-01",
        fecha_limite="2026-11-01",
    )

    caso_mod = ModificarObjetivoSmart(repo)
    # Prórroga válida
    modificado = caso_mod.ejecutar(
        id_objetivo=obj.id,
        fecha_limite="2026-12-01"
    )
    assert modificado.fecha_limite == date(2026, 12, 1)


def test_modificar_fechas_incoherentes_es_rechazado(repo):
    """Prueba 11: ModificarObjetivoSmart rechaza prórrogas que dejen fecha límite anterior a inicio."""
    caso_crear = CrearObjetivoSmart(repo)
    obj = caso_crear.ejecutar(
        id_atleta=1,
        descripcion="Original",
        fecha_inicio="2026-09-01",
        fecha_limite="2026-11-01",
    )

    caso_mod = ModificarObjetivoSmart(repo)
    # Intento de modificación inválida (fecha_limite anterior a la de inicio)
    with pytest.raises(ErrorValidacion) as exc_info:
        caso_mod.ejecutar(
            id_objetivo=obj.id,
            fecha_limite="2026-08-01"
        )
    assert "La fecha límite no puede ser anterior a la fecha de inicio." in str(exc_info.value)


def test_aprobar_y_listar_objetivos(repo):
    """Prueba 12: Flujo integrado de aprobación y consulta por atleta conservando integridad de fechas."""
    caso_crear = CrearObjetivoSmart(repo)
    obj = caso_crear.ejecutar(
        id_atleta=1,
        descripcion="Objetivo Atleta 1",
        fecha_inicio="2026-09-01",
        fecha_limite="2026-10-01",
    )

    caso_aprobar = AprobarObjetivoSmart(repo)
    aprobado = caso_aprobar.ejecutar(obj.id)
    assert aprobado.aprobado_por_entrenador is True
    assert aprobado.estado == EstadoObjetivo.EN_PROCESO

    caso_listar = ListarObjetivosPorAtleta(repo)
    lista = caso_listar.ejecutar(1)
    assert any(o.id == obj.id for o in lista)


if __name__ == "__main__":
    # Permite ejecutar directamente el archivo con 'python tests/test_objetivos_smart.py'
    sys.exit(pytest.main([__file__, "-v"]))
