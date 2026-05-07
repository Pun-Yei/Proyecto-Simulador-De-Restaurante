from enum import Enum

class EstadoPedido(Enum):
    PENDIENTE = "Pendiente"
    EN_PREPARACION = "En preparacion"
    LISTO = "Listo"
    ENTREGADO = "Entregado"

class Pedido:
    def __init__(self, id_pedido, id_cliente, id_mesa, tiempo_preparacion):
        self.id = id_pedido
        self.id_cliente = id_cliente
        self.id_mesa = id_mesa
        self.estado = EstadoPedido.PENDIENTE
        self.tiempo_preparacion = tiempo_preparacion

    def __str__(self):
        return (
            f"Pedido("
            f"id={self.id}, "
            f"cliente={self.id_cliente}, "
            f"mesa={self.id_mesa}, "
            f"estado={self.estado.value}"
            f")"
        )
