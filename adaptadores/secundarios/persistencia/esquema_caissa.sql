-- ==============================================================================
-- SE CAISSA ANALYTICS - Esquema Relacional Oficial Docente (Sumativa 3)
-- Adaptadores de Persistencia - Requerimiento RF-03.3
-- ==============================================================================

-- 1. LIMPIEZA DE TABLAS PREVIAS
DROP TABLE IF EXISTS registros_auditoria;
DROP TABLE IF EXISTS evaluacion_calificaciones_indicador;
DROP TABLE IF EXISTS evaluaciones_atleta;
DROP TABLE IF EXISTS alertas;
DROP TABLE IF EXISTS indicadores_rendimiento;
DROP TABLE IF EXISTS estadisticas_aperturas;
DROP TABLE IF EXISTS aperturas_repertorio;
DROP TABLE IF EXISTS patrones_detectados;
DROP TABLE IF EXISTS analisis_tecnico_partidas;
DROP TABLE IF EXISTS partidas;
DROP TABLE IF EXISTS asistencias;
DROP TABLE IF EXISTS ejecuciones_entrenamiento;
DROP TABLE IF EXISTS sesiones_entrenamiento;
DROP TABLE IF EXISTS planes_entrenamiento;
DROP TABLE IF EXISTS indicadores_avance_objetivo;
DROP TABLE IF EXISTS objetivos_smart;
DROP TABLE IF EXISTS perfiles_historicos_atleta;
DROP TABLE IF EXISTS atleta_entrenadores;
DROP TABLE IF EXISTS atleta_clubs;
DROP TABLE IF EXISTS atleta_categorias;
DROP TABLE IF EXISTS atletas;
DROP TABLE IF EXISTS categorias;
DROP TABLE IF EXISTS usuarios;

-- 2. TABLAS PRINCIPALES Y DE IDENTIDAD
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    correo VARCHAR(100) NOT NULL UNIQUE,
    hash_contrasena VARCHAR(100) NOT NULL,
    rol VARCHAR(12) NOT NULL CHECK (rol IN ('ENTRENADOR', 'ATLETA', 'INVITADO')),
    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(50) NOT NULL,
    tipo VARCHAR(10) NOT NULL CHECK (tipo IN ('EDAD', 'NIVEL', 'ELO')),
    rango VARCHAR(30) NOT NULL,
    editable_por_admin BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE atletas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(100) NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    sexo VARCHAR(10) NOT NULL,
    identidad_opcional VARCHAR(20),
    fotografia_opcional VARCHAR(255),
    federacion VARCHAR(50),
    universidad VARCHAR(80),
    carrera VARCHAR(80),
    rating_clasicas SMALLINT CHECK (rating_clasicas BETWEEN 0 AND 4000),
    rating_rapidas SMALLINT CHECK (rating_rapidas BETWEEN 0 AND 4000),
    rating_blitz SMALLINT CHECK (rating_blitz BETWEEN 0 AND 4000),
    rating_chess_com SMALLINT CHECK (rating_chess_com BETWEEN 0 AND 4000),
    rating_lichess SMALLINT CHECK (rating_lichess BETWEEN 0 AND 4000),
    fecha_actualizacion_rating DATE,
    activo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE atleta_categorias (
    id_atleta INTEGER NOT NULL,
    id_categoria INTEGER NOT NULL,
    PRIMARY KEY (id_atleta, id_categoria),
    FOREIGN KEY (id_atleta) REFERENCES atletas(id) ON DELETE CASCADE,
    FOREIGN KEY (id_categoria) REFERENCES categorias(id) ON DELETE CASCADE
);

CREATE TABLE atleta_clubs (
    id_atleta INTEGER NOT NULL,
    club VARCHAR(60) NOT NULL,
    PRIMARY KEY (id_atleta, club),
    FOREIGN KEY (id_atleta) REFERENCES atletas(id) ON DELETE CASCADE
);

CREATE TABLE atleta_entrenadores (
    id_atleta INTEGER NOT NULL,
    id_entrenador INTEGER NOT NULL,
    PRIMARY KEY (id_atleta, id_entrenador),
    FOREIGN KEY (id_atleta) REFERENCES atletas(id) ON DELETE CASCADE,
    FOREIGN KEY (id_entrenador) REFERENCES usuarios(id) ON DELETE CASCADE
);

CREATE TABLE perfiles_historicos_atleta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_atleta INTEGER NOT NULL,
    anio SMALLINT NOT NULL,
    torneo VARCHAR(100),
    rating_clasicas SMALLINT,
    rating_rapidas SMALLINT,
    rating_blitz SMALLINT,
    rating_chess_com SMALLINT,
    rating_lichess SMALLINT,
    fecha_actualizacion_rating DATE,
    observaciones VARCHAR(500),
    FOREIGN KEY (id_atleta) REFERENCES atletas(id) ON DELETE CASCADE
);

-- 3. OBJETIVOS SMART (RF-03, RF-03.3)
CREATE TABLE objetivos_smart (
    id_objetivo INTEGER PRIMARY KEY AUTOINCREMENT,
    id_atleta INTEGER NOT NULL,
    titulo VARCHAR(150),
    descripcion VARCHAR(300) NOT NULL,
    rating_actual SMALLINT NOT NULL CHECK (rating_actual BETWEEN 0 AND 4000),
    rating_meta SMALLINT NOT NULL CHECK (rating_meta BETWEEN 0 AND 4000),
    fecha_inicio DATE NOT NULL,
    fecha_limite DATE NOT NULL,
    porcentaje_avance DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE_APROBACION' CHECK (estado IN ('PENDIENTE_APROBACION', 'EN_PROCESO', 'RETRASADO', 'FINALIZADO')),
    creado_por VARCHAR(100),
    fecha_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    indicador_meta VARCHAR(20) NOT NULL DEFAULT 'RATING' CHECK (indicador_meta IN ('HORAS_ENTRENADAS', 'RATING', 'TAREAS', 'TORNEOS', 'MEDALLAS')),
    valor_meta DECIMAL(8,2) NOT NULL DEFAULT 0.00,
    aprobado_por_entrenador BOOLEAN NOT NULL DEFAULT FALSE,
    cumplido_por_entrenador BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT CHK_FechasValidas CHECK (date(fecha_limite) >= date(fecha_inicio)),
    FOREIGN KEY (id_atleta) REFERENCES atletas(id) ON DELETE CASCADE
);

CREATE TABLE indicadores_avance_objetivo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_objetivo INTEGER NOT NULL,
    tipo VARCHAR(30) NOT NULL,
    valor_actual DECIMAL(8,2) NOT NULL,
    valor_esperado DECIMAL(8,2) NOT NULL,
    FOREIGN KEY (id_objetivo) REFERENCES objetivos_smart(id_objetivo) ON DELETE CASCADE
);

-- 4. ENTRENAMIENTOS Y ASISTENCIA
CREATE TABLE planes_entrenamiento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_atleta INTEGER NOT NULL,
    semana SMALLINT NOT NULL CHECK (semana BETWEEN 1 AND 53),
    anio SMALLINT NOT NULL CHECK (anio BETWEEN 2000 AND 2100),
    FOREIGN KEY (id_atleta) REFERENCES atletas(id) ON DELETE CASCADE
);

CREATE TABLE sesiones_entrenamiento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_plan INTEGER NOT NULL,
    tipo VARCHAR(25) NOT NULL CHECK (tipo IN (
        'APERTURAS', 'MEDIO_JUEGO', 'FINALES', 'TACTICA', 'ESTRATEGIA',
        'CALCULO', 'VISUALIZACION', 'ANALISIS_PARTIDAS', 'CLASES_TEORICAS',
        'PREPARACION_FISICA', 'PSICOLOGICA_DEPORTIVA', 'PREPARACION_COMPETITIVA'
    )),
    dia_semana VARCHAR(10) NOT NULL,
    horas_planificadas DECIMAL(4,2) NOT NULL,
    horas_ejecutadas DECIMAL(4,2),
    estado VARCHAR(15) NOT NULL CHECK (estado IN ('PROGRAMADA', 'REPROGRAMADA', 'CANCELADA', 'EJECUTADA')),
    ejecucion_aprobada BOOLEAN NOT NULL DEFAULT FALSE,
    observaciones VARCHAR(500),
    FOREIGN KEY (id_plan) REFERENCES planes_entrenamiento(id) ON DELETE CASCADE
);

CREATE TABLE ejecuciones_entrenamiento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_sesion INTEGER NOT NULL,
    horas_ejecutadas DECIMAL(4,2) NOT NULL,
    fecha_registro DATE NOT NULL,
    registrado_por_atleta BOOLEAN NOT NULL DEFAULT TRUE,
    aprobado_por_entrenador BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (id_sesion) REFERENCES sesiones_entrenamiento(id) ON DELETE CASCADE
);

CREATE TABLE asistencias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_atleta INTEGER NOT NULL,
    id_sesion INTEGER NOT NULL,
    fecha DATE NOT NULL,
    estado VARCHAR(11) NOT NULL CHECK (estado IN ('PRESENTE', 'AUSENTE', 'JUSTIFICADO')),
    FOREIGN KEY (id_atleta) REFERENCES atletas(id) ON DELETE CASCADE,
    FOREIGN KEY (id_sesion) REFERENCES sesiones_entrenamiento(id) ON DELETE CASCADE
);

-- 5. PARTIDAS Y ANÁLISIS TÉCNICO
CREATE TABLE partidas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_atleta INTEGER NOT NULL,
    evento VARCHAR(100) NOT NULL,
    fecha DATE NOT NULL,
    jugador_blancas VARCHAR(60) NOT NULL,
    jugador_negras VARCHAR(60) NOT NULL,
    rating_blancas SMALLINT NOT NULL,
    rating_negras SMALLINT NOT NULL,
    resultado VARCHAR(7) NOT NULL CHECK (resultado IN ('1-0', '0-1', '1/2-1/2')),
    apertura_eco VARCHAR(5) NOT NULL,
    control_tiempo VARCHAR(20),
    fuente VARCHAR(15) NOT NULL CHECK (fuente IN ('PGN', 'CHESS_COM', 'LICHESS', 'MANUAL', 'CHESSBASE')),
    color_atleta VARCHAR(7) CHECK (color_atleta IN ('BLANCAS', 'NEGRAS')),
    FOREIGN KEY (id_atleta) REFERENCES atletas(id) ON DELETE CASCADE
);

CREATE TABLE analisis_tecnico_partidas (
    id_partida INTEGER PRIMARY KEY,
    accuracy DECIMAL(5,2) CHECK (accuracy BETWEEN 0.00 AND 100.00),
    acpl DECIMAL(6,2) CHECK (acpl >= 0.00),
    blunders SMALLINT NOT NULL DEFAULT 0,
    errores SMALLINT NOT NULL DEFAULT 0,
    imprecisiones SMALLINT NOT NULL DEFAULT 0,
    brilliant_moves SMALLINT NOT NULL DEFAULT 0,
    excelente SMALLINT NOT NULL DEFAULT 0,
    buena SMALLINT NOT NULL DEFAULT 0,
    libro SMALLINT NOT NULL DEFAULT 0,
    tiempo_promedio_jugada DECIMAL(6,2),
    perdidas_por_tiempo SMALLINT NOT NULL DEFAULT 0,
    FOREIGN KEY (id_partida) REFERENCES partidas(id) ON DELETE CASCADE
);

-- 6. PATRONES DE ERROR Y REPERTORIO DE APERTURAS
CREATE TABLE patrones_detectados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_atleta INTEGER NOT NULL,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('TACTICO', 'ESTRATEGICO', 'APERTURA', 'FINALES', 'GESTION_TIEMPO', 'COMPETITIVO', 'DISCIPLINA')),
    descripcion VARCHAR(300) NOT NULL,
    frecuencia_absoluta SMALLINT NOT NULL,
    frecuencia_relativa DECIMAL(5,2),
    periodo_inicio DATE,
    periodo_fin DATE,
    FOREIGN KEY (id_atleta) REFERENCES atletas(id) ON DELETE CASCADE
);

CREATE TABLE aperturas_repertorio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_atleta INTEGER NOT NULL,
    codigo_eco VARCHAR(5) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    variante VARCHAR(100),
    color VARCHAR(7) NOT NULL CHECK (color IN ('BLANCAS', 'NEGRAS')),
    estado VARCHAR(15) NOT NULL CHECK (estado IN ('EN_ESTUDIO', 'ACTIVA', 'EN_REVISION', 'DESCARTADA')),
    nivel_dominio VARCHAR(12) NOT NULL CHECK (nivel_dominio IN ('INICIAL', 'INTERMEDIO', 'AVANZADO')),
    fuente_estudio VARCHAR(255),
    observaciones VARCHAR(300),
    clasificacion_uso VARCHAR(10) NOT NULL CHECK (clasificacion_uso IN ('PRINCIPAL', 'SECUNDARIA')),
    FOREIGN KEY (id_atleta) REFERENCES atletas(id) ON DELETE CASCADE
);

CREATE TABLE estadisticas_aperturas (
    id_apertura INTEGER PRIMARY KEY,
    partidas_jugadas SMALLINT NOT NULL DEFAULT 0,
    victorias SMALLINT NOT NULL DEFAULT 0,
    empates SMALLINT NOT NULL DEFAULT 0,
    derrotas SMALLINT NOT NULL DEFAULT 0,
    accuracy_promedio DECIMAL(5,2),
    acpl_promedio DECIMAL(6,2),
    errores_frecuentes SMALLINT NOT NULL DEFAULT 0,
    evaluacion_motor_promedio DECIMAL(5,2),
    tiempo_promedio DECIMAL(6,2),
    FOREIGN KEY (id_apertura) REFERENCES aperturas_repertorio(id) ON DELETE CASCADE
);

-- 7. INDICADORES, ALERTAS Y EVALUACIONES
CREATE TABLE indicadores_rendimiento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_atleta INTEGER NOT NULL,
    tipo VARCHAR(35) NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    rango_evaluacion VARCHAR(22) NOT NULL CHECK (rango_evaluacion IN ('EXCELENTE', 'BUENO', 'ACEPTABLE', 'REQUIERE_INTERVENCION')),
    periodo_inicio DATE NOT NULL,
    periodo_fin DATE NOT NULL,
    FOREIGN KEY (id_atleta) REFERENCES atletas(id) ON DELETE CASCADE
);

CREATE TABLE alertas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_atleta INTEGER NOT NULL,
    tipo VARCHAR(25) NOT NULL CHECK (tipo IN ('BAJA_ASISTENCIA', 'OBJETIVO_VENCIDO', 'DISMINUCION_RENDIMIENTO')),
    fecha_generacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(10) NOT NULL CHECK (estado IN ('ACTIVA', 'ATENDIDA', 'EXPIRADA')),
    FOREIGN KEY (id_atleta) REFERENCES atletas(id) ON DELETE CASCADE
);

CREATE TABLE evaluaciones_atleta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_atleta INTEGER NOT NULL,
    id_entrenador INTEGER NOT NULL,
    periodo VARCHAR(10) NOT NULL CHECK (periodo IN ('TORNEO', 'MES', 'MESOCICLO', 'ANIO')),
    referencia_periodo VARCHAR(50) NOT NULL,
    fecha_realizacion DATE NOT NULL,
    fortalezas VARCHAR(500),
    aspectos_por_mejorar VARCHAR(500),
    recomendaciones VARCHAR(500),
    es_autoevaluacion BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (id_atleta) REFERENCES atletas(id) ON DELETE CASCADE,
    FOREIGN KEY (id_entrenador) REFERENCES usuarios(id) ON DELETE CASCADE
);

CREATE TABLE evaluacion_calificaciones_indicador (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_evaluacion INTEGER NOT NULL,
    tipo_indicador VARCHAR(40) NOT NULL,
    calificacion SMALLINT NOT NULL CHECK (calificacion BETWEEN 1 AND 10),
    FOREIGN KEY (id_evaluacion) REFERENCES evaluaciones_atleta(id) ON DELETE CASCADE
);

CREATE TABLE registros_auditoria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario VARCHAR(100) NOT NULL,
    fecha_hora TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    entidad_afectada VARCHAR(50) NOT NULL,
    tipo_operacion VARCHAR(10) NOT NULL CHECK (tipo_operacion IN ('CREAR', 'MODIFICAR', 'ELIMINAR')),
    campo_modificado VARCHAR(50),
    valor_anterior VARCHAR(500),
    valor_nuevo VARCHAR(500)
);

-- 8. ÍNDICES COMPUESTOS
CREATE INDEX idx_atletas_activo ON atletas(activo);
CREATE INDEX idx_partidas_atleta_fecha ON partidas(id_atleta, fecha DESC);
CREATE INDEX idx_partidas_eco ON partidas(apertura_eco);
CREATE INDEX idx_objetivos_atleta_estado ON objetivos_smart(id_atleta, estado);
CREATE INDEX idx_planes_atleta_semana ON planes_entrenamiento(id_atleta, anio, semana);
CREATE INDEX idx_sesiones_plan_estado ON sesiones_entrenamiento(id_plan, estado);
CREATE INDEX idx_asistencias_atleta_fecha ON asistencias(id_atleta, fecha);
CREATE INDEX idx_aperturas_atleta_color ON aperturas_repertorio(id_atleta, color);
CREATE INDEX idx_alertas_estado_atleta ON alertas(estado, id_atleta);
CREATE INDEX idx_auditoria_fecha ON registros_auditoria(fecha_hora DESC);

-- 9. DATOS DE PRUEBA
INSERT INTO usuarios (correo, hash_contrasena, rol) VALUES
('entrenador.magnus@caissa.org', 'pbkdf2:sha256:hash_entrenador_123', 'ENTRENADOR'),
('atleta.kasparov@caissa.org', 'pbkdf2:sha256:hash_atleta_456', 'ATLETA');

INSERT INTO categorias (nombre, tipo, rango, editable_por_admin) VALUES
('Sub-18', 'EDAD', '16-18 años', TRUE),
('Elite FIDE', 'ELO', '2000-2200', TRUE);

INSERT INTO atletas (nombre, fecha_nacimiento, sexo, federacion, rating_clasicas, rating_rapidas, rating_blitz, rating_chess_com, rating_lichess, fecha_actualizacion_rating, activo) VALUES
('Garry Kasparov Jr.', '2008-04-13', 'MASCULINO', 'FIDE', 2150, 2180, 2210, 2300, 2350, '2026-08-01', TRUE);

INSERT INTO atleta_entrenadores (id_atleta, id_entrenador) VALUES (1, 1);
INSERT INTO atleta_categorias (id_atleta, id_categoria) VALUES (1, 1), (1, 2);
INSERT INTO atleta_clubs (id_atleta, club) VALUES (1, 'Club Caissa Central');

INSERT INTO objetivos_smart (id_atleta, titulo, descripcion, indicador_meta, valor_meta, rating_actual, rating_meta, fecha_inicio, fecha_limite, porcentaje_avance, estado, aprobado_por_entrenador, creado_por) VALUES
(1, 'Meta ELO 2200', 'Alcanzar ELO FIDE 2200 en ritmo clásico', 'RATING', 2200.00, 2150, 2200, '2026-08-01', '2026-12-31', 50.00, 'EN_PROCESO', TRUE, 'entrenador.magnus@caissa.org');
