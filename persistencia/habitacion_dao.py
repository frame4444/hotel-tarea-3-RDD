from .fabricas import crear_habitacion

_SELECT = """
    SELECT h.numero, h.tipo, t.precio_noche,
           COALESCE(array_agg(c.comodidad) FILTER (WHERE c.comodidad IS NOT NULL),
                    ARRAY[]::varchar[]),
           h.camas_matrimoniales, h.camas_individuales, h.banos, h.descripcion, h.imagen
    FROM habitacion h
    JOIN tipo_habitacion t ON t.tipo = h.tipo
    LEFT JOIN habitacion_comodidad c ON c.numero_habitacion = h.numero
"""
_GROUP = " GROUP BY h.numero, h.tipo, t.precio_noche ORDER BY h.numero"


class HabitacionDAO:
    def __init__(self, conexion):
        self._conn = conexion

    def obtener(self, numero):
        with self._conn, self._conn.cursor() as cur:
            cur.execute(_SELECT + " WHERE h.numero = %s" + _GROUP, (numero,))
            fila = cur.fetchone()
        return self._a_objeto(fila) if fila else None

    def listar(self, tipo=None):
        with self._conn, self._conn.cursor() as cur:
            if tipo is None:
                cur.execute(_SELECT + _GROUP)
            else:
                cur.execute(_SELECT + " WHERE h.tipo = %s" + _GROUP, (tipo,))
            filas = cur.fetchall()
        return [self._a_objeto(f) for f in filas]

    @staticmethod
    def _a_objeto(fila):
        numero, tipo, precio, comodidades, c_matrim, c_indiv, banos, desc, imagen = fila
        return crear_habitacion(tipo, numero, comodidades, precio,
                                camas_matrimoniales=c_matrim, camas_individuales=c_indiv,
                                banos=banos, descripcion=desc, imagen=imagen)
