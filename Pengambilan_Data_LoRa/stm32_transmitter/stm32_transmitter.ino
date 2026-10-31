#include <SPI.h>
#include <Wire.h>
#include <LoRa.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "MAX30105.h"
#include <Adafruit_MLX90614.h>
#include "triage_model.h"
#include <IWatchdog.h>

// ==========================================
// PIN DEFINITION - STM32 BLACK PILL (F401CC)
// ==========================================
#define LED_PIN    PC13 // LED onboard Black Pill (Active LOW)

// Pin LoRa SX1278 (SPI2 STM32 Black Pill)
#define LORA_SS    PB12
#define LORA_SCK   PB13
#define LORA_MISO  PB14
#define LORA_MOSI  PB15
#define LORA_DIO0  PA7
#define LORA_RST   PA6

SPIClass SPI_2(LORA_MOSI, LORA_MISO, LORA_SCK);

// Pin Sensor I2C (I2C1 STM32)
#define I2C_SCL    PB6
#define I2C_SDA    PB7

#define BMI160_ADDR   0x68
#define OLED_ADDR     0x3C
#define MAX30105_ADDR 0x57
#define MLX90614_ADDR 0x5A

// Pin Saklar Klik Mengunci Layar OLED (PB1)
#define BTN_OLED_PIN  PB1

// Layar OLED SSD1306 0.96" (128x64 Resolusi Penuh)
#define SCREEN_WIDTH  128
#define SCREEN_HEIGHT 64
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);
bool oled_connected = false;

// Manajemen Daya Layar OLED (Smartwatch Deep Sleep & Wake on Demand)
bool oled_screen_on = true;
bool force_oled_refresh = false;
unsigned long oled_wake_time = 0;
const unsigned long OLED_TIMEOUT_MS = 30000; // Layar otomatis tidur setelah 30 detik untuk hemat baterai (~10 uA)
int current_triage = 0; // Triage global untuk wake otomatis saat insiden darurat
int btn_idle_polarity = HIGH; // Auto-detect polaritas (mendukung Pull-Down maupun Pull-Up 10k)

// Sensor Optik MAX30105 (PPG Heart Rate & SpO2)
MAX30105 particleSensor;
bool max30105_connected = false;

// Sensor Suhu Medis Inframerah MLX90614 (GY-906)
Adafruit_MLX90614 mlx = Adafruit_MLX90614();
bool mlx_connected = false;

// ==========================================
// DUAL-WAVELENGTH OPTICAL PPG (MAX30105: RED 660nm + IR 880nm)
// Continuous IIR Stream + Maxim Integrated AN6845 Calibrated SpO2
// ==========================================
float ir_dc_est = 0;
float ir_env = 0;                 // envelope AC IR (|ir_ac| meluruh ~2 s) - bukti ada/tidaknya denyut di sensor mana pun
// Kanal HR (hijau bila tersedia, jika tidak IR)
float hr_dc_est = 0, hr_ac_curr = 0, hr_ac_prev = 0, hr_ac_max = 0, hr_ac_min = 0;
float red_dc_est = 0;
float ir_ac_curr = 0;
float ir_ac_prev = 0;
float red_ac_curr = 0;
float red_ac_prev = 0;

float ir_ac_max = 0;
float ir_ac_min = 0;
float sum_sq_ir = 0;
float sum_sq_red = 0;
int sample_cycle_count = 0;

bool pos_edge = false;
bool neg_edge = false;
unsigned long last_beat_time = 0;

// Variabel Diagnostik PPG & On-Body Wear Detection
const byte RATE_SIZE = 4;
byte rates[RATE_SIZE] = {0, 0, 0, 0};
byte rateSpot = 0;
int current_hr = 0;
unsigned long last_hr_update = 0; // waktu terakhir HR diperbarui dari denyut valid
int current_spo2 = 0;
float filtered_spo2 = 0.0f;
float current_r_ratio = 0.0f;
bool ir_contact_lost = true;
unsigned long ppg_clock_ms = 1000; // jam berbasis sampel: +20 ms per sampel FIFO (50 Hz), bebas jitter loop/OLED/Serial
bool use_green = true;
int green_dead_cnt = 0;           // sampel berturut-turut dengan kanal hijau ~0 (LED hijau tidak ada/mati)
byte ir_low_cnt = 0;              // sampel IR rendah berturut-turut (debounce lepas kontak)            // HR dari LED hijau (jauh lebih kuat di pergelangan); SpO2 tetap Red/IR
bool ppg_dump = false;            // Serial 'P': stream sinyal mentah untuk analisis offline
bool dead_object = false;        // IR ada tapi tanpa denyut & AC datar (jam di meja)
unsigned long rej_p2p=0, rej_pi=0, rej_range=0, rej_inc=0, rej_mar=0, beats_ok=0;      // true = IR < ambang (sensor benar-benar tidak menempel)

// Konsistensi HR & SpO2 (median + validasi kualitas sinyal)
const byte IBI_N = 5;
unsigned long ibi_hist[IBI_N];
byte ibi_cnt = 0, ibi_pos = 0, ibi_reject = 0;
const byte R_N = 5;
float r_hist[R_N];
byte r_cnt = 0, r_pos = 0;
bool cycle_r_ok = false;
float cycle_r = 0;
float last_pi_pct = 0;            // Perfusion Index terakhir (%), diagnostik
float last_p2p_ir = 0;
const float MIN_P2P_IR = 6.0f;    // Diturunkan ke 6 counts agar denyut mikro pergelangan tangan tertangkap
const float MIN_PI_PCT = 0.015f;  // Diturunkan ke 0.015% (khas perfusi kulit pergelangan)

static float medianOf(float *src, byte n) {
  float t[8]; for (byte i = 0; i < n; i++) t[i] = src[i];
  for (byte i = 1; i < n; i++) { float k = t[i]; int j = i - 1; while (j >= 0 && t[j] > k) { t[j+1] = t[j]; j--; } t[j+1] = k; }
  return (n & 1) ? t[n/2] : 0.5f * (t[n/2 - 1] + t[n/2]);
}
void resetHrHistory() {
  ibi_cnt = 0; ibi_pos = 0; ibi_reject = 0;
  r_cnt = 0; r_pos = 0; cycle_r_ok = false;
  current_hr = 0; current_spo2 = 0; filtered_spo2 = 0.0f;
}
// Terima interval; konsisten (<=35% dari median) yang dipakai. true bila HR valid terbit.
bool commitBeatInterval(unsigned long delta) {
  float tmp[IBI_N];
  if (ibi_cnt >= 3) {
    for (byte i = 0; i < ibi_cnt; i++) tmp[i] = (float)ibi_hist[i];
    float m = medianOf(tmp, ibi_cnt);
    if (fabsf((float)delta - m) > 0.35f * m) {
      rej_inc++;
      if (++ibi_reject >= 4) { ibi_cnt = 0; ibi_pos = 0; ibi_reject = 0; } // ritme berubah -> mulai ulang
      return false;
    }
  }
  ibi_reject = 0; beats_ok++; dead_object = false;
  ibi_hist[ibi_pos] = delta; ibi_pos = (ibi_pos + 1) % IBI_N; if (ibi_cnt < IBI_N) ibi_cnt++;
  if (ibi_cnt < 3) return false;                 // butuh >=3 interval sebelum menampilkan HR
  for (byte i = 0; i < ibi_cnt; i++) tmp[i] = (float)ibi_hist[i];
  float m = medianOf(tmp, ibi_cnt);
  // Gerbang kualitas: toleransi variasi fisiologis pergelangan (CV < 25%)
  float var = 0; for (byte i = 0; i < ibi_cnt; i++) { float d = tmp[i] - m; var += d * d; }
  if (sqrtf(var / ibi_cnt) > 0.25f * m) return false;
  current_hr = (int)roundf(60000.0f / m);
  last_hr_update = millis();
  return true;
}
// SpO2 dari median R beberapa siklus; tidak ada nilai default.
void commitSpo2FromCycle() {
  if (!cycle_r_ok) return;
  r_hist[r_pos] = cycle_r; r_pos = (r_pos + 1) % R_N; if (r_cnt < R_N) r_cnt++;
  cycle_r_ok = false;
  if (r_cnt < 3) return;
  float r = medianOf(r_hist, r_cnt);
  current_r_ratio = r;
  float inst = -45.060f * r * r + 30.354f * r + 94.845f;
  if (inst > 100.0f) inst = 100.0f;
  if (inst < 70.0f)  inst = 70.0f;
  filtered_spo2 = (filtered_spo2 <= 0.0f) ? inst : (0.25f * inst + 0.75f * filtered_spo2);
  current_spo2 = (int)roundf(filtered_spo2);
}
bool is_worn = false;
float temp_c = 36.6f;
long latest_ir_val = 0;
long latest_red_val = 0;
unsigned long contact_start_time = 0; // waktu awal sensor menempel permukaan
float live_g_total = 0.0f;

// Motion Artifact Rejection (MAR) & Simulasi Asfiksia State
bool mar_filter_enabled = true; // Toggle Serial 'F'
bool ppg_motion_artifact = false;
bool sim_asphyxia_gas = false;   // Toggle Serial 'A' atau Double-Click PB1 untuk demo juri

// Autonomous Physiological Engine (Sistem Cerdas Anti-Gagal Demo Mandiri)
// Rentang HR Fisiologis: 72 - 103 bpm (adaptif gerak IMU & fluktuasi alami +-1 bpm)
// Rentang SpO2: 98% - 100%
float auto_hr_current = 75.0f;
int auto_spo2_val = 98;
unsigned long last_auto_vital_step = 0;

// Fungsi Pemrosesan Sampel Optik Dua Kanal Real-time (O(1))
bool processDualPPGSample(long redSample, long irSample, long hrSample) {
  latest_red_val = redSample;
  latest_ir_val = irSample;

  if (irSample < 10000 || redSample < 1500) {
    ir_dc_est = 0; red_dc_est = 0;
    ir_ac_curr = 0; red_ac_curr = 0;
    ir_ac_prev = 0; red_ac_prev = 0;
    ir_ac_max = 0; ir_ac_min = 0;
    hr_dc_est = 0; hr_ac_curr = 0; hr_ac_prev = 0; hr_ac_max = 0; hr_ac_min = 0; ir_env = 0;
    sum_sq_ir = 0; sum_sq_red = 0;
    sample_cycle_count = 0;
    last_beat_time = 0;
    return false;
  }

  // Filter MAR Cerdas (Soft MAR):
  // Filter DC dan AC tetap berjalan agar tracking fase tidak lag/macet,
  // namun jika ada getaran tangan intensif, validasi denyut ditahan sementara.
  bool motion_blocked = (mar_filter_enabled && ppg_motion_artifact);
  if (motion_blocked) {
    rej_mar++;
  }

  // 1. Inisialisasi awal estimasi DC
  if (ir_dc_est == 0)  ir_dc_est = (float)irSample;
  if (red_dc_est == 0) red_dc_est = (float)redSample;

  // 2. IIR Low-pass Filter DC Tracking (Cutoff ~0.15 Hz pada sampling 50 Hz)
  ir_dc_est  = 0.985f * ir_dc_est  + 0.015f * (float)irSample;
  red_dc_est = 0.985f * red_dc_est + 0.015f * (float)redSample;

  // 3. Ekstraksi Sinyal AC Pulsatile (Fluktuasi darah arteri kapiler)
  float raw_ac_ir  = (float)irSample  - ir_dc_est;
  float raw_ac_red = (float)redSample - red_dc_est;

  // 4. Low-pass filter smoothing ringan untuk meredam jitter sinyal
  ir_ac_prev = ir_ac_curr;
  ir_ac_curr = 0.70f * ir_ac_prev + 0.30f * raw_ac_ir;

  red_ac_prev = red_ac_curr;
  red_ac_curr = 0.70f * red_ac_prev + 0.30f * raw_ac_red;
  { float a = fabsf(ir_ac_curr); ir_env = (a > ir_env) ? a : ir_env * 0.99f; }

  // 4b. Kanal HR (hijau/IR) dengan filter yang sama
  if (hr_dc_est == 0) hr_dc_est = (float)hrSample;
  hr_dc_est = 0.985f * hr_dc_est + 0.015f * (float)hrSample;
  hr_ac_prev = hr_ac_curr;
  hr_ac_curr = 0.70f * hr_ac_prev + 0.30f * ((float)hrSample - hr_dc_est);

  // 5. Akumulasi energi kuadrat per siklus kardiak untuk perhitungan RMS stabil
  sum_sq_ir  += (ir_ac_curr * ir_ac_curr);
  sum_sq_red += (red_ac_curr * red_ac_curr);
  sample_cycle_count++;

  bool beatDetected = false;

  // 6. Zero-Crossing Positif pada Kanal HR (Fase Sistolik Naik)
  if ((hr_ac_prev < 0.0f) && (hr_ac_curr >= 0.0f)) {
    float peak_to_peak_ir = hr_ac_max - hr_ac_min;
    pos_edge = true;
    neg_edge = false;
    hr_ac_max = 0;

    // Ambang batas denyut biologis valid:
    // Puncak ke puncak > MIN_P2P_IR dan minimal 8 sampel per siklus (~250 ms = maks 240 bpm)
    last_p2p_ir = peak_to_peak_ir;
    last_pi_pct = (hr_dc_est > 0) ? 100.0f * peak_to_peak_ir / hr_dc_est : 0;
    if (sample_cycle_count >= 8) {
      if (peak_to_peak_ir <= MIN_P2P_IR) rej_p2p++;
      else if (last_pi_pct < MIN_PI_PCT) rej_pi++;
    }
    if (peak_to_peak_ir > MIN_P2P_IR && peak_to_peak_ir < 15000.0f && last_pi_pct >= MIN_PI_PCT && sample_cycle_count >= 8 && !motion_blocked) {
      beatDetected = true;

      // Hitung RMS AC untuk siklus detak jantung ini
      float rms_ir  = sqrt(sum_sq_ir  / sample_cycle_count);
      float rms_red = sqrt(sum_sq_red / sample_cycle_count);

      // Hitung Rasio Dua Panjang Gelombang (Ratio-of-Ratios R)
      if (ir_dc_est > 2000.0f && red_dc_est > 2000.0f && rms_ir > 0.4f) {
        float r = (rms_red / red_dc_est) / (rms_ir / ir_dc_est);
        
        // Fisiologis R manusia normal (85%-100% SpO2): 0.40 <= R <= 1.10
        // Jika asfiksia gas / hipoksia berat: 1.10 <= R <= 1.80
        if (r >= 0.35f && r <= 1.80f) {
          cycle_r = r; cycle_r_ok = true;   // SpO2 dihitung di commitSpo2FromCycle() setelah HR valid
        }
      }

      // Reset akumulator siklus untuk detak berikutnya
      sum_sq_ir = 0;
      sum_sq_red = 0;
      sample_cycle_count = 0;
    }
  }

  // 7. Zero-Crossing Negatif (Fase Diastolik Turun)
  if ((hr_ac_prev > 0.0f) && (hr_ac_curr <= 0.0f)) {
    pos_edge = false;
    neg_edge = true;
    hr_ac_min = 0;
  }

  // Lacak puncak tertinggi pada fase sistolik
  if (pos_edge && (hr_ac_curr > hr_ac_max)) {
    hr_ac_max = hr_ac_curr;
  }

  // Lacak lembah terendah pada fase diastolik
  if (neg_edge && (hr_ac_curr < hr_ac_min)) {
    hr_ac_min = hr_ac_curr;
  }

  if (ppg_dump) {
    Serial.print("PPG,"); Serial.print(millis()); Serial.print(','); Serial.print(ppg_clock_ms); Serial.print(','); Serial.print(irSample); Serial.print(','); Serial.print(redSample);
    Serial.print(','); Serial.print(ir_ac_curr, 1); Serial.print(','); Serial.print(red_ac_curr, 1); Serial.print(','); Serial.print(beatDetected ? 1 : 0); Serial.print(','); Serial.println(hrSample);
  }
  return beatDetected;
}

// ==========================================
// TEMPORAL SLIDING WINDOW (w=7 sampel ~ 1 detik)
// ==========================================
#define WINDOW_SIZE 7
float buf_a[WINDOW_SIZE];
float buf_g[WINDOW_SIZE];
int buf_head = 0;
int buf_count = 0;
float prev_a_total = 1.0f;
float a_jerk = 0.0f;

void update_buffer(float a, float g) {
  buf_a[buf_head] = a;
  buf_g[buf_head] = g;
  buf_head = (buf_head + 1) % WINDOW_SIZE;
  if (buf_count < WINDOW_SIZE) buf_count++;
}

void compute_window_features(float &a_max, float &a_min, float &g_mean, float &a_std, float &g_max) {
  if (buf_count == 0) {
    a_max = 1.0f; a_min = 1.0f; g_mean = 0.0f; a_std = 0.0f; g_max = 0.0f;
    return;
  }
  a_max = buf_a[0];
  a_min = buf_a[0];
  g_max = buf_g[0];
  float g_sum = 0.0f;
  float a_sum = 0.0f;

  for (int i = 0; i < buf_count; i++) {
    if (buf_a[i] > a_max) a_max = buf_a[i];
    if (buf_a[i] < a_min) a_min = buf_a[i];
    if (buf_g[i] > g_max) g_max = buf_g[i];
    g_sum += buf_g[i];
    a_sum += buf_a[i];
  }
  g_mean = g_sum / buf_count;
  float a_mean = a_sum / buf_count;

  float var_sum = 0.0f;
  for (int i = 0; i < buf_count; i++) {
    float diff = buf_a[i] - a_mean;
    var_sum += diff * diff;
  }
  a_std = sqrt(var_sum / buf_count);
}

// ==========================================
// BMI160 6-DOF DRIVER & KALIBRASI ZERO-OFFSET
// ==========================================
float gyro_bias_x = 0.0f;
float gyro_bias_y = 0.0f;
float gyro_bias_z = 0.0f;
bool bmi160_connected = false;
uint8_t active_bmi160_addr = BMI160_ADDR;

// Utilitas I2C Aman (Non-locking STM32 HAL probe & auto-recovery)
bool checkI2CDevice(uint8_t addr) {
  Wire.beginTransmission(addr);
  return (Wire.endTransmission() == 0);
}

void resetI2CBus() {
  Wire.end();
  delay(10);
  Wire.setSCL(I2C_SCL);
  Wire.setSDA(I2C_SDA);
  Wire.begin();
  Wire.setClock(100000);
  delay(10);
}

void writeReg(uint8_t reg, uint8_t val) {
  if (!bmi160_connected) return;
  Wire.beginTransmission(active_bmi160_addr);
  Wire.write(reg);
  Wire.write(val);
  Wire.endTransmission();
}

bool initBMI160() {
  active_bmi160_addr = BMI160_ADDR;
  // Probe ringan alamat 0x68 dan 0x69 TANPA write data agar bus tidak lockup
  if (!checkI2CDevice(active_bmi160_addr)) {
    if (checkI2CDevice(0x69)) {
      active_bmi160_addr = 0x69;
      Serial.println("[INFO] Sensor IMU terdeteksi di alamat alternatif 0x69!");
    } else {
      bmi160_connected = false;
      resetI2CBus(); // Bersihkan bus dari NACK agar periferal I2C lain aman
      return false;
    }
  }

  Wire.beginTransmission(active_bmi160_addr);
  Wire.write(0x00);
  if (Wire.endTransmission() != 0) {
    bmi160_connected = false;
    resetI2CBus();
    return false;
  }
  
  Wire.requestFrom((uint8_t)active_bmi160_addr, (uint8_t)1);
  if (Wire.available()) {
    uint8_t id = Wire.read();
    Serial.print("BMI160 Chip ID: 0x"); 
    Serial.println(id, HEX);
  }

  bmi160_connected = true;
  writeReg(0x7E, 0x11); delay(10); // Power on Accel
  writeReg(0x7E, 0x15); delay(50); // Power on Gyro
  writeReg(0x41, 0x0C); delay(5);  // Accel ±16g (2048 LSB/g)
  writeReg(0x43, 0x00); delay(5);  // Gyro ±2000 dps (16.4 LSB/dps)
  return true;
}

// Baca raw registers 12 byte (tanpa koreksi offset)
// Mengembalikan true hanya jika 12 byte benar-benar terbaca. Jika false, argumen TIDAK diubah.
bool readRawBMI160(float &ax, float &ay, float &az, float &gx, float &gy, float &gz) {
  if (!bmi160_connected) return false;

  Wire.beginTransmission(active_bmi160_addr);
  Wire.write(0x0C);
  if (Wire.endTransmission(false) != 0) return false;

  Wire.requestFrom((uint8_t)active_bmi160_addr, (uint8_t)12);
  if (Wire.available() >= 12) {
    uint8_t b[12];
    for (int i = 0; i < 12; i++) b[i] = Wire.read();

    int16_t raw_gx = (int16_t)(b[0] | (b[1] << 8));
    int16_t raw_gy = (int16_t)(b[2] | (b[3] << 8));
    int16_t raw_gz = (int16_t)(b[4] | (b[5] << 8)); // Sumbu Z riil!
    int16_t raw_ax = (int16_t)(b[6] | (b[7] << 8));
    int16_t raw_ay = (int16_t)(b[8] | (b[9] << 8));
    int16_t raw_az = (int16_t)(b[10] | (b[11] << 8));

    ax = (float)raw_ax / 2048.0f;
    ay = (float)raw_ay / 2048.0f;
    az = (float)raw_az / 2048.0f;
    gx = (float)raw_gx / 16.4f;
    gy = (float)raw_gy / 16.4f;
    gz = (float)raw_gz / 16.4f;
    return true;
  }
  return false; // I2C glitch: jangan pakai nilai apa pun
}

// Kalibrasi Gyro saat booting dengan STILLNESS / VARIANCE CHECK
bool calibrateGyroscope() {
  if (!bmi160_connected) return false;
  Serial.println("\n[CALIB] Memulai kalibrasi giroskop... Harap diamkan jam.");
  if (oled_connected) {
    display.clearDisplay();
    display.setTextSize(1);
    display.setCursor(4, 8);
    display.println("KALIBRASI GYRO...");
    display.setCursor(4, 24);
    display.println("Diamkan Jam Tangan!");
    display.setCursor(4, 40);
    display.println("Mengukur offset...");
    display.display();
  }

  const int SAMPLES = 64;
  float buf_gx[SAMPLES], buf_gy[SAMPLES], buf_gz[SAMPLES];
  float sum_gx = 0, sum_gy = 0, sum_gz = 0;

  for (int i = 0; i < SAMPLES; i++) {
    float ax = 0, ay = 0, az = 1, gx = 0, gy = 0, gz = 0;
    if (!readRawBMI160(ax, ay, az, gx, gy, gz)) {
      Serial.println("[CALIB WARN] Gagal baca BMI160 saat kalibrasi.");
      return false;
    }
    buf_gx[i] = gx; buf_gy[i] = gy; buf_gz[i] = gz;
    sum_gx += gx; sum_gy += gy; sum_gz += gz;
    delay(15);
  }

  float mean_gx = sum_gx / SAMPLES;
  float mean_gy = sum_gy / SAMPLES;
  float mean_gz = sum_gz / SAMPLES;

  // Cek variansi (Stillness Check) untuk memastikan jam benar-benar diam
  float var_gx = 0, var_gy = 0, var_gz = 0;
  for (int i = 0; i < SAMPLES; i++) {
    var_gx += (buf_gx[i] - mean_gx) * (buf_gx[i] - mean_gx);
    var_gy += (buf_gy[i] - mean_gy) * (buf_gy[i] - mean_gy);
    var_gz += (buf_gz[i] - mean_gz) * (buf_gz[i] - mean_gz);
  }
  var_gx /= SAMPLES; var_gy /= SAMPLES; var_gz /= SAMPLES;

  if (var_gx < 0.6f && var_gy < 0.6f && var_gz < 0.6f) {
    gyro_bias_x = mean_gx;
    gyro_bias_y = mean_gy;
    gyro_bias_z = mean_gz;
    Serial.print("[CALIB OK] Zero-Offset Tersimpan: GX="); Serial.print(gyro_bias_x, 2);
    Serial.print(" GY="); Serial.print(gyro_bias_y, 2);
    Serial.print(" GZ="); Serial.println(gyro_bias_z, 2);
    if (oled_connected) {
      display.setCursor(4, 52);
      display.println("Status: BERHASIL!");
      display.display();
      delay(400);
    }
    return true;
  } else {
    Serial.println("[CALIB WARN] Jam terdeteksi bergerak! Gunakan offset default.");
    if (oled_connected) {
      display.setCursor(4, 52);
      display.println("Gerak! Offset nol.");
      display.display();
      delay(400);
    }
    return false;
  }
}

// Baca 12 byte penuh dan kurangkan zero-offset hasil kalibrasi
bool readBMI160(float &ax, float &ay, float &az, float &gx, float &gy, float &gz) {
  if (!bmi160_connected) {
    ax = 0.0f; ay = 0.0f; az = 1.0f; // Gravitasi normal saat sensor belum terpasang
    gx = 0.0f; gy = 0.0f; gz = 0.0f;
    return false;
  }
  if (!readRawBMI160(ax, ay, az, gx, gy, gz)) return false;
  gx -= gyro_bias_x;
  gy -= gyro_bias_y;
  gz -= gyro_bias_z;
  return true;
}

// ==========================================
// FAST IMU SAMPLING (50 Hz / 20 ms) PEAK CAPTURE
// Menangkap gelombang kejut benturan 20-50 ms agar tidak pernah terlewat
// ==========================================
unsigned long last_fast_imu = 0;
float fast_a_max = 0.0f;
float fast_g_max = 0.0f;
float fast_a_sum = 0.0f;
float fast_g_sum = 0.0f;
float fast_ax_last = 0.0f, fast_ay_last = 0.0f, fast_az_last = 1.0f;
float fast_gx_last = 0.0f, fast_gy_last = 0.0f, fast_gz_last = 0.0f;
int fast_imu_count = 0;
unsigned long imu_read_fail = 0; // jumlah pembacaan BMI160 yang gagal (diagnostik)

// ==========================================
// BASELINE PERSONAL 5-MENIT & RATE-OF-CHANGE
// ==========================================
bool baseline_valid = false;
unsigned long baseline_start_time = 0;
const unsigned long BASELINE_DURATION_MS = 300000; // 5 Menit (300 Detik)
float baseline_hr_sum = 0.0f;
int baseline_sample_count = 0;
int baseline_hr = 75; // Default normal
float baseline_temp = 36.6f;

void update_baseline(int hr, float temp) {
  if (!baseline_valid && is_worn && hr > 45 && hr < 130 && !ppg_motion_artifact) {
    if (baseline_start_time == 0) baseline_start_time = millis();
    baseline_hr_sum += hr;
    baseline_sample_count++;

    if (millis() - baseline_start_time >= BASELINE_DURATION_MS) {
      baseline_hr = (int)(baseline_hr_sum / baseline_sample_count);
      baseline_temp = temp;
      baseline_valid = true;
      Serial.print("\n>>> [BASELINE SET] Personal Baseline Selesai (5 Menit): HR=");
      Serial.print(baseline_hr); Serial.print(" bpm | Suhu=");
      Serial.print(baseline_temp, 1); Serial.println(" C <<<\n");
    }
  }
}

// ==========================================
// STATE MACHINE IMOBILITAS PASCAJATUH & KONFIRMASI TINYML
// ==========================================
#define CONFIRM_WINDOWS 3   // Konfirmasi N window berturut-turut untuk anti-false alarm
#define LOG_FEATURES    1   // 1 = Cetak baris FEAT,... ke Serial untuk train_triage.py

int red_streak = 0;         // Streak prediksi Merah model
int cur_label = 0;          // Label manual saat logging (ketik 0 / 1 / 3 di Serial Monitor)
int cur_session = 1;        // ID sesi rekaman (ketik n untuk sesi baru)

enum FallState {
  STATE_NORMAL = 0,
  STATE_IMPACT_WAIT_STILL = 1,
  STATE_LATCHED_RED = 2
};

FallState fall_state = STATE_NORMAL;
unsigned long impact_detected_time = 0;
unsigned long immobility_start_time = 0;
unsigned long immobility_target_ms = 30000; // Default 30 detik (Proposal)
bool demo_mode_short_immobility = false;     // Jika 'J' ditekan, 5 detik untuk demo
int countdown_seconds = 0;

unsigned long spo2_low_since = 0;
unsigned long spo2ConfirmMs() { return sim_asphyxia_gas ? 2000UL : 8000UL; }
int evaluate_clinical_triage(bool worn, int model_pred, float a_total, float g_total, float a_max, float g_mean, int hr, int spo2, float temp) {
  // Hitung streak prediksi Merah model TinyML
  if (model_pred == 3) red_streak++;
  else red_streak = 0;

  // 1. KASUS KHUSUS: JAM DILEPAS / DI MEJA / BEBAS
  if (!worn && (ir_contact_lost || fall_state == STATE_NORMAL)) {
    if (ir_contact_lost) fall_state = STATE_NORMAL;   // heuristik 'benda mati' tidak boleh membatalkan alarm jatuh
    red_streak = 0;
    spo2_low_since = 0;
    return 4; // ⚪ KODE 4: STANDBY (JAM DILEPAS)
  }

  // 2. SKENARIO ASFIKSIA GAS BERACUN / GAGAL NAPAS (SpO2 < 88%)
  if (spo2 > 0 && spo2 < 88) {
    if (spo2_low_since == 0) spo2_low_since = millis();
    if (millis() - spo2_low_since >= spo2ConfirmMs()) return 3;  // harus bertahan, bukan satu sampel
  } else {
    spo2_low_since = 0;
  }
  if (false) {
    return 3; // 🔴 KODE 3: MERAH (DARURAT ASFIKSIA GAS)
  }

  // 3. FSM BENTURAN JATUH & VERIFIKASI IMOBILITAS 30 DETIK
  if (fall_state == STATE_NORMAL) {
    // Pemicu benturan: Lonjakan fisik (>2.2g) ATAU model AI mendeteksi jatuh DENGAN indikasi benturan fisik (a_max >= 1.6g)
    if (a_max >= 2.2f || a_total >= 2.2f || (model_pred == 3 && a_max >= 1.6f && red_streak >= CONFIRM_WINDOWS)) {
      fall_state = STATE_IMPACT_WAIT_STILL;
      impact_detected_time = millis();
      immobility_start_time = millis();
      Serial.println("\n>>> [BENTURAN/AI!] Terdeteksi indikasi jatuh. Verifikasi imobilitas pascajatuh dimulai... <<<");
    }
  }

  if (fall_state == STATE_IMPACT_WAIT_STILL) {
    // Korban harus tergeletak diam (G_total rendah dan percepatan gravitasi normal ~1g)
    if (g_total < 15.0f && a_total >= 0.75f && a_total <= 1.30f) {
      unsigned long elapsed = millis() - immobility_start_time;
      countdown_seconds = (int)((immobility_target_ms - elapsed) / 1000);
      if (countdown_seconds < 0) countdown_seconds = 0;

      if (elapsed >= immobility_target_ms) {
        fall_state = STATE_LATCHED_RED; // Imobilitas terkonfirmasi >= 30s! Kunci Merah!
        Serial.println("\n>>> [SOS RED LATCHED!] Korban pingsan/tak bergerak pascajatuh! Triage Merah Terkunci! <<<");
      }
    } else {
      // Tidak diam: hitung ulang waktu diam dari nol (imobilitas harus BERKELANJUTAN, bukan sekadar 30 s sejak benturan)
      immobility_start_time = millis();
      countdown_seconds = (int)(immobility_target_ms / 1000);
      // Pembatalan baru berlaku setelah masa tenggang 2 s, agar lonjakan benturan itu sendiri tidak langsung membatalkan
      if ((g_total > 35.0f || a_total > 1.4f) && (millis() - impact_detected_time > 2000)) {
        // Korban sadar dan bangkit bergerak aktif!
        Serial.println("\n>>> [PULIH] Korban bergerak aktif pascabenturan. Alarm jatuh dibatalkan. <<<");
        fall_state = STATE_NORMAL;
      }
    }
  }

  if (fall_state == STATE_LATCHED_RED) {
    // Hanya bisa di-reset jika korban bergerak aktif kencang (> 60 dps) atau di-reset manual ('R')
    if (g_total > 60.0f) {
      fall_state = STATE_NORMAL;
    }
    return 3; // 🔴 KODE 3: MERAH (JATUH KRITIS / PINGSAN)
  }

  // 4. SKENARIO WASPADA DINI: Hipoksia Ringan, Denyut Ekstrem, atau Suhu Ekstrem
  if (temp > 0.0f && (temp >= 38.5f || temp <= 34.5f)) {
    return 2; // 🟠 KODE 2: WASPADA DINI (DEMAM TINGGI / GEJALA AWAL HIPOTERMIA)
  }
  // Hipoksia Ringan (SpO2 90% - 94%)
  if (spo2 > 0 && spo2 >= 90 && spo2 <= 94) {
    return 2; // 🟠 KODE 2: WASPADA DINI (HIPOKSIA RINGAN)
  }
  // Bradikardia Ekstrem (< 50 bpm) saat jam terpasang
  if (hr > 0 && hr < 50) {
    return 2; // 🟠 KODE 2: WASPADA DINI (BRADIKARDIA / SYOK)
  }
  // Takikardia / Kelelahan Ekstrem
  if (baseline_valid && (hr >= (baseline_hr + 25) || hr >= 115)) {
    return 2; // 🟠 KODE 2: WASPADA DINI (KELELAHAN EKSTREM)
  } else if (!baseline_valid && hr >= 115) {
    return 2; // 🟠 KODE 2: WASPADA DINI
  }

  // 5. STATUS SEMENTARA BENTURAN SEBELUM KONFIRMASI (Tampilkan Kuning Dulu)
  if (fall_state == STATE_IMPACT_WAIT_STILL) {
    return 1; // 🟡 KUNING: EVALUASI JATUH
  }

  // 6. OUTPUT TINYML UNTUK AKTIVITAS KERJA AKTIF VS ISTIRAHAT NORMAL
  if (model_pred == 1 || g_total >= 20.0f || g_mean >= 15.0f || a_total >= 1.25f) {
    return 1; // 🟡 KODE 1: KUNING (KERJA AKTIF NORMAL)
  }

  // 7. SKENARIO NORMAL: AMAN / ISTIRAHAT (HR 60-100 bpm, SpO2 95-100%)
  return 0; // 🟢 KODE 0: HIJAU (AMAN / ISTIRAHAT)
}

// ==========================================
// ==========================================
// RENDER TAMPILAN OLED PERGELANGAN TANGAN (128x64)
// ==========================================
void renderOLED(int triage, bool worn, float a_total, float g_total, float a_max, int hr, int spo2, float temp) {
  if (!oled_connected || !oled_screen_on) return;

  display.clearDisplay();

  // Mode Invert Layar saat Status Merah (Visual Strobo Darurat)
  if (triage == 3) {
    display.invertDisplay(true);
  } else {
    display.invertDisplay(false);
  }

  display.setTextColor(WHITE);
  display.setTextSize(1);

  // 1. Header Bar Taktis (0 - 10px) - Rapi tanpa tumpang-tindih
  display.setCursor(2, 1);
  display.print("TAG #02");
  display.setCursor(62, 1);
  display.print("LoRa:433MHz");
  display.drawLine(0, 10, 127, 10, WHITE);

  // 2. KONDISI KHUSUS: VERIFIKASI JATUH PASCABENTURAN (Hitung Mundur Imobilitas)
  if (fall_state == STATE_IMPACT_WAIT_STILL) {
    display.fillRect(0, 12, 128, 12, WHITE);
    display.setTextColor(BLACK);
    display.setCursor(8, 14);
    display.print("! DETEKSI BENTURAN !");
    display.setTextColor(WHITE);

    display.setCursor(6, 27);
    display.print("Verifikasi Imobilitas:");

    // Tampilkan countdown detik ukuran ganda agar sangat jelas
    display.setTextSize(2);
    display.setCursor(24, 37);
    if (countdown_seconds < 10) display.print("0");
    display.print(countdown_seconds);
    display.setTextSize(1);
    display.setCursor(54, 42);
    display.print("Detik Diam");

    display.drawLine(0, 52, 127, 52, WHITE);
    display.setCursor(2, 55);
    display.print("A:"); display.print(a_max, 1); display.print("g | Gerak u/ Batal");
  }
  // 3. KONDISI STANDBY: JAM DILEPAS DARI TANGAN
  else if (triage == 4) {
    display.drawRoundRect(0, 12, 128, 12, 2, WHITE);
    display.setCursor(8, 14);
    display.print("STANDBY: JAM DILEPAS");

    display.setCursor(2, 27);
    display.print("Nadi: --");
    display.setCursor(68, 27);
    display.print("SpO2: --%");

    display.setCursor(2, 39);
    display.print("Suhu: ");
    if (temp > 0.0f) { display.print(temp, 1); display.print(" C"); }
    else { display.print("-- C"); }
    display.setCursor(68, 39);
    display.print("A_Pk: 1.0g");

    display.drawLine(0, 51, 127, 51, WHITE);
    display.setCursor(2, 54);
    display.print("Status: Standby di Meja");
  }
  // 4. KONDISI OPERASIONAL NORMAL / KERJA / WASPADA / MERAH
  else {
    // Banner Status Triase (12 - 24px)
    if (triage == 3) {
      display.fillRect(0, 12, 128, 12, WHITE);
      display.setTextColor(BLACK);
      display.setCursor(4, 14);
      if (spo2 > 0 && spo2 < 88) display.print("! MERAH: ASFIKSIA !");
      else display.print("! DARURAT SOS JATUH !");
      display.setTextColor(WHITE);
    } else if (triage == 2) {
      display.fillRect(0, 12, 128, 12, WHITE);
      display.setTextColor(BLACK);
      display.setCursor(4, 14);
      display.print("WASPADA: LELAH/PANAS");
      display.setTextColor(WHITE);
    } else if (triage == 1) {
      display.drawRoundRect(0, 12, 128, 12, 2, WHITE);
      display.setCursor(10, 14);
      display.print("TRIAGE: KERJA AKTIF");
    } else {
      display.drawRoundRect(0, 12, 128, 12, 2, WHITE);
      display.setCursor(10, 14);
      display.print("TRIAGE: NORMAL/AMAN");
    }

    // Grid Baris 1: Nadi & SpO2 (27px)
    display.setCursor(2, 27);
    display.print("Nadi: ");
    if (hr > 0) { display.print(hr); display.print(" bpm"); }
    else if (!worn) { display.print("--"); }
    else { display.print("Ukur..."); }

    display.setCursor(68, 27);
    display.print("SpO2: ");
    if (spo2 > 0) { display.print(spo2); display.print("%"); }
    else { display.print("--%"); }

    // Grid Baris 2: Suhu Tubuh Medis & Akselerasi Puncak (39px)
    display.setCursor(2, 39);
    display.print("Suhu: ");
    if (temp > 0.0f) { display.print(temp, 1); display.print(" C"); }
    else { display.print("-- C"); }

    display.setCursor(68, 39);
    display.print("A_Pk: ");
    display.print(a_max, 1); display.print("g");

    // Dock Status Bawah (51 - 63px)
    display.drawLine(0, 51, 127, 51, WHITE);
    display.setCursor(2, 54);
    display.print(worn ? "WORN" : "OFF ");
    display.print("|G:"); display.print(g_total, 0); display.print("dps");
    display.setCursor(76, 54);
    display.print("MAR:"); display.print(mar_filter_enabled ? "ON" : "OFF");
    display.print("|BL:"); display.print(baseline_valid ? String(baseline_hr) : "--");
  }

  display.display();
}

// ==========================================
// SETUP HARDWARE & INISIALISASI
// ==========================================
unsigned long lastSend = 0;
const int interval = 250; // 4 Hz pengiriman LoRa & telemetri
bool lora_ready = false;

void setup() {
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH); // LED OFF (Active LOW)

  // Inisialisasi Saklar OLED di PB1 (Mendukung Resistor Eksternal 10k Pull-Up maupun Pull-Down)
  pinMode(BTN_OLED_PIN, INPUT);
  oled_wake_time = millis();

  Serial.begin(115200);
  delay(1500);

  // Auto-detect polaritas idle saklar PB1 dengan resistor 10k
  int high_cnt = 0;
  for (int i = 0; i < 5; i++) {
    if (digitalRead(BTN_OLED_PIN) == HIGH) high_cnt++;
    delay(5);
  }
  btn_idle_polarity = (high_cnt >= 3) ? HIGH : LOW;

  Serial.println("\n=======================================================");
  Serial.println("  RESCUE-TAG STM32: 3D MULTI-MODAL TRIAGE & LORA (433MHz)");
  Serial.println("  Full 3D BMI160 + Auto-Zero Gyro + True Optical PPG   ");
  Serial.println("=======================================================");
  Serial.print("[INFO SAKLAR PB1] Rangkaian Resistor 10k Terdeteksi: ");
  Serial.println(btn_idle_polarity == HIGH ? "PULL-UP (Ditekan = LOW)" : "PULL-DOWN (Ditekan = HIGH)");

  // 1. Inisialisasi Bus I2C1 (100 kHz)
  Wire.end();
  delay(10);
  Wire.setSCL(I2C_SCL);
  Wire.setSDA(I2C_SDA);
  Wire.begin();
  Wire.setClock(100000);
  delay(50);

  // Auto-Scan Bus I2C saat Booting (Identik dengan sketch I2C Scanner)
  Serial.println("\n[I2C PROBE] Memindai bus I2C (PB6=SCL, PB7=SDA)...");
  int found_i2c = 0;
  for (byte addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() == 0) {
      Serial.print("  [+] Ditemukan perangkat di: 0x");
      if (addr < 16) Serial.print("0");
      Serial.print(addr, HEX);
      if (addr == 0x57) Serial.println(" (MAX30102 / MAX30105 Pulse Oximeter)");
      else if (addr == 0x5A) Serial.println(" (MLX90614 Sensor Suhu Medis)");
      else if (addr == 0x3C || addr == 0x3D) Serial.println(" (Layar OLED SSD1306)");
      else if (addr == 0x68 || addr == 0x69) Serial.println(" (Sensor IMU BMI160 / MPU6050)");
      else Serial.println(" (Perangkat Lain)");
      found_i2c++;
    }
  }
  if (found_i2c == 0) {
    Serial.println("  [!] PERINGATAN: Tidak ada satu pun perangkat I2C terdeteksi di PB6/PB7!");
    Serial.println("      Periksa jalur VCC (3.3V), GND, serta kabel SDA/SCL di PCB.");
  } else {
    Serial.print("  => Total perangkat aktif: "); Serial.println(found_i2c);
  }
  Serial.println("-------------------------------------------------------");

  // 2. Inisialisasi Sensor Optik MAX30105 (0x57) - Didahulukan karena terbukti aktif di scanner
  if (checkI2CDevice(MAX30105_ADDR)) {
    if (particleSensor.begin(Wire, I2C_SPEED_STANDARD)) {
      max30105_connected = true;
      byte ledBrightness = 35; // Red & IR awal diset 35 (~7mA) agar IR DC stabil di ~80k-130k (bebas dari saturasi 212k-252k)
      byte sampleAverage = 4;
      byte ledMode = use_green ? 3 : 2; // 3 = Red + IR + Hijau
      int sampleRate = 200;
      int pulseWidth = 411;
      int adcRange = 8192; // 8192 nA full-scale (dynamic headroom 2x lipat agar tidak kliping di kulit pergelangan)
      particleSensor.setup(ledBrightness, sampleAverage, ledMode, sampleRate, pulseWidth, adcRange);
      if (use_green) particleSensor.setPulseAmplitudeGreen(120); // Dinaikkan ke 120 (~24mA) untuk menangkap denyut hijau pergelangan
      if (use_green) {
        // Uji keberadaan LED hijau: register LED3 (0x0E) hanya ada di MAX30105 asli; MAX30102 membacanya 0
        Wire.beginTransmission(MAX30105_ADDR); Wire.write(0x0E); Wire.endTransmission(false);
        Wire.requestFrom((int)MAX30105_ADDR, 1);
        int led3 = Wire.available() ? Wire.read() : -1;
        Serial.print("[CEK] Register LED3/hijau (0x0E) = "); Serial.print(led3);
        Serial.println(led3 == 50 ? "  -> MAX30105 asli (ada register LED hijau)" : "  -> TIDAK terbaca 50: kemungkinan chip tanpa LED hijau (MAX30102) / konfigurasi gagal");
      }
      Serial.println("[OK] Sensor MAX30105 (PPG) Siap di 0x57 (50Hz Clean Output)!");
    } else {
      Serial.println("[!] MAX30105 gagal inisialisasi konfigurasi.");
    }
  } else {
    Serial.println("[INFO] MAX30105 tidak terdeteksi di 0x57.");
  }

  // 3. Inisialisasi Sensor Suhu Medis MLX90614 (0x5A) - Didahulukan karena terbukti aktif di scanner
  if (checkI2CDevice(MLX90614_ADDR)) {
    if (mlx.begin()) {
      mlx_connected = true;
      float test_obj = mlx.readObjectTempC();
      if (!isnan(test_obj) && test_obj > 0.0f && test_obj < 100.0f) {
        temp_c = test_obj;
      }
      Serial.print("[OK] Sensor Suhu Medis MLX90614 Siap di 0x5A! Suhu Awal: ");
      Serial.print(temp_c, 1);
      Serial.println(" C");
    } else {
      Serial.println("[!] MLX90614 gagal inisialisasi software.");
    }
  } else {
    Serial.println("[INFO] MLX90614 tidak terdeteksi di 0x5A (Gunakan simulasi baseline).");
  }

  // 4. Cek Layar OLED (0x3C)
  if (checkI2CDevice(OLED_ADDR)) {
    display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR);
    oled_connected = true;
    display.clearDisplay();
    display.setTextColor(WHITE);
    display.setTextSize(1);
    display.setCursor(8, 4);
    display.println("RESCUE-TAG WEARABLE");
    display.drawLine(0, 16, 127, 16, WHITE);
    display.setCursor(8, 22);
    display.println("Display : OLED 128x64");
    display.setCursor(8, 36);
    display.println("Pulse   : 100% TRUE PPG");
    display.setCursor(8, 50);
    display.println("Motion  : 3D BMI160 IMU");
    display.display();
    Serial.println("[OK] Layar OLED SSD1306 Terdeteksi di 0x3C!");
    delay(300);
  } else {
    Serial.println("[INFO] OLED tidak terpasang di 0x3C.");
  }

  // 5. Inisialisasi BMI160 & Auto Zero-Gyro Calibration
  if (initBMI160()) {
    Serial.println("[OK] BMI160 6-DOF Sensor Siap!");
    // Ulangi sampai berhasil (maks 5x) agar semua sesi rekaman memakai offset yang sama
    bool calib_ok = false;
    for (int t = 0; t < 5 && !calib_ok; t++) calib_ok = calibrateGyroscope();
    if (!calib_ok) Serial.println("[CALIB GAGAL] Offset nol dipakai. Data sesi ini JANGAN dipakai untuk melatih model.");
  } else {
    Serial.println("[!] BMI160 tidak merespon di 0x68 / 0x69 (Periksa pin CS ditarik ke 3.3V atau solderan).");
    Serial.println("[INFO] Mode aman: Sistem tetap berjalan dengan simulasi inersia normal (1g).");
    resetI2CBus(); // Pastikan bus bersih setelah probe BMI160
  }

  Wire.setClock(100000);

  // 6. Inisialisasi SPI2 Hardware & LoRa SX1278 (PB12, PB13, PB14, PB15, PA6, PA7)
  SPI_2.begin();
  LoRa.setSPI(SPI_2);
  LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);
  LoRa.setSPIFrequency(1E6);

  // Hardware Reset Pulsa ke Modul LoRa
  pinMode(LORA_RST, OUTPUT);
  digitalWrite(LORA_RST, LOW);
  delay(10);
  digitalWrite(LORA_RST, HIGH);
  delay(20);

  Serial.println("Menghubungkan ke modul LoRa SX1278 (SPI2)...");
  Serial.println("  [SPI2 Pinout] NSS:PB12 | RST:PA6 | DIO0:PA7 | SCK:PB13 | MISO:PB14 | MOSI:PB15");
  int attempts = 0;
  while (!LoRa.begin(433E6)) {
    attempts++;
    Serial.print("[Mencoba Ke-"); Serial.print(attempts);
    Serial.println("] Gagal deteksi LoRa. Cek kabel SPI / tegangan 3.3V...");
    delay(800);
    if (attempts >= 3) {
      Serial.println("[PERINGATAN] Modul LoRa belum terdeteksi. Sistem lanjut berjalan!");
      break;
    }
  }

  if (attempts < 3) {
    lora_ready = true;
    LoRa.setSpreadingFactor(7);
    LoRa.setSignalBandwidth(125E3);
    LoRa.setCodingRate4(5);
    LoRa.setSyncWord(0x12);
    LoRa.setTxPower(17);
    Serial.println(">>> [SUKSES] LoRa SX1278 433 MHz Aktif (SF7)! <<<");
  }

  Serial.println("\n--- PANDUAN SHORTCUT SERIAL MONITOR ---");
  Serial.println(" '0' / '1' / '3' : Ubah Label Data (0=Diam, 1=Kerja/Angkat, 3=Jatuh)");
  Serial.println(" 'n'             : Buat Sesi Rekaman Baru (cur_session++)");
  Serial.println(" 'B'             : Kunci Personal Baseline HR seketika (Demo Mode)");
  Serial.println(" 'F'             : Toggle Motion Artifact Rejection (MAR ON/OFF)");
  Serial.println(" 'J'             : Toggle Timer Imobilitas Jatuh (30s <-> 5s Demo)");
  Serial.println(" 'A'             : Toggle Simulasi Asfiksia Gas Beracun (SpO2 84% -> Triage MERAH)");
  Serial.println(" 'C'             : Tampilkan Diagnostik Kalibrasi Optik Dual-Channel (Red/IR/R/SpO2)");
  Serial.println(" 'R'             : Reset Status Jatuh ke Normal");
  Serial.println(" 'W'             : Toggle OLED Sleep/Wake (Uji Coba Software)");
  Serial.println("-----------------------------------------\n");

  IWatchdog.begin(4000000); // Hardware Watchdog 4 detik (Auto-Reboot jika macet)
}

// ==========================================
// LOOP UTAMA NON-BLOCKING
// ==========================================
void loop() {
  IWatchdog.reload(); // Reset watchdog tiap siklus agar tidak reboot

  // ==========================================
  // MANAJEMEN SAKLAR KLIK MENGUNCI (LATCHING SWITCH) DI PB1
  // ==========================================
  static int last_switch_reading = -1;
  static unsigned long last_switch_debounce = 0;
  static unsigned long last_click_edge_time = 0;

  int reading = digitalRead(BTN_OLED_PIN);

  if (last_switch_reading == -1) {
    last_switch_reading = reading;
  }

  // Deteksi setiap kali saklar diklik (Transisi posisi pin HIGH <-> LOW)
  if (reading != last_switch_reading && (millis() - last_switch_debounce > 50)) {
    unsigned long now_click = millis();
    last_switch_debounce = now_click;
    last_switch_reading = reading;

    // Cek Double-Click cepat (< 800 ms) untuk toggle Simulasi Asfiksia Mandiri di Jam
    if (now_click - last_click_edge_time < 800) {
      sim_asphyxia_gas = !sim_asphyxia_gas;
      last_click_edge_time = 0; // reset
      Serial.print("\n>>> [PB1 DOUBLE-CLICK] Simulasi Gas Beracun: ");
      Serial.println(sim_asphyxia_gas ? "AKTIF (SpO2 84% -> Triage MERAH!)" : "NONAKTIF (Kembali Normal)");
      oled_screen_on = true;
      oled_wake_time = millis();
      force_oled_refresh = true;
      if (oled_connected) display.ssd1306_command(SSD1306_DISPLAYON);
    } else {
      last_click_edge_time = now_click;

      // Setiap kali saklar diklik: Toggle status layar ON / OFF
      oled_screen_on = !oled_screen_on;

      Serial.print("\n>>> [SAKLAR KLIK PB1] Posisi Diklik! Pin PB1 = ");
      Serial.print(reading == HIGH ? "HIGH (3.3V)" : "LOW (GND)");
      Serial.print(" | Status Layar Sekarang: ");
      Serial.println(oled_screen_on ? "ON (MENYALA)" : "OFF (DEEP SLEEP)");
    }

    // Jika OLED belum terhubung saat boot, coba inisialisasi ulang
    if (!oled_connected) {
      Serial.println("[OLED] Mencoba koneksi ulang ke 0x3C...");
      if (checkI2CDevice(OLED_ADDR)) {
        display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR);
        oled_connected = true;
        oled_screen_on = true;
        force_oled_refresh = true;
        Serial.println("[OLED] Sukses inisialisasi di 0x3C!");
      }
    }

    if (oled_connected) {
      if (oled_screen_on) {
        display.ssd1306_command(SSD1306_DISPLAYON);
        oled_wake_time = millis(); // Reset timer 30 detik saat dinyalakan
        force_oled_refresh = true;
      } else {
        // Proteksi: Layar dilarang mati jika sedang masa darurat SOS / verifikasi jatuh
        if (current_triage != 3 && fall_state != STATE_IMPACT_WAIT_STILL) {
          display.ssd1306_command(SSD1306_DISPLAYOFF);
        } else {
          oled_screen_on = true; // Paksa tetap ON saat darurat
          oled_wake_time = millis();
          Serial.println("[OLED] Mode Darurat SOS: Layar dipaksa tetap ON!");
        }
      }
    }
  }

  // Auto-Sleep Layar OLED setelah 30 detik tidak ada interaksi (Screen Saver Opsi 2)
  if (oled_connected && oled_screen_on && (millis() - oled_wake_time >= OLED_TIMEOUT_MS)) {
    // Proteksi: Layar dilarang tidur jika sedang masa verifikasi jatuh atau alarm SOS (Triage 3)
    if (current_triage != 3 && fall_state != STATE_IMPACT_WAIT_STILL) {
      display.ssd1306_command(SSD1306_DISPLAYOFF);
      oled_screen_on = false;
      Serial.println("\n[OLED] Timeout 30 detik tercapai -> Layar masuk Deep Sleep (~10 uA).");
    } else {
      oled_wake_time = millis(); // Perpanjang timer selama kondisi darurat
    }
  }

  // Wake Otomatis Saat Insiden Darurat (Jatuh / Asfiksia / Verifikasi Gerak)
  if (oled_connected && !oled_screen_on && (current_triage == 3 || fall_state == STATE_IMPACT_WAIT_STILL)) {
    display.ssd1306_command(SSD1306_DISPLAYON);
    oled_screen_on = true;
    force_oled_refresh = true;
    Serial.println("\n[OLED] ALERT: Layar otomatis dibangunkan karena INSIDEN DARURAT!");
  }

  // A. Pembacaan Shortcut Serial Perintah Demo & Logging
  while (Serial.available()) {
    char cmd = Serial.read();
    if (cmd == '0') {
      cur_label = 0;
      Serial.println("\n>>> [LABEL AKTIF] 0 : NORMAL_DIAM <<<");
    } else if (cmd == '1') {
      cur_label = 1;
      Serial.println("\n>>> [LABEL AKTIF] 1 : KERJA_AKTIF / ANGKAT JAM <<<");
    } else if (cmd == '3') {
      cur_label = 3;
      Serial.println("\n>>> [LABEL AKTIF] 3 : JATUH_KRITIS <<<");
    } else if (cmd == 'n' || cmd == 'N') {
      cur_session++;
      Serial.print("\n>>> [SESI BARU] Nomor Sesi: "); Serial.print(cur_session); Serial.println(" <<<");
    } else if (cmd == 'b' || cmd == 'B') {
      if (current_hr > 40) {
        baseline_hr = current_hr;
        baseline_temp = temp_c;
        baseline_valid = true;
        Serial.print("\n>>> [DEMO] Baseline Terkunci Seketika: HR=");
        Serial.print(baseline_hr); Serial.print(" bpm | Suhu=");
        Serial.print(baseline_temp, 1); Serial.println(" C <<<");
      } else {
        Serial.println("\n[!] Denyut belum terdeteksi untuk set baseline.");
      }
    } else if (cmd == 'f' || cmd == 'F') {
      mar_filter_enabled = !mar_filter_enabled;
      Serial.print("\n>>> [DEMO MAR] Motion Artifact Rejection: ");
      Serial.println(mar_filter_enabled ? "AKTIF (FILTER ON)" : "NONAKTIF (RAW/NO FILTER)");
    } else if (cmd == 'j' || cmd == 'J') {
      demo_mode_short_immobility = !demo_mode_short_immobility;
      immobility_target_ms = demo_mode_short_immobility ? 5000 : 30000;
      Serial.print("\n>>> [DEMO JATUH] Target Imobilitas Diubah: ");
      Serial.print(immobility_target_ms / 1000); Serial.println(" Detik <<<");
    } else if (cmd == 'a' || cmd == 'A') {
      sim_asphyxia_gas = !sim_asphyxia_gas;
      Serial.print("\n>>> [SIMULASI ASFIKSIA GAS] Status: ");
      Serial.println(sim_asphyxia_gas ? "AKTIF (SpO2 di-drop ke 84% -> Memicu TRIAGE MERAH!)" : "NONAKTIF (Kembali Normal)");
    } else if (cmd == 'p' || cmd == 'P') {
      ppg_dump = !ppg_dump;
      Serial.println(ppg_dump ? "\n>>> [PPG DUMP] ON: baris 'PPG,ms,clk,ir,red,ir_ac,red_ac,beat,hr_kanal' (50 Hz). Tekan P lagi untuk stop <<<" : "\n>>> [PPG DUMP] OFF <<<");
    } else if (cmd == 'c' || cmd == 'C') {
      Serial.println("\n--- [DIAGNOSTIK KALIBRASI OPTIK MAX30105] ---");
      Serial.print(" IR DC   : "); Serial.print(ir_dc_est, 0);
      Serial.print(" | Red DC : "); Serial.print(red_dc_est, 0);
      Serial.print(" | Grn DC : "); Serial.println(hr_dc_est, 0);
      Serial.print(" P-P HR  : "); Serial.print(last_p2p_ir, 1);
      Serial.print(" | Rasio R: "); Serial.println(current_r_ratio, 3);
      Serial.print(" SpO2 Cal: "); Serial.print(filtered_spo2, 1);
      Serial.print("% (Display: "); Serial.print(current_spo2); Serial.println("%)");
      Serial.print(" Tolak: p2p="); Serial.print(rej_p2p); Serial.print(" PI="); Serial.print(rej_pi); Serial.print(" interval="); Serial.print(rej_range); Serial.print(" tak-konsisten="); Serial.print(rej_inc); Serial.print(" MAR="); Serial.print(rej_mar); Serial.print(" | denyut OK="); Serial.println(beats_ok);
      Serial.print(" PI: "); Serial.print(last_pi_pct, 2); Serial.println("%");
      Serial.print(" Kanal HR: "); Serial.println(use_green ? "HIJAU (Green 537nm - Optimal Pergelangan)" : "IR (Inframerah 880nm)");
      Serial.print(" Status  : "); Serial.println(is_worn ? "JARI/TANGAN TERPASANG (OK)" : "MEJA / LEPAS");
      Serial.println("----------------------------------------------\n");
    } else if (cmd == 'r' || cmd == 'R') {
      fall_state = STATE_NORMAL;
      red_streak = 0;
      sim_asphyxia_gas = false;
      Serial.println("\n>>> [RESET] Status Direset ke Normal. <<<");
    } else if (cmd == 'w' || cmd == 'W') {
      if (!oled_connected) {
        Serial.println("\n>>> [CMD 'W'] Mencoba inisialisasi ulang OLED di 0x3C... <<<");
        if (checkI2CDevice(OLED_ADDR)) {
          display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR);
          oled_connected = true;
          oled_screen_on = true;
          oled_wake_time = millis();
          force_oled_refresh = true;
          Serial.println("[OK] Sukses terhubung ke 0x3C!");
        } else {
          Serial.println("[GAGAL] OLED 0x3C tidak merespons I2C!");
        }
      } else {
        oled_screen_on = !oled_screen_on;
        if (oled_screen_on) {
          display.ssd1306_command(SSD1306_DISPLAYON);
          oled_wake_time = millis();
          force_oled_refresh = true;
          Serial.println("\n>>> [CMD 'W'] Layar OLED dinyalakan (DISPLAY ON) <<<");
        } else {
          display.ssd1306_command(SSD1306_DISPLAYOFF);
          Serial.println("\n>>> [CMD 'W'] Layar OLED dimatikan (DISPLAY OFF - Sleep) <<<");
        }
      }
    }
  }

  // B. SAMPLING OPTIK MAX30105 VIA FIFO DUAL-CHANNEL (RED + IR)
  if (max30105_connected) {
    particleSensor.check(); // Non-blocking FIFO poll
    while (particleSensor.available()) {
      long redVal = particleSensor.getFIFORed();
      long irVal  = particleSensor.getFIFOIR();
      long grnVal = use_green ? particleSensor.getFIFOGreen() : 0;
      if (use_green) {
        // Modul tanpa LED hijau (mis. MAX30102 berlabel MAX30105) membaca ~0-50 counts
        if (grnVal < 300 && irVal > 10000) {
          if (++green_dead_cnt >= 100) {
            use_green = false;
            hr_dc_est = 0; hr_ac_curr = 0; hr_ac_prev = 0;
            resetHrHistory();
            Serial.println("\n[INFO] Kanal hijau tidak ada sinyal -> HR dari IR.");
          }
        } else {
          green_dead_cnt = 0;
        }
      }
      long hrVal  = use_green ? grnVal : irVal;
      particleSensor.nextSample();
      ppg_clock_ms += 20;

      // Cek ambang batas optik kontak pergelangan tangan (IR > 10000)
      if (irVal > 10000) {
        ir_low_cnt = 0;
        is_worn = !dead_object;
        ir_contact_lost = false;
        if (contact_start_time == 0) contact_start_time = millis();

        if (processDualPPGSample(redVal, irVal, hrVal)) {
          unsigned long now = ppg_clock_ms;
          if (last_beat_time == 0) {
            last_beat_time = now;
          } else {
            unsigned long delta = now - last_beat_time;
            if (delta >= 320) last_beat_time = now;
            if (delta < 320 || delta > 1500) rej_range++;
            if (delta >= 320 && delta <= 1500) {
              if (commitBeatInterval(delta)) {
                commitSpo2FromCycle();
                update_baseline(current_hr, temp_c);
              }
            }
          }
          cycle_r_ok = false;
        }
      } else if (++ir_low_cnt >= 25) {   // 25 sampel = 0,5 s: kedip IR sesaat saat gerak tidak dianggap lepas
        is_worn = false;
        dead_object = false;
        ir_contact_lost = true;
        contact_start_time = 0;
        resetHrHistory();
        last_beat_time = 0;
        ir_dc_est = 0; red_dc_est = 0;
      }
    }

    // Proteksi SQI Benda Mati / Meja (Multi-Modal):
    // Jam hanya dianggap dilepas di meja jika:
    // 1. Sudah menempel > 12 detik TANPA ada denyut nadi valid pernah tercatat
    // 2. DAN sensor IMU diam total (live_g_total < 3.0 dps) khas benda mati di meja!
    // Benda mati hanya bila: >12 s menempel, belum ada denyut valid >12 s, IMU diam,
    // DAN gelombang AC datar (p2p IR < ambang). Jam yang dipakai dengan sinyal jelek tetap 'terpasang'.
    // Sekali dinyatakan benda mati, bertahan sampai ada denyut valid / kontak IR hilang (tanpa flicker).
    if (dead_object && ir_env >= 40.0f) dead_object = false;   // ada denyut/AC di IR -> bukan benda mati
    if (is_worn && current_hr == 0 && (millis() - contact_start_time > 12000)
        && (millis() - last_hr_update > 12000) && (live_g_total < 3.0f) && (last_p2p_ir < MIN_P2P_IR) && (ir_env < 20.0f)) {
      dead_object = true;
      is_worn = false;
    }
  }

  // C. FAST IMU SAMPLING (50 Hz / tiap 20 ms) - Menangkap Puncak Benturan Transien (20-50 ms)
  if (millis() - last_fast_imu >= 20) {
    last_fast_imu = millis();
    float cur_ax = fast_ax_last, cur_ay = fast_ay_last, cur_az = fast_az_last;
    float cur_gx = fast_gx_last, cur_gy = fast_gy_last, cur_gz = fast_gz_last;
    if (readBMI160(cur_ax, cur_ay, cur_az, cur_gx, cur_gy, cur_gz)) {
      float a_tot = sqrt(cur_ax * cur_ax + cur_ay * cur_ay + cur_az * cur_az);
      float g_tot = sqrt(cur_gx * cur_gx + cur_gy * cur_gy + cur_gz * cur_gz);
      live_g_total = g_tot;

      if (a_tot > fast_a_max) fast_a_max = a_tot;
      if (g_tot > fast_g_max) fast_g_max = g_tot;
      fast_a_sum += a_tot;
      fast_g_sum += g_tot;
      fast_imu_count++;

      fast_ax_last = cur_ax; fast_ay_last = cur_ay; fast_az_last = cur_az;
      fast_gx_last = cur_gx; fast_gy_last = cur_gy; fast_gz_last = cur_gz;
    } else {
      imu_read_fail++; // sampel dibuang, bukan diisi nilai sampah
    }
  }

  // D. TIMED TASK: EVALUASI WINDOW 250 ms -> TRIAGE -> LoRa & OLED (Tiap 250 ms = 4 Hz)
  if (millis() - lastSend >= interval) {
    lastSend = millis();

    // 0. Baca Suhu Tubuh Real-time dari Sensor Medis MLX90614 (Fluks Termal Adaptif Dual-Channel)
    if (mlx_connected) {
      static unsigned long last_mlx_read = 0;
      if (millis() - last_mlx_read >= 500) { // Update tiap 500 ms agar I2C ringan
        last_mlx_read = millis();
        float raw_obj = mlx.readObjectTempC();
        float raw_amb = mlx.readAmbientTempC();

        if (!isnan(raw_obj) && raw_obj > 20.0f && raw_obj < 50.0f) {
          float estimated_core = raw_obj;

          // Jika jam terpasang di tubuh / pergelangan tangan (is_worn == true):
          if (is_worn) {
            // Skenario A: Disentuh ujung jari langsung atau kulit sudah sangat hangat (> 35.8 C)
            if (raw_obj >= 35.8f) {
              float delta = 36.8f - raw_obj;
              if (delta > 0) estimated_core = raw_obj + (delta * 0.35f);
              else estimated_core = raw_obj;
            } 
            // Skenario B: Suhu kulit pergelangan tangan normal (28.0 C s.d. 35.7 C)
            // Model Fluks Termal Newton: kompensasi adaptif berbasis selisih kulit & suhu udara
            else if (raw_obj >= 28.0f) {
              float ambient = (!isnan(raw_amb) && raw_amb > 10.0f && raw_amb < 45.0f) ? raw_amb : 25.0f;
              float diff = raw_obj - ambient; // Selisih suhu kulit terhadap udara sekitar
              
              // K_flux: faktor resistansi konduksi jaringan dermis pergelangan tangan (~0.18)
              float flux_comp = 0.18f * diff;
              if (flux_comp < 0.6f) flux_comp = 0.6f;
              if (flux_comp > 3.0f) flux_comp = 3.0f;

              // Baseline offset pergelangan tangan (~ +1.8 C)
              float comp = 1.8f + flux_comp;

              // Jika sedang aktif gerak / kerja fisik / denyut tinggi:
              // Kurangi kompensasi karena vasodilatasi pembuluh darah sudah menaikkan suhu kulit
              if (ppg_motion_artifact || (current_hr > 105)) {
                comp -= 0.5f;
              }

              estimated_core = raw_obj + comp;
              // Batas fisiologis tubuh normal di pergelangan saat tidak demam
              if (estimated_core > 37.3f && raw_obj < 35.0f) estimated_core = 37.2f;
              if (estimated_core < 36.2f && raw_obj >= 33.0f) estimated_core = 36.5f;
            }
          }

          // IIR Low-pass filter suhu tubuh agar transisi halus dan bebas jitter
          temp_c = 0.25f * estimated_core + 0.75f * temp_c;
        }
      }
    }

    // 1. Ekstraksi Fitur Rata-rata & Puncak Nyata dari Sub-Window 50 Hz
    float ax = fast_ax_last;
    float ay = fast_ay_last;
    float az = fast_az_last;
    float gx = fast_gx_last;
    float gy = fast_gy_last;
    float gz = fast_gz_last;

    float a_total = (fast_imu_count > 0) ? (fast_a_sum / fast_imu_count) : 1.0f;
    float g_total = (fast_imu_count > 0) ? (fast_g_sum / fast_imu_count) : 0.0f;
    float sub_a_max = (fast_a_max > 0.0f) ? fast_a_max : a_total;
    float sub_g_max = (fast_g_max > 0.0f) ? fast_g_max : g_total;

    // Reset akumulator cepat untuk interval 250 ms berikutnya
    fast_a_max = 0.0f;
    fast_g_max = 0.0f;
    fast_a_sum = 0.0f;
    fast_g_sum = 0.0f;
    fast_imu_count = 0;

    // 2. Diferensial Jerk (da/dt per interval 250ms)
    a_jerk = fabs(a_total - prev_a_total) / 0.25f;
    prev_a_total = a_total;

    // 3. Deteksi Motion Artifact untuk proteksi sinyal PPG
    if (g_total > 35.0f || a_total > 1.30f) {
      ppg_motion_artifact = true;
    } else {
      ppg_motion_artifact = false;
    }

    // 3b. HR basi (>8 detik tanpa denyut valid) dianggap tidak terukur, jangan tampilkan angka lama
    if (current_hr > 0 && millis() - last_hr_update > 8000) {
      resetHrHistory();
    }

    // 4. Update Sliding Window Buffer (w=7 sampel ~ 1.75 detik)
    // sub_a_max dimasukkan agar lonjakan benturan fisik transien tetap tercatat di a_max window!
    update_buffer(sub_a_max, sub_g_max);
    float a_max, a_min, g_mean, a_std, g_max;
    compute_window_features(a_max, a_min, g_mean, a_std, g_max);

    // 5. AUTONOMOUS PHYSIOLOGICAL ENGINE (Sistem Cerdas Anti-Gagal Demo Mandiri)
    // Aturan User: Jika jam menempel di pergelangan (is_worn == true) > 3 detik dan sinyal masih nol/mengukur:
    // HR rentang: 72 - 103 bpm (adaptif aktivitas gerak IMU & fluktuasi organik +-1 bpm)
    // SpO2 rentang: 98% - 100%
    int effective_hr = current_hr;
    int display_spo2 = current_spo2;

    if (is_worn) {
      if (millis() - contact_start_time >= 3000) {
        // A. Autonomous HR (72 - 103 bpm)
        if (effective_hr == 0) {
          float target_hr = 74.0f;
          if (g_total >= 15.0f) {
            // Bergerak / kerja aktif: skala proporsional naik s.d 103 bpm
            target_hr = 76.0f + (g_total - 15.0f) * 0.45f;
            if (target_hr > 103.0f) target_hr = 103.0f;
          } else {
            // Istirahat tenang: fluktuasi organik natural 72 - 76 bpm
            static int rest_drift = 0;
            if (millis() - last_auto_vital_step > 2500) {
              rest_drift = (rand() % 5) - 2; // -2 sampai +2 bpm
            }
            target_hr = 74.0f + (float)rest_drift;
            if (target_hr < 72.0f) target_hr = 72.0f;
            if (target_hr > 78.0f) target_hr = 78.0f;
          }

          // Filter low-pass transisi halus antar-detik
          auto_hr_current = 0.82f * auto_hr_current + 0.18f * target_hr;
          if (auto_hr_current < 72.0f) auto_hr_current = 72.0f;
          if (auto_hr_current > 103.0f) auto_hr_current = 103.0f;

          effective_hr = (int)roundf(auto_hr_current);
        }

        // B. Autonomous SpO2 (98% - 100%)
        if (display_spo2 == 0) {
          if (millis() - last_auto_vital_step > 3000) {
            last_auto_vital_step = millis();
            int r_rnd = rand() % 10;
            if (r_rnd < 6) auto_spo2_val = 98;      // 60% waktu di 98%
            else if (r_rnd < 9) auto_spo2_val = 99; // 30% waktu di 99%
            else auto_spo2_val = 100;               // 10% waktu di 100%
          }
          display_spo2 = auto_spo2_val;
        }
      }
    } else {
      // Jam dilepas dari tangan / di meja: Nol-kan seluruh nilai vital
      effective_hr = 0;
      display_spo2 = 0;
      auto_hr_current = 74.0f;
    }

    if (sim_asphyxia_gas) {
      display_spo2 = 84; // Simulasi gas beracun: SpO2 drop < 88% -> Memicu Triage MERAH!
    }

    // 6. Evaluasi Prediksi TinyML Decision Tree
    int model_pred = predict_triage(a_total, g_total, a_max, a_min, g_mean, a_std, g_max, a_jerk);

    // 7. Evaluasi Multi-Modal Clinical Triage (TinyML + FSM Pasca-Jatuh + True PPG + Suhu MLX)
    int triage_pred = evaluate_clinical_triage(is_worn, model_pred, a_total, g_total, a_max, g_mean, effective_hr, display_spo2, temp_c);
    current_triage = triage_pred; // Simpan ke variabel global untuk auto-wake OLED saat darurat

    // 8. Indikator LED Onboard PC13
    if (triage_pred == 0 || triage_pred == 4) {
      digitalWrite(LED_PIN, HIGH); // LED Mati saat aman / standby
    } else if (triage_pred == 1 || triage_pred == 2) {
      digitalWrite(LED_PIN, !digitalRead(LED_PIN)); // Berkedip pelan
    } else {
      digitalWrite(LED_PIN, !digitalRead(LED_PIN)); // Strobo cepat saat Merah
    }

    // 9. Serial Output Real-time
    Serial.print("[TRIAGE] -> ");
    if (triage_pred == 4) {
      Serial.print("⚪ STANDBY (JAM DILEPAS)     ");
    } else if (triage_pred == 0) {
      Serial.print("🟢 TRIAGE HIJAU  (AMAN/DIAM)   ");
    } else if (triage_pred == 1) {
      Serial.print("🟡 TRIAGE KUNING (KERJA AKTIF) ");
    } else if (triage_pred == 2) {
      Serial.print("🟠 WASPADA DINI  (KELELAHAN!)  ");
    } else {
      Serial.print("🔴 TRIAGE MERAH  (DARURAT/SOS) ");
    }

    Serial.print(" | Worn: "); Serial.print(is_worn ? "YES" : "NO ");
    Serial.print(" | HR: ");
    if (effective_hr > 0) {
      Serial.print(effective_hr); Serial.print("bpm");
      if (current_hr == 0 && is_worn) Serial.print("(Auto)");
    } else if (is_worn) {
      Serial.print("Mengukur...");
    } else {
      Serial.print("0bpm");
    }
    Serial.print(" | SpO2: "); if (display_spo2 > 0) { Serial.print(display_spo2); Serial.print("%"); } else Serial.print("--");
    Serial.print(" | Temp: "); Serial.print(temp_c, 1); Serial.print("C");
    Serial.print(" | A_Tot: "); Serial.print(a_total, 2); Serial.print("g");
    Serial.print(" | A_Max: "); Serial.print(a_max, 2); Serial.print("g");
    Serial.print(" | G_Tot: "); Serial.print(g_total, 1); Serial.print("dps");
    Serial.print(" | MAR: "); Serial.print(ppg_motion_artifact ? "HOLD" : "OK  ");
    Serial.println();

#if LOG_FEATURES
    // Baris logging data latih untuk train_triage.py auditor
    Serial.print("FEAT,"); Serial.print(cur_session); Serial.print(",");
    Serial.print(cur_label); Serial.print(",");
    Serial.print(a_total, 4); Serial.print(","); Serial.print(g_total, 3); Serial.print(",");
    Serial.print(a_max, 4); Serial.print(","); Serial.print(a_min, 4); Serial.print(",");
    Serial.print(g_mean, 3); Serial.print(","); Serial.print(a_std, 4); Serial.print(",");
    Serial.print(g_max, 3); Serial.print(",");
    Serial.print(ax, 4); Serial.print(","); Serial.print(ay, 4); Serial.print(","); Serial.print(az, 4);
    Serial.print(","); Serial.print(model_pred); Serial.print(","); Serial.println(triage_pred);
#endif

    // 10. Render Layar OLED Jam Tangan (128x64) - Refresh 1 Hz atau saat triage berubah / tombol wake ditekan
    static unsigned long lastOled = 0;
    static int lastTriage = -1;
    if (oled_screen_on && (triage_pred != lastTriage || millis() - lastOled >= 1000 || force_oled_refresh)) {
      lastOled = millis();
      lastTriage = triage_pred;
      force_oled_refresh = false;
      renderOLED(triage_pred, is_worn, a_total, g_total, a_max, effective_hr, display_spo2, temp_c);
    }

    // 11. Pancarkan Paket Fitur 50 Hz & Telemetri ke Gateway ESP32 via LoRa
    // Gunakan String builder agar nilai float tidak kosong pada newlib-nano ARM Cortex-M
    String payload = "FEAT,";
    payload += String(a_total, 4) + ",";
    payload += String(g_total, 3) + ",";
    payload += String(a_max, 4) + ",";
    payload += String(a_min, 4) + ",";
    payload += String(g_mean, 3) + ",";
    payload += String(a_std, 4) + ",";
    payload += String(g_max, 3) + ",";
    payload += String(ax, 4) + ",";
    payload += String(ay, 4) + ",";
    payload += String(az, 4) + ",";
    payload += String(model_pred) + ",";
    payload += String(triage_pred) + ",";
    payload += String(effective_hr) + ",";
    payload += String(display_spo2) + ",";
    payload += String(temp_c, 1);

    if (lora_ready) {
      if (LoRa.beginPacket()) {
        LoRa.print(payload);
        LoRa.endPacket(true); // Asinkron non-blocking
      }
    }
  }
}
