# -*- coding: utf-8 -*-
"""
Build script v2 for RescueTag Command Center.
Fully addresses user request:
1. Sizing: Match Image 3 / health_overview_dashboard.html:
   - Width: 1180px, Height: 856px, 3-column (84px | 1fr | 414px) Doppelrand container.
2. Color Palette Unified:
   - Warm Sand #FAF6F1, White cards #FFFFFF with #F0ECE6 borders, Dark Charcoal #2D2B2A text.
   - Fleet Roster, GIS Map, Audit Trail, and Hardware Spec now share the exact same palette as Command Overview.
   - No dark floating modals! All views are full integrated views inside the center container.
3. Remove "Hardware REV 2.0":
   - Changed to "RescueTag Wearable Smartwatch" as explicitly requested.
4. Download Excel:
   - Built-in Excel/CSV export with UTF-8 BOM for Microsoft Excel.
5. Zero emojis, pure high-end typography and spring physics.
"""

import os
import base64

# Read base64 image
with open('smartwatch_grey_oled.png', 'rb') as f:
    b64_img = base64.b64encode(f.read()).decode('utf-8')
data_uri = f"data:image/png;base64,{b64_img}"

HTML_TEMPLATE = r'''<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>RescueTag Command Center // Subterranean Disaster Triage & LoRa 1-Hop Mesh</title>
  
  <!-- CSS & Typography -->
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Mulish:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  
  <!-- Leaflet GIS, Chart.js & MQTT.js -->
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script src="https://unpkg.com/mqtt@4.3.7/dist/mqtt.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

  <style>
    * {
      box-sizing: border-box;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
    }

    body {
      margin: 0;
      padding: 0;
      background-color: #050505;
      font-family: 'Mulish', 'Plus Jakarta Sans', sans-serif;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #2D2B2A;
      overflow-x: auto;
    }

    .font-mono {
      font-family: 'JetBrains Mono', monospace;
    }

    /* Fixed-aspect golden-ratio container matching Image 3 / health_overview_dashboard.html */
    .dashboard-wrapper {
      width: 1180px;
      min-width: 1180px;
      height: 856px;
      background-color: #FAF6F1;
      border-radius: 34px;
      display: grid;
      grid-template-columns: 84px 1fr 414px;
      overflow: hidden;
      box-shadow: 0 25px 70px rgba(0, 0, 0, 0.75);
      position: relative;
      border: 1px solid rgba(255, 255, 255, 0.14);
      user-select: none;
    }

    @media (max-width: 1220px) {
      body {
        align-items: flex-start;
        padding: 1rem;
      }
      .dashboard-wrapper {
        min-width: unset;
        width: 100%;
        max-width: 1180px;
        height: auto;
        min-height: 856px;
        grid-template-columns: 84px 1fr;
      }
      .right-tactical-panel {
        grid-column: span 2;
        border-radius: 0 0 34px 34px !important;
        border-left: none;
        border-top: 1px solid #3D3A3A;
      }
    }

    @media (max-width: 768px) {
      .dashboard-wrapper {
        grid-template-columns: 1fr;
        border-radius: 20px;
      }
      .left-sidebar {
        flex-direction: row !important;
        width: 100% !important;
        height: auto !important;
        padding: 0.75rem 1rem !important;
        border-right: none !important;
        border-bottom: 1px solid #F0ECE6 !important;
      }
      .left-sidebar nav {
        flex-direction: row !important;
        margin: 0 !important;
        gap: 0.5rem !important;
      }
      .right-tactical-panel {
        grid-column: span 1;
      }
    }

    /* Tactile Metric Cards */
    .metric-card {
      background: #FFFFFF;
      border-radius: 18px;
      border: 1px solid #F0ECE6;
      box-shadow: 0 10px 30px rgba(145, 132, 118, 0.08);
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
      transform: translateY(-2px);
      box-shadow: 0 14px 34px rgba(145, 132, 118, 0.13);
    }

    /* Action Buttons */
    .icon-btn {
      width: 40px;
      height: 40px;
      border-radius: 12px;
      background: #FFFFFF;
      border: 1px solid #EAE5DE;
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.04);
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      color: #302E2D;
      transition: all 0.15s ease;
    }
    .icon-btn:hover {
      transform: translateY(-1px);
      box-shadow: 0 6px 18px rgba(0, 0, 0, 0.08);
      background: #FAF6F1;
    }

    /* Left Nav Buttons */
    .nav-btn {
      width: 44px;
      height: 44px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #6E6D6B;
      cursor: pointer;
      transition: all 0.2s ease;
      position: relative;
    }
    .nav-btn:hover {
      background: #F4EFEA;
      color: #2B2B2B;
    }
    .nav-btn.active {
      background: #2C2A2A;
      color: #FFFFFF;
      box-shadow: 0 6px 14px rgba(44, 42, 42, 0.25);
    }

    /* START Triage Dynamic Gradient Bar */
    .triage-gradient-bar {
      height: 9px;
      border-radius: 999px;
      background: linear-gradient(90deg, 
        #9CC3EB 0%, 
        #9CE0D8 28%, 
        #CBE8BA 50%, 
        #F0E09A 74%, 
        #E59399 100%
      );
      position: relative;
      cursor: pointer;
    }

    /* Rotated X-axis timestamps */
    .x-label {
      transform: rotate(-42deg);
      transform-origin: top right;
      font-size: 9px;
      color: #8E8B86;
      font-weight: 600;
      white-space: nowrap;
      margin-top: 6px;
      letter-spacing: -0.01em;
      font-family: 'JetBrains Mono', monospace;
    }

    /* Draggable Ruler Sliders */
    .ruler-slider {
      -webkit-appearance: none;
      appearance: none;
      width: 100%;
      height: 22px;
      background: transparent;
      cursor: ew-resize;
      position: absolute;
      top: 6px;
      left: 0;
      z-index: 10;
      opacity: 0;
    }

    /* Multi-segment Pill Bars */
    .day-col:hover .pill-seg {
      filter: brightness(1.08);
      transform: scaleX(1.18);
    }
    .pill-seg {
      transition: all 0.15s ease;
    }

    /* 3D Anatomical Ring Glow Effects */
    .ring-glow {
      filter: drop-shadow(0 0 5px rgba(240, 82, 72, 0.65));
      transition: all 0.25s ease;
      cursor: pointer;
    }
    .ring-glow:hover {
      filter: drop-shadow(0 0 10px rgba(255, 95, 85, 0.95)) !important;
      transform: scale(1.03);
      transform-origin: 105px center;
    }

    .measure-card {
      transition: all 0.2s ease;
      cursor: pointer;
    }
    .measure-card:hover {
      transform: translateX(3px);
      box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25);
    }

    /* Worker Selector Switcher */
    .worker-pill-btn {
      padding: 5px 12px;
      border-radius: 10px;
      font-size: 11px;
      font-weight: 700;
      transition: all 0.2s ease;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .worker-pill-btn.active {
      background: #2C2A2A;
      color: #FFFFFF;
      box-shadow: 0 4px 10px rgba(44, 42, 42, 0.2);
    }
    .worker-pill-btn:not(.active) {
      background: #FFFFFF;
      color: #6E6B66;
      border: 1px solid #E6E1DA;
    }
    .worker-pill-btn:not(.active):hover {
      background: #F5EFEB;
      color: #2D2B2A;
    }

    /* Tactical Table */
    .warm-table th {
      font-family: 'JetBrains Mono', monospace;
      font-size: 9.5px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #8E8B86;
      padding: 10px 14px;
      text-align: left;
      border-bottom: 1px solid #F0ECE6;
    }
    .warm-table td {
      font-size: 11.5px;
      padding: 12px 14px;
      border-bottom: 1px solid #F5F1EB;
    }

    /* Center Views Transitions */
    .center-view {
      transition: opacity 0.2s ease, transform 0.2s ease;
    }
    .center-view.hidden {
      display: none !important;
      opacity: 0;
      transform: scale(0.99);
    }
  </style>
</head>
<body>

  <!-- ================= MASTER DASHBOARD CONTAINER (1180px by 856px) ================= -->
  <div class="dashboard-wrapper">

    <!-- ================= 1. LEFT SIDEBAR (84px) ================= -->
    <aside class="left-sidebar bg-white h-full flex flex-col items-center py-8 justify-between border-r border-[#F0ECE6] z-10 select-none">
      
      <!-- Top Emblem: RescueTag LoRa Intertwined Gold Logo -->
      <button class="mt-1 cursor-pointer group flex flex-col items-center focus:outline-none" onclick="switchCenterView('overview')" title="RescueTag Command Hub">
        <svg width="34" height="34" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="11.5" y="4.5" width="13" height="27" rx="6.5" transform="rotate(-45 18 18)" stroke="#C68B39" stroke-width="2.3"/>
          <rect x="11.5" y="4.5" width="13" height="27" rx="6.5" transform="rotate(45 18 18)" stroke="#C68B39" stroke-width="2.3"/>
        </svg>
        <span class="text-[9px] font-mono font-bold tracking-widest text-[#9C9892] mt-1.5 uppercase">SEC-01</span>
      </button>

      <!-- Navigation Tactile Icons -->
      <nav class="flex flex-col items-center gap-7 -mt-8">
        <!-- 1. Overview Dashboard (Active) -->
        <button id="navBtn-overview" class="nav-btn active" onclick="switchCenterView('overview')" title="Command Overview">
          <svg width="18" height="18" viewBox="0 0 20 20" fill="none">
            <rect x="2" y="2" width="6.5" height="6.5" rx="1.2" fill="currentColor"/>
            <rect x="11.5" y="2" width="6.5" height="4.2" rx="1.2" fill="currentColor"/>
            <rect x="2" y="11.5" width="6.5" height="6.5" rx="1.2" fill="currentColor"/>
            <rect x="11.5" y="9.2" width="6.5" height="8.8" rx="1.2" fill="currentColor"/>
          </svg>
        </button>

        <!-- 2. Dual-Worker Fleet Telemetry Roster Table -->
        <button id="navBtn-fleet-roster" class="nav-btn" onclick="switchCenterView('fleet-roster')" title="Subterranean Worker Fleet Roster & LoRa Diagnostics">
          <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="3" width="18" height="18" rx="2.5"></rect>
            <path d="M3 9h18"></path>
            <path d="M9 21V9"></path>
          </svg>
        </button>

        <!-- 3. Subterranean Spatial Mine Navigation (OpenStreetMap GIS) -->
        <button id="navBtn-gis-map" class="nav-btn" onclick="switchCenterView('gis-map')" title="Subterranean Spatial Mine Navigation // OpenStreetMap GIS">
          <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">
            <polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"></polygon>
            <line x1="8" y1="2" x2="8" y2="18"></line>
            <line x1="16" y1="6" x2="16" y2="22"></line>
          </svg>
        </button>

        <!-- 4. Chronological SAR Triage & Mesh Audit Trail -->
        <button id="navBtn-audit-trail" class="nav-btn" onclick="switchCenterView('audit-trail')" title="Chronological SAR Triage & Mesh Audit Trail">
          <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <line x1="16" y1="13" x2="8" y2="13"></line>
            <line x1="16" y1="17" x2="8" y2="17"></line>
            <polyline points="10 9 9 9 8 9"></polyline>
          </svg>
        </button>

        <!-- 5. RescueTag Wearable Smartwatch Spec Viewer -->
        <button id="navBtn-hardware-spec" class="nav-btn" onclick="switchCenterView('hardware-spec')" title="RescueTag Wearable Smartwatch">
          <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round">
            <rect x="6" y="2" width="12" height="20" rx="3"></rect>
            <circle cx="12" cy="12" r="3"></circle>
            <line x1="12" y1="18" x2="12.01" y2="18"></line>
          </svg>
        </button>

        <!-- 6. Emergency Siren Audio Synthesizer Toggle -->
        <button id="sirenBtn" class="nav-btn" onclick="toggleAudioAlert()" title="Toggle Emergency Siren Synthesizer">
          <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">
            <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
            <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path>
          </svg>
        </button>
      </nav>

      <!-- Bottom Status Pill (MQTT Online indicator) -->
      <button class="flex flex-col items-center gap-1.5 cursor-pointer focus:outline-none" onclick="toggleMqttInfo()" title="MQTT EMQX Broker Connection Details">
        <span id="mqttDot" class="w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)] animate-pulse"></span>
        <span class="text-[9px] font-mono text-[#8E8B86] font-semibold">EMQX</span>
      </button>
    </aside>

    <!-- ================= 2. CENTER CONTENT (1fr, Warm Sand #FAF6F1) ================= -->
    <main class="px-9 py-8 flex flex-col justify-between h-full overflow-y-auto relative">

      <!-- ================= VIEW 1: COMMAND OVERVIEW (DEFAULT) ================= -->
      <div id="view-overview" class="center-view flex flex-col justify-between h-full">

        <!-- Header -->
        <header class="flex items-center justify-between">
          <div>
            <div class="flex items-center gap-3">
              <h1 class="text-[23px] font-bold text-[#2D2B2A] tracking-tight leading-tight">
                RescueTag Subterranean Command
              </h1>
              <span class="px-2.5 py-0.5 rounded-[6px] bg-[#EAE4DC] text-[#4A4744] text-[10px] font-mono font-bold tracking-wider uppercase">
                LORA 1-HOP MESH P2P
              </span>
            </div>
            <p class="text-[12px] font-medium text-[#7B7874] mt-1 flex items-center gap-2">
              <span id="liveClock" class="font-mono text-[#4A4744]">12:45:00 UTC</span>
              <span>&bull;</span>
              <span id="headerSectorStatus">Sektor 7 Tambang Bawah Tanah &bull; 1-Hop Mesh Relaying</span>
            </p>
          </div>

          <div class="flex items-center gap-3">
            <!-- Worker Switcher Tabs -->
            <div class="flex items-center gap-1.5 bg-[#EFE9E0] p-1.5 rounded-xl border border-[#E5DFD4]">
              <button id="tabWorker02" onclick="selectWorker(2)" class="worker-pill-btn active" title="Switch to Worker #02 (Agus Salim)">
                <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
                <span>Pekerja #02 (Agus)</span>
              </button>
              <button id="tabWorker01" onclick="selectWorker(1)" class="worker-pill-btn" title="Switch to Worker #01 (Bambang Relay)">
                <span class="w-2 h-2 rounded-full bg-amber-500"></span>
                <span>Pekerja #01 (Bambang)</span>
              </button>
            </div>

            <!-- View Audit Notifications -->
            <button class="icon-btn relative" onclick="switchCenterView('audit-trail')" title="Chronological SAR Triage & Mesh Audit Trail">
              <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#302E2D" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
              </svg>
              <span id="alertCountBadge" class="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-[#EF4444] text-white text-[9px] font-bold flex items-center justify-center font-mono">
                0
              </span>
            </button>
          </div>
        </header>

        <!-- ROW 1: 3 Live Telemetry Cards -->
        <section class="grid grid-cols-3 gap-5 my-1">
          
          <!-- Metric Card 1: Heart Rate (MAX30102 PPG) -->
          <div class="metric-card p-4 pb-3 flex flex-col justify-between h-[218px] relative overflow-hidden" 
               onmouseenter="highlightSensorRing('chestRing', true)" 
               onmouseleave="highlightSensorRing('chestRing', false)"
               onclick="switchCenterView('fleet-roster')"
               title="MAX30102 PPG Arterial Pulse">
            <div>
              <div class="flex items-center gap-3">
                <div class="w-[46px] h-[46px] rounded-[13px] bg-[#FBF0F1] flex items-center justify-center shrink-0">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <path d="M12 20.5C12 20.5 3.5 15.2 3.5 8.9C3.5 6.1 5.7 4 8.3 4C9.9 4 11.3 4.8 12 6.1C12.7 4.8 14.1 4 15.7 4C18.3 4 20.5 6.1 20.5 8.9C20.5 15.2 12 20.5 12 20.5Z" fill="#DE6D72"/>
                    <path d="M5.5 11.5H9L10.4 9L12.5 14L14.1 10.5L15.2 11.5H18.5" stroke="#FBF0F1" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </div>
                <div>
                  <span class="text-[14px] font-bold text-[#2D2B2A] block leading-tight">Heart Rate</span>
                  <span class="text-[10px] font-mono text-[#86837F]">MAX30102 PPG</span>
                </div>
              </div>

              <div class="mt-3.5 flex items-baseline gap-1.5">
                <span id="val-hr" class="text-[26px] font-normal text-[#2D2B2A] leading-none font-mono">75</span>
                <span class="text-[12px] font-semibold text-[#86837F]">bpm</span>
              </div>

              <div class="mt-2">
                <span id="badge-hr" class="inline-block px-2.5 py-0.5 rounded-[5px] bg-[#FBE7E8] text-[#3B3031] text-[10.5px] font-bold">
                  Normal
                </span>
              </div>
            </div>

            <!-- Pulsing Red/Pink Sparkline -->
            <div class="w-full h-[54px] mt-1">
              <svg viewBox="0 0 160 52" class="w-full h-full overflow-visible" preserveAspectRatio="none">
                <defs>
                  <linearGradient id="heartGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="#DE6D72" stop-opacity="0.32"/>
                    <stop offset="95%" stop-color="#FBE7E8" stop-opacity="0.0"/>
                  </linearGradient>
                </defs>
                <path d="M 0 34 C 14 25, 28 24, 42 32 C 55 39, 66 41, 76 31 C 86 21, 95 16, 110 18 C 125 20, 142 12, 160 6 L 160 52 L 0 52 Z" fill="url(#heartGrad)"/>
                <path d="M 0 34 C 14 25, 28 24, 42 32 C 55 39, 66 41, 76 31 C 86 21, 95 16, 110 18 C 125 20, 142 12, 160 6" fill="none" stroke="#DE6D72" stroke-width="1.6" stroke-linecap="round"/>
              </svg>
            </div>
          </div>

          <!-- Metric Card 2: SpO2 Blood Oxygen -->
          <div class="metric-card p-4 pb-3 flex flex-col justify-between h-[218px] relative overflow-hidden" 
               onmouseenter="highlightSensorRing('chestRing', true)" 
               onmouseleave="highlightSensorRing('chestRing', false)"
               onclick="switchCenterView('fleet-roster')"
               title="MAX30102 Blood Oxygen">
            <div>
              <div class="flex items-center gap-3">
                <div class="w-[46px] h-[46px] rounded-[13px] bg-[#D5F2F8] flex items-center justify-center shrink-0">
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
                    <path d="M12 3.2C12 3.2 6 10.2 6 14.6C6 18.0 8.69 20.6 12 20.6C15.31 20.6 18 18.0 18 14.6C18 10.2 12 3.2 12 3.2Z" fill="#478F9E"/>
                    <path d="M12 12V17.2M9.4 14.6H14.6" stroke="#D5F2F8" stroke-width="1.6" stroke-linecap="round"/>
                  </svg>
                </div>
                <div>
                  <span class="text-[13.5px] font-bold text-[#2D2B2A] leading-tight">Blood O2<br/>(SpO2)</span>
                </div>
              </div>

              <div class="mt-3.5 flex items-baseline gap-1">
                <span id="val-spo2" class="text-[26px] font-normal text-[#2D2B2A] leading-none font-mono">98</span>
                <span class="text-[11.5px] font-semibold text-[#86837F]">% Saturation</span>
              </div>

              <div class="mt-2">
                <span id="badge-spo2" class="inline-block px-2.5 py-0.5 rounded-[5px] bg-[#D0F1F8] text-[#263C41] text-[10.5px] font-bold">
                  Normal
                </span>
              </div>
            </div>

            <!-- Pulsing Teal/Cyan Sparkline -->
            <div class="w-full h-[54px] mt-1">
              <svg viewBox="0 0 160 52" class="w-full h-full overflow-visible" preserveAspectRatio="none">
                <defs>
                  <linearGradient id="bpGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="#60C3D8" stop-opacity="0.34"/>
                    <stop offset="95%" stop-color="#D0F1F8" stop-opacity="0.0"/>
                  </linearGradient>
                </defs>
                <path d="M 0 32 C 12 38, 26 39, 38 29 C 50 18, 60 14, 76 17 C 90 19, 102 22, 114 14 C 128 5, 144 4, 160 28 L 160 52 L 0 52 Z" fill="url(#bpGrad)"/>
                <path d="M 0 32 C 12 38, 26 39, 38 29 C 50 18, 60 14, 76 17 C 90 19, 102 22, 114 14 C 128 5, 144 4, 160 28" fill="none" stroke="#53ACC0" stroke-width="1.6" stroke-linecap="round"/>
              </svg>
            </div>
          </div>

          <!-- Metric Card 3: IR Skin Temperature -->
          <div class="metric-card p-4 pb-3 flex flex-col justify-between h-[218px] relative overflow-hidden" 
               onmouseenter="highlightSensorRing('wristRing', true)" 
               onmouseleave="highlightSensorRing('wristRing', false)"
               onclick="switchCenterView('fleet-roster')"
               title="MLX90614 Contactless IR Temp">
            <div>
              <div class="flex items-center gap-3">
                <div class="w-[46px] h-[46px] rounded-[13px] bg-[#F8DFC2] flex items-center justify-center shrink-0">
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#E09B48" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"></path>
                  </svg>
                </div>
                <div>
                  <span class="text-[14px] font-bold text-[#2D2B2A]">Skin IR Temp</span>
                  <span class="text-[10px] font-mono text-[#86837F]">MLX90614</span>
                </div>
              </div>

              <div class="mt-3.5 flex items-baseline gap-1.5">
                <span id="val-temp" class="text-[26px] font-normal text-[#2D2B2A] leading-none font-mono">36.5</span>
                <span class="text-[12px] font-semibold text-[#86837F]">&deg;C</span>
              </div>

              <div class="mt-2">
                <span id="badge-temp" class="inline-block px-2.5 py-0.5 rounded-[5px] bg-[#F8DFC2] text-[#3B352E] text-[10.5px] font-bold">
                  Normal
                </span>
              </div>
            </div>

            <!-- Pulsing Orange Sparkline -->
            <div class="w-full h-[54px] mt-1">
              <svg viewBox="0 0 160 52" class="w-full h-full overflow-visible" preserveAspectRatio="none">
                <defs>
                  <linearGradient id="sugarGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="#E79B3F" stop-opacity="0.38"/>
                    <stop offset="95%" stop-color="#F8DFC2" stop-opacity="0.0"/>
                  </linearGradient>
                </defs>
                <path d="M 0 38 C 16 28, 30 22, 46 28 C 60 33, 74 34, 88 22 C 100 11, 108 6, 120 12 C 132 18, 140 31, 160 24 L 160 52 L 0 52 Z" fill="url(#sugarGrad)"/>
                <path d="M 0 38 C 16 28, 30 22, 46 28 C 60 33, 74 34, 88 22 C 100 11, 108 6, 120 12 C 132 18, 140 31, 160 24" fill="none" stroke="#E59A43" stroke-width="1.6" stroke-linecap="round"/>
              </svg>
            </div>
          </div>

        </section>

        <!-- ROW 2: Kinematics & TinyML Activity Stream (Height 346px) -->
        <section class="metric-card px-6 py-5 flex flex-col justify-between h-[346px]">
          <!-- Card Header -->
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <h2 class="text-[16px] font-bold text-[#2D2B2A]">Kinematics & TinyML Activity Stream</h2>
              <span id="liveAccelPill" class="px-2.5 py-0.5 rounded-[6px] bg-[#EFE9E0] text-[#3E3C39] font-mono text-[10.5px] font-bold">
                1.02g &bull; Normal
              </span>
            </div>
            <button id="monthToggleBtn" onclick="cycleShift()" class="flex items-center gap-2.5 px-3 py-1.5 rounded-[10px] border border-[#EAE6E1] text-[11.5px] font-semibold text-[#4A4744] hover:bg-[#FAF6F1] transition">
              <span id="shiftLabel">Shift Pagi // Sektor 7</span>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="6 9 12 15 18 9"/>
              </svg>
            </button>
          </div>

          <!-- Bar Chart Area -->
          <div class="relative flex-1 mt-4 mb-2 flex">
            <!-- Y-Axis Labels -->
            <div class="flex flex-col justify-between text-[9px] font-mono font-semibold text-[#8E8B86] pr-3 pb-7 pt-2 select-none">
              <span>4.0g (Shock)</span>
              <span>2.5g (Active)</span>
              <span>1.5g (Work)</span>
              <span>1.0g (Rest)</span>
            </div>

            <!-- Horizontal Grid Lines + 18 Multi-Segment Pill Bars -->
            <div class="flex-1 relative flex flex-col justify-between pb-7 pt-3">
              <div class="w-full border-b border-[#F4F1ED]"></div>
              <div class="w-full border-b border-[#F4F1ED]"></div>
              <div class="w-full border-b border-[#F4F1ED]"></div>
              <div class="w-full border-b border-[#F4F1ED]"></div>

              <!-- 18 Multi-Segment Pill Bars -->
              <div id="kinematicsBarsContainer" class="absolute inset-0 bottom-6 flex items-end justify-between px-3">
                <!-- Populated by JS -->
              </div>
            </div>
          </div>

          <!-- Legend & Simulation Controls -->
          <div class="flex items-center justify-between pt-1">
            <div class="flex items-center gap-7">
              <div class="flex items-center gap-2.5">
                <span class="w-2.5 h-2.5 rounded-full bg-[#DA7468]"></span>
                <span class="text-[10.5px] font-semibold text-[#6E6B67]">G-Force Shock (>3.0g)</span>
              </div>
              <div class="flex items-center gap-2.5">
                <span class="w-2.5 h-2.5 rounded-full bg-[#438D9B]"></span>
                <span class="text-[10.5px] font-semibold text-[#6E6B67]">Kerja Aktif (1.2-2.5g)</span>
              </div>
              <div class="flex items-center gap-2.5">
                <span class="w-2.5 h-2.5 rounded-full bg-[#CD8A39]"></span>
                <span class="text-[10.5px] font-semibold text-[#6E6B67]">Diam / Baseline (1.0g)</span>
              </div>
            </div>

            <div class="flex items-center gap-2">
              <button onclick="testSimSOS()" class="px-2.5 py-1 rounded-[6px] bg-red-50 text-red-700 text-[10px] font-bold font-mono hover:bg-red-100 transition border border-red-200">
                Simulate SOS
              </button>
              <button onclick="testSimNormal()" class="px-2.5 py-1 rounded-[6px] bg-emerald-50 text-emerald-700 text-[10px] font-bold font-mono hover:bg-emerald-100 transition border border-emerald-200">
                Simulate Normal
              </button>
            </div>
          </div>
        </section>

        <!-- ROW 3: LoRa 1-Hop Mesh Transmission Link (Height 66px) -->
        <section class="metric-card px-6 py-4 flex items-center justify-between h-[66px]">
          <div class="flex items-center gap-3">
            <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)] animate-ping"></span>
            <h3 class="text-[14.5px] font-bold text-[#2D2B2A]">LoRa 1-Hop Mesh Transmission Link</h3>
          </div>
          
          <div class="flex items-center gap-2.5">
            <span class="px-3 py-1 rounded-[8px] bg-[#CEF0F7] text-[#283B40] text-[10.5px] font-bold tracking-tight font-mono">
              18ms Estafet Latency &bull; -68 dBm
            </span>
            <button onclick="switchCenterView('gis-map')" class="px-3 py-1 rounded-[8px] bg-[#2C2A2A] text-white text-[10.5px] font-semibold hover:bg-[#1D1B1B] transition">
              Open Subterranean GIS Map
            </button>
          </div>

          <button onclick="switchCenterView('fleet-roster')" class="text-[12px] font-semibold text-[#5A5754] hover:text-[#2D2B2A] transition">
            View Dual-Worker Diagnostics &rarr;
          </button>
        </section>

      </div>

      <!-- ================= VIEW 2: SUBTERRANEAN WORKER FLEET ROSTER & LORA DIAGNOSTICS ================= -->
      <div id="view-fleet-roster" class="center-view hidden flex flex-col justify-between h-full">
        <!-- Header -->
        <header class="flex items-center justify-between pb-3 border-b border-[#F0ECE6]">
          <div>
            <h1 class="text-[20px] font-bold text-[#2D2B2A] tracking-tight">
              Subterranean Worker Fleet Roster &amp; LoRa Diagnostics
            </h1>
            <p class="text-[12px] font-medium text-[#7B7874] mt-0.5">
              Real-Time Telemetry &amp; 1-Hop Forwarding State for Both Personnel
            </p>
          </div>
          <button onclick="switchCenterView('overview')" class="px-3.5 py-1.5 rounded-[10px] bg-[#2C2A2A] text-white text-[11.5px] font-semibold hover:bg-[#1C1A1A] transition">
            &larr; Back to Overview
          </button>
        </header>

        <!-- Main Roster Table Card -->
        <div class="metric-card p-5 my-3 flex-1 flex flex-col justify-between">
          <div class="overflow-x-auto">
            <table class="w-full warm-table border-collapse">
              <thead>
                <tr>
                  <th>Worker Name &amp; Tag ID</th>
                  <th>Vital Signs (HR &bull; SpO2 &bull; Temp)</th>
                  <th>Activity State (TinyML)</th>
                  <th>Transmission Route</th>
                  <th>START Triage Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <!-- Row 1: Worker #02 (Agus Salim) -->
                <tr id="rosterRow02" class="hover:bg-[#FAF6F1] transition">
                  <td>
                    <div class="font-bold text-[#2D2B2A] text-xs">Pekerja #02 (Agus Salim)</div>
                    <div class="text-[10px] text-[#7B7874] font-mono">Jam Tangan #02 &bull; Sektor 7 (Lorong C-4)</div>
                  </td>
                  <td>
                    <span id="rosterVitals02" class="font-mono text-emerald-700 font-semibold text-xs">
                      75 BPM &bull; 98% SpO2 &bull; 36.5&deg;C
                    </span>
                  </td>
                  <td>
                    <span id="rosterActivity02" class="px-2 py-0.5 rounded bg-emerald-50 text-emerald-800 border border-emerald-200 text-[10.5px]">
                      Diam / Istirahat Normal
                    </span>
                  </td>
                  <td>
                    <span class="px-2 py-0.5 rounded bg-blue-50 text-blue-800 border border-blue-200 text-[10.5px] font-mono">
                      1-Hop Relay via Jam #01
                    </span>
                  </td>
                  <td>
                    <span id="rosterTriage02" class="px-2.5 py-1 rounded bg-emerald-100 text-emerald-900 border border-emerald-300 font-bold text-[10px]">
                      HIJAU - Minor (Aman)
                    </span>
                  </td>
                  <td>
                    <div class="flex items-center gap-1.5">
                      <button onclick="focusFromRoster(2)" class="px-2.5 py-1 rounded bg-[#EFE9E0] hover:bg-[#E5DFD4] text-[10.5px] font-mono transition text-[#2D2B2A] font-bold">
                        Focus Map
                      </button>
                      <button onclick="runDiagWatch(2)" class="px-2.5 py-1 rounded bg-amber-100 hover:bg-amber-200 text-amber-900 text-[10.5px] font-mono transition font-bold">
                        Run Diag
                      </button>
                    </div>
                  </td>
                </tr>

                <!-- Row 2: Worker #01 (Bambang Relay Host) -->
                <tr id="rosterRow01" class="hover:bg-[#FAF6F1] transition">
                  <td>
                    <div class="font-bold text-[#2D2B2A] text-xs">Pekerja #01 (Bambang)</div>
                    <div class="text-[10px] text-[#7B7874] font-mono">Jam Tangan #01 &bull; Junction B-02 (Shaft Poros)</div>
                  </td>
                  <td>
                    <span id="rosterVitals01" class="font-mono text-amber-700 font-semibold text-xs">
                      106 BPM &bull; 93% SpO2 &bull; 37.6&deg;C
                    </span>
                  </td>
                  <td>
                    <span id="rosterActivity01" class="px-2 py-0.5 rounded bg-amber-50 text-amber-800 border border-amber-200 text-[10.5px]">
                      Tremor / Kelelahan Ringan
                    </span>
                  </td>
                  <td>
                    <span class="px-2 py-0.5 rounded bg-orange-50 text-orange-800 border border-orange-200 text-[10.5px] font-mono">
                      Direct + Relay Host (Hop 1)
                    </span>
                  </td>
                  <td>
                    <span id="rosterTriage01" class="px-2.5 py-1 rounded bg-amber-100 text-amber-900 border border-amber-300 font-bold text-[10px]">
                      KUNING - Delayed
                    </span>
                  </td>
                  <td>
                    <div class="flex items-center gap-1.5">
                      <button onclick="focusFromRoster(1)" class="px-2.5 py-1 rounded bg-[#EFE9E0] hover:bg-[#E5DFD4] text-[10.5px] font-mono transition text-[#2D2B2A] font-bold">
                        Focus Map
                      </button>
                      <button onclick="runDiagWatch(1)" class="px-2.5 py-1 rounded bg-amber-100 hover:bg-amber-200 text-amber-900 text-[10.5px] font-mono transition font-bold">
                        Run Diag
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Bottom Battery & Signal Diagnostics Cards -->
          <div class="grid grid-cols-3 gap-4 pt-4 mt-2 border-t border-[#F0ECE6]">
            <div class="p-3 bg-[#FAF6F1] rounded-xl border border-[#F0ECE6]">
              <span class="text-[10px] text-[#7B7874] font-mono block">RF LINK QUALITY</span>
              <span class="font-bold text-xs text-[#2D2B2A] font-mono">RSSI -68 dBm // SNR +8.5 dB</span>
            </div>
            <div class="p-3 bg-[#FAF6F1] rounded-xl border border-[#F0ECE6]">
              <span class="text-[10px] text-[#7B7874] font-mono block">JAM TANGAN #01 BATTERY</span>
              <span class="font-bold text-xs text-amber-700 font-mono">81% (4.12V LiPo) &bull; Relay Active</span>
            </div>
            <div class="p-3 bg-[#FAF6F1] rounded-xl border border-[#F0ECE6]">
              <span class="text-[10px] text-[#7B7874] font-mono block">JAM TANGAN #02 BATTERY</span>
              <span class="font-bold text-xs text-emerald-700 font-mono">78% (4.06V LiPo) &bull; P2P Connected</span>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="flex items-center justify-between text-xs text-[#7B7874] font-mono">
          <span>Sub-GHz 433.05 MHz Mesh &bull; CRC-16 Hardware Checksum</span>
          <div class="flex gap-2">
            <button onclick="testSimSOS()" class="px-3 py-1 rounded bg-red-100 text-red-800 font-bold hover:bg-red-200 transition">
              Simulate SOS Incident
            </button>
            <button onclick="testSimNormal()" class="px-3 py-1 rounded bg-emerald-100 text-emerald-800 font-bold hover:bg-emerald-200 transition">
              Simulate Normal State
            </button>
          </div>
        </div>
      </div>

      <!-- ================= VIEW 3: SUBTERRANEAN SPATIAL MINE NAVIGATION (GIS MAP) ================= -->
      <div id="view-gis-map" class="center-view hidden flex flex-col justify-between h-full">
        <!-- Header -->
        <header class="flex items-center justify-between pb-3 border-b border-[#F0ECE6]">
          <div>
            <h1 class="text-[20px] font-bold text-[#2D2B2A] tracking-tight">
              Subterranean Spatial Mine Navigation // OpenStreetMap GIS
            </h1>
            <p class="text-[12px] font-medium text-[#7B7874] mt-0.5">
              Lorong C-4 Sektor 7 &bull; Poros Shaft B-02 &bull; Posko Permukaan Gateway
            </p>
          </div>
          <div class="flex items-center gap-2">
            <button onclick="toggleMapTileStyle()" class="px-3 py-1.5 rounded-[10px] border border-[#EAE6E1] text-[11.5px] font-semibold text-[#4A4744] hover:bg-[#FAF6F1] transition">
              Toggle Canvas
            </button>
            <button onclick="switchCenterView('overview')" class="px-3.5 py-1.5 rounded-[10px] bg-[#2C2A2A] text-white text-[11.5px] font-semibold hover:bg-[#1C1A1A] transition">
              &larr; Back to Overview
            </button>
          </div>
        </header>

        <!-- GIS Map Card Container -->
        <div class="metric-card p-3 my-3 flex-1 flex flex-col overflow-hidden relative">
          <div id="leafletMapContainer" class="w-full flex-1 rounded-xl bg-[#E8E4DE] overflow-hidden min-h-[460px]"></div>
        </div>

        <!-- GIS Map Footer Bar -->
        <div class="flex items-center justify-between text-xs font-mono">
          <div class="flex items-center gap-2">
            <button onclick="focusMapNode(2)" class="px-3 py-1 rounded bg-emerald-100 text-emerald-800 font-bold hover:bg-emerald-200 transition">
              Focus: Agus (#02)
            </button>
            <button onclick="focusMapNode(1)" class="px-3 py-1 rounded bg-amber-100 text-amber-800 font-bold hover:bg-amber-200 transition">
              Focus: Bambang (#01 Relay)
            </button>
            <button onclick="pulseHopSimulation()" class="px-3 py-1 rounded bg-[#CEF0F7] text-[#1E454E] font-bold hover:bg-[#BDE7F0] transition">
              Simulate 1-Hop Mesh Pulse
            </button>
          </div>
          <span class="text-[#7B7874]">Anchor: Lat -8.2465 Lon 113.6965</span>
        </div>
      </div>

      <!-- ================= VIEW 4: CHRONOLOGICAL SAR TRIAGE & MESH AUDIT TRAIL ================= -->
      <div id="view-audit-trail" class="center-view hidden flex flex-col justify-between h-full">
        <!-- Header -->
        <header class="flex items-center justify-between pb-3 border-b border-[#F0ECE6]">
          <div>
            <h1 class="text-[20px] font-bold text-[#2D2B2A] tracking-tight">
              Chronological SAR Triage &amp; Mesh Audit Trail
            </h1>
            <p class="text-[12px] font-medium text-[#7B7874] mt-0.5">
              Live Timestamped Disaster Event Records
            </p>
          </div>
          <div class="flex items-center gap-2.5">
            <!-- DOWNLOAD EXCEL / CSV BUTTON -->
            <button onclick="downloadChronologicalExcel()" class="flex items-center gap-2 px-3.5 py-1.5 rounded-[10px] bg-emerald-700 hover:bg-emerald-800 text-white text-[11.5px] font-semibold transition shadow-sm" title="Download Audit Log as Excel-compatible CSV">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="7 10 12 15 17 10"></polyline>
                <line x1="12" y1="15" x2="12" y2="3"></line>
              </svg>
              <span>Download Excel (.CSV)</span>
            </button>
            
            <button onclick="dispatchAlphaSquad()" class="px-3 py-1.5 rounded-[10px] bg-red-100 hover:bg-red-200 text-red-800 text-[11.5px] font-bold transition border border-red-200">
              Dispatch SAR Squad
            </button>
            <button onclick="switchCenterView('overview')" class="px-3.5 py-1.5 rounded-[10px] bg-[#2C2A2A] text-white text-[11.5px] font-semibold hover:bg-[#1C1A1A] transition">
              &larr; Back to Overview
            </button>
          </div>
        </header>

        <!-- Audit Trail Card List (Matching Warm Sand / White Palette) -->
        <div class="metric-card p-5 my-3 flex-1 overflow-y-auto">
          <div id="auditLogList" class="space-y-3 font-mono text-xs">
            <!-- Populated dynamically by appendAuditTrail -->
          </div>
        </div>

        <!-- Footer -->
        <div class="flex items-center justify-between text-xs text-[#7B7874] font-mono">
          <span>Encrypted Local Audit Trail &bull; Automatic 1-Hop Hop Forwarding Log</span>
          <span>Excel Export Format: RFC-4180 CSV (UTF-8 BOM)</span>
        </div>
      </div>

      <!-- ================= VIEW 5: RESCUETAG WEARABLE SMARTWATCH ================= -->
      <div id="view-hardware-spec" class="center-view hidden flex flex-col justify-between h-full">
        <!-- Header -->
        <header class="flex items-center justify-between pb-3 border-b border-[#F0ECE6]">
          <div>
            <h1 class="text-[20px] font-bold text-[#2D2B2A] tracking-tight">
              RescueTag Wearable Smartwatch
            </h1>
            <p class="text-[12px] font-medium text-[#7B7874] mt-0.5">
              Industrial Subterranean Miner Wearable Unit
            </p>
          </div>
          <button onclick="switchCenterView('overview')" class="px-3.5 py-1.5 rounded-[10px] bg-[#2C2A2A] text-white text-[11.5px] font-semibold hover:bg-[#1C1A1A] transition">
            &larr; Back to Overview
          </button>
        </header>

        <!-- Hardware Card Grid (Matching Warm Sand / White Palette) -->
        <div class="metric-card p-6 my-3 flex-1 flex flex-col justify-between">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
            
            <!-- Hardware Image Container -->
            <div class="bg-[#FAF6F1] rounded-2xl p-4 border border-[#F0ECE6] flex items-center justify-center">
              <img id="hardwarePhotoImg" src="BASE64_IMAGE_PLACEHOLDER" alt="RescueTag Wearable Smartwatch" class="max-h-[300px] object-contain drop-shadow-xl" />
            </div>

            <!-- Technical Specification Breakdown -->
            <div class="space-y-3 font-mono text-xs">
              <div class="bg-[#FAF6F1] p-3.5 rounded-xl border border-[#F0ECE6]">
                <span class="text-[#7B7874] block text-[10px] font-bold uppercase">ENCLOSURE &amp; PROTECTION</span>
                <span class="font-bold text-[#2D2B2A] text-sm">IP68 Rugged ABS Shock-Proof Enclosure</span>
              </div>
              <div class="bg-[#FAF6F1] p-3.5 rounded-xl border border-[#F0ECE6]">
                <span class="text-[#7B7874] block text-[10px] font-bold uppercase">MICROCONTROLLER &amp; SENSORS</span>
                <span class="font-bold text-[#2D2B2A]">STM32 Ultra-Low Power + MAX30102 + MLX90614 + BMI160</span>
              </div>
              <div class="bg-[#FAF6F1] p-3.5 rounded-xl border border-[#F0ECE6]">
                <span class="text-[#7B7874] block text-[10px] font-bold uppercase">TELEMETRY &amp; MESH PROTOCOL</span>
                <span class="font-bold text-[#C68B39]">SX1278 LoRa 433.05 MHz Sub-GHz (1-Hop Peer-to-Peer)</span>
              </div>
              <div class="bg-[#FAF6F1] p-3.5 rounded-xl border border-[#F0ECE6]">
                <span class="text-[#7B7874] block text-[10px] font-bold uppercase">AUTONOMOUS POWER</span>
                <span class="font-bold text-emerald-700">850mAh LiPo &bull; 18 Jam Operasional Bawah Tanah</span>
              </div>
            </div>

          </div>
        </div>

        <!-- Footer -->
        <div class="flex items-center justify-between text-xs text-[#7B7874] font-mono">
          <span>Field Testing: Tambang Batubara Bawah Tanah &bull; 0.96" Monochrome Live OLED</span>
          <button onclick="testSimSOS()" class="px-3 py-1 rounded bg-amber-100 text-amber-900 font-bold hover:bg-amber-200 transition">
            Test Shock Waveform
          </button>
        </div>
      </div>

    </main>

    <!-- ================= 3. RIGHT DARK TACTICAL PANEL (414px, #2D2B2B) ================= -->
    <aside class="right-tactical-panel bg-[#2D2B2B] h-full rounded-l-[34px] px-8 py-8 flex flex-col justify-between text-white relative overflow-hidden select-none border-l border-[#3D3A3A]">

      <!-- TOP SECTION: START Triage Risk Simulator -->
      <div>
        <!-- Header -->
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-[17px] font-semibold text-[#F4F1EA] tracking-tight">START Triage Risk Simulator</h2>
            <p class="text-[11px] font-medium text-[#B8B4B0] mt-0.5">Simple Triage and Rapid Treatment</p>
          </div>
          <button id="simModeToggleBtn" onclick="toggleSimMode()" class="flex items-center gap-2 px-3 py-1 rounded-[10px] border border-[#6E6C6C] text-[11px] font-medium text-[#D1CECA] hover:border-[#9E9C9C] transition font-mono">
            <span id="simModeLabel">Live MQTT</span>
          </button>
        </div>

        <!-- Sliders & Result Grid -->
        <div class="grid grid-cols-[152px_1fr] gap-3.5 mt-5">
          
          <!-- Left Column: Height & Weight Style Ruler Cards -->
          <div class="flex flex-col gap-3.5">
            
            <!-- HR Slider Card (Peach #F6D6B8) -->
            <div class="bg-[#F6D6B8] rounded-[14px] px-3.5 py-2.5 h-[68px] flex flex-col justify-between relative text-[#2C2A29]" title="Drag left/right to adjust Heart Rate">
              <input type="range" min="40" max="180" value="75" id="sliderHR" class="ruler-slider" oninput="onSimulatorInput()" />
              <div class="flex items-start justify-end gap-[6.5px] pr-1 pt-0.5 pointer-events-none">
                <span class="w-[1.3px] h-2 bg-[#7A6855]"></span>
                <span class="w-[1.3px] h-2 bg-[#7A6855]"></span>
                <span class="w-[1.3px] h-2 bg-[#7A6855]"></span>
                <span class="w-[1.3px] h-2 bg-[#7A6855]"></span>
                <span class="w-[1.6px] h-3.5 bg-[#D4554B]"></span>
                <span class="w-[1.3px] h-2 bg-[#2C2A29]"></span>
                <span class="w-[1.3px] h-2 bg-[#2C2A29]"></span>
                <span class="w-[1.3px] h-2 bg-[#2C2A29]"></span>
                <span class="w-[1.3px] h-2 bg-[#2C2A29]"></span>
              </div>
              <div class="flex items-center justify-between text-[11.5px] font-semibold pb-0.5">
                <span class="text-[#4A4138]">Heart Rate</span>
                <span id="simHRText" class="font-bold text-[#2C2A29] font-mono">75 bpm</span>
              </div>
            </div>

            <!-- SpO2 Slider Card (Light Blue #C8EAEF) -->
            <div class="bg-[#C8EAEF] rounded-[14px] px-3.5 py-2.5 h-[68px] flex flex-col justify-between relative text-[#2C2A29]" title="Drag left/right to adjust SpO2">
              <input type="range" min="70" max="100" value="98" id="sliderSpO2" class="ruler-slider" oninput="onSimulatorInput()" />
              <div class="flex items-start justify-end gap-[6.5px] pr-1 pt-0.5 pointer-events-none">
                <span class="w-[1.3px] h-2 bg-[#6A8185]"></span>
                <span class="w-[1.3px] h-2 bg-[#6A8185]"></span>
                <span class="w-[1.3px] h-2 bg-[#6A8185]"></span>
                <span class="w-[1.3px] h-2 bg-[#6A8185]"></span>
                <span class="w-[1.6px] h-3.5 bg-[#D4554B]"></span>
                <span class="w-[1.3px] h-2 bg-[#2C2A29]"></span>
                <span class="w-[1.3px] h-2 bg-[#2C2A29]"></span>
                <span class="w-[1.3px] h-2 bg-[#2C2A29]"></span>
                <span class="w-[1.3px] h-2 bg-[#2C2A29]"></span>
              </div>
              <div class="flex items-center justify-between text-[11.5px] font-semibold pb-0.5">
                <span class="text-[#3C4B4E]">SpO2 Sat</span>
                <span id="simSpO2Text" class="font-bold text-[#2C2A29] font-mono">98 %</span>
              </div>
            </div>

          </div>

          <!-- Right Column: Result Card (#434141) -->
          <div class="bg-[#434141] rounded-[16px] px-4 py-3.5 flex flex-col justify-between h-[150px]">
            <div class="text-[11.5px] font-medium text-[#D9D6D2] flex justify-between">
              <span>START Assessment</span>
              <span id="simModeIndicator" class="text-[9px] font-mono text-[#B8B4B0]">LIVE</span>
            </div>

            <div class="flex items-center justify-between my-1">
              <span id="triagePriorityText" class="text-[20px] font-extrabold text-[#34D399] leading-none font-mono">HIJAU</span>
              <span id="triageBadgePill" class="px-2.5 py-1 rounded-[7px] bg-[#D5F4EA] text-[#213B33] text-[10px] font-bold">
                Aman / Stabil
              </span>
            </div>

            <!-- Gradient Priority Bar with Dynamic Indicator Dot -->
            <div class="mt-1" onclick="onTriageBarClick(event)" title="Click to test triage stages">
              <div class="relative pt-2.5">
                <div id="triageDot" class="w-[7px] h-[7px] rounded-full bg-[#E15249] border border-white absolute top-0 -translate-x-1/2 transition-all duration-300" style="left: 18%;"></div>
                <div class="triage-gradient-bar"></div>
              </div>
              <div class="flex items-center justify-between text-[9px] font-semibold text-[#D0CDCA] mt-2 font-mono">
                <span onclick="setTriageDirect('HIJAU')" class="hover:text-emerald-300 cursor-pointer">HIJAU</span>
                <span onclick="setTriageDirect('KUNING')" class="hover:text-amber-300 cursor-pointer">KUNING</span>
                <span onclick="setTriageDirect('MERAH')" class="hover:text-red-300 cursor-pointer">MERAH</span>
                <span onclick="setTriageDirect('HITAM')" class="hover:text-gray-200 cursor-pointer">HITAM</span>
              </div>
            </div>
          </div>

        </div>
      </div>

      <!-- Divider Line -->
      <div class="w-full h-[1px] bg-[#454343] my-1"></div>

      <!-- BOTTOM SECTION: Wearable Sensor Ergonomics -->
      <div class="flex-1 flex flex-col justify-between pt-1 relative">
        
        <div class="grid grid-cols-[175px_1fr] h-full items-start relative">
          
          <!-- Left Column: Info + 3 Stacked White Sensor Cards -->
          <div class="flex flex-col justify-between h-full z-10 pr-1">
            <div>
              <h2 class="text-[17px] font-semibold text-[#F4F1EA] tracking-tight">Sensor Ergonomics</h2>
              <p class="text-[11.5px] font-medium text-[#B8B4B0] mt-0.5">Hardware Anatomical Placement</p>
              <div class="mt-2.5 inline-block px-3 py-1 rounded-[8px] bg-[#494747] text-[#DFDCD8] text-[10.5px] font-mono">
                SEC-01 // NODE-01
              </div>
            </div>

            <!-- 3 Stacked White Measurement Cards -->
            <div class="flex flex-col gap-3 mb-1 mt-3">
              
              <!-- Chest Card (MAX30102) -->
              <div class="measure-card bg-white rounded-[13px] w-[122px] h-[74px] flex flex-col items-center justify-center shadow-md p-2" 
                   onmouseenter="highlightRing('chestRing', true)" 
                   onmouseleave="highlightRing('chestRing', false)"
                   onclick="switchCenterView('overview')"
                   title="MAX30102 PPG Arterial Pulse">
                <span class="text-[10px] font-bold text-[#6E6B68]">PPG Pulse Sensor</span>
                <div class="flex items-center gap-1.5 mt-0.5">
                  <span class="text-[17px] font-bold text-[#242221]">MAX30102</span>
                </div>
                <span class="text-[9px] text-[#A6A29C] font-mono">Chest &bull; Arterial</span>
              </div>

              <!-- Waist Card (BMI160 IMU) -->
              <div class="measure-card bg-white rounded-[13px] w-[122px] h-[74px] flex flex-col items-center justify-center shadow-md p-2" 
                   onmouseenter="highlightRing('waistRing', true)" 
                   onmouseleave="highlightRing('waistRing', false)"
                   onclick="switchCenterView('overview')"
                   title="BMI160 6-DOF IMU Kinematics">
                <span class="text-[10px] font-bold text-[#6E6B68]">Core Kinematics</span>
                <div class="flex items-center gap-1.5 mt-0.5">
                  <span class="text-[17px] font-bold text-[#242221]">BMI160 IMU</span>
                </div>
                <span class="text-[9px] text-[#A6A29C] font-mono">Waist &bull; 6-DOF</span>
              </div>

              <!-- Wrist Card (Smartwatch Enclosure) -->
              <div class="measure-card bg-white rounded-[13px] w-[122px] h-[74px] flex flex-col items-center justify-center shadow-md p-2" 
                   onmouseenter="highlightRing('hipRing', true)" 
                   onmouseleave="highlightRing('hipRing', false)"
                   onclick="switchCenterView('hardware-spec')"
                   title="RescueTag Wearable Smartwatch">
                <span class="text-[10px] font-bold text-[#6E6B68]">Smartwatch</span>
                <div class="flex items-center gap-1.5 mt-0.5">
                  <span class="text-[16px] font-bold text-[#242221]">IP68 ABS</span>
                </div>
                <span class="text-[9px] text-[#C68B39] font-mono font-bold">Left Wrist OLED</span>
              </div>

            </div>
          </div>

          <!-- Right Column: High-Precision SVG Male Illustration + 3 Glowing Rings -->
          <div class="h-full flex items-end justify-center relative -mr-3 pt-3">
            <svg viewBox="0 0 210 440" class="w-[196px] h-[418px] overflow-visible select-none" fill="none" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <filter id="redGlow" x="-30%" y="-40%" width="160%" height="180%">
                  <feGaussianBlur stdDeviation="2.5" result="blur" />
                  <feMerge>
                    <feMergeNode in="blur" />
                    <feMergeNode in="SourceGraphic" />
                  </feMerge>
                </filter>
                <linearGradient id="neckShadow" x1="105" y1="54" x2="105" y2="76" gradientUnits="userSpaceOnUse">
                  <stop offset="0%" stop-color="#D79E73" stop-opacity="0.75"/>
                  <stop offset="100%" stop-color="#F7C9A6" stop-opacity="0"/>
                </linearGradient>
                <linearGradient id="tankGrad" x1="65" y1="78" x2="145" y2="195" gradientUnits="userSpaceOnUse">
                  <stop offset="0%" stop-color="#FDF4EE"/>
                  <stop offset="55%" stop-color="#FBF0E9"/>
                  <stop offset="100%" stop-color="#F5E4DA"/>
                </linearGradient>
              </defs>

              <!-- BACK HALF OF 3D RED RINGS -->
              <path d="M 38 112 A 67 11 0 0 1 172 112" stroke="#D9534F" stroke-width="1.7" stroke-opacity="0.75" fill="none" />
              <path d="M 55 160 A 50 9 0 0 1 155 160" stroke="#D9534F" stroke-width="1.7" stroke-opacity="0.75" fill="none" />
              <path d="M 48 214 A 57 10 0 0 1 162 214" stroke="#D9534F" stroke-width="1.7" stroke-opacity="0.75" fill="none" />

              <!-- FULL BODY ANATOMY -->
              <path d="M 88 52 L 86 68 L 62 76 L 148 76 L 124 68 L 122 52 Z" fill="#F7C9A6"/>
              <path d="M 88 55 Q 105 70 122 55 L 123 68 Q 105 76 87 68 Z" fill="url(#neckShadow)"/>

              <path d="M 64 76 C 48 80, 42 92, 43 114 C 43 125, 38 142, 41 156 C 36 172, 36 196, 39 216 C 37 224, 37 238, 41 246 C 44 252, 48 254, 49 250 C 51 253, 54 252, 54 248 C 56 249, 58 247, 57 244 C 54 239, 53 234, 53 228 C 52 222, 49 217, 49 212 C 53 196, 56 175, 58 160 C 64 148, 69 135, 70 120 Z" fill="#F7C9A6"/>

              <path d="M 146 76 C 162 80, 168 92, 167 114 C 167 125, 172 142, 169 156 C 174 172, 174 196, 171 216 C 173 224, 173 238, 169 246 C 166 252, 162 254, 161 250 C 159 253, 156 252, 156 248 C 154 249, 152 247, 153 244 C 156 239, 157 234, 157 228 C 158 222, 161 217, 161 212 C 157 196, 154 175, 152 160 C 146 148, 141 135, 140 120 Z" fill="#F7C9A6"/>

              <path d="M 65 242 C 64 268, 66 294, 70 312 C 66 326, 65 344, 69 362 C 71 375, 73 392, 74 404 L 91 404 C 91 390, 95 372, 99 354 C 102 338, 100 322, 96 310 C 101 290, 103 266, 103 244 Z" fill="#F7C9A6"/>

              <path d="M 145 242 C 146 268, 144 294, 140 312 C 144 326, 145 344, 141 362 C 139 375, 137 392, 136 404 L 119 404 C 119 390, 115 372, 111 354 C 108 338, 110 322, 114 310 C 109 290, 107 266, 107 244 Z" fill="#F7C9A6"/>

              <path d="M 74 72 L 85 70 C 88 86, 94 94, 105 94 C 116 94, 122 86, 125 70 L 136 72 C 134 92, 136 108, 143 118 C 141 136, 136 154, 136 170 C 136 178, 137 183, 136 187 C 116 191, 94 191, 74 187 C 73 183, 74 178, 74 170 C 74 154, 69 136, 67 118 C 74 108, 76 92, 74 72 Z" fill="url(#tankGrad)"/>

              <path d="M 72 117 C 82 123, 98 123, 103 116" stroke="#EDD5C5" stroke-width="1.2" stroke-linecap="round"/>
              <path d="M 138 117 C 128 123, 112 123, 107 116" stroke="#EDD5C5" stroke-width="1.2" stroke-linecap="round"/>

              <path d="M 62 116 Q 66 109 70 118 M 65 113 Q 64 122 61 126" stroke="#DC8751" stroke-width="1.2" stroke-linecap="round"/>
              <path d="M 148 116 Q 144 109 140 118 M 145 113 Q 146 122 149 126" stroke="#DC8751" stroke-width="1.2" stroke-linecap="round"/>
              <path d="M 76 310 C 75 318, 80 324, 80 333 M 91 311 C 93 316, 92 321, 90 324" stroke="#DC8751" stroke-width="1.2" stroke-linecap="round"/>
              <path d="M 134 310 C 135 318, 130 324, 130 333 M 119 311 C 117 316, 118 321, 120 324" stroke="#DC8751" stroke-width="1.2" stroke-linecap="round"/>

              <path d="M 73 185 C 94 189, 116 189, 137 185 C 143 204, 148 226, 148 244 C 146 251, 134 254, 107 253 L 106 245 L 104 245 L 103 253 C 76 254, 64 251, 62 244 C 62 226, 67 204, 73 185 Z" fill="#171615"/>

              <path d="M 86 38 C 83 37, 82 42, 84 46 C 85 48, 87 49, 88 48" fill="#F7C9A6" stroke="#DC8751" stroke-width="0.9"/>
              <path d="M 124 38 C 127 37, 128 42, 126 46 C 125 48, 123 49, 122 48" fill="#F7C9A6" stroke="#DC8751" stroke-width="0.9"/>
              <path d="M 86 28 C 86 16, 94 10, 105 10 C 116 10, 124 16, 124 28 C 124 44, 117 59, 105 59 C 93 59, 86 44, 86 28 Z" fill="#F7C9A6"/>

              <path d="M 86 34 C 84 25, 85 14, 92 10 C 98 6, 112 6, 119 11 C 125 15, 126 25, 124 34 C 123 28, 121 22, 117 20 C 111 18, 98 20, 92 18 C 88 21, 87 28, 86 34 Z" fill="#141313"/>

              <!-- Shoes -->
              <g>
                <path d="M 73 400 C 70 406, 65 418, 65 426 C 65 433, 73 436, 82 436 C 91 436, 95 432, 94 424 C 93 414, 93 405, 91 400 C 87 403, 78 403, 73 400 Z" fill="#0D0D0D"/>
                <path d="M 65 426 C 65 433, 73 436, 82 436 C 91 436, 95 432, 94 427 C 91 432, 70 432, 65 426 Z" fill="#AEACA9"/>
                <path d="M 76 408 L 86 408 L 76 412 L 86 415 L 76 418 L 86 420 L 76 421" stroke="#FFFFFF" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
              </g>
              <g>
                <path d="M 119 400 C 117 405, 117 414, 116 424 C 115 432, 119 436, 128 436 C 137 436, 145 433, 145 426 C 145 418, 140 406, 137 400 C 132 403, 123 403, 119 400 Z" fill="#0D0D0D"/>
                <path d="M 116 427 C 115 432, 119 436, 128 436 C 137 436, 145 433, 145 426 C 140 432, 119 432, 116 427 Z" fill="#AEACA9"/>
                <path d="M 124 408 L 134 408 L 124 412 L 134 415 L 124 418 L 134 420 L 124 421" stroke="#FFFFFF" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
              </g>

              <!-- FRONT HALF OF 3D GLOWING RINGS -->
              <g id="chestRing" class="ring-glow" onclick="switchCenterView('overview')">
                <path d="M 38 112 A 67 11 0 0 0 172 112" stroke="#FF6B63" stroke-width="3.2" stroke-opacity="0.45" filter="url(#redGlow)" fill="none" />
                <path d="M 38 112 A 67 11 0 0 0 172 112" stroke="#F0645A" stroke-width="1.7" fill="none" />
              </g>
              <g id="waistRing" class="ring-glow" onclick="switchCenterView('overview')">
                <path d="M 55 160 A 50 9 0 0 0 155 160" stroke="#FF6B63" stroke-width="3.2" stroke-opacity="0.45" filter="url(#redGlow)" fill="none" />
                <path d="M 55 160 A 50 9 0 0 0 155 160" stroke="#F0645A" stroke-width="1.7" fill="none" />
              </g>
              <g id="hipRing" class="ring-glow" onclick="switchCenterView('hardware-spec')">
                <path d="M 48 214 A 57 10 0 0 0 162 214" stroke="#FF6B63" stroke-width="3.2" stroke-opacity="0.45" filter="url(#redGlow)" fill="none" />
                <path d="M 48 214 A 57 10 0 0 0 162 214" stroke="#F0645A" stroke-width="1.7" fill="none" />
              </g>
            </svg>
          </div>

        </div>

      </div>

    </aside>

  </div>

  <!-- ================= JAVASCRIPT LOGIC ENGINE ================= -->
  <script>
    // -------------------------------------------------------------
    // 1. STATE & DATA MODELS FOR BOTH WORKERS
    // -------------------------------------------------------------
    let currentWorker = 2; // Default viewing Worker #02 (Agus Salim)
    let isSimulatorMode = false;
    let audioAlertEnabled = false;
    let audioCtx = null;
    let leafletMap = null;
    let hopPolyline = null;
    let uplinkPolyline = null;
    let watch1Marker = null;
    let watch2Marker = null;
    let gatewayMarker = null;
    let isDarkMapTile = false;

    // In-memory Audit Trail Log Data for Excel Export
    const auditLogsData = [];

    // Both workers initial state
    const workers = {
      1: {
        id: 'WRK-001',
        tagId: 'RESCUE-TAG-01',
        name: 'Bambang (Relay Host)',
        role: 'SAR Relawan & LoRa Relay Host',
        sector: 'Junction Poros Shaft B-02',
        hr: 106,
        spo2: 93,
        temp: 37.6,
        accel: 1.45,
        activity: 'Tremor / Kelelahan Ringan',
        route: 'Direct Uplink (Hop 1 Host)',
        rssi: -65,
        triageCode: 1, // KUNING
        triageLabel: 'KUNING - Delayed',
        isEmergency: false
      },
      2: {
        id: 'WRK-002',
        tagId: 'RESCUE-TAG-02',
        name: 'Agus Salim (Active Miner)',
        role: 'Operator Tambang Batubara',
        sector: 'Sektor 7 (Lorong C-4)',
        hr: 75,
        spo2: 98,
        temp: 36.5,
        accel: 1.02,
        activity: 'Diam / Istirahat Normal',
        route: '1-Hop Relay via Jam #01',
        rssi: -68,
        triageCode: 0, // HIJAU
        triageLabel: 'HIJAU - Minor (Aman)',
        isEmergency: false
      }
    };

    // -------------------------------------------------------------
    // 2. CENTER VIEW CONTROLLER (FULL VIEWS IN CONTAINER)
    // -------------------------------------------------------------
    function switchCenterView(viewId) {
      document.querySelectorAll('.center-view').forEach(v => v.classList.add('hidden'));
      const target = document.getElementById('view-' + viewId);
      if (target) {
        target.classList.remove('hidden');
      }

      document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
      const activeNav = document.getElementById('navBtn-' + viewId);
      if (activeNav) activeNav.classList.add('active');

      if (viewId === 'gis-map') {
        if (!leafletMap) {
          setTimeout(initLeafletMap, 100);
        } else {
          setTimeout(() => leafletMap.invalidateSize(), 150);
        }
      }
    }

    // -------------------------------------------------------------
    // 3. UI SYNCHRONIZATION WITH CURRENT WORKER
    // -------------------------------------------------------------
    function selectWorker(workerId) {
      currentWorker = workerId;
      const tab1 = document.getElementById('tabWorker01');
      const tab2 = document.getElementById('tabWorker02');
      if (tab1) tab1.classList.toggle('active', workerId === 1);
      if (tab2) tab2.classList.toggle('active', workerId === 2);
      
      const w = workers[workerId];
      const sectorEl = document.getElementById('headerSectorStatus');
      if (sectorEl) sectorEl.textContent = w.sector + ' • ' + w.route;
      
      const slHR = document.getElementById('sliderHR');
      const slSpO2 = document.getElementById('sliderSpO2');
      if (slHR) slHR.value = w.hr;
      if (slSpO2) slSpO2.value = w.spo2;
      
      const hrText = document.getElementById('simHRText');
      const spText = document.getElementById('simSpO2Text');
      if (hrText) hrText.textContent = w.hr + ' bpm';
      if (spText) spText.textContent = w.spo2 + ' %';

      updateTelemetryDisplay(w);
      evaluateSTART(w.hr, w.spo2);
      updateRosterTableUI();
    }

    function updateTelemetryDisplay(w) {
      const valHR = document.getElementById('val-hr');
      if (valHR) valHR.textContent = w.hr > 0 ? w.hr : '--';
      const badgeHR = document.getElementById('badge-hr');
      if (badgeHR) {
        if (w.hr > 120) {
          badgeHR.textContent = 'Takikardia';
          badgeHR.className = 'inline-block px-2.5 py-0.5 rounded-[5px] bg-[#FBE7E8] text-[#DE6D72] text-[10.5px] font-bold';
        } else if (w.hr < 50 && w.hr > 0) {
          badgeHR.textContent = 'Bradikardia';
          badgeHR.className = 'inline-block px-2.5 py-0.5 rounded-[5px] bg-[#FBE7E8] text-[#C0565B] text-[10.5px] font-bold';
        } else {
          badgeHR.textContent = 'Normal';
          badgeHR.className = 'inline-block px-2.5 py-0.5 rounded-[5px] bg-[#E8F8F0] text-[#1D6A4E] text-[10.5px] font-bold';
        }
      }

      const valSpO2 = document.getElementById('val-spo2');
      if (valSpO2) valSpO2.textContent = w.spo2 > 0 ? w.spo2 : '--';
      const badgeSpO2 = document.getElementById('badge-spo2');
      if (badgeSpO2) {
        if (w.spo2 < 90 && w.spo2 > 0) {
          badgeSpO2.textContent = 'Hipoksia Berat';
          badgeSpO2.className = 'inline-block px-2.5 py-0.5 rounded-[5px] bg-[#FBE7E8] text-[#DE6D72] text-[10.5px] font-bold';
        } else if (w.spo2 < 95 && w.spo2 > 0) {
          badgeSpO2.textContent = 'Hipoksia Ringan';
          badgeSpO2.className = 'inline-block px-2.5 py-0.5 rounded-[5px] bg-[#FFF2DE] text-[#A6681E] text-[10.5px] font-bold';
        } else {
          badgeSpO2.textContent = 'Normal';
          badgeSpO2.className = 'inline-block px-2.5 py-0.5 rounded-[5px] bg-[#D0F1F8] text-[#263C41] text-[10.5px] font-bold';
        }
      }

      const valTemp = document.getElementById('val-temp');
      if (valTemp) valTemp.textContent = w.temp.toFixed(1);
      const badgeTemp = document.getElementById('badge-temp');
      if (badgeTemp) {
        if (w.temp > 38.0) {
          badgeTemp.textContent = 'Hipertermia';
          badgeTemp.className = 'inline-block px-2.5 py-0.5 rounded-[5px] bg-[#FBE7E8] text-[#DE6D72] text-[10.5px] font-bold';
        } else if (w.temp < 35.5) {
          badgeTemp.textContent = 'Hipotermia';
          badgeTemp.className = 'inline-block px-2.5 py-0.5 rounded-[5px] bg-[#D0F1F8] text-[#1E4D57] text-[10.5px] font-bold';
        } else {
          badgeTemp.textContent = 'Normal';
          badgeTemp.className = 'inline-block px-2.5 py-0.5 rounded-[5px] bg-[#F8DFC2] text-[#3B352E] text-[10.5px] font-bold';
        }
      }

      const accelPill = document.getElementById('liveAccelPill');
      if (accelPill) {
        if (w.accel > 3.0) {
          accelPill.className = 'px-2.5 py-0.5 rounded-[6px] bg-red-100 text-red-700 font-mono text-[10.5px] font-bold animate-pulse';
          accelPill.textContent = w.accel.toFixed(2) + 'g • BENTURAN SHOCK';
        } else {
          accelPill.className = 'px-2.5 py-0.5 rounded-[6px] bg-[#EFE9E0] text-[#3E3C39] font-mono text-[10.5px] font-bold';
          accelPill.textContent = w.accel.toFixed(2) + 'g • ' + w.activity;
        }
      }
    }

    function updateRosterTableUI() {
      const w1 = workers[1];
      const w2 = workers[2];

      const v1 = document.getElementById('rosterVitals01');
      if (v1) v1.innerHTML = w1.hr + ' BPM &bull; ' + w1.spo2 + '% SpO2 &bull; ' + w1.temp.toFixed(1) + '&deg;C';
      const a1 = document.getElementById('rosterActivity01');
      if (a1) a1.textContent = w1.activity;
      const t1 = document.getElementById('rosterTriage01');
      if (t1) {
        t1.textContent = w1.triageLabel;
        t1.className = w1.triageCode === 3 
          ? 'px-2.5 py-1 rounded bg-red-100 text-red-900 border border-red-300 font-bold text-[10px] animate-pulse'
          : (w1.triageCode === 1 ? 'px-2.5 py-1 rounded bg-amber-100 text-amber-900 border border-amber-300 font-bold text-[10px]' : 'px-2.5 py-1 rounded bg-emerald-100 text-emerald-900 border border-emerald-300 font-bold text-[10px]');
      }

      const v2 = document.getElementById('rosterVitals02');
      if (v2) v2.innerHTML = w2.hr + ' BPM &bull; ' + w2.spo2 + '% SpO2 &bull; ' + w2.temp.toFixed(1) + '&deg;C';
      const a2 = document.getElementById('rosterActivity02');
      if (a2) a2.textContent = w2.activity;
      const t2 = document.getElementById('rosterTriage02');
      if (t2) {
        t2.textContent = w2.triageLabel;
        t2.className = w2.triageCode === 3 
          ? 'px-2.5 py-1 rounded bg-red-100 text-red-900 border border-red-300 font-bold text-[10px] animate-pulse'
          : 'px-2.5 py-1 rounded bg-emerald-100 text-emerald-900 border border-emerald-300 font-bold text-[10px]';
      }
    }

    // -------------------------------------------------------------
    // 4. START TRIAGE RISK SIMULATOR ENGINE
    // -------------------------------------------------------------
    function onSimulatorInput() {
      isSimulatorMode = true;
      const label = document.getElementById('simModeLabel');
      const ind = document.getElementById('simModeIndicator');
      if (label) label.textContent = 'Simulator';
      if (ind) ind.textContent = 'MANUAL';
      
      const hr = parseInt(document.getElementById('sliderHR').value);
      const spo2 = parseInt(document.getElementById('sliderSpO2').value);

      const hrText = document.getElementById('simHRText');
      const spText = document.getElementById('simSpO2Text');
      if (hrText) hrText.textContent = hr + ' bpm';
      if (spText) spText.textContent = spo2 + ' %';

      evaluateSTART(hr, spo2);
    }

    function toggleSimMode() {
      isSimulatorMode = !isSimulatorMode;
      const label = document.getElementById('simModeLabel');
      const ind = document.getElementById('simModeIndicator');
      if (isSimulatorMode) {
        if (label) label.textContent = 'Simulator';
        if (ind) ind.textContent = 'MANUAL';
      } else {
        if (label) label.textContent = 'Live MQTT';
        if (ind) ind.textContent = 'LIVE';
        const w = workers[currentWorker];
        const slHR = document.getElementById('sliderHR');
        const slSpO2 = document.getElementById('sliderSpO2');
        if (slHR) slHR.value = w.hr;
        if (slSpO2) slSpO2.value = w.spo2;
        const hrText = document.getElementById('simHRText');
        const spText = document.getElementById('simSpO2Text');
        if (hrText) hrText.textContent = w.hr + ' bpm';
        if (spText) spText.textContent = w.spo2 + ' %';
        evaluateSTART(w.hr, w.spo2);
      }
    }

    function setTriageDirect(tier) {
      isSimulatorMode = true;
      const label = document.getElementById('simModeLabel');
      const ind = document.getElementById('simModeIndicator');
      if (label) label.textContent = 'Simulator';
      if (ind) ind.textContent = tier;

      const slHR = document.getElementById('sliderHR');
      const slSpO2 = document.getElementById('sliderSpO2');
      if (tier === 'HIJAU') {
        if (slHR) slHR.value = 75;
        if (slSpO2) slSpO2.value = 98;
      } else if (tier === 'KUNING') {
        if (slHR) slHR.value = 106;
        if (slSpO2) slSpO2.value = 93;
      } else if (tier === 'MERAH') {
        if (slHR) slHR.value = 138;
        if (slSpO2) slSpO2.value = 86;
      } else if (tier === 'HITAM') {
        if (slHR) slHR.value = 40;
        if (slSpO2) slSpO2.value = 70;
      }
      onSimulatorInput();
    }

    function onTriageBarClick(e) {
      const rect = e.currentTarget.getBoundingClientRect();
      const pct = (e.clientX - rect.left) / rect.width;
      if (pct < 0.28) setTriageDirect('HIJAU');
      else if (pct < 0.58) setTriageDirect('KUNING');
      else if (pct < 0.85) setTriageDirect('MERAH');
      else setTriageDirect('HITAM');
    }

    function evaluateSTART(hr, spo2) {
      const pText = document.getElementById('triagePriorityText');
      const dot = document.getElementById('triageDot');
      const badge = document.getElementById('triageBadgePill');

      if (hr <= 40 || (hr > 160 && spo2 < 75)) {
        if (pText) {
          pText.textContent = 'HITAM';
          pText.className = 'text-[20px] font-extrabold text-gray-400 leading-none font-mono';
        }
        if (dot) dot.style.left = '92%';
        if (badge) {
          badge.textContent = 'Expectant';
          badge.className = 'px-2.5 py-1 rounded-[7px] bg-gray-700 text-gray-200 text-[10px] font-bold';
        }
      } else if (hr > 125 || hr < 48 || spo2 < 88) {
        if (pText) {
          pText.textContent = 'MERAH';
          pText.className = 'text-[20px] font-extrabold text-[#EF4444] leading-none font-mono animate-pulse';
        }
        if (dot) dot.style.left = '80%';
        if (badge) {
          badge.textContent = 'Immediate SOS';
          badge.className = 'px-2.5 py-1 rounded-[7px] bg-[#FAD2D4] text-[#4A1C1F] text-[10px] font-bold animate-pulse';
        }
        if (audioAlertEnabled) playEmergencyBeep();
      } else if (hr > 100 || spo2 < 94) {
        if (pText) {
          pText.textContent = 'KUNING';
          pText.className = 'text-[20px] font-extrabold text-[#F59E0B] leading-none font-mono';
        }
        if (dot) dot.style.left = '52%';
        if (badge) {
          badge.textContent = 'Delayed';
          badge.className = 'px-2.5 py-1 rounded-[7px] bg-[#F7E8BA] text-[#453813] text-[10px] font-bold';
        }
      } else {
        if (pText) {
          pText.textContent = 'HIJAU';
          pText.className = 'text-[20px] font-extrabold text-[#34D399] leading-none font-mono';
        }
        if (dot) dot.style.left = '18%';
        if (badge) {
          badge.textContent = "You're Healthy";
          badge.className = 'px-2.5 py-1 rounded-[7px] bg-[#D5F4EA] text-[#213B33] text-[10px] font-bold';
        }
      }
    }

    // -------------------------------------------------------------
    // 5. 18 MULTI-SEGMENT BARS MATCHING DESKTOP - 2.JPG
    // -------------------------------------------------------------
    const janData = [
      [27, 46, 19], [11, 65, 22], [48, 17, 13], [38, 22, 8], [13, 25, 42],
      [24, 42, 11], [54, 30, 17], [27, 40, 21], [12, 46, 33], [17, 16, 46],
      [21, 13, 18], [38, 14, 17], [25, 36, 36], [39, 17, 36], [41, 16, 18],
      [53, 30, 11], [29, 12, 9],  [38, 39, 18]
    ];

    const febData = [
      [34, 38, 18], [20, 52, 20], [42, 22, 16], [30, 28, 14], [18, 32, 34],
      [28, 38, 15], [48, 26, 20], [32, 36, 18], [18, 42, 28], [22, 20, 40],
      [26, 18, 20], [34, 20, 18], [28, 34, 30], [35, 22, 32], [38, 20, 20],
      [48, 26, 15], [32, 18, 12], [40, 34, 20]
    ];

    let currentShiftIndex = 0;
    const shifts = [
      { label: 'Shift Pagi // Sektor 7', prefix: 'T+', data: janData },
      { label: 'Shift Siang // Lorong C', prefix: 'T+', data: febData }
    ];

    function renderKinematicsBars() {
      const container = document.getElementById('kinematicsBarsContainer');
      if (!container) return;
      const activeShift = shifts[currentShiftIndex];
      container.innerHTML = '';

      activeShift.data.forEach((segments, idx) => {
        const [redH, tealH, ochreH] = segments;
        const intervalNum = (idx * 10);

        const col = document.createElement('div');
        col.className = 'day-col flex flex-col items-center justify-end h-full relative cursor-pointer group';
        col.style.width = '18px';
        col.onclick = () => {
          const g = ((redH * 0.04) + (tealH * 0.02) + (ochreH * 0.015)).toFixed(2);
          const pill = document.getElementById('liveAccelPill');
          if (pill) pill.textContent = g + 'g @ T+' + intervalNum + 'm';
        };

        const totalG = ((redH * 0.04) + (tealH * 0.02) + (ochreH * 0.015)).toFixed(2);
        col.innerHTML = `
          <div class="opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity duration-150 absolute -top-7 bg-[#2C2A2A] text-white text-[9.5px] font-mono font-bold px-2 py-0.5 rounded shadow-md whitespace-nowrap z-20">
            T+` + intervalNum + `m: ` + totalG + `g
          </div>
          <div class="flex flex-col items-center gap-[5px] mb-1">
            <span class="pill-seg w-[4.5px] rounded-full bg-[#CC8B3C]" style="height: ` + ochreH + `px"></span>
            <span class="pill-seg w-[4.5px] rounded-full bg-[#3E8D9B]" style="height: ` + tealH + `px"></span>
            <span class="pill-seg w-[4.5px] rounded-full bg-[#DA7468]" style="height: ` + redH + `px"></span>
          </div>
          <div class="h-0 w-full flex justify-end">
            <span class="x-label">T+` + intervalNum + `m</span>
          </div>
        `;
        container.appendChild(col);
      });
    }

    function cycleShift() {
      currentShiftIndex = (currentShiftIndex + 1) % shifts.length;
      const shiftEl = document.getElementById('shiftLabel');
      if (shiftEl) shiftEl.textContent = shifts[currentShiftIndex].label;
      renderKinematicsBars();
    }

    // -------------------------------------------------------------
    // 6. 3D GLOWING RING HIGHLIGHT ON CARD HOVER
    // -------------------------------------------------------------
    function highlightRing(ringId, isHover) {
      const ring = document.getElementById(ringId);
      if (!ring) return;
      if (isHover) {
        ring.style.transform = 'scale(1.03)';
        ring.style.transformOrigin = '105px center';
        ring.style.filter = 'drop-shadow(0 0 10px rgba(255, 95, 85, 0.95))';
      } else {
        ring.style.transform = 'scale(1)';
        ring.style.filter = 'drop-shadow(0 0 5px rgba(240, 82, 72, 0.65))';
      }
    }

    function highlightSensorRing(ringId, isHover) {
      highlightRing(ringId, isHover);
    }

    // -------------------------------------------------------------
    // 7. LEAFLET SUBTERRANEAN GIS MINE MAP
    // -------------------------------------------------------------
    function initLeafletMap() {
      const mapContainer = document.getElementById('leafletMapContainer');
      if (!mapContainer || leafletMap) return;

      const gatewayPos = [-8.2435, 113.6928];
      const watch1Pos = [-8.2465, 113.6965];
      const watch2Pos = [-8.2498, 113.7012];

      leafletMap = L.map('leafletMapContainer', {
        zoomControl: true,
        attributionControl: false
      }).setView(watch1Pos, 15);

      L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
        maxZoom: 16
      }).addTo(leafletMap);

      const createMarker = (title, subtitle, color) => {
        return L.divIcon({
          className: 'tactical-div-icon',
          html: `<div style="background: rgba(255,255,255,0.96); border: 1.5px solid ` + color + `; padding: 4px 8px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.12); display: flex; align-items: center; gap: 6px; white-space: nowrap; font-family: monospace; font-size: 10px; color: #2D2B2A;">
                   <span style="width: 8px; height: 8px; border-radius: 999px; background: ` + color + `;"></span>
                   <b>` + title + `</b>
                   <span style="color: #7B7874;">(` + subtitle + `)</span>
                 </div>`,
          iconSize: [180, 26],
          iconAnchor: [90, 24]
        });
      };

      gatewayMarker = L.marker(gatewayPos, {
        icon: createMarker('GATEWAY BASECAMP', 'Surface Node', '#059669')
      }).addTo(leafletMap).bindPopup('<div class="font-mono text-xs"><b>Posko Permukaan Basecamp</b><br/>ESP32 Gateway + LTE Uplink</div>');

      watch1Marker = L.marker(watch1Pos, {
        icon: createMarker('JAM #01: BAMBANG', 'Relay Host', '#D97706')
      }).addTo(leafletMap).bindPopup('<div class="font-mono text-xs"><b>Jam Tangan #01: Bambang</b><br/>Junction B-02 Poros Shaft<br/>Peran: LoRa 1-Hop Mesh Relay Forwarder</div>');

      watch2Marker = L.marker(watch2Pos, {
        icon: createMarker('JAM #02: AGUS SALIM', 'Sektor 7 Miner', '#2563EB')
      }).addTo(leafletMap).bindPopup('<div class="font-mono text-xs"><b>Jam Tangan #02: Agus Salim</b><br/>Lorong C-4 Sektor 7 Tambang<br/>Status: Normal / Terhubung Mesh</div>');

      hopPolyline = L.polyline([watch2Pos, watch1Pos], {
        color: '#10B981',
        weight: 3.5,
        opacity: 0.85
      }).addTo(leafletMap);

      uplinkPolyline = L.polyline([watch1Pos, gatewayPos], {
        color: '#EA580C',
        weight: 4,
        dashArray: '6, 6',
        opacity: 0.9
      }).addTo(leafletMap);
    }

    function toggleMapTileStyle() {
      if (!leafletMap) return;
      isDarkMapTile = !isDarkMapTile;
      leafletMap.eachLayer((layer) => {
        if (layer instanceof L.TileLayer) {
          leafletMap.removeLayer(layer);
        }
      });

      const url = isDarkMapTile 
        ? 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
        : 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}';
      
      L.tileLayer(url, { maxZoom: 16 }).addTo(leafletMap);
    }

    function focusMapNode(id) {
      if (!leafletMap) return;
      if (id === 1 && watch1Marker) {
        leafletMap.setView(watch1Marker.getLatLng(), 16);
        watch1Marker.openPopup();
      } else if (id === 2 && watch2Marker) {
        leafletMap.setView(watch2Marker.getLatLng(), 16);
        watch2Marker.openPopup();
      }
    }

    function focusFromRoster(workerId) {
      selectWorker(workerId);
      switchCenterView('gis-map');
      setTimeout(() => focusMapNode(workerId), 250);
    }

    function pulseHopSimulation() {
      if (!hopPolyline || !uplinkPolyline) return;
      hopPolyline.setStyle({ weight: 7, color: '#FCD34D' });
      setTimeout(() => {
        hopPolyline.setStyle({ weight: 3.5, color: '#10B981' });
        uplinkPolyline.setStyle({ weight: 7, color: '#EF4444' });
        setTimeout(() => {
          uplinkPolyline.setStyle({ weight: 4, color: '#EA580C' });
          appendAuditTrail('LoRa 1-Hop Mesh Transmission Success', 'Jam Tangan #01', 'Jam #02 -> Jam #01 -> Surface Gateway Basecamp (18ms)', 'teal');
        }, 600);
      }, 600);
    }

    function runDiagWatch(workerId) {
      const w = workers[workerId];
      alert("DIAGNOSTIK JAM TANGAN #" + (workerId < 10 ? '0' + workerId : workerId) + " (" + w.name + "):\nStatus Hardware: Aktif Normal\nLoRa Link: " + w.route + " (" + w.rssi + " dBm)\nVitals: " + w.hr + " BPM • " + w.spo2 + "% SpO2 • " + w.temp.toFixed(1) + "°C\nTriage: " + w.triageLabel + "\nBaterai LiPo: 81% (4.12V)\nForwarding Mesh: 1-Hop P2P Aktif");
    }

    // -------------------------------------------------------------
    // 8. CHRONOLOGICAL AUDIT TRAIL & EXCEL DOWNLOAD
    // -------------------------------------------------------------
    function appendAuditTrail(title, nodeName, detailText, level) {
      const now = new Date();
      const timeStr = now.toTimeString().split(' ')[0] + ' UTC';
      
      const logItem = {
        time: timeStr,
        title: title,
        node: nodeName,
        desc: detailText,
        status: level === 'red' ? 'MERAH (Immediate)' : (level === 'amber' ? 'KUNING (Delayed)' : 'HIJAU (Normal)'),
        severity: level
      };
      auditLogsData.unshift(logItem);

      const container = document.getElementById('auditLogList');
      if (!container) return;

      const div = document.createElement('div');
      
      let borderClass = 'border-l-4 border-emerald-500 bg-white text-slate-800';
      if (level === 'red') {
        borderClass = 'border-l-4 border-red-500 bg-red-50/70 text-red-900';
      } else if (level === 'amber') {
        borderClass = 'border-l-4 border-amber-500 bg-amber-50/70 text-amber-900';
      } else if (level === 'teal') {
        borderClass = 'border-l-4 border-teal-500 bg-teal-50/70 text-teal-900';
      }

      div.className = 'p-3.5 rounded-xl border border-[#F0ECE6] shadow-sm ' + borderClass + ' transition';
      div.innerHTML = `
        <div class="flex justify-between font-bold text-xs">
          <span>` + timeStr + ` &bull; ` + title + `</span>
          <span class="text-[10px] uppercase font-mono tracking-wider">` + nodeName + `</span>
        </div>
        <p class="text-[11px] text-[#5A5754] mt-1">` + detailText + `</p>
      `;

      container.insertBefore(div, container.firstChild);

      const badge = document.getElementById('alertCountBadge');
      if (badge && level === 'red') {
        const count = parseInt(badge.textContent || '0') + 1;
        badge.textContent = count;
      }
    }

    // Excel Export Feature (RFC-4180 CSV with UTF-8 BOM)
    function downloadChronologicalExcel() {
      let csv = "\uFEFF"; // UTF-8 BOM for Microsoft Excel auto-encoding
      csv += "Timestamp (UTC);Event Title;Personnel / Node;Details Description;Triage Status;Severity Tier\n";
      
      auditLogsData.forEach(item => {
        csv += '"' + item.time + '";"' + item.title + '";"' + item.node + '";"' + item.desc.replace(/"/g, '""') + '";"' + item.status + '";"' + item.severity + '"\n';
      });

      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      const dateStr = new Date().toISOString().split('T')[0];
      link.setAttribute("href", url);
      link.setAttribute("download", "RescueTag_SAR_Audit_Trail_" + dateStr + ".csv");
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      alert("FILE EXCEL BERHASIL DIUNDUH!\nNama File: RescueTag_SAR_Audit_Trail_" + dateStr + ".csv\nFormat: Microsoft Excel Compatible (UTF-8 BOM)");
    }

    function dispatchAlphaSquad() {
      alert("PERINTAH DISPATCH TERKIRIM:\nRegu Penolong Alpha Search Squad telah diberangkatkan menuju Sektor 7 (C-4) untuk evakuasi darurat!");
      appendAuditTrail('SAR Alpha Squad Dispatched', 'COMMAND HUB', 'Unit penolong bergerak menuju Sektor 7 (C-4)', 'red');
      pulseHopSimulation();
    }

    // -------------------------------------------------------------
    // 9. WEB AUDIO API SYNTHESIZER FOR EMERGENCY ALERT
    // -------------------------------------------------------------
    function toggleAudioAlert() {
      audioAlertEnabled = !audioAlertEnabled;
      const btn = document.getElementById('sirenBtn');
      if (audioAlertEnabled) {
        if (btn) {
          btn.classList.add('bg-red-500', 'text-white');
          btn.classList.remove('nav-btn');
          btn.style.width = '44px';
          btn.style.height = '44px';
        }
        playEmergencyBeep();
      } else {
        if (btn) {
          btn.classList.remove('bg-red-500', 'text-white');
          btn.classList.add('nav-btn');
        }
      }
    }

    function playEmergencyBeep() {
      try {
        if (!audioCtx) {
          audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        }
        if (audioCtx.state === 'suspended') {
          audioCtx.resume();
        }
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(880, audioCtx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(440, audioCtx.currentTime + 0.35);
        gain.gain.setValueAtTime(0.2, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.35);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.36);
      } catch (err) {
        console.warn('Audio alert blocked:', err);
      }
    }

    // -------------------------------------------------------------
    // 10. REAL-TIME MQTT ENGINE (broker.emqx.io:8084)
    // -------------------------------------------------------------
    function initMQTT() {
      const dot = document.getElementById('mqttDot');
      try {
        const clientId = 'rescuetag_cmd_' + Math.random().toString(16).substring(2, 8);
        const client = mqtt.connect('wss://broker.emqx.io:8084/mqtt', {
          clientId: clientId,
          clean: true,
          connectTimeout: 5000,
          reconnectPeriod: 3000
        });

        client.on('connect', () => {
          console.log('[MQTT] Connected to broker.emqx.io:8084');
          if (dot) dot.className = 'w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)]';
          client.subscribe('rescue/tag/data');
          client.subscribe('rescue/tag/alert');
          appendAuditTrail('MQTT EMQX Online', 'EMQX BROKER', 'Listening to rescue/tag/data & rescue/tag/alert', 'teal');
        });

        client.on('message', (topic, payload) => {
          try {
            const data = JSON.parse(payload.toString());
            console.log('[MQTT RX]', topic, data);

            let workerNum = 2;
            if (data.device_id === 'RESCUE-TAG-01' || data.worker_id === 'WRK-001' || (data.worker_name && data.worker_name.includes('Bambang'))) {
              workerNum = 1;
            }

            const w = workers[workerNum];
            if (data.vitals) {
              if (data.vitals.hr) w.hr = data.vitals.hr;
              if (data.vitals.spo2) w.spo2 = data.vitals.spo2;
              if (data.vitals.temp) w.temp = data.vitals.temp;
            }
            if (data.kinematics) {
              if (data.kinematics.a_max) w.accel = data.kinematics.a_max;
              if (data.kinematics.summary) w.activity = data.kinematics.summary;
            }
            if (data.triage) {
              if (data.triage.code !== undefined) w.triageCode = data.triage.code;
              if (data.triage.label) w.triageLabel = data.triage.label;
              if (data.triage.is_emergency !== undefined) w.isEmergency = data.triage.is_emergency;
            }

            updateRosterTableUI();

            if (currentWorker === workerNum && !isSimulatorMode) {
              updateTelemetryDisplay(w);
              evaluateSTART(w.hr, w.spo2);
              const slHR = document.getElementById('sliderHR');
              const slSpO2 = document.getElementById('sliderSpO2');
              if (slHR) slHR.value = w.hr;
              if (slSpO2) slSpO2.value = w.spo2;
              const hrText = document.getElementById('simHRText');
              const spText = document.getElementById('simSpO2Text');
              if (hrText) hrText.textContent = w.hr + ' bpm';
              if (spText) spText.textContent = w.spo2 + ' %';
            }

            if (topic === 'rescue/tag/alert' || w.triageCode === 3) {
              appendAuditTrail(
                'DARURAT MEDIS / IMPACT DETECTED',
                w.tagId,
                w.name + ' di ' + w.sector + '. HR: ' + w.hr + ' BPM, SpO2: ' + w.spo2 + '%. Prioritas SAR MERAH!',
                'red'
              );
              if (audioAlertEnabled) playEmergencyBeep();
            }

          } catch (err) {
            console.warn('[MQTT PARSE ERR]', err);
          }
        });

        client.on('offline', () => {
          if (dot) dot.className = 'w-2.5 h-2.5 rounded-full bg-amber-500';
        });

        client.on('error', (err) => {
          if (dot) dot.className = 'w-2.5 h-2.5 rounded-full bg-red-500';
        });

      } catch (e) {
        console.warn('Running in autonomous simulation mode', e);
        if (dot) dot.className = 'w-2.5 h-2.5 rounded-full bg-gray-500';
      }
    }

    // -------------------------------------------------------------
    // 11. DEMO TRIGGER FUNCTIONS FOR COMPETITION JURY
    // -------------------------------------------------------------
    function testSimSOS() {
      const w = workers[2];
      w.hr = 138;
      w.spo2 = 86;
      w.temp = 38.6;
      w.accel = 4.85;
      w.activity = 'Free-Fall & Immobility >30s';
      w.triageCode = 3;
      w.triageLabel = 'MERAH - Immediate (SOS)';
      w.isEmergency = true;

      selectWorker(2);
      appendAuditTrail('Simulated Free-Fall Shock & Tachycardia', 'Agus Salim', 'Sektor 7: Benturan 4.85g dan Hipoksia 86%', 'red');
      pulseHopSimulation();
    }

    function testSimNormal() {
      const w = workers[2];
      w.hr = 75;
      w.spo2 = 98;
      w.temp = 36.5;
      w.accel = 1.02;
      w.activity = 'Diam / Istirahat Normal';
      w.triageCode = 0;
      w.triageLabel = 'HIJAU - Minor (Aman)';
      w.isEmergency = false;

      selectWorker(2);
      appendAuditTrail('Simulated Normal Baseline Telemetry', 'Agus Salim', 'Sektor 7: Vitals stabil', 'green');
    }

    function toggleMqttInfo() {
      alert("MQTT BROKER STATUS:\nBroker: broker.emqx.io\nPort: 8084 (Secure WebSocket)\nTopics: rescue/tag/data, rescue/tag/alert\nRelay: LoRa 1-Hop Mesh P2P");
    }

    // -------------------------------------------------------------
    // 12. INITIALIZATION ON LOAD
    // -------------------------------------------------------------
    window.addEventListener('DOMContentLoaded', () => {
      // 1. Clock
      setInterval(() => {
        const now = new Date();
        const clk = document.getElementById('liveClock');
        if (clk) clk.textContent = now.toTimeString().split(' ')[0] + ' UTC';
      }, 1000);

      // 2. Kinematics Bars
      renderKinematicsBars();

      // 3. Select Worker #02 default
      selectWorker(2);

      // 4. Initial Seed Audit Logs
      appendAuditTrail('RescueTag Command Hub Initialized', 'BASECAMP', 'Dual-worker subterranean mesh gateway ready', 'teal');
      appendAuditTrail('LoRa 1-Hop Mesh Topology Synchronized', 'Jam Tangan #01', 'Node #02 (Sektor 7) -> Node #01 Relay (Junction B-02)', 'amber');

      // 5. Connect MQTT
      initMQTT();
    });
  </script>
</body>
</html>
'''

# Replace base64 image placeholder
final_html = HTML_TEMPLATE.replace("BASE64_IMAGE_PLACEHOLDER", data_uri)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(final_html)

print("Generated index.html v2 successfully! Total size:", len(final_html))
