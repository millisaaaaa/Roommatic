# D1 mini Setup

This document explains how to upload the D1 mini firmware used by Roommatic.

## Firmware Location

Place the D1 mini Arduino sketch in:

```text
firmware/d1_mini/d1_mini.ino
```

The recommended project structure is:

```text
Roommatic/
└── firmware/
    └── d1_mini/
        └── d1_mini.ino
```

## Arduino IDE Setup

Open Arduino IDE and go to:

```text
File > Preferences > Additional Boards Manager URLs
```

Add the ESP8266 board URL:

```text
https://arduino.esp8266.com/stable/package_esp8266com_index.json
```

Then open:

```text
Tools > Board > Boards Manager
```

Search for and install:

```text
esp8266
```

Select the board:

```text
LOLIN(WEMOS) D1 R2 & mini
```

## Required Libraries

Install the following libraries from Arduino IDE Library Manager:

```text
DHT sensor library
Adafruit Unified Sensor
IRremoteESP8266
```

## Pin Settings

The current firmware uses:

```cpp
#define DHTPIN D2
#define DHTTYPE DHT22

const uint16_t kIrLed = D6;
```

If the wiring is changed, update the pin settings in:

```text
firmware/d1_mini/d1_mini.ino
```

## Upload Firmware

Connect the D1 mini to the computer by USB.

Arduino IDE settings:

```text
Board: LOLIN(WEMOS) D1 R2 & mini
Port: D1 mini serial port
Baud rate: 9600
```

Upload the firmware to the D1 mini.

## Serial Test

Open Serial Monitor and set:

```text
Baud rate: 9600
Line ending: Newline
```

Test commands:

```text
TEMP
GREE26
GREE_OFF
KEL26
KEL_OFF
```

If the D1 mini responds correctly, it can be connected to the Raspberry Pi.

## Raspberry Pi Serial Port

After connecting the D1 mini to the Raspberry Pi, check the serial port:

```bash
ls /dev/ttyUSB*
ls /dev/ttyACM*
```

If permission is denied, run:

```bash
sudo usermod -aG dialout pi
```

Then reboot or log in again.
