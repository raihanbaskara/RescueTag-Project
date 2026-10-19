"""
=============================================================================
RESCUE-TAG: PANDUAN PEREKAMAN DATA PROTOKOL AUDITOR (50 Hz WIRELESS)
=============================================================================
Memandu perekaman 40 sesi terstruktur sesuai PROTOKOL_REKAM_DATA.md:
  - 8 Sesi Diam (D1 - D8)
  - 12 Sesi Kerja (K1 - K12, termasuk negatif sulit: pukul meja, lompat, dsb.)
  - 20 Sesi Jatuh (J1 - J20, variasi arah & tangan ke kasur/matras tebal)

Otomatis:
  - Menghitung mundur durasi per sesi
  - Memberikan sinyal audio bip (mulai, aba-aba jatuh, selesai)
  - Memberikan label (0, 1, 3) dan nomor sesi baru yang bersih tanpa tertukar
  - Menyimpan langsung ke log_dataset_audit_clean.txt
=============================================================================
"""

import sys
import os
import time
import json
import msvcrt
import serial
import serial.tools.list_ports

try:
    import winsound
    HAS_SOUND = True
except ImportError:
    HAS_SOUND = False

def play_beep(freq, duration_ms):
    if HAS_SOUND:
        try:
            winsound.Beep(freq, duration_ms)
        except Exception:
            pass

def sound_start():
    play_beep(1200, 200)

def sound_fall_cue():
    play_beep(800, 150)
    time.sleep(0.05)
    play_beep(1000, 150)
    time.sleep(0.05)
    play_beep(1500, 350)

def sound_done():
    play_beep(1000, 150)
    time.sleep(0.05)
    play_beep(1400, 250)

# DAFTAR LENGKAP 40 SESI PROTOKOL AUDIT
PROTOKOL = [
    # --- DIAM (Label 0) ---
    {"code": "D1", "name": "Duduk, tangan di paha", "label": 0, "type": "steady", "duration": 30,
     "desc": "Duduk santai di kursi, tangan diletakkan rileks di atas paha."},
    {"code": "D2", "name": "Duduk di meja, mengetik", "label": 0, "type": "steady", "duration": 30,
     "desc": "Duduk di depan meja, tangan di atas meja/mengetik santai tanpa hentakan."},
    {"code": "D3", "name": "Berdiri diam", "label": 0, "type": "steady", "duration": 30,
     "desc": "Berdiri tegak santai, tangan rileks di samping tubuh."},
    {"code": "D4", "name": "Berbaring telentang", "label": 0, "type": "steady", "duration": 30,
     "desc": "Berbaring telentang di kasur/lantai, tangan diam di samping."},
    {"code": "D5", "name": "Berbaring miring", "label": 0, "type": "steady", "duration": 30,
     "desc": "Berbaring miring ke kiri/kanan, posisi tangan santai."},
    {"code": "D6", "name": "Jam dipegang diam di tangan", "label": 0, "type": "steady", "duration": 20,
     "desc": "Tangan memegang jam atau posisi santai sambil mengobrol ringan."},
    {"code": "D7", "name": "Duduk tenang (getaran halus)", "label": 0, "type": "steady", "duration": 30,
     "desc": "Duduk di kursi, goyang kaki pelan atau getaran tubuh alami."},
    {"code": "D8", "name": "Duduk, tangan dilipat di dada", "label": 0, "type": "steady", "duration": 30,
     "desc": "Duduk rileks dengan kedua tangan bersedekap di dada."},

    # --- KERJA (Label 1) ---
    {"code": "K1", "name": "Berjalan santai", "label": 1, "type": "steady", "duration": 30,
     "desc": "Berjalan santai bolak-balik di dalam ruangan."},
    {"code": "K2", "name": "Berjalan cepat", "label": 1, "type": "steady", "duration": 30,
     "desc": "Berjalan cepat / tergesa-gesa dengan ayunan tangan normal."},
    {"code": "K3", "name": "Berlari kecil di tempat", "label": 1, "type": "steady", "duration": 20,
     "desc": "Jogging santai / lari kecil di tempat."},
    {"code": "K4", "name": "Mengangkat & memindah barang", "label": 1, "type": "steady", "duration": 30,
     "desc": "Mengangkat barang (buku/tas/kardus) dari meja ke lantai atau sebaliknya."},
    {"code": "K5", "name": "Mengayun tangan kerja (alat/palu)", "label": 1, "type": "steady", "duration": 30,
     "desc": "Simulasi mengayun tangan seperti memegang perkakas atau alat tambang."},
    {"code": "K6", "name": "Memukul meja dengan tangan (NEGATIF SULIT)", "label": 1, "type": "steady", "duration": 20,
     "desc": "Ketuk atau tepuk meja dengan tangan beberapa kali (tanpa jatuh). Ajari AI bahwa hentakan ini bukan jatuh!"},
    {"code": "K7", "name": "Melompat (NEGATIF SULIT)", "label": 1, "type": "steady", "duration": 20,
     "desc": "Melompat 3-5 kali di tempat lalu mendarat dengan berdiri stabil."},
    {"code": "K8", "name": "Duduk lalu berdiri berulang", "label": 1, "type": "steady", "duration": 30,
     "desc": "Duduk di kursi, berdiri, duduk lagi secara berkala (3-4 kali)."},
    {"code": "K9", "name": "Tersandung lalu pulih (NEGATIF SULIT)", "label": 1, "type": "steady", "duration": 30,
     "desc": "Simulasi tersandung/terhuyung sesaat lalu kembali tegak berdiri tanpa jatuh."},
    {"code": "K10", "name": "Meletakkan jam/tangan kasar (NEGATIF SULIT)", "label": 1, "type": "steady", "duration": 15,
     "desc": "Taruh pergelangan tangan agak keras ke atas meja beberapa kali."},
    {"code": "K11", "name": "Naik turun tangga / bangku", "label": 1, "type": "steady", "duration": 30,
     "desc": "Naik turun satu anak tangga atau undakan secara berulang."},
    {"code": "K12", "name": "Membungkuk mengambil barang", "label": 1, "type": "steady", "duration": 30,
     "desc": "Membungkuk ke lantai mengambil benda lalu berdiri tegak kembali."},

    # --- JATUH (Label 3) ---
    {"code": "J1",  "name": "Jatuh DEPAN (Tangan menahan) #1", "label": 3, "type": "fall", "duration": 10,
     "desc": "Berdiri diam 3s -> Jatuh ke kasur depan dengan tangan menahan -> Diam di kasur 5s."},
    {"code": "J2",  "name": "Jatuh DEPAN (Tangan menahan) #2", "label": 3, "type": "fall", "duration": 10,
     "desc": "Berdiri diam 3s -> Jatuh ke kasur depan dengan tangan menahan -> Diam di kasur 5s."},
    {"code": "J3",  "name": "Jatuh DEPAN (Tangan menahan) #3", "label": 3, "type": "fall", "duration": 10,
     "desc": "Berdiri diam 3s -> Jatuh ke kasur depan dengan tangan menahan -> Diam di kasur 5s."},
    {"code": "J4",  "name": "Jatuh DEPAN (Tangan lepas/tidak menahan) #1", "label": 3, "type": "fall", "duration": 10,
     "desc": "Berdiri diam 3s -> Jatuh ke kasur depan tanpa menahan tangan -> Diam di kasur 5s."},
    {"code": "J5",  "name": "Jatuh DEPAN (Tangan lepas/tidak menahan) #2", "label": 3, "type": "fall", "duration": 10,
     "desc": "Berdiri diam 3s -> Jatuh ke kasur depan tanpa menahan tangan -> Diam di kasur 5s."},
    {"code": "J6",  "name": "Jatuh DEPAN (Tangan lepas/tidak menahan) #3", "label": 3, "type": "fall", "duration": 10,
     "desc": "Berdiri diam 3s -> Jatuh ke kasur depan tanpa menahan tangan -> Diam di kasur 5s."},
    {"code": "J7",  "name": "Jatuh BELAKANG (Tangan menahan) #1", "label": 3, "type": "fall", "duration": 10,
     "desc": "Berdiri diam 3s -> Jatuh punggung ke kasur dengan tangan menyangga -> Diam di kasur 5s."},
    {"code": "J8",  "name": "Jatuh BELAKANG (Tangan menahan) #2", "label": 3, "type": "fall", "duration": 10,
     "desc": "Berdiri diam 3s -> Jatuh punggung ke kasur dengan tangan menyangga -> Diam di kasur 5s."},
    {"code": "J9",  "name": "Jatuh BELAKANG (Tangan menahan) #3", "label": 3, "type": "fall", "duration": 10,
     "desc": "Berdiri diam 3s -> Jatuh punggung ke kasur dengan tangan menyangga -> Diam di kasur 5s."},
    {"code": "J10", "name": "Jatuh BELAKANG (Tangan lepas) #1", "label": 3, "type": "fall", "duration": 10,
     "desc": "Berdiri diam 3s -> Jatuh telentang bebas ke kasur -> Diam di kasur 5s."},
    {"code": "J11", "name": "Jatuh BELAKANG (Tangan lepas) #2", "label": 3, "type": "fall", "duration": 10,
     "desc": "Berdiri diam 3s -> Jatuh telentang bebas ke kasur -> Diam di kasur 5s."},
    {"code": "J12", "name": "Jatuh BELAKANG (Tangan lepas) #3", "label": 3, "type": "fall", "duration": 10,
     "desc": "Berdiri diam 3s -> Jatuh telentang bebas ke kasur -> Diam di kasur 5s."},
    {"code": "J13", "name": "Jatuh SAMPING KIRI #1", "label": 3, "type": "fall", "duration": 10,
     "desc": "Berdiri diam 3s -> Miringkan badan & jatuh ke kiri di kasur -> Diam di kasur 5s."},
    {"code": "J14", "name": "Jatuh SAMPING KIRI #2", "label": 3, "type": "fall", "duration": 10,
     "desc": "Berdiri diam 3s -> Miringkan badan & jatuh ke kiri di kasur -> Diam di kasur 5s."},
    {"code": "J15", "name": "Jatuh SAMPING KIRI #3", "label": 3, "type": "fall", "duration": 10,
     "desc": "Berdiri diam 3s -> Miringkan badan & jatuh ke kiri di kasur -> Diam di kasur 5s."},
    {"code": "J16", "name": "Jatuh SAMPING KANAN #1", "label": 3, "type": "fall", "duration": 10,
     "desc": "Berdiri diam 3s -> Miringkan badan & jatuh ke kanan di kasur -> Diam di kasur 5s."},
    {"code": "J17", "name": "Jatuh SAMPING KANAN #2", "label": 3, "type": "fall", "duration": 10,
     "desc": "Berdiri diam 3s -> Miringkan badan & jatuh ke kanan di kasur -> Diam di kasur 5s."},
    {"code": "J18", "name": "Jatuh SAMPING KANAN #3", "label": 3, "type": "fall", "duration": 10,
     "desc": "Berdiri diam 3s -> Miringkan badan & jatuh ke kanan di kasur -> Diam di kasur 5s."},
    {"code": "J19", "name": "Jatuh LEMAS / MEROSOT (Sinkop/Pingsan) #1", "label": 3, "type": "fall", "duration": 10,
     "desc": "Berdiri diam 3s -> Lutut lemas menekuk & jatuh melorot ke kasur -> Diam di kasur 5s."},
    {"code": "J20", "name": "Jatuh LEMAS / MEROSOT (Sinkop/Pingsan) #2", "label": 3, "type": "fall", "duration": 10,
     "desc": "Berdiri diam 3s -> Lutut lemas menekuk & jatuh melorot ke kasur -> Diam di kasur 5s."},
    {"code": "J21", "name": "Jatuh DEPAN Penguat #4", "label": 3, "type": "fall", "duration": 10,
     "desc": "Berdiri diam 3s -> Jatuh ke kasur depan -> Diam di kasur 5s."},
    {"code": "J22", "name": "Jatuh BELAKANG Penguat #4", "label": 3, "type": "fall", "duration": 10,
     "desc": "Berdiri diam 3s -> Jatuh ke kasur belakang -> Diam di kasur 5s."},
    {"code": "J23", "name": "Jatuh SAMPING Penguat #4", "label": 3, "type": "fall", "duration": 10,
     "desc": "Berdiri diam 3s -> Jatuh ke kasur samping -> Diam di kasur 5s."},
    {"code": "J24", "name": "Jatuh LEMAS Penguat #3", "label": 3, "type": "fall", "duration": 10,
     "desc": "Berdiri diam 3s -> Lutut lemas & jatuh melorot ke kasur -> Diam di kasur 5s."}
]

DATA_FILE = "Pengambilan_Data_LoRa/log_dataset_audit_clean.txt"
META_FILE = "Pengambilan_Data_LoRa/log_dataset_audit_clean.meta.json"

def find_esp32_port():
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        return None
    for p in ports:
        desc = p.description.lower()
        if any(x in desc for x in ["cp210", "ch340", "usb", "serial", "uart"]):
            return p.device
    return ports[0].device

def load_meta():
    if os.path.exists(META_FILE):
        try:
            with open(META_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {"completed_codes": {}, "max_session_id": 0}

def save_meta(meta):
    with open(META_FILE, 'w') as f:
        json.dump(meta, f, indent=2)

def record_single_session(ser, session_id, task, file_handle):
    code = task["code"]
    name = task["name"]
    label = task["label"]
    ttype = task["type"]
    duration = task["duration"]
    desc = task["desc"]

    label_str = {0: "DIAM (HIJAU)", 1: "KERJA (KUNING)", 3: "JATUH (MERAH)"}[label]

    print("\n" + "=" * 72)
    print(f"  SESI {session_id:02d} : [{code}] {name.upper()}")
    print(f"  Label Target : {label} - {label_str}")
    print(f"  Instruksi    : {desc}")
    print("=" * 72)

    if ttype == "fall":
        print("\n>>> PANDUAN JATUH AMAN KE KASUR:")
        print("  1. Berdiri tegak di depan kasur tebal.")
        print("  2. Saat Anda menekan ENTER, sistem akan hitung mundur 3 DETIK diam.")
        print("  3. Begitu bunyi BIP PANJANG ('JATUH SEKARANG!'), jatuhkan badan ke kasur!")
        print("  4. Setelah mendarat di kasur, TETAP DIAM selama 5 DETIK sampai bunyi selesai.")
        print("  (Semua aba-aba ada suara BIP, jadi tidak perlu melihat layar laptop saat jatuh)\n")

    input(f"Tekan [ENTER] jika Anda sudah SIAP untuk memulai sesi [{code}]...")

    # Flush serial buffer sebelum merekam
    ser.reset_input_buffer()

    samples_collected = 0
    t_start = time.time()
    sound_start()

    if ttype == "steady":
        print(f"\n[*] MEREKAM [{code}] selama {duration} detik... Lakukan aktivitas sekarang!\n")
        while True:
            elapsed = time.time() - t_start
            remaining = duration - elapsed
            if remaining <= 0:
                break

            line = ser.readline().decode('utf-8', errors='ignore').strip()
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

                        clean_line = (f"FEAT,{session_id},{label},"
                                      f"{a_total:.4f},{g_total:.3f},"
                                      f"{a_max:.4f},{a_min:.4f},"
                                      f"{g_mean:.3f},{a_std:.4f},{g_max:.3f},"
                                      f"{ax:.4f},{ay:.4f},{az:.4f},"
                                      f"{model_pred},{triage_pred}\n")
                        file_handle.write(clean_line)
                        file_handle.flush()
                        samples_collected += 1

                        print(f"\r  [REKAM {code}] Sisa: {remaining:4.1f}s | Sampel: {samples_collected:3d} | "
                              f"A_Tot: {a_total:4.2f}g | A_Max: {a_max:4.2f}g | G_Tot: {g_total:5.1f}dps | HR: {hr:2d} ",
                              end="", flush=True)
                    except (ValueError, IndexError):
                        pass

    elif ttype == "fall":
        # Fase 1: Berdiri Diam (3 detik)
        print("\n[*] FASE 1: Berdiri diam di depan kasur (3 detik)...")
        phase1_start = time.time()
        while time.time() - phase1_start < 3.0:
            remaining = 3.0 - (time.time() - phase1_start)
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line.startswith("FEAT,"):
                parts = [p.strip() for p in line.split(',') if p.strip()]
                if len(parts) >= 13:
                    try:
                        clean_line = (f"FEAT,{session_id},{label},"
                                      f"{float(parts[1]):.4f},{float(parts[2]):.3f},"
                                      f"{float(parts[3]):.4f},{float(parts[4]):.4f},"
                                      f"{float(parts[5]):.3f},{float(parts[6]):.4f},{float(parts[7]):.3f},"
                                      f"{float(parts[8]):.4f},{float(parts[9]):.4f},{float(parts[10]):.4f},"
                                      f"{int(parts[11])},{int(parts[12])}\n")
                        file_handle.write(clean_line)
                        file_handle.flush()
                        samples_collected += 1
                        print(f"\r  [FASE 1: DIAM] Sisa: {remaining:3.1f}s | Sampel: {samples_collected:2d} ", end="", flush=True)
                    except (ValueError, IndexError):
                        pass

        # Fase 2: ABA-ABA JATUH!
        print("\n\n>>> !!! JATUH SEKARANG KE KASUR !!! <<<")
        sound_fall_cue()

        # Fase 3: Rekam Jatuh & Mendarat (2 detik)
        phase2_start = time.time()
        while time.time() - phase2_start < 2.0:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line.startswith("FEAT,"):
                parts = [p.strip() for p in line.split(',') if p.strip()]
                if len(parts) >= 13:
                    try:
                        clean_line = (f"FEAT,{session_id},{label},"
                                      f"{float(parts[1]):.4f},{float(parts[2]):.3f},"
                                      f"{float(parts[3]):.4f},{float(parts[4]):.4f},"
                                      f"{float(parts[5]):.3f},{float(parts[6]):.4f},{float(parts[7]):.3f},"
                                      f"{float(parts[8]):.4f},{float(parts[9]):.4f},{float(parts[10]):.4f},"
                                      f"{int(parts[11])},{int(parts[12])}\n")
                        file_handle.write(clean_line)
                        file_handle.flush()
                        samples_collected += 1
                    except (ValueError, IndexError):
                        pass

        # Fase 4: Diam di Kasur (5 detik)
        print("\n[*] FASE 3: Tergeletak diam di kasur (5 detik)...")
        phase3_start = time.time()
        while time.time() - phase3_start < 5.0:
            remaining = 5.0 - (time.time() - phase3_start)
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line.startswith("FEAT,"):
                parts = [p.strip() for p in line.split(',') if p.strip()]
                if len(parts) >= 13:
                    try:
                        clean_line = (f"FEAT,{session_id},{label},"
                                      f"{float(parts[1]):.4f},{float(parts[2]):.3f},"
                                      f"{float(parts[3]):.4f},{float(parts[4]):.4f},"
                                      f"{float(parts[5]):.3f},{float(parts[6]):.4f},{float(parts[7]):.3f},"
                                      f"{float(parts[8]):.4f},{float(parts[9]):.4f},{float(parts[10]):.4f},"
                                      f"{int(parts[11])},{int(parts[12])}\n")
                        file_handle.write(clean_line)
                        file_handle.flush()
                        samples_collected += 1
                        print(f"\r  [FASE 3: DIAM DI KASUR] Sisa: {remaining:3.1f}s | Sampel: {samples_collected:2d} ", end="", flush=True)
                    except (ValueError, IndexError):
                        pass

    sound_done()
    print(f"\n\n[OK] Sesi [{code}] SELESAI! ({samples_collected} jendela tersimpan ke log).")

    # Konfirmasi apakah pengguna puas dengan sesi ini
    while True:
        choice = input("Simpan sesi ini? ([y]=Ya lanjut / [r]=Ulangi sesi ini / [q]=Simpan & keluar): ").strip().lower()
        if choice in ['', 'y', 'yes']:
            return True, samples_collected
        elif choice in ['r', 'repeat']:
            print("[*] Sesi ini akan diulang...")
            return False, 0
        elif choice in ['q', 'quit']:
            return 'quit', samples_collected

def main():
    print("=" * 72)
    print("       RESCUE-TAG: PANDUAN PEREKAMAN DATA PROTOKOL AUDITOR (50 Hz)")
    print("           Bebas Bingung Tombol • Terstruktur • Standar UGM")
    print("=" * 72)

    os.makedirs("Pengambilan_Data_LoRa", exist_ok=True)

    port = find_esp32_port()
    if not port:
        print("[!] Port COM ESP32 tidak terdeteksi otomatis.")
        port = input("Ketik nama port COM ESP32 manual (misal COM3): ").strip()
    else:
        print(f"[*] Port ESP32 Gateway terdeteksi: {port}")

    baud_rate = 115200
    print(f"[*] Menghubungkan ke {port} @ {baud_rate} baud...")
    try:
        ser = serial.Serial(port, baud_rate, timeout=0.1)
        time.sleep(1.5)
        print(f"[OK] Terhubung ke ESP32 Gateway!")
    except Exception as e:
        print(f"[ERROR] Gagal membuka port {port}: {e}")
        print("Tutup Serial Monitor Arduino IDE terlebih dahulu jika masih terbuka.")
        sys.exit(1)

    meta = load_meta()
    completed_codes = meta.get("completed_codes", {})
    cur_session_id = meta.get("max_session_id", 0) + 1

    d_done = sum(1 for c in completed_codes if c.startswith('D'))
    k_done = sum(1 for c in completed_codes if c.startswith('K'))
    j_done = sum(1 for c in completed_codes if c.startswith('J'))

    print("\nStatus Progres Sesi Tersimpan Saat Ini:")
    print(f"  • Diam  (D) : {d_done:02d} / 08 sesi")
    print(f"  • Kerja (K) : {k_done:02d} / 12 sesi")
    print(f"  • Jatuh (J) : {j_done:02d} / 20 sesi")
    print(f"  • Total Sesi: {len(completed_codes):02d} / 40 sesi selesai")
    print(f"  • File Log  : '{DATA_FILE}'")

    print("\nPilih Mode Mulai:")
    print("  [1] Lanjutkan otomatis dari sesi yang belum selesai (Direkomendasikan)")
    print("  [2] Pilih kode sesi manual (misal mau langsung rekam D1, K6, atau J1)")
    print("  [3] Reset & mulai baru dari nol")
    choice = input("\nPilihan Anda (1/2/3) [Default 1]: ").strip()

    tasks_to_run = []
    if choice == '3':
        confirm = input("Yakin ingin menghapus riwayat sesi? (ketik 'ya'): ").strip().lower()
        if confirm == 'ya':
            meta = {"completed_codes": {}, "max_session_id": 0}
            save_meta(meta)
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
            cur_session_id = 1
            completed_codes = {}
            tasks_to_run = PROTOKOL[:]
            print("[*] Riwayat di-reset. Memulai dari D1.")
        else:
            tasks_to_run = [t for t in PROTOKOL if t["code"] not in completed_codes]
    elif choice == '2':
        target = input("Ketik kode sesi (misal K6 atau J1): ").strip().upper()
        matching = [t for t in PROTOKOL if t["code"] == target]
        if matching:
            tasks_to_run = matching
        else:
            print(f"[!] Kode '{target}' tidak ditemukan di daftar protokol.")
            tasks_to_run = [t for t in PROTOKOL if t["code"] not in completed_codes]
    else:
        tasks_to_run = [t for t in PROTOKOL if t["code"] not in completed_codes]

    if not tasks_to_run:
        print("\n[SELAMAT!] Semua 40 sesi protokol telah selesai direkam!")
        run_loso = input("Jalankan evaluasi model LOSO sekarang? (y/n) [y]: ").strip().lower()
        if run_loso in ['', 'y', 'yes']:
            ser.close()
            os.system(f'python "Pengambilan_Data_LoRa/catatan audit/train_triage_loso.py" "{DATA_FILE}"')
        return

    with open(DATA_FILE, 'a', encoding='utf-8') as f_out:
        for task in tasks_to_run:
            while True:
                status, n_samples = record_single_session(ser, cur_session_id, task, f_out)
                if status == 'quit':
                    print("\n[INFO] Menyimpan sesi terakhir dan keluar...")
                    meta["max_session_id"] = cur_session_id
                    save_meta(meta)
                    ser.close()
                    return
                elif status is True:
                    completed_codes[task["code"]] = {
                        "session_id": cur_session_id,
                        "samples": n_samples,
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                    }
                    meta["completed_codes"] = completed_codes
                    meta["max_session_id"] = cur_session_id
                    save_meta(meta)
                    cur_session_id += 1
                    break
                else:
                    # Ulangi sesi yang sama
                    pass

    ser.close()
    print("\n" + "=" * 72)
    print("  PENGAMBILAN DATA SESI BERHASIL DISELESAIKAN!")
    print(f"  Log tersimpan di: '{DATA_FILE}'")
    print("=" * 72)

    run_loso = input("\nJalankan evaluasi model LOSO sekarang? (y/n) [y]: ").strip().lower()
    if run_loso in ['', 'y', 'yes']:
        os.system(f'python "Pengambilan_Data_LoRa/catatan audit/train_triage_loso.py" "{DATA_FILE}" --out "Pengambilan_Data_LoRa/stm32_transmitter/triage_model.h"')

if __name__ == '__main__':
    main()
