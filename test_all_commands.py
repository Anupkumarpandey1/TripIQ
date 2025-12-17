#!/usr/bin/env python3
"""
Test all command methods to ensure they work with newline addition
"""

def test_all_command_methods():
    """Test all command methods in the backend"""
    
    print("🧪 Testing All Command Methods")
    print("=" * 40)
    
    try:
        from backend import ESP32Backend
        
        # Create backend instance
        backend = ESP32Backend()
        
        # Mock client to capture commands
        sent_commands = []
        
        class MockClient:
            def send(self, data):
                sent_commands.append(data.decode('utf-8'))
                return len(data)
        
        backend.client = MockClient()
        backend.connected = True
        
        print("✅ Backend setup complete")
        
        # Test all command methods
        test_methods = [
            ("Short Circuit Test", lambda: backend.start_short_circuit_test(1000, 0.8)),
            ("Trip Test", lambda: backend.start_trip_test('C', 16)),
            ("Temperature Test", lambda: backend.start_temperature_test(16)),
            ("Power Factor", lambda: backend.set_power_factor(1000, 0.8)),
            ("RL Configuration", lambda: backend.configure_rl_circuit(25, 0.01)),
            ("Variable RL Config", lambda: backend.set_variable_rl_configuration(25, 0.01)),
            ("Stop Test", lambda: backend.stop_test()),
            ("Reset System", lambda: backend.reset_system()),
            ("Get Status", lambda: backend.get_status()),
            ("Calibrate Sensors", lambda: backend.calibrate_sensors()),
        ]
        
        print("\n🔧 Testing all command methods:")
        
        all_passed = True
        
        for method_name, method_func in test_methods:
            sent_commands.clear()
            
            try:
                success = method_func()
                
                if success and sent_commands:
                    sent_cmd = sent_commands[0]
                    has_newline = sent_cmd.endswith('\n')
                    
                    print(f"✅ {method_name}: '{repr(sent_cmd)}' (newline: {has_newline})")
                    
                    if not has_newline:
                        print(f"❌ ERROR: {method_name} missing newline!")
                        all_passed = False
                        
                elif success:
                    print(f"✅ {method_name}: Method executed (no command sent)")
                else:
                    print(f"❌ {method_name}: Method failed")
                    all_passed = False
                    
            except Exception as e:
                print(f"❌ {method_name}: Exception - {e}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 Testing All Command Methods with Newlines")
    print("=" * 50)
    
    success = test_all_command_methods()
    
    print("\n" + "=" * 50)
    
    if success:
        print("🎉 ALL COMMAND METHODS PASSED!")
        print("✅ Every command sent to ESP32 will have a newline!")
        print("💡 Your ESP32 controller should now receive properly formatted commands")
    else:
        print("❌ Some command methods failed!")
        
    print("\n✅ Test completed!")