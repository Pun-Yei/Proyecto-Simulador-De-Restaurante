import threading
from datetime import datetime

class ObservadorProcesos:
    _instance = None
    _observers = []
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def suscribir(self, callback):
        with self._lock:
            self._observers.append(callback)
    
    def notificar(self, evento, proceso_id, progreso, estado, detalles=""):
        with self._lock:
            datos = {
                'evento': evento,
                'id': proceso_id,
                'progreso': progreso,
                'estado': estado,
                'detalles': detalles,
                'timestamp': datetime.now()
            }
            for callback in self._observers:
                try:
                    callback(datos)
                except Exception as e:
                    print(f"Error notificando: {e}")