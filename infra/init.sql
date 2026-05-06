-- Tablas maestras basadas en el Excel
CREATE TABLE DistribucionTerritorial (
    codigo_territorial TEXT PRIMARY KEY, -- Usamos codigo_territorial como PK para mayor consistencia
    depto TEXT,
    provincia TEXT,
    municipio TEXT
);

CREATE TABLE RecintosElectorales (
    codigo_recinto TEXT PRIMARY KEY,
    nombre TEXT,
    direccion TEXT,
    codigo_territorial TEXT REFERENCES DistribucionTerritorial(codigo_territorial)
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

-- Restricción UNIQUE para evitar duplicados en votos por acta/candidato
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
