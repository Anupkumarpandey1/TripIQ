"""
Backend Communication Module for MCB Testing System
Handles WiFi communication with ESP32 microcontroller
"""

import socket
import threading
import time
import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal, QTimer

class ESP32Backend(QObject):
    # Signals for communication with frontend
    connection_status_changed = pyqtSignal(bool, str)  # connected, message
    data_received = pyqtSignal(dict)  # {time, temp, current, voltage, etc}
    command_sent = pyqtSignal(str)  # command sent confirmation
    error_occurred = pyqtSignal(str)  # error message
    rl_config_confirmed = pyqtSignal(str)  # R-L configuration confirmation
    voltage_data_received = pyqtSignal(list, list)  # voltage_values, timestamps
    real_time_waveform = pyqtSignal(dict)  # real-time voltage and calculated current

    def __init__(self, esp_ip="10.91.136.24", port=8888):
        super().__init__()
        self.esp_ip = esp_ip
        self.port = port
        self.client = None
        self.connected = False
        self.receive_thread = None
        self.running = False
        # Data storage
        self.time_vals = []
        self.temp_vals = []
        self.current_vals = []
        self.voltage_vals = []
        # Real-time voltage data
        self.voltage_readings = []
        self.timestamps = []
        self.current_power_factor = 0.8  # Default power factor
        self.current_target_current = 1000  # Default target current
        # DC offset removal
        self.voltage_window = []  # Store recent voltage readings for offset calculation
        self.window_size = 100  # Number of samples to use for offset calculation
        self.dc_offset = None  # Calculated DC offset
        
        # Cycle management for smooth looping
        self.cycle_data = []  # Store one complete cycle
        self.cycle_timestamps = []  # Timestamps for one cycle
        self.cycle_captured = False  # Flag to indicate if we have a complete cycle
        self.cycle_start_time = None  # When the cycle capture started
        self.cycle_duration = 0.02  # 20ms for 50Hz (one complete cycle)
        self.loop_start_time = None  # When to start looping
        self.data_start_time = None  # First data timestamp

    def connect(self):
        """Create TCP connection to ESP32 and start receive thread."""
        try:
            # Use SOCK_STREAM for TCP
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.settimeout(10)  # 10 second connection timeout
            
            # Connect to ESP32
            self.client.connect((self.esp_ip, self.port))
            self.connected = True
            self.running = True
            
            # Reset cycle data for new connection
            self.reset_cycle_data()
            
            # Start receive thread for confirmations
            self.receive_thread = threading.Thread(target=self._receive_data, daemon=True)
            self.receive_thread.start()
            
            self.connection_status_changed.emit(True, f"TCP connected to {self.esp_ip}:{self.port}")
            return True
        except Exception as e:
            self.connected = False
            self.connection_status_changed.emit(False, f"TCP connection failed: {str(e)}")
            return False

    def disconnect(self):
        """Disconnect from ESP32"""
        self.connected = False
        self.running = False
        
        if self.receive_thread and self.receive_thread.is_alive():
            self.receive_thread.join(timeout=1)
            
        if self.client:
            try:
                self.client.close()
            except Exception as e:
                self.error_occurred.emit(f"Error closing socket: {str(e)}")
            self.client = None
        
        # Reset cycle data for next connection
        self.reset_cycle_data()
        
        self.connection_status_changed.emit(False, "Disconnected")
    
    def reset_cycle_data(self):
        """Reset cycle capture data"""
        self.cycle_data = []
        self.cycle_timestamps = []
        self.cycle_captured = False
        self.cycle_start_time = None
        self.loop_start_time = None
        self.data_start_time = None
        self.dc_offset = None
        self.voltage_window = []
    
    def _receive_data(self):
        """Receive data from ESP32 in background thread"""
        buffer = ""
        while self.running and self.connected:
            try:
                if self.client:
                    # Set socket timeout for non-blocking receive
                    self.client.settimeout(1.0)
                    data = self.client.recv(4096)  # Larger buffer for voltage data
                    if data:
                        message = data.decode('utf-8')
                        buffer += message
                        
                        # Process complete messages delimited by '@'
                        while '@' in buffer:
                            line, buffer = buffer.split('@', 1)
                            line = line.strip()
                            
                            if line:
                                # Parse voltage data format: "voltage,timestamp"
                                if ',' in line and line.replace(',', '').replace('.', '').replace('-', '').isdigit():
                                    try:
                                        parts = line.split(',')
                                        if len(parts) == 2:
                                            raw_voltage = float(parts[0])
                                            timestamp = int(parts[1])
                                            
                                            # Update DC offset calculation
                                            self.update_dc_offset(raw_voltage)
                                            
                                            # Remove DC offset to get AC waveform
                                            voltage_ac = self.remove_dc_offset(raw_voltage)
                                            
                                            # Initialize voltage with AC voltage as default (ensures voltage is always defined)
                                            voltage = voltage_ac
                                            
                                            try:
                                                # Capture cycle data for looping
                                                cycle_ready = self.capture_cycle_data(voltage_ac, timestamp)
                                                
                                                # Use looped voltage if cycle is captured and available
                                                if cycle_ready:
                                                    looped_voltage = self.get_looped_voltage(timestamp)
                                                    if looped_voltage is not None:
                                                        voltage = looped_voltage
                                                    # If looped_voltage is None, keep using voltage_ac
                                            except Exception as cycle_error:
                                                # If cycle processing fails, use original AC voltage
                                                print(f"Cycle processing error: {cycle_error}")
                                                voltage = voltage_ac
                                            
                                            # Store processed voltage data
                                            self.voltage_readings.append(voltage)
                                            self.timestamps.append(timestamp)
                                            
                                            # Calculate current from voltage and power factor
                                            try:
                                                current = self.calculate_current_from_voltage(voltage, timestamp)
                                            except Exception as current_error:
                                                print(f"Current calculation error: {current_error}")
                                                current = 0.0  # Default current value
                                            
                                            # Emit real-time waveform data
                                            waveform_data = {
                                                'voltage': voltage,
                                                'current': current,
                                                'timestamp': timestamp,
                                                'power_factor': self.current_power_factor,
                                                'raw_voltage': raw_voltage,
                                                'dc_offset': self.dc_offset if self.dc_offset is not None else 0.0,
                                                'cycle_captured': self.cycle_captured,
                                                'cycle_samples': len(self.cycle_data) if self.cycle_captured else 0
                                            }
                                            self.real_time_waveform.emit(waveform_data)
                                            
                                            # Also emit as regular data
                                            data_dict = {
                                                'time': timestamp / 1000000.0,  # Convert microseconds to seconds
                                                'voltage': voltage,
                                                'current': current,
                                                'temperature': 25.0,  # Default temp
                                                'power_factor': self.current_power_factor,
                                                'raw_voltage': raw_voltage,
                                                'dc_offset': self.dc_offset if self.dc_offset is not None else 0.0
                                            }
                                            self.data_received.emit(data_dict)
                                            
                                    except (ValueError, IndexError) as e:
                                        # Not voltage data, handle as message
                                        self._handle_message(line)
                                else:
                                    # Handle other messages
                                    self._handle_message(line)
                        
                        # Also handle newline characters for robustness
                        while '\n' in buffer or '\r' in buffer:
                            if '\n' in buffer:
                                line, buffer = buffer.split('\n', 1)
                            else:
                                line, buffer = buffer.split('\r', 1)
                            line = line.strip()
                            
                            if line and line not in ['', ' ']:
                                self._handle_message(line)
                                
            except socket.timeout:
                # Normal timeout, continue loop
                continue
            except Exception as e:
                if self.running:  # Only emit error if we're still supposed to be running
                    self.error_occurred.emit(f"Receive error: {str(e)}")
                break
                
            time.sleep(0.01)  # Faster polling for real-time data
    
    def _handle_message(self, message):
        """Handle non-voltage messages"""
        if "R-L_CONFIG_COMPLETE" in message:
            self.rl_config_confirmed.emit("R-L Configuration completed successfully!")
        elif "CONFIRMATION:" in message:
            self.rl_config_confirmed.emit(message)
        else:
            # Emit as raw data for logging
            self.data_received.emit({'raw': message})
    
    def update_dc_offset(self, voltage):
        """Update DC offset calculation using a rolling window"""
        # Add voltage to window
        self.voltage_window.append(voltage)
        
        # Keep window size limited
        if len(self.voltage_window) > self.window_size:
            self.voltage_window.pop(0)
        
        # Calculate DC offset as minimum value in window
        if len(self.voltage_window) >= 10:  # Need at least 10 samples
            self.dc_offset = min(self.voltage_window)
        
        return self.dc_offset
    
    def remove_dc_offset(self, voltage):
        """Remove DC offset from voltage reading"""
        if self.dc_offset is not None:
            return voltage - self.dc_offset
        else:
            return voltage  # Return original if offset not calculated yet
    
    def capture_cycle_data(self, voltage, timestamp):
        """Capture one complete cycle of voltage data"""
        current_time = timestamp / 1000000.0  # Convert to seconds
        
        # Set data start time on first sample
        if self.data_start_time is None:
            self.data_start_time = current_time
            self.cycle_start_time = current_time
        
        # Calculate relative time from start
        relative_time = current_time - self.data_start_time
        
        # Capture data for the first cycle (0 to 0.02 seconds)
        if not self.cycle_captured and relative_time <= self.cycle_duration:
            self.cycle_data.append(voltage)
            self.cycle_timestamps.append(relative_time)
        elif not self.cycle_captured and relative_time > self.cycle_duration:
            # Mark cycle as captured
            self.cycle_captured = True
            self.loop_start_time = current_time
            print(f"✅ Cycle captured: {len(self.cycle_data)} samples over {self.cycle_duration}s")
        
        return self.cycle_captured
    
    def get_looped_voltage(self, timestamp):
        """Get voltage from looped cycle data"""
        if not self.cycle_captured or len(self.cycle_data) == 0:
            return None
        
        current_time = timestamp / 1000000.0
        
        # Calculate time since loop started
        if self.loop_start_time is None:
            return None
        
        loop_time = current_time - self.loop_start_time
        
        # Map loop time to cycle time (0 to cycle_duration)
        cycle_time = loop_time % self.cycle_duration
        
        # Find closest sample in captured cycle
        if len(self.cycle_timestamps) > 1:
            # Interpolate to find voltage at cycle_time
            cycle_times = np.array(self.cycle_timestamps)
            cycle_voltages = np.array(self.cycle_data)
            
            # Find the closest time index
            time_idx = np.searchsorted(cycle_times, cycle_time)
            
            if time_idx >= len(cycle_voltages):
                time_idx = len(cycle_voltages) - 1
            elif time_idx > 0:
                # Linear interpolation between two points
                t1, t2 = cycle_times[time_idx-1], cycle_times[time_idx]
                v1, v2 = cycle_voltages[time_idx-1], cycle_voltages[time_idx]
                
                if t2 != t1:
                    voltage = v1 + (v2 - v1) * (cycle_time - t1) / (t2 - t1)
                else:
                    voltage = v1
            else:
                voltage = cycle_voltages[0]
            
            return voltage
        
        return self.cycle_data[0] if self.cycle_data else None
    
    def calculate_current_from_voltage(self, voltage, timestamp):
        """Calculate current waveform from voltage using power factor"""
        try:
            # Convert timestamp to time in seconds
            time_sec = timestamp / 1000000.0
            
            # Calculate phase angle from power factor
            phase_angle = np.arccos(np.clip(self.current_power_factor, 0, 1))
            
            # Assume 50Hz frequency
            frequency = 50.0
            omega = 2 * np.pi * frequency
            
            # Calculate current based on voltage and impedance
            if len(self.voltage_readings) > 10:  # Need some history for RMS calculation
                # Calculate RMS voltage from recent readings
                recent_voltages = self.voltage_readings[-20:] if len(self.voltage_readings) >= 20 else self.voltage_readings
                voltage_rms = np.sqrt(np.mean(np.array(recent_voltages)**2)) if recent_voltages else 230.0
                
                # Calculate impedance based on target current and RMS voltage
                if voltage_rms > 1.0 and self.current_target_current > 0:
                    impedance = voltage_rms / self.current_target_current
                else:
                    impedance = 0.23  # Default impedance
                
                # Calculate instantaneous current with phase shift
                if impedance > 0:
                    current_amplitude = voltage / impedance
                    # Apply phase shift based on power factor
                    current = current_amplitude * np.cos(phase_angle)
                else:
                    current = 0.0
            else:
                # Not enough data yet, use simple calculation
                current = voltage * 0.1  # Simple scaling factor
                
            return current
            
        except Exception as e:
            return 0.0

    def send_command(self, command):
        """Send command to ESP32 via TCP"""
        if not self.connected or not self.client:
            self.error_occurred.emit("Not connected. Cannot send command.")
            return False
        
        try:
            # Add newline character to the end of command
            if not command.endswith('\n'):
                command += '\n'
            
            # For TCP, we use send()
            self.client.send(command.encode('utf-8'))
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
        # Store for current calculation
        self.current_target_current = float(current_value)
        self.current_power_factor = float(power_factor)
        
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
        command = f"{float(current_value)}\n{float(power_factor):.3f}"
        return self.send_command(command)
    
    def configure_rl_circuit(self, resistance, inductance):
        """
        Configure R-XL circuit
        Args:
            resistance: Resistance in Ohms
            inductance: Inductance in Henries
        """
        command = f"CONFIG:RL,{resistance},{inductance}"
        return self.send_command(command)
    
    def set_variable_rl_configuration(self, resistance, inductance):
        """
        Set variable resistance and inductance configuration
        Args:
            resistance: Resistance in Ohms (12 to 50, integer only)
            inductance: Inductance in Henries (0.0000 to 0.0214)
        """
        # Calculate power factor from R and L for current calculation
        omega = 2 * np.pi * 50  # 50Hz
        reactance = omega * inductance
        impedance = np.sqrt(resistance**2 + reactance**2)
        self.current_power_factor = resistance / impedance if impedance > 0 else 0.8
        
        # Format: "R:value,L:value"
        command = f"{resistance:.4f},{inductance:.4f}"
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
