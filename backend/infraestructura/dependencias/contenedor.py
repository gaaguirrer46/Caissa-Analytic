"""Contenedor de dependencias para conectar dominio, adaptadores e infraestructura."""
from __future__ import annotations

import sqlite3
from typing import Optional

from adaptadores.secundarios.autenticacion import ServicioHashPbkdf2
from adaptadores.secundarios.reportes import ServicioReportesArchivo
from adaptadores.secundarios.persistencia import (
    ProveedorDatosAperturaSqlite,
    ProveedorDatosAvanceSqlite,
    RepositorioAnalisisTecnicoSqlite,
    RepositorioAsistenciaSqlite,
    RepositorioAtletasSqlite,
    RepositorioAperturasSqlite,
    RepositorioAuditoriaSqlite,
    RepositorioCategoriasSqlite,
    RepositorioConfiguracionSqlite,
    RepositorioEntrenamientosSqlite,
    RepositorioEvaluacionesSqlite,
    RepositorioIndicadoresSqlite,
    RepositorioObjetivosSqlite,
    RepositorioPartidasSqlite,
    RepositorioUsuariosSqlite,
    ProveedorDatosPartidasSqlite,
    ProveedorDatosRendimientoSqlite,
    ProveedorInformacionAtletaSqlite,
    ProveedorInformacionAutorizadaSqlite,
)
from adaptadores.secundarios.pgn.proveedor_pgn import ProveedorPGNEstandar
from dominio.atletas.casos_de_uso import (
    ActualizarPerfilAtleta,
    ActualizarRating,
    AsignarCategoriaAAtleta,
    AsignarEntrenadorAAtleta,
    ConfigurarCategoria,
    ConsultarMiInformacion,
    ConsultarPerfilAtleta,
    ConsultarSerieHistorica,
    ListarAtletasPorEntrenador,
    RegistrarAtleta,
    RetirarEntrenadorDeAtleta,
    VincularUsuarioAtleta,
)
from dominio.aperturas.casos_de_uso import (
    ActualizarEstadoApertura,
    CalcularEstadisticasApertura,
    ClasificarAperturaPrincipalSecundaria,
    ClasificarAperturasPorFrecuencia,
    ConsultarEstadisticasGeneralesApertura,
    ConsultarEstadisticasPorTorneo,
    EvaluarEfectividadApertura,
    RegistrarAperturaRepertorio,
)
from dominio.auditoria.casos_de_uso import (
    ConsultarHistorialCambios,
    RegistrarCambio,
    ValidarIntegridadDatos,
)
from dominio.configuracion.casos_de_uso import (
    ActualizarConfiguracion,
    ConfigurarAccesoInvitado,
    ConsultarConfiguracion,
)
from dominio.configuracion.proveedor_rangos import ProveedorRangosConfiguracion
from dominio.entrenamientos.casos_de_uso import (
    AprobarHorasEjecutadas,
    CancelarSesion,
    ConsultarCumplimientoSemanal,
    ConsultarDetalleSemanal,
    ConsultarHistorialEntrenamientos,
    PlanificarEntrenamientoSemanal,
    RegistrarAsistencia,
    RegistrarEjecucionEntrenamiento,
    RegistrarMiEjecucionEntrenamiento,
    ReprogramarSesion,
)
from dominio.evaluaciones.casos_de_uso import (
    ActualizarEvaluacion,
    ConsultarEvaluacionesPorAtleta,
    ConsultarMisEvaluaciones,
    CrearEvaluacion,
    ResumirEvaluaciones,
)
from dominio.indicadores.casos_de_uso import (
    CalcularIndicadoresPrincipales,
    CalcularIndicadoresSecundarios,
    ConsultarIndicadoresPermanentes,
    CompararConGrupo,
    CompararConPares,
    CompararTendencias,
    CompararTendenciasPeriodicas,
    EvaluadorRangos,
    GenerarDashboardAtleta,
    GenerarDashboardEntrenador,
    GenerarGraficoRendimiento,
    GenerarGraficoTendencias,
    GenerarReporte,
    GenerarReporteGrupal,
    GenerarReporteIndividualAtleta,
    GenerarReporteInstitucional,
    GenerarReporteIntegralAtleta,
    GenerarTablaDetallada,
)
from dominio.objetivos.casos_de_uso import (
    AprobarObjetivoSmart,
    CalcularAvanceObjetivo,
    CrearObjetivoSmart,
    EvaluarEstadoObjetivo,
    ListarObjetivosPorAtleta,
    ProponerObjetivoAtleta,
    ValidarCumplimientoObjetivo,
)
from dominio.patrones.casos_de_uso import DetectarPatronesError
from dominio.partidas.casos_de_uso import (
    ClasificarPartida,
    ConsultarEstadisticasPorFase,
    ImportarPartidaDesdePGN,
    RegistrarAnalisisTecnico,
    RegistrarPartida,
)
from dominio.usuarios.casos_de_uso import (
    AutenticarUsuario,
    CambiarRolUsuario,
    ConsultarInformacionAutorizada,
    CrearUsuario,
    ListarUsuariosPorRol,
    ObtenerUsuarioActual,
    VerificarPermiso,
)
from infraestructura.base_de_datos.conexion import obtener_conexion
from infraestructura.base_de_datos.inicializador import inicializar_base_de_datos

class Contenedor:
    """Fábrica y ensamblador de dependencias de la aplicación."""

    def __init__(self, conexion: Optional[sqlite3.Connection] = None) -> None:
        self.conexion = conexion or obtener_conexion()

        self.servicio_hash = ServicioHashPbkdf2()
        self.servicio_reportes = ServicioReportesArchivo()
        self.repo_usuarios = RepositorioUsuariosSqlite(self.conexion)
        self.repo_atletas = RepositorioAtletasSqlite(self.conexion)
        self.repo_categorias = RepositorioCategoriasSqlite(self.conexion)
        self.repo_objetivos = RepositorioObjetivosSqlite(self.conexion)
        self.proveedor_datos = ProveedorDatosAvanceSqlite(self.conexion)
        self.repo_entrenamientos = RepositorioEntrenamientosSqlite(self.conexion)
        self.repo_asistencia = RepositorioAsistenciaSqlite(self.conexion)
        self.repo_partidas = RepositorioPartidasSqlite(self.conexion)
        self.repo_analisis = RepositorioAnalisisTecnicoSqlite(self.conexion)
        self.repo_auditoria = RepositorioAuditoriaSqlite(self.conexion)
        self.repo_evaluaciones = RepositorioEvaluacionesSqlite(self.conexion)
        self.repo_configuracion = RepositorioConfiguracionSqlite(self.conexion)
        self.repo_indicadores = RepositorioIndicadoresSqlite(self.conexion)
        self.repo_aperturas = RepositorioAperturasSqlite(self.conexion)
        self.proveedor_aperturas = ProveedorDatosAperturaSqlite(self.conexion)
        self.proveedor_rendimiento = ProveedorDatosRendimientoSqlite(self.conexion)
        self.proveedor_informacion = ProveedorInformacionAtletaSqlite(
            self.conexion,
            self.repo_entrenamientos,
            self.repo_objetivos,
            self.repo_partidas,
            self.repo_analisis,
        )
        self.proveedor_informacion_autorizada = ProveedorInformacionAutorizadaSqlite(
            self.conexion
        )

        self.registrar_cambio = RegistrarCambio(self.repo_auditoria)

        self.autenticar_usuario = AutenticarUsuario(self.repo_usuarios, self.servicio_hash)
        self.crear_usuario = CrearUsuario(self.repo_usuarios, self.servicio_hash)
        self.cambiar_rol = CambiarRolUsuario(self.repo_usuarios)
        self.listar_usuarios_por_rol = ListarUsuariosPorRol(self.repo_usuarios)
        self.verificar_permiso = VerificarPermiso()
        self.obtener_usuario_actual = ObtenerUsuarioActual(self.repo_usuarios)

        self.registrar_atleta = RegistrarAtleta(
            self.repo_atletas, self.repo_categorias, self.repo_configuracion
        )
        self.actualizar_perfil_atleta = ActualizarPerfilAtleta(
            self.repo_atletas, self.repo_configuracion
        )
        self.consultar_perfil_atleta = ConsultarPerfilAtleta(self.repo_atletas)
        self.consultar_serie_historica = ConsultarSerieHistorica(self.repo_atletas)
        self.asignar_categoria = AsignarCategoriaAAtleta(self.repo_atletas, self.repo_categorias)
        self.configurar_categoria = ConfigurarCategoria(self.repo_categorias)
        self.asignar_entrenador = AsignarEntrenadorAAtleta(
            self.repo_atletas, self.repo_configuracion
        )
        self.retirar_entrenador = RetirarEntrenadorDeAtleta(self.repo_atletas)
        self.actualizar_rating = ActualizarRating(
            self.repo_atletas, auditor=self.registrar_cambio
        )
        self.listar_atletas_por_entrenador = ListarAtletasPorEntrenador(self.repo_atletas)
        self.consultar_mi_informacion = ConsultarMiInformacion(
            self.repo_usuarios, self.repo_atletas, self.proveedor_informacion
        )
        self.vincular_usuario_atleta = VincularUsuarioAtleta(
            self.proveedor_informacion
        )

        self.crear_objetivo = CrearObjetivoSmart(self.repo_objetivos)
        self.proponer_objetivo_atleta = ProponerObjetivoAtleta(
            self.repo_objetivos, self.proveedor_informacion
        )
        self.aprobar_objetivo = AprobarObjetivoSmart(self.repo_objetivos)
        self.calcular_avance_objetivo = CalcularAvanceObjetivo(self.repo_objetivos, self.proveedor_datos)
        self.evaluar_estado_objetivo = EvaluarEstadoObjetivo(self.repo_objetivos)
        self.validar_cumplimiento_objetivo = ValidarCumplimientoObjetivo(
            self.repo_objetivos, auditor=self.registrar_cambio
        )
        self.listar_objetivos_atleta = ListarObjetivosPorAtleta(self.repo_objetivos)

        self.planificar_entrenamiento = PlanificarEntrenamientoSemanal(self.repo_entrenamientos)
        self.reprogramar_sesion = ReprogramarSesion(self.repo_entrenamientos)
        self.cancelar_sesion = CancelarSesion(self.repo_entrenamientos)
        self.registrar_ejecucion = RegistrarEjecucionEntrenamiento(self.repo_entrenamientos)
        self.registrar_mi_ejecucion = RegistrarMiEjecucionEntrenamiento(
            self.repo_entrenamientos, self.proveedor_informacion
        )
        self.aprobar_horas = AprobarHorasEjecutadas(
            self.repo_entrenamientos, auditor=self.registrar_cambio
        )
        self.consultar_cumplimiento_semanal = ConsultarCumplimientoSemanal(self.repo_entrenamientos)
        self.consultar_detalle_semanal = ConsultarDetalleSemanal(self.repo_entrenamientos)
        self.registrar_asistencia = RegistrarAsistencia(
            self.repo_asistencia, self.repo_entrenamientos
        )
        self.consultar_historial_entrenamientos = ConsultarHistorialEntrenamientos(self.repo_entrenamientos)

        self.proveedor_patrones = ProveedorDatosPartidasSqlite(self.conexion)
        self.detectar_patrones = DetectarPatronesError(self.proveedor_patrones)

        self.registrar_apertura = RegistrarAperturaRepertorio(self.repo_aperturas)
        self.actualizar_estado_apertura = ActualizarEstadoApertura(
            self.repo_aperturas, auditor=self.registrar_cambio
        )
        self.clasificar_apertura_uso = ClasificarAperturaPrincipalSecundaria(self.repo_aperturas)
        self.clasificar_aperturas_frecuencia = ClasificarAperturasPorFrecuencia(self.repo_aperturas)
        self.evaluar_efectividad_apertura = EvaluarEfectividadApertura(self.repo_aperturas)
        self.consultar_estadisticas_apertura = ConsultarEstadisticasGeneralesApertura(self.repo_aperturas)
        self.calcular_estadisticas_apertura = CalcularEstadisticasApertura(
            self.repo_aperturas, self.proveedor_aperturas
        )
        self.consultar_estadisticas_por_torneo = ConsultarEstadisticasPorTorneo(self.repo_aperturas)

        self.registrar_partida = RegistrarPartida(self.repo_partidas)
        self.registrar_analisis_tecnico = RegistrarAnalisisTecnico(self.repo_analisis, self.repo_partidas)
        self.clasificar_partida = ClasificarPartida()
        self.consultar_estadisticas_por_fase = ConsultarEstadisticasPorFase(self.repo_partidas, self.repo_analisis)

        self.importar_partida_pgn = ImportarPartidaDesdePGN(
            self.repo_partidas, ProveedorPGNEstandar()
        )

        self.crear_evaluacion = CrearEvaluacion(
            self.repo_evaluaciones, self.proveedor_informacion
        )

        self.resumir_evaluaciones = ResumirEvaluaciones(self.repo_evaluaciones)
        self.actualizar_evaluacion = ActualizarEvaluacion(self.repo_evaluaciones)
        self.consultar_evaluaciones_atleta = ConsultarEvaluacionesPorAtleta(self.repo_evaluaciones)
        self.consultar_mis_evaluaciones = ConsultarMisEvaluaciones(
            self.repo_evaluaciones, self.proveedor_informacion
        )

        self.consultar_configuracion = ConsultarConfiguracion(self.repo_configuracion)
        self.actualizar_configuracion = ActualizarConfiguracion(self.repo_configuracion)
        self.configurar_acceso_invitado = ConfigurarAccesoInvitado(
            self.repo_configuracion, auditor=self.registrar_cambio
        )
        self.proveedor_rangos = ProveedorRangosConfiguracion(self.repo_configuracion)
        self.consultar_informacion_autorizada = ConsultarInformacionAutorizada(
            self.repo_configuracion, self.proveedor_informacion_autorizada
        )

        self.evaluador_rangos = EvaluadorRangos(self.proveedor_rangos)
        self.calcular_indicadores_principales = CalcularIndicadoresPrincipales(
            self.repo_indicadores, self.proveedor_rendimiento, self.evaluador_rangos
        )
        self.calcular_indicadores_secundarios = CalcularIndicadoresSecundarios(
            self.repo_indicadores, self.proveedor_rendimiento, self.evaluador_rangos
        )
        self.generar_dashboard_entrenador = GenerarDashboardEntrenador(
            self.repo_indicadores, self.proveedor_rendimiento
        )
        self.generar_dashboard_atleta = GenerarDashboardAtleta(
            self.repo_indicadores,
            self.proveedor_rendimiento,

            resolutor=self.proveedor_informacion,
        )
        self.comparar_tendencias = CompararTendencias(self.proveedor_rendimiento)
        self.comparar_tendencias_periodicas = CompararTendenciasPeriodicas(
            self.proveedor_rendimiento
        )
        self.comparar_con_grupo = CompararConGrupo(self.proveedor_rendimiento)
        self.comparar_con_pares = CompararConPares(self.proveedor_rendimiento)
        self.consultar_indicadores_permanentes = ConsultarIndicadoresPermanentes(
            self.proveedor_rendimiento,

            resolutor=self.proveedor_informacion,
        )
        self.generar_grafico_tendencias = GenerarGraficoTendencias(
            self.proveedor_rendimiento, self.servicio_reportes
        )

        self.generar_reporte = GenerarReporte(self.servicio_reportes)

        self.generar_reporte_individual = GenerarReporteIndividualAtleta(
            self.servicio_reportes, self.proveedor_rendimiento, self.repo_atletas
        )
        self.generar_reporte_integral = GenerarReporteIntegralAtleta(
            self.servicio_reportes,
            self.proveedor_rendimiento,
            self.repo_atletas,
        )
        self.generar_reporte_grupal = GenerarReporteGrupal(
            self.servicio_reportes, self.proveedor_rendimiento
        )
        self.generar_reporte_institucional = GenerarReporteInstitucional(
            self.servicio_reportes, self.proveedor_rendimiento
        )

        self.generar_grafico_rendimiento = GenerarGraficoRendimiento(
            self.proveedor_rendimiento, self.servicio_reportes
        )
        self.generar_tabla_detallada = GenerarTablaDetallada(
            self.servicio_reportes,
            self.proveedor_rendimiento,
            self.repo_partidas,
            self.repo_entrenamientos,
            self.repo_objetivos,
        )

        self.consultar_historial_cambios = ConsultarHistorialCambios(self.repo_auditoria)
        self.validar_integridad_datos = ValidarIntegridadDatos()

    @classmethod
    def crear_para_pruebas(cls) -> Contenedor:
        """Crea un contenedor con base de datos SQLite en memoria lista con el esquema oficial."""
        conn = inicializar_base_de_datos(en_memoria=True)
        contenedor = cls(conexion=conn)

        contenedor.proveedor_informacion.vincular_usuario(2, 1)
        return contenedor
