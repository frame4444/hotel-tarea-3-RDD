import os

import psycopg2


def obtener_conexion():
    """Abre una conexión a PostgreSQL. Los datos salen de variables de entorno
    (las mismas que usa psql), con valores por defecto para desarrollo."""
    return psycopg2.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=os.getenv("PGPORT", "5432"),
        dbname=os.getenv("PGDATABASE", "hotel"),
        user=os.getenv("PGUSER", "hotel"),
        password=os.getenv("PGPASSWORD", "hotel"),
    )
