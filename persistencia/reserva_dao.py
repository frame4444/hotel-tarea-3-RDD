import psycopg2.errors

from modelo import Reserva, ReservaSolapada


class ReservaDAO:
    def __init__(self, conexion, cliente_dao, habitacion_dao):
        # Necesita los otros DAO para reconstruir los objetos Cliente y Habitacion
        self._conn = conexion
        self._clientes = cliente_dao
        self._habitaciones = habitacion_dao

    def listar_por_habitacion(self, numero_habitacion):
        habitacion = self._habitaciones.obtener(numero_habitacion)
        if habitacion is None:
            return []
        with self._conn, self._conn.cursor() as cur:
            cur.execute(
                """SELECT numero, numero_cliente, fecha_inicio, dias
                   FROM reserva WHERE numero_habitacion = %s ORDER BY fecha_inicio""",
                (numero_habitacion,))
            filas = cur.fetchall()
        return [Reserva(self._clientes.obtener(f[1]), habitacion, f[2], f[3], numero=f[0])
                for f in filas]

    def guardar(self, reserva):
        try:
            with self._conn, self._conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO reserva (numero_cliente, numero_habitacion,
                                            fecha_inicio, dias)
                       VALUES (%s, %s, %s, %s) RETURNING numero""",
                    (reserva.cliente.numero, reserva.habitacion.numero,
                     reserva.fecha_inicio, reserva.dias))
                numero = cur.fetchone()[0]
        except psycopg2.errors.ExclusionViolation as e:
            raise ReservaSolapada("La habitación ya está reservada en esas fechas") from e
        return Reserva(reserva.cliente, reserva.habitacion, reserva.fecha_inicio,
                       reserva.dias, numero=numero)
