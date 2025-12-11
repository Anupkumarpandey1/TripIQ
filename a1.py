import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QStackedWidget,
                             QFrame, QScrollArea, QGridLayout, QTextEdit, QGraphicsDropShadowEffect,
                             QSizePolicy)
from PyQt5.QtGui import (QFont, QColor, QPalette)
import serial.tools.list_ports
from PyQt5.QtCore import (Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty, 
                          QParallelAnimationGroup, QRect, QPoint, QSize, 
                          QSequentialAnimationGroup)

# --- ENHANCED: Modern Professional Color Palette ---
# Following Material Design 3 and modern industrial UI principles
COLOR_BACKGROUND_PRIMARY = "#0A0E27"      # Deep navy-blue dark
COLOR_BACKGROUND_SECONDARY = "#151932"    # Slightly lighter navy
COLOR_BACKGROUND_CARD = "#1A1F3A"        # Card background
COLOR_BACKGROUND_ELEVATED = "#1F2544"     # Elevated surfaces

COLOR_PRIMARY = "#00D9FF"                 # Cyan primary (modern, tech-focused)
COLOR_PRIMARY_DARK = "#00B8D4"           # Darker cyan
COLOR_PRIMARY_LIGHT = "#18FFFF"          # Lighter cyan
COLOR_ACCENT = "#7C4DFF"                 # Purple accent
COLOR_ACCENT_LIGHT = "#B388FF"           # Light purple

COLOR_SUCCESS = "#00E676"                 # Success green
COLOR_WARNING = "#FFD600"                 # Warning yellow
COLOR_DANGER = "#FF5252"                  # Danger red
COLOR_INFO = "#2196F3"                    # Info blue

COLOR_TEXT_PRIMARY = "#FFFFFF"            # Primary text
COLOR_TEXT_SECONDARY = "#FFFFFF"         # Secondary text
COLOR_TEXT_MUTED = "#FFFFFF"             # Muted text
COLOR_TEXT_DISABLED = "#FFFFFF"          # Disabled text

COLOR_BORDER = "#2A3150"                  # Subtle borders
COLOR_BORDER_FOCUS = COLOR_PRIMARY        # Focus state


# --- Animated Stacked Widget ---
class AnimatedStackedWidget(QStackedWidget):
    def __init__(self, parent=None):
        super(AnimatedStackedWidget, self).__init__(parent)
        self.m_duration = 400
        self.m_direction = Qt.Horizontal
        self.m_current_index = 0

    def setDuration(self, duration):
        self.m_duration = duration

    def setDirection(self, direction):
        self.m_direction = direction

    def slideIn(self, index):
        if index == self.m_current_index:
            return

        old_widget = self.widget(self.m_current_index)
        new_widget = self.widget(index)
        
        old_widget.resize(self.size())
        new_widget.resize(self.size())

        offset_x = self.width()
        offset_y = self.height()

        if self.m_direction == Qt.Horizontal:
            if index > self.m_current_index:
                new_widget.move(offset_x, 0)
                old_pos = QPoint(0, 0)
                new_pos = QPoint(-offset_x, 0)
            else:
                new_widget.move(-offset_x, 0)
                old_pos = QPoint(0, 0)
                new_pos = QPoint(offset_x, 0)
        else:
            if index > self.m_current_index:
                new_widget.move(0, offset_y)
                old_pos = QPoint(0, 0)
                new_pos = QPoint(0, -offset_y)
            else:
                new_widget.move(0, -offset_y)
                old_pos = QPoint(0, 0)
                new_pos = QPoint(0, offset_y)
        
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
        anim_new.setEndValue(old_pos)
        anim_new.setEasingCurve(QEasingCurve.OutCubic)

        self.anim_group = QParallelAnimationGroup()
        self.anim_group.addAnimation(anim_old)
        self.anim_group.addAnimation(anim_new)
        
        self.anim_group.finished.connect(lambda: self.setCurrentIndex(index))
        self.m_current_index = index
        self.anim_group.start()

    def setCurrentIndex(self, index):
        super().setCurrentIndex(index)


class ModernButton(QPushButton):
    def __init__(self, text, primary=False, danger=False):
        super().__init__(text)
        self.primary = primary
        self.danger = danger
        self.setMinimumHeight(48)
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.update_style()
        
        # Enhanced shadow
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
                    font-size: 18px;
                    font-weight: 600;
                    padding: 12px 24px;
                    letter-spacing: 0.3px;
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
                    letter-spacing: 0.3px;
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
        
        # Icon container with gradient
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


class MCBTestingSoftware(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MCB Testing System - IEC 60898-1:2015")
        self.setGeometry(100, 100, 1400, 900)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        central_widget.setLayout(main_layout)
        
        self.stacked_widget = AnimatedStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        self.create_usb_connection_screen()
        self.create_test_selection_screen()
        self.create_test_details_screen()
        
        self.stacked_widget.setCurrentIndex(0)
        
        self.usb_timer = QTimer()
        self.usb_timer.timeout.connect(self.check_usb_connection)
        self.usb_timer.start(1000)
        
        QTimer.singleShot(100, self.start_usb_animation)
        
    def create_usb_connection_screen(self):
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
        
        subtitle = QLabel("IEC 60898-1:2015 COMPLIANT")
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
        
        # USB Icon container
        usb_container = QFrame()
        usb_container.setMaximumSize(120, 120)
        usb_container.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 {COLOR_PRIMARY}, stop:1 {COLOR_ACCENT});
                border-radius: 60px;
                border: 2px solid {COLOR_BORDER_FOCUS};
            }}
        """)
        
        usb_layout = QVBoxLayout()
        usb_layout.setContentsMargins(0, 0, 0, 0)
        self.usb_icon = QLabel("🔌")
        self.usb_icon.setStyleSheet("""
            QLabel {
                font-size: 64px;
                background: transparent;
            }
        """)
        self.usb_icon.setAlignment(Qt.AlignCenter)
        usb_layout.addWidget(self.usb_icon)
        usb_container.setLayout(usb_layout)
        
        usb_center_layout = QHBoxLayout()
        usb_center_layout.addStretch()
        usb_center_layout.addWidget(usb_container)
        usb_center_layout.addStretch()
        
        # Status label
        self.usb_status = QLabel("⚠ Please connect USB device...")
        self.usb_status.setObjectName("UsbStatus")
        self.update_usb_status_style(connected=False)
        self.usb_status.setAlignment(Qt.AlignCenter)
        
        # Info text
        info_text = QLabel("Connect your MCB testing microcontroller via USB\nto begin the automated testing process")
        info_text.setStyleSheet(f"""
            QLabel {{
                color: {COLOR_TEXT_SECONDARY};
                font-size: 14px;
                background: transparent;
                line-height: 1.6;
            }}
        """)
        info_text.setAlignment(Qt.AlignCenter)
        info_text.setWordWrap(True)
        
        # Continue button
        self.continue_btn = ModernButton("Continue to Testing →", primary=True)
        self.continue_btn.clicked.connect(lambda: self.stacked_widget.slideIn(1))
        self.continue_btn.hide()
        
        container_layout.addWidget(title)
        container_layout.addWidget(subtitle)
        container_layout.addSpacing(32)
        container_layout.addLayout(usb_center_layout)
        container_layout.addSpacing(24)
        container_layout.addWidget(self.usb_status)
        container_layout.addWidget(info_text)
        container_layout.addSpacing(32)
        container_layout.addWidget(self.continue_btn)
        
        container.setLayout(container_layout)
        layout.addWidget(container)
        
        screen.setLayout(layout)
        self.stacked_widget.addWidget(screen)

    def start_usb_animation(self):
        try:
            self.usb_anim_group = QParallelAnimationGroup()
            self.usb_anim_group.setLoopCount(-1)

            start_pos = self.usb_icon.pos()
            end_pos = QPoint(start_pos.x(), start_pos.y() - 8)

            anim_up = QPropertyAnimation(self.usb_icon, b"pos")
            anim_up.setDuration(1200)
            anim_up.setStartValue(start_pos)
            anim_up.setEndValue(end_pos)
            anim_up.setEasingCurve(QEasingCurve.InOutSine)

            anim_down = QPropertyAnimation(self.usb_icon, b"pos")
            anim_down.setDuration(1200)
            anim_down.setStartValue(end_pos)
            anim_down.setEndValue(start_pos)
            anim_down.setEasingCurve(QEasingCurve.InOutSine)

            seq_group = QSequentialAnimationGroup()
            seq_group.addAnimation(anim_up)
            seq_group.addAnimation(anim_down)
            
            self.usb_anim_group.addAnimation(seq_group)
            self.usb_anim_group.start()
        except Exception as e:
            print(f"Animation failed to start: {e}")

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
        
        # Stats section with modern badges
        stats_section = QWidget()
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        
        stats_data = [
            ("12", "Total Tests", COLOR_PRIMARY),
            ("IEC 60898-1", "Standard", COLOR_ACCENT),
            ("10kA", "Max Current", COLOR_SUCCESS)
        ]
        
        for value, label, color in stats_data:
            stat_widget = QFrame()
            stat_widget.setStyleSheet(f"""
                QFrame {{
                    background: {COLOR_BACKGROUND_ELEVATED};
                    border-radius: 8px;
                    padding: 12px 16px;
                    border: 1px solid {COLOR_BORDER};
                }}
            """)
            stat_layout_inner = QVBoxLayout()
            stat_layout_inner.setSpacing(4)
            stat_layout_inner.setContentsMargins(0, 0, 0, 0)
            
            stat_value = QLabel(value)
            stat_value.setStyleSheet(f"""
                QLabel {{
                    color: {color};
                    font-size: 18px;
                    font-weight: 700;
                    background: transparent;
                }}
            """)
            
            stat_label = QLabel(label)
            stat_label.setStyleSheet(f"""
                QLabel {{
                    color: {COLOR_TEXT_MUTED};
                    font-size: 10px;
                    background: transparent;
                    letter-spacing: 1px;
                }}
            """)
            
            stat_layout_inner.addWidget(stat_value)
            stat_layout_inner.addWidget(stat_label)
            stat_widget.setLayout(stat_layout_inner)
            stats_layout.addWidget(stat_widget)
        
        stats_section.setLayout(stats_layout)
        
        header_layout.addWidget(title_section)
        header_layout.addStretch()
        header_layout.addWidget(stats_section)
        header.setLayout(header_layout)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet(f"background: {COLOR_BACKGROUND_PRIMARY};")
        
        scroll_layout = QGridLayout()
        scroll_layout.setSpacing(20)
        scroll_layout.setContentsMargins(10, 10, 10, 10)
        
        # Test definitions with varied accent colors
        tests = [
            # ("Short-Circuit Breaking Capacity", 
            #  "Test MCB under maximum rated short-circuit current up to 10,000A",
            #  "⚡", COLOR_PRIMARY),
            ("Trip Characteristics (B, C, D Curves)", 
             "Verify instantaneous trip thresholds and time-current curves",
             "📊", COLOR_ACCENT),
            ("Temperature Rise Test", 
             "Measure contact and terminal temperature under rated current",
             "🌡️", COLOR_WARNING),
            # ("Endurance Test", 
            #  "Perform mechanical and electrical endurance operations",
            #  "🔄", COLOR_SUCCESS),
            ("Dielectric Strength Test", 
             "Verify insulation withstand voltage capability",
             "🛡️", COLOR_INFO),
            ("R-XL Circuit Configuration", 
             "Configure and verify power factor using R and XL combinations",
             "⚙️", COLOR_PRIMARY),
            # ("Multi-Pole Testing (SPN/DP/TP/FP)", 
            #  "Test 1P, 2P, 3P, and 4P MCB configurations",
            #  "🔌", COLOR_ACCENT),
            # ("Current Injection Test", 
            #  "Precise current injection from 0.5A to 10,000A",
            #  "➡️", COLOR_WARNING),
            # ("Arc Chute Performance", 
            #  "Evaluate arc extinction and containment",
            #  "💥", COLOR_DANGER),
            ("Breaking Time Measurement", 
             "High-speed waveform capture and analysis",
             "⏱️", COLOR_INFO),
            ("Contact Resistance Test", 
             "Measure contact resistance at rated current",
             "🔧", COLOR_SUCCESS),
            ("Calibration & Verification", 
             "System calibration and accuracy verification",
             "✓", COLOR_PRIMARY)
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
        
        # Action buttons
        action_layout = QHBoxLayout()
        action_layout.setSpacing(12)
        
        start_btn = ModernButton("▶ Start Test", primary=True)
        start_btn.setMinimumWidth(160)
        
        configure_btn = ModernButton("⚙ Configure", primary=False)
        configure_btn.setMinimumWidth(160)
        
        export_btn = ModernButton("📄 Export Report", primary=False)
        export_btn.setMinimumWidth(160)
        
        action_layout.addWidget(start_btn)
        action_layout.addWidget(configure_btn)
        action_layout.addWidget(export_btn)
        action_layout.addStretch()
        
        details_layout.addWidget(self.test_details_text)
        details_layout.addLayout(action_layout)
        
        details_container.setLayout(details_layout)
        
        layout.addWidget(header)
        layout.addWidget(details_container)
        
        screen.setLayout(layout)
        self.stacked_widget.addWidget(screen)

    def update_usb_status_style(self, connected):
        if connected:
            self.usb_status.setText("✓ USB Device Connected")
            self.usb_status.setStyleSheet(f"""
                QLabel {{
                    color: {COLOR_SUCCESS};
                    font-size: 16px;
                    font-weight: 600;
                    background: transparent;
                    padding: 16px;
                    letter-spacing: 0.5px;
                }}
            """)
        else:
            self.usb_status.setText("⚠ Please Connect USB Device")
            self.usb_status.setStyleSheet(f"""
                QLabel {{
                    color: {COLOR_WARNING};
                    font-size: 16px;
                    font-weight: 600;
                    background: transparent;
                    padding: 16px;
                    letter-spacing: 0.5px;
                }}
            """)

    def check_usb_connection(self):
        ports = serial.tools.list_ports.comports()
        
        if ports:
            self.update_usb_status_style(connected=True)
            self.continue_btn.show()
        else:
            self.update_usb_status_style(connected=False)
            self.continue_btn.hide()
    
    def show_test_details(self, test_name):
        self.test_title_label.setText(test_name)
        
        style_block = f"""
<style>
    h3 {{ 
        color: {COLOR_PRIMARY}; 
        font-size: 20px; 
        font-weight: 700; 
        margin-top: 24px; 
        margin-bottom: 12px; 
        letter-spacing: 0.3px; 
    }}
    p {{ 
        color: {COLOR_TEXT_SECONDARY}; 
        font-size: 14px; 
        line-height: 1.7; 
        margin-bottom: 12px; 
    }}
    ul, ol {{ 
        color: {COLOR_TEXT_SECONDARY}; 
        font-size: 14px; 
        line-height: 1.7; 
        margin-left: 20px; 
    }}
    li {{ 
        margin-bottom: 10px; 
        padding-left: 8px; 
    }}
    b {{ 
        color: {COLOR_PRIMARY_LIGHT}; 
        font-weight: 600; 
    }}
</style>
"""
        
        test_info = {
            "Short-Circuit Breaking Capacity": style_block + """
<h3>⚡ Test Overview</h3>
<p>This test verifies the MCB's ability to interrupt high fault currents safely and reliably according to <b>IEC 60898-1:2015 Clause 9</b>. The test subjects the MCB to extreme conditions to ensure it can protect electrical installations under worst-case fault scenarios.</p>
<h3>🔬 Test Approach</h3>
<ol>
<li><b>Pre-Test Setup:</b><br>
    • Mount MCB in universal test fixture with precision alignment<br>
    • Connect to high-current power source (transformer-based, up to <b>10,000A</b>)<br>
    • Configure arc chute and install safety barriers<br>
    • Set up high-speed data acquisition system (<b>>100kHz sampling rate</b>)</li>
<li><b>Circuit Configuration:</b><br>
    • Configure automated R-XL combination for desired power factor (<b>0.45-0.50</b>)<br>
    • Verify circuit impedance using precision measurement instruments<br>
    • Set test voltage to rated voltage <b>±5%</b> tolerance<br>
    • Program prospective current levels (<b>Icn: 3000A, 4500A, 6000A, 10000A</b>)</li>
<li><b>Test Execution:</b><br>
    • Close MCB contacts under controlled conditions<br>
    • Initiate fault current injection with precise timing<br>
    • Monitor real-time voltage and current waveforms<br>
    • Measure breaking time (arcing time + mechanical opening time)<br>
    • Capture arc energy, peak let-through current, and <b>I²t values</b></li>
<li><b>Post-Test Analysis:</b><br>
    • Verify MCB successfully interrupted fault current without damage<br>
    • Inspect contact condition and measure erosion levels<br>
    • Measure insulation resistance to ensure integrity<br>
    • Evaluate arc chute condition and effectiveness<br>
    • Generate comprehensive compliance report with all parameters</li>
</ol>
<h3>✅ Acceptance Criteria</h3>
<ul>
<li>MCB must interrupt current within specified time (typically <b>≤5ms</b>)</li>
<li>No sustained arcing, explosion, or ejection of components</li>
<li>Contacts must withstand rated number of breaking operations</li>
<li>Post-test dielectric strength must meet <b>≥2000V</b> requirement</li>
<li>Temperature rise within acceptable limits during test</li>
</ul>
<h3>⚠️ Safety Parameters</h3>
<p><b>High Energy Test - Automated Arc Containment Active</b><br>
Maximum arc energy: Up to <b>500kJ per operation</b><br>
Personnel exclusion zone: <b>3 meters</b> during test execution<br>
Multiple safety interlocks prevent accidental operation</p>
""",
            "Trip Characteristics (B, C, D Curves)": style_block + """
<h3>📊 Test Overview</h3>
<p>Verify MCB trip characteristics match specified curve (B, C, or D type) per <b>IEC 60898-1:2015 Clause 8.6</b>.</p>
<h3>🔬 Test Approach</h3>
<ol>
<li><b>Test Points:</b><br>
    • B-Curve: <b>3-5 × In</b> (instantaneous), <b>1.13 × In</b> (thermal)<br>
    • C-Curve: <b>5-10 × In</b> (instantaneous), <b>1.45 × In</b> (thermal)<br>
    • D-Curve: <b>10-20 × In</b> (instantaneous), <b>1.45 × In</b> (thermal)</li>
<li><b>Thermal Trip Test:</b><br>
    • Apply <b>1.13 × In</b> for B-type (<b>1.45 × In</b> for C/D)<br>
    • Monitor time to trip (should be <60 minutes)<br>
    • Measure temperature rise during test</li>
<li><b>Magnetic Trip Test:</b><br>
    • Apply instantaneous current per curve type<br>
    • Measure trip time (should be <b><0.1 seconds</b>)<br>
    • Verify tripping threshold accuracy</li>
<li><b>Time-Current Curve Plotting:</b><br>
    • Test at multiple current levels (<b>1.0, 1.13, 1.45, 2.0, 3.0, 5.0, 10.0 × In</b>)<br>
    • Record trip time for each level<br>
    • Plot actual vs. specified curve<br>
    • Calculate deviation percentage</li>
</ol>
<h3>✅ Acceptance Criteria</h3>
<ul>
<li>Trip time must fall within IEC specified zones</li>
<li>Thermal trip: <b>1.13 × In → trip in <1 hour</b></li>
<li>Magnetic trip: Within instantaneous threshold</li>
<li>Curve deviation: <b>±10% maximum</b></li>
</ul>
""",
            "Temperature Rise Test": style_block + """
<h3>🌡️ Test Overview</h3>
<p>Measure temperature rise of MCB terminals and contacts under continuous rated current per <b>IEC 60898-1:2015 Clause 8.2</b>.</p>
<h3>🔬 Test Approach</h3>
<ol>
<li><b>Preparation:</b><br>
    • Install thermocouples on terminals, contacts, and enclosure<br>
    • Set ambient temperature monitoring<br>
    • Connect MCB to load circuit at rated current (<b>In</b>)</li>
<li><b>Test Execution:</b><br>
    • Apply rated current continuously<br>
    • Monitor temperatures at <b>15-minute intervals</b><br>
    • Record ambient temperature<br>
    • Continue until thermal equilibrium (<b>ΔT <1°C/hour</b>)</li>
<li><b>Measurement Points:</b><br>
    • Terminal screws<br>
    • Contact surfaces (non-intrusive IR measurement)<br>
    • MCB housing<br>
    • Busbar connections</li>
<li><b>Data Analysis:</b><br>
    • Calculate temperature rise (<b>ΔT = T_measured - T_ambient</b>)<br>
    • Compare against IEC limits<br>
    • Identify hot spots<br>
    • Generate thermal profile report</li>
</ol>
<h3>✅ Acceptance Criteria</h3>
<ul>
<li>Terminal temperature rise: <b>≤60K</b> for screw terminals</li>
<li>Contact temperature rise: <b>≤75K</b></li>
<li>Enclosure temperature rise: <b>≤50K</b></li>
<li>No thermal runaway or instability</li>
</ul>
"""
        }
        
        default_info = style_block + """
<h3>🔬 Test Overview</h3>
<p>Detailed test procedure for this test is being configured according to <b>IEC 60898-1:2015</b> standards.</p>
<h3>⚙️ Test Approach</h3>
<ol>
<li><b>Pre-Test Configuration:</b><br>
    • System calibration and verification<br>
    • MCB mounting and secure connection<br>
    • Safety system activation and verification<br>
    • Parameter configuration and validation</li>
<li><b>Test Execution:</b><br>
    • Automated test sequence initiation<br>
    • Real-time monitoring and data acquisition<br>
    • Safety interlocks active throughout test<br>
    • Continuous parameter adjustment and optimization</li>
<li><b>Data Analysis:</b><br>
    • Automated data processing and validation<br>
    • Comparison with IEC 60898-1:2015 limits<br>
    • Comprehensive report generation<br>
    • Pass/Fail determination with detailed metrics</li>
</ol>
<h3>🛡️ Safety Features</h3>
<ul>
<li><b>Automated arc containment</b> - Advanced arc chute protection system</li>
<li><b>Emergency stop systems</b> - Multiple redundant safety cutoffs</li>
<li><b>Personnel safety interlocks</b> - Access control and monitoring</li>
<li><b>Real-time monitoring</b> - Continuous parameter surveillance</li>
</ul>
"""
        
        content = test_info.get(test_name, default_info)
        self.test_details_text.setHtml(content)
        
        self.stacked_widget.slideIn(2)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    set_global_style(app)
    
    window = MCBTestingSoftware()
    window.show()
    
    sys.exit(app.exec_())