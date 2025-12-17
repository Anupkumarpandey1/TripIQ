#!/usr/bin/env python3
"""
Test script to verify DC offset removal functionality
"""

import numpy as np
import matplotlib.pyplot as plt

def test_dc_offset_removal():
    """Test DC offset removal with simulated data"""
    
    # Generate test data: AC signal with DC offset
    time = np.linspace(0, 0.1, 1000)  # 100ms, 1000 samples
    frequency = 50  # 50Hz
    
    # Pure AC signal (what we want to see)
    pure_ac = 325 * np.sin(2 * np.pi * frequency * time)
    
    # Add DC offset (simulating ADC readings)
    dc_offset = 1750  # Similar to what you're seeing
    voltage_with_offset = pure_ac + dc_offset
    
    print("🧪 Testing DC Offset Removal")
    print("=" * 40)
    print(f"Original AC signal range: {np.min(pure_ac):.1f}V to {np.max(pure_ac):.1f}V")
    print(f"With DC offset range: {np.min(voltage_with_offset):.1f}V to {np.max(voltage_with_offset):.1f}V")
    print(f"DC offset value: {dc_offset}V")
    
    # Simulate our DC offset removal algorithm
    voltage_window = []
    processed_voltages = []
    
    for voltage in voltage_with_offset:
        # Add to window
        voltage_window.append(voltage)
        if len(voltage_window) > 100:  # Keep window size limited
            voltage_window.pop(0)
        
        # Calculate DC offset as minimum
        if len(voltage_window) >= 10:
            calculated_offset = min(voltage_window)
            processed_voltage = voltage - calculated_offset
        else:
            processed_voltage = voltage  # No processing yet
        
        processed_voltages.append(processed_voltage)
    
    processed_voltages = np.array(processed_voltages)
    
    print(f"\nAfter DC removal:")
    print(f"Processed signal range: {np.min(processed_voltages):.1f}V to {np.max(processed_voltages):.1f}V")
    print(f"Calculated DC offset: {min(voltage_with_offset):.1f}V")
    
    # Calculate error
    # Skip first 10 samples (before offset is calculated)
    error = np.mean(np.abs(processed_voltages[10:] - pure_ac[10:]))
    print(f"Average error: {error:.2f}V")
    
    # Create visualization
    plt.figure(figsize=(12, 8))
    
    plt.subplot(3, 1, 1)
    plt.plot(time * 1000, pure_ac, 'g-', linewidth=2, label='Original AC Signal')
    plt.title('Original AC Signal (Target)')
    plt.ylabel('Voltage (V)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.subplot(3, 1, 2)
    plt.plot(time * 1000, voltage_with_offset, 'r-', linewidth=2, label='With DC Offset')
    plt.title('Signal with DC Offset (What ESP32 sends)')
    plt.ylabel('Voltage (V)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.subplot(3, 1, 3)
    plt.plot(time * 1000, processed_voltages, 'b-', linewidth=2, label='After DC Removal')
    plt.plot(time * 1000, pure_ac, 'g--', alpha=0.7, label='Target AC Signal')
    plt.title('After DC Offset Removal (Our Algorithm)')
    plt.xlabel('Time (ms)')
    plt.ylabel('Voltage (V)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('dc_offset_test.png', dpi=150, bbox_inches='tight')
    print(f"\n📊 Visualization saved as 'dc_offset_test.png'")
    
    # Show the plot
    plt.show()
    
    return error < 5.0  # Accept if error is less than 5V

if __name__ == "__main__":
    success = test_dc_offset_removal()
    
    if success:
        print("\n✅ DC offset removal test PASSED!")
        print("💡 The algorithm should work correctly with your ESP32 data")
    else:
        print("\n❌ DC offset removal test FAILED!")
        
    print("\n🚀 Now run 'python frontend.py' to test with real data!")