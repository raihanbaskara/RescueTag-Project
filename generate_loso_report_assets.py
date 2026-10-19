import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

OUT_DIR = "LAPORAN_HASIL_AUDIT_FINAL_LOSO_50HZ"
os.makedirs(OUT_DIR, exist_ok=True)

plt.rcParams.update({'font.sans-serif': 'DejaVu Sans', 'font.size': 11})

# 1. Confusion Matrix Heatmap
cm = np.array([
    [768, 150, 3],
    [95,  802, 113],
    [1,   45,  138]
])
classes = ['Diam (Hijau)', 'Kerja (Kuning)', 'Jatuh (Merah)']

plt.figure(figsize=(7, 6), dpi=300)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False,
            xticklabels=classes, yticklabels=classes,
            annot_kws={'size': 14, 'weight': 'bold'})
plt.title('Confusion Matrix - Leave-One-Session-Out (LOSO) CV\nRescue-Tag 50 Hz (2.115 Jendela, 46 Sesi)', fontsize=12, pad=15, weight='bold')
plt.xlabel('Prediksi Model', fontsize=11, labelpad=10, weight='bold')
plt.ylabel('Kondisi Aktual (Ground Truth)', fontsize=11, labelpad=10, weight='bold')
plt.tight_layout()
cm_path = os.path.join(OUT_DIR, "confusion_matrix_loso.png")
plt.savefig(cm_path)
plt.close()
print(f"[OK] Saved: {cm_path}")

# 2. Per-Class Metrics Bar Chart
metrics = {
    'Kelas': ['Diam (Hijau)', 'Kerja (Kuning)', 'Jatuh (Merah)'],
    'Presisi (%)': [88.9, 80.4, 54.3],
    'Recall (%)':  [83.4, 79.4, 75.0],
    'F1-Score (%)': [86.1, 79.9, 63.0]
}

x = np.arange(len(classes))
width = 0.25

fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
r1 = ax.bar(x - width, metrics['Presisi (%)'], width, label='Presisi', color='#2b5c8f')
r2 = ax.bar(x, metrics['Recall (%)'], width, label='Recall', color='#41924B')
r3 = ax.bar(x + width, metrics['F1-Score (%)'], width, label='F1-Score', color='#D97706')

ax.set_ylabel('Persentase (%)', fontsize=11, weight='bold')
ax.set_title('Metrik Performa Per Kelas (Leave-One-Session-Out Cross Validation)\nMacro-F1: 76.3% | Akurasi Per Jendela: 80.8%', fontsize=11, weight='bold', pad=15)
ax.set_xticks(x)
ax.set_xticklabels(classes, weight='bold')
ax.set_ylim(0, 105)
ax.legend(loc='lower right', frameon=True)
ax.grid(axis='y', linestyle='--', alpha=0.5)

def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        ax.annotate(f'{height:.1f}%',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=9, weight='bold')

autolabel(r1)
autolabel(r2)
autolabel(r3)

plt.tight_layout()
bar_path = os.path.join(OUT_DIR, "performa_per_kelas_loso.png")
plt.savefig(bar_path)
plt.close()
print(f"[OK] Saved: {bar_path}")

# 3. Perbandingan Baseline vs TinyML Decision Tree
categories = ['Deteksi Jatuh\n(Event Recall)', 'False Alarm\n(Jendela Non-Jatuh)', 'False Alarm\npada Kelas Diam']
baseline_vals = [27/35*100, 286, 17]
tinyml_vals   = [31/35*100, 116, 3]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5), dpi=300)

# Subplot 1: Event Recall
x1 = np.arange(1)
w1 = 0.35
ax1.bar(x1 - w1/2, [baseline_vals[0]], w1, label='Baseline (a_max >= 2.2g)', color='#94A3B8')
ax1.bar(x1 + w1/2, [tinyml_vals[0]], w1, label='TinyML Decision Tree', color='#10B981')
ax1.set_ylabel('Recall Kejadian (%)', fontsize=11, weight='bold')
ax1.set_title('Kemampuan Deteksi Jatuh', fontsize=11, weight='bold')
ax1.set_xticks(x1)
ax1.set_xticklabels(['Kejadian Jatuh (Merah)'], weight='bold')
ax1.set_ylim(0, 110)
ax1.annotate('27/35 (77.1%)', xy=(x1[0]-w1/2, baseline_vals[0]), xytext=(0, 3), textcoords='offset points', ha='center', weight='bold')
ax1.annotate('31/35 (88.6%)', xy=(x1[0]+w1/2, tinyml_vals[0]), xytext=(0, 3), textcoords='offset points', ha='center', weight='bold', color='#047857')
ax1.legend(loc='lower right')
ax1.grid(axis='y', linestyle='--', alpha=0.5)

# Subplot 2: False Alarms
x2 = np.arange(2)
w2 = 0.35
ax2.bar(x2 - w2/2, [baseline_vals[1], baseline_vals[2]], w2, label='Baseline (a_max >= 2.2g)', color='#EF4444')
ax2.bar(x2 + w2/2, [tinyml_vals[1], tinyml_vals[2]], w2, label='TinyML Decision Tree', color='#3B82F6')
ax2.set_ylabel('Jumlah Jendela Salah-Merah', fontsize=11, weight='bold')
ax2.set_title('Penyaringan Alarm Palsu (False Positives)', fontsize=11, weight='bold')
ax2.set_xticks(x2)
ax2.set_xticklabels(['Total Non-Jatuh', 'Khusus Kelas Diam'], weight='bold')
ax2.set_ylim(0, 320)
ax2.annotate('286 jendela', xy=(x2[0]-w2/2, baseline_vals[1]), xytext=(0, 3), textcoords='offset points', ha='center', weight='bold')
ax2.annotate('116 jendela\n(-59.4%)', xy=(x2[0]+w2/2, tinyml_vals[1]), xytext=(0, 3), textcoords='offset points', ha='center', weight='bold', color='#1D4ED8')
ax2.annotate('17 jendela', xy=(x2[1]-w2/2, baseline_vals[2]), xytext=(0, 3), textcoords='offset points', ha='center', weight='bold')
ax2.annotate('3 jendela\n(-82.4%)', xy=(x2[1]+w2/2, tinyml_vals[2]), xytext=(0, 3), textcoords='offset points', ha='center', weight='bold', color='#1D4ED8')
ax2.legend(loc='upper right')
ax2.grid(axis='y', linestyle='--', alpha=0.5)

plt.tight_layout()
comp_path = os.path.join(OUT_DIR, "perbandingan_baseline_false_alarm.png")
plt.savefig(comp_path)
plt.close()
print(f"[OK] Saved: {comp_path}")
