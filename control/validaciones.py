import re
from datetime import date

from .errores import DatosInvalidos

TIPOS_IDENTIFICACION = {"cedula": "Cédula", "dimex": "DIMEX", "pasaporte": "Pasaporte"}
_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def texto_requerido(valor, nombre, maximo=100):
    valor = (valor or "").strip()
    if not valor:
        raise DatosInvalidos(f"{nombre} es obligatorio")
    if len(valor) > maximo:
        raise DatosInvalidos(f"{nombre} es demasiado largo")
    return valor


def texto_opcional(valor, maximo=100):
    valor = (valor or "").strip()
    if len(valor) > maximo:
        raise DatosInvalidos("Uno de los textos es demasiado largo")
    return valor


def correo(valor):
    valor = texto_requerido(valor, "El correo electrónico", 150)
    if not _CORREO.match(valor):
        raise DatosInvalidos("El correo electrónico no es válido")
    return valor


def telefono(valor):
    valor = texto_requerido(valor, "El número telefónico", 30)
    if not 8 <= len(re.sub(r"\D", "", valor)) <= 15 or re.search(
        r"[^\d\s+\-()]", valor
    ):
        raise DatosInvalidos("El número telefónico no es válido")
    return valor


def tipo_identificacion(valor):
    if valor not in TIPOS_IDENTIFICACION:
        raise DatosInvalidos("Seleccione un tipo de identificación")
    return valor


def entero(valor, nombre):
    try:
        return int(valor)
    except (TypeError, ValueError):
        raise DatosInvalidos(f"{nombre} no es válido") from None


def fecha_iso(valor, nombre):
    try:
        return date.fromisoformat(valor)
    except (TypeError, ValueError):
        raise DatosInvalidos(f"{nombre} no es válida") from None


def noches_entre(entrada, salida):
    dias = (salida - entrada).days
    if dias < 1:
        raise DatosInvalidos("La salida debe ser posterior a la entrada")
    return dias


def validar_tarjeta(tarjeta, hoy=None):
    """Solo valida el formato. Los datos de la tarjeta NO se guardan en ningún lado."""
    hoy = hoy or date.today()
    texto_requerido(tarjeta.get("nombre"), "El nombre de la tarjeta")
    texto_requerido(tarjeta.get("apellidos"), "Los apellidos de la tarjeta")
    numero = re.sub(r"[\s-]", "", tarjeta.get("numero") or "")
    if not numero.isdigit() or not 13 <= len(numero) <= 19:
        raise DatosInvalidos("El número de tarjeta no es válido")
    try:
        anio, mes = (int(x) for x in (tarjeta.get("vencimiento") or "").split("-"))
        vencida = (mes, anio) < (hoy.month, hoy.year)
        if not 1 <= mes <= 12:
            raise ValueError
    except ValueError:
        raise DatosInvalidos("La fecha de vencimiento no es válida") from None
    if vencida:
        raise DatosInvalidos("La tarjeta está vencida")
    if not re.fullmatch(r"\d{3,4}", (tarjeta.get("codigo") or "").strip()):
        raise DatosInvalidos("El código de seguridad no es válido")
