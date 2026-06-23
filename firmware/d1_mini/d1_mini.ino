#include <Arduino.h>
#include <DHT.h>

#include <IRremoteESP8266.h>
#include <IRsend.h>
#include <ir_Gree.h>
#include <ir_Kelvinator.h>

// =======================  
// 腳位設定
// =======================
#define DHTPIN D2
#define DHTTYPE DHT22

const uint16_t kIrLed = D6;

// =======================
// 物件建立
// =======================
DHT dht(DHTPIN, DHTTYPE);

IRGreeAC gree(kIrLed);
IRKelvinatorAC kel(kIrLed);

String inputString = "";
bool stringComplete = false;

// =======================
// DHT22 讀取
// =======================
void readDHT22() {
  float h = dht.readHumidity();
  float t = dht.readTemperature();

  if (isnan(h) || isnan(t)) {
    Serial.println("DHT_ERROR");
    return;
  }

  Serial.print("TEMP=");
  Serial.print(t, 2);
  Serial.print(",RH=");
  Serial.println(h, 2);
}

// =======================
// GREE 冷氣控制
// =======================
void greeSendCool(uint8_t temp, uint8_t fan) {
  Serial.print("[GREE] COOL ");
  Serial.print(temp);
  Serial.print("C, FAN=");
  Serial.println(fan);

  gree.begin();
  gree.on();
  gree.setMode(GREE_COOL);
  gree.setTemp(temp);
  gree.setFan(fan);
  gree.send();

  Serial.println("IR_DONE");
}

void greeOff() {
  Serial.println("[GREE] OFF");

  gree.begin();
  gree.off();
  gree.send();

  Serial.println("IR_DONE");
}

// =======================
// KELVINATOR 冷氣控制
// =======================
void kelSendCool(uint8_t temp, uint8_t fan) {
  Serial.print("[KELVINATOR] COOL ");
  Serial.print(temp);
  Serial.print("C, FAN=");
  Serial.println(fan);

  kel.begin();
  kel.on();
  kel.setMode(kKelvinatorCool);
  kel.setTemp(temp);
  kel.setFan(fan);
  kel.send();

  Serial.println("IR_DONE");
}

void kelOff() {
  Serial.println("[KELVINATOR] OFF");

  kel.begin();
  kel.off();
  kel.send();

  Serial.println("IR_DONE");
}

// =======================
// 指令處理
// =======================
void handleCommand(String cmd) {
  cmd.trim();

  if (cmd == "TEMP") {
    readDHT22();
  }
  else if (cmd == "GREE26") {
    greeSendCool(26, 3);
  }
  else if (cmd == "GREE_OFF") {
    greeOff();
  }
  else if (cmd == "KEL26") {
    kelSendCool(26, 3);
  }
  else if (cmd == "KEL_OFF") {
    kelOff();
  }
  else {
    Serial.print("UNKNOWN_CMD=");
    Serial.println(cmd);
  }
}

// =======================
// setup
// =======================
void setup() {
  Serial.begin(9600);
  delay(1000);

  dht.begin();

  gree.begin();
  kel.begin();

  Serial.println("D1_MINI_READY");
  Serial.println("Commands: TEMP, GREE26, GREE_OFF, KEL26, KEL_OFF");
}

// =======================
// loop
// =======================
void loop() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();

    if (inChar == '\n') {
      stringComplete = true;
    } else {
      inputString += inChar;
    }
  }

  if (stringComplete) {
    handleCommand(inputString);
    inputString = "";
    stringComplete = false;
  }
}