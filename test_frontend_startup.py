#!/usr/bin/env python3
"""
Test script to verify frontend.py starts without errors
"""

import sys
from PyQt5.QtWidgets import QApplication

def test_frontend_startup():
    """Test that frontend starts without import errors"""
    try:
        # Create QApplication
        app = QApplication(sys.argv)
        
        # Import frontend
        from frontend import MCBTestingSoftware
        
        # Create main window
        window = MCBTestingSoftware()
        
        print("✅ Frontend created successfully!")
        print("✅ All imports working correctly!")
        print("✅ MCBTestingSoftware window initialized!")
        
        # Don't show the window, just test creation
        # window.show()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Frontend Startup")
    print("=" * 30)
    
    success = test_frontend_startup()
    
    if success:
        print("\n🎉 All tests passed!")
        print("💡 You can now run: python frontend.py")
    else:
        print("\n❌ Tests failed!")
        
    print("\n✅ Test completed!")