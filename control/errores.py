class ErrorControl(Exception):
    """Base de todos los errores que el controlador comunica a la vista.
    La vista captura esta clase y muestra str(error) al usuario."""


class DatosInvalidos(ErrorControl):
    pass


class ErrorReserva(ErrorControl):
    pass


class ClienteNoEncontrado(ErrorReserva):
    pass


class HabitacionNoEncontrada(ErrorReserva):
    pass


class HabitacionNoDisponible(ErrorReserva):
    pass


class CorreoEnUso(ErrorControl):
    pass


class CredencialesInvalidas(ErrorControl):
    pass
