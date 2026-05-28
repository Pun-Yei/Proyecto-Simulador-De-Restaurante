import threading
from sincronizacion.colas import Cola
from sincronizacion.semaforos import Semaforo

# =========================
# COLAS
# =========================
cola_clientes_esperando = Cola()
cola_pedidos = Cola()
cola_comida_lista = Cola()

# =========================
# MUTEX
# =========================
mutex_clientes = threading.Lock()
mutex_pedidos = threading.Lock()
mutex_comida_lista = threading.Lock()

# =========================
# SEMAFOROS
# =========================
mesas_disponibles = Semaforo(5)
clientes_esperando = Semaforo(0)
pedidos_pendientes = Semaforo(0)
comida_lista = Semaforo(0)
espacio_cocina = Semaforo(3)

# =========================
# CALLBACK UI (se asigna desde la ventana)
# =========================
ui_callback = None

def notificar_ui(evento, datos=None):
    if ui_callback is not None:
        try:
            ui_callback(evento, datos)
        except Exception:
            pass
