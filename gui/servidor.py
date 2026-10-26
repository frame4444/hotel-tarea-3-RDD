"""Servidor web con la biblioteca estándar (sin frameworks).

Esta capa solo traduce HTTP: lee la petición, llama al controlador y devuelve el HTML
que arma vistas.py. Ninguna regla de negocio vive aquí.
"""
import secrets
import traceback
from datetime import date
from http import cookies
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlparse

from control import DatosInvalidos, ErrorControl, HabitacionNoEncontrada
from control.validaciones import entero, fecha_iso, noches_entre

from . import vistas

ESTATICOS = (Path(__file__).parent / "estaticos").resolve()
TIPOS_MIME = {".css": "text/css; charset=utf-8", ".js": "text/javascript; charset=utf-8",
              ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg"}
MAX_FORMULARIO = 20_000  # bytes


def _destino_seguro(ruta):
    """Solo rutas internas: evita redirecciones a otros sitios o inyectar cabeceras."""
    if ruta and ruta.startswith("/") and not ruta.startswith("//") and "\\" not in ruta:
        return quote(ruta, safe="/?=&%:")
    return "/"


class _Aplicacion:
    def __init__(self, reserva, cuenta):
        self.reserva = reserva
        self.cuenta = cuenta
        self.sesiones = {}        # token -> número de cliente
        self.confirmaciones = {}  # token -> Reserva recién hecha

    def guardar_confirmacion(self, reserva):
        token = secrets.token_urlsafe(16)
        self.confirmaciones[token] = reserva
        if len(self.confirmaciones) > 200:
            self.confirmaciones.pop(next(iter(self.confirmaciones)))
        return token


class Manejador(BaseHTTPRequestHandler):
    app = None  # lo asigna crear_servidor

    # ---------- despacho ----------
    def do_GET(self):
        self._despachar("GET")

    def do_POST(self):
        self._despachar("POST")

    def _despachar(self, metodo):
        url = urlparse(self.path)
        self.ruta = url.path + (f"?{url.query}" if url.query else "")
        self.consulta = {k: v[0] for k, v in parse_qs(url.query).items()}
        self.cliente = None
        try:
            self.form = self._leer_formulario() if metodo == "POST" else {}
            self.cliente = self._cliente_actual()
            if metodo == "GET" and url.path.startswith("/estaticos/"):
                return self._estatico(url.path[len("/estaticos/"):])
            nombre = RUTAS.get((metodo, url.path))
            if nombre is None:
                return self._error(404, "Página no encontrada", "La página que busca no existe.")
            getattr(self, nombre)()
        except HabitacionNoEncontrada as ex:
            self._error(404, "No encontrado", str(ex))
        except ErrorControl as ex:
            self._error(400, "Solicitud no válida", str(ex))
        except Exception:
            traceback.print_exc()
            self._error(500, "Error del servidor", "Ocurrió un problema. Intente de nuevo.")

    # ---------- utilidades HTTP ----------
    def _leer_formulario(self):
        try:
            largo = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            raise DatosInvalidos("Solicitud no válida") from None
        if not 0 <= largo <= MAX_FORMULARIO:
            raise DatosInvalidos("El formulario es demasiado grande")
        cuerpo = self.rfile.read(largo).decode("utf-8", errors="replace")
        return {k: v[0] for k, v in parse_qs(cuerpo, keep_blank_values=True).items()}

    def _cliente_actual(self):
        try:
            galleta = cookies.SimpleCookie(self.headers.get("Cookie", "")).get("sesion")
        except cookies.CookieError:
            return None
        numero = self.app.sesiones.get(galleta.value) if galleta else None
        return self.app.cuenta.obtener_cliente(numero) if numero is not None else None

    def _nueva_sesion(self, cliente):
        token = secrets.token_urlsafe(32)
        self.app.sesiones[token] = cliente.numero
        return f"sesion={token}; HttpOnly; SameSite=Lax; Path=/"

    def _enviar(self, codigo, cuerpo, tipo="text/html; charset=utf-8", cabeceras=()):
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(cuerpo)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy",
                         "default-src 'self'; img-src 'self'; form-action 'self'; frame-ancestors 'none'")
        for nombre, valor in cabeceras:
            self.send_header(nombre, valor)
        self.end_headers()
        self.wfile.write(cuerpo)

    def _redirigir(self, destino, cabeceras=()):
        self.send_response(303)
        self.send_header("Location", destino)
        self.send_header("Content-Length", "0")
        for nombre, valor in cabeceras:
            self.send_header(nombre, valor)
        self.end_headers()

    def _error(self, codigo, titulo, mensaje):
        self._enviar(codigo, vistas.error_pagina(titulo, mensaje, self.cliente, self.ruta))

    def _estatico(self, relativa):
        archivo = (ESTATICOS / unquote(relativa)).resolve()
        if (archivo.suffix not in TIPOS_MIME or not archivo.is_relative_to(ESTATICOS)
                or not archivo.is_file()):
            return self._error(404, "Página no encontrada", "El archivo no existe.")
        self._enviar(200, archivo.read_bytes(), TIPOS_MIME[archivo.suffix],
                     [("Cache-Control", "max-age=300")])

    # ---------- pantallas ----------
    def principal(self):
        tipo = self.consulta.get("tipo") or None
        reserva = self.app.reserva
        self._enviar(200, vistas.principal(reserva.listar_habitaciones(tipo),
                                           reserva.tipos_habitacion(), tipo, self.cliente, self.ruta))

    def detalle(self):
        numero = entero(self.consulta.get("numero"), "La habitación")
        h = self.app.reserva.obtener_habitacion(numero)
        self._enviar(200, vistas.detalle(h, self.cliente, self.ruta))

    def reservar_get(self):
        numero = entero(self.consulta.get("habitacion"), "La habitación")
        h = self.app.reserva.obtener_habitacion(numero)
        self._mostrar_reserva(h, {}, "", "")

    def reservar_post(self):
        f = self.form
        reserva = self.app.reserva
        h = reserva.obtener_habitacion(entero(f.get("habitacion"), "La habitación"))
        entrada, salida = f.get("entrada", ""), f.get("salida", "")
        if f.get("accion") != "reservar":  # "Ver disponibilidad"
            return self._mostrar_reserva(h, f, entrada, salida)
        try:
            fecha = fecha_iso(entrada, "La fecha de entrada")
            dias = noches_entre(fecha, fecha_iso(salida, "La fecha de salida"))
            tarjeta = {"nombre": f.get("tarjeta_nombre"), "apellidos": f.get("tarjeta_apellidos"),
                       "numero": f.get("tarjeta_numero"), "vencimiento": f.get("tarjeta_vencimiento"),
                       "codigo": f.get("tarjeta_codigo")}
            if self.cliente is not None:
                hecha = reserva.reservar_con_cuenta(self.cliente.numero, tarjeta, h.numero, fecha, dias)
            else:
                hecha = reserva.reservar_como_visitante(f, tarjeta, h.numero, fecha, dias)
        except ErrorControl as ex:
            return self._mostrar_reserva(h, f, entrada, salida, str(ex), 400)
        self._redirigir(f"/confirmacion?t={self.app.guardar_confirmacion(hecha)}")

    def _mostrar_reserva(self, h, valores, entrada, salida, error="", codigo=200):
        reserva = self.app.reserva
        disponibles = cotizacion = None
        if entrada and salida:
            try:
                fecha = fecha_iso(entrada, "La fecha de entrada")
                dias = noches_entre(fecha, fecha_iso(salida, "La fecha de salida"))
                disponibles = reserva.habitaciones_disponibles(h.tipo, fecha, dias)
                numero_cliente = self.cliente.numero if self.cliente else None
                cotizacion = (dias, *reserva.cotizar(numero_cliente, h.numero, dias))
                if not error and not any(x.numero == h.numero for x in disponibles):
                    error = (f"La habitación #{h.numero} no está disponible en esas fechas. "
                             "Elija otra de la lista." if disponibles else
                             "No hay habitaciones de este tipo disponibles en esas fechas.")
            except ErrorControl as ex:
                error, disponibles, cotizacion = error or str(ex), None, None
        cuerpo = vistas.reserva(h, self.cliente, valores, entrada, salida, disponibles,
                                cotizacion, date.today().isoformat(), error, self.ruta)
        self._enviar(codigo, cuerpo)

    def confirmacion(self):
        hecha = self.app.confirmaciones.get(self.consulta.get("t", ""))
        if hecha is None:
            return self._error(404, "No encontrado", "No se encontró esa confirmación.")
        self._enviar(200, vistas.confirmacion(hecha, self.cliente))

    def registro_get(self):
        self._enviar(200, vistas.registro({}, self.consulta.get("siguiente", "/")))

    def registro_post(self):
        f = self.form
        try:
            cliente = self.app.cuenta.registrar(
                f.get("nombre"), f.get("apellidos"), f.get("tipo_identificacion"),
                f.get("identificacion"), f.get("telefono"), f.get("correo"),
                f.get("clave"), f.get("confirmacion"))
        except ErrorControl as ex:
            return self._enviar(400, vistas.registro(f, f.get("siguiente", "/"), str(ex)))
        self._redirigir(_destino_seguro(f.get("siguiente")),
                        [("Set-Cookie", self._nueva_sesion(cliente))])

    def login_get(self):
        self._enviar(200, vistas.login({}, self.consulta.get("siguiente", "/")))

    def login_post(self):
        f = self.form
        try:
            cliente = self.app.cuenta.iniciar_sesion(f.get("correo"), f.get("clave"))
        except ErrorControl as ex:
            return self._enviar(400, vistas.login(f, f.get("siguiente", "/"), str(ex)))
        self._redirigir(_destino_seguro(f.get("siguiente")),
                        [("Set-Cookie", self._nueva_sesion(cliente))])

    def salir(self):
        try:
            galleta = cookies.SimpleCookie(self.headers.get("Cookie", "")).get("sesion")
        except cookies.CookieError:
            galleta = None
        if galleta:
            self.app.sesiones.pop(galleta.value, None)
        self._redirigir("/", [("Set-Cookie", "sesion=; Max-Age=0; HttpOnly; SameSite=Lax; Path=/")])


RUTAS = {
    ("GET", "/"): "principal",
    ("GET", "/habitacion"): "detalle",
    ("GET", "/reservar"): "reservar_get",
    ("POST", "/reservar"): "reservar_post",
    ("GET", "/confirmacion"): "confirmacion",
    ("GET", "/registro"): "registro_get",
    ("POST", "/registro"): "registro_post",
    ("GET", "/login"): "login_get",
    ("POST", "/login"): "login_post",
    ("POST", "/salir"): "salir",
}


def crear_servidor(reserva, cuenta, host="127.0.0.1", puerto=8000):
    clase = type("ManejadorHotel", (Manejador,), {"app": _Aplicacion(reserva, cuenta)})
    return HTTPServer((host, puerto), clase)
