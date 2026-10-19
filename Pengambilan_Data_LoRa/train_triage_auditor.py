"""
Latih decision tree Rescue-Tag dari log Serial jam (baris "FEAT,...") dan ekspor triage_model.h.

Cara pakai di Google Colab:
  1. Upload file ini, atau tempel isinya ke satu sel, lalu jalankan.
  2. Saat diminta, upload satu atau lebih file log (hasil salin Serial Monitor, .txt / .csv / .log).
  3. triage_model.h otomatis terunduh. Salin ke folder sketch Arduino menggantikan yang lama.

Cara pakai di laptop:  python train_triage.py log1.txt log2.txt

Format baris log (dicetak firmware, boleh ada awalan jam dari Serial Monitor):
  FEAT,sesi,label,a_total,g_total,a_max,a_min,g_mean,a_std,g_max,ax,ay,az,prediksi_model,status
"""
import glob
import sys
import datetime

import numpy as np
import pandas as pd
from sklearn.metrics import (accuracy_score, balanced_accuracy_score,
                             confusion_matrix, precision_score, recall_score)
from sklearn.model_selection import GroupKFold, cross_val_predict
from sklearn.tree import DecisionTreeClassifier, export_text

# ======================= PENGATURAN =======================
USE_ORIENTATION = False         # False = buang ax, ay, az (100% Orientation-Invariant sesuai saran audit)
RED_WEIGHT_GRID = [1, 2, 3, 5]  # bobot kelas Merah yang dicoba (naikkan = recall Merah naik, alarm palsu naik)
DEPTH_GRID = [3, 4, 5, 6]
LEAF_GRID = [5, 10, 20]         # min sampel per daun; makin besar makin tahan overfit
SKIP_AFTER_CHANGE = 8           # buang N baris pertama tiap ganti label/sesi (window masih berisi data kegiatan lama)
OUT_HEADER = "triage_model.h"
OUT_PNG = "confusion_matrix.png"
# ==========================================================

COLS = ["sess", "label", "a_total", "g_total", "a_max", "a_min", "g_mean", "a_std",
        "g_max", "ax", "ay", "az", "model_pred", "triage"]
FEATS_ALL = ["a_total", "g_total", "a_max", "a_min", "g_mean", "a_std", "g_max", "ax", "ay", "az"]
FEATS_NO_ORI = [f for f in FEATS_ALL if f not in ("ax", "ay", "az")]
CLASS_NAMES = {0: "Hijau", 1: "Kuning", 3: "Merah"}


def load_feat(path):
    rows = []
    with open(path, errors="ignore") as f:
        for line in f:
            i = line.find("FEAT,")
            if i < 0:
                continue
            p = line[i + 5:].strip().split(",")
            if len(p) != len(COLS):
                continue
            try:
                rows.append([float(x) for x in p])
            except ValueError:
                continue
    df = pd.DataFrame(rows, columns=COLS)
    df["group"] = path + ":" + df["sess"].astype(int).astype(str)
    return df


def prepare(paths):
    df = pd.concat([load_feat(p) for p in paths], ignore_index=True)
    df["label"] = df["label"].astype(int)
    # buang baris awal tiap segmen (group, label) karena window-nya masih campur kegiatan sebelumnya
    seg = ((df["group"] != df["group"].shift()) | (df["label"] != df["label"].shift())).cumsum()
    df = df[df.groupby(seg).cumcount() >= SKIP_AFTER_CHANGE].reset_index(drop=True)
    df = df.replace([np.inf, -np.inf], np.nan).dropna(subset=FEATS_ALL)
    return df


def make_clf(depth, leaf, red_w):
    return DecisionTreeClassifier(criterion="entropy", max_depth=depth, min_samples_leaf=leaf,
                                  class_weight={0: 1, 1: 1, 3: red_w}, random_state=42)


def search(df, feats, nfold):
    X, y, g = df[feats], df["label"], df["group"]
    best = None
    for depth in DEPTH_GRID:
        for leaf in LEAF_GRID:
            for w in RED_WEIGHT_GRID:
                pred = cross_val_predict(make_clf(depth, leaf, w), X, y, groups=g,
                                         cv=GroupKFold(n_splits=nfold))
                rec_red = recall_score(y, pred, labels=[3], average="macro", zero_division=0)
                score = 0.5 * (balanced_accuracy_score(y, pred) + rec_red)
                if best is None or score > best["score"]:
                    best = dict(score=score, depth=depth, leaf=leaf, w=w, pred=pred)
    return best


# ---------- ekspor ke C ----------
def build(tree, node, classes):
    t = tree.tree_
    if t.children_left[node] == -1:
        return ("leaf", int(classes[np.argmax(t.value[node][0])]))
    l = build(tree, t.children_left[node], classes)
    r = build(tree, t.children_right[node], classes)
    if l[0] == "leaf" and r[0] == "leaf" and l[1] == r[1]:
        return l  # cabang kembar digabung
    return ("split", int(t.feature[node]), float(t.threshold[node]), l, r)


def emit(n, names, depth):
    pad = "  " * depth
    if n[0] == "leaf":
        return f"{pad}return {n[1]}; // {CLASS_NAMES[n[1]]}\n"
    _, fi, thr, l, r = n
    return (f"{pad}if ({names[fi]} <= {thr:.4f}f) {{\n" + emit(l, names, depth + 1) +
            f"{pad}}} else {{\n" + emit(r, names, depth + 1) + f"{pad}}}\n")


def export_header(clf, feats, info, path):
    root = build(clf, 0, clf.classes_)
    body = emit(root, feats, 1)
    h = f"""// ========================================================
// MODEL DECISION TREE RESCUE-TAG (digenerate otomatis oleh train_triage.py)
// Dibuat   : {datetime.datetime.now():%Y-%m-%d %H:%M}
// Data     : {info}
// Fitur    : {', '.join(feats)}
// Label    : 0 = Hijau, 1 = Kuning, 3 = Merah
// ========================================================
#ifndef TRIAGE_MODEL_H
#define TRIAGE_MODEL_H

#include <math.h>

// Parameter yang tidak dipakai pohon (a_jerk dan fitur yang dibuang) diabaikan.
static inline int predict_triage(float a_total, float g_total, float a_max, float a_min,
                                 float g_mean, float a_std, float g_max, float a_jerk) {{
  (void)a_total; (void)g_total; (void)a_max; (void)a_min;
  (void)g_mean; (void)a_std; (void)g_max; (void)a_jerk;
{body}}}

#endif // TRIAGE_MODEL_H
"""
    open(path, "w").write(h)


def main(paths):
    df = prepare(paths)
    n_sess = df["group"].nunique()
    print(f"Data: {len(df)} window, {n_sess} sesi")
    print(df.groupby("label").agg(window=("label", "size"), sesi=("group", "nunique")).rename(index=CLASS_NAMES))

    if set(df["label"].unique()) != {0, 1, 3}:
        sys.exit("ERROR: butuh data untuk ketiga label (0, 1, 3).")
    few = df.groupby("label")["group"].nunique()
    if (few < 2).any():
        sys.exit("ERROR: tiap kelas butuh minimal 2 sesi berbeda (ketik 'n' di Serial Monitor tiap ganti kegiatan).")
    if (few < 4).any():
        print("PERINGATAN: ada kelas dengan <4 sesi; hasil CV masih sangat kasar. Rekam lebih banyak sesi.")
    nfold = min(5, n_sess)

    results = {}
    for name, feats in (("dengan orientasi (ax,ay,az)", FEATS_ALL), ("tanpa orientasi", FEATS_NO_ORI)):
        b = search(df, feats, nfold)
        results[name] = (feats, b)
        rec = recall_score(df["label"], b["pred"], labels=[0, 1, 3], average=None, zero_division=0)
        print(f"\n[{name}] depth={b['depth']} leaf={b['leaf']} bobotMerah={b['w']}  "
              f"akurasi CV per-sesi={accuracy_score(df['label'], b['pred']):.3f}  "
              f"recall H/K/M={np.round(rec, 3).tolist()}")

    key = "dengan orientasi (ax,ay,az)" if USE_ORIENTATION else "tanpa orientasi"
    feats, b = results[key]
    y, pred = df["label"], b["pred"]
    labs = [0, 1, 3]
    print(f"\n=== MODEL TERPILIH: {key} ===")
    cm = confusion_matrix(y, pred, labels=labs)
    print(pd.DataFrame(cm, index=[f"aktual {CLASS_NAMES[l]}" for l in labs],
                       columns=[f"pred {CLASS_NAMES[l]}" for l in labs]))
    for l, r, p in zip(labs, recall_score(y, pred, labels=labs, average=None, zero_division=0),
                       precision_score(y, pred, labels=labs, average=None, zero_division=0)):
        print(f"  {CLASS_NAMES[l]:7s} recall={r:.3f}  precision={p:.3f}")
    print("Angka ini dari validasi silang PER SESI (sesi uji tidak pernah dilihat saat latih).")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import seaborn as sns
        plt.figure(figsize=(5.5, 4.5))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                    xticklabels=[CLASS_NAMES[l] for l in labs], yticklabels=[CLASS_NAMES[l] for l in labs])
        plt.xlabel("Prediksi model"); plt.ylabel("Kondisi aktual")
        plt.title(f"Confusion matrix validasi per-sesi (akurasi {accuracy_score(y, pred):.1%})")
        plt.tight_layout(); plt.savefig(OUT_PNG, dpi=150)
        print("Gambar:", OUT_PNG)
    except Exception as e:  # gambar opsional
        print("Lewati gambar:", e)

    final = make_clf(b["depth"], b["leaf"], b["w"]).fit(df[feats], df["label"])
    print("\nPohon akhir (dilatih dari semua data):")
    print(export_text(final, feature_names=feats))
    export_header(final, feats, f"{len(df)} window, {n_sess} sesi; CV per-sesi akurasi {accuracy_score(y, pred):.1%}", OUT_HEADER)
    print("Header ditulis:", OUT_HEADER)


if __name__ == "__main__":
    try:
        from google.colab import files  # type: ignore
        IN_COLAB = True
    except ImportError:
        IN_COLAB = False

    if IN_COLAB:
        up = files.upload()
        main(list(up.keys()))
        files.download(OUT_HEADER)
    else:
        paths = sys.argv[1:] or sorted(glob.glob("*.txt") + glob.glob("*.log") + glob.glob("feat*.csv"))
        if not paths:
            sys.exit("Beri nama file log: python train_triage.py log1.txt log2.txt")
        main(paths)
