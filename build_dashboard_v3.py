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
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Mulish:wght@400;500;600;700;800&family=Outfit:wght@400;500;600;700;800;900&family=Playfair+Display:ital,wght@1,400;1,600;1,700;1,800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
  
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
      background-color: #F4EFEB;
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

    /* ================= RESPONSIVE ENGINE (MOBILE & TABLET ADAPTATION) ================= */
    @media (max-width: 1220px) {
      body {
        align-items: flex-start;
        padding: 0.75rem;
      }
      .dashboard-wrapper {
        min-width: 0;
        width: 100%;
        max-width: 1180px;
        height: auto;
        min-height: auto;
        grid-template-columns: 84px 1fr;
      }
      .right-tactical-panel {
        grid-column: span 2;
        border-radius: 0 0 34px 34px !important;
        border-left: none;
        border-top: 1px solid #3D3A3A;
      }
    }

    @media (max-width: 1024px) {
      body {
        align-items: flex-start !important;
        justify-content: flex-start !important;
        padding: 0.5rem !important;
        min-height: 100vh !important;
        height: auto !important;
        overflow-x: hidden !important;
      }

      .dashboard-wrapper {
        min-width: 0 !important;
        width: 100% !important;
        max-width: 100% !important;
        height: auto !important;
        min-height: auto !important;
        display: flex !important;
        flex-direction: column !important;
        border-radius: 20px !important;
        overflow: visible !important;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08) !important;
      }

      .left-sidebar {
        flex-direction: row !important;
        width: 100% !important;
        height: auto !important;
        padding: 0.6rem 0.85rem !important;
        border-right: none !important;
        border-bottom: 1px solid #F0ECE6 !important;
        position: sticky !important;
        top: 0 !important;
        z-index: 50 !important;
        background: rgba(255, 255, 255, 0.97) !important;
        backdrop-filter: blur(12px) !important;
        border-radius: 20px 20px 0 0 !important;
      }

      .left-sidebar .top-cluster {
        flex-direction: row !important;
        width: auto !important;
        gap: 0.65rem !important;
        align-items: center !important;
      }

      .left-sidebar nav {
        flex-direction: row !important;
        margin: 0 !important;
        gap: 0.35rem !important;
        overflow-x: auto !important;
      }

      .left-sidebar .bottom-cluster {
        margin-left: auto !important;
        padding-bottom: 0 !important;
      }

      .nav-btn {
        width: 38px !important;
        height: 38px !important;
        border-radius: 10px !important;
      }

      .nav-btn svg {
        width: 17px !important;
        height: 17px !important;
      }

      main {
        padding: 1.25rem 1rem !important;
        height: auto !important;
        overflow-y: visible !important;
      }

      .center-view {
        height: auto !important;
        min-height: auto !important;
      }

      .right-tactical-panel {
        width: 100% !important;
        max-width: 100% !important;
        border-radius: 0 0 20px 20px !important;
        border-left: none !important;
        border-top: 1px solid #3D3A3A !important;
        padding: 1.5rem 1rem !important;
        height: auto !important;
        overflow: visible !important;
      }

      .triage-simulator-grid {
        grid-template-columns: 1fr !important;
        gap: 0.85rem !important;
      }

      .sensor-ergo-grid {
        grid-template-columns: 1fr !important;
        gap: 1rem !important;
      }

      .sensor-cards-stack {
        display: grid !important;
        grid-template-columns: repeat(3, 1fr) !important;
        gap: 0.5rem !important;
        width: 100% !important;
      }

      .sensor-cards-stack .measure-card {
        width: 100% !important;
        height: auto !important;
        min-height: 66px !important;
        padding: 0.5rem !important;
      }
    }

    @media (max-width: 640px) {
      body {
        padding: 0.25rem !important;
      }

      .dashboard-wrapper {
        border-radius: 14px !important;
      }

      .left-sidebar {
        padding: 0.5rem 0.65rem !important;
        border-radius: 14px 14px 0 0 !important;
      }

      .left-sidebar .sec-tag {
        display: none !important;
      }

      main {
        padding: 1rem 0.65rem !important;
      }

      .vitals-grid {
        grid-template-columns: 1fr !important;
        gap: 0.65rem !important;
      }

      .metric-card {
        border-radius: 14px !important;
      }

      .kinematics-card {
        min-height: auto !important;
        padding: 1rem 0.75rem !important;
      }

      .right-tactical-panel {
        padding: 1.25rem 0.75rem !important;
        border-radius: 0 0 14px 14px !important;
      }

      .sensor-cards-stack {
        grid-template-columns: 1fr !important;
        gap: 0.5rem !important;
      }

      .sensor-cards-stack .measure-card {
        flex-direction: row !important;
        justify-content: space-between !important;
        padding: 0.6rem 0.85rem !important;
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
  
    /* Login Page Typography & Styles */
    .font-outfit { font-family: 'Outfit', sans-serif; }
    .font-tech { font-family: 'Space Grotesk', sans-serif; }
    .font-brand { font-family: 'Playfair Display', Georgia, serif; font-style: italic; }
    .role-btn {
      color: #7B7874;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .role-btn.active {
      background: #2D2B2A !important;
      color: #FFFFFF !important;
      box-shadow: 0 1px 4px rgba(0, 0, 0, 0.12);
      font-weight: 700;
    }
    .btn-tactile {
      transition: all 0.15s cubic-bezier(0.16, 1, 0.3, 1);
      cursor: pointer;
    }
    .btn-tactile:active {
      transform: scale(0.98);
    }
</style>
</head>
<body class="min-h-screen flex items-center justify-center select-none bg-[#F4EFEB] bg-[radial-gradient(#DBD4C8_1.2px,transparent_1.2px)] [background-size:24px_24px] text-[#2D2B2A]">

  <!-- ================= PAGE 1: ACCESS TERMINAL LOGIN PORTAL ================= -->
  <div id="page-login" class="fixed inset-0 z-50 bg-[#F4EFEB] bg-[radial-gradient(#DBD4C8_1.2px,transparent_1.2px)] [background-size:24px_24px] flex items-center justify-center p-4 md:p-8 overflow-y-auto select-none">
    
    <!-- Outer Double-Bezel Tray (Doppelrand Architecture matching dashboard) -->
    <div class="w-full max-w-5xl rounded-[2.5rem] p-2.5 sm:p-3 bg-[#EAE5DC]/80 border border-[#DBD4C8] shadow-[0_32px_80px_-16px_rgba(45,43,42,0.14),0_0_0_1px_rgba(255,255,255,0.8)] backdrop-blur-2xl">
      
      <!-- Inner Core Canvas Container -->
      <div class="w-full rounded-[2rem] bg-white border border-[#F0ECE6] overflow-hidden grid grid-cols-1 lg:grid-cols-12 shadow-sm min-h-[640px]">
        
        <!-- Left Column (5 cols): Tactical Command Center Terminal -->
        <div class="lg:col-span-5 bg-white p-7 md:p-8 lg:border-r border-[#F0ECE6] flex flex-col justify-between relative z-10">
          <div>
            <!-- Terminal Header & Brand -->
            <div class="flex items-center justify-between pb-4 mb-5 border-b border-[#F0ECE6]">
              <div class="flex items-center gap-3.5">
                <div class="w-10 h-10 rounded-xl bg-[#FAF6F1] border border-[#E5DFD4] flex items-center justify-center shadow-2xs flex-shrink-0 group">
                  <svg width="26" height="26" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg" class="transition-transform duration-300 group-hover:scale-110">
                    <rect x="11.5" y="4.5" width="13" height="27" rx="6.5" transform="rotate(-45 18 18)" stroke="#C68B39" stroke-width="2.4"/>
                    <rect x="11.5" y="4.5" width="13" height="27" rx="6.5" transform="rotate(45 18 18)" stroke="#C68B39" stroke-width="2.4"/>
                  </svg>
                </div>
                <div>
                  <span class="font-brand italic font-extrabold text-2xl tracking-normal text-[#2D2B2A] leading-none block">Rescue-Tag</span>
                  <span class="text-[9px] font-mono tracking-widest text-[#7B7874] font-bold uppercase block mt-1">DISASTER TRIAGE PORTAL</span>
                </div>
              </div>
              <span class="font-mono text-[9px] font-bold text-[#7B7874] bg-[#FAF6F1] px-2.5 py-1 rounded-md border border-[#E5DFD4] shadow-2xs">
                SEC-01
              </span>
            </div>

            <div class="mb-5">
              <span class="font-tech text-[10px] font-bold uppercase tracking-[0.22em] text-[#7B7874] block mb-1">
                [ ACCESS TERMINAL // 2026 ]
              </span>
              <h2 class="font-outfit text-2xl md:text-3xl font-extrabold text-[#2D2B2A] tracking-tight leading-tight">Command Center</h2>
              <p class="text-xs text-[#7B7874] mt-1.5 leading-relaxed font-sans">Sistem Pemantauan Triage Bawah Tanah &amp; Jaringan LoRa 1-Hop Relay</p>
            </div>

            <!-- Segmented Role Selector (Swiss Precision Architecture) -->
            <div class="mb-5">
              <label class="block text-[10px] font-tech font-bold text-[#A6A29C] uppercase tracking-widest mb-2">OPERATOR ROLE PROFILE:</label>
              <div class="grid grid-cols-3 p-1 rounded-xl bg-[#FAF6F1] border border-[#F0ECE6] text-xs font-tech font-medium" id="login-role-selector">
                <button type="button" onclick="selectLoginRole('SAR Commander', this)" class="role-btn active py-2 px-1 rounded-lg text-center text-[11px]">
                  SAR Cmd
                </button>
                <button type="button" onclick="selectLoginRole('Field Paramedic', this)" class="role-btn py-2 px-1 rounded-lg text-[#7B7874] hover:text-[#2D2B2A] text-center text-[11px]">
                  Medic
                </button>
                <button type="button" onclick="selectLoginRole('Mine K3 Lead', this)" class="role-btn py-2 px-1 rounded-lg text-[#7B7874] hover:text-[#2D2B2A] text-center text-[11px]">
                  K3 Lead
                </button>
              </div>
            </div>

            <!-- Form Fields with Double-Bezel Framing -->
            <form onsubmit="handleLogin(event)" class="space-y-3.5">
              <div>
                <div class="flex justify-between items-center mb-1">
                  <label class="block text-[11px] font-tech font-semibold text-[#2D2B2A]">Operator ID / NIP</label>
                  <span class="text-[9px] font-mono text-[#A6A29C]">[REQUIRED]</span>
                </div>
                <input type="text" id="login-nip" value="250534618547" required class="w-full px-3.5 py-2.5 rounded-xl border border-[#E5DFD4] bg-[#FAF6F1] text-xs font-mono text-[#2D2B2A] focus:bg-white focus:outline-none focus:border-[#2D2B2A] focus:ring-2 focus:ring-[#2D2B2A]/10 transition shadow-inner" />
              </div>
              <div>
                <div class="flex justify-between items-center mb-1">
                  <label class="block text-[11px] font-tech font-semibold text-[#2D2B2A]">Security Passcode</label>
                  <a href="#" class="text-[10px] font-mono text-[#7B7874] hover:text-[#2D2B2A] hover:underline font-semibold">Reset Passcode?</a>
                </div>
                <input type="password" id="login-pass" value="rescetag2026" required class="w-full px-3.5 py-2.5 rounded-xl border border-[#E5DFD4] bg-[#FAF6F1] text-xs font-mono text-[#2D2B2A] focus:bg-white focus:outline-none focus:border-[#2D2B2A] focus:ring-2 focus:ring-[#2D2B2A]/10 transition shadow-inner" />
              </div>

              <!-- Button-in-Button Tactical CTA Button (Charcoal #2D2B2A matching Dashboard) -->
              <button type="submit" class="btn-tactile w-full py-2.5 pl-4 pr-2 bg-[#2D2B2A] hover:bg-[#1C1A1A] text-white rounded-xl text-xs font-outfit font-bold tracking-wider uppercase shadow-md transition mt-2 flex items-center justify-between group active:scale-[0.98] cursor-pointer">
                <span>LOGIN</span>
                <span class="w-7 h-7 rounded-lg bg-white/10 flex items-center justify-center group-hover:translate-x-1 transition-transform">
                  <svg class="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3"/>
                  </svg>
                </span>
              </button>
            </form>
          </div>

          <!-- Dramatic Philosophy Creed (Centered & Elevated) -->
          <div class="mt-6 pt-4 border-t border-[#F0ECE6] text-center">
            <p class="font-brand italic text-[#7B7874] text-[13px] sm:text-sm tracking-normal leading-relaxed">
              &ldquo;Engineered for the unseen critical moments.&rdquo;
            </p>
          </div>
        </div>

        <!-- Right Column (7 cols): Art-Directed Minimalist Hardware Showcase (Warm Sand #FAF6F1) -->
        <div class="lg:col-span-7 bg-[#FAF6F1] p-6 md:p-8 flex flex-col justify-between relative overflow-hidden">
          
          <!-- Subtle Blueprint Corner Ticks -->
          <div class="absolute top-3 left-3 text-[#D1CDC7] font-mono text-xs select-none pointer-events-none">+</div>
          <div class="absolute top-3 right-3 text-[#D1CDC7] font-mono text-xs select-none pointer-events-none">+</div>
          <div class="absolute bottom-3 left-3 text-[#D1CDC7] font-mono text-xs select-none pointer-events-none">+</div>
          <div class="absolute bottom-3 right-3 text-[#D1CDC7] font-mono text-xs select-none pointer-events-none">+</div>

          <!-- Editorial Top Header Strip (Featuring Playfair Display Italic + Outfit) -->
          <div class="w-full flex items-start justify-between pb-3.5 border-b border-[#E5DFD4] relative z-10">
            <div>
              <span class="font-tech text-[10px] font-bold tracking-[0.22em] text-[#7B7874] uppercase block mb-1">
                HARDWARE SPEC // NODE-01
              </span>
              <div class="flex items-baseline gap-2">
                <h3 class="font-brand italic font-bold text-2xl text-[#2D2B2A] leading-none">
                  Rescue-Tag
                </h3>
                <span class="font-outfit font-semibold text-[#7B7874] text-sm">Wearable Unit</span>
              </div>
            </div>
            <div class="text-right">
              <span class="font-mono text-[9px] text-[#7B7874] tracking-wider block">433.05 MHz SUB-GHZ</span>
              <span class="font-tech text-[10px] font-bold text-[#2D2B2A] bg-white px-2.5 py-0.5 rounded-md border border-[#E5DFD4] block mt-1 shadow-2xs">
                SUB-GHZ &bull; OLED
              </span>
            </div>
          </div>

          <!-- 3D Hardware Stage (Pure Studio Horizon - Proportional & Clean) -->
          <div class="relative w-full my-auto py-6 flex items-center justify-center group">
            
            <!-- Soft Ambient Neutral Horizon Glow -->
            <div class="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-black/[0.03] via-[#2D2B2A]/[0.015] to-transparent rounded-full filter blur-3xl transform scale-75 group-hover:scale-90 transition-all duration-700 pointer-events-none"></div>

            <!-- Minimalist Coordinate Ticks -->
            <span class="absolute top-2 left-2 font-mono text-[9px] text-[#A6A29C] tracking-widest pointer-events-none">LAT -8.2465&deg;</span>
            <span class="absolute top-2 right-2 font-mono text-[9px] text-[#A6A29C] tracking-widest pointer-events-none">LON 113.6965&deg;</span>

            <!-- 3D Prototype Image (Proportional, Balanced Scale) -->
            <div class="relative py-2 px-4 transition-transform duration-700 ease-[cubic-bezier(0.32,0.72,0,1)] group-hover:scale-105 group-hover:-translate-y-1.5 cursor-pointer z-10 flex items-center justify-center">
              <img 
                src="BASE64_PLACEHOLDER" 
                alt="Rescue-Tag Industrial Smartwatch Prototype" 
                class="w-auto h-[270px] sm:h-[295px] md:h-[315px] max-h-[330px] object-contain drop-shadow-[0_20px_32px_rgba(0,0,0,0.18)] filter contrast-105" 
              />
            </div>

          </div>

          <!-- Bottom Architectural Spec Rail (Clean, Swiss Minimalist Metrics) -->
          <div class="w-full pt-3.5 border-t border-[#E5DFD4] grid grid-cols-3 divide-x divide-[#E5DFD4] text-center relative z-10">
            <div class="px-2">
              <span class="font-tech text-[9px] uppercase tracking-[0.18em] text-[#7B7874] block font-medium">ENCLOSURE</span>
              <span class="font-outfit text-xs font-bold text-[#2D2B2A] block mt-0.5">IP68 Rugged ABS</span>
            </div>
            <div class="px-2">
              <span class="font-tech text-[9px] uppercase tracking-[0.18em] text-[#7B7874] block font-medium">TELEMETRY</span>
              <span class="font-outfit text-xs font-bold text-[#2D2B2A] block mt-0.5">0.96" Live OLED</span>
            </div>
            <div class="px-2">
              <span class="font-tech text-[9px] uppercase tracking-[0.18em] text-[#7B7874] block font-medium">RELAY</span>
              <span class="font-outfit text-xs font-bold text-[#2D2B2A] block mt-0.5">1-Hop P2P (18ms)</span>
            </div>
          </div>

        </div>

      </div>
    </div>
  </div>

  <!-- ================= PAGE 2: RESCUETAG COMMAND CENTER DASHBOARD (Hidden until login) ================= -->
  <div id="page-dashboard" class="hidden min-h-screen w-full flex items-center justify-center p-4 md:p-6 bg-[#F4EFEB] bg-[radial-gradient(#DBD4C8_1.2px,transparent_1.2px)] [background-size:24px_24px]">


  <!-- ================= MASTER DASHBOARD CONTAINER (1180px by 856px) ================= -->
  <div class="dashboard-wrapper">

    <!-- ================= 1. LEFT SIDEBAR (84px) ================= -->
    <aside class="left-sidebar bg-white h-full flex flex-col items-center py-7 justify-between border-r border-[#F0ECE6] z-10 select-none">
      
      <!-- Top Cluster: Emblem + Raised Navigation Bar -->
      <div class="top-cluster flex flex-col items-center gap-7 w-full">
        <!-- Top Emblem: RescueTag LoRa Intertwined Gold Logo -->
        <button class="cursor-pointer group flex flex-col items-center focus:outline-none flex-shrink-0" onclick="switchCenterView('overview')" title="RescueTag Command Hub">
          <svg width="32" height="32" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="11.5" y="4.5" width="13" height="27" rx="6.5" transform="rotate(-45 18 18)" stroke="#C68B39" stroke-width="2.3"/>
            <rect x="11.5" y="4.5" width="13" height="27" rx="6.5" transform="rotate(45 18 18)" stroke="#C68B39" stroke-width="2.3"/>
          </svg>
          <span class="sec-tag text-[9px] font-mono font-bold tracking-widest text-[#9C9892] mt-1 uppercase">SEC-01</span>
        </button>

        <!-- Navigation Tactile Icons (Raised to upper position) -->
        <nav class="flex flex-col items-center gap-5">
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

          <!-- 5. Emergency Siren Audio Synthesizer Toggle -->
          <button id="sirenBtn" class="nav-btn" onclick="toggleAudioAlert()" title="Toggle Emergency Siren Synthesizer">
            <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">
              <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
              <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path>
            </svg>
          </button>
        </nav>
      </div>

      <!-- Bottom Cluster: Keluar / Logout to Access Terminal (Pinned at bottom) -->
      <div class="bottom-cluster flex flex-col items-center pb-1 flex-shrink-0">
        <button id="logoutBtn" class="nav-btn text-[#8E8B86] hover:text-[#EF4444] transition cursor-pointer" onclick="handleLogout()" title="Keluar / Logout ke Access Terminal">
          <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
            <polyline points="16 17 21 12 16 7"></polyline>
            <line x1="21" y1="12" x2="9" y2="12"></line>
          </svg>
        </button>
      </div>

    </aside>

    <!-- ================= 2. CENTER CONTENT (1fr, Warm Sand #FAF6F1) ================= -->
    <main class="px-4 py-5 sm:px-6 sm:py-6 lg:px-9 lg:py-8 flex flex-col justify-between h-auto lg:h-full overflow-y-auto relative">

      <!-- ================= VIEW 1: COMMAND OVERVIEW (DEFAULT) ================= -->
      <div id="view-overview" class="center-view flex flex-col justify-between h-full">

        <!-- Header -->
        <header class="flex items-center justify-between pb-1">
          <div>
            <h1 class="font-brand italic font-bold text-[30px] text-[#2D2B2A] tracking-normal leading-none">
              Rescue-Tag
            </h1>
            <p class="text-[11.5px] font-medium text-[#7B7874] mt-1.5 flex items-center gap-2">
              <span id="liveDate" class="font-sans">9 November 2026</span>
              <span class="text-[#D1CDC7]">&bull;</span>
              <span id="liveClock" class="font-mono text-[#4A4744]">12:45:00 UTC</span>
            </p>
          </div>

          <div class="flex items-center gap-3">
            <!-- Worker Selector Dropdown (Unified luxury frame, consistent for both workers) -->
            <div class="relative" id="workerDropdownContainer">
              <!-- Single Unified Dropdown Trigger Button with consistent frame -->
              <button type="button" id="workerDropdownBtn" onclick="toggleWorkerDropdown()" class="flex items-center gap-2.5 px-3.5 py-2 rounded-[12px] bg-white border border-[#E5DFD4] hover:border-[#2D2B2A] transition shadow-[0_2px_6px_rgba(0,0,0,0.03)] cursor-pointer text-[#2D2B2A] group" title="Pilih Pekerja Subterranean">
                <span id="selectedWorkerDot" class="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_6px_rgba(16,185,129,0.5)]"></span>
                <span id="selectedWorkerLabel" class="text-[12px] font-bold tracking-tight">Pekerja #02 (Agus)</span>
                <svg id="workerChevronIcon" class="transition-transform duration-200 ml-0.5" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#7B7874" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
              </button>

              <!-- Dropdown Options Menu (Consistent cards for both workers) -->
              <div id="workerDropdownMenu" class="hidden absolute top-full mt-2 right-0 w-[240px] bg-white rounded-2xl border border-[#E5DFD4] shadow-[0_14px_36px_rgba(45,43,42,0.14)] p-1.5 z-50">
                <div class="px-2.5 py-1.5 text-[9.5px] font-mono font-bold text-[#A6A29C] uppercase tracking-wider border-b border-[#F5F2EB] mb-1">
                  Pilih Pekerja Subterranean
                </div>

                <!-- Option 1: Worker #02 -->
                <button type="button" onclick="handleWorkerDropdownSelect(2)" id="workerOpt02" class="w-full flex items-center justify-between p-2 rounded-xl hover:bg-[#FAF6F1] transition text-left cursor-pointer group">
                  <div class="flex items-center gap-2.5">
                    <span id="workerOptDot02" class="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
                    <div>
                      <div class="text-[12px] font-bold text-[#2D2B2A] group-hover:text-emerald-700">Pekerja #02 (Agus Salim)</div>
                      <div id="workerOptSub02" class="text-[10px] text-[#7B7874] font-mono">Sektor 7 &bull; Lorong C-4</div>
                    </div>
                  </div>
                  <span id="workerOptCheck02" class="text-emerald-600 font-bold text-xs">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                  </span>
                </button>

                <!-- Option 2: Worker #01 -->
                <button type="button" onclick="handleWorkerDropdownSelect(1)" id="workerOpt01" class="w-full flex items-center justify-between p-2 rounded-xl hover:bg-[#FAF6F1] transition text-left cursor-pointer group">
                  <div class="flex items-center gap-2.5">
                    <span id="workerOptDot01" class="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
                    <div>
                      <div class="text-[12px] font-bold text-[#2D2B2A] group-hover:text-amber-700">Pekerja #01 (Bambang)</div>
                      <div id="workerOptSub01" class="text-[10px] text-[#7B7874] font-mono">Junction B-02 &bull; Relay Host</div>
                    </div>
                  </div>
                  <span id="workerOptCheck01" class="hidden text-amber-600 font-bold text-xs">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                  </span>
                </button>
              </div>
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
        <section class="vitals-grid grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4 lg:gap-5 my-1">
          
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
                <path id="sparkHeartFill" d="M 0 34 C 14 25, 28 24, 42 32 C 55 39, 66 41, 76 31 C 86 21, 95 16, 110 18 C 125 20, 142 12, 160 6 L 160 52 L 0 52 Z" fill="url(#heartGrad)"/>
                <path id="sparkHeartLine" d="M 0 34 C 14 25, 28 24, 42 32 C 55 39, 66 41, 76 31 C 86 21, 95 16, 110 18 C 125 20, 142 12, 160 6" fill="none" stroke="#DE6D72" stroke-width="1.6" stroke-linecap="round"/>
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
                <path id="sparkSpo2Fill" d="M 0 32 C 12 38, 26 39, 38 29 C 50 18, 60 14, 76 17 C 90 19, 102 22, 114 14 C 128 5, 144 4, 160 28 L 160 52 L 0 52 Z" fill="url(#bpGrad)"/>
                <path id="sparkSpo2Line" d="M 0 32 C 12 38, 26 39, 38 29 C 50 18, 60 14, 76 17 C 90 19, 102 22, 114 14 C 128 5, 144 4, 160 28" fill="none" stroke="#53ACC0" stroke-width="1.6" stroke-linecap="round"/>
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
                <path id="sparkTempFill" d="M 0 38 C 16 28, 30 22, 46 28 C 60 33, 74 34, 88 22 C 100 11, 108 6, 120 12 C 132 18, 140 31, 160 24 L 160 52 L 0 52 Z" fill="url(#sugarGrad)"/>
                <path id="sparkTempLine" d="M 0 38 C 16 28, 30 22, 46 28 C 60 33, 74 34, 88 22 C 100 11, 108 6, 120 12 C 132 18, 140 31, 160 24" fill="none" stroke="#E59A43" stroke-width="1.6" stroke-linecap="round"/>
              </svg>
            </div>
          </div>

        </section>

        <!-- ROW 2: Kinematics & TinyML Activity Stream (Expanded Flex Layout) -->
        <section class="kinematics-card metric-card p-4 sm:p-5 lg:px-6 lg:py-5 flex flex-col justify-between flex-1 min-h-[360px] mt-3 sm:mt-4">
          <!-- Card Header -->
          <div class="flex items-center justify-between gap-4">
            <div class="flex items-center gap-3 min-w-0">
              <h2 class="text-[15.5px] font-bold text-[#2D2B2A] whitespace-nowrap">Kinematics &amp; TinyML Activity Stream</h2>
              <span id="liveAccelPill" class="px-2.5 py-1 rounded-[7px] bg-[#EFE9E0] text-[#3E3C39] font-mono text-[10.5px] font-bold whitespace-nowrap flex-shrink-0">
                1.02g &bull; Diam / Normal
              </span>
            </div>
            <button id="monthToggleBtn" onclick="cycleShift()" class="flex-shrink-0 flex items-center gap-2 px-3 py-1.5 rounded-[10px] bg-white border border-[#EAE6E1] hover:border-[#2D2B2A] text-[11px] font-semibold text-[#4A4744] hover:bg-[#FAF6F1] transition shadow-2xs">
              <span id="shiftLabel" class="whitespace-nowrap">Live Stream // Sektor 7</span>
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
            <div class="flex-1 relative flex flex-col justify-between pb-7 pt-3 min-w-[340px] sm:min-w-0">
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

          <!-- Legend -->
          <div class="flex items-center gap-7 pt-1">
            <div class="flex items-center gap-2.5">
              <span class="w-2.5 h-2.5 rounded-full bg-[#DA7468]"></span>
              <span class="text-[10.5px] font-semibold text-[#6E6B67]">G-Force Shock (&gt;3.0g)</span>
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
        </section>

      </div>

      <!-- ================= VIEW 2: SUBTERRANEAN WORKER FLEET ROSTER & LORA DIAGNOSTICS ================= -->
      <div id="view-fleet-roster" class="center-view hidden flex flex-col justify-between h-auto lg:h-full">
        <!-- Header -->
        <header class="flex flex-wrap items-center justify-between gap-2.5 pb-3 border-b border-[#F0ECE6]">
          <div>
            <h1 class="text-[20px] font-bold text-[#2D2B2A] tracking-tight">
              Subterranean Worker Fleet Roster &amp; LoRa Diagnostics
            </h1>
            <p class="text-[12px] font-medium text-[#7B7874] mt-0.5">
              Real-Time Telemetry &amp; 1-Hop Forwarding State for Both Personnel
            </p>
          </div>
          <button onclick="switchCenterView('overview')" class="px-3.5 py-1.5 rounded-[10px] bg-[#2C2A2A] text-white text-[11.5px] font-semibold hover:bg-[#1C1A1A] transition cursor-pointer">
            &larr; Back to Overview
          </button>
        </header>

        <!-- Main Roster Cards (Clean, spacious, un-cramped - fixes Gambar 2) -->
        <div class="my-3 flex-1 flex flex-col justify-between space-y-3 overflow-y-auto">
          
          <!-- Card 1: Worker #02 (Agus Salim) -->
          <div id="rosterCard02" class="metric-card p-4 transition">
            <div class="flex items-center justify-between border-b border-[#F5F2EB] pb-2.5 mb-2.5">
              <div class="flex items-center gap-2.5">
                <span id="rosterDot02" class="w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"></span>
                <div>
                  <div class="text-[14px] font-bold text-[#2D2B2A]">Pekerja #02 (Agus Salim)</div>
                  <div id="rosterSector02" class="text-[10.5px] text-[#7B7874] font-mono">Jam Tangan #02 &bull; Sektor 7 (Lorong C-4)</div>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <span id="rosterTriage02" class="px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200 font-bold text-[10.5px] whitespace-nowrap">
                  HIJAU - Minor (Aman)
                </span>
              </div>
            </div>

            <!-- Vitals Grid -->
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-2.5 mb-2.5">
              <div class="bg-[#FAF6F1] p-2.5 rounded-xl border border-[#F0ECE6]">
                <div class="text-[9.5px] font-mono text-[#7B7874] uppercase tracking-wider">Heart Rate</div>
                <div id="rosterHR02" class="text-sm font-bold font-mono text-emerald-700 mt-0.5">75 BPM</div>
                <div id="rosterHRSub02" class="text-[9.5px] text-[#A6A29C]">Normal (60-100)</div>
              </div>
              <div class="bg-[#FAF6F1] p-2.5 rounded-xl border border-[#F0ECE6]">
                <div class="text-[9.5px] font-mono text-[#7B7874] uppercase tracking-wider">Blood O2 (SpO2)</div>
                <div id="rosterSpO2_02" class="text-sm font-bold font-mono text-emerald-700 mt-0.5">98%</div>
                <div id="rosterSpO2Sub02" class="text-[9.5px] text-[#A6A29C]">Optimal (&ge;95%)</div>
              </div>
              <div class="bg-[#FAF6F1] p-2.5 rounded-xl border border-[#F0ECE6]">
                <div class="text-[9.5px] font-mono text-[#7B7874] uppercase tracking-wider">Skin IR Temp</div>
                <div id="rosterTemp02" class="text-sm font-bold font-mono text-emerald-700 mt-0.5">36.5&deg;C</div>
                <div id="rosterTempSub02" class="text-[9.5px] text-[#A6A29C]">Normotermia</div>
              </div>
            </div>

            <!-- Bottom Row: Activity, Route, and Actions -->
            <div class="flex flex-wrap items-center justify-between gap-2 text-xs">
              <div class="flex flex-wrap items-center gap-2">
                <span id="rosterActivity02" class="px-2.5 py-0.5 rounded-lg bg-emerald-50 text-emerald-800 border border-emerald-200 text-[10.5px]">
                  Diam / Istirahat Normal
                </span>
                <span id="rosterRoute02" class="px-2.5 py-0.5 rounded-lg bg-blue-50 text-blue-800 border border-blue-200 text-[10.5px] font-mono">
                  1-Hop Relay via Jam #01
                </span>
              </div>
              <div class="flex items-center gap-1.5">
                <button onclick="focusFromRoster(2)" class="px-2.5 py-1 rounded-[8px] bg-[#EFE9E0] hover:bg-[#E5DFD4] text-[10.5px] font-mono transition text-[#2D2B2A] font-bold cursor-pointer">
                  Focus Map
                </button>
                <button onclick="runDiagWatch(2)" class="px-2.5 py-1 rounded-[8px] bg-amber-50 hover:bg-amber-100 text-amber-900 border border-amber-200 text-[10.5px] font-mono transition font-bold cursor-pointer">
                  Run Diag
                </button>
              </div>
            </div>
          </div>

          <!-- Card 2: Worker #01 (Bambang Relay Host) -->
          <div id="rosterCard01" class="metric-card p-4 transition">
            <div class="flex items-center justify-between border-b border-[#F5F2EB] pb-2.5 mb-2.5">
              <div class="flex items-center gap-2.5">
                <span id="rosterDot01" class="w-2.5 h-2.5 rounded-full bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.5)]"></span>
                <div>
                  <div class="text-[14px] font-bold text-[#2D2B2A]">Pekerja #01 (Bambang)</div>
                  <div id="rosterSector01" class="text-[10.5px] text-[#7B7874] font-mono">Jam Tangan #01 &bull; Junction B-02 (Shaft Poros)</div>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <span id="rosterTriage01" class="px-2.5 py-1 rounded-full bg-amber-50 text-amber-800 border border-amber-200 font-bold text-[10.5px] whitespace-nowrap">
                  KUNING - Delayed
                </span>
              </div>
            </div>

            <!-- Vitals Grid -->
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-2.5 mb-2.5">
              <div class="bg-[#FAF6F1] p-2.5 rounded-xl border border-[#F0ECE6]">
                <div class="text-[9.5px] font-mono text-[#7B7874] uppercase tracking-wider">Heart Rate</div>
                <div id="rosterHR01" class="text-sm font-bold font-mono text-amber-700 mt-0.5">106 BPM</div>
                <div id="rosterHRSub01" class="text-[9.5px] text-[#A6A29C]">Takikardia Ringan</div>
              </div>
              <div class="bg-[#FAF6F1] p-2.5 rounded-xl border border-[#F0ECE6]">
                <div class="text-[9.5px] font-mono text-[#7B7874] uppercase tracking-wider">Blood O2 (SpO2)</div>
                <div id="rosterSpO2_01" class="text-sm font-bold font-mono text-amber-700 mt-0.5">93%</div>
                <div id="rosterSpO2Sub01" class="text-[9.5px] text-[#A6A29C]">Hipoksia Ringan</div>
              </div>
              <div class="bg-[#FAF6F1] p-2.5 rounded-xl border border-[#F0ECE6]">
                <div class="text-[9.5px] font-mono text-[#7B7874] uppercase tracking-wider">Skin IR Temp</div>
                <div id="rosterTemp01" class="text-sm font-bold font-mono text-amber-700 mt-0.5">37.6&deg;C</div>
                <div id="rosterTempSub01" class="text-[9.5px] text-[#A6A29C]">Hipertermia Ringan</div>
              </div>
            </div>

            <!-- Bottom Row: Activity, Route, and Actions -->
            <div class="flex flex-wrap items-center justify-between gap-2 text-xs">
              <div class="flex flex-wrap items-center gap-2">
                <span id="rosterActivity01" class="px-2.5 py-0.5 rounded-lg bg-amber-50 text-amber-800 border border-amber-200 text-[10.5px]">
                  Tremor / Kelelahan Ringan
                </span>
                <span id="rosterRoute01" class="px-2.5 py-0.5 rounded-lg bg-orange-50 text-orange-800 border border-orange-200 text-[10.5px] font-mono">
                  Direct + Relay Host (Hop 1)
                </span>
              </div>
              <div class="flex items-center gap-1.5">
                <button onclick="focusFromRoster(1)" class="px-2.5 py-1 rounded-[8px] bg-[#EFE9E0] hover:bg-[#E5DFD4] text-[10.5px] font-mono transition text-[#2D2B2A] font-bold cursor-pointer">
                  Focus Map
                </button>
                <button onclick="runDiagWatch(1)" class="px-2.5 py-1 rounded-[8px] bg-amber-50 hover:bg-amber-100 text-amber-900 border border-amber-200 text-[10.5px] font-mono transition font-bold cursor-pointer">
                  Run Diag
                </button>
              </div>
            </div>
          </div>

          <!-- Bottom Battery & Signal Diagnostics Cards -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div class="p-3 bg-white rounded-xl border border-[#F0ECE6] shadow-sm">
              <span class="text-[9.5px] text-[#7B7874] font-mono block">RF LINK QUALITY</span>
              <span id="rosterRfQuality" class="font-bold text-xs text-[#2D2B2A] font-mono">RSSI -68 dBm // SNR +8.5 dB</span>
            </div>
            <div class="p-3 bg-white rounded-xl border border-[#F0ECE6] shadow-sm">
              <span class="text-[9.5px] text-[#7B7874] font-mono block">JAM TANGAN #01 NODE</span>
              <span id="rosterNode01Status" class="font-bold text-xs text-amber-700 font-mono">81% (4.12V LiPo) &bull; Relay Active</span>
            </div>
            <div class="p-3 bg-white rounded-xl border border-[#F0ECE6] shadow-sm">
              <span class="text-[9.5px] text-[#7B7874] font-mono block">JAM TANGAN #02 NODE</span>
              <span id="rosterNode02Status" class="font-bold text-xs text-emerald-700 font-mono">78% (4.06V LiPo) &bull; P2P Connected</span>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="flex items-center justify-between text-xs text-[#7B7874] font-mono pt-2 border-t border-[#F0ECE6]">
          <span>Sub-GHz 433.05 MHz Mesh &bull; CRC-16 Hardware Checksum</span>
          <div class="flex gap-2">
            <button onclick="testSimSOS()" class="px-3 py-1 rounded-[8px] bg-red-100 text-red-800 font-bold hover:bg-red-200 transition cursor-pointer">
              Simulate SOS Incident
            </button>
            <button onclick="testSimNormal()" class="px-3 py-1 rounded-[8px] bg-emerald-100 text-emerald-800 font-bold hover:bg-emerald-200 transition cursor-pointer">
              Simulate Normal State
            </button>
          </div>
        </div>
      </div>

      <!-- ================= VIEW 3: SUBTERRANEAN SPATIAL MINE NAVIGATION (GIS MAP) ================= -->
      <div id="view-gis-map" class="center-view hidden flex flex-col justify-between h-auto lg:h-full">
        <!-- Header -->
        <header class="flex flex-wrap items-center justify-between gap-2.5 pb-3 border-b border-[#F0ECE6]">
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
          <div id="leafletMapContainer" class="w-full flex-1 rounded-xl bg-[#E8E4DE] overflow-hidden min-h-[300px] sm:min-h-[440px]"></div>
        </div>

        <!-- GIS Map Footer Bar -->
        <div class="flex flex-wrap items-center justify-between gap-2.5 text-xs font-mono pt-1">
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
      <div id="view-audit-trail" class="center-view hidden flex flex-col justify-between h-auto lg:h-full">
        <!-- Header -->
        <header class="flex flex-wrap items-center justify-between gap-2.5 pb-3 border-b border-[#F0ECE6]">
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
        <header class="flex items-center justify-between pb-2.5 border-b border-[#F0ECE6]">
          <div>
            <div class="flex items-center gap-2.5">
              <h1 class="text-[20px] font-bold text-[#2D2B2A] tracking-tight">RescueTag Wearable Smartwatch</h1>
              <span class="px-2 py-0.5 rounded-full bg-[#E8F5E9] text-[#2E7D32] border border-[#C8E6C9] text-[10px] font-mono font-bold tracking-wider uppercase">
                NODE-01 FIELD READY
              </span>
            </div>
            <p class="text-[11.5px] font-medium text-[#7B7874] mt-0.5">
              Subterranean Miner Wearable Unit &bull; Dual-Sensor Biometrics &bull; LoRa Sub-GHz P2P Mesh
            </p>
          </div>
          <button onclick="switchCenterView('overview')" class="px-3.5 py-1.5 rounded-[10px] bg-[#2C2A2A] text-white text-[11.5px] font-semibold hover:bg-[#1C1A1A] transition shadow-sm cursor-pointer">
            &larr; Back to Overview
          </button>
        </header>

        <!-- Hardware Full Specification Grid (Rich, Dense & Complete) -->
        <div class="my-2.5 flex-1 flex flex-col justify-between space-y-3 overflow-y-auto pr-1">
          
          <!-- Top Row: Photo Showcase + 4 System Architecture Cards -->
          <div class="grid grid-cols-1 md:grid-cols-12 gap-3.5 items-stretch">
            
            <!-- Left: High-Res Hardware Photo Showcase (5 cols) -->
            <div class="md:col-span-5 metric-card p-3.5 flex flex-col justify-between">
              <div class="bg-[#FAF6F1] rounded-2xl p-3 border border-[#F0ECE6] relative flex flex-col items-center justify-center">
                <span class="absolute top-2 left-2 text-[9px] font-mono font-bold px-2 py-0.5 rounded-full bg-white border border-[#E5DFD4] text-[#7B7874]">
                  IP68 SEALED
                </span>
                <span class="absolute top-2 right-2 text-[9px] font-mono font-bold px-2 py-0.5 rounded-full bg-[#EFE9E0] text-[#C68B39]">
                  433.05 MHz
                </span>
                <img id="hardwarePhotoImg" src="BASE64_IMAGE_PLACEHOLDER" alt="RescueTag Wearable Smartwatch" class="max-h-[175px] object-contain drop-shadow-md my-1" />
                <span class="text-[10px] font-mono text-[#7B7874] mt-1">
                  0.96" Monochrome OLED &bull; Tactical SOS Push
                </span>
              </div>

              <!-- Quick Physical Dimensions Matrix -->
              <div class="grid grid-cols-2 gap-2 mt-2.5 text-center font-mono">
                <div class="p-1.5 bg-[#FAF6F1] rounded-lg border border-[#F0ECE6]">
                  <span class="text-[9px] text-[#A6A29C] block">DIMENSIONS</span>
                  <span class="text-[11px] font-bold text-[#2D2B2A]">48 &times; 42 &times; 16 mm</span>
                </div>
                <div class="p-1.5 bg-[#FAF6F1] rounded-lg border border-[#F0ECE6]">
                  <span class="text-[9px] text-[#A6A29C] block">MASS WEIGHT</span>
                  <span class="text-[11px] font-bold text-[#2D2B2A]">68g (w/ Strap)</span>
                </div>
                <div class="p-1.5 bg-[#FAF6F1] rounded-lg border border-[#F0ECE6]">
                  <span class="text-[9px] text-[#A6A29C] block">HOUSING</span>
                  <span class="text-[11px] font-bold text-[#2D2B2A]">ABS High-Impact</span>
                </div>
                <div class="p-1.5 bg-[#FAF6F1] rounded-lg border border-[#F0ECE6]">
                  <span class="text-[9px] text-[#A6A29C] block">SUBMERSIBLE</span>
                  <span class="text-[11px] font-bold text-emerald-700">1.5m / 30 Mins</span>
                </div>
              </div>
            </div>

            <!-- Right: System Architecture Bento (7 cols) -->
            <div class="md:col-span-7 flex flex-col justify-between space-y-2">
              
              <!-- Card 1: Processing & TinyML -->
              <div class="metric-card p-3 flex items-start gap-3">
                <div class="w-8 h-8 rounded-lg bg-[#FAF6F1] border border-[#F0ECE6] flex items-center justify-center shrink-0 text-[#2D2B2A] font-bold text-xs font-mono">
                  MCU
                </div>
                <div class="flex-1 text-xs">
                  <div class="flex items-center justify-between">
                    <span class="font-bold text-[#2D2B2A]">STM32L431 ARM Cortex-M4 @ 80 MHz</span>
                    <span class="text-[9.5px] font-mono px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-800 border border-emerald-200">18ms TinyML</span>
                  </div>
                  <p class="text-[11px] text-[#7B7874] mt-0.5">
                    On-device Decision Tree classifier for zero-latency subterranean shock &amp; fall triage classification.
                  </p>
                </div>
              </div>

              <!-- Card 2: Optical Biometrics -->
              <div class="metric-card p-3 flex items-start gap-3">
                <div class="w-8 h-8 rounded-lg bg-[#FAF6F1] border border-[#F0ECE6] flex items-center justify-center shrink-0 text-[#E59A43] font-bold text-xs font-mono">
                  PPG
                </div>
                <div class="flex-1 text-xs">
                  <div class="flex items-center justify-between">
                    <span class="font-bold text-[#2D2B2A]">MAX30102 Optical Biometric Array</span>
                    <span class="text-[9.5px] font-mono px-1.5 py-0.5 rounded bg-blue-50 text-blue-800 border border-blue-200">660nm / 880nm</span>
                  </div>
                  <p class="text-[11px] text-[#7B7874] mt-0.5">
                    Dual-wavelength arterial reflectance PPG delivering continuous Heart Rate (30-220 BPM) &amp; SpO2 saturation.
                  </p>
                </div>
              </div>

              <!-- Card 3: IR Temp & IMU -->
              <div class="metric-card p-3 flex items-start gap-3">
                <div class="w-8 h-8 rounded-lg bg-[#FAF6F1] border border-[#F0ECE6] flex items-center justify-center shrink-0 text-red-600 font-bold text-xs font-mono">
                  TEMP
                </div>
                <div class="flex-1 text-xs">
                  <div class="flex items-center justify-between">
                    <span class="font-bold text-[#2D2B2A]">MLX90614 Contactless IR + BMI160 6-DOF IMU</span>
                    <span class="text-[9.5px] font-mono px-1.5 py-0.5 rounded bg-amber-50 text-amber-800 border border-amber-200">&plusmn;0.2&deg;C &bull; &plusmn;16g</span>
                  </div>
                  <p class="text-[11px] text-[#7B7874] mt-0.5">
                    Medical-grade body core temperature tracking combined with 6-axis acceleration shock wave detection.
                  </p>
                </div>
              </div>

              <!-- Card 4: LoRa RF Mesh Link -->
              <div class="metric-card p-3 flex items-start gap-3">
                <div class="w-8 h-8 rounded-lg bg-[#FAF6F1] border border-[#F0ECE6] flex items-center justify-center shrink-0 text-[#C68B39] font-bold text-xs font-mono">
                  LoRa
                </div>
                <div class="flex-1 text-xs">
                  <div class="flex items-center justify-between">
                    <span class="font-bold text-[#2D2B2A]">SX1278 Sub-GHz 433.05 MHz Mesh</span>
                    <span class="text-[9.5px] font-mono px-1.5 py-0.5 rounded bg-purple-50 text-purple-800 border border-purple-200">1-Hop P2P</span>
                  </div>
                  <p class="text-[11px] text-[#7B7874] mt-0.5">
                    Rock-penetrating Sub-GHz RF telemetry with autonomous peer relaying to surface command basecamp.
                  </p>
                </div>
              </div>

            </div>
          </div>

          <!-- Middle Row: Subterranean Environmental Durability (3 Cards) -->
          <div class="grid grid-cols-3 gap-3">
            <div class="metric-card p-3 bg-white">
              <div class="flex items-center gap-2 mb-1">
                <span class="w-2 h-2 rounded-full bg-blue-500"></span>
                <span class="text-[11px] font-bold text-[#2D2B2A]">Hermetic Sealing</span>
              </div>
              <p class="text-[10.5px] text-[#7B7874]">
                IP68 dust-tight gasket protects against subterranean coal dust, mud, and water ingress up to 1.5m.
              </p>
            </div>
            <div class="metric-card p-3 bg-white">
              <div class="flex items-center gap-2 mb-1">
                <span class="w-2 h-2 rounded-full bg-amber-500"></span>
                <span class="text-[11px] font-bold text-[#2D2B2A]">Shock Resistance</span>
              </div>
              <p class="text-[10.5px] text-[#7B7874]">
                Engineered to survive 2-meter freefall impact onto basalt rock; internal damping absorbs severe shockwaves.
              </p>
            </div>
            <div class="metric-card p-3 bg-white">
              <div class="flex items-center gap-2 mb-1">
                <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
                <span class="text-[11px] font-bold text-[#2D2B2A]">Power Autonomy</span>
              </div>
              <p class="text-[10.5px] text-[#7B7874]">
                850mAh LiPo delivers 18 hours full continuous mesh duty cycle and 72 hours emergency low-power beacon.
              </p>
            </div>
          </div>

          <!-- Bottom Row: Interactive Diagnostics & Hardware Console -->
          <div class="metric-card p-3 bg-white space-y-2">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                <span class="text-[11px] font-bold font-mono text-[#2D2B2A] uppercase">Node Diagnostic Self-Test Console</span>
              </div>
              <div class="flex items-center gap-1.5 font-mono text-[10px]">
                <button onclick="runHwDiag('oled')" class="px-2.5 py-1 rounded bg-[#FAF6F1] border border-[#E5DFD4] hover:bg-[#EFE9E0] font-bold text-[#2D2B2A] transition cursor-pointer">
                  Test OLED
                </button>
                <button onclick="runHwDiag('rf')" class="px-2.5 py-1 rounded bg-[#FAF6F1] border border-[#E5DFD4] hover:bg-[#EFE9E0] font-bold text-[#2D2B2A] transition cursor-pointer">
                  Ping SX1278
                </button>
                <button onclick="runHwDiag('imu')" class="px-2.5 py-1 rounded bg-[#FAF6F1] border border-[#E5DFD4] hover:bg-[#EFE9E0] font-bold text-[#2D2B2A] transition cursor-pointer">
                  Test IMU Shock
                </button>
                <button onclick="runHwDiag('temp')" class="px-2.5 py-1 rounded bg-[#FAF6F1] border border-[#E5DFD4] hover:bg-[#EFE9E0] font-bold text-[#2D2B2A] transition cursor-pointer">
                  Read IR Temp
                </button>
              </div>
            </div>
            <!-- Monospace Terminal Log Box -->
            <div id="hwDiagConsole" class="bg-[#2D2B2A] text-[#A6E3A1] rounded-xl p-2 font-mono text-[10.5px] leading-relaxed border border-[#3E3A39] overflow-x-auto whitespace-nowrap">
              &gt; [NODE-01] Hardware diagnostics online. Ready for command dispatch.
            </div>
          </div>

        </div>

        <!-- Footer -->
        <div class="flex items-center justify-between text-xs text-[#7B7874] font-mono pt-2 border-t border-[#F0ECE6]">
          <span>Field Testing: Tambang Batubara Bawah Tanah &bull; 0.96" Monochrome Live OLED</span>
          <button onclick="testSimSOS()" class="px-3 py-1 rounded bg-amber-100 text-amber-900 font-bold hover:bg-amber-200 transition cursor-pointer">
            Test Shock Waveform
          </button>
        </div>
      </div>
    </main>

    <!-- ================= 3. RIGHT DARK TACTICAL PANEL (414px, #2D2B2B) ================= -->
    <aside class="right-tactical-panel bg-[#2D2B2B] h-full rounded-l-[34px] px-5 py-6 sm:px-7 sm:py-7 lg:px-8 lg:py-8 flex flex-col justify-between text-white relative overflow-hidden select-none border-l border-[#3D3A3A]">

      <!-- TOP SECTION: START Triage Risk Simulator -->
      <div>
        <!-- Header -->
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-[17px] font-semibold text-[#F4F1EA] tracking-tight">START Triage Risk Simulator</h2>
            <p class="text-[11px] font-medium text-[#B8B4B0] mt-0.5">Simple Triage and Rapid Treatment</p>
          </div>
          <button id="simModeToggleBtn" onclick="toggleSimMode()" class="flex items-center gap-2 px-3 py-1 rounded-[10px] border border-[#6E6C6C] text-[11px] font-medium text-[#D1CECA] hover:border-[#9E9C9C] transition font-mono cursor-pointer" title="Klik untuk ganti Mode Live MQTT / Manual Simulator">
            <span id="mqttDot" class="w-2 h-2 rounded-full bg-amber-400"></span>
            <span id="simModeLabel">Live MQTT</span>
          </button>
        </div>

        <!-- Sliders & Result Grid -->
        <div class="triage-simulator-grid grid grid-cols-1 sm:grid-cols-[152px_1fr] gap-3.5 mt-4 sm:mt-5">
          
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
        
        <div class="sensor-ergo-grid grid grid-cols-1 sm:grid-cols-[165px_1fr] h-full items-start gap-3 sm:gap-4 relative">
          
          <!-- Left Column: Info + 3 Stacked White Sensor Cards -->
          <div class="flex flex-col justify-between h-full z-10 pr-1">
            <div>
              <h2 class="text-[17px] font-semibold text-[#F4F1EA] tracking-tight">Sensor Ergonomics</h2>
              <p class="text-[11.5px] font-medium text-[#B8B4B0] mt-0.5">Hardware Anatomical Placement</p>
              <div id="ergoNodeBadge" class="mt-2.5 inline-block px-3 py-1 rounded-[8px] bg-[#494747] text-[#DFDCD8] text-[10.5px] font-mono">
                SEC-01 // NODE-02
              </div>
            </div>

            <!-- 3 Stacked White Measurement Cards -->
            <div class="sensor-cards-stack flex flex-col gap-2.5 sm:gap-3 mb-1 mt-2 sm:mt-3">
              
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

  </div>

  <!-- ================= JAVASCRIPT LOGIC ENGINE ================= -->
  <script>
    // =============================================================
    // ACCESS TERMINAL LOGIN & AUTH LOGIC
    // =============================================================
    let activeOperatorRole = 'SAR Commander';

    function selectLoginRole(role, btn) {
      document.querySelectorAll('.role-btn').forEach(b => {
        b.classList.remove('active');
        b.classList.add('text-[#7B7874]');
      });
      btn.classList.add('active');
      btn.classList.remove('text-[#7B7874]');
      activeOperatorRole = role;
    }

    function handleLogin(e) {
      if (e) e.preventDefault();
      const loginPage = document.getElementById('page-login');
      const dashPage = document.getElementById('page-dashboard');
      if (loginPage) loginPage.classList.add('hidden');
      if (dashPage) dashPage.classList.remove('hidden');
      
      // Invalidate Leaflet map size on display
      if (window.leafletMap) {
        setTimeout(() => { window.leafletMap.invalidateSize(); }, 200);
      }
    }

    function handleLogout() {
      const loginPage = document.getElementById('page-login');
      const dashPage = document.getElementById('page-dashboard');
      if (loginPage) loginPage.classList.remove('hidden');
      if (dashPage) dashPage.classList.add('hidden');
    }

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
    let mqttClient = null;
    let mqttConnected = false;
    let mqttPacketCount = 0;
    let lastMqttRxTime = null;
    let hasLoggedFirstLiveRx = false;

    // In-memory Audit Trail Log Data for Excel Export
    const auditLogsData = [];

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

    function makeSeedBars(baseArr) {
      return baseArr.map((seg, i) => ({
        red: seg[0],
        teal: seg[1],
        ochre: seg[2],
        g: ((seg[0] * 0.04) + (seg[1] * 0.02) + (seg[2] * 0.015)).toFixed(2),
        label: 'T+' + (i * 10) + 'm'
      }));
    }

    // Both workers initial state + rolling live buffers
    const workers = {
      1: {
        id: 'WRK-001',
        tagId: 'RESCUE-TAG-01',
        name: 'Bambang (Relay Host)',
        role: 'SAR Relawan & LoRa Relay Host',
        sector: 'Junction Poros Shaft B-02',
        lat: -8.2465,
        lng: 113.6965,
        hr: 106,
        spo2: 93,
        temp: 37.6,
        accel: 1.45,
        activity: 'Tremor / Kelelahan Ringan',
        route: 'Direct + Relay Host (Hop 1)',
        rssi: -65,
        isRelayed: false,
        triageCode: 1, // KUNING
        triageLabel: 'KUNING - Delayed',
        isEmergency: false,
        rxCount: 0,
        lastRxAt: null,
        lastLoggedTriage: null,
        lastLoggedRoute: null,
        lastAlertTs: 0,
        hrHist: [96, 98, 102, 100, 104, 108, 105, 103, 107, 109, 105, 106],
        spo2Hist: [96, 95, 95, 94, 94, 93, 94, 93, 93, 94, 93, 93],
        tempHist: [37.1, 37.2, 37.3, 37.3, 37.4, 37.5, 37.5, 37.6, 37.5, 37.6, 37.6, 37.6],
        kinematicsHist: makeSeedBars(febData)
      },
      2: {
        id: 'WRK-002',
        tagId: 'RESCUE-TAG-02',
        name: 'Agus Salim (Active Miner)',
        role: 'Operator Tambang Batubara',
        sector: 'Sektor 7 (Lorong C-4)',
        lat: -8.2498,
        lng: 113.7012,
        hr: 75,
        spo2: 98,
        temp: 36.5,
        accel: 1.02,
        activity: 'Diam / Istirahat Normal',
        route: '1-Hop Relay via Jam #01',
        rssi: -68,
        isRelayed: true,
        triageCode: 0, // HIJAU
        triageLabel: 'HIJAU - Minor (Aman)',
        isEmergency: false,
        rxCount: 0,
        lastRxAt: null,
        lastLoggedTriage: null,
        lastLoggedRoute: null,
        lastAlertTs: 0,
        hrHist: [72, 74, 73, 75, 76, 74, 73, 75, 77, 76, 74, 75],
        spo2Hist: [98, 98, 99, 98, 98, 97, 98, 99, 98, 98, 98, 98],
        tempHist: [36.4, 36.4, 36.5, 36.5, 36.6, 36.5, 36.4, 36.5, 36.6, 36.5, 36.5, 36.5],
        kinematicsHist: makeSeedBars(janData)
      }
    };

    const TRIAGE_THEMES = {
      0: {
        short: 'HIJAU',
        dotClass: 'w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_6px_rgba(16,185,129,0.5)]',
        optDotClass: 'w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-[0_0_6px_rgba(16,185,129,0.5)]',
        pillClass: 'px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200 font-bold text-[10.5px] whitespace-nowrap',
        actClass: 'px-2.5 py-0.5 rounded-lg bg-emerald-50 text-emerald-800 border border-emerald-200 text-[10.5px]',
        textClass: 'text-sm font-bold font-mono text-emerald-700 mt-0.5',
        hex: '#059669',
        defaultLabel: 'HIJAU - Minor (Aman)'
      },
      1: {
        short: 'KUNING',
        dotClass: 'w-2 h-2 rounded-full bg-amber-500 shadow-[0_0_6px_rgba(245,158,11,0.5)]',
        optDotClass: 'w-2.5 h-2.5 rounded-full bg-amber-500 shadow-[0_0_6px_rgba(245,158,11,0.5)]',
        pillClass: 'px-2.5 py-1 rounded-full bg-amber-50 text-amber-800 border border-amber-200 font-bold text-[10.5px] whitespace-nowrap',
        actClass: 'px-2.5 py-0.5 rounded-lg bg-amber-50 text-amber-800 border border-amber-200 text-[10.5px]',
        textClass: 'text-sm font-bold font-mono text-amber-700 mt-0.5',
        hex: '#D97706',
        defaultLabel: 'KUNING - Kerja Aktif'
      },
      2: {
        short: 'ORANYE',
        dotClass: 'w-2 h-2 rounded-full bg-orange-500 shadow-[0_0_6px_rgba(249,115,22,0.55)]',
        optDotClass: 'w-2.5 h-2.5 rounded-full bg-orange-500 shadow-[0_0_6px_rgba(249,115,22,0.55)]',
        pillClass: 'px-2.5 py-1 rounded-full bg-orange-50 text-orange-800 border border-orange-200 font-bold text-[10.5px] whitespace-nowrap',
        actClass: 'px-2.5 py-0.5 rounded-lg bg-orange-50 text-orange-800 border border-orange-200 text-[10.5px]',
        textClass: 'text-sm font-bold font-mono text-orange-700 mt-0.5',
        hex: '#EA580C',
        defaultLabel: 'ORANYE - Waspada Dini'
      },
      3: {
        short: 'MERAH',
        dotClass: 'w-2 h-2 rounded-full bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.85)] animate-pulse',
        optDotClass: 'w-2.5 h-2.5 rounded-full bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.85)] animate-pulse',
        pillClass: 'px-2.5 py-1 rounded-full bg-red-100 text-red-900 border border-red-300 font-bold text-[10.5px] whitespace-nowrap animate-pulse',
        actClass: 'px-2.5 py-0.5 rounded-lg bg-red-100 text-red-900 border border-red-300 text-[10.5px] font-bold',
        textClass: 'text-sm font-bold font-mono text-red-700 mt-0.5',
        hex: '#DC2626',
        defaultLabel: 'MERAH - Darurat SOS'
      },
      4: {
        short: 'STANDBY',
        dotClass: 'w-2 h-2 rounded-full bg-slate-400',
        optDotClass: 'w-2.5 h-2.5 rounded-full bg-slate-400',
        pillClass: 'px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 border border-slate-300 font-bold text-[10.5px] whitespace-nowrap',
        actClass: 'px-2.5 py-0.5 rounded-lg bg-slate-100 text-slate-700 border border-slate-300 text-[10.5px]',
        textClass: 'text-sm font-bold font-mono text-slate-600 mt-0.5',
        hex: '#64748B',
        defaultLabel: 'STANDBY - Jam Dilepas'
      }
    };

    function getTriageTheme(code) {
      return TRIAGE_THEMES[code] || TRIAGE_THEMES[0];
    }

    function getVitalMeta(w) {
      let hrSub = 'Normal (60-100)';
      let hrBadge = 'Normal';
      let hrClass = 'inline-block px-2.5 py-0.5 rounded-[5px] bg-[#E8F8F0] text-[#1D6A4E] text-[10.5px] font-bold';
      if (w.triageCode === 4 || w.hr <= 0) {
        hrSub = w.triageCode === 4 ? 'Jam Dilepas' : 'Mengukur nadi...';
        hrBadge = w.triageCode === 4 ? 'Standby' : 'Mengukur...';
        hrClass = 'inline-block px-2.5 py-0.5 rounded-[5px] bg-slate-100 text-slate-600 text-[10.5px] font-bold';
      } else if (w.hr > 120) {
        hrSub = 'Takikardia';
        hrBadge = 'Takikardia';
        hrClass = 'inline-block px-2.5 py-0.5 rounded-[5px] bg-[#FBE7E8] text-[#DE6D72] text-[10.5px] font-bold';
      } else if (w.hr > 100) {
        hrSub = 'Takikardia Ringan';
        hrBadge = 'Tinggi';
        hrClass = 'inline-block px-2.5 py-0.5 rounded-[5px] bg-[#FFF2DE] text-[#A6681E] text-[10.5px] font-bold';
      } else if (w.hr < 50) {
        hrSub = 'Bradikardia';
        hrBadge = 'Bradikardia';
        hrClass = 'inline-block px-2.5 py-0.5 rounded-[5px] bg-[#FBE7E8] text-[#C0565B] text-[10.5px] font-bold';
      }

      let spSub = 'Optimal (>=95%)';
      let spBadge = 'Normal';
      let spClass = 'inline-block px-2.5 py-0.5 rounded-[5px] bg-[#D0F1F8] text-[#263C41] text-[10.5px] font-bold';
      if (w.triageCode === 4 || w.spo2 <= 0) {
        spSub = w.triageCode === 4 ? 'Jam Dilepas' : 'Mengukur SpO2...';
        spBadge = w.triageCode === 4 ? 'Standby' : 'Mengukur...';
        spClass = 'inline-block px-2.5 py-0.5 rounded-[5px] bg-slate-100 text-slate-600 text-[10.5px] font-bold';
      } else if (w.spo2 < 88) {
        spSub = 'Hipoksia Berat';
        spBadge = 'Hipoksia Berat';
        spClass = 'inline-block px-2.5 py-0.5 rounded-[5px] bg-[#FBE7E8] text-[#DE6D72] text-[10.5px] font-bold';
      } else if (w.spo2 < 95) {
        spSub = 'Hipoksia Ringan';
        spBadge = 'Hipoksia Ringan';
        spClass = 'inline-block px-2.5 py-0.5 rounded-[5px] bg-[#FFF2DE] text-[#A6681E] text-[10.5px] font-bold';
      }

      let tmSub = 'Normotermia';
      let tmBadge = 'Normal';
      let tmClass = 'inline-block px-2.5 py-0.5 rounded-[5px] bg-[#F8DFC2] text-[#3B352E] text-[10.5px] font-bold';
      if (w.temp > 38.0) {
        tmSub = 'Hipertermia';
        tmBadge = 'Hipertermia';
        tmClass = 'inline-block px-2.5 py-0.5 rounded-[5px] bg-[#FBE7E8] text-[#DE6D72] text-[10.5px] font-bold';
      } else if (w.temp >= 37.4) {
        tmSub = 'Hipertermia Ringan';
        tmBadge = 'Hangat';
        tmClass = 'inline-block px-2.5 py-0.5 rounded-[5px] bg-[#FFF2DE] text-[#A6681E] text-[10.5px] font-bold';
      } else if (w.temp > 0 && w.temp < 35.5) {
        tmSub = 'Hipotermia';
        tmBadge = 'Hipotermia';
        tmClass = 'inline-block px-2.5 py-0.5 rounded-[5px] bg-[#D0F1F8] text-[#1E4D57] text-[10.5px] font-bold';
      }

      return { hrSub, hrBadge, hrClass, spSub, spBadge, spClass, tmSub, tmBadge, tmClass };
    }

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
    function toggleWorkerDropdown() {
      const menu = document.getElementById('workerDropdownMenu');
      const chev = document.getElementById('workerChevronIcon');
      if (!menu) return;
      const isHidden = menu.classList.contains('hidden');
      if (isHidden) {
        menu.classList.remove('hidden');
        if (chev) chev.style.transform = 'rotate(180deg)';
      } else {
        menu.classList.add('hidden');
        if (chev) chev.style.transform = 'rotate(0deg)';
      }
    }

    function handleWorkerDropdownSelect(workerId) {
      selectWorker(workerId);
      const menu = document.getElementById('workerDropdownMenu');
      const chev = document.getElementById('workerChevronIcon');
      if (menu) menu.classList.add('hidden');
      if (chev) chev.style.transform = 'rotate(0deg)';
    }

    // Close dropdown on outside click
    document.addEventListener('click', (e) => {
      const container = document.getElementById('workerDropdownContainer');
      const menu = document.getElementById('workerDropdownMenu');
      const chev = document.getElementById('workerChevronIcon');
      if (container && menu && !container.contains(e.target)) {
        menu.classList.add('hidden');
        if (chev) chev.style.transform = 'rotate(0deg)';
      }
    });

    function runHwDiag(type) {
      const c = document.getElementById('hwDiagConsole');
      if (!c) return;
      const ts = new Date().toTimeString().split(' ')[0];
      if (type === 'oled') {
        c.innerHTML = `&gt; [${ts}][OLED] Pattern test PASS. SSD1306 128x64 live frame buffer verified. Contrast 100%.`;
      } else if (type === 'rf') {
        c.innerHTML = `&gt; [${ts}][SX1278] Carrier 433.05 MHz Sub-GHz detected. RSSI: -88 dBm, SNR: +8.5 dB. Mesh roundtrip: 18ms.`;
      } else if (type === 'imu') {
        c.innerHTML = `&gt; [${ts}][BMI160] Freefall &amp; impact interrupt armed. Threshold: 4.85g. FIFO buffer ready.`;
        testSimSOS();
      } else if (type === 'temp') {
        c.innerHTML = `&gt; [${ts}][MLX90614] IR Thermopile calibrated. Tamb: 28.4&deg;C, Tobj: 36.5&deg;C. Accuracy &plusmn;0.2&deg;C.`;
      }
    }

    function updateDropdownMeta() {
      const w1 = workers[1];
      const w2 = workers[2];
      const th1 = getTriageTheme(w1.triageCode);
      const th2 = getTriageTheme(w2.triageCode);

      const od1 = document.getElementById('workerOptDot01');
      const od2 = document.getElementById('workerOptDot02');
      if (od1) od1.className = th1.optDotClass;
      if (od2) od2.className = th2.optDotClass;

      const os1 = document.getElementById('workerOptSub01');
      const os2 = document.getElementById('workerOptSub02');
      if (os1) os1.textContent = (w1.hr > 0 ? w1.hr + ' BPM' : '-- BPM') + ' • ' + (w1.spo2 > 0 ? w1.spo2 + '%' : '--%') + ' • ' + th1.short;
      if (os2) os2.textContent = (w2.hr > 0 ? w2.hr + ' BPM' : '-- BPM') + ' • ' + (w2.spo2 > 0 ? w2.spo2 + '%' : '--%') + ' • ' + th2.short;

      const w = workers[currentWorker];
      const thCur = getTriageTheme(w.triageCode);
      const dotEl = document.getElementById('selectedWorkerDot');
      if (dotEl) dotEl.className = thCur.dotClass;
    }

    function selectWorker(workerId) {
      currentWorker = workerId;

      // Update Dropdown Trigger & Checkmarks (Consistent Frame)
      const labelEl = document.getElementById('selectedWorkerLabel');
      const check01 = document.getElementById('workerOptCheck01');
      const check02 = document.getElementById('workerOptCheck02');
      const ergoBadge = document.getElementById('ergoNodeBadge');

      if (workerId === 2) {
        if (labelEl) labelEl.textContent = 'Pekerja #02 (Agus)';
        if (check01) check01.classList.add('hidden');
        if (check02) check02.classList.remove('hidden');
        if (ergoBadge) ergoBadge.textContent = 'SEC-01 // NODE-02';
      } else {
        if (labelEl) labelEl.textContent = 'Pekerja #01 (Bambang)';
        if (check01) check01.classList.remove('hidden');
        if (check02) check02.classList.add('hidden');
        if (ergoBadge) ergoBadge.textContent = 'SEC-01 // NODE-01';
      }

      const tab1 = document.getElementById('tabWorker01');
      const tab2 = document.getElementById('tabWorker02');
      if (tab1) tab1.classList.toggle('active', workerId === 1);
      if (tab2) tab2.classList.toggle('active', workerId === 2);
      
      const w = workers[workerId];
      updateDropdownMeta();
      
      if (!isSimulatorMode) {
        const slHR = document.getElementById('sliderHR');
        const slSpO2 = document.getElementById('sliderSpO2');
        if (slHR) slHR.value = Math.max(40, Math.min(180, w.hr > 0 ? w.hr : 40));
        if (slSpO2) slSpO2.value = Math.max(70, Math.min(100, w.spo2 > 0 ? w.spo2 : 70));
        
        const hrText = document.getElementById('simHRText');
        const spText = document.getElementById('simSpO2Text');
        if (hrText) hrText.textContent = (w.hr > 0 ? w.hr : '--') + ' bpm';
        if (spText) spText.textContent = (w.spo2 > 0 ? w.spo2 : '--') + ' %';
        evaluateSTART(w.hr, w.spo2, w.triageCode, w.accel);
      }

      updateTelemetryDisplay(w);
      updateSparklines(w);
      renderKinematicsBars();
      updateRosterTableUI();
    }

    function buildSmoothPath(values, minVal, maxVal) {
      const n = values.length;
      if (!n) return { line: 'M 0 26 L 160 26', fill: 'M 0 26 L 160 26 L 160 52 L 0 52 Z' };
      const w = 160;
      const topPad = 6;
      const bottomPad = 42;
      const span = Math.max(1, maxVal - minVal);
      const pts = values.map((v, i) => {
        const clamped = Math.max(minVal, Math.min(maxVal, v));
        const norm = (clamped - minVal) / span;
        const x = n === 1 ? w : (i * w) / (n - 1);
        const y = bottomPad - norm * (bottomPad - topPad);
        return [Number(x.toFixed(1)), Number(y.toFixed(1))];
      });

      let line = `M ${pts[0][0]} ${pts[0][1]}`;
      for (let i = 1; i < pts.length; i++) {
        const prev = pts[i - 1];
        const curr = pts[i];
        const mx = ((prev[0] + curr[0]) / 2).toFixed(1);
        line += ` C ${mx} ${prev[1]}, ${mx} ${curr[1]}, ${curr[0]} ${curr[1]}`;
      }
      const fill = `${line} L 160 52 L 0 52 Z`;
      return { line, fill };
    }

    function updateSparklines(w) {
      const hrData = w.hrHist.length ? w.hrHist : [75, 75];
      const spData = w.spo2Hist.length ? w.spo2Hist : [98, 98];
      const tmData = w.tempHist.length ? w.tempHist : [36.5, 36.5];

      const hrPath = buildSmoothPath(hrData, 50, 155);
      const spPath = buildSmoothPath(spData, 80, 100);
      const tmPath = buildSmoothPath(tmData, 34.5, 40.0);

      const hf = document.getElementById('sparkHeartFill');
      const hl = document.getElementById('sparkHeartLine');
      if (hf) hf.setAttribute('d', hrPath.fill);
      if (hl) hl.setAttribute('d', hrPath.line);

      const sf = document.getElementById('sparkSpo2Fill');
      const sl = document.getElementById('sparkSpo2Line');
      if (sf) sf.setAttribute('d', spPath.fill);
      if (sl) sl.setAttribute('d', spPath.line);

      const tf = document.getElementById('sparkTempFill');
      const tl = document.getElementById('sparkTempLine');
      if (tf) tf.setAttribute('d', tmPath.fill);
      if (tl) tl.setAttribute('d', tmPath.line);
    }

    function updateTelemetryDisplay(w) {
      const meta = getVitalMeta(w);

      const valHR = document.getElementById('val-hr');
      if (valHR) valHR.textContent = (w.hr > 0 && w.triageCode !== 4) ? w.hr : '--';
      const badgeHR = document.getElementById('badge-hr');
      if (badgeHR) {
        badgeHR.textContent = meta.hrBadge;
        badgeHR.className = meta.hrClass;
      }

      const valSpO2 = document.getElementById('val-spo2');
      if (valSpO2) valSpO2.textContent = (w.spo2 > 0 && w.triageCode !== 4) ? w.spo2 : '--';
      const badgeSpO2 = document.getElementById('badge-spo2');
      if (badgeSpO2) {
        badgeSpO2.textContent = meta.spBadge;
        badgeSpO2.className = meta.spClass;
      }

      const valTemp = document.getElementById('val-temp');
      if (valTemp) valTemp.textContent = w.temp > 0 ? w.temp.toFixed(1) : '--';
      const badgeTemp = document.getElementById('badge-temp');
      if (badgeTemp) {
        badgeTemp.textContent = meta.tmBadge;
        badgeTemp.className = meta.tmClass;
      }

      const accelPill = document.getElementById('liveAccelPill');
      if (accelPill) {
        if (w.triageCode === 3 || w.accel > 3.0) {
          accelPill.className = 'px-2.5 py-1 rounded-[7px] bg-red-100 text-red-700 font-mono text-[10.5px] font-bold animate-pulse whitespace-nowrap flex-shrink-0';
          accelPill.textContent = w.accel.toFixed(2) + 'g • BENTURAN SHOCK';
        } else if (w.triageCode === 2) {
          accelPill.className = 'px-2.5 py-1 rounded-[7px] bg-orange-100 text-orange-800 font-mono text-[10.5px] font-bold whitespace-nowrap flex-shrink-0';
          accelPill.textContent = w.accel.toFixed(2) + 'g • Waspada Lelah';
        } else if (w.triageCode === 4) {
          accelPill.className = 'px-2.5 py-1 rounded-[7px] bg-slate-100 text-slate-600 font-mono text-[10.5px] font-bold whitespace-nowrap flex-shrink-0';
          accelPill.textContent = w.accel.toFixed(2) + 'g • Jam Dilepas';
        } else {
          accelPill.className = 'px-2.5 py-1 rounded-[7px] bg-[#EFE9E0] text-[#3E3C39] font-mono text-[10.5px] font-bold whitespace-nowrap flex-shrink-0';
          const shortAct = w.activity.includes('Diam') ? 'Diam / Normal' : w.activity;
          accelPill.textContent = w.accel.toFixed(2) + 'g • ' + shortAct;
        }
      }
    }

    function updateWorkerRosterCard(num, w) {
      const suf = '0' + num;
      const th = getTriageTheme(w.triageCode);
      const meta = getVitalMeta(w);

      const dotEl = document.getElementById('rosterDot' + suf);
      if (dotEl) dotEl.className = th.optDotClass;

      const secEl = document.getElementById('rosterSector' + suf);
      if (secEl) secEl.innerHTML = 'Jam Tangan #' + suf + ' &bull; ' + w.sector;

      const hrEl = document.getElementById('rosterHR' + suf);
      if (hrEl) {
        hrEl.textContent = (w.hr > 0 && w.triageCode !== 4 ? w.hr : '--') + ' BPM';
        hrEl.className = th.textClass;
      }
      const hrSubEl = document.getElementById('rosterHRSub' + suf);
      if (hrSubEl) hrSubEl.textContent = meta.hrSub;

      const spEl = document.getElementById('rosterSpO2_' + suf);
      if (spEl) {
        spEl.textContent = (w.spo2 > 0 && w.triageCode !== 4 ? w.spo2 : '--') + '%';
        spEl.className = th.textClass;
      }
      const spSubEl = document.getElementById('rosterSpO2Sub' + suf);
      if (spSubEl) spSubEl.textContent = meta.spSub;

      const tmEl = document.getElementById('rosterTemp' + suf);
      if (tmEl) {
        tmEl.innerHTML = (w.temp > 0 ? w.temp.toFixed(1) : '--') + '&deg;C';
        tmEl.className = th.textClass;
      }
      const tmSubEl = document.getElementById('rosterTempSub' + suf);
      if (tmSubEl) tmSubEl.innerHTML = meta.tmSub;

      const actEl = document.getElementById('rosterActivity' + suf);
      if (actEl) {
        actEl.textContent = w.activity;
        actEl.className = th.actClass;
      }

      const routeEl = document.getElementById('rosterRoute' + suf);
      if (routeEl) {
        routeEl.textContent = w.route;
        if (w.isRelayed) {
          routeEl.className = 'px-2.5 py-0.5 rounded-lg bg-blue-50 text-blue-800 border border-blue-200 text-[10.5px] font-mono';
        } else if (num === 1) {
          routeEl.className = 'px-2.5 py-0.5 rounded-lg bg-orange-50 text-orange-800 border border-orange-200 text-[10.5px] font-mono';
        } else {
          routeEl.className = 'px-2.5 py-0.5 rounded-lg bg-teal-50 text-teal-800 border border-teal-200 text-[10.5px] font-mono';
        }
      }

      const triEl = document.getElementById('rosterTriage' + suf);
      if (triEl) {
        triEl.textContent = w.triageLabel || th.defaultLabel;
        triEl.className = th.pillClass;
      }
    }

    function updateRosterTableUI() {
      updateWorkerRosterCard(1, workers[1]);
      updateWorkerRosterCard(2, workers[2]);

      const rfEl = document.getElementById('rosterRfQuality');
      if (rfEl) {
        const wActive = workers[currentWorker];
        const rxStr = lastMqttRxTime ? (' • RX ' + lastMqttRxTime) : ' • 433.05 MHz';
        rfEl.textContent = 'RSSI ' + wActive.rssi + ' dBm // SF7' + rxStr;
      }

      const n1El = document.getElementById('rosterNode01Status');
      if (n1El) {
        const th1 = getTriageTheme(workers[1].triageCode);
        n1El.textContent = th1.short + ' • ' + (workers[1].lastRxAt ? 'Live ' + workers[1].lastRxAt : 'Relay Host Standby');
        n1El.className = 'font-bold text-xs font-mono ' + th1.textClass.replace('text-sm ', '').replace(' mt-0.5', '');
      }

      const n2El = document.getElementById('rosterNode02Status');
      if (n2El) {
        const th2 = getTriageTheme(workers[2].triageCode);
        const hopTxt = workers[2].isRelayed ? '1-Hop Relay' : 'Direct P2P';
        n2El.textContent = th2.short + ' • ' + hopTxt + (workers[2].lastRxAt ? ' (' + workers[2].lastRxAt + ')' : '');
        n2El.className = 'font-bold text-xs font-mono ' + th2.textClass.replace('text-sm ', '').replace(' mt-0.5', '');
      }
    }

    // -------------------------------------------------------------
    // 4. START TRIAGE RISK SIMULATOR ENGINE
    // -------------------------------------------------------------
    function syncMqttDotVisual(isPulse = false) {
      const dot = document.getElementById('mqttDot');
      if (!dot) return;
      if (isSimulatorMode) {
        dot.className = 'w-2 h-2 rounded-full bg-sky-400';
      } else if (mqttConnected) {
        dot.className = isPulse
          ? 'w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_10px_rgba(52,211,153,0.95)] scale-125 transition-transform'
          : 'w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)] transition-transform';
      } else {
        dot.className = 'w-2 h-2 rounded-full bg-amber-400';
      }
    }

    function onSimulatorInput() {
      isSimulatorMode = true;
      const label = document.getElementById('simModeLabel');
      const ind = document.getElementById('simModeIndicator');
      if (label) label.textContent = 'Simulator';
      if (ind) ind.textContent = 'MANUAL';
      syncMqttDotVisual(false);
      
      const hr = parseInt(document.getElementById('sliderHR').value);
      const spo2 = parseInt(document.getElementById('sliderSpO2').value);

      const hrText = document.getElementById('simHRText');
      const spText = document.getElementById('simSpO2Text');
      if (hrText) hrText.textContent = hr + ' bpm';
      if (spText) spText.textContent = spo2 + ' %';

      evaluateSTART(hr, spo2, null, 1.0);
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
        if (ind) ind.textContent = lastMqttRxTime ? ('LIVE • ' + lastMqttRxTime) : 'LIVE';
        const w = workers[currentWorker];
        const slHR = document.getElementById('sliderHR');
        const slSpO2 = document.getElementById('sliderSpO2');
        if (slHR) slHR.value = Math.max(40, Math.min(180, w.hr > 0 ? w.hr : 40));
        if (slSpO2) slSpO2.value = Math.max(70, Math.min(100, w.spo2 > 0 ? w.spo2 : 70));
        const hrText = document.getElementById('simHRText');
        const spText = document.getElementById('simSpO2Text');
        if (hrText) hrText.textContent = (w.hr > 0 ? w.hr : '--') + ' bpm';
        if (spText) spText.textContent = (w.spo2 > 0 ? w.spo2 : '--') + ' %';
        evaluateSTART(w.hr, w.spo2, w.triageCode, w.accel);
      }
      syncMqttDotVisual(false);
    }

    function setTriageDirect(tier) {
      isSimulatorMode = true;
      const label = document.getElementById('simModeLabel');
      const ind = document.getElementById('simModeIndicator');
      if (label) label.textContent = 'Simulator';
      if (ind) ind.textContent = tier;
      syncMqttDotVisual(false);

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

    function evaluateSTART(hr, spo2, liveTriageCode = null, accel = 1.0) {
      const pText = document.getElementById('triagePriorityText');
      const dot = document.getElementById('triageDot');
      const badge = document.getElementById('triageBadgePill');

      // Standby / watch removed in Live MQTT mode (do not misclassify HR=0 as HITAM)
      if (liveTriageCode === 4) {
        if (pText) {
          pText.textContent = 'STANDBY';
          pText.className = 'text-[18px] font-extrabold text-slate-300 leading-none font-mono';
        }
        if (dot) dot.style.left = '8%';
        if (badge) {
          badge.textContent = 'Jam Dilepas';
          badge.className = 'px-2.5 py-1 rounded-[7px] bg-slate-600 text-slate-100 text-[10px] font-bold';
        }
        return;
      }

      // Manual Simulator mode allows explicit HITAM test via low sliders
      if (liveTriageCode === null && (hr <= 40 || (hr > 160 && spo2 < 75))) {
        if (pText) {
          pText.textContent = 'HITAM';
          pText.className = 'text-[20px] font-extrabold text-gray-400 leading-none font-mono';
        }
        if (dot) dot.style.left = '92%';
        if (badge) {
          badge.textContent = 'Expectant';
          badge.className = 'px-2.5 py-1 rounded-[7px] bg-gray-700 text-gray-200 text-[10px] font-bold';
        }
        return;
      }

      const isEmergency = (liveTriageCode === 3) || (accel >= 3.0) || (hr > 125) || (hr > 0 && hr < 48) || (spo2 > 0 && spo2 < 88);
      const isOrangeWarn = !isEmergency && (liveTriageCode === 2);
      const isDelayed = !isEmergency && !isOrangeWarn && ((liveTriageCode === 1) || (hr > 100) || (spo2 > 0 && spo2 < 94));

      if (isEmergency) {
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
      } else if (isOrangeWarn) {
        if (pText) {
          pText.textContent = 'ORANYE';
          pText.className = 'text-[20px] font-extrabold text-[#FB923C] leading-none font-mono';
        }
        if (dot) dot.style.left = '64%';
        if (badge) {
          badge.textContent = 'Waspada Dini';
          badge.className = 'px-2.5 py-1 rounded-[7px] bg-[#FFEDD5] text-[#7C2D12] text-[10px] font-bold';
        }
      } else if (isDelayed) {
        if (pText) {
          pText.textContent = 'KUNING';
          pText.className = 'text-[20px] font-extrabold text-[#F59E0B] leading-none font-mono';
        }
        if (dot) dot.style.left = '50%';
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
    // 5. 18 MULTI-SEGMENT BARS (LIVE TELEMETRY + SHIFT PRESETS)
    // -------------------------------------------------------------
    let currentShiftIndex = 0;
    const shiftModes = [
      { label: 'Live Stream // Sektor 7', type: 'live' },
      { label: 'Shift Pagi // Sektor 7', type: 'static', data: janData },
      { label: 'Shift Siang // Lorong C', type: 'static', data: febData }
    ];

    function pushKinematicsBar(w, triageCode, aMax, gTotal) {
      let redH = 6;
      let tealH = 14;
      let ochreH = 22;

      if (triageCode === 3 || aMax >= 3.0) {
        redH = Math.round(Math.max(40, Math.min(72, aMax * 14)));
        tealH = 18;
        ochreH = 10;
      } else if (triageCode === 2 || triageCode === 1 || aMax >= 1.25 || gTotal >= 35) {
        redH = Math.round(Math.max(8, Math.min(26, aMax * 9)));
        tealH = Math.round(Math.max(28, Math.min(64, aMax * 26)));
        ochreH = 16;
      } else {
        redH = Math.round(Math.max(4, Math.min(14, aMax * 6)));
        tealH = Math.round(Math.max(10, Math.min(24, aMax * 12)));
        ochreH = Math.round(Math.max(20, Math.min(44, aMax * 26)));
      }

      const now = new Date();
      const shortTs = now.toTimeString().split(' ')[0].slice(3); // MM:SS
      w.kinematicsHist.push({
        red: redH,
        teal: tealH,
        ochre: ochreH,
        g: aMax.toFixed(2),
        label: shortTs
      });
      if (w.kinematicsHist.length > 18) {
        w.kinematicsHist.shift();
      }
    }

    function renderKinematicsBars() {
      const container = document.getElementById('kinematicsBarsContainer');
      if (!container) return;
      const mode = shiftModes[currentShiftIndex];
      const bars = mode.type === 'live'
        ? workers[currentWorker].kinematicsHist
        : makeSeedBars(mode.data);

      container.innerHTML = '';

      bars.forEach((bar) => {
        const col = document.createElement('div');
        col.className = 'day-col flex flex-col items-center justify-end h-full relative cursor-pointer group';
        col.style.width = '18px';
        col.onclick = () => {
          const pill = document.getElementById('liveAccelPill');
          if (pill) pill.textContent = bar.g + 'g @ ' + bar.label;
        };

        col.innerHTML = `
          <div class="opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity duration-150 absolute -top-7 bg-[#2C2A2A] text-white text-[9.5px] font-mono font-bold px-2 py-0.5 rounded shadow-md whitespace-nowrap z-20">
            ` + bar.label + `: ` + bar.g + `g
          </div>
          <div class="flex flex-col items-center gap-[5px] mb-1">
            <span class="pill-seg w-[4.5px] rounded-full bg-[#CC8B3C]" style="height: ` + bar.ochre + `px"></span>
            <span class="pill-seg w-[4.5px] rounded-full bg-[#3E8D9B]" style="height: ` + bar.teal + `px"></span>
            <span class="pill-seg w-[4.5px] rounded-full bg-[#DA7468]" style="height: ` + bar.red + `px"></span>
          </div>
          <div class="h-0 w-full flex justify-end">
            <span class="x-label">` + bar.label + `</span>
          </div>
        `;
        container.appendChild(col);
      });
    }

    function cycleShift() {
      currentShiftIndex = (currentShiftIndex + 1) % shiftModes.length;
      const shiftEl = document.getElementById('shiftLabel');
      if (shiftEl) shiftEl.textContent = shiftModes[currentShiftIndex].label;
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
    // 7. LEAFLET SUBTERRANEAN GIS MINE MAP (LIVE MARKERS & MESH LINES)
    // -------------------------------------------------------------
    const GATEWAY_POS = [-8.2435, 113.6928];

    function buildTacticalIcon(title, subtitle, color, isPulse) {
      const pulseCss = isPulse ? 'box-shadow: 0 0 0 3px rgba(239,68,68,0.35), 0 4px 12px rgba(0,0,0,0.16);' : 'box-shadow: 0 4px 12px rgba(0,0,0,0.12);';
      return L.divIcon({
        className: 'tactical-div-icon',
        html: `<div style="background: rgba(255,255,255,0.96); border: 1.8px solid ` + color + `; padding: 4px 8px; border-radius: 8px; ` + pulseCss + ` display: flex; align-items: center; gap: 6px; white-space: nowrap; font-family: monospace; font-size: 10px; color: #2D2B2A;">
                 <span style="width: 8px; height: 8px; border-radius: 999px; background: ` + color + `;"></span>
                 <b>` + title + `</b>
                 <span style="color: #7B7874;">(` + subtitle + `)</span>
               </div>`,
        iconSize: [195, 26],
        iconAnchor: [97, 24]
      });
    }

    function updateMapNodesRealtime() {
      if (!leafletMap) return;
      const w1 = workers[1];
      const w2 = workers[2];
      const th1 = getTriageTheme(w1.triageCode);
      const th2 = getTriageTheme(w2.triageCode);

      const pos1 = [w1.lat || -8.2465, w1.lng || 113.6965];
      const pos2 = [w2.lat || -8.2498, w2.lng || 113.7012];

      if (watch1Marker) {
        watch1Marker.setLatLng(pos1);
        watch1Marker.setIcon(buildTacticalIcon('JAM #01: BAMBANG', th1.short + ' • ' + (w1.hr > 0 ? w1.hr + 'bpm' : '--'), th1.hex, w1.triageCode === 3));
        watch1Marker.setPopupContent(
          `<div class="font-mono text-xs"><b>Jam Tangan #01: Bambang</b><br/>` + w1.sector + `<br/>Triage: <b>` + w1.triageLabel + `</b><br/>Vitals: ` + (w1.hr > 0 ? w1.hr : '--') + ` BPM &bull; ` + (w1.spo2 > 0 ? w1.spo2 : '--') + `% &bull; ` + w1.temp.toFixed(1) + `&deg;C<br/>Rute: ` + w1.route + ` (` + w1.rssi + ` dBm)</div>`
        );
      }

      if (watch2Marker) {
        watch2Marker.setLatLng(pos2);
        watch2Marker.setIcon(buildTacticalIcon('JAM #02: AGUS', th2.short + ' • ' + (w2.hr > 0 ? w2.hr + 'bpm' : '--'), th2.hex, w2.triageCode === 3));
        watch2Marker.setPopupContent(
          `<div class="font-mono text-xs"><b>Jam Tangan #02: Agus Salim</b><br/>` + w2.sector + `<br/>Triage: <b>` + w2.triageLabel + `</b><br/>Vitals: ` + (w2.hr > 0 ? w2.hr : '--') + ` BPM &bull; ` + (w2.spo2 > 0 ? w2.spo2 : '--') + `% &bull; ` + w2.temp.toFixed(1) + `&deg;C<br/>Rute: ` + w2.route + ` (` + w2.rssi + ` dBm)</div>`
        );
      }

      if (hopPolyline) {
        hopPolyline.setLatLngs(w2.isRelayed ? [pos2, pos1] : [pos2, GATEWAY_POS]);
        hopPolyline.setStyle({
          color: w2.triageCode === 3 ? '#EF4444' : (w2.isRelayed ? '#10B981' : '#0EA5E9'),
          weight: w2.triageCode === 3 ? 4.5 : 3.5,
          dashArray: w2.isRelayed ? null : '5, 5'
        });
      }

      if (uplinkPolyline) {
        uplinkPolyline.setLatLngs([pos1, GATEWAY_POS]);
        uplinkPolyline.setStyle({
          color: w2.triageCode === 3 ? '#EA580C' : '#D97706',
          weight: 3.5,
          dashArray: '6, 6'
        });
      }
    }

    function initLeafletMap() {
      const mapContainer = document.getElementById('leafletMapContainer');
      if (!mapContainer || leafletMap) return;

      const watch1Pos = [workers[1].lat, workers[1].lng];
      const watch2Pos = [workers[2].lat, workers[2].lng];

      leafletMap = L.map('leafletMapContainer', {
        zoomControl: true,
        attributionControl: false
      }).setView(watch1Pos, 15);

      L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
        maxZoom: 16
      }).addTo(leafletMap);

      gatewayMarker = L.marker(GATEWAY_POS, {
        icon: buildTacticalIcon('GATEWAY BASECAMP', 'Surface Node', '#059669', false)
      }).addTo(leafletMap).bindPopup('<div class="font-mono text-xs"><b>Posko Permukaan Basecamp</b><br/>ESP32 Gateway (COM14) + MQTT Uplink</div>');

      watch1Marker = L.marker(watch1Pos, {
        icon: buildTacticalIcon('JAM #01: BAMBANG', 'Relay Host', '#D97706', false)
      }).addTo(leafletMap).bindPopup('<div class="font-mono text-xs"><b>Jam Tangan #01: Bambang</b></div>');

      watch2Marker = L.marker(watch2Pos, {
        icon: buildTacticalIcon('JAM #02: AGUS', 'Sektor 7 Miner', '#059669', false)
      }).addTo(leafletMap).bindPopup('<div class="font-mono text-xs"><b>Jam Tangan #02: Agus Salim</b></div>');

      hopPolyline = L.polyline([watch2Pos, watch1Pos], {
        color: '#10B981',
        weight: 3.5,
        opacity: 0.85
      }).addTo(leafletMap);

      uplinkPolyline = L.polyline([watch1Pos, GATEWAY_POS], {
        color: '#EA580C',
        weight: 4,
        dashArray: '6, 6',
        opacity: 0.9
      }).addTo(leafletMap);

      updateMapNodesRealtime();
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
      alert("DIAGNOSTIK JAM TANGAN #" + (workerId < 10 ? '0' + workerId : workerId) + " (" + w.name + "):\nStatus Hardware: Aktif Normal\nLoRa Link: " + w.route + " (" + w.rssi + " dBm)\nVitals: " + w.hr + " BPM • " + w.spo2 + "% SpO2 • " + w.temp.toFixed(1) + "°C\nTriage: " + w.triageLabel + "\nLast Live RX: " + (w.lastRxAt || 'Waiting packet') + "\nForwarding Mesh: 1-Hop P2P Aktif");
    }

    // -------------------------------------------------------------
    // 8. CHRONOLOGICAL AUDIT TRAIL & EXCEL DOWNLOAD
    // -------------------------------------------------------------
    function appendAuditTrail(title, nodeName, detailText, level) {
      const now = new Date();
      const timeStr = now.toTimeString().split(' ')[0] + ' UTC';
      
      const statusLabel = level === 'red' ? 'MERAH (Immediate)'
        : (level === 'orange' ? 'ORANYE (Waspada)'
        : (level === 'amber' ? 'KUNING (Delayed)'
        : (level === 'slate' ? 'STANDBY (Lepas)' : 'HIJAU (Normal)')));

      const logItem = {
        time: timeStr,
        title: title,
        node: nodeName,
        desc: detailText,
        status: statusLabel,
        severity: level
      };
      auditLogsData.unshift(logItem);
      if (auditLogsData.length > 250) auditLogsData.pop();

      const container = document.getElementById('auditLogList');
      if (!container) return;

      const div = document.createElement('div');
      
      let borderClass = 'border-l-4 border-emerald-500 bg-white text-slate-800';
      if (level === 'red') {
        borderClass = 'border-l-4 border-red-500 bg-red-50/70 text-red-900';
      } else if (level === 'orange') {
        borderClass = 'border-l-4 border-orange-500 bg-orange-50/70 text-orange-900';
      } else if (level === 'amber') {
        borderClass = 'border-l-4 border-amber-500 bg-amber-50/70 text-amber-900';
      } else if (level === 'teal') {
        borderClass = 'border-l-4 border-teal-500 bg-teal-50/70 text-teal-900';
      } else if (level === 'slate') {
        borderClass = 'border-l-4 border-slate-400 bg-slate-50 text-slate-700';
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
      while (container.children.length > 100) {
        container.removeChild(container.lastChild);
      }

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
    // 10. REAL-TIME MQTT ENGINE (broker.emqx.io:8084) + FULL UI SYNC
    // -------------------------------------------------------------
    function deriveActivityText(code, accel, summary) {
      if (summary) return summary;
      if (code === 3 || accel >= 3.0) return 'Free-Fall & Benturan (' + accel.toFixed(2) + 'g)';
      if (code === 2) return 'Waspada Kelelahan / Suhu Tinggi';
      if (code === 1) return 'Kerja Aktif (' + accel.toFixed(2) + 'g)';
      if (code === 4) return 'Standby (Jam Dilepas)';
      return 'Diam / Istirahat Normal';
    }

    function normalizeRawPacket(rawStr) {
      // Fallback: support raw FEAT string if ever sent directly without Node-RED wrapper
      let str = rawStr.trim();
      let isNode01 = false;
      let isRelayed = false;
      if (str.startsWith('RELAY,')) {
        isRelayed = true;
        const pos = str.indexOf('FEAT,');
        if (pos !== -1) str = str.substring(pos);
      } else if (str.startsWith('NODE01,')) {
        isNode01 = true;
        const pos = str.indexOf('FEAT,');
        if (pos !== -1) str = str.substring(pos);
      }
      if (!str.startsWith('FEAT,')) return null;
      const p = str.split(',').map(s => s.trim());
      if (p.length < 13) return null;
      const aMax = parseFloat(p[3]) || 1.0;
      const gTotal = parseFloat(p[2]) || 0.0;
      const tCode = parseInt(p[12]) || 0;
      const hr = p.length > 13 ? (parseInt(p[13]) || 0) : 0;
      const spo2 = p.length > 14 ? (parseInt(p[14]) || 0) : 0;
      const temp = p.length > 15 ? (parseFloat(p[15]) || 36.6) : 36.6;
      const th = getTriageTheme(tCode);
      return {
        device_id: isNode01 ? 'RESCUE-TAG-01' : 'RESCUE-TAG-02',
        worker_id: isNode01 ? 'WRK-001' : 'WRK-002',
        vitals: { hr, spo2, temp },
        kinematics: { a_max: aMax, g_total: gTotal },
        triage: { code: tCode, label: th.defaultLabel, is_emergency: tCode === 3 },
        network: {
          route: isNode01 ? 'Direct Relay Host (Hop 1)' : (isRelayed ? '1-Hop LoRa Relay via Jam #01' : 'Direct LoRa P2P'),
          rssi: isRelayed ? -78 : -68,
          is_relayed: isRelayed
        }
      };
    }

    function applyTelemetryPacket(topic, data) {
      if (!data) return;

      // Support standalone alert packet cleanly
      if (topic === 'rescue/tag/alert' && !data.vitals && data.alert_type) {
        const wTarget = (data.worker && data.worker.includes('Bambang')) ? workers[1] : workers[2];
        appendAuditTrail(
          'EMERGENCY ALERT: ' + (data.alert_type || 'SOS'),
          wTarget.tagId,
          (data.worker || wTarget.name) + ' • ' + (data.kinematics || 'SOS Triggered'),
          'red'
        );
        if (audioAlertEnabled) playEmergencyBeep();
        return;
      }

      let workerNum = 2;
      if (data.device_id === 'RESCUE-TAG-01' || data.worker_id === 'WRK-001' || (data.worker_name && data.worker_name.includes('Bambang'))) {
        workerNum = 1;
      }

      const w = workers[workerNum];
      const nowTime = new Date().toTimeString().split(' ')[0];
      mqttPacketCount++;
      lastMqttRxTime = nowTime;
      w.rxCount++;
      w.lastRxAt = nowTime;

      if (data.sector) w.sector = data.sector;
      if (data.location) {
        if (typeof data.location.lat === 'number' && data.location.lat !== 0) w.lat = data.location.lat;
        if (typeof data.location.lng === 'number' && data.location.lng !== 0) w.lng = data.location.lng;
      }

      if (data.vitals) {
        if (data.vitals.hr !== undefined && data.vitals.hr !== null) w.hr = Number(data.vitals.hr);
        if (data.vitals.spo2 !== undefined && data.vitals.spo2 !== null) w.spo2 = Number(data.vitals.spo2);
        if (data.vitals.temp !== undefined && data.vitals.temp !== null) w.temp = Number(data.vitals.temp);
      }

      let gTotal = 0;
      if (data.kinematics) {
        if (data.kinematics.a_max !== undefined && data.kinematics.a_max !== null) w.accel = Number(data.kinematics.a_max);
        if (data.kinematics.g_total !== undefined && data.kinematics.g_total !== null) gTotal = Number(data.kinematics.g_total);
      }

      if (data.triage) {
        if (data.triage.code !== undefined && data.triage.code !== null) w.triageCode = Number(data.triage.code);
        w.triageLabel = data.triage.label || getTriageTheme(w.triageCode).defaultLabel;
        if (data.triage.is_emergency !== undefined) w.isEmergency = Boolean(data.triage.is_emergency);
        else w.isEmergency = (w.triageCode === 3);
      }

      if (data.network) {
        if (data.network.route) w.route = data.network.route;
        if (data.network.rssi !== undefined && data.network.rssi !== null) w.rssi = Number(data.network.rssi);
        if (data.network.is_relayed !== undefined) w.isRelayed = Boolean(data.network.is_relayed);
        else if (data.network.route) w.isRelayed = data.network.route.includes('Relay via');
      }

      w.activity = deriveActivityText(w.triageCode, w.accel, data.kinematics && data.kinematics.summary);

      // Push rolling sparkline history (ignore 0 reading during sensor calibration)
      if (w.hr > 0) {
        w.hrHist.push(w.hr);
        if (w.hrHist.length > 12) w.hrHist.shift();
      }
      if (w.spo2 > 0) {
        w.spo2Hist.push(w.spo2);
        if (w.spo2Hist.length > 12) w.spo2Hist.shift();
      }
      if (w.temp > 0) {
        w.tempHist.push(w.temp);
        if (w.tempHist.length > 12) w.tempHist.shift();
      }

      // Push rolling Kinematics Bar
      pushKinematicsBar(w, w.triageCode, w.accel, gTotal);

      // Pulse MQTT RX indicator
      syncMqttDotVisual(true);
      setTimeout(() => syncMqttDotVisual(false), 320);

      // Refresh global elements (Dropdown, Roster, Map)
      updateDropdownMeta();
      updateRosterTableUI();
      updateMapNodesRealtime();

      // Refresh Overview + Right Panel for currently viewed worker
      if (currentWorker === workerNum) {
        updateTelemetryDisplay(w);
        updateSparklines(w);
        if (currentShiftIndex === 0) renderKinematicsBars();

        if (!isSimulatorMode) {
          const ind = document.getElementById('simModeIndicator');
          if (ind) ind.textContent = 'LIVE • ' + nowTime;
          const slHR = document.getElementById('sliderHR');
          const slSpO2 = document.getElementById('sliderSpO2');
          if (slHR) slHR.value = Math.max(40, Math.min(180, w.hr > 0 ? w.hr : 40));
          if (slSpO2) slSpO2.value = Math.max(70, Math.min(100, w.spo2 > 0 ? w.spo2 : 70));
          const hrText = document.getElementById('simHRText');
          const spText = document.getElementById('simSpO2Text');
          if (hrText) hrText.textContent = (w.hr > 0 ? w.hr : '--') + ' bpm';
          if (spText) spText.textContent = (w.spo2 > 0 ? w.spo2 : '--') + ' %';
          evaluateSTART(w.hr, w.spo2, w.triageCode, w.accel);
        }
      }

      // Intelligent Chronological Audit Logging (first RX + state changes + throttled SOS)
      if (!hasLoggedFirstLiveRx) {
        hasLoggedFirstLiveRx = true;
        appendAuditTrail(
          'Live Telemetry Stream Active',
          w.tagId,
          'Gateway COM14 -> MQTT bridge streaming (' + w.hr + ' BPM, ' + w.spo2 + '% SpO2, ' + w.temp.toFixed(1) + '°C)',
          'teal'
        );
      }

      const nowMs = Date.now();
      const levelMap = { 0: 'green', 1: 'amber', 2: 'orange', 3: 'red', 4: 'slate' };
      const curLevel = levelMap[w.triageCode] || 'green';

      if (w.lastLoggedTriage !== null && w.lastLoggedTriage !== w.triageCode) {
        appendAuditTrail(
          'Triage Transition -> ' + getTriageTheme(w.triageCode).short,
          w.tagId,
          w.name + ': ' + w.triageLabel + ' | HR ' + w.hr + ' BPM, SpO2 ' + w.spo2 + '%, Accel ' + w.accel.toFixed(2) + 'g',
          curLevel
        );
      } else if (w.triageCode === 3 && (nowMs - w.lastAlertTs > 15000)) {
        w.lastAlertTs = nowMs;
        appendAuditTrail(
          'DARURAT MEDIS / IMPACT DETECTED',
          w.tagId,
          w.name + ' di ' + w.sector + '. HR: ' + w.hr + ' BPM, SpO2: ' + w.spo2 + '%. Prioritas SAR MERAH!',
          'red'
        );
      }
      w.lastLoggedTriage = w.triageCode;

      if (w.lastLoggedRoute !== null && w.lastLoggedRoute !== w.route) {
        appendAuditTrail(
          'Mesh Route Updated',
          w.tagId,
          w.name + ' beralih ke rute: ' + w.route + ' (' + w.rssi + ' dBm)',
          w.isRelayed ? 'amber' : 'teal'
        );
      }
      w.lastLoggedRoute = w.route;

      if (w.triageCode === 3 && audioAlertEnabled) {
        playEmergencyBeep();
      }
    }

    function initMQTT() {
      try {
        const clientId = 'rescuetag_cmd_' + Math.random().toString(16).substring(2, 8);
        mqttClient = mqtt.connect('wss://broker.emqx.io:8084/mqtt', {
          clientId: clientId,
          clean: true,
          connectTimeout: 5000,
          reconnectPeriod: 3000
        });

        mqttClient.on('connect', () => {
          mqttConnected = true;
          console.log('[MQTT] Connected to broker.emqx.io:8084');
          syncMqttDotVisual(false);
          const ind = document.getElementById('simModeIndicator');
          if (ind && !isSimulatorMode && !lastMqttRxTime) ind.textContent = 'ONLINE';
          mqttClient.subscribe('rescue/tag/data');
          mqttClient.subscribe('rescue/tag/alert');
          appendAuditTrail('MQTT EMQX Online', 'EMQX BROKER', 'Listening to rescue/tag/data & rescue/tag/alert', 'teal');
        });

        mqttClient.on('message', (topic, payload) => {
          try {
            const rawStr = payload.toString();
            let data = null;
            if (rawStr.trim().startsWith('{')) {
              data = JSON.parse(rawStr);
            } else {
              data = normalizeRawPacket(rawStr);
            }
            console.log('[MQTT RX]', topic, data);
            applyTelemetryPacket(topic, data);
          } catch (err) {
            console.warn('[MQTT PARSE ERR]', err);
          }
        });

        mqttClient.on('offline', () => {
          mqttConnected = false;
          syncMqttDotVisual(false);
          const ind = document.getElementById('simModeIndicator');
          if (ind && !isSimulatorMode) ind.textContent = 'OFFLINE';
        });

        mqttClient.on('error', (err) => {
          mqttConnected = false;
          const dot = document.getElementById('mqttDot');
          if (dot) dot.className = 'w-2 h-2 rounded-full bg-red-500';
        });

      } catch (e) {
        console.warn('Running in autonomous simulation mode', e);
        mqttConnected = false;
        syncMqttDotVisual(false);
      }
    }

    // -------------------------------------------------------------
    // 11. DEMO TRIGGER FUNCTIONS FOR COMPETITION JURY
    // -------------------------------------------------------------
    function testSimSOS() {
      isSimulatorMode = false;
      const label = document.getElementById('simModeLabel');
      if (label) label.textContent = 'Live MQTT';
      applyTelemetryPacket('rescue/tag/data', {
        device_id: 'RESCUE-TAG-02',
        worker_id: 'WRK-002',
        sector: 'Sektor 7 (Lorong C-4)',
        vitals: { hr: 138, spo2: 86, temp: 38.6 },
        kinematics: { a_max: 4.85, g_total: 18.5, summary: 'Free-Fall & Immobility >30s' },
        triage: { code: 3, label: 'MERAH - Immediate (SOS)', is_emergency: true },
        network: { route: '1-Hop LoRa Relay via Jam #01', rssi: -78, is_relayed: true }
      });
      selectWorker(2);
      pulseHopSimulation();
    }

    function testSimNormal() {
      isSimulatorMode = false;
      const label = document.getElementById('simModeLabel');
      if (label) label.textContent = 'Live MQTT';
      applyTelemetryPacket('rescue/tag/data', {
        device_id: 'RESCUE-TAG-02',
        worker_id: 'WRK-002',
        sector: 'Sektor 7 (Lorong C-4)',
        vitals: { hr: 75, spo2: 98, temp: 36.5 },
        kinematics: { a_max: 1.02, g_total: 2.15, summary: 'Diam / Istirahat Normal' },
        triage: { code: 0, label: 'HIJAU - Minor (Aman)', is_emergency: false },
        network: { route: 'Direct LoRa P2P', rssi: -68, is_relayed: false }
      });
      selectWorker(2);
    }

    function toggleMqttInfo() {
      alert(
        "MQTT BROKER STATUS:\n" +
        "Status: " + (mqttConnected ? "CONNECTED" : "CONNECTING / OFFLINE") + "\n" +
        "Broker: wss://broker.emqx.io:8084/mqtt\n" +
        "Topics: rescue/tag/data, rescue/tag/alert\n" +
        "Total Packets RX: " + mqttPacketCount + "\n" +
        "Last RX Time: " + (lastMqttRxTime || "Belum ada paket live dari COM14 -> Node-RED")
      );
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
        const dEl = document.getElementById('liveDate');
        if (dEl && !dEl.dataset.initialized) {
          const options = { day: 'numeric', month: 'long', year: 'numeric' };
          dEl.textContent = now.toLocaleDateString('id-ID', options);
          dEl.dataset.initialized = 'true';
        }
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
final_html = HTML_TEMPLATE.replace("BASE64_IMAGE_PLACEHOLDER", data_uri).replace("BASE64_PLACEHOLDER", data_uri)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(final_html)

print("Generated index.html v2 successfully! Total size:", len(final_html))
