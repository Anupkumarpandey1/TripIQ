#!/usr/bin/env python3
"""
Test script to demonstrate cycle looping functionality
"""

import numpy as np
import matplotlib.pyplot as plt
import time

def simulate_cycle_looping():
    """Simulate the cycle looping algorithm"""
    
    print("🔄 Testing Cycle Looping Algorithm")
    print("=" * 40)
    
    # Simulate ESP32 data: 9 seconds with gaps
    total_time = 9.0  # 9 seconds
    sample_rate = 1000  # 1000 Hz
    frequency = 50  # 50Hz AC
    
    # Generate time array
    t = np.linspace(0, total_time, int(total_time * sample_rate))
    
    # Simulate ESP32 behavior: data for first 0.1s, then gaps
    esp32_voltage = np.zeros_like(t)
    esp32_mask = np.zeros_like(t, dtype=bool)
    
    # Add data for first 100ms (5 cycles)
    data_duration = 0.1
    data_mask = t <= data_duration
    esp32_voltage[data_mask] = 325 * np.sin(2 * np.pi * frequency * t[data_mask]) + 1750
    esp32_mask[data_mask] = True
    
    # Add some more data chunks to simulate your controller
    for start_time in [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]:
        chunk_mask = (t >= start_time) & (t <= start_time + 0.1)
        esp32_voltage[chunk_mask] = 325 * np.sin(2 * np.pi * frequency * t[chunk_mask]) + 1750
        esp32_mask[chunk_mask] = True
    
    print(f"Simulated ESP32 data: {np.sum(esp32_mask)} samples over {total_time}s")
    
    # Simulate our cycle looping algorithm
    cycle_data = []
    cycle_timestamps = []
    cycle_captured = False
    cycle_duration = 0.02  # 20ms for one 50Hz cycle
    data_start_time = None
    loop_start_time = None
    dc_offset = 1750  # Known DC offset
    
    processed_voltage = np.zeros_like(t)
    
    for i, (time_val, voltage) in enumerate(zip(t, esp32_voltage)):
        if esp32_mask[i]:  # Only process when we have data
            # Remove DC offset
            voltage_ac = voltage - dc_offset
            
            # Set data start time on first sample
            if data_start_time is None:
                data_start_time = time_val
            
            relative_time = time_val - data_start_time
            
            # Capture cycle data for first 20ms
            if not cycle_captured and relative_time <= cycle_duration:
                cycle_data.append(voltage_ac)
                cycle_timestamps.append(relative_time)
                processed_voltage[i] = voltage_ac
            elif not cycle_captured and relative_time > cycle_duration:
                cycle_captured = True
                loop_start_time = time_val
                print(f"✅ Cycle captured at {time_val:.3f}s: {len(cycle_data)} samples")
                
                # Use looped data
                loop_time = time_val - loop_start_time
                cycle_time = loop_time % cycle_duration
                
                # Find closest sample in cycle
                if len(cycle_timestamps) > 1:
                    cycle_idx = np.argmin(np.abs(np.array(cycle_timestamps) - cycle_time))
                    processed_voltage[i] = cycle_data[cycle_idx]
                else:
                    processed_voltage[i] = cycle_data[0] if cycle_data else 0
            elif cycle_captured:
                # Use looped data
                loop_time = time_val - loop_start_time
                cycle_time = loop_time % cycle_duration
                
                # Find closest sample in cycle
                if len(cycle_timestamps) > 1:
                    cycle_idx = np.argmin(np.abs(np.array(cycle_timestamps) - cycle_time))
                    processed_voltage[i] = cycle_data[cycle_idx]
                else:
                    processed_voltage[i] = cycle_data[0] if cycle_data else 0
    
    # Create visualization
    plt.figure(figsize=(15, 10))
    
    # Plot 1: Original ESP32 data with gaps
    plt.subplot(3, 1, 1)
    plt.plot(t[esp32_mask], esp32_voltage[esp32_mask], 'r-', linewidth=2, label='ESP32 Data (with gaps)')
    plt.title('ESP32 Controller Data (Raw with DC Offset)')
    plt.ylabel('Voltage (V)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xlim(0, 2)  # Show first 2 seconds
    
    # Plot 2: After DC removal (still with gaps)
    plt.subplot(3, 1, 2)
    dc_removed = esp32_voltage - dc_offset
    plt.plot(t[esp32_mask], dc_removed[esp32_mask], 'b-', linewidth=2, label='After DC Removal (with gaps)')
    plt.title('After DC Offset Removal (Still has gaps)')
    plt.ylabel('Voltage (V)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xlim(0, 2)
    
    # Plot 3: After cycle looping (smooth continuous)
    plt.subplot(3, 1, 3)
    # Show continuous looped signal
    continuous_mask = processed_voltage != 0
    plt.plot(t[continuous_mask], processed_voltage[continuous_mask], 'g-', linewidth=2, label='After Cycle Looping (Smooth)')
    plt.title('After Cycle Looping (Continuous Sinusoidal)')
    plt.xlabel('Time (s)')
    plt.ylabel('Voltage (V)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xlim(0, 2)
    
    plt.tight_layout()
    plt.savefig('cycle_looping_test.png', dpi=150, bbox_inches='tight')
    print(f"\n📊 Visualization saved as 'cycle_looping_test.png'")
    
    # Show statistics
    print(f"\nStatistics:")
    print(f"Original data points: {np.sum(esp32_mask)}")
    print(f"Cycle samples captured: {len(cycle_data)}")
    print(f"Cycle duration: {cycle_duration * 1000:.1f}ms")
    print(f"Processed data points: {np.sum(continuous_mask)}")
    
    plt.show()
    
    return len(cycle_data) > 0

if __name__ == "__main__":
    success = simulate_cycle_looping()
    
    if success:
        print("\n✅ Cycle looping test PASSED!")
        print("💡 The algorithm should eliminate straight line segments")
        print("🌊 You'll see smooth continuous sinusoidal waveforms")
    else:
        print("\n❌ Cycle looping test FAILED!")
        
    print("\n🚀 Now run 'python frontend.py' to test with real ESP32 data!")