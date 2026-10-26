from datetime import date
from typing import Optional

from modelo import Esporadico, Habitacion, Reserva, ReservaSolapada

from . import validaciones as v
from .contratos import ClienteRepo, HabitacionRepo, ReservaRepo
from .errores import (
    ClienteNoEncontrado,
    DatosInvalidos,
    HabitacionNoDisponible,
    HabitacionNoEncontrada,
)


class ControladorReserva:
    """Caso de uso: reservar una habitación para un cliente."""

    def __init__(self, clientes: ClienteRepo, habitaciones: HabitacionRepo,
                 reservas: ReservaRepo):
        # Los repositorios llegan desde afuera (main.py los crea). Así el
        # controlador no sabe si hay PostgreSQL o una lista en memoria.
        self._clientes = clientes
        self._habitaciones = habitaciones
        self._reservas = reservas

    # ---- consultas que usa la vista ----
    def listar_clientes(self):
        return self._clientes.listar()

    def listar_habitaciones(self, tipo: Optional[str] = None) -> list[Habitacion]:
        return self._habitaciones.listar(tipo)

    def tipos_habitacion(self) -> list[str]:
        return sorted({h.tipo for h in self._habitaciones.listar()})

    def obtener_habitacion(self, numero: int) -> Habitacion:
        habitacion = self._habitaciones.obtener(numero)
        if habitacion is None:
            raise HabitacionNoEncontrada(f"No existe la habitación {numero}")
        return habitacion

    def habitaciones_disponibles(self, tipo: Optional[str], fecha_inicio: date,
                                 dias: int) -> list[Habitacion]:
        self._validar_periodo(fecha_inicio, dias)
        return [h for h in self._habitaciones.listar(tipo)
                if self._esta_libre(h, fecha_inicio, dias)]

    def cotizar(self, numero_cliente: Optional[int], numero_habitacion: int,
                dias: Optional[int] = None):
        """(precio por noche, total) para ese cliente. Sin cliente (visitante)
        no hay descuento. El total es None si no se indican los días."""
        habitacion = self.obtener_habitacion(numero_habitacion)
        if numero_cliente is None:
            cliente = Esporadico(None, "")
        else:
            cliente = self._clientes.obtener(numero_cliente)
            if cliente is None:
                raise ClienteNoEncontrado(f"No existe el cliente {numero_cliente}")
        precio = habitacion.precio_para(cliente)
        return precio, (precio * dias if dias else None)

    def precio_total(self, numero_cliente: int, numero_habitacion: int,
                     fecha_inicio: date, dias: int) -> float:
        """Calcula el precio sin guardar nada."""
        return self._armar_reserva(numero_cliente, numero_habitacion,
                                   fecha_inicio, dias).calcular_total()

    # ---- el caso de uso ----
    def reservar(self, numero_cliente: int, numero_habitacion: int,
                 fecha_inicio: date, dias: int) -> Reserva:
        reserva = self._armar_reserva(numero_cliente, numero_habitacion,
                                      fecha_inicio, dias)
        if not self._esta_libre(reserva.habitacion, fecha_inicio, dias):
            raise HabitacionNoDisponible(
                f"La habitación {numero_habitacion} no está disponible en esas fechas")
        try:
            return self._reservas.guardar(reserva)
        except ReservaSolapada as e:
            # Otra persona reservó entre la verificación y el guardado
            raise HabitacionNoDisponible(
                f"La habitación {numero_habitacion} acaba de ser reservada") from e

    def reservar_con_cuenta(self, numero_cliente: int, tarjeta: dict,
                            numero_habitacion: int, fecha_inicio: date, dias: int):
        """Cliente habitual (con sesión iniciada): solo falta la tarjeta."""
        v.validar_tarjeta(tarjeta)
        return self.reservar(numero_cliente, numero_habitacion, fecha_inicio, dias)

    def reservar_como_visitante(self, datos: dict, tarjeta: dict, numero_habitacion: int,
                                fecha_inicio: date, dias: int):
        """Cliente esporádico: llena todos sus datos y se guarda como cliente."""
        self._validar_periodo(fecha_inicio, dias)
        direccion = ", ".join(p for p in (
            v.texto_opcional(datos.get("direccion"), 200),
            v.texto_opcional(datos.get("ciudad")),
            v.texto_opcional(datos.get("provincia")),
            v.texto_opcional(datos.get("pais")),
            v.texto_opcional(datos.get("codigo_postal"), 20)) if p)
        visitante = Esporadico(
            None,
            v.texto_requerido(datos.get("nombre"), "El nombre"),
            v.texto_requerido(datos.get("apellidos"), "Los apellidos"),
            v.texto_requerido(datos.get("identificacion"), "La identificación", 30),
            v.tipo_identificacion(datos.get("tipo_identificacion")),
            v.correo(datos.get("correo")),
            v.telefono(datos.get("telefono")),
            direccion,
        )
        v.validar_tarjeta(tarjeta)
        habitacion = self.obtener_habitacion(numero_habitacion)
        if not self._esta_libre(habitacion, fecha_inicio, dias):
            raise HabitacionNoDisponible(
                f"La habitación {numero_habitacion} no está disponible en esas fechas")
        visitante = self._clientes.guardar(visitante)
        return self.reservar(visitante.numero, numero_habitacion, fecha_inicio, dias)

    # ---- auxiliares privados ----
    def _armar_reserva(self, numero_cliente, numero_habitacion, fecha_inicio, dias):
        self._validar_periodo(fecha_inicio, dias)
        cliente = self._clientes.obtener(numero_cliente)
        if cliente is None:
            raise ClienteNoEncontrado(f"No existe el cliente {numero_cliente}")
        habitacion = self.obtener_habitacion(numero_habitacion)
        return Reserva(cliente, habitacion, fecha_inicio, dias)

    def _esta_libre(self, habitacion: Habitacion, fecha_inicio: date, dias: int) -> bool:
        existentes = self._reservas.listar_por_habitacion(habitacion.numero)
        return not any(r.se_solapa_con(fecha_inicio, dias) for r in existentes)

    @staticmethod
    def _validar_periodo(fecha_inicio, dias):
        if not isinstance(fecha_inicio, date):
            raise DatosInvalidos("La fecha de inicio no es válida")
        if not isinstance(dias, int) or dias < 1:
            raise DatosInvalidos("Los días deben ser un entero mayor o igual a 1")
        if fecha_inicio < date.today():
            raise DatosInvalidos("La fecha de inicio no puede estar en el pasado")
