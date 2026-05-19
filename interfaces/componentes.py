import tkinter as tk
from tkinter import ttk
import threading

class PanelProceso(ttk.LabelFrame):
    
    def __init__(self, parent, titulo, proceso_id, color="blue"):
        super().__init__(parent, text=titulo, padding=10)
        self.proceso_id = proceso_id
        self.color = color
        
        # Frame para información
        self.info_frame = ttk.Frame(self)
        self.info_frame.pack(fill=tk.X, pady=5)
        
        # Label de estado
        self.lbl_estado = ttk.Label(self.info_frame, text="🟡 Inicializando...")
        self.lbl_estado.pack(side=tk.LEFT)
        
        # Label de porcentaje
        self.lbl_porcentaje = ttk.Label(self.info_frame, text="0%")
        self.lbl_porcentaje.pack(side=tk.RIGHT)
        
        # Barra de progreso
        self.progress = ttk.Progressbar(
            self, 
            length=300, 
            mode='determinate',
            style=f"{color}.Horizontal.TProgressbar"
        )
        self.progress.pack(pady=5, fill=tk.X)
        
        # Label de detalles
        self.lbl_detalles = ttk.Label(self, text="Esperando...", font=("Arial", 8))
        self.lbl_detalles.pack(fill=tk.X)
        
        # Configurar estilos de color
        self._configurar_estilos()
    
    def _configurar_estilos(self):
        style = ttk.Style()
        
        # Estilo para cliente (verde)
        style.configure("green.Horizontal.TProgressbar", 
                       troughcolor='#e0e0e0', 
                       background='#4CAF50',
                       thickness=20)
        
        # Estilo para mesero (azul)
        style.configure("blue.Horizontal.TProgressbar", 
                       troughcolor='#e0e0e0', 
                       background='#2196F3',
                       thickness=20)
        
        # Estilo para cocinero (naranja)
        style.configure("orange.Horizontal.TProgressbar", 
                       troughcolor='#e0e0e0', 
                       background='#FF9800',
                       thickness=20)
    
    def actualizar(self, progreso, estado, detalles=""):
        def _actualizar():
            self.progress['value'] = progreso
            self.lbl_porcentaje.config(text=f"{int(progreso)}%")
            
            iconos = {
                "completado": "✅",
                "error": "❌",
                "en progreso": "🟢",
                "esperando": "🟡",
                "iniciando": "🔵"
            }
            icono = iconos.get(estado.lower(), "🟡")
            self.lbl_estado.config(text=f"{icono} {estado}")
            
            if detalles:
                self.lbl_detalles.config(text=detalles)
        
        if threading.current_thread() != threading.main_thread():
            self.master.after(0, _actualizar)
        else:
            _actualizar()

class PanelControl(ttk.Frame):
    
    def __init__(self, parent):
        super().__init__(parent, padding=10)
        
        self.btn_agregar = ttk.Button(
            self, 
            text="Agregar Cliente",
            command=self._on_agregar_cliente
        )
        self.btn_agregar.pack(side=tk.LEFT, padx=5)
        
        self.btn_cerrar = ttk.Button(
            self,
            text="Cerrar Restaurante",
            command=self._on_cerrar
        )
        self.btn_cerrar.pack(side=tk.LEFT, padx=5)
        
        self.lbl_contador = ttk.Label(
            self, 
            text="Clientes atendidos: 0",
            font=("Arial", 10, "bold")
        )
        self.lbl_contador.pack(side=tk.RIGHT, padx=10)
        
        self.on_agregar_cliente = None
        self.on_cerrar = None
    
    def _on_agregar_cliente(self):
        if self.on_agregar_cliente:
            self.on_agregar_cliente()
    
    def _on_cerrar(self):
        if self.on_cerrar:
            self.on_cerrar()
    
    def actualizar_contador(self, total):
        def _actualizar():
            self.lbl_contador.config(text=f"Clientes atendidos: {total}")
        
        if threading.current_thread() != threading.main_thread():
            self.master.after(0, _actualizar)
        else:
            _actualizar()