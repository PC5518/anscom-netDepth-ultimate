# anscom-netDepth-ultimate
A high-performance, multi-threaded network telemetry dashboard built with Python, CustomTkinter, and Matplotlib. Monitors 40+ metrics in real-time. -->> use soft1.py to run the code.
# 🌐 NetDepth Ultimate
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

**NetDepth Ultimate** is a professional-grade network analysis tool designed to visualize deep telemetry data. Unlike standard speed tests, NetDepth runs a **dual-threaded engine** that monitors connection stability, hardware health, and bandwidth throughput in real-time without freezing the UI.
## My overview demo video explained: https://youtu.be/Okklr9g9bYw

## System Design   
<img width="1719" height="892" alt="image" src="https://github.com/user-attachments/assets/39003bca-60f3-40ae-a6ab-be56bcdabf83" />

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

**NetDepth Ultimate** is a professional-grade network analysis tool designed to visualize deep telemetry data. Unlike standard speed tests, NetDepth runs a **dual-threaded engine** that monitors connection stability, hardware health, and bandwidth throughput in real-time without freezing the UI.
<img width="1919" height="1018" alt="image" src="https://github.com/user-attachments/assets/464f76c3-c9ca-44fb-a9e6-c7994993961d" /> <img width="1919" height="1017" alt="image" src="https://github.com/user-attachments/assets/b3de1880-0d0c-4e12-bd6e-c72814490028" />

## ⚠️NOTE:
🐍 Standard Libraries (Do NOT install these)
These come pre-installed with Python. You do not need to do anything for them.
threading (Runs code in parallel)
socket (Network connections)
time (Time delays)
platform (OS detection)
subprocess (Running system commands)
re (Regular expressions/text searching)
uuid (Getting MAC address)
collections (Specifically deque for the moving graph buffer)
datetime (Timestamps)

### 📦 External Libraries (You MUST install these)

These are not included with Python by default.

| Import Name | Pip Package Name | Usage |
| :--- | :--- | :--- |
| `customtkinter` | `customtkinter` | The modern, dark-mode GUI framework. |
| `speedtest` | **`speedtest-cli`** | Performs the upload/download bandwidth test. <br>*(⚠️ Note: Install `speedtest-cli`, not `speedtest`)* |
| `psutil` | `psutil` | Fetches system stats like CPU, RAM, and network usage. |
| `requests` | `requests` | HTTP library used here to fetch Geo-IP data. |
| `numpy` | `numpy` | Math library used for calculating averages and standard deviation. |
| `matplotlib` | `matplotlib` | Used to draw the live moving graphs. |



## ✨ Key Features

### 📊 Live Visualization
- **Real-Time Graphs:** Embedded `Matplotlib` charts tracking latency (ms) and bandwidth usage (MB/s) at 60 FPS.
- **Statistical Analysis:** Automatic calculation of **Jitter**, **Standard Deviation (Stability)**, and **Moving Averages (SMA-3/SMA-10)**.

### 🚀 Dual-Engine Architecture
1.  **Monitor Thread (24/7):** Lightweight background loop checking generic latency, packet loss, and CPU/RAM health every second.
2.  **Audit Thread:** On-demand heavy bandwidth stress testing (Download/Upload) via `speedtest-cli`.

### 🛡️ Deep Telemetry (40+ Metrics)
- **Identity:** Internal/External IP, MAC Address, Hostname, ISP Organization.
- **Geo-Location:** City, Region, Timezone mapping.
- **Hardware:** Active Interface, CPU Load, RAM Usage, Thread Count.
- **Connection:** Bytes Sent/Recv, Live Data Rates, Error Packets, Drops.

## 📦 Installation

Ensure you have Python installed. Clone the repository and install the dependencies:

```bash
git clone https://github.com/YOUR_USERNAME/NetDepth-Ultimate.git
cd NetDepth-Ultimate
pip install customtkinter speedtest-cli psutil requests matplotlib numpy
