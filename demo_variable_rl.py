#!/usr/bin/env python3
"""
Demo: Variable Resistance and Inductance Configuration
Shows how to use the new R-L configuration feature
"""

import sys
import time
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from backend import ESP32Backend

def demo_variable_rl():
    """Demonstrate the new Variable R-L Configuration feature"""
    
    print("🔧 Variable R-L Configuration Demo")
    print("=" * 50)
    
    # Create backend instance (updated for your controller)
    backend = ESP32Backend(esp_ip="10.91.136.24", port=8888)
    
    # Connect signals to see what happens
    backend.connection_status_changed.connect(
        lambda connected, msg: print(f"📡 Connection: {msg}")
    )
    backend.command_sent.connect(
        lambda cmd: print(f"📤 Sent: {cmd}")
    )
    backend.rl_config_confirmed.connect(
        lambda msg: print(f"✅ ESP32 Confirmed:\n{msg}")
    )
    backend.error_occurred.connect(
        lambda err: print(f"❌ Error: {err}")
    )
    
    # Connect to ESP32
    print("\n1. Connecting to ESP32...")
    if backend.connect():
        print("   ✅ Connected successfully!")
        
        # Wait a moment for connection to stabilize
        time.sleep(2)
        
        # Test different R-L configurations (within new ranges)
        test_configs = [
            (15, 0.0050),   # Lower range values
            (25, 0.0100),   # Mid range values  
            (35, 0.0150),   # Higher range values
            (45, 0.0200),   # Near maximum values
        ]
        
        print(f"\n2. Testing {len(test_configs)} different R-L configurations...")
        
        for i, (resistance, inductance) in enumerate(test_configs, 1):
            print(f"\n   Test {i}/4: R={resistance}Ω, L={inductance}H")
            print(f"   📤 Sending configuration to ESP32...")
            
            success = backend.set_variable_rl_configuration(resistance, inductance)
            
            if success:
                print(f"   ✅ Command sent successfully")
                print(f"   ⏳ Waiting for ESP32 confirmation...")
                time.sleep(3)  # Wait for confirmation
            else:
                print(f"   ❌ Failed to send command")
            
            print(f"   " + "-" * 40)
        
        print(f"\n3. Demo completed!")
        
        # Disconnect
        print(f"\n4. Disconnecting...")
        backend.disconnect()
        print(f"   ✅ Disconnected")
        
    else:
        print("   ❌ Connection failed!")
        print("   💡 Make sure ESP32 is running and IP address is correct")

if __name__ == "__main__":
    # Create QApplication for PyQt5 signals
    app = QApplication(sys.argv)
    
    # Run demo
    demo_variable_rl()
    
    # Keep app running briefly to process any remaining signals
    QTimer.singleShot(2000, app.quit)
    
    print(f"\n🎉 Demo finished!")
    print(f"💡 To use in GUI: Run 'python frontend.py' and select")
    print(f"   'Variable Resistance and Inductance Configuration'")
    
    sys.exit(app.exec_())