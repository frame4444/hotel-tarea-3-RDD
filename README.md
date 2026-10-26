# Sistema de reservas del hotel (MVC en Python)

Tarea Programa 3 - IC-5821 Requerimientos de Software.
Web sin frameworks + PostgreSQL.
- `pip install -r requirements.txt`

## Arrancar
```bash
createdb hotel                      # o: CREATE DATABASE hotel; desde psql
psql -d hotel -f persistencia/schema.sql
psql -d hotel -f persistencia/datos_iniciales.sql
python main.py                      # abre http://127.0.0.1:8000
```

## Notas
- Quien se registra queda como cliente **habitual** (descuento); quien reserva sin
  iniciar sesión es **esporádico**.
- Las contraseñas se guardan con hash (scrypt). Los datos de la tarjeta solo se
  validan, nunca se guardan.
- Precio por noche y descuento se modifican en las tablas `tipo_habitacion` y
  `tipo_cliente`.
