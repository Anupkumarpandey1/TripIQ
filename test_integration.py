"""
Test Integration Example
Demonstrates how to use the backend independently
"""

from backend import ESP32Backend
import time

def test_backend():
    """Test backend communication"""
    
    # Create backend instance
    backend = ESP32Backend(esp_ip="192.168.1.100", port=5000)
    
    # Connect signals
    backend.connection_status_changed.connect(
        lambda connected, msg: print(f"Connection: {msg}")
    )
    backend.data_received.connect(
        lambda data: print(f"Data: {data}")
    )
    backend.command_sent.connect(
        lambda cmd: print(f"Sent: {cmd}")
    )
    backend.error_occurred.connect(
        lambda err: print(f"Error: {err}")
    )
    backend.rl_config_confirmed.connect(
        lambda msg: print(f"R-L Config Confirmed: {msg}")
    )
    
    # Connect to ESP32
    print("Connecting to ESP32...")
    if backend.connect():
        print("Connected successfully!")
        
        # Wait a bit
        time.sleep(2)
        
        # Send some test commands
        print("\n--- Testing Commands ---")
        
        # 1. Get status
        print("1. Requesting status...")
        backend.get_status()
        time.sleep(1)
        
        # 2. Set power factor
        print("2. Setting power factor to 0.85...")
        backend.set_power_factor(1000, 0.85)
        time.sleep(1)
        
        # 2.5. Test variable R-L configuration
        print("2.5. Testing variable R-L configuration...")
        backend.set_variable_rl_configuration(30, 0.0120)
        time.sleep(3)  # Wait for confirmation
        
        # 3. Start short circuit test
        print("3. Starting short circuit test with 3000A...")
        backend.start_short_circuit_test(3000)
        time.sleep(5)  # Let it run for 5 seconds
        
        # 4. Stop test
        print("4. Stopping test...")
        backend.stop_test()
        time.sleep(1)
        
        # 5. Get collected data
        print("\n--- Collected Data ---")
        data = backend.get_all_data()
        print(f"Time points: {len(data['time'])}")
        print(f"Temperature points: {len(data['temperature'])}")
        print(f"Current points: {len(data['current'])}")
        
        if len(data['time']) > 0:
            print(f"\nLatest readings:")
            print(f"  Time: {data['time'][-1]}s")
            print(f"  Temperature: {data['temperature'][-1]}°C")
            print(f"  Current: {data['current'][-1]}A")
            print(f"  Voltage: {data['voltage'][-1]}V")
        
        # Disconnect
        print("\nDisconnecting...")
        backend.disconnect()
        print("Test complete!")
        
    else:
        print("Connection failed!")

if __name__ == "__main__":
    # Note: This requires PyQt5 event loop for signals to work
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # Run test
    test_backend()
    
    # Keep app running briefly to process signals
    QTimer = __import__('PyQt5.QtCore', fromlist=['QTimer']).QTimer
    QTimer.singleShot(1000, app.quit)
    
    sys.exit(app.exec_())
