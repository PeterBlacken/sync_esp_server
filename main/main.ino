// Draft ESP32-S3 sketch for local time sync against the Python server.
//
// Steps:
// 1. Fill in your WiFi credentials and server IP/port.
// 2. Deploy to the ESP32-S3.
// 3. The device will connect to WiFi, issue an HTTP GET to /time, and log
//    the server's timestamp payload. You can expand this to compute clock
//    offsets using round-trip timing and apply it to your own RTC.

#include <WiFi.h>
#include <HTTPClient.h>

// TODO: update with your WiFi credentials
const char *WIFI_SSID = "YOUR_WIFI_SSID";
const char *WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// TODO: update with the machine running python/main.py
const char *SERVER_HOST = "192.168.1.10"; // Local IP of the Python server
const int SERVER_PORT = 8000;

// How long to wait between sync attempts (milliseconds)
const unsigned long SYNC_INTERVAL_MS = 5 * 60 * 1000;

unsigned long lastSync = 0;

void connectToWiFi()
{
  Serial.print("Connecting to WiFi");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  unsigned long startAttemptTime = millis();
  const unsigned long wifiTimeout = 20000; // 20 seconds

  while (WiFi.status() != WL_CONNECTED && millis() - startAttemptTime < wifiTimeout)
  {
    Serial.print(".");
    delay(500);
  }

  if (WiFi.status() == WL_CONNECTED)
  {
    Serial.printf("\nConnected! IP address: %s\n", WiFi.localIP().toString().c_str());
  }
  else
  {
    Serial.println("\nFailed to connect to WiFi");
  }
}

void requestServerTime()
{
  if (WiFi.status() != WL_CONNECTED)
  {
    Serial.println("WiFi not connected; skipping sync");
    return;
  }

  HTTPClient http;
  String url = String("http://") + SERVER_HOST + ":" + SERVER_PORT + "/time";

  Serial.printf("Requesting server time from %s\n", url.c_str());

  unsigned long requestStart = millis();
  http.begin(url);
  int httpCode = http.GET();
  unsigned long responseTime = millis() - requestStart;

  if (httpCode > 0)
  {
    String payload = http.getString();
    Serial.printf("Response code: %d, RTT: %lu ms\n", httpCode, responseTime);
    Serial.printf("Payload: %s\n", payload.c_str());

    // TODO: parse payload JSON and adjust RTC/timekeeping as needed.
    // For now we simply log the payload for debugging.
  }
  else
  {
    Serial.printf("HTTP request failed: %s\n", http.errorToString(httpCode).c_str());
  }

  http.end();
}

void setup()
{
  Serial.begin(115200);
  delay(500);
  connectToWiFi();
}

void loop()
{
  unsigned long now = millis();
  if (now - lastSync >= SYNC_INTERVAL_MS || lastSync == 0)
  {
    requestServerTime();
    lastSync = now;
  }

  // Simple retry if WiFi drops
  if (WiFi.status() != WL_CONNECTED)
  {
    connectToWiFi();
  }

  delay(1000);
}
