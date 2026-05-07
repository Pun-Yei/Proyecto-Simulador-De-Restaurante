import threading
import time
import random

from modelos.pedido import EstadoPedido

from sincronizacion.recursos import (
    cola_pedidos,
    cola_comida_lista,

    mutex_pedidos,
    mutex_comida_lista,

    pedidos_pendientes,
    comida_lista,
    espacio_cocina
)


class CocineroThread(threading.Thread):

    def __init__(self, cocinero):
        super().__init__()

        self.cocinero = cocinero

    def run(self):

        while True:

            # =========================
            # ESPERAR PEDIDO
            # =========================

            pedidos_pendientes.acquire()

            # =========================
            # ESPERAR ESPACIO COCINA
            # =========================

            espacio_cocina.acquire()

            # =========================
            # TOMAR PEDIDO
            # =========================

            with mutex_pedidos:

                pedido = cola_pedidos.sacar()

            if pedido is None:

                espacio_cocina.release()
                continue

            # =========================
            # ASIGNAR PEDIDO
            # =========================

            self.cocinero.asignar_pedido(pedido)

            pedido.estado = EstadoPedido.EN_PREPARACION

            print(
                f"Cocinero {self.cocinero.id} "
                f"tomó pedido {pedido.id}"
            )

            # =========================
            # COCINAR
            # =========================

            tiempo_cocina = random.randint(3, 7)

            print(
                f"Cocinero {self.cocinero.id} "
                f"cocinando pedido {pedido.id} "
                f"({tiempo_cocina}s)"
            )

            time.sleep(tiempo_cocina)

            # =========================
            # PEDIDO LISTO
            # =========================

            pedido.estado = EstadoPedido.LISTO

            print(
                f"Cocinero {self.cocinero.id} "
                f"terminó pedido {pedido.id}"
            )

            # =========================
            # PUBLICAR COMIDA LISTA
            # =========================

            with mutex_comida_lista:

                cola_comida_lista.agregar(pedido)

            comida_lista.release()

            print(
                f"Pedido {pedido.id} "
                f"agregado a comida lista"
            )

            # =========================
            # LIBERAR COCINA
            # =========================

            espacio_cocina.release()

            # =========================
            # LIBERAR COCINERO
            # =========================

            self.cocinero.liberar()