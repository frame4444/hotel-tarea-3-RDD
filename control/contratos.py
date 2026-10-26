"""Lo que el controlador espera de la capa de persistencia.

Son Protocols: cualquier clase que tenga estos métodos los cumple, sin necesidad
de heredar de nada. Los DAO de PostgreSQL los implementan.
"""
from typing import Optional, Protocol

from modelo import Cliente, Habitacion, Reserva


class ClienteRepo(Protocol):
    def obtener(self, numero: int) -> Optional[Cliente]: ...
    def listar(self) -> list[Cliente]: ...
    def guardar(self, cliente: Cliente) -> Cliente:
        """Guarda y devuelve el cliente ya con el número asignado por la BD."""
        ...


class CuentaRepo(Protocol):
    def registrar(self, cliente: Cliente, correo: str, clave_hash: str) -> Cliente:
        """Crea cliente y cuenta juntos. Lanza CorreoYaRegistrado si el correo existe."""
        ...
    def obtener_credenciales(self, correo: str) -> Optional[tuple]:
        """(clave_hash, numero_cliente) o None."""
        ...


class HabitacionRepo(Protocol):
    def obtener(self, numero: int) -> Optional[Habitacion]: ...
    def listar(self, tipo: Optional[str] = None) -> list[Habitacion]: ...


class ReservaRepo(Protocol):
    def listar_por_habitacion(self, numero_habitacion: int) -> list[Reserva]: ...
    def guardar(self, reserva: Reserva) -> Reserva:
        """Guarda y devuelve la reserva ya con el número asignado por la BD.
        Lanza ReservaSolapada si la habitación ya está ocupada en ese período."""
        ...
