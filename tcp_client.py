import socket
import threading
from PyQt5.QtCore import QObject, pyqtSignal

class TCPClient(QObject):
    connection_status_changed = pyqtSignal(bool)
    new_voltage_data = pyqtSignal(float)

    def __init__(self, host="192.168.0.105", port=8888):
        super().__init__()
        self.host = host
        self.port = port
        self.sock = None
        self.connected = False
        self.thread = None
        self.stop_thread = False

    def connect(self):
        if self.connected:
            return
        self.stop_thread = False
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()

    def _run(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(5) # 5-second timeout for connection
            self.sock.connect((self.host, self.port))
            self.connected = True
            self.connection_status_changed.emit(True)
            self.sock.settimeout(1) # 1-second timeout for subsequent reads

            buffer = ""
            while self.connected and not self.stop_thread:
                try:
                    data = self.sock.recv(1024).decode('utf-8')
                    if not data:
                        break # Connection closed by server
                    
                    buffer += data
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        line = line.strip()
                        if line:
                            try:
                                # Assuming data is sent as a raw number, e.g., "12"
                                voltage = float(line)
                                self.new_voltage_data.emit(voltage)
                            except (ValueError, IndexError) as e:
                                print(f"Error parsing voltage data: {e} | Received: '{line}'")

                except socket.timeout:
                    continue # No data received, just loop again
                except (socket.error, ConnectionResetError) as e:
                    print(f"Socket error: {e}")
                    break

        except socket.timeout:
            print(f"Connection to {self.host}:{self.port} timed out.")
        except socket.error as e:
            print(f"Failed to connect to {self.host}:{self.port}. Error: {e}")
        finally:
            self.disconnect()

    def disconnect(self):
        self.stop_thread = True
        if self.sock:
            self.sock.close()
            self.sock = None
        if self.connected:
            self.connected = False
            self.connection_status_changed.emit(False)
            print("Disconnected from TCP server.")

    def is_connected(self):
        return self.connected
