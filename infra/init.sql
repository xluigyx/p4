-- Tablas maestras basadas en el Excel
CREATE TABLE distribucion (depto TEXT, provincia TEXT, municipio TEXT);
CREATE TABLE recintos (codigo_recinto TEXT PRIMARY KEY, nombre TEXT, direccion TEXT);
CREATE TABLE actas_impresas (codigo_acta TEXT PRIMARY KEY, habilitados INT, nro_mesa INT);

-- Registro de eventos (Event Sourcing) para auditoría
CREATE TABLE logs_procesamiento (
    id SERIAL PRIMARY KEY,
    codigo_acta TEXT,
    fuente TEXT, -- 'OCR' o 'CSV'
    estado TEXT, -- 'ACEPTADA', 'RECHAZADA'
    motivo_rechazo TEXT, -- 'MANCHADA', 'ROTA', 'ERROR_SUMA'
    creado_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
