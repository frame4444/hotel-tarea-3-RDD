-- Esquema del hotel (PostgreSQL 12 o superior)
-- Uso:  psql -h localhost -U hotel -d hotel -f persistencia/schema.sql
DROP TABLE IF EXISTS reserva, cuenta, habitacion_comodidad, habitacion, cliente,
                     tipo_habitacion, tipo_cliente CASCADE;

CREATE EXTENSION IF NOT EXISTS btree_gist;  -- necesaria para la restricción anti-solapamiento

-- El precio es del TIPO de habitación (el administrador lo modifica aquí)
CREATE TABLE tipo_habitacion (
    tipo         VARCHAR(20)   PRIMARY KEY,
    precio_noche NUMERIC(12,2) NOT NULL CHECK (precio_noche > 0)
);

-- El descuento es del TIPO de cliente
CREATE TABLE tipo_cliente (
    tipo      VARCHAR(20)  PRIMARY KEY,
    descuento NUMERIC(5,2) NOT NULL CHECK (descuento BETWEEN 0 AND 100)
);

CREATE TABLE habitacion (
    numero              INTEGER      PRIMARY KEY,
    tipo                VARCHAR(20)  NOT NULL REFERENCES tipo_habitacion(tipo),
    camas_matrimoniales INTEGER      NOT NULL DEFAULT 0 CHECK (camas_matrimoniales >= 0),
    camas_individuales  INTEGER      NOT NULL DEFAULT 0 CHECK (camas_individuales >= 0),
    banos               INTEGER      NOT NULL DEFAULT 1 CHECK (banos >= 0),
    descripcion         TEXT         NOT NULL DEFAULT '',
    imagen              VARCHAR(100) NOT NULL DEFAULT ''
);

CREATE TABLE habitacion_comodidad (
    numero_habitacion INTEGER     NOT NULL REFERENCES habitacion(numero) ON DELETE CASCADE,
    comodidad         VARCHAR(20) NOT NULL CHECK (comodidad IN ('frigobar', 'tv', 'dvd', 'terraza')),
    PRIMARY KEY (numero_habitacion, comodidad)
);

CREATE TABLE cliente (
    numero              SERIAL       PRIMARY KEY,
    nombre              VARCHAR(100) NOT NULL,
    apellidos           VARCHAR(100) NOT NULL DEFAULT '',
    identificacion      VARCHAR(30)  NOT NULL DEFAULT '',
    tipo_identificacion VARCHAR(20)  NOT NULL DEFAULT ''
                        CHECK (tipo_identificacion IN ('', 'cedula', 'dimex', 'pasaporte')),
    correo              VARCHAR(150) NOT NULL DEFAULT '',
    telefono            VARCHAR(30)  NOT NULL DEFAULT '',
    direccion           TEXT         NOT NULL DEFAULT '',
    tipo                VARCHAR(20)  NOT NULL REFERENCES tipo_cliente(tipo)
);

-- Solo los clientes registrados (habituales) tienen cuenta. La contraseña se
-- guarda como hash, nunca en texto plano.
CREATE TABLE cuenta (
    correo         VARCHAR(150) PRIMARY KEY,
    clave_hash     TEXT         NOT NULL,
    numero_cliente INTEGER      NOT NULL UNIQUE REFERENCES cliente(numero)
);

CREATE TABLE reserva (
    numero            SERIAL  PRIMARY KEY,
    numero_cliente    INTEGER NOT NULL REFERENCES cliente(numero),
    numero_habitacion INTEGER NOT NULL REFERENCES habitacion(numero),
    fecha_inicio      DATE    NOT NULL,
    dias              INTEGER NOT NULL CHECK (dias >= 1),
    fecha_fin         DATE    GENERATED ALWAYS AS (fecha_inicio + dias) STORED,
    -- La propia BD impide dos reservas de la misma habitación con fechas que se pisan
    EXCLUDE USING gist (
        numero_habitacion WITH =,
        daterange(fecha_inicio, fecha_fin, '[)') WITH &&
    )
);
