-- Tablas maestras basadas en el Excel
CREATE TABLE DistribucionTerritorial (
    id SERIAL PRIMARY KEY,
    depto TEXT,
    provincia TEXT,
    municipio TEXT
);

CREATE TABLE RecintosElectorales (
    codigo_recinto TEXT PRIMARY KEY,
    nombre TEXT,
    direccion TEXT,
    distribucion_id INT REFERENCES DistribucionTerritorial(id)
);

CREATE TABLE ActasImpresas (
    codigo_acta TEXT PRIMARY KEY,
    habilitados INT,
    nro_mesa INT,
    codigo_recinto TEXT REFERENCES RecintosElectorales(codigo_recinto)
);

CREATE TABLE Transcripciones (
    id SERIAL PRIMARY KEY,
    codigo_acta TEXT REFERENCES ActasImpresas(codigo_acta),
    candidato TEXT,
    votos INT,
    creado_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Esto crea la restricción de unicidad que el bot necesita para el ON CONFLICT
ALTER TABLE Transcripciones 
ADD CONSTRAINT unique_voto UNIQUE (codigo_acta, candidato);

-- Tabla de logs para registrar ráfagas de bots
CREATE TABLE logs_auditoria (
    id SERIAL PRIMARY KEY,
    bot_id TEXT,
    accion TEXT,
    detalles TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
