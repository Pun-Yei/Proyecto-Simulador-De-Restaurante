from enum import Enum
import threading

class EstadoPedido(Enum):
    PENDIENTE = "Pendiente"
    EN_PREPARACION = "En preparacion"
    LISTO = "Listo"
    ENTREGADO = "Entregado"



class Pedido:

    contador_id = 1

    def __init__(self, cliente_id):

        self.id = Pedido.contador_id
        Pedido.contador_id += 1

        self.cliente_id = cliente_id
        self.estado = EstadoPedido.PENDIENTE

        # Evento para avisar comida lista
        self.comida_entregada = threading.Event()