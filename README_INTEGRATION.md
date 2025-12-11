# MCB Testing System - WiFi Integration Guide

## 🎯 Overview

This system integrates the frontend GUI (a1.py) with backend WiFi communication (recieve.py) to create a complete MCB testing solution that communicates with ESP32 microcontroller.

## 📁 File Structure

```
├── backend.py              # WiFi communication module (Python)
├── frontend.py             # Enhanced GUI with test controls (Python)
├── esp32_receiver.ino      # ESP32 receiver code (C/Arduino)
├── a1.py                   # Original frontend (reference)
├── recieve.py              # Original backend (reference)
└── README_INTEGRATION.md   # This file
```

## 🚀 Quick Start

### 1. Setup ESP32

1. Open `esp32_receiver.ino` in Arduino IDE
2. Update WiFi credentials:
   ```cpp
   const char* ssid = "YOUR_WIFI_SSID";
   const char* password = "YOUR_WIFI_PASSWORD";
   ```
3. Upload to ESP32
4. Note the IP address shown in Serial Monitor

### 2. Run Python Application

```bash
python frontend.py
```

### 3. Connect to ESP32

1. Enter ESP32 IP address in the connection screen
2. Click "Connect to ESP32"
3. Wait for connection confirmation
4. Click "Continue to Testing"

## 🔧 Features

### Frontend (frontend.py)
- Modern PyQt5 GUI with dark theme
- WiFi connection management
- Test selection dashboard
- Configuration dialogs for each test
- Real-time status updates

### Backend (backend.py)
- WiFi socket communication
- Command protocol implementation
- Data parsing and storage
- Signal-based event system
- Thread-safe operations

### ESP32 (esp32_receiver.ino)
- WiFi server implementation
- Command parsing
- Test execution control
- Sensor data transmission
- Safety interlocks

## 📡 Communication Protocol

### Commands (PC → ESP32)

```
TEST:SHORT_CIRCUIT,CURRENT:3000    # Start short circuit test
TEST:TRIP,TYPE:C,MULT:1.45         # Start trip test
TEST:TEMPERATURE,CURRENT:16        # Start temperature test
SET_PF:0.850                       # Set power factor
CONFIG:RL,R:0.5,L:0.001           # Configure R-L circuit
STOP                               # Emergency stop
STATUS                             # Request status
RESET                              # Reset system
```

### Data (ESP32 → PC)

```
TIME,TEMP,CURRENT,VOLTAGE          # Sensor data (CSV format)
STATUS:TEST_STARTED,TYPE:...       # Status updates
ERROR:MESSAGE                      # Error messages
```

## 🧪 Test Examples

### Short Circuit Test
```python
# User clicks "Short-Circuit Breaking Capacity"
# Configures: Current = 3000A, Voltage = 230V
# Backend sends: "TEST:SHORT_CIRCUIT,CURRENT:3000"
# ESP32 activates relay and starts test
# Data streams back: "0,25.5,2998.3,230.1"
```

### Trip Characteristics Test
```python
# User clicks "Trip Characteristics"
# Configures: MCB Type = C, Multiplier = 1.45
# Backend sends: "TEST:TRIP,TYPE:C,MULT:1.45"
# ESP32 applies current and measures trip time
```

## 🔌 Hardware Connections

```
ESP32 Pin Assignments:
- GPIO 25: Relay control (MCB activation)
- GPIO 34: Current sensor (ADC)
- GPIO 35: Voltage sensor (ADC)
- GPIO 32: Temperature sensor
- GPIO 2:  Status LED
```

## 🛠️ Customization

### Adding New Tests

1. **Frontend**: Add test card in `create_test_selection_screen()`
2. **Backend**: Add command method in `ESP32Backend` class
3. **ESP32**: Add command handler in `processCommand()`

### Modifying Communication

- Edit `backend.py` for protocol changes
- Update `esp32_receiver.ino` command parsing
- Maintain backward compatibility

## 📊 Data Flow

```
User Action → Frontend UI → Backend Command → WiFi → ESP32
                                                        ↓
User Display ← Frontend UI ← Backend Parser ← WiFi ← Sensor Data
```

## ⚠️ Safety Features

- Connection status monitoring
- Emergency stop button
- Test timeout protection
- Error handling and reporting
- Automatic disconnection on failure

## 🐛 Troubleshooting

### Connection Issues
- Check ESP32 IP address
- Verify WiFi network
- Check firewall settings
- Ensure port 5000 is open

### Data Not Received
- Check ESP32 serial monitor
- Verify test is running
- Check network stability
- Review error messages

## 📝 Notes

- ESP32 must be on same network as PC
- Use static IP for ESP32 (recommended)
- Monitor serial output for debugging
- Keep firmware updated

## 🔄 Migration from Original Files

If migrating from `a1.py` and `recieve.py`:
1. Backend logic is now in `backend.py`
2. Frontend is enhanced in `frontend.py`
3. ESP32 code is in `esp32_receiver.ino`
4. All features are preserved and improved
