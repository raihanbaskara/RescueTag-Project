# -*- coding: utf-8 -*-
"""
Upgraded build script for RescueTag Dashboard.
Enforces:
1. 100% interactive clickable elements (Zero dead buttons).
2. Doppelrand 3-column architecture (84px | 1fr | 414px) with high-end-visual-design.
3. Zero-emoji compliance with gpt-taste.
4. Semantic tokens and color system with stitch-design-taste.
5. Full dual-worker telemetry & interactive Subterranean Fleet Roster table with Focus Map & Run Diag.
6. Interactive Metric Modals, START Triage gauge clicks, Search modal, and SAR Dispatch modal.
"""

import os
import base64

# Read base64 image for self-contained embedding
with open('smartwatch_grey_oled.png', 'rb') as f:
    b64_img = base64.b64encode(f.read()).decode('utf-8')
data_uri = f"data:image/png;base64,{b64_img}"

HTML_TEMPLATE = r"""<!DOCTYPE html>
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
      overflow-x: hidden;
    }

    .font-mono {
      font-family: 'JetBrains Mono', monospace;
    }

    /* Doppelrand (Double-Bezel) Container Architecture */
    .dashboard-wrapper {
      width: 100%;
      max-width: 1400px;
      min-height: 880px;
      background-color: #FAF6F1;
      border-radius: 34px;
      display: grid;
      grid-template-columns: 84px 1fr 414px;
      overflow: hidden;
      box-shadow: 0 35px 80px -15px rgba(0, 0, 0, 0.85), 0 0 0 1px rgba(255, 255, 255, 0.12);
      position: relative;
      border: 1px solid rgba(255, 255, 255, 0.14);
      margin: 1.5rem auto;
      transition: all 0.3s cubic-bezier(0.32, 0.72, 0, 1);
    }

    @media (max-width: 1200px) {
      .dashboard-wrapper {
        grid-template-columns: 84px 1fr;
        min-height: auto;
      }
      .right-tactical-panel {
        grid-column: span 2;
        border-radius: 0 !important;
      }
    }

    @media (max-width: 820px) {
      .dashboard-wrapper {
        grid-template-columns: 1fr;
        border-radius: 20px;
        margin: 0.5rem;
      }
      .left-sidebar {
        flex-direction: row !important;
        width: 100% !important;
        height: auto !important;
        padding: 0.75rem 1.25rem !important;
        border-right: none !important;
        border-bottom: 1px solid #F0ECE6 !important;
      }
      .left-sidebar nav {
        flex-direction: row !important;
        margin-top: 0 !important;
        gap: 0.75rem !important;
      }
      .right-tactical-panel {
        grid-column: span 1;
      }
    }

    /* Tactile Metric Cards with Spring Hover */
    .metric-card {
      background: #FFFFFF;
      border-radius: 20px;
      border: 1px solid #F0ECE6;
      box-shadow: 0 10px 30px rgba(145, 132, 118, 0.08);
      transition: transform 0.25s cubic-bezier(0.32, 0.72, 0, 1), box-shadow 0.25s cubic-bezier(0.32, 0.72, 0, 1);
      cursor: pointer;
    }
    .metric-card:hover {
      transform: translateY(-3px);
      box-shadow: 0 18px 40px rgba(145, 132, 118, 0.15);
    }
    .metric-card:active {
      transform: translateY(-1px) scale(0.995);
    }

    /* Icon Action Buttons */
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
      transition: all 0.2s cubic-bezier(0.32, 0.72, 0, 1);
    }
    .icon-btn:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 20px rgba(0, 0, 0, 0.09);
      background: #FAF6F1;
    }
    .icon-btn:active {
      transform: scale(0.96);
    }

    /* Left Nav Buttons */
    .nav-btn {
      width: 46px;
      height: 46px;
      border-radius: 14px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #716E6A;
      cursor: pointer;
      transition: all 0.2s cubic-bezier(0.32, 0.72, 0, 1);
      position: relative;
    }
    .nav-btn:hover {
      background: #F4EFEA;
      color: #1F1E1E;
      transform: translateY(-1px);
    }
    .nav-btn:active {
      transform: scale(0.94);
    }
    .nav-btn.active {
      background: #2C2A2A;
      color: #FFFFFF;
      box-shadow: 0 8px 18px rgba(44, 42, 42, 0.3);
    }

    /* START Triage Dynamic Gradient Bar */
    .triage-gradient-bar {
      height: 10px;
      border-radius: 999px;
      background: linear-gradient(90deg, 
        #34D399 0%, 
        #A7F3D0 25%, 
        #FDE68A 50%, 
        #F59E0B 70%, 
        #EF4444 88%,
        #1E293B 100%
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
      height: 30px;
      background: transparent;
      cursor: ew-resize;
      position: absolute;
      top: 4px;
      left: 0;
      z-index: 10;
      opacity: 0;
    }

    /* Multi-segment Pill Bars */
    .day-col:hover .pill-seg {
      filter: brightness(1.2);
      transform: scaleX(1.3);
    }
    .day-col.selected-bar .pill-seg {
      filter: brightness(1.3) drop-shadow(0 0 4px rgba(229, 154, 67, 0.8));
      transform: scaleX(1.4);
    }
    .pill-seg {
      transition: all 0.2s cubic-bezier(0.32, 0.72, 0, 1);
    }

    /* 3D Anatomical Ring Glow Effects */
    .ring-glow {
      filter: drop-shadow(0 0 6px rgba(240, 82, 72, 0.7));
      transition: all 0.28s cubic-bezier(0.32, 0.72, 0, 1);
      cursor: pointer;
    }
    .ring-glow:hover {
      filter: drop-shadow(0 0 14px rgba(255, 140, 60, 1)) !important;
      transform: scale(1.08);
      transform-origin: center center;
    }

    .measure-card {
      transition: all 0.2s cubic-bezier(0.32, 0.72, 0, 1);
      cursor: pointer;
    }
    .measure-card:hover {
      transform: translateX(4px);
      box-shadow: 0 8px 22px rgba(0, 0, 0, 0.35);
      background-color: #383535;
    }
    .measure-card:active {
      transform: scale(0.98);
    }

    /* Worker Selector Switcher */
    .worker-pill-btn {
      padding: 6px 14px;
      border-radius: 12px;
      font-size: 11.5px;
      font-weight: 700;
      transition: all 0.2s cubic-bezier(0.32, 0.72, 0, 1);
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 7px;
    }
    .worker-pill-btn.active {
      background: #2C2A2A;
      color: #FFFFFF;
      box-shadow: 0 4px 12px rgba(44, 42, 42, 0.2);
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

    /* Modal Backdrop */
    .modal-overlay {
      position: fixed;
      inset: 0;
      background: rgba(10, 10, 10, 0.84);
      backdrop-filter: blur(8px);
      z-index: 100;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 1.5rem;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.25s cubic-bezier(0.32, 0.72, 0, 1);
    }
    .modal-overlay.open {
      opacity: 1;
      pointer-events: auto;
    }

    /* Subtle Table Styles */
    .tactical-table th {
      font-family: 'JetBrains Mono', monospace;
      font-size: 10px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #9C9892;
      padding: 10px 12px;
      text-align: left;
      border-bottom: 1px solid #383535;
    }
    .tactical-table td {
      font-size: 11.5px;
      padding: 12px;
      border-bottom: 1px solid #2B2828;
    }
  </style>
</head>
<body>

  <!-- ================= MASTER DASHBOARD CONTAINER ================= -->
  <div class="dashboard-wrapper">

    <!-- ================= 1. LEFT SIDEBAR (84px) ================= -->
    <aside class="left-sidebar bg-white h-full flex flex-col items-center py-7 justify-between border-r border-[#F0ECE6] z-10 select-none">
      
      <!-- Top High-Tech RescueTag Emblem (Clickable to Reset) -->
      <button class="cursor-pointer group flex flex-col items-center focus:outline-none" onclick="resetToOverview()" title="Reset View to Command Hub">
        <div class="w-11 h-11 rounded-2xl bg-gradient-to-br from-[#2D2B2A] to-[#171615] flex items-center justify-center shadow-md group-hover:scale-105 transition-transform">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#E59A43" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
            <polyline points="2 17 12 22 22 17"></polyline>
            <polyline points="2 12 12 17 22 12"></polyline>
          </svg>
        </div>
        <span class="text-[9px] font-mono font-bold tracking-widest text-[#9C9892] mt-1.5 uppercase">SEC-01</span>
      </button>

      <!-- Navigation Tactile Icons -->
      <nav class="flex flex-col items-center gap-5 my-auto">
        <!-- 1. Overview Dashboard (Active) -->
        <button id="navBtnOverview" class="nav-btn active" onclick="setActiveNav(this, 'overview')" title="Command Overview (3-Column Doppelrand)">
          <svg width="19" height="19" viewBox="0 0 20 20" fill="none">
            <rect x="2" y="2" width="6.5" height="6.5" rx="1.5" fill="currentColor"/>
            <rect x="11.5" y="2" width="6.5" height="4.5" rx="1.5" fill="currentColor"/>
            <rect x="2" y="11.5" width="6.5" height="6.5" rx="1.5" fill="currentColor"/>
            <rect x="11.5" y="9.5" width="6.5" height="8.5" rx="1.5" fill="currentColor"/>
          </svg>
        </button>

        <!-- 2. Dual-Worker Fleet Telemetry Roster Table -->
        <button id="navBtnRoster" class="nav-btn" onclick="openModal('modal-fleet-roster')" title="Subterranean Worker Fleet Roster & Diagnostic Table">
          <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="3" width="18" height="18" rx="2"></rect>
            <path d="M3 9h18"></path>
            <path d="M9 21V9"></path>
          </svg>
        </button>

        <!-- 3. Subterranean GIS Map Modal Trigger -->
        <button id="navBtnMap" class="nav-btn" onclick="openModal('modal-gis-map')" title="Subterranean Spatial Mine Navigation (OpenStreetMap GIS)">
          <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">
            <polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"></polygon>
            <line x1="8" y1="2" x2="8" y2="18"></line>
            <line x1="16" y1="6" x2="16" y2="22"></line>
          </svg>
        </button>

        <!-- 4. SAR Chronological Audit Trail Modal -->
        <button id="navBtnAudit" class="nav-btn" onclick="openModal('modal-audit-trail')" title="Chronological Triage Audit Log">
          <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <line x1="16" y1="13" x2="8" y2="13"></line>
            <line x1="16" y1="17" x2="8" y2="17"></line>
            <polyline points="10 9 9 9 8 9"></polyline>
          </svg>
        </button>

        <!-- 5. Wearable Hardware Spec & Prototype Viewer -->
        <button id="navBtnHardware" class="nav-btn" onclick="openModal('modal-hardware-spec')" title="Hardware REV 2.0 Specifications">
          <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">
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
    <main class="px-8 py-7 flex flex-col justify-between h-full overflow-y-auto">

      <!-- Center Header -->
      <header class="flex flex-wrap items-center justify-between gap-4">
        <div>
          <div class="flex items-center gap-3">
            <h1 class="text-[23px] font-extrabold text-[#2D2B2A] tracking-tight leading-tight">
              RescueTag Subterranean Command
            </h1>
            <span class="px-2.5 py-0.5 rounded-[6px] bg-[#EAE4DC] text-[#4A4744] text-[10.5px] font-mono font-bold tracking-wider uppercase">
              REV 2.0 // LORA P2P
            </span>
          </div>
          <p class="text-[12px] font-semibold text-[#7B7874] mt-1 flex items-center gap-2">
            <span id="liveClock" class="font-mono text-[#4A4744]">12:45:00 UTC</span>
            <span>&bull;</span>
            <span id="headerSectorStatus">Sektor 7 Tambang Bawah Tanah &bull; 1-Hop Mesh Relaying</span>
          </p>
        </div>

        <!-- Worker Roster Switcher Tabs -->
        <div class="flex items-center gap-2 bg-[#EFE9E0] p-1.5 rounded-2xl border border-[#E5DFD4]">
          <button id="tabWorker02" onclick="selectWorker(2)" class="worker-pill-btn active" title="Switch to Worker #02 (Agus Salim)">
            <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
            <span>Pekerja #02 (Agus)</span>
          </button>
          <button id="tabWorker01" onclick="selectWorker(1)" class="worker-pill-btn" title="Switch to Worker #01 (Bambang Relay)">
            <span class="w-2 h-2 rounded-full bg-amber-500"></span>
            <span>Pekerja #01 (Bambang Relay)</span>
          </button>
        </div>

        <!-- Top Right Actions -->
        <div class="flex items-center gap-2.5">
          <!-- Search / Quick Sector Command Palette -->
          <button class="icon-btn" onclick="openModal('modal-search')" title="Quick Command & Shaft Search">
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="11" cy="11" r="8"></circle>
              <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>
          </button>
          
          <!-- Alert Notifications Counter -->
          <button class="icon-btn relative" onclick="openModal('modal-audit-trail')" title="View SAR Incident Logs">
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
              <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
            </svg>
            <span id="alertCountBadge" class="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-[#EF4444] text-white text-[9px] font-bold flex items-center justify-center font-mono">
              0
            </span>
          </button>
        </div>
      </header>

      <!-- ROW 1: 3 Live Telemetry Cards (Clickable for Diagnostics & 3D Ring Highlight) -->
      <section class="grid grid-cols-1 md:grid-cols-3 gap-4 my-2">
        
        <!-- Metric Card 1: Heart Rate (MAX30102 PPG) -->
        <div class="metric-card p-4 pb-3 flex flex-col justify-between h-[208px] relative overflow-hidden" 
             onclick="openMetricDetail('hr')" 
             onmouseenter="highlightSensorRing('chestRing', true)" 
             onmouseleave="highlightSensorRing('chestRing', false)"
             title="Click to view Heart Rate PPG diagnostics">
          <div>
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2.5">
                <div class="w-[42px] h-[42px] rounded-[12px] bg-[#FBF0F1] flex items-center justify-center shrink-0">
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
                    <path d="M12 20.5C12 20.5 3.5 15.2 3.5 8.9C3.5 6.1 5.7 4 8.3 4C9.9 4 11.3 4.8 12 6.1C12.7 4.8 14.1 4 15.7 4C18.3 4 20.5 6.1 20.5 8.9C20.5 15.2 12 20.5 12 20.5Z" fill="#DE6D72"/>
                    <path d="M5.5 11.5H9L10.4 9L12.5 14L14.1 10.5L15.2 11.5H18.5" stroke="#FBF0F1" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </div>
                <div>
                  <span class="text-[13px] font-bold text-[#2D2B2A] block leading-tight">Heart Rate</span>
                  <span class="text-[10px] font-mono text-[#86837F]">MAX30102 PPG</span>
                </div>
              </div>
              <span id="badge-hr" class="px-2 py-0.5 rounded-[5px] bg-[#FBE7E8] text-[#7A2A2E] text-[10px] font-bold">
                Normal
              </span>
            </div>

            <div class="mt-3 flex items-baseline gap-1.5">
              <span id="val-hr" class="text-[28px] font-bold text-[#2D2B2A] leading-none font-mono">75</span>
              <span class="text-[12px] font-semibold text-[#86837F]">BPM</span>
            </div>
          </div>

          <!-- Pulsing Red/Pink Sparkline -->
          <div class="w-full h-[52px] mt-1">
            <svg viewBox="0 0 160 52" class="w-full h-full overflow-visible" preserveAspectRatio="none">
              <defs>
                <linearGradient id="hrGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stop-color="#DE6D72" stop-opacity="0.35"/>
                  <stop offset="95%" stop-color="#FBE7E8" stop-opacity="0.0"/>
                </linearGradient>
              </defs>
              <path id="hrSparklineFill" d="M 0 34 C 14 25, 28 24, 42 34 C 56 44, 70 42, 84 26 C 96 14, 110 8, 124 16 C 136 24, 148 30, 160 22 L 160 52 L 0 52 Z" fill="url(#hrGrad)"/>
              <path id="hrSparklinePath" d="M 0 34 C 14 25, 28 24, 42 34 C 56 44, 70 42, 84 26 C 96 14, 110 8, 124 16 C 136 24, 148 30, 160 22" fill="none" stroke="#DE6D72" stroke-width="1.8" stroke-linecap="round"/>
            </svg>
          </div>
        </div>

        <!-- Metric Card 2: SpO2 Blood Oxygen (MAX30102 Red/IR) -->
        <div class="metric-card p-4 pb-3 flex flex-col justify-between h-[208px] relative overflow-hidden" 
             onclick="openMetricDetail('spo2')" 
             onmouseenter="highlightSensorRing('chestRing', true)" 
             onmouseleave="highlightSensorRing('chestRing', false)"
             title="Click to view SpO2 oxygenation curve">
          <div>
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2.5">
                <div class="w-[42px] h-[42px] rounded-[12px] bg-[#D5F2F8] flex items-center justify-center shrink-0">
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
                    <path d="M12 3.2C12 3.2 6 10.2 6 14.6C6 18.0 8.69 20.6 12 20.6C15.31 20.6 18 18.0 18 14.6C18 10.2 12 3.2 12 3.2Z" fill="#478F9E"/>
                    <path d="M12 12V17.2M9.4 14.6H14.6" stroke="#D5F2F8" stroke-width="1.6" stroke-linecap="round"/>
                  </svg>
                </div>
                <div>
                  <span class="text-[13px] font-bold text-[#2D2B2A] block leading-tight">Blood O2 (SpO2)</span>
                  <span class="text-[10px] font-mono text-[#86837F]">Red/IR Ratio</span>
                </div>
              </div>
              <span id="badge-spo2" class="px-2 py-0.5 rounded-[5px] bg-[#D0F1F8] text-[#1E4D57] text-[10px] font-bold">
                Optimal
              </span>
            </div>

            <div class="mt-3 flex items-baseline gap-1.5">
              <span id="val-spo2" class="text-[28px] font-bold text-[#2D2B2A] leading-none font-mono">98</span>
              <span class="text-[12px] font-semibold text-[#86837F]">% Saturation</span>
            </div>
          </div>

          <!-- Pulsing Teal/Cyan Sparkline -->
          <div class="w-full h-[52px] mt-1">
            <svg viewBox="0 0 160 52" class="w-full h-full overflow-visible" preserveAspectRatio="none">
              <defs>
                <linearGradient id="spo2Grad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stop-color="#60C3D8" stop-opacity="0.35"/>
                  <stop offset="95%" stop-color="#D0F1F8" stop-opacity="0.0"/>
                </linearGradient>
              </defs>
              <path id="spo2SparklineFill" d="M 0 32 C 12 38, 26 39, 38 29 C 50 18, 60 14, 76 17 C 90 19, 102 22, 114 14 C 128 5, 144 4, 160 28 L 160 52 L 0 52 Z" fill="url(#spo2Grad)"/>
              <path id="spo2SparklinePath" d="M 0 32 C 12 38, 26 39, 38 29 C 50 18, 60 14, 76 17 C 90 19, 102 22, 114 14 C 128 5, 144 4, 160 28" fill="none" stroke="#478F9E" stroke-width="1.8" stroke-linecap="round"/>
            </svg>
          </div>
        </div>

        <!-- Metric Card 3: IR Skin Temperature (MLX90614) -->
        <div class="metric-card p-4 pb-3 flex flex-col justify-between h-[208px] relative overflow-hidden" 
             onclick="openMetricDetail('temp')" 
             onmouseenter="highlightSensorRing('wristRing', true)" 
             onmouseleave="highlightSensorRing('wristRing', false)"
             title="Click to view MLX90614 Thermal Telemetry">
          <div>
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2.5">
                <div class="w-[42px] h-[42px] rounded-[12px] bg-[#F8DFC2] flex items-center justify-center shrink-0">
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#E09B48" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"></path>
                  </svg>
                </div>
                <div>
                  <span class="text-[13px] font-bold text-[#2D2B2A] block leading-tight">Skin IR Temp</span>
                  <span class="text-[10px] font-mono text-[#86837F]">MLX90614 Contactless</span>
                </div>
              </div>
              <span id="badge-temp" class="px-2 py-0.5 rounded-[5px] bg-[#F8DFC2] text-[#5C3912] text-[10px] font-bold">
                Normotermia
              </span>
            </div>

            <div class="mt-3 flex items-baseline gap-1.5">
              <span id="val-temp" class="text-[28px] font-bold text-[#2D2B2A] leading-none font-mono">36.5</span>
              <span class="text-[12px] font-semibold text-[#86837F]">&deg;C</span>
            </div>
          </div>

          <!-- Pulsing Amber Sparkline -->
          <div class="w-full h-[52px] mt-1">
            <svg viewBox="0 0 160 52" class="w-full h-full overflow-visible" preserveAspectRatio="none">
              <defs>
                <linearGradient id="tempGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stop-color="#E79B3F" stop-opacity="0.38"/>
                  <stop offset="95%" stop-color="#F8DFC2" stop-opacity="0.0"/>
                </linearGradient>
              </defs>
              <path id="tempSparklineFill" d="M 0 38 C 16 28, 30 22, 46 28 C 60 33, 74 34, 88 22 C 100 11, 108 6, 120 12 C 132 18, 140 31, 160 24 L 160 52 L 0 52 Z" fill="url(#tempGrad)"/>
              <path id="tempSparklinePath" d="M 0 38 C 16 28, 30 22, 46 28 C 60 33, 74 34, 88 22 C 100 11, 108 6, 120 12 C 132 18, 140 31, 160 24" fill="none" stroke="#E59A43" stroke-width="1.8" stroke-linecap="round"/>
            </svg>
          </div>
        </div>

      </section>

      <!-- ROW 2: Kinematics & TinyML Activity Stream (Height 346px) -->
      <section class="metric-card px-6 py-5 flex flex-col justify-between h-[346px] my-1">
        <!-- Card Header -->
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-[16px] font-bold text-[#2D2B2A]">Kinematics & TinyML Activity Stream</h2>
            <p class="text-[11px] text-[#787571] mt-0.5">
              Live Edge BMI160 6-DOF IMU Telemetry &bull; Click any bar to inspect interval
            </p>
          </div>
          
          <div class="flex items-center gap-3">
            <span id="liveAccelPill" class="px-2.5 py-1 rounded-[8px] bg-[#EFE9E0] text-[#3E3C39] font-mono text-[11px] font-bold cursor-pointer" onclick="testSimSOS()" title="Click to test Shock alert">
              1.02g &bull; Normal
            </span>
            <button id="shiftSelectorBtn" onclick="cycleShift()" class="flex items-center gap-2 px-3 py-1.5 rounded-[10px] border border-[#EAE6E1] text-[11.5px] font-semibold text-[#4A4744] hover:bg-[#FAF6F1] transition">
              <span id="shiftLabel">Shift Pagi // Sektor 7</span>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="6 9 12 15 18 9"></polyline>
              </svg>
            </button>
          </div>
        </div>

        <!-- 18 Multi-Segment Pill Bars Container -->
        <div class="relative flex-1 mt-3 mb-1 flex">
          <!-- Y-Axis Labels -->
          <div class="flex flex-col justify-between text-[9px] font-mono font-semibold text-[#8E8B86] pr-3 pb-6 pt-2 select-none">
            <span>4.0g (Shock)</span>
            <span>2.5g (Active)</span>
            <span>1.5g (Work)</span>
            <span>1.0g (Rest)</span>
          </div>

          <!-- Horizontal Grid Lines + Bars -->
          <div class="flex-1 relative flex flex-col justify-between pb-6 pt-3">
            <div class="w-full border-b border-[#F4F1ED]"></div>
            <div class="w-full border-b border-[#F4F1ED]"></div>
            <div class="w-full border-b border-[#F4F1ED]"></div>
            <div class="w-full border-b border-[#F4F1ED]"></div>

            <!-- The 18 Bars -->
            <div id="kinematicsBarsContainer" class="absolute inset-0 bottom-5 flex items-end justify-between px-2">
              <!-- Dynamically populated by JS -->
            </div>
          </div>
        </div>

        <!-- Legend and Trigger Controls -->
        <div class="flex flex-wrap items-center justify-between pt-1 border-t border-[#F6F2EC]">
          <div class="flex items-center gap-6">
            <button onclick="setFilterActivity('shock')" class="flex items-center gap-2 hover:opacity-80 transition focus:outline-none">
              <span class="w-2.5 h-2.5 rounded-full bg-[#DA7468]"></span>
              <span class="text-[10.5px] font-semibold text-[#6E6B67]">G-Force Shock (>3.0g)</span>
            </button>
            <button onclick="setFilterActivity('work')" class="flex items-center gap-2 hover:opacity-80 transition focus:outline-none">
              <span class="w-2.5 h-2.5 rounded-full bg-[#438D9B]"></span>
              <span class="text-[10.5px] font-semibold text-[#6E6B67]">Kerja Tambang Aktif (1.2-2.5g)</span>
            </button>
            <button onclick="setFilterActivity('rest')" class="flex items-center gap-2 hover:opacity-80 transition focus:outline-none">
              <span class="w-2.5 h-2.5 rounded-full bg-[#CD8A39]"></span>
              <span class="text-[10.5px] font-semibold text-[#6E6B67]">Diam / Baseline (1.0g)</span>
            </button>
          </div>

          <div class="flex items-center gap-2">
            <button onclick="testSimSOS()" class="px-2.5 py-1 rounded-[7px] bg-red-100 text-red-800 text-[10.5px] font-bold hover:bg-red-200 transition font-mono" title="Simulate 4.85g Free-Fall & Tachycardia">
              Simulate SOS (Shock)
            </button>
            <button onclick="testSimNormal()" class="px-2.5 py-1 rounded-[7px] bg-emerald-100 text-emerald-800 text-[10.5px] font-bold hover:bg-emerald-200 transition font-mono" title="Simulate 1.02g Stable Vitals">
              Simulate Normal
            </button>
          </div>
        </div>
      </section>

      <!-- ROW 3: LoRa 1-Hop Mesh Transmission Link Bar (Height 66px) -->
      <section class="metric-card px-6 py-3.5 flex flex-wrap items-center justify-between h-auto md:h-[66px] gap-3">
        <div class="flex items-center gap-3">
          <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)] animate-ping"></span>
          <div>
            <h3 class="text-[14px] font-bold text-[#2D2B2A] leading-tight">LoRa 1-Hop Mesh Transmission Link</h3>
            <p class="text-[10.5px] text-[#7A7773] font-mono">SX1278 433.05 MHz Sub-GHz &bull; CRC-16 Validated</p>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <button onclick="pulseHopSimulation()" class="px-3 py-1 rounded-[8px] bg-[#CEF0F7] text-[#1E454E] text-[10.5px] font-bold font-mono tracking-tight hover:bg-[#BDE7F0] transition" title="Click to test 18ms Hop Relay pulse">
            18ms Estafet Latency
          </button>
          <span class="px-3 py-1 rounded-[8px] bg-[#F3ECE4] text-[#4F4A44] text-[10.5px] font-bold font-mono">
            RSSI -68 dBm // SNR +8.5 dB
          </span>
        </div>

        <div class="flex items-center gap-2">
          <button onclick="openModal('modal-fleet-roster')" class="flex items-center gap-1.5 px-3 py-1.5 rounded-[10px] bg-[#EDE7DF] text-[#3E3C39] text-[11px] font-semibold hover:bg-[#E2DAD0] transition">
            <span>Fleet Roster Table</span>
          </button>
          <button onclick="openModal('modal-gis-map')" class="flex items-center gap-2 px-3.5 py-1.5 rounded-[10px] bg-[#2C2A2A] text-white text-[11px] font-semibold hover:bg-[#1E1D1D] transition shadow-sm">
            <span>Open GIS Map</span>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="9 18 15 12 9 6"></polyline>
            </svg>
          </button>
        </div>
      </section>

    </main>

    <!-- ================= 3. RIGHT DARK TACTICAL PANEL (414px, #2D2B2B) ================= -->
    <aside class="right-tactical-panel bg-[#2D2B2B] h-full rounded-l-[34px] px-7 py-7 flex flex-col justify-between text-white relative overflow-hidden select-none border-l border-[#3D3A3A]">

      <!-- TOP HALF: START Triage Risk Simulator -->
      <div>
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-[16px] font-bold text-[#F4F1EA] tracking-tight">START Triage Risk Simulator</h2>
            <p class="text-[10.5px] text-[#A6A29C] font-mono">Simple Triage and Rapid Treatment</p>
          </div>
          <button id="simModeToggleBtn" onclick="toggleSimMode()" class="flex items-center gap-1.5 px-2.5 py-1 rounded-[8px] border border-[#524E4E] text-[10.5px] font-semibold text-[#D1CECA] hover:border-[#8E8B86] transition font-mono">
            <span id="simModeLabel">Mode: Live MQTT</span>
          </button>
        </div>

        <!-- Sliders & Triage Result Grid -->
        <div class="grid grid-cols-[148px_1fr] gap-3 mt-4">
          
          <!-- Left Stack: HR & SpO2 Draggable Ruler Cards -->
          <div class="flex flex-col gap-2.5">
            
            <!-- HR Ruler Card (Peach #F6D6B8) -->
            <div class="bg-[#F6D6B8] rounded-[14px] px-3 py-2 h-[68px] flex flex-col justify-between relative text-[#2C2A29]" title="Drag left/right to adjust Heart Rate">
              <input type="range" min="40" max="180" value="75" id="sliderHR" class="ruler-slider" oninput="onSimulatorInput()" />
              <!-- Ruler Ticks -->
              <div class="flex items-start justify-end gap-[5px] pr-1 pt-0.5 pointer-events-none">
                <span class="w-[1.2px] h-2 bg-[#7A6855]"></span>
                <span class="w-[1.2px] h-2 bg-[#7A6855]"></span>
                <span class="w-[1.2px] h-2 bg-[#7A6855]"></span>
                <span class="w-[1.6px] h-3.5 bg-[#D4554B]"></span>
                <span class="w-[1.2px] h-2 bg-[#2C2A29]"></span>
                <span class="w-[1.2px] h-2 bg-[#2C2A29]"></span>
                <span class="w-[1.2px] h-2 bg-[#2C2A29]"></span>
              </div>
              <div class="flex items-center justify-between text-[11px] font-semibold pb-0.5">
                <span class="text-[#4A4138]">Sim Heart Rate</span>
                <span id="simHRText" class="font-bold text-[#2C2A29] font-mono">75 BPM</span>
              </div>
            </div>

            <!-- SpO2 Ruler Card (Light Cyan #C8EAEF) -->
            <div class="bg-[#C8EAEF] rounded-[14px] px-3 py-2 h-[68px] flex flex-col justify-between relative text-[#2C2A29]" title="Drag left/right to adjust SpO2">
              <input type="range" min="70" max="100" value="98" id="sliderSpO2" class="ruler-slider" oninput="onSimulatorInput()" />
              <!-- Ruler Ticks -->
              <div class="flex items-start justify-end gap-[5px] pr-1 pt-0.5 pointer-events-none">
                <span class="w-[1.2px] h-2 bg-[#6A8185]"></span>
                <span class="w-[1.2px] h-2 bg-[#6A8185]"></span>
                <span class="w-[1.2px] h-2 bg-[#6A8185]"></span>
                <span class="w-[1.6px] h-3.5 bg-[#D4554B]"></span>
                <span class="w-[1.2px] h-2 bg-[#2C2A29]"></span>
                <span class="w-[1.2px] h-2 bg-[#2C2A29]"></span>
                <span class="w-[1.2px] h-2 bg-[#2C2A29]"></span>
              </div>
              <div class="flex items-center justify-between text-[11px] font-semibold pb-0.5">
                <span class="text-[#3C4B4E]">Sim SpO2 Sat</span>
                <span id="simSpO2Text" class="font-bold text-[#2C2A29] font-mono">98 %</span>
              </div>
            </div>

          </div>

          <!-- Right Result Card: START Triage Priority (#434141) -->
          <div class="bg-[#434141] rounded-[16px] px-3.5 py-3 flex flex-col justify-between h-[148px] border border-[#524E4E]">
            <div class="text-[11px] font-medium text-[#D9D6D2] flex items-center justify-between">
              <span>START Assessment</span>
              <span id="simModeIndicator" class="text-[9px] font-mono text-[#A6A29C]">LIVE HARDWARE</span>
            </div>

            <div>
              <div id="triagePriorityText" class="text-[20px] font-extrabold text-[#34D399] tracking-tight font-mono leading-tight">
                HIJAU
              </div>
              <div id="triageSubtitleText" class="text-[10px] text-[#CCC8C2] mt-0.5 font-medium">
                Minor / Korban Stabil
              </div>
            </div>

            <!-- Gradient Priority Bar with Dynamic Indicator Dot (Clickable) -->
            <div onclick="onTriageBarClick(event)" title="Click anywhere on the bar to test triage stages">
              <div class="triage-gradient-bar mt-1">
                <div id="triageDot" class="w-3.5 h-3.5 rounded-full bg-white shadow-md border-[2.5px] border-[#2C2A2A] absolute -top-[3px] transition-all duration-300" style="left: 15%;"></div>
              </div>
              <div class="flex justify-between text-[8px] font-mono text-[#A39E97] mt-1.5 font-semibold">
                <span onclick="setTriageDirect('HIJAU')" class="hover:text-emerald-400 cursor-pointer">HIJAU</span>
                <span onclick="setTriageDirect('KUNING')" class="hover:text-amber-400 cursor-pointer">KUNING</span>
                <span onclick="setTriageDirect('MERAH')" class="hover:text-red-400 cursor-pointer">MERAH</span>
                <span onclick="setTriageDirect('HITAM')" class="hover:text-gray-200 cursor-pointer">HITAM</span>
              </div>
            </div>

            <div class="flex items-center justify-between pt-1">
              <span id="triageBadgePill" class="px-2 py-0.5 rounded-[6px] bg-[#D5F4EA] text-[#1D4A3D] text-[9.5px] font-bold">
                Aman &bull; Tidak Perlu Evakuasi Cepat
              </span>
            </div>
          </div>

        </div>
      </div>

      <!-- BOTTOM HALF: Wearable Sensor Ergonomics Node Map -->
      <div class="pt-4 border-t border-[#3D3A3A]">
        <div class="flex items-center justify-between mb-3">
          <div>
            <h3 class="text-[15px] font-bold text-[#F4F1EA] tracking-tight">Wearable Sensor Ergonomics</h3>
            <p class="text-[10px] text-[#A6A29C] font-mono">Hardware REV 2.0 Anatomical Inset</p>
          </div>
          <button onclick="openModal('modal-hardware-spec')" class="text-[10px] font-mono text-[#D4AF37] px-2 py-0.5 rounded bg-[#3A3322] border border-[#5A4D2E] hover:bg-[#4D442C] transition">
            NODE-01 FIXED
          </button>
        </div>

        <div class="grid grid-cols-[148px_1fr] gap-3 items-center">
          
          <!-- Left Stack: 3 Interactive Hardware Sensor Cards -->
          <div class="flex flex-col gap-2">
            
            <!-- Card 1: Wrist Smartwatch IP68 (Triggers Wrist Ring) -->
            <div class="measure-card bg-[#383535] rounded-[13px] px-3 py-2 flex flex-col justify-between border border-[#484444]" 
                 onmouseenter="highlightSensorRing('wristRing', true)" 
                 onmouseleave="highlightSensorRing('wristRing', false)"
                 onclick="openModal('modal-hardware-spec')"
                 title="Click to inspect OLED Watch Enclosure">
              <div class="text-[11px] font-bold text-[#F4F1EA] flex items-center justify-between">
                <span>Smartwatch IP68</span>
                <span class="text-[9px] font-mono text-[#E59A43]">REV 2.0</span>
              </div>
              <div class="flex items-baseline justify-between mt-1">
                <span class="text-[9.5px] text-[#A6A29C]">STM32 + LoRa 433</span>
                <span class="text-[10.5px] font-mono font-bold text-white">Left Wrist</span>
              </div>
            </div>

            <!-- Card 2: PPG Arterial Pulse (Triggers Chest Ring) -->
            <div class="measure-card bg-[#383535] rounded-[13px] px-3 py-2 flex flex-col justify-between border border-[#484444]" 
                 onmouseenter="highlightSensorRing('chestRing', true)" 
                 onmouseleave="highlightSensorRing('chestRing', false)"
                 onclick="openMetricDetail('hr')"
                 title="Click to inspect PPG Pulse Optical Sensor">
              <div class="text-[11px] font-bold text-[#F4F1EA] flex items-center justify-between">
                <span>MAX30102 PPG</span>
                <span class="text-[9px] font-mono text-[#DE6D72]">Optic</span>
              </div>
              <div class="flex items-baseline justify-between mt-1">
                <span class="text-[9.5px] text-[#A6A29C]">HR & SpO2 Sensor</span>
                <span class="text-[10.5px] font-mono font-bold text-white">Arterial Pulse</span>
              </div>
            </div>

            <!-- Card 3: Core IMU Kinematics (Triggers Waist Ring) -->
            <div class="measure-card bg-[#383535] rounded-[13px] px-3 py-2 flex flex-col justify-between border border-[#484444]" 
                 onmouseenter="highlightSensorRing('waistRing', true)" 
                 onmouseleave="highlightSensorRing('waistRing', false)"
                 onclick="openModal('modal-tinyml-detail')"
                 title="Click to view TinyML Fall Detection Network">
              <div class="text-[11px] font-bold text-[#F4F1EA] flex items-center justify-between">
                <span>BMI160 6-DOF IMU</span>
                <span class="text-[9px] font-mono text-[#478F9E]">TinyML</span>
              </div>
              <div class="flex items-baseline justify-between mt-1">
                <span class="text-[9.5px] text-[#A6A29C]">Fall & Impact ML</span>
                <span class="text-[10.5px] font-mono font-bold text-white">Core Vector</span>
              </div>
            </div>

          </div>

          <!-- Right Column: High-Precision Anatomical Human Miner SVG with 3D Glowing Rings -->
          <div class="flex items-center justify-center relative">
            <svg viewBox="0 0 210 440" class="w-[180px] h-[360px] overflow-visible select-none" fill="none" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <filter id="sensorGlow" x="-30%" y="-40%" width="160%" height="180%">
                  <feGaussianBlur stdDeviation="3.0" result="blur" />
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

              <!-- BACK HALF OF 3D SENSOR RINGS -->
              <path d="M 38 112 A 67 11 0 0 1 172 112" stroke="#E59A43" stroke-width="1.7" stroke-opacity="0.6" fill="none" />
              <path d="M 55 160 A 50 9 0 0 1 155 160" stroke="#E59A43" stroke-width="1.7" stroke-opacity="0.6" fill="none" />
              <path d="M 30 226 A 24 6 0 0 1 66 226" stroke="#E59A43" stroke-width="1.7" stroke-opacity="0.6" fill="none" />

              <!-- FULL HUMAN ANATOMY -->
              <!-- Neck & Shoulders -->
              <path d="M 88 52 L 86 68 L 62 76 L 148 76 L 124 68 L 122 52 Z" fill="#F7C9A6"/>
              <path d="M 88 55 Q 105 70 122 55 L 123 68 Q 105 76 87 68 Z" fill="url(#neckShadow)"/>

              <!-- Left Arm with Watch Contour -->
              <path d="M 64 76 C 48 80, 42 92, 43 114 C 43 125, 38 142, 41 156 C 36 172, 36 196, 39 216 C 37 224, 37 238, 41 246 C 44 252, 48 254, 49 250 C 51 253, 54 252, 54 248 C 56 249, 58 247, 57 244 C 54 239, 53 234, 53 228 C 52 222, 49 217, 49 212 C 53 196, 56 175, 58 160 C 64 148, 69 135, 70 120 Z" fill="#F7C9A6"/>

              <!-- Right Arm -->
              <path d="M 146 76 C 162 80, 168 92, 167 114 C 167 125, 172 142, 169 156 C 174 172, 174 196, 171 216 C 173 224, 173 238, 169 246 C 166 252, 162 254, 161 250 C 159 253, 156 252, 156 248 C 154 249, 152 247, 153 244 C 156 239, 157 234, 157 228 C 158 222, 161 217, 161 212 C 157 196, 154 175, 152 160 C 146 148, 141 135, 140 120 Z" fill="#F7C9A6"/>

              <!-- Legs -->
              <path d="M 65 242 C 64 268, 66 294, 70 312 C 66 326, 65 344, 69 362 C 71 375, 73 392, 74 404 L 91 404 C 91 390, 95 372, 99 354 C 102 338, 100 322, 96 310 C 101 290, 103 266, 103 244 Z" fill="#F7C9A6"/>
              <path d="M 145 242 C 146 268, 144 294, 140 312 C 144 326, 145 344, 141 362 C 139 375, 137 392, 136 404 L 119 404 C 119 390, 115 372, 111 354 C 108 338, 110 322, 114 310 C 109 290, 107 266, 107 244 Z" fill="#F7C9A6"/>

              <!-- White Tactile Vest / Tank Top -->
              <path d="M 74 72 L 85 70 C 88 86, 94 94, 105 94 C 116 94, 122 86, 125 70 L 136 72 C 134 92, 136 108, 143 118 C 141 136, 136 154, 136 170 C 136 178, 137 183, 136 187 C 116 191, 94 191, 74 187 C 73 183, 74 178, 74 170 C 74 154, 69 136, 67 118 C 74 108, 76 92, 74 72 Z" fill="url(#tankGrad)"/>

              <!-- Tactical Miner Pants -->
              <path d="M 73 185 C 94 189, 116 189, 137 185 C 143 204, 148 226, 148 244 C 146 251, 134 254, 107 253 L 106 245 L 104 245 L 103 253 C 76 254, 64 251, 62 244 C 62 226, 67 204, 73 185 Z" fill="#1C1A19"/>

              <!-- Head & Safety Helmet / Hair -->
              <path d="M 86 38 C 83 37, 82 42, 84 46 C 85 48, 87 49, 88 48" fill="#F7C9A6" stroke="#DC8751" stroke-width="0.9"/>
              <path d="M 124 38 C 127 37, 128 42, 126 46 C 125 48, 123 49, 122 48" fill="#F7C9A6" stroke="#DC8751" stroke-width="0.9"/>
              <path d="M 86 28 C 86 16, 94 10, 105 10 C 116 10, 124 16, 124 28 C 124 44, 117 59, 105 59 C 93 59, 86 44, 86 28 Z" fill="#F7C9A6"/>
              <path d="M 86 34 C 84 25, 85 14, 92 10 C 98 6, 112 6, 119 11 C 125 15, 126 25, 124 34 C 123 28, 121 22, 117 20 C 111 18, 98 20, 92 18 C 88 21, 87 28, 86 34 Z" fill="#141313"/>

              <!-- Boots -->
              <path d="M 73 400 C 70 406, 65 418, 65 426 C 65 433, 73 436, 82 436 C 91 436, 95 432, 94 424 C 93 414, 93 405, 91 400 Z" fill="#171615"/>
              <path d="M 119 400 C 117 405, 117 414, 116 424 C 115 432, 119 436, 128 436 C 137 436, 145 433, 145 426 C 145 418, 140 406, 137 400 Z" fill="#171615"/>

              <!-- FRONT HALF OF 3D GLOWING SENSOR RINGS (Clickable) -->
              <!-- 1. Chest Ring: MAX30102 PPG Arterial Pulse -->
              <g id="chestRing" class="ring-glow" onclick="openMetricDetail('hr')">
                <path d="M 38 112 A 67 11 0 0 0 172 112" stroke="#FF6B63" stroke-width="3.2" stroke-opacity="0.45" filter="url(#sensorGlow)" fill="none" />
                <path d="M 38 112 A 67 11 0 0 0 172 112" stroke="#F0645A" stroke-width="1.8" fill="none" />
              </g>

              <!-- 2. Waist Ring: BMI160 6-DOF IMU Kinematics -->
              <g id="waistRing" class="ring-glow" onclick="openModal('modal-tinyml-detail')">
                <path d="M 55 160 A 50 9 0 0 0 155 160" stroke="#478F9E" stroke-width="3.2" stroke-opacity="0.45" filter="url(#sensorGlow)" fill="none" />
                <path d="M 55 160 A 50 9 0 0 0 155 160" stroke="#60C3D8" stroke-width="1.8" fill="none" />
              </g>

              <!-- 3. Wrist Ring: Smartwatch IP68 REV 2.0 (Left Wrist) -->
              <g id="wristRing" class="ring-glow" onclick="openModal('modal-hardware-spec')">
                <path d="M 30 226 A 24 6 0 0 0 66 226" stroke="#E59A43" stroke-width="3.2" stroke-opacity="0.5" filter="url(#sensorGlow)" fill="none" />
                <path d="M 30 226 A 24 6 0 0 0 66 226" stroke="#F5A84D" stroke-width="2.0" fill="none" />
                <rect x="42" y="220" width="12" height="12" rx="3" fill="#2C2A29" stroke="#E59A43" stroke-width="1.2" />
              </g>

            </svg>
          </div>

        </div>

      </div>

    </aside>

  </div>

  <!-- ================= MODAL 1: SUBTERRANEAN FLEET ROSTER & DIAGNOSTICS ================= -->
  <div id="modal-fleet-roster" class="modal-overlay">
    <div class="bg-[#1C1A1A] text-white w-full max-w-5xl rounded-[28px] border border-[#383535] shadow-2xl p-6 relative flex flex-col max-h-[90vh] overflow-hidden">
      <div class="flex items-center justify-between pb-4 border-b border-[#383535]">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-orange-500/20 text-orange-400 flex items-center justify-center">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="3" width="18" height="18" rx="2"></rect>
              <path d="M3 9h18"></path>
              <path d="M9 21V9"></path>
            </svg>
          </div>
          <div>
            <h3 class="text-base font-bold font-mono">Subterranean Worker Fleet Roster & LoRa Diagnostics</h3>
            <p class="text-xs text-gray-400">Real-Time Telemetry & 1-Hop Forwarding State for Both Personnel</p>
          </div>
        </div>
        <button onclick="closeModal('modal-fleet-roster')" class="w-8 h-8 rounded-lg bg-[#333030] hover:bg-[#444040] flex items-center justify-center text-gray-300">
          &times;
        </button>
      </div>

      <!-- Fleet Table -->
      <div class="overflow-x-auto mt-4 flex-1">
        <table class="w-full tactical-table border-collapse">
          <thead>
            <tr>
              <th>Worker & Tag ID</th>
              <th>Vitals (HR &bull; SpO2 &bull; Temp)</th>
              <th>TinyML Activity State</th>
              <th>Transmission Route</th>
              <th>START Triage Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <!-- Row 1: Worker #02 (Agus Salim) -->
            <tr id="rosterRow02" class="hover:bg-[#252222] transition">
              <td>
                <div class="font-bold text-white text-xs">Pekerja #02 (Agus Salim)</div>
                <div class="text-[10px] text-gray-400 font-mono">Jam Tangan #02 &bull; Sektor 7 (Lorong C-4)</div>
              </td>
              <td>
                <span id="rosterVitals02" class="font-mono text-emerald-400 font-semibold">
                  75 BPM &bull; 98% SpO2 &bull; 36.5&deg;C
                </span>
              </td>
              <td>
                <span id="rosterActivity02" class="px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800 text-[10.5px]">
                  Diam / Istirahat Normal
                </span>
              </td>
              <td>
                <span class="px-2 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800 text-[10.5px] font-mono">
                  1-Hop Relay via Jam #01
                </span>
              </td>
              <td>
                <span id="rosterTriage02" class="px-2.5 py-1 rounded bg-emerald-950/80 text-emerald-300 border border-emerald-600 font-bold text-[10px]">
                  HIJAU - Minor (Aman)
                </span>
              </td>
              <td>
                <div class="flex items-center gap-2">
                  <button onclick="focusFromRoster(2)" class="px-2.5 py-1 rounded bg-[#333030] hover:bg-[#444040] text-[11px] font-mono transition">
                    Focus Map
                  </button>
                  <button onclick="runDiagWatch(2)" class="px-2.5 py-1 rounded bg-orange-950 hover:bg-orange-900 text-orange-300 border border-orange-800 text-[11px] font-mono transition">
                    Run Diag
                  </button>
                </div>
              </td>
            </tr>

            <!-- Row 2: Worker #01 (Bambang Relay Host) -->
            <tr id="rosterRow01" class="hover:bg-[#252222] transition">
              <td>
                <div class="font-bold text-white text-xs">Pekerja #01 (Bambang)</div>
                <div class="text-[10px] text-gray-400 font-mono">Jam Tangan #01 &bull; Junction B-02 (Shaft Poros)</div>
              </td>
              <td>
                <span id="rosterVitals01" class="font-mono text-amber-400 font-semibold">
                  106 BPM &bull; 93% SpO2 &bull; 37.6&deg;C
                </span>
              </td>
              <td>
                <span id="rosterActivity01" class="px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800 text-[10.5px]">
                  Tremor / Kelelahan Ringan
                </span>
              </td>
              <td>
                <span class="px-2 py-0.5 rounded bg-orange-950 text-orange-300 border border-orange-800 text-[10.5px] font-mono">
                  Direct + Relay Host (Hop 1)
                </span>
              </td>
              <td>
                <span id="rosterTriage01" class="px-2.5 py-1 rounded bg-amber-950/80 text-amber-300 border border-amber-600 font-bold text-[10px]">
                  KUNING - Delayed
                </span>
              </td>
              <td>
                <div class="flex items-center gap-2">
                  <button onclick="focusFromRoster(1)" class="px-2.5 py-1 rounded bg-[#333030] hover:bg-[#444040] text-[11px] font-mono transition">
                    Focus Map
                  </button>
                  <button onclick="runDiagWatch(1)" class="px-2.5 py-1 rounded bg-orange-950 hover:bg-orange-900 text-orange-300 border border-orange-800 text-[11px] font-mono transition">
                    Run Diag
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Quick Actions Footer -->
      <div class="flex flex-wrap items-center justify-between pt-4 mt-2 border-t border-[#383535] text-xs font-mono">
        <div class="flex items-center gap-3">
          <button onclick="testSimSOS()" class="px-3 py-1.5 rounded bg-red-950 text-red-200 border border-red-700 hover:bg-red-900 transition">
            Test Incident SOS (Worker #02)
          </button>
          <button onclick="testSimNormal()" class="px-3 py-1.5 rounded bg-emerald-950 text-emerald-200 border border-emerald-700 hover:bg-emerald-900 transition">
            Test Baseline Normal
          </button>
        </div>
        <div class="text-gray-400">
          Radio Frequency: 433.05 MHz Sub-GHz &bull; Hop Latency: 18ms
        </div>
      </div>
    </div>
  </div>

  <!-- ================= MODAL 2: SUBTERRANEAN GIS MINE MAP ================= -->
  <div id="modal-gis-map" class="modal-overlay">
    <div class="bg-[#1C1A1A] text-white w-full max-w-4xl h-[620px] rounded-[28px] border border-[#383535] shadow-2xl flex flex-col overflow-hidden relative">
      <!-- Modal Header -->
      <div class="px-6 py-4 bg-[#262424] border-b border-[#383535] flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-[#E59A43]/20 flex items-center justify-center text-[#E59A43]">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"></polygon>
            </svg>
          </div>
          <div>
            <h3 class="text-sm font-bold font-mono tracking-tight">Subterranean Spatial Mine Navigation // OpenStreetMap GIS</h3>
            <p class="text-[10px] text-[#A6A29C]">Lorong C-4 Sektor 7 &bull; Poros Shaft B-02 &bull; Posko Permukaan Gateway</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <button onclick="toggleMapTileStyle()" class="px-2.5 py-1 rounded-lg bg-[#333030] text-xs font-mono hover:bg-[#444040] transition">
            Toggle Canvas Style
          </button>
          <button onclick="closeModal('modal-gis-map')" class="w-8 h-8 rounded-lg bg-[#333030] hover:bg-[#444040] flex items-center justify-center text-gray-300">
            &times;
          </button>
        </div>
      </div>

      <!-- Map Container -->
      <div id="leafletMapContainer" class="flex-1 w-full h-full bg-[#121212]"></div>

      <!-- Tactical Map Footer Controls -->
      <div class="px-6 py-3 bg-[#262424] border-t border-[#383535] flex items-center justify-between text-xs font-mono">
        <div class="flex items-center gap-3">
          <button onclick="focusMapNode(2)" class="px-3 py-1 rounded bg-emerald-950/80 border border-emerald-500/80 text-emerald-300 hover:bg-emerald-900 transition">
            Focus: Pekerja #02 (Agus)
          </button>
          <button onclick="focusMapNode(1)" class="px-3 py-1 rounded bg-amber-950/80 border border-amber-500/80 text-amber-300 hover:bg-amber-900 transition">
            Focus: Pekerja #01 (Bambang Relay)
          </button>
          <button onclick="pulseHopSimulation()" class="px-3 py-1 rounded bg-[#E59A43]/20 border border-[#E59A43] text-[#E59A43] hover:bg-[#E59A43]/30 transition">
            Simulate 1-Hop Forwarding
          </button>
        </div>
        <span class="text-gray-400">Anchor: Lat -8.2465 Lon 113.6965</span>
      </div>
    </div>
  </div>

  <!-- ================= MODAL 3: HARDWARE REV 2.0 SPECIFICATION ================= -->
  <div id="modal-hardware-spec" class="modal-overlay">
    <div class="bg-[#1C1A1A] text-white w-full max-w-3xl rounded-[28px] border border-[#383535] shadow-2xl p-6 relative">
      <div class="flex items-center justify-between pb-4 border-b border-[#383535]">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-orange-500/20 text-orange-400 flex items-center justify-center">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="6" y="2" width="12" height="20" rx="3"></rect>
              <circle cx="12" cy="12" r="3"></circle>
            </svg>
          </div>
          <div>
            <h3 class="text-base font-bold font-mono">RescueTag Wearable Smartwatch // Hardware REV 2.0</h3>
            <p class="text-xs text-gray-400">Industrial Miner Prototype Specification</p>
          </div>
        </div>
        <button onclick="closeModal('modal-hardware-spec')" class="w-8 h-8 rounded-lg bg-[#333030] hover:bg-[#444040] flex items-center justify-center text-gray-300">
          &times;
        </button>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-5 items-center">
        <!-- Hardware Prototype Image (Self-Contained Base64) -->
        <div class="bg-black/60 rounded-2xl p-3 border border-[#333] flex items-center justify-center">
          <img id="hardwarePhotoImg" src="BASE64_IMAGE_PLACEHOLDER" alt="RescueTag Hardware Prototype" class="w-full max-h-[300px] object-contain drop-shadow-2xl" />
        </div>

        <!-- Technical Specs -->
        <div class="space-y-3 font-mono text-xs">
          <div class="bg-[#262424] p-3 rounded-xl border border-[#383535]">
            <span class="text-gray-400 block text-[10px]">ENCLOSURE & PROTECTION</span>
            <span class="font-bold text-white text-sm">IP68 Rugged ABS Shock-Proof Enclosure</span>
          </div>
          <div class="bg-[#262424] p-3 rounded-xl border border-[#383535]">
            <span class="text-gray-400 block text-[10px]">MICROCONTROLLER & SENSORS</span>
            <span class="font-bold text-white">STM32 Ultra-Low Power + MAX30102 + MLX90614 + BMI160</span>
          </div>
          <div class="bg-[#262424] p-3 rounded-xl border border-[#383535]">
            <span class="text-gray-400 block text-[10px]">TELEMETRY & MESH PROTOCOL</span>
            <span class="font-bold text-[#E59A43]">SX1278 LoRa 433.05 MHz Sub-GHz (1-Hop Peer-to-Peer)</span>
          </div>
          <div class="bg-[#262424] p-3 rounded-xl border border-[#383535]">
            <span class="text-gray-400 block text-[10px]">AUTONOMOUS POWER</span>
            <span class="font-bold text-emerald-400">850mAh LiPo &bull; 18 Jam Operasional Bawah Tanah</span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- ================= MODAL 4: SAR AUDIT TRAIL LOGS ================= -->
  <div id="modal-audit-trail" class="modal-overlay">
    <div class="bg-[#1C1A1A] text-white w-full max-w-2xl h-[520px] rounded-[28px] border border-[#383535] shadow-2xl flex flex-col p-6 relative">
      <div class="flex items-center justify-between pb-4 border-b border-[#383535]">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-red-500/20 text-red-400 flex items-center justify-center">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            </svg>
          </div>
          <div>
            <h3 class="text-base font-bold font-mono">Chronological SAR Triage & Mesh Audit Trail</h3>
            <p class="text-xs text-gray-400">Live Timestamped Disaster Event Records</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <button onclick="dispatchAlphaSquad()" class="px-2.5 py-1 rounded-lg bg-red-900 hover:bg-red-800 text-xs font-mono text-red-200 border border-red-600 transition">
            Dispatch SAR Squad
          </button>
          <button onclick="closeModal('modal-audit-trail')" class="w-8 h-8 rounded-lg bg-[#333030] hover:bg-[#444040] flex items-center justify-center text-gray-300">
            &times;
          </button>
        </div>
      </div>

      <div id="auditLogList" class="flex-1 overflow-y-auto mt-4 space-y-2.5 font-mono text-xs pr-1">
        <!-- Log entries populated here -->
      </div>
    </div>
  </div>

  <!-- ================= MODAL 5: METRIC DETAIL POPOVER ================= -->
  <div id="modal-metric-detail" class="modal-overlay">
    <div class="bg-[#1C1A1A] text-white w-full max-w-md rounded-[24px] border border-[#383535] shadow-2xl p-6 relative">
      <div class="flex items-center justify-between pb-3 border-b border-[#383535]">
        <h3 id="metricDetailTitle" class="text-sm font-bold font-mono">Metric Diagnostics</h3>
        <button onclick="closeModal('modal-metric-detail')" class="w-7 h-7 rounded-lg bg-[#333030] hover:bg-[#444040] flex items-center justify-center text-gray-300">
          &times;
        </button>
      </div>
      <div id="metricDetailBody" class="mt-4 space-y-3 font-mono text-xs">
        <!-- Populated on click -->
      </div>
    </div>
  </div>

  <!-- ================= MODAL 6: TINYML MOTION MODEL DETAIL ================= -->
  <div id="modal-tinyml-detail" class="modal-overlay">
    <div class="bg-[#1C1A1A] text-white w-full max-w-lg rounded-[24px] border border-[#383535] shadow-2xl p-6 relative">
      <div class="flex items-center justify-between pb-3 border-b border-[#383535]">
        <div class="flex items-center gap-2.5">
          <span class="w-3 h-3 rounded-full bg-cyan-400"></span>
          <h3 class="text-sm font-bold font-mono">TinyML Edge Kinematics Classifier (BMI160)</h3>
        </div>
        <button onclick="closeModal('modal-tinyml-detail')" class="w-7 h-7 rounded-lg bg-[#333030] hover:bg-[#444040] flex items-center justify-center text-gray-300">
          &times;
        </button>
      </div>
      <div class="mt-4 space-y-3 font-mono text-xs text-gray-300">
        <p>Model: Quantized Feed-Forward Neural Network (12KB SRAM footprint on STM32).</p>
        <div class="bg-[#262424] p-3 rounded-xl border border-[#383535] space-y-1">
          <div><span class="text-gray-400">Input Vector:</span> 6-DOF Accel (X,Y,Z) + Gyro (Roll,Pitch,Yaw) @ 50 Hz</div>
          <div><span class="text-gray-400">Class 0:</span> Diam / Istirahat Normal (a_total ~ 1.0g)</div>
          <div><span class="text-gray-400">Class 1:</span> Kerja Aktif Menambang (1.2g - 2.5g)</div>
          <div><span class="text-gray-400">Class 2:</span> Kelelahan / Tremor Lengan (Vibrasi Mikro)</div>
          <div><span class="text-gray-400">Class 3:</span> Benturan Jatuh Bebas / Free-Fall (Peak > 3.0g, Imobilitas >30s)</div>
        </div>
        <div class="flex justify-end gap-2 pt-2">
          <button onclick="testSimSOS(); closeModal('modal-tinyml-detail');" class="px-3 py-1.5 rounded bg-red-950 text-red-200 border border-red-700 hover:bg-red-900 transition">
            Test Free-Fall Trigger
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- ================= MODAL 7: QUICK SEARCH COMMAND PALETTE ================= -->
  <div id="modal-search" class="modal-overlay">
    <div class="bg-[#1C1A1A] text-white w-full max-w-lg rounded-[24px] border border-[#383535] shadow-2xl p-5 relative">
      <div class="flex items-center gap-3 pb-3 border-b border-[#383535]">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
        <input type="text" id="searchInput" placeholder="Search workers, shafts, sensor nodes..." class="bg-transparent text-white font-mono text-sm w-full outline-none" oninput="onSearchFilter()" />
        <button onclick="closeModal('modal-search')" class="text-gray-400 hover:text-white">&times;</button>
      </div>
      <div id="searchResults" class="mt-3 space-y-2 font-mono text-xs max-h-60 overflow-y-auto">
        <div onclick="selectWorker(2); closeModal('modal-search');" class="p-2.5 rounded-xl bg-[#262424] hover:bg-[#333030] cursor-pointer flex justify-between">
          <span>Pekerja #02: Agus Salim</span>
          <span class="text-emerald-400">Sektor 7 (Lorong C-4)</span>
        </div>
        <div onclick="selectWorker(1); closeModal('modal-search');" class="p-2.5 rounded-xl bg-[#262424] hover:bg-[#333030] cursor-pointer flex justify-between">
          <span>Pekerja #01: Bambang (Relay Host)</span>
          <span class="text-amber-400">Junction B-02 (Poros Shaft)</span>
        </div>
        <div onclick="openModal('modal-gis-map'); closeModal('modal-search');" class="p-2.5 rounded-xl bg-[#262424] hover:bg-[#333030] cursor-pointer flex justify-between">
          <span>Subterranean GIS Mine Map</span>
          <span class="text-orange-400">OpenStreetMap Canvas</span>
        </div>
        <div onclick="openModal('modal-fleet-roster'); closeModal('modal-search');" class="p-2.5 rounded-xl bg-[#262424] hover:bg-[#333030] cursor-pointer flex justify-between">
          <span>Dual-Worker Fleet Roster Table</span>
          <span class="text-blue-400">Full Diagnostics</span>
        </div>
      </div>
    </div>
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
    let isDarkMapTile = true;

    // Both workers state
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
    // 2. UI SYNCHRONIZATION WITH CURRENT WORKER
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
      
      // Update simulator sliders to match selected worker
      const slHR = document.getElementById('sliderHR');
      const slSpO2 = document.getElementById('sliderSpO2');
      if (slHR) slHR.value = w.hr;
      if (slSpO2) slSpO2.value = w.spo2;
      
      const hrText = document.getElementById('simHRText');
      const spText = document.getElementById('simSpO2Text');
      if (hrText) hrText.textContent = w.hr + ' BPM';
      if (spText) spText.textContent = w.spo2 + ' %';

      updateTelemetryDisplay(w);
      evaluateSTART(w.hr, w.spo2);
      updateRosterTableUI();
    }

    function updateTelemetryDisplay(w) {
      // 1. HR
      const valHR = document.getElementById('val-hr');
      if (valHR) valHR.textContent = w.hr > 0 ? w.hr : '--';
      const badgeHR = document.getElementById('badge-hr');
      if (badgeHR) {
        if (w.hr > 120) {
          badgeHR.textContent = 'Takikardia';
          badgeHR.className = 'px-2 py-0.5 rounded-[5px] bg-[#FBE7E8] text-[#DE6D72] text-[10px] font-bold';
        } else if (w.hr < 50 && w.hr > 0) {
          badgeHR.textContent = 'Bradikardia';
          badgeHR.className = 'px-2 py-0.5 rounded-[5px] bg-[#FBE7E8] text-[#C0565B] text-[10px] font-bold';
        } else {
          badgeHR.textContent = 'Normal';
          badgeHR.className = 'px-2 py-0.5 rounded-[5px] bg-[#E8F8F0] text-[#1D6A4E] text-[10px] font-bold';
        }
      }

      // 2. SpO2
      const valSpO2 = document.getElementById('val-spo2');
      if (valSpO2) valSpO2.textContent = w.spo2 > 0 ? w.spo2 : '--';
      const badgeSpO2 = document.getElementById('badge-spo2');
      if (badgeSpO2) {
        if (w.spo2 < 90 && w.spo2 > 0) {
          badgeSpO2.textContent = 'Hipoksia Berat';
          badgeSpO2.className = 'px-2 py-0.5 rounded-[5px] bg-[#FBE7E8] text-[#DE6D72] text-[10px] font-bold';
        } else if (w.spo2 < 95 && w.spo2 > 0) {
          badgeSpO2.textContent = 'Hipoksia Ringan';
          badgeSpO2.className = 'px-2 py-0.5 rounded-[5px] bg-[#FFF2DE] text-[#A6681E] text-[10px] font-bold';
        } else {
          badgeSpO2.textContent = 'Optimal';
          badgeSpO2.className = 'px-2 py-0.5 rounded-[5px] bg-[#D0F1F8] text-[#1E4D57] text-[10px] font-bold';
        }
      }

      // 3. Temperature
      const valTemp = document.getElementById('val-temp');
      if (valTemp) valTemp.textContent = w.temp.toFixed(1);
      const badgeTemp = document.getElementById('badge-temp');
      if (badgeTemp) {
        if (w.temp > 38.0) {
          badgeTemp.textContent = 'Hipertermia';
          badgeTemp.className = 'px-2 py-0.5 rounded-[5px] bg-[#FBE7E8] text-[#DE6D72] text-[10px] font-bold';
        } else if (w.temp < 35.5) {
          badgeTemp.textContent = 'Hipotermia';
          badgeTemp.className = 'px-2 py-0.5 rounded-[5px] bg-[#D0F1F8] text-[#1E4D57] text-[10px] font-bold';
        } else {
          badgeTemp.textContent = 'Normotermia';
          badgeTemp.className = 'px-2 py-0.5 rounded-[5px] bg-[#F8DFC2] text-[#5C3912] text-[10px] font-bold';
        }
      }

      // 4. Acceleration Indicator
      const accelPill = document.getElementById('liveAccelPill');
      if (accelPill) {
        if (w.accel > 3.0) {
          accelPill.className = 'px-2.5 py-1 rounded-[8px] bg-red-100 text-red-700 font-mono text-[11px] font-bold animate-pulse cursor-pointer';
          accelPill.textContent = w.accel.toFixed(2) + 'g • BENTURAN SHOCK';
        } else {
          accelPill.className = 'px-2.5 py-1 rounded-[8px] bg-[#EFE9E0] text-[#3E3C39] font-mono text-[11px] font-bold cursor-pointer';
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
          ? 'px-2.5 py-1 rounded bg-red-950 text-red-300 border border-red-600 font-bold text-[10px] animate-pulse'
          : (w1.triageCode === 1 ? 'px-2.5 py-1 rounded bg-amber-950/80 text-amber-300 border border-amber-600 font-bold text-[10px]' : 'px-2.5 py-1 rounded bg-emerald-950/80 text-emerald-300 border border-emerald-600 font-bold text-[10px]');
      }

      const v2 = document.getElementById('rosterVitals02');
      if (v2) v2.innerHTML = w2.hr + ' BPM &bull; ' + w2.spo2 + '% SpO2 &bull; ' + w2.temp.toFixed(1) + '&deg;C';
      const a2 = document.getElementById('rosterActivity02');
      if (a2) a2.textContent = w2.activity;
      const t2 = document.getElementById('rosterTriage02');
      if (t2) {
        t2.textContent = w2.triageLabel;
        t2.className = w2.triageCode === 3 
          ? 'px-2.5 py-1 rounded bg-red-950 text-red-300 border border-red-600 font-bold text-[10px] animate-pulse'
          : 'px-2.5 py-1 rounded bg-emerald-950/80 text-emerald-300 border border-emerald-600 font-bold text-[10px]';
      }
    }

    // -------------------------------------------------------------
    // 3. START TRIAGE RISK SIMULATOR ENGINE & DIRECT CLICKS
    // -------------------------------------------------------------
    function onSimulatorInput() {
      isSimulatorMode = true;
      const label = document.getElementById('simModeLabel');
      const ind = document.getElementById('simModeIndicator');
      if (label) label.textContent = 'Mode: Simulator';
      if (ind) ind.textContent = 'MANUAL SIMULATOR';
      
      const hr = parseInt(document.getElementById('sliderHR').value);
      const spo2 = parseInt(document.getElementById('sliderSpO2').value);

      const hrText = document.getElementById('simHRText');
      const spText = document.getElementById('simSpO2Text');
      if (hrText) hrText.textContent = hr + ' BPM';
      if (spText) spText.textContent = spo2 + ' %';

      evaluateSTART(hr, spo2);
    }

    function toggleSimMode() {
      isSimulatorMode = !isSimulatorMode;
      const label = document.getElementById('simModeLabel');
      const ind = document.getElementById('simModeIndicator');
      if (isSimulatorMode) {
        if (label) label.textContent = 'Mode: Simulator';
        if (ind) ind.textContent = 'MANUAL SIMULATOR';
      } else {
        if (label) label.textContent = 'Mode: Live MQTT';
        if (ind) ind.textContent = 'LIVE HARDWARE';
        const w = workers[currentWorker];
        const slHR = document.getElementById('sliderHR');
        const slSpO2 = document.getElementById('sliderSpO2');
        if (slHR) slHR.value = w.hr;
        if (slSpO2) slSpO2.value = w.spo2;
        const hrText = document.getElementById('simHRText');
        const spText = document.getElementById('simSpO2Text');
        if (hrText) hrText.textContent = w.hr + ' BPM';
        if (spText) spText.textContent = w.spo2 + ' %';
        evaluateSTART(w.hr, w.spo2);
      }
    }

    function setTriageDirect(tier) {
      isSimulatorMode = true;
      const label = document.getElementById('simModeLabel');
      const ind = document.getElementById('simModeIndicator');
      if (label) label.textContent = 'Mode: Simulator';
      if (ind) ind.textContent = 'MANUAL: ' + tier;

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
      if (pct < 0.25) setTriageDirect('HIJAU');
      else if (pct < 0.55) setTriageDirect('KUNING');
      else if (pct < 0.85) setTriageDirect('MERAH');
      else setTriageDirect('HITAM');
    }

    function evaluateSTART(hr, spo2) {
      const pText = document.getElementById('triagePriorityText');
      const subText = document.getElementById('triageSubtitleText');
      const dot = document.getElementById('triageDot');
      const badge = document.getElementById('triageBadgePill');

      if (hr <= 40 || (hr > 160 && spo2 < 75)) {
        // HITAM (Expectant)
        if (pText) {
          pText.textContent = 'HITAM';
          pText.className = 'text-[20px] font-extrabold text-gray-400 tracking-tight font-mono leading-tight';
        }
        if (subText) subText.textContent = 'Expectant / Non-Salvable';
        if (dot) dot.style.left = '92%';
        if (badge) {
          badge.textContent = 'Prioritas Rendah • Paliatif';
          badge.className = 'px-2 py-0.5 rounded-[6px] bg-gray-700 text-gray-200 text-[9.5px] font-bold';
        }
      } else if (hr > 125 || hr < 48 || spo2 < 88) {
        // MERAH (Immediate)
        if (pText) {
          pText.textContent = 'MERAH';
          pText.className = 'text-[20px] font-extrabold text-[#EF4444] tracking-tight font-mono leading-tight animate-pulse';
        }
        if (subText) subText.textContent = 'Immediate / Darurat Kritis SAR';
        if (dot) dot.style.left = '80%';
        if (badge) {
          badge.textContent = 'EVAKUASI SEGERA • PRIORITAS 1';
          badge.className = 'px-2 py-0.5 rounded-[6px] bg-red-950 text-red-200 border border-red-500 text-[9.5px] font-bold animate-pulse';
        }
        if (audioAlertEnabled) playEmergencyBeep();
      } else if (hr > 100 || spo2 < 94) {
        // KUNING (Delayed)
        if (pText) {
          pText.textContent = 'KUNING';
          pText.className = 'text-[20px] font-extrabold text-[#F59E0B] tracking-tight font-mono leading-tight';
        }
        if (subText) subText.textContent = 'Delayed / Waspada Kelelahan';
        if (dot) dot.style.left = '52%';
        if (badge) {
          badge.textContent = 'Pantau Stabil • Prioritas 2';
          badge.className = 'px-2 py-0.5 rounded-[6px] bg-[#F7E8BA] text-[#5C4511] text-[9.5px] font-bold';
        }
      } else {
        // HIJAU (Minor)
        if (pText) {
          pText.textContent = 'HIJAU';
          pText.className = 'text-[20px] font-extrabold text-[#34D399] tracking-tight font-mono leading-tight';
        }
        if (subText) subText.textContent = 'Minor / Personel Stabil Normal';
        if (dot) dot.style.left = '16%';
        if (badge) {
          badge.textContent = 'Aman • Tidak Perlu Evakuasi Cepat';
          badge.className = 'px-2 py-0.5 rounded-[6px] bg-[#D5F4EA] text-[#1D4A3D] text-[9.5px] font-bold';
        }
      }
    }

    // -------------------------------------------------------------
    // 4. KINEMATICS ACTIVITY STREAM BARS & CLICKS
    // -------------------------------------------------------------
    const shiftData = {
      pagi: [
        [15, 30, 20], [18, 45, 15], [20, 20, 35], [45, 25, 10], [25, 40, 20],
        [18, 55, 15], [30, 25, 25], [20, 35, 30], [22, 28, 20], [60, 20, 10],
        [35, 30, 15], [20, 40, 25], [25, 35, 20], [30, 25, 30], [18, 45, 15],
        [22, 38, 22], [28, 22, 35], [20, 40, 20]
      ],
      siang: [
        [30, 35, 15], [25, 40, 20], [40, 20, 20], [22, 45, 18], [28, 30, 25],
        [35, 25, 20], [20, 50, 15], [45, 20, 15], [30, 30, 25], [25, 35, 20],
        [20, 42, 22], [35, 28, 18], [28, 32, 25], [22, 45, 18], [32, 28, 20],
        [40, 22, 18], [25, 35, 25], [30, 30, 20]
      ],
      malam: [
        [12, 20, 45], [15, 25, 40], [18, 20, 50], [25, 22, 35], [15, 30, 40],
        [20, 25, 45], [18, 28, 38], [22, 20, 45], [15, 35, 35], [28, 20, 40],
        [18, 25, 42], [20, 22, 45], [15, 30, 40], [22, 25, 38], [18, 28, 40],
        [25, 20, 42], [15, 30, 40], [20, 25, 40]
      ]
    };

    let currentShiftKey = 'pagi';
    const shiftKeys = ['pagi', 'siang', 'malam'];
    const shiftLabels = {
      pagi: 'Shift Pagi // Sektor 7',
      siang: 'Shift Siang // Lorong C',
      malam: 'Shift Malam // Poros B'
    };

    function renderKinematicsBars() {
      const container = document.getElementById('kinematicsBarsContainer');
      if (!container) return;
      container.innerHTML = '';
      const bars = shiftData[currentShiftKey];

      bars.forEach((segs, idx) => {
        const [redH, tealH, ochreH] = segs;
        const col = document.createElement('div');
        col.className = 'day-col flex flex-col items-center justify-end h-full relative cursor-pointer group';
        col.style.width = '18px';
        col.onclick = () => selectBarInterval(idx, redH, tealH, ochreH);

        const totalG = ((redH * 0.045) + (tealH * 0.025) + (ochreH * 0.015)).toFixed(2);

        col.innerHTML = `
          <div class="opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity duration-150 absolute -top-8 bg-[#2C2A2A] text-white text-[9.5px] font-mono font-bold px-2.5 py-1 rounded-md shadow-lg whitespace-nowrap z-20">
            T+` + (idx * 10) + `m: ` + totalG + `g &bull; ` + (redH > 40 ? 'BENTURAN' : (tealH > 35 ? 'KERJA AKTIF' : 'NORMAL')) + `
          </div>
          <div class="flex flex-col items-center gap-[4.5px] mb-1">
            <span class="pill-seg w-[4.5px] rounded-full bg-[#CD8A39]" style="height: ` + ochreH + `px"></span>
            <span class="pill-seg w-[4.5px] rounded-full bg-[#438D9B]" style="height: ` + tealH + `px"></span>
            <span class="pill-seg w-[4.5px] rounded-full bg-[#DA7468]" style="height: ` + redH + `px"></span>
          </div>
          <div class="h-0 w-full flex justify-end">
            <span class="x-label">T+` + (idx * 10) + `m</span>
          </div>
        `;
        container.appendChild(col);
      });
    }

    function selectBarInterval(idx, r, t, o) {
      document.querySelectorAll('.day-col').forEach(c => c.classList.remove('selected-bar'));
      const cols = document.querySelectorAll('.day-col');
      if (cols[idx]) cols[idx].classList.add('selected-bar');
      
      const g = ((r * 0.045) + (t * 0.025) + (o * 0.015)).toFixed(2);
      const accelPill = document.getElementById('liveAccelPill');
      if (accelPill) {
        accelPill.textContent = g + 'g @ T+' + (idx * 10) + 'm';
      }
    }

    function cycleShift() {
      const nextIdx = (shiftKeys.indexOf(currentShiftKey) + 1) % shiftKeys.length;
      currentShiftKey = shiftKeys[nextIdx];
      const shiftEl = document.getElementById('shiftLabel');
      if (shiftEl) shiftEl.textContent = shiftLabels[currentShiftKey];
      renderKinematicsBars();
    }

    function setFilterActivity(type) {
      if (type === 'shock') testSimSOS();
      else if (type === 'work') {
        const w = workers[currentWorker];
        w.accel = 1.95;
        w.activity = 'Kerja Tambang Aktif';
        updateTelemetryDisplay(w);
      } else {
        testSimNormal();
      }
    }

    // -------------------------------------------------------------
    // 5. WEARABLE SENSOR ANATOMICAL HIGHLIGHTING
    // -------------------------------------------------------------
    function highlightSensorRing(ringId, isHover) {
      const ring = document.getElementById(ringId);
      if (!ring) return;
      if (isHover) {
        ring.style.transform = 'scale(1.08)';
        ring.style.transformOrigin = 'center center';
        ring.style.filter = 'drop-shadow(0 0 14px rgba(255, 140, 60, 1))';
      } else {
        ring.style.transform = 'scale(1)';
        ring.style.filter = 'drop-shadow(0 0 6px rgba(240, 82, 72, 0.7))';
      }
    }

    // -------------------------------------------------------------
    // 6. METRIC DETAIL POPOVER MODAL
    // -------------------------------------------------------------
    function openMetricDetail(type) {
      const title = document.getElementById('metricDetailTitle');
      const body = document.getElementById('metricDetailBody');
      const w = workers[currentWorker];

      if (type === 'hr') {
        if (title) title.textContent = 'MAX30102 PPG Arterial Pulse Diagnostics';
        if (body) {
          body.innerHTML = `
            <div class="bg-[#262424] p-3 rounded-xl border border-[#383535] space-y-1.5">
              <div><span class="text-gray-400">Target Personnel:</span> ` + w.name + `</div>
              <div><span class="text-gray-400">Current Rate:</span> <b class="text-white text-base">` + w.hr + ` BPM</b></div>
              <div><span class="text-gray-400">Sensor:</span> Dual Red (660nm) & IR (880nm) Photoplethysmography</div>
              <div><span class="text-gray-400">Sampling Rate:</span> 100 Hz Hardware ADC Buffer</div>
              <div><span class="text-gray-400">Clinical Status:</span> <span class="text-emerald-400 font-bold">` + (w.hr > 120 ? 'Takikardia (Waspada)' : 'Ritme Sinus Normal') + `</span></div>
            </div>
          `;
        }
        highlightSensorRing('chestRing', true);
      } else if (type === 'spo2') {
        if (title) title.textContent = 'Blood Oxygen Saturation (SpO2)';
        if (body) {
          body.innerHTML = `
            <div class="bg-[#262424] p-3 rounded-xl border border-[#383535] space-y-1.5">
              <div><span class="text-gray-400">Target Personnel:</span> ` + w.name + `</div>
              <div><span class="text-gray-400">Current Saturation:</span> <b class="text-cyan-400 text-base">` + w.spo2 + ` %</b></div>
              <div><span class="text-gray-400">Calculation:</span> AC/DC Ratio Calibration Curve</div>
              <div><span class="text-gray-400">Subterranean O2 Limit:</span> 19.5% Minimum Ambient Threshold</div>
              <div><span class="text-gray-400">Hypoxia Risk:</span> <span class="text-emerald-400 font-bold">` + (w.spo2 < 90 ? 'BAHAYA HIPOKSIA KRITIS' : 'Optimal Non-Hypoxic') + `</span></div>
            </div>
          `;
        }
        highlightSensorRing('chestRing', true);
      } else if (type === 'temp') {
        if (title) title.textContent = 'MLX90614 Contactless IR Thermopile';
        if (body) {
          body.innerHTML = `
            <div class="bg-[#262424] p-3 rounded-xl border border-[#383535] space-y-1.5">
              <div><span class="text-gray-400">Target Personnel:</span> ` + w.name + `</div>
              <div><span class="text-gray-400">Skin Temperature:</span> <b class="text-amber-400 text-base">` + w.temp.toFixed(1) + ` &deg;C</b></div>
              <div><span class="text-gray-400">Optics:</span> 90&deg; Field-of-View IR Medical Sensor</div>
              <div><span class="text-gray-400">Thermal Index:</span> ` + (w.temp > 38 ? 'Hipertermia Bawah Tanah' : 'Normotermia Fisiologis') + `</div>
            </div>
          `;
        }
        highlightSensorRing('wristRing', true);
      }
      openModal('modal-metric-detail');
    }

    // -------------------------------------------------------------
    // 7. MODAL SYSTEM & NAVIGATION
    // -------------------------------------------------------------
    function openModal(modalId) {
      const modal = document.getElementById(modalId);
      if (modal) {
        modal.classList.add('open');
        if (modalId === 'modal-gis-map') {
          if (!leafletMap) {
            setTimeout(initLeafletMap, 150);
          } else {
            setTimeout(() => leafletMap.invalidateSize(), 150);
          }
        }
      }
    }

    function closeModal(modalId) {
      const modal = document.getElementById(modalId);
      if (modal) modal.classList.remove('open');
    }

    // Close on backdrop click
    document.addEventListener('click', (e) => {
      if (e.target.classList.contains('modal-overlay')) {
        e.target.classList.remove('open');
      }
    });

    // Close on ESC key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        document.querySelectorAll('.modal-overlay.open').forEach(m => m.classList.remove('open'));
      }
    });

    function setActiveNav(btn, view) {
      document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
    }

    function resetToOverview() {
      selectWorker(2);
      document.querySelectorAll('.modal-overlay').forEach(m => m.classList.remove('open'));
      const btn = document.getElementById('navBtnOverview');
      if (btn) setActiveNav(btn, 'overview');
    }

    function focusFromRoster(workerId) {
      closeModal('modal-fleet-roster');
      selectWorker(workerId);
      openModal('modal-gis-map');
      setTimeout(() => focusMapNode(workerId), 250);
    }

    function runDiagWatch(workerId) {
      const w = workers[workerId];
      alert("DIAGNOSTIK JAM TANGAN #" + (workerId < 10 ? '0' + workerId : workerId) + " (" + w.name + "):\nStatus Hardware: Aktif Normal\nLoRa Link: " + w.route + " (" + w.rssi + " dBm)\nVitals: " + w.hr + " BPM • " + w.spo2 + "% SpO2 • " + w.temp.toFixed(1) + "°C\nTriage: " + w.triageLabel + "\nBaterai LiPo: 81% (4.12V)\nForwarding Mesh: 1-Hop P2P Aktif");
    }

    // -------------------------------------------------------------
    // 8. LEAFLET SUBTERRANEAN GIS MAP
    // -------------------------------------------------------------
    function initLeafletMap() {
      const mapContainer = document.getElementById('leafletMapContainer');
      if (!mapContainer) return;

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

      // Tactical Markers with Inline CSS
      const createMarker = (title, subtitle, color) => {
        return L.divIcon({
          className: 'tactical-div-icon',
          html: `<div style="background: rgba(28,26,26,0.96); border: 1.5px solid ` + color + `; padding: 4px 8px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.5); display: flex; align-items: center; gap: 6px; white-space: nowrap; font-family: monospace; font-size: 10px; color: white;">
                   <span style="width: 8px; height: 8px; border-radius: 999px; background: ` + color + `;"></span>
                   <b>` + title + `</b>
                   <span style="color: #9C9892;">(` + subtitle + `)</span>
                 </div>`,
          iconSize: [180, 26],
          iconAnchor: [90, 24]
        });
      };

      gatewayMarker = L.marker(gatewayPos, {
        icon: createMarker('BASECAMP GATEWAY', 'Surface Node', '#34D399')
      }).addTo(leafletMap).bindPopup('<div class="font-mono text-xs"><b>Posko Permukaan Basecamp</b><br/>ESP32 Gateway + LTE Uplink</div>');

      watch1Marker = L.marker(watch1Pos, {
        icon: createMarker('JAM #01: BAMBANG', 'Relay Host', '#F59E0B')
      }).addTo(leafletMap).bindPopup('<div class="font-mono text-xs"><b>Jam Tangan #01: Bambang</b><br/>Junction B-02 Poros Shaft<br/>Peran: LoRa 1-Hop Mesh Relay Forwarder</div>');

      watch2Marker = L.marker(watch2Pos, {
        icon: createMarker('JAM #02: AGUS SALIM', 'Sektor 7 Miner', '#10B981')
      }).addTo(leafletMap).bindPopup('<div class="font-mono text-xs"><b>Jam Tangan #02: Agus Salim</b><br/>Lorong C-4 Sektor 7 Tambang<br/>Status: Normal / Terhubung Mesh</div>');

      // Hop Vector Lines
      hopPolyline = L.polyline([watch2Pos, watch1Pos], {
        color: '#10B981',
        weight: 3.5,
        opacity: 0.85
      }).addTo(leafletMap);

      uplinkPolyline = L.polyline([watch1Pos, gatewayPos], {
        color: '#E59A43',
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
        ? 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}'
        : 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';
      
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

    function pulseHopSimulation() {
      if (!hopPolyline || !uplinkPolyline) return;
      hopPolyline.setStyle({ weight: 7, color: '#FCD34D' });
      setTimeout(() => {
        hopPolyline.setStyle({ weight: 3.5, color: '#10B981' });
        uplinkPolyline.setStyle({ weight: 7, color: '#EF4444' });
        setTimeout(() => {
          uplinkPolyline.setStyle({ weight: 4, color: '#E59A43' });
          appendAuditTrail('LoRa 1-Hop Mesh Transmission Success', 'Hop 1 Forwarded (18ms)', 'Jam #02 -> Jam #01 -> Surface Gateway Basecamp', 'green');
        }, 600);
      }, 600);
    }

    // -------------------------------------------------------------
    // 9. SAR CHRONOLOGICAL AUDIT TRAIL & DISPATCH
    // -------------------------------------------------------------
    function appendAuditTrail(title, tag, desc, color) {
      const container = document.getElementById('auditLogList');
      if (!container) return;

      const now = new Date();
      const timeStr = now.toTimeString().split(' ')[0] + ' UTC';

      const div = document.createElement('div');
      const borderColors = {
        red: 'border-l-4 border-red-500 bg-red-950/40 text-red-100',
        amber: 'border-l-4 border-amber-500 bg-amber-950/40 text-amber-100',
        green: 'border-l-4 border-emerald-500 bg-emerald-950/40 text-emerald-100',
        orange: 'border-l-4 border-orange-500 bg-orange-950/40 text-orange-100'
      };

      div.className = 'p-3 rounded-xl border border-[#383535] ' + (borderColors[color] || borderColors.green) + ' transition';
      div.innerHTML = `
        <div class="flex justify-between font-bold">
          <span>` + timeStr + ` &bull; ` + title + `</span>
          <span class="text-[10px] uppercase font-mono tracking-wider">` + tag + `</span>
        </div>
        <p class="text-[11px] text-gray-300 mt-1">` + desc + `</p>
      `;

      container.insertBefore(div, container.firstChild);

      const badge = document.getElementById('alertCountBadge');
      if (badge && color === 'red') {
        const count = parseInt(badge.textContent || '0') + 1;
        badge.textContent = count;
      }
    }

    function dispatchAlphaSquad() {
      alert("PERINTAH DISPATCH TERKIRIM:\nRegu Penolong Alpha Search Squad telah diberangkatkan menuju Sektor 7 (C-4) untuk evakuasi darurat!");
      appendAuditTrail('SAR Alpha Squad Dispatched', 'DISPATCH', 'Unit penolong bergerak menuju Sektor 7 (C-4)', 'red');
      pulseHopSimulation();
    }

    // -------------------------------------------------------------
    // 10. WEB AUDIO API SYNTHESIZER FOR EMERGENCY ALERT
    // -------------------------------------------------------------
    function toggleAudioAlert() {
      audioAlertEnabled = !audioAlertEnabled;
      const btn = document.getElementById('sirenBtn');
      if (audioAlertEnabled) {
        if (btn) {
          btn.classList.add('bg-red-500', 'text-white');
          btn.classList.remove('nav-btn');
          btn.style.width = '46px';
          btn.style.height = '46px';
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
    // 11. SEARCH PALETTE FILTER
    // -------------------------------------------------------------
    function onSearchFilter() {
      const q = (document.getElementById('searchInput')?.value || '').toLowerCase();
      const items = document.querySelectorAll('#searchResults > div');
      items.forEach(el => {
        el.style.display = el.textContent.toLowerCase().includes(q) ? 'flex' : 'none';
      });
    }

    // -------------------------------------------------------------
    // 12. REAL-TIME MQTT ENGINE (broker.emqx.io:8084)
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
          appendAuditTrail('MQTT EMQX Online', 'CONNECTED', 'Listening to rescue/tag/data & rescue/tag/alert', 'green');
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

            // Update fleet table
            updateRosterTableUI();

            // If currently viewing this worker, update active dashboard
            if (currentWorker === workerNum && !isSimulatorMode) {
              updateTelemetryDisplay(w);
              evaluateSTART(w.hr, w.spo2);
              const slHR = document.getElementById('sliderHR');
              const slSpO2 = document.getElementById('sliderSpO2');
              if (slHR) slHR.value = w.hr;
              if (slSpO2) slSpO2.value = w.spo2;
              const hrText = document.getElementById('simHRText');
              const spText = document.getElementById('simSpO2Text');
              if (hrText) hrText.textContent = w.hr + ' BPM';
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
    // 13. DEMO TRIGGER FUNCTIONS FOR COMPETITION JURY
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
      appendAuditTrail('Simulated Free-Fall Shock & Tachycardia', 'TEST SOS', 'Agus Salim Sektor 7: Benturan 4.85g dan Hipoksia 86%', 'red');
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
      appendAuditTrail('Simulated Normal Baseline Telemetry', 'TEST NORMAL', 'Agus Salim Sektor 7: Vitals stabil', 'green');
    }

    function toggleMqttInfo() {
      alert("MQTT BROKER STATUS:\nBroker: broker.emqx.io\nPort: 8084 (Secure WebSocket)\nTopics: rescue/tag/data, rescue/tag/alert\nRelay: LoRa 1-Hop Mesh P2P");
    }

    // -------------------------------------------------------------
    // 14. INITIALIZATION ON LOAD
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

      // 4. Initial Audit Trail
      appendAuditTrail('RescueTag Command Hub Initialized', 'BOOT', 'Dual-worker subterranean mesh gateway ready', 'green');
      appendAuditTrail('LoRa 1-Hop Mesh Topology Synchronized', 'ROUTER', 'Node #02 (Sektor 7) -> Node #01 Relay (Junction B-02)', 'orange');

      // 5. Connect MQTT
      initMQTT();
    });
  </script>
</body>
</html>
"""

# Replace base64 image placeholder
final_html = HTML_TEMPLATE.replace("BASE64_IMAGE_PLACEHOLDER", data_uri)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(final_html)

print(f"Generated index.html successfully! Length: {len(final_html)} bytes.")
