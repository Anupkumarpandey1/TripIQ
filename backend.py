"""
Backend Communication Module for MCB Testing System
Handles WiFi communication with ESP32 microcontroller
"""

import socket
import threading
import time
from PyQt5.QtCore import QObject, pyqtSignal, QTimer

class ESP32Backend(QObject):
    # Signals for communication with frontend
    connection_status_changed = pyqtSignal(bool, str)  # connected, message
    data_received = pyqtSignal(dict)  # {time, temp, current, voltage, etc}
    command_sent = pyqtSignal(str)  # command sent confirmation
    error_occurred = pyqtSignal(str)  # error message

    def __init__(self, esp_ip="192.168.137.187", port=5000):
        super().__init__()
        self.esp_ip = esp_ip
        self.port = port
        self.client = None
        self.connected = False
        # No buffer or receive thread needed for one-way UDP

    def connect(self):
        """Create UDP socket for sending commands."""
        try:
            # Use SOCK_DGRAM for UDP
            self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.connected = True
            self.connection_status_changed.emit(True, f"UDP socket created for {self.esp_ip}:{self.port}")
            return True
        except Exception as e:
            self.connected = False
            self.connection_status_changed.emit(False, f"Socket creation failed: {str(e)}")
            return False

    def disconnect(self):
        """Disconnect from ESP32"""
        self.connected = False
        if self.client:
            try:
                self.client.close()
            except Exception as e:
                self.error_occurred.emit(f"Error closing socket: {str(e)}")
            self.client = None
        self.connection_status_changed.emit(False, "Disconnected")

    def send_command(self, command):
        """Send command to ESP32 via UDP"""
        if not self.connected or not self.client:
            self.error_occurred.emit("Not connected. Cannot send command.")
            return False
        
        try:
            # For UDP, we use sendto()
            self.client.sendto(command.encode('utf-8'), (self.esp_ip, self.port))
            self.command_sent.emit(command.strip())
            return True
        except Exception as e:
            self.error_occurred.emit(f"Send error: {str(e)}")
            return False

    # ===== TEST-SPECIFIC COMMANDS =====

    def start_short_circuit_test(self, current_value, power_factor):
        """
        Start short circuit test by sending current and power factor.
        Args:
            current_value: Target current in Amperes (e.g., 3000)
            power_factor: Target power factor (e.g., 0.8)
        """
        # Format matches ESP32 sscanf: "%f,%f"
        command = f"{float(current_value)},{float(power_factor)}"
        return self.send_command(command)
    
    def start_trip_test(self, mcb_type, current_rating):
        """
        Start trip characteristics test
        Args:
            mcb_type: 'B', 'C', or 'D'
            current_rating: MCB current rating in Amperes (e.g., 6, 10, 16, 20, 32)
        """
        command = f"TEST:TRIP,TYPE:{mcb_type},RATING:{current_rating}"
        return self.send_command(command)
    
    def start_temperature_test(self, rated_current):
        """
        Start temperature rise test
        Args:
            rated_current: Rated current in Amperes
        """
        command = f"TEST:TEMPERATURE,CURRENT:{rated_current}"
        return self.send_command(command)
    
    def set_power_factor(self, current_value, power_factor):
        """
        Set power factor for R-XL configuration
        Args:
            current_value: Target current in Amperes
            power_factor: Value between 0.3 and 1.0
        """
        command = f"{float(current_value)},{float(power_factor):.3f}"
        return self.send_command(command)
    
    def configure_rl_circuit(self, resistance, inductance):
        """
        Configure R-XL circuit
        Args:
            resistance: Resistance in Ohms
            inductance: Inductance in Henries
        """
        command = f"CONFIG:RL,R:{resistance},L:{inductance}"
        return self.send_command(command)
    
    def stop_test(self):
        """Emergency stop current test"""
        command = "STOP"
        return self.send_command(command)
    
    def reset_system(self):
        """Reset ESP32 system"""
        command = "RESET"
        return self.send_command(command)
    
    def get_status(self):
        """Request system status"""
        command = "STATUS"
        return self.send_command(command)
    
    def calibrate_sensors(self):
        """Calibrate sensors"""
        command = "CALIBRATE"
        return self.send_command(command)
    
    # ===== DATA ACCESS =====
    
    def get_latest_data(self):
        """Get the latest sensor readings"""
        if len(self.time_vals) > 0:
            return {
                'time': self.time_vals[-1],
                'temperature': self.temp_vals[-1],
                'current': self.current_vals[-1],
                'voltage': self.voltage_vals[-1] if self.voltage_vals else 0
            }
        return None
    
    def get_all_data(self):
        """Get all stored data"""
        return {
            'time': self.time_vals.copy(),
            'temperature': self.temp_vals.copy(),
            'current': self.current_vals.copy(),
            'voltage': self.voltage_vals.copy()
        }
    
    def clear_data(self):
        """Clear all stored data"""
        self.time_vals.clear()
        self.temp_vals.clear()
        self.current_vals.clear()
        self.voltage_vals.clear()
