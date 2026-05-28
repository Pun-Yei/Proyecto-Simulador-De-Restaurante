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
    espacio_cocina,
    notificar_ui,
)


class CocineroThread(threading.Thread):

    def __init__(self, cocinero):
        super().__init__(daemon=True)
        self.cocinero = cocinero

    def run(self):
        while True:
            # =========================
            # ESPERAR PEDIDO
            # =========================
            notificar_ui("cocinero_estado", {"id": self.cocinero.id, "estado": "Esperando pedido", "pedido": None})
            pedidos_pendientes.acquire()
            notificar_ui("semaforo_cambio", None)

            # =========================
            # ESPERAR ESPACIO COCINA
            # =========================
            notificar_ui("cocinero_estado", {"id": self.cocinero.id, "estado": "Esperando espacio", "pedido": None})
            espacio_cocina.acquire()
            notificar_ui("semaforo_cambio", None)

            # =========================
            # TOMAR PEDIDO
            # =========================
            with mutex_pedidos:
                pedido = cola_pedidos.sacar()
            notificar_ui("cola_cambio", None)

            if pedido is None:
                espacio_cocina.release()
                notificar_ui("semaforo_cambio", None)
                continue

            self.cocinero.asignar_pedido(pedido)
            pedido.estado = EstadoPedido.EN_PREPARACION
            notificar_ui("cocinero_estado", {"id": self.cocinero.id, "estado": "Cocinando", "pedido": pedido.id})

            # =========================
            # COCINAR
            # =========================
            tiempo_cocina = random.randint(3, 7)
            time.sleep(10)

            # =========================
            # PEDIDO LISTO
            # =========================
            pedido.estado = EstadoPedido.LISTO

            with mutex_comida_lista:
                cola_comida_lista.agregar(pedido)
            notificar_ui("cola_cambio", None)

            comida_lista.release()
            notificar_ui("semaforo_cambio", None)
            notificar_ui("cocinero_estado", {"id": self.cocinero.id, "estado": "Pedido listo", "pedido": pedido.id})

            # =========================
            # LIBERAR COCINA
            # =========================
            espacio_cocina.release()
            notificar_ui("semaforo_cambio", None)

            self.cocinero.liberar()
            notificar_ui("cocinero_estado", {"id": self.cocinero.id, "estado": "Libre", "pedido": None})
