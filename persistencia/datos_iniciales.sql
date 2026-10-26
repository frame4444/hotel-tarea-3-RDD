-- Datos de prueba. Los precios son de relleno: ajústelos.
INSERT INTO tipo_habitacion (tipo, precio_noche) VALUES
    ('simple', 25000), ('doble', 40000), ('matrimonial', 50000);

INSERT INTO tipo_cliente (tipo, descuento) VALUES
    ('habitual', 10), ('esporadico', 0);

INSERT INTO habitacion (numero, tipo, camas_matrimoniales, camas_individuales, banos,
                        descripcion, imagen) VALUES
    (101, 'simple', 0, 1, 1, 'Habitación sencilla y tranquila, ideal para una persona.', 'simple.svg'),
    (102, 'simple', 0, 1, 1, 'Habitación sencilla con frigobar, ideal para una persona.', 'simple.svg'),
    (201, 'doble', 0, 2, 1, 'Dos camas individuales, perfecta para amigos o familia.', 'doble.svg'),
    (202, 'doble', 0, 2, 1, 'Dos camas individuales con frigobar.', 'doble.svg'),
    (301, 'matrimonial', 1, 0, 1, 'Cama matrimonial con todas las comodidades.', 'matrimonial.svg'),
    (302, 'matrimonial', 1, 0, 2, 'Cama matrimonial, dos baños y terraza privada.', 'matrimonial_terraza.svg');

INSERT INTO habitacion_comodidad (numero_habitacion, comodidad) VALUES
    (101, 'tv'), (102, 'tv'), (102, 'frigobar'),
    (201, 'tv'), (201, 'dvd'), (202, 'tv'), (202, 'frigobar'),
    (301, 'tv'), (301, 'dvd'), (301, 'frigobar'),
    (302, 'tv'), (302, 'frigobar'), (302, 'terraza');

INSERT INTO cliente (nombre, apellidos, identificacion, tipo_identificacion, correo, telefono, tipo) VALUES
    ('Ana', 'Rojas', '1-1111-1111', 'cedula', 'ana@correo.com', '88888888', 'habitual'),
    ('Luis', 'Mora', '2-2222-2222', 'cedula', 'luis@correo.com', '87777777', 'esporadico');
