# 🚀 Quick Start Guide - MCB Testing System

## ⚡ 5-Minute Setup

### Step 1: Upload ESP32 Code (2 minutes)

1. Open Arduino IDE
2. Open `esp32_receiver.ino`
3. Change these lines (lines 9-10):
   ```cpp
   const char* ssid = "YOUR_WIFI_NAME";      // ← Your WiFi name
   const char* password = "YOUR_PASSWORD";    // ← Your WiFi password
   ```
4. Click Upload button
5. Open Serial Monitor (115200 baud)
6. **Write down the IP address** shown (e.g., 192.168.1.100)

### Step 2: Run Python Application (1 minute)

```bash
# Install dependencies (first time only)
pip install PyQt5 numpy matplotlib

# Run the application
python frontend.py
```

### Step 3: Connect and Test (2 minutes)

1. **Connection Screen**:
   - Enter ESP32 IP address (from Step 1)
   - Port: 5000 (default)
   - Click "Connect to ESP32"
   - Wait for "✓ Connected"
   - Click "Continue to Testing"

2. **Test Dashboard**:
   - Click any test card (e.g., "Short-Circuit Breaking Capacity")

3. **Test Configuration**:
   - Click "⚙ Configure"
   - Set parameters (e.g., Current: 3000A)
   - Click OK

4. **Start Test**:
   - Click "▶ Start Test"
   - Watch real-time data
   - Click "⏹ Stop Test" when done

## 🎯 That's It!

You're now running a professional MCB testing system with WiFi communication!

## 📝 Quick Reference

### Common Test Parameters

**Short Circuit Test**:
- Current: 3000A, 6000A, or 10000A
- Voltage: 230V or 400V

**Trip Test**:
- MCB Type: B, C, or D
- Multiplier: 1.13× or 1.45×

**Temperature Test**:
- Rated Current: 16A, 20A, 32A
- Duration: 3600 seconds

### Troubleshooting

**Can't connect?**
- Check ESP32 Serial Monitor for IP
- Ensure PC and ESP32 on same WiFi
- Try pinging ESP32 IP

**No data?**
- Check test is running (ESP32 LED should be on)
- Look at Serial Monitor for errors
- Try sending STATUS command

## 🔗 Next Steps

- Read `README_INTEGRATION.md` for detailed info
- Check `INTEGRATION_SUMMARY.md` for architecture
- Run `test_integration.py` for backend testing
- Customize tests in `frontend.py`

## 💡 Pro Tips

1. **Use Static IP**: Configure ESP32 with static IP for reliability
2. **Monitor Serial**: Keep Serial Monitor open for debugging
3. **Test Connection**: Use STATUS command to verify ESP32 is responding
4. **Save Configs**: Configuration dialogs remember last values
5. **Emergency Stop**: Always available during tests

## 🎉 Enjoy Testing!

Your MCB testing system is ready for professional use!
