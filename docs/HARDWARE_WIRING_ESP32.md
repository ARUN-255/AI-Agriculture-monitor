# Agri Guard ESP32 wiring plan

This wiring plan is for a low-voltage bench prototype using an ESP32 DevKit V1. It does not include a mains-powered or high-current pump circuit.

## Parts

- ESP32 DevKit V1
- Capacitive soil-moisture sensor with analog output
- DHT22 temperature/humidity sensor
- JSN-SR04T waterproof ultrasonic distance sensor (or a compatible 5 V ultrasonic module)
- Resistors for two voltage dividers (solar and battery channels)
- Breadboard/jumper wires for bench testing
- Regulated supply appropriate for the ESP32 and each sensor

## Pin map

| Part | Signal | ESP32 pin |
|---|---|---|
| Capacitive soil sensor | AO | GPIO 34 |
| DHT22 | DATA | GPIO 4 |
| Ultrasonic sensor | TRIG | GPIO 5 |
| Ultrasonic sensor | ECHO through divider | GPIO 18 |
| Solar voltage divider | midpoint | GPIO 35 |
| Battery voltage divider | midpoint | GPIO 32 |
| All sensors | GND | GND |

GPIO 34, 35 and 32 are ADC1 inputs and are suitable for analog readings while Wi-Fi is active. Do not use 5 V logic on ESP32 GPIO pins.

## Wiring notes

### Capacitive soil moisture sensor
- Power from 3.3 V if the particular sensor supports it; verify its datasheet first.
- GND to ESP32 GND.
- AO to GPIO 34.
- Do not connect AO if the sensor can output more than 3.3 V. Use a suitable divider/buffer if needed.
- Calibrate raw readings in dry soil and in thoroughly wet soil. Enter the measured values as `SOIL_DRY_RAW` and `SOIL_WET_RAW` in `config.h`.

### DHT22
- VCC to 3.3 V, GND to GND, DATA to GPIO 4.
- For a bare 4-pin DHT22, add a 4.7k–10k pull-up from DATA to 3.3 V. Many breakout modules already include it.
- Confirm the pin order from the exact module datasheet.

### Waterproof ultrasonic tank sensor
- Power the selected JSN-SR04T module according to its datasheet (commonly 5 V).
- GND must be common with ESP32 GND.
- TRIG to GPIO 5 (check the module accepts 3.3 V trigger).
- ECHO is commonly 5 V logic: **never connect it directly** to ESP32. Use a divider, e.g. 10k from ECHO to GPIO 18 and 20k from GPIO 18 to GND (about 3.3 V from a 5 V echo).
- Mount the sensor above the tank, pointing down. Keep it away from the tank wall and turbulent inlet.
- Measure sensor-to-water distance with the tank empty and at the chosen full level; set `TANK_EMPTY_DISTANCE_CM` and `TANK_FULL_DISTANCE_CM`.

### Solar and battery voltage measurement
Use a separate divider for each channel:
- Monitored positive input -> 100k resistor -> ADC midpoint.
- ADC midpoint -> 10k resistor -> GND.
- ADC midpoint -> GPIO 35 (solar) or GPIO 32 (battery).
- Monitored negative -> common GND, only where the system design permits a shared reference.
- Ratio is (100k + 10k) / 10k = 11. A 30 V input becomes about 2.73 V at the ADC.
- Add an appropriately rated input fuse, reverse-polarity protection and filtering; use resistors with suitable voltage and power ratings.
- This example is for inputs no higher than 30 V. For higher voltages, redesign and verify the divider and protection before connecting anything.
- Do not connect a solar panel or battery directly to an ESP32 pin.
- Configure battery empty/full voltage limits for the exact battery chemistry and series count. A voltage-only percentage is approximate and can be misleading under load or while charging.

## First power-on checklist

1. Inspect for shorts before applying power.
2. Power the ESP32 from a regulated USB supply.
3. Verify sensor supply voltages with a multimeter.
4. Confirm no ESP32 GPIO receives more than 3.3 V.
5. Open Serial Monitor at 115200 baud.
6. Calibrate soil and tank values before relying on dashboard percentages.
7. Confirm telemetry appears in the cloud dashboard.

## Pump safety — not included in this prototype

The sketch intentionally has no pump output pin and never actuates a relay. Do not wire a pump to the ESP32. A later pump stage requires a properly rated relay/contactor or motor driver, fuse, enclosure, independent dry-run/low-water interlock, overcurrent protection, local emergency stop, watchdog/fail-off behavior and review by a qualified electrician. Cloud commands must not be the only safety mechanism.
