from modelos.cocina import Cocinero
from hilos.cocinero_thread import CocineroThread

class GestorCocina:
    def __init__(self, total_cocineros=2):
        self.cocineros = []
        self.total_cocineros = total_cocineros
    
    def inicializar_cocineros(self):
        for i in range(1, self.total_cocineros + 1):
            cocinero = Cocinero(i)
            self.cocineros.append(cocinero)
            
            thread_cocinero = CocineroThread(cocinero)
            thread_cocinero.daemon = True
            thread_cocinero.start()
        
        print(f"{self.total_cocineros} cocineros inicializados")