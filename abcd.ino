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
const char* ssid = "M14"; // <-- IMPORTANT: SET YOUR WIFI NAME
const char* password = "12345677"; // <-- IMPORTANT: SET YOUR WIFI PASSWORD

// TCP Server for Python App
WiFiServer server(8888);
WiFiClient client;

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
  
  // Send data if a client is connected
  if (client && client.connected()) {
    sendVoltageData();
  } else {
    Serial.println("No client connected. Data not sent.");
  }
}

// Capture voltage readings as fast as possible
void captureVoltageReading() {
  if(isCapturing && sampleCount < MAX_SAMPLES) {
    voltageReadings[sampleCount] = analogRead(ADC_1_PIN);
    sampleCount++;
  }
}

// Send voltage data to the connected Python client
void sendVoltageData() {
  if (!client || !client.connected()) {
    Serial.println("Cannot send data, no client.");
    return;
  }

  Serial.println("Sending voltage data to Python client...");

  // Send each reading as a new line
  for (int i = 0; i < sampleCount; i++) {
    // Convert the integer reading to a scaled voltage value
    float voltage = (voltageReadings[i] * ADC_VREF / ADC_MAX) * VOLTAGE_SCALE_FACTOR;
    client.println(voltage, 2); // Send as float with 2 decimal places
    
    // A small delay can help prevent overwhelming the client
    delay(1);
  }

  Serial.println("Voltage data sending complete.");
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
  
  server.begin();
  Serial.println("TCP server started.");
  
  Serial.println("\nWaiting for commands...");
  Serial.println("Send: 'TRIGGER' to connect circuit for 100ms and capture data");
  Serial.println("Send: 'STATUS' to check system status");
  Serial.println("Send: 'Current,PowerFactor' to set load parameters");
}

void loop() {
  // Handle high-frequency tasks
  if (isCapturing) {
    captureVoltageReading();
  }
  checkRelay6Timeout();

  // Check for new client connections
  if (server.hasClient()) {
    // If a client is already connected, disconnect it first
    if (client && client.connected()) {
      client.stop();
      Serial.println("Existing client disconnected.");
    }
    client = server.available();
    if (client) {
      Serial.println("New Python client connected!");
    }
  }

  // If a client is connected, check for incoming commands
  if (client && client.connected()) {
    if (client.available()) {
      String command = client.readStringUntil('\n');
      command.trim();
      Serial.print("Received command from Python: ");
      Serial.println(command);

      // --- Command Parsing ---
      if (command.equalsIgnoreCase("TRIGGER")) {
        triggerRelay6();
        client.println("ACK: TRIGGER command received.");
      } 
      else if (command.equalsIgnoreCase("STATUS")) {
        char statusBuffer[150];
        snprintf(statusBuffer, sizeof(statusBuffer), 
                 "STATUS|Relay6:%s|Path_L:%d|Path_R:%d|LastCapture:%d", 
                 relay6Active ? "ACTIVE" : "INACTIVE",
                 instantaneousInductancePath,
                 instantaneousResistancePath,
                 sampleCount);
        client.println(statusBuffer);
      } 
      else {
        // Try parsing for "Current,PowerFactor"
        if (sscanf(command.c_str(), "%f,%f", &targetCurrent, &targetPf) == 2) {
          float VRms = getVRms();
          float targetZ = VRms / targetCurrent;
          float targetR = targetPf * targetZ;
          float targetXL = sqrt(targetZ * targetZ - targetR * targetR);
          float targetL = (targetXL / OMEGA) * 1000.0; // Convert to mH
          
          selectBestPath(targetL, targetR);
          client.println("ACK: Power Factor command processed.");
          
          // Auto-trigger after setting path
          delay(100);
          triggerRelay6();
        }
        // Try parsing for "R:value,L:value"
        else {
          float directR, directL;
          if (sscanf(command.c_str(), "R:%f,L:%f", &directR, &directL) == 2) {
            float targetL_mH = directL * 1000.0;
            selectBestPath(targetL_mH, directR);
            client.println("ACK: R-L command processed.");
            
            // Auto-trigger after setting path
            delay(100);
            triggerRelay6();
          } else {
            client.println("ERROR: Unknown command format.");
          }
        }
      }
    }
  }
}