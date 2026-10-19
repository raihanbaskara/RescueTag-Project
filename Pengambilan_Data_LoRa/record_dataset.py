import serial
import serial.tools.list_ports
import csv
import time
import sys

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
    print("=" * 60)
    print("    RESCUE-TAG WIRELESS DATA LOGGER (LORA to CSV)")
    print("=" * 60)

    port = find_esp32_port()
    if not port:
        print("[!] Tidak ada port COM terdeteksi!")
        port = input("Ketik nama port manual (misal COM3): ").strip()
    else:
        print(f"[*] Port terdeteksi otomatis: {port}")

    baud_rate = 115200
    output_file = "dataset_bmi160_raw.csv"

    print(f"[*] Menghubungkan ke {port} @ {baud_rate} baud...")
    try:
        ser = serial.Serial(port, baud_rate, timeout=2)
        time.sleep(2)
        print(f"[OK] Berhasil terhubung ke ESP32 Gateway!")
    except Exception as e:
        print(f"[ERROR] Gagal membuka port {port}: {e}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("PETUNJUK PENGAMBILAN DATA (BEBAS KABEL):")
    print("1. Menit ke-1: Jalan santai & duduk (Aktivitas Normal)")
    print("2. Menit ke-2: Ayunkan tangan seolah bekerja tambang (Kerja Aktif)")
    print("3. Menit ke-3: Jatuhkan jam ke bantal/kasur, lalu DIAMKAN 20-30 detik (Jatuh)")
    print("------------------------------------------------------------")
    print("Tekan [Ctrl + C] jika sudah selesai merekam data.")
    print("=" * 60 + "\n")

    row_count = 0
    with open(output_file, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'ax', 'ay', 'az', 'gx', 'gy', 'gz', 'rssi'])

        try:
            while True:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line and not line.startswith("ESP") and not line.startswith("HEADER") and not line.startswith("ERROR"):
                    parts = line.split(',')
                    # Format yang diharapkan: ax,ay,az,gx,gy,gz,rssi (total 7 bagian)
                    if len(parts) >= 6:
                        ts = round(time.time(), 3)
                        writer.writerow([ts] + parts)
                        row_count += 1
                        print(f"[{row_count:04d}] RX: {line}")
        except KeyboardInterrupt:
            print("\n" + "=" * 60)
            print(f"[SELESAI] Data logging dihentikan.")
            print(f"[FILE TERSIMPAN] Total {row_count} baris terekam di: '{output_file}'")
            print("=" * 60)
        finally:
            ser.close()

if __name__ == '__main__':
    main()
