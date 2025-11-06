import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import matplotlib
matplotlib.use('Agg')

# Global references for system monitoring
cpu_label = None
memory_label = None
disk_label = None
uptime_label = None
os_label = None
cpu_bar = None
memory_bar = None
disk_bar = None
text_display = None
root = None

def create_gui(start_thread, open_vault, update_system_info_func, get_system_info_func):
    global root, cpu_label, memory_label, disk_label, uptime_label, os_label
    global cpu_bar, memory_bar, disk_bar, text_display

    root = tk.Tk()
    root.title("Desktop Assistant - Professional Edition")
    root.geometry("1000x750")
    root.configure(bg="#0d1b2a")

    # Modern color scheme
    COLORS = {
        "dark_blue": "#0d1b2a",
        "navy_blue": "#1b263b",
        "medium_blue": "#415a77",
        "light_blue": "#778da9",
        "off_white": "#e0e1dd",
        "accent_yellow": "#ffb703",
        "accent_orange": "#fb8500",
        "accent_red": "#e63946",
        "accent_green": "#2a9d8f"
    }

    # Custom title bar
    title_bar = tk.Frame(root, bg=COLORS["navy_blue"], height=40, relief='raised', bd=0)
    title_bar.pack(fill='x', side='top')
    title_bar.pack_propagate(False)

    title_label = tk.Label(title_bar, text="Desktop Assistant Pro", 
                          font=("Arial", 14, "bold"), 
                          bg=COLORS["navy_blue"], 
                          fg=COLORS["accent_yellow"])
    title_label.pack(side='left', padx=15, pady=8)

    # Header with gradient effect
    header_frame = tk.Frame(root, bg=COLORS["dark_blue"], height=80)
    header_frame.pack(fill="x", padx=0, pady=0)
    header_frame.pack_propagate(False)

    header_content = tk.Frame(header_frame, bg=COLORS["dark_blue"])
    header_content.pack(expand=True, fill='both')

    # Main title
    main_title = tk.Label(header_content, text="Desktop Assistant Pro", 
                         font=("Arial", 28, "bold"), 
                         bg=COLORS["dark_blue"], 
                         fg=COLORS["off_white"])
    main_title.pack(pady=10)

    subtitle = tk.Label(header_content, text="Professional Desktop Management System", 
                       font=("Arial", 12), 
                       bg=COLORS["dark_blue"], 
                       fg=COLORS["light_blue"])
    subtitle.pack(pady=(0, 10))

    # Main Content Frame with modern layout
    main_frame = tk.Frame(root, bg=COLORS["dark_blue"])
    main_frame.pack(fill="both", expand=True, padx=15, pady=10)

    # Left Panel - System Monitoring with modern cards
    left_frame = tk.Frame(main_frame, bg=COLORS["navy_blue"], relief="flat", bd=0)
    left_frame.pack(side="left", fill="y", padx=(0, 10))

    # System Monitoring Card
    monitor_card = tk.Frame(left_frame, bg=COLORS["navy_blue"], relief="flat", bd=1, highlightbackground=COLORS["medium_blue"], highlightthickness=1)
    monitor_card.pack(fill="x", pady=(0, 10))

    monitor_title = tk.Label(monitor_card, text="SYSTEM MONITOR", 
                            font=("Arial", 12, "bold"), 
                            bg=COLORS["navy_blue"], 
                            fg=COLORS["accent_yellow"])
    monitor_title.pack(pady=15)

    # System Info Display with improved styling
    info_frame = tk.Frame(monitor_card, bg=COLORS["navy_blue"])
    info_frame.pack(fill="both", expand=True, padx=15, pady=10)

    # CPU Usage with modern progress bar
    cpu_card = tk.Frame(info_frame, bg=COLORS["navy_blue"], relief="flat", bd=1, highlightbackground=COLORS["medium_blue"], highlightthickness=1)
    cpu_card.pack(fill="x", pady=8, padx=5)
    tk.Label(cpu_card, text="CPU USAGE", font=("Arial", 10, "bold"), 
            bg=COLORS["navy_blue"], fg=COLORS["off_white"]).pack(anchor="w", padx=10, pady=(10, 5))
    cpu_label = tk.Label(cpu_card, text="CPU: 0%", font=("Arial", 9), 
                        bg=COLORS["navy_blue"], fg=COLORS["light_blue"])
    cpu_label.pack(anchor="w", padx=10)
    cpu_bar = ttk.Progressbar(cpu_card, orient="horizontal", length=200, mode="determinate")
    cpu_bar.pack(fill="x", padx=10, pady=(5, 10))

    # Memory Usage
    memory_card = tk.Frame(info_frame, bg=COLORS["navy_blue"], relief="flat", bd=1, highlightbackground=COLORS["medium_blue"], highlightthickness=1)
    memory_card.pack(fill="x", pady=8, padx=5)
    tk.Label(memory_card, text="MEMORY USAGE", font=("Arial", 10, "bold"), 
            bg=COLORS["navy_blue"], fg=COLORS["off_white"]).pack(anchor="w", padx=10, pady=(10, 5))
    memory_label = tk.Label(memory_card, text="RAM: 0/0GB (0%)", font=("Arial", 9), 
                           bg=COLORS["navy_blue"], fg=COLORS["light_blue"])
    memory_label.pack(anchor="w", padx=10)
    memory_bar = ttk.Progressbar(memory_card, orient="horizontal", length=200, mode="determinate")
    memory_bar.pack(fill="x", padx=10, pady=(5, 10))

    # Disk Usage
    disk_card = tk.Frame(info_frame, bg=COLORS["navy_blue"], relief="flat", bd=1, highlightbackground=COLORS["medium_blue"], highlightthickness=1)
    disk_card.pack(fill="x", pady=8, padx=5)
    tk.Label(disk_card, text="DISK USAGE", font=("Arial", 10, "bold"), 
            bg=COLORS["navy_blue"], fg=COLORS["off_white"]).pack(anchor="w", padx=10, pady=(10, 5))
    disk_label = tk.Label(disk_card, text="Disk: 0/0GB (0%)", font=("Arial", 9), 
                         bg=COLORS["navy_blue"], fg=COLORS["light_blue"])
    disk_label.pack(anchor="w", padx=10)
    disk_bar = ttk.Progressbar(disk_card, orient="horizontal", length=200, mode="determinate")
    disk_bar.pack(fill="x", padx=10, pady=(5, 10))

    # Additional System Info
    additional_card = tk.Frame(info_frame, bg=COLORS["navy_blue"], relief="flat", bd=1, highlightbackground=COLORS["medium_blue"], highlightthickness=1)
    additional_card.pack(fill="x", pady=8, padx=5)
    tk.Label(additional_card, text="SYSTEM INFO", font=("Arial", 10, "bold"), 
            bg=COLORS["navy_blue"], fg=COLORS["off_white"]).pack(anchor="w", padx=10, pady=(10, 5))
    
    uptime_label = tk.Label(additional_card, text="Uptime: 00:00:00", font=("Arial", 9), 
                           bg=COLORS["navy_blue"], fg=COLORS["light_blue"])
    uptime_label.pack(anchor="w", padx=10, pady=2)
    
    os_label = tk.Label(additional_card, text="OS: Unknown", font=("Arial", 9), 
                       bg=COLORS["navy_blue"], fg=COLORS["light_blue"])
    os_label.pack(anchor="w", padx=10, pady=2)

    # Right Panel - Chat and Controls with modern design
    right_frame = tk.Frame(main_frame, bg=COLORS["dark_blue"])
    right_frame.pack(side="right", fill="both", expand=True)

    # Chat Display Card
    chat_card = tk.Frame(right_frame, bg=COLORS["navy_blue"], relief="flat", bd=1, highlightbackground=COLORS["medium_blue"], highlightthickness=1)
    chat_card.pack(fill="both", expand=True, pady=(0, 10))

    chat_header = tk.Frame(chat_card, bg=COLORS["navy_blue"])
    chat_header.pack(fill="x", padx=15, pady=10)

    chat_label = tk.Label(chat_header, text="Conversation Log", font=("Arial", 14, "bold"), 
                         bg=COLORS["navy_blue"], fg=COLORS["off_white"])
    chat_label.pack(side="left")

    # Modern text display
    text_display = scrolledtext.ScrolledText(chat_card, wrap=tk.WORD, width=70, height=20, 
                                            font=("Consolas", 10),
                                            bg="#1a1f2e", fg=COLORS["off_white"],
                                            insertbackground=COLORS["off_white"],
                                            relief="flat", bd=0,
                                            padx=15, pady=15)
    text_display.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    # Controls Frame with modern buttons
    controls_card = tk.Frame(right_frame, bg=COLORS["navy_blue"], relief="flat", bd=1, highlightbackground=COLORS["medium_blue"], highlightthickness=1)
    controls_card.pack(fill="x", pady=10)

    controls_frame = tk.Frame(controls_card, bg=COLORS["navy_blue"])
    controls_frame.pack(fill="both", padx=20, pady=20)

    # Modern button style function
    def create_modern_button(parent, text, command, bg_color, hover_color, width=14):
        btn = tk.Button(parent, text=text, command=command,
                       font=("Arial", 11, "bold"),
                       bg=bg_color, fg=COLORS["off_white"],
                       width=width, height=1,
                       relief="flat", bd=0,
                       cursor="hand2")
        
        def on_enter(e):
            btn['bg'] = hover_color
        def on_leave(e):
            btn['bg'] = bg_color
            
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn

    # Button grid with modern styling
    start_btn = create_modern_button(controls_frame, "🎤 Start Listening", 
                                    start_thread, 
                                    COLORS["accent_green"], "#34c759")
    start_btn.grid(row=0, column=0, padx=8, pady=8)

    vault_btn = create_modern_button(controls_frame, "🔒 Secure Vault", 
                                    open_vault, 
                                    COLORS["accent_yellow"], "#ffd166")
    vault_btn.grid(row=0, column=1, padx=8, pady=8)

    exit_btn = create_modern_button(controls_frame, "⏻ Exit", 
                                   root.quit, 
                                   COLORS["accent_red"], "#ff6b6b")
    exit_btn.grid(row=0, column=2, padx=8, pady=8)

    # Additional info buttons row
    additional_frame = tk.Frame(controls_frame, bg=COLORS["navy_blue"])
    additional_frame.grid(row=1, column=0, columnspan=3, pady=10)

    system_info_btn = create_modern_button(additional_frame, "📊 System Info", 
                                          lambda: messagebox.showinfo("System Info", "Real-time system monitoring is displayed on the left panel"), 
                                          COLORS["medium_blue"], "#5a7aa7", width=16)
    system_info_btn.grid(row=0, column=0, padx=5)

    help_btn = create_modern_button(additional_frame, "❓ Help", 
                                   lambda: messagebox.showinfo("Help", "Voice Commands:\n• 'Hello' - Greeting\n• 'Open/Close [app]' - Control applications\n• 'Google/Youtube [query]' - Search\n• 'Volume up/down' - Adjust volume\n• 'Sleep mode' - Pause assistant"), 
                                   COLORS["medium_blue"], "#5a7aa7", width=16)
    help_btn.grid(row=0, column=1, padx=5)

    # Status Bar with modern design
    status_frame = tk.Frame(root, bg=COLORS["navy_blue"], height=30, relief='flat', bd=0)
    status_frame.pack(fill="x", side="bottom")
    status_frame.pack_propagate(False)

    status_content = tk.Frame(status_frame, bg=COLORS["navy_blue"])
    status_content.pack(fill='both', padx=15)

    status_label = tk.Label(status_content, text="🟢 System Ready - Desktop Assistant Active", 
                           font=("Arial", 9), 
                           bg=COLORS["navy_blue"], 
                           fg=COLORS["off_white"])
    status_label.pack(side="left")

    # Time display
    time_label = tk.Label(status_content, text="", 
                         font=("Arial", 9), 
                         bg=COLORS["navy_blue"], 
                         fg=COLORS["light_blue"])
    time_label.pack(side="right")

    def update_time():
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        time_label.config(text=f"🕒 {current_time}")
        try:
            if root and root.winfo_exists():
                root.after(1000, update_time)
        except:
            pass

    # Configure ttk style for modern progress bars
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("Horizontal.TProgressbar", 
                    background=COLORS["accent_green"],
                    troughcolor=COLORS["navy_blue"],
                    bordercolor=COLORS["medium_blue"],
                    lightcolor=COLORS["accent_green"],
                    darkcolor=COLORS["accent_green"])

    # Start monitoring and time updates
    root.after(100, lambda: update_system_info_func(
        cpu_label, memory_label, disk_label, uptime_label, os_label, 
        cpu_bar, memory_bar, disk_bar
    ))
    update_time()

    return root, text_display