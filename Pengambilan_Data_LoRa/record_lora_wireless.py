"""
=============================================================================
RESCUE-TAG: WIRELESS LORA 50Hz DATA LOGGER (ESP32 GATEWAY TO LOG FILE)
=============================================================================
Menangkap data 50 Hz secara nirkabel via LoRa 433 MHz dari jam tangan STM32.
Jam tangan bertenaga baterai di tangan, ESP32 Gateway tercolok di laptop.

Kontrol Keyboard Real-time:
  [0] : Set Label 0 -> NORMAL_DIAM  (Duduk/diam santai di pergelangan tangan)
  [1] : Set Label 1 -> KERJA_AKTIF  (Jalan mondar-mandir / ayun tangan / angkat barang)
  [3] : Set Label 3 -> JATUH_KRITIS (HANYA saat jam mendarat & tergeletak diam di bantal)
  [n] : Ganti ke SESI BARU (cur_session++)
  [x] : JEDA / SKIP (Abaikan data transisi, misal saat mengangkat jam kembali)
  [q] : SELESAI & SIMPAN LOG FILE

Format yang disimpan 100% kompatibel dengan train_triage_auditor.py:
  FEAT,sess,label,a_total,g_total,a_max,a_min,g_mean,a_std,g_max,ax,ay,az,model_pred,triage
=============================================================================
"""

import sys
import time
import msvcrt
import serial
import serial.tools.list_ports

OUTPUT_LOG_FILE = "log_firmware_50hz.txt"

def find_esp32_port():
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        return None
    for p in ports:
        desc = p.description.lower()
        if "cp210" in desc or "ch340" in desc or "usb" in desc or "serial" in desc or "uart" in desc:
            return p.device
    return ports[0].device

def main():
    print("=" * 70)
    print("   RESCUE-TAG: WIRELESS LORA DATA LOGGER (PENGAMBILAN DATA 50 Hz)")
    print("        Jam Tangan Wireless di Baterai  <--->  ESP32 di Laptop   ")
    print("=" * 70)

    port = find_esp32_port()
    if not port:
        print("[!] Port COM ESP32 tidak terdeteksi otomatis.")
        port = input("Ketik nama port COM ESP32 manual (misal COM3): ").strip()
    else:
        print(f"[*] Port ESP32 Gateway terdeteksi: {port}")

    baud_rate = 115200

    print(f"[*] Menghubungkan ke {port} @ {baud_rate} baud...")
    try:
        ser = serial.Serial(port, baud_rate, timeout=1)
        time.sleep(1.5)
        print(f"[OK] Berhasil terhubung ke ESP32 Gateway!")
    except Exception as e:
        print(f"[ERROR] Gagal membuka port {port}: {e}")
        print("Pastikan Serial Monitor Arduino IDE ditutup terlebih dahulu.")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("PANDUAN PROTOKOL PENGAMBILAN DATA (SESI AUDIT TEKNIK):")
    print("  1. Label [0] NORMAL DIAM : Rekam minimal 4 sesi (15-20s per sesi).")
    print("     - Sesi 1: Tangan di atas meja.")
    print("     - Tekan 'n' untuk ganti sesi -> Sesi 2: Tangan di paha.")
    print("     - Tekan 'n' -> Sesi 3: Berdiri diam rileks.")
    print("     - Tekan 'n' -> Sesi 4: Mengetik santai di keyboard.")
    print("  2. Label [1] KERJA AKTIF : Rekam minimal 4 sesi (15-20s per sesi).")
    print("     - Tekan '1' -> Sesi 5: Berjalan mondar-mandir.")
    print("     - Tekan 'n' -> Sesi 6: Mengayun tangan kerja aktif.")
    print("     - Tekan 'n' -> Sesi 7: Mengambil/mengangkat barang.")
    print("     - Tekan 'n' -> Sesi 8: Memutar pergelangan tangan.")
    print("  3. Label [3] JATUH KRITIS: Rekam minimal 4 sesi (10-15s per sesi).")
    print("     - Tekan 'x' saat mengangkat jam ke atas kasur/bantal.")
    print("     - Jatuhkan jam ke bantal.")
    print("     - Begitu jam mendarat diam, tekan '3' dan biarkan 10 detik.")
    print("     - Tekan 'n' tiap kali selesai 1 kali jatuh.")
    print("  4. Tekan 'q' jika sudah selesai semua sesi.")
    print("=" * 70 + "\n")

    cur_session = 1
    cur_label = 0
    class_names = {0: "Normal_Diam", 1: "Kerja_Aktif", 3: "Jatuh_Kritis"}
    is_paused = False

    counts = {0: 0, 1: 0, 3: 0}
    session_counts = {}
    total_saved = 0

    import os
    if os.path.exists(OUTPUT_LOG_FILE):
        with open(OUTPUT_LOG_FILE, 'r', errors='ignore') as f_old:
            for l in f_old:
                if l.startswith("FEAT,"):
                    p = l.strip().split(',')
                    if len(p) >= 3:
                        try:
                            s_id = int(p[1])
                            l_id = int(p[2])
                            counts[l_id] = counts.get(l_id, 0) + 1
                            session_counts[s_id] = session_counts.get(s_id, 0) + 1
                            total_saved += 1
                            if s_id >= cur_session:
                                cur_session = s_id + 1
                        except ValueError:
                            pass
        if total_saved > 0:
            print(f"[*] Melanjutkan file yang ada: '{OUTPUT_LOG_FILE}'")
            print(f"[*] Data tersimpan sebelumnya: {total_saved} baris (0:{counts[0]} | 1:{counts[1]} | 3:{counts[3]})")
            if counts[0] >= 50 and counts[1] >= 50 and counts[3] == 0:
                cur_label = 3
                is_paused = True
                print(f">>> [SIAP REKAM JATUH] Sesi {cur_session:02d} | Label: [3] Jatuh_Kritis (Mode JEDA AKTIF) <<<")
                print(">>> Siapkan jam di atas bantal/kasur, jatuhkan, lalu tekan tombol [3] di keyboard! <<<\n")
            else:
                print(f">>> [AKTIF] Melanjutkan ke Sesi {cur_session:02d} | Label: [{cur_label}] {class_names.get(cur_label, cur_label)} <<<\n")

    with open(OUTPUT_LOG_FILE, mode='a', encoding='utf-8') as f:
        print(f"[*] Merekam ke file: {OUTPUT_LOG_FILE}")
        if not (total_saved > 0 and counts[3] == 0):
            print(f">>> [AKTIF] Sesi {cur_session:02d} | Label: [{cur_label}] {class_names.get(cur_label, cur_label)} <<<\n")

        try:
            while True:
                # 1. Cek Input Keyboard Non-blocking
                if msvcrt.kbhit():
                    key = msvcrt.getch().decode('utf-8', errors='ignore').lower()
                    if key == '0':
                        cur_label = 0
                        is_paused = False
                        print(f"\n>>> [LABEL DIUBAH] -> [0] NORMAL_DIAM (Duduk/Diam Santai) <<<")
                    elif key == '1':
                        cur_label = 1
                        is_paused = False
                        print(f"\n>>> [LABEL DIUBAH] -> [1] KERJA_AKTIF (Ayun Tangan / Bergerak) <<<")
                    elif key == '3':
                        cur_label = 3
                        is_paused = False
                        print(f"\n>>> [LABEL DIUBAH] -> [3] JATUH_KRITIS (Tergeletak Diam di Bantal) <<<")
                    elif key == 'n':
                        cur_session += 1
                        print(f"\n>>> [SESI BARU] -> Sesi {cur_session:02d} Dimulai (Label: [{cur_label}] {class_names[cur_label]}) <<<")
                    elif key == 'x':
                        is_paused = not is_paused
                        state_str = "JEDA / SKIP (Data dibuang)" if is_paused else "RESUME (Merekam kembali)"
                        print(f"\n>>> [{state_str}] <<<")
                    elif key == 'q':
                        print("\n[INFO] Tombol 'q' ditekan. Menyimpan dan mengakhiri sesi...")
                        break

                # 2. Baca Baris LoRa dari ESP32 Gateway
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if not line:
                    continue

                # Cek apakah baris berupa paket FEAT dari LoRa STM32:
                # FEAT,a_total,g_total,a_max,a_min,g_mean,a_std,g_max,ax,ay,az,model_pred,triage_pred,hr,spo2,temp
                if line.startswith("FEAT,"):
                    parts = [p.strip() for p in line.split(',') if p.strip()]
                    if len(parts) >= 13:
                        try:
                            a_total = float(parts[1])
                            g_total = float(parts[2])
                            a_max   = float(parts[3])
                            a_min   = float(parts[4])
                            g_mean  = float(parts[5])
                            a_std   = float(parts[6])
                            g_max   = float(parts[7])
                            ax      = float(parts[8])
                            ay      = float(parts[9])
                            az      = float(parts[10])
                            model_pred  = int(parts[11])
                            triage_pred = int(parts[12])

                            hr   = int(parts[13]) if len(parts) > 13 else 0
                            spo2 = int(parts[14]) if len(parts) > 14 else 0

                            # Format C yang 100% kompatibel dengan train_triage_auditor.py:
                            # FEAT,sess,label,a_total,g_total,a_max,a_min,g_mean,a_std,g_max,ax,ay,az,model_pred,triage
                            clean_line = (f"FEAT,{cur_session},{cur_label},"
                                          f"{a_total:.4f},{g_total:.3f},"
                                          f"{a_max:.4f},{a_min:.4f},"
                                          f"{g_mean:.3f},{a_std:.4f},{g_max:.3f},"
                                          f"{ax:.4f},{ay:.4f},{az:.4f},"
                                          f"{model_pred},{triage_pred}\n")

                            if not is_paused:
                                f.write(clean_line)
                                f.flush()
                                counts[cur_label] += 1
                                session_counts[cur_session] = session_counts.get(cur_session, 0) + 1
                                total_saved += 1
                                status_txt = f"[{cur_label}] {class_names[cur_label]:<12}"
                            else:
                                status_txt = "[SKIP / DILEWATI] "

                            hr_str = f"{hr:3d}bpm" if hr > 0 else "Ukur..."
                            spo2_str = f"{spo2:2d}%" if spo2 > 0 else "--%"

                            print(f"[{total_saved:04d}] Sesi:{cur_session:02d} | {status_txt} | "
                                  f"A_Tot:{a_total:4.2f}g | A_Max:{a_max:4.2f}g | G_Tot:{g_total:5.1f}dps | "
                                  f"HR:{hr_str} | SpO2:{spo2_str} | (0:{counts[0]} | 1:{counts[1]} | 3:{counts[3]})")
                        except (ValueError, IndexError):
                            pass
                elif not line.startswith("HEADER") and not line.startswith("ESP"):
                    # Print log debug lainnya jika ada
                    pass

        except KeyboardInterrupt:
            print("\n[INFO] Dihentikan oleh pengguna (Ctrl+C).")
        finally:
            ser.close()

    print("\n" + "=" * 70)
    print("HASIL AKHIR PENGAMBILAN DATA NIRKABEL (50 Hz):")
    print(f" File tersimpan   : '{OUTPUT_LOG_FILE}'")
    print(f" Total baris data : {total_saved} window (~{total_saved * 0.25:.1f} detik rekaman)")
    print(f" • Label 0 (Normal Diam)  : {counts[0]} sampel")
    print(f" • Label 1 (Kerja Aktif)  : {counts[1]} sampel")
    print(f" • Label 3 (Jatuh Kritis) : {counts[3]} sampel")
    print(f" Total Sesi Unik          : {len(session_counts)} sesi")
    for s_id, s_cnt in sorted(session_counts.items()):
        print(f"   - Sesi {s_id:02d}: {s_cnt} window")
    print("=" * 70)
    print("\nLangkah Berikutnya:")
    print(f"  Jalankan pelatihan model auditor:")
    print(f"  > python train_triage_auditor.py {OUTPUT_LOG_FILE}")
    print("=" * 70 + "\n")

if __name__ == '__main__':
    main()
