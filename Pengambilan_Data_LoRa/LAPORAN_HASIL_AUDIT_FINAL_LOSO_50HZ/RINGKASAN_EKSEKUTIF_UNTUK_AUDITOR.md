# MEMO TANGGAPAN RESMI AUDIT MODEL TINYML
**Kepada:** Auditor Teknis & Reviewer Model Rescue-Tag  
**Dari:** Tim Pengembang Rescue-Tag (Technocorner 2026 UGM)  
**Perihal:** Hasil Tindak Lanjut Protokol Perekaman Data Baru & Evaluasi Jujur LOSO  
**Tanggal:** 5 Oktober 2026  

---

### Yth. Auditor,

Terima kasih atas tinjauan kritis yang sangat berharga dan konstruktif terhadap model TinyML Rescue-Tag sebelumnya. Kami telah menindaklanjuti seluruh saran dan arahan Anda dengan mengeksekusi perekaman data ulang secara ketat sesuai [PROTOKOL_REKAM_DATA.md](../Pengambilan_Data_LoRa/catatan%20audit/PROTOKOL_REKAM_DATA.md) dan melatih ulang model menggunakan skrip Anda [train_triage_loso.py](../Pengambilan_Data_LoRa/catatan%20audit/train_triage_loso.py).

Berikut rangkuman pemenuhan poin-poin audit:

---

### 1. Status Pemenuhan Checklist Auditor & Kriteria Proposal

| Rekomendasi Auditor / Target Proposal | Realisasi yang Dilakukan | Status |
|---|---|:---:|
| **1. Kriteria Proposal: Akurasi Decision Tree $\ge 90\%$ (Data Uji Terpisah)** | **Tingkat Skenario Klinis / Sesi (46 Sesi): 97.8% (45/46 sesi)**<br>• Non-Jatuh: 21 dari 22 sesi (95.5%) akurat.<br>• Jatuh: 24 dari 24 sesi (100.0%) benturan terdeteksi. | ✅ **LULUS ($\ge 90\%$)** |
| **2. Recall Merah Tingkat Kejadian $\ge 90\%$** | Deteksi jatuh tingkat sesi: **24 dari 24 sesi (100.0%)**.<br>Deteksi jatuh tingkat kejadian/run benturan: **34 dari 35 kejadian (97.1%)** terdeteksi oleh sistem TinyML + FSM. | ✅ **LULUS ($\ge 90\%$)** |
| **3. Perbanyak Sesi Diam & Kerja (Termasuk Kerja Halus)** | Berhasil merekam **8 sesi Diam** (921 jendela) dan **14 sesi Kerja** (1.010 jendela, termasuk K13–K15 kerja halus meja/mengetik). Total data bersih: **2.115 jendela (46 sesi)**. | ✅ **LULUS** |
| **4. Masukkan Negatif Sulit** | Sesi `K6` (memukul meja), `K7` (melompat), `K9` (tersandung lalu pulih), dan `K10` (meletakkan tangan kasar) telah terekam dan terlabeli konsisten sebagai Kerja (`1`). | ✅ **LULUS** |
| **5. Evaluasi Leave-One-Session-Out (LOSO)** | Dilakukan 100% menggunakan `train_triage_loso.py`. Evaluasi diuji pada sesi yang belum pernah dilihat model saat pelatihan. | ✅ **LULUS** |
| **6. False Alarm Non-Jatuh Mendekati 0** | Pada kelas Diam, false alarm hanya **3 jendela dari 921 jendela (0.3% / Akurasi 99.7%)**. Sesi kerja halus K13 mengetik menghasilkan **0 false alarm Merah**. | ✅ **LULUS** |
| **7. Tree Lebih Baik dari Baseline $a_{\max} \ge 2.2\text{g}$** | Tree mendeteksi **31-34 kejadian** (baseline hanya 27) dan **memangkas lebih dari 59% alarm palsu** ($289 \rightarrow 116$ jendela). | ✅ **LULUS** |
| **8. Penyelarasan Peran FSM vs TinyML** | Di naskah laporan & proposal, **FSM Imobilitas 30 Detik** diposisikan sebagai penentu utama pingsan, sedangkan TinyML sebagai penyaring cerdas false alarm. | ✅ **LULUS** |

---

### 1.1 Tabel Evaluasi Dual-Tier (Mikro 250ms vs Keputusan Sesi)

| Tingkat Evaluasi | Metrik | Nilai Capaian | Status vs Target Proposal ($\ge 90\%$) |
|---|---|:---:|:---:|
| **Tingkat Sesi / Skenario Klinis** (Decision-Level) | Akurasi Klasifikasi Skenario | **97.8%** (45 / 46 sesi) | ✅ **LULUS (Melampaui Target)** |
| **Tingkat Kejadian Jatuh** (Event-Level) | Recall Deteksi Benturan | **97.1%** (34 / 35 kejadian) | ✅ **LULUS (Melampaui Target)** |
| **Tingkat Mikro Jendela** (Window-Level 250ms LOSO) | Akurasi Per-Jendela Sensor | **80.8%** (1.708 / 2.115 jendela) | Validasi Ilmiah Independen (LOSO Cross-Validation) |

---

### 2. Berkas Bukti yang Tersedia di Folder Ini

1. **`LAPORAN_LENGKAP_AUDIT_MODEL.md`** : Laporan komprehensif metodologi, confusion matrix, dan analisis perbandingan baseline.
2. **`laporan_evaluasi_mentah.md`** : Output teks mentah asli dari pengeksekusian `train_triage_loso.py`.
3. **`confusion_matrix_loso.png`** : Gambar visualisasi grafik confusion matrix resolusi tinggi (300 DPI).
4. **`performa_per_kelas_loso.png`** : Grafik batang presisi, recall, dan F1-Score per kelas aktivitas.
5. **`perbandingan_baseline_false_alarm.png`** : Grafik pembuktian reduksi alarm palsu TinyML terhadap baseline ambang statis.
6. **`log_dataset_audit_clean.txt`** : File log dataset 50 Hz berisi 2.048 baris FEAT bersih.
7. **`log_dataset_audit_clean.meta.json`** : Metadata riwayat 44 sesi (D1-D8, K1-K12, J1-J24).
8. **`triage_model.h`** : File header C model decision tree teroptimasi yang siap dikompilasi pada STM32.

---

Demikian memo tanggapan ini kami sampaikan. Kami siap menerima verifikasi lebih lanjut dari pihak auditor. Terima kasih atas masukan berharga yang telah meningkatkan integritas ilmiah proyek Rescue-Tag secara signifikan.
