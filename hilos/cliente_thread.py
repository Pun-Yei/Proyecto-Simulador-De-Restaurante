import threading
import time
import random

from modelos.pedido import Pedido

from sincronizacion.recursos import (
    mesas_disponibles,
    cola_clientes_esperando,
    mutex_clientes,
    clientes_esperando
)


class ClienteThread(threading.Thread):

    def __init__(self, cliente):
        super().__init__()

        self.cliente = cliente

    def run(self):

        print(
            f"Cliente {self.cliente.id} llegó al restaurante"
        )

        # =========================
        # ESPERAR MESA
        # =========================

        mesas_disponibles.acquire()

        print(
            f"Cliente {self.cliente.id} obtuvo mesa"
        )

        # =========================
        # CREAR PEDIDO
        # =========================

        pedido = Pedido(
            cliente_id=self.cliente.id
        )

        self.cliente.pedido = pedido

        print(
            f"Cliente {self.cliente.id} creó "
            f"pedido {pedido.id}"
        )

        # =========================
        # ENTRAR A COLA DE ESPERA
        # =========================

        with mutex_clientes:

            cola_clientes_esperando.agregar(
                self.cliente
            )

        print(
            f"Cliente {self.cliente.id} "
            f"esperando mesero"
        )

        # =========================
        # AVISAR CLIENTE DISPONIBLE
        # =========================

        clientes_esperando.release()

        # =========================
        # ESPERAR COMIDA
        # =========================

        print(
            f"Cliente {self.cliente.id} "
            f"esperando comida"
        )

        pedido.comida_entregada.wait()

        # =========================
        # COMER
        # =========================

        print(
            f"Cliente {self.cliente.id} comiendo"
        )

        time.sleep(random.randint(2, 5))

        # =========================
        # LIBERAR MESA
        # =========================

        mesas_disponibles.release()

        print(
            f"Cliente {self.cliente.id} "
            f"liberó mesa"
        )

        # =========================
        # SALIR
        # =========================

        self.cliente.salir()

        print(
            f"Cliente {self.cliente.id} salió"
        )