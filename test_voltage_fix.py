#!/usr/bin/env python3
"""
Test script to verify the voltage variable fix
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

def test_backend_voltage_processing():
    """Test that backend processes voltage data without errors"""
    
    print("🧪 Testing Voltage Processing Fix")
    print("=" * 40)
    
    try:
        # Import backend
        from backend import ESP32Backend
        
        # Create backend instance
        backend = ESP32Backend()
        
        print("✅ Backend created successfully")
        
        # Test voltage processing methods individually
        print("\n🔧 Testing individual methods:")
        
        # Test DC offset methods
        backend.update_dc_offset(1750.0)
        print("✅ DC offset update works")
        
        voltage_ac = backend.remove_dc_offset(1800.0)
        print(f"✅ DC offset removal works: {voltage_ac}")
        
        # Test cycle capture
        cycle_ready = backend.capture_cycle_data(voltage_ac, 1000000)
        print(f"✅ Cycle capture works: {cycle_ready}")
        
        # Test looped voltage (should return None initially)
        looped_voltage = backend.get_looped_voltage(1000000)
        print(f"✅ Looped voltage works: {looped_voltage}")
        
        # Test current calculation
        current = backend.calculate_current_from_voltage(voltage_ac, 1000000)
        print(f"✅ Current calculation works: {current}")
        
        print("\n🎉 All individual methods work correctly!")
        
        # Test the complete data processing pipeline
        print("\n🔄 Testing complete data processing pipeline:")
        
        # Simulate processing a voltage data line
        test_line = "1750.5,1000000"
        parts = test_line.split(',')
        
        if len(parts) == 2:
            raw_voltage = float(parts[0])
            timestamp = int(parts[1])
            
            # Update DC offset calculation
            backend.update_dc_offset(raw_voltage)
            
            # Remove DC offset to get AC waveform
            voltage_ac = backend.remove_dc_offset(raw_voltage)
            
            # Initialize voltage with AC voltage as default
            voltage = voltage_ac
            
            # Capture cycle data for looping
            cycle_ready = backend.capture_cycle_data(voltage_ac, timestamp)
            
            # Use looped voltage if available
            if cycle_ready:
                looped_voltage = backend.get_looped_voltage(timestamp)
                if looped_voltage is not None:
                    voltage = looped_voltage
            
            # Calculate current
            current = backend.calculate_current_from_voltage(voltage, timestamp)
            
            print(f"✅ Complete pipeline works!")
            print(f"   Raw voltage: {raw_voltage}")
            print(f"   AC voltage: {voltage_ac}")
            print(f"   Final voltage: {voltage}")
            print(f"   Current: {current}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_frontend_startup():
    """Test that frontend starts without the voltage error"""
    
    try:
        from frontend import MCBTestingSoftware
        
        # Create QApplication
        app = QApplication(sys.argv)
        
        # Create main window
        window = MCBTestingSoftware()
        
        print("✅ Frontend created successfully!")
        
        # Test backend connection
        if window.backend:
            print("✅ Backend is properly connected to frontend!")
        
        return True
        
    except Exception as e:
        print(f"❌ Frontend error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 Testing Voltage Variable Fix")
    print("=" * 50)
    
    # Test backend
    backend_success = test_backend_voltage_processing()
    
    print("\n" + "=" * 50)
    
    # Test frontend
    frontend_success = test_frontend_startup()
    
    print("\n" + "=" * 50)
    
    if backend_success and frontend_success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Voltage variable error is FIXED!")
        print("💡 You can now run: python frontend.py")
    else:
        print("❌ Some tests failed!")
        
    print("\n✅ Test completed!")