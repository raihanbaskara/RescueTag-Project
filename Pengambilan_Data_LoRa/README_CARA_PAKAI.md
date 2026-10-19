# Panduan Pengambilan Data Sensor BMI160 Wireless via LoRa

Paket ini dirancang untuk mengambil data gerakan sensor BMI160 secara **bebas kabel (wireless)** menggunakan jaringan transmisi **LoRa 433 MHz** antara **STM32 Black Pill (Jam Tangan)** dan **ESP32 (Gateway USB Laptop)**.

---

## 📁 Struktur Folder
```text
Pengambilan_Data_LoRa/
├── stm32_transmitter/
│   └── stm32_transmitter.ino      <-- Upload ke STM32 Black Pill
├── esp32_gateway_receiver/
│   └── esp32_gateway_receiver.ino  <-- Upload ke ESP32 Gateway
├── record_dataset.py               <-- Jalankan di laptop untuk rekam CSV
└── README_CARA_PAKAI.md            <-- Panduan langkah demi langkah
```

---

## 🛠️ Persiapan Arduino IDE & Library

1. **Board yang Diinstall di Arduino IDE:**
   * **STM32:** `STM32 MCU based boards` by STMicroelectronics (Pilih: *Generic STM32F4 series* -> *BlackPill F401CC*).
   * **ESP32:** `esp32` by Espressif Systems (Pilih: *ESP32 Dev Module*).

2. **Library yang Wajib Diinstall (via Arduino Library Manager):**
   * `LoRa` by Sandeep Mistry (Wajib untuk STM32 dan ESP32).
   * `BMI160-Arduino` by EmotiBit / DFRobot (Untuk STM32).
   * `Adafruit SSD1306` & `Adafruit GFX` (Untuk OLED di ESP32 Gateway).

---

## 📌 Pemetaan Pin yang Digunakan

### A. STM32 Black Pill (Transmitter)
* **LoRa SX1278 (SPI1):**
  * `SCK`  = `PA5`
  * `MISO` = `PA6`
  * `MOSI` = `PA7`
  * `NSS`  = `PA4`
  * `RST`  = `PA3`
  * `DIO0` = `PA2`
* **Sensor BMI160 (I2C1):**
  * `SCL`  = `PB6`
  * `SDA`  = `PB7`

### B. ESP32 Gateway (Receiver - Sesuai PCB)
* **LoRa SX1278 (VSPI):**
  * `NSS`  = `GPIO 5` (`D05`)
  * `RST`  = `GPIO 14` (`D14`)
  * `DIO0` = `GPIO 26` (`D26`)
  * `SCK`  = `GPIO 18`, `MISO` = `GPIO 19`, `MOSI` = `GPIO 23`
* **OLED 0.96" (I2C):**
  * `SCL`  = `GPIO 22` (`D22`)
  * `SDA`  = `GPIO 21` (`D21`)

---

## 🚀 Langkah Menjalankan

1. **Upload ke STM32:**
   * Buka `stm32_transmitter/stm32_transmitter.ino` di Arduino IDE dan upload ke STM32.
2. **Upload ke ESP32:**
   * Buka `esp32_gateway_receiver/esp32_gateway_receiver.ino` di Arduino IDE dan upload ke ESP32.
3. **Colokkan ESP32 ke Laptop lewat USB.**
4. **Jalankan Perekam Data di Terminal / CMD Laptop:**
   ```bash
   cd "Pengambilan_Data_LoRa"
   python record_dataset.py
   ```
5. **Nyalakan Jam STM32 (Baterai LiPo / Power Bank kecil) dan Lakukan Gerakan:**
   * **Menit 1:** Duduk & berjalan santai (*Normal*).
   * **Menit 2:** Mengayunkan tangan seperti mencangkul (*Kerja Aktif*).
   * **Menit 3:** Jatuhkan jam ke bantal/kasur, lalu **diamkan 20–30 detik** (*Jatuh/Pingsan*). Ulangi 5–10 kali.
6. **Selesai:** Tekan `Ctrl + C` di terminal laptop. File `dataset_bmi160_raw.csv` langsung siap dilatih menjadi model Decision Tree!
