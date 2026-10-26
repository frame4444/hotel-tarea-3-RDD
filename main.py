import os

from control import ControladorCuenta, ControladorReserva
from gui import crear_servidor
from persistencia import (ClienteDAO, CuentaDAO, HabitacionDAO, ReservaDAO,
                          obtener_conexion)


def main():
    conexion = obtener_conexion()
    clientes, habitaciones = ClienteDAO(conexion), HabitacionDAO(conexion)
    reservas = ReservaDAO(conexion, clientes, habitaciones)
    puerto = int(os.getenv("PUERTO", "8000"))
    servidor = crear_servidor(ControladorReserva(clientes, habitaciones, reservas),
                              ControladorCuenta(CuentaDAO(conexion), clientes),
                              "127.0.0.1", puerto)
    print(f"Hotel en http://127.0.0.1:{puerto}  (Ctrl+C para detener)")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        servidor.server_close()
        conexion.close()


if __name__ == "__main__":
    main()
