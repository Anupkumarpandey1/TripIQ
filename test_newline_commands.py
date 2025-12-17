#!/usr/bin/env python3
"""
Test script to verify newline characters are added to commands
"""

def test_command_formatting():
    """Test that commands get newline characters added"""
    
    print("🧪 Testing Command Newline Addition")
    print("=" * 40)
    
    try:
        # Import backend
        from backend import ESP32Backend
        
        # Create backend instance (don't connect)
        backend = ESP32Backend()
        
        print("✅ Backend created successfully")
        
        # Test the command formatting by checking what would be sent
        # We'll override the send method temporarily to capture the command
        sent_commands = []
        
        original_send = backend.client.send if backend.client else None
        
        def mock_send(data):
            sent_commands.append(data.decode('utf-8'))
            return len(data)
        
        # Create a mock client
        class MockClient:
            def send(self, data):
                sent_commands.append(data.decode('utf-8'))
                return len(data)
        
        backend.client = MockClient()
        backend.connected = True
        
        # Test various commands
        test_commands = [
            "TEST:COMMAND",
            "1000,0.8",
            "CONFIG:RL,25,0.0100",
            "STOP",
            "STATUS"
        ]
        
        print("\n🔧 Testing command formatting:")
        
        for cmd in test_commands:
            sent_commands.clear()
            backend.send_command(cmd)
            
            if sent_commands:
                sent_cmd = sent_commands[0]
                has_newline = sent_cmd.endswith('\n')
                print(f"✅ '{cmd}' -> '{repr(sent_cmd)}' (newline: {has_newline})")
                
                if not has_newline:
                    print(f"❌ ERROR: Command '{cmd}' missing newline!")
                    return False
            else:
                print(f"❌ ERROR: Command '{cmd}' was not sent!")
                return False
        
        print("\n🎉 All commands correctly formatted with newlines!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_double_newline_prevention():
    """Test that double newlines are prevented"""
    
    print("\n🔧 Testing double newline prevention:")
    
    try:
        from backend import ESP32Backend
        
        backend = ESP32Backend()
        
        sent_commands = []
        
        class MockClient:
            def send(self, data):
                sent_commands.append(data.decode('utf-8'))
                return len(data)
        
        backend.client = MockClient()
        backend.connected = True
        
        # Test command that already has newline
        test_cmd = "TEST:COMMAND\n"
        sent_commands.clear()
        backend.send_command(test_cmd)
        
        if sent_commands:
            sent_cmd = sent_commands[0]
            newline_count = sent_cmd.count('\n')
            print(f"✅ '{repr(test_cmd)}' -> '{repr(sent_cmd)}' (newlines: {newline_count})")
            
            if newline_count == 1:
                print("✅ Double newline prevention works!")
                return True
            else:
                print(f"❌ ERROR: Expected 1 newline, got {newline_count}")
                return False
        else:
            print("❌ ERROR: Command was not sent!")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Testing Command Newline Addition")
    print("=" * 50)
    
    # Test basic newline addition
    basic_success = test_command_formatting()
    
    # Test double newline prevention
    double_success = test_double_newline_prevention()
    
    print("\n" + "=" * 50)
    
    if basic_success and double_success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Commands will always end with exactly one newline!")
        print("💡 ESP32 should now receive properly formatted commands")
    else:
        print("❌ Some tests failed!")
        
    print("\n✅ Test completed!")