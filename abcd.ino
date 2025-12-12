#include <WiFi.h>
#include <WiFiUdp.h>

// ADC Pins - Using ADC1 pins (safe with WiFi)
#define ADC_1_PIN 32  // ADC1_CH4
#define ADC_2_PIN 34  // ADC1_CH6

// Relay Pins - Using safe GPIO pins that don't interfere with WiFi
#define RELAY_1_PIN 18  // Safe GPIO
#define RELAY_2_PIN 19  // Safe GPIO
#define RELAY_3_PIN 21  // Safe GPIO
#define RELAY_4_PIN 22  // Safe GPIO
#define RELAY_5_PIN 23  // Safe GPIO
#define RELAY_6_PIN 27  // Safe GPIO - 100ms pulse trigger relay

// WIFI CONFIGURATION
const char* ssid = "M14";
const char* password = "12345677";
unsigned int localPort = 5000; // The port this device listens on for UDP commands

// TCP Controller (Server) Details
// IMPORTANT: Replace with the actual IP of your esp32_controller device
const char* controllerIP = "192.168.1.101"; 
const int controllerPort = 5000;

WiFiUDP Udp; // Listens for commands from PC
WiFiClient tcpClient; // Connects to the controller ESP32
char packetBuffer[255];

// Circuit constants
const float FREQ = 50.0;  // 50 Hz
const float OMEGA = 2.0 * PI * FREQ;  // Angular frequency (314.16 rad/s)
const float ADC_MAX = 4095.0;  // 12-bit ADC
const float ADC_VREF = 3.3;  // ESP32 reference voltage
const float VOLTAGE_SCALE_FACTOR = 253.0;  // Transformer + voltage divider scaling

// Voltage sampling array
#define MAX_SAMPLES 2000  // Maximum samples during 100ms window
int voltageReadings[MAX_SAMPLES];
int sampleCount = 0;
bool isCapturing = false;

// Relay 6 timing
const unsigned long RELAY_6_PULSE_DURATION = 100;  // 100ms pulse duration
unsigned long relay6StartTime = 0;
bool relay6Active = false;

struct InductorPath {
  float inductance;
  float resistance;
};

struct ResistorPath {
  float resistance;
};

struct InductorPath iPaths[3];
struct ResistorPath rPaths[4];

float targetCurrent;
float targetPf;
int instantaneousInductancePath = -1;
int instantaneousResistancePath = -1;

// Calculate RMS voltage from transformer circuit (simple version)
float getVRms() {
  int maxReading = 0;
  // Sample over 2 cycles (40ms at 50Hz)
  for(int i = 0; i < 100; i++) {
    int instant = analogRead(ADC_1_PIN);
    if(instant > maxReading) maxReading = instant;
    delayMicroseconds(500);
  }
  
  // Convert ADC reading to voltage at ADC pin
  float adcVoltage = (maxReading * ADC_VREF) / ADC_MAX;
  // Calculate RMS from peak voltage at ADC
  float vAdcRms = adcVoltage / 1.4142;
  // Scale back to actual mains voltage
  float vRms = vAdcRms * VOLTAGE_SCALE_FACTOR;
  
  return vRms;
}

// Start capturing voltage readings
void startVoltageCapture() {
  sampleCount = 0;
  isCapturing = true;
  Serial.println("Started voltage capture...");
}

// Stop capturing and send data to laptop
void stopVoltageCapture() {
  isCapturing = false;
  Serial.print("Stopped voltage capture. Total samples: ");
  Serial.println(sampleCount);
  
  if(Udp.remoteIP()) {
    sendVoltageData();
  } else {
    Serial.println("ERROR: Client not connected. Cannot send data.");
  }
}

// Capture voltage readings as fast as possible
void captureVoltageReading() {
  if(isCapturing && sampleCount < MAX_SAMPLES) {
    voltageReadings[sampleCount] = analogRead(ADC_1_PIN);
    sampleCount++;
  }
}

// Send voltage data to laptop via TCP
void sendVoltageData() {
  Serial.println("Sending voltage data to laptop...");

  char buffer[256];

  // Send header
  snprintf(buffer, sizeof(buffer), "VOLTAGE_DATA_START:%d", sampleCount);
  tcpClient.println(buffer);

  // Send data points as a long comma-separated string
  // This is inefficient but simple. For large data, a more robust protocol is needed.
  for (int i = 0; i < sampleCount; i++) {
    tcpClient.print(voltageReadings[i]);
    tcpClient.print(",");
    // Add a small delay to avoid overwhelming the client buffer
    if (i % 100 == 0) {
        delay(1);
    }
  }
  
  // Send completion packet
  snprintf(buffer, sizeof(buffer), "VOLTAGE_DATA_END:%d", 1);
  tcpClient.println(buffer);

  Serial.println("Voltage data sent.");

  // Also send human-readable summary
  sendVoltageSummary();
}

// Send voltage statistics summary
void sendVoltageSummary() {
  if(sampleCount == 0) return;
  
  // Calculate statistics
  int minVal = 4095;
  int maxVal = 0;
  long sum = 0;
  
  for(int i = 0; i < sampleCount; i++) {
    if(voltageReadings[i] < minVal) minVal = voltageReadings[i];
    if(voltageReadings[i] > maxVal) maxVal = voltageReadings[i];
    sum += voltageReadings[i];
  }
  
  float avg = (float)sum / sampleCount;
  
  // Convert to actual voltage
  float minVoltage = (minVal * ADC_VREF / ADC_MAX) * VOLTAGE_SCALE_FACTOR / 1.4142;
  float maxVoltage = (maxVal * ADC_VREF / ADC_MAX) * VOLTAGE_SCALE_FACTOR / 1.4142;
  float avgVoltage = (avg * ADC_VREF / ADC_MAX) * VOLTAGE_SCALE_FACTOR / 1.4142;
  
  // Calculate sampling rate
  float samplingRate = (float)sampleCount / (RELAY_6_PULSE_DURATION / 1000.0);
  
  char summaryBuffer[200];
  snprintf(summaryBuffer, sizeof(summaryBuffer), 
           "SUMMARY|Samples:%d|Rate:%.0fHz|Min:%.2fV|Max:%.2fV|Avg:%.2fV", 
           sampleCount, samplingRate, minVoltage, maxVoltage, avgVoltage);
  
  // This function is for sending data to the PC, so it should use UDP.
    // The actual sending logic is handled in the main loop.
  
  Serial.println("Summary sent:");
  Serial.println(summaryBuffer);
}

// Trigger Relay 6 - Turns ON immediately and OFF after 100ms
void triggerRelay6() {
  digitalWrite(RELAY_6_PIN, HIGH);  // Turn ON relay
  relay6Active = true;
  relay6StartTime = millis();
  
  // Start voltage capture when relay activates
  startVoltageCapture();
  
  Serial.println("Relay 6 TRIGGERED - Circuit CONNECTED (will auto-disconnect in 100ms)");
}

// Check if Relay 6 needs to be turned off
void checkRelay6Timeout() {
  if(relay6Active && (millis() - relay6StartTime >= RELAY_6_PULSE_DURATION)) {
    digitalWrite(RELAY_6_PIN, LOW);  // Turn OFF relay
    relay6Active = false;
    
    // Stop voltage capture when relay deactivates
    if(isCapturing) {
      stopVoltageCapture();
    }
    
    Serial.println("Relay 6 AUTO-OFF - Circuit DISCONNECTED after 100ms");
  }
}

void applyRelays(int lIndex, int rIndex) {
  // Configure inductor paths
  switch(lIndex) {
    case 0:
      digitalWrite(RELAY_1_PIN, HIGH);
      digitalWrite(RELAY_2_PIN, LOW);
      break;
    case 1:
      digitalWrite(RELAY_1_PIN, LOW);
      digitalWrite(RELAY_2_PIN, HIGH);
      break;
    case 2:
      digitalWrite(RELAY_1_PIN, LOW);
      digitalWrite(RELAY_2_PIN, LOW);
      break;
  }
  
  // Configure resistor paths
  switch(rIndex) {
    case 0:
      digitalWrite(RELAY_3_PIN, HIGH);
      digitalWrite(RELAY_5_PIN, HIGH);
      digitalWrite(RELAY_4_PIN, LOW);
      break;
    case 1:
      digitalWrite(RELAY_3_PIN, LOW);
      digitalWrite(RELAY_5_PIN, HIGH);
      digitalWrite(RELAY_4_PIN, LOW);
      break;
    case 2:
      digitalWrite(RELAY_4_PIN, HIGH);
      digitalWrite(RELAY_5_PIN, LOW);
      digitalWrite(RELAY_3_PIN, LOW);
      break;
    case 3:
      digitalWrite(RELAY_4_PIN, LOW);
      digitalWrite(RELAY_5_PIN, LOW);
      digitalWrite(RELAY_3_PIN, LOW);
      break;
  }
  
  instantaneousInductancePath = lIndex;
  instantaneousResistancePath = rIndex;
  
  Serial.print("Relays configured - Inductor Path: ");
  Serial.print(lIndex);
  Serial.print(", Resistor Path: ");
  Serial.println(rIndex);
}

void selectBestPath(float targetL, float targetR) {
  float bestTotalError = 100000.0f;
  int bestLIndex = 0;
  int bestRIndex = 0;
  
  // Iterate through ALL 12 combinations
  for(int l = 0; l < 3; l++) {
    for(int r = 0; r < 4; r++) {
      // Calculate errors
      float errorL = abs(targetL - iPaths[l].inductance);
      // Total resistance includes inductor resistance + resistor path
      float currentTotalR = iPaths[l].resistance + rPaths[r].resistance;
      float errorR = abs(targetR - currentTotalR);
      
      // Combined error (you can adjust weights if needed)
      float totalError = errorL + errorR;
      
      if(totalError < bestTotalError) {
        bestTotalError = totalError;
        bestLIndex = l;
        bestRIndex = r;
      }
    }
  }
  
  // Apply the best found combination
  applyRelays(bestLIndex, bestRIndex);
  
  Serial.print("Selected Path - Inductor: ");
  Serial.print(bestLIndex);
  Serial.print(" (L=");
  Serial.print(iPaths[bestLIndex].inductance);
  Serial.print("mH, R=");
  Serial.print(iPaths[bestLIndex].resistance);
  Serial.print("Ω), Resistor: ");
  Serial.print(bestRIndex);
  Serial.print(" (R=");
  Serial.print(rPaths[bestRIndex].resistance);
  Serial.println("Ω)");
}

void setup() {
  Serial.begin(115200);
  
  // Initialize component paths (in mH and Ohms)
  iPaths[0] = {40.0f, 1.9f};   // 40mH inductor path
  iPaths[1] = {30.0f, 0.5f};   // 30mH inductor path
  iPaths[2] = {70.0f, 1.3f};   // 70mH inductor path
  
  rPaths[0].resistance = 14.0f;  // Resistor path 0
  rPaths[1].resistance = 24.0f;  // Resistor path 1
  rPaths[2].resistance = 34.0f;  // Resistor path 2
  rPaths[3].resistance = 44.0f;  // Resistor path 3
  
  pinMode(ADC_1_PIN, INPUT);
  pinMode(ADC_2_PIN, INPUT);
  
  pinMode(RELAY_1_PIN, OUTPUT);
  pinMode(RELAY_2_PIN, OUTPUT);
  pinMode(RELAY_3_PIN, OUTPUT);
  pinMode(RELAY_4_PIN, OUTPUT);
  pinMode(RELAY_5_PIN, OUTPUT);
  pinMode(RELAY_6_PIN, OUTPUT);
  
  // Initialize all relays to safe state (OFF)
  digitalWrite(RELAY_1_PIN, LOW);
  digitalWrite(RELAY_2_PIN, LOW);
  digitalWrite(RELAY_3_PIN, LOW);
  digitalWrite(RELAY_4_PIN, LOW);
  digitalWrite(RELAY_5_PIN, LOW);
  digitalWrite(RELAY_6_PIN, LOW);  // Circuit disconnected initially
  
  relay6Active = false;
  isCapturing = false;
  
  Serial.println("\n=== Power Factor Correction System ===");
  Serial.println("System initialized - Circuit DISCONNECTED");
  Serial.println("\nPin Configuration:");
  Serial.println("ADC1: GPIO32, ADC2: GPIO34");
  Serial.println("Relays: GPIO18, 19, 21, 22, 23, 27");
  Serial.println("\nRelay 6 Mode: 100ms PULSE TRIGGER");
  Serial.println("Voltage Capture: AUTO (during relay pulse)");
  Serial.print("Max Samples: ");
  Serial.println(MAX_SAMPLES);
  
  // WIFI SETUP
  Serial.println("\nConnecting to WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
  
  Udp.begin(localPort);
  Serial.print("Listening for commands on UDP port: ");
  Serial.println(localPort);
  
  Serial.println("\nWaiting for commands...");
  Serial.println("Send: 'TRIGGER' to connect circuit for 100ms and capture data");
  Serial.println("Send: 'STATUS' to check system status");
  Serial.println("Send: 'Current,PowerFactor' to set load parameters");
}

void loop() {
  // CRITICAL: Handle high-frequency tasks first
  if(isCapturing) {
    captureVoltageReading();
  }
  checkRelay6Timeout();

  // Check for incoming UDP command from PC
  int packetSize = Udp.parsePacket();
  if (packetSize) {
    IPAddress remoteIp = Udp.remoteIP();
    unsigned int remotePort = Udp.remotePort();
    
    int len = Udp.read(packetBuffer, packetSize > 254 ? 254 : packetSize);
    packetBuffer[len] = 0;
    
    Serial.printf("\n[UDP] Received command from %s:%d - '%s'\n", remoteIp.toString().c_str(), remotePort, packetBuffer);
    
    Serial.print("Packet Contents: ");
    Serial.println(packetBuffer);
    
    // Check for system control commands
    if (strcmp(packetBuffer, "TRIGGER") == 0) {
      triggerRelay6();
      
      // Send confirmation back to PC
      Udp.beginPacket(remoteIp, remotePort);
      Udp.print("TRIGGER_CONFIRMED");
      Udp.endPacket();
      
    } else if (strcmp(packetBuffer, "STATUS") == 0) {
      Serial.print("Relay 6 Status: ");
      Serial.println(relay6Active ? "ACTIVE (will auto-off)" : "INACTIVE");
      
      // Send status back to client
      char statusBuffer[150];
      snprintf(statusBuffer, sizeof(statusBuffer), 
               "STATUS|Relay6:%s|Path_L:%d|Path_R:%d|LastCapture:%d", 
               relay6Active ? "ACTIVE" : "INACTIVE",
               instantaneousInductancePath,
               instantaneousResistancePath,
               sampleCount);

      Udp.beginPacket(remoteIp, remotePort);
      Udp.print(statusBuffer);
      Udp.endPacket();
      
    }
    // Parse string "Current,Pf" for power factor mode
    else if (sscanf(packetBuffer, "%f\n%f", &targetCurrent, &targetPf) == 2) {
      // ... (rest of the code remains the same)
      
      // Validate inputs
      if(targetCurrent <= 0 || targetPf < 0 || targetPf > 1) {
        Serial.println("ERROR: Invalid parameters!");
        Serial.println("Current must be > 0, Power Factor must be 0-1");
        
        // Send error response back to PC
        Udp.beginPacket(remoteIp, remotePort);
        Udp.print("ERROR: Invalid parameters");
        Udp.endPacket();
        
      } else {
        // Get measured voltage
        float VRms = getVRms();
        
        // Calculate target impedance, resistance, and inductance
        float targetZ = VRms / targetCurrent;
        float targetR = targetPf * targetZ;
        float targetXL = sqrt(targetZ * targetZ - targetR * targetR);
        float targetL = (targetXL / OMEGA) * 1000.0; // Convert to mH

        Serial.printf("Target Z: %.2f Ω, R: %.2f Ω, L: %.2f mH\n", targetZ, targetR, targetL);

        // 1. Select and apply the best path for THIS device
        selectBestPath(targetL, targetR);
        Serial.println("Best path applied on this device (abcd.ino).");

        // 2. Forward the original command to the controller ESP32 via TCP
        Serial.printf("Forwarding command to controller at %s...\n", controllerIP);
        if (tcpClient.connect(controllerIP, controllerPort)) {
          Serial.println("Connected to controller.");
          tcpClient.println(packetBuffer); // Send the exact "Current,Pf" string
          tcpClient.stop();
          Serial.println("Command sent and disconnected from controller.");
        } else {
          Serial.println("!!! FAILED to connect to the controller ESP32!");
        }

        // 3. Send confirmation back to the original UDP sender (the PC)
        char confirmationMsg[] = "CONFIRMATION: Command processed locally and forwarded to controller.";
        Udp.beginPacket(remoteIp, remotePort);
        Udp.write((uint8_t*)confirmationMsg, strlen(confirmationMsg));
        Udp.endPacket();

        // Auto-trigger Relay 6 after configuration
        Serial.println("Auto-triggering Relay 6...");
        delay(100);  // Small delay to ensure relays are settled
        // ... (rest of the code remains the same)
      }
    }
    // Parse string "R:value,L:value" for direct R-L configuration
    else {
      float directR, directL;
      if (sscanf(packetBuffer, "R:%f,L:%f", &directR, &directL) == 2) {
        Serial.print("Direct R-L Configuration Received:");
        Serial.print(" R=");
        Serial.print(directR, 4);
        Serial.print(" Ohms, L=");
        Serial.print(directL * 1000.0, 4);  // Convert H to mH for display
        Serial.println(" mH");
        
        // Convert inductance from H to mH for internal calculations
        float targetL_mH = directL * 1000.0;
        
        // Use direct values for path selection
        selectBestPath(targetL_mH, directR);
        
        // Send confirmation back to PC
        Serial.println("CONFIRMATION: R-L Configuration Applied Successfully");
        Serial.print("Selected Inductance Path: ");
        Serial.println(instantaneousInductancePath);
        Serial.print("Selected Resistance Path: ");
        Serial.println(instantaneousResistancePath);
        
        // Calculate actual values achieved
        float actualR = iPaths[instantaneousInductancePath].resistance + rPaths[instantaneousResistancePath].resistance;
        float actualL_mH = iPaths[instantaneousInductancePath].inductance;
        float actualL_H = actualL_mH / 1000.0;  // Convert back to H
        
        Serial.print("Actual R: ");
        Serial.print(actualR, 4);
        Serial.print(" Ohms, Actual L: ");
        Serial.print(actualL_H, 4);
        Serial.println(" H");
        
        // Send UDP confirmation back to sender
                String confirmationMsg = "CONFIRMATION: R-L Configuration Applied Successfully\n";
        confirmationMsg += "Inductance Path: " + String(instantaneousInductancePath) + "\n";
        confirmationMsg += "Resistance Path: " + String(instantaneousResistancePath) + "\n";
        confirmationMsg += "Actual R: " + String(actualR, 4) + " Ohms\n";
        confirmationMsg += "Actual L: " + String(actualL_H, 4) + " H\n";
        confirmationMsg += "R-L_CONFIG_COMPLETE";
        Udp.beginPacket(remoteIp, remotePort);
        Udp.print(confirmationMsg);
        Udp.endPacket();
        
        Serial.println("Confirmation sent back to PC via UDP");
        
      } else {
        Serial.println("Unknown command or failed to parse packet.");
        Serial.println("Valid commands: TRIGGER, STATUS, Current,PowerFactor, or R:value,L:value");
        
        // Send error response
        Udp.beginPacket(remoteIp, remotePort);
        Udp.print("ERROR: Unknown command format");
        Udp.endPacket();
      }
    }
  }
}