@echo off
title PELATIHAN MODEL TINYML LOSO (RESCUE-TAG 50 Hz)
color 0D
cd /d "%~dp0"
echo ======================================================================
echo    RESCUE-TAG: PELATIHAN ^& EVALUASI LEAVE-ONE-SESSION-OUT (LOSO)     
echo           Skrip Standar Auditor Technocorner 2026 (UGM)              
echo ======================================================================
echo.

if exist "Pengambilan_Data_LoRa\log_dataset_audit_clean.txt" (
    echo [*] Menggunakan dataset bersih: Pengambilan_Data_LoRa\log_dataset_audit_clean.txt
    python "Pengambilan_Data_LoRa\catatan audit\train_triage_loso.py" "Pengambilan_Data_LoRa\log_dataset_audit_clean.txt" --depth 4 --red-min-amax 1.6 --out "Pengambilan_Data_LoRa\stm32_transmitter\triage_model.h"
) else (
    echo [*] File Pengambilan_Data_LoRa\log_dataset_audit_clean.txt belum ditemukan.
    echo [*] Menjalankan evaluasi pada log_firmware_50hz.txt...
    python "Pengambilan_Data_LoRa\catatan audit\train_triage_loso.py" "log_firmware_50hz.txt" --depth 4 --red-min-amax 1.6 --out "Pengambilan_Data_LoRa\stm32_transmitter\triage_model.h"
)

echo.
echo ======================================================================
echo   PELATIHAN SELESAI!
echo   File Header: Pengambilan_Data_LoRa\stm32_transmitter\triage_model.h
echo   Laporan    : laporan_evaluasi.md
echo ======================================================================
echo.
pause
