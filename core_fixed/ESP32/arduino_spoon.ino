#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>

// === Configure these ===
const char* ssid = "YOUR_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* SERVER = "https://your-public-host.example.com"; // include https://
const char* DEVICE_TOKEN = "REPLACE_WITH_DEVICE_UUID_TOKEN";

// If you have the CA certificate for your server, paste it here and use client.setCACert(ca_pem)
// const char* root_ca = "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----\n";

void setup() {
  Serial.begin(115200);
  delay(100);
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(250);
    Serial.print('.');
  }
  Serial.println("\nWiFi connected");

  WiFiClientSecure client;
  // Production: use setCACert(root_ca) or implement certificate pinning
  // client.setCACert(root_ca);
  client.setInsecure(); // DEVELOPMENT ONLY

  HTTPClient https;
  String url = String(SERVER) + "/dashboard/api/sodium/add-meal/";
  https.begin(client, url);
  https.addHeader("Content-Type", "application/json");
  https.addHeader("Authorization", String("Token ") + DEVICE_TOKEN);

  String payload = "{\"name\":\"spoon-meal\",\"sodium_mg\":123}";
  Serial.println("POST payload: " + payload);

  int httpCode = https.POST(payload);
  Serial.print("HTTP code: "); Serial.println(httpCode);
  if (httpCode > 0) {
    String resp = https.getString();
    Serial.println("Response: ");
    Serial.println(resp);
  } else {
    Serial.print("Request failed, error: ");
    Serial.println(https.errorToString(httpCode).c_str());
  }
  https.end();
}

void loop() {
  // Nothing — this example posts once on boot
  delay(10000);
}
