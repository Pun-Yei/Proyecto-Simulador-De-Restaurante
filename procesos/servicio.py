from modelos.mesero import Mesero
from hilos.mesero_thread import MeseroThread

class GestorServicio:
    def __init__(self, total_meseros=2):
        self.meseros = []
        self.total_meseros = total_meseros
    
    def inicializar_meseros(self):
        for i in range(1, self.total_meseros + 1):
            mesero = Mesero(i)
            self.meseros.append(mesero)
            
            thread_mesero = MeseroThread(mesero)
            thread_mesero.daemon = True
            thread_mesero.start()
        
        print(f"{self.total_meseros} meseros inicializados")