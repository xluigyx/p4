-- Event Sourcing Schema para Actas
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tablas maestras
CREATE TABLE IF NOT EXISTS departamentos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS recintos (
    id SERIAL PRIMARY KEY,
    departamento_id INT REFERENCES departamentos(id),
    nombre VARCHAR(255) NOT NULL,
    abstencion_estimada DECIMAL DEFAULT 0.0
);

-- Tabla de Eventos inmutables (Event Sourcing)
CREATE TABLE IF NOT EXISTS acta_events (
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    acta_id VARCHAR(50) NOT NULL,
    recinto_id INT REFERENCES recintos(id),
    event_type VARCHAR(50) NOT NULL, -- e.g., 'ACTA_PROCESADA', 'ERROR_OCR', 'ERROR_VALIDACION'
    payload JSONB NOT NULL,          -- Contiene votos: {"p1": 100, "p2": 50, ...} o log de errores
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Proyecciones (Vista materializada o tabla actualizada por workers para lectura rápida - CQRS)
CREATE TABLE IF NOT EXISTS acta_projections (
    acta_id VARCHAR(50) PRIMARY KEY,
    recinto_id INT REFERENCES recintos(id),
    votos_p1 INT DEFAULT 0,
    votos_p2 INT DEFAULT 0,
    votos_p3 INT DEFAULT 0,
    votos_p4 INT DEFAULT 0,
    votos_validos INT DEFAULT 0,
    votos_blancos INT DEFAULT 0,
    votos_nulos INT DEFAULT 0,
    estado VARCHAR(50) NOT NULL, -- 'VALIDADA', 'INCONSISTENCIA_ARITMETICA', 'CONFLICTO_ANFORA', 'ACTA_DAÑADA'
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indices para alta concurrencia
CREATE INDEX idx_acta_events_acta_id ON acta_events(acta_id);
CREATE INDEX idx_projections_estado ON acta_projections(estado);
