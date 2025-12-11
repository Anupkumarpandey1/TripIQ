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

    // Read the packet into the buffer
    int len = Udp.read(packetBuffer, 255);
    if (len > 0) {
      packetBuffer[len] = 0;
    }

    Serial.print("Packet Contents: ");
    Serial.println(packetBuffer);

    // Parse string "Current,Pf"
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
    } else {
      Serial.println("Failed to parse packet.");
    }
  } 
  // The loop will continue to run, checking for new packets on each iteration.
  // Add a small delay to avoid spamming the CPU if you have other tasks.
  delay(10);
}
