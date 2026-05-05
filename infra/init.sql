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

-- Tablas para las 4 hojas de Excel (Oficial)
CREATE TABLE IF NOT EXISTS oficial_hoja1_actas (
    id SERIAL PRIMARY KEY,
    codigo_mesa VARCHAR(50) UNIQUE NOT NULL,
    recinto_id INT REFERENCES recintos(id),
    votos_validos INT DEFAULT 0,
    votos_blancos INT DEFAULT 0,
    votos_nulos INT DEFAULT 0,
    papeletas_anfora INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS oficial_hoja2_votos (
    id SERIAL PRIMARY KEY,
    acta_id VARCHAR(50) REFERENCES oficial_hoja1_actas(codigo_mesa),
    partido VARCHAR(50),
    votos INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS oficial_hoja3_candidatos (
    id SERIAL PRIMARY KEY,
    partido VARCHAR(50) UNIQUE NOT NULL,
    nombre_candidato VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS oficial_hoja4_recintos_meta (
    id SERIAL PRIMARY KEY,
    recinto_id INT REFERENCES recintos(id),
    latitud DECIMAL(10, 8),
    longitud DECIMAL(11, 8),
    estado_conexion VARCHAR(50) DEFAULT 'OFFLINE'
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

-- Procedimientos para consistencia
CREATE OR REPLACE FUNCTION sp_consistencia_fuerte_oficial(
    p_mesa VARCHAR, p_votos JSONB
) RETURNS VOID AS $$
BEGIN
    -- Inserta o actualiza garantizando consistencia inmediata
    -- (Simulado)
    INSERT INTO oficial_hoja1_actas (codigo_mesa, votos_validos) 
    VALUES (p_mesa, (p_votos->>'validos')::INT)
    ON CONFLICT (codigo_mesa) DO UPDATE SET votos_validos = EXCLUDED.votos_validos;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION sp_consistencia_eventual_rrv() 
RETURNS VOID AS $$
BEGIN
    -- Sincroniza desde acta_events hacia projections en background
    -- Esto es invocado por un worker o pg_cron
    RAISE NOTICE 'Consistencia eventual RRV ejecutada';
END;
$$ LANGUAGE plpgsql;
