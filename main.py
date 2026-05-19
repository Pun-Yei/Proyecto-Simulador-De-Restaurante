from procesos.servicio import GestorServicio
from procesos.cocina import GestorCocina
from procesos.clientes import GestorClientes

# =========================
# CONFIGURACION
# =========================
TOTAL_MESEROS = 2
TOTAL_COCINEROS = 2

# =========================
# INICIALIZAR GESTORES
# =========================
gestor_meseros = GestorServicio(TOTAL_MESEROS)
gestor_cocineros = GestorCocina(TOTAL_COCINEROS)
gestor_clientes = GestorClientes()

# =========================
# INICIAR SERVICIOS
# =========================
gestor_meseros.inicializar_meseros()
gestor_cocineros.inicializar_cocineros()

# =========================
# LOOP PRINCIPAL
# =========================
print("\n=== RESTAURANTE ABIERTO ===")
print("Comandos:")
print("  enter -> agregar cliente")
print("  salir -> cerrar restaurante")

while True:
    comando = input("\n> ").strip().lower()
    
    if comando == "salir":
        print("\nCerrando restaurante...")
        break
    
    # Crear y iniciar thread del cliente
    thread_cliente = gestor_clientes.crear_cliente()
    thread_cliente.start()

print("\nRestaurante cerrado")