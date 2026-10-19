# Evaluasi model triage (leave-one-session-out)

## 1. Profil data

- Total jendela (250 ms): **2048** dari **44 sesi** (8.5 menit)
- Jendela Jatuh asli (label 3): 513; setelah hanya jendela benturan (a_max >= 1.6 g): **184** | diubah jadi Diam: 329 (fase diam pascajatuh, ditangani FSM)

| Kelas | Jendela | Sesi |
|---|---:|---:|
| Diam (Hijau) | 921 | 32 |
| Kerja (Kuning) | 943 | 12 |
| Jatuh (Merah) | 184 | 24 |

- **Kejadian jatuh terpisah: 35** (run jendela Jatuh berurutan)

### Peringatan kualitas data

- Sesi 7 (label [0]) punya a_max 2.7 g (setara benturan) - pastikan label benar.
- Sesi 9 (label [1]) punya a_max 2.4 g (setara benturan) - pastikan label benar.
- Sesi 10 (label [1]) punya a_max 2.2 g (setara benturan) - pastikan label benar.
- Sesi 11 (label [1]) punya a_max 3.1 g (setara benturan) - pastikan label benar.
- Sesi 12 (label [1]) punya a_max 2.4 g (setara benturan) - pastikan label benar.
- Sesi 13 (label [1]) punya a_max 5.3 g (setara benturan) - pastikan label benar.
- Sesi 14 (label [1]) punya a_max 4.1 g (setara benturan) - pastikan label benar.
- Sesi 15 (label [1]) punya a_max 5.6 g (setara benturan) - pastikan label benar.
- Sesi 17 (label [1]) punya a_max 3.7 g (setara benturan) - pastikan label benar.
- Sesi 18 (label [1]) punya a_max 10.5 g (setara benturan) - pastikan label benar.
- Sesi 19 (label [1]) punya a_max 3.4 g (setara benturan) - pastikan label benar.
- Sesi 20 (label [1]) punya a_max 2.8 g (setara benturan) - pastikan label benar.
- Sesi 28 sangat pendek (9 jendela).
- Sesi 43 sangat pendek (9 jendela).

## 2. Pemilihan hiperparameter (LOSO)

| Kedalaman | min leaf | Macro-F1 | Kejadian jatuh terdeteksi | Jendela salah-Merah |
|---:|---:|---:|---:|---:|
| 4 | 1 | 76.4% | 31/35 | 116 |
| 4 | 3 | 76.5% | 31/35 | 116 | **<- dipilih**
| 4 | 5 | 76.5% | 31/35 | 116 |

*Catatan: hiperparameter dipilih dari hasil LOSO yang sama, jadi angka terbaik sedikit optimistis; perlu data uji sesi baru untuk angka final.*

## 3. Hasil leave-one-session-out (data uji = sesi yang tidak dilatih)

- Akurasi per jendela: **81.0%**
- Macro-F1: **76.5%**

| Kelas | Jumlah jendela | Presisi | Recall | F1 |
|---|---:|---:|---:|---:|
| Diam (Hijau) | 921 | 88.6% | 86.0% | 87.3% |
| Kerja (Kuning) | 943 | 81.0% | 77.3% | 79.1% |
| Jatuh (Merah) | 184 | 54.3% | 75.0% | 63.0% |

Confusion matrix:

| Aktual \ Prediksi | Diam | Kerja | Jatuh |
|---|---:|---:|---:|
| Diam (Hijau) | 792 | 126 | 3 |
| Kerja (Kuning) | 101 | 729 | 113 |
| Jatuh (Merah) | 1 | 45 | 138 |

- **Recall Merah tingkat kejadian: 31/35** (89%)
- Jendela non-jatuh yang salah diprediksi Merah: **116** dari 1864 (~14.9 per menit data non-jatuh)

Per sesi (LOSO):

| Sesi | Label | Jendela | Akurasi | Pred Merah (benar/salah) |
|---:|---|---:|---:|---|
| 1 | [0] | 123 | 71% | 0/1 |
| 2 | [0] | 60 | 100% | 0/0 |
| 3 | [0] | 62 | 100% | 0/0 |
| 4 | [0] | 61 | 100% | 0/0 |
| 5 | [0] | 122 | 96% | 0/0 |
| 6 | [0] | 41 | 85% | 0/0 |
| 7 | [0] | 60 | 70% | 0/0 |
| 8 | [0] | 63 | 68% | 0/2 |
| 9 | [1] | 63 | 97% | 0/1 |
| 10 | [1] | 62 | 95% | 0/1 |
| 11 | [1] | 81 | 96% | 0/2 |
| 12 | [1] | 63 | 86% | 0/5 |
| 13 | [1] | 126 | 69% | 0/37 |
| 14 | [1] | 41 | 93% | 0/2 |
| 15 | [1] | 126 | 64% | 0/22 |
| 16 | [1] | 63 | 48% | 0/0 |
| 17 | [1] | 65 | 94% | 0/4 |
| 18 | [1] | 62 | 48% | 0/23 |
| 19 | [1] | 128 | 77% | 0/11 |
| 20 | [1] | 63 | 81% | 0/5 |
| 21 | [3] | 48 | 71% | 12/0 |
| 22 | [3] | 23 | 96% | 5/0 |
| 23 | [3] | 22 | 95% | 9/0 |
| 24 | [3] | 24 | 75% | 3/0 |
| 25 | [3] | 14 | 79% | 3/0 |
| 27 | [3] | 24 | 92% | 10/0 |
| 28 | [3] | 9 | 44% | 3/0 |
| 33 | [3] | 23 | 91% | 9/0 |
| 34 | [3] | 23 | 78% | 6/0 |
| 35 | [3] | 23 | 78% | 7/0 |
| 36 | [3] | 22 | 73% | 5/0 |
| 37 | [3] | 22 | 82% | 4/0 |
| 38 | [3] | 23 | 78% | 5/0 |
| 39 | [3] | 23 | 91% | 8/0 |
| 40 | [3] | 22 | 100% | 9/0 |
| 41 | [3] | 15 | 100% | 5/0 |
| 42 | [3] | 16 | 75% | 2/0 |
| 43 | [3] | 9 | 100% | 5/0 |
| 44 | [3] | 14 | 100% | 5/0 |
| 45 | [3] | 23 | 91% | 5/0 |
| 46 | [3] | 22 | 77% | 3/0 |
| 47 | [3] | 23 | 83% | 5/0 |
| 48 | [3] | 23 | 78% | 5/0 |
| 49 | [3] | 23 | 61% | 5/0 |

## 4. Baseline aturan sederhana (a_max >= 2.2 g -> Merah, selain itu Diam)

- Kejadian jatuh terdeteksi: 27/35; jendela non-jatuh salah-Merah: 286
- Jika tree tidak lebih baik dari baseline pada kedua angka ini, jelaskan peran tree sebagai penyaring false alarm/pembeda Kerja vs Diam, dan andalkan FSM untuk keputusan Merah.

## 5. Model akhir (dilatih pada SEMUA sesi)

- Kedalaman 4, min leaf 3, bobot Merah 5.0
- Akurasi di data latih: 84.6%  *(hanya pembanding; JANGAN dilaporkan sebagai akurasi model)*
- Header ditulis ke `Pengambilan_Data_LoRa/stm32_transmitter/triage_model.h`