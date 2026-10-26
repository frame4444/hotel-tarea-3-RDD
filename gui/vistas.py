"""Vista: arma el HTML a partir de las plantillas. No contiene lógica de negocio."""

import html
from pathlib import Path
from string import Template
from urllib.parse import quote

from control.validaciones import TIPOS_IDENTIFICACION

_DIR = Path(__file__).parent / "plantillas"
_PLANTILLAS = {
    p.stem: Template(p.read_text(encoding="utf-8")) for p in _DIR.glob("*.html")
}

_COMODIDADES = {"tv": "TV", "dvd": "DVD", "frigobar": "Frigobar", "terraza": "Terraza"}
ACTIVIDADES = [
    ("SPA", "Masajes, relajación", "spa.svg"),
    ("Restaurante", "Buffet", "restaurante.svg"),
    ("Playas", "Nombre de playa ficticia", "playas.svg"),
    ("Bar", "Para toda la familia hasta las 9:00pm", "bar.svg"),
]


# ---------- utilidades ----------
def e(valor):
    """Escapa texto para HTML (evita inyección de código en la página)."""
    return html.escape("" if valor is None else str(valor), quote=True)


def dinero(valor):
    return f"₡{valor:,.0f}"


def _plural(n, uno, varios):
    return f"{n} {uno if n == 1 else varios}"


def _render(plantilla, /, **valores):
    return _PLANTILLAS[plantilla].substitute(valores)


def _li(textos):
    return "".join(f"<li>{e(t)}</li>" for t in textos) or "<li>Ninguno</li>"


def _comodidades(h):
    presentes = {c.value for c in h.comodidades}
    return [nombre for clave, nombre in _COMODIDADES.items() if clave in presentes]


def _titulo(h):
    return f"Habitación {h.tipo.capitalize()} #{h.numero}"


def _resumen(h):
    partes = []
    if h.camas_matrimoniales:
        partes.append(
            _plural(h.camas_matrimoniales, "cama matrimonial", "camas matrimoniales")
        )
    if h.camas_individuales:
        partes.append(
            _plural(h.camas_individuales, "cama individual", "camas individuales")
        )
    partes.append(_plural(h.banos, "baño", "baños"))
    return ", ".join(partes + _comodidades(h))


def _detalles(h):
    return _li(
        [
            f"Camas matrimoniales: {h.camas_matrimoniales}",
            f"Camas individuales: {h.camas_individuales}",
            f"Baños: {h.banos}",
        ]
    )


def _precio(h, cliente=None):
    if cliente is not None and cliente.porcentaje_descuento() > 0:
        return (
            f"<s>{dinero(h.precio_noche)}</s> <strong>{dinero(h.precio_para(cliente))}</strong>"
            f" <small>(descuento de {cliente.porcentaje_descuento():g}%)</small>"
        )
    return f"<strong>{dinero(h.precio_noche)}</strong>"


def _imagen(nombre, alt):
    return f'<img src="/estaticos/img/{e(nombre)}" alt="{e(alt)}" width="384" height="228">'


def _opciones_tipos(seleccionado=""):
    opciones = ['<option value="">Tipo de identificación</option>']
    for clave, nombre in TIPOS_IDENTIFICACION.items():
        sel = " selected" if clave == seleccionado else ""
        opciones.append(f'<option value="{clave}"{sel}>{e(nombre)}</option>')
    return "".join(opciones)


def _campo(
    valores, nombre, etiqueta, tipo="text", clase="", requerido=True, atributos=""
):
    req = " required" if requerido else ""
    return (
        f'<label class="campo {clase}">{e(etiqueta)}'
        f'<input type="{tipo}" name="{nombre}" value="{e(valores.get(nombre, ""))}"'
        f' placeholder="{e(etiqueta)}"{req} {atributos}></label>'
    )


# ---------- página base ----------
def pagina(titulo, contenido, izquierda="", cliente=None, error="", ruta="/"):
    if cliente is None:
        sig = quote(ruta, safe="")
        acciones = (
            f'<a class="boton" href="/registro?siguiente={sig}">Registrarse</a>'
            f'<a class="boton" href="/login?siguiente={sig}">Iniciar Sesión</a>'
        )
    else:
        acciones = (
            f"<span>Hola, {e(cliente.nombre)}</span>"
            '<form method="post" action="/salir"><button class="boton">Cerrar Sesión</button></form>'
        )
    aviso = f'<div class="mensaje error" role="alert">{e(error)}</div>' if error else ""
    return _render(
        "base",
        titulo=e(titulo),
        izquierda=izquierda,
        acciones=acciones,
        mensaje=aviso,
        contenido=contenido,
    ).encode("utf-8")


def error_pagina(titulo, mensaje, cliente=None, ruta="/"):
    cuerpo = f'<h1>{e(titulo)}</h1><p>{e(mensaje)}</p><p><a class="boton" href="/">Volver al inicio</a></p>'
    return pagina(titulo, cuerpo, cliente=cliente, ruta=ruta)


# ---------- pantallas ----------
def principal(habitaciones, tipos, tipo_sel, cliente, ruta):
    tarjetas = (
        "".join(
            f'<a class="tarjeta" href="/habitacion?numero={h.numero}">{_imagen(h.imagen, _titulo(h))}'
            f"<strong>{e(_titulo(h))}</strong><span>{e(_resumen(h))}</span>"
            f"<em>{_precio(h, cliente)} / noche</em></a>"
            for h in habitaciones
        )
        or "<p>No hay habitaciones de ese tipo.</p>"
    )
    actividades = "".join(
        f'<div class="tarjeta">{_imagen(img, nombre)}<strong>{e(nombre)}</strong><span>{e(desc)}</span></div>'
        for nombre, desc, img in ACTIVIDADES
    )
    opciones = '<option value="">Filtrar: todas</option>' + "".join(
        f'<option value="{e(t)}"{" selected" if t == tipo_sel else ""}>{e(t.capitalize())}</option>'
        for t in tipos
    )
    izquierda = (
        '<h2>Habitaciones</h2><form method="get" action="/">'
        f'<select name="tipo" data-auto>{opciones}</select>'
        '<noscript><button class="boton">Filtrar</button></noscript></form>'
    )
    cuerpo = _render("principal", habitaciones=tarjetas, actividades=actividades)
    return pagina("Inicio", cuerpo, izquierda, cliente, ruta=ruta)


def detalle(h, cliente, ruta):
    cuerpo = _render(
        "detalle",
        galeria=_imagen(h.imagen, _titulo(h)) * 4,
        detalles=_detalles(h),
        extras=_li(_comodidades(h)),
        descripcion=e(h.descripcion),
        precio=_precio(h, cliente),
        numero=h.numero,
    )
    return pagina(_titulo(h), cuerpo, f"<h1>{e(_titulo(h))}</h1>", cliente, ruta=ruta)


def _tarjeta_form(v):
    return (
        '<h3>Información de tarjeta</h3><div class="fila">'
        + _campo(v, "tarjeta_nombre", "Nombre")
        + _campo(v, "tarjeta_apellidos", "Apellidos")
        + _campo(
            {},
            "tarjeta_numero",
            "Número de tarjeta",
            clase="ancho",
            atributos='inputmode="numeric" autocomplete="off"',
        )
        + _campo(v, "tarjeta_vencimiento", "Vencimiento (yyyy-mm)", tipo="month")
        + _campo(
            {},
            "tarjeta_codigo",
            "Código",
            tipo="password",
            atributos='inputmode="numeric" autocomplete="off"',
        )
        + '</div><p class="nota">No almacenamos datos bancarios.</p>'
    )


def _panel_visitante(v, ruta):
    def c(*a, **k):
        return _campo(v, *a, **k)

    return (
        '<h3>Información Personal</h3><div class="fila">'
        + c("nombre", "Nombre")
        + c("apellidos", "Apellidos")
        + c("identificacion", "Identificación")
        + '<label class="campo">Tipo de identificación<select name="tipo_identificacion">'
        + _opciones_tipos(v.get("tipo_identificacion", ""))
        + "</select></label></div>"
        '<h3>Contacto</h3><div class="fila">'
        + c("correo", "Correo electrónico", tipo="email")
        + c("telefono", "Número telefónico", tipo="tel")
        + '</div><h3>Dirección</h3><div class="fila">'
        + c("pais", "País", requerido=False)
        + c("provincia", "Estado/Provincia", requerido=False)
        + c("ciudad", "Ciudad/Cantón", requerido=False)
        + c("codigo_postal", "Código postal", requerido=False)
        + c("direccion", "Dirección específica", clase="ancho", requerido=False)
        + "</div>"
        + _tarjeta_form(v)
        + f'<p class="nota"><a href="/login?siguiente={quote(ruta, safe="")}">¿Iniciar sesión?</a>'
        " - Aplican descuentos</p>"
    )


def _panel_habitual(cliente, v):
    tipo_id = TIPOS_IDENTIFICACION.get(cliente.tipo_identificacion, "")
    return (
        '<h3>Información Personal</h3><dl class="datos">'
        f"<dt>Nombre</dt><dd>{e(cliente.nombre_completo)}</dd>"
        f"<dt>Identificación</dt><dd>{e(tipo_id)} {e(cliente.identificacion)}</dd>"
        f"<dt>Contacto</dt><dd>{e(cliente.correo)} &nbsp; {e(cliente.telefono)}</dd>"
        f"<dt>Dirección</dt><dd>{e(cliente.direccion or 'No registrada')}</dd></dl>"
        + _tarjeta_form(v)
    )


def reserva(
    h, cliente, valores, entrada, salida, disponibles, cotizacion, hoy, error, ruta
):
    lista = [h] if disponibles is None else disponibles
    opciones = (
        "".join(
            f'<option value="{x.numero}"{" selected" if x.numero == h.numero else ""}>{e(_titulo(x))}</option>'
            for x in lista
        )
        or '<option value="">Sin habitaciones disponibles</option>'
    )
    if cotizacion:
        dias, precio, total = cotizacion
        resumen = (
            f"{_plural(dias, 'noche', 'noches')}<br>Precio/Noche: {dinero(precio)}"
            f"<br><strong>Total: {dinero(total)}</strong>"
        )
    else:
        resumen = f"Precio/Noche<br>{_precio(h, cliente)}"
    panel = (
        _panel_visitante(valores, ruta)
        if cliente is None
        else _panel_habitual(cliente, valores)
    )
    cuerpo = _render(
        "reserva",
        detalles=_detalles(h),
        extras=_li(_comodidades(h)),
        descripcion=e(h.descripcion),
        panel=panel,
        hoy=hoy,
        entrada=e(entrada),
        salida=e(salida),
        opciones=opciones,
        resumen=resumen,
    )
    return pagina(
        f"Reservar {_titulo(h)}",
        cuerpo,
        f"<h1>{e(_titulo(h))}</h1>",
        cliente,
        error,
        ruta,
    )


def registro(valores, siguiente, error=""):
    return pagina(
        "Registro",
        _render(
            "registro",
            siguiente=e(siguiente),
            correo=e(valores.get("correo")),
            nombre=e(valores.get("nombre")),
            apellidos=e(valores.get("apellidos")),
            identificacion=e(valores.get("identificacion")),
            telefono=e(valores.get("telefono")),
            tipos=_opciones_tipos(valores.get("tipo_identificacion", "")),
        ),
        error=error,
    )


def login(valores, siguiente, error=""):
    return pagina(
        "Iniciar sesión",
        _render(
            "login",
            siguiente=e(siguiente),
            siguiente_url=quote(siguiente, safe=""),
            correo=e(valores.get("correo")),
        ),
        error=error,
    )


def confirmacion(r, cliente):
    filas = [
        ("Número de reserva", r.numero),
        ("Habitación", _titulo(r.habitacion)),
        ("Cliente", r.cliente.nombre_completo),
        ("Entrada", r.fecha_inicio.strftime("%d/%m/%Y")),
        ("Salida", r.fecha_fin.strftime("%d/%m/%Y")),
        ("Noches", r.dias),
    ]
    if r.cliente.porcentaje_descuento() > 0:
        filas.append(
            ("Descuento", f"{r.cliente.porcentaje_descuento():g}% (cliente habitual)")
        )
    filas.append(("Total", dinero(r.calcular_total())))
    datos = "".join(f"<dt>{e(k)}</dt><dd>{e(val)}</dd>" for k, val in filas)
    return pagina(
        "Reserva confirmada", _render("confirmacion", datos=datos), cliente=cliente
    )
