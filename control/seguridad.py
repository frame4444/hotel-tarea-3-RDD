"""Hash de contraseñas con scrypt (biblioteca estándar). Nunca se guarda la clave."""
import hashlib
import hmac
import os

_N, _R, _P = 2 ** 14, 8, 1


def hash_clave(clave):
    sal = os.urandom(16)
    h = hashlib.scrypt(clave.encode(), salt=sal, n=_N, r=_R, p=_P)
    return f"scrypt${sal.hex()}${h.hex()}"


def verificar_clave(clave, almacenado):
    try:
        _, sal, esperado = almacenado.split("$")
        calculado = hashlib.scrypt(clave.encode(), salt=bytes.fromhex(sal),
                                   n=_N, r=_R, p=_P)
    except ValueError:
        return False
    return hmac.compare_digest(calculado.hex(), esperado)
