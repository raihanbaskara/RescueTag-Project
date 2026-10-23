/*
 =========================================================================================
 RESCUE-TAG: NODE 01 - 1-HOP LORA RELAY WATCH (REKAN KERJA / HOST REPEATER)
 Platform    : ESP32 DevKit V1 + SX1278 LoRa (433 MHz) + OLED SSD1306 (128x64)
 Peran       : Jam Tangan #01 (Bambang - Rekan Kerja). 
               Menampilkan kondisi standby normal pekerja sehat saat tidak ada bahaya.
               Saat Jam #02 (Agus Salim) mengirim paket darurat di blindspot,
               Jam #01 ini menangkapnya, mengaktifkan peringatan rekan di layarnya,
               lalu me-relay paket tersebut ke Gateway Posko SAR!
 =========================================================================================
*/

#include <SPI.h>
#include <LoRa.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// ==========================================
// PIN DEFINITION - ESP32 DEVKIT V1
// ==========================================
#define LORA_SS    5    // D5 (NSS)
#define LORA_RST   14   // D14 (Reset)
#define LORA_DIO0  26   // D26 (DIO0)

#define OLED_SDA   21   // D21 (I2C SDA)
#define OLED_SCL   22   // D22 (I2C SCL)

Adafruit_SSD1306 display(128, 64, &Wire, -1);

// Baseline Virtual Pekerja #01 (Jam Standby Rekan Sehat)
int my_hr = 76;
int my_spo2 = 98;
float my_temp = 36.5f;

// Buffer & Status Relaying
unsigned long last_relay_rx = 0;
bool relay_alert_active = false;
int relay_counter = 0;

// Data Rekan (Jam #02) yang Sedang Ditolong
int friend_triage = 0;
int friend_hr = 0;
int friend_spo2 = 0;
float friend_temp = 36.6f;
float friend_amax = 1.0f;
int friend_rssi = -90;
String friend_last_raw = "";

// Anti-Looping Cache (Menyimpan 4 paket terakhir)
String recent_hashes[4] = {"", "", "", ""};
int hash_idx = 0;

bool is_packet_duplicate(String &pkt) {
  for (int i = 0; i < 4; i++) {
    if (recent_hashes[i] == pkt) return true;
  }
  recent_hashes[hash_idx] = pkt;
  hash_idx = (hash_idx + 1) % 4;
  return false;
}

void renderWatchDisplay() {
  display.clearDisplay();
  display.setTextSize(1);

  // KONDISI 1: POP-UP ALARM REKAN (Jam #02 Terdeteksi Bahaya & Sedang Di-relay)
  if (relay_alert_active && (millis() - last_relay_rx < 6000)) {
    // Header Bar Hitam-Putih (Inverse)
    display.fillRect(0, 0, 128, 12, WHITE);
    display.setTextColor(BLACK);
    display.setCursor(4, 2);
    display.println("! PERINGATAN REKAN !");
    display.setTextColor(WHITE);

    display.setCursor(0, 16);
    display.print("DARI   : JAM #02 (Agus)");

    display.setCursor(0, 27);
    display.print("TRIAGE : ");
    if (friend_triage == 3) {
      display.print("[MERAH/JATUH!]");
    } else if (friend_triage == 2) {
      display.print("[WASPADA DINI]");
    } else {
      display.print("[KUNING/KERJA]");
    }

    display.setCursor(0, 39);
    display.print("HR:"); display.print(friend_hr); display.print(" ");
    display.print("SpO2:"); display.print(friend_spo2); display.print("%");

    display.setCursor(0, 50);
    display.print("Suhu:"); display.print(friend_temp, 1); display.print("C ");
    display.print("RSSI:"); display.print(friend_rssi);

    display.drawLine(0, 62, 127, 62, WHITE);
  } 
  // KONDISI 2: STANDBY JAM TANGAN PEKERJA #01 (BAMBANG - NORMAL)
  else {
    relay_alert_active = false;

    // Header Jam Tangan #01
    display.setCursor(0, 2);
    display.println("RESCUE-TAG #01 [RELAY]");
    display.drawLine(0, 12, 127, 12, WHITE);

    display.setCursor(0, 16);
    display.println("TRIAGE: [NORMAL/SEHAT]");

    display.setCursor(0, 28);
    display.print("HR    : "); display.print(my_hr); display.println(" BPM");

    display.setCursor(0, 39);
    display.print("SpO2  : "); display.print(my_spo2); display.println(" %");

    display.setCursor(0, 50);
    display.print("Suhu  : "); display.print(my_temp, 1); display.print(" C | Hop:OK");

    display.drawLine(0, 62, 127, 62, WHITE);
  }

  display.display();
}

void setup() {
  Serial.begin(115200);

  // Inisialisasi Layar OLED (0x3C)
  Wire.begin(OLED_SDA, OLED_SCL);
  if (display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    display.clearDisplay();
    display.setTextColor(WHITE);
    display.setTextSize(1);
    display.setCursor(4, 8);
    display.println("RESCUE-TAG NODE #01");
    display.drawLine(0, 20, 127, 20, WHITE);
    display.setCursor(4, 28);
    display.println("1-Hop Relay Host");
    display.setCursor(4, 44);
    display.println("Starting LoRa 433MHz");
    display.display();
    delay(800);
  }

  // Inisialisasi LoRa SX1278
  LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);
  if (!LoRa.begin(433E6)) {
    Serial.println("[ERROR] LoRa Relay Init Failed!");
    display.clearDisplay();
    display.setCursor(0, 24);
    display.println("LORA INIT FAILED!");
    display.display();
    while (1);
  }

  // Konfigurasi Parameter LoRa (Sama Persis dengan Jam #02 & Gateway)
  LoRa.setSpreadingFactor(7);     // SF7 Fast Respon
  LoRa.setSignalBandwidth(125E3); // 125 kHz
  LoRa.setCodingRate4(5);        // 4/5
  LoRa.setSyncWord(0x12);        // Sync Word Terpadu
  LoRa.setTxPower(17);           // Daya pancar kuat untuk melempar ke posko

  Serial.println("=====================================================");
  Serial.println(" RESCUE-TAG #01: 1-HOP LORA RELAY WATCH AKTIF");
  Serial.println(" Frekuensi: 433 MHz | SF7 | Sync 0x12");
  Serial.println(" Siap me-relay paket blindspot dari Jam Tangan #02");
  Serial.println("=====================================================");

  renderWatchDisplay();
}

void loop() {
  // 1. Cek Apakah Ada Paket LoRa Masuk dari Jam Tangan #02
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    String incoming = "";
    while (LoRa.available()) {
      incoming += (char)LoRa.read();
    }
    int rssi = LoRa.packetRssi();

    // Pastikan paket adalah paket asli FEAT dari Jam (bukan paket yang sudah berawalan RELAY agar anti-loop)
    if (incoming.startsWith("FEAT,")) {
      if (!is_packet_duplicate(incoming)) {
        relay_counter++;
        last_relay_rx = millis();
        friend_rssi = rssi;
        friend_last_raw = incoming;

        // Parse nilai triage, hr, spo2, suhu dari paket Jam #02
        // Format: FEAT,a_total,g_total,a_max,a_min,g_mean,a_std,g_max,ax,ay,az,model_pred,triage_pred,hr,spo2,temp
        int commaIdx[16];
        int commaCount = 0;
        for (int i = 0; i < incoming.length() && commaCount < 16; i++) {
          if (incoming.charAt(i) == ',') {
            commaIdx[commaCount++] = i;
          }
        }

        if (commaCount >= 12) {
          friend_amax = incoming.substring(commaIdx[2] + 1, commaIdx[3]).toFloat();
          friend_triage = incoming.substring(commaIdx[11] + 1, commaIdx[12]).toInt();
        }
        if (commaCount >= 14) {
          friend_hr = incoming.substring(commaIdx[12] + 1, commaIdx[13]).toInt();
          friend_spo2 = incoming.substring(commaIdx[13] + 1, commaIdx[14]).toInt();
        }
        if (commaCount >= 15) {
          friend_temp = incoming.substring(commaIdx[14] + 1).toFloat();
        }

        // Aktifkan alert pop-up di layar Jam #01
        relay_alert_active = true;
        renderWatchDisplay();

        Serial.print("[RELAY #"); Serial.print(relay_counter);
        Serial.print("] Menerima dari Jam #02 (RSSI: "); Serial.print(rssi); Serial.println(" dBm)");
        Serial.print("  -> Triage: "); Serial.print(friend_triage);
        Serial.print(" | HR: "); Serial.print(friend_hr);
        Serial.print(" | SpO2: "); Serial.print(friend_spo2);
        Serial.print(" | Suhu: "); Serial.println(friend_temp, 1);

        // Beri sedikit jeda acak 25-50ms agar tidak tabrakan frekuensi
        delay(random(25, 50));

        // Format Terusan Berpenanda Hop: RELAY,TAG01,FEAT,...
        String forwardedPacket = "RELAY,TAG01," + incoming;

        // Pancarkan kembali ke arah Gateway Posko
        if (LoRa.beginPacket()) {
          LoRa.print(forwardedPacket);
          LoRa.endPacket(true); // Non-blocking transmit
          Serial.println("  -> [SUKSES TERUSKAN KE GATEWAY POSKO]\n");
        }
      }
    }
  }

  // 2. Render Ulang Layar Berkala (Tiap 1 Detik)
  static unsigned long lastOledRefresh = 0;
  if (millis() - lastOledRefresh >= 1000) {
    lastOledRefresh = millis();
    renderWatchDisplay();
  }
}
