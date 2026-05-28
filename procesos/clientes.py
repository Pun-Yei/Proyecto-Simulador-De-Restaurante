from modelos.cliente import Cliente
from hilos.cliente_thread import ClienteThread


class GestorClientes:
    def __init__(self):
        self.contador_clientes = 1

    def crear_cliente(self):
        cliente = Cliente(self.contador_clientes)
        thread_cliente = ClienteThread(cliente)
        self.contador_clientes += 1
        return thread_cliente
