import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import requests
import random
import time
import math
from datetime import datetime, timedelta

# ==========================================
# 1. CẤU HÌNH TRANG & KHỞI TẠO STATE
# ==========================================
st.set_page_config(
    page_title="Trạm Quan Trắc Không Khí · DSA Super Pro",
    page_icon="🍃",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "show_comparison" not in st.session_state:
    st.session_state.show_comparison = True
if "current_env" not in st.session_state:
    st.session_state.current_env = "🏠 Nhà ở"

current_hour = datetime.now().hour
is_daytime = 6 <= current_hour < 18

# NỀN GRADIENT ĐA LỚP THEO THỜI GIAN THỰC
if is_daytime:
    bg_gradient = """
        radial-gradient(1200px 800px at 88% -5%, rgba(251, 191, 36, 0.22), transparent 65%),
        radial-gradient(1000px 700px at 8% 10%, rgba(56, 189, 248, 0.18), transparent 60%),
        radial-gradient(900px 600px at 50% 100%, rgba(16, 185, 129, 0.10), transparent 65%),
        linear-gradient(180deg, #0f172a 0%, #1e293b 50%, #0f172a 100%)
    """
else:
    bg_gradient = """
        radial-gradient(1300px 850px at 88% -5%, rgba(56, 189, 248, 0.24), transparent 65%),
        radial-gradient(1000px 700px at 92% 20%, rgba(192, 132, 252, 0.18), transparent 60%),
        radial-gradient(900px 600px at 10% 90%, rgba(14, 165, 233, 0.12), transparent 65%),
        linear-gradient(180deg, #020617 0%, #0f172a 55%, #020617 100%)
    """

celestial_html = """
<div class="ambient-grid"></div>
<div class="celestial-container">
    <div class="sun-glow-outer"></div>
    <div class="sun-glow-inner"></div>
    <div class="sun-core"></div>
</div>
""" if is_daytime else """
<div class="ambient-grid"></div>
<div class="starfield"></div>
<div class="celestial-container">
    <div class="moon-glow-outer"></div>
    <div class="moon-glow-inner"></div>
    <div class="moon-core"></div>
</div>
"""

# ==========================================
# 2. CSS ULTRA-LUXURY: GLASSMORPHISM & HUD
# ==========================================
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap');

    :root {{
        --text-main: #f8fafc;
        --text-sub: #cbd5e1;
        --text-muted: #64748b;
        --blue-glow: #38bdf8;
        --purple-glow: #c084fc;
        --emerald-glow: #34d399;
        --amber-glow: #fbbf24;
        --rose-glow: #fb7185;
    }}

    html, body {{
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        -webkit-font-smoothing: antialiased;
        overflow-x: hidden;
        scroll-behavior: smooth;
    }}

    /* THANH CUỘN TINH TẾ */
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: rgba(2, 6, 23, 0.6); }}
    ::-webkit-scrollbar-thumb {{ background: rgba(100, 116, 139, 0.5); border-radius: 999px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: rgba(56, 189, 248, 0.7); }}
    ::selection {{ background: rgba(56, 189, 248, 0.3); color: #ffffff; }}

    .stApp {{
        background: {bg_gradient};
        background-attachment: fixed;
    }}
    .block-container {{
        padding-top: 1.1rem;
        padding-bottom: 3rem;
        max-width: 1480px;
        position: relative;
        z-index: 2;
    }}

    /* LƯỚI TỌA ĐỘ KHÔNG GIAN & SAO ĐÊM */
    .ambient-grid {{
        position: fixed; inset: 0; pointer-events: none; z-index: 0;
        background-image: 
            linear-gradient(to right, rgba(255,255,255,0.022) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(255,255,255,0.022) 1px, transparent 1px);
        background-size: 48px 48px;
        mask-image: radial-gradient(circle at 50% 30%, black 30%, transparent 85%);
        -webkit-mask-image: radial-gradient(circle at 50% 30%, black 30%, transparent 85%);
    }}
    .starfield {{
        position: fixed; inset: 0; pointer-events: none; z-index: 0;
        background-image: 
            radial-gradient(1.5px 1.5px at 15% 20%, rgba(255,255,255,0.7), transparent),
            radial-gradient(1px 1px at 35% 12%, rgba(56,189,248,0.8), transparent),
            radial-gradient(2px 2px at 65% 28%, rgba(255,255,255,0.5), transparent),
            radial-gradient(1.5px 1.5px at 82% 45%, rgba(192,132,252,0.7), transparent),
            radial-gradient(1px 1px at 25% 65%, rgba(255,255,255,0.4), transparent);
        animation: twinkle 6s infinite alternate ease-in-out;
    }}
    @keyframes twinkle {{ 0% {{ opacity: 0.4; }} 100% {{ opacity: 0.95; }} }}

    /* VẬT THỂ THIÊN VĂN */
    .celestial-container {{
        position: fixed; top: 18px; right: 42px; width: 220px; height: 220px;
        z-index: 0; pointer-events: none; display: flex; align-items: center; justify-content: center;
    }}
    .sun-core {{
        position: absolute; width: 88px; height: 88px;
        background: radial-gradient(circle, #ffffff 15%, #fef08a 45%, #f59e0b 92%);
        border-radius: 50%;
        box-shadow: 0 0 45px 15px rgba(255, 255, 255, 0.9), 0 0 90px 35px rgba(254, 240, 138, 0.65), 0 0 160px 70px rgba(245, 158, 11, 0.35);
        animation: sun-pulse 4s infinite alternate ease-in-out;
    }}
    .sun-glow-inner {{
        position: absolute; width: 240px; height: 240px;
        background: radial-gradient(circle, rgba(255, 255, 255, 0.4) 0%, rgba(253, 224, 71, 0.2) 45%, transparent 70%);
        border-radius: 50%; animation: sun-pulse 4s infinite alternate ease-in-out;
    }}
    .sun-glow-outer {{
        position: absolute; width: 520px; height: 520px;
        background: radial-gradient(circle, rgba(253, 224, 71, 0.15) 0%, rgba(245, 158, 11, 0.05) 45%, transparent 65%);
        border-radius: 50%;
    }}
    @keyframes sun-pulse {{ 0% {{ transform: scale(0.94); opacity: 0.85; }} 100% {{ transform: scale(1.06); opacity: 1; }} }}

    .moon-core {{
        position: absolute; width: 92px; height: 92px; border-radius: 50%;
        box-shadow: -22px 13px 0 0 #f8fafc, inset 0 0 14px rgba(255,255,255,0.65);
        filter: drop-shadow(0 0 28px rgba(56, 189, 248, 0.85)) drop-shadow(0 0 70px rgba(56, 189, 248, 0.55));
        animation: float-moon 6s infinite alternate ease-in-out; background: transparent;
    }}
    .moon-glow-inner {{
        position: absolute; width: 260px; height: 260px;
        background: radial-gradient(circle, rgba(56, 189, 248, 0.32) 0%, transparent 62%);
        border-radius: 50%; animation: moon-pulse 4.5s infinite alternate ease-in-out;
    }}
    .moon-glow-outer {{
        position: absolute; width: 560px; height: 560px;
        background: radial-gradient(circle, rgba(56, 189, 248, 0.14) 0%, rgba(192, 132, 252, 0.06) 45%, transparent 65%);
        border-radius: 50%;
    }}
    @keyframes moon-pulse {{ 0% {{ transform: scale(0.9); opacity: 0.65; }} 100% {{ transform: scale(1.1); opacity: 1; }} }}
    @keyframes float-moon {{ 0% {{ transform: translateY(0px) rotate(0deg); }} 100% {{ transform: translateY(-12px) rotate(4deg); }} }}

    /* HERO BANNER - COMMAND CENTER HUD */
    .hero-banner {{
        position: sticky; top: 10px; z-index: 999;
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.88) 0%, rgba(30, 41, 59, 0.92) 100%);
        border: 1px solid rgba(255, 255, 255, 0.18);
        border-top: 1px solid rgba(255, 255, 255, 0.32);
        border-radius: 24px; padding: 18px 28px; margin-bottom: 24px;
        backdrop-filter: blur(28px) saturate(190%);
        -webkit-backdrop-filter: blur(28px) saturate(190%);
        box-shadow: 0 22px 48px -12px rgba(0, 0, 0, 0.75), inset 0 1px 0 rgba(255, 255, 255, 0.22);
        display: flex; justify-content: space-between; align-items: center; gap: 20px; flex-wrap: wrap;
    }}
    .hero-brand-tag {{
        display: inline-flex; align-items: center; gap: 6px;
        font-size: 0.7rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.12em;
        color: #38bdf8; background: rgba(56, 189, 248, 0.12);
        border: 1px solid rgba(56, 189, 248, 0.3); padding: 3px 10px; border-radius: 999px; margin-bottom: 6px;
    }}
    .hero-title {{
        font-size: 1.95rem; font-weight: 900; margin: 0; line-height: 1.18; letter-spacing: -0.03em;
        background: linear-gradient(90deg, #ffffff 0%, #7dd3fc 48%, #c084fc 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }}
    .hero-sub {{
        color: #cbd5e1; font-size: 0.86rem; font-weight: 600; margin-top: 6px;
        display: flex; align-items: center; flex-wrap: wrap; gap: 8px;
    }}
    .mono-num {{
        font-family: 'JetBrains Mono', monospace;
        font-variant-numeric: tabular-nums;
    }}
    .hero-hud-right {{
        display: flex; align-items: center; gap: 12px; flex-wrap: wrap;
    }}
    .hud-pill {{
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.14);
        border-radius: 16px; padding: 8px 14px;
        display: flex; flex-direction: column; align-items: flex-end;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.08);
    }}
    .hud-pill-label {{ font-size: 0.66rem; font-weight: 700; text-transform: uppercase; color: #94a3b8; letter-spacing: 0.06em; }}
    .hud-pill-val {{ font-family: 'JetBrains Mono', monospace; font-size: 0.95rem; font-weight: 800; color: #f8fafc; }}

    /* PING DOT */
    .pulse-dot {{
        position: relative; display: inline-block; width: 8px; height: 8px;
        background: #34d399; border-radius: 50%; margin: 0 4px;
    }}
    .pulse-dot::after {{
        content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: #34d399; border-radius: 50%;
        animation: ping 1.6s cubic-bezier(0, 0, 0.2, 1) infinite;
    }}
    @keyframes ping {{ 75%, 100% {{ transform: scale(2.8); opacity: 0; }} }}

    /* THẺ CHỈ SỐ LUXURY (METRIC CARD) */
    .metric-card {{
        background: linear-gradient(160deg, rgba(30, 41, 59, 0.78) 0%, rgba(15, 23, 42, 0.92) 100%);
        padding: 20px 22px 16px; border-radius: 22px;
        border: 1px solid rgba(255, 255, 255, 0.13);
        border-top: 1px solid rgba(255, 255, 255, 0.26);
        color: var(--text-main); backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);
        position: relative; overflow: hidden;
        transition: all 0.32s cubic-bezier(0.16, 1, 0.3, 1); margin-bottom: 16px;
        box-shadow: 0 14px 32px -10px rgba(0, 0, 0, 0.55), inset 0 1px 0 rgba(255, 255, 255, 0.12);
    }}
    /* Viền sáng đỉnh thẻ */
    .metric-card::before {{
        content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
        background: linear-gradient(90deg, var(--glow, var(--blue-glow)), transparent 85%);
    }}
    /* Quầng sáng góc thẻ */
    .metric-card::after {{
        content: ''; position: absolute; top: -40px; right: -40px; width: 130px; height: 130px;
        background: radial-gradient(circle, color-mix(in srgb, var(--glow, var(--blue-glow)) 22%, transparent) 0%, transparent 70%);
        pointer-events: none; transition: all 0.4s ease;
    }}
    .metric-card:hover {{
        transform: translateY(-5px);
        border-color: color-mix(in srgb, var(--glow, var(--blue-glow)) 60%, rgba(255,255,255,0.2));
        box-shadow: 0 20px 42px -12px color-mix(in srgb, var(--glow, var(--blue-glow)) 32%, rgba(0,0,0,0.8));
    }}
    .metric-card:hover::after {{ transform: scale(1.35); }}

    .metric-header {{ display: flex; align-items: center; gap: 11px; margin-bottom: 12px; position: relative; z-index: 1; }}
    .metric-icon-box {{
        width: 42px; height: 42px; border-radius: 13px; display: flex; align-items: center; justify-content: center;
        font-size: 1.25rem;
        background: linear-gradient(135deg, color-mix(in srgb, var(--glow, var(--blue-glow)) 25%, transparent), rgba(15, 23, 42, 0.6));
        border: 1px solid color-mix(in srgb, var(--glow, var(--blue-glow)) 45%, transparent);
        box-shadow: 0 4px 12px color-mix(in srgb, var(--glow, var(--blue-glow)) 20%, transparent);
    }}
    .metric-title-group {{ flex: 1; display: flex; flex-direction: column; }}
    .metric-title {{ font-size: 0.78rem; font-weight: 800; text-transform: uppercase; color: #e2e8f0; letter-spacing: 0.03em; line-height: 1.2; }}
    .sensor-chip {{
        font-family: 'JetBrains Mono', monospace; font-size: 0.63rem; font-weight: 700;
        color: #94a3b8; letter-spacing: 0.04em; margin-top: 2px;
    }}

    .metric-value-box {{ display: flex; align-items: baseline; gap: 7px; margin-bottom: 10px; position: relative; z-index: 1; }}
    .metric-value {{
        font-family: 'JetBrains Mono', monospace; font-variant-numeric: tabular-nums;
        font-size: 2.15rem; font-weight: 800; line-height: 1; color: #ffffff; letter-spacing: -0.03em;
    }}
    .metric-unit {{ font-size: 0.82rem; color: #94a3b8; font-weight: 700; }}

    .badge-row {{ display: flex; justify-content: space-between; align-items: center; gap: 8px; margin-bottom: 8px; }}
    .pill-badge {{
        font-size: 0.73rem; font-weight: 700; display: inline-flex; align-items: center; gap: 5px;
        padding: 4px 11px; border-radius: 999px; width: fit-content;
        background: rgba(52, 211, 153, 0.15); color: #34d399; border: 1px solid rgba(52, 211, 153, 0.38);
    }}
    .pill-badge.warn {{ background: rgba(251, 191, 36, 0.15); color: #fbbf24; border-color: rgba(251, 191, 36, 0.4); }}
    .pill-badge.danger {{ background: rgba(251, 113, 133, 0.18); color: #fda4af; border-color: rgba(251, 113, 133, 0.48); }}

    /* THANH TIẾN TRÌNH NGƯỠNG VI MÔ (THRESHOLD GAUGE BAR) */
    .micro-gauge-track {{
        width: 100%; height: 5px; background: rgba(15, 23, 42, 0.8);
        border-radius: 999px; overflow: hidden; margin: 6px 0 2px;
        border: 1px solid rgba(255, 255, 255, 0.07);
    }}
    .micro-gauge-fill {{
        height: 100%; border-radius: 999px;
        transition: width 0.6s cubic-bezier(0.16, 1, 0.3, 1);
        box-shadow: 0 0 8px var(--glow, #38bdf8);
    }}

    /* THƯỚC QUANG PHỔ AQI EPA */
    .epa-spectrum-wrap {{ position: relative; margin: 14px 0 8px; padding-top: 6px; }}
    .epa-spectrum-bar {{
        height: 7px; width: 100%; border-radius: 999px;
        background: linear-gradient(90deg, #34d399 0%, #fbbf24 22%, #fb923c 42%, #f87171 62%, #c084fc 82%, #dc2626 100%);
        box-shadow: inset 0 1px 2px rgba(0,0,0,0.4);
    }}
    .epa-pointer {{
        position: absolute; top: -3px; transform: translateX(-50%);
        width: 12px; height: 12px; border-radius: 50%; background: #ffffff;
        border: 2.5px solid #0f172a; box-shadow: 0 0 10px #ffffff;
        transition: left 0.6s cubic-bezier(0.16, 1, 0.3, 1);
    }}

    /* KHỐI PIN 4 CELL TRỰC QUAN */
    .battery-cells {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 5px; margin: 14px 0 8px; }}
    .bat-cell {{
        height: 7px; border-radius: 4px; background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(255,255,255,0.1); overflow: hidden;
    }}
    .bat-cell-fill {{ height: 100%; border-radius: 3px; transition: width 0.5s ease; }}

    .metric-footer-stats {{
        display: flex; justify-content: space-between; align-items: center;
        margin-top: 10px; padding-top: 10px;
        border-top: 1px dashed rgba(255, 255, 255, 0.13);
        font-size: 0.72rem; color: #94a3b8; font-weight: 600;
    }}
    .metric-footer-stats b {{
        font-family: 'JetBrains Mono', monospace; color: #f1f5f9; font-weight: 700;
    }}

    /* TIÊU ĐỀ PHÂN KHU */
    .glass-section-title {{
        font-size: 1.02rem; font-weight: 800; color: #ffffff; letter-spacing: 0.01em;
        margin: 22px 0 14px; display: flex; align-items: center; gap: 10px;
    }}
    .glass-section-title span.sec-badge {{
        font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; font-weight: 700;
        color: #38bdf8; background: rgba(56, 189, 248, 0.12); border: 1px solid rgba(56, 189, 248, 0.28);
        padding: 2px 8px; border-radius: 6px;
    }}
    .glass-section-title::after {{
        content: ''; flex: 1; height: 1px;
        background: linear-gradient(90deg, rgba(56, 189, 248, 0.45), transparent);
    }}

    /* KHUNG KÍNH TỰ ĐỘNG CHO BIỂU ĐỒ PLOTLY */
    div[data-testid="stPlotlyChart"] {{
        background: linear-gradient(160deg, rgba(30, 41, 59, 0.68) 0%, rgba(15, 23, 42, 0.86) 100%);
        border: 1px solid rgba(255, 255, 255, 0.13);
        border-top: 1px solid rgba(255, 255, 255, 0.24);
        border-radius: 22px; padding: 10px 14px 6px;
        backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
        box-shadow: 0 14px 32px -10px rgba(0, 0, 0, 0.5);
        margin-bottom: 12px;
        transition: border-color 0.3s ease;
    }}
    div[data-testid="stPlotlyChart"]:hover {{
        border-color: rgba(56, 189, 248, 0.4);
    }}

    /* SIDEBAR CAO CẤP */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.98) 0%, rgba(2, 6, 23, 0.99) 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.12);
    }}
    .system-status-card {{
        background: rgba(30, 41, 59, 0.55); border-radius: 13px; padding: 10px 14px; margin-bottom: 8px;
        border: 1px solid rgba(255, 255, 255, 0.1); display: flex; justify-content: space-between; align-items: center;
        transition: all 0.2s ease;
    }}
    .system-status-card:hover {{ border-color: rgba(56, 189, 248, 0.35); background: rgba(30, 41, 59, 0.8); }}
    .system-label {{ font-size: 0.82rem; font-weight: 600; color: #cbd5e1; display: flex; align-items: center; gap: 8px; }}
    .system-val {{ font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; font-weight: 700; }}

    .stButton > button {{
        background: linear-gradient(135deg, #0284c7 0%, #6366f1 50%, #8b5cf6 100%) !important;
        color: #ffffff !important; border-radius: 14px !important;
        border: 1px solid rgba(255,255,255,0.2) !important; padding: 12px 20px !important;
        font-weight: 800 !important; font-size: 0.9rem !important;
        box-shadow: 0 8px 22px -4px rgba(99, 102, 241, 0.55) !important;
        transition: all 0.25s ease !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 28px -4px rgba(139, 92, 246, 0.75) !important;
    }}

    /* NÚT CHỌN MÔI TRƯỜNG (RADIO PILLS) */
    div[data-testid="stRadio"] > div {{ flex-direction: row; gap: 12px; background: transparent; }}
    div[data-testid="stRadio"] label {{
        background: rgba(30, 41, 59, 0.65) !important; padding: 10px 22px !important; border-radius: 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important; cursor: pointer; transition: all 0.25s ease;
    }}
    div[data-testid="stRadio"] label:hover {{
        border-color: rgba(56, 189, 248, 0.55) !important; background: rgba(56, 189, 248, 0.12) !important;
    }}
    div[data-testid="stRadio"] label[data-checked="true"] {{
        background: linear-gradient(135deg, rgba(56, 189, 248, 0.25), rgba(192, 132, 252, 0.25)) !important;
        border-color: #38bdf8 !important; box-shadow: 0 0 22px rgba(56, 189, 248, 0.32);
    }}
    div[data-testid="stRadio"] label > div:first-child {{ display: none !important; }}
    div[data-testid="stRadio"] label p {{ font-size: 0.94rem; color: #f1f5f9; font-weight: 700; margin: 0; }}

    /* THẺ ĐỐI SÁT & KHUYẾN NGHỊ */
    @keyframes slideInUp {{
        from {{ opacity: 0; transform: translateY(16px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    .compare-card {{
        background: linear-gradient(160deg, rgba(30, 41, 59, 0.72) 0%, rgba(15, 23, 42, 0.88) 100%);
        border: 1px solid rgba(255,255,255,0.12); border-top: 1px solid rgba(255,255,255,0.22);
        border-radius: 16px; padding: 14px 18px; margin-bottom: 12px; backdrop-filter: blur(14px);
        display: flex; flex-direction: column; gap: 6px;
        animation: slideInUp 0.45s cubic-bezier(0.16, 1, 0.3, 1) both;
    }}
    .compare-card:hover {{ border-color: rgba(56, 189, 248, 0.45); transform: translateX(3px); transition: all 0.25s ease; }}
    .compare-header {{ display: flex; justify-content: space-between; align-items: baseline; font-weight: 700; font-size: 0.9rem; color: #fff; }}
    .compare-bars {{ display: flex; gap: 4px; height: 8px; width: 100%; border-radius: 999px; overflow: hidden; background: rgba(2, 6, 23, 0.65); }}
    .bar-current {{ height: 100%; border-radius: 999px; transition: width 0.6s ease; box-shadow: 0 0 10px var(--c); }}
    .bar-past {{ height: 100%; border-radius: 999px; opacity: 0.45; transition: width 0.6s ease; }}

    .advisor-card {{
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.65), rgba(15, 23, 42, 0.85));
        border-radius: 16px; padding: 14px 16px; margin-bottom: 10px;
        border: 1px solid rgba(255,255,255,0.12); border-left: 3.5px solid var(--adv-color, #38bdf8);
        display: flex; align-items: center; gap: 14px; backdrop-filter: blur(12px);
        transition: transform 0.25s ease;
    }}
    .advisor-card:hover {{ transform: translateX(4px); }}
    .advisor-icon {{ font-size: 1.35rem; width: 42px; height: 42px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }}
    .advisor-text {{ font-size: 0.84rem; color: #e2e8f0; font-weight: 500; line-height: 1.45; }}

    #MainMenu, footer {{ visibility: hidden; }}
</style>
""", unsafe_allow_html=True)

st.markdown(celestial_html, unsafe_allow_html=True)

# ==========================================
# 3. THUẬT TOÁN KHÍ TƯỢNG & CHỈ SỐ AQI CHUẨN
# ==========================================
def calculate_heat_index(temp_c: float, hum: float) -> float:
    """Tính chỉ số nóng bức (Heat Index - Cảm giác thực tế) theo chuẩn NOAA."""
    t_f = temp_c * 9.0 / 5.0 + 32.0
    hi_f = 0.5 * (t_f + 61.0 + ((t_f - 68.0) * 1.2) + (hum * 0.094))
    if hi_f >= 80.0:
        hi_f = (
            -42.379
            + 2.04901523 * t_f
            + 10.14333127 * hum
            - 0.22475541 * t_f * hum
            - 0.00683783 * t_f * t_f
            - 0.05481717 * hum * hum
            + 0.00122874 * t_f * t_f * hum
            + 0.00085282 * t_f * hum * hum
            - 0.00000199 * t_f * t_f * hum * hum
        )
    return round((hi_f - 32.0) * 5.0 / 9.0, 1)

def calculate_dew_point(temp_c: float, hum: float) -> float:
    """Tính điểm sương (Dew Point) bằng công thức Magnus-Tetens."""
    a, b = 17.27, 237.7
    safe_hum = max(1.0, min(100.0, float(hum)))
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(safe_hum / 100.0)
    dp = (b * alpha) / (a - alpha)
    return round(dp, 1)

def estimate_pack_voltage(bat_pct: int) -> float:
    """Nội suy điện áp thực tế khối pin Li-ion 1S4P (3.20V - 4.20V)."""
    pct = max(0.0, min(100.0, float(bat_pct)))
    return round(3.25 + (pct / 100.0) * 0.93, 2)

AQI_PM25_TABLE = [
    (0.0, 12.0, 0, 50, "Tốt", "#34d399", "😊"),
    (12.0, 35.4, 51, 100, "Trung bình", "#fbbf24", "😐"),
    (35.4, 55.4, 101, 150, "Kém", "#fb923c", "😷"),
    (55.4, 150.4, 151, 200, "Xấu", "#f87171", "🤢"),
    (150.4, 250.4, 201, 300, "Rất xấu", "#c084fc", "🚨"),
    (250.4, 500.4, 301, 500, "Nguy hại", "#dc2626", "☠️"),
]

AQI_PM10_TABLE = [
    (0.0, 54.0, 0, 50, "Tốt", "#34d399", "😊"),
    (54.0, 154.0, 51, 100, "Trung bình", "#fbbf24", "😐"),
    (154.0, 254.0, 101, 150, "Kém", "#fb923c", "😷"),
    (254.0, 354.0, 151, 200, "Xấu", "#f87171", "🤢"),
    (354.0, 424.0, 201, 300, "Rất xấu", "#c084fc", "🚨"),
    (424.0, 604.0, 301, 500, "Nguy hại", "#dc2626", "☠️"),
]

def calc_aqi_sub(val: float, table: list):
    v = max(0.0, float(val))
    for c_lo, c_hi, i_lo, i_hi, cat, col, emo in table:
        if c_lo <= v <= c_hi:
            aqi_val = round(((i_hi - i_lo) / (c_hi - c_lo)) * (v - c_lo) + i_lo)
            return aqi_val, cat, col, emo
    return 500, "Nguy hại", "#dc2626", "☠️"

def overall_aqi_calc(d: dict):
    aqi_25 = calc_aqi_sub(d["pm25"], AQI_PM25_TABLE)
    aqi_10 = calc_aqi_sub(d["pm10"], AQI_PM10_TABLE)
    return aqi_25 if aqi_25[0] >= aqi_10[0] else aqi_10

def health_score_calc(d: dict):
    def sub(v, g, b):
        return 100.0 if v <= g else 0.0 if v >= b else 100.0 * (1.0 - (v - g) / (b - g))

    s = {
        "pm25": sub(d["pm25"], 12.0, 120.0),
        "pm10": sub(d["pm10"], 50.0, 250.0),
        "co2": sub(d["co2"], 700.0, 1800.0),
        "tvoc": sub(d["tvoc"], 200.0, 1000.0),
        "hcho": sub(d["hcho"], 0.04, 0.20),
    }
    weights = {"pm25": 0.35, "pm10": 0.15, "co2": 0.15, "tvoc": 0.15, "hcho": 0.20}
    final_score = round(sum(s[k] * weights[k] for k in weights), 1)
    if final_score >= 85: return final_score, "Xuất sắc", "#34d399"
    if final_score >= 70: return final_score, "Tốt", "#4ade80"
    if final_score >= 55: return final_score, "Khá", "#fbbf24"
    if final_score >= 40: return final_score, "Kém", "#fb923c"
    return final_score, "Nguy hại", "#f87171"

ENV_PROFILES = {
    "🏠 Nhà ở": {
        "desc": "Ưu tiên kiểm soát Formaldehyde nội thất, độ ẩm chống nấm mốc và bụi mịn phòng ngủ.",
        "co2": (800, 1200, "Thoáng khí", "Cần mở hé cửa", "Ngột ngạt · Mở cửa"),
        "pm25": (15.0, 35.4, "Trong lành", "Bụi nhẹ", "Ô nhiễm · Bật lọc khí"),
        "tvoc": (220, 500, "Khí sạch", "Có mùi sinh hoạt", "Nồng độ VOC cao"),
        "hcho": (0.06, 0.10, "An toàn nội thất", "Cần thông gió", "Vượt ngưỡng WHO!"),
        "temp": (24.0, 29.0),
        "hum": (45.0, 65.0),
    },
    "🏫 Trường học": {
        "desc": "Ưu tiên kiểm soát CO₂ chống buồn ngủ trong lớp học đông người và bụi phấn PM2.5/PM10.",
        "co2": (1000, 1500, "Đủ oxy · Tỉnh táo", "Dễ gây buồn ngủ", "Thiếu oxy · Mở cửa sổ"),
        "pm25": (20.0, 40.0, "An toàn học tập", "Có bụi phấn/cát", "Ảnh hưởng hô hấp"),
        "tvoc": (280, 600, "Bình thường", "Mùi dụng cụ/sơn", "Cần bật quạt hút"),
        "hcho": (0.06, 0.10, "An toàn", "Lưu ý bàn ghế mới", "Vượt ngưỡng an toàn"),
        "temp": (23.0, 28.5),
        "hum": (45.0, 70.0),
    },
    "🏢 Văn phòng": {
        "desc": "Ưu tiên kiểm soát hiệu suất làm việc (CO₂), khí thải từ máy in/thiết bị (TVOC) và nhiệt ẩm điều hòa.",
        "co2": (800, 1100, "Tối ưu tập trung", "Giảm sự tỉnh táo", "Hiệu suất giảm · Cấp khí tươi"),
        "pm25": (15.0, 35.0, "Đạt chuẩn Green", "Cần vệ sinh lọc ĐH", "Bụi mịn vượt chuẩn"),
        "tvoc": (200, 450, "Không khí sạch", "Mùi máy in/thảm", "TVOC cao · Thông gió"),
        "hcho": (0.05, 0.08, "Đạt chuẩn", "Lưu ý vách ngăn", "Cảnh báo HCHO"),
        "temp": (22.5, 26.5),
        "hum": (40.0, 60.0),
    },
}

# ==========================================
# 4. QUẢN LÝ DỮ LIỆU & ĐỒNG BỘ BLYNK SGP1
# ==========================================
def init_system_state():
    if st.session_state.get("_ready"):
        return
    st.session_state._ready = True
    now = datetime.now()
    records = []
    p1, p25, p10 = 11.5, 20.5, 29.0
    c2, tem, hum = 540.0, 28.0, 62.0
    tvc, hch = 115.0, 0.022

    for i in range(60):
        t = now - timedelta(minutes=60 - i)
        p1  = max(2.0, min(120.0, p1 + random.gauss(0.05, 0.6)))
        p25 = max(4.0, min(180.0, p25 + random.gauss(0.1, 0.9)))
        p10 = max(p25 + 3.0, min(250.0, p10 + random.gauss(0.1, 1.2)))
        c2  = max(400.0, min(2200.0, c2 + random.gauss(0.3, 6.5)))
        tem = max(18.0, min(39.0, tem + random.gauss(0.01, 0.05)))
        hum = max(30.0, min(88.0, hum + random.gauss(0.0, 0.45)))
        tvc = max(40.0, min(1200.0, tvc + random.gauss(0.1, 3.8)))
        hch = max(0.005, min(0.25, hch + random.gauss(0.0, 0.001)))
        records.append({
            "time": t, "pm1_0": p1, "pm25": p25, "pm10": p10,
            "co2": c2, "temp": tem, "hum": hum, "tvoc": tvc, "hcho": hch
        })
    st.session_state.history = records
    st.session_state.battery = 88
    st.session_state.blynk_status = "Đang kết nối..."
    st.session_state.last_sync = 0.0

init_system_state()

def get_current_reading() -> dict:
    return st.session_state.history[-1]

def safe_float(val, default: float) -> float:
    try:
        if isinstance(val, (list, tuple)):
            return float(val[0])
        return float(val)
    except (ValueError, TypeError, IndexError):
        return float(default)

def fetch_blynk_live(token: str):
    if not token or not token.strip():
        st.session_state.blynk_status = "Thiếu Token"
        return None
    try:
        url = f"https://sgp1.blynk.cloud/external/api/get?token={token.strip()}&v0&v1&v2&v3&v4&v5&v6&v7&v8"
        resp = requests.get(url, timeout=3.0)
        if resp.status_code == 200:
            data = resp.json()
            st.session_state.blynk_status = "Online (SGP1)"
            def parse_pin(pin, default):
                raw = data.get(pin.lower(), data.get(pin.upper(), default))
                return safe_float(raw, default)
            return {
                "pm1_0": parse_pin("v0", 14.0),
                "pm25": parse_pin("v1", 24.0),
                "pm10": parse_pin("v2", 32.0),
                "co2": parse_pin("v3", 580.0),
                "temp": parse_pin("v4", 28.5),
                "hum": parse_pin("v5", 65.0),
                "tvoc": parse_pin("v6", 125.0),
                "hcho": parse_pin("v7", 0.028),
                "bat": int(max(0, min(100, parse_pin("v8", 85.0)))),
            }
        else:
            st.session_state.blynk_status = f"Lỗi HTTP {resp.status_code}"
    except Exception:
        st.session_state.blynk_status = "Mất kết nối SGP1"
    return None

def sync_data_stream(source_mode: str, blynk_token: str, force: bool = False):
    if not force and (time.time() - st.session_state.last_sync < 2.5):
        return
    now = datetime.now()
    new_data = None

    if source_mode == "Blynk Cloud (Live)":
        b_res = fetch_blynk_live(blynk_token)
        if b_res:
            new_data = {
                "time": now,
                "pm1_0": b_res["pm1_0"], "pm25": b_res["pm25"], "pm10": b_res["pm10"],
                "co2": b_res["co2"], "temp": b_res["temp"], "hum": b_res["hum"],
                "tvoc": b_res["tvoc"], "hcho": b_res["hcho"],
            }
            st.session_state.battery = b_res["bat"]

    if new_data is None:
        last = get_current_reading()
        p1 = max(2.0, last["pm1_0"] + random.gauss(0, 0.8))
        p25 = max(4.0, last["pm25"] + random.gauss(0, 1.4))
        p10 = max(p25 + 2.0, last["pm10"] + random.gauss(0, 1.8))
        new_data = {
            "time": now,
            "pm1_0": p1,
            "pm25": p25,
            "pm10": p10,
            "co2": max(400.0, last["co2"] + random.gauss(0, 9.0)),
            "temp": max(16.0, min(42.0, last["temp"] + random.gauss(0, 0.05))),
            "hum": max(25.0, min(92.0, last["hum"] + random.gauss(0, 0.6))),
            "tvoc": max(45.0, last["tvoc"] + random.gauss(0, 5.0)),
            "hcho": max(0.005, last["hcho"] + random.gauss(0, 0.001)),
        }
        if source_mode != "Blynk Cloud (Live)":
            st.session_state.blynk_status = "Mô phỏng (Realtime)"

    st.session_state.history.append(new_data)
    st.session_state.history = st.session_state.history[-180:]
    st.session_state.last_sync = time.time()

# ==========================================
# 5. UI COMPONENTS: CUBIC BEZIER SPARKLINE & LUXURY CARDS
# ==========================================
def render_smooth_sparkline(values, color="#38bdf8", width=260, height=44):
    """Vẽ đồ thị SVG Cubic Bezier mượt mà kèm đường trung bình và tâm sáng đôi."""
    if not values or len(values) < 2:
        return ""
    vmin, vmax = min(values), max(values)
    vavg = sum(values) / len(values)
    rng = (vmax - vmin) if (vmax - vmin) > 1e-6 else 1.0

    coords = []
    for i, v in enumerate(values):
        x = (i / (len(values) - 1)) * (width - 10) + 5
        y = height - 6 - ((v - vmin) / rng) * (height - 12)
        coords.append((x, y))

    # Nội suy đường cong Cubic Bezier mượt mà
    path_cmds = [f"M {coords[0][0]:.1f},{coords[0][1]:.1f}"]
    for i in range(len(coords) - 1):
        x0, y0 = coords[i]
        x1, y1 = coords[i + 1]
        cpx1 = x0 + (x1 - x0) * 0.42
        cpx2 = x1 - (x1 - x0) * 0.42
        path_cmds.append(f"C {cpx1:.1f},{y0:.1f} {cpx2:.1f},{y1:.1f} {x1:.1f},{y1:.1f}")
    smooth_path = " ".join(path_cmds)

    avg_y = height - 6 - ((vavg - vmin) / rng) * (height - 12)
    last_x, last_y = coords[-1]
    gid = f"glow_{abs(hash(color + str(values[-1]))) % 99999}"

    return (
        f'<svg width="100%" height="{height}" viewBox="0 0 {width} {height}" preserveAspectRatio="none" style="margin-top:10px; overflow:visible;">'
        f'<defs>'
        f'<linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0%" stop-color="{color}" stop-opacity="0.42"/>'
        f'<stop offset="100%" stop-color="{color}" stop-opacity="0.0"/>'
        f'</linearGradient>'
        f'</defs>'
        f'<line x1="5" y1="{avg_y:.1f}" x2="{width-5}" y2="{avg_y:.1f}" stroke="rgba(255,255,255,0.14)" stroke-width="1" stroke-dasharray="3,3" />'
        f'<path d="{smooth_path} L {last_x:.1f},{height} L 5,{height} Z" fill="url(#{gid})"/>'
        f'<path d="{smooth_path}" stroke="{color}" stroke-width="2.3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<circle cx="{last_x:.1f}" cy="{last_y:.1f}" r="6" fill="{color}" opacity="0.28" />'
        f'<circle cx="{last_x:.1f}" cy="{last_y:.1f}" r="3.2" fill="#ffffff" stroke="{color}" stroke-width="2" style="filter: drop-shadow(0 0 6px {color});" />'
        f'</svg>'
    )

def draw_luxury_metric(
    icon, title, sensor_chip, value, unit, badge_text, badge_level,
    history_vals, glow_color, fill_pct=50.0, trend_val=None, custom_sub=None
):
    lvl_class = {"ok": "", "warn": "warn", "danger": "danger"}.get(badge_level, "")
    trend_html = ""
    if trend_val is not None:
        if abs(trend_val) < 0.8:
            trend_html = '<span style="font-size:0.71rem; color:#94a3b8; font-weight:700;">● Ổn định</span>'
        else:
            arr = "↑" if trend_val > 0 else "↓"
            c = "#f87171" if trend_val > 0 else "#34d399"
            trend_html = (
                f'<span class="mono-num" style="font-size:0.71rem; color:{c}; font-weight:700; '
                f'background:{c}1f; border:1px solid {c}44; padding:2px 8px; border-radius:8px;">{arr} {abs(trend_val):.1f}%</span>'
            )

    safe_pct = max(4.0, min(100.0, float(fill_pct)))
    stats_html = ""
    if history_vals:
        vmin, vmax = min(history_vals), max(history_vals)
        vavg = sum(history_vals) / len(history_vals)
        sub_desc = custom_sub if custom_sub else f"MIN <b>{vmin:.1f}</b> · AVG <b>{vavg:.1f}</b> · MAX <b>{vmax:.1f}</b>"
        stats_html = f'<div class="metric-footer-stats"><span>{sub_desc}</span></div>'

    st.markdown(
        f'<div class="metric-card" style="--glow: {glow_color};">'
        f'<div class="metric-header">'
        f'<div class="metric-icon-box">{icon}</div>'
        f'<div class="metric-title-group"><div class="metric-title">{title}</div><div class="sensor-chip">{sensor_chip}</div></div>'
        f'{trend_html}'
        f'</div>'
        f'<div class="metric-value-box"><span class="metric-value">{value}</span><span class="metric-unit">{unit}</span></div>'
        f'<div class="badge-row"><div class="pill-badge {lvl_class}">● {badge_text}</div>'
        f'<span class="mono-num" style="font-size:0.68rem; color:#94a3b8; font-weight:700;">{safe_pct:.0f}% ngưỡng</span></div>'
        f'<div class="micro-gauge-track"><div class="micro-gauge-fill" style="width:{safe_pct:.1f}%; background:{glow_color};"></div></div>'
        f'{render_smooth_sparkline(history_vals, glow_color)}{stats_html}'
        f'</div>',
        unsafe_allow_html=True,
    )

# ==========================================
# 6. SIDEBAR ĐIỀU KHIỂN TRẠM
# ==========================================
with st.sidebar:
    st.markdown(
        '<div style="display:flex; align-items:center; gap:12px; margin-bottom:16px; padding: 6px 4px;">'
        '<div style="width:42px; height:42px; border-radius:12px; background:linear-gradient(135deg, rgba(56,189,248,0.25), rgba(192,132,252,0.25)); border:1px solid rgba(56,189,248,0.4); display:flex; align-items:center; justify-content:center; font-size:1.5rem;">🍃</div>'
        '<div><div style="font-size:0.65rem; font-weight:800; color:#38bdf8; letter-spacing:0.1em;">TELEMETRY OS v4.2</div>'
        '<h2 style="margin:0; font-weight:900; background:linear-gradient(90deg, #ffffff, #93c5fd); '
        '-webkit-background-clip:text; -webkit-text-fill-color:transparent; font-size:1.28rem;">DSA SUPER PRO</h2></div></div>',
        unsafe_allow_html=True,
    )
    page = st.radio(
        "Điều hướng hệ thống",
        ("📊 Trung Tâm Giám Sát", "🎯 Radar & Đánh Giá AQI", "📈 Mạng Nhện Đối Sát"),
        label_visibility="collapsed",
    )
    st.markdown("<hr style='border-color: rgba(255, 255, 255, 0.1); margin: 16px 0;'>", unsafe_allow_html=True)

    source_mode = st.selectbox("Nguồn cấp dữ liệu", ["Mô phỏng (Realtime)", "Blynk Cloud (Live)"], index=1)
    blynk_token = st.text_input("Blynk Device Token", value="HiwqFyEFslSik__qXJMw5lDbFpUW82Yh", type="password")

    if st.button("⚡ Kích hoạt đo ngay (Wake-up)", use_container_width=True):
        try:
            requests.get(f"https://sgp1.blynk.cloud/external/api/update?token={blynk_token.strip()}&v9=1", timeout=2.5)
            st.toast("🚀 Đã gửi xung đánh thức trạm qua Virtual Pin V9!", icon="⚡")
        except Exception:
            st.toast("Không thể truyền xung tới Blynk SGP1!", icon="⚠️")
        time.sleep(0.8)
        sync_data_stream(source_mode, blynk_token, force=True)
        st.rerun()

    auto_refresh = st.toggle("🔄 Tự động đồng bộ (5s)", value=True)
    sync_data_stream(source_mode, blynk_token)

    st.markdown("<hr style='border-color: rgba(255, 255, 255, 0.1); margin: 16px 0;'>", unsafe_allow_html=True)
    st.markdown("<div style='color:#94a3b8; font-size:0.72rem; font-weight:800; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:10px;'>Chẩn đoán phần cứng</div>", unsafe_allow_html=True)

    c_cloud = "#34d399" if "Online" in st.session_state.blynk_status else "#fbbf24" if "Mô phỏng" in st.session_state.blynk_status else "#f87171"
    pulse_html = '<span class="pulse-dot"></span>' if "Online" in st.session_state.blynk_status else ''

    st.markdown(
        f'<div class="system-status-card"><span class="system-label">☁️ Blynk Cloud</span>'
        f'<span class="system-val" style="color:{c_cloud}; display:flex; align-items:center;">{pulse_html}{st.session_state.blynk_status}</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="system-status-card"><span class="system-label">📡 Vi điều khiển</span>'
        '<span class="system-val" style="color:#38bdf8;">ESP32 · Wi-Fi</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="system-status-card"><span class="system-label">📶 SSID Mạng</span>'
        '<span class="system-val" style="color:#c084fc;">LeThanhHa</span></div>',
        unsafe_allow_html=True,
    )

    bat_val = st.session_state.battery
    v_pack = estimate_pack_voltage(bat_val)
    c_bat = "#34d399" if bat_val > 50 else "#fbbf24" if bat_val > 20 else "#f87171"
    st.markdown(
        f'<div class="system-status-card"><span class="system-label">🔋 Nguồn 1S4P</span>'
        f'<span class="system-val" style="color:{c_bat};">{bat_val}% ({v_pack}V)</span></div>',
        unsafe_allow_html=True,
    )

    st.markdown("<hr style='border-color: rgba(255, 255, 255, 0.1); margin: 16px 0;'>", unsafe_allow_html=True)
    df_export = pd.DataFrame(st.session_state.history)
    st.download_button(
        "⬇️ Xuất nhật ký CSV",
        data=df_export.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"DSA_SuperPro_{datetime.now():%Y%m%d_%H%M%S}.csv",
        mime="text/csv",
        use_container_width=True,
    )

# ==========================================
# 7. TRANG 1: TRUNG TÂM GIÁM SÁT (ĐỦ 8 CẢM BIẾN)
# ==========================================
def render_main_overview():
    d = get_current_reading()
    recent = st.session_state.history[-30:]

    def calc_trend(vals):
        if len(vals) < 6 or abs(vals[-6]) < 1e-6:
            return 0.0
        return (vals[-1] - vals[-6]) / abs(vals[-6]) * 100.0

    aqi, aqi_cat, aqi_col, aqi_emo = overall_aqi_calc(d)
    h_score, h_label, h_color = health_score_calc(d)
    heat_idx = calculate_heat_index(d["temp"], d["hum"])
    dew_pt = calculate_dew_point(d["temp"], d["hum"])

    st.markdown('<div class="glass-section-title">📍 Không gian quan trắc & Quy chuẩn áp dụng <span class="sec-badge">PROFILE ENGINE</span></div>', unsafe_allow_html=True)
    env = st.radio(
        "Môi trường",
        ("🏠 Nhà ở", "🏫 Trường học", "🏢 Văn phòng"),
        horizontal=True,
        label_visibility="collapsed",
    )
    st.session_state.current_env = env
    prof = ENV_PROFILES[env]
    st.markdown(
        f"<div style='color:#94a3b8; font-size:0.84rem; margin: 4px 0 18px; padding: 8px 14px; "
        f"background: rgba(15,23,42,0.55); border-left: 3px solid #38bdf8; border-radius: 0 10px 10px 0;'>"
        f"ℹ️ <b>Tiêu chuẩn {env}:</b> {prof['desc']}</div>",
        unsafe_allow_html=True,
    )

    # 3 THẺ KPI TỔNG HỢP VỚI HIỆU ỨNG TRỰC QUAN
    k1, k2, k3 = st.columns(3, gap="medium")
    with k1:
        aqi_25_sub = calc_aqi_sub(d["pm25"], AQI_PM25_TABLE)[0]
        aqi_10_sub = calc_aqi_sub(d["pm10"], AQI_PM10_TABLE)[0]
        ptr_pos = min(97.0, max(3.0, (aqi / 300.0) * 100.0))
        st.markdown(
            f'<div class="metric-card" style="--glow: {aqi_col};">'
            f'<div class="metric-header">'
            f'<div class="metric-icon-box">{aqi_emo}</div>'
            f'<div class="metric-title-group"><div class="metric-title">CHỈ SỐ AQI TỔNG HỢP</div><div class="sensor-chip">US-EPA STANDARD</div></div>'
            f'<div class="pill-badge {"danger" if aqi > 150 else "warn" if aqi > 100 else ""}">● {aqi_cat}</div>'
            f'</div>'
            f'<div class="metric-value-box"><span class="metric-value" style="color:{aqi_col};">{aqi}</span><span class="metric-unit">AQI</span></div>'
            f'<div class="epa-spectrum-wrap"><div class="epa-spectrum-bar"></div><div class="epa-pointer" style="left:{ptr_pos:.1f}%;"></div></div>'
            f'<div class="metric-footer-stats"><span>AQI PM2.5: <b>{aqi_25_sub}</b></span><span>AQI PM10: <b>{aqi_10_sub}</b></span></div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with k2:
        st.markdown(
            f'<div class="metric-card" style="--glow: {h_color};">'
            f'<div class="metric-header">'
            f'<div class="metric-icon-box">🛡️</div>'
            f'<div class="metric-title-group"><div class="metric-title">CHỈ SỐ AN TOÀN SỨC KHỎE</div><div class="sensor-chip">MULTI-SENSOR FUSION</div></div>'
            f'<div class="pill-badge {"danger" if h_score < 45 else "warn" if h_score < 70 else ""}">● {h_label}</div>'
            f'</div>'
            f'<div class="metric-value-box"><span class="metric-value" style="color:{h_color};">{h_score}</span><span class="metric-unit">/ 100 điểm</span></div>'
            f'<div class="micro-gauge-track" style="height:7px; margin: 14px 0 8px;"><div class="micro-gauge-fill" style="width:{h_score}%; background:linear-gradient(90deg, #f87171, #fbbf24, #34d399);"></div></div>'
            f'<div class="metric-footer-stats"><span>Cảm giác thực: <b>{heat_idx}°C</b></span><span>Điểm sương: <b>{dew_pt}°C</b></span></div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with k3:
        bat = st.session_state.battery
        v_pack = estimate_pack_voltage(bat)
        bat_col = "#f87171" if bat <= 20 else "#fbbf24" if bat <= 45 else "#38bdf8"
        cells_html = ""
        for idx in range(4):
            c_fill = max(0.0, min(100.0, (bat - idx * 25) * 4.0))
            cells_html += f'<div class="bat-cell"><div class="bat-cell-fill" style="width:{c_fill}%; background:{bat_col};"></div></div>'

        st.markdown(
            f'<div class="metric-card" style="--glow: {bat_col};">'
            f'<div class="metric-header">'
            f'<div class="metric-icon-box">🔋</div>'
            f'<div class="metric-title-group"><div class="metric-title">QUẢN LÝ NĂNG LƯỢNG TRẠM</div><div class="sensor-chip">LI-ION 1S4P · 13.200mAh</div></div>'
            f'<div class="pill-badge {"danger" if bat <= 20 else ""}">● {"Cần sạc ngay!" if bat <= 20 else "Deep Sleep Ready"}</div>'
            f'</div>'
            f'<div class="metric-value-box"><span class="metric-value" style="color:{bat_col};">{bat}</span><span class="metric-unit">% · {v_pack}V</span></div>'
            f'<div class="battery-cells">{cells_html}</div>'
            f'<div class="metric-footer-stats"><span>Màn hình: <b>e-Paper 7.5"</b></span><span>Dòng nghỉ: <b>~18 µA</b></span></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown(f'<div class="glass-section-title">🔬 Ma trận 8 thông số cảm biến thời gian thực <span class="sec-badge">{env.upper()}</span></div>', unsafe_allow_html=True)

    def eval_level(val, warn_th, danger_th, labels):
        if val < warn_th:
            return "ok", labels[0]
        if val < danger_th:
            return "warn", labels[1]
        return "danger", labels[2]

    co2_lvl, co2_txt = eval_level(d["co2"], prof["co2"][0], prof["co2"][1], prof["co2"][2:])
    pm25_lvl, pm25_txt = eval_level(d["pm25"], prof["pm25"][0], prof["pm25"][1], prof["pm25"][2:])
    tvoc_lvl, tvoc_txt = eval_level(d["tvoc"], prof["tvoc"][0], prof["tvoc"][1], prof["tvoc"][2:])
    hcho_lvl, hcho_txt = eval_level(d["hcho"], prof["hcho"][0], prof["hcho"][1], prof["hcho"][2:])

    t_lo, t_hi = prof["temp"]
    temp_lvl = "ok" if t_lo <= d["temp"] <= t_hi else "warn" if (t_lo - 3 <= d["temp"] <= t_hi + 3) else "danger"
    temp_txt = "Lý tưởng" if temp_lvl == "ok" else "Chênh lệch nhiệt" if temp_lvl == "warn" else "Quá nóng/lạnh"

    h_lo, h_hi = prof["hum"]
    hum_lvl = "ok" if h_lo <= d["hum"] <= h_hi else "warn" if (30 <= d["hum"] <= 75) else "danger"
    hum_txt = "Cân bằng ẩm" if hum_lvl == "ok" else "Khí khô" if d["hum"] < h_lo else "Ẩm cao · Nguy cơ mốc"

    pm10_lvl = "ok" if d["pm10"] < 54 else "warn" if d["pm10"] < 154 else "danger"
    pm10_txt = "An toàn" if pm10_lvl == "ok" else "Bụi lơ lửng cao" if pm10_lvl == "warn" else "Ô nhiễm bụi thô"

    pm1_lvl = "ok" if d["pm1_0"] < 12 else "warn" if d["pm1_0"] < 30 else "danger"
    pm1_txt = "Rất sạch" if pm1_lvl == "ok" else "Bụi siêu mịn tăng" if pm1_lvl == "warn" else "Xâm nhập phế nang"

    # HÀNG 1: 4 THÔNG SỐ CHỦ CHỐT
    r1_c1, r1_c2, r1_c3, r1_c4 = st.columns(4, gap="medium")
    with r1_c1:
        draw_luxury_metric(
            "💨", "Khí CO₂", "NDIR SENSOR · V3", f'{d["co2"]:.0f}', "ppm", co2_txt, co2_lvl,
            [x["co2"] for x in recent], "#34d399", (d["co2"] / prof["co2"][1]) * 100, calc_trend([x["co2"] for x in recent])
        )
    with r1_c2:
        draw_luxury_metric(
            "🔸", "Bụi Mịn PM2.5", "LASER PMS7003 · V1", f'{d["pm25"]:.1f}', "µg/m³", pm25_txt, pm25_lvl,
            [x["pm25"] for x in recent], "#c084fc", (d["pm25"] / prof["pm25"][1]) * 100, calc_trend([x["pm25"] for x in recent])
        )
    with r1_c3:
        draw_luxury_metric(
            "☣️", "Hợp Chất TVOC", "SENSIRION SGP40 · V6", f'{d["tvoc"]:.0f}', "ppb", tvoc_txt, tvoc_lvl,
            [x["tvoc"] for x in recent], "#fbbf24", (d["tvoc"] / prof["tvoc"][1]) * 100, calc_trend([x["tvoc"] for x in recent])
        )
    with r1_c4:
        draw_luxury_metric(
            "⚗️", "Formaldehyde", "WINSEN ZE08-CH2O · V7", f'{d["hcho"]:.3f}', "mg/m³", hcho_txt, hcho_lvl,
            [x["hcho"] for x in recent], "#f472b6", (d["hcho"] / prof["hcho"][1]) * 100, calc_trend([x["hcho"] for x in recent]),
            custom_sub=f"Ngưỡng {env.split(' ')[1]}: <b>{prof['hcho'][0]:.2f}</b> · MAX <b>{max(x['hcho'] for x in recent):.3f}</b>"
        )

    # HÀNG 2: NHIỆT ẨM & PHỔ HẠT BỤI
    r2_c1, r2_c2, r2_c3, r2_c4 = st.columns(4, gap="medium")
    with r2_c1:
        draw_luxury_metric(
            "🌡️", "Nhiệt Độ", "SENSIRION SHT40 · V4", f'{d["temp"]:.1f}', "°C", temp_txt, temp_lvl,
            [x["temp"] for x in recent], "#fb923c", (d["temp"] / 40.0) * 100, calc_trend([x["temp"] for x in recent]),
            custom_sub=f"Heat Index: <b>{heat_idx}°C</b> · Chuẩn: <b>{t_lo:.0f}-{t_hi:.0f}°C</b>"
        )
    with r2_c2:
        mold_risk = "Cao" if (d["hum"] > 70 or (d["temp"] - dew_pt) < 3.0) else "Thấp"
        draw_luxury_metric(
            "💧", "Độ Ẩm Không Khí", "SENSIRION SHT40 · V5", f'{d["hum"]:.0f}', "%", hum_txt, hum_lvl,
            [x["hum"] for x in recent], "#22d3ee", d["hum"], calc_trend([x["hum"] for x in recent]),
            custom_sub=f"Điểm sương: <b>{dew_pt}°C</b> · Nấm mốc: <b>{mold_risk}</b>"
        )
    with r2_c3:
        draw_luxury_metric(
            "💠", "Bụi Thô PM10", "LASER PMS7003 · V2", f'{d["pm10"]:.1f}', "µg/m³", pm10_txt, pm10_lvl,
            [x["pm10"] for x in recent], "#818cf8", (d["pm10"] / 154.0) * 100, calc_trend([x["pm10"] for x in recent])
        )
    with r2_c4:
        draw_luxury_metric(
            "🔹", "Bụi Siêu Mịn PM1.0", "LASER PMS7003 · V0", f'{d["pm1_0"]:.1f}', "µg/m³", pm1_txt, pm1_lvl,
            [x["pm1_0"] for x in recent], "#38bdf8", (d["pm1_0"] / 35.0) * 100, calc_trend([x["pm1_0"] for x in recent])
        )

# ==========================================
# 8. TRANG 2: RADAR & ĐÁNH GIÁ AQI
# ==========================================
def render_aqi_and_radar():
    d = get_current_reading()
    aqi, cat, color, emoji = overall_aqi_calc(d)

    k1, k2, k3 = st.columns(3, gap="medium")
    with k1:
        st.markdown(
            f'<div class="metric-card" style="--glow: {color};">'
            f'<div class="metric-header"><div class="metric-icon-box">{emoji}</div>'
            f'<div class="metric-title-group"><div class="metric-title">MỨC ĐỘ Ô NHIỄM HIỆN TẠI</div><div class="sensor-chip">REALTIME EPA INDEX</div></div></div>'
            f'<div class="metric-value-box"><span class="metric-value" style="color:{color};">{aqi}</span><span class="metric-unit">AQI</span></div>'
            f'<div class="pill-badge {"danger" if aqi > 150 else "warn" if aqi > 100 else ""}">● Phân loại: {cat}</div></div>',
            unsafe_allow_html=True,
        )
    with k2:
        aqi_25 = calc_aqi_sub(d["pm25"], AQI_PM25_TABLE)[0]
        aqi_10 = calc_aqi_sub(d["pm10"], AQI_PM10_TABLE)[0]
        main_pol = "PM2.5" if aqi_25 >= aqi_10 else "PM10"
        main_val = d["pm25"] if main_pol == "PM2.5" else d["pm10"]
        st.markdown(
            f'<div class="metric-card" style="--glow: #fbbf24;">'
            f'<div class="metric-header"><div class="metric-icon-box">🎯</div>'
            f'<div class="metric-title-group"><div class="metric-title">TÁC NHÂN Ô NHIỄM CHÍNH</div><div class="sensor-chip">PRIMARY POLLUTANT</div></div></div>'
            f'<div class="metric-value-box"><span class="metric-value" style="color:#fbbf24;">{main_pol}</span><span class="metric-unit">Hạt lơ lửng</span></div>'
            f'<div class="pill-badge warn">● Nồng độ: {main_val:.1f} µg/m³</div></div>',
            unsafe_allow_html=True,
        )
    with k3:
        risk_level = "Thấp" if aqi <= 50 else "Trung bình" if aqi <= 100 else "Cao" if aqi <= 150 else "Rất cao"
        risk_color = "#34d399" if aqi <= 50 else "#fbbf24" if aqi <= 100 else "#fb923c" if aqi <= 150 else "#f87171"
        st.markdown(
            f'<div class="metric-card" style="--glow: {risk_color};">'
            f'<div class="metric-header"><div class="metric-icon-box">⚠️</div>'
            f'<div class="metric-title-group"><div class="metric-title">RỦI RO SỨC KHỎE HÔ HẤP</div><div class="sensor-chip">EXPOSURE ASSESSMENT</div></div></div>'
            f'<div class="metric-value-box"><span class="metric-value" style="color:{risk_color}; font-family:\'Plus Jakarta Sans\',sans-serif;">{risk_level}</span></div>'
            f'<div class="pill-badge" style="background:{risk_color}22; color:{risk_color}; border-color:{risk_color}44;">● Khuyến nghị tự động bên dưới</div></div>',
            unsafe_allow_html=True,
        )

    col_gauge, col_radar = st.columns([1, 1], gap="large")
    with col_gauge:
        st.markdown('<div class="glass-section-title">🧭 Đồng Hồ Đo Chỉ Số AQI <span class="sec-badge">GAUGE</span></div>', unsafe_allow_html=True)
        fig_g = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=aqi,
                number={"font": {"size": 68, "color": color, "family": "JetBrains Mono"}},
                gauge={
                    "axis": {"range": [0, 300], "tickcolor": "#94a3b8", "tickfont": {"color": "#cbd5e1", "size": 11, "family": "JetBrains Mono"}},
                    "bar": {"color": color, "thickness": 0.34},
                    "bgcolor": "rgba(15, 23, 42, 0.55)",
                    "borderwidth": 1,
                    "bordercolor": "rgba(255,255,255,0.1)",
                    "steps": [
                        {"range": [0, 50], "color": "rgba(52, 211, 153, 0.18)"},
                        {"range": [50, 100], "color": "rgba(251, 191, 36, 0.18)"},
                        {"range": [100, 150], "color": "rgba(251, 146, 60, 0.18)"},
                        {"range": [150, 200], "color": "rgba(248, 113, 113, 0.18)"},
                        {"range": [200, 300], "color": "rgba(192, 132, 252, 0.18)"},
                    ],
                    "threshold": {"line": {"color": "#ffffff", "width": 4}, "thickness": 0.85, "value": aqi},
                },
            )
        )
        fig_g.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font={"color": "white", "family": "Plus Jakarta Sans"},
            height=295, margin=dict(l=28, r=28, t=32, b=12),
        )
        st.plotly_chart(fig_g, use_container_width=True, config={"displayModeBar": False})

        st.markdown('<div class="glass-section-title">🩺 Khuyến Nghị Hành Động Thông Minh <span class="sec-badge">AI ADVISOR</span></div>', unsafe_allow_html=True)
        recs = []
        if aqi <= 50:
            recs.append(("🏃", "<b>Chất lượng khí lý tưởng:</b> Thoải mái mở cửa sổ đón gió tự nhiên và vận động.", "#34d399"))
        elif aqi <= 100:
            recs.append(("😷", "<b>Chất lượng trung bình:</b> Nhóm nhạy cảm nên hạn chế mở toang cửa hướng mặt đường.", "#fbbf24"))
        else:
            recs.append(("🚨", "<b>Cảnh báo bụi mịn:</b> Đóng kín cửa sổ, kích hoạt máy lọc không khí màng HEPA.", "#f87171"))

        if d["co2"] > 1000:
            recs.append(("🪟", f"<b>CO₂ cao ({d['co2']:.0f} ppm):</b> Bật quạt cấp khí tươi hoặc mở hé cửa đối lưu 10 phút.", "#fb923c"))
        else:
            recs.append(("🍃", f"<b>Độ thông thoáng tốt ({d['co2']:.0f} ppm):</b> Nồng độ oxy đảm bảo sự tỉnh táo.", "#34d399"))

        if d["hcho"] >= 0.08 or d["tvoc"] >= 350:
            recs.append(("☣️", "<b>Phát hiện khí hữu cơ/HCHO:</b> Kiểm tra mùi sơn, đồ gỗ mới hoặc hóa chất tẩy rửa.", "#f472b6"))
        else:
            recs.append(("🛡️", "<b>An toàn hóa chất bay hơi:</b> Nồng độ HCHO và TVOC nằm sâu trong ngưỡng an toàn.", "#38bdf8"))

        for icon, text, c in recs:
            st.markdown(
                f'<div class="advisor-card" style="--adv-color:{c};"><div class="advisor-icon" style="background:{c}22; color:{c}; border:1px solid {c}44;">{icon}</div>'
                f'<div class="advisor-text">{text}</div></div>',
                unsafe_allow_html=True,
            )

    with col_radar:
        st.markdown('<div class="glass-section-title">🕸️ Điểm An Toàn Đa Chiều <span class="sec-badge">100 = LÝ TƯỞNG</span></div>', unsafe_allow_html=True)
        rc = ["PM2.5", "PM10", "CO₂", "TVOC", "HCHO", "Độ Ẩm"]
        rv = [
            max(0, min(100, 100 - (d["pm25"] / 55.0) * 50)),
            max(0, min(100, 100 - (d["pm10"] / 150.0) * 50)),
            max(0, min(100, 100 - (max(0, d["co2"] - 400) / 1000.0) * 50)),
            max(0, min(100, 100 - (d["tvoc"] / 400.0) * 50)),
            max(0, min(100, 100 - (d["hcho"] / 0.1) * 50)),
            max(0, min(100, 100 - abs(d["hum"] - 55) * 1.5)),
        ]
        fig_r = go.Figure(
            go.Scatterpolar(
                r=rv + [rv[0]], theta=rc + [rc[0]], fill="toself",
                fillcolor="rgba(56, 189, 248, 0.28)", line=dict(color="#38bdf8", width=3),
                marker=dict(size=8, color="#c084fc", line=dict(color="#ffffff", width=1.5)),
            )
        )
        fig_r.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(color="#94a3b8", size=10, family="JetBrains Mono"), gridcolor="rgba(255,255,255,0.12)"),
                angularaxis=dict(tickfont=dict(color="#f8fafc", size=12, family="Plus Jakarta Sans"), gridcolor="rgba(255,255,255,0.12)"),
                bgcolor="rgba(15, 23, 42, 0.45)",
            ),
            paper_bgcolor="rgba(0,0,0,0)", height=525,
            margin=dict(l=45, r=45, t=35, b=35), font={"family": "Plus Jakarta Sans"},
            hoverlabel=dict(bgcolor="rgba(15,23,42,0.95)", bordercolor="#38bdf8", font=dict(color="white", family="Plus Jakarta Sans")),
        )
        st.plotly_chart(fig_r, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<div class="glass-section-title">📉 Diễn Biến AQI & Phổ Bụi Mịn (PM1.0 · PM2.5 · PM10) <span class="sec-badge">60 PHÚT QUA</span></div>', unsafe_allow_html=True)
    h = st.session_state.history
    times = [x["time"] for x in h]

    fig_hist = make_subplots(specs=[[{"secondary_y": True}]])
    fig_hist.add_trace(
        go.Scatter(
            x=times, y=[overall_aqi_calc(x)[0] for x in h], name="AQI Tổng hợp",
            mode="lines", line=dict(color=color, width=3, shape="spline"),
            fill="tozeroy", fillcolor="rgba(56, 189, 248, 0.10)",
        ),
        secondary_y=False,
    )
    fig_hist.add_trace(
        go.Scatter(x=times, y=[x["pm25"] for x in h], name="PM2.5 (µg/m³)", mode="lines", line=dict(color="#c084fc", width=2.2, dash="dot")),
        secondary_y=True,
    )
    fig_hist.add_trace(
        go.Scatter(x=times, y=[x["pm1_0"] for x in h], name="PM1.0 (µg/m³)", mode="lines", line=dict(color="#38bdf8", width=1.8, dash="dash")),
        secondary_y=True,
    )
    fig_hist.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#cbd5e1", "family": "Plus Jakarta Sans"},
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="Chỉ số AQI"),
        yaxis2=dict(gridcolor="rgba(255,255,255,0.0)", title="Nồng độ bụi (µg/m³)"),
        legend=dict(orientation="h", y=1.14, x=0.5, xanchor="center"),
        height=300, margin=dict(l=20, r=20, t=35, b=20), hovermode="x unified",
        hoverlabel=dict(bgcolor="rgba(15,23,42,0.95)", bordercolor="rgba(56,189,248,0.5)", font=dict(color="white")),
    )
    st.plotly_chart(fig_hist, use_container_width=True, config={"displayModeBar": False})

# ==========================================
# 9. TRANG 3: MẠNG NHỆN ĐỐI SÁT & TƯƠNG QUAN
# ==========================================
def render_deep_analytics():
    h = st.session_state.history
    cur = h[-1]
    one_hour_ago = min(h, key=lambda x: abs(x["time"] - (cur["time"] - timedelta(hours=1))))

    st.markdown('<div class="glass-section-title">🕸️ Đối Sát Mạng Nhện Hiện Tại vs Quá Khứ <span class="sec-badge">TIME-SHIFT ANALYSIS</span></div>', unsafe_allow_html=True)
    col_toggle, _ = st.columns([3.5, 6.5])
    with col_toggle:
        st.toggle("🔍 Hiển thị bảng đối sát chi tiết 8 thông số", key="show_comparison")

    def normalize_score(key, val):
        if key == "pm25": return max(0, min(100, 100 - (val / 55.0) * 50))
        if key == "pm10": return max(0, min(100, 100 - (val / 150.0) * 50))
        if key == "co2":  return max(0, min(100, 100 - (max(0, val - 400) / 1000.0) * 50))
        if key == "tvoc": return max(0, min(100, 100 - (val / 400.0) * 50))
        if key == "hcho": return max(0, min(100, 100 - (val / 0.1) * 50))
        if key == "temp": return max(0, min(100, 100 - abs(val - 26) * 5))
        if key == "hum":  return max(0, min(100, 100 - abs(val - 55) * 1.5))
        return 100

    categories = ["PM2.5", "PM10", "CO₂", "TVOC", "HCHO", "Nhiệt độ", "Độ ẩm"]
    keys = ["pm25", "pm10", "co2", "tvoc", "hcho", "temp", "hum"]
    scores_current = [normalize_score(k, cur[k]) for k in keys]
    scores_past = [normalize_score(k, one_hour_ago[k]) for k in keys]

    fig_spider = go.Figure()
    fig_spider.add_trace(
        go.Scatterpolar(
            r=scores_past + [scores_past[0]], theta=categories + [categories[0]],
            fill="toself", fillcolor="rgba(192, 132, 252, 0.12)",
            line=dict(color="#c084fc", width=2, dash="dot"), name="Mốc Đối Sát Trước",
        )
    )
    fig_spider.add_trace(
        go.Scatterpolar(
            r=scores_current + [scores_current[0]], theta=categories + [categories[0]],
            fill="toself", fillcolor="rgba(56, 189, 248, 0.28)",
            line=dict(color="#38bdf8", width=3), name="Hiện Tại",
        )
    )
    fig_spider.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(color="#94a3b8", size=10, family="JetBrains Mono"), gridcolor="rgba(255,255,255,0.12)"),
            angularaxis=dict(tickfont=dict(color="#ffffff", size=12), gridcolor="rgba(255,255,255,0.12)"),
            bgcolor="rgba(15, 23, 42, 0.45)",
        ),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=475,
        margin=dict(l=55, r=55, t=40, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="center", x=0.5, font=dict(color="#fff")),
    )

    if not st.session_state.show_comparison:
        _, col_center, _ = st.columns([1, 8, 1])
        with col_center:
            st.plotly_chart(fig_spider, use_container_width=True, config={"displayModeBar": False})
    else:
        col_radar, col_compare = st.columns([4.2, 5.8], gap="large")
        with col_radar:
            st.plotly_chart(fig_spider, use_container_width=True, config={"displayModeBar": False})

        with col_compare:
            def render_compare_card(label, current, past, unit, dec, max_val, color, delay_idx=0):
                w_cur = min(100.0, max(3.0, (current / max_val) * 100.0)) if max_val > 0 else 0
                w_past = min(100.0, max(3.0, (past / max_val) * 100.0)) if max_val > 0 else 0
                diff = current - past
                is_bad = (label in ["PM2.5", "PM10", "PM1.0", "CO₂", "TVOC", "HCHO"] and diff > 0) or (
                    label == "Nhiệt độ" and (current > 31 or current < 20)
                )
                trend_icon = "↑" if diff > 0 else "↓" if diff < 0 else "→"
                trend_color = "#f87171" if is_bad else "#34d399" if diff < 0 else "#94a3b8"

                st.markdown(
                    f"""
                    <div class="compare-card" style="animation-delay: {delay_idx * 0.05:.2f}s;">
                        <div class="compare-header">
                            <span>{label}</span>
                            <span class="mono-num" style="color:{color};">{current:.{dec}f} <span style="font-size:0.74rem; color:#94a3b8;">{unit}</span></span>
                        </div>
                        <div class="compare-bars"><div class="bar-current" style="width: {w_cur:.1f}%; background: {color}; --c: {color};"></div></div>
                        <div style="display:flex; justify-content:space-between; font-size:0.73rem; color:#94a3b8; margin-top:2px;">
                            <span>Hiện tại</span>
                            <span class="mono-num" style="color:{trend_color}; font-weight:700;">{trend_icon} {abs(diff):.{dec}f} {unit}</span>
                        </div>
                        <div class="compare-bars" style="height: 5px; margin-top:2px;"><div class="bar-past" style="width: {w_past:.1f}%; background: #94a3b8;"></div></div>
                        <div style="display:flex; justify-content:space-between; font-size:0.69rem; color:#64748b;">
                            <span>Mốc trước</span><span class="mono-num">{past:.{dec}f} {unit}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            r1, r2 = st.columns(2)
            with r1:
                render_compare_card("PM2.5", cur["pm25"], one_hour_ago["pm25"], "µg/m³", 1, 100, "#c084fc", 0)
                render_compare_card("PM10", cur["pm10"], one_hour_ago["pm10"], "µg/m³", 1, 200, "#818cf8", 1)
                render_compare_card("CO₂", cur["co2"], one_hour_ago["co2"], "ppm", 0, 2000, "#34d399", 2)
                render_compare_card("HCHO", cur["hcho"], one_hour_ago["hcho"], "mg/m³", 3, 0.2, "#f472b6", 3)
            with r2:
                render_compare_card("TVOC", cur["tvoc"], one_hour_ago["tvoc"], "ppb", 0, 1000, "#fbbf24", 4)
                render_compare_card("Nhiệt độ", cur["temp"], one_hour_ago["temp"], "°C", 1, 45, "#fb923c", 5)
                render_compare_card("Độ ẩm", cur["hum"], one_hour_ago["hum"], "%", 0, 100, "#22d3ee", 6)
                render_compare_card("PM1.0", cur["pm1_0"], one_hour_ago["pm1_0"], "µg/m³", 1, 50, "#38bdf8", 7)

    st.markdown('<div class="glass-section-title">📈 Phân Tích Tương Quan Khí Độc & Ngưỡng Cảnh Báo <span class="sec-badge">DUAL-AXIS TELEMETRY</span></div>', unsafe_allow_html=True)
    c_chart1, c_chart2 = st.columns(2, gap="medium")
    times = [x["time"] for x in h]

    with c_chart1:
        fig_c = go.Figure()
        fig_c.add_trace(
            go.Scatter(
                x=times, y=[x["co2"] for x in h], mode="lines", name="CO₂ (ppm)",
                line=dict(color="#34d399", width=3, shape="spline"),
                fill="tozeroy", fillcolor="rgba(52,211,153,0.14)",
            )
        )
        fig_c.add_hline(y=1000, line_dash="dash", line_color="#fbbf24", annotation_text="Ngưỡng khuyến nghị (1000 ppm)")
        fig_c.update_layout(
            title="Biến thiên nồng độ CO₂ (ppm)", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font={"color": "#cbd5e1", "family": "Plus Jakarta Sans"}, height=285,
            margin=dict(l=20, r=20, t=42, b=20), xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)"), hovermode="x unified",
            hoverlabel=dict(bgcolor="rgba(15,23,42,0.95)", bordercolor="#34d399", font=dict(color="white")),
        )
        st.plotly_chart(fig_c, use_container_width=True, config={"displayModeBar": False})

    with c_chart2:
        fig_t = make_subplots(specs=[[{"secondary_y": True}]])
        fig_t.add_trace(
            go.Scatter(
                x=times, y=[x["tvoc"] for x in h], mode="lines", name="TVOC (ppb)",
                line=dict(color="#fbbf24", width=3, shape="spline"),
                fill="tozeroy", fillcolor="rgba(251,191,36,0.12)",
            ),
            secondary_y=False,
        )
        fig_t.add_trace(
            go.Scatter(
                x=times, y=[x["hcho"] for x in h], mode="lines", name="HCHO (mg/m³)",
                line=dict(color="#f472b6", width=2.2, dash="dot"),
            ),
            secondary_y=True,
        )
        fig_t.update_layout(
            title="Tương quan TVOC (ppb) & Formaldehyde (mg/m³)",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font={"color": "#cbd5e1", "family": "Plus Jakarta Sans"}, height=285,
            margin=dict(l=20, r=20, t=42, b=20), xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
            legend=dict(orientation="h", y=1.15, x=0.5, xanchor="center"), hovermode="x unified",
            hoverlabel=dict(bgcolor="rgba(15,23,42,0.95)", bordercolor="#fbbf24", font=dict(color="white")),
        )
        st.plotly_chart(fig_t, use_container_width=True, config={"displayModeBar": False})

# ==========================================
# 10. MAIN VIEW & LIVE HUD BANNER
# ==========================================
def render_app():
    sync_data_stream(source_mode, blynk_token)

    now = datetime.now()
    hr = now.hour
    d = get_current_reading()
    aqi_val, aqi_cat, aqi_col, _ = overall_aqi_calc(d)

    greeting = (
        "🌅 Khởi đầu buổi sáng" if 5 <= hr < 11
        else "☀️ Buổi trưa năng lượng" if 11 <= hr < 14
        else "🌇 Buổi chiều tĩnh lặng" if 14 <= hr < 18
        else "🌙 Giám sát ban đêm"
    )

    st.markdown(
        f"""
        <div class="hero-banner">
            <div>
                <div class="hero-brand-tag"><span class="pulse-dot"></span>DSA SUPER PRO MAX · TELEMETRY STATION</div>
                <h1 class="hero-title">Trạm Quan Trắc Không Khí Thông Minh</h1>
                <div class="hero-sub">
                    <span>{greeting}</span>
                    <span>·</span>
                    <span>Đồng bộ: <b class="mono-num">{now:%H:%M:%S · %d/%m/%Y}</b></span>
                    <span>·</span>
                    <span style="color:#38bdf8; font-weight:700;">{st.session_state.blynk_status}</span>
                </div>
            </div>
            <div class="hero-hud-right">
                <div class="hud-pill">
                    <span class="hud-pill-label">VI KHÍ HẬU</span>
                    <span class="hud-pill-val" style="color:#fb923c;">{d['temp']:.1f}°C <span style="color:#64748b;">|</span> <span style="color:#22d3ee;">{d['hum']:.0f}%</span></span>
                </div>
                <div class="hud-pill">
                    <span class="hud-pill-label">CHỈ SỐ AQI</span>
                    <span class="hud-pill-val" style="color:{aqi_col};">{aqi_val} · {aqi_cat}</span>
                </div>
                <div class="hud-pill">
                    <span class="hud-pill-label">NGUỒN 1S4P</span>
                    <span class="hud-pill-val" style="color:#34d399;">{st.session_state.battery}% ({estimate_pack_voltage(st.session_state.battery)}V)</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if page.startswith("📊"):
        render_main_overview()
    elif page.startswith("🎯"):
        render_aqi_and_radar()
    else:
        render_deep_analytics()

if auto_refresh and hasattr(st, "fragment"):
    @st.fragment(run_every="5s")
    def live_fragment():
        render_app()
    live_fragment()
else:
    render_app()
    if auto_refresh:
        time.sleep(5)
        st.rerun()