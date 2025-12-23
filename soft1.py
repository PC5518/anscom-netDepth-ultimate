import customtkinter as ctk
import threading
import speedtest
import psutil
import socket
import requests
import time
import platform
import subprocess
import re
import uuid
import numpy as np
from collections import deque
from datetime import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# --- Theme Configuration ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# --- Constants ---
# Color Palette for Graphs
GRAPH_BG = "#212121"
LINE_COLOR_1 = "#00ffcc" # Cyan for Latency
LINE_COLOR_2 = "#ff9900" # Orange for Jitter
TEXT_COLOR = "#e0e0e0"

class MetricBox(ctk.CTkFrame):
    def __init__(self, master, title, icon_text="📊", width=160):
        super().__init__(master, width=width)
        self.configure(fg_color="#1a1a1a", corner_radius=6, border_width=1, border_color="#333333")
        self.grid_columnconfigure(0, weight=1)
        
        self.title_label = ctk.CTkLabel(self, text=title.upper(), font=("Roboto", 9, "bold"), text_color="#777777")
        self.title_label.grid(row=0, column=0, sticky="w", padx=10, pady=(5, 0))
        
        self.value_label = ctk.CTkLabel(self, text="-", font=("Roboto Mono", 16, "bold"), text_color="white")
        self.value_label.grid(row=1, column=0, sticky="w", padx=10, pady=(0, 0))
        
        self.unit_label = ctk.CTkLabel(self, text="...", font=("Roboto", 9), text_color="#555555")
        self.unit_label.grid(row=2, column=0, sticky="w", padx=10, pady=(0, 5))

    def update(self, value, unit=None, color=None):
        self.value_label.configure(text=str(value))
        if color: self.value_label.configure(text_color=color)
        if unit: self.unit_label.configure(text=unit)

class LiveGraph(ctk.CTkFrame):
    def __init__(self, master, title, y_label):
        super().__init__(master, fg_color="#212121")
        self.title = title
        
        # Data Buffers (Store last 60 points)
        self.x_data = list(range(60))
        self.y_data = deque([0]*60, maxlen=60)
        self.y_data2 = deque([0]*60, maxlen=60) # Secondary line (e.g. Average)

        # Matplotlib Setup
        self.fig = Figure(figsize=(5, 2.5), dpi=100, facecolor=GRAPH_BG)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor(GRAPH_BG)
        
        # Styling
        self.ax.tick_params(axis='x', colors=TEXT_COLOR, labelsize=7)
        self.ax.tick_params(axis='y', colors=TEXT_COLOR, labelsize=7)
        self.ax.spines['bottom'].set_color('#444')
        self.ax.spines['top'].set_color('#444') 
        self.ax.spines['left'].set_color('#444')
        self.ax.spines['right'].set_color('#444')
        self.ax.set_title(title, color=TEXT_COLOR, fontsize=9)
        self.ax.grid(True, color='#333', linestyle='--', linewidth=0.5)

        # Initial Lines
        self.line1, = self.ax.plot(self.x_data, self.y_data, color=LINE_COLOR_1, linewidth=1.5)
        self.line2, = self.ax.plot(self.x_data, self.y_data2, color=LINE_COLOR_2, linewidth=1, linestyle="--", alpha=0.5)

        # Canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def update_graph(self, new_val, avg_val=None):
        self.y_data.append(new_val)
        if avg_val is not None:
            self.y_data2.append(avg_val)
        else:
            self.y_data2.append(new_val)
            
        self.line1.set_ydata(self.y_data)
        self.line2.set_ydata(self.y_data2)
        
        # Dynamic Scaling
        curr_max = max(max(self.y_data), max(self.y_data2))
        self.ax.set_ylim(0, curr_max * 1.2 if curr_max > 0 else 10)
        
        self.canvas.draw()

class UltimateNetAnalyzer(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("NETDEPTH ULTIMATE // 24/7 NETWORK MONITOR")
        self.geometry("1400x900")
        
        # State
        self.running = False
        self.continuous_mode = False
        self.latency_history = deque([], maxlen=100)
        self.start_time = time.time()
        
        # --- Layout ---
        self.grid_columnconfigure(0, weight=3) # Main Dashboard
        self.grid_columnconfigure(1, weight=1) # Sidebar controls
        self.grid_rowconfigure(1, weight=1)

        # Header
        self.header = ctk.CTkFrame(self, height=50, fg_color="transparent")
        self.header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=10)
        ctk.CTkLabel(self.header, text="AnsCom NETWORK TELEMETRY DECK", font=("Arial", 20, "bold")).pack(side="left")
        self.status_lbl = ctk.CTkLabel(self.header, text="READY", text_color="#00ffcc")
        self.status_lbl.pack(side="left", padx=20)

        # Main Scrollable Area
        self.main_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_scroll.grid(row=1, column=0, sticky="nsew", padx=10)
        
        # 1. Graphs Section
        self.graph_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        self.graph_frame.pack(fill="x", pady=10)
        
        self.ping_graph = LiveGraph(self.graph_frame, "LIVE LATENCY (ms) + AVG", "ms")
        self.ping_graph.pack(side="left", fill="both", expand=True, padx=5)
        
        self.net_usage_graph = LiveGraph(self.graph_frame, "BANDWIDTH USAGE (MB/s)", "MB/s")
        self.net_usage_graph.pack(side="left", fill="both", expand=True, padx=5)

        # 2. Metric Categories
        self.create_metric_grid()

        # Sidebar Controls
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=1, column=1, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="CONTROLS", font=("Roboto", 14, "bold")).pack(pady=20)
        
        self.btn_run_full = ctk.CTkButton(self.sidebar, text="RUN FULL AUDIT", fg_color="#009900", command=self.run_full_audit)
        self.btn_run_full.pack(pady=10, padx=20, fill="x")
        
        self.switch_monitor = ctk.CTkSwitch(self.sidebar, text="24/7 LIVE MONITOR", command=self.toggle_monitoring)
        self.switch_monitor.pack(pady=10, padx=20, anchor="w")

        ctk.CTkLabel(self.sidebar, text="LOGS", font=("Roboto", 12)).pack(pady=(20,5))
        self.log_box = ctk.CTkTextbox(self.sidebar, height=400, font=("Consolas", 10))
        self.log_box.pack(pady=5, padx=10, fill="x")

        # Initialize Data
        self.metrics_map = {}
        self.last_net_io = psutil.net_io_counters()

    def create_metric_grid(self):
        # We need lots of boxes. Let's categorize them.
        categories = {
            "SPEED & BANDWIDTH": [
                "Download Spd", "Upload Spd", "Bytes Sent", "Bytes Recv", 
                "Live Send Rate", "Live Recv Rate", "Peak Download", "Peak Upload"
            ],
            "LATENCY & STABILITY": [
                "Ping (Live)", "Jitter", "Packet Loss", "Stability (StdDev)", 
                "Avg Ping (3s)", "Avg Ping (10s)", "Min Ping", "Max Ping"
            ],
            "CONNECTION QUALITY": [
                "Signal Strength", "WiFi SSID", "Gateway Latency", "DNS Latency",
                "Interface Err In", "Interface Err Out", "Drop In", "Drop Out"
            ],
            "IDENTITY & GEO": [
                "Internal IP", "External IP", "MAC Address", "Hostname",
                "ISP Org", "City", "Region", "Timezone"
            ],
            "HARDWARE HEALTH": [
                "CPU Usage", "RAM Usage", "Active Threads", "Uptime",
                "Interface Name", "DNS Server", "Gateway IP", "Protocol"
            ]
        }
        
        self.box_refs = {}
        
        for cat_name, items in categories.items():
            # Category Header
            head = ctk.CTkLabel(self.main_scroll, text=f"// {cat_name}", font=("Roboto", 12, "bold"), anchor="w", text_color="#888")
            head.pack(fill="x", padx=10, pady=(20, 5))
            
            # Grid Frame
            grid_f = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
            grid_f.pack(fill="x", padx=5)
            
            # Create Boxes (4 columns)
            for i, item in enumerate(items):
                box = MetricBox(grid_f, title=item)
                row = i // 4
                col = i % 4
                box.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
                grid_f.grid_columnconfigure(col, weight=1)
                self.box_refs[item] = box

    def log(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_box.insert("0.0", f"[{timestamp}] {msg}\n")

    def toggle_monitoring(self):
        if self.switch_monitor.get() == 1:
            self.running = True
            threading.Thread(target=self.live_monitor_loop, daemon=True).start()
            self.status_lbl.configure(text="LIVE MONITORING ACTIVE                                                                                   Powered by AnsCom             ", text_color="#00ffcc")
            self.log("Live monitoring started.")
        else:
            self.running = False
            self.status_lbl.configure(text="IDLE", text_color="gray")
            self.log("Monitoring paused.")

    def live_monitor_loop(self):
        """Runs every 1 second to update live stats without heavy speedtest"""
        while self.running:
            try:
                # 1. Hardware Stats
                cpu = psutil.cpu_percent()
                ram = psutil.virtual_memory().percent
                self.box_refs["CPU Usage"].update(f"{cpu}%", "Load")
                self.box_refs["RAM Usage"].update(f"{ram}%", "Used")
                self.box_refs["Active Threads"].update(threading.active_count(), "Threads")
                
                uptime = int(time.time() - self.start_time)
                self.box_refs["Uptime"].update(f"{uptime}s", "Session")

                # 2. Network I/O (Throughput)
                curr_net_io = psutil.net_io_counters()
                sent_diff = curr_net_io.bytes_sent - self.last_net_io.bytes_sent
                recv_diff = curr_net_io.bytes_recv - self.last_net_io.bytes_recv
                
                self.last_net_io = curr_net_io
                
                # Update Totals
                self.box_refs["Bytes Sent"].update(f"{curr_net_io.bytes_sent/1024/1024:.1f}", "MB")
                self.box_refs["Bytes Recv"].update(f"{curr_net_io.bytes_recv/1024/1024:.1f}", "MB")
                
                # Update Live Rates
                sent_mbps = (sent_diff * 8) / 1_000_000
                recv_mbps = (recv_diff * 8) / 1_000_000
                self.box_refs["Live Send Rate"].update(f"{sent_mbps:.2f}", "Mbps")
                self.box_refs["Live Recv Rate"].update(f"{recv_mbps:.2f}", "Mbps")
                
                # Update Errors
                self.box_refs["Interface Err In"].update(curr_net_io.errin, "Count")
                self.box_refs["Drop In"].update(curr_net_io.dropin, "Count")

                # Graph Update (Throughput)
                self.net_usage_graph.update_graph(recv_mbps/8, sent_mbps/8) # Convert to MB/s for graph

                # 3. Latency Check (Lightweight Ping)
                st = time.time()
                try:
                    # Ping Google DNS via HTTP request (approximate but works everywhere)
                    requests.get("http://8.8.8.8", timeout=1)
                    lat = (time.time() - st) * 1000
                except:
                    lat = 0
                
                self.latency_history.append(lat)
                
                # Statistical Calcs
                if len(self.latency_history) > 0:
                    avg_3 = np.mean(list(self.latency_history)[-3:])
                    avg_10 = np.mean(list(self.latency_history)[-10:])
                    std_dev = np.std(list(self.latency_history))
                    jitter = abs(lat - avg_3)
                    
                    self.box_refs["Ping (Live)"].update(f"{lat:.1f}", "ms", "#00ffcc")
                    self.box_refs["Avg Ping (3s)"].update(f"{avg_3:.1f}", "ms")
                    self.box_refs["Avg Ping (10s)"].update(f"{avg_10:.1f}", "ms")
                    self.box_refs["Stability (StdDev)"].update(f"±{std_dev:.1f}", "ms")
                    self.box_refs["Jitter"].update(f"{jitter:.1f}", "ms")
                    self.box_refs["Min Ping"].update(f"{min(self.latency_history):.1f}", "ms")
                    self.box_refs["Max Ping"].update(f"{max(self.latency_history):.1f}", "ms")
                    
                    # Update Graph
                    self.ping_graph.update_graph(lat, avg_10)

            except Exception as e:
                print(e)
            
            time.sleep(1)

    def run_full_audit(self):
        """Runs the heavy speedtest in a separate thread"""
        self.btn_run_full.configure(state="disabled", text="SCANNING...")
        threading.Thread(target=self._perform_speedtest).start()

    def _perform_speedtest(self):
        self.log("Starting Full Speedtest Audit...")
        try:
            st = speedtest.Speedtest()
            
            self.log("Finding optimal server...")
            st.get_best_server()
            
            self.log("Testing Download...")
            dl = st.download() / 1_000_000
            self.box_refs["Download Spd"].update(f"{dl:.2f}", "Mbps", "#00ffcc")
            self.box_refs["Peak Download"].update(f"{dl:.2f}", "Mbps")
            
            self.log("Testing Upload...")
            ul = st.upload() / 1_000_000
            self.box_refs["Upload Spd"].update(f"{ul:.2f}", "Mbps", "#ff9900")
            self.box_refs["Peak Upload"].update(f"{ul:.2f}", "Mbps")
            
            # Fetch Geo Data
            self.log("Resolving Geo-Identity...")
            try:
                r = requests.get('https://ipinfo.io/json', timeout=3)
                data = r.json()
                self.box_refs["External IP"].update(data.get('ip', 'N/A'))
                self.box_refs["ISP Org"].update(data.get('org', 'N/A')[:15])
                self.box_refs["City"].update(data.get('city', 'N/A'))
                self.box_refs["Region"].update(data.get('region', 'N/A'))
                self.box_refs["Timezone"].update(data.get('timezone', 'N/A'))
            except:
                self.log("Geo-Identity Failed")

            # Local Info
            self.box_refs["Internal IP"].update(socket.gethostbyname(socket.gethostname()))
            self.box_refs["Hostname"].update(socket.gethostname())
            self.box_refs["MAC Address"].update(':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0,8*6,8)][::-1]).upper())

            self.log("Audit Complete.")

        except Exception as e:
            self.log(f"Speedtest Error: {e}")
        
        self.btn_run_full.configure(state="normal", text="RUN FULL AUDIT")

if __name__ == "__main__":
    app = UltimateNetAnalyzer()

    app.mainloop()
