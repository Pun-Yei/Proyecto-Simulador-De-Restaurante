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