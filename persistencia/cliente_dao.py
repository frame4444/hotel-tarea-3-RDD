from .fabricas import crear_cliente

_SELECT = """
    SELECT c.numero, c.nombre, c.tipo, t.descuento, c.apellidos, c.identificacion,
           c.tipo_identificacion, c.correo, c.telefono, c.direccion
    FROM cliente c JOIN tipo_cliente t ON t.tipo = c.tipo
"""


def _a_objeto(f):
    return crear_cliente(f[2], f[0], f[1], f[3], apellidos=f[4], identificacion=f[5],
                         tipo_identificacion=f[6], correo=f[7], telefono=f[8],
                         direccion=f[9])


def insertar_cliente(cur, cliente):
    """INSERT dentro de una transacción ya abierta (la usa también CuentaDAO).
    Devuelve el cliente con el número que asignó la BD."""
    cur.execute(
        """INSERT INTO cliente (nombre, apellidos, identificacion, tipo_identificacion,
                                correo, telefono, direccion, tipo)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING numero""",
        (cliente.nombre, cliente.apellidos, cliente.identificacion,
         cliente.tipo_identificacion, cliente.correo, cliente.telefono,
         cliente.direccion, cliente.tipo))
    numero = cur.fetchone()[0]
    return crear_cliente(cliente.tipo, numero, cliente.nombre,
                         cliente.porcentaje_descuento(), apellidos=cliente.apellidos,
                         identificacion=cliente.identificacion,
                         tipo_identificacion=cliente.tipo_identificacion,
                         correo=cliente.correo, telefono=cliente.telefono,
                         direccion=cliente.direccion)


class ClienteDAO:
    def __init__(self, conexion):
        self._conn = conexion

    def obtener(self, numero):
        # 'with conexion' confirma (commit) al salir, o deshace (rollback) si hubo error
        with self._conn, self._conn.cursor() as cur:
            cur.execute(_SELECT + " WHERE c.numero = %s", (numero,))
            fila = cur.fetchone()
        return _a_objeto(fila) if fila else None

    def listar(self):
        with self._conn, self._conn.cursor() as cur:
            cur.execute(_SELECT + " ORDER BY c.numero")
            filas = cur.fetchall()
        return [_a_objeto(f) for f in filas]

    def guardar(self, cliente):
        with self._conn, self._conn.cursor() as cur:
            return insertar_cliente(cur, cliente)
