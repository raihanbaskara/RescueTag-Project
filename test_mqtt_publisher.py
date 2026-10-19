"""
=============================================================================
RESCUE-TAG: MQTT SIMULATOR & TEST PUBLISHER (TCP 1883 -> EMQX)
=============================================================================
Mengirimkan data telemetri JSON langsung ke broker MQTT publik (broker.emqx.io)
pada topik 'rescue/tag/data' untuk menguji respon Web Command Center.

Kontrol Keyboard:
  [0] : Kirim Status HIJAU   (Aman / Normal: HR 72, SpO2 98%, Temp 36.5°C)
  [1] : Kirim Status KUNING  (Kerja Aktif: HR 98, SpO2 96%, Temp 36.9°C)
  [2] : Kirim Status ORANYE  (Waspada Kelelahan: HR 126, SpO2 94%, Temp 37.8°C)
  [3] : Kirim Status MERAH   (Darurat Jatuh SOS: HR 138, SpO2 86%, Temp 38.6°C)
  [a] : Mode Auto Loop (Kirim berkala tiap 2 detik)
  [q] : Keluar
=============================================================================
"""

import sys
import time
import json
import msvcrt
import paho.mqtt.client as mqtt

BROKER = "broker.emqx.io"
PORT = 1883
TOPIC_DATA = "rescue/tag/data"
TOPIC_ALERT = "rescue/tag/alert"

def create_payload(triage_code):
    triage_info = {
        0: {
            "code": 0, "label": "HIJAU - Normal / Aman", "status": "NORMAL_AMAN",
            "hr": 74, "spo2": 98, "temp": 36.5, "a_max": 1.02, "g_total": 2.5,
            "kinematics": "Istirahat santai / normal (0.01g tremor)", "route": "Direct LoRa Link (Posko)"
        },
        1: {
            "code": 1, "label": "KUNING - Kerja Aktif", "status": "KERJA_AKTIF",
            "hr": 98, "spo2": 96, "temp": 36.9, "a_max": 1.75, "g_total": 92.4,
            "kinematics": "Aktivitas dinamis kerja tambang", "route": "1-Hop LoRa Relay via Jam #01"
        },
        2: {
            "code": 2, "label": "ORANYE - Waspada Dini", "status": "WASPADA_DINI",
            "hr": 128, "spo2": 93, "temp": 37.8, "a_max": 1.95, "g_total": 115.0,
            "kinematics": "Takikardia terdeteksi (Kelelahan Ekstrem)", "route": "1-Hop LoRa Relay via Jam #01"
        },
        3: {
            "code": 3, "label": "MERAH - Darurat SOS", "status": "DARURAT_JATUH",
            "hr": 138, "spo2": 86, "temp": 38.6, "a_max": 4.85, "g_total": 18.5,
            "kinematics": "⚠ Free-Fall & Immobility >30s (Impact 4.85g)", "route": "1-Hop LoRa Relay via Jam #01"
        }
    }

    item = triage_info.get(triage_code, triage_info[0])

    return {
        "device_id": "RESCUE-TAG-02",
        "worker_id": "WRK-002",
        "worker_name": "Agus Salim",
        "sector": "Sektor 7 (Lorong C-4)",
        "location": {
            "name": "Sektor 7 (C-4 Level -120m)",
            "lat": -8.2498,
            "lng": 113.7012
        },
        "triage": {
            "code": item["code"],
            "label": item["label"],
            "status": item["status"],
            "is_emergency": (item["code"] == 3)
        },
        "vitals": {
            "hr": item["hr"],
            "spo2": item["spo2"],
            "temp": item["temp"],
            "hr_text": f"{item['hr']} BPM",
            "spo2_text": f"{item['spo2']}%",
            "temp_text": f"{item['temp']:.1f}°C"
        },
        "kinematics": {
            "a_max": item["a_max"],
            "g_total": item["g_total"],
            "summary": item["kinematics"]
        },
        "network": {
            "route": item["route"],
            "rssi": -68
        },
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
    }

def main():
    print("=" * 70)
    print("   RESCUE-TAG: MQTT TEST PUBLISHER (TCP 1883 -> EMQX BROKER)")
    print("=" * 70)
    print(f"[*] Menghubungkan ke MQTT Broker: {BROKER}:{PORT}...")

    client = mqtt.Client(client_id="rescue_tag_test_publisher")
    try:
        client.connect(BROKER, PORT, keepalive=60)
        client.loop_start()
        print(f"[OK] Berhasil terhubung ke broker {BROKER}!")
    except Exception as e:
        print(f"[ERROR] Gagal terhubung ke broker MQTT: {e}")
        sys.exit(1)

    print("\nPetunjuk Tombol:")
    print("  [0] : Kirim HIJAU   (Normal / Aman)")
    print("  [1] : Kirim KUNING  (Kerja Aktif)")
    print("  [2] : Kirim ORANYE  (Waspada Kelelahan HR)")
    print("  [3] : Kirim MERAH   (Darurat Jatuh / SOS)")
    print("  [a] : Mode Auto (Berganti otomatis tiap 3 detik)")
    print("  [q] : Keluar")
    print("-" * 70)

    auto_mode = False
    cur_sim = 1
    last_auto = time.time()

    try:
        while True:
            if msvcrt.kbhit():
                key = msvcrt.getch().decode('utf-8', errors='ignore').lower()
                if key in ['0', '1', '2', '3']:
                    code = int(key)
                    auto_mode = False
                    payload = create_payload(code)
                    client.publish(TOPIC_DATA, json.dumps(payload))
                    print(f"\n[TX MQTT] Dipublikasikan ke '{TOPIC_DATA}' -> Triage [{code}]: {payload['triage']['label']} | HR: {payload['vitals']['hr_text']} | SpO2: {payload['vitals']['spo2_text']}")
                    if code == 3:
                        client.publish(TOPIC_ALERT, json.dumps({"alert": "SOS_FALL", "worker": "Agus Salim"}))
                        print(f"[TX ALERT] Dipublikasikan ke '{TOPIC_ALERT}' -> SOS ALERT DISPATCH!")
                elif key == 'a':
                    auto_mode = not auto_mode
                    print(f"\n[MODE AUTO] {'AKTIF' if auto_mode else 'NONAKTIF'}")
                elif key == 'q':
                    print("\n[INFO] Mengakhiri publisher...")
                    break

            if auto_mode and (time.time() - last_auto >= 3.0):
                last_auto = time.time()
                cur_sim = (cur_sim + 1) % 4
                payload = create_payload(cur_sim)
                client.publish(TOPIC_DATA, json.dumps(payload))
                print(f"[AUTO TX] Triage [{cur_sim}] -> {payload['triage']['label']} | HR: {payload['vitals']['hr_text']} | SpO2: {payload['vitals']['spo2_text']}")

            time.sleep(0.05)

    except KeyboardInterrupt:
        pass
    finally:
        client.loop_stop()
        client.disconnect()
        print("[*] Terputus dari MQTT broker.")

if __name__ == '__main__':
    main()
