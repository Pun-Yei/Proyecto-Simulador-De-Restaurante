from modelos.cliente import Cliente
from modelos.mesero import Mesero
from modelos.cocina import Cocinero

from hilos.cliente_thread import ClienteThread
from hilos.mesero_thread import MeseroThread
from hilos.cocinero_thread import CocineroThread


# =========================
# CONFIGURACION
# =========================

TOTAL_MESEROS = 2
TOTAL_COCINEROS = 2


# =========================
# CONTADOR CLIENTES
# =========================

contador_clientes = 1


# =========================
# CREAR MESEROS
# =========================

meseros = []

for i in range(1, TOTAL_MESEROS + 1):

    mesero = Mesero(i)

    meseros.append(mesero)


# =========================
# CREAR COCINEROS
# =========================

cocineros = []

for i in range(1, TOTAL_COCINEROS + 1):

    cocinero = Cocinero(i)

    cocineros.append(cocinero)


# =========================
# INICIAR THREADS MESEROS
# =========================

for mesero in meseros:

    thread_mesero = MeseroThread(mesero)

    thread_mesero.daemon = True

    thread_mesero.start()


# =========================
# INICIAR THREADS COCINEROS
# =========================

for cocinero in cocineros:

    thread_cocinero = CocineroThread(cocinero)

    thread_cocinero.daemon = True

    thread_cocinero.start()


print("\n=== RESTAURANTE ABIERTO ===")
print("Comandos:")
print("  enter -> agregar cliente")
print("  salir -> cerrar restaurante")


# =========================
# LOOP PRINCIPAL
# =========================

while True:

    comando = input("\n> ").strip().lower()

    # =========================
    # CERRAR RESTAURANTE
    # =========================

    if comando == "salir":

        print("\nCerrando restaurante...")

        break

    # =========================
    # CREAR CLIENTE
    # =========================

    cliente = Cliente(contador_clientes)

    thread_cliente = ClienteThread(cliente)

    thread_cliente.start()

    print(
        f"Cliente {contador_clientes} agregado al restaurante"
    )

    contador_clientes += 1


print("\nRestaurante cerrado")