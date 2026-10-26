from datetime import timedelta


class Reserva:
    def __init__(self, cliente, habitacion, fecha_inicio, dias, numero=None):
        if dias < 1:
            raise ValueError("La reserva debe ser de al menos 1 día")
        self._numero = numero  # lo asigna la BD si es None
        self._cliente = cliente
        self._habitacion = habitacion
        self._fecha_inicio = fecha_inicio  # datetime.date
        self._dias = dias

    @property
    def numero(self):
        return self._numero

    @property
    def cliente(self):
        return self._cliente

    @property
    def habitacion(self):
        return self._habitacion

    @property
    def fecha_inicio(self):
        return self._fecha_inicio

    @property
    def dias(self):
        return self._dias

    @property
    def fecha_fin(self):
        """Día de salida (la noche de este día ya no se ocupa)."""
        return self._fecha_inicio + timedelta(days=self._dias)

    def se_solapa_con(self, fecha_inicio, dias):
        otro_fin = fecha_inicio + timedelta(days=dias)
        return self._fecha_inicio < otro_fin and fecha_inicio < self.fecha_fin

    def calcular_total(self):
        return self._habitacion.precio_para(self._cliente) * self._dias
