-- ============================================
-- VetCare Pro - Script de Base de Datos
-- Sistema de Gestión de Veterinaria
-- SQL Server 2019+
-- VERSIÓN 2.0 - Con relaciones de Usuarios
-- ============================================

-- Crear la base de datos
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'VetCareDB')
BEGIN
    CREATE DATABASE VetCareDB;
END
GO

USE VetCareDB;
GO

-- ============================================
-- TABLA: Usuarios (PRIMERO - porque otros dependen de ella)
-- ============================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'usuarios')
BEGIN
    CREATE TABLE usuarios (
        id_usuario INT IDENTITY(1,1) PRIMARY KEY,
        username VARCHAR(50) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        nombre_completo VARCHAR(100) NOT NULL,
        email VARCHAR(100) NOT NULL UNIQUE,
        rol VARCHAR(20) NOT NULL DEFAULT 'Recepcionista'
            CHECK (rol IN ('Administrador', 'Veterinario', 'Recepcionista')),
        activo BIT NOT NULL DEFAULT 1,
        fecha_creacion DATETIME NOT NULL DEFAULT GETDATE(),
        ultimo_acceso DATETIME
    );
    
    CREATE INDEX idx_usuarios_username ON usuarios(username);
    CREATE INDEX idx_usuarios_email ON usuarios(email);
    CREATE INDEX idx_usuarios_rol ON usuarios(rol);
END
GO

-- ============================================
-- TABLA: Especies
-- ============================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'especies')
BEGIN
    CREATE TABLE especies (
        id_especie INT IDENTITY(1,1) PRIMARY KEY,
        nombre VARCHAR(50) NOT NULL UNIQUE,
        descripcion VARCHAR(200),
        activo BIT NOT NULL DEFAULT 1
    );
    
    -- Datos iniciales
    INSERT INTO especies (nombre, descripcion) VALUES 
    ('Perro', 'Canis lupus familiaris'),
    ('Gato', 'Felis catus'),
    ('Ave', 'Aves domésticas'),
    ('Conejo', 'Oryctolagus cuniculus'),
    ('Hámster', 'Cricetinae'),
    ('Pez', 'Peces ornamentales'),
    ('Tortuga', 'Testudines'),
    ('Otro', 'Otras especies');
END
GO

-- ============================================
-- TABLA: Propietarios
-- ============================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'propietarios')
BEGIN
    CREATE TABLE propietarios (
        id_propietario INT IDENTITY(1,1) PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL,
        documento VARCHAR(20) NOT NULL UNIQUE,
        telefono VARCHAR(20) NOT NULL,
        email VARCHAR(100),
        direccion VARCHAR(200),
        fecha_registro DATETIME NOT NULL DEFAULT GETDATE(),
        activo BIT NOT NULL DEFAULT 1
    );
    
    CREATE INDEX idx_propietarios_documento ON propietarios(documento);
    CREATE INDEX idx_propietarios_nombre ON propietarios(nombre);
END
GO

-- ============================================
-- TABLA: Veterinarios (CON RELACIÓN A USUARIOS)
-- ============================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'veterinarios')
BEGIN
    CREATE TABLE veterinarios (
        id_veterinario INT IDENTITY(1,1) PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL,
        colegiatura VARCHAR(20) NOT NULL UNIQUE,
        especialidad VARCHAR(100),
        telefono VARCHAR(20),
        email VARCHAR(100),
        activo BIT NOT NULL DEFAULT 1,
        
        -- *** RELACIÓN CON USUARIO (1:1) ***
        id_usuario INT NULL UNIQUE,
        
        CONSTRAINT FK_veterinarios_usuario FOREIGN KEY (id_usuario) 
            REFERENCES usuarios(id_usuario)
    );
    
    CREATE INDEX idx_veterinarios_usuario ON veterinarios(id_usuario);
    
    -- Veterinario de ejemplo
    INSERT INTO veterinarios (nombre, colegiatura, especialidad, telefono) VALUES 
    ('Dr. Juan García López', 'CMVP-12345', 'Medicina General', '999888777');
END
GO

-- ============================================
-- TABLA: Mascotas
-- ============================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'mascotas')
BEGIN
    CREATE TABLE mascotas (
        id_mascota INT IDENTITY(1,1) PRIMARY KEY,
        id_propietario INT NOT NULL,
        id_especie INT NOT NULL,
        nombre VARCHAR(50) NOT NULL,
        raza VARCHAR(50),
        fecha_nacimiento DATE,
        sexo CHAR(1) CHECK (sexo IN ('M', 'H')),
        peso DECIMAL(5,2),
        color VARCHAR(30),
        observaciones TEXT,
        foto_url VARCHAR(255),
        activo BIT NOT NULL DEFAULT 1,
        
        CONSTRAINT FK_mascotas_propietario FOREIGN KEY (id_propietario) 
            REFERENCES propietarios(id_propietario),
        CONSTRAINT FK_mascotas_especie FOREIGN KEY (id_especie) 
            REFERENCES especies(id_especie)
    );
    
    CREATE INDEX idx_mascotas_propietario ON mascotas(id_propietario);
    CREATE INDEX idx_mascotas_especie ON mascotas(id_especie);
END
GO

-- ============================================
-- TABLA: Consultas (CON TRAZABILIDAD DE USUARIO)
-- ============================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'consultas')
BEGIN
    CREATE TABLE consultas (
        id_consulta INT IDENTITY(1,1) PRIMARY KEY,
        id_mascota INT NOT NULL,
        id_veterinario INT NOT NULL,
        fecha_hora DATETIME NOT NULL,
        motivo VARCHAR(200) NOT NULL,
        diagnostico TEXT,
        peso_actual DECIMAL(5,2),
        temperatura DECIMAL(4,1),
        estado VARCHAR(20) NOT NULL DEFAULT 'Programada' 
            CHECK (estado IN ('Programada', 'En Curso', 'Completada', 'Cancelada')),
        observaciones TEXT,
        costo DECIMAL(10,2),
        fecha_creacion DATETIME NOT NULL DEFAULT GETDATE(),
        
        -- *** TRAZABILIDAD: Usuario que registró la consulta ***
        id_usuario_registro INT NULL,
        
        CONSTRAINT FK_consultas_mascota FOREIGN KEY (id_mascota) 
            REFERENCES mascotas(id_mascota),
        CONSTRAINT FK_consultas_veterinario FOREIGN KEY (id_veterinario) 
            REFERENCES veterinarios(id_veterinario),
        CONSTRAINT FK_consultas_usuario FOREIGN KEY (id_usuario_registro) 
            REFERENCES usuarios(id_usuario)
    );
    
    CREATE INDEX idx_consultas_mascota ON consultas(id_mascota);
    CREATE INDEX idx_consultas_veterinario ON consultas(id_veterinario);
    CREATE INDEX idx_consultas_fecha ON consultas(fecha_hora);
    CREATE INDEX idx_consultas_estado ON consultas(estado);
    CREATE INDEX idx_consultas_usuario ON consultas(id_usuario_registro);
END
GO

-- ============================================
-- TABLA: Tratamientos
-- ============================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'tratamientos')
BEGIN
    CREATE TABLE tratamientos (
        id_tratamiento INT IDENTITY(1,1) PRIMARY KEY,
        id_consulta INT NOT NULL,
        descripcion VARCHAR(200) NOT NULL,
        medicamento VARCHAR(100),
        dosis VARCHAR(100),
        duracion_dias INT,
        indicaciones TEXT,
        costo DECIMAL(10,2),
        fecha_inicio DATE DEFAULT GETDATE(),
        fecha_fin DATE,
        estado VARCHAR(20) NOT NULL DEFAULT 'Activo'
            CHECK (estado IN ('Activo', 'Completado', 'Suspendido')),
        
        CONSTRAINT FK_tratamientos_consulta FOREIGN KEY (id_consulta) 
            REFERENCES consultas(id_consulta)
    );
    
    CREATE INDEX idx_tratamientos_consulta ON tratamientos(id_consulta);
END
GO

-- ============================================
-- TABLA: Vacunas
-- ============================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'vacunas')
BEGIN
    CREATE TABLE vacunas (
        id_vacuna INT IDENTITY(1,1) PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL,
        descripcion VARCHAR(200),
        intervalo_dias INT NOT NULL DEFAULT 365,
        id_especie INT,
        dosis_requeridas INT DEFAULT 1,
        edad_minima_dias INT,
        activo BIT NOT NULL DEFAULT 1,
        
        CONSTRAINT FK_vacunas_especie FOREIGN KEY (id_especie) 
            REFERENCES especies(id_especie)
    );
    
    -- Vacunas comunes para perros (id_especie = 1)
    INSERT INTO vacunas (nombre, descripcion, intervalo_dias, id_especie) VALUES 
    ('Rabia', 'Vacuna antirrábica', 365, 1),
    ('Parvovirus', 'Previene parvovirosis canina', 365, 1),
    ('Moquillo', 'Previene distemper canino', 365, 1),
    ('Hepatitis', 'Hepatitis infecciosa canina', 365, 1),
    ('Leptospirosis', 'Previene leptospirosis', 365, 1),
    ('Polivalente', 'Vacuna múltiple canina', 365, 1);
    
    -- Vacunas comunes para gatos (id_especie = 2)
    INSERT INTO vacunas (nombre, descripcion, intervalo_dias, id_especie) VALUES 
    ('Rabia Felina', 'Vacuna antirrábica felina', 365, 2),
    ('Triple Felina', 'Panleucopenia, Rinotraqueitis, Calicivirus', 365, 2),
    ('Leucemia Felina', 'Previene leucemia viral felina', 365, 2);
END
GO

-- ============================================
-- TABLA: Calendario de Vacunación (CON TRAZABILIDAD)
-- ============================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'calendario_vacunacion')
BEGIN
    CREATE TABLE calendario_vacunacion (
        id_calendario INT IDENTITY(1,1) PRIMARY KEY,
        id_mascota INT NOT NULL,
        id_vacuna INT NOT NULL,
        fecha_programada DATE NOT NULL,
        fecha_aplicacion DATE,
        fecha_proxima DATE,
        dosis_numero INT DEFAULT 1,
        estado VARCHAR(20) NOT NULL DEFAULT 'Pendiente'
            CHECK (estado IN ('Pendiente', 'Aplicada', 'Vencida', 'Cancelada')),
        recordatorio_enviado BIT NOT NULL DEFAULT 0,
        observaciones VARCHAR(200),
        lote_vacuna VARCHAR(50),
        
        -- Veterinario que aplicó la vacuna
        id_veterinario INT,
        
        -- *** TRAZABILIDAD: Usuario que registró/programó ***
        id_usuario_registro INT NULL,
        fecha_registro DATETIME DEFAULT GETDATE(),
        
        CONSTRAINT FK_calendario_mascota FOREIGN KEY (id_mascota) 
            REFERENCES mascotas(id_mascota),
        CONSTRAINT FK_calendario_vacuna FOREIGN KEY (id_vacuna) 
            REFERENCES vacunas(id_vacuna),
        CONSTRAINT FK_calendario_veterinario FOREIGN KEY (id_veterinario) 
            REFERENCES veterinarios(id_veterinario),
        CONSTRAINT FK_calendario_usuario FOREIGN KEY (id_usuario_registro) 
            REFERENCES usuarios(id_usuario)
    );
    
    CREATE INDEX idx_calendario_mascota ON calendario_vacunacion(id_mascota);
    CREATE INDEX idx_calendario_fecha ON calendario_vacunacion(fecha_programada);
    CREATE INDEX idx_calendario_estado ON calendario_vacunacion(estado);
    CREATE INDEX idx_calendario_usuario ON calendario_vacunacion(id_usuario_registro);
END
GO

-- ============================================
-- VISTAS ÚTILES
-- ============================================

-- Vista: Mascotas con información completa
IF EXISTS (SELECT * FROM sys.views WHERE name = 'vw_mascotas_completo')
    DROP VIEW vw_mascotas_completo;
GO

CREATE VIEW vw_mascotas_completo AS
SELECT 
    m.id_mascota,
    m.nombre AS mascota_nombre,
    m.raza,
    m.fecha_nacimiento,
    m.sexo,
    m.peso,
    m.color,
    e.nombre AS especie,
    p.nombre AS propietario,
    p.telefono AS propietario_telefono,
    p.email AS propietario_email,
    DATEDIFF(YEAR, m.fecha_nacimiento, GETDATE()) AS edad_anos
FROM mascotas m
INNER JOIN especies e ON m.id_especie = e.id_especie
INNER JOIN propietarios p ON m.id_propietario = p.id_propietario
WHERE m.activo = 1;
GO

-- Vista: Consultas del día con trazabilidad
IF EXISTS (SELECT * FROM sys.views WHERE name = 'vw_consultas_hoy')
    DROP VIEW vw_consultas_hoy;
GO

CREATE VIEW vw_consultas_hoy AS
SELECT 
    c.id_consulta,
    c.fecha_hora,
    c.motivo,
    c.estado,
    m.nombre AS mascota,
    e.nombre AS especie,
    p.nombre AS propietario,
    p.telefono,
    v.nombre AS veterinario,
    u.nombre_completo AS registrado_por  -- *** TRAZABILIDAD ***
FROM consultas c
INNER JOIN mascotas m ON c.id_mascota = m.id_mascota
INNER JOIN especies e ON m.id_especie = e.id_especie
INNER JOIN propietarios p ON m.id_propietario = p.id_propietario
INNER JOIN veterinarios v ON c.id_veterinario = v.id_veterinario
LEFT JOIN usuarios u ON c.id_usuario_registro = u.id_usuario  -- *** TRAZABILIDAD ***
WHERE CAST(c.fecha_hora AS DATE) = CAST(GETDATE() AS DATE);
GO

-- Vista: Vacunaciones próximas con trazabilidad
IF EXISTS (SELECT * FROM sys.views WHERE name = 'vw_vacunaciones_proximas')
    DROP VIEW vw_vacunaciones_proximas;
GO

CREATE VIEW vw_vacunaciones_proximas AS
SELECT 
    cv.id_calendario,
    cv.fecha_programada,
    cv.estado,
    m.nombre AS mascota,
    e.nombre AS especie,
    p.nombre AS propietario,
    p.telefono,
    p.email,
    v.nombre AS vacuna,
    u.nombre_completo AS programado_por  -- *** TRAZABILIDAD ***
FROM calendario_vacunacion cv
INNER JOIN mascotas m ON cv.id_mascota = m.id_mascota
INNER JOIN especies e ON m.id_especie = e.id_especie
INNER JOIN propietarios p ON m.id_propietario = p.id_propietario
INNER JOIN vacunas v ON cv.id_vacuna = v.id_vacuna
LEFT JOIN usuarios u ON cv.id_usuario_registro = u.id_usuario  -- *** TRAZABILIDAD ***
WHERE cv.estado = 'Pendiente'
  AND cv.fecha_programada BETWEEN GETDATE() AND DATEADD(DAY, 7, GETDATE());
GO

-- *** NUEVA VISTA: Usuarios con sus roles y veterinarios asociados ***
IF EXISTS (SELECT * FROM sys.views WHERE name = 'vw_usuarios_detalle')
    DROP VIEW vw_usuarios_detalle;
GO

CREATE VIEW vw_usuarios_detalle AS
SELECT 
    u.id_usuario,
    u.username,
    u.nombre_completo,
    u.email,
    u.rol,
    u.activo,
    u.fecha_creacion,
    u.ultimo_acceso,
    v.id_veterinario,
    v.nombre AS veterinario_nombre,
    v.colegiatura,
    v.especialidad
FROM usuarios u
LEFT JOIN veterinarios v ON u.id_usuario = v.id_usuario;
GO

-- ============================================
-- PROCEDIMIENTOS ALMACENADOS
-- ============================================

-- SP: Actualizar vacunaciones vencidas
IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'sp_actualizar_vacunaciones_vencidas')
    DROP PROCEDURE sp_actualizar_vacunaciones_vencidas;
GO

CREATE PROCEDURE sp_actualizar_vacunaciones_vencidas
AS
BEGIN
    UPDATE calendario_vacunacion
    SET estado = 'Vencida'
    WHERE estado = 'Pendiente'
      AND fecha_programada < CAST(GETDATE() AS DATE);
    
    SELECT @@ROWCOUNT AS registros_actualizados;
END
GO

-- SP: Reporte de consultas por período
IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'sp_reporte_consultas_periodo')
    DROP PROCEDURE sp_reporte_consultas_periodo;
GO

CREATE PROCEDURE sp_reporte_consultas_periodo
    @fecha_inicio DATE,
    @fecha_fin DATE
AS
BEGIN
    SELECT 
        CAST(c.fecha_hora AS DATE) AS fecha,
        COUNT(*) AS total_consultas,
        SUM(CASE WHEN c.estado = 'Completada' THEN 1 ELSE 0 END) AS completadas,
        SUM(CASE WHEN c.estado = 'Cancelada' THEN 1 ELSE 0 END) AS canceladas,
        SUM(ISNULL(c.costo, 0)) AS ingresos_totales
    FROM consultas c
    WHERE c.fecha_hora >= @fecha_inicio 
      AND c.fecha_hora < DATEADD(DAY, 1, @fecha_fin)
    GROUP BY CAST(c.fecha_hora AS DATE)
    ORDER BY fecha;
END
GO

-- *** NUEVO SP: Reporte de actividad por usuario ***
IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'sp_reporte_actividad_usuario')
    DROP PROCEDURE sp_reporte_actividad_usuario;
GO

CREATE PROCEDURE sp_reporte_actividad_usuario
    @id_usuario INT,
    @fecha_inicio DATE,
    @fecha_fin DATE
AS
BEGIN
    -- Consultas registradas
    SELECT 
        'Consultas Registradas' AS tipo,
        COUNT(*) AS total
    FROM consultas
    WHERE id_usuario_registro = @id_usuario
      AND fecha_creacion >= @fecha_inicio
      AND fecha_creacion < DATEADD(DAY, 1, @fecha_fin)
    
    UNION ALL
    
    -- Vacunaciones programadas
    SELECT 
        'Vacunaciones Programadas' AS tipo,
        COUNT(*) AS total
    FROM calendario_vacunacion
    WHERE id_usuario_registro = @id_usuario
      AND fecha_registro >= @fecha_inicio
      AND fecha_registro < DATEADD(DAY, 1, @fecha_fin);
END
GO

-- *** NUEVO SP: Vincular veterinario con usuario ***
IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'sp_vincular_veterinario_usuario')
    DROP PROCEDURE sp_vincular_veterinario_usuario;
GO

CREATE PROCEDURE sp_vincular_veterinario_usuario
    @id_veterinario INT,
    @id_usuario INT
AS
BEGIN
    -- Verificar que el usuario tenga rol de Veterinario
    IF NOT EXISTS (SELECT 1 FROM usuarios WHERE id_usuario = @id_usuario AND rol = 'Veterinario')
    BEGIN
        RAISERROR('El usuario debe tener rol de Veterinario', 16, 1);
        RETURN;
    END
    
    -- Verificar que el veterinario no tenga ya un usuario
    IF EXISTS (SELECT 1 FROM veterinarios WHERE id_veterinario = @id_veterinario AND id_usuario IS NOT NULL)
    BEGIN
        RAISERROR('El veterinario ya tiene un usuario asignado', 16, 1);
        RETURN;
    END
    
    -- Vincular
    UPDATE veterinarios
    SET id_usuario = @id_usuario
    WHERE id_veterinario = @id_veterinario;
    
    SELECT 'Vinculación exitosa' AS resultado;
END
GO

PRINT '============================================';
PRINT 'VetCareDB v2.0 creada exitosamente';
PRINT 'Incluye relaciones de trazabilidad de usuarios';
PRINT '============================================';
GO
