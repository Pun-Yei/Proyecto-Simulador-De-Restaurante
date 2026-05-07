import threading


class Semaforo:

    def __init__(self, valor_inicial):
        self.contador = valor_inicial
        self.lock = threading.Lock()
        self.condicion = threading.Condition(self.lock)

    def acquire(self):

        with self.condicion:

            while self.contador == 0:
                self.condicion.wait()

            self.contador -= 1

    def release(self):

        with self.condicion:

            self.contador += 1
            self.condicion.notify()