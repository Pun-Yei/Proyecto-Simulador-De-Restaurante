from collections import deque


class Cola:

    def __init__(self):
        self.items = deque()

    def agregar(self, item):
        self.items.append(item)

    def sacar(self):
        if self.esta_vacia():
            return None

        return self.items.popleft()

    def esta_vacia(self):
        return len(self.items) == 0

    def tamanio(self):
        return len(self.items)

    def ver_primero(self):
        if self.esta_vacia():
            return None

        return self.items[0]

    def __str__(self):
        return f"Cola({list(self.items)})"