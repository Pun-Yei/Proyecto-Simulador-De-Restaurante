"""
VentanaPrincipal — Restaurante OS con canvas animado + sprites pixel-art
"""
import tkinter as tk
from tkinter import font
import threading
import time
import math
import random

import sincronizacion.recursos as recursos

# ─────────────────────────────────────────────
#  PALETA
# ─────────────────────────────────────────────
BG        = "#1a1a2e"
BG_PANEL  = "#16213e"
BG_CARD   = "#0f3460"
ACCENT    = "#e94560"
SUCCESS   = "#4ecca3"
WARNING   = "#f5a623"
DANGER    = "#f0524f"
TEXT_PRI  = "#eaeaea"
TEXT_SEC  = "#8888aa"
TEXT_DIM  = "#555577"
BORDER    = "#2a2a4a"
FLOOR     = "#23233a"
WALL      = "#2d2d50"
TABLE_C   = "#3a2a1a"
TABLE_B   = "#6b4226"
CHAIR_C   = "#4a3020"
COUNTER_C = "#1a3a2a"
COUNTER_B = "#2d6a4a"

SEM_ON    = "#4ecca3"
SEM_OFF   = "#1a2a3a"
SEM_DEAD  = "#f0524f"

# ─────────────────────────────────────────────
#  POSICIONES DE ZONAS EN EL CANVAS (800×520)
# ─────────────────────────────────────────────
CW, CH = 820, 480          # canvas width / height

ENTRY_POS   = (50,  240)   # puerta de entrada
QUEUE_POS   = (130, 240)   # cola de espera
KITCHEN_POS = (720, 130)   # cocina (centro)
COUNTER_POS = (590, 240)   # mostrador entrega
EXIT_POS    = (50,  380)   # salida

# Mesas: 5 posiciones fijas
MESAS_POS = [
    (220, 140), (340, 140), (460, 140),
    (280, 310), (420, 310),
]

# Posiciones de cocineros dentro de cocina
COOK_SLOTS = [(690, 80), (740, 80)]

# Posiciones de espera de meseros (junto al mostrador)
WAITER_IDLE = [(570, 310), (620, 310)]

# ─────────────────────────────────────────────
#  SPRITE HELPERS  (dibujo pixel-art con Canvas)
# ─────────────────────────────────────────────

def draw_person(canvas, x, y, color, label="", hat_color=None, tag=None):
    """Dibuja un personaje tipo pixel-art simple (16×22 px)."""
    tags = (tag,) if tag else ()
    hc = hat_color or color
    # sombra
    canvas.create_oval(x-8, y+18, x+8, y+24, fill="#000000",
                       outline="", tags=tags)
    # cuerpo
    canvas.create_rectangle(x-6, y+8, x+6, y+18, fill=color,
                             outline="", tags=tags)
    # cabeza
    canvas.create_oval(x-6, y-4, x+6, y+8, fill="#f5cba7",
                       outline="", tags=tags)
    # ojos
    canvas.create_oval(x-3, y, x-1, y+2, fill="#333", outline="", tags=tags)
    canvas.create_oval(x+1, y, x+3, y+2, fill="#333", outline="", tags=tags)
    # sombrero / gorro
    canvas.create_rectangle(x-7, y-8, x+7, y-3, fill=hc,
                             outline="", tags=tags)
    # etiqueta
    if label:
        canvas.create_text(x, y+28, text=label, fill=TEXT_PRI,
                           font=("Helvetica", 7, "bold"), tags=tags)

def draw_table(canvas, x, y, numero):
    """Mesa con sillas."""
    # sillas
    for dx, dy in [(-22, 0), (22, 0), (0, -18), (0, 18)]:
        canvas.create_oval(x+dx-7, y+dy-7, x+dx+7, y+dy+7,
                           fill=CHAIR_C, outline=TABLE_B, width=1)
    # mesa
    canvas.create_rectangle(x-16, y-12, x+16, y+12,
                             fill=TABLE_C, outline=TABLE_B, width=2)
    canvas.create_text(x, y, text=str(numero), fill="#c8a96e",
                       font=("Helvetica", 9, "bold"))

def draw_kitchen(canvas):
    """Zona de cocina."""
    canvas.create_rectangle(640, 30, CW-10, 200,
                             fill=COUNTER_C, outline=COUNTER_B, width=2)
    canvas.create_text(720, 45, text="👨‍🍳 COCINA", fill=SUCCESS,
                       font=("Helvetica", 9, "bold"))
    # fogones
    for fx in [660, 700, 740]:
        canvas.create_oval(fx-12, 60, fx+12, 84,
                           fill="#1a1a1a", outline="#555", width=1)
        canvas.create_oval(fx-8,  64, fx+8,  80,
                           fill="#3a1a00", outline="#f5a623", width=1)

def draw_counter(canvas):
    """Mostrador de entrega."""
    canvas.create_rectangle(530, 210, 650, 270,
                             fill=COUNTER_C, outline=COUNTER_B, width=2)
    canvas.create_text(590, 240, text="📋 MOSTRADOR", fill=SUCCESS,
                       font=("Helvetica", 8, "bold"))

def draw_entry(canvas):
    canvas.create_rectangle(20, 210, 80, 270,
                             fill="#1a2a1a", outline=SUCCESS, width=2)
    canvas.create_text(50, 240, text="ENTRADA", fill=SUCCESS,
                       font=("Helvetica", 7, "bold"))

def draw_exit(canvas):
    canvas.create_rectangle(20, 350, 80, 410,
                             fill="#2a1a1a", outline=DANGER, width=2)
    canvas.create_text(50, 380, text="SALIDA", fill=DANGER,
                       font=("Helvetica", 7, "bold"))


# ─────────────────────────────────────────────
#  CLASE SPRITE  (actor animado en canvas)
# ─────────────────────────────────────────────
class Sprite:
    """Un personaje que puede moverse suavemente hacia un destino."""

    SPEED = 3.5   # px por frame (frame = 30ms)

    def __init__(self, canvas, x, y, color, label, hat_color=None):
        self.canvas    = canvas
        self.x         = float(x)
        self.y         = float(y)
        self.tx        = float(x)   # target x
        self.ty        = float(y)   # target y
        self.color     = color
        self.label     = label
        self.hat_color = hat_color
        self.tag       = f"sprite_{id(self)}"
        self.bubble_tag = f"bubble_{id(self)}"
        self._bubble_after = None
        self._draw()

    def _draw(self):
        self.canvas.delete(self.tag)
        draw_person(self.canvas, int(self.x), int(self.y),
                    self.color, self.label, self.hat_color, tag=self.tag)

    def move_to(self, tx, ty):
        self.tx = float(tx)
        self.ty = float(ty)

    def step(self):
        """Avanza un frame hacia el destino. Retorna True si llegó."""
        dx = self.tx - self.x
        dy = self.ty - self.y
        dist = math.hypot(dx, dy)
        if dist < self.SPEED:
            self.x, self.y = self.tx, self.ty
            self._draw()
            return True
        self.x += (dx / dist) * self.SPEED
        self.y += (dy / dist) * self.SPEED
        self._draw()
        return False

    def say(self, text, ms=1800):
        """Burbuja de diálogo flotante."""
        self.canvas.delete(self.bubble_tag)
        if self._bubble_after:
            try:
                self.canvas.after_cancel(self._bubble_after)
            except Exception:
                pass
        bx, by = int(self.x), int(self.y) - 30
        pad = 4
        t = self.canvas.create_text(bx, by, text=text, fill=TEXT_PRI,
                                     font=("Helvetica", 8),
                                     tags=self.bubble_tag)
        bb = self.canvas.bbox(t)
        if bb:
            r = self.canvas.create_rectangle(
                bb[0]-pad, bb[1]-pad, bb[2]+pad, bb[3]+pad,
                fill="#2a2a50", outline=ACCENT, width=1,
                tags=self.bubble_tag
            )
            self.canvas.tag_raise(t)
        def _clear():
            self.canvas.delete(self.bubble_tag)
        self._bubble_after = self.canvas.after(ms, _clear)

    def destroy(self):
        self.canvas.delete(self.tag)
        self.canvas.delete(self.bubble_tag)


# ─────────────────────────────────────────────
#  VENTANA PRINCIPAL
# ─────────────────────────────────────────────
class VentanaPrincipal:

    MAX_MESAS     = 5
    MAX_COCINA    = 3
    LOG_MAX_LINES = 150

    def __init__(self, gestor_meseros, gestor_cocineros, gestor_clientes):
        self.gestor_meseros   = gestor_meseros
        self.gestor_cocineros = gestor_cocineros
        self.gestor_clientes  = gestor_clientes

        self._lock = threading.Lock()

        # Estado lógico (reflejado desde hilos)
        self._clientes_data   = {}   # cid -> {"estado":str, "mesa_idx":int|None}
        self._meseros_data    = {}
        self._cocineros_data  = {}
        self._atendidos  = 0
        self._deadlocks  = 0
        self._deadlock_mode = False

        # Mesas libres/ocupadas
        self._mesas_ocupadas = {}   # idx -> cid

        # Cola de eventos desde hilos
        self._eventos      = []
        self._eventos_lock = threading.Lock()

        # Sprites vivos
        self._sprites_clientes  = {}   # cid  -> Sprite
        self._sprites_meseros   = {}   # mid  -> Sprite
        self._sprites_cocineros = {}   # coid -> Sprite

        # Registrar actores iniciales
        for m in gestor_meseros.meseros:
            self._meseros_data[m.id] = {"estado": "Libre", "pedido": None}
        for c in gestor_cocineros.cocineros:
            self._cocineros_data[c.id] = {"estado": "Esperando", "pedido": None}

        recursos.ui_callback = self._on_evento_hilo
        self._build_ui()
        self._init_sprites_fijos()
        self._tick()

    # ──────────────────────────────────────────
    #  CALLBACK DESDE HILOS
    # ──────────────────────────────────────────
    def _on_evento_hilo(self, evento, datos):
        with self._eventos_lock:
            self._eventos.append((evento, datos))

    # ──────────────────────────────────────────
    #  PROCESAMIENTO DE EVENTOS
    # ──────────────────────────────────────────
    def _procesar_eventos(self):
        with self._eventos_lock:
            evs, self._eventos = self._eventos[:], []
        for ev, d in evs:
            self._aplicar(ev, d or {})

    def _aplicar(self, ev, d):
        cid = d.get("id")

        if ev == "cliente_llego":
            with self._lock:
                self._clientes_data[cid] = {"estado": "Llegando", "mesa_idx": None}
            self._log(f"Cliente {cid} llegó", "info")
            # Spawn siempre en la entrada; los movimientos siguientes llevan
            # un pequeño delay para que el sprite sea visible partiendo desde ahí
            self.root.after(0,   lambda c=cid: self._spawn_cliente(c))

        elif ev == "cliente_estado":
            estado = d.get("estado", "")
            with self._lock:
                if cid in self._clientes_data:
                    self._clientes_data[cid]["estado"] = estado

            if "esperando mesa" in estado.lower():
                self._log(f"  C{cid} espera mesa (semáforo)", "warn")
                # Delay para que el sprite haya sido creado antes de moverlo
                self.root.after(80, lambda c=cid: self._mover_sprite_cliente(c, *QUEUE_POS))

            elif "en mesa" in estado.lower():
                self._log(f"  C{cid} obtuvo mesa ✓", "success")
                # Delay para que el sprite pase visiblemente por la cola antes de sentarse
                self.root.after(160, lambda c=cid: self._sentar_cliente(c))

            elif "esperando mesero" in estado.lower():
                self._log(f"  C{cid} esperando mesero", "warn")
                self.root.after(0, lambda c=cid: self._say_sprite("c", c, "🙋 Mesero!"))

            elif "esperando comida" in estado.lower():
                self._log(f"  C{cid} esperando pedido", "warn")
                self.root.after(0, lambda c=cid: self._say_sprite("c", c, "⏳ Esperando..."))

            elif "comiendo" in estado.lower():
                self._log(f"  C{cid} comiendo 🍽", "success")
                self.root.after(0, lambda c=cid: self._say_sprite("c", c, "😋 ¡Delicioso!"))

            elif "saliendo" in estado.lower():
                self._log(f"  C{cid} liberó mesa", "dim")
                self.root.after(0, lambda c=cid: self._liberar_mesa_visual(c))
                self.root.after(0, lambda c=cid: self._mover_sprite_cliente(c, *EXIT_POS))

        elif ev == "cliente_salio":
            self._log(f"  C{cid} salió ✓", "success")
            with self._lock:
                # Liberar mesa ANTES de eliminar la entrada del cliente,
                # así mesa_idx siempre está disponible
                info = self._clientes_data.get(cid, {})
                mesa_idx = info.get("mesa_idx")
                if mesa_idx is not None:
                    self._mesas_ocupadas.pop(mesa_idx, None)
                    info["mesa_idx"] = None
                    dot = self._mesa_items[mesa_idx]
                    self.root.after(0, lambda d=dot: self.canvas.itemconfig(d, fill=SUCCESS))
                self._clientes_data.pop(cid, None)
                self._atendidos += 1
            self.root.after(800, lambda c=cid: self._destroy_sprite("c", c))

        elif ev == "pedido_creado":
            self._log(f"  Pedido P{d['pedido_id']} creado", "info")

        elif ev == "pedido_entregado":
            self._log(f"  ✓ P{d['pedido_id']} entregado a C{d['cliente_id']}", "success")

        elif ev == "mesero_estado":
            mid   = d["id"]
            estado = d["estado"]
            pid   = d.get("pedido")
            with self._lock:
                self._meseros_data[mid] = {"estado": estado, "pedido": pid}
            self._log(f"  Mesero {mid} → {estado}" + (f" [P{pid}]" if pid else ""), "dim")
            self.root.after(0, lambda m=mid, e=estado, p=pid:
                            self._actualizar_mesero_visual(m, e, p))

        elif ev == "cocinero_estado":
            coid  = d["id"]
            estado = d["estado"]
            pid   = d.get("pedido")
            with self._lock:
                self._cocineros_data[coid] = {"estado": estado, "pedido": pid}
            self._log(f"  Cocinero {coid} → {estado}" + (f" [P{pid}]" if pid else ""), "dim")
            self.root.after(0, lambda co=coid, e=estado, p=pid:
                            self._actualizar_cocinero_visual(co, e, p))

        elif ev in ("semaforo_cambio", "cola_cambio"):
            pass

    # ──────────────────────────────────────────
    #  CONSTRUCCIÓN DE LA UI
    # ──────────────────────────────────────────
    def _build_ui(self):
        self.root = tk.Tk()
        self.root.title("Restaurante OS — Vista Interactiva")
        self.root.configure(bg=BG)
        self.root.geometry("1200x820")
        self.root.minsize(1000, 700)

        self.f_title = tk.font.Font(family="Helvetica", size=12, weight="bold")
        self.f_label = tk.font.Font(family="Helvetica", size=10)
        self.f_small = tk.font.Font(family="Helvetica", size=9)
        self.f_mono  = tk.font.Font(family="Courier",   size=9)
        self.f_big   = tk.font.Font(family="Helvetica", size=16, weight="bold")

        self._build_header()

        # Cuerpo: canvas izquierda + panel derecha
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=6, pady=(0,4))

        self._build_canvas(body)
        self._build_right_panel(body)

    # ── HEADER ───────────────────────────────
    def _build_header(self):
        hdr = tk.Frame(self.root, bg=BG_PANEL, pady=7)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🍽  Restaurante OS",
                 font=self.f_title, bg=BG_PANEL, fg=TEXT_PRI).pack(side="left", padx=14)
        self._lbl_status = tk.Label(hdr, text="● ABIERTO",
                                    font=self.f_label, bg=BG_PANEL, fg=SUCCESS)
        self._lbl_status.pack(side="left", padx=6)

        ctrl = tk.Frame(hdr, bg=BG_PANEL)
        ctrl.pack(side="right", padx=10)

        self._btn_cliente  = self._btn(ctrl, "+ Cliente",        self._agregar_cliente,   ACCENT)
        self._btn_batch    = self._btn(ctrl, "+3 Clientes",      self._agregar_batch,     "#5db8f5")
        self._btn_deadlock = self._btn(ctrl, "⚠ Simular Deadlock", self._simular_deadlock, WARNING)
        self._btn_resolve  = self._btn(ctrl, "↺ Resolver",       self._resolver_deadlock, SUCCESS)
        self._btn_resolve.config(state="disabled")
        self._btn_clear    = self._btn(ctrl, "Limpiar log",      self._limpiar_log,       TEXT_DIM)
        for b in (self._btn_cliente, self._btn_batch, self._btn_deadlock,
                  self._btn_resolve, self._btn_clear):
            b.pack(side="left", padx=3)

    # ── CANVAS (mapa del restaurante) ─────────
    def _build_canvas(self, parent):
        frame = tk.Frame(parent, bg=BG, bd=0)
        frame.pack(side="left", fill="both", expand=True)

        self.canvas = tk.Canvas(frame, width=CW, height=CH,
                                bg=FLOOR, highlightthickness=1,
                                highlightbackground=BORDER)
        self.canvas.pack(fill="both", expand=True)
        self._draw_static_map()

    def _draw_static_map(self):
        c = self.canvas
        # Paredes laterales
        c.create_rectangle(0, 0, CW, 20,    fill=WALL, outline="")
        c.create_rectangle(0, CH-20, CW, CH, fill=WALL, outline="")
        c.create_rectangle(0, 0, 20, CH,    fill=WALL, outline="")
        c.create_rectangle(CW-20, 0, CW, CH, fill=WALL, outline="")

        # Separador zona comedor / cocina
        c.create_rectangle(620, 20, 630, CH-20, fill=WALL, outline="")

        # Título zonas
        c.create_text(320, 35, text="ZONA COMEDOR", fill=TEXT_DIM,
                      font=("Helvetica", 9))
        c.create_text(720, 15, text="COCINA", fill=TEXT_DIM,
                      font=("Helvetica", 8))

        # Cocina y mostrador
        draw_kitchen(c)
        draw_counter(c)
        draw_entry(c)
        draw_exit(c)

        # Mesas
        self._mesa_items = []
        for i, (mx, my) in enumerate(MESAS_POS):
            draw_table(c, mx, my, i+1)
            # Indicador de estado (circulos pequeños)
            dot = c.create_oval(mx+12, my-20, mx+22, my-10,
                                fill=SUCCESS, outline="")
            self._mesa_items.append(dot)

        # Leyenda
        leg_x, leg_y = 100, CH - 50
        for col, txt in [(SUCCESS,"Libre"), (DANGER,"Ocupada"),
                         ("#4a9eff","Cliente"), (WARNING,"Mesero"), ("#c84fc8","Cocinero")]:
            c.create_oval(leg_x-6, leg_y-6, leg_x+6, leg_y+6, fill=col, outline="")
            c.create_text(leg_x+18, leg_y, text=txt, fill=TEXT_SEC,
                          font=("Helvetica", 8), anchor="w")
            leg_x += 80

    # ── PANEL DERECHO (semáforos + stats + log) ──
    def _build_right_panel(self, parent):
        right = tk.Frame(parent, bg=BG, width=340)
        right.pack(side="right", fill="both", padx=(6,0))
        right.pack_propagate(False)

        self._build_stats(right)
        self._build_semaforos(right)
        self._build_log_panel(right)

    def _build_stats(self, parent):
        f = tk.Frame(parent, bg=BG)
        f.pack(fill="x", pady=(4,4))
        stats = [
            ("Atendidos",   "_sv_atend",   SUCCESS),
            ("En espera",   "_sv_esp",     WARNING),
            ("Cocinando",   "_sv_cook",    "#5db8f5"),
            ("Deadlocks",   "_sv_dead",    DANGER),
        ]
        for label, attr, col in stats:
            card = tk.Frame(f, bg=BG_CARD, padx=8, pady=4)
            card.pack(side="left", fill="x", expand=True, padx=2)
            sv = tk.Label(card, text="0", font=self.f_big, bg=BG_CARD, fg=col)
            sv.pack()
            tk.Label(card, text=label, font=self.f_small,
                     bg=BG_CARD, fg=TEXT_SEC).pack()
            setattr(self, attr, sv)

    def _build_semaforos(self, parent):
        pnl = tk.Frame(parent, bg=BG_PANEL, padx=8, pady=6)
        pnl.pack(fill="x", pady=(0,4))
        tk.Label(pnl, text="🚦 Semáforos", font=self.f_label,
                 bg=BG_PANEL, fg=TEXT_PRI).pack(anchor="w")
        tk.Frame(pnl, bg=BORDER, height=1).pack(fill="x", pady=(2,4))

        self._sem_rows = {}
        self._mutex_dots = {}

        sems = [
            ("mesas_disponibles",  self.MAX_MESAS, "mesas_disponibles"),
            ("espacio_cocina",     self.MAX_COCINA,"espacio_cocina"),
            ("clientes_esperando", 5,              "clientes_esperando"),
            ("pedidos_pendientes", 5,              "pedidos_pendientes"),
            ("comida_lista",       5,              "comida_lista"),
        ]
        for key, slots, label in sems:
            row = tk.Frame(pnl, bg=BG_PANEL)
            row.pack(fill="x", pady=1)
            tk.Label(row, text=label, font=self.f_small, bg=BG_PANEL,
                     fg=TEXT_SEC, width=20, anchor="w").pack(side="left")
            dots = []
            for _ in range(slots):
                cv = tk.Canvas(row, width=13, height=13,
                               bg=BG_PANEL, highlightthickness=0)
                cv.pack(side="left", padx=1)
                oid = cv.create_oval(1,1,11,11, fill=SEM_OFF, outline=BORDER)
                dots.append((cv, oid))
            self._sem_rows[key] = dots

        tk.Frame(pnl, bg=BORDER, height=1).pack(fill="x", pady=(4,2))
        tk.Label(pnl, text="Mutex", font=self.f_small,
                 bg=BG_PANEL, fg=TEXT_SEC).pack(anchor="w")
        mf = tk.Frame(pnl, bg=BG_PANEL)
        mf.pack(fill="x")
        for mname in ("mutex_clientes","mutex_pedidos","mutex_comida_lista"):
            mc = tk.Frame(mf, bg=BG_CARD, padx=5, pady=2)
            mc.pack(side="left", padx=2, pady=2)
            cv = tk.Canvas(mc, width=10, height=10, bg=BG_CARD,
                           highlightthickness=0)
            cv.pack(side="left", padx=(0,3))
            oid = cv.create_oval(1,1,9,9, fill=SUCCESS, outline="")
            tk.Label(mc, text=mname.replace("mutex_",""),
                     font=self.f_small, bg=BG_CARD, fg=TEXT_SEC).pack(side="left")
            self._mutex_dots[mname] = (cv, oid)

        # Banner deadlock
        self._lbl_dl = tk.Label(pnl, text="", font=self.f_small,
                                bg=BG_PANEL, fg=DANGER, wraplength=300,
                                justify="left")
        self._lbl_dl.pack(fill="x", pady=(4,0))

    def _build_log_panel(self, parent):
        pnl = tk.Frame(parent, bg=BG_PANEL, padx=6, pady=6)
        pnl.pack(fill="both", expand=True)
        tk.Label(pnl, text="📟 Log", font=self.f_label,
                 bg=BG_PANEL, fg=TEXT_PRI).pack(anchor="w")
        tk.Frame(pnl, bg=BORDER, height=1).pack(fill="x", pady=(2,4))
        self._log_text = tk.Text(
            pnl, bg="#0d0d1a", fg=TEXT_PRI, font=self.f_mono,
            state="disabled", relief="flat", bd=0, wrap="word"
        )
        sb = tk.Scrollbar(pnl, command=self._log_text.yview, bg=BG_PANEL)
        self._log_text.config(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._log_text.pack(fill="both", expand=True)
        for tag, col in [("info","#5db8f5"),("success",SUCCESS),
                         ("warn",WARNING),("error",DANGER),
                         ("dim",TEXT_DIM),("deadlock",DANGER)]:
            self._log_text.tag_config(tag, foreground=col)

    # ──────────────────────────────────────────
    #  SPRITES FIJOS (meseros y cocineros)
    # ──────────────────────────────────────────
    def _init_sprites_fijos(self):
        for m in self.gestor_meseros.meseros:
            x, y = WAITER_IDLE[m.id - 1]
            s = Sprite(self.canvas, x, y, color=WARNING,
                       label=f"M{m.id}", hat_color="#a07010")
            self._sprites_meseros[m.id] = s

        for c in self.gestor_cocineros.cocineros:
            x, y = COOK_SLOTS[c.id - 1]
            s = Sprite(self.canvas, x, y, color="#c84fc8",
                       label=f"C{c.id}", hat_color="#7a1f7a")
            self._sprites_cocineros[c.id] = s

    # ──────────────────────────────────────────
    #  MOVIMIENTOS DE CLIENTES
    # ──────────────────────────────────────────
    def _spawn_cliente(self, cid):
        s = Sprite(self.canvas, *ENTRY_POS, color="#4a9eff",
                   label=f"C{cid}", hat_color="#1a5fa0")
        s.say("¡Hola!")
        self._sprites_clientes[cid] = s

    def _sentar_cliente(self, cid):
        # Asignar primera mesa libre
        # _mesas_ocupadas = {idx_mesa: cid} → buscar en KEYS, no en values
        with self._lock:
            for idx, (mx, my) in enumerate(MESAS_POS):
                if idx not in self._mesas_ocupadas:          # ← fix
                    self._mesas_ocupadas[idx] = cid
                    if cid in self._clientes_data:
                        self._clientes_data[cid]["mesa_idx"] = idx
                    mesa_dot = self._mesa_items[idx]
                    # canvas.itemconfig se hace fuera del lock para evitar
                    # bloqueos cruzados con el hilo de Tk
                    self.root.after(0, lambda d=mesa_dot: self.canvas.itemconfig(d, fill=DANGER))
                    self._mover_sprite_cliente(cid, mx + 25, my + 5)
                    return

    def _liberar_mesa_visual(self, cid):
        """Libera la mesa visual del cliente. Es seguro llamarla varias veces."""
        mesa_dot = None
        with self._lock:
            info = self._clientes_data.get(cid, {})
            idx  = info.get("mesa_idx")
            if idx is not None:
                self._mesas_ocupadas.pop(idx, None)
                info["mesa_idx"] = None
                mesa_dot = self._mesa_items[idx]
        if mesa_dot is not None:
            self.canvas.itemconfig(mesa_dot, fill=SUCCESS)

    def _mover_sprite_cliente(self, cid, tx, ty):
        s = self._sprites_clientes.get(cid)
        if s:
            s.move_to(tx, ty)

    def _say_sprite(self, tipo, aid, txt):
        sprites = {"c": self._sprites_clientes,
                   "m": self._sprites_meseros,
                   "co": self._sprites_cocineros}
        s = sprites.get(tipo, {}).get(aid)
        if s:
            s.say(txt)

    def _destroy_sprite(self, tipo, aid):
        sprites = {"c": self._sprites_clientes,
                   "m": self._sprites_meseros,
                   "co": self._sprites_cocineros}
        d = sprites.get(tipo, {})
        s = d.pop(aid, None)
        if s:
            s.destroy()

    # ──────────────────────────────────────────
    #  MOVIMIENTOS MESEROS
    # ──────────────────────────────────────────
    def _actualizar_mesero_visual(self, mid, estado, pid):
        s = self._sprites_meseros.get(mid)
        if not s:
            return
        e = estado.lower()

        if "esperando cliente" in e or "libre" in e:
            s.move_to(*WAITER_IDLE[mid - 1])

        elif "tomando pedido" in e:
            # Ir a la mesa del cliente con ese pedido
            pos = self._buscar_mesa_por_pedido(pid)
            if pos:
                s.move_to(pos[0] - 25, pos[1])
                s.say("📝 Anotando")
            else:
                s.move_to(*QUEUE_POS)
                s.say("📝 Anotando")

        elif "enviando a cocina" in e:
            s.move_to(*COUNTER_POS)
            s.say("→ Cocina")

        elif "esperando comida" in e:
            s.move_to(COUNTER_POS[0], COUNTER_POS[1] + 30)

        elif "entregando comida" in e:
            pos = self._buscar_mesa_por_pedido(pid)
            if pos:
                s.move_to(pos[0] - 25, pos[1])
                s.say("🍽 ¡Su pedido!")
            else:
                s.move_to(*COUNTER_POS)

    def _buscar_mesa_por_pedido(self, pid):
        """Devuelve posición de la mesa del cliente dueño del pedido."""
        if pid is None:
            return None
        with self._lock:
            for cid, info in self._clientes_data.items():
                if pid != cid:
                    continue
                idx = info.get("mesa_idx")
                if idx is not None:
                    return MESAS_POS[idx]
        return None

    # ──────────────────────────────────────────
    #  MOVIMIENTOS COCINEROS
    # ──────────────────────────────────────────
    def _actualizar_cocinero_visual(self, coid, estado, pid):
        s = self._sprites_cocineros.get(coid)
        if not s:
            return
        e = estado.lower()
        slot = COOK_SLOTS[coid - 1]

        if "esperando" in e or "libre" in e:
            s.move_to(*slot)

        elif "cocinando" in e:
            # Pequeño movimiento en la cocina hacia el fogón
            fx = 650 + (coid - 1) * 40
            s.move_to(fx, 100)
            s.say("🔥 Cocinando")

        elif "pedido listo" in e:
            s.move_to(*COUNTER_POS)
            s.say("✅ ¡Listo!")

    # ──────────────────────────────────────────
    #  TICK PRINCIPAL (30 fps)
    # ──────────────────────────────────────────
    def _tick(self):
        if not self._deadlock_mode:
            self._procesar_eventos()
            # Animar todos los sprites
            for s in list(self._sprites_clientes.values()):
                s.step()
            for s in list(self._sprites_meseros.values()):
                s.step()
            for s in list(self._sprites_cocineros.values()):
                s.step()
            self._refresh_semaforos()
            self._refresh_stats()
            self._refresh_mesas()
        self.root.after(33, self._tick)   # ~30 fps

    # ──────────────────────────────────────────
    #  REFRESH INDICADORES
    # ──────────────────────────────────────────
    def _refresh_stats(self):
        with self._lock:
            atend = self._atendidos
            dead  = self._deadlocks
            esp   = len(recursos.cola_clientes_esperando.items)
            cook  = sum(1 for v in self._cocineros_data.values()
                        if v["estado"] == "Cocinando")
        self._sv_atend.config(text=str(atend))
        self._sv_esp.config(text=str(esp))
        self._sv_cook.config(text=str(cook))
        self._sv_dead.config(text=str(dead))

    def _refresh_mesas(self):
        with self._lock:
            ocupadas = set(self._mesas_ocupadas.keys())
        for i, dot in enumerate(self._mesa_items):
            if self._deadlock_mode:
                self.canvas.itemconfig(dot, fill=DANGER)
            elif i in ocupadas:
                self.canvas.itemconfig(dot, fill=DANGER)
            else:
                self.canvas.itemconfig(dot, fill=SUCCESS)

    def _refresh_semaforos(self):
        sem_map = {
            "mesas_disponibles":  (recursos.mesas_disponibles,  self.MAX_MESAS),
            "espacio_cocina":     (recursos.espacio_cocina,      self.MAX_COCINA),
            "clientes_esperando": (recursos.clientes_esperando,  5),
            "pedidos_pendientes": (recursos.pedidos_pendientes,  5),
            "comida_lista":       (recursos.comida_lista,        5),
        }
        for key, (sem, mx) in sem_map.items():
            if key not in self._sem_rows:
                continue
            val = min(sem.contador, mx)
            for i, (cv, oid) in enumerate(self._sem_rows[key]):
                col = (SEM_DEAD if self._deadlock_mode
                       else (SEM_ON if i < val else SEM_OFF))
                cv.itemconfig(oid, fill=col)

        for mname, mtx in [("mutex_clientes",    recursos.mutex_clientes),
                            ("mutex_pedidos",     recursos.mutex_pedidos),
                            ("mutex_comida_lista",recursos.mutex_comida_lista)]:
            if mname not in self._mutex_dots:
                continue
            cv, oid = self._mutex_dots[mname]
            locked = not mtx.acquire(blocking=False)
            if not locked:
                mtx.release()
            col = (DANGER if self._deadlock_mode
                   else (WARNING if locked else SUCCESS))
            cv.itemconfig(oid, fill=col)

    # ──────────────────────────────────────────
    #  ACCIONES BOTONES
    # ──────────────────────────────────────────
    def _agregar_cliente(self):
        t = self.gestor_clientes.crear_cliente()
        t.start()

    def _agregar_batch(self):
        for i in range(3):
            self.root.after(i * 600, self._agregar_cliente)

    def _simular_deadlock(self):
        self._deadlock_mode = True
        with self._lock:
            self._deadlocks += 1

        self._btn_deadlock.config(state="disabled")
        self._btn_resolve.config(state="normal")
        self._btn_cliente.config(state="disabled")
        self._btn_batch.config(state="disabled")
        self._lbl_status.config(text="● DEADLOCK", fg=DANGER)

        # Congelar semáforos
#        recursos.mesas_disponibles.contador = 0
#        recursos.espacio_cocina.contador    = 0

        # Sprites "se congelan" y gritan
        for s in self._sprites_clientes.values():
            s.say("😱 ¡Bloqueado!", ms=99999)
        for s in self._sprites_meseros.values():
            s.say("🔒 Bloqueado", ms=99999)
        for s in self._sprites_cocineros.values():
            s.say("🔒 Bloqueado", ms=99999)

        # Parpadeo rojo en canvas
        self._deadlock_flash(0)

        self._lbl_dl.config(text=(
            "⚠ DEADLOCK\n"
            "M1 espera mutex_comida_lista\n"
            "C1 espera mutex_pedidos\n"
            "→ Ciclo M1→C1→M1"
        ))
        self._log("══ DEADLOCK ══ Espera circular detectada", "deadlock")
        self._log("  Condición 1: Exclusión mutua (mutex tomados)", "error")
        self._log("  Condición 2: Retención y espera", "error")
        self._log("  Condición 3: Sin preempción", "error")
        self._log("  Condición 4: Ciclo M1→C1→M1", "deadlock")

    def _deadlock_flash(self, n):
        if not self._deadlock_mode:
            return
        col = DANGER if n % 2 == 0 else "#3a0000"
        self.canvas.config(bg=col if n % 2 == 0 else FLOOR)
        if n < 8:
            self.root.after(300, lambda: self._deadlock_flash(n + 1))
        else:
            self.canvas.config(bg=FLOOR)

    def _resolver_deadlock(self):
        self._deadlock_mode = False

        self._btn_deadlock.config(state="normal")
        self._btn_resolve.config(state="disabled")
        self._btn_cliente.config(state="normal")
        self._btn_batch.config(state="normal")
        self._lbl_status.config(text="● ABIERTO", fg=SUCCESS)
        self._lbl_dl.config(text="")

#        recursos.mesas_disponibles.contador = self.MAX_MESAS
#        recursos.espacio_cocina.contador    = self.MAX_COCINA
        with recursos.mesas_disponibles.condicion:
            recursos.mesas_disponibles.condicion.notify_all()
        with recursos.espacio_cocina.condicion:
            recursos.espacio_cocina.condicion.notify_all()

        # Limpiar burbujas
        for s in list(self._sprites_clientes.values()) + \
                 list(self._sprites_meseros.values()) + \
                 list(self._sprites_cocineros.values()):
            s.canvas.delete(s.bubble_tag)
            s._bubble_after = None
            s.say("😮‍💨 ¡Libre!", ms=2000)

        self._log("══ RESUELTO ══ Preempción aplicada", "success")
        self._log("  Semáforos restaurados, hilos notificados", "success")

    def _limpiar_log(self):
        self._log_text.config(state="normal")
        self._log_text.delete("1.0", tk.END)
        self._log_text.config(state="disabled")

    # ──────────────────────────────────────────
    #  HELPERS
    # ──────────────────────────────────────────
    def _log(self, msg, tag=""):
        def _do():
            ts = time.strftime("%H:%M:%S")
            self._log_text.config(state="normal")
            self._log_text.insert(tk.END, f"[{ts}] {msg}\n", tag or "")
            lines = int(self._log_text.index("end-1c").split(".")[0])
            if lines > self.LOG_MAX_LINES:
                self._log_text.delete("1.0", "10.0")
            self._log_text.see(tk.END)
            self._log_text.config(state="disabled")
        self.root.after(0, _do)

    def _btn(self, parent, text, cmd, col):
        return tk.Button(parent, text=text, command=cmd,
                         bg=BG_CARD, fg=col,
                         activebackground=BG_PANEL, activeforeground=col,
                         relief="flat", bd=0, padx=10, pady=4,
                         font=self.f_small, cursor="hand2")
