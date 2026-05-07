class Cliente:

    def __init__(self, id_cliente):
        self.id = id_cliente
        self.mesa_asignada = None
        self.atendido = False

    def asignar_mesa(self, mesa):
        self.mesa_asignada = mesa

    def marcar_atendido(self):
        self.atendido = True

    def salir(self):
        self.mesa_asignada = None

    def __str__(self):
        return (
            f"Cliente("
            f"id={self.id}, "
            f"mesa={self.mesa_asignada}, "
            f"atendido={self.atendido}"
            f")"
        )