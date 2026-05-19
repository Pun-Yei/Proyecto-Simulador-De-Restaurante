import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
from datetime import datetime

from interfaces.componentes import PanelProceso, PanelControl
from utils.observador import ObservadorProcesos

class VentanaPrincipal:
    def __init__(self, gestor_meseros, gestor_cocineros, gestor_clientes):
        self.gestor_meseros = gestor_meseros
        self.gestor_cocineros = gestor_cocineros
        self.gestor_clientes = gestor_clientes
        self.observador = ObservadorProcesos()
        
        # Diccionario para almacenar referencias a paneles de procesos activos
        self.paneles_activos = {}
        
        self.root = tk.Tk()
        self.root.title("🍽️ Sistema de Gestión de Restaurante")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        self._crear_widgets()
        self._configurar_eventos()
        
        # Suscribir observador
        self.observador.suscribir(self.actualizar_proceso)
    
    def _crear_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Panel de control (arriba)
        self.panel_control = PanelControl(main_frame)
        self.panel_control.pack(fill=tk.X, pady=(0, 10))
        
        # Canvas con scroll para los paneles de procesos
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, bg='#f0f0f0')
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Área de logs
        self._crear_log_area(main_frame)
        
        # Panel de estadísticas
        self._crear_panel_estadisticas(main_frame)
        
        # Organizar paneles de procesos por tipo
        self.panel_clientes = ttk.LabelFrame(self.scrollable_frame, text="Clientes Activos", padding=10)
        self.panel_clientes.pack(fill=tk.X, pady=5)
        
        self.panel_meseros = ttk.LabelFrame(self.scrollable_frame, text="Meseros", padding=10)
        self.panel_meseros.pack(fill=tk.X, pady=5)
        
        self.panel_cocineros = ttk.LabelFrame(self.scrollable_frame, text="Cocineros", padding=10)
        self.panel_cocineros.pack(fill=tk.X, pady=5)
        
        # Inicializar paneles para meseros y cocineros fijos
        self._inicializar_paneles_fijos()
    
    def _crear_log_area(self, parent):
        """Crea el área de logs"""
        log_frame = ttk.LabelFrame(parent, text="📋 Registro de Eventos", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            height=8, 
            width=80,
            font=("Consolas", 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configurar tags de color para logs
        self.log_text.tag_config("INFO", foreground="blue")
        self.log_text.tag_config("ERROR", foreground="red")
        self.log_text.tag_config("SUCCESS", foreground="green")
        self.log_text.tag_config("WARNING", foreground="orange")
    
    def _crear_panel_estadisticas(self, parent):
        stats_frame = ttk.LabelFrame(parent, text="📊 Estadísticas", padding=10)
        stats_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.stats_vars = {
            'total_clientes': tk.StringVar(value="0"),
            'activos': tk.StringVar(value="0"),
            'completados': tk.StringVar(value="0"),
            'tiempo_medio': tk.StringVar(value="0s")
        }
        
        # Grid de estadísticas
        row = 0
        for key, var in self.stats_vars.items():
            label_text = {
                'total_clientes': "Total Clientes:",
                'activos': "Activos:",
                'completados': "Completados:",
                'tiempo_medio': "Tiempo medio:"
            }
            
            ttk.Label(stats_frame, text=label_text[key], font=("Arial", 10, "bold")).grid(
                row=row, column=0, sticky=tk.W, padx=5, pady=2
            )
            ttk.Label(stats_frame, textvariable=var, font=("Arial", 10)).grid(
                row=row, column=1, sticky=tk.W, padx=5, pady=2
            )
            row += 1
    
    def _inicializar_paneles_fijos(self):
        """Crea paneles para meseros y cocineros que son fijos"""
        # Paneles para meseros
        for mesero in self.gestor_meseros.meseros:
            panel = PanelProceso(
                self.panel_meseros, 
                f"Mesero {mesero.id}", 
                f"mesero_{mesero.id}",
                color="blue"
            )
            panel.pack(fill=tk.X, pady=2)
            self.paneles_activos[f"mesero_{mesero.id}"] = panel
        
        # Paneles para cocineros
        for cocinero in self.gestor_cocineros.cocineros:
            panel = PanelProceso(
                self.panel_cocineros, 
                f"Cocinero {cocinero.id}", 
                f"cocinero_{cocinero.id}",
                color="orange"
            )
            panel.pack(fill=tk.X, pady=2)
            self.paneles_activos[f"cocinero_{cocinero.id}"] = panel
    
    def _configurar_eventos(self):
        self.panel_control.on_agregar_cliente = self.agregar_cliente
        self.panel_control.on_cerrar = self.cerrar_restaurante
        
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_restaurante)
    
    def agregar_cliente(self):
        thread_cliente = self.gestor_clientes.crear_cliente()
        
        # Crear panel visual para el cliente
        cliente_id = self.gestor_clientes.contador_clientes - 1
        panel = PanelProceso(
            self.panel_clientes,
            f"Cliente {cliente_id}",
            f"cliente_{cliente_id}",
            color="green"
        )
        panel.pack(fill=tk.X, pady=2)
        self.paneles_activos[f"cliente_{cliente_id}"] = panel
        
        # Iniciar thread
        thread_cliente.start()
        
        # Actualizar contador
        self.panel_control.actualizar_contador(cliente_id)
        
        self.agregar_log(f"Cliente {cliente_id} ingresó al restaurante", "INFO")
    
    def actualizar_proceso(self, datos):
        proceso_id = datos['id']
        progreso = datos['progreso']
        estado = datos['estado']
        detalles = datos['detalles']
        
        # Buscar o crear panel
        if proceso_id in self.paneles_activos:
            panel = self.paneles_activos[proceso_id]
            panel.actualizar(progreso, estado, detalles)
        
        # Actualizar estadísticas
        self._actualizar_estadisticas()
        
        # Loggear eventos importantes
        if progreso >= 100:
            self.agregar_log(f"{proceso_id} completado", "SUCCESS")
        elif 'error' in estado.lower():
            self.agregar_log(f"Error en {proceso_id}: {detalles}", "ERROR")
    
    def _actualizar_estadisticas(self):
        # Contar paneles activos y completados
        total = len([p for p in self.paneles_activos.values() if hasattr(p, 'progress')])
        activos = len([p for p in self.paneles_activos.values() 
                      if hasattr(p, 'progress') and p.progress['value'] < 100])
        completados = total - activos
        
        self.stats_vars['total_clientes'].set(str(total))
        self.stats_vars['activos'].set(str(activos))
        self.stats_vars['completados'].set(str(completados))
    
    def agregar_log(self, mensaje, tipo="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_msg = f"[{timestamp}] [{tipo}] {mensaje}\n"
        
        def _agregar():
            self.log_text.insert(tk.END, log_msg, tipo)
            self.log_text.see(tk.END)
        
        if threading.current_thread() != threading.main_thread():
            self.root.after(0, _agregar)
        else:
            _agregar()
    
    def cerrar_restaurante(self):
        self.agregar_log("Cerrando restaurante...", "WARNING")
        self.root.after(2000, self.root.destroy)
    
    def ejecutar(self):
        self.root.mainloop()