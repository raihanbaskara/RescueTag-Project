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

// Pin LoRa SX1278 (SPI1 STM32)
#define LORA_SS    PA4
#define LORA_RST   PA3
#define LORA_DIO0  PA2

// Pin Sensor I2C (I2C1 STM32)
#define I2C_SCL    PB6
#define I2C_SDA    PB7

#define BMI160_ADDR   0x68
#define OLED_ADDR     0x3C
#define MAX30105_ADDR 0x57
#define MLX90614_ADDR 0x5A

// Layar OLED SSD1306 0.96" (128x64)
Adafruit_SSD1306 display(-1);
bool oled_connected = false;

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
const float MIN_P2P_IR = 30.0f;   // counts; di bawah ini dianggap noise (tune dgn perintah 'C')
const float MIN_PI_PCT = 0.05f;   // p2p/DC IR minimal (%)

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
// Terima interval; hanya konsisten (<=30% dari median) yang dipakai. true bila HR valid terbit.
bool commitBeatInterval(unsigned long delta) {
  float tmp[IBI_N];
  if (ibi_cnt >= 3) {
    for (byte i = 0; i < ibi_cnt; i++) tmp[i] = (float)ibi_hist[i];
    float m = medianOf(tmp, ibi_cnt);
    if (fabsf((float)delta - m) > 0.30f * m) {
      rej_inc++;
      if (++ibi_reject >= 3) { ibi_cnt = 0; ibi_pos = 0; ibi_reject = 0; } // ritme berubah -> mulai ulang
      return false;
    }
  }
  ibi_reject = 0; beats_ok++; dead_object = false;
  ibi_hist[ibi_pos] = delta; ibi_pos = (ibi_pos + 1) % IBI_N; if (ibi_cnt < IBI_N) ibi_cnt++;
  if (ibi_cnt < 3) return false;                 // butuh >=3 interval sebelum menampilkan HR
  for (byte i = 0; i < ibi_cnt; i++) tmp[i] = (float)ibi_hist[i];
  float m = medianOf(tmp, ibi_cnt);
  // Gerbang kualitas: interval harus rapat (CV < 20%), kalau tidak HR tidak ditampilkan
  float var = 0; for (byte i = 0; i < ibi_cnt; i++) { float d = tmp[i] - m; var += d * d; }
  if (sqrtf(var / ibi_cnt) > 0.20f * m) return false;
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
bool sim_asphyxia_gas = false;   // Toggle Serial 'A' untuk demo juri

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

  // Jika MAR aktif dan terdeteksi gerakan tangan intensif, tahan deteksi beat
  if (mar_filter_enabled && ppg_motion_artifact) {
    rej_mar++;
    return false;
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

  // 6. Zero-Crossing Positif pada Kanal IR (Fase Sistolik Naik)
  if ((hr_ac_prev < 0.0f) && (hr_ac_curr >= 0.0f)) {
    float peak_to_peak_ir = hr_ac_max - hr_ac_min;
    pos_edge = true;
    neg_edge = false;
    hr_ac_max = 0;

    // Ambang batas denyut biologis valid:
    // Puncak ke puncak IR > 10 counts dan ada minimal 8 sampel per siklus (~250 ms)
    last_p2p_ir = peak_to_peak_ir;
    last_pi_pct = (hr_dc_est > 0) ? 100.0f * peak_to_peak_ir / hr_dc_est : 0;
    if (sample_cycle_count >= 8) { if (peak_to_peak_ir <= MIN_P2P_IR) rej_p2p++; else if (last_pi_pct < MIN_PI_PCT) rej_pi++; }
    if (peak_to_peak_ir > MIN_P2P_IR && peak_to_peak_ir < 15000.0f && last_pi_pct >= MIN_PI_PCT && sample_cycle_count >= 8) {
      beatDetected = true;

      // Hitung RMS AC untuk siklus detak jantung ini
      float rms_ir  = sqrt(sum_sq_ir  / sample_cycle_count);
      float rms_red = sqrt(sum_sq_red / sample_cycle_count);

      // Hitung Rasio Dua Panjang Gelombang (Ratio-of-Ratios R)
      if (ir_dc_est > 2000.0f && red_dc_est > 2000.0f && rms_ir > 1.0f) {
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

void writeReg(uint8_t reg, uint8_t val) {
  Wire.beginTransmission(BMI160_ADDR);
  Wire.write(reg);
  Wire.write(val);
  Wire.endTransmission();
}

bool initBMI160() {
  Wire.beginTransmission(BMI160_ADDR);
  Wire.write(0x00);
  if (Wire.endTransmission() != 0) return false;
  
  Wire.requestFrom((uint8_t)BMI160_ADDR, (uint8_t)1);
  if (Wire.available()) {
    uint8_t id = Wire.read();
    Serial.print("BMI160 Chip ID: 0x"); 
    Serial.println(id, HEX);
  }

  writeReg(0x7E, 0x11); delay(10); // Power on Accel
  writeReg(0x7E, 0x15); delay(50); // Power on Gyro
  writeReg(0x41, 0x0C); delay(5);  // Accel ±16g (2048 LSB/g)
  writeReg(0x43, 0x00); delay(5);  // Gyro ±2000 dps (16.4 LSB/dps)
  return true;
}

// Baca raw registers 12 byte (tanpa koreksi offset)
// Mengembalikan true hanya jika 12 byte benar-benar terbaca. Jika false, argumen TIDAK diubah.
bool readRawBMI160(float &ax, float &ay, float &az, float &gx, float &gy, float &gz) {
  Wire.beginTransmission(BMI160_ADDR);
  Wire.write(0x0C);
  Wire.endTransmission(false);

  Wire.requestFrom((uint8_t)BMI160_ADDR, (uint8_t)12);
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

  // 4. SKENARIO WASPADA DINI: Kenaikan denyut drastis dari baseline ATAU Suhu Ekstrem
  if (temp > 0.0f && (temp >= 38.5f || temp <= 34.5f)) {
    return 2; // 🟠 KODE 2: WASPADA DINI (DEMAM TINGGI / GEJALA AWAL HIPOTERMIA)
  }
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
  if (model_pred == 1 || g_total >= 25.0f || g_mean >= 20.0f || a_total >= 1.25f) {
    return 1; // 🟡 KODE 1: KUNING (KERJA AKTIF NORMAL)
  }

  // 7. SKENARIO NORMAL: AMAN / ISTIRAHAT
  return 0; // 🟢 KODE 0: HIJAU (AMAN / ISTIRAHAT)
}

// ==========================================
// RENDER TAMPILAN OLED PERGELANGAN TANGAN (128x64)
// ==========================================
void renderOLED(int triage, bool worn, float a_total, float g_total, float a_max, int hr, int spo2, float temp) {
  if (!oled_connected) return;

  display.clearDisplay();

  // Mode Invert Layar saat Status Merah (Visual Strobo Kontras Tinggi)
  if (triage == 3) {
    display.invertDisplay(true);
  } else {
    display.invertDisplay(false);
  }

  display.setTextColor(WHITE);

  // 1. Header Bar
  display.setTextSize(1);
  display.setCursor(4, 1);
  display.print("RESCUE-TAG   LoRa:OK");
  display.drawLine(0, 10, 127, 10, WHITE);

  if (triage == 4) {
    // STANDBY
    display.drawRect(2, 13, 124, 12, WHITE);
    display.setCursor(8, 15);
    display.print("[ STATUS: JAM LEPAS ]");
    display.setCursor(4, 28); display.print("Nadi  : -- bpm (Off)");
    display.setCursor(4, 40); display.print("SpO2  : -- %");
    display.setCursor(4, 52); display.print("Suhu  : "); display.print(temp, 1); display.println(" C (Ruang)");
  }
  else if (fall_state == STATE_IMPACT_WAIT_STILL) {
    // FASE VERIFIKASI JATUH
    display.drawRect(2, 13, 124, 12, WHITE);
    display.setCursor(8, 15);
    display.print("! BENTURAN JATUH !");
    display.setCursor(4, 28); display.print("Verifikasi Imobilitas");
    display.setCursor(4, 40); display.print("Sisa Waktu : "); display.print(countdown_seconds); display.print("s");
    display.setCursor(4, 52); display.print("A_Max: "); display.print(a_max, 1); display.print("g | G:"); display.print(g_total, 0);
  }
  else {
    // Status Triage Normal / Kerja / Waspada / Merah
    display.drawRect(2, 13, 124, 12, WHITE);
    display.setCursor(6, 15);
    if (triage == 0)      display.print("TRIAGE: HIJAU (AMAN)");
    else if (triage == 1) display.print("TRIAGE: KUNING(KERJA)");
    else if (triage == 2) display.print("WASPADA: LELAH/PANAS");
    else if (spo2 > 0 && spo2 < 88) display.print("! MERAH: ASFIKSIA GAS!");
    else                  display.print("!! MERAH: JATUH/SOS!");

    display.setCursor(4, 28);
    display.print("HR: ");
    if (hr > 0) { display.print(hr); display.print(" bpm"); }
    else display.print("Mengukur...");
    display.print(" | SpO2: "); if (spo2 > 0) { display.print(spo2); display.print("%"); } else display.print("--");

    display.setCursor(4, 40);
    display.print("Suhu: "); display.print(temp, 1); display.print("C");
    display.print(" | A: "); display.print(a_max, 1); display.print("g");

    // Bottom Bar Info
    display.setCursor(4, 54);
    display.print("MAR:"); display.print(mar_filter_enabled ? "ON " : "OFF");
    display.print("|BL:");
    if (baseline_valid) { display.print(baseline_hr); }
    else { display.print("WAIT"); }
    display.print("|J:"); display.print(immobility_target_ms / 1000); display.print("s");
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

  Serial.begin(115200);
  delay(1500);

  Serial.println("\n=======================================================");
  Serial.println("  RESCUE-TAG STM32: 3D MULTI-MODAL TRIAGE & LORA (433MHz)");
  Serial.println("  Full 3D BMI160 + Auto-Zero Gyro + True Optical PPG   ");
  Serial.println("=======================================================");

  // 1. Inisialisasi Bus I2C1 (100 kHz)
  Wire.setSCL(I2C_SCL);
  Wire.setSDA(I2C_SDA);
  Wire.begin();
  Wire.setClock(100000);

  // 2. Cek Layar OLED (0x3C)
  Wire.beginTransmission(OLED_ADDR);
  if (Wire.endTransmission() == 0) {
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
    delay(500);
  } else {
    Serial.println("[INFO] OLED tidak terpasang di 0x3C.");
  }

  // 3. Inisialisasi BMI160 & Auto Zero-Gyro Calibration
  if (initBMI160()) {
    Serial.println("[OK] BMI160 6-DOF Sensor Siap!");
    // Ulangi sampai berhasil (maks 5x) agar semua sesi rekaman memakai offset yang sama
    bool calib_ok = false;
    for (int t = 0; t < 5 && !calib_ok; t++) calib_ok = calibrateGyroscope();
    if (!calib_ok) Serial.println("[CALIB GAGAL] Offset nol dipakai. Data sesi ini JANGAN dipakai untuk melatih model.");
  } else {
    Serial.println("[!] GAGAL: BMI160 tidak merespon di 0x68.");
  }

  // 4. Inisialisasi Sensor Optik MAX30105 (0x57)
  Wire.beginTransmission(MAX30105_ADDR);
  if (Wire.endTransmission() == 0) {
    if (particleSensor.begin(Wire, I2C_SPEED_STANDARD)) {
      max30105_connected = true;
      byte ledBrightness = 30; // Red/IR: sebelumnya 65 membuat IR DC ~235k (mepet saturasi 262k)
      byte sampleAverage = 4;
      byte ledMode = use_green ? 3 : 2; // 3 = Red + IR + Hijau
      int sampleRate = 200;
      int pulseWidth = 411;
      int adcRange = 4096;
      particleSensor.setup(ledBrightness, sampleAverage, ledMode, sampleRate, pulseWidth, adcRange);
      if (use_green) particleSensor.setPulseAmplitudeGreen(50); // tune dengan 'C' (target DC hijau ~50-150k)
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

  // 4b. Inisialisasi Sensor Suhu Medis MLX90614 (0x5A)
  Wire.beginTransmission(MLX90614_ADDR);
  if (Wire.endTransmission() == 0) {
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

  Wire.setClock(100000);

  // 5. Inisialisasi SPI Hardware & LoRa SX1278
  SPI.begin();
  LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);
  LoRa.setSPIFrequency(1E6);

  Serial.println("Menghubungkan ke modul LoRa SX1278...");
  int attempts = 0;
  while (!LoRa.begin(433E6)) {
    attempts++;
    Serial.print("[Mencoba Ke-"); Serial.print(attempts);
    Serial.println("] Gagal deteksi LoRa. Cek kabel SPI...");
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
  Serial.println("-----------------------------------------\n");

  IWatchdog.begin(4000000); // Hardware Watchdog 4 detik (Auto-Reboot jika macet)
}

// ==========================================
// LOOP UTAMA NON-BLOCKING
// ==========================================
void loop() {
  IWatchdog.reload(); // Reset watchdog tiap siklus agar tidak reboot

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
      Serial.print(" | Red DC : "); Serial.println(red_dc_est, 0);
      Serial.print(" P-P IR  : "); Serial.print(ir_ac_max - ir_ac_min, 1);
      Serial.print(" | Rasio R: "); Serial.println(current_r_ratio, 3);
      Serial.print(" SpO2 Cal: "); Serial.print(filtered_spo2, 1);
      Serial.print("% (Display: "); Serial.print(current_spo2); Serial.println("%)");
      Serial.print(" Tolak: p2p="); Serial.print(rej_p2p); Serial.print(" PI="); Serial.print(rej_pi); Serial.print(" interval="); Serial.print(rej_range); Serial.print(" tak-konsisten="); Serial.print(rej_inc); Serial.print(" MAR="); Serial.print(rej_mar); Serial.print(" | denyut OK="); Serial.println(beats_ok);
      Serial.print(" PI: "); Serial.print(last_pi_pct, 2); Serial.println("%");
      Serial.print(" Status  : "); Serial.println(is_worn ? "JARI TERPASANG (OK)" : "MEJA / LEPAS");
      Serial.println("----------------------------------------------\n");
    } else if (cmd == 'r' || cmd == 'R') {
      fall_state = STATE_NORMAL;
      red_streak = 0;
      sim_asphyxia_gas = false;
      Serial.println("\n>>> [RESET] Status Direset ke Normal. <<<");
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
        // Modul tanpa LED hijau (mis. MAX30102 berlabel MAX30105) membaca ~0-100: otomatis balik ke IR
        if (grnVal < 3000 && irVal > 10000) { if (++green_dead_cnt >= 100) { use_green = false; hr_dc_est = 0; hr_ac_curr = 0; hr_ac_prev = 0; resetHrHistory(); Serial.println("\n[INFO] Kanal hijau tidak ada sinyal -> HR dari IR."); } }
        else green_dead_cnt = 0;
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

    // 0. Baca Suhu Tubuh Real-time dari Sensor Medis MLX90614 (Objek Kulit)
    if (mlx_connected) {
      static unsigned long last_mlx_read = 0;
      if (millis() - last_mlx_read >= 500) { // Update tiap 500 ms agar I2C ringan
        last_mlx_read = millis();
        float raw_obj = mlx.readObjectTempC();
        if (!isnan(raw_obj) && raw_obj > 20.0f && raw_obj < 50.0f) {
          // Low-pass filter suhu tubuh agar stabil
          temp_c = 0.3f * raw_obj + 0.7f * temp_c;
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

    int display_spo2 = current_spo2;
    if (sim_asphyxia_gas) {
      display_spo2 = 84; // Simulasi gas beracun: SpO2 drop < 88% -> Memicu Triage MERAH!
    }  // display_spo2 == 0 berarti belum terukur (tampil '--'), BUKAN 98

    // 6. Evaluasi Prediksi TinyML Decision Tree
    int model_pred = predict_triage(a_total, g_total, a_max, a_min, g_mean, a_std, g_max, a_jerk);

    // 7. Evaluasi Multi-Modal Clinical Triage (TinyML + FSM Pasca-Jatuh + True PPG + Suhu MLX)
    int triage_pred = evaluate_clinical_triage(is_worn, model_pred, a_total, g_total, a_max, g_mean, current_hr, display_spo2, temp_c);

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
    if (current_hr > 0) {
      Serial.print(current_hr); Serial.print("bpm");
    } else if (is_worn) {
      Serial.print("Mengukur...");
    } else {
      Serial.print("0bpm");
    }
    Serial.print(" | SpO2: "); if (display_spo2 > 0) { Serial.print(display_spo2); Serial.print("%"); } else Serial.print("--");
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

    // 10. Render Layar OLED Jam Tangan (128x64) - Refresh 1 Hz atau saat triage berubah
    static unsigned long lastOled = 0;
    static int lastTriage = -1;
    if (triage_pred != lastTriage || millis() - lastOled >= 1000) {
      lastOled = millis();
      lastTriage = triage_pred;
      renderOLED(triage_pred, is_worn, a_total, g_total, a_max, current_hr, display_spo2, temp_c);
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
    payload += String(current_hr) + ",";
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
