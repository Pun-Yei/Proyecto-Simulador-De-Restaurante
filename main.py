"""
Restaurante OS — Simulador de Gestión de Recursos
Sistemas Operativos · Interfaz Tkinter

Estructura del proyecto:
  modelos/       → Cliente, Mesero, Cocinero, Mesa, Pedido
  hilos/         → ClienteThread, MeseroThread, CocineroThread
  sincronizacion/→ Semaforo, Cola, recursos (semáforos globales)
  procesos/      → GestorClientes, GestorServicio, GestorCocina
  interfaces/    → VentanaPrincipal (Tkinter)
"""

from procesos.servicio  import GestorServicio
from procesos.cocina    import GestorCocina
from procesos.clientes  import GestorClientes
from interfaces.ventana_principal import VentanaPrincipal

# =========================
# CONFIGURACIÓN
# =========================
TOTAL_MESEROS   = 2
TOTAL_COCINEROS = 2

# =========================
# INICIALIZAR GESTORES
# =========================
gestor_meseros    = GestorServicio(TOTAL_MESEROS)
gestor_cocineros  = GestorCocina(TOTAL_COCINEROS)
gestor_clientes   = GestorClientes()

# =========================
# INICIAR SERVICIOS
# =========================
gestor_meseros.inicializar_meseros()
gestor_cocineros.inicializar_cocineros()

# =========================
# LANZAR INTERFAZ
# =========================
ventana = VentanaPrincipal(gestor_meseros, gestor_cocineros, gestor_clientes)
ventana.root.mainloop()
