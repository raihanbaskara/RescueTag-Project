// ========================================================
// MODEL DECISION TREE RESCUE-TAG (firmware 50 Hz)  -  dibuat oleh train_triage_loso.py
// Data: 2115 jendela, 46 sesi, 35 kejadian jatuh | LOSO acc 80.8%, macro-F1 76.3%, jatuh 31/35
// Orientation-invariant: tanpa ax, ay, az.  Label: 0 Hijau, 1 Kuning, 3 Merah.
// ========================================================
#ifndef TRIAGE_MODEL_H
#define TRIAGE_MODEL_H

static inline int predict_triage(float a_total, float g_total, float a_max, float a_min,
                                 float g_mean, float a_std, float g_max, float a_jerk) {
  (void)a_jerk;
  if (a_max <= 1.5982f) {
    if (a_max <= 1.2609f) {
      if (g_max <= 16.5235f) {
        if (a_min <= 1.0737f) {
          return 0;
        } else {
          return 1;
        }
      } else {
        return 0;
      }
    } else {
      if (g_total <= 32.4030f) {
        if (g_max <= 109.6955f) {
          return 1;
        } else {
          return 0;
        }
      } else {
        return 1;
      }
    }
  } else {
    if (a_max <= 5.3635f) {
      if (g_mean <= 178.0555f) {
        if (g_max <= 253.7355f) {
          return 1;
        } else {
          return 3;
        }
      } else {
        return 1;
      }
    } else {
      if (a_max <= 10.5539f) {
        if (a_std <= 2.6111f) {
          return 3;
        } else {
          return 1;
        }
      } else {
        return 3;
      }
    }
  }
}

#endif // TRIAGE_MODEL_H
