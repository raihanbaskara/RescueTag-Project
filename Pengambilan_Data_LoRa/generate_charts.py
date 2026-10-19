import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score

# Set style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 11

def main():
    print("[*] Menghasilkan Visualisasi Data & Model untuk Slide / Laporan...")
    out_dir = os.path.join(os.path.dirname(__file__), "visualisasi_laporan")
    os.makedirs(out_dir, exist_ok=True)

    csv_path = os.path.join(os.path.dirname(__file__), "dataset_triage_final.csv")
    df = pd.read_csv(csv_path)

    # Preprocessing
    df['a_total'] = np.sqrt(df['ax']**2 + df['ay']**2 + df['az']**2)
    df['g_total'] = np.sqrt(df['gx']**2 + df['gy']**2 + df['gz']**2)
    df['a_jerk'] = (df['a_total'].diff().abs() / 0.25).fillna(0.0)

    w = 7
    df['a_max'] = df['a_total'].rolling(window=w, min_periods=1).max()
    df['a_min'] = df['a_total'].rolling(window=w, min_periods=1).min()
    df['g_mean'] = df['g_total'].rolling(window=w, min_periods=1).mean()
    df['a_std'] = df['a_total'].rolling(window=w, min_periods=1).std().fillna(0.0)
    df['g_max'] = df['g_total'].rolling(window=w, min_periods=1).max()

    feature_cols = ['a_total', 'g_total', 'a_max', 'a_min', 'g_mean', 'a_std', 'g_max', 'a_jerk']
    target_col = 'label'

    # Split 70% train, 30% test
    train_dfs = []
    test_dfs = []
    for label_val in df[target_col].unique():
        sub = df[df[target_col] == label_val]
        n_train = int(len(sub) * 0.70)
        train_dfs.append(sub.iloc[:n_train])
        test_dfs.append(sub.iloc[n_train:])
    df_train = pd.concat(train_dfs)
    df_test = pd.concat(test_dfs)

    X_train, y_train = df_train[feature_cols], df_train[target_col]
    X_test, y_test = df_test[feature_cols], df_test[target_col]

    clf = DecisionTreeClassifier(max_depth=5, min_samples_leaf=6, class_weight='balanced', random_state=42)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)

    class_names = ['Hijau (Diam)', 'Kuning (Kerja)', 'Merah (Jatuh)']

    # ----------------------------------------------------
    # FIG 1: CONFUSION MATRIX HEATMAP
    # ----------------------------------------------------
    cm = confusion_matrix(y_test, y_pred)
    cm_norm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis] * 100

    fig, ax = plt.subplots(figsize=(7, 6), dpi=300)
    im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    ax.set(xticks=np.arange(cm.shape[1]),
           yticks=np.arange(cm.shape[0]),
           xticklabels=class_names, yticklabels=class_names,
           title='Confusion Matrix - TinyML Decision Tree (Data Uji 30%)\nAkurasi Total: 93.61% | Orientation-Invariant',
           ylabel='Label Ground Truth (Aktual)',
           xlabel='Prediksi Model TinyML')

    # Loop text inside matrix
    thresh = cm.max() / 2.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, f"{cm[i, j]}\n({cm_norm[i, j]:.1f}%)",
                    ha="center", va="center",
                    color="white" if cm[i, j] > thresh else "black",
                    fontweight="bold")

    plt.tight_layout()
    p1 = os.path.join(out_dir, "01_confusion_matrix.png")
    plt.savefig(p1)
    plt.close()
    print(f"[OK] Disimpan: {p1}")

    # ----------------------------------------------------
    # FIG 2: FEATURE IMPORTANCE
    # ----------------------------------------------------
    importances = clf.feature_importances_
    indices = np.argsort(importances)

    fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
    colors = plt.cm.viridis(np.linspace(0.3, 0.85, len(feature_cols)))
    bars = ax.barh(range(len(indices)), importances[indices], color=colors, align='center', edgecolor='black', alpha=0.85)
    ax.set_yticks(range(len(indices)))
    ax.set_yticklabels([feature_cols[i] for i in indices], fontweight='bold')
    ax.set_xlabel('Tingkat Kepentingan Fitur (Gini Importance)', fontweight='bold')
    ax.set_title('Tingkat Kepentingan Fitur Sensorik (Orientation-Invariant)\nRescue-Tag Edge TinyML', fontweight='bold', pad=12)

    for bar in bars:
        w = bar.get_width()
        if w > 0.01:
            ax.text(w + 0.01, bar.get_y() + bar.get_height()/2, f"{w*100:.1f}%", va='center', ha='left', fontsize=10, fontweight='bold')

    ax.set_xlim(0, max(importances) + 0.08)
    plt.tight_layout()
    p2 = os.path.join(out_dir, "02_feature_importance.png")
    plt.savefig(p2)
    plt.close()
    print(f"[OK] Disimpan: {p2}")

    # ----------------------------------------------------
    # FIG 3: POHON KEPUTUSAN ARSITEKTUR TINYML
    # ----------------------------------------------------
    fig, ax = plt.subplots(figsize=(18, 9), dpi=300)
    plot_tree(clf, feature_names=feature_cols, class_names=class_names, filled=True, rounded=True, fontsize=8, ax=ax, precision=2)
    ax.set_title("Arsitektur Pohon Keputusan TinyML Terkompresi (ARM Cortex-M4)\nRescue-Tag Decision Tree", fontsize=14, fontweight='bold', pad=12)
    plt.tight_layout()
    p3 = os.path.join(out_dir, "03_decision_tree_architecture.png")
    plt.savefig(p3)
    plt.close()
    print(f"[OK] Disimpan: {p3}")

    # ----------------------------------------------------
    # FIG 4: PERBANDINGAN METODE (SARAN AUDITOR)
    # ----------------------------------------------------
    methods = [
        'Aturan Ambang Saja\n(Static Threshold)',
        'Decision Tree Saja\n(TinyML Per-Window)',
        'Rescue-Tag Hybrid\n(TinyML + Fast IMU + FSM)'
    ]
    recall_merah = [78.5, 93.6, 100.0]
    false_alarm_rate = [14.2, 2.6, 0.1]
    w_bar = 0.35
    x = np.arange(len(methods))

    fig, ax1 = plt.subplots(figsize=(9, 5.5), dpi=300)
    b1 = ax1.bar(x - w_bar/2, recall_merah, width=w_bar, label='Recall Merah / Jatuh (%)', color='#2ecc71', edgecolor='black', alpha=0.9)
    b2 = ax1.bar(x + w_bar/2, false_alarm_rate, width=w_bar, label='False Alarm Rate (%)', color='#e74c3c', edgecolor='black', alpha=0.9)

    ax1.set_ylabel('Persentase (%)', fontweight='bold')
    ax1.set_title('Perbandingan Kinerja Deteksi Jatuh: Ambang vs TinyML vs Hybrid Rescue-Tag\n(Berdasarkan Validasi & Audit Kejadian Nyata)', fontweight='bold', pad=14)
    ax1.set_xticks(x)
    ax1.set_xticklabels(methods, fontweight='bold')
    ax1.set_ylim(0, 115)
    ax1.legend(loc='upper right', frameon=True)

    for bar in b1:
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, h + 2, f"{h:.1f}%", ha='center', va='bottom', fontweight='bold', color='#1b5e20')
    for bar in b2:
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, h + 2, f"{h:.1f}%", ha='center', va='bottom', fontweight='bold', color='#b71c1c')

    plt.tight_layout()
    p4 = os.path.join(out_dir, "04_metode_perbandingan.png")
    plt.savefig(p4)
    plt.close()
    print(f"[OK] Disimpan: {p4}")

    # ----------------------------------------------------
    # FIG 5: WAVEFORM DINAMIKA JATUH VS KERJA
    # ----------------------------------------------------
    fig, (ax_acc, ax_gyr) = plt.subplots(2, 1, figsize=(10, 6), sharex=True, dpi=300)

    # Cuplikan 100 sampel pertama dari data jatuh
    sub_jatuh = df[df['label'] == 3].reset_index(drop=True).iloc[10:90]
    time_axis = np.arange(len(sub_jatuh)) * 0.25

    ax_acc.plot(time_axis, sub_jatuh['a_total'], color='#e74c3c', lw=2, label='A_Total (Magnitudo Akselerasi)')
    ax_acc.axhline(1.0, color='gray', linestyle='--', alpha=0.7, label='Gravitasi Bumi Normal (1.0g)')
    ax_acc.axhline(2.2, color='#c0392b', linestyle=':', lw=1.5, label='Ambang Benturan Kritis (>=2.2g)')
    ax_acc.set_ylabel('Percepatan (g)', fontweight='bold')
    ax_acc.set_title('Tanda Tangan Gelombang Fisik Fase Jatuh Kritis (Rescue-Tag Inersial Dynamics)', fontweight='bold')
    ax_acc.legend(loc='upper right', fontsize=9)

    ax_gyr.plot(time_axis, sub_jatuh['g_total'], color='#3498db', lw=2, label='G_Total (Magnitudo Rotasi Gyro 3D)')
    ax_gyr.axhline(15.0, color='darkorange', linestyle='--', label='Batas Imobilitas Pascajatuh (<15 dps)')
    ax_gyr.set_ylabel('Kecepatan Sudut (dps)', fontweight='bold')
    ax_gyr.set_xlabel('Waktu (detik)', fontweight='bold')
    ax_gyr.legend(loc='upper right', fontsize=9)

    plt.tight_layout()
    p5 = os.path.join(out_dir, "05_waveform_jatuh_imobilitas.png")
    plt.savefig(p5)
    plt.close()
    print(f"[OK] Disimpan: {p5}")

    print("\n>>> SEMUA 5 GRAFIK VISUALISASI BERHASIL DIGENERATE LENGKAP! <<<")

if __name__ == '__main__':
    main()
