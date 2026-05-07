import threading
import time
import random

from modelos.pedido import EstadoPedido

from sincronizacion.recursos import (
    cola_clientes_esperando,
    cola_pedidos,
    cola_comida_lista,

    mutex_clientes,
    mutex_pedidos,
    mutex_comida_lista,

    clientes_esperando,
    pedidos_pendientes,
    comida_lista
)


class MeseroThread(threading.Thread):

    def __init__(self, mesero):
        super().__init__()

        self.mesero = mesero

    def run(self):

        while True:

            # =========================
            # ESPERAR CLIENTE
            # =========================

            clientes_esperando.acquire()

            # =========================
            # TOMAR CLIENTE
            # =========================

            with mutex_clientes:

                cliente = cola_clientes_esperando.sacar()

            if cliente is None:
                continue

            pedido = cliente.pedido

            self.mesero.asignar_pedido(pedido)

            print(
                f"Mesero {self.mesero.id} tomó "
                f"pedido {pedido.id} "
                f"del cliente {cliente.id}"
            )

            time.sleep(random.randint(1, 2))

            # =========================
            # METER PEDIDO A COCINA
            # =========================

            with mutex_pedidos:

                cola_pedidos.agregar(pedido)

            pedido.estado = EstadoPedido.PENDIENTE

            print(
                f"Mesero {self.mesero.id} envió "
                f"pedido {pedido.id} a cocina"
            )

            # =========================
            # AVISAR PEDIDO DISPONIBLE
            # =========================

            pedidos_pendientes.release()

            # =========================
            # ESPERAR COMIDA LISTA
            # =========================

            comida_lista.acquire()

            # =========================
            # TOMAR COMIDA LISTA
            # =========================

            with mutex_comida_lista:

                pedido_listo = cola_comida_lista.sacar()

            if pedido_listo is None:
                continue

            # =========================
            # ENTREGAR COMIDA
            # =========================

            pedido_listo.estado = EstadoPedido.ENTREGADO

            print(
                f"Mesero {self.mesero.id} entregó "
                f"pedido {pedido_listo.id}"
            )

            time.sleep(random.randint(1, 2))

            # =========================
            # DESPERTAR CLIENTE
            # =========================

            pedido_listo.comida_entregada.set()

            self.mesero.liberar()