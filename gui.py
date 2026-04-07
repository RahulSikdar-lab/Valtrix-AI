import customtkinter as ctk
import tkinter as tk
from datetime import datetime
import math
import random
import json
import os
import queue

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "valtrix_config.json")

# ══════════════════════════════════════════════════════
#  THEMES
# ══════════════════════════════════════════════════════

THEMES = {
    "Midnight": {
        "bg": "#0b0f19", "card": "#111827", "sidebar": "#0d1117",
        "accent": "#3b82f6", "green": "#10b981", "red": "#ef4444",
        "yellow": "#f59e0b", "purple": "#8b5cf6", "text": "#e2e8f0",
        "dim": "#64748b", "border": "#1e293b", "chat_bg": "#0d1117",
        "user_bubble": "#1e3a5f", "bot_bubble": "#1a1f2e",
    },
    "Cyberpunk": {
        "bg": "#0a0a0f", "card": "#1a0a2e", "sidebar": "#0f0a1a",
        "accent": "#ff00ff", "green": "#00ff88", "red": "#ff0044",
        "yellow": "#ffaa00", "purple": "#aa00ff", "text": "#e0e0ff",
        "dim": "#7a6b9a", "border": "#2a1a4e", "chat_bg": "#0d0a15",
        "user_bubble": "#2a0a4e", "bot_bubble": "#1a0a2e",
    },
    "Ocean": {
        "bg": "#0a192f", "card": "#112240", "sidebar": "#0a1628",
        "accent": "#64ffda", "green": "#64ffda", "red": "#ff6b6b",
        "yellow": "#ffd93d", "purple": "#bd93f9", "text": "#ccd6f6",
        "dim": "#8892b0", "border": "#1d3557", "chat_bg": "#0d1b30",
        "user_bubble": "#1d3557", "bot_bubble": "#112240",
    },
    "Emerald": {
        "bg": "#0a1a14", "card": "#0d2818", "sidebar": "#081a10",
        "accent": "#10b981", "green": "#34d399", "red": "#f87171",
        "yellow": "#fbbf24", "purple": "#a78bfa", "text": "#d1fae5",
        "dim": "#6b8f7b", "border": "#1a3a28", "chat_bg": "#0a1f14",
        "user_bubble": "#1a3a28", "bot_bubble": "#0d2818",
    },
    "Rose": {
        "bg": "#1a0a14", "card": "#2a1020", "sidebar": "#140a10",
        "accent": "#f43f5e", "green": "#4ade80", "red": "#ff6b6b",
        "yellow": "#fbbf24", "purple": "#f0abfc", "text": "#fce7f3",
        "dim": "#9b7a8a", "border": "#3a1a28", "chat_bg": "#180a12",
        "user_bubble": "#3a1a28", "bot_bubble": "#2a1020",
    },
}


def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {"theme": "Midnight"}


def save_config(cfg):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(cfg, f, indent=2)


# ══════════════════════════════════════════════════════
#  WAVEFORM VISUALIZER
# ══════════════════════════════════════════════════════

class WaveformVisualizer:
    def __init__(self, parent, C, width=500, height=40):
        self.C = C
        self.frame = ctk.CTkFrame(parent, fg_color="transparent", height=height + 10)
        self.canvas = tk.Canvas(self.frame, width=width, height=height,
                                bg=C["chat_bg"], highlightthickness=0, bd=0)
        self.canvas.pack(expand=True, fill="x")
        self.width = width
        self.height = height
        self.num_bars = 45
        self.state = "idle"
        self.phase = 0.0
        self._animate()

    def set_state(self, state):
        self.state = state

    def _animate(self):
        self.canvas.delete("all")
        cy = self.height // 2
        cw = self.canvas.winfo_width() or self.width
        bw = max(3, (cw // self.num_bars) - 3)
        sp = cw / self.num_bars

        if self.state == "idle":
            for i in range(self.num_bars):
                x = sp * i + sp / 2 - bw / 2
                h = 2 + 1.5 * math.sin(self.phase + i * 0.2)
                self.canvas.create_rectangle(x, cy - h, x + bw, cy + h,
                                             fill=self.C["border"], outline="")
            self.phase += 0.04

        elif self.state == "listening":
            for i in range(self.num_bars):
                x = sp * i + sp / 2 - bw / 2
                amp = abs(math.sin(self.phase + i * 0.3))
                h = 3 + 16 * amp * random.uniform(0.4, 1.0)
                ratio = min(h / 18, 1.0)
                r = int(16 + (59 - 16) * ratio)
                g = int(185 + (130 - 185) * ratio)
                b = int(129 + (246 - 129) * ratio)
                self.canvas.create_rectangle(x, cy - h, x + bw, cy + h,
                                             fill=f"#{r:02x}{g:02x}{b:02x}", outline="")
            self.phase += 0.12

        elif self.state == "speaking":
            for i in range(self.num_bars):
                x = sp * i + sp / 2 - bw / 2
                h = 2 + 10 * abs(math.sin(self.phase * 1.5 + i * 0.25))
                self.canvas.create_rectangle(x, cy - h, x + bw, cy + h,
                                             fill=self.C["purple"], outline="")
            self.phase += 0.1

        self.canvas.after(50, self._animate)


# ══════════════════════════════════════════════════════
#  CHAT DISPLAY WITH BUBBLES
# ══════════════════════════════════════════════════════

class ChatDisplay:
    def __init__(self, parent, root_ref, C):
        self.root = root_ref
        self.C = C
        self.msg_queue = queue.Queue()

        self.scroll = ctk.CTkScrollableFrame(parent, fg_color=C["chat_bg"],
                                             corner_radius=10)
        self.scroll.pack(fill="both", expand=True, padx=12, pady=(4, 0))
        self._check_queue()
        self.add_message("system", "Welcome to Valtrix AI  ✦  Say 'Hello' or click Start Listening.")

    def add_message(self, sender, text):
        self.msg_queue.put((sender, text))

    def _check_queue(self):
        while not self.msg_queue.empty():
            try:
                sender, text = self.msg_queue.get_nowait()
                self._create_bubble(sender, text)
            except Exception:
                break
        try:
            self.root.after(100, self._check_queue)
        except Exception:
            pass

    def _create_bubble(self, sender, text):
        C = self.C
        ts = datetime.now().strftime("%H:%M")
        outer = ctk.CTkFrame(self.scroll, fg_color="transparent")
        outer.pack(fill="x", pady=3, padx=5)

        if sender.lower() in ("you", "user"):
            bubble = ctk.CTkFrame(outer, fg_color=C["user_bubble"], corner_radius=14)
            bubble.pack(side="right", padx=(80, 5))
            ctk.CTkLabel(bubble, text=f"You  {ts}", font=("Arial", 9),
                         text_color=C["dim"], anchor="e").pack(fill="x", padx=12, pady=(8, 0))
            ctk.CTkLabel(bubble, text=text, font=("Arial", 11), text_color=C["text"],
                         wraplength=320, anchor="w", justify="left"
                         ).pack(padx=12, pady=(2, 8))

        elif sender.lower() in ("valtrix", "assistant"):
            bubble = ctk.CTkFrame(outer, fg_color=C["bot_bubble"], corner_radius=14)
            bubble.pack(side="left", padx=(5, 80))
            ctk.CTkLabel(bubble, text=f"✦ Valtrix  {ts}", font=("Arial", 9),
                         text_color=C["accent"], anchor="w").pack(fill="x", padx=12, pady=(8, 0))
            ctk.CTkLabel(bubble, text=text, font=("Arial", 11), text_color=C["text"],
                         wraplength=320, anchor="w", justify="left"
                         ).pack(padx=12, pady=(2, 8))
        else:
            ctk.CTkLabel(outer, text=text, font=("Arial", 10),
                         text_color=C["dim"]).pack(anchor="center")

        self.scroll.after(50, lambda: self.scroll._parent_canvas.yview_moveto(1.0))

    # Backward-compat shims
    def insert(self, index, text):
        text = text.strip()
        if not text:
            return
        if text.startswith("Valtrix:"):
            self.add_message("valtrix", text.split(":", 1)[1].strip())
        elif text.startswith("You:"):
            self.add_message("you", text.split(":", 1)[1].strip())
        else:
            self.add_message("system", text)

    def see(self, _idx):
        self.scroll.after(50, lambda: self.scroll._parent_canvas.yview_moveto(1.0))


# ══════════════════════════════════════════════════════
#  USAGE ANALYTICS
# ══════════════════════════════════════════════════════

class UsageAnalytics:
    def __init__(self):
        self.file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "analytics.json")
        self.data = self._load()

    def _load(self):
        if os.path.exists(self.file):
            try:
                with open(self.file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {"total": 0, "today": 0, "today_date": "", "types": {},
                "daily": {}, "sessions": 0}

    def save(self):
        try:
            with open(self.file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception:
            pass

    def track(self, cmd_type):
        today = datetime.now().strftime("%Y-%m-%d")
        if self.data.get("today_date") != today:
            self.data["today_date"] = today
            self.data["today"] = 0
        self.data["total"] += 1
        self.data["today"] += 1
        self.data["types"][cmd_type] = self.data["types"].get(cmd_type, 0) + 1
        self.data["daily"][today] = self.data["daily"].get(today, 0) + 1
        self.save()

    def new_session(self):
        self.data["sessions"] = self.data.get("sessions", 0) + 1
        self.save()

    def show_popup(self, parent, C):
        w = ctk.CTkToplevel(parent)
        w.title("Valtrix AI - Usage Analytics")
        w.geometry("450x500")
        w.configure(fg_color=C["bg"])
        w.attributes("-topmost", True)

        ctk.CTkLabel(w, text="Usage Analytics", font=("Arial", 20, "bold"),
                     text_color=C["text"]).pack(pady=(20, 15))

        # Stats cards
        stats = [
            ("Total Commands", str(self.data.get("total", 0)), C["accent"]),
            ("Today's Commands", str(self.data.get("today", 0)), C["green"]),
            ("Sessions", str(self.data.get("sessions", 0)), C["purple"]),
        ]
        for label, val, color in stats:
            card = ctk.CTkFrame(w, fg_color=C["card"], corner_radius=12,
                                border_width=1, border_color=C["border"])
            card.pack(fill="x", padx=25, pady=4)
            ctk.CTkLabel(card, text=label, font=("Arial", 11),
                         text_color=C["dim"]).pack(side="left", padx=15, pady=12)
            ctk.CTkLabel(card, text=val, font=("Arial", 18, "bold"),
                         text_color=color).pack(side="right", padx=15, pady=12)

        # Top commands
        ctk.CTkLabel(w, text="Top Commands", font=("Arial", 14, "bold"),
                     text_color=C["text"]).pack(pady=(15, 5))

        types = self.data.get("types", {})
        sorted_types = sorted(types.items(), key=lambda x: x[1], reverse=True)[:8]
        if sorted_types:
            max_val = sorted_types[0][1] if sorted_types else 1
            for name, count in sorted_types:
                row = ctk.CTkFrame(w, fg_color=C["card"], corner_radius=8)
                row.pack(fill="x", padx=25, pady=2)
                ctk.CTkLabel(row, text=name.replace("_", " ").title(),
                             font=("Arial", 10), text_color=C["text"],
                             width=120, anchor="w").pack(side="left", padx=12, pady=6)
                bar_frame = ctk.CTkFrame(row, fg_color="transparent")
                bar_frame.pack(side="left", fill="x", expand=True, padx=5)
                bar = ctk.CTkProgressBar(bar_frame, height=8, corner_radius=4,
                                         progress_color=C["accent"])
                bar.pack(fill="x", pady=8)
                bar.set(count / max_val)
                ctk.CTkLabel(row, text=str(count), font=("Arial", 10, "bold"),
                             text_color=C["accent"]).pack(side="right", padx=12, pady=6)
        else:
            ctk.CTkLabel(w, text="No commands tracked yet", font=("Arial", 11),
                         text_color=C["dim"]).pack(pady=10)


# ══════════════════════════════════════════════════════
#  MAIN GUI BUILDER
# ══════════════════════════════════════════════════════

# Global for theme restart
restart_with_theme = [None]


def create_gui(start_thread, open_vault, update_system_info_func, get_system_info_func):
    cfg = load_config()
    theme_name = cfg.get("theme", "Midnight")
    if theme_name not in THEMES:
        theme_name = "Midnight"
    C = THEMES[theme_name]

    root = ctk.CTk()
    root.title("Valtrix AI")
    root.geometry("1100x750")
    root.minsize(900, 600)
    root.configure(fg_color=C["bg"])

    analytics = UsageAnalytics()
    analytics.new_session()

    # ══════ SIDEBAR ══════
    sidebar = ctk.CTkFrame(root, width=72, fg_color=C["sidebar"], corner_radius=0)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    logo_f = ctk.CTkFrame(sidebar, fg_color="transparent", height=80)
    logo_f.pack(fill="x")
    logo_f.pack_propagate(False)
    logo_bg = ctk.CTkFrame(logo_f, width=44, height=44, corner_radius=12, fg_color=C["accent"])
    logo_bg.pack(pady=(18, 2))
    logo_bg.pack_propagate(False)
    ctk.CTkLabel(logo_bg, text="V", font=("Arial", 22, "bold"), text_color="white").pack(expand=True)
    ctk.CTkLabel(sidebar, text="VALTRIX", font=("Arial", 7, "bold"), text_color=C["dim"]).pack(pady=(0, 20))
    ctk.CTkFrame(sidebar, height=1, fg_color=C["border"]).pack(fill="x", padx=12)

    def _sbtn(emoji, label, cmd):
        f = ctk.CTkFrame(sidebar, fg_color="transparent", height=62)
        f.pack(fill="x", pady=2)
        f.pack_propagate(False)
        ctk.CTkButton(f, text=emoji, width=48, height=48, font=("Arial", 18),
                      fg_color="transparent", hover_color="#1e293b", corner_radius=12,
                      command=cmd).pack(expand=True, pady=(4, 0))
        ctk.CTkLabel(f, text=label, font=("Arial", 8), text_color=C["dim"]).pack()

    _sbtn("🏠", "Home", lambda: None)
    _sbtn("🔒", "Vault", open_vault)

    ctk.CTkFrame(sidebar, fg_color="transparent").pack(fill="both", expand=True)
    ctk.CTkFrame(sidebar, width=8, height=8, corner_radius=4, fg_color=C["green"]).pack(pady=(0, 20))

    # ══════ MAIN ══════
    main = ctk.CTkFrame(root, fg_color=C["bg"], corner_radius=0)
    main.pack(side="right", fill="both", expand=True)

    # Header with theme selector
    header = ctk.CTkFrame(main, fg_color="transparent", height=50)
    header.pack(fill="x", padx=20, pady=(12, 4))
    header.pack_propagate(False)
    ctk.CTkLabel(header, text="Valtrix AI", font=("Arial", 24, "bold"),
                 text_color=C["text"]).pack(side="left")
    ctk.CTkLabel(header, text="Intelligent Desktop Assistant", font=("Arial", 12),
                 text_color=C["dim"]).pack(side="left", padx=(12, 0), pady=(6, 0))

    def on_theme_change(choice):
        save_config({"theme": choice})
        restart_with_theme[0] = choice
        root.destroy()

    theme_menu = ctk.CTkOptionMenu(header, values=list(THEMES.keys()),
                                   command=on_theme_change, width=120, height=30,
                                   fg_color=C["card"], button_color=C["accent"],
                                   button_hover_color=C["border"],
                                   dropdown_fg_color=C["card"],
                                   dropdown_hover_color=C["border"],
                                   font=("Arial", 11))
    theme_menu.set(theme_name)
    theme_menu.pack(side="right", padx=5)
    ctk.CTkLabel(header, text="Theme:", font=("Arial", 10), text_color=C["dim"]).pack(side="right")

    # ══════ SYSTEM CARDS ══════
    cards = ctk.CTkFrame(main, fg_color="transparent", height=105)
    cards.pack(fill="x", padx=20, pady=6)
    cards.pack_propagate(False)
    cards.columnconfigure((0, 1, 2, 3), weight=1)

    def _card(title, emoji, col, bar_color):
        c = ctk.CTkFrame(cards, fg_color=C["card"], corner_radius=14,
                         border_width=1, border_color=C["border"])
        c.grid(row=0, column=col, padx=4, sticky="nsew")
        cards.rowconfigure(0, weight=1)
        top = ctk.CTkFrame(c, fg_color="transparent")
        top.pack(fill="x", padx=12, pady=(10, 0))
        ctk.CTkLabel(top, text=emoji, font=("Arial", 16)).pack(side="left")
        ctk.CTkLabel(top, text=title, font=("Arial", 9, "bold"),
                     text_color=C["dim"]).pack(side="left", padx=(5, 0))
        val = ctk.CTkLabel(c, text="—", font=("Arial", 15, "bold"), text_color=C["text"])
        val.pack(pady=(2, 1))
        bar = ctk.CTkProgressBar(c, width=140, height=5, corner_radius=3,
                                 progress_color=bar_color, fg_color=C["border"])
        bar.pack(pady=(0, 10))
        bar.set(0)
        return val, bar

    cpu_label, cpu_bar = _card("CPU", "⚡", 0, C["green"])
    mem_label, mem_bar = _card("RAM", "🧠", 1, C["purple"])
    disk_label, disk_bar = _card("DISK", "💾", 2, C["yellow"])

    sys_card = ctk.CTkFrame(cards, fg_color=C["card"], corner_radius=14,
                            border_width=1, border_color=C["border"])
    sys_card.grid(row=0, column=3, padx=4, sticky="nsew")
    st = ctk.CTkFrame(sys_card, fg_color="transparent")
    st.pack(fill="x", padx=12, pady=(10, 0))
    ctk.CTkLabel(st, text="🖥️", font=("Arial", 16)).pack(side="left")
    ctk.CTkLabel(st, text="SYSTEM", font=("Arial", 9, "bold"), text_color=C["dim"]).pack(side="left", padx=(5, 0))
    up_label = ctk.CTkLabel(sys_card, text="Uptime: —", font=("Arial", 11, "bold"), text_color=C["text"])
    up_label.pack(pady=(6, 1))
    os_label = ctk.CTkLabel(sys_card, text="OS: —", font=("Arial", 9), text_color=C["dim"])
    os_label.pack(pady=(0, 10))

    # ══════ CHAT ══════
    chat_card = ctk.CTkFrame(main, fg_color=C["card"], corner_radius=14,
                             border_width=1, border_color=C["border"])
    chat_card.pack(fill="both", expand=True, padx=20, pady=6)

    ch = ctk.CTkFrame(chat_card, fg_color="transparent", height=32)
    ch.pack(fill="x", padx=15, pady=(8, 0))
    ch.pack_propagate(False)
    ctk.CTkLabel(ch, text="💬  Conversation", font=("Arial", 13, "bold"),
                 text_color=C["text"]).pack(side="left")

    chat_display = ChatDisplay(chat_card, root, C)

    # ══════ WAVEFORM ══════
    waveform = WaveformVisualizer(chat_card, C, height=35)
    waveform.frame.pack(fill="x", padx=12, pady=(2, 10))

    # ══════ CONTROLS ══════
    ctrl = ctk.CTkFrame(main, fg_color="transparent", height=52)
    ctrl.pack(fill="x", padx=20, pady=(0, 6))
    ctrl.pack_propagate(False)
    br = ctk.CTkFrame(ctrl, fg_color="transparent")
    br.pack(expand=True)

    def _btn(text, cmd, fg, hover, tc="white", w=155):
        ctk.CTkButton(br, text=text, command=cmd, font=("Arial", 12, "bold"),
                      fg_color=fg, hover_color=hover, text_color=tc,
                      width=w, height=40, corner_radius=12).pack(side="left", padx=5)

    _btn("🎤 Start Listening", start_thread, C["green"], "#059669")
    _btn("🔒 Secure Vault", open_vault, C["yellow"], "#d97706", tc="#0a0e1a")
    _btn("⏻ Exit", root.quit, C["red"], "#dc2626")

    def show_help():
        hw = ctk.CTkToplevel(root)
        hw.title("Help")
        hw.geometry("500x450")
        hw.configure(fg_color=C["bg"])
        hw.attributes("-topmost", True)
        ctk.CTkLabel(hw, text="Voice Commands", font=("Arial", 18, "bold"),
                     text_color=C["text"]).pack(pady=15)
        sf = ctk.CTkScrollableFrame(hw, fg_color=C["bg"])
        sf.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        for cmd, desc in [("'Hello'", "Greet"), ("'Open/Close [app]'", "Apps"),
                          ("'Google [query]'", "Search"), ("'Youtube [query]'", "Videos"),
                          ("'What/Who/How...'", "Wikipedia"), ("'Volume up/down'", "Volume"),
                          ("'Pause/Play/Mute'", "Media"), ("'Sleep mode'", "Pause"),
                          ("'Deactivate'", "Shutdown")]:
            r = ctk.CTkFrame(sf, fg_color=C["card"], corner_radius=10)
            r.pack(fill="x", pady=2)
            ctk.CTkLabel(r, text=cmd, font=("Arial", 11, "bold"), text_color=C["accent"],
                         width=180, anchor="w").pack(side="left", padx=12, pady=7)
            ctk.CTkLabel(r, text=desc, font=("Arial", 11), text_color=C["dim"]
                         ).pack(side="right", padx=12, pady=7)

    _btn("❓ Help", show_help, "#6366f1", "#4f46e5", w=100)
    _btn("📊 Stats", lambda: analytics.show_popup(root, C), C["card"], C["border"], tc=C["text"], w=100)

    # Tray button
    def minimize_to_tray():
        try:
            import pystray
            from PIL import Image, ImageDraw
            root.withdraw()
            img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
            d = ImageDraw.Draw(img)
            d.rounded_rectangle([4, 4, 60, 60], radius=12, fill=(59, 130, 246, 255))
            def on_show(icon, item):
                icon.stop()
                root.after(0, root.deiconify)
                root.after(10, root.lift)
            def on_quit(icon, item):
                icon.stop()
                root.after(0, root.quit)
            icon = pystray.Icon("valtrix", img, "Valtrix AI", pystray.Menu(
                pystray.MenuItem("Show Valtrix AI", on_show, default=True),
                pystray.MenuItem("Quit", on_quit)))
            import threading
            threading.Thread(target=icon.run, daemon=True).start()
        except Exception:
            root.iconify()

    _btn("🔽 Tray", minimize_to_tray, C["sidebar"], C["border"], tc=C["dim"], w=90)

    # Sidebar buttons
    _sbtn("❓", "Help", show_help)
    _sbtn("📊", "Stats", lambda: analytics.show_popup(root, C))

    # ══════ STATUS BAR ══════
    sbar = ctk.CTkFrame(root, fg_color=C["sidebar"], height=26, corner_radius=0)
    sbar.pack(fill="x", side="bottom")
    sbar.pack_propagate(False)

    status_text = ctk.CTkLabel(sbar, text="", font=("Arial", 10), text_color=C["dim"])
    status_text.pack(side="left", padx=15)
    time_lbl = ctk.CTkLabel(sbar, text="", font=("Arial", 10), text_color=C["dim"])
    time_lbl.pack(side="right", padx=15)

    def tick():
        time_lbl.configure(text=datetime.now().strftime("🕒 %Y-%m-%d  %H:%M:%S"))
        today = datetime.now().strftime("%Y-%m-%d")
        if analytics.data.get("today_date") == today:
            cnt = analytics.data.get("today", 0)
        else:
            cnt = 0
        status_text.configure(text=f"🟢  Valtrix AI Ready  |  {cnt} commands today")
        try:
            root.after(1000, tick)
        except Exception:
            pass

    # Start
    root.after(100, lambda: update_system_info_func(
        cpu_label, mem_label, disk_label, up_label, os_label,
        cpu_bar, mem_bar, disk_bar))
    tick()

    return root, chat_display, waveform, analytics