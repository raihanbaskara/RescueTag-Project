#include <SPI.h>
#include <LoRa.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// ==========================================
// PIN DEFINITION SESUAI DESAIN PCB ESP32
// ==========================================
#define LORA_SS    5    // D05
#define LORA_RST   14   // D14
#define LORA_DIO0  26   // D26

#define OLED_SCL   22   // D22
#define OLED_SDA   21   // D21

Adafruit_SSD1306 display(-1);

void setup() {
  Serial.begin(115200);

  // Inisialisasi OLED SSD1306 (128x64)
  Wire.begin(OLED_SDA, OLED_SCL);
  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  display.clearDisplay();
  display.setTextColor(WHITE);
  display.setTextSize(1);
  display.setCursor(0, 4);
  display.println("RESCUE-TAG GATEWAY");
  display.drawLine(0, 14, 127, 14, WHITE);
  display.setCursor(0, 20);
  display.println("Init LoRa 433 MHz...");
  display.display();

  // Inisialisasi LoRa SX1278
  LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);
  if (!LoRa.begin(433E6)) {
    Serial.println("ERROR: ESP32 LoRa Init Failed! Cek solderan/jalur PCB.");
    display.setCursor(0, 35);
    display.println("LoRa INIT ERROR!");
    display.display();
    while (1);
  }

  // Parameter LoRa SAMA PERSIS DENGAN STM32
  LoRa.setSpreadingFactor(7);     // SF7 respon super cepat (~77 ms)
  LoRa.setSignalBandwidth(125E3); // 125 kHz
  LoRa.setCodingRate4(5);        // 4/5
  LoRa.setSyncWord(0x12);        // Sync word identik

  Serial.println("ESP32 Gateway Ready. Listening LoRa packets (SF7, Sync 0x12)...");
  Serial.println("HEADER:FEAT,a_total,g_total,a_max,a_min,g_mean,a_std,g_max,ax,ay,az,model_pred,triage_pred,hr,spo2,temp");

  display.clearDisplay();
  display.setCursor(0, 4);
  display.println("RESCUE-TAG GATEWAY");
  display.drawLine(0, 14, 127, 14, WHITE);
  display.setCursor(0, 22);
  display.println("LoRa: 433 MHz [OK]");
  display.setCursor(0, 36);
  display.println("Mode: SF7 Listening");
  display.setCursor(0, 50);
  display.println("Menunggu transmisi...");
  display.display();
}

void loop() {
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    String incoming = "";
    while (LoRa.available()) {
      incoming += (char)LoRa.read();
    }
    int rssi = LoRa.packetRssi();

    int triageCode = -1;
    int hr = 0;
    int spo2 = 0;
    float a_max = 1.0f;
    float temp = 36.6f;
    bool is_relayed = false;
    String cleanFeat = incoming;

    // A1. Cek Apakah Paket Datang Melalui 1-Hop Relay: RELAY,TAG01,FEAT,...
    if (incoming.startsWith("RELAY,")) {
      is_relayed = true;
      int featPos = incoming.indexOf("FEAT,");
      if (featPos != -1) {
        cleanFeat = incoming.substring(featPos);
      }
    }

    // A2. Parse Paket FEAT 50 Hz (Langsung maupun via Relay)
    // Format: FEAT,a_total,g_total,a_max,a_min,g_mean,a_std,g_max,ax,ay,az,model_pred,triage_pred,hr,spo2,temp
    if (cleanFeat.startsWith("FEAT,")) {
      // 1. Cetak ke Serial USB Laptop untuk ditangkap Node-RED & Python
      // Jika relay, beri tanda agar Node-RED bisa mengenali jalur 1-Hop Relay
      if (is_relayed) {
        Serial.print("RELAY,TAG01,");
      }
      Serial.println(cleanFeat);

      // 2. Ekstraksi parameter klinis untuk display OLED
      int commaIdx[16];
      int commaCount = 0;
      for (int i = 0; i < cleanFeat.length() && commaCount < 16; i++) {
        if (cleanFeat.charAt(i) == ',') {
          commaIdx[commaCount++] = i;
        }
      }

      if (commaCount >= 12) {
        a_max = cleanFeat.substring(commaIdx[2] + 1, commaIdx[3]).toFloat();
        triageCode = cleanFeat.substring(commaIdx[11] + 1, commaIdx[12]).toInt();
      }
      if (commaCount >= 14) {
        hr = cleanFeat.substring(commaIdx[12] + 1, commaIdx[13]).toInt();
        spo2 = cleanFeat.substring(commaIdx[13] + 1, commaIdx[14]).toInt();
      }
      if (commaCount >= 15) {
        temp = cleanFeat.substring(commaIdx[14] + 1).toFloat();
      }
    } 
    // B. Fallback Format Telemetri Lama: ax,ay,az,gx,gy,gz,hr,spo2,temp,triage
    else {
      Serial.print(incoming);
      Serial.print(",");
      Serial.println(rssi);

      int lastComma = incoming.lastIndexOf(',');
      if (lastComma != -1) {
        triageCode = incoming.substring(lastComma + 1).toInt();
      }
    }

    // 3. Tampilkan Status Real-time pada Layar OLED Gateway
    display.clearDisplay();
    display.setTextSize(1);

    if (triageCode == 3) {
      // 🔴 DARURAT JATUH / ASFIKSIA (Inverse Header)
      display.fillRect(0, 0, 128, 13, WHITE);
      display.setTextColor(BLACK);
      display.setCursor(4, 3);
      display.println("! ! ALARM DARURAT ! !");
      display.setTextColor(WHITE);

      display.setCursor(0, 17);
      display.println("TRIAGE: [JATUH / SOS]");
    } 
    else if (triageCode == 2) {
      // 🟠 WASPADA DINI (KELELAHAN EKSTREM)
      display.fillRect(0, 0, 128, 13, WHITE);
      display.setTextColor(BLACK);
      display.setCursor(4, 3);
      display.println("! WASPADA DINI !");
      display.setTextColor(WHITE);

      display.setCursor(0, 17);
      display.println("TRIAGE: [KELELAHAN/HR]");
    }
    else if (triageCode == 1) {
      // 🟡 KERJA AKTIF
      display.setTextColor(WHITE);
      display.setCursor(0, 2);
      display.println("RESCUE-TAG GATEWAY");
      display.drawLine(0, 12, 127, 12, WHITE);

      display.setCursor(0, 17);
      display.println("TRIAGE: [KERJA AKTIF]");
    } 
    else if (triageCode == 4) {
      // ⚪ STANDBY (JAM DILEPAS)
      display.setTextColor(WHITE);
      display.setCursor(0, 2);
      display.println("RESCUE-TAG GATEWAY");
      display.drawLine(0, 12, 127, 12, WHITE);

      display.setCursor(0, 17);
      display.println("TRIAGE: [JAM DILEPAS]");
    }
    else {
      // 🟢 NORMAL / AMAN
      display.setTextColor(WHITE);
      display.setCursor(0, 2);
      display.println("RESCUE-TAG GATEWAY");
      display.drawLine(0, 12, 127, 12, WHITE);

      display.setCursor(0, 17);
      display.println("TRIAGE: [AMAN / NORMAL]");
    }

    // Baris 3: Detak Jantung & Saturasi Oksigen
    display.setCursor(0, 31);
    display.print("Nadi : ");
    if (hr > 0) { display.print(hr); display.print(" bpm"); }
    else if (triageCode == 4) { display.print("-- (Lepas)"); }
    else { display.print("Ukur..."); }

    display.print(" | ");
    if (spo2 > 0) { display.print(spo2); display.print("%"); }
    else { display.print("--%"); }

    // Baris 4: Akselerasi Puncak & Sinyal LoRa
    display.setCursor(0, 44);
    display.print("A_Max: "); display.print(a_max, 1); display.print("g");
    display.print(" | "); display.print(rssi); display.println("dBm");

    // Baris 5: Link Status & Route
    display.setCursor(0, 56);
    if (is_relayed) {
      display.print("Rute : 1-Hop [TAG #01]");
    } else {
      display.print("Rute : Direct LoRa OK");
    }

    display.display();
  }
}
