import serial
import serial.tools.list_ports
import csv
import time
import sys
import msvcrt

def find_esp32_port():
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        return None
    for p in ports:
        desc = p.description.lower()
        if "cp210" in desc or "ch340" in desc or "usb" in desc or "serial" in desc:
            return p.device
    return ports[0].device

def main():
    print("=" * 65)
    print("   RESCUE-TAG INTERACTIVE WIRELESS DATA LOGGER (LORA TO CSV)")
    print("        Pengambilan Data Bersih & Akurat (Bebas Salah Label) ")
    print("=" * 65)

    port = find_esp32_port()
    if not port:
        print("[!] Tidak ada port COM terdeteksi otomatis.")
        port = input("Ketik nama port ESP32 Gateway manual (misal COM3): ").strip()
    else:
        print(f"[*] Port ESP32 Gateway terdeteksi: {port}")

    baud_rate = 115200
    output_file = "dataset_triage_clean_v2.csv"

    print(f"[*] Menghubungkan ke {port} @ {baud_rate} baud...")
    try:
        ser = serial.Serial(port, baud_rate, timeout=1)
        time.sleep(2)
        print(f"[OK] Berhasil terhubung ke ESP32 Gateway!")
    except Exception as e:
        print(f"[ERROR] Gagal membuka port {port}: {e}")
        sys.exit(1)

    print("\n" + "=" * 65)
    print("PANDUAN PENGAMBILAN DATA BERSIH (KONTROL KEYBOARD REAL-TIME):")
    print("  [0] : Set Label 0 -> NORMAL_DIAM  (Duduk/diam santai di tangan)")
    print("  [1] : Set Label 1 -> KERJA_AKTIF  (Mengayun tangan / saat mengangkat jam)")
    print("  [3] : Set Label 3 -> JATUH_KRITIS (HANYA saat jam mendarat & tergeletak diam)")
    print("  [x] : JEDA / SKIP (Abaikan data transisi agar tidak mengotori dataset)")
    print("  [q] : SELESAI & SIMPAN DATASET")
    print("=" * 65)
    print("Tips: Saat simulasi jatuh:")
    print("  1. Tekan '1' atau 'x' saat mengangkat jam ke atas.")
    print("  2. Jatuhkan jam ke bantal.")
    print("  3. Begitu jam mendarat diam di bantal, tekan '3' selama 5-10 detik.")
    print("  4. Sebelum mengambil jam lagi, tekan 'x' atau '1'.")
    print("=" * 65 + "\n")

    current_label = 0
    class_names = {0: "Normal_Diam", 1: "Kerja_Aktif", 3: "Jatuh_Kritis"}
    is_paused = False

    counts = {0: 0, 1: 0, 3: 0}
    total_saved = 0

    with open(output_file, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'ax', 'ay', 'az', 'gx', 'gy', 'gz', 'hr', 'spo2', 'temp', 'rssi', 'label', 'class_name'])

        try:
            while True:
                # Cek input keyboard tanpa blocking
                if msvcrt.kbhit():
                    key = msvcrt.getch().decode('utf-8', errors='ignore').lower()
                    if key == '0':
                        current_label = 0
                        is_paused = False
                        print(f"\n>>> [LABEL AKTIF] 0 : NORMAL_DIAM (Duduk/Diam Santai) <<<")
                    elif key == '1':
                        current_label = 1
                        is_paused = False
                        print(f"\n>>> [LABEL AKTIF] 1 : KERJA_AKTIF (Ayun Tangan / Angkat Jam) <<<")
                    elif key == '3':
                        current_label = 3
                        is_paused = False
                        print(f"\n>>> [LABEL AKTIF] 3 : JATUH_KRITIS (Tergeletak Diam di Bantal) <<<")
                    elif key == 'x':
                        is_paused = True
                        print(f"\n>>> [JEDA / SKIP] Data saat ini TIDAK disimpan ke CSV <<<")
                    elif key == 'q':
                        print("\n[INFO] Tombol 'q' ditekan. Mengakhiri sesi perekaman...")
                        break

                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line and not line.startswith("ESP") and not line.startswith("HEADER") and not line.startswith("ERROR"):
                    parts = [p.strip() for p in line.split(',') if p.strip()]
                    # Format yang diharapkan dari ESP32 Gateway:
                    # ax, ay, az, gx, gy, gz, hr, spo2, temp, triage, rssi (total 11 elemen)
                    if len(parts) >= 7:
                        try:
                            ax = float(parts[0])
                            ay = float(parts[1])
                            az = float(parts[2])
                            gx = float(parts[3])
                            gy = float(parts[4])
                            gz = float(parts[5])

                            hr = int(float(parts[6])) if len(parts) > 6 else 0
                            spo2 = int(float(parts[7])) if len(parts) > 7 else 0
                            temp = float(parts[8]) if len(parts) > 8 else 36.6
                            rssi = float(parts[-1]) if len(parts) > 10 else -70.0

                            g_tot = (gx**2 + gy**2 + gz**2)**0.5
                            a_tot = (ax**2 + ay**2 + az**2)**0.5

                            ts = round(time.time(), 3)

                            if not is_paused:
                                writer.writerow([ts, ax, ay, az, gx, gy, gz, hr, spo2, temp, rssi, current_label, class_names[current_label]])
                                f.flush()
                                counts[current_label] += 1
                                total_saved += 1
                                status_str = f"LABEL: [{current_label}] {class_names[current_label]:<13}"
                            else:
                                status_str = "[SKIP / DILEWATI]              "

                            print(f"[{total_saved:04d}] {status_str} | A_Tot:{a_tot:4.2f}g | G_Tot:{g_tot:5.1f}dps | (0:{counts[0]} | 1:{counts[1]} | 3:{counts[3]})")
                        except ValueError:
                            pass
        except KeyboardInterrupt:
            print("\n[INFO] Keyboard interrupt terdeteksi.")
        finally:
            ser.close()

    print("\n" + "=" * 65)
    print("HASIL AKHIR PENGAMBILAN DATASET:")
    print(f" File tersimpan   : '{output_file}'")
    print(f" Total baris data : {total_saved}")
    print(f" • Normal Diam    : {counts[0]} sampel")
    print(f" • Kerja Aktif    : {counts[1]} sampel")
    print(f" • Jatuh Kritis   : {counts[3]} sampel")
    print("=" * 65)

if __name__ == '__main__':
    main()
