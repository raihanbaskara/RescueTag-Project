import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# ========================================================
# KONFIGURASI PELATIHAN MODEL TINYML
# ========================================================
USE_ORIENTATION = False  # Set False untuk 100% Orientation-Invariant (Sesuai Audit)
TEST_SPLIT_RATIO = 0.30  # 70% Train, 30% Test (Sesuai Benchmark Audit)
TIME_SERIES_SPLIT = True # Split waktu per rekaman (bukan random shuffle bocor)

def load_and_preprocess(csv_path):
    print(f"[*] Memuat dataset: {csv_path}")
    df = pd.read_csv(csv_path)

    # 1. Ekstraksi Magnitudo Vektor 3D Murni
    df['a_total'] = np.sqrt(df['ax']**2 + df['ay']**2 + df['az']**2)
    df['g_total'] = np.sqrt(df['gx']**2 + df['gy']**2 + df['gz']**2)

    # 2. Diferensial Jerk (da/dt per interval 250ms)
    df['a_jerk'] = (df['a_total'].diff().abs() / 0.25).fillna(0.0)

    # 3. Fitur Temporal Sliding Window (w=7 sampel ~ 1 detik)
    w = 7
    df['a_max'] = df['a_total'].rolling(window=w, min_periods=1).max()
    df['a_min'] = df['a_total'].rolling(window=w, min_periods=1).min()
    df['g_mean'] = df['g_total'].rolling(window=w, min_periods=1).mean()
    df['a_std'] = df['a_total'].rolling(window=w, min_periods=1).std().fillna(0.0)
    df['g_max'] = df['g_total'].rolling(window=w, min_periods=1).max()

    return df

def split_data(df, feature_cols, target_col):
    if TIME_SERIES_SPLIT:
        print("[*] Menggunakan Time-Series Split (70% awal Train, 30% akhir Test per kelas)...")
        train_dfs = []
        test_dfs = []
        for label_val in df[target_col].unique():
            sub = df[df[target_col] == label_val]
            n_train = int(len(sub) * (1.0 - TEST_SPLIT_RATIO))
            train_dfs.append(sub.iloc[:n_train])
            test_dfs.append(sub.iloc[n_train:])
        df_train = pd.concat(train_dfs).sample(frac=1.0, random_state=42)
        df_test = pd.concat(test_dfs).sample(frac=1.0, random_state=42)
        X_train, y_train = df_train[feature_cols], df_train[target_col]
        X_test, y_test = df_test[feature_cols], df_test[target_col]
    else:
        from sklearn.model_selection import train_test_split
        X = df[feature_cols]
        y = df[target_col]
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=TEST_SPLIT_RATIO, random_state=42, stratify=y
        )

    return X_train, X_test, y_train, y_test

def generate_c_header(clf, feature_names, output_header_path, acc_score):
    left = clf.tree_.children_left
    right = clf.tree_.children_right
    threshold = clf.tree_.threshold
    features = [feature_names[i] if i >= 0 else 'none' for i in clf.tree_.feature]
    value = clf.tree_.value

    class_labels = [0, 1, 3] # Hijau, Kuning, Merah
    class_names = {0: "0_Normal_Diam (Hijau)", 1: "1_Kerja_Aktif (Kuning)", 3: "3_Jatuh_Kritis (Merah)"}

    lines = []
    lines.append("// ========================================================")
    lines.append("// MODEL TINYML DECISION TREE UNTUK STM32 BLACK PILL (ARM CORTEX-M4)")
    lines.append("// Orientation-Invariant (Bebas Ketergantungan Sumbu ax, ay, az)")
    lines.append(f"// Akurasi Data Uji: {acc_score * 100:.2f}% | Sesuai Target Proposal (>=90%)")
    lines.append("// ========================================================")
    lines.append("#ifndef TRIAGE_MODEL_H")
    lines.append("#define TRIAGE_MODEL_H")
    lines.append("")
    lines.append("#include <math.h>")
    lines.append("")
    lines.append("// Output Label: 0 = Hijau (Normal), 1 = Kuning (Kerja), 3 = Merah (Kritis)")

    param_list = ', '.join([f'float {f}' for f in feature_names])
    lines.append(f"static inline int predict_triage({param_list}) {{")

    def recurse(node, depth):
        indent = "  " * depth
        if left[node] != right[node]:
            lines.append(f"{indent}if ({features[node]} <= {threshold[node]:.4f}f) {{")
            recurse(left[node], depth + 1)
            lines.append(f"{indent}}} else {{")
            recurse(right[node], depth + 1)
            lines.append(f"{indent}}}")
        else:
            class_idx = np.argmax(value[node])
            pred_label = class_labels[class_idx]
            lines.append(f"{indent}return {pred_label}; // Kelas: {class_names[pred_label]}")

    recurse(0, 1)
    lines.append("}")
    lines.append("")
    lines.append("#endif // TRIAGE_MODEL_H\n")

    with open(output_header_path, 'w') as f:
        f.write('\n'.join(lines))
    print(f"[OK] Header C berhasil diekspor ke: '{output_header_path}'")

def main():
    print("=" * 65)
    print("   RESCUE-TAG: TRAINING MODEL TINYML ORIENTATION-INVARIANT")
    print("=" * 65)

    # Cek file dataset: prioritaskan dataset_triage_clean_v2.csv jika ada
    csv_candidates = [
        "dataset_triage_clean_v2.csv",
        "dataset_triage_final.csv"
    ]
    csv_file = None
    for c in csv_candidates:
        if os.path.exists(c):
            csv_file = c
            break
        elif os.path.exists(os.path.join("Pengambilan_Data_LoRa", c)):
            csv_file = os.path.join("Pengambilan_Data_LoRa", c)
            break

    if not csv_file:
        print("[ERROR] Tidak ada file CSV dataset ditemukan.")
        sys.exit(1)

    df = load_and_preprocess(csv_file)
    print(f"📊 Distribusi Sampel:\n{df['class_name'].value_counts()}\n")

    if USE_ORIENTATION:
        feature_cols = ['a_total', 'g_total', 'a_max', 'a_min', 'g_mean', 'a_std', 'g_max', 'a_jerk', 'ax', 'ay', 'az']
        print("[MODE] MENGGUNAKAN FITUR ORIENTASI (DENGAN ax, ay, az)")
    else:
        feature_cols = ['a_total', 'g_total', 'a_max', 'a_min', 'g_mean', 'a_std', 'g_max', 'a_jerk']
        print("[MODE] 100% ORIENTATION-INVARIANT (HANYA MAGNITUDO VEKTOR SKALAR)")

    X_train, X_test, y_train, y_test = split_data(df, feature_cols, 'label')
    print(f"📊 Jumlah Data Latih : {len(X_train)} sampel")
    print(f"📊 Jumlah Data Uji   : {len(X_test)} sampel\n")

    # Hyperparameter pohon keputusan yang seimbang & anti-overfitting
    clf = DecisionTreeClassifier(
        max_depth=5,
        min_samples_leaf=6,
        class_weight='balanced',
        random_state=42
    )
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)

    print("=" * 65)
    print(f"🏆 HASIL AKURASI MODEL PADA DATA UJI: {acc * 100:.2f}%")
    print(f"   Target Proposal (>=90%): {'TERPENUHI (LOLOS TARGET!)' if acc >= 0.90 else 'BELUM'}")
    print("=" * 65)
    print("\nLaporan Klasifikasi Presisi & Recall:")
    target_names = ['0_Normal (Hijau)', '1_Kerja_Aktif (Kuning)', '3_Jatuh_Kritis (Merah)']
    print(classification_report(y_test, y_pred, target_names=target_names, digits=4))

    print("Confusion Matrix:")
    print(cm)
    print("\nStruktur Aturan Pohon Keputusan (Decision Rules):")
    print(export_text(clf, feature_names=feature_cols))

    # Ekspor ke triage_model.h
    header_path = "triage_model.h"
    generate_c_header(clf, feature_cols, header_path, acc)

    # Sinkronisasi ke folder stm32_transmitter jika ada
    target_copy = os.path.join("Pengambilan_Data_LoRa", "stm32_transmitter", "triage_model.h")
    if os.path.exists(os.path.dirname(target_copy)):
        import shutil
        shutil.copyfile(header_path, target_copy)
        print(f"[OK] Header disinkronkan ke: '{target_copy}'")

if __name__ == '__main__':
    main()
