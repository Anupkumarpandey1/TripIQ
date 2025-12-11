import socket
import sys
import numpy as np
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLineEdit, QLabel, QFrame, QGroupBox, QSlider, QStackedWidget)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QPalette, QColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.animation import FuncAnimation

# ========= ESP INPUT ==========
ESP_IP = "10.116.213.78"
PORT = 5000

# ========= DATA ARRAYS =========
temp = []
curr = []
time_vals = []

# ========= SOCKET CONNECTION =========
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((ESP_IP, PORT))
print("Connected to ESP server...\nPlotting Live Graph...\n")

buffer = ""

# ========= PYQT5 WINDOW ==========
class LivePlot(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("📊 ESP32 Live Sensor Monitor")
        self.resize(1200, 850)
        
        # Power factor value and animation time
        self.power_factor = 0.8
        self.animation_time = 0
        
        # Set modern dark theme
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e2e;
                color: #cdd6f4;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
                background-color: #89b4fa;
                color: #1e1e2e;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #74c7ec;
            }
            QPushButton:pressed {
                background-color: #89dceb;
            }
            QPushButton:disabled {
                background-color: #45475a;
                color: #6c7086;
            }
            QPushButton#active {
                background-color: #a6e3a1;
                color: #1e1e2e;
            }
            QLineEdit {
                background-color: #313244;
                color: #cdd6f4;
                border: 2px solid #45475a;
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #89b4fa;
            }
            QLabel {
                color: #cdd6f4;
                font-size: 13px;
            }
            QGroupBox {
                border: 2px solid #45475a;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
                color: #89b4fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #45475a;
                height: 8px;
                background: #313244;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #89b4fa;
                border: 2px solid #74c7ec;
                width: 20px;
                height: 20px;
                margin: -7px 0;
                border-radius: 10px;
            }
            QSlider::handle:horizontal:hover {
                background: #74c7ec;
            }
            QSlider::sub-page:horizontal {
                background: #89b4fa;
                border-radius: 4px;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # ========= HEADER ==========
        header = QLabel("🔌 ESP32 Real-Time Data Monitor")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #89b4fa;
            padding: 10px;
        """)
        main_layout.addWidget(header)

        # ========= CONNECTION STATUS ==========
        self.status_label = QLabel(f"✅ Connected to {ESP_IP}:{PORT}")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            background-color: #313244;
            border-radius: 8px;
            padding: 8px;
            font-size: 12px;
            color: #a6e3a1;
        """)
        main_layout.addWidget(self.status_label)

        # ========= TAB NAVIGATION ==========
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(10)
        
        self.btn_power_view = QPushButton("⚡ Power Factor Analysis")
        self.btn_sensor_view = QPushButton("📊 Sensor Data Graphs")
        
        self.btn_power_view.setObjectName("active")
        
        self.btn_power_view.clicked.connect(lambda: self.switch_view(0))
        self.btn_sensor_view.clicked.connect(lambda: self.switch_view(1))
        
        nav_layout.addWidget(self.btn_power_view)
        nav_layout.addWidget(self.btn_sensor_view)
        
        main_layout.addLayout(nav_layout)

        # ========= STACKED WIDGET FOR VIEWS ==========
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget, stretch=1)

        # ========= VIEW 1: POWER FACTOR ANALYSIS ==========
        power_view = QWidget()
        power_layout = QVBoxLayout(power_view)
        power_layout.setSpacing(15)

        # Power Factor Control Group
        pf_group = QGroupBox("⚡ Power Factor Control")
        pf_layout = QVBoxLayout()
        
        # Power factor display and slider container
        pf_control_layout = QHBoxLayout()
        
        # Left side - Display values
        pf_display_layout = QVBoxLayout()
        
        self.pf_value_label = QLabel(f"Power Factor: {self.power_factor:.1f}")
        self.pf_value_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #f9e2af;
            padding: 5px;
        """)
        self.pf_value_label.setAlignment(Qt.AlignCenter)
        
        self.phase_diff_label = QLabel(f"Phase Difference: {self.calculate_phase_diff(self.power_factor):.1f}°")
        self.phase_diff_label.setStyleSheet("""
            font-size: 16px;
            color: #fab387;
            padding: 5px;
        """)
        self.phase_diff_label.setAlignment(Qt.AlignCenter)
        
        pf_display_layout.addWidget(self.pf_value_label)
        pf_display_layout.addWidget(self.phase_diff_label)
        
        # Right side - Slider
        pf_slider_layout = QVBoxLayout()
        
        slider_labels = QHBoxLayout()
        min_label = QLabel("0.5")
        min_label.setStyleSheet("color: #f38ba8; font-weight: bold;")
        max_label = QLabel("1.0")
        max_label.setStyleSheet("color: #a6e3a1; font-weight: bold;")
        slider_labels.addWidget(min_label)
        slider_labels.addStretch()
        slider_labels.addWidget(max_label)
        
        self.pf_slider = QSlider(Qt.Horizontal)
        self.pf_slider.setMinimum(50)
        self.pf_slider.setMaximum(100)
        self.pf_slider.setValue(80)
        self.pf_slider.setTickPosition(QSlider.TicksBelow)
        self.pf_slider.setTickInterval(5)
        self.pf_slider.valueChanged.connect(self.update_power_factor)
        
        pf_slider_layout.addLayout(slider_labels)
        pf_slider_layout.addWidget(self.pf_slider)
        
        pf_control_layout.addLayout(pf_display_layout, 1)
        pf_control_layout.addLayout(pf_slider_layout, 2)
        
        pf_layout.addLayout(pf_control_layout)
        
        # Waveform canvas for voltage and current (animated)
        self.fig_waveform, self.ax_waveform = plt.subplots(figsize=(12, 5), facecolor='#1e1e2e')
        self.ax_waveform.set_facecolor('#313244')
        self.canvas_waveform = FigureCanvas(self.fig_waveform)
        self.canvas_waveform.setMinimumHeight(400)
        pf_layout.addWidget(self.canvas_waveform)
        
        pf_group.setLayout(pf_layout)
        power_layout.addWidget(pf_group)

        self.stacked_widget.addWidget(power_view)

        # ========= VIEW 2: SENSOR DATA GRAPHS ==========
        sensor_view = QWidget()
        sensor_layout = QVBoxLayout(sensor_view)
        sensor_layout.setSpacing(15)

        # Graph Canvas
        graph_group = QGroupBox("📈 Live Data Visualization")
        graph_layout = QVBoxLayout()
        
        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots(facecolor='#1e1e2e')
        self.ax.set_facecolor('#313244')
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setMinimumHeight(400)
        graph_layout.addWidget(self.canvas)
        
        graph_group.setLayout(graph_layout)
        sensor_layout.addWidget(graph_group)

        # Graph Control Buttons
        btn_group = QGroupBox("📊 Graph Selection")
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn1 = QPushButton("🌡️ Temp vs Time")
        self.btn2 = QPushButton("⚡ Current vs Time")
        self.btn3 = QPushButton("📉 Current vs Temp")

        btn_layout.addWidget(self.btn1)
        btn_layout.addWidget(self.btn2)
        btn_layout.addWidget(self.btn3)

        self.btn1.clicked.connect(self.plot_temp_time)
        self.btn2.clicked.connect(self.plot_curr_time)
        self.btn3.clicked.connect(self.plot_curr_temp)

        btn_group.setLayout(btn_layout)
        sensor_layout.addWidget(btn_group)

        # Data Display
        data_layout = QHBoxLayout()
        
        self.temp_label = QLabel("🌡️ Temp: -- °C")
        self.curr_label = QLabel("⚡ Current: -- mA")
        self.time_label = QLabel("⏱️ Time: -- s")
        
        for label in [self.temp_label, self.curr_label, self.time_label]:
            label.setStyleSheet("""
                background-color: #313244;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            """)
            label.setAlignment(Qt.AlignCenter)
            data_layout.addWidget(label)
        
        sensor_layout.addLayout(data_layout)

        self.stacked_widget.addWidget(sensor_view)

        # ========= SEND COMMAND SECTION (Bottom - Always Visible) ==========
        cmd_group = QGroupBox("📤 Send Command to ESP32")
        cmd_layout = QHBoxLayout()
        cmd_layout.setSpacing(10)

        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText("Enter command to send to microcontroller...")
        self.cmd_input.returnPressed.connect(self.send_command)
        
        self.send_btn = QPushButton("📨 Send")
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #a6e3a1;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #94e2d5;
            }
        """)
        self.send_btn.clicked.connect(self.send_command)

        cmd_layout.addWidget(self.cmd_input, stretch=4)
        cmd_layout.addWidget(self.send_btn, stretch=1)
        
        cmd_group.setLayout(cmd_layout)
        main_layout.addWidget(cmd_group)

        # ========= TIMERS ==========
        # Timer for data reading
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_data)
        self.timer.start(100)
        
        # Timer for waveform animation
        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self.animate_waveform)
        self.anim_timer.start(50)  # 20 FPS animation
        
        # Initialize first plot
        self.plot_temp_time()
        self.draw_waveform()

    # ===== SWITCH VIEW =====
    def switch_view(self, index):
        self.stacked_widget.setCurrentIndex(index)
        
        # Update button styles
        if index == 0:
            self.btn_power_view.setObjectName("active")
            self.btn_sensor_view.setObjectName("")
        else:
            self.btn_power_view.setObjectName("")
            self.btn_sensor_view.setObjectName("active")
        
        # Force style update
        self.btn_power_view.style().unpolish(self.btn_power_view)
        self.btn_power_view.style().polish(self.btn_power_view)
        self.btn_sensor_view.style().unpolish(self.btn_sensor_view)
        self.btn_sensor_view.style().polish(self.btn_sensor_view)

    # ===== CALCULATE PHASE DIFFERENCE =====
    def calculate_phase_diff(self, pf):
        """Calculate phase difference in degrees from power factor"""
        phase_rad = np.arccos(np.clip(pf, 0, 1))
        phase_deg = np.degrees(phase_rad)
        return phase_deg

    # ===== UPDATE POWER FACTOR =====
    def update_power_factor(self, value):
        self.power_factor = value / 100.0
        phase_diff = self.calculate_phase_diff(self.power_factor)
        
        self.pf_value_label.setText(f"Power Factor: {self.power_factor:.1f}")
        self.phase_diff_label.setText(f"Phase Difference: {phase_diff:.2f}°")
        
        # Send to ESP32
        self.send_power_factor_to_esp()

    # ===== SEND POWER FACTOR TO ESP32 =====
    def send_power_factor_to_esp(self):
        try:
            command = f"SET_PF:{self.power_factor:.3f}"
            client.sendall((command + "\n").encode())
            print(f"Sent power factor: {self.power_factor:.1f}")
        except Exception as e:
            print(f"Error sending power factor: {e}")

    # ===== ANIMATE WAVEFORM =====
    def animate_waveform(self):
        self.animation_time += 0.05
        if self.animation_time > 2 * np.pi:
            self.animation_time = 0
        self.draw_waveform()

    # ===== DRAW VOLTAGE AND CURRENT WAVEFORM (ANIMATED) =====
    def draw_waveform(self):
        self.ax_waveform.clear()
        
        # Generate time array for 2 complete cycles
        t = np.linspace(0, 4 * np.pi, 1000)
        
        # Voltage waveform (reference, phase = 0) - animated
        voltage = np.sin(t + self.animation_time)
        
        # Current waveform (lagging by phase difference) - animated
        phase_rad = np.arccos(np.clip(self.power_factor, 0, 1))
        current = np.sin(t - phase_rad + self.animation_time)
        
        # Plot waveforms
        self.ax_waveform.plot(t, voltage, color='#f38ba8', linewidth=3, label='Voltage', alpha=0.9)
        self.ax_waveform.plot(t, current, color='#a6e3a1', linewidth=3, label='Current', alpha=0.9)
        
        # Find peaks in visible range for annotation
        visible_range = slice(0, 500)
        voltage_peaks = np.where((voltage[1:-1] > voltage[:-2]) & (voltage[1:-1] > voltage[2:]))[0] + 1
        current_peaks = np.where((current[1:-1] > current[:-2]) & (current[1:-1] > current[2:]))[0] + 1
        
        if len(voltage_peaks) > 0 and len(current_peaks) > 0:
            v_peak_idx = voltage_peaks[0]
            c_peak_idx = current_peaks[0]
            
            # Draw vertical lines at peaks
            self.ax_waveform.axvline(x=t[v_peak_idx], color='#f38ba8', linestyle='--', alpha=0.4, linewidth=1.5)
            self.ax_waveform.axvline(x=t[c_peak_idx], color='#a6e3a1', linestyle='--', alpha=0.4, linewidth=1.5)
            
            # Phase difference arrow
            if c_peak_idx > v_peak_idx:
                arrow_y = -0.5
                self.ax_waveform.annotate('', xy=(t[c_peak_idx], arrow_y), xytext=(t[v_peak_idx], arrow_y),
                                          arrowprops=dict(arrowstyle='<->', color='#fab387', lw=2.5))
                
                phase_deg = self.calculate_phase_diff(self.power_factor)
                mid_point = (t[v_peak_idx] + t[c_peak_idx]) / 2
                self.ax_waveform.text(mid_point, arrow_y - 0.25, f'φ = {phase_deg:.1f}°', 
                                     color='#fab387', fontsize=12, ha='center', fontweight='bold',
                                     bbox=dict(boxstyle='round,pad=0.5', facecolor='#1e1e2e', 
                                              edgecolor='#fab387', linewidth=2))
        
        self.ax_waveform.set_xlabel("Time (radians)", fontsize=12, color='#cdd6f4', fontweight='bold')
        self.ax_waveform.set_ylabel("Amplitude", fontsize=12, color='#cdd6f4', fontweight='bold')
        self.ax_waveform.set_title(f"⚡ Live Voltage & Current Waveforms (PF = {self.power_factor:.1f})", 
                                   fontsize=14, color='#89b4fa', pad=15, fontweight='bold')
        self.ax_waveform.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
        self.ax_waveform.legend(loc='upper right', framealpha=0.9, facecolor='#313244', 
                               edgecolor='#89b4fa', fontsize=11, frameon=True)
        self.ax_waveform.set_ylim(-1.4, 1.4)
        self.ax_waveform.set_xlim(0, 4 * np.pi)
        self.ax_waveform.tick_params(colors='#cdd6f4', labelsize=10)
        
        self.fig_waveform.tight_layout()
        self.canvas_waveform.draw()

    # ===== SEND COMMAND TO ESP32 =====
    def send_command(self):
        command = self.cmd_input.text().strip()
        if command:
            try:
                client.sendall((command + "\n").encode())
                self.status_label.setText(f"✅ Sent: '{command}'")
                self.status_label.setStyleSheet("""
                    background-color: #313244;
                    border-radius: 8px;
                    padding: 8px;
                    font-size: 12px;
                    color: #a6e3a1;
                """)
                self.cmd_input.clear()
            except Exception as e:
                self.status_label.setText(f"❌ Error: {str(e)}")
                self.status_label.setStyleSheet("""
                    background-color: #313244;
                    border-radius: 8px;
                    padding: 8px;
                    font-size: 12px;
                    color: #f38ba8;
                """)

    # ===== SOCKET PARSER =====
    def read_data(self):
        global buffer
        try:
            chunk = client.recv(1024).decode()
            buffer += chunk

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)

                try:
                    x, y, z = map(int, line.split(","))
                    time_vals.append(x)
                    temp.append(y)
                    curr.append(z)
                    
                    # Update live data display
                    self.temp_label.setText(f"🌡️ Temp: {y} °C")
                    self.curr_label.setText(f"⚡ Current: {z} mA")
                    self.time_label.setText(f"⏱️ Time: {x} s")
                    
                    # Auto-refresh current graph
                    self.refresh_current_plot()

                except ValueError:
                    print("Invalid frame skipped:", line)

        except Exception as e:
            pass  # Silent fail for non-critical errors

    # ===== REFRESH CURRENT PLOT =====
    def refresh_current_plot(self):
        if hasattr(self, 'current_plot'):
            self.current_plot()

    # ========= GRAPH FUNCTIONS ==========
    def plot_temp_time(self):
        self.current_plot = self.plot_temp_time
        self.ax.clear()
        if len(time_vals) > 0:
            self.ax.plot(time_vals, temp, color='#f38ba8', linewidth=2.5, marker='o', 
                        markersize=5, markevery=max(1, len(time_vals)//20), alpha=0.9)
        self.ax.set_xlabel("Time (s)", fontsize=12, color='#cdd6f4', fontweight='bold')
        self.ax.set_ylabel("Temperature (°C)", fontsize=12, color='#cdd6f4', fontweight='bold')
        self.ax.set_title("🌡️ Temperature vs Time", fontsize=14, color='#89b4fa', pad=15, fontweight='bold')
        self.ax.grid(True, alpha=0.3, linestyle='--')
        self.ax.tick_params(colors='#cdd6f4')
        self.fig.tight_layout()
        self.canvas.draw()

    def plot_curr_time(self):
        self.current_plot = self.plot_curr_time
        self.ax.clear()
        if len(time_vals) > 0:
            self.ax.plot(time_vals, curr, color='#a6e3a1', linewidth=2.5, marker='o', 
                        markersize=5, markevery=max(1, len(time_vals)//20), alpha=0.9)
        self.ax.set_xlabel("Time (s)", fontsize=12, color='#cdd6f4', fontweight='bold')
        self.ax.set_ylabel("Current (mA)", fontsize=12, color='#cdd6f4', fontweight='bold')
        self.ax.set_title("⚡ Current vs Time", fontsize=14, color='#89b4fa', pad=15, fontweight='bold')
        self.ax.grid(True, alpha=0.3, linestyle='--')
        self.ax.tick_params(colors='#cdd6f4')
        self.fig.tight_layout()
        self.canvas.draw()

    def plot_curr_temp(self):
        self.current_plot = self.plot_curr_temp
        self.ax.clear()
        if len(temp) > 0:
            self.ax.plot(temp, curr, color='#89dceb', linewidth=2.5, marker='o', 
                        markersize=5, markevery=max(1, len(temp)//20), alpha=0.9)
        self.ax.set_xlabel("Temperature (°C)", fontsize=12, color='#cdd6f4', fontweight='bold')
        self.ax.set_ylabel("Current (mA)", fontsize=12, color='#cdd6f4', fontweight='bold')
        self.ax.set_title("📉 Current vs Temperature", fontsize=14, color='#89b4fa', pad=15, fontweight='bold')
        self.ax.grid(True, alpha=0.3, linestyle='--')
        self.ax.tick_params(colors='#cdd6f4')
        self.fig.tight_layout()
        self.canvas.draw()


# ========= MAIN APP ==========
app = QApplication(sys.argv)
window = LivePlot()
window.show()
sys.exit(app.exec())