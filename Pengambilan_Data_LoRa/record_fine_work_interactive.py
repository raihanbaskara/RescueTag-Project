"""
=============================================================================
RESCUE-TAG: PEREKAMAN KERJA HALUS INTERAKTIF (PERSIS SEPERTI KEMARIN)
=============================================================================
Kontrol Manual via Keyboard:
  - Tekan [Enter] untuk mulai tiap sesi saat kamu sudah siap.
  - Terdapat hitung mundur visual dan suara bip.
  - Sesi otomatis tersimpan ke dataset audit.
=============================================================================
"""

import sys
import os
import time
import serial
import serial.tools.list_ports

try:
    import winsound
    HAS_SOUND = True
except ImportError:
    HAS_SOUND = False

def beep(freq, dur):
    if HAS_SOUND:
        try:
            winsound.Beep(freq, dur)
        except Exception:
            pass

SESI_KERJA_HALUS = [
    {
        "code": "K13",
        "name": "Mengetik Keyboard Laptop Aktif",
        "label": 1,
        "duration": 30,
        "desc": "Ketik teks di keyboard laptop secara santai tapi aktif terus menerus."
    },
    {
        "code": "K14",
        "name": "Merakit Komponen / Menulis",
        "label": 1,
        "duration": 30,
        "desc": "Gerakkan tangan seperti merakit alat elektronik, pegang alat, atau menulis."
    },
    {
        "code": "K15",
        "name": "Menggerakkan Mouse & Kontrol Meja",
        "label": 1,
        "duration": 30,
        "desc": "Gerakkan mouse di meja, klik, scroll, atau tekan tombol perangkat kontrol."
    }
]

DATASET_FILE = "Pengambilan_Data_LoRa/log_dataset_audit_clean.txt"

def get_next_session_id():
    max_sess = 0
    if os.path.exists(DATASET_FILE):
        with open(DATASET_FILE, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if line.startswith("FEAT,"):
                    parts = line.split(",")
                    if len(parts) > 1:
                        try:
                            s = int(parts[1])
                            if s > max_sess:
                                max_sess = s
                        except ValueError:
                            pass
    return max_sess + 1

def find_serial_port():
    ports = [p.device for p in serial.tools.list_ports.comports()]
    if "COM14" in ports:
        return "COM14"
    if len(ports) > 0:
        return ports[0]
    return None

def main():
    os.system("cls" if os.name == "nt" else "clear")
    print("=" * 72)
    print("   RESCUE-TAG: PEREKAMAN KERJA HALUS (K13, K14, K15)")
    print("   Mode Interaktif - Kendali Penuh di Tangan Kamu")
    print("=" * 72)

    port = find_serial_port()
    if not port:
        print("[!] ERROR: Port COM tidak terdeteksi. Pastikan USB sudah tertancap!")
        input("\nTekan Enter untuk keluar...")
        sys.exit(1)

    print(f"[*] Menghubungkan ke port: {port} (115200 baud)...")
    try:
        ser = serial.Serial(port, 115200, timeout=1)
        time.sleep(1.5)
        ser.reset_input_buffer()
        print(f"[✓] Berhasil terhubung ke {port}!\n")
    except Exception as e:
        print(f"[!] Gagal membuka port {port}: {e}")
        print("    Pastikan Node-RED atau aplikasi Serial lain sudah DITUTUP.")
        input("\nTekan Enter untuk keluar...")
        sys.exit(1)

    next_sess_id = get_next_session_id()
    print(f"[*] Nomor sesi baru akan dimulai dari: Sesi #{next_sess_id}")
    print("[*] Total ada 3 sesi singkat (masing-masing 30 detik).\n")

    recorded_lines = []

    for idx, item in enumerate(SESI_KERJA_HALUS):
        current_sess = next_sess_id + idx
        print("=" * 72)
        print(f" SESI [{idx+1}/3] : {item['code']} - {item['name'].upper()}")
        print("=" * 72)
        print(f" Instruksi Gerakan : {item['desc']}")
        print(f" Target Durasi     : {item['duration']} detik")
        print(f" Label AI          : {item['label']} (KERJA)")
        print("-" * 72)
        
        input(" >>> Pasang posisi tanganmu, lalu TEKAN [ENTER] jika sudah siap... <<< ")

        print("\n [*] Bersiap dalam hitungan mundur:")
        for cd in range(3, 0, -1):
            print(f"     >> {cd} ...")
            beep(900, 150)
            time.sleep(1)

        print("\n [>> MULAI <<] LAKUKAN GERAKAN SEKARANG!")
        beep(1500, 350)

        ser.reset_input_buffer()
        start_time = time.time()
        sess_lines = []

        while time.time() - start_time < item["duration"]:
            elapsed = time.time() - start_time
            remaining = int(item["duration"] - elapsed)
            
            while ser.in_waiting:
                raw = ser.readline().decode("utf-8", errors="ignore").strip()
                if raw.startswith("FEAT,"):
                    parts = [p.strip() for p in raw.split(",") if p.strip()]
                    if len(parts) >= 13:
                        # Differentiate between LoRa ESP32 packet vs direct STM32 packet
                        if "." in parts[1]:
                            # LoRa: FEAT, a_total, g_total, ..., triage_pred, [hr, spo2, temp]
                            feat_vals = parts[1:13]
                        elif len(parts) >= 15:
                            # Direct STM32: FEAT, sess, label, a_total, g_total, ..., triage_pred
                            feat_vals = parts[3:15]
                        else:
                            feat_vals = None

                        if feat_vals and len(feat_vals) == 12:
                            formatted_line = f"FEAT,{current_sess},{item['label']}," + ",".join(feat_vals)
                            sess_lines.append(formatted_line)

            # Progress bar visual
            progress_pct = int((elapsed / item["duration"]) * 30)
            bar = "█" * progress_pct + "░" * (30 - progress_pct)
            print(f" [{bar}] Sisa: {remaining:02d}s | Sampel didapat: {len(sess_lines)} jendela ", end="\r")
            time.sleep(0.08)

        beep(1000, 150)
        time.sleep(0.05)
        beep(1400, 250)
        print(f"\n\n [✓ SELESAI] Sesi {item['code']} selesai! Berhasil merekam {len(sess_lines)} sampel data.\n")
        recorded_lines.extend(sess_lines)

        if idx < len(SESI_KERJA_HALUS) - 1:
            print(" Istirahat sejenak 5 detik sebelum sesi berikutnya...\n")
            time.sleep(3)

    ser.close()

    print("=" * 72)
    print(" RINGKASAN PENGAMBILAN DATA")
    print("=" * 72)
    print(f" Total sampel baru terkumpul : {len(recorded_lines)} baris jendela FEAT")
    
    if len(recorded_lines) > 0:
        with open(DATASET_FILE, "a", encoding="utf-8") as f:
            for l in recorded_lines:
                f.write(l + "\n")
        print(f" [✓] Dataset otomatis diperbarui di: {DATASET_FILE}")
    else:
        print(" [!] Peringatan: Tidak ada data FEAT yang terbaca dari sensor.")
    
    print("=" * 72)
    print(" Semua sesi kerja halus selesai! Kamu bisa kembali ke chat.")
    input("\nTekan Enter untuk menutup...")

if __name__ == "__main__":
    main()
