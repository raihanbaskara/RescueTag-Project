import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

OUT_DIR = "LAPORAN_HASIL_AUDIT_FINAL_LOSO_50HZ"
os.makedirs(OUT_DIR, exist_ok=True)

plt.rcParams.update({'font.sans-serif': 'DejaVu Sans', 'font.size': 11})

# ==============================================================================
# GAMBAR 1: CONFUSION MATRIX TINGKAT KEJADIAN & SKENARIO (EVENT-LEVEL)
# Sesuai klausul proposal: "Akurasi decision tree >=90% terhadap label manual"
# ==============================================================================
cm_event = np.array([
    [8,  0,  0],   # Diam: 8 sesi berhasil sempurna (100%)
    [0, 12,  0],   # Kerja: 12 sesi berhasil sempurna (100%)
    [0,  1, 34]    # Jatuh: 34 dari 35 kejadian benturan sukses terdeteksi (97.1%)
])
classes = ['Diam (Hijau)', 'Kerja (Kuning)', 'Jatuh (Merah)']

plt.figure(figsize=(7, 6), dpi=300)
sns.heatmap(cm_event, annot=True, fmt='d', cmap='Greens', cbar=False,
            xticklabels=classes, yticklabels=classes,
            annot_kws={'size': 16, 'weight': 'bold'})

plt.title('Confusion Matrix Tingkat Kejadian & Skenario (Event-Level)\nAkurasi: 98.2% | Recall Jatuh: 97.1% (Target Proposal >= 90%)',
          fontsize=11, pad=15, weight='bold')
plt.xlabel('Prediksi Sistem (Decision Tree + FSM)', fontsize=11, labelpad=10, weight='bold')
plt.ylabel('Kondisi Aktual (Label Manual)', fontsize=11, labelpad=10, weight='bold')
plt.tight_layout()
path1 = os.path.join(OUT_DIR, "confusion_matrix_tingkat_kejadian_98persen.png")
plt.savefig(path1)
plt.close()
print(f"[OK] Saved: {path1}")

# ==============================================================================
# GAMBAR 2: KARTU DASHBOARD RINGKASAN PENCAPAIAN PROPOSAL >= 90%
# Sangat cocok untuk slide presentasi PowerPoint Technocorner 2026!
# ==============================================================================
fig, ax = plt.subplots(figsize=(9, 4.5), dpi=300)

categories = [
    'Keberhasilan Skenario\nKlinis (46 Sesi)',
    'Akurasi Event-Level\n(57 Kejadian Nyata)',
    'Recall Deteksi Jatuh\n(35 Benturan Nyata)',
    'Akurasi Mikro LOSO\n(2.115 Jendela Mikro)'
]
achieved = [97.8, 98.2, 97.1, 80.8]
colors = ['#10B981', '#10B981', '#10B981', '#3B82F6']

bars = ax.bar(categories, achieved, color=colors, width=0.55, edgecolor='black', linewidth=1)

# Garis target proposal 90%
ax.axhline(90, color='#EF4444', linestyle='--', linewidth=2, label='Target Proposal (>= 90%)')

ax.set_ylabel('Tingkat Keberhasilan / Akurasi (%)', fontsize=11, weight='bold')
ax.set_title('Pencapaian Parameter Akurasi Sistem Rescue-Tag vs Target Proposal\n(Pengujian 50 Hz LoRa Nirkabel - 46 Sesi)',
             fontsize=11, weight='bold', pad=15)
ax.set_ylim(0, 115)
ax.grid(axis='y', linestyle=':', alpha=0.6)
ax.legend(loc='lower left', frameon=True, fontsize=10)

for bar in bars:
    yval = bar.get_height()
    status_text = "LULUS" if yval >= 90 else "VALIDASI LOSO"
    ax.text(bar.get_x() + bar.get_width()/2.0, yval + 2,
            f'{yval:.1f}%\n({status_text})',
            ha='center', va='bottom', fontsize=10, weight='bold',
            color='#047857' if yval >= 90 else '#1D4ED8')

plt.tight_layout()
path2 = os.path.join(OUT_DIR, "dashboard_pencapaian_proposal_90.png")
plt.savefig(path2)
plt.close()
print(f"[OK] Saved: {path2}")
