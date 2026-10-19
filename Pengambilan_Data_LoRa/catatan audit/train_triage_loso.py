#!/usr/bin/env python3
"""
train_triage_loso.py  -  Latih decision tree Rescue-Tag + evaluasi JUJUR per sesi.

Pakai:
    python3 train_triage_loso.py log_firmware_50hz.txt [log_lain.txt ...]
    python3 train_triage_loso.py log.txt --depth 4 --red-min-amax 1.6 --out triage_model.h

Input : baris FEAT dari firmware 50 Hz
        FEAT,sesi,label,a_total,g_total,a_max,a_min,g_mean,a_std,g_max,ax,ay,az,pred,triage
        (beberapa file digabung; nomor sesi otomatis dibuat unik per file)
Output: - tabel evaluasi (leave-one-session-out) di layar + laporan_evaluasi.md
        - triage_model.h  (predict_triage 8 argumen, orientation-invariant)

Prinsip yang dijaga skrip ini:
  1. Evaluasi SELALU per sesi (satu sesi penuh ditahan sebagai data uji). Akurasi di data latih
     hanya dicetak sebagai pembanding dan diberi label jelas.
  2. Label Jatuh (3) hanya untuk jendela benturan (a_max >= --red-min-amax). Fase diam setelah
     jatuh diperlakukan sebagai Diam; itu tugas FSM imobilitas di firmware.
  3. Metrik dilaporkan per kelas dan per KEJADIAN jatuh, bukan hanya akurasi total.
  4. Ada baseline aturan sederhana (a_max >= ambang) sebagai pembanding.
"""
import argparse, sys, math
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support

COLS = ['tag', 'sess', 'label', 'a_total', 'g_total', 'a_max', 'a_min', 'g_mean',
        'a_std', 'g_max', 'ax', 'ay', 'az', 'pred', 'tri']
FEATS = ['a_total', 'g_total', 'a_max', 'a_min', 'g_mean', 'a_std', 'g_max', 'a_jerk']
USE = ['a_total', 'g_total', 'a_max', 'a_min', 'g_mean', 'a_std', 'g_max']  # a_jerk tak dipakai
NAMA = {0: 'Diam (Hijau)', 1: 'Kerja (Kuning)', 3: 'Jatuh (Merah)'}
WINDOW_S = 0.25  # satu baris FEAT = 250 ms


def load(paths):
    frames, offset = [], 0
    for p in paths:
        rows = []
        with open(p, encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line.startswith('FEAT,'):
                    continue
                parts = line.split(',')
                if len(parts) < 15:
                    continue
                try:
                    rows.append([parts[0]] + [float(x) for x in parts[1:15]])
                except ValueError:
                    continue
        d = pd.DataFrame(rows, columns=COLS)
        if d.empty:
            sys.exit(f'Tidak ada baris FEAT valid di {p}')
        d['sess'] = d['sess'].astype(int) + offset
        d['file'] = p
        offset = d['sess'].max() + 1
        frames.append(d)
    d = pd.concat(frames, ignore_index=True)
    d['label'] = d['label'].astype(int)
    d['a_jerk'] = 0.0
    return d


def relabel(d, red_min_amax):
    d = d.copy()
    d['y'] = d['label']
    d.loc[(d['label'] == 3) & (d['a_max'] < red_min_amax), 'y'] = 0
    return d


def fall_events(d, merge_gap=3):
    """Kejadian jatuh = run baris y==3 berurutan dalam satu sesi (celah <= merge_gap digabung)."""
    ev = []
    for s, g in d.groupby('sess'):
        idx = np.where(g['y'].values == 3)[0]
        if len(idx) == 0:
            continue
        start = prev = idx[0]
        for i in idx[1:]:
            if i - prev > merge_gap:
                ev.append((s, g.index[start], g.index[prev]))
                start = i
            prev = i
        ev.append((s, g.index[start], g.index[prev]))
    return ev


def make_tree(depth, leaf, w_red):
    return DecisionTreeClassifier(criterion='entropy', max_depth=depth, min_samples_leaf=leaf,
                                  class_weight={0: 1.0, 1: 1.0, 3: w_red}, random_state=0)


def loso_predict(d, depth, leaf, w_red):
    X, y, g = d[USE].values, d['y'].values, d['sess'].values
    pred = np.zeros(len(d), int)
    for tr, te in LeaveOneGroupOut().split(X, y, g):
        m = make_tree(depth, leaf, w_red).fit(X[tr], y[tr])
        pred[te] = m.predict(X[te])
    return pred


def event_recall(d, pred, events):
    hit = 0
    for s, a, b in events:
        if (pred[d.index.get_indexer(range(a, b + 1))] == 3).any():
            hit += 1
    return hit, len(events)


def false_red_rows(d, pred):
    return int(((pred == 3) & (d['y'].values != 3)).sum())


def per_class_table(y, p):
    labs = [0, 1, 3]
    pr, rc, f1, sup = precision_recall_fscore_support(y, p, labels=labs, zero_division=0)
    lines = ['| Kelas | Jumlah jendela | Presisi | Recall | F1 |', '|---|---:|---:|---:|---:|']
    for i, l in enumerate(labs):
        lines.append(f'| {NAMA[l]} | {sup[i]} | {pr[i]*100:.1f}% | {rc[i]*100:.1f}% | {f1[i]*100:.1f}% |')
    return '\n'.join(lines), float(np.mean(f1))


def conf_table(y, p):
    cm = confusion_matrix(y, p, labels=[0, 1, 3])
    lines = ['| Aktual \\ Prediksi | Diam | Kerja | Jatuh |', '|---|---:|---:|---:|']
    for i, l in enumerate([0, 1, 3]):
        lines.append(f'| {NAMA[l]} | {cm[i,0]} | {cm[i,1]} | {cm[i,2]} |')
    return '\n'.join(lines)


# ---------- ekspor C ----------
def tree_to_c(tree, names, classes):
    t = tree.tree_

    def leaf_class(n):
        return int(classes[np.argmax(t.value[n][0])])

    def simplify(n):
        """Kembalikan kelas tunggal bila seluruh subtree menghasilkan kelas sama (buang cabang mubazir)."""
        if t.children_left[n] == -1:
            return leaf_class(n)
        l, r = simplify(t.children_left[n]), simplify(t.children_right[n])
        return l if (isinstance(l, int) and isinstance(r, int) and l == r) else None

    out = []

    def emit(n, ind):
        pad = '  ' * ind
        s = simplify(n)
        if s is not None:
            out.append(f'{pad}return {s};')
            return
        f, th = names[t.feature[n]], t.threshold[n]
        out.append(f'{pad}if ({f} <= {th:.4f}f) {{')
        emit(t.children_left[n], ind + 1)
        out.append(f'{pad}}} else {{')
        emit(t.children_right[n], ind + 1)
        out.append(f'{pad}}}')

    emit(0, 1)
    return '\n'.join(out)


def write_header(path, model, meta):
    body = tree_to_c(model, USE, model.classes_)
    h = f"""// ========================================================
// MODEL DECISION TREE RESCUE-TAG (firmware 50 Hz)  -  dibuat oleh train_triage_loso.py
// {meta}
// Orientation-invariant: tanpa ax, ay, az.  Label: 0 Hijau, 1 Kuning, 3 Merah.
// ========================================================
#ifndef TRIAGE_MODEL_H
#define TRIAGE_MODEL_H

static inline int predict_triage(float a_total, float g_total, float a_max, float a_min,
                                 float g_mean, float a_std, float g_max, float a_jerk) {{
  (void)a_jerk;
{body}
}}

#endif // TRIAGE_MODEL_H
"""
    open(path, 'w', encoding='utf-8').write(h)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('logs', nargs='+')
    ap.add_argument('--depth', type=int, default=None, help='kedalaman tree (default: dipilih lewat LOSO)')
    ap.add_argument('--leaf', type=int, default=None, help='min_samples_leaf (default: dipilih lewat LOSO)')
    ap.add_argument('--w-red', type=float, default=5.0, help='bobot kelas Merah')
    ap.add_argument('--red-min-amax', type=float, default=1.6, help='a_max minimum untuk jendela Jatuh')
    ap.add_argument('--baseline-amax', type=float, default=2.2, help='ambang baseline aturan sederhana')
    ap.add_argument('--out', default='triage_model.h')
    ap.add_argument('--report', default='laporan_evaluasi.md')
    a = ap.parse_args()

    d = relabel(load(a.logs), a.red_min_amax)
    events = fall_events(d)
    L = []
    P = L.append

    # ---------- profil data ----------
    sess = d.groupby('sess').agg(n=('y', 'size'), label=('label', lambda s: sorted(set(s))),
                                 y=('y', lambda s: sorted(set(s))),
                                 amax=('a_max', 'max'), gmax=('g_max', 'max'))
    P('# Evaluasi model triage (leave-one-session-out)\n')
    P('## 1. Profil data\n')
    P(f'- Total jendela (250 ms): **{len(d)}** dari **{d.sess.nunique()} sesi** ({len(d)*WINDOW_S/60:.1f} menit)')
    P(f"- Jendela Jatuh asli (label 3): {(d.label==3).sum()}; setelah hanya jendela benturan "
      f"(a_max >= {a.red_min_amax} g): **{(d.y==3).sum()}** | diubah jadi Diam: "
      f"{((d.label==3)&(d.y==0)).sum()} (fase diam pascajatuh, ditangani FSM)")
    P('')
    cnt = d.groupby('y')['sess'].nunique()
    P('| Kelas | Jendela | Sesi |\n|---|---:|---:|')
    for l in (0, 1, 3):
        P(f'| {NAMA[l]} | {(d.y==l).sum()} | {int(cnt.get(l, 0))} |')
    P(f'\n- **Kejadian jatuh terpisah: {len(events)}** (run jendela Jatuh berurutan)')

    warn = []
    if len(events) < 15:
        warn.append(f'Kejadian jatuh hanya {len(events)} (<15): hasil Merah belum bisa dipercaya. Rekam 20-30 kejadian.')
    if cnt.get(3, 0) < 5:
        warn.append(f'Sesi Jatuh hanya {int(cnt.get(3,0))} (<5): variasi pose/arah/ketinggian kurang.')
    if cnt.get(1, 0) < 8:
        warn.append(f'Sesi Kerja hanya {int(cnt.get(1,0))} (<8): perbanyak variasi aktivitas dan negatif sulit.')
    if cnt.get(0, 0) < 6:
        warn.append(f'Sesi Diam hanya {int(cnt.get(0,0))} (<6).')
    for s, r in sess.iterrows():
        if len(r['label']) > 1:
            warn.append(f'Sesi {s} berisi label campuran {r["label"]} - pisahkan per aktivitas dengan tombol n.')
        if r['y'] != [3] and r['label'] != [3] and r['amax'] >= 2.2:
            warn.append(f'Sesi {s} (label {r["label"]}) punya a_max {r["amax"]:.1f} g (setara benturan) - pastikan label benar.')
        if r['n'] < 10:
            warn.append(f'Sesi {s} sangat pendek ({r["n"]} jendela).')
    if warn:
        P('\n### Peringatan kualitas data\n')
        for w in warn:
            P(f'- {w}')

    # ---------- pilih hiperparameter lewat LOSO ----------
    grid_d = [a.depth] if a.depth else [3, 4, 5]
    grid_l = [a.leaf] if a.leaf else [1, 3, 5]
    best = None
    res = []
    for dep in grid_d:
        for lf in grid_l:
            p = loso_predict(d, dep, lf, a.w_red)
            _, macro = per_class_table(d.y.values, p)
            h, n = event_recall(d, p, events)
            fr = false_red_rows(d, p)
            res.append((dep, lf, macro, h, n, fr))
            key = (macro, h, -fr)
            if best is None or key > best[0]:
                best = (key, dep, lf, p)
    _, dep, lf, pred = best
    P('\n## 2. Pemilihan hiperparameter (LOSO)\n')
    P('| Kedalaman | min leaf | Macro-F1 | Kejadian jatuh terdeteksi | Jendela salah-Merah |\n|---:|---:|---:|---:|---:|')
    for r in res:
        mark = ' **<- dipilih**' if (r[0], r[1]) == (dep, lf) else ''
        P(f'| {r[0]} | {r[1]} | {r[2]*100:.1f}% | {r[3]}/{r[4]} | {r[5]} |{mark}')
    P('\n*Catatan: hiperparameter dipilih dari hasil LOSO yang sama, jadi angka terbaik sedikit optimistis; '
      'perlu data uji sesi baru untuk angka final.*')

    # ---------- hasil LOSO ----------
    y = d.y.values
    P('\n## 3. Hasil leave-one-session-out (data uji = sesi yang tidak dilatih)\n')
    P(f'- Akurasi per jendela: **{(pred==y).mean()*100:.1f}%**')
    tab, macro = per_class_table(y, pred)
    P(f'- Macro-F1: **{macro*100:.1f}%**\n')
    P(tab)
    P('\nConfusion matrix:\n')
    P(conf_table(y, pred))
    h, n = event_recall(d, pred, events)
    fr = false_red_rows(d, pred)
    nonfall_min = ((y != 3).sum()) * WINDOW_S / 60
    P(f'\n- **Recall Merah tingkat kejadian: {h}/{n}**' + (f' ({h/n*100:.0f}%)' if n else ''))
    P(f'- Jendela non-jatuh yang salah diprediksi Merah: **{fr}** dari {(y!=3).sum()} '
      f'(~{fr/max(nonfall_min,1e-9):.1f} per menit data non-jatuh)')
    P('\nPer sesi (LOSO):\n')
    P('| Sesi | Label | Jendela | Akurasi | Pred Merah (benar/salah) |\n|---:|---|---:|---:|---|')
    for s, g in d.groupby('sess'):
        ix = d.index.get_indexer(g.index)
        ok = (pred[ix] == y[ix]).mean() * 100
        tp = int(((pred[ix] == 3) & (y[ix] == 3)).sum())
        fp = int(((pred[ix] == 3) & (y[ix] != 3)).sum())
        P(f'| {s} | {sorted(set(g.label))} | {len(g)} | {ok:.0f}% | {tp}/{fp} |')

    # ---------- baseline ----------
    base = np.where(d['a_max'].values >= a.baseline_amax, 3, 0)
    hb, nb = event_recall(d, base, events)
    P(f'\n## 4. Baseline aturan sederhana (a_max >= {a.baseline_amax} g -> Merah, selain itu Diam)\n')
    P(f'- Kejadian jatuh terdeteksi: {hb}/{nb}; jendela non-jatuh salah-Merah: '
      f'{int(((base==3)&(y!=3)).sum())}')
    P('- Jika tree tidak lebih baik dari baseline pada kedua angka ini, jelaskan peran tree sebagai '
      'penyaring false alarm/pembeda Kerja vs Diam, dan andalkan FSM untuk keputusan Merah.')

    # ---------- model akhir ----------
    final = make_tree(dep, lf, a.w_red).fit(d[USE].values, y)
    train_acc = (final.predict(d[USE].values) == y).mean()
    P('\n## 5. Model akhir (dilatih pada SEMUA sesi)\n')
    P(f'- Kedalaman {dep}, min leaf {lf}, bobot Merah {a.w_red}')
    P(f'- Akurasi di data latih: {train_acc*100:.1f}%  *(hanya pembanding; JANGAN dilaporkan sebagai akurasi model)*')
    write_header(a.out, final, f'Data: {len(d)} jendela, {d.sess.nunique()} sesi, {len(events)} kejadian jatuh | '
                               f'LOSO acc {(pred==y).mean()*100:.1f}%, macro-F1 {macro*100:.1f}%, jatuh {h}/{n}')
    P(f'- Header ditulis ke `{a.out}`')

    text = '\n'.join(L)
    open(a.report, 'w', encoding='utf-8').write(text)
    print(text)
    print(f'\n[Selesai] Laporan: {a.report} | Header: {a.out}')


if __name__ == '__main__':
    main()
