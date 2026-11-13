"""Adaptadores de persistencia SQLite."""
from .repositorio_aperturas_sqlite import (
    ProveedorDatosAperturaSqlite,
    RepositorioAperturasSqlite,
)
from .repositorio_atletas_sqlite import (
    RepositorioAtletasSqlite,
    RepositorioCategoriasSqlite,
)
from .repositorio_auditoria_sqlite import RepositorioAuditoriaSqlite
from .repositorio_configuracion_sqlite import RepositorioConfiguracionSqlite
from .proveedor_informacion_atleta_sqlite import ProveedorInformacionAtletaSqlite
from .proveedor_patrones_sqlite import ProveedorDatosPartidasSqlite
from .proveedor_informacion_autorizada_sqlite import (
    ProveedorInformacionAutorizadaSqlite,
)
from .repositorio_entrenamientos_sqlite import (
    RepositorioAsistenciaSqlite,
    RepositorioEntrenamientosSqlite,
)
from .repositorio_evaluaciones_sqlite import RepositorioEvaluacionesSqlite
from .repositorio_indicadores_sqlite import (
    ProveedorDatosRendimientoSqlite,
    RepositorioIndicadoresSqlite,
)
from .repositorio_objetivos_sqlite import (
    ProveedorDatosAvanceSqlite,
    RepositorioObjetivosSqlite,
)
from .repositorio_partidas_sqlite import (
    RepositorioAnalisisTecnicoSqlite,
    RepositorioPartidasSqlite,
)
from .repositorio_usuarios_sqlite import RepositorioUsuariosSqlite

__all__ = [
    "RepositorioUsuariosSqlite",
    "RepositorioAperturasSqlite",
    "ProveedorDatosAperturaSqlite",
    "RepositorioAtletasSqlite",
    "RepositorioCategoriasSqlite",
    "RepositorioObjetivosSqlite",
    "ProveedorDatosAvanceSqlite",
    "RepositorioEntrenamientosSqlite",
    "RepositorioAsistenciaSqlite",
    "RepositorioPartidasSqlite",
    "RepositorioAnalisisTecnicoSqlite",
    "RepositorioAuditoriaSqlite",
    "RepositorioConfiguracionSqlite",
    "RepositorioEvaluacionesSqlite",
    "RepositorioIndicadoresSqlite",
    "ProveedorDatosPartidasSqlite",
    "ProveedorDatosRendimientoSqlite",
    "ProveedorInformacionAtletaSqlite",
    "ProveedorInformacionAutorizadaSqlite",
]
