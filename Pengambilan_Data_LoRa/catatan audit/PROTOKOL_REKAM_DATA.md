# Protokol Perekaman Data Triage (Rescue-Tag, firmware 50 Hz)

Tujuan: data yang cukup dan bersih agar evaluasi per sesi bisa dipertanggungjawabkan.
Target minimal: **20-30 kejadian jatuh**, **>= 8 sesi Diam**, **>= 10 sesi Kerja**.

## Sebelum mulai (tiap kali boot)
- [ ] Taruh jam diam di meja saat boot sampai muncul `[CALIB OK]`. Kalau `[CALIB GAGAL]`, reset dan ulangi; **jangan pakai data sesi itu**.
- [ ] Jam dipakai di pergelangan seperti saat dipakai sebenarnya (strap pas).
- [ ] Catat tanggal, orang, dan tangan yang dipakai di lembar catatan di bawah.

## Cara merekam satu sesi
1. Tekan `n` untuk membuat sesi baru, lalu tekan label: `0` Diam, `1` Kerja, `3` Jatuh.
2. Lakukan SATU aktivitas saja selama 20-40 detik. Jangan ganti aktivitas di tengah sesi (pisahkan dengan `n`).
3. Untuk sesi Jatuh: satu sesi = satu jatuh. Mulai dengan berdiri diam 3 detik, jatuh, lalu diam di kasur 5 detik. Boleh tetap berlabel `3`; skrip akan memakai jendela benturannya saja.
4. Jatuh hanya ke kasur/matras tebal. Jangan ke lantai keras.

## Daftar sesi yang diminta

### Diam (label 0) - minimal 8 sesi
| # | Aktivitas | Durasi | Catatan |
|---|---|---|---|
| D1 | Duduk, tangan di paha | 30 s | |
| D2 | Duduk, tangan di meja, mengetik | 30 s | |
| D3 | Berdiri diam | 30 s | |
| D4 | Berbaring telentang | 30 s | |
| D5 | Berbaring miring | 30 s | |
| D6 | Jam dipegang diam di tangan | 20 s | |
| D7 | Duduk di kendaraan/kursi goyang (getaran halus) | 30 s | opsional |
| D8 | Duduk, tangan dilipat di dada | 30 s | |

### Kerja (label 1) - minimal 10 sesi, termasuk negatif sulit
| # | Aktivitas | Durasi | Catatan |
|---|---|---|---|
| K1 | Berjalan santai | 30 s | |
| K2 | Berjalan cepat | 30 s | |
| K3 | Berlari kecil di tempat | 20 s | |
| K4 | Mengangkat dan memindah barang | 30 s | |
| K5 | Menggerakkan palu/alat (ayun tangan) | 30 s | |
| K6 | Memukul meja dengan tangan | 20 s | **negatif sulit**, jangan salah dilabeli Jatuh |
| K7 | Melompat | 20 s | **negatif sulit** |
| K8 | Duduk lalu berdiri berulang | 30 s | |
| K9 | Tersandung lalu pulih (tanpa jatuh) | 5-10 kali | **negatif sulit** |
| K10 | Meletakkan jam/tangan dengan kasar ke meja | 15 s | **negatif sulit** |
| K11 | Naik turun tangga | 30 s | |
| K12 | Membungkuk mengambil barang | 30 s | |

### Jatuh (label 3) - minimal 20 sesi (satu jatuh per sesi)
Ulangi di ke-4 arah dan variasi tangan, masing-masing >= 3 kali:
| Arah | Tangan menahan | Tangan tidak menahan |
|---|---|---|
| Depan | J1-J3 | J4-J6 |
| Belakang | J7-J9 | J10-J12 |
| Samping kiri | J13-J15 | |
| Samping kanan | J16-J18 | |
| Lemas/merosot dari berdiri | J19-J20 | |

## Lembar catatan sesi
| Sesi (nomor dari `n`) | Kode (D1/K6/J4...) | Label | Calib OK? | Catatan |
|---|---|---|---|---|
| | | | | |

## Setelah merekam
```
python3 train_triage_loso.py log1.txt log2.txt ... --out triage_model.h
```
Laporkan angka dari `laporan_evaluasi.md` (bagian LOSO dan kejadian jatuh), bukan akurasi di data latih.

## Kriteria lolos
- Recall Merah tingkat kejadian >= 90%.
- Jendela non-jatuh yang salah-Merah mendekati 0 per sesi, terutama pada sesi Kerja negatif sulit.
- Akurasi per jendela >= 90% (LOSO) dan recall Kuning dilaporkan terpisah.
- Tree lebih baik dari baseline `a_max >= 2.2 g`, atau perannya dijelaskan sebagai penyaring false alarm.
