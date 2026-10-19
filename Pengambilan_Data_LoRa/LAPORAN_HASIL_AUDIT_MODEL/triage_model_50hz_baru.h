// ========================================================
// MODEL TINYML DECISION TREE RESCUE-TAG (FIRMWARE 50 Hz)
// Tanggal Latih : 2026-10-05
// Dataset       : log_firmware_50hz.txt (503 window, 15 sesi nirkabel)
// Akurasi       : 94.83% (Target Proposal >= 90%)
// Karakteristik : 100% Orientation-Invariant (Tanpa ax, ay, az)
// False Alarm   : 0% pada kondisi duduk/diam santai
// ========================================================
#ifndef TRIAGE_MODEL_H
#define TRIAGE_MODEL_H

#include <math.h>

static inline int predict_triage(float a_total, float g_total, float a_max, float a_min,
                                 float g_mean, float a_std, float g_max, float a_jerk) {
  (void)a_jerk;
  if (g_mean <= 68.1120f) {
    if (a_std <= 0.0048f) {
        if (g_total <= 2.1070f) {
            return 0; // Kelas: 0
          } else {
            if (a_std <= 0.0008f) {
                return 0; // Kelas: 0
              } else {
                return 0; // Kelas: 0
              }
          }
      } else {
        if (a_total <= 1.0141f) {
            if (a_min <= 1.0104f) {
                return 0; // Kelas: 0
              } else {
                return 1; // Kelas: 1
              }
          } else {
            if (a_min <= 1.0413f) {
                return 0; // Kelas: 0
              } else {
                return 1; // Kelas: 1
              }
          }
      }
  } else {
    if (a_std <= 0.3959f) {
        if (g_total <= 48.6140f) {
            if (a_min <= 1.0229f) {
                return 0; // Kelas: 0
              } else {
                return 1; // Kelas: 1
              }
          } else {
            if (g_mean <= 122.2270f) {
                return 1; // Kelas: 1
              } else {
                return 1; // Kelas: 1
              }
          }
      } else {
        if (g_max <= 400.6130f) {
            if (g_mean <= 185.9115f) {
                return 3; // Kelas: 3
              } else {
                return 1; // Kelas: 1
              }
          } else {
            return 1; // Kelas: 1
          }
      }
  }
}

#endif // TRIAGE_MODEL_H
