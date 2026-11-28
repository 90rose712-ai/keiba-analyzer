import streamlit as st
import pandas as pd
import numpy as np
import os
import glob
import re

st.set_page_config(
    page_title="競馬予想10 完全版 - 的中重視厳選＆2026年間実証Vr",
    layout="wide",
    initial_sidebar_state="expanded"
)

def render_html(html_str):
    """空行・過剰インデントによるMarkdownコードブロック誤爆を完全に防ぐHTML描画ヘルパー"""
    cleaned = "\n".join(line.strip() for line in html_str.splitlines() if line.strip())
    st.markdown(cleaned, unsafe_allow_html=True)

st.markdown("""
<style>
    div[data-baseweb="select"] input {
        inputmode: none !important;
        pointer-events: none !important;
    }
    .date-header-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        border: 1px solid #3b82f6;
        padding: 6px 16px;
        border-radius: 20px;
        color: #60a5fa;
        font-size: 14.5px;
        font-weight: bold;
        margin-bottom: 12px;
    }
    .as-race-map-box {
        background: #111827;
        border: 1px solid #374151;
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 10px;
    }
    .as-race-chip-f1 {
        display: inline-block;
        background: linear-gradient(135deg, #7c3aed 0%, #b45309 100%);
        color: #fef08a;
        font-weight: 900;
        font-size: 12.5px;
        padding: 3px 9px;
        border-radius: 6px;
        border: 1.5px solid #fde047;
        margin: 3px 4px 3px 0;
        box-shadow: 0 0 8px rgba(167, 139, 250, 0.55);
    }
    .as-race-chip-std {
        display: inline-block;
        background: linear-gradient(135deg, #1d4ed8 0%, #4c1d95 100%);
        color: #e0e7ff;
        font-weight: bold;
        font-size: 12.5px;
        padding: 3px 9px;
        border-radius: 6px;
        border: 1px solid #818cf8;
        margin: 3px 4px 3px 0;
    }
    .as-race-chip-none {
        display: inline-block;
        background: #1f2937;
        color: #6b7280;
        font-size: 12px;
        padding: 3px 8px;
        border-radius: 6px;
        border: 1px solid #374151;
        margin: 3px 4px 3px 0;
    }
    .race-type-banner {
        padding: 12px 18px;
        border-radius: 8px;
        margin-bottom: 10px;
        font-size: 15px;
        font-weight: bold;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .race-type-s-class {
        background: linear-gradient(135deg, #7c2d12 0%, #b45309 30%, #dc2626 100%);
        color: #fef3c7;
        border: 2px solid #fde68a;
        box-shadow: 0 0 15px rgba(239, 68, 68, 0.6);
    }
    .race-type-a-class {
        background: linear-gradient(135deg, #7c2d12 0%, #b45309 50%, #d97706 100%);
        color: #fef3c7;
        border: 2px solid #fde68a;
        box-shadow: 0 0 10px rgba(245, 158, 11, 0.5);
    }
    .race-type-b-class {
        background: linear-gradient(135deg, #064e3b 0%, #047857 100%);
        color: #d1fae5;
        border: 2px solid #6ee7b7;
    }
    .race-type-c-class {
        background: #374151;
        color: #9ca3af;
        border: 1px solid #4b5563;
    }
    .vol-banner-solid {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
        border: 2px solid #38bdf8;
        color: #e0f2fe;
        padding: 12px 18px;
        border-radius: 8px;
        margin-bottom: 14px;
        box-shadow: 0 0 12px rgba(56, 189, 248, 0.35);
    }
    .vol-banner-std {
        background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
        border: 2px solid #fbbf24;
        color: #fef3c7;
        padding: 12px 18px;
        border-radius: 8px;
        margin-bottom: 14px;
    }
    .vol-banner-chaos {
        background: linear-gradient(135deg, #450a0a 0%, #7f1d1d 50%, #581c87 100%);
        border: 2px solid #f43f5e;
        color: #ffe4e6;
        padding: 12px 18px;
        border-radius: 8px;
        margin-bottom: 14px;
        box-shadow: 0 0 14px rgba(244, 63, 94, 0.45);
    }
    .recom-panel-go {
        background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
        border: 2px solid #10b981;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 20px;
    }
    .recom-title-go {
        font-size: 16px;
        font-weight: bold;
        color: #34d399;
        margin-bottom: 12px;
        border-bottom: 1px solid #374151;
        padding-bottom: 5px;
    }
    .recom-row {
        margin-bottom: 8px;
        font-size: 14.5px;
        line-height: 1.6;
    }
    .recom-block {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 14px;
    }
    .recom-val-num {
        color: #ffffff;
        font-weight: bold;
        font-size: 15.5px;
        letter-spacing: 1px;
    }
    .horse-card {
        background-color: #161e2e;
        border-left: 5px solid #238636;
        padding: 14px 18px;
        border-radius: 8px;
        margin-bottom: 14px;
        border: 1px solid #30363d;
        transition: opacity 0.2s ease;
    }
    .horse-card-fade {
        background-color: #111621;
        border-left: 5px solid #4b5563;
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 12px;
        border: 1px solid #272e3a;
        opacity: 0.45;
    }
    .horse-card-fade:hover {
        opacity: 0.85;
    }
    .horse-card-cut {
        background-color: #0d1117;
        border-left: 5px solid #374151;
        padding: 10px 16px;
        border-radius: 8px;
        margin-bottom: 10px;
        border: 1px dashed #374151;
        opacity: 0.30;
    }
    .horse-card-cut:hover {
        opacity: 0.78;
    }
    .horse-card-header {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 8px;
    }
    .horse-card-title {
        font-size: 18px;
        font-weight: bold;
        color: #ffffff;
    }
    .race-badge-title {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: #ffffff;
        font-weight: bold;
        font-size: 14px;
        padding: 2px 10px;
        border-radius: 6px;
        border: 1px solid #93c5fd;
        margin-right: 6px;
    }
    .horse-card-list {
        list-style-type: none;
        padding-left: 0;
        margin: 0;
    }
    .horse-card-list li {
        font-size: 13.5px;
        color: #c9d1d9;
        margin-bottom: 6px;
        line-height: 1.6;
    }
    .horse-card-list li::before {
        content: "• ";
        color: #58a6ff;
        font-weight: bold;
    }
    .badge-mark-honmei { display: inline-flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%); color: #ffffff; font-size: 12.5px; font-weight: 900; padding: 2px 8px; border-radius: 4px; border: 1px solid #fca5a5; margin-right: 6px; width: auto; height: auto; }
    .badge-mark-taikou { display: inline-flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: #ffffff; font-size: 12.5px; font-weight: 900; padding: 2px 8px; border-radius: 4px; border: 1px solid #93c5fd; margin-right: 6px; width: auto; height: auto; }
    .badge-mark-ana { display: inline-flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #d97706 0%, #b45309 100%); color: #ffffff; font-size: 12.5px; font-weight: 900; padding: 2px 8px; border-radius: 4px; border: 1px solid #fde68a; margin-right: 6px; width: auto; height: auto; }
    .badge-c-mark { display: inline-flex; align-items: center; background: linear-gradient(135deg, #b45309 0%, #d97706 100%); color: #fff; font-weight: 900; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #fde68a; margin-right: 4px; width: auto; height: auto; }
    .badge-c-horse { display: inline-flex; align-items: center; background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); color: #fff; font-weight: 900; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #93c5fd; margin-right: 4px; width: auto; height: auto; }
    .badge-cushion-fit { display: inline-flex; align-items: center; background-color: #064e3b; color: #6ee7b7; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #10b981; margin-right: 4px; width: auto; height: auto; }
    .badge-notebook-hit { display: inline-flex; align-items: center; background-color: #831843; color: #f472b6; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #db2777; margin-right: 4px; width: auto; height: auto; }
    .badge-stable-hit { display: inline-flex; align-items: center; background-color: #1e3a8a; color: #93c5fd; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #3b82f6; margin-right: 4px; width: auto; height: auto; }
    .badge-rescued { display: inline-flex; align-items: center; background-color: #581c87; color: #f0abfc; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #c084fc; margin-right: 4px; width: auto; height: auto; }
    .badge-as-intersect { display: inline-flex; align-items: center; background: linear-gradient(135deg, #7c3aed 0%, #4c1d95 100%); color: #f5f3ff; font-weight: 900; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #a78bfa; margin-right: 4px; width: auto; height: auto; }
    .badge-top3-win { display: inline-flex; align-items: center; background: linear-gradient(135deg, #b91c1c 0%, #7c2d12 50%, #d97706 100%); color: #ffffff; font-weight: 900; font-size: 12.5px; padding: 3px 10px; border-radius: 4px; border: 2px solid #fef08a; margin-right: 5px; box-shadow: 0 0 12px rgba(250,204,21,0.8); width: auto; height: auto; }

    .badge-complete-cut { display: inline-flex; align-items: center; background: #1f2937; color: #9ca3af; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px dashed #6b7280; margin-right: 4px; }
    .badge-zero5-fade { display: inline-flex; align-items: center; background: #374151; color: #d1d5db; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #6b7280; margin-right: 4px; }
    .badge-zero5-keep { display: inline-flex; align-items: center; background: linear-gradient(135deg, #0f766e 0%, #059669 100%); color: #ecfdf5; font-weight: 900; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #6ee7b7; margin-right: 4px; }

    .badge-course-win { display: inline-flex; align-items: center; background: linear-gradient(135deg, #b91c1c 0%, #ef4444 100%); color: #fff; font-weight: 900; font-size: 12.5px; padding: 3px 10px; border-radius: 6px; border: 2px solid #fca5a5; margin-right: 5px; box-shadow: 0 0 10px rgba(239, 68, 68, 0.7); width: auto; height: auto; }
    .badge-course-place { display: inline-flex; align-items: center; background: linear-gradient(135deg, #047857 0%, #10b981 100%); color: #fff; font-weight: 900; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #6ee7b7; margin-right: 4px; box-shadow: 0 0 8px rgba(16, 185, 129, 0.5); width: auto; height: auto; }
    .badge-course-ana { display: inline-flex; align-items: center; background: linear-gradient(135deg, #7c3aed 0%, #8b5cf6 100%); color: #fff; font-weight: 900; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #c4b5fd; margin-right: 4px; box-shadow: 0 0 8px rgba(139, 92, 246, 0.5); width: auto; height: auto; }

    .badge-new-same-hit { display: inline-flex; align-items: center; background: linear-gradient(135deg, #be123c 0%, #f59e0b 100%); color: #ffffff; font-weight: 900; font-size: 12.5px; padding: 3px 10px; border-radius: 6px; border: 2px solid #fef08a; margin-right: 5px; box-shadow: 0 0 12px rgba(245, 158, 11, 0.75); width: auto; height: auto; }
    .badge-new-same-axis { display: inline-flex; align-items: center; background: linear-gradient(135deg, #0f766e 0%, #0284c7 100%); color: #ffffff; font-weight: 900; font-size: 12px; padding: 2px 9px; border-radius: 5px; border: 1px solid #7dd3fc; margin-right: 4px; box-shadow: 0 0 8px rgba(14, 165, 233, 0.55); width: auto; height: auto; }

    .badge-golden-combo { display: inline-flex; align-items: center; background: linear-gradient(135deg, #991b1b 0%, #d97706 100%); color: #fef08a; font-weight: 900; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #fde047; margin-right: 4px; box-shadow: 0 0 8px rgba(245,158,11,0.5); width: auto; height: auto; }
    .badge-value-combo { display: inline-flex; align-items: center; background: linear-gradient(135deg, #065f46 0%, #0284c7 100%); color: #e0f2fe; font-weight: 900; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #7dd3fc; margin-right: 4px; width: auto; height: auto; }
    .badge-danger-fan { display: inline-flex; align-items: center; background-color: #7f1d1d; color: #fca5a5; font-weight: 900; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #ef4444; margin-right: 4px; width: auto; height: auto; }
    .badge-high-level { display: inline-flex; align-items: center; background-color: #065f46; color: #34d399; font-weight: 900; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #10b981; margin-right: 4px; width: auto; height: auto; }
    .badge-f-eval-s { display: inline-flex; align-items: center; background: linear-gradient(135deg, #7c2d12 0%, #dc2626 100%); color: #fff; font-weight: 900; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #f87171; margin-right: 4px; box-shadow: 0 0 8px rgba(239,68,68,0.5); width: auto; height: auto; }
    .badge-f-eval-a { display: inline-flex; align-items: center; background: linear-gradient(135deg, #b45309 0%, #d97706 100%); color: #fff; font-weight: 900; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #fde68a; margin-right: 4px; width: auto; height: auto; }
    .badge-f-eval-b { display: inline-flex; align-items: center; background: #2563eb; color: #fff; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #93c5fd; margin-right: 4px; width: auto; height: auto; }
    .badge-jockey-same-umaban { display: inline-flex; align-items: center; background: linear-gradient(135deg, #b45309 0%, #d97706 100%); color: #fff; font-weight: 900; font-size: 12.5px; padding: 3px 10px; border-radius: 4px; border: 1px solid #fde68a; margin-right: 6px; box-shadow: 0 0 10px rgba(245,158,11,0.7); width: auto; height: auto; }
    .val-rank-1 { color: #ffffff; background-color: #d97706; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #fde68a; }
    .val-rank-2 { color: #ffffff; background-color: #2563eb; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #93c5fd; }
    .val-rank-3 { color: #ffffff; background-color: #047857; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #6ee7b7; }
    .fup-badge-rank1-high { color: #ffffff; background: linear-gradient(135deg, #dc2626 0%, #d97706 100%); font-weight: 900; padding: 1px 7px; border-radius: 4px; border: 1px solid #fef08a; box-shadow: 0 0 8px rgba(245,158,11,0.6); }
    .fup-badge-rank1 { color: #ffffff; background-color: #d97706; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #fde68a; }
    .fup-badge-top { color: #ffffff; background: linear-gradient(135deg, #991b1b 0%, #dc2626 100%); font-weight: 900; padding: 1px 7px; border-radius: 4px; border: 1px solid #fca5a5; box-shadow: 0 0 6px rgba(239,68,68,0.5); }
    .fup-badge-mid { color: #ffffff; background: linear-gradient(135deg, #b45309 0%, #ea580c 100%); font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #fdba74; }
    .fup-badge-low { color: #c9d1d9; }
    .filter-result-box { background: linear-gradient(135deg, #111827 0%, #1f2937 100%); border: 2px solid #3b82f6; border-radius: 10px; padding: 14px 18px; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

ACE_TRAINERS = ['藤原', '杉山', '矢作', '中内田', '木村', '堀', '友道', '池添', '吉岡', '大竹', '斉藤', '音無', '国枝']

COURSE_WIN_PATTERNS = [
    ("中京", "ダ", 1800, "S1位", 35.7, 40.0),
    ("京都", "ダ", 1800, "F1位", 33.9, 40.0),
    ("新潟", "芝", 1800, "S1位", 32.3, 40.0),
    ("札幌", "ダ", 1700, "F1位", 31.5, 40.0),
    ("中山", "芝", 2000, "F1位", 31.2, 40.0),
    ("東京", "芝", 1800, "F1位", 31.0, 40.0),
    ("中京", "ダ", 0, "F1位", 30.5, 35.0),
    ("中京", "ダ", 0, "S1位", 28.7, 35.0),
    ("中京", "芝", 2000, "S1位", 30.8, 35.0),
    ("東京", "ダ", 2100, "F1位", 30.3, 35.0),
]

COURSE_PLACE_PATTERNS = [
    ("阪神", "芝", 1800, "F1位", 74.2, 35.0),
    ("東京", "芝", 2000, "F1位", 72.5, 35.0),
    ("東京", "芝", 1800, "F1位", 72.4, 35.0),
    ("京都", "芝", 1800, "F1位", 71.4, 35.0),
    ("東京", "ダ", 1600, "F1位", 63.3, 30.0),
    ("中山", "芝", 1600, "F1位", 63.3, 30.0),
    ("京都", "芝", 1800, "S1位", 62.9, 30.0),
    ("東京", "芝", 0, "F1位", 61.9, 30.0),
    ("新潟", "ダ", 0, "F1位", 60.3, 30.0),
]

COURSE_ANA_PATTERNS = [
    ("札幌", "ダ", 1700, "TUA1位", 58.5, 35.0),
    ("札幌", "芝", 1500, "Fup1位", 53.3, 30.0),
    ("函館", "芝", 1200, "Fup2_6以上", 53.1, 30.0),
    ("京都", "芝", 1400, "ARM1位", 52.8, 35.0),
    ("阪神", "ダ", 1800, "Fup2_6以上", 52.6, 30.0),
    ("函館", "ダ", 1700, "Fup2_6以上", 52.5, 30.0),
    ("京都", "芝", 1800, "ARM1位", 51.5, 35.0),
    ("函館", "芝", 1200, "TUA1位", 51.1, 30.0),
    ("福島", "芝", 0, "TUA1位", 48.4, 30.0),
    ("京都", "芝", 0, "ARM1位", 43.9, 25.0),
]

def clean_str(val):
    if pd.isnull(val): return ""
    return str(val).strip().replace("*", "").replace("$", "").replace(" ", "").replace(" ", "")

def get_cushion_category(cushion_val, venue_name):
    c_val = float(cushion_val)
    if venue_name == "札幌":
        if c_val <= 7.3: return "場内低<=7.3"
        elif c_val >= 7.7: return "場内高>=7.7"
        else: return "場内中7.4-7.6"
    elif venue_name == "函館":
        if c_val <= 7.2: return "場内低<=7.2"
        elif c_val >= 7.5: return "場内高>=7.5"
        else: return "場内中7.3-7.4"
    elif venue_name == "京都":
        if c_val <= 9.7: return "推奨低め<=9.7"
        elif c_val >= 10.5: return ">=10.5 超高"
        else: return "10.0-10.4 高"
    elif venue_name in ["中山", "中京"]:
        if c_val <= 9.3: return "やや低め8.6-9.4"
        elif c_val >= 10.0: return ">=10.5 超高" if c_val >= 10.5 else "10.0-10.4 高"
        else: return "9.5-9.9 標準高"
    elif venue_name == "福島":
        if c_val <= 8.7: return "<=8.5低"
        elif c_val >= 9.2: return "9.5-9.9 標準高"
        else: return "8.6-9.4 やや低"
    elif venue_name in ["新潟", "東京", "阪神", "小倉"]:
        if c_val <= 9.2: return "やや低め8.6-9.4"
        elif c_val >= 9.5: return "9.5-9.9 標準高"
        else: return "8.6-9.4 やや低"
    if c_val <= 8.5: return "<=8.5低"
    elif c_val <= 9.4: return "8.6-9.4 やや低"
    elif c_val <= 9.9: return "9.5-9.9 標準高"
    elif c_val <= 10.4: return "10.0-10.4高"
    else: return ">=10.5 超高"

CUSHION_DATA_BOOK = {
    ("阪神", "芝", 1800, "キズナ", "9.5-9.9 標準高"): ("最重要", "N56 勝19.6% 複41.1% 単421"),
    ("東京", "芝", 1600, "エピファネイア", "9.5-9.9 標準高"): ("最重要", "N98 勝13.3% 複39.8% 単277"),
    ("東京", "芝", 1400, "モーリス", "9.5-9.9 標準高"): ("最重要", "N69 勝10.1% 複29.0% 単408"),
    ("東京", "芝", 1800, "ディープインパクト", "9.5-9.9 標準高"): ("最重要", "N57 勝15.8% 複38.6% 単228"),
    ("東京", "芝", 2000, "キズナ", "8.6-9.4 やや低"): ("最重要", "N66 勝19.7% 複42.4% 単200"),
    ("中京", "芝", 2000, "ディープインパクト", "8.6-9.4 やや低"): ("最重要", "N61 勝18.0% 複42.6% 単178"),
    ("小倉", "芝", 1200, "ダイワメジャー", "9.5-9.9 標準高"): ("最重要", "N66 勝13.6% 複30.3% 単173"),
    ("函館", "芝", 1800, "キズナ", "<=8.5低"): ("最重要", "N62 勝17.7% 複38.7% 単143"),
    ("札幌", "芝", 2000, "オルフェーヴル", "<=8.5低"): ("最重要", "N57 勝15.8% 複35.1% 単136"),
    ("京都", "芝", 2000, "キタサンブラック", ">=10.5 超高"): ("最重要", "N38 勝21.1% 複50.0% 単149"),
}

def load_external_training_csvs():
    sakaro_df, wood_df = pd.DataFrame(), pd.DataFrame()
    for enc in ['utf-8-sig', 'utf-8', 'cp932', 'shift-jis']:
        try:
            if os.path.exists("出馬表_坂路.csv"):
                sakaro_df = pd.read_csv("出馬表_坂路.csv", encoding=enc)
                if not sakaro_df.empty: break
        except: pass
    for enc in ['utf-8-sig', 'utf-8', 'cp932', 'shift-jis']:
        try:
            if os.path.exists("出馬表_ウッド.csv"):
                wood_df = pd.read_csv("出馬表_ウッド.csv", encoding=enc)
                if not wood_df.empty: break
        except: pass
    return sakaro_df, wood_df

def read_csv_robust():
    candidates = ["当日全指数統合.csv", "データ統合.csv", "*全指数統合*.csv"]
    all_found = []
    for c in candidates:
        all_found.extend(glob.glob(c))
    if all_found:
        newest = max(all_found, key=os.path.getmtime)
        for enc in ['utf-8-sig', 'utf-8', 'cp932', 'shift-jis']:
            try:
                df = pd.read_csv(newest, encoding=enc, low_memory=False)
                if not df.empty and df.shape[1] >= 38:
                    return df, newest
            except Exception:
                continue
    return pd.DataFrame(), ""

def parse_and_judge_lap(l1_val, l2_val, t4_val):
    try:
        l1 = float(l1_val) if pd.notnull(l1_val) else 0.0
        l2 = float(l2_val) if pd.notnull(l2_val) else 0.0
        t4 = float(t4_val) if pd.notnull(t4_val) else 99.0
    except:
        return "判定不能", "#374151"

    if t4 > 56.0 or l1 > 13.0 or l1 <= 0: return "基準外(軽め)", "#374151"
    if l1 < l2:
        if l1 <= 11.9: return "A3 (終い11秒台加速🔥)", "#dc2626"
        elif 12.0 <= l2 <= 12.9 and 12.0 <= l1 <= 12.9: return "A2 (終い2Fともに12秒台加速)", "#d97706"
        elif l2 >= 13.0 and 12.0 <= l1 <= 12.9: return "A1 (終いのみ12秒台加速)", "#2563eb"
        else: return "A型 (加速)", "#047857"
    else:
        if l2 <= 11.9: return "B3 (2F目11秒台減速)", "#7c2d12"
        elif 12.0 <= l2 <= 12.9 and 12.0 <= l1 <= 12.9: return "B2 (終い2Fともに12秒台減速)", "#4b5563"
        elif 12.0 <= l2 <= 12.9 and l1 >= 13.0: return "B1 (2Fのみ12秒台減速)", "#4b5563"
        else: return "B型 (減速)", "#374151"

def build_training_summaries(sakaro_raw, wood_raw):
    sakaro_latest = {}
    sakaro_main_accel = {}
    if not sakaro_raw.empty:
        s_df = sakaro_raw.copy()
        s_df['馬名_clean'] = s_df['馬名'].astype(str).apply(clean_str)
        s_df['調教師_clean'] = s_df['調教師'].astype(str).apply(clean_str) if '調教師' in s_df.columns else ""
        s_df['年月日_num'] = pd.to_numeric(s_df['年月日'], errors='coerce')
        s_df['Time1_num'] = pd.to_numeric(s_df.get('Time1', s_df.get('Time4', np.nan)), errors='coerce')
        s_df['Lap2_num'] = pd.to_numeric(s_df.get('Lap2', np.nan), errors='coerce')
        s_df['Lap1_num'] = pd.to_numeric(s_df.get('Lap1', np.nan), errors='coerce')
        s_df['曜日_str'] = s_df['曜日'].astype(str).str.strip() if '曜日' in s_df.columns else ""

        max_ymd = s_df['年月日_num'].max()
        wk_cut = max_ymd - 5 if pd.notnull(max_ymd) else 0

        for h_name, grp in s_df.groupby('馬名_clean'):
            grp_sorted = grp.sort_values('年月日_num')
            wk_wm = grp_sorted[(grp_sorted['年月日_num'] >= wk_cut) & (grp_sorted['曜日_str'].isin(['水', '木']))]
            main_row = wk_wm.iloc[-1] if not wk_wm.empty else grp_sorted.iloc[-1]
            latest_row = grp_sorted.iloc[-1]

            sakaro_latest[h_name] = main_row
            for t_name, t_grp in grp_sorted.groupby('調教師_clean'):
                t_wm = t_grp[(t_grp['年月日_num'] >= wk_cut) & (t_grp['曜日_str'].isin(['水', '木']))]
                sakaro_latest[(h_name, t_name)] = t_wm.iloc[-1] if not t_wm.empty else t_grp.iloc[-1]

            t1, l2, l1 = main_row['Time1_num'], main_row['Lap2_num'], main_row['Lap1_num']
            is_acc = bool(pd.notnull(t1) and t1 <= 56.0 and pd.notnull(l1) and l1 <= 13.0 and pd.notnull(l2) and l1 < l2)
            if not is_acc:
                t1_l, l2_l, l1_l = latest_row['Time1_num'], latest_row['Lap2_num'], latest_row['Lap1_num']
                is_acc = bool(pd.notnull(t1_l) and t1_l <= 56.0 and pd.notnull(l1_l) and l1_l <= 13.0 and pd.notnull(l2_l) and l1_l < l2_l)
            sakaro_main_accel[h_name] = is_acc

    wood_latest = {}
    wood_has = set()
    wood_best_l1 = {}
    wood_main_accel_11 = {}
    if not wood_raw.empty:
        w_df = wood_raw.copy()
        w_df['馬名_clean'] = w_df['馬名'].astype(str).apply(clean_str)
        w_df['調教師_clean'] = w_df['調教師'].astype(str).apply(clean_str) if '調教師' in w_df.columns else ""
        w_df['年月日_num'] = pd.to_numeric(w_df['年月日'], errors='coerce')
        w_df['Lap2_num'] = pd.to_numeric(w_df.get('Lap2', np.nan), errors='coerce')
        w_df['Lap1_num'] = pd.to_numeric(w_df.get('Lap1', np.nan), errors='coerce')
        w_df['曜日_str'] = w_df['曜日'].astype(str).str.strip() if '曜日' in w_df.columns else ""

        max_ymd_w = w_df['年月日_num'].max()
        wk_cut_w = max_ymd_w - 5 if pd.notnull(max_ymd_w) else 0

        for h_name, grp in w_df.groupby('馬名_clean'):
            wood_has.add(h_name)
            grp_sorted = grp.sort_values('年月日_num')
            wk_wm = grp_sorted[(grp_sorted['年月日_num'] >= wk_cut_w) & (grp_sorted['曜日_str'].isin(['水', '木']))]
            main_row = wk_wm.iloc[-1] if not wk_wm.empty else grp_sorted.iloc[-1]
            latest_row = grp_sorted.iloc[-1]

            wood_latest[h_name] = main_row
            for t_name, t_grp in grp_sorted.groupby('調教師_clean'):
                t_wm = t_grp[(t_grp['年月日_num'] >= wk_cut_w) & (t_grp['曜日_str'].isin(['水', '木']))]
                wood_latest[(h_name, t_name)] = t_wm.iloc[-1] if not t_wm.empty else t_grp.iloc[-1]

            l1_min = grp_sorted['Lap1_num'].min()
            if pd.notnull(l1_min):
                wood_best_l1[h_name] = float(l1_min)

            l2, l1 = main_row['Lap2_num'], main_row['Lap1_num']
            is_w11 = bool(pd.notnull(l1) and pd.notnull(l2) and l1 < l2 and l1 <= 11.9)
            if not is_w11:
                l2_l, l1_l = latest_row['Lap2_num'], latest_row['Lap1_num']
                is_w11 = bool(pd.notnull(l1_l) and pd.notnull(l2_l) and l1_l < l2_l and l1_l <= 11.9)
            wood_main_accel_11[h_name] = is_w11

    return sakaro_latest, sakaro_main_accel, wood_latest, wood_has, wood_best_l1, wood_main_accel_11

def evaluate_new_same_umaban_targets(r, same_umaban_cnt):
    if same_umaban_cnt < 2:
        return 0.0, False, False, [], []

    f_rk = int(pd.to_numeric(r.get('F順位', 99), errors='coerce') or 99)
    s_rk = int(pd.to_numeric(r.get('S順位', 99), errors='coerce') or 99)
    has_wood = bool(r.get('has_wood', False))
    wood_best_l1_rk = pd.to_numeric(r.get('ウッド最速L1順位', np.nan), errors='coerce')
    wood_main_accel_11 = bool(r.get('wood_main_accel_11', False))
    sakaro_main_accel = bool(r.get('sakaro_main_accel', False))

    pts = 0.0
    is_strike = False
    is_axis = False
    labels = []
    short_tags = []

    if pd.notnull(wood_best_l1_rk) and int(wood_best_l1_rk) == 1:
        pts += 55.0
        is_strike = True
        labels.append(("new-same-hit", "👑【新同馬番・一撃特注】同馬番×ウッド最速L1 1位 [複43.6%/単265.6%]"))
        short_tags.append("W最速L1-1位")

    if same_umaban_cnt >= 3:
        pts += 40.0
        is_strike = True
        if has_wood:
            pts += 10.0
            labels.append(("new-same-hit", f"🔥【新同馬番・3回以上×W併用】({same_umaban_cnt}回騎乗)"))
            short_tags.append(f"{same_umaban_cnt}回×W")
        else:
            labels.append(("new-same-hit", f"🔥【新同馬番・3回以上騎乗】({same_umaban_cnt}回騎乗)"))
            short_tags.append(f"{same_umaban_cnt}回")

    if (f_rk <= 3 or s_rk <= 3) and (sakaro_main_accel or wood_main_accel_11):
        is_axis = True
        if sakaro_main_accel and wood_main_accel_11:
            pts += 50.0
            labels.append(("new-same-axis", "🎯【新同馬番・連軸鉄板】同馬番×F/S上位×坂路&W加速"))
            short_tags.append("F/S×坂&W加速")
        elif sakaro_main_accel:
            pts += 45.0
            labels.append(("new-same-axis", "🎯【新同馬番・連軸鉄板】同馬番×F/S上位×坂路本追加速"))
            short_tags.append("F/S×坂加速")
        else:
            pts += 40.0
            labels.append(("new-same-axis", "🎯【新同馬番・連軸鉄板】同馬番×F/S上位×W11秒台加速"))
            short_tags.append("F/S×W11s加速")

    if has_wood and not is_strike and not is_axis:
        pts += 15.0
        labels.append(("value", "🌲【同馬番×ウッド併用】調教裏付けあり"))

    return pts, is_strike, is_axis, labels, short_tags

def evaluate_f_index_strict(r, race_subset):
    try:
        f_val = float(r.get('F', 0.0) or 0.0)
        f_rk = int(r.get('F順位', 99) or 99)
    except:
        return "非該当", 0
    cond_a = (f_val >= 66.0)
    cond_b = (f_rk <= 3)
    try:
        f_series = pd.to_numeric(race_subset['F'], errors='coerce').dropna()
        if not f_series.empty:
            f_mean = f_series.mean()
            diffs = f_series - f_mean
            top_20_pct_n = int(np.ceil(len(f_series) * 0.2))
            top_diffs = diffs.sort_values(ascending=False).head(top_20_pct_n)
            my_diff = f_val - f_mean
            cond_c = (my_diff in top_diffs.values) or (my_diff >= top_diffs.min() if not top_diffs.empty else False)
        else: cond_c = False
    except: cond_c = False

    score = sum([1 for x in [cond_a, cond_b, cond_c] if x])
    if score == 3: return "S評価", 3
    elif score == 2: return "A評価", 2
    elif score == 1: return "B評価", 1
    else: return "非該当", 0

def get_race_balance_level(race_subset, track_type, class_name):
    try:
        s_top3_df = race_subset[pd.to_numeric(race_subset['S順位'], errors='coerce') <= 3]
        f_top3_df = race_subset[pd.to_numeric(race_subset['F順位'], errors='coerce') <= 3]
        s_vals = pd.to_numeric(s_top3_df['S'], errors='coerce').dropna()
        f_vals = pd.to_numeric(f_top3_df['F'], errors='coerce').dropna()
        if s_vals.empty: s_vals = pd.to_numeric(race_subset['S'], errors='coerce').dropna().sort_values(ascending=False).head(3)
        if f_vals.empty: f_vals = pd.to_numeric(race_subset['F'], errors='coerce').dropna().sort_values(ascending=False).head(3)
        s_avg_top3 = s_vals.mean() if len(s_vals) > 0 else 50.0
        f_avg_top3 = f_vals.mean() if len(f_vals) > 0 else 60.0
    except:
        return "標準", "標準"

    r_uid_str = str(race_subset['race_uid'].iloc[0]) if not race_subset.empty and 'race_uid' in race_subset.columns else ""
    m_rn = re.search(r'\d+', r_uid_str)
    r_no = int(m_rn.group()) if m_rn else 1

    if track_type == "芝":
        if "重賞" in class_name or "G" in class_name: s_low, s_high, f_low, f_high = 53.7, 56.7, 66.0, 68.3
        elif "OP" in class_name or "L" in class_name or "オープン" in class_name or r_no == 11: s_low, s_high, f_low, f_high = 53.3, 56.0, 62.7, 65.0
        elif "2勝" in class_name or "3勝" in class_name or r_no in [9, 10]: s_low, s_high, f_low, f_high = 53.3, 55.7, 64.0, 66.0
        else: s_low, s_high, f_low, f_high = 52.3, 55.3, 62.6, 65.0
    else:
        if "重賞" in class_name or "G" in class_name: s_low, s_high, f_low, f_high = 57.0, 58.3, 64.0, 67.3
        elif "OP" in class_name or "L" in class_name or "オープン" in class_name or r_no == 11: s_low, s_high, f_low, f_high = 53.7, 56.3, 63.7, 66.0
        elif "2勝" in class_name or "3勝" in class_name or r_no in [9, 10]: s_low, s_high, f_low, f_high = 54.3, 56.7, 63.7, 65.7
        else: s_low, s_high, f_low, f_high = 53.7, 56.0, 62.0, 64.3

    s_level = "高" if s_avg_top3 >= s_high else ("低" if s_avg_top3 <= s_low else "標準")
    f_level = "高" if f_avg_top3 >= f_high else ("低" if f_avg_top3 <= f_low else "標準")
    return s_level, f_level

def judge_race_volatility(race_df, s_lvl, f_lvl):
    if race_df.empty:
        return "⚖️ 標準〜小波乱（ヒモ荒れ注意）", "⚖️【標準:ヒモ荒れ】", "データなし", "vol-banner-std"
    is_newcomer = (race_df['間隔'].astype(str) == '初走').mean() > 0.5
    f_sorted = race_df.sort_values('F順位')
    f1_h = f_sorted.iloc[0]
    f1_val = float(pd.to_numeric(f1_h['F'], errors='coerce') or 0.0)
    f2_series = pd.to_numeric(race_df[race_df['F順位'] == 2]['F'], errors='coerce').dropna()
    f2_val = float(f2_series.max()) if not f2_series.empty else f1_val
    f_gap12 = f1_val - f2_val
    f_2_5_series = pd.to_numeric(race_df[(race_df['F順位'] >= 2) & (race_df['F順位'] <= 5)]['F'], errors='coerce').dropna()
    f_2_5_mean = float(f_2_5_series.mean()) if not f_2_5_series.empty else f1_val
    f_diff_25 = f1_val - f_2_5_mean
    s1_h = race_df.sort_values('S順位').iloc[0]
    s1_val = float(pd.to_numeric(s1_h['S'], errors='coerce') or 0.0)
    f1_s_rk = int(pd.to_numeric(f1_h['S順位'], errors='coerce') or 99)
    f1_c_rk = int(pd.to_numeric(f1_h['コース連順位'], errors='coerce') or 99)
    f1_k_rk = int(pd.to_numeric(f1_h['血統連順位'], errors='coerce') or 99)
    f1_in = float(pd.to_numeric(f1_h['印'], errors='coerce')) if pd.notna(f1_h['印']) else 2.0
    s1_f_rk = int(pd.to_numeric(s1_h['F順位'], errors='coerce') or 99)
    as_cnt = len(race_df[(race_df['S順位'] <= 3) & (race_df['F順位'] <= 3)])

    solid_score, chaos_score = 0, 0
    reasons = []

    if s_lvl == '低' and f_lvl == '低':
        if is_newcomer and f1_c_rk == 1: solid_score += 2; reasons.append("新馬戦×F1位馬がコース連1位も独占し適性突出")
        elif f_gap12 >= 15.0: solid_score += 1; reasons.append(f"両低水準だがF1位が2位に+{f_gap12:.0f}ptの大差")
        else: chaos_score += 3; reasons.append("S・Fとも低水準（波乱傾向）")
    elif s_lvl == '低':
        if f1_s_rk >= 6 and f1_val < 72.0: chaos_score += 3; reasons.append(f"S低水準×F1位のS順位が{f1_s_rk}位（人気でも割引）")
        elif f1_val >= 72.0 or (f1_val >= 68.0 and f_diff_25 >= 8.0 and f1_s_rk <= 5 and (f1_c_rk <= 3 or f1_k_rk <= 3 or as_cnt >= 2)): solid_score += 3; reasons.append(f"S低水準×F1位({f1_val:.0f})が絶対値・相手差とも抜けS5位以内確保")
        else: chaos_score += 2; reasons.append("S低水準だがF上位馬に適性裏付け不足")
    elif f_lvl == '低':
        if s1_val >= 60.0 and s1_f_rk <= 3: solid_score += 3; reasons.append(f"F低水準×S1位({s1_val:.0f})がS60以上＆F3位以内で抜ける")
        elif f_diff_25 >= 11.0 and s1_val >= 55.0: solid_score += 2; reasons.append(f"F低水準だがF1位が相手2〜5位平均に+{f_diff_25:.1f}ptの大差")
        else: chaos_score += 3; reasons.append(f"F低水準×S1位が割引条件に合致")
    else:
        has_aptitude = (f1_c_rk <= 3) or (f1_k_rk <= 3)
        if f1_val >= 70.0 and f_diff_25 >= 6.0 and has_aptitude and f1_in != 0: solid_score += 3; reasons.append(f"高水準×F1位({f1_val:.0f})が相手差+{f_diff_25:.1f}pt＆適性上位の鉄板条件")
        elif f1_val >= 71.0 and f_gap12 >= 8.0: solid_score += 3; reasons.append(f"高水準×F1位({f1_val:.0f})が2位に+{f_gap12:.0f}ptの能力断層")
        else:
            if not has_aptitude: chaos_score += 2; reasons.append(f"高水準だがF1位に適性裏付けなし")
            if f_diff_25 < 6.0 or f_gap12 <= 1.0: chaos_score += 2; reasons.append(f"高水準で上位密集の潰し合い(差{f_gap12:.0f}pt)")
            if f1_in == 0: chaos_score += 2; reasons.append("F1位が前走馬券内0頭(印=0)で信頼度低下")

    if solid_score >= 2 and chaos_score == 0: return ("🔒 堅い（順当・軸信頼） [検証実績: 1番人気複勝率88.2% / F1位複勝率82.4% / 波乱率0%]", "🔒【堅い:軸信頼】", " / ".join(reasons) + " ➔ 本命・F1位からの単勝・馬単・絞った連系勝負推奨", "vol-banner-solid")
    elif chaos_score >= 3: return ("🌪️ 荒れる（波乱・穴狙い） [検証実績: 波乱発生率73.3% / 1番人気複勝率20.0%(危険)]", "🌪️【波乱:穴狙い】", " / ".join(reasons) + " ➔ 人気馬過信禁物！コース連1位×S上位や特注穴からの3連複手広め推奨", "vol-banner-chaos")
    else: return ("⚖️ 標準〜小波乱（ヒモ荒れ注意） [検証実績: 軸は堅実も2〜3着に中穴台頭]", "⚖️【標準:ヒモ荒れ】", " / ".join(reasons) + " ➔ A群上位を軸にしつつ3列目・ワイド保険に中穴を絡める構成推奨", "vol-banner-std")

def evaluate_top3_win_pattern(r):
    f_val = float(pd.to_numeric(r.get('F', 0.0), errors='coerce') or 0.0)
    f_rk = int(pd.to_numeric(r.get('F順位', 99), errors='coerce') or 99)
    s_rk = int(pd.to_numeric(r.get('S順位', 99), errors='coerce') or 99)
    c_rk = int(pd.to_numeric(r.get('コース連順位', 99), errors='coerce') or 99)
    c_mark = clean_str(r.get('C(マーク)', ''))
    style = clean_str(r.get('前走脚質', ''))
    w_raw = pd.to_numeric(str(r.get('前場体重', '')).replace('kg', ''), errors='coerce')
    weight = float(w_raw) if pd.notnull(w_raw) else 470.0
    is_as = (f_rk <= 3) and (s_rk <= 3)
    is_triple = (f_rk == 1) and (s_rk <= 3) and (c_rk <= 3)

    if f_val >= 72.0 and style == '後' and weight >= 500.0: return 1, 45.5, 72.7, "👑【驚異の勝率1位:45.5%】F≧72×追込×500kg超"
    if c_mark != "" and is_as and style == '先' and 0 < weight <= 459.0: return 2, 42.5, 55.0, f"👑【驚異の勝率2位:42.5%】C({c_mark})×AS交差×先行×軽量"
    if f_val >= 72.0 and style == '中' and 0 < weight <= 459.0: return 3, 42.2, 73.4, "👑【驚異の勝率3位:42.2%】F≧72×中団×軽量"
    if is_triple and style == '中' and 0 < weight <= 459.0: return 4, 42.1, 63.2, "🔥【特注:42.1%】極限3重交差×中団×軽量"
    if f_val >= 72.0 and style == '先' and 0 < weight <= 459.0: return 4, 41.7, 77.1, "🔥【特注:41.7%】F≧72×先行×軽量"
    if f_val >= 72.0 and style == '先' and weight >= 500.0: return 4, 37.5, 70.8, "🔥【特注:37.5%】F≧72×先行×500kg超"
    return 0, 0.0, 0.0, ""

def evaluate_course_specific_patterns(r, venue_name, track_type, dist_val):
    f_rk = int(pd.to_numeric(r.get('F順位', 99), errors='coerce') or 99)
    s_rk = int(pd.to_numeric(r.get('S順位', 99), errors='coerce') or 99)
    tua_rk = int(pd.to_numeric(r.get('TUA順位', 99), errors='coerce') or 99)
    arm_rk = int(pd.to_numeric(r.get('ARM順位', 99), errors='coerce') or 99)
    fup_val = pd.to_numeric(r.get('Fup2', 0), errors='coerce')
    fup_rk = int(pd.to_numeric(r.get('Fup2順位', 99), errors='coerce') or 99)

    conds = { "F1位": f_rk == 1, "S1位": s_rk == 1, "TUA1位": tua_rk == 1, "ARM1位": arm_rk == 1, "Fup1位": fup_rk == 1, "Fup2_6以上": fup_val >= 6 }

    win_flag, place_flag, ana_flag = False, False, False
    bonuses, labels = [], []
    dist_val = int(dist_val) if str(dist_val).isdigit() else 0

    for v, t, d, cond_key, rate, pts in COURSE_WIN_PATTERNS:
        if v == venue_name and t == track_type and (d == 0 or d == dist_val):
            if conds.get(cond_key, False):
                win_flag = True
                lbl = f"👑【1着特注】{v}{t}{d if d>0 else ''}m×{cond_key} (勝率{rate}%)"
                bonuses.append(pts); labels.append((lbl, "course-win"))

    for v, t, d, cond_key, rate, pts in COURSE_PLACE_PATTERNS:
        if v == venue_name and t == track_type and (d == 0 or d == dist_val):
            if conds.get(cond_key, False):
                place_flag = True
                lbl = f"🎯【連軸鉄板】{v}{t}{d if d>0 else ''}m×{cond_key} (複勝率{rate}%)"
                bonuses.append(pts); labels.append((lbl, "course-place"))

    for v, t, d, cond_key, rate, pts in COURSE_ANA_PATTERNS:
        if v == venue_name and t == track_type and (d == 0 or d == dist_val):
            if conds.get(cond_key, False):
                ana_flag = True
                lbl = f"💣【穴馬覚醒】{v}{t}{d if d>0 else ''}m×{cond_key} (複勝率{rate}%)"
                bonuses.append(pts); labels.append((lbl, "course-ana"))

    total_pts = sum(bonuses)
    return total_pts, win_flag, place_flag, ana_flag, labels

def evaluate_annual_2026_ranking(r, same_umaban_cnt=1):
    """2026年年間通算（3,030R・41,354頭）の実証複勝率ランキング評価"""
    f_val = float(pd.to_numeric(r.get('F', 0.0), errors='coerce') or 0.0)
    f_rk = int(pd.to_numeric(r.get('F順位', 99), errors='coerce') or 99)
    s_val = float(pd.to_numeric(r.get('S', 0.0), errors='coerce') or 0.0)
    s_rk = int(pd.to_numeric(r.get('S順位', 99), errors='coerce') or 99)
    fup_rk = int(pd.to_numeric(r.get('Fup2順位', 99), errors='coerce') or 99)
    arm_rk = int(pd.to_numeric(r.get('ARM順位', 99), errors='coerce') or 99)
    tua_rk = int(pd.to_numeric(r.get('TUA順位', 99), errors='coerce') or 99)
    c_rk = int(pd.to_numeric(r.get('コース連順位', 99), errors='coerce') or 99)
    k_rk = int(pd.to_numeric(r.get('血統連順位', 99), errors='coerce') or 99)
    in_v = float(pd.to_numeric(r.get('印', 2), errors='coerce') or 2.0)
    pop = int(pd.to_numeric(r.get('人気順位', 99), errors='coerce') or 99)
    c_mark = clean_str(r.get('C(マーク)', '')).upper()
    trainer = clean_str(r.get('調教師', ''))
    track = r.get('track', '芝')

    is_as = (f_rk <= 3) and (s_rk <= 3)
    is_ace = any(ac in trainer for ac in ACE_TRAINERS)
    is_cnzm = c_mark in ['C', 'N', 'Z', 'M']
    cnt5 = sum([1 for x in [f_rk, s_rk, fup_rk, arm_rk, tua_rk] if x <= 3])

    if cnt5 == 0:
        if c_mark == 'N':
            return 47.1, "例外残し:指数0×N印[複47.1%]", 0
        if pop <= 3:
            return 46.1, "例外残し:指数0×1〜3人気[複46.1%]", 0
        if pop >= 10:
            return 3.9, "完全消し:10人気以下×主5指数0個[複3.9%]", 0
        elif pop >= 7:
            return 12.1, "薄表示:7〜9人気×主5指数0個[複12.1%]", 0
        else:
            return 22.5, "薄表示:4〜6人気×主5指数0個[複22.5%]", 0

    hits = []
    if is_as and f_val >= 72.0: hits.append((71.5, "1位:AS交差×F≧72"))
    if f_val >= 72.0: hits.append((68.8, "2位:F≧72[鉄板級]"))
    if f_rk == 1 and s_rk == 1: hits.append((62.3, "3位:F1位×S1位"))
    if cnt5 >= 4 and f_rk == 1: hits.append((61.4, "4位:主5重なり4個+×F1位"))
    if c_mark == 'N': hits.append((61.2, "特注:N印単体[勝42.7%]"))
    if is_cnzm and is_as: hits.append((59.3, f"5位:{c_mark}印×AS交差"))
    if f_rk == 1 and c_rk <= 3: hits.append((57.9, "6位:F1位×コース連上位"))
    if is_ace and is_as: hits.append((57.2, "7位:特選厩舎×AS交差"))
    if f_rk == 1 and (c_rk <= 3 or k_rk <= 3): hits.append((56.5, "8位:F1位×コース/血統連"))
    if f_rk == 1 and k_rk <= 3: hits.append((55.3, "9位:F1位×血統連上位"))
    if same_umaban_cnt >= 2 and is_as: hits.append((55.2, "10位:同馬番×AS交差"))
    if cnt5 == 5: hits.append((54.8, "11位:主5すべて重なり"))
    if is_cnzm and f_rk <= 3: hits.append((54.6, f"12位:{c_mark}印×F1〜3位"))
    if f_val >= 70.0 or s_val >= 60.0: hits.append((54.4, "13位:極限馬(F≧70/S≧60)"))
    if f_rk == 1: hits.append((53.8, "14位:F指数1位"))
    if is_as: hits.append((52.2, "15位:AS交差(F&S上位)"))
    if is_ace and f_rk <= 3: hits.append((50.7, "16位:特選厩舎×F上位"))
    if cnt5 >= 4: hits.append((50.4, "17位:主5重なり4個+"))
    if s_rk == 1: hits.append((48.5, "18位:S指数1位"))
    if in_v >= 3 and f_rk <= 3: hits.append((47.8, "19位:印≧3×F上位"))
    if same_umaban_cnt >= 2 and f_rk <= 3: hits.append((47.6, "20位:同馬番×F上位"))
    if track == 'ダ' and tua_rk <= 3 and f_rk <= 3: hits.append((47.1, "21位:ダ×TUA×F上位"))
    if c_rk == 1 and s_rk <= 3: hits.append((41.6, "24位:コース連1位×S上位"))
    if is_cnzm: hits.append((41.5, f"25位:{c_mark}印"))

    if same_umaban_cnt >= 2:
        w_best_rk = pd.to_numeric(r.get('ウッド最速L1順位', np.nan), errors='coerce')
        if pd.notnull(w_best_rk) and int(w_best_rk) == 1:
            hits.append((43.6, "特注:同馬番×W最速L1-1位[単265%]"))

    if not hits:
        base_by_cnt5 = {1: (19.3, "主5指数1個"), 2: (33.3, "主5指数2個"), 3: (41.3, "主5指数3個")}.get(cnt5, (15.0, "該当なし"))
        return base_by_cnt5[0], base_by_cnt5[1], cnt5

    hits.sort(key=lambda x: x[0], reverse=True)
    top_rate, top_label = hits[0]
    bonus = min(len([x for x in hits if x[0] >= 50.0]) * 0.3, 2.5)
    return round(top_rate + bonus, 1), top_label, cnt5

def calc_upgraded_dynamic_score(r, race_subset, venue_name, track_type, dist_val, c_category, class_name, s_row_laps, w_row_data, same_umaban_cnt=1):
    score = 0.0
    f_val = float(pd.to_numeric(r.get('F', 0.0), errors='coerce') or 0.0)
    f_rk = int(pd.to_numeric(r.get('F順位', 99), errors='coerce') or 99)
    fup = int(pd.to_numeric(r.get('Fup2', 0), errors='coerce') or 0)
    fup_rk = int(pd.to_numeric(r.get('Fup2順位', 99), errors='coerce') or 99)
    arm_val = float(pd.to_numeric(r.get('ARM', 0.0), errors='coerce') or 0.0)
    arm_rk = int(pd.to_numeric(r.get('ARM順位', 99), errors='coerce') or 99)
    tua_val = float(pd.to_numeric(r.get('TUA', 0.0), errors='coerce') or 0.0)
    tua_rk = int(pd.to_numeric(r.get('TUA順位', 99), errors='coerce') or 99)
    s_val = float(pd.to_numeric(r.get('S', 0.0), errors='coerce') or 0.0)
    s_rk = int(pd.to_numeric(r.get('S順位', 99), errors='coerce') or 99)
    pop = int(pd.to_numeric(r.get('人気順位', 99), errors='coerce') or 99)
    u_no = int(pd.to_numeric(r.get('馬番', 99), errors='coerce') or 99)

    trainer = clean_str(r.get('調教師', ''))
    track_change = clean_str(r.get('芝ダート変わり', ''))
    run_style = clean_str(r.get('前走脚質', ''))
    interval = str(r.get('間隔', ''))
    weight = float(pd.to_numeric(str(r.get('前場体重', '480')).replace('kg', ''), errors='coerce') or 480.0)
    c_mark_str = clean_str(r.get('C(マーク)', '')).upper()

    cnt5 = sum([1 for x in [f_rk, s_rk, fup_rk, arm_rk, tua_rk] if x <= 3])
    is_zero5_n_keep = (cnt5 == 0) and (c_mark_str == 'N')
    is_zero5_pop_keep = (cnt5 == 0) and (c_mark_str != 'N') and (pop <= 3)
    is_complete_cut = (cnt5 == 0) and (c_mark_str != 'N') and (pop >= 10)
    is_zero5_fade = (cnt5 == 0) and (c_mark_str != 'N') and (pop >= 4) and (not is_complete_cut)

    f_eval_label, _ = evaluate_f_index_strict(r, race_subset)
    if f_eval_label == "S評価": score += 60.0
    elif f_eval_label == "A評価": score += 40.0
    elif f_eval_label == "B評価": score += 20.0

    in_val = pd.to_numeric(r.get('印', 2), errors='coerce')
    if pd.isna(in_val): in_val = 2.0

    if in_val == 0: score -= 50.0
    elif in_val == 1: score += 10.0
    elif 3 <= in_val <= 4: score += 25.0
    elif 5 <= in_val <= 7: score += 45.0
    elif 8 <= in_val <= 10: score += 75.0
    elif in_val >= 11: score += 110.0

    m2_val = pd.to_numeric(r.get('M2', 0), errors='coerce')
    if not pd.isna(m2_val) and m2_val >= 5: score += min(m2_val * 8.0, 70.0)

    hc_rk = int(pd.to_numeric(r.get('坂路調順位', 99), errors='coerce') or 99)
    c_rk = int(pd.to_numeric(r.get('コース連順位', 99), errors='coerce') or 99)
    k_rk = int(pd.to_numeric(r.get('血統連順位', 99), errors='coerce') or 99)
    b_rk = int(pd.to_numeric(r.get('バランス順位', 99), errors='coerce') or 99)

    nb_hits, stable_hits, combo_hits = [], [], []
    is_as_cross = (f_rk <= 3) and (s_rk <= 3)
    is_ace_stbl = any(ac in trainer for ac in ACE_TRAINERS)

    if cnt5 >= 4 and f_rk == 1:
        score += 45.0
        combo_hits.append(("golden", "👑 主5重なり4個+×F1位 [年間複61.4%]"))
    elif cnt5 >= 4:
        score += 25.0
        combo_hits.append(("value", f"⭐ 主5指数{cnt5}個重なり [年間複50.4%]"))

    top3_win_rk, _, _, top3_lbl = evaluate_top3_win_pattern(r)
    if top3_win_rk == 1: score += 85.0; combo_hits.append(("top3_win", top3_lbl))
    elif top3_win_rk in [2, 3]: score += 80.0; combo_hits.append(("top3_win", top3_lbl))
    elif top3_win_rk == 4: score += 70.0; combo_hits.append(("top3_win", top3_lbl))

    course_pts, is_c_win, is_c_place, is_c_ana, c_labels = evaluate_course_specific_patterns(r, venue_name, track_type, dist_val)
    score += course_pts
    for lbl_text, lbl_type in c_labels:
        combo_hits.append((lbl_type, lbl_text))

    new_same_pts, is_same_strike, is_same_axis, same_labels, same_short_tags = evaluate_new_same_umaban_targets(r, same_umaban_cnt)
    score += new_same_pts
    combo_hits.extend(same_labels)

    if venue_name == "京都" and track_type == "芝" and int(dist_val) == 2200:
        if f_rk == 1 or f_val >= 70.0: score += 40.0; combo_hits.append(("golden", "🎯 京都芝2200特注: F1位/F≧70[複83〜85%]"))
        if f_rk == 1 and c_rk <= 3: score += 35.0; combo_hits.append(("golden", "👑 京都芝2200絶対軸: F1位×コース連上位[複100%]"))
        if run_style == "先" or is_as_cross: score += 20.0
        elif run_style == "後": score -= 20.0; combo_hits.append(("value", "⚠️ 京都芝2200割引: 前走後方脚質"))
        if 5 <= u_no <= 7: score += 25.0; combo_hits.append(("value", f"🎯 京都芝2200絶好枠({u_no}番)"))
        elif u_no in [11, 13]: score -= 20.0

    if f_val >= 72.0: score += 65.0; combo_hits.append(("golden", "👑 鉄板級 F≧72 [年間複68.8%]"))
    elif f_val >= 70.0 and s_rk <= 3: score += 45.0; combo_hits.append(("golden", "🔥 極限クロス(F≧70×S上位)"))
    if f_rk == 1 and s_rk <= 3 and c_rk <= 3: score += 75.0; combo_hits.append(("golden", "🌟 極限3重交差(F1位×S上位×コース連上位)"))
    elif f_rk == 1 and c_rk <= 3: score += 50.0; combo_hits.append(("golden", "🎯 F1位×コース連上位[年間複57.9%]"))
    if f_rk == 1 and c_rk == 1: score += 25.0; combo_hits.append(("golden", "💯 F1位×コース連1位(完全一致)"))
    if f_val >= 70.0 and k_rk <= 3: score += 45.0; combo_hits.append(("golden", "🧬 F≧70×血統連上位[高信頼]"))
    elif f_rk == 1 and k_rk <= 3: score += 35.0; combo_hits.append(("golden", "🧬 F1位×血統連上位[年間複55.3%]"))

    if c_mark_str == 'N': score += 55.0; combo_hits.append(("golden", "👑 N印特注 [年間勝42.7%/複61.2%]"))
    if c_mark_str and is_as_cross: score += 60.0; combo_hits.append(("golden", f"🌟 C({c_mark_str})×AS交差 [年間複59.3%]"))
    elif c_mark_str and f_rk <= 3: score += 45.0; combo_hits.append(("golden", f"🌟 C({c_mark_str})×F上位 [年間複54.6%]"))
    if is_ace_stbl and is_as_cross: score += 45.0; combo_hits.append(("golden", "🌟 特選厩舎×AS交差 [年間複57.2%]"))
    elif is_ace_stbl and f_rk <= 3: score += 25.0; combo_hits.append(("value", "⭐ 特選厩舎×F上位 [年間複50.7%]"))
    if same_umaban_cnt >= 2 and is_as_cross: score += 45.0; combo_hits.append(("golden", "🌟 同馬番複数×AS交差 [年間複55.2%]"))
    elif same_umaban_cnt >= 2 and f_rk <= 3: score += 30.0; combo_hits.append(("value", "⭐ 同馬番複数×F上位 [年間複47.6%]"))
    if in_val >= 3 and f_rk <= 3: score += 30.0; combo_hits.append(("value", f"🌟 前走{int(in_val)}頭馬券内×F上位 [年間複47.8%]"))
    if track_type == 'ダ' and tua_rk == 1 and f_rk <= 3: score += 65.0; combo_hits.append(("golden", "🚀 ダート最強軸(TUA1位×F上位)[年間複44.0%]"))
    elif track_type == '芝' and tua_rk == 1 and f_rk <= 3: score += 40.0; combo_hits.append(("value", "🌐 TUA1位×F上位"))
    if track_type == 'ダ' and f_rk == 1 and tua_rk <= 3 and tua_rk != 1: score += 45.0; combo_hits.append(("golden", "🔥 ダート黄金(F1位×TUA上位)"))
    if c_rk == 1 and s_rk <= 3: score += 45.0; combo_hits.append(("value", "💣 歪み激走特注(コース連1位×S上位)[年間複41.6%]"))
    if f_rk <= 3 and c_rk <= 3 and k_rk <= 3: score += 40.0; combo_hits.append(("value", "💎 3複合上位(F×コース連×血統連)"))
    if f_rk <= 3 and hc_rk <= 3 and c_rk <= 3: score += 40.0; combo_hits.append(("value", "⚡ 3複合上位(F×坂路調×コース連)"))
    if track_type == '芝' and s_rk <= 3 and fup_rk <= 3: score += 30.0; combo_hits.append(("value", "🌱 芝ヒモ特注(S上位×Fup2上位)"))
    if s_val >= 60.0: score += 30.0; combo_hits.append(("value", "⚡ 高S指数(S≧60)"))

    s_lvl_r, f_lvl_r = get_race_balance_level(race_subset, track_type, class_name)
    if s_lvl_r == "低" and f_rk <= 3 and f_val >= 68.0 and s_rk <= 5: score += 35.0; combo_hits.append(("golden", "📘 NB信頼: S低水準×F上位(F≧68)"))
    elif s_lvl_r == "低" and f_rk <= 3 and s_rk >= 6 and f_val < 72.0: score -= 20.0; combo_hits.append(("value", "⚠️ NB割引: S低水準×F上位のみ(S6位以下)"))
    if f_lvl_r == "低" and s_rk <= 3 and s_val >= 60.0 and f_rk <= 3: score += 35.0; combo_hits.append(("golden", "📘 NB信頼: F低水準×S≧60＆F上位"))
    elif f_lvl_r == "低" and s_rk <= 3 and f_rk >= 4: score -= 15.0; combo_hits.append(("value", "⚠️ NB割引: F低水準×S上位(F4位以下)"))

    if track_type == 'ダ' and s_rk == 1 and weight >= 480: score += 50.0; nb_hits.append("🐎 ダートで食う(S1位・大型)")
    is_a3_lap = False
    try:
        l1 = float(s_row_laps.get('Lap1', 99) or 99)
        l2 = float(s_row_laps.get('Lap2', 99) or 99)
        if l1 <= 11.9 and l1 < l2: is_a3_lap = True
    except: pass
    if interval.isdigit() and int(interval) >= 12 and is_a3_lap: score += 60.0; nb_hits.append("🔥 Z11/Nなごり(休み明け12週+A3)")

    try:
        w_5f_val = float(w_row_data.get('5F', 99) or 99)
        s_time1 = float(s_row_laps.get('Time1', 99) or 99)
        if arm_rk <= 3 and w_5f_val <= 69.0 and s_time1 <= 59.9: score += 55.0; nb_hits.append("🌲 Ｃ馬特注(ウッド鉄則)")
    except: pass

    # 動的スコア・馬情報には ARMS×FUP黄金クロス・ARMS・Fup2 等をそのまま保持
    if arm_rk == 1 and fup >= 6: score += 50.0; nb_hits.append("✨ ARMS×FUP(黄金クロス:単勝特化)")
    if track_type == 'ダ' and tua_val >= 190.0 and tua_rk <= 3 and s_rk <= 8: score += 40.0; nb_hits.append("💎 TUAダート特注")
    if ('芝→ダ' in track_change or 'ダ→芝' in track_change) and tua_rk <= 3: score += 30.0; nb_hits.append("🔄 トラック変わり激走特注")

    if '藤原' in trainer: score += 30.0; stable_hits.append("厩舎: 藤原英昭(A3/B3特注)")
    if '杉山' in trainer: score += 30.0; stable_hits.append("厩舎: 杉山晴紀(A3黄金)")
    if '矢作' in trainer: score += 30.0; stable_hits.append("厩舎: 矢作芳人(A2真髄)")
    if '中内田' in trainer: score += 35.0; stable_hits.append("厩舎: 中内田充正(鉄板)")
    if '木村' in trainer: score += 30.0; stable_hits.append("厩舎: 木村哲也(ルメール鉄板)")
    if '堀' in trainer: score += 25.0; stable_hits.append("厩舎: 堀宣行(ウッド速め)")
    if '友道' in trainer: score += 25.0; stable_hits.append("厩舎: 友道康夫(地味A1)")
    if '池添' in trainer: score += 25.0; stable_hits.append("厩舎: 池添学(A3特注)")
    if '吉岡' in trainer: score += 25.0; stable_hits.append("厩舎: 吉岡辰弥(前週坂路超速)")
    if '大竹' in trainer: score += 25.0; stable_hits.append("厩舎: 大竹正博(前週坂路57秒以下)")
    if '斉藤崇' in trainer: score += 25.0; stable_hits.append("厩舎: 斉藤崇史(芝ウッド/ダ坂路)")
    if '音無' in trainer: score += 25.0; stable_hits.append("厩舎: 音無秀孝(定年直前勝負)")
    if '国枝' in trainer: score += 25.0; stable_hits.append("厩舎: 国枝栄(前週坂路59秒以下)")

    if fup == 7: score += 50.0
    elif fup >= 5: score += 35.0
    if c_rk <= 3: score += 30.0
    if k_rk <= 3: score += 20.0
    if b_rk <= 3: score += 30.0

    if is_complete_cut:
        score -= 80.0
        is_rescued = False
    elif is_zero5_fade:
        score -= 35.0
        is_rescued = False
    else:
        if is_zero5_n_keep:
            score += 35.0
        elif is_zero5_pop_keep:
            score += 15.0

        is_sss = (f_val >= 65.0) and (arm_val >= 120.0) and (tua_val >= 200.0)
        is_quad_crown = (f_rk <= 3) and (arm_rk <= 3) and (tua_rk <= 3) and (fup >= 5)
        is_solid_axis = (f_rk == 1) and (fup >= 5)
        is_kakugen = (fup == 7)
        is_f65_top = (f_val >= 65.0) or (f_eval_label == "S評価")
        has_strong_bonus = (
            is_sss or is_quad_crown or is_solid_axis or is_kakugen or is_f65_top
            or len(nb_hits) > 0 or len(stable_hits) > 0 or len(combo_hits) > 0
            or (fup >= 6) or (arm_rk <= 2) or is_same_strike or is_same_axis
            or is_zero5_n_keep or is_zero5_pop_keep
        )
        is_rescued = has_strong_bonus
        if not is_rescued:
            if c_rk >= 6: score -= 10.0
            if b_rk >= 6: score -= 5.0
            if pop <= 3 and fup <= 1: score -= 15.0

    is_sss_flag = (f_val >= 65.0) and (arm_val >= 120.0) and (tua_val >= 200.0)
    emp_place_rate, annual_top_lbl, cnt5_val = evaluate_annual_2026_ranking(r, same_umaban_cnt=same_umaban_cnt)

    return (
        score, is_rescued, is_sss_flag, nb_hits, stable_hits, f_eval_label,
        combo_hits, top3_win_rk, emp_place_rate, annual_top_lbl, cnt5_val,
        is_c_win, is_c_place, is_c_ana, is_same_strike, is_same_axis, same_short_tags,
        is_complete_cut, is_zero5_fade, is_zero5_n_keep, is_zero5_pop_keep
    )

def evaluate_race_rating(r_subset):
    sub = r_subset.copy()
    for col in ['F', 'F順位', 'ARM', 'ARM順位', 'TUA', 'TUA順位', 'S', 'S順位', 'Fup2', 'コース連順位', '血統連順位', '印', 'M2']:
        if col in sub.columns:
            sub[col] = pd.to_numeric(sub[col], errors='coerce')

    max_f = sub['F'].max() if not sub.empty else 0.0
    as_count = ((sub['F順位'] <= 3) & (sub['S順位'] <= 3)).sum() if 'F順位' in sub and 'S順位' in sub else 0
    gc_count = ((sub['ARM順位'] == 1) & (sub['Fup2'] >= 6)).sum() if 'ARM順位' in sub and 'Fup2' in sub else 0
    f1_course_count = ((sub['F順位'] == 1) & (sub['コース連順位'] <= 3)).sum() if 'F順位' in sub and 'コース連順位' in sub else 0
    dirt_tua_f_count = ((sub['track'] == 'ダ') & (sub['TUA順位'] == 1) & (sub['F順位'] <= 3)).sum() if {'track', 'TUA順位', 'F順位'}.issubset(sub.columns) else 0
    high_in_count = (sub['印'] >= 3).sum() if '印' in sub else 0
    high_m2_count = (sub['M2'] >= 5).sum() if 'M2' in sub else 0

    if max_f >= 72.0: return "S"
    elif max_f >= 66.0 and (high_in_count >= 3 or high_m2_count >= 3 or f1_course_count >= 1 or dirt_tua_f_count >= 1): return "S"
    elif as_count == 1 and max_f >= 63.0: return "S"
    elif max_f >= 62.0 or gc_count >= 1 or high_in_count >= 2 or f1_course_count >= 1 or dirt_tua_f_count >= 1: return "A"
    elif max_f >= 55.0 or as_count >= 2: return "B"
    else: return "C"

def get_rank_class(rank_val):
    try:
        r = int(rank_val)
        if r == 1: return "val-rank-1"
        elif r == 2: return "val-rank-2"
        elif r == 3: return "val-rank-3"
    except: pass
    return ""

def main():
    st.sidebar.markdown("## 📂 CSVデータ読込管理")
    df_raw, loaded_filename = read_csv_robust()
    sakaro_raw, wood_raw = load_external_training_csvs()

    if not sakaro_raw.empty:
        st.sidebar.success(f"✅ 坂路調教CSV読込成功 ({len(sakaro_raw)}件)")
    else:
        st.sidebar.warning("⚠️ 出馬表_坂路.csv が見つかりません。")

    if not wood_raw.empty:
        st.sidebar.success(f"✅ ウッド調教CSV読込成功 ({len(wood_raw)}件)")
    else:
        st.sidebar.warning("⚠️ 出馬表_ウッド.csv が見つかりません。")

    uploaded_file = st.sidebar.file_uploader("全42〜44列マスターCSVを指定", type=['csv'])
    if uploaded_file is not None:
        for enc in ['utf-8-sig', 'utf-8', 'cp932', 'shift-jis']:
            try:
                uploaded_file.seek(0)
                df_raw = pd.read_csv(uploaded_file, encoding=enc, low_memory=False)
                if not df_raw.empty and df_raw.shape[1] >= 38:
                    loaded_filename = uploaded_file.name
                    break
            except Exception:
                continue

    if df_raw.empty:
        render_html("<div class='race-type-banner race-type-c-class'>⚠️ マスターCSVが見つかりません。サイドバーからCSVを指定してください。</div>")
        st.stop()

    if '日付' in df_raw.columns:
        unique_dates = [str(d).strip() for d in df_raw['日付'].dropna().unique() if str(d).strip() != "" and str(d).strip() != "日付"]
        if len(unique_dates) > 1:
            selected_date_filter = st.sidebar.selectbox("📅 開催日選択（年間CSV対応）", options=unique_dates[::-1], index=0)
            df_raw = df_raw[df_raw['日付'].astype(str).str.strip() == selected_date_filter].copy()

    st.sidebar.success(f"✅ 指数CSV読込成功: {loaded_filename} (対象{len(df_raw)}頭)")

    venue_dict = {"東": "東京", "中": "中山", "京": "京都", "阪": "阪神", "名": "中京", "小": "小倉", "新": "新潟", "福": "福島", "函": "函館", "札": "札幌"}

    sakaro_dict, sakaro_main_accel, wood_dict, wood_has, wood_best_l1, wood_main_accel_11 = build_training_summaries(sakaro_raw, wood_raw)

    records = []
    for _, row in df_raw.iterrows():
        race_id = clean_str(row.get('場所R', ''))
        dist_raw = row.get('距離', 1600)
        umaban = row.get('馬番', 99)
        horse = clean_str(row.get('馬名', ''))
        trainer = clean_str(row.get('調教師', ''))
        jockey = clean_str(row.get('騎手', ''))
        pop = row.get('人気順位', 99)
        raw_c = clean_str(row.get('C', row.get('C(馬)', '')))
        mark = row.get('印', 2)
        m2_raw = row.get('M2', 0)
        c_mark = clean_str(row.get('C(マーク)', ''))
        c_horse = clean_str(row.get('C(馬)', ''))
        track_change = clean_str(row.get('芝ダート変わり', ''))

        dist_str = clean_str(dist_raw)
        if "ダ" in dist_str or "ダ" in raw_c or track_change.endswith("ダ"): track = "ダ"
        elif "芝" in dist_str or "芝" in raw_c or track_change.endswith("芝"): track = "芝"
        else: track = "芝"
        dist_int = int(re.sub(r'\D', '', str(dist_raw))) if re.sub(r'\D', '', str(dist_raw)).isdigit() else 1600

        fup = int(pd.to_numeric(row.get('Fup2', 0), errors='coerce') or 0)
        fup_rk = int(pd.to_numeric(row.get('Fup2順位', 99), errors='coerce') or 99)
        f_val = float(pd.to_numeric(row.get('F', 0.0), errors='coerce') or 0.0)
        f_rk = int(pd.to_numeric(row.get('F順位', 99), errors='coerce') or 99)
        arm_val = float(pd.to_numeric(row.get('ARM', 0.0), errors='coerce') or 0.0)
        arm_rk = int(pd.to_numeric(row.get('ARM順位', 99), errors='coerce') or 99)
        tua_val = float(pd.to_numeric(row.get('TUA', 0.0), errors='coerce') or 0.0)
        tua_rk = int(pd.to_numeric(row.get('TUA順位', 99), errors='coerce') or 99)
        s_val = float(pd.to_numeric(row.get('S', 0.0), errors='coerce') or 0.0)
        s_rk = int(pd.to_numeric(row.get('S順位', 99), errors='coerce') or 99)

        hc_rk = int(pd.to_numeric(row.get('坂路調順位', 99), errors='coerce') or 99)
        hk_rk = int(pd.to_numeric(row.get('坂路血順位', 99), errors='coerce') or 99)
        tk_rk = int(pd.to_numeric(row.get('時計血順位', 99), errors='coerce') or 99)
        c_rk = int(pd.to_numeric(row.get('コース連順位', 99), errors='coerce') or 99)
        k_rk = int(pd.to_numeric(row.get('血統連順位', 99), errors='coerce') or 99)
        b_rk = int(pd.to_numeric(row.get('バランス順位', 99), errors='coerce') or 99)

        sire = clean_str(row.get('種牡馬', ''))
        run_style = clean_str(row.get('前走脚質', ''))
        pass_style = clean_str(row.get('前走決手', ''))
        interval = clean_str(row.get('間隔', ''))
        weight_val = clean_str(row.get('前場体重', '480'))
        race_date = clean_str(row.get('日付', '11.01'))
        class_str = clean_str(str(row.iloc[3]) if row.shape[0] > 3 else "1勝クラス")

        in_num = pd.to_numeric(mark, errors='coerce')
        if pd.isna(in_num): in_num = 2
        m2_num = pd.to_numeric(m2_raw, errors='coerce')
        if pd.isna(m2_num): m2_num = 0

        match_v = re.match(r'([^\d]+)(\d+)', race_id)
        v_name = venue_dict.get(match_v.group(1), match_v.group(1)) if match_v else "新"

        h_clean = clean_str(horse)
        t_clean = clean_str(trainer)

        s_row = sakaro_dict.get((h_clean, t_clean), sakaro_dict.get(h_clean, pd.Series()))
        w_row = wood_dict.get((h_clean, t_clean), wood_dict.get(h_clean, pd.Series()))

        s_4f_val = pd.to_numeric(s_row.get('Time1', s_row.get('Time4', np.nan)), errors='coerce') if isinstance(s_row, pd.Series) and not s_row.empty else np.nan
        s_l2_val = pd.to_numeric(s_row.get('Lap2', np.nan), errors='coerce') if isinstance(s_row, pd.Series) and not s_row.empty else np.nan
        s_l1_val = pd.to_numeric(s_row.get('Lap1', np.nan), errors='coerce') if isinstance(s_row, pd.Series) and not s_row.empty else np.nan
        w_5f_val = pd.to_numeric(w_row.get('5F', np.nan), errors='coerce') if isinstance(w_row, pd.Series) and not w_row.empty else np.nan
        w_l1_val = pd.to_numeric(w_row.get('Lap1', np.nan), errors='coerce') if isinstance(w_row, pd.Series) and not w_row.empty else np.nan

        if horse and pd.notnull(pd.to_numeric(umaban, errors='coerce')):
            records.append({
                'race_id': race_id, 'race_uid': race_id, '競馬場名': v_name, 'track': track, 'dist': dist_int, 'class_name': class_str,
                '馬番': int(float(umaban)), '馬名': horse, '印': in_num, 'M2': m2_num,
                'C(マーク)': c_mark, 'C(馬)': c_horse,
                '調教師': trainer, '騎手': jockey, '種牡馬': sire, '人気順位': int(float(pop)) if pd.notnull(pd.to_numeric(pop, errors='coerce')) else 99,
                'Fup2': fup, 'Fup2順位': fup_rk, 'F': f_val, 'F順位': f_rk, 'ARM': arm_val, 'ARM順位': arm_rk,
                'TUA': tua_val, 'TUA順位': tua_rk, 'S': s_val, 'S順位': s_rk,
                's_row': s_row, 'w_row': w_row,
                '坂路T4': s_4f_val,
                '坂路L2': s_l2_val,
                '坂路L1': s_l1_val,
                '坂路加速': (s_l2_val - s_l1_val) if (pd.notnull(s_l2_val) and pd.notnull(s_l1_val)) else np.nan,
                'ウッド5F': w_5f_val,
                'ウッドL1': w_l1_val,
                'has_wood': h_clean in wood_has,
                'ウッド最速L1': wood_best_l1.get(h_clean, np.nan),
                'wood_main_accel_11': wood_main_accel_11.get(h_clean, False),
                'sakaro_main_accel': sakaro_main_accel.get(h_clean, False),
                '坂路調順位': hc_rk, '坂路血順位': hk_rk, '時計血順位': tk_rk,
                'コース連順位': c_rk, '血統連順位': k_rk, 'バランス順位': b_rk,
                '芝ダート変わり': track_change, '前走脚質': run_style, '前走決手': pass_style,
                '間隔': interval, '前場体重': weight_val, '日付': race_date
            })

    df = pd.DataFrame(records)
    if df.empty:
        st.error("解析可能な有効データが存在しません。")
        st.stop()

    df['ウッド最速L1順位'] = df.groupby('race_uid')['ウッド最速L1'].rank(method='min', ascending=True)
    df['cnt5_all'] = (
        (df['F順位'] <= 3).astype(int) +
        (df['S順位'] <= 3).astype(int) +
        (df['Fup2順位'] <= 3).astype(int) +
        (df['ARM順位'] <= 3).astype(int) +
        (df['TUA順位'] <= 3).astype(int)
    )

    race_date_str = str(df['日付'].iloc[0]) if not df.empty and '日付' in df.columns else "11.01"

    st.sidebar.markdown('---')
    st.sidebar.markdown("### 🌿 馬場・クッション値設定")
    track_cond = st.sidebar.selectbox("芝馬場状態", ["良", "稍重", "重", "不良"], index=0)
    cushion_val = st.sidebar.slider("当日クッション値", min_value=6.0, max_value=12.5, value=9.5, step=0.1, format="%.1f")

    render_html(f"<div class='date-header-badge'>📅 開催日: 2026年{race_date_str} | JRAデータ解析エンジン「競馬予想10 完全版・的中重視厳選＆2026年間実証Vr」</div>")

    race_vol_map = {}
    solid_race_summary, chaos_race_summary = [], []
    for r_uid_k, r_grp in df.groupby('race_uid', sort=False):
        trk_k = r_grp['track'].iloc[0]
        cls_k = r_grp['class_name'].iloc[0]
        v_k = r_grp['競馬場名'].iloc[0]
        m_rn = re.search(r'\d+', str(r_uid_k))
        r_no_txt = m_rn.group() if m_rn else ""
        s_l, f_l = get_race_balance_level(r_grp, trk_k, cls_k)
        v_title, v_short, v_rsn, v_cls = judge_race_volatility(r_grp, s_l, f_l)
        race_vol_map[r_uid_k] = (s_l, f_l, v_title, v_short, v_rsn, v_cls)

        f1_row = r_grp.sort_values('F順位').iloc[0]
        if "堅い" in v_short:
            solid_race_summary.append(f"【{v_k}{r_no_txt}R({trk_k}{r_grp['dist'].iloc[0]}m)】 軸:{int(f1_row['馬番'])}番 {f1_row['馬名']}(F:{f1_row['F']})")
        elif "波乱" in v_short:
            c1_row = r_grp.sort_values(['コース連順位', 'S順位']).iloc[0]
            chaos_race_summary.append(f"【{v_k}{r_no_txt}R({trk_k}{r_grp['dist'].iloc[0]}m)】 穴注目:{int(c1_row['馬番'])}番 {c1_row['馬名']}(C連1位)")

    # -------------------------------------------------------------
    # サイドバー：的中重視・厳選チェックBOXフィルタ（スッキリ版）
    # ※ ARMS×FUP黄金クロス・ARMS120+・Fup2 6+・同馬番単体・ブリンカー単体は削除
    # -------------------------------------------------------------
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎯 的中重視・厳選フィルタ")

    hide_complete_cut = st.sidebar.checkbox("👻 完全消し馬（10人気以下×主5指数0個）をカルテから隠す", value=False)
    filter_vol_solid = st.sidebar.checkbox(f"🔒 堅いレース一覧 [軸信頼] ({len(solid_race_summary)}R)")
    filter_vol_chaos = st.sidebar.checkbox(f"🌪️ 荒れるレース一覧 [波乱・穴] ({len(chaos_race_summary)}R)")

    jockey_umaban_counts = df.groupby(['騎手', '馬番']).size().to_dict() if {'騎手', '馬番'}.issubset(df.columns) else {}

    def get_filter_matches(filter_type):
        matched_records = []
        for _, r in df.iterrows():
            is_match = False
            u_no = int(r['馬番'])
            j_name = r['騎手']
            pair_cnt = jockey_umaban_counts.get((j_name, u_no), 1)
            f_val_v = float(r['F']) if pd.notnull(r['F']) else 0.0
            f_rk_v = int(r['F順位']) if pd.notnull(r['F順位']) else 99
            s_rk_v = int(r['S順位']) if pd.notnull(r['S順位']) else 99
            cnt5_v = int(r['cnt5_all']) if pd.notnull(r['cnt5_all']) else 0
            is_ace = any(ac in str(r['調教師']) for ac in ACE_TRAINERS)
            c_mk = str(r['C(マーク)']).strip().upper() if pd.notnull(r['C(マーク)']) else ""
            extra_tag = ""

            if filter_type == "f72_plus":
                if f_val_v >= 72.0:
                    is_match = True
                    extra_tag = f" [F:{f_val_v:.0f}]"
            elif filter_type == "f1_s1":
                if f_rk_v == 1 and s_rk_v == 1:
                    is_match = True
                    extra_tag = f" [F:{f_val_v:.0f}]"
            elif filter_type == "cnt5_4plus_f1":
                if cnt5_v >= 4 and f_rk_v == 1:
                    is_match = True
                    extra_tag = f" [主5:{cnt5_v}個]"
            elif filter_type == "n_mark":
                if c_mk == "N":
                    is_match = True
                    extra_tag = f" [F{f_rk_v}×S{s_rk_v}]"
            elif filter_type == "f1_as_cross":
                if f_rk_v == 1 and s_rk_v <= 3:
                    is_match = True
                    extra_tag = f" [F1×S{s_rk_v}]"
            elif filter_type == "as_cross":
                if f_rk_v <= 3 and s_rk_v <= 3:
                    is_match = True
                    extra_tag = f" [F{f_rk_v}×S{s_rk_v}]"
            elif filter_type == "f1_course_blood":
                if f_rk_v == 1 and ((pd.notnull(r['コース連順位']) and int(r['コース連順位']) <= 3) or (pd.notnull(r['血統連順位']) and int(r['血統連順位']) <= 3)):
                    is_match = True
            elif filter_type == "c_mark_f_top3":
                if c_mk in ['C', 'N', 'Z', 'M'] and f_rk_v <= 3:
                    is_match = True
                    extra_tag = f" [{c_mk}印]"
            elif filter_type == "stable_as_cross":
                if is_ace and f_rk_v <= 3 and s_rk_v <= 3:
                    is_match = True
            elif filter_type == "high_in_f_top3":
                if pd.notnull(r['印']) and float(r['印']) >= 3 and f_rk_v <= 3:
                    is_match = True
                    extra_tag = f" [印{int(r['印'])}]"
            elif filter_type == "new_same_umaban":
                _, is_st, is_ax, _, s_tags = evaluate_new_same_umaban_targets(r, pair_cnt)
                if is_st or is_ax:
                    is_match = True
                    extra_tag = f" [{'/'.join(s_tags)}]" if s_tags else ""
            elif filter_type == "top3_win_pattern":
                w_rk, _, _, _ = evaluate_top3_win_pattern(r)
                if w_rk > 0: is_match = True
            elif filter_type == "danger_in0":
                if pd.notnull(r['印']) and float(r['印']) == 0: is_match = True

            if is_match:
                m_rnum = re.search(r'\d+', str(r['race_id']))
                r_num_txt = m_rnum.group() if m_rnum else ""
                matched_records.append(f"【{r['競馬場名']}{r_num_txt}R】 {u_no}番 {r['馬名']} ({r['騎手']}){extra_tag}")
        return matched_records

    st.sidebar.markdown("##### 🥇 鉄板軸（年間複勝率60%超）")
    c_f72_matches = get_filter_matches("f72_plus")
    filter_f72_plus = st.sidebar.checkbox(f"👑 F指数 72以上 [複68.8〜71.5%] ({len(c_f72_matches)}頭)")

    c_f1_s1_matches = get_filter_matches("f1_s1")
    filter_f1_s1 = st.sidebar.checkbox(f"👑 F1位 × S1位 [複62.3%] ({len(c_f1_s1_matches)}頭)")

    c_cnt5_f1_matches = get_filter_matches("cnt5_4plus_f1")
    filter_cnt5_4plus_f1 = st.sidebar.checkbox(f"👑 主5指数4個+ × F1位 [複61.4%] ({len(c_cnt5_f1_matches)}頭)")

    c_n_mark_matches = get_filter_matches("n_mark")
    filter_n_mark = st.sidebar.checkbox(f"🏷️ N印 単体 [勝42.7% / 複61.2%] ({len(c_n_mark_matches)}頭)")

    st.sidebar.markdown("##### 🎯 準軸・AS交差・高信頼クロス")
    c_f1_as_matches = get_filter_matches("f1_as_cross")
    filter_f1_as_cross = st.sidebar.checkbox(f"🌟 F1のAS交差馬 (F1×S1〜3) ({len(c_f1_as_matches)}頭)")

    c_as_matches = get_filter_matches("as_cross")
    filter_as_cross = st.sidebar.checkbox(f"👑 AS交差馬 (F1〜3×S1〜3) ({len(c_as_matches)}頭)")

    c_f1_cb_matches = get_filter_matches("f1_course_blood")
    filter_f1_course_blood = st.sidebar.checkbox(f"🎯 F1位×コース/血統連上位 [複56.5%] ({len(c_f1_cb_matches)}頭)")

    c_cmark_f_matches = get_filter_matches("c_mark_f_top3")
    filter_cmark_f_top3 = st.sidebar.checkbox(f"🌟 C/N/Z/M印×F1〜3位 [複54.6%] ({len(c_cmark_f_matches)}頭)")

    c_stbl_as_matches = get_filter_matches("stable_as_cross")
    filter_stable_as_cross = st.sidebar.checkbox(f"🌟 特選厩舎×AS交差 [複57.2%] ({len(c_stbl_as_matches)}頭)")

    c_high_in_f_matches = get_filter_matches("high_in_f_top3")
    filter_high_in_f_top3 = st.sidebar.checkbox(f"🌟 印≧3×F1〜3位 [複47.8%] ({len(c_high_in_f_matches)}頭)")

    st.sidebar.markdown("##### 🔥 一撃特注 ＆ 危険除外")
    c_new_same_matches = get_filter_matches("new_same_umaban")
    filter_new_same_umaban = st.sidebar.checkbox(f"🔥 新・同馬番狙い目 [W最速/3回+/加速] ({len(c_new_same_matches)}頭)")

    c_top3_win_matches = get_filter_matches("top3_win_pattern")
    filter_top3_win = st.sidebar.checkbox(f"👑 驚異の高勝率TOP3+α [1着固定] ({len(c_top3_win_matches)}頭)")

    c_danger_matches = get_filter_matches("danger_in0")
    filter_danger_in0 = st.sidebar.checkbox(f"🚨 前走馬券内0頭（買い目除外連動） ({len(c_danger_matches)}頭)")

    active_filters = []
    if filter_vol_solid: active_filters.append(("🔒 ノートブック判定：堅いレース一覧", solid_race_summary))
    if filter_vol_chaos: active_filters.append(("🌪️ ノートブック判定：荒れるレース一覧", chaos_race_summary))
    if filter_f72_plus: active_filters.append(("👑 F指数 72以上 [鉄板級・年間複68.8〜71.5%]", c_f72_matches))
    if filter_f1_s1: active_filters.append(("👑 F1位 × S1位（ダブル1位）[年間複62.3%]", c_f1_s1_matches))
    if filter_cnt5_4plus_f1: active_filters.append(("👑 主要5指数 4個以上重なり × F1位 [年間複61.4%]", c_cnt5_f1_matches))
    if filter_n_mark: active_filters.append(("🏷️ N印 単体 [年間勝42.7% / 複61.2%]", c_n_mark_matches))
    if filter_f1_as_cross: active_filters.append(("🌟 F1のAS交差馬 (F順位1位 × S順位1〜3位)", c_f1_as_matches))
    if filter_as_cross: active_filters.append(("👑 AS交差馬 (F順位1〜3位 × S順位1〜3位)", c_as_matches))
    if filter_f1_course_blood: active_filters.append(("🎯 F1位 × コース連/血統連上位 [年間複56.5%]", c_f1_cb_matches))
    if filter_cmark_f_top3: active_filters.append(("🌟 C/N/Z/M印 × F1〜3位 [年間複54.6〜59.3%]", c_cmark_f_matches))
    if filter_stable_as_cross: active_filters.append(("🌟 特選厩舎 × AS交差馬 [年間複57.2%]", c_stbl_as_matches))
    if filter_high_in_f_top3: active_filters.append(("🌟 前走馬券内3頭以上(印≧3) × F1〜3位", c_high_in_f_matches))
    if filter_new_same_umaban: active_filters.append(("🔥 新・同馬番狙い目 [W最速L1-1位 / 3回+ / F・S上位×本追加速]", c_new_same_matches))
    if filter_top3_win: active_filters.append(("👑 驚異の高勝率パターンTOP3+α [1着固定特注]", c_top3_win_matches))
    if filter_danger_in0: active_filters.append(("🚨 前走馬券内0頭（買い目除外中）", c_danger_matches))

    if active_filters:
        filter_blocks = ["<div class='filter-result-box'>", "<h3 style='margin-top:0; color:#f8fafc;'>📌 選択中フィルターの該当一覧（リアルタイム抽出）</h3>"]
        for f_name, f_list in active_filters:
            filter_blocks.append(f"<div style='font-weight:bold; color:#e2e8f0; margin-top:6px;'>{f_name} (計 {len(f_list)}件)</div>")
            if f_list:
                formatted_items = " ｜ ".join([f"<span style='background:#1f2937; padding:2px 8px; border-radius:4px; border:1px solid #374151; color:#60a5fa;'>{item}</span>" for item in f_list])
                filter_blocks.append(f"<div style='margin: 6px 0 12px 0; line-height: 2.2;'>{formatted_items}</div>")
            else:
                filter_blocks.append("<div style='color: #9ca3af; margin: 4px 0 10px 0;'>該当なし</div>")
        filter_blocks.append("</div>")
        render_html("\n".join(filter_blocks))

    venue_sort_order = ["東京", "中山", "京都", "阪神", "中京", "小倉", "新潟", "福島", "函館", "札幌", "新"]
    existing_venues = [v for v in venue_sort_order if v in df['競馬場名'].unique()]
    chosen_venue = st.radio("開催場選択", options=existing_venues, horizontal=True)

    v_df = df[df['競馬場名'] == chosen_venue]
    def extract_race_number(uid):
        m = re.search(r'\d+', str(uid))
        return int(m.group()) if m else 99

    races_in_v = v_df[['race_uid', 'race_id', 'track', 'dist', 'class_name']].drop_duplicates('race_uid')
    races_sorted = sorted(races_in_v.to_dict('records'), key=lambda x: extract_race_number(x['race_uid']))

    race_options = {}
    as_race_chips = []
    for r in races_sorted:
        r_uid = r['race_uid']
        r_no_num = extract_race_number(r_uid)
        r_subset = v_df[v_df['race_uid'] == r_uid]
        r_rating = evaluate_race_rating(r_subset)
        s_lvl, f_lvl, _, v_short, _, _ = race_vol_map.get(r_uid, ("標準", "標準", "", "⚖️【標準】", "", ""))

        has_f1_as = bool(((r_subset['F順位'] == 1) & (r_subset['S順位'] <= 3)).any())
        has_any_as = bool(((r_subset['F順位'] <= 3) & (r_subset['S順位'] <= 3)).any())

        if has_f1_as:
            as_prefix = "🟣【F1×AS交差】"
            as_race_chips.append(f"<span class='as-race-chip-f1'>{r_no_num}R ★F1×AS</span>")
        elif has_any_as:
            as_prefix = "🔵【AS交差】"
            as_race_chips.append(f"<span class='as-race-chip-std'>{r_no_num}R AS交差</span>")
        else:
            as_prefix = "⚪ "
            as_race_chips.append(f"<span class='as-race-chip-none'>{r_no_num}R</span>")

        race_tags = []
        if r_rating == "S": race_tags.append("🔥【S級勝負】")
        elif r_rating == "A": race_tags.append("🎯【A級準勝負】")
        elif r_rating == "B": race_tags.append("⚖️【B級標準】")
        else: race_tags.append("📌【見送り推奨】")

        race_tags.append(v_short)
        race_tags.append(f"水準[S:{s_lvl}/F:{f_lvl}]")

        tag_str = f" [{' '.join(race_tags)}]"
        race_options[r_uid] = f"{as_prefix} {r['race_uid']} ({r['track']}{r['dist']}m){tag_str}"

    render_html(f"""
    <div class='as-race-map-box'>
        <div style='font-size: 12.5px; color: #cbd5e1; margin-bottom: 5px; font-weight: bold;'>
            🎨 {chosen_venue}開催 AS交差レース色分け一覧（<span style='color:#fde047;'>紫金＝F1位×AS交差</span> ／ <span style='color:#a5b4fc;'>青紫＝AS交差あり</span> ／ <span style='color:#6b7280;'>灰＝なし</span>）
        </div>
        <div>{''.join(as_race_chips)}</div>
    </div>
    """)

    selected_race_uid = st.selectbox("レース選択（1R〜順次）", options=list(race_options.keys()), format_func=lambda x: race_options[x])
    race_df = df[df['race_uid'] == selected_race_uid].copy()
    c_cat = get_cushion_category(cushion_val, chosen_venue)

    scores, rescued_flags, sss_flags, nb_hits_list, stable_hits_list, f_eval_labels, combo_hits_list = [], [], [], [], [], [], []
    top3_win_rks, emp_place_rates, annual_top_lbls, cnt5_list = [], [], [], []
    c_wins, c_places, c_anas = [], [], []
    same_strikes, same_axes, same_tags_list = [], [], []
    complete_cuts, zero5_fades, zero5_n_keeps, zero5_pop_keeps = [], [], [], []

    for _, r in race_df.iterrows():
        u_cnt = jockey_umaban_counts.get((r['騎手'], int(r['馬番'])), 1)
        (sc, res, sss, nb, stbl, f_lbl, cmb, t3_rk, emp_pr, ann_lbl, c5_v,
         c_win, c_place, c_ana, s_st, s_ax, s_tags,
         is_cut, is_fade, is_n_keep, is_p_keep) = calc_upgraded_dynamic_score(
            r, race_df, chosen_venue, r['track'], r['dist'], c_cat, r['class_name'],
            r['s_row'], r['w_row'], same_umaban_cnt=u_cnt
        )
        scores.append(sc); rescued_flags.append(res); sss_flags.append(sss)
        nb_hits_list.append(nb); stable_hits_list.append(stbl); f_eval_labels.append(f_lbl)
        combo_hits_list.append(cmb); top3_win_rks.append(t3_rk); emp_place_rates.append(emp_pr)
        annual_top_lbls.append(ann_lbl); cnt5_list.append(c5_v)
        c_wins.append(c_win); c_places.append(c_place); c_anas.append(c_ana)
        same_strikes.append(s_st); same_axes.append(s_ax); same_tags_list.append(s_tags)
        complete_cuts.append(is_cut); zero5_fades.append(is_fade)
        zero5_n_keeps.append(is_n_keep); zero5_pop_keeps.append(is_p_keep)

    race_df['dynamic_score'] = scores
    race_df['is_rescued'] = rescued_flags
    race_df['is_sss'] = sss_flags
    race_df['nb_hits'] = nb_hits_list
    race_df['stable_hits'] = stable_hits_list
    race_df['f_eval'] = f_eval_labels
    race_df['combo_hits'] = combo_hits_list
    race_df['top3_win_rk'] = top3_win_rks
    race_df['emp_place_rate'] = emp_place_rates
    race_df['annual_top_lbl'] = annual_top_lbls
    race_df['cnt5'] = cnt5_list
    race_df['course_win'] = c_wins
    race_df['course_place'] = c_places
    race_df['course_ana'] = c_anas
    race_df['same_strike'] = same_strikes
    race_df['same_axis'] = same_axes
    race_df['same_tags'] = same_tags_list
    race_df['is_complete_cut'] = complete_cuts
    race_df['is_zero5_fade'] = zero5_fades
    race_df['is_zero5_n_keep'] = zero5_n_keeps
    race_df['is_zero5_pop_keep'] = zero5_pop_keeps

    sel_rating = evaluate_race_rating(race_df)
    s_lvl_sel, f_lvl_sel, vol_title, vol_short, vol_reason, vol_banner_cls = race_vol_map.get(
        selected_race_uid,
        ("標準", "標準", "⚖️ 標準〜小波乱", "⚖️【標準】", "", "vol-banner-std")
    )

    if sel_rating == "S":
        banner_cls = "race-type-s-class"
        banner_txt = f"🔥🌟【S級絶対勝負レース】レース水準[S:{s_lvl_sel}/F:{f_lvl_sel}] 極限合致の最優先勝負レース（単勝・軸馬鉄板）"
    elif sel_rating == "A":
        banner_cls = "race-type-a-class"
        banner_txt = f"🎯👑【A級準勝負レース】レース水準[S:{s_lvl_sel}/F:{f_lvl_sel}] 黄金クロス・特注条件合致の狙い目レース"
    elif sel_rating == "B":
        banner_cls = "race-type-b-class"
        banner_txt = f"⚖️🎯【B級標準レース】レース水準[S:{s_lvl_sel}/F:{f_lvl_sel}] 的中重視レース"
    else:
        banner_cls = "race-type-c-class"
        banner_txt = f"📌⚠️【C級・見送り推奨レース】レース水準[S:{s_lvl_sel}/F:{f_lvl_sel}] 低レベル混戦のため資金投入非推奨"

    render_html(f"<div class='race-type-banner {banner_cls}'><div>{banner_txt}</div><div>クッション値帯: {c_cat}</div></div>")
    render_html(f"<div class='{vol_banner_cls}'><div style='font-size: 15.5px; font-weight: bold; margin-bottom: 4px;'>📘 ノートブック『S・Fバランス攻略』波乱度判定：{vol_title}</div><div style='font-size: 13.5px; opacity: 0.95;'>🔍 <strong>判定根拠＆馬券戦略</strong>: {vol_reason}</div></div>")

    complete_cut_nums = sorted(race_df[race_df['is_complete_cut']]['馬番'].tolist())
    zero5_keep_nums = sorted(race_df[race_df['is_zero5_n_keep'] | race_df['is_zero5_pop_keep']]['馬番'].tolist())

    safe_race_df = race_df[~race_df['is_complete_cut']].copy()
    if filter_danger_in0:
        safe_race_df = safe_race_df[safe_race_df['印'] > 0].copy()
    if safe_race_df.empty:
        safe_race_df = race_df.copy()

    f_safe_top3 = safe_race_df[safe_race_df['F順位'] <= 3]['馬番'].tolist() if (safe_race_df['F順位'] <= 3).any() else safe_race_df.sort_values('F順位').head(3)['馬番'].tolist()
    s_safe_top3 = safe_race_df[safe_race_df['S順位'] <= 3]['馬番'].tolist() if (safe_race_df['S順位'] <= 3).any() else safe_race_df.sort_values('S順位').head(3)['馬番'].tolist()

    top3_win_nums = safe_race_df[safe_race_df['top3_win_rk'] > 0].sort_values(['top3_win_rk', 'emp_place_rate', 'dynamic_score'], ascending=[True, False, False])['馬番'].tolist()
    course_win_nums = safe_race_df[safe_race_df['course_win']]['馬番'].tolist()
    course_place_nums = safe_race_df[safe_race_df['course_place']]['馬番'].tolist()
    course_ana_nums = safe_race_df[safe_race_df['course_ana']]['馬番'].tolist()

    new_same_strike_df = safe_race_df[safe_race_df['same_strike']].sort_values(['dynamic_score', 'emp_place_rate'], ascending=[False, False])
    new_same_all_df = safe_race_df[safe_race_df['same_strike'] | safe_race_df['same_axis']].sort_values(['dynamic_score', 'emp_place_rate'], ascending=[False, False])
    new_same_strike_nums = new_same_strike_df['馬番'].tolist()
    new_same_all_nums = new_same_all_df['馬番'].tolist()
    new_same_display_items = [
        f"<strong>{int(r_s['馬番'])}番 {r_s['馬名']}</strong>({r_s['騎手']}: {'/'.join(r_s['same_tags'])})"
        for _, r_s in new_same_all_df.iterrows()
    ]

    f1_cb_nums = safe_race_df[(safe_race_df['F順位'] == 1) & ((safe_race_df['コース連順位'] <= 3) | (safe_race_df['血統連順位'] <= 3))]['馬番'].tolist()
    cnzm_all_nums = safe_race_df[safe_race_df['C(マーク)'].astype(str).str.strip().str.upper().isin(['C', 'N', 'Z', 'M'])]['馬番'].tolist()

    a_group_nums = sorted(list(set(f_safe_top3 + s_safe_top3)))
    as_intersect_nums = sorted(list(set(f_safe_top3) & set(s_safe_top3)))
    f1_as_nums = safe_race_df[(safe_race_df['F順位'] == 1) & (safe_race_df['S順位'] <= 3)]['馬番'].tolist()

    z_pool = safe_race_df[(~safe_race_df['馬番'].isin(a_group_nums)) & (~safe_race_df['is_zero5_fade'])]
    if len(z_pool) < 3:
        z_pool = safe_race_df[~safe_race_df['馬番'].isin(a_group_nums)]
    z_candidates = z_pool.sort_values(
        ['コース連順位', '血統連順位', '坂路調順位', 'dynamic_score'],
        ascending=[True, True, True, False]
    )
    z_nums = z_candidates.head(3)['馬番'].tolist()

    annual_ranked_df = safe_race_df.sort_values(['emp_place_rate', 'dynamic_score', 'F'], ascending=[False, False, False])
    axis_row = annual_ranked_df.iloc[0]
    axis_num = int(axis_row['馬番'])

    opp_top1_df = safe_race_df[
        (safe_race_df['馬番'] != axis_num) & (
            (safe_race_df['F順位'] == 1) |
            (safe_race_df['S順位'] == 1) |
            (safe_race_df['Fup2順位'] == 1) |
            (safe_race_df['ARM順位'] == 1) |
            (safe_race_df['TUA順位'] == 1) |
            (safe_race_df['emp_place_rate'] >= 55.0) |
            (safe_race_df['is_zero5_n_keep'])
        )
    ].sort_values(['emp_place_rate', 'dynamic_score'], ascending=[False, False])
    opp_top1_nums = opp_top1_df['馬番'].tolist()[:4]
    if not opp_top1_nums:
        opp_top1_nums = annual_ranked_df[annual_ranked_df['馬番'] != axis_num]['馬番'].tolist()[:3]

    opp_2plus_nums = safe_race_df[
        (safe_race_df['馬番'] != axis_num) & (safe_race_df['cnt5'] >= 2)
    ].sort_values(['emp_place_rate', 'dynamic_score'], ascending=[False, False])['馬番'].tolist()
    opp_wide_pool = list(dict.fromkeys(
        opp_top1_nums + opp_2plus_nums + [n for n in (zero5_keep_nums + cnzm_all_nums + new_same_all_nums + z_nums) if n != axis_num]
    ))[:7]

    rank_order_str = " ➔ ".join([
        f"<strong>{int(r_row['馬番'])}番</strong>(複{r_row['emp_place_rate']:.1f}%:{r_row['annual_top_lbl']})"
        for _, r_row in annual_ranked_df.head(5).iterrows()
    ])

    axis_judge_txt = "🔥【F1×AS交差・年間上位軸 勝負可】" if (axis_num in f1_as_nums or axis_row['emp_place_rate'] >= 60.0) else "⚖️【標準軸（複勝・ワイド中心）】"

    new_same_html_block = ""
    if new_same_display_items:
        new_same_html_block = (
            "<div style='background: linear-gradient(135deg, rgba(190, 18, 60, 0.22) 0%, rgba(245, 158, 11, 0.22) 100%); "
            "border: 1px solid #f59e0b; border-radius: 6px; padding: 6px 10px; margin: 6px 0;'>"
            "🔥 <strong style='color: #fde047;'>【新・同馬番狙い目 該当あり（調教CSV×3回以上連動）】</strong>: "
            f"<span style='color: #ffffff;'>{' ｜ '.join(new_same_display_items)}</span>"
            "</div>"
        )

    render_html(f"""
    <div class='recom-block' style='border: 2px solid #3b82f6;'>
        <h4 style='color: #60a5fa; margin-top: 0;'>🎯 第3の馬券：2026年年間通算（3,030R・41,354頭）複勝率ランキング連動馬券</h4>
        {new_same_html_block}
        <div style='font-size: 13.5px; color: #cbd5e1; margin-bottom: 8px;'>
            📊 <strong>【2026年間実証 複勝率上位】</strong>: <span style='color: #93c5fd;'>{rank_order_str}</span><br>
            <strong>A群（F上位1〜3位 ＋ S上位1〜3位）</strong>: {', '.join([f"<strong>{n}番</strong>" for n in a_group_nums])} ｜ 🌟 <strong>【F1×AS交差馬】</strong>: <span style='color: #fde047; font-weight: bold;'>{", ".join(map(str, f1_as_nums)) if f1_as_nums else "なし"}</span> ｜ 👑 <strong>【AS交差馬全体】</strong>: {", ".join(map(str, as_intersect_nums)) if as_intersect_nums else "なし"}<br>
            🔥 <strong>【驚異の高勝率パターン】</strong>: <span style='color: #fef08a;'>{", ".join(map(str, top3_win_nums)) if top3_win_nums else "なし"}</span> ｜ 👑 <strong>【コース1着特注】</strong>: <span style='color: #fca5a5;'>{", ".join(map(str, course_win_nums)) if course_win_nums else "なし"}</span> ｜ 🎯 <strong>【コース連軸】</strong>: <span style='color: #6ee7b7;'>{", ".join(map(str, course_place_nums)) if course_place_nums else "なし"}</span> ｜ 💣 <strong>【コース穴覚醒】</strong>: <span style='color: #c4b5fd;'>{", ".join(map(str, course_ana_nums)) if course_ana_nums else "なし"}</span><br>
            🎯 <strong>【F1位×コース/血統連】</strong>: <span style='color: #fde047;'>{", ".join(map(str, f1_cb_nums)) if f1_cb_nums else "なし"}</span> ｜ 🏷️ <strong>【C/N/Z/M印】</strong>: <span style='color: #fde047;'>{", ".join(map(str, cnzm_all_nums)) if cnzm_all_nums else "なし"}</span> ｜ 🎯 <strong>【厳選Z馬（3列目特化）】</strong>: <span style='color: #38bdf8; font-weight: bold;'>{", ".join(map(str, z_nums)) if z_nums else "なし"}</span><br>
            ⚡ <strong>【主5指数0個・例外残し（N印 / 1〜3人気）】</strong>: <span style='color: #6ee7b7; font-weight: bold;'>{", ".join(map(str, zero5_keep_nums)) if zero5_keep_nums else "なし"}</span> ｜ 👻 <strong>【自動除外（完全消し：10人気以下×主5指数0個）】</strong>: <span style='color: #9ca3af;'>{", ".join(map(str, complete_cut_nums)) if complete_cut_nums else "なし"}</span>
        </div>
        <div style='background: rgba(59, 130, 246, 0.12); border: 1px solid #3b82f6; border-radius: 6px; padding: 10px 14px; margin-top: 6px;'>
            <div style='font-size: 13.5px; color: #fde047; font-weight: bold; margin-bottom: 6px;'>{axis_judge_txt}</div>
            <div style='font-size: 14.5px; line-height: 1.85;'>
                🥇 <strong>単勝・複勝（年間ランキング最上位軸）</strong>: <span style='color: #fbbf24; font-weight: bold; font-size: 15.5px;'>{axis_num}番 {axis_row['馬名']}</span>（年間複勝率 {axis_row['emp_place_rate']:.1f}% / {axis_row['annual_top_lbl']}）<br>
                🥈 <strong>馬連・ワイド（主要5指数1位＋年間複55%超へ絞り流し・{len(opp_top1_nums)}点）</strong>: <span style='color: #34d399; font-weight: bold; font-size: 15px;'>{axis_num} － {", ".join(map(str, opp_top1_nums))}</span><br>
                🥉 <strong>3連複 軸1頭流し（主5指数2個以上＋例外残し・印・新同馬番・厳選Z馬・計{len(opp_wide_pool)}頭へ）</strong>: <span style='color: #38bdf8; font-weight: bold;'>{axis_num} － {", ".join(map(str, opp_wide_pool))}</span>
            </div>
        </div>
    </div>
    """)

    honmei = safe_race_df.sort_values(['dynamic_score', 'emp_place_rate', 'F順位'], ascending=[False, False, True]).iloc[0]
    honmei_num = int(honmei['馬番'])
    opponents = safe_race_df[safe_race_df['馬番'] != honmei_num].copy()

    taikou_df = opponents.sort_values(['emp_place_rate', 'dynamic_score'], ascending=[False, False])
    taikou = taikou_df.iloc[0] if not taikou_df.empty else honmei
    taikou_num = int(taikou['馬番'])

    ana_pool = opponents[~opponents['is_zero5_fade']].copy()
    if ana_pool.empty:
        ana_pool = opponents.copy()

    ana_cands = ana_pool[ana_pool['馬番'].isin(course_ana_nums)].sort_values('dynamic_score', ascending=False)
    if not ana_cands.empty:
        ana = ana_cands.iloc[0]
    else:
        ana_cands_same = ana_pool[ana_pool['馬番'].isin(new_same_strike_nums)].sort_values('dynamic_score', ascending=False)
        if not ana_cands_same.empty:
            ana = ana_cands_same.iloc[0]
        else:
            ana_cands2 = ana_pool[ana_pool['人気順位'] >= 4].sort_values(['dynamic_score', 'コース連順位', 'TUA順位'], ascending=[False, True, True]) if not ana_pool.empty else pd.DataFrame()
            if not ana_cands2.empty:
                ana = ana_cands2.iloc[0]
            elif not opponents.empty:
                ana = opponents.iloc[-1]
            else:
                ana = honmei
    ana_num = int(ana['馬番'])

    render_html(f"""
    <div class='recom-panel-go'>
        <div class='recom-title-go'>🔥 ハイブリッド注目馬ピックアップ（本命・対抗・穴特注）</div>
        <div class='recom-row'>🥇 <strong>本命・連軸</strong>: <span class='recom-val-num'>{honmei_num}番 {honmei['馬名']}</span>（F指数: {honmei['F']} / 年間複勝率: {honmei['emp_place_rate']:.1f}% / 動的スコア: {honmei['dynamic_score']:.1f}）</div>
        <div class='recom-row'>🛡️ <strong>対抗・相手筆頭</strong>: <span class='recom-val-num'>{taikou_num}番 {taikou['馬名']}</span>（F指数: {taikou['F']} / S順位: {taikou['S順位']}位 / 年間複勝率: {taikou['emp_place_rate']:.1f}%）</div>
        <div class='recom-row'>💣 <strong>激走穴特注（保険）</strong>: <span class='recom-val-num'>{ana_num}番 {ana['馬名']}</span>（{ana['人気順位']}番人気 / 穴特注スコア上位）</div>
    </div>
    """)

    # カルテ表示フィルタ連動（厳選フィルタのみ）
    display_df = race_df.copy()
    if hide_complete_cut:
        display_df = display_df[~display_df['is_complete_cut']]
    if filter_f72_plus:
        filtered = display_df[display_df['F'] >= 72.0]
        if not filtered.empty: display_df = filtered
    if filter_f1_s1:
        filtered = display_df[(display_df['F順位'] == 1) & (display_df['S順位'] == 1)]
        if not filtered.empty: display_df = filtered
    if filter_cnt5_4plus_f1:
        filtered = display_df[(display_df['cnt5'] >= 4) & (display_df['F順位'] == 1)]
        if not filtered.empty: display_df = filtered
    if filter_n_mark:
        filtered = display_df[display_df['C(マーク)'].astype(str).str.strip().str.upper() == 'N']
        if not filtered.empty: display_df = filtered
    if filter_f1_as_cross:
        filtered = display_df[(display_df['F順位'] == 1) & (display_df['S順位'] <= 3)]
        if not filtered.empty: display_df = filtered
    if filter_as_cross:
        filtered = display_df[(display_df['F順位'] <= 3) & (display_df['S順位'] <= 3)]
        if not filtered.empty: display_df = filtered
    if filter_f1_course_blood:
        filtered = display_df[(display_df['F順位'] == 1) & ((display_df['コース連順位'] <= 3) | (display_df['血統連順位'] <= 3))]
        if not filtered.empty: display_df = filtered
    if filter_cmark_f_top3:
        filtered = display_df[display_df['C(マーク)'].astype(str).str.strip().str.upper().isin(['C', 'N', 'Z', 'M']) & (display_df['F順位'] <= 3)]
        if not filtered.empty: display_df = filtered
    if filter_stable_as_cross:
        filtered = display_df[display_df['調教師'].apply(lambda t: any(ac in str(t) for ac in ACE_TRAINERS)) & (display_df['F順位'] <= 3) & (display_df['S順位'] <= 3)]
        if not filtered.empty: display_df = filtered
    if filter_high_in_f_top3:
        filtered = display_df[(display_df['印'] >= 3) & (display_df['F順位'] <= 3)]
        if not filtered.empty: display_df = filtered
    if filter_new_same_umaban:
        filtered = display_df[display_df['same_strike'] | display_df['same_axis']]
        if not filtered.empty: display_df = filtered
    if filter_top3_win:
        filtered = display_df[display_df['top3_win_rk'] > 0]
        if not filtered.empty: display_df = filtered

    st.markdown("### 🏇 出走馬詳細カルテ ＆ レース内調教比較")
    sort_col1, sort_col2 = st.columns(2)
    with sort_col1:
        sort_criterion = st.selectbox('📊 並び替え基準（指数・調教比較）', [
            '総合動的評価スコア順', '2026年間実証複勝率順', '坂路全体タイム順（速い順）', '坂路ラスト1F順（速い順）', '坂路加速量順（切れ味順）', 'ウッド全体タイム(5F)順', 'ウッドラスト1F順',
            'F指数 降順', 'ARM指数 降順', 'TUA指数 降順', 'S指数 降順', 'Fup2点数 降順', '馬番順'
        ], index=0)

    if sort_criterion == '総合動的評価スコア順': sorted_df = display_df.sort_values('dynamic_score', ascending=False)
    elif sort_criterion == '2026年間実証複勝率順': sorted_df = display_df.sort_values(['emp_place_rate', 'dynamic_score'], ascending=[False, False])
    elif sort_criterion == '坂路全体タイム順（速い順）': sorted_df = display_df.sort_values('坂路T4', ascending=True, na_position='last')
    elif sort_criterion == '坂路ラスト1F順（速い順）': sorted_df = display_df.sort_values('坂路L1', ascending=True, na_position='last')
    elif sort_criterion == '坂路加速量順（切れ味順）': sorted_df = display_df.sort_values('坂路加速', ascending=False, na_position='last')
    elif sort_criterion == 'ウッド全体タイム(5F)順': sorted_df = display_df.sort_values('ウッド5F', ascending=True, na_position='last')
    elif sort_criterion == 'ウッドラスト1F順': sorted_df = display_df.sort_values('ウッドL1', ascending=True, na_position='last')
    elif sort_criterion == 'F指数 降順': sorted_df = display_df.sort_values(['F', 'F順位'], ascending=[False, True])
    elif sort_criterion == 'ARM指数 降順': sorted_df = display_df.sort_values(['ARM', 'ARM順位'], ascending=[False, True])
    elif sort_criterion == 'TUA指数 降順': sorted_df = display_df.sort_values(['TUA', 'TUA順位'], ascending=[False, True])
    elif sort_criterion == 'S指数 降順': sorted_df = display_df.sort_values(['S', 'S順位'], ascending=[False, True])
    elif sort_criterion == 'Fup2点数 降順': sorted_df = display_df.sort_values(['Fup2', 'Fup2順位'], ascending=[False, True])
    else: sorted_df = display_df.sort_values('馬番', ascending=True)

    for _, h in sorted_df.iterrows():
        u_no = int(h['馬番'])
        badges = []

        if h['is_complete_cut']:
            card_cls = "horse-card-cut"
            badges.append("<span class='badge-complete-cut'>👻 完全消し（10人気以下×主5指数0個 / 複3.9%）</span>")
        elif h['is_zero5_fade']:
            card_cls = "horse-card-fade"
            badges.append("<span class='badge-zero5-fade'>🌫️ 主5指数0個（N印なし・薄表示）</span>")
        else:
            card_cls = "horse-card"
            if h['is_zero5_n_keep']:
                badges.append("<span class='badge-zero5-keep'>⚡ 例外残し：主5指数0個×N印（複47.1%）</span>")
            elif h['is_zero5_pop_keep']:
                badges.append("<span class='badge-zero5-keep'>⚡ 例外残し：主5指数0個×1〜3人気（複46.1%）</span>")

        if u_no == honmei_num: badges.append("<span class='badge-mark-honmei'>◎ 本命</span>")
        elif u_no == taikou_num: badges.append("<span class='badge-mark-taikou'>◯ 対抗</span>")
        elif u_no == ana_num: badges.append("<span class='badge-mark-ana'>🔥 穴特注(保険)</span>")

        j_name = h['騎手']
        pair_cnt = jockey_umaban_counts.get((j_name, u_no), 1)
        if j_name and pair_cnt >= 2:
            badges.append(f"<span class='badge-jockey-same-umaban'>🔥 同馬番複数騎乗(勝負): {j_name}({pair_cnt}回・{u_no}番)</span>")

        in_v = h['印']
        m2_v = h['M2']
        if h['C(マーク)']: badges.append(f"<span class='badge-c-mark'>🏷️ C(マーク): {h['C(マーク)']}</span>")
        if h['C(馬)']:
            c_h_txt = "B" if str(h['C(馬)']).strip().upper() == "B" else str(h['C(馬)']).strip()
            badges.append(f"<span class='badge-c-horse'>{c_h_txt}</span>")

        f_eval = h['f_eval']
        if f_eval == "S評価": badges.append("<span class='badge-f-eval-s'>🔥 F指数 S評価(特注馬)</span>")
        elif f_eval == "A評価": badges.append("<span class='badge-f-eval-a'>⭐ F指数 A評価</span>")
        elif f_eval == "B評価": badges.append("<span class='badge-f-eval-b'>📌 F指数 B評価</span>")

        for c_type, c_text in h.get('combo_hits', []):
            if c_type == "top3_win": badges.append(f"<span class='badge-top3-win'>{c_text}</span>")
            elif c_type == "new-same-hit": badges.append(f"<span class='badge-new-same-hit'>{c_text}</span>")
            elif c_type == "new-same-axis": badges.append(f"<span class='badge-new-same-axis'>{c_text}</span>")
            elif c_type == "course-win": badges.append(f"<span class='badge-course-win'>{c_text}</span>")
            elif c_type == "course-place": badges.append(f"<span class='badge-course-place'>{c_text}</span>")
            elif c_type == "course-ana": badges.append(f"<span class='badge-course-ana'>{c_text}</span>")
            elif c_type == "golden": badges.append(f"<span class='badge-golden-combo'>{c_text}</span>")
            else: badges.append(f"<span class='badge-value-combo'>{c_text}</span>")

        if in_v == 0: badges.append("<span class='badge-danger-fan'>🚨 前走相手馬券内0頭(凡戦注意)</span>")
        elif in_v >= 8: badges.append(f"<span class='badge-high-level'>👑 前走相手馬券内{in_v}頭(超ハイレベル)</span>")
        elif in_v >= 3: badges.append(f"<span class='badge-notebook-hit'>🔥 前走相手馬券内{in_v}頭</span>")
        if m2_v >= 5: badges.append(f"<span class='badge-cushion-fit'>⭐ 前走相手掲示板{m2_v}頭(出世レース)</span>")

        is_f1_as = h['F順位'] == 1 and h['S順位'] <= 3
        is_as = h['F順位'] <= 3 and h['S順位'] <= 3
        if is_f1_as: badges.append("<span class='badge-as-intersect'>🌟 F1×AS交差馬</span>")
        elif is_as: badges.append("<span class='badge-as-intersect'>👑 AS交差馬 (F&S上位)</span>")
        if u_no in z_nums: badges.append("<span class='badge-value-combo'>🎯 厳選Z馬</span>")
        if h['is_rescued']: badges.append("<span class='badge-rescued'>🛡️ 強力加点・保険救済馬</span>")
        for nb in h['nb_hits']: badges.append(f"<span class='badge-notebook-hit'>{nb}</span>")
        for stbl in h['stable_hits']: badges.append(f"<span class='badge-stable-hit'>{stbl}</span>")

        c_key = (chosen_venue, h['track'], h['dist'], h['種牡馬'], c_cat)
        if c_key in CUSHION_DATA_BOOK:
            judg, stat_txt = CUSHION_DATA_BOOK[c_key]
            if judg == '最重要': badges.append(f"<span class='badge-cushion-fit'>🌿 クッション特注: {h['種牡馬']} ({stat_txt})</span>")

        fup_val = int(h['Fup2'])
        fup_rk = int(h['Fup2順位'])
        if fup_rk == 1 and fup_val >= 5: fup_badge = f"<span class='fup-badge-rank1-high'>👑🔥 {fup_val}点 (順位1位)</span>"
        elif fup_rk == 1: fup_badge = f"<span class='fup-badge-rank1'>👑 {fup_val}点 (順位1位)</span>"
        elif fup_val >= 7: fup_badge = f"<span class='fup-badge-top'>⚡ {fup_val}点 (順位{fup_rk})</span>"
        elif fup_val >= 5: fup_badge = f"<span class='fup-badge-mid'>🔥 {fup_val}点 (順位{fup_rk})</span>"
        elif fup_rk == 2: fup_badge = f"<span class='val-rank-2'>{fup_val}点 (順位2)</span>"
        elif fup_rk == 3: fup_badge = f"<span class='val-rank-3'>{fup_val}点 (順位3)</span>"
        else: fup_badge = f"<span class='fup-badge-low'>{fup_val}点 (順位{fup_rk})</span>"

        f_rk_cls = get_rank_class(h['F順位'])
        s_rk_cls = get_rank_class(h['S順位'])
        arm_rk_cls = get_rank_class(h['ARM順位'])
        tua_rk_cls = get_rank_class(h['TUA順位'])
        hk_rk_cls = get_rank_class(h['坂路血順位'])
        tk_rk_cls = get_rank_class(h['時計血順位'])
        c_rk_cls = get_rank_class(h['コース連順位'])
        k_rk_cls = get_rank_class(h['血統連順位'])
        b_rk_cls = get_rank_class(h['バランス順位'])

        s_t4 = h.get('坂路T4', np.nan)
        s_l2 = h.get('坂路L2', np.nan)
        s_l1 = h.get('坂路L1', np.nan)
        w_5f = h.get('ウッド5F', np.nan)
        w_l1 = h.get('ウッドL1', np.nan)
        w_best_l1 = h.get('ウッド最速L1', np.nan)
        w_best_rk = h.get('ウッド最速L1順位', np.nan)

        judge_label, judge_color = parse_and_judge_lap(s_l1, s_l2, s_t4)
        sakaro_str = f"坂路[4F:{s_t4 if pd.notnull(s_t4) else '---'} | L2:{s_l2 if pd.notnull(s_l2) else '---'} → L1:{s_l1 if pd.notnull(s_l1) else '---'}]" if pd.notnull(s_t4) else "坂路データなし"
        w_rk_txt = f" (最速L1:{w_best_l1} / 順位{int(w_best_rk)}位)" if pd.notnull(w_best_l1) and pd.notnull(w_best_rk) else ""
        wood_str = f"ウッド[5F:{w_5f if pd.notnull(w_5f) else '---'} → L1:{w_l1 if pd.notnull(w_l1) else '---'}]{w_rk_txt}" if (pd.notnull(w_5f) or pd.notnull(w_l1)) else "ウッドデータなし"

        m_uid = re.search(r'\d+', str(h['race_uid']))
        r_num_str = m_uid.group() if m_uid else ''
        race_place_num_str = f"【{chosen_venue}{r_num_str}R】" if r_num_str else f"【{chosen_venue}】"

        render_html(f"""
        <div class='{card_cls}'>
            <div class='horse-card-header'>
                <span class='race-badge-title'>{race_place_num_str} {u_no}番</span>
                <span class='horse-card-title'>{h['馬番']}番 {h['馬名']}</span>
                <span style='color: #9ca3af; font-size: 13.5px;'>（{h['調教師']} / {h['騎手']} / {h['人気順位']}番人気）</span>
            </div>
            <div style='margin-bottom: 8px;'>{' '.join(badges)}</div>
            <ul class='horse-card-list'>
                <li><strong>主要5大指数</strong>:
                    F指数: <span class='{f_rk_cls}'>{h['F']} (順位{h['F順位']})</span> /
                    Fup2: {fup_badge} /
                    ARM: <span class='{arm_rk_cls}'>{h['ARM']} (順位{h['ARM順位']})</span> /
                    TUA: <span class='{tua_rk_cls}'>{h['TUA']} (順位{h['TUA順位']})</span> /
                    S指数: <span class='{s_rk_cls}'>{h['S']} (順位{h['S順位']})</span>
                </li>
                <li><strong>対戦レベル評価</strong>: 前走馬券内頭数(印): <strong>{in_v}頭</strong> ｜ 前走掲示板内頭数(M2): <strong>{m2_v}頭</strong></li>
                <li><strong>調教ラップ＆判定</strong>: <span style='background-color: {judge_color}; color: #fff; padding: 2px 6px; border-radius: 4px; font-weight: bold;'>{judge_label}</span><br>
                    <span style='font-size: 12.5px; color: #94a3b8;'>{sakaro_str} ｜ {wood_str}</span> ｜ 坂路血: <span class='{hk_rk_cls}'>{h['坂路血順位']}位</span> / 時計血: <span class='{tk_rk_cls}'>{h['時計血順位']}位</span></li>
                <li><strong>適性・補正順位</strong>: コース連: <span class='{c_rk_cls}'>{h['コース連順位']}位</span> / 血統連: <span class='{k_rk_cls}'>{h['血統連順位']}位</span> / Balance: <span class='{b_rk_cls}'>{h['バランス順位']}位</span></li>
                <li><strong>血統＆展開</strong>: 父 {h['種牡馬']} ｜ トラック替: {h['芝ダート変わり']} ｜ 前走脚質: {h['前走脚質']}（決手: {h['前走決手']}）｜ 間隔: {h['間隔']}週 ｜ 前場体重: {h['前場体重']}kg</li>
                <li><strong>総合動的スコア</strong>: <span style='color: #facc15; font-weight: bold; font-size: 15px;'>{h['dynamic_score']:.1f}点</span> ｜ <strong>2026年間実証複勝率</strong>: <span style='color: #38bdf8; font-weight: bold; font-size: 14.5px;'>{h['emp_place_rate']:.1f}%</span>（{h['annual_top_lbl']}）</li>
            </ul>
        </div>
        """)

if __name__ == "__main__":
    main()
