"""
=============================================================================
RESCUE-TAG: PEREKAMAN DATA KERJA HALUS (K13, K14, K15)
=============================================================================
Menambah 3 sesi data kerja motorik halus untuk mempertegas batas Kerja vs Diam:
  1. K13: Mengetik keyboard / laptop aktif kontinu (30s)
  2. K14: Merakit komponen / memegang alat kecil / menulis (30s)
  3. K15: Menggerakkan mouse & navigasi perangkat kontrol (30s)
=============================================================================
"""

import sys
import os
import time
import json
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
        "desc": "Ketik teks di keyboard laptop secara santai tapi aktif kontinu tanpa jeda panjang."
    },
    {
        "code": "K14",
        "name": "Merakit Komponen / Menulis",
        "label": 1,
        "duration": 30,
        "desc": "Gerakkan tangan seperti merakit alat elektronik, memegang obeng/baut kecil, atau menulis."
    },
    {
        "code": "K15",
        "name": "Menggerakkan Mouse & Operasional Kontrol",
        "label": 1,
        "duration": 30,
        "desc": "Gerakkan mouse di meja, klik tombol, geser perangkat kontrol secara kontinu."
    }
]

DATASET_FILE = "Pengambilan_Data_LoRa/log_dataset_audit_clean.txt"
META_FILE = "Pengambilan_Data_LoRa/log_dataset_audit_clean.meta.json"

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
    print("=" * 70)
    print("   RESCUE-TAG: PEREKAMAN KERJA HALUS (FINE-GRAINED WORK SESSIONS)")
    print("=" * 70)

    port = find_serial_port()
    if not port:
        print("[!] ERROR: Tidak ada COM Port yang terdeteksi. Pastikan kabel USB sudah tertancap!")
        sys.exit(1)

    print(f"[*] Port terdeteksi: {port} (115200 baud)")
    try:
        ser = serial.Serial(port, 115200, timeout=1)
        time.sleep(2)
        ser.reset_input_buffer()
    except Exception as e:
        print(f"[!] Gagal membuka {port}: {e}")
        print("    Pastikan Node-RED atau Serial Monitor lain sudah DITUTUP!")
        sys.exit(1)

    print("[*] Port Serial BERHASIL terhubung!\n")

    next_sess_id = get_next_session_id()
    print(f"[*] Sesi ID baru akan dimulai dari: Sesi #{next_sess_id}\n")

    recorded_lines = []

    for idx, item in enumerate(SESI_KERJA_HALUS):
        current_sess = next_sess_id + idx
        print("-" * 70)
        print(f"[{idx+1}/3] PERSIAPAN: {item['code']} - {item['name']}")
        print(f"      Instruksi : {item['desc']}")
        print(f"      Durasi    : {item['duration']} detik | Label: {item['label']} (KERJA)")
        print("-" * 70)
        
        # Hitung mundur 5 detik
        for cd in range(5, 0, -1):
            print(f"  >> Bersiap dalam {cd} detik... (Posisikan tangan)", end="\r")
            beep(800, 100)
            time.sleep(1)
        
        print("\n  [MULAI] LAKUKAN GERAKAN SEKARANG!                          ")
        beep(1400, 300)

        ser.reset_input_buffer()
        start_time = time.time()
        sess_lines = []

        while time.time() - start_time < item["duration"]:
            remaining = int(item["duration"] - (time.time() - start_time))
            while ser.in_waiting:
                raw = ser.readline().decode("utf-8", errors="ignore").strip()
                if raw.startswith("FEAT,"):
                    parts = [p.strip() for p in raw.split(",") if p.strip()]
                    if len(parts) >= 13:
                        if "." in parts[1]:
                            feat_vals = parts[1:13]
                        elif len(parts) >= 15:
                            feat_vals = parts[3:15]
                        else:
                            feat_vals = None

                        if feat_vals and len(feat_vals) == 12:
                            formatted_line = f"FEAT,{current_sess},{item['label']}," + ",".join(feat_vals)
                            sess_lines.append(formatted_line)
            print(f"  >> Perekaman berjalan... Sisa waktu: {remaining:02d}s | Sampel: {len(sess_lines)} baris", end="\r")
            time.sleep(0.05)

        beep(1000, 150)
        time.sleep(0.05)
        beep(1400, 250)
        print(f"\n  [SELESAI] Sesi {item['code']} berhasil direkam: {len(sess_lines)} jendela (250ms)!\n")
        recorded_lines.extend(sess_lines)
        time.sleep(1.5)

    ser.close()

    print("=" * 70)
    print(f"[*] Total sampel baru terkumpul: {len(recorded_lines)} baris jendela.")
    if len(recorded_lines) > 0:
        with open(DATASET_FILE, "a", encoding="utf-8") as f:
            for l in recorded_lines:
                f.write(l + "\n")
        print(f"[✓] Data berhasil disimpan dan digabungkan ke: {DATASET_FILE}")
    else:
        print("[!] Peringatan: Tidak ada data FEAT yang diterima dari jam.")
    print("=" * 70)

if __name__ == "__main__":
    main()
