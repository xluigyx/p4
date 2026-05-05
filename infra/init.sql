-- Tablas Maestras (Distribución y Recintos)
CREATE TABLE recintos (
    codigo_recinto TEXT PRIMARY KEY,
    nombre TEXT,
    municipio TEXT,
    departamento TEXT,
    num_mesas INT
);

-- Event Sourcing: Log de ráfaga de actas para los Bots
CREATE TABLE eventos_actas (
    id SERIAL PRIMARY KEY,
    codigo_acta TEXT,
    fuente TEXT, -- 'OCR', 'SMS', 'CSV'
    datos_json JSONB,
    estado TEXT DEFAULT 'PROCESANDO', -- 'VALIDA', 'OBSERVADA'
    motivo_observacion TEXT,
    creado_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
