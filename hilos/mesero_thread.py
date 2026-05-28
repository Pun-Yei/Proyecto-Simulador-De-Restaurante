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
    comida_lista,
    notificar_ui,
)


class MeseroThread(threading.Thread):

    def __init__(self, mesero):
        super().__init__(daemon=True)
        self.mesero = mesero

    def run(self):
        while True:
            # =========================
            # ESPERAR CLIENTE
            # =========================
            notificar_ui("mesero_estado", {"id": self.mesero.id, "estado": "Esperando cliente", "pedido": None})
            clientes_esperando.acquire()
            notificar_ui("semaforo_cambio", None)

            # =========================
            # TOMAR CLIENTE
            # =========================
            with mutex_clientes:
                cliente = cola_clientes_esperando.sacar()
            notificar_ui("cola_cambio", None)

            if cliente is None:
                continue
            time.sleep(2)

            pedido = cliente.pedido
            self.mesero.asignar_pedido(pedido)
            notificar_ui("mesero_estado", {"id": self.mesero.id, "estado": "Tomando pedido", "pedido": pedido.id})

            time.sleep(10)

            # =========================
            # METER PEDIDO A COCINA
            # =========================
            with mutex_pedidos:
                cola_pedidos.agregar(pedido)
            notificar_ui("cola_cambio", None)

            pedido.estado = EstadoPedido.PENDIENTE
            notificar_ui("mesero_estado", {"id": self.mesero.id, "estado": "Enviando a cocina", "pedido": pedido.id})

            pedidos_pendientes.release()
            notificar_ui("semaforo_cambio", None)

            # =========================
            # ESPERAR COMIDA LISTA
            # =========================
            notificar_ui("mesero_estado", {"id": self.mesero.id, "estado": "Esperando comida", "pedido": pedido.id})
            comida_lista.acquire()
            notificar_ui("semaforo_cambio", None)

            # =========================
            # TOMAR COMIDA LISTA
            # =========================
            with mutex_comida_lista:
                pedido_listo = cola_comida_lista.sacar()
            notificar_ui("cola_cambio", None)

            if pedido_listo is None:
                continue

            # =========================
            # ENTREGAR COMIDA
            # =========================
            pedido_listo.estado = EstadoPedido.ENTREGADO
            notificar_ui("mesero_estado", {"id": self.mesero.id, "estado": "Entregando comida", "pedido": pedido_listo.id})

            time.sleep(5)

            pedido_listo.comida_entregada.set()
            notificar_ui("pedido_entregado", {"pedido_id": pedido_listo.id, "cliente_id": pedido_listo.cliente_id})

            self.mesero.liberar()
            notificar_ui("mesero_estado", {"id": self.mesero.id, "estado": "Libre", "pedido": None})
