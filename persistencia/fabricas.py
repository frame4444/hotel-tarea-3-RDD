"""Traduce el texto guardado en la BD ('doble', 'habitual') a la clase del modelo.

Para agregar un tipo nuevo: crear la subclase en modelo/, agregarla a estos
diccionarios e insertar una fila en tipo_habitacion o tipo_cliente.
"""
from modelo import Comodidad, Doble, Esporadico, Habitual, Matrimonial, Simple

TIPOS_HABITACION = {"simple": Simple, "doble": Doble, "matrimonial": Matrimonial}
TIPOS_CLIENTE = {"habitual": Habitual, "esporadico": Esporadico}


def crear_habitacion(tipo, numero, comodidades, precio_noche, **detalles):
    if tipo not in TIPOS_HABITACION:
        raise ValueError(f"Tipo de habitación desconocido en la BD: {tipo}")
    clase = TIPOS_HABITACION[tipo]
    clase.modificar_precio(float(precio_noche))  # el precio vigente es el de la BD
    return clase(numero, [Comodidad(c) for c in comodidades], **detalles)


def crear_cliente(tipo, numero, nombre, descuento, **datos):
    if tipo not in TIPOS_CLIENTE:
        raise ValueError(f"Tipo de cliente desconocido en la BD: {tipo}")
    clase = TIPOS_CLIENTE[tipo]
    if hasattr(clase, "modificar_descuento"):
        clase.modificar_descuento(float(descuento))  # el descuento vigente es el de la BD
    return clase(numero, nombre, **datos)
