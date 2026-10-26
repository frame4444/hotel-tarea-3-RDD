from modelo import CorreoYaRegistrado, Habitual

from . import validaciones as v
from .contratos import ClienteRepo, CuentaRepo
from .errores import CorreoEnUso, CredencialesInvalidas, DatosInvalidos
from .seguridad import hash_clave, verificar_clave

_HASH_FALSO = hash_clave(
    "clave-de-relleno"
)  # para que un correo inexistente tarde igual


class ControladorCuenta:
    """Registro e inicio de sesión. Quien se registra queda como cliente habitual."""

    def __init__(self, cuentas: CuentaRepo, clientes: ClienteRepo):
        self._cuentas = cuentas
        self._clientes = clientes

    def registrar(
        self,
        nombre,
        apellidos,
        tipo_identificacion,
        identificacion,
        telefono,
        correo,
        clave,
        confirmacion,
    ):
        cliente = Habitual(
            None,
            v.texto_requerido(nombre, "El nombre"),
            v.texto_requerido(apellidos, "Los apellidos"),
            v.texto_requerido(identificacion, "La identificación", 30),
            v.tipo_identificacion(tipo_identificacion),
            v.correo(correo),
            v.telefono(telefono),
        )
        clave = clave or ""
        if len(clave) < 8:
            raise DatosInvalidos("La contraseña debe tener al menos 8 caracteres")
        if clave != confirmacion:
            raise DatosInvalidos("Las contraseñas no coinciden")
        try:
            return self._cuentas.registrar(cliente, cliente.correo, hash_clave(clave))
        except CorreoYaRegistrado as e:
            raise CorreoEnUso("Ya existe una cuenta con ese correo") from e

    def iniciar_sesion(self, correo, clave):
        credenciales = self._cuentas.obtener_credenciales(correo or "")
        almacenado = credenciales[0] if credenciales else _HASH_FALSO
        correcta = verificar_clave(clave or "", almacenado)
        cliente = self._clientes.obtener(credenciales[1]) if credenciales else None
        if not correcta or cliente is None:
            raise CredencialesInvalidas("Correo o contraseña incorrectos")
        return cliente

    def obtener_cliente(self, numero):
        return self._clientes.obtener(numero)
