/*
  Agri Guard ESP32 sensor firmware - prototype only.
  Reads sensors and posts telemetry to the existing FastAPI device endpoints.
  Pump commands are received and logged only; no pump GPIO/relay is driven.
  Copy config.example.h to config.h and fill in your own private values.
*/
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include "config.h"

#define DHT_TYPE DHT22
DHT dht(DHT_PIN, DHT_TYPE);

static unsigned long lastSend = 0;
static unsigned long lastCommandPoll = 0;
static bool lastReportedPumpCommand = false;

float readSoilPercent() {
  const int raw = analogRead(SOIL_PIN);
  // Sensor raw values vary; calibrate dry/wet values in config.h.
  float pct = 100.0f * (SOIL_DRY_RAW - raw) / float(SOIL_DRY_RAW - SOIL_WET_RAW);
  return constrain(pct, 0.0f, 100.0f);
}

float readVoltage(uint8_t pin, float dividerRatio) {
  // analogReadMilliVolts() uses the ESP32 ADC calibration where supported.
  const float adcVolts = analogReadMilliVolts(pin) / 1000.0f;
  return adcVolts * dividerRatio;
}

float readTankPercent() {
  digitalWrite(ULTRASONIC_TRIG_PIN, LOW);
  delayMicroseconds(3);
  digitalWrite(ULTRASONIC_TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(ULTRASONIC_TRIG_PIN, LOW);

  // A timeout prevents the firmware from hanging if the sensor is disconnected.
  const unsigned long duration = pulseIn(ULTRASONIC_ECHO_PIN, HIGH, 30000UL);
  if (duration == 0) return NAN;

  const float distanceCm = duration * 0.0343f / 2.0f;
  const float pct = 100.0f * (TANK_EMPTY_DISTANCE_CM - distanceCm) /
                    (TANK_EMPTY_DISTANCE_CM - TANK_FULL_DISTANCE_CM);
  return constrain(pct, 0.0f, 100.0f);
}

float batteryPercentFromVoltage(float volts) {
  // These limits MUST be configured for the exact battery chemistry and pack.
  const float pct = 100.0f * (volts - BATTERY_EMPTY_VOLTS) /
                    (BATTERY_FULL_VOLTS - BATTERY_EMPTY_VOLTS);
  return constrain(pct, 0.0f, 100.0f);
}

bool ensureWiFi() {
  if (WiFi.status() == WL_CONNECTED) return true;
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to Wi-Fi");
  const unsigned long started = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - started < 20000) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("Wi-Fi connected. IP: ");
    Serial.println(WiFi.localIP());
    return true;
  }
  Serial.println("Wi-Fi unavailable; will retry.");
  return false;
}

bool postReading(float soil, float temperature, float humidity,
                 float tank, float batteryPct, float solarVolts) {
  if (!ensureWiFi()) return false;

  WiFiClientSecure tls;
  // Prototype convenience only. Before production, replace with tls.setCACert()
  // using the verified root CA certificate for the API host.
  tls.setInsecure();

  HTTPClient http;
  const String url = String(API_BASE_URL) + "/readings";
  if (!http.begin(tls, url)) {
    Serial.println("Could not start HTTPS request.");
    return false;
  }
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-Device-Token", DEVICE_TOKEN);

  JsonDocument doc;
  doc["user_id"] = FARM_USER_ID;
  doc["soil_moisture"] = soil;
  doc["temperature"] = temperature;
  doc["humidity"] = humidity;
  doc["water_tank"] = tank;
  doc["battery_level"] = batteryPct;
  doc["solar_voltage"] = solarVolts;
  // No physical pump is connected in this firmware version.
  doc["pump_on"] = false;
  doc["water_used_l"] = 0.0;

  String body;
  serializeJson(doc, body);
  const int status = http.POST(body);
  const String response = http.getString();
  Serial.printf("POST /readings -> HTTP %d\n", status);
  if (status < 200 || status >= 300) Serial.println(response);
  http.end();
  return status >= 200 && status < 300;
}

void pollPumpCommand() {
  if (!ensureWiFi()) return;

  WiFiClientSecure tls;
  // Prototype convenience only; replace with tls.setCACert() before production.
  tls.setInsecure();

  HTTPClient http;
  String url = String(API_BASE_URL) + "/device/command?user_id=" + FARM_USER_ID;
  if (!http.begin(tls, url)) return;
  http.addHeader("X-Device-Token", DEVICE_TOKEN);
  const int status = http.GET();
  if (status == 200) {
    JsonDocument doc;
    const DeserializationError err = deserializeJson(doc, http.getString());
    if (!err) {
      const bool command = doc["pump_command"] | false;
      const char* mode = doc["mode"] | "unknown";
      if (command != lastReportedPumpCommand) {
        Serial.printf("Cloud pump command changed: %s (mode: %s). "
                      "No relay is connected; command is NOT executed.\n",
                      command ? "ON" : "OFF", mode);
        lastReportedPumpCommand = command;
      }
    }
  } else {
    Serial.printf("GET /device/command -> HTTP %d\n", status);
  }
  http.end();
}

void setup() {
  Serial.begin(115200);
  delay(300);
  pinMode(ULTRASONIC_TRIG_PIN, OUTPUT);
  pinMode(ULTRASONIC_ECHO_PIN, INPUT);
  analogReadResolution(12);
  analogSetPinAttenuation(SOIL_PIN, ADC_11db);
  analogSetPinAttenuation(SOLAR_VOLTAGE_PIN, ADC_11db);
  analogSetPinAttenuation(BATTERY_VOLTAGE_PIN, ADC_11db);
  dht.begin();

  Serial.println("\nAgri Guard ESP32 sensor prototype starting.");
  Serial.println("Pump output is disabled. Do not connect a live pump.");
  ensureWiFi();
}

void loop() {
  const unsigned long now = millis();

  if (now - lastSend >= SENSOR_INTERVAL_MS || lastSend == 0) {
    lastSend = now;
    const float temperature = dht.readTemperature();
    const float humidity = dht.readHumidity();
    const float tank = readTankPercent();
    const float solar = readVoltage(SOLAR_VOLTAGE_PIN, SOLAR_DIVIDER_RATIO);
    const float battery = readVoltage(BATTERY_VOLTAGE_PIN, BATTERY_DIVIDER_RATIO);

    if (isnan(temperature) || isnan(humidity) || isnan(tank)) {
      Serial.println("Sensor read failed. Check DHT22/tank sensor wiring; skipping upload.");
    } else {
      const float soil = readSoilPercent();
      const float batteryPct = batteryPercentFromVoltage(battery);
      Serial.printf("Soil %.1f%% | Air %.1f C | RH %.1f%% | Tank %.1f%% | "
                    "Battery %.2f V (%.1f%%) | Solar %.2f V\n",
                    soil, temperature, humidity, tank, battery, batteryPct, solar);
      postReading(soil, temperature, humidity, tank, batteryPct, solar);
    }
  }

  if (now - lastCommandPoll >= COMMAND_POLL_INTERVAL_MS || lastCommandPoll == 0) {
    lastCommandPoll = now;
    pollPumpCommand();
  }
  delay(20);
}
