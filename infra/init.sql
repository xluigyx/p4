-- Esquema Simplificado: Solo almacenamiento de resultados de actas procesadas (RRV)
-- El catálogo maestro (CSV) se gestiona exclusivamente en MongoDB Oficial

CREATE TABLE Transcripciones (
    id SERIAL PRIMARY KEY,
    codigo_acta TEXT, -- Identificador único del acta (limpio)
    candidato TEXT,   -- Lannister, Targaryen, Baratheon, Stark
    votos INT,        -- Cantidad de votos detectados
    creado_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Restricción UNIQUE para evitar duplicados en votos por acta/candidato
ALTER TABLE Transcripciones 
ADD CONSTRAINT unique_voto UNIQUE (codigo_acta, candidato);

-- Tabla de logs para registrar ráfagas de bots y auditoría básica
CREATE TABLE logs_auditoria (
    id SERIAL PRIMARY KEY,
    bot_id TEXT,
    accion TEXT,
    detalles TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
