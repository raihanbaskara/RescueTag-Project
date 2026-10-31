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

#define SCREEN_WIDTH  128
#define SCREEN_HEIGHT 64
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

// Variabel status telemetri terakhir untuk update layar stabil
int last_triage = -1;
int last_hr = 0;
int last_spo2 = 0;
float last_temp = 36.6f;
float last_amax = 1.0f;
int last_rssi = -65;
bool last_relayed = false;
bool last_node01 = false;
unsigned long last_rx_time = 0;
unsigned long last_direct_rx = 0; // Waktu terakhir paket langsung dari Jam #02 diterima

void renderGatewayOLED(int triageCode, int hr, int spo2, float temp, float a_max, int rssi, bool is_relayed, bool is_node01) {
  display.clearDisplay();
  display.setTextSize(1);

  // 1. Header Taktis Posko - Rata Tengah Sesuai Permintaan (0 - 10px)
  display.setTextColor(WHITE);
  display.setCursor(10, 1); // 18 karakter * 6px = 108px -> (128-108)/2 = x=10 (Tepat di Tengah!)
  display.print("GATEWAY RESCUE-TAG");
  display.drawLine(0, 10, 127, 10, WHITE);

  // 2. Banner Status Triage (12 - 23px)
  if (triageCode == 3) {
    display.fillRect(0, 12, 128, 12, WHITE);
    display.setTextColor(BLACK);
    display.setCursor(4, 14);
    if (spo2 > 0 && spo2 < 88) display.print("! ASFIKSIA GAS SOS !");
    else display.print("! ALARM SOS: JATUH !");
    display.setTextColor(WHITE);
  } else if (triageCode == 2) {
    display.fillRect(0, 12, 128, 12, WHITE);
    display.setTextColor(BLACK);
    display.setCursor(4, 14);
    display.print("WASPADA: LELAH/PANAS");
    display.setTextColor(WHITE);
  } else if (triageCode == 1) {
    display.drawRoundRect(0, 12, 128, 12, 2, WHITE);
    display.setTextColor(WHITE);
    display.setCursor(7, 14);
    display.print("TRIAGE: KERJA AKTIF");
  } else if (triageCode == 4) {
    display.drawRoundRect(0, 12, 128, 12, 2, WHITE);
    display.setTextColor(WHITE);
    display.setCursor(4, 14);
    display.print("STANDBY: JAM DILEPAS");
  } else if (triageCode == 0) {
    display.drawRoundRect(0, 12, 128, 12, 2, WHITE);
    display.setTextColor(WHITE);
    display.setCursor(7, 14);
    display.print("TRIAGE: NORMAL/AMAN");
  } else {
    display.drawRoundRect(0, 12, 128, 12, 2, WHITE);
    display.setTextColor(WHITE);
    display.setCursor(10, 14);
    display.print("MENUNGGU SINYAL...");
  }

  // 3. Grid Baris 1: Nadi & SpO2 (27px) - Jarak Aman Kolom Kiri & Kanan Tanpa Tabrakan
  display.setTextColor(WHITE);
  display.setCursor(2, 27);
  display.print("Nadi:");
  if (hr > 0) { display.print(hr); display.print("bpm"); }
  else if (triageCode == 4) { display.print("LEPAS"); }
  else { display.print("Ukur.."); }

  display.setCursor(70, 27);
  display.print("SpO2:");
  if (spo2 > 0) { display.print(spo2); display.print("%"); }
  else { display.print("--%"); }

  // 4. Grid Baris 2: Suhu Medis & Akselerasi Puncak (39px)
  display.setCursor(2, 39);
  display.print("Suhu:");
  if (temp > 0.0f) { display.print(temp, 1); display.print("C"); }
  else { display.print("--C"); }

  display.setCursor(70, 39);
  display.print("A_Pk:");
  display.print(a_max, 1); display.print("g");

  // 5. Dock Status Bawah (50 - 63px) - Rute Transmisi & RSSI dB Pas Tanpa Huruf B Turun
  display.drawLine(0, 50, 127, 50, WHITE);
  display.setCursor(2, 53);
  if (is_relayed) {
    display.print("1-Hop TAG1");
  } else if (is_node01) {
    display.print("Node01 Rly");
  } else {
    display.print("Direct P2P");
  }

  display.setCursor(68, 53);
  display.print("RSS:");
  display.print(rssi);
  display.print("dB"); // x=68 + 4*6 + 3*6 + 2*6 = 122px <= 128px (Sangat Rapi & Pas!)

  display.display();
}

void setup() {
  Serial.begin(115200);

  // Inisialisasi OLED SSD1306 (128x64 Resolusi Penuh & I2C Cepat 400kHz)
  Wire.begin(OLED_SDA, OLED_SCL);
  Wire.setClock(400000);
  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  display.clearDisplay();
  display.setTextColor(WHITE);
  display.setTextSize(1);
  display.setCursor(4, 4);
  display.println("RESCUE-TAG GATEWAY");
  display.drawLine(0, 14, 127, 14, WHITE);
  display.setCursor(4, 22);
  display.println("Posko Base Station");
  display.setCursor(4, 38);
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
    bool is_node01 = false;
    String cleanFeat = incoming;

    // A1. Cek Apakah Paket Datang Melalui 1-Hop Relay: RELAY,TAG01,FEAT,...
    if (incoming.startsWith("RELAY,")) {
      is_relayed = true;
      int featPos = incoming.indexOf("FEAT,");
      if (featPos != -1) {
        cleanFeat = incoming.substring(featPos);
      }
    } 
    // A2. Cek Apakah Paket Telemetri Mandiri Node #01 (Relawan/Relay): NODE01,FEAT,...
    else if (incoming.startsWith("NODE01,")) {
      is_node01 = true;
      int featPos = incoming.indexOf("FEAT,");
      if (featPos != -1) {
        cleanFeat = incoming.substring(featPos);
      }
    }
    // A3. Paket Diterima LANGSUNG dari Jam Tangan #02 (Direct LoRa)
    else {
      last_direct_rx = millis();
    }

    // A4. Parse Paket FEAT 50 Hz (Langsung maupun via Relay)
    // Format: FEAT,a_total,g_total,a_max,a_min,g_mean,a_std,g_max,ax,ay,az,model_pred,triage_pred,hr,spo2,temp
    if (cleanFeat.startsWith("FEAT,")) {
      // 1. Cetak ke Serial USB Laptop untuk ditangkap Node-RED & Python
      if (is_relayed) {
        Serial.print("RELAY,TAG01,");
      } else if (is_node01) {
        Serial.print("NODE01,");
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

    // Prioritas Rute Cerdas (Opportunistic Routing):
    // Jika Jam #02 masih terdengar langsung (< 2000 ms), rute tetap DIRECT P2P!
    // Hanya jika paket langsung HILANG (> 2000 ms, misal di blindspot), rute beralih ke 1-HOP RELAY!
    bool effective_relayed = is_relayed;
    if (is_relayed && (millis() - last_direct_rx < 2000)) {
      effective_relayed = false;
    }

    // 3. Simpan telemetri terakhir & Render OLED Gateway (128x64 Resolusi Penuh)
    last_triage = triageCode;
    last_hr = hr;
    last_spo2 = spo2;
    last_temp = temp;
    last_amax = a_max;
    last_rssi = rssi;
    last_relayed = effective_relayed;
    last_node01 = is_node01;
    last_rx_time = millis();

    renderGatewayOLED(last_triage, last_hr, last_spo2, last_temp, last_amax, last_rssi, last_relayed, last_node01);
  }

  // Refresh tampilan tiap 1 detik jika transmisi sedang jeda
  static unsigned long lastGatewayRefresh = 0;
  if (millis() - lastGatewayRefresh >= 1000) {
    lastGatewayRefresh = millis();
    renderGatewayOLED(last_triage, last_hr, last_spo2, last_temp, last_amax, last_rssi, last_relayed, last_node01);
  }
}
