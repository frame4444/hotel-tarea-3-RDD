import psycopg2.errors

from modelo import CorreoYaRegistrado

from .cliente_dao import insertar_cliente


class CuentaDAO:
    def __init__(self, conexion):
        self._conn = conexion

    def registrar(self, cliente, correo, clave_hash):
        """Crea el cliente y su cuenta en UNA sola transacción: o se guardan
        los dos o no se guarda ninguno."""
        try:
            with self._conn, self._conn.cursor() as cur:
                nuevo = insertar_cliente(cur, cliente)
                cur.execute(
                    """INSERT INTO cuenta (correo, clave_hash, numero_cliente)
                       VALUES (%s, %s, %s)""",
                    (correo.strip().lower(), clave_hash, nuevo.numero))
        except psycopg2.errors.UniqueViolation as e:
            raise CorreoYaRegistrado("Ya existe una cuenta con ese correo") from e
        return nuevo

    def obtener_credenciales(self, correo):
        """Devuelve (clave_hash, numero_cliente) o None si el correo no existe."""
        with self._conn, self._conn.cursor() as cur:
            cur.execute("SELECT clave_hash, numero_cliente FROM cuenta WHERE correo = %s",
                        (correo.strip().lower(),))
            return cur.fetchone()
