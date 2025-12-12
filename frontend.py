"""
Enhanced Frontend for MCB Testing System
Integrates with backend.py for ESP32 communication
"""

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QStackedWidget,
                             QFrame, QScrollArea, QGridLayout, QTextEdit, QGraphicsDropShadowEffect,
                             QSizePolicy, QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox,
                             QGroupBox, QMessageBox, QDialog, QDialogButtonBox, QFormLayout)
from PyQt5.QtGui import (QFont, QColor)
from PyQt5.QtCore import (Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, QSize, 
                          QParallelAnimationGroup, QSequentialAnimationGroup)

# Import backend
from backend import ESP32Backend

# Color scheme (same as a1.py)
COLOR_BACKGROUND_PRIMARY = "#0A0E27"
COLOR_BACKGROUND_SECONDARY = "#151932"
COLOR_BACKGROUND_CARD = "#1A1F3A"
COLOR_BACKGROUND_ELEVATED = "#1F2544"

COLOR_PRIMARY = "#00D9FF"
COLOR_PRIMARY_DARK = "#00B8D4"
COLOR_PRIMARY_LIGHT = "#18FFFF"
COLOR_ACCENT = "#7C4DFF"
COLOR_ACCENT_LIGHT = "#B388FF"

COLOR_SUCCESS = "#00E676"
COLOR_WARNING = "#FFD600"
COLOR_DANGER = "#FF5252"
COLOR_INFO = "#2196F3"

COLOR_TEXT_PRIMARY = "#FFFFFF"
COLOR_TEXT_SECONDARY = "#B0B0B0"
COLOR_TEXT_MUTED = "#808080"

COLOR_BORDER = "#2A3150"
COLOR_BORDER_FOCUS = COLOR_PRIMARY


# ===== Test Configuration Dialog =====
class TestConfigDialog(QDialog):
    def __init__(self, test_name, parent=None):
        super().__init__(parent)
        self.test_name = test_name
        self.config_values = {}
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle(f"Configure {self.test_name}")
        self.setMinimumWidth(500)
        self.setStyleSheet(f"""
            QDialog {{
                background: {COLOR_BACKGROUND_CARD};
            }}
            QLabel {{
                color: {COLOR_TEXT_PRIMARY};
                font-size: 13px;
            }}
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
                background: {COLOR_BACKGROUND_ELEVATED};
                color: {COLOR_TEXT_PRIMARY};
                border: 2px solid {COLOR_BORDER};
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            }}
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
                border-color: {COLOR_PRIMARY};
            }}
            QPushButton {{
                background: {COLOR_PRIMARY};
                color: {COLOR_BACKGROUND_PRIMARY};
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: {COLOR_PRIMARY_LIGHT};
            }}
        """)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel(f"⚙️ {self.test_name} Configuration")
        title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {COLOR_PRIMARY};
            padding: 10px;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        # Different inputs based on test type
        if "Short-Circuit" in self.test_name or "R-XL" in self.test_name:
            # Merged: Short-Circuit + R-XL Configuration
            self.current_input = QSpinBox()
            self.current_input.setRange(1, 10000)
            self.current_input.setValue(1)
            self.current_input.setSuffix(" A")
            form_layout.addRow("Target Current:", self.current_input)
            
            self.power_factor = QComboBox()
            self.pf_values = ["0.5", "0.6", "0.7", "0.8", "0.9"]
            self.power_factor.addItems(self.pf_values)
            self.power_factor.setCurrentText("0.8")
            form_layout.addRow("Power Factor:", self.power_factor)
            
        elif "Variable Resistance and Inductance" in self.test_name:
            # Direct R-L Configuration
            self.resistance_input = QSpinBox()
            self.resistance_input.setRange(12, 50)
            self.resistance_input.setValue(25)
            self.resistance_input.setSuffix(" Ω")
            form_layout.addRow("Resistance:", self.resistance_input)
            
            self.inductance_input = QDoubleSpinBox()
            self.inductance_input.setRange(0.0000, 0.0214)
            self.inductance_input.setValue(0.0100)
            self.inductance_input.setSuffix(" H")
            self.inductance_input.setDecimals(4)
            form_layout.addRow("Inductance:", self.inductance_input)
            
        elif "Trip" in self.test_name:
            self.mcb_type = QComboBox()
            self.mcb_type.addItems(["B-Curve", "C-Curve", "D-Curve"])
            form_layout.addRow("MCB Curve Type:", self.mcb_type)
            
            self.current_rating = QSpinBox()
            self.current_rating.setRange(1, 100)
            self.current_rating.setValue(16)
            self.current_rating.setSuffix(" A")
            form_layout.addRow("MCB Current Rating:", self.current_rating)
            
        elif "Temperature" in self.test_name:
            self.rated_current = QSpinBox()
            self.rated_current.setRange(1, 100)
            self.rated_current.setValue(16)
            self.rated_current.setSuffix(" A")
            form_layout.addRow("Rated Current:", self.rated_current)
            
            self.duration = QSpinBox()
            self.duration.setRange(60, 14400)
            self.duration.setValue(3600)
            self.duration.setSuffix(" seconds")
            form_layout.addRow("Test Duration:", self.duration)
            
        elif "Dielectric" in self.test_name:
            self.test_voltage = QSpinBox()
            self.test_voltage.setRange(500, 5000)
            self.test_voltage.setValue(2000)
            self.test_voltage.setSuffix(" V")
            form_layout.addRow("Test Voltage:", self.test_voltage)
            
            self.duration = QSpinBox()
            self.duration.setRange(1, 60)
            self.duration.setValue(5)
            self.duration.setSuffix(" seconds")
            form_layout.addRow("Test Duration:", self.duration)
            
        elif "Breaking Time" in self.test_name:
            self.test_current = QSpinBox()
            self.test_current.setRange(100, 10000)
            self.test_current.setValue(1)
            self.test_current.setSuffix(" A")
            form_layout.addRow("Test Current:", self.test_current)
            
        elif "Contact Resistance" in self.test_name:
            self.test_current = QSpinBox()
            self.test_current.setRange(1, 100)
            self.test_current.setValue(16)
            self.test_current.setSuffix(" A")
            form_layout.addRow("Test Current:", self.test_current)
            
        elif "Calibration" in self.test_name:
            info_label = QLabel("This will calibrate all sensors and verify system accuracy.")
            info_label.setWordWrap(True)
            info_label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; padding: 10px;")
            form_layout.addRow(info_label)
        elif "Just a Test" in self.test_name:
            info_label = QLabel("This is for testing purposes only.")
            info_label.setWordWrap(True)
            info_label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; padding: 10px;")
            form_layout.addRow(info_label)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def get_config(self):
        """Get configuration values"""
        config = {}
        
        if "Short-Circuit" in self.test_name or "R-XL" in self.test_name:
            config['current'] = self.current_input.value()
            config['power_factor'] = float(self.power_factor.currentText())
            
        elif "Variable Resistance and Inductance" in self.test_name:
            config['resistance'] = self.resistance_input.value()
            config['inductance'] = self.inductance_input.value()
            
        elif "Trip" in self.test_name:
            config['mcb_type'] = self.mcb_type.currentText()[0]  # B, C, or D
            config['current_rating'] = self.current_rating.value()
            
        elif "Temperature" in self.test_name:
            config['rated_current'] = self.rated_current.value()
            config['duration'] = self.duration.value()
            
        elif "Dielectric" in self.test_name:
            config['test_voltage'] = self.test_voltage.value()
            config['duration'] = self.duration.value()
            
        elif "Breaking Time" in self.test_name:
            config['test_current'] = self.test_current.value()
            
        elif "Contact Resistance" in self.test_name:
            config['test_current'] = self.test_current.value()
            
        elif "Calibration" in self.test_name:
            config['calibrate'] = True
        elif "Just a Test" in self.test_name:
            config['test'] = True
        
        return config


# ===== Animated Stacked Widget (from a1.py) =====
class AnimatedStackedWidget(QStackedWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_duration = 400
        self.m_direction = Qt.Horizontal
        self.m_current_index = 0

    def slideIn(self, index):
        if index == self.m_current_index:
            return

        old_widget = self.widget(self.m_current_index)
        new_widget = self.widget(index)
        
        old_widget.resize(self.size())
        new_widget.resize(self.size())

        offset_x = self.width()

        if index > self.m_current_index:
            new_widget.move(offset_x, 0)
            new_pos = QPoint(-offset_x, 0)
        else:
            new_widget.move(-offset_x, 0)
            new_pos = QPoint(offset_x, 0)
        
        new_widget.show()
        new_widget.raise_()

        anim_old = QPropertyAnimation(old_widget, b"pos")
        anim_old.setDuration(self.m_duration)
        anim_old.setStartValue(QPoint(0, 0))
        anim_old.setEndValue(new_pos)
        anim_old.setEasingCurve(QEasingCurve.OutCubic)

        anim_new = QPropertyAnimation(new_widget, b"pos")
        anim_new.setDuration(self.m_duration)
        anim_new.setStartValue(new_widget.pos())
        anim_new.setEndValue(QPoint(0, 0))
        anim_new.setEasingCurve(QEasingCurve.OutCubic)

        self.anim_group = QParallelAnimationGroup()
        self.anim_group.addAnimation(anim_old)
        self.anim_group.addAnimation(anim_new)
        
        self.anim_group.finished.connect(lambda: self.setCurrentIndex(index))
        self.m_current_index = index
        self.anim_group.start()

    def setCurrentIndex(self, index):
        super().setCurrentIndex(index)


# ===== Modern Button (from a1.py) =====
class ModernButton(QPushButton):
    def __init__(self, text, primary=False, danger=False):
        super().__init__(text)
        self.primary = primary
        self.danger = danger
        self.setMinimumHeight(48)
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.update_style()
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)
        
    def update_style(self):
        if self.danger:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {COLOR_DANGER};
                    color: {COLOR_TEXT_PRIMARY};
                    border: none;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: 600;
                    padding: 12px 24px;
                }}
                QPushButton:hover {{
                    background: #FF6B6B;
                }}
                QPushButton:pressed {{
                    background: #E53935;
                }}
            """)
        elif self.primary:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                    stop:0 {COLOR_PRIMARY}, stop:1 {COLOR_PRIMARY_LIGHT});
                    color: {COLOR_BACKGROUND_PRIMARY};
                    border: none;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: 600;
                    padding: 12px 24px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                    stop:0 {COLOR_PRIMARY_LIGHT}, stop:1 #00E5FF);
                }}
                QPushButton:pressed {{
                    background: {COLOR_PRIMARY_DARK};
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {COLOR_BACKGROUND_ELEVATED};
                    color: {COLOR_PRIMARY};
                    border: 1px solid {COLOR_BORDER};
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: 500;
                    padding: 12px 24px;
                }}
                QPushButton:hover {{
                    background: {COLOR_BACKGROUND_CARD};
                    border-color: {COLOR_PRIMARY};
                }}
                QPushButton:pressed {{
                    background: {COLOR_BACKGROUND_SECONDARY};
                }}
            """)


# ===== Test Card (from a1.py) =====
class TestCard(QFrame):
    def __init__(self, title, description, icon_text, color_accent=COLOR_PRIMARY):
        super().__init__()
        self.color_accent = color_accent
        self.setFrameShape(QFrame.StyledPanel)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(160)
        self.setMaximumHeight(190)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 100))
        self.setGraphicsEffect(shadow)
        
        self.setStyleSheet(f"""
            QFrame {{
                background: {COLOR_BACKGROUND_CARD};
                border: 1px solid {COLOR_BORDER};
                border-radius: 12px;
                padding: 20px;
            }}
            QFrame:hover {{
                background: {COLOR_BACKGROUND_ELEVATED};
                border: 1px solid {self.color_accent};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Icon container
        icon_container = QFrame()
        icon_container.setMaximumSize(56, 56)
        icon_container.setMinimumSize(56, 56)
        icon_container.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 {self.color_accent}, stop:1 {COLOR_ACCENT});
                border-radius: 10px;
                border: none;
            }}
        """)
        icon_layout = QVBoxLayout()
        icon_layout.setContentsMargins(0, 0, 0, 0)
        
        icon_label = QLabel(icon_text)
        icon_label.setStyleSheet(f"""
            QLabel {{
                color: {COLOR_TEXT_PRIMARY};
                font-size: 26px;
                font-weight: bold;
                background: transparent;
                border: none;
            }}
        """)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(icon_label)
        icon_container.setLayout(icon_layout)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {COLOR_TEXT_PRIMARY};
                font-size: 15px;
                font-weight: 600;
                background: transparent;
                border: none;
                padding: 2px 0px;
            }}
        """)
        title_label.setWordWrap(True)
        title_label.setMinimumHeight(40)
        title_label.setMaximumHeight(50)
        title_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setStyleSheet(f"""
            QLabel {{
                color: {COLOR_TEXT_SECONDARY};
                font-size: 12px;
                background: transparent;
                border: none;
                line-height: 1.5;
                padding: 0px;
            }}
        """)
        desc_label.setWordWrap(True)
        desc_label.setMinimumHeight(35)
        desc_label.setMaximumHeight(45)
        desc_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        layout.addWidget(icon_container)
        layout.addSpacing(4)
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addStretch()
        
        self.setLayout(layout)


def set_global_style(app):
    app.setStyleSheet(f"""
        QMainWindow {{
            background: {COLOR_BACKGROUND_PRIMARY};
        }}
        
        QFrame#CardFrame {{
            background: {COLOR_BACKGROUND_CARD};
            border-radius: 16px;
            border: 1px solid {COLOR_BORDER};
            padding: 48px;
        }}

        QFrame#DashboardHeader, QFrame#TestDetailsHeader {{
            background: {COLOR_BACKGROUND_CARD};
            border-radius: 12px;
            padding: 24px 32px;
            border: 1px solid {COLOR_BORDER};
        }}
        
        QFrame#TestDetailsContainer {{
            background: {COLOR_BACKGROUND_CARD};
            border-radius: 12px;
            padding: 32px;
            border: 1px solid {COLOR_BORDER};
        }}

        QScrollArea {{
            border: none;
            background: {COLOR_BACKGROUND_PRIMARY};
        }}
        
        QScrollBar:vertical {{
            border: none;
            background: {COLOR_BACKGROUND_SECONDARY};
            width: 10px;
            border-radius: 5px;
            margin: 0px;
        }}
        QScrollBar::handle:vertical {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 {COLOR_PRIMARY}, stop:1 {COLOR_PRIMARY_LIGHT});
            border-radius: 5px;
            min-height: 30px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {COLOR_PRIMARY_LIGHT};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
        }}
        
        QTextEdit {{
            border: none;
            background: transparent;
            font-size: 14px;
            color: {COLOR_TEXT_SECONDARY};
            line-height: 1.7;
            selection-background-color: {COLOR_PRIMARY};
            selection-color: {COLOR_BACKGROUND_PRIMARY};
        }}
    """)



from tcp_client import TCPClient
import numpy as np
from collections import deque

# ===== Power Factor Visualization Window (Standalone - Exact copy of recieve.py) =====
class PowerFactorWindow(QMainWindow):
    def __init__(self, current_value, power_factor, backend, parent=None):
        super().__init__(parent)
        self.current_value = current_value
        self.power_factor = power_factor
        self.backend = backend
        
        # Data storage
        self.voltage_data = deque(maxlen=500) # Store last 500 voltage points
        self.time_data = deque(maxlen=500) # Corresponding time points
        self.start_time = None

        # TCP Client
        self.tcp_client = TCPClient(host="10.91.136.24", port=8888)
        self.tcp_client.new_voltage_data.connect(self.handle_new_data)
        self.tcp_client.connection_status_changed.connect(self.update_connection_status)
        
        self.setWindowTitle("⚡ ESP32 Power Factor Monitor")
        self.resize(1200, 850)
        
        # Exact same dark theme as recieve.py
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
        
        # Create central widget for QMainWindow
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QLabel("🔌 Power Factor Real-Time Analysis")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #89b4fa;
            padding: 10px;
        """)
        main_layout.addWidget(header)
        
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
        
        import numpy as np
        phase_diff = np.degrees(np.arccos(np.clip(self.power_factor, 0, 1)))
        self.phase_diff_label = QLabel(f"Phase Difference: {phase_diff:.1f}°")
        self.phase_diff_label.setStyleSheet("""
            font-size: 16px;
            color: #fab387;
            padding: 5px;
        """)
        self.phase_diff_label.setAlignment(Qt.AlignCenter)

        # Current input
        current_layout = QHBoxLayout()
        current_label = QLabel("Current (A):")
        self.current_input = QSpinBox()
        self.current_input.setRange(1, 10000)
        self.current_input.setValue(self.current_value)
        self.current_input.valueChanged.connect(self.update_current)
        current_layout.addWidget(current_label)
        current_layout.addWidget(self.current_input)

        # Connection Status & Button
        self.connection_status_label = QLabel("Status: Disconnected")
        self.connection_status_label.setStyleSheet("color: #f38ba8; font-weight: bold;")
        self.connect_button = QPushButton("Connect to ESP32")
        self.connect_button.clicked.connect(self.toggle_connection)
        
        pf_display_layout.addWidget(self.pf_value_label)
        pf_display_layout.addWidget(self.phase_diff_label)
        pf_display_layout.addLayout(current_layout)
        pf_display_layout.addSpacing(10)
        pf_display_layout.addWidget(self.connection_status_label)
        pf_display_layout.addWidget(self.connect_button)
        
        # Right side - Slider
        pf_slider_layout = QVBoxLayout()
        
        slider_labels = QHBoxLayout()
        min_label = QLabel("0.5")
        min_label.setStyleSheet("color: #f38ba8; font-weight: bold;")
        max_label = QLabel("0.9")
        max_label.setStyleSheet("color: #a6e3a1; font-weight: bold;")
        slider_labels.addWidget(min_label)
        slider_labels.addStretch()
        slider_labels.addWidget(max_label)
        
        from PyQt5.QtWidgets import QSlider
        self.pf_values = [0.5, 0.6, 0.7, 0.8, 0.9]
        self.pf_slider = QSlider(Qt.Horizontal)
        self.pf_slider.setMinimum(0)
        self.pf_slider.setMaximum(len(self.pf_values) - 1)
        try:
            initial_index = self.pf_values.index(self.power_factor)
        except ValueError:
            initial_index = min(range(len(self.pf_values)), key=lambda i: abs(self.pf_values[i]-self.power_factor))
        self.pf_slider.setValue(initial_index)
        self.pf_slider.setTickPosition(QSlider.TicksBelow)
        self.pf_slider.setTickInterval(1)
        self.pf_slider.valueChanged.connect(self.update_power_factor)
        
        pf_slider_layout.addLayout(slider_labels)
        pf_slider_layout.addWidget(self.pf_slider)
        
        pf_control_layout.addLayout(pf_display_layout, 1)
        pf_control_layout.addLayout(pf_slider_layout, 2)
        
        pf_layout.addLayout(pf_control_layout)
        
        # Waveform canvas
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
            import time

            self.fig_waveform, self.ax_waveform = plt.subplots(figsize=(12, 5), facecolor='#1e1e2e')
            self.ax_waveform.set_facecolor('#313244')
            self.canvas_waveform = FigureCanvas(self.fig_waveform)
            self.canvas_waveform.setMinimumHeight(400)
            pf_layout.addWidget(self.canvas_waveform)
            
            pf_group.setLayout(pf_layout)
            main_layout.addWidget(pf_group)
            
            # Update timer for the plot
            self.plot_timer = QTimer()
            self.plot_timer.timeout.connect(self.draw_waveform)
            self.plot_timer.start(100) # Update plot 10 times per second
            
            self.draw_waveform() # Initial draw
        except ImportError:
            error_label = QLabel("Matplotlib not installed. Cannot show waveform visualization.")
            error_label.setStyleSheet("color: #f38ba8; font-size: 14px; padding: 20px;")
            error_label.setAlignment(Qt.AlignCenter)
            pf_layout.addWidget(error_label)
            pf_group.setLayout(pf_layout)
            main_layout.addWidget(pf_group)
    
    def update_power_factor(self, index):
        """Update power factor from slider"""
        self.power_factor = self.pf_values[index]
        phase_diff = self.calculate_phase_diff(self.power_factor)
        
        self.pf_value_label.setText(f"Power Factor: {self.power_factor:.2f}")
        self.phase_diff_label.setText(f"Phase Difference: {phase_diff:.2f}°")
        
        # Send to ESP32
        if self.backend and self.backend.connected:
            self.backend.set_power_factor(self.current_value, self.power_factor)

    def update_current(self, new_current):
        """Update current value from spinbox and send to ESP32"""
        self.current_value = new_current
        # Send the new current value with the existing power factor
        if self.backend and self.backend.connected:
            self.backend.set_power_factor(self.current_value, self.power_factor)
    
    def calculate_phase_diff(self, pf):
        """Calculate phase difference in degrees from power factor"""
        phase_rad = np.arccos(np.clip(pf, 0, 1))
        phase_deg = np.degrees(phase_rad)
        return phase_deg

    def toggle_connection(self):
        if self.tcp_client.is_connected():
            self.tcp_client.disconnect()
        else:
            self.tcp_client.connect()

    def update_connection_status(self, connected):
        if connected:
            self.connection_status_label.setText("Status: Connected")
            self.connection_status_label.setStyleSheet("color: #a6e3a1; font-weight: bold;")
            self.connect_button.setText("Disconnect")
            self.start_time = time.time()
            self.voltage_data.clear()
            self.time_data.clear()
        else:
            self.connection_status_label.setText("Status: Disconnected")
            self.connection_status_label.setStyleSheet("color: #f38ba8; font-weight: bold;")
            self.connect_button.setText("Connect to ESP32")

    def handle_new_data(self, voltage):
        if self.start_time is None: # Should be set on connection, but as a fallback
            self.start_time = time.time()
        
        current_time = time.time() - self.start_time
        self.voltage_data.append(voltage)
        self.time_data.append(current_time)

    def closeEvent(self, event):
        """Ensure TCP client is disconnected when window is closed."""
        self.tcp_client.disconnect()
        super().closeEvent(event)

    def draw_waveform(self):
        """Draw waveform from live data"""
        self.ax_waveform.clear()

        if not self.voltage_data:
            # Show a placeholder message if no data is available
            self.ax_waveform.text(0.5, 0.5, 'Not Connected or No Data Received...',
                                  ha='center', va='center', color='#cdd6f4', fontsize=14)
        else:
            # Plot Voltage (Real Data)
            self.ax_waveform.plot(self.time_data, self.voltage_data, color='#f38ba8', linewidth=2, label='Voltage (Live)')

            # Calculate and Plot Current (Calculated)
            phase_rad = np.arccos(np.clip(self.power_factor, 0, 1))
            
            if len(self.voltage_data) > 2:
                v_peak_real = np.max(self.voltage_data)
                current_peak_calc = self.current_input.value() * np.sqrt(2) # I = I_rms * sqrt(2)
                
                time_for_calc = np.linspace(self.time_data[0], self.time_data[-1], len(self.time_data))
                
                v_np = np.array(self.voltage_data)
                zero_crossings = np.where(np.diff(np.sign(v_np)))[0]
                if len(zero_crossings) > 1:
                    time_diffs = np.diff(np.array(self.time_data)[zero_crossings])
                    avg_period = np.mean(time_diffs) * 2
                    frequency = 1 / avg_period if avg_period > 0 else 50
                else:
                    frequency = 50 # Default if no crossings found

                omega = 2 * np.pi * frequency
                current_calculated = current_peak_calc * np.sin(omega * time_for_calc - phase_rad)

                self.ax_waveform.plot(time_for_calc, current_calculated, color='#a6e3a1', linewidth=2, label=f'Current (Calculated)', linestyle='--')

        self.ax_waveform.set_xlabel("Time (s)", fontsize=12, color='#cdd6f4', fontweight='bold')
        self.ax_waveform.set_ylabel("Amplitude", fontsize=12, color='#cdd6f4', fontweight='bold')
        self.ax_waveform.set_title(f"⚡ Live Voltage & Current Waveforms (PF = {self.power_factor:.2f})", 
                                   fontsize=14, color='#89b4fa', pad=15, fontweight='bold')
        self.ax_waveform.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
        self.ax_waveform.legend(loc='upper right', framealpha=0.9, facecolor='#313244', 
                               edgecolor='#89b4fa', fontsize=11, frameon=True)
        
        if self.voltage_data:
            self.ax_waveform.set_xlim(self.time_data[0], self.time_data[-1])

        self.ax_waveform.tick_params(colors='#cdd6f4', labelsize=10)
        
        self.fig_waveform.tight_layout()
        self.canvas_waveform.draw()


# ===== Main MCB Testing Software =====
class MCBTestingSoftware(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MCB Testing System - IEC 60898-1:2015 | WiFi Integrated")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize backend
        self.backend = ESP32Backend()
        self.setup_backend_connections()
        
        # Current test info
        self.current_test_name = ""
        self.test_running = False
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        central_widget.setLayout(main_layout)
        
        self.stacked_widget = AnimatedStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        self.create_connection_screen()
        self.create_test_selection_screen()
        self.create_test_details_screen()
        
        self.stacked_widget.setCurrentIndex(0)
        
    def setup_backend_connections(self):
        """Connect backend signals to frontend slots"""
        self.backend.connection_status_changed.connect(self.on_connection_status_changed)
        self.backend.data_received.connect(self.on_data_received)
        self.backend.command_sent.connect(self.on_command_sent)
        self.backend.error_occurred.connect(self.on_error_occurred)
        self.backend.rl_config_confirmed.connect(self.on_rl_config_confirmed)
    
    def create_connection_screen(self):
        screen = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(40, 40, 40, 40)
        
        container = QFrame()
        container.setObjectName("CardFrame")
        container.setMaximumWidth(700)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 120))
        container.setGraphicsEffect(shadow)
        
        container_layout = QVBoxLayout()
        container_layout.setSpacing(24)
        
        # Title
        title = QLabel("MCB Testing System")
        title.setStyleSheet(f"""
            QLabel {{
                color: {COLOR_TEXT_PRIMARY};
                font-size: 38px;
                font-weight: 700;
                background: transparent;
                letter-spacing: 1px;
            }}
        """)
        title.setAlignment(Qt.AlignCenter)
        
        subtitle = QLabel("IEC 60898-1:2015 COMPLIANT | WiFi INTEGRATED")
        subtitle.setStyleSheet(f"""
            QLabel {{
                color: {COLOR_PRIMARY};
                font-size: 13px;
                font-weight: 600;
                background: transparent;
                letter-spacing: 3px;
            }}
        """)
        subtitle.setAlignment(Qt.AlignCenter)
        
        # WiFi Icon
        wifi_container = QFrame()
        wifi_container.setMaximumSize(120, 120)
        wifi_container.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 {COLOR_PRIMARY}, stop:1 {COLOR_ACCENT});
                border-radius: 60px;
                border: 2px solid {COLOR_BORDER_FOCUS};
            }}
        """)
        
        wifi_layout = QVBoxLayout()
        wifi_layout.setContentsMargins(0, 0, 0, 0)
        wifi_icon = QLabel("📡")
        wifi_icon.setStyleSheet("""
            QLabel {
                font-size: 64px;
                background: transparent;
            }
        """)
        wifi_icon.setAlignment(Qt.AlignCenter)
        wifi_layout.addWidget(wifi_icon)
        wifi_container.setLayout(wifi_layout)
        
        wifi_center_layout = QHBoxLayout()
        wifi_center_layout.addStretch()
        wifi_center_layout.addWidget(wifi_container)
        wifi_center_layout.addStretch()
        
        # ESP32 IP Configuration
        config_group = QGroupBox("ESP32 Configuration")
        config_group.setStyleSheet(f"""
            QGroupBox {{
                color: {COLOR_PRIMARY};
                font-weight: bold;
                border: 2px solid {COLOR_BORDER};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }}
        """)
        
        config_layout = QFormLayout()
        
        self.ip_input = QLineEdit("10.91.136.24")
        self.ip_input.setPlaceholderText("ESP32 IP Address")
        self.ip_input.setStyleSheet(f"""
            QLineEdit {{
                background: {COLOR_BACKGROUND_ELEVATED};
                color: {COLOR_TEXT_PRIMARY};
                border: 2px solid {COLOR_BORDER};
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border-color: {COLOR_PRIMARY};
            }}
        """)
        
        self.port_input = QSpinBox()
        self.port_input.setRange(1000, 65535)
        self.port_input.setValue(8888)
        self.port_input.setStyleSheet(f"""
            QSpinBox {{
                background: {COLOR_BACKGROUND_ELEVATED};
                color: {COLOR_TEXT_PRIMARY};
                border: 2px solid {COLOR_BORDER};
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
            }}
            QSpinBox:focus {{
                border-color: {COLOR_PRIMARY};
            }}
        """)
        
        config_layout.addRow("IP Address:", self.ip_input)
        config_layout.addRow("Port:", self.port_input)
        config_group.setLayout(config_layout)
        
        # Status label
        self.connection_status = QLabel("⚠ Not Connected")
        self.connection_status.setStyleSheet(f"""
            QLabel {{
                color: {COLOR_WARNING};
                font-size: 16px;
                font-weight: 600;
                background: transparent;
                padding: 16px;
                letter-spacing: 0.5px;
            }}
        """)
        self.connection_status.setAlignment(Qt.AlignCenter)
        
        # Connect button
        self.connect_btn = ModernButton("Connect to Device", primary=True)
        self.connect_btn.clicked.connect(self.connect_to_esp32)
        
        # Continue button (initially hidden)
        self.continue_btn = ModernButton("Continue to Testing →", primary=True)
        self.continue_btn.clicked.connect(lambda: self.stacked_widget.slideIn(1))
        self.continue_btn.hide()
        
        container_layout.addWidget(title)
        container_layout.addWidget(subtitle)
        container_layout.addSpacing(32)
        container_layout.addLayout(wifi_center_layout)
        container_layout.addSpacing(24)
        container_layout.addWidget(config_group)
        container_layout.addWidget(self.connection_status)
        container_layout.addSpacing(16)
        container_layout.addWidget(self.connect_btn)
        container_layout.addWidget(self.continue_btn)
        
        container.setLayout(container_layout)
        layout.addWidget(container)
        
        screen.setLayout(layout)
        self.stacked_widget.addWidget(screen)
    
    def create_test_selection_screen(self):
        screen = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(32, 32, 32, 32)
        main_layout.setSpacing(24)
        
        # Header
        header = QFrame()
        header.setObjectName("DashboardHeader")
        
        header_shadow = QGraphicsDropShadowEffect()
        header_shadow.setBlurRadius(20)
        header_shadow.setXOffset(0)
        header_shadow.setYOffset(4)
        header_shadow.setColor(QColor(0, 0, 0, 100))
        header.setGraphicsEffect(header_shadow)
        
        header_layout = QHBoxLayout()
        header_layout.setSpacing(40)
        
        # Title section
        title_section = QWidget()
        title_layout = QVBoxLayout()
        title_layout.setSpacing(6)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("MCB Testing Dashboard")
        title.setStyleSheet(f"""
            QLabel {{
                color: {COLOR_TEXT_PRIMARY};
                font-size: 26px;
                font-weight: 700;
                background: transparent;
                letter-spacing: 0.5px;
            }}
        """)
        
        subtitle = QLabel("Select a test to perform according to IEC 60898-1:2015 standards")
        subtitle.setStyleSheet(f"""
            QLabel {{
                color: {COLOR_TEXT_SECONDARY};
                font-size: 13px;
                font-weight: 500;
                background: transparent;
            }}
        """)
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        title_section.setLayout(title_layout)
        
        # Connection status badge
        self.dashboard_status = QLabel("✓ Connected")
        self.dashboard_status.setStyleSheet(f"""
            QLabel {{
                background: {COLOR_SUCCESS};
                color: {COLOR_BACKGROUND_PRIMARY};
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }}
        """)
        
        header_layout.addWidget(title_section)
        header_layout.addStretch()
        header_layout.addWidget(self.dashboard_status)
        header.setLayout(header_layout)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet(f"background: {COLOR_BACKGROUND_PRIMARY};")
        
        scroll_layout = QGridLayout()
        scroll_layout.setSpacing(20)
        scroll_layout.setContentsMargins(10, 10, 10, 10)
        
        # Test definitions
        tests = [
            ("Short-Circuit Breaking Capacity & R-XL Configuration", 
             "Test MCB with configurable current and power factor, view live waveforms",
             "⚡", COLOR_PRIMARY),
            ("Variable Resistance and Inductance Configuration", 
             "Direct R-L configuration with precise resistance and inductance values",
             "�", COLOR_ACCENT),
            ("Trip Characteristics (B, C, D Curves)", 
             "Verify instantaneous trip thresholds and time-current curves",
             "📊", COLOR_ACCENT),
            ("Temperature Rise Test", 
             "Measure contact and terminal temperature under rated current",
             "🌡️", COLOR_WARNING),
            ("Dielectric Strength Test", 
             "Verify insulation withstand voltage capability",
             "🛡️", COLOR_INFO),
            ("Breaking Time Measurement", 
             "High-speed waveform capture and analysis",
             "⏱️", COLOR_INFO),
            ("Contact Resistance Test", 
             "Measure contact resistance at rated current",
             "🔧", COLOR_SUCCESS),
            ("Calibration & Verification", 
             "System calibration and accuracy verification",
             "✓", COLOR_SUCCESS),
            ("Just a Test",
             "A simple test for development and debugging purposes",
             "🐞", COLOR_WARNING),
        ]
        
        row, col = 0, 0
        for title_text, desc, icon, color in tests:
            card = TestCard(title_text, desc, icon, color)
            card.mousePressEvent = lambda e, t=title_text: self.show_test_details(t)
            scroll_layout.addWidget(card, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1
        
        scroll_content.setLayout(scroll_layout)
        scroll.setWidget(scroll_content)
        
        main_layout.addWidget(header)
        main_layout.addWidget(scroll)
        
        screen.setLayout(main_layout)
        self.stacked_widget.addWidget(screen)
    
    def create_test_details_screen(self):
        screen = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        
        # Header
        header = QFrame()
        header.setObjectName("TestDetailsHeader")
        
        header_shadow = QGraphicsDropShadowEffect()
        header_shadow.setBlurRadius(20)
        header_shadow.setXOffset(0)
        header_shadow.setYOffset(4)
        header_shadow.setColor(QColor(0, 0, 0, 100))
        header.setGraphicsEffect(header_shadow)
        
        header_layout = QVBoxLayout()
        header_layout.setSpacing(12)
        
        # Back button row
        back_row = QHBoxLayout()
        back_btn = ModernButton("← Back to Tests", primary=False)
        back_btn.clicked.connect(lambda: self.stacked_widget.slideIn(1))
        back_btn.setMaximumWidth(180)
        back_row.addWidget(back_btn)
        back_row.addStretch()
        
        self.test_title_label = QLabel()
        self.test_title_label.setStyleSheet(f"""
            QLabel {{
                color: {COLOR_TEXT_PRIMARY};
                font-size: 28px;
                font-weight: 700;
                background: transparent;
                letter-spacing: 0.5px;
            }}
        """)
        
        test_subtitle = QLabel("Complete test procedure and approach")
        test_subtitle.setStyleSheet(f"""
            QLabel {{
                color: {COLOR_TEXT_SECONDARY};
                font-size: 13px;
                font-weight: 500;
                background: transparent;
            }}
        """)
        
        header_layout.addLayout(back_row)
        header_layout.addWidget(self.test_title_label)
        header_layout.addWidget(test_subtitle)
        header.setLayout(header_layout)
        
        # Details container
        details_container = QFrame()
        details_container.setObjectName("TestDetailsContainer")
        
        details_shadow = QGraphicsDropShadowEffect()
        details_shadow.setBlurRadius(20)
        details_shadow.setXOffset(0)
        details_shadow.setYOffset(4)
        details_shadow.setColor(QColor(0, 0, 0, 100))
        details_container.setGraphicsEffect(details_shadow)
        
        details_layout = QVBoxLayout()
        details_layout.setSpacing(20)
        
        self.test_details_text = QTextEdit()
        self.test_details_text.setReadOnly(True)

        # Log box for received data
        log_group = QGroupBox("ESP32 Output Log")
        log_group.setStyleSheet(f"""
            QGroupBox {{
                color: {COLOR_PRIMARY};
                font-weight: bold;
                border: 1px solid {COLOR_BORDER};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }}
        """)
        log_layout = QVBoxLayout()
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setStyleSheet(f"""
            QTextEdit {{
                background: {COLOR_BACKGROUND_SECONDARY};
                color: {COLOR_TEXT_SECONDARY};
                border: none;
                font-family: Consolas, 'Courier New', monospace;
                font-size: 13px;
                padding: 10px;
            }}
        """)
        self.log_box.setPlaceholderText("Waiting for data from ESP32...")
        self.log_box.setMinimumHeight(150)
        log_layout.addWidget(self.log_box)
        log_group.setLayout(log_layout)
        
        # Action buttons
        action_layout = QHBoxLayout()
        action_layout.setSpacing(12)
        
        self.start_btn = ModernButton("▶ Start Test", primary=True)
        self.start_btn.setMinimumWidth(160)
        self.start_btn.clicked.connect(self.start_test)
        
        self.configure_btn = ModernButton("⚙ Configure", primary=False)
        self.configure_btn.setMinimumWidth(160)
        self.configure_btn.clicked.connect(self.configure_test)
        
        self.stop_btn = ModernButton("⏹ Stop Test", danger=True)
        self.stop_btn.setMinimumWidth(160)
        self.stop_btn.clicked.connect(self.stop_test)
        self.stop_btn.hide()
        
        action_layout.addWidget(self.start_btn)
        action_layout.addWidget(self.configure_btn)
        action_layout.addWidget(self.stop_btn)
        action_layout.addStretch()
        
        details_layout.addWidget(self.test_details_text)
        details_layout.addWidget(log_group)
        details_layout.addLayout(action_layout)
        
        details_container.setLayout(details_layout)
        
        layout.addWidget(header)
        layout.addWidget(details_container)
        
        screen.setLayout(layout)
        self.stacked_widget.addWidget(screen)
    
    # ===== Backend Event Handlers =====
    
    def on_connection_status_changed(self, connected, message):
        """Handle connection status changes"""
        if connected:
            self.connection_status.setText(f"✓ {message}")
            self.connection_status.setStyleSheet(f"""
                QLabel {{
                    color: {COLOR_SUCCESS};
                    font-size: 16px;
                    font-weight: 600;
                    background: transparent;
                    padding: 16px;
                    letter-spacing: 0.5px;
                }}
            """)
            self.continue_btn.show()
            self.connect_btn.setText("Disconnect")
            self.dashboard_status.setText("✓ Connected")
            self.dashboard_status.setStyleSheet(f"""
                QLabel {{
                    background: {COLOR_SUCCESS};
                    color: {COLOR_BACKGROUND_PRIMARY};
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 12px;
                }}
            """)
        else:
            self.connection_status.setText(f"⚠ {message}")
            self.connection_status.setStyleSheet(f"""
                QLabel {{
                    color: {COLOR_DANGER};
                    font-size: 16px;
                    font-weight: 600;
                    background: transparent;
                    padding: 16px;
                    letter-spacing: 0.5px;
                }}
            """)
            self.continue_btn.hide()
            self.connect_btn.setText("Connect to ESP32")
            self.dashboard_status.setText("✗ Disconnected")
            self.dashboard_status.setStyleSheet(f"""
                QLabel {{
                    background: {COLOR_DANGER};
                    color: {COLOR_TEXT_PRIMARY};
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 12px;
                }}
            """)
    
    def on_data_received(self, data):
        """Handle data received from ESP32"""
        if 'raw' in data:
            self.log_box.append(data['raw'])
        else:
            # Handle other data formats if needed
            self.log_box.append(str(data))
        # Auto-scroll to the bottom
        self.log_box.verticalScrollBar().setValue(self.log_box.verticalScrollBar().maximum())
    
    def on_command_sent(self, command):
        """Handle command sent confirmation"""
        print(f"Command sent: {command}")
    
    
    def on_error_occurred(self, error):
        """Handle errors"""
        QMessageBox.critical(self, "Error", error)
    
    def on_rl_config_confirmed(self, message):
        """Handle R-L configuration confirmation from ESP32"""
        QMessageBox.information(self, "Configuration Confirmed", 
                               f"ESP32 Confirmation:\n{message}")
        print(f"R-L Config Confirmed: {message}")
    
    # ===== Connection Management =====
    
    def connect_to_esp32(self):
        """Connect or disconnect from ESP32"""
        if self.backend.connected:
            self.backend.disconnect()
        else:
            esp_ip = self.ip_input.text()
            port = self.port_input.value()
            self.backend.esp_ip = esp_ip
            self.backend.port = port
            self.backend.connect()
    
    # ===== Test Management =====
    
    def show_test_details(self, test_name):
        """Show test details screen"""
        self.current_test_name = test_name
        self.test_title_label.setText(test_name)
        
        # Load test details (simplified version)
        details = f"""
        <h2 style="color: {COLOR_PRIMARY};">{test_name}</h2>
        <p style="color: {COLOR_TEXT_SECONDARY};">
        This test will be executed on the ESP32 microcontroller with the configured parameters.
        Click "Configure" to set test parameters, then "Start Test" to begin.
        </p>
        <h3 style="color: {COLOR_PRIMARY};">Test Parameters:</h3>
        <ul style="color: {COLOR_TEXT_SECONDARY};">
        <li>Test will be executed remotely on ESP32</li>
        <li>Real-time data will be received and displayed</li>
        <li>Results will be logged automatically</li>
        </ul>
        """
        
        self.test_details_text.setHtml(details)
        self.log_box.clear() # Clear logs for the new test
        self.stacked_widget.slideIn(2)
    
    def configure_test(self):
        """Open test configuration dialog"""
        dialog = TestConfigDialog(self.current_test_name, self)
        if dialog.exec_() == QDialog.Accepted:
            config = dialog.get_config()
            QMessageBox.information(self, "Configuration Saved", 
                                   f"Test configuration saved:\n{config}")
    
    def start_test(self):
        """Start the selected test"""
        if not self.backend.connected:
            QMessageBox.warning(self, "Not Connected", 
                               "Please connect to ESP32 before starting a test.")
            return
        
        # Open configuration dialog first
        dialog = TestConfigDialog(self.current_test_name, self)
        if dialog.exec_() != QDialog.Accepted:
            return
        
        config = dialog.get_config()
        
        # Send appropriate command based on test type
        success = False
        if "Short-Circuit" in self.current_test_name or "R-XL" in self.current_test_name:
            # Merged test: Send current and power factor, then show visualization
            current = config.get('current', 1)
            power_factor = config.get('power_factor', 0.8)
            
            # Send both current and power factor in one command
            success = self.backend.start_short_circuit_test(current, power_factor)
            
            # Open power factor visualization window
            if success:
                self.show_power_factor_window(current, power_factor)
                
        elif "Variable Resistance and Inductance" in self.current_test_name:
            # Direct R-L Configuration
            resistance = config.get('resistance', 0.5)
            inductance = config.get('inductance', 0.001)
            
            # Send R-L configuration command
            success = self.backend.set_variable_rl_configuration(resistance, inductance)
            
            if success:
                # Show confirmation dialog
                QMessageBox.information(self, "Configuration Sent", 
                                       f"R-L Configuration sent to ESP32:\n"
                                       f"Resistance: {resistance:.4f} Ω\n"
                                       f"Inductance: {inductance:.4f} H\n\n"
                                       f"Waiting for confirmation from microcontroller...")
                
        elif "Trip" in self.current_test_name:
            success = self.backend.start_trip_test(
                config.get('mcb_type', 'C'), 
                config.get('current_rating', 16)
            )
        elif "Temperature" in self.current_test_name:
            success = self.backend.start_temperature_test(config.get('rated_current', 16))
        elif "Dielectric" in self.current_test_name:
            success = self.backend.send_command(
                f"TEST:DIELECTRIC,VOLTAGE:{config.get('test_voltage', 2000)},DURATION:{config.get('duration', 5)}"
            )
        elif "Breaking Time" in self.current_test_name:
            success = self.backend.send_command(
                f"TEST:BREAKING_TIME,CURRENT:{config.get('test_current', 1)}"
            )
        elif "Contact Resistance" in self.current_test_name:
            success = self.backend.send_command(
                f"TEST:CONTACT_RESISTANCE,CURRENT:{config.get('test_current', 16)}"
            )
        elif "Calibration" in self.current_test_name:
            success = self.backend.calibrate_sensors()
        elif "Just a Test" in self.current_test_name:
            success = self.backend.send_command("TEST:JUST_A_TEST")
        
        if success:
            self.test_running = True
            self.start_btn.hide()
            self.configure_btn.hide()
            self.stop_btn.show()
            QMessageBox.information(self, "Test Started", 
                                   f"{self.current_test_name} has been started on ESP32.")
        else:
            QMessageBox.critical(self, "Error", "Failed to start test.")
    
    def stop_test(self):
        """Stop the current test"""
        if self.backend.stop_test():
            self.test_running = False
            self.start_btn.show()
            self.configure_btn.show()
            self.stop_btn.hide()
            QMessageBox.information(self, "Test Stopped", "Test has been stopped.")
    
    def show_power_factor_window(self, current_value, power_factor):
        """Show power factor visualization window"""
        self.pf_window = PowerFactorWindow(current_value, power_factor, self.backend, self)
        self.pf_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    set_global_style(app)
    
    window = MCBTestingSoftware()
    window.show()
    
    sys.exit(app.exec_())
