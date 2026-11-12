// Copy this file to config.h. Never commit config.h or share the device token.
#pragma once

#define WIFI_SSID "YOUR_WIFI_NAME"
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"

// Use the deployed HTTPS API base URL, without a trailing slash.
#define API_BASE_URL "https://agri-guard-api.onrender.com"
#define FARM_USER_ID "YOUR_SUPABASE_AUTH_USER_UUID"
#define DEVICE_TOKEN "YOUR_RENDER_DEVICE_TOKEN"

// ESP32 DevKit V1 pin plan (ADC1 pins are used for analog sensors).
#define SOIL_PIN 34
#define DHT_PIN 4
#define ULTRASONIC_TRIG_PIN 5
#define ULTRASONIC_ECHO_PIN 18
#define SOLAR_VOLTAGE_PIN 35
#define BATTERY_VOLTAGE_PIN 32

// Soil sensor calibration: measure raw ADC values in dry and wet soil.
// Replace these example values after calibration.
#define SOIL_DRY_RAW 3000
#define SOIL_WET_RAW 1300

// Tank sensor calibration: measure distance from sensor face to water surface
// when tank is empty and when it is at the chosen "full" level.
#define TANK_EMPTY_DISTANCE_CM 100.0f
#define TANK_FULL_DISTANCE_CM 15.0f

// Each voltage divider: R_TOP from monitored positive voltage to ADC input;
// R_BOTTOM from ADC input to GND. With 100k and 10k, ratio = (100+10)/10 = 11.
// Use appropriately rated resistors, protection and a common ground.
// Do not measure more than 30 V with this example divider/firmware configuration.
#define SOLAR_DIVIDER_RATIO 11.0f
#define BATTERY_DIVIDER_RATIO 11.0f

// REQUIRED: set these to the safe empty/full voltage limits for your exact
// battery chemistry and series count. The following are placeholders ONLY
// for a nominal 12 V lead-acid example; do not use them for another battery.
#define BATTERY_EMPTY_VOLTS 11.8f
#define BATTERY_FULL_VOLTS 12.7f

#define SENSOR_INTERVAL_MS 10000UL
#define COMMAND_POLL_INTERVAL_MS 5000UL
