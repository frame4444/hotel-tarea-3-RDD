from abc import ABC, abstractmethod


class Cliente(ABC):
    """Clase base abstracta de los clientes."""

    def __init__(self, numero, nombre, apellidos="", identificacion="",
                 tipo_identificacion="", correo="", telefono="", direccion=""):
        self._numero = numero
        self._nombre = nombre
        self._apellidos = apellidos
        self._identificacion = identificacion
        self._tipo_identificacion = tipo_identificacion
        self._correo = correo
        self._telefono = telefono
        self._direccion = direccion

    @property
    def numero(self):
        return self._numero

    @property
    def nombre(self):
        return self._nombre

    @property
    def apellidos(self):
        return self._apellidos

    @property
    def nombre_completo(self):
        return f"{self._nombre} {self._apellidos}".strip()

    @property
    def identificacion(self):
        return self._identificacion

    @property
    def tipo_identificacion(self):
        return self._tipo_identificacion

    @property
    def correo(self):
        return self._correo

    @property
    def telefono(self):
        return self._telefono

    @property
    def direccion(self):
        return self._direccion

    @property
    @abstractmethod
    def tipo(self) -> str:
        """'habitual', 'esporadico', ..."""

    @abstractmethod
    def porcentaje_descuento(self) -> float:
        """Descuento (0-100) que recibe este tipo de cliente."""

    def __repr__(self):
        return f"<{self.tipo} {self._nombre}>"


class Habitual(Cliente):
    @property
    def tipo(self) -> str:
        return "habitual"

    descuento = 10.0  # compartido por todos los habituales

    def porcentaje_descuento(self) -> float:
        return Habitual.descuento

    @classmethod
    def modificar_descuento(cls, nuevo):
        if not 0 <= nuevo <= 100:
            raise ValueError("El descuento debe estar entre 0 y 100")
        cls.descuento = nuevo


class Esporadico(Cliente):
    @property
    def tipo(self) -> str:
        return "esporadico"

    def porcentaje_descuento(self) -> float:
        return 0.0
