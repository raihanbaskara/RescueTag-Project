@echo off
title RESCUE-TAG DATA RECORDER (50 Hz WIRELESS LORA)
color 0B
cd /d "%~dp0"

:MENU
cls
echo ======================================================================
echo          RESCUE-TAG: PENGAMBILAN DATA ^& PELATIHAN TINYML (50 Hz)     
echo                   Protokol Standar Auditor Technocorner 2026         
echo ======================================================================
echo.
echo   PILIH MODE OPERASI:
echo.
echo   [1] MODE PANDUAN PROTOKOL OTOMATIS (SANGAT DIREKOMENDASIKAN)
echo       - Dipandu langkah demi langkah (D1-D8, K1-K12, J1-J20)
echo       - Ada aba-aba suara BIP saat mulai & saat jatuh ke kasur
echo       - Otomatis ganti sesi, timer hitung mundur, 100%% bebas salah label
echo.
echo   [2] MODE MANUAL BEBAS
echo       - Kontrol tombol keyboard: [0]=Diam, [1]=Kerja, [3]=Jatuh
echo       - Tombol [n]=Sesi Baru, [x]=Jeda/Skip, [q]=Selesai
echo.
echo   [3] JALANKAN PELATIHAN & EVALUASI JUJUR (train_triage_loso.py)
echo       - Evaluasi Leave-One-Session-Out (LOSO)
echo       - Otomatis ekspor header triage_model.h ke firmware STM32
echo.
echo   [4] KELUAR
echo.
echo ======================================================================
set /p opt="Ketik nomor pilihan (1/2/3/4) lalu tekan ENTER: "

if "%opt%"=="1" goto GUIDED
if "%opt%"=="2" goto MANUAL
if "%opt%"=="3" goto TRAIN
if "%opt%"=="4" goto END
goto MENU

:GUIDED
cls
color 0A
python Pengambilan_Data_LoRa\record_guided_protocol.py
echo.
echo ======================================================================
echo   Perekaman Sesi Panduan Selesai!
echo ======================================================================
pause
goto MENU

:MANUAL
cls
color 0E
python Pengambilan_Data_LoRa\record_lora_wireless.py
echo.
echo ======================================================================
echo   Perekaman Manual Selesai!
echo ======================================================================
pause
goto MENU

:TRAIN
cls
color 0D
echo ======================================================================
echo   MENJALANKAN PELATIHAN TINYML LEAVE-ONE-SESSION-OUT (LOSO)
echo ======================================================================
if exist "Pengambilan_Data_LoRa\log_dataset_audit_clean.txt" (
    python "Pengambilan_Data_LoRa\catatan audit\train_triage_loso.py" "Pengambilan_Data_LoRa\log_dataset_audit_clean.txt" --out "Pengambilan_Data_LoRa\stm32_transmitter\triage_model.h"
) else (
    echo [!] File 'Pengambilan_Data_LoRa\log_dataset_audit_clean.txt' belum ada.
    echo [*] Menguji dengan log sebelumnya 'log_firmware_50hz.txt'...
    python "Pengambilan_Data_LoRa\catatan audit\train_triage_loso.py" "log_firmware_50hz.txt" --out "Pengambilan_Data_LoRa\stm32_transmitter\triage_model.h"
)
echo.
pause
goto MENU

:END
exit
