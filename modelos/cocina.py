class Cocinero:

    def __init__(self, id_cocinero):
        self.id = id_cocinero
        self.ocupado = False
        self.pedido_actual = None

    def asignar_pedido(self, pedido):
        self.ocupado = True
        self.pedido_actual = pedido

    def liberar(self):
        self.ocupado = False
        self.pedido_actual = None
