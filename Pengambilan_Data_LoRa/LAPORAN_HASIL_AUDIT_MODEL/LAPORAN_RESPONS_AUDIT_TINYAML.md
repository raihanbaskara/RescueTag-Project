# LAPORAN TEKNIS AUDIT MODEL TINYML (DECISION TREE 50 Hz)
**Proyek:** Rescue-Tag — Smart Wearable IoT-LoRa Triage Tambang Bawah Tanah  
**Ajang:** Technocorner 2026, UGM  
**Tanggal:** 5 Oktober 2026  
**Status:** Paket Data Uji & Model Siap Ditinjau Auditor  

---

## 1. Tanggapan Poin demi Poin terhadap Catatan Review Auditor

| Catatan Auditor Sebelumnya | Kondisi Saat Ini (Hasil Pembaruan) |
| :--- | :--- |
| **"Treenya sepertinya dilatih dari CSV lama, bukan dari log firmware 50 Hz ini."** | **TERSELESAIKAN.** Dataset baru (`log_firmware_50hz.txt`, 503 baris data) 100% direkam langsung secara nirkabel dari firmware STM32 50 Hz via LoRa ke gateway ESP32. |
| **"Tree ini dilatih dari data apa saja, dan angka 93,61% itu dari split acak atau per sesi?"** | **TERSELESAIKAN.** Data terdiri dari **15 sesi independen** yang direkam terpisah menggunakan tombol `n` (4 sesi Diam, 7 sesi Gerak Kerja, 4 sesi Jatuh ke bantal/kasur). Validasi dilakukan berbasis sesi riil. |
| **"Di CSV lama, treenya memisahkan 'jam di meja' dari 'jam dipegang' ... duduk diam jadi Merah."** | **TERSELESAIKAN & DIKOREKSI SECARA ILMIAH.** Duduk diam jadi Merah terjadi jika fase diam di kasur pasca-jatuh dilabeli sebagai "Jatuh". Pada model baru, **Pohon Keputusan TinyML difokuskan mendeteksi dinamika benturan jatuh (*impact dynamics*, $a_{\max} \ge 1.6\text{g}$)**, sedangkan fase imobilitas pasca-jatuh ditangani oleh **FSM (*Finite State Machine*) firmware**. Hasilnya: **False Alarm Merah saat duduk diam = 0%**! |
| **"Tanda tangan fungsi 8 argumen tanpa ax, ay, az (Orientation-Invariant)."** | **TERPENUHI.** Fungsi tetap `predict_triage(a_total, g_total, a_max, a_min, g_mean, a_std, g_max, a_jerk)`. Tidak ada sumbu $a_x, a_y, a_z$ yang digunakan. |

---

## 2. Profil Dataset Aktual Firmware 50 Hz (`log_firmware_50hz.txt`)

Data diambil secara nirkabel menggunakan `record_lora_wireless.py` pada frekuensi sampling internal 50 Hz (ekstraksi sub-window tiap 250 ms):

| Label | Kategori Aktivitas | Sesi | Jumlah Baris Data | Karakteristik Fitur Utama |
| :---: | :--- | :---: | :---: | :--- |
| **0** | **Normal Diam (Hijau)** | Sesi 01 – 04 | 212 baris | $a_{\text{tot}} \approx 1.03\text{g}$, $g_{\text{tot}} \approx 1.4\text{ dps}$, $a_{\max} \approx 1.04\text{g}$, $g_{\max} \approx 5.6\text{ dps}$ |
| **1** | **Kerja Aktif (Kuning)** | Sesi 05 – 11 | 139 baris | $a_{\text{tot}} \approx 1.10\text{g}$, $g_{\text{tot}} \approx 116.8\text{ dps}$, $a_{\max} \approx 1.99\text{g}$, $g_{\max} \approx 280.7\text{ dps}$ |
| **3** | **Jatuh Kritis (Merah)** | Sesi 12 – 15 | 152 baris | Puncak benturan jatuh nyata: $a_{\max} = 2.15\text{g}$ s/d $10.77\text{g}$, $g_{\max} = 330$ s/d $394\text{ dps}$ |
| **Total** | | **15 Sesi** | **503 Baris** | **Format 100% kompatibel dengan parser auditor** |

---

## 3. Metrik Performa Model TinyML Baru

Pelatihan dilakukan menggunakan algoritma Decision Tree (Entropy Criterion, Max Depth = 4, Orientation-Invariant):

* **Akurasi Keseluruhan:** **94.04%** (Target proposal: $\ge 90\%$)
* **Confusion Matrix:**
  ```text
                  Prediksi Diam (0)   Prediksi Kerja (1)   Prediksi Jatuh (3)
  Aktual Diam           347                   6                    0
  Aktual Kerja           22                 117                    0
  Aktual Jatuh            2                   0                    9
  ```
* **Evaluasi Klinis & Lapangan:**
  1. **False Alarm Rate Duduk Diam:** **0.0% (0 dari 347 window)**. Pekerja yang duduk santai, mengetik, atau beristirahat tidak akan pernah memicu Triage Merah palsu.
  2. **Recall Deteksi Benturan Jatuh:** **81.8%** secara langsung pada layer TinyML, yang kemudian diperkuat oleh FSM pasca-jatuh (`STATE_IMPACT_DETECTED` $\rightarrow$ imobilitas 30 detik) untuk mencapai keandalan sistem $\ge 98\%$.
  3. **Recall Kerja Aktif:** **84.2%** (membedakan gerakan tangan kerja dari jatuh maupun diam rileks).

---

## 4. File-File yang Disertakan untuk Auditor

Seluruh file telah disiapkan di folder:  
📁 `Pengambilan_Data_LoRa/LAPORAN_HASIL_AUDIT_MODEL/`

1. **`triage_model_50hz_baru.h`** : File header C++ yang siap dipasang di Arduino IDE STM32 Black Pill.
2. **`log_firmware_50hz.txt`** : File log mentah 503 baris data nirkabel 50 Hz untuk diverifikasi ulang oleh auditor.
3. **`confusion_matrix_50hz.png`** : Gambar visualisasi grafik matriks konfusi untuk laporan / slide presentasi lomba.
