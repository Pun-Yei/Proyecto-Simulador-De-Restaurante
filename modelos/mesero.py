class Mesero:

    def __init__(self, id_mesero):
        self.id = id_mesero
        self.ocupado = False
        self.pedido_actual = None

    def asignar_pedido(self, pedido):
        self.ocupado = True
        self.pedido_actual = pedido

    def liberar(self):
        self.ocupado = False
        self.pedido_actual = None

    def __str__(self):
        return (
            f"Mesero("
            f"id={self.id}, "
            f"ocupado={self.ocupado}, "
            f"pedido_actual={self.pedido_actual}"
            f")"
        )