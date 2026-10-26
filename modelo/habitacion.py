from abc import ABC, abstractmethod
from enum import Enum


class Comodidad(Enum):
    FRIGOBAR = "frigobar"
    TV = "tv"
    DVD = "dvd"
    TERRAZA = "terraza"


class Habitacion(ABC):
    """Clase base abstracta de las habitaciones.

    El precio por noche pertenece al TIPO (a la clase), no a cada objeto:
    modificarlo afecta a todas las habitaciones de ese tipo.
    """

    precio_noche = 0.0  # cada subclase define el suyo

    def __init__(self, numero, comodidades=None, camas_matrimoniales=0,
                 camas_individuales=0, banos=1, descripcion="", imagen=""):
        self._numero = numero
        self._comodidades = set(comodidades or [])
        self._camas_matrimoniales = camas_matrimoniales
        self._camas_individuales = camas_individuales
        self._banos = banos
        self._descripcion = descripcion
        self._imagen = imagen  # nombre del archivo de imagen

    @property
    def numero(self):
        return self._numero

    @property
    def comodidades(self):
        return frozenset(self._comodidades)

    @property
    def camas_matrimoniales(self):
        return self._camas_matrimoniales

    @property
    def camas_individuales(self):
        return self._camas_individuales

    @property
    def banos(self):
        return self._banos

    @property
    def descripcion(self):
        return self._descripcion

    @property
    def imagen(self):
        return self._imagen

    @property
    @abstractmethod
    def tipo(self) -> str:
        """Nombre del tipo, p. ej. 'simple'. Cada subclase lo define."""

    def precio_para(self, cliente):
        """Precio por noche para ese cliente (ya con su descuento)."""
        return self.precio_noche * (1 - cliente.porcentaje_descuento() / 100)

    @classmethod
    def modificar_precio(cls, nuevo_precio):
        if nuevo_precio <= 0:
            raise ValueError("El precio debe ser mayor que cero")
        cls.precio_noche = nuevo_precio  # se guarda en la subclase que lo llama

    def __repr__(self):
        return f"<{self.tipo} #{self._numero}>"


class Simple(Habitacion):
    @property
    def tipo(self) -> str:
        return "simple"

    precio_noche = 25000.0


class Doble(Habitacion):
    @property
    def tipo(self) -> str:
        return "doble"

    precio_noche = 40000.0


class Matrimonial(Habitacion):
    @property
    def tipo(self) -> str:
        return "matrimonial"

    precio_noche = 50000.0
