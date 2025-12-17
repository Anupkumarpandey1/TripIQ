#!/usr/bin/env python3
"""
Test script to verify TCP connection with your ESP32 controller
This will connect and receive the voltage data format: "voltage,timestamp@"
"""

import socket
import time
import threading

class ControllerTester:
    def __init__(self, host="10.91.136.24", port=8888):
        self.host = host
        self.port = port
        self.client = None
        self.connected = False
        self.running = False
        
    def connect(self):
        """Connect to ESP32 controller"""
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.settimeout(10)
            
            print(f"Connecting to {self.host}:{self.port}...")
            self.client.connect((self.host, self.port))
            
            self.connected = True
            self.running = True
            
            print("✅ Connected successfully!")
            
            # Start receiving data
            self.receive_thread = threading.Thread(target=self.receive_data, daemon=True)
            self.receive_thread.start()
            
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def receive_data(self):
        """Receive data from controller"""
        buffer = ""
        data_count = 0
        
        print("📡 Starting data reception...")
        
        while self.running and self.connected:
            try:
                data = self.client.recv(4096)
                if data:
                    message = data.decode('utf-8')
                    buffer += message
                    
                    # Process complete messages delimited by '@'
                    while '@' in buffer:
                        line, buffer = buffer.split('@', 1)
                        line = line.strip()
                        
                        if line and ',' in line:
                            try:
                                parts = line.split(',')
                                if len(parts) == 2:
                                    voltage = float(parts[0])
                                    timestamp = int(parts[1])
                                    
                                    data_count += 1
                                    
                                    # Print every 10th data point to avoid spam
                                    if data_count % 10 == 0:
                                        print(f"📊 Data #{data_count}: Voltage={voltage:.2f}V, Time={timestamp}μs")
                                    
                                    # Show first few data points in detail
                                    if data_count <= 5:
                                        print(f"🔍 Raw data: {line}")
                                        
                            except (ValueError, IndexError):
                                print(f"⚠️ Could not parse: {line}")
                        
                else:
                    print("❌ No data received, connection might be closed")
                    break
                    
            except socket.timeout:
                continue
            except Exception as e:
                print(f"❌ Receive error: {e}")
                break
        
        print(f"📈 Total data points received: {data_count}")
    
    def disconnect(self):
        """Disconnect from controller"""
        self.running = False
        self.connected = False
        
        if self.client:
            try:
                self.client.close()
            except:
                pass
        
        print("🔌 Disconnected")

def main():
    print("🧪 ESP32 Controller Connection Test")
    print("=" * 50)
    
    tester = ControllerTester()
    
    if tester.connect():
        try:
            print("\n⏳ Receiving data for 10 seconds...")
            print("   (Your controller sends 100 samples every 10 seconds)")
            
            # Let it run for 10 seconds to receive data
            time.sleep(10)
            
        except KeyboardInterrupt:
            print("\n⏹️ Interrupted by user")
        
        finally:
            tester.disconnect()
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    main()