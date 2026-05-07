class Mesa:

    def __init__(self, id_mesa):
        self.id = id_mesa
        self.ocupada = False
        self.id_cliente_actual = None

    def ocupar(self, id_cliente):
        self.ocupada = True
        self.id_cliente_actual = id_cliente

    def liberar(self):
        self.ocupada = False
        self.id_cliente_actual = None

    def __str__(self):
        estado = "Ocupada" if self.ocupada else "Libre"

        return (
            f"Mesa("
            f"id={self.id}, "
            f"estado={estado}, "
            f"cliente={self.id_cliente_actual}"
            f")"
        )