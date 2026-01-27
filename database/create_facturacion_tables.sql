-- =====================================================
-- VetCare Pro - Script de Creación de Tablas de Facturación
-- Base de Datos: SQL Server
-- =====================================================

USE VetCare_Pro;
GO

-- =====================================================
-- Tabla: SERVICIOS
-- Catálogo de servicios ofrecidos por la veterinaria
-- =====================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'servicios')
BEGIN
    CREATE TABLE servicios (
        id_servicio INT IDENTITY(1,1) PRIMARY KEY,
        codigo VARCHAR(20) NOT NULL UNIQUE,
        nombre VARCHAR(100) NOT NULL,
        descripcion TEXT,
        categoria VARCHAR(50) DEFAULT 'Otro',
        precio DECIMAL(10,2) NOT NULL,
        duracion_minutos INT,
        activo BIT DEFAULT 1,
        fecha_creacion DATETIME DEFAULT GETDATE(),
        fecha_actualizacion DATETIME DEFAULT GETDATE()
    );

    -- Índices
    CREATE INDEX IX_servicios_codigo ON servicios(codigo);
    CREATE INDEX IX_servicios_categoria ON servicios(categoria);
    CREATE INDEX IX_servicios_activo ON servicios(activo);

    PRINT 'Tabla SERVICIOS creada exitosamente';
END
GO

-- =====================================================
-- Tabla: FACTURAS
-- Facturas emitidas a los clientes
-- =====================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'facturas')
BEGIN
    CREATE TABLE facturas (
        id_factura INT IDENTITY(1,1) PRIMARY KEY,
        numero_factura VARCHAR(20) NOT NULL UNIQUE,
        id_propietario INT NOT NULL,
        id_mascota INT,
        id_consulta INT,

        fecha_emision DATETIME NOT NULL DEFAULT GETDATE(),
        fecha_vencimiento DATE,

        subtotal DECIMAL(10,2) DEFAULT 0,
        descuento DECIMAL(10,2) DEFAULT 0,
        igv DECIMAL(10,2) DEFAULT 0,
        total DECIMAL(10,2) DEFAULT 0,

        estado VARCHAR(20) NOT NULL DEFAULT 'Pendiente',
        metodo_pago VARCHAR(30),
        fecha_pago DATETIME,
        monto_pagado DECIMAL(10,2) DEFAULT 0,

        observaciones TEXT,

        -- Trazabilidad
        id_usuario_registro INT,
        fecha_creacion DATETIME DEFAULT GETDATE(),

        -- Foreign Keys
        CONSTRAINT FK_facturas_propietario FOREIGN KEY (id_propietario)
            REFERENCES propietarios(id_propietario),
        CONSTRAINT FK_facturas_mascota FOREIGN KEY (id_mascota)
            REFERENCES mascotas(id_mascota),
        CONSTRAINT FK_facturas_consulta FOREIGN KEY (id_consulta)
            REFERENCES consultas(id_consulta),
        CONSTRAINT FK_facturas_usuario FOREIGN KEY (id_usuario_registro)
            REFERENCES usuarios(id_usuario),

        -- Check Constraints
        CONSTRAINT CK_facturas_estado CHECK (estado IN ('Pendiente', 'Pagada', 'Pago Parcial', 'Anulada')),
        CONSTRAINT CK_facturas_metodo_pago CHECK (metodo_pago IS NULL OR metodo_pago IN ('Efectivo', 'Tarjeta', 'Transferencia', 'Yape/Plin', 'Otro'))
    );

    -- Índices
    CREATE INDEX IX_facturas_numero ON facturas(numero_factura);
    CREATE INDEX IX_facturas_propietario ON facturas(id_propietario);
    CREATE INDEX IX_facturas_estado ON facturas(estado);
    CREATE INDEX IX_facturas_fecha ON facturas(fecha_emision);

    PRINT 'Tabla FACTURAS creada exitosamente';
END
GO

-- =====================================================
-- Tabla: DETALLES_FACTURA
-- Líneas de detalle de cada factura
-- =====================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'detalles_factura')
BEGIN
    CREATE TABLE detalles_factura (
        id_detalle INT IDENTITY(1,1) PRIMARY KEY,
        id_factura INT NOT NULL,
        id_servicio INT,

        descripcion VARCHAR(200) NOT NULL,
        cantidad INT DEFAULT 1,
        precio_unitario DECIMAL(10,2) NOT NULL,
        descuento DECIMAL(10,2) DEFAULT 0,
        subtotal DECIMAL(10,2) NOT NULL,

        -- Foreign Keys
        CONSTRAINT FK_detalles_factura FOREIGN KEY (id_factura)
            REFERENCES facturas(id_factura) ON DELETE CASCADE,
        CONSTRAINT FK_detalles_servicio FOREIGN KEY (id_servicio)
            REFERENCES servicios(id_servicio)
    );

    -- Índices
    CREATE INDEX IX_detalles_factura ON detalles_factura(id_factura);
    CREATE INDEX IX_detalles_servicio ON detalles_factura(id_servicio);

    PRINT 'Tabla DETALLES_FACTURA creada exitosamente';
END
GO

-- =====================================================
-- Datos Iniciales: Servicios Básicos
-- =====================================================
IF NOT EXISTS (SELECT 1 FROM servicios)
BEGIN
    INSERT INTO servicios (codigo, nombre, descripcion, categoria, precio, duracion_minutos) VALUES
    -- Consultas
    ('SRV-0001', 'Consulta General', 'Consulta médica veterinaria general', 'Consulta', 50.00, 30),
    ('SRV-0002', 'Consulta de Emergencia', 'Atención de emergencia las 24 horas', 'Emergencia', 100.00, 45),
    ('SRV-0003', 'Consulta Especializada', 'Consulta con veterinario especialista', 'Consulta', 80.00, 45),

    -- Vacunación
    ('SRV-0004', 'Vacuna Antirrábica', 'Aplicación de vacuna contra la rabia', 'Vacunación', 35.00, 15),
    ('SRV-0005', 'Vacuna Múltiple Canina', 'Vacuna polivalente para perros', 'Vacunación', 45.00, 15),
    ('SRV-0006', 'Vacuna Triple Felina', 'Vacuna triple para gatos', 'Vacunación', 40.00, 15),

    -- Cirugías
    ('SRV-0007', 'Esterilización Canina (Macho)', 'Castración de perro', 'Cirugía', 150.00, 60),
    ('SRV-0008', 'Esterilización Canina (Hembra)', 'Ovariohisterectomía de perra', 'Cirugía', 200.00, 90),
    ('SRV-0009', 'Esterilización Felina (Macho)', 'Castración de gato', 'Cirugía', 100.00, 45),
    ('SRV-0010', 'Esterilización Felina (Hembra)', 'Ovariohisterectomía de gata', 'Cirugía', 150.00, 60),
    ('SRV-0011', 'Cirugía Menor', 'Procedimientos quirúrgicos menores', 'Cirugía', 120.00, 45),

    -- Laboratorio
    ('SRV-0012', 'Hemograma Completo', 'Análisis de sangre completo', 'Laboratorio', 40.00, 30),
    ('SRV-0013', 'Perfil Bioquímico', 'Análisis bioquímico sanguíneo', 'Laboratorio', 60.00, 30),
    ('SRV-0014', 'Examen de Orina', 'Urianálisis completo', 'Laboratorio', 25.00, 15),
    ('SRV-0015', 'Examen Coprológico', 'Análisis de heces', 'Laboratorio', 20.00, 15),

    -- Estética
    ('SRV-0016', 'Baño Canino Pequeño', 'Baño para perros pequeños (hasta 10kg)', 'Estética', 25.00, 45),
    ('SRV-0017', 'Baño Canino Mediano', 'Baño para perros medianos (10-25kg)', 'Estética', 35.00, 60),
    ('SRV-0018', 'Baño Canino Grande', 'Baño para perros grandes (más de 25kg)', 'Estética', 50.00, 90),
    ('SRV-0019', 'Corte de Uñas', 'Corte y limado de uñas', 'Estética', 15.00, 15),
    ('SRV-0020', 'Limpieza de Oídos', 'Limpieza y revisión de oídos', 'Estética', 20.00, 15),

    -- Hospitalización
    ('SRV-0021', 'Hospitalización (por día)', 'Internamiento con monitoreo', 'Hospitalización', 80.00, NULL),
    ('SRV-0022', 'Hospitalización UCI (por día)', 'Cuidados intensivos', 'Hospitalización', 150.00, NULL),

    -- Otros
    ('SRV-0023', 'Desparasitación Interna', 'Aplicación de antiparasitario interno', 'Otro', 20.00, 10),
    ('SRV-0024', 'Desparasitación Externa', 'Aplicación de antiparasitario externo', 'Otro', 25.00, 15),
    ('SRV-0025', 'Microchip', 'Implantación de microchip de identificación', 'Otro', 50.00, 15);

    PRINT 'Datos iniciales de SERVICIOS insertados exitosamente';
END
GO

PRINT '=====================================================';
PRINT 'Módulo de Facturación instalado exitosamente';
PRINT '=====================================================';
GO
