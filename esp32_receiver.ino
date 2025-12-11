#include <WiFi.h>
#include <WiFiUdp.h>

#define ADC_1_PIN 32
#define ADC_2_PIN 34
#define RELAY_1_PIN 18
#define RELAY_2_PIN 19
#define RELAY_3_PIN 21
#define RELAY_4_PIN 22
#define RELAY_5_PIN 23

// WIFI CONFIGURATION
const char* ssid = "M14";         // Enter your WiFi name
const char* password = "12345677"; // Enter your WiFi password
unsigned int localPort = 5000;               // Port to listen on

WiFiUDP Udp;
char packetBuffer[255];
IPAddress senderIP;
unsigned int senderPort;

struct InductorPath
{
  float inductance;
  float resistance;
};
struct ResistorPath
{
  float resistance;
};

struct InductorPath iPaths[3];
struct ResistorPath rPaths[4];

float targetCurrent;
float targetPf;
int instantaneousInductancePath;
int instantaneousResistancePath;

float getVRms()
{
  int max = 0;
  for(int i = 0; i < 100; i++)
  {
    int instant = analogRead(ADC_1_PIN);
    if(instant > max) max = instant;
    delayMicroseconds(500);
  }
  max -= 2042;
  float vRms = max * 0.321;
  vRms /= 1.4142;
  return vRms;
}

void selectBestPath(float targetL, float targetR)
{
  float min = 10000.0f;
  int bestInductancePath;
  int bestResistancePath;
  for(int i = 0; i < 3; i++)
  {
    float difference = targetL - iPaths[i].inductance;
    if(difference < 0.0f) difference *= -1;
    if(difference < min)
    {
      min = difference;
      bestInductancePath = i;
    }
  }

  min = 10000.0f;
  for(int i = 0; i < 4; i++)
  {
    float difference = targetR - iPaths[bestInductancePath].resistance - rPaths[i].resistance;
    if(difference < 0.0f) difference *= -1;
    if(difference < min)
    {
      min = difference;
      bestResistancePath = i;
    }
  }

  switch(bestInductancePath)
  {
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
  switch(bestResistancePath)
  {
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
  instantaneousInductancePath = bestInductancePath;
  instantaneousResistancePath = bestResistancePath;
}

void setup() {
  // put your setup code here, to run once:
  iPaths[0] = {30.0f, 0.5f};
  iPaths[1] = {50.0f, 1.0f};
  iPaths[2] = {70.0f, 1.3f};
  rPaths[0].resistance = 14.0f;
  rPaths[1].resistance = 24.0f;
  rPaths[2].resistance = 34.0f;
  rPaths[3].resistance = 44.0f;

  pinMode(32, INPUT);
  pinMode(34, INPUT);
  
  pinMode(RELAY_1_PIN, OUTPUT);
  pinMode(RELAY_2_PIN, OUTPUT);
  pinMode(RELAY_3_PIN, OUTPUT);
  pinMode(RELAY_4_PIN, OUTPUT);
  pinMode(RELAY_5_PIN, OUTPUT);

  Serial.begin(115200);

  // WIFI SETUP
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("Waiting for connection"); // Added line
  }
  Serial.println("Connected");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
  
  Udp.begin(localPort);
}

void loop() {
  // Check for incoming packets
  int packetSize = Udp.parsePacket();

  if (packetSize) {
    Serial.print("Received packet of size ");
    Serial.println(packetSize);
    
    // Get sender information for response
    senderIP = Udp.remoteIP();
    senderPort = Udp.remotePort();

    // Read the packet into the buffer
    int len = Udp.read(packetBuffer, 255);
    if (len > 0) {
      packetBuffer[len] = 0;
    }

    Serial.print("Packet Contents: ");
    Serial.println(packetBuffer);
    Serial.print("From IP: ");
    Serial.print(senderIP);
    Serial.print(", Port: ");
    Serial.println(senderPort);

    // Try to parse as "Current,Pf" format first
    if (sscanf(packetBuffer, "%f,%f", &targetCurrent, &targetPf) == 2) {
      Serial.print("Parsed Current: ");
      Serial.println(targetCurrent);
      Serial.print("Parsed Power Factor: ");
      Serial.println(targetPf);

      // Proceed with calculations and path selection
      float VRms = getVRms();
      float targetZ = VRms / targetCurrent;
      float targetR = targetPf * targetZ;
      float targetL = sqrt(targetZ * targetZ - targetR * targetR) / 0.31416;
      selectBestPath(targetL, targetR);
      Serial.println("Best path selected based on new data.");
    } 
    // Try to parse as "R:value,L:value" format for direct R-L configuration
    else {
      float directR, directL;
      if (sscanf(packetBuffer, "R:%f,L:%f", &directR, &directL) == 2) {
        Serial.print("Direct R-L Configuration Received:");
        Serial.print(" R=");
        Serial.print(directR, 4);
        Serial.print(" Ohms, L=");
        Serial.print(directL, 4);
        Serial.println(" H");
        
        // Use direct values for path selection
        selectBestPath(directL, directR);
        
        // Send confirmation back to PC via UDP
        Serial.println("CONFIRMATION: R-L Configuration Applied Successfully");
        Serial.print("Selected Inductance Path: ");
        Serial.println(instantaneousInductancePath);
        Serial.print("Selected Resistance Path: ");
        Serial.println(instantaneousResistancePath);
        
        // Calculate actual values achieved
        float actualR = iPaths[instantaneousInductancePath].resistance + rPaths[instantaneousResistancePath].resistance;
        float actualL = iPaths[instantaneousInductancePath].inductance;
        
        Serial.print("Actual R: ");
        Serial.print(actualR, 4);
        Serial.print(" Ohms, Actual L: ");
        Serial.print(actualL, 4);
        Serial.println(" H");
        
        // Send UDP confirmation back to sender
        String confirmationMsg = "CONFIRMATION: R-L Configuration Applied Successfully\n";
        confirmationMsg += "Inductance Path: " + String(instantaneousInductancePath) + "\n";
        confirmationMsg += "Resistance Path: " + String(instantaneousResistancePath) + "\n";
        confirmationMsg += "Actual R: " + String(actualR, 4) + " Ohms\n";
        confirmationMsg += "Actual L: " + String(actualL, 4) + " H\n";
        confirmationMsg += "R-L_CONFIG_COMPLETE";
        
        Udp.beginPacket(senderIP, senderPort);
        Udp.print(confirmationMsg);
        Udp.endPacket();
        
        Serial.println("Confirmation sent back to PC via UDP");
      } else {
        Serial.println("Failed to parse packet in any known format.");
      }
    }
  } 
  // The loop will continue to run, checking for new packets on each iteration.
  // Add a small delay to avoid spamming the CPU if you have other tasks.
  delay(10);
}
