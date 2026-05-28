import threading
import time
import random

from modelos.pedido import Pedido

from sincronizacion.recursos import (
    mesas_disponibles,
    cola_clientes_esperando,
    mutex_clientes,
    clientes_esperando,
    notificar_ui,
)


class ClienteThread(threading.Thread):

    def __init__(self, cliente):
        super().__init__(daemon=True)
        self.cliente = cliente

    def run(self):
        cid = self.cliente.id
        notificar_ui("cliente_llego", {"id": cid})

        # =========================
        # ESPERAR MESA
        # =========================
        notificar_ui("cliente_estado", {"id": cid, "estado": "Esperando mesa"})
        mesas_disponibles.acquire()
        time.sleep(2)
        notificar_ui("cliente_estado", {"id": cid, "estado": "En mesa"})
        notificar_ui("semaforo_cambio", None)

        # =========================
        # CREAR PEDIDO
        # =========================
        pedido = Pedido(cliente_id=cid)
        self.cliente.pedido = pedido
        notificar_ui("pedido_creado", {"cliente_id": cid, "pedido_id": pedido.id})
        time.sleep(2)

        # =========================
        # ENTRAR A COLA DE ESPERA
        # =========================
        with mutex_clientes:
            cola_clientes_esperando.agregar(self.cliente)
        notificar_ui("cliente_estado", {"id": cid, "estado": "Esperando mesero"})
        notificar_ui("cola_cambio", None)

        clientes_esperando.release()
        notificar_ui("semaforo_cambio", None)

        # =========================
        # ESPERAR COMIDA
        # =========================
        notificar_ui("cliente_estado", {"id": cid, "estado": "Esperando comida"})
        pedido.comida_entregada.wait()

        # =========================
        # COMER
        # =========================
        time.sleep(1)
        notificar_ui("cliente_estado", {"id": cid, "estado": "Comiendo"})
        time.sleep(10)

        # =========================
        # LIBERAR MESA
        # =========================
        mesas_disponibles.release()
        notificar_ui("semaforo_cambio", None)
        notificar_ui("cliente_estado", {"id": cid, "estado": "Saliendo"})

        # =========================
        # SALIR
        # =========================
        self.cliente.salir()
        notificar_ui("cliente_salio", {"id": cid})
