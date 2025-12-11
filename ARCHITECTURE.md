# System Architecture

## 📐 Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE                          │
│                     (frontend.py)                           │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ Connection   │  │    Test      │  │    Test      │    │
│  │   Screen     │→ │  Dashboard   │→ │   Details    │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│         ↓                  ↓                  ↓            │
└─────────┼──────────────────┼──────────────────┼────────────┘
          │                  │                  │
          └──────────────────┴──────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│                  BACKEND LOGIC                              │
│                  (backend.py)                               │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         ESP32Backend Class                           │  │
│  │                                                      │  │
│  │  • WiFi Connection Management                       │  │
│  │  • Command Protocol                                 │  │
│  │  • Data Reception & Parsing                         │  │
│  │  • Signal Emission (PyQt5)                          │  │
│  │  • Thread-Safe Operations                           │  │
│  └──────────────────────────────────────────────────────┘  │
│                             ↓                               │
└─────────────────────────────┼───────────────────────────────┘
                              │
                    WiFi Socket (TCP)
                    Port: 5000
                              │
┌─────────────────────────────┼───────────────────────────────┐
│                             ↓                               │
│                    ESP32 MICROCONTROLLER                    │
│                    (esp32_receiver.ino)                     │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         WiFi Server                                  │  │
│  │  • Command Reception                                 │  │
│  │  • Command Parsing                                   │  │
│  │  • Test Execution                                    │  │
│  │  • Sensor Reading                                    │  │
│  │  • Data Transmission                                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                             ↓                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Hardware Control                             │  │
│  │                                                      │  │
│  │  GPIO 25 → Relay (MCB Control)                      │  │
│  │  GPIO 34 ← Current Sensor (ADC)                     │  │
│  │  GPIO 35 ← Voltage Sensor (ADC)                     │  │
│  │  GPIO 32 ← Temperature Sensor                       │  │
│  │  GPIO 2  → Status LED                               │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Data Flow

### Command Flow (PC → ESP32)

```
User Action
    ↓
Frontend UI (Button Click)
    ↓
Backend Method Call
    ↓
Command String Formation
    ↓
Socket Send (WiFi)
    ↓
ESP32 Receive Buffer
    ↓
Command Parser
    ↓
Test Execution
    ↓
Hardware Control
```

### Data Flow (ESP32 → PC)

```
Sensor Reading
    ↓
Data Formatting (CSV)
    ↓
Socket Send (WiFi)
    ↓
Backend Receive Thread
    ↓
Data Parser
    ↓
Signal Emission
    ↓
Frontend Update
    ↓
UI Display
```

## 🔌 Communication Protocol

### Message Format

**Commands (PC → ESP32)**:
```
Format: COMMAND:PARAM1,PARAM2,...\n
Example: TEST:SHORT_CIRCUIT,CURRENT:3000\n
```

**Data (ESP32 → PC)**:
```
Format: TIME,TEMP,CURRENT,VOLTAGE\n
Example: 15,28.5,2998.3,230.1\n
```

**Status (ESP32 → PC)**:
```
Format: STATUS:KEY1:VALUE1,KEY2:VALUE2,...\n
Example: STATUS:TEST:SHORT_CIRCUIT,RUNNING:YES\n
```

## 🧩 Class Structure

### Frontend (frontend.py)

```python
MCBTestingSoftware (QMainWindow)
├── ESP32Backend instance
├── AnimatedStackedWidget
│   ├── Connection Screen
│   ├── Test Dashboard
│   └── Test Details Screen
├── Signal Handlers
│   ├── on_connection_status_changed()
│   ├── on_data_received()
│   ├── on_command_sent()
│   └── on_error_occurred()
└── Test Management
    ├── show_test_details()
    ├── configure_test()
    ├── start_test()
    └── stop_test()

TestConfigDialog (QDialog)
├── Dynamic form generation
├── Test-specific inputs
└── Configuration validation

ModernButton (QPushButton)
TestCard (QFrame)
AnimatedStackedWidget (QStackedWidget)
```

### Backend (backend.py)

```python
ESP32Backend (QObject)
├── Signals
│   ├── connection_status_changed
│   ├── data_received
│   ├── command_sent
│   └── error_occurred
├── Connection Management
│   ├── connect()
│   ├── disconnect()
│   └── _receive_data() [Thread]
├── Command Methods
│   ├── start_short_circuit_test()
│   ├── start_trip_test()
│   ├── start_temperature_test()
│   ├── set_power_factor()
│   ├── configure_rl_circuit()
│   ├── stop_test()
│   └── get_status()
└── Data Management
    ├── _parse_data()
    ├── get_latest_data()
    ├── get_all_data()
    └── clear_data()
```

### ESP32 (esp32_receiver.ino)

```cpp
Main Functions
├── setup()
│   ├── WiFi initialization
│   ├── Pin configuration
│   └── Server start
├── loop()
│   ├── Client connection handling
│   ├── Command reception
│   └── Data transmission
├── Command Processing
│   ├── processCommand()
│   ├── extractValue()
│   └── Test-specific handlers
├── Test Functions
│   ├── startShortCircuitTest()
│   ├── startTripTest()
│   ├── startTemperatureTest()
│   ├── setPowerFactor()
│   └── configureRLCircuit()
└── Sensor Functions
    ├── readSensors()
    ├── sendData()
    └── sendStatus()
```

## 🔐 Security Considerations

1. **Network Security**:
   - Use WPA2/WPA3 WiFi encryption
   - Consider VPN for remote access
   - Implement authentication (future)

2. **Command Validation**:
   - ESP32 validates all commands
   - Range checking on parameters
   - Timeout protection

3. **Safety Interlocks**:
   - Emergency stop always available
   - Maximum test duration limits
   - Automatic shutdown on errors

## 📊 Performance Metrics

- **Connection Time**: < 2 seconds
- **Command Latency**: < 50ms
- **Data Rate**: 10 samples/second
- **Max Data Points**: 10,000 per test
- **Memory Usage**: ~50MB (Python), ~100KB (ESP32)

## 🔧 Extensibility

### Adding New Tests

1. **Frontend**: Add test card and configuration dialog
2. **Backend**: Add command method
3. **ESP32**: Add command handler and test logic

### Adding New Sensors

1. **ESP32**: Add GPIO pin and reading function
2. **Backend**: Update data parser
3. **Frontend**: Add display widget

### Protocol Extensions

- Add authentication header
- Implement encryption
- Add compression for large data
- Support binary protocol

## 🎯 Design Principles

1. **Separation of Concerns**: UI, Logic, Hardware separated
2. **Event-Driven**: Signal-slot pattern for loose coupling
3. **Thread-Safe**: Background threads for I/O
4. **Modular**: Easy to extend and maintain
5. **User-Friendly**: Clear feedback and error handling
