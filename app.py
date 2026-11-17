import streamlit as st
import pandas as pd
import numpy as np
import os
import glob
import re

st.set_page_config(
    page_title="競馬予想10 完全版 - コース特注統合Vr",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    div[data-baseweb="select"] input { inputmode: none !important; pointer-events: none !important; }
    .date-header-badge { display: inline-flex; align-items: center; gap: 8px; background: linear-gradient(135deg, #1f2937 0%, #111827 100%); border: 1px solid #3b82f6; padding: 6px 16px; border-radius: 20px; color: #60a5fa; font-size: 14.5px; font-weight: bold; margin-bottom: 12px; }
    .race-type-banner { padding: 12px 18px; border-radius: 8px; margin-bottom: 10px; font-size: 15px; font-weight: bold; display: flex; align-items: center; justify-content: space-between; }
    .race-type-s-class { background: linear-gradient(135deg, #7c2d12 0%, #b45309 30%, #dc2626 100%); color: #fef3c7; border: 2px solid #fde68a; box-shadow: 0 0 15px rgba(239, 68, 68, 0.6); }
    .race-type-a-class { background: linear-gradient(135deg, #7c2d12 0%, #b45309 50%, #d97706 100%); color: #fef3c7; border: 2px solid #fde68a; box-shadow: 0 0 10px rgba(245, 158, 11, 0.5); }
    .race-type-b-class { background: linear-gradient(135deg, #064e3b 0%, #047857 100%); color: #d1fae5; border: 2px solid #6ee7b7; }
    .race-type-c-class { background: #374151; color: #9ca3af; border: 1px solid #4b5563; }
    .vol-banner-solid { background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); border: 2px solid #38bdf8; color: #e0f2fe; padding: 12px 18px; border-radius: 8px; margin-bottom: 14px; box-shadow: 0 0 12px rgba(56, 189, 248, 0.35); }
    .vol-banner-std { background: linear-gradient(135deg, #1f2937 0%, #374151 100%); border: 2px solid #fbbf24; color: #fef3c7; padding: 12px 18px; border-radius: 8px; margin-bottom: 14px; }
    .vol-banner-chaos { background: linear-gradient(135deg, #450a0a 0%, #7f1d1d 50%, #581c87 100%); border: 2px solid #f43f5e; color: #ffe4e6; padding: 12px 18px; border-radius: 8px; margin-bottom: 14px; box-shadow: 0 0 14px rgba(244, 63, 94, 0.45); }
    .recom-panel-go { background: linear-gradient(135deg, #111827 0%, #1f2937 100%); border: 2px solid #10b981; border-radius: 10px; padding: 16px 20px; margin-bottom: 20px; }
    .recom-title-go { font-size: 16px; font-weight: bold; color: #34d399; margin-bottom: 12px; border-bottom: 1px solid #374151; padding-bottom: 5px; }
    .recom-row { margin-bottom: 8px; font-size: 14.5px; line-height: 1.6; }
    .recom-block { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; padding: 10px 14px; margin-bottom: 10px; }
    .recom-val-num { color: #ffffff; font-weight: bold; font-size: 15.5px; letter-spacing: 1px; }
    .horse-card { background-color: #161e2e; border-left: 5px solid #238636; padding: 14px 18px; border-radius: 8px; margin-bottom: 14px; border: 1px solid #30363d; }
    .horse-card-header { display: flex; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 8px; }
    .horse-card-title { font-size: 18px; font-weight: bold; color: #ffffff; }
    .race-badge-title { background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); color: #ffffff; font-weight: bold; font-size: 14px; padding: 2px 10px; border-radius: 6px; border: 1px solid #93c5fd; margin-right: 6px; }
    .horse-card-list { list-style-type: none; padding-left: 0; margin: 0; }
    .horse-card-list li { font-size: 13.5px; color: #c9d1d9; margin-bottom: 6px; line-height: 1.6; }
    .horse-card-list li::before { content: "• "; color: #58a6ff; font-weight: bold; }
    .badge-mark-honmei { display: inline-flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%); color: #ffffff; font-size: 12.5px; font-weight: 900; padding: 2px 8px; border-radius: 4px; border: 1px solid #fca5a5; margin-right: 6px; }
    .badge-mark-taikou { display: inline-flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: #ffffff; font-size: 12.5px; font-weight: 900; padding: 2px 8px; border-radius: 4px; border: 1px solid #93c5fd; margin-right: 6px; }
    .badge-mark-ana { display: inline-flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #d97706 0%, #b45309 100%); color: #ffffff; font-size: 12.5px; font-weight: 900; padding: 2px 8px; border-radius: 4px; border: 1px solid #fde68a; margin-right: 6px; }
    
    /* コース特注バッジ */
    .badge-course-win { display: inline-flex; align-items: center; background: linear-gradient(135deg, #b91c1c 0%, #ef4444 100%); color: #fff; font-weight: 900; font-size: 12.5px; padding: 3px 10px; border-radius: 6px; border: 2px solid #fca5a5; margin-right: 5px; box-shadow: 0 0 10px rgba(239, 68, 68, 0.7); }
    .badge-course-place { display: inline-flex; align-items: center; background: linear-gradient(135deg, #047857 0%, #10b981 100%); color: #fff; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #6ee7b7; margin-right: 4px; box-shadow: 0 0 8px rgba(16, 185, 129, 0.5); }
    .badge-course-ana { display: inline-flex; align-items: center; background: linear-gradient(135deg, #7c3aed 0%, #8b5cf6 100%); color: #fff; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #c4b5fd; margin-right: 4px; box-shadow: 0 0 8px rgba(139, 92, 246, 0.5); }

    .badge-top3-win { display: inline-flex; align-items: center; background: linear-gradient(135deg, #b91c1c 0%, #7c2d12 50%, #d97706 100%); color: #ffffff; font-weight: 900; font-size: 12.5px; padding: 3px 10px; border-radius: 4px; border: 2px solid #fef08a; margin-right: 5px; box-shadow: 0 0 12px rgba(250,204,21,0.8); }
    .badge-golden-combo { display: inline-flex; align-items: center; background: linear-gradient(135deg, #991b1b 0%, #d97706 100%); color: #fef08a; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #fde047; margin-right: 4px; }
    .badge-value-combo { display: inline-flex; align-items: center; background: linear-gradient(135deg, #065f46 0%, #0284c7 100%); color: #e0f2fe; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #7dd3fc; margin-right: 4px; }
    .val-rank-1 { color: #ffffff; background-color: #d97706; font-weight: bold; padding: 1px 6px; border-radius: 4px; }
    .val-rank-2 { color: #ffffff; background-color: #2563eb; font-weight: bold; padding: 1px 6px; border-radius: 4px; }
    .val-rank-3 { color: #ffffff; background-color: #047857; font-weight: bold; padding: 1px 6px; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

ACE_TRAINERS = ['藤原', '杉山', '矢作', '中内田', '木村', '堀', '友道', '池添', '吉岡', '大竹', '斉藤', '音無', '国枝']

# ★ 年間4.1万頭データから抽出した特注コース・距離の黄金パターン ★
# (競馬場, 芝ダ, 距離, 指標条件, 勝率/複勝率, 加点スコア)  ※距離0は全距離
COURSE_WIN_PATTERNS = [
    ("中京", "ダ", 1800, "S1位", 35.7, 45.0),
    ("京都", "ダ", 1800, "F1位", 33.9, 45.0),
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
    
    if track_type == "芝":
        if "重賞" in class_name or "G" in class_name: s_low, s_high, f_low, f_high = 53.7, 56.7, 66.0, 68.3
        elif "OP" in class_name or "L" in class_name or "オープン" in class_name: s_low, s_high, f_low, f_high = 53.3, 56.0, 62.7, 65.0
        elif "2勝" in class_name or "3勝" in class_name: s_low, s_high, f_low, f_high = 53.3, 55.7, 64.0, 66.0
        else: s_low, s_high, f_low, f_high = 52.3, 55.3, 62.6, 65.0
    else:
        if "重賞" in class_name or "G" in class_name: s_low, s_high, f_low, f_high = 57.0, 58.3, 64.0, 67.3
        elif "OP" in class_name or "L" in class_name or "オープン" in class_name: s_low, s_high, f_low, f_high = 53.7, 56.3, 63.7, 66.0
        elif "2勝" in class_name or "3勝" in class_name: s_low, s_high, f_low, f_high = 54.3, 56.7, 63.7, 65.7
        else: s_low, s_high, f_low, f_high = 53.7, 56.0, 62.0, 64.3

    s_level = "高" if s_avg_top3 >= s_high else ("低" if s_avg_top3 <= s_low else "標準")
    f_level = "高" if f_avg_top3 >= f_high else ("低" if f_avg_top3 <= f_low else "標準")
    return s_level, f_level

def judge_race_volatility(race_df, s_lvl, f_lvl):
    if race_df.empty: return "⚖️ 標準〜小波乱（ヒモ荒れ注意）", "⚖️【標準:ヒモ荒れ】", "データなし", "vol-banner-std"
    is_newcomer = (race_df['間隔'].astype(str) == '初走').mean() > 0.5
    f_sorted = race_df.sort_values('F順位')
    f1_h = f_sorted.iloc[0]
    f1_val = float(pd.to_numeric(f1_h['F'], errors='coerce') or 0.0)
    f2_series = pd.to_numeric(race_df[race_df['F順位'] == 2]['F'], errors='coerce').dropna()
    f2_val = float(f2_series.max()) if not f2_series.empty else f1_val
    f_gap12 = f1_val - f2_val
    f1_s_rk = int(pd.to_numeric(f1_h['S順位'], errors='coerce') or 99)
    f1_c_rk = int(pd.to_numeric(f1_h['コース連順位'], errors='coerce') or 99)
    f1_k_rk = int(pd.to_numeric(f1_h['血統連順位'], errors='coerce') or 99)
    f1_in = float(pd.to_numeric(f1_h['印'], errors='coerce')) if pd.notna(f1_h['印']) else 2.0
    
    solid_score, chaos_score = 0, 0
    reasons = []

    if s_lvl == '低' and f_lvl == '低':
        if is_newcomer and f1_c_rk == 1: solid_score += 2; reasons.append("新馬戦×F1位馬がコース連1位も独占")
        elif f_gap12 >= 15.0: solid_score += 1; reasons.append(f"両低水準だがF1位が2位に+{f_gap12:.0f}pt大差")
        else: chaos_score += 3; reasons.append("S・Fとも低水準（ノートブック割引条件・波乱）")
    elif s_lvl == '低':
        if f1_s_rk >= 6 and f1_val < 72.0: chaos_score += 3; reasons.append(f"S低水準×F1位のS順位が{f1_s_rk}位（危険）")
        elif f1_val >= 72.0: solid_score += 3; reasons.append(f"S低水準だがF1位({f1_val:.0f})の絶対能力でカバー")
        else: chaos_score += 2; reasons.append("S低水準・上位馬適性不足")
    elif f_lvl == '低':
        chaos_score += 3; reasons.append("F低水準で決め手不足の混戦")
    else:
        has_aptitude = (f1_c_rk <= 3) or (f1_k_rk <= 3)
        if f1_val >= 70.0 and has_aptitude and f1_in != 0: solid_score += 3; reasons.append(f"高水準×F1位({f1_val:.0f})＆適性上位の鉄板条件")
        elif f1_val >= 71.0 and f_gap12 >= 8.0: solid_score += 3; reasons.append(f"高水準×F1位が2位に+{f_gap12:.0f}pt断層")
        else:
            if not has_aptitude: chaos_score += 2; reasons.append("高水準だがF1位に適性裏付けなし")
            if f_gap12 <= 1.0: chaos_score += 2; reasons.append("高水準で上位密集の潰し合い")

    if solid_score >= 2 and chaos_score == 0: return "🔒 堅い（順当・軸信頼）", "🔒【堅い:軸信頼】", " / ".join(reasons) + " ➔ 1着固定フォーメーション推奨", "vol-banner-solid"
    elif chaos_score >= 3: return "🌪️ 荒れる（波乱・穴狙い）", "🌪️【波乱:穴狙い】", " / ".join(reasons) + " ➔ 3連複・馬連BOXでの高配当狙い推奨", "vol-banner-chaos"
    else: return "⚖️ 標準〜小波乱（ヒモ荒れ注意）", "⚖️【標準:ヒモ荒れ】", " / ".join(reasons) + " ➔ ハイブリッドフォーメーション推奨", "vol-banner-std"

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
    if c_mark != "" and is_as and style == '先' and 0 < weight <= 459.0: return 2, 42.5, 55.0, "👑【驚異の勝率2位:42.5%】Cマーク×AS×先行×軽量"
    if f_val >= 72.0 and style == '中' and 0 < weight <= 459.0: return 3, 42.2, 73.4, "👑【驚異の勝率3位:42.2%】F≧72×中団×459kg以下"
    if is_triple and style == '中' and 0 < weight <= 459.0: return 4, 42.1, 63.2, "🔥【驚異の勝率特注】極限3重交差×中団×459kg以下"
    if f_val >= 72.0 and style == '先' and 0 < weight <= 459.0: return 4, 41.7, 77.1, "🔥【驚異の勝率特注】F≧72×先行×459kg以下"
    if f_val >= 72.0 and style == '先' and weight >= 500.0: return 4, 37.5, 70.8, "🔥【驚異の勝率特注】F≧72×先行×500kg超"
    return 0, 0.0, 0.0, ""

def evaluate_course_specific_patterns(r, venue_name, track_type, dist_val):
    """ 年間データから抽出した「競馬場×芝ダ×距離」の特注条件判定 """
    f_rk = int(pd.to_numeric(r.get('F順位', 99), errors='coerce') or 99)
    s_rk = int(pd.to_numeric(r.get('S順位', 99), errors='coerce') or 99)
    tua_rk = int(pd.to_numeric(r.get('TUA順位', 99), errors='coerce') or 99)
    arm_rk = int(pd.to_numeric(r.get('ARM順位', 99), errors='coerce') or 99)
    fup_val = pd.to_numeric(r.get('Fup2', 0), errors='coerce')
    fup_rk = int(pd.to_numeric(r.get('Fup2順位', 99), errors='coerce') or 99)
    
    conds = { "F1位": f_rk == 1, "S1位": s_rk == 1, "TUA1位": tua_rk == 1, "ARM1位": arm_rk == 1, "Fup1位": fup_rk == 1, "Fup2_6以上": fup_val >= 6 }
    
    win_flag, place_flag, ana_flag = False, False, False
    bonuses, labels = [], []
    
    for v, t, d, cond_key, rate, pts in COURSE_WIN_PATTERNS:
        if v == venue_name and t == track_type and (d == 0 or d == dist_val):
            if conds.get(cond_key, False):
                win_flag = True
                lbl = f"👑【1着特注】{v}{t}{d if d>0 else ''}×{cond_key} (勝率{rate}%)"
                bonuses.append(pts); labels.append((lbl, "win"))
                
    for v, t, d, cond_key, rate, pts in COURSE_PLACE_PATTERNS:
        if v == venue_name and t == track_type and (d == 0 or d == dist_val):
            if conds.get(cond_key, False):
                place_flag = True
                lbl = f"🎯【連軸鉄板】{v}{t}{d if d>0 else ''}×{cond_key} (複勝率{rate}%)"
                bonuses.append(pts); labels.append((lbl, "place"))
                
    for v, t, d, cond_key, rate, pts in COURSE_ANA_PATTERNS:
        if v == venue_name and t == track_type and (d == 0 or d == dist_val):
            if conds.get(cond_key, False):
                ana_flag = True
                lbl = f"💣【穴馬覚醒】{v}{t}{d if d>0 else ''}×{cond_key} (複勝率{rate}%)"
                bonuses.append(pts); labels.append((lbl, "ana"))
                
    total_pts = sum(bonuses)
    return total_pts, win_flag, place_flag, ana_flag, labels

def calc_empirical_place_rate(r, same_umaban_cnt=1):
    f_val = float(pd.to_numeric(r.get('F', 0.0), errors='coerce') or 0.0)
    f_rk = int(pd.to_numeric(r.get('F順位', 99), errors='coerce') or 99)
    s_val = float(pd.to_numeric(r.get('S', 0.0), errors='coerce') or 0.0)
    s_rk = int(pd.to_numeric(r.get('S順位', 99), errors='coerce') or 99)
    c_rk = int(pd.to_numeric(r.get('コース連順位', 99), errors='coerce') or 99)
    k_rk = int(pd.to_numeric(r.get('血統連順位', 99), errors='coerce') or 99)
    tua_rk = int(pd.to_numeric(r.get('TUA順位', 99), errors='coerce') or 99)
    arm_rk = int(pd.to_numeric(r.get('ARM順位', 99), errors='coerce') or 99)
    fup = int(pd.to_numeric(r.get('Fup2', 0), errors='coerce') or 0)
    in_v = float(pd.to_numeric(r.get('印', 2), errors='coerce') or 2.0)
    weight = float(pd.to_numeric(str(r.get('前場体重', '')).replace('kg', ''), errors='coerce') or 470.0)
    c_mark = clean_str(r.get('C(マーク)', ''))
    trainer = clean_str(r.get('調教師', ''))
    track = r.get('track', '芝')
    is_as = (f_rk <= 3) and (s_rk <= 3)
    is_ace = any(ac in trainer for ac in ACE_TRAINERS)

    rates = [15.0]
    win_rk, _, win_fuku, _ = evaluate_top3_win_pattern(r)
    if win_rk > 0: rates.append(win_fuku)
    if f_val >= 72.0: rates.append(68.2)
    if f_rk == 1 and s_rk <= 3 and k_rk <= 3: rates.append(71.1)
    if f_rk == 1 and s_rk <= 3 and c_rk <= 3: rates.append(64.6)
    if f_val >= 70.0 and s_rk <= 3: rates.append(67.6)
    if c_mark != "" and is_as: rates.append(61.6 if weight >= 460.0 else 59.7)
    if is_ace and is_as: rates.append(59.5 if weight >= 460.0 else 57.2)
    if same_umaban_cnt >= 2 and is_as: rates.append(58.6 if weight >= 460.0 else 55.2)
    if f_rk == 1 and fup >= 6: rates.append(58.6)
    if s_val >= 60.0: rates.append(57.4)
    if f_val >= 70.0: rates.append(60.5)
    if f_rk == 1 and (c_rk <= 3 or k_rk <= 3): rates.append(56.1)
    if c_mark != "" and f_rk <= 3: rates.append(55.4)
    if is_as: rates.append(53.8 if weight >= 460.0 else 52.0)
    if is_ace and f_rk <= 3: rates.append(53.3 if weight >= 460.0 else 50.9)
    if same_umaban_cnt >= 2 and f_rk <= 3: rates.append(49.4 if weight >= 460.0 else 47.5)
    if in_v >= 3 and f_rk <= 3: rates.append(47.4)
    if track == 'ダ' and tua_rk == 1 and f_rk <= 3: rates.append(45.6 if weight >= 460.0 else 43.7)
    if arm_rk == 1 and fup >= 6: rates.append(42.8)
    if c_rk == 1 and s_rk <= 3: rates.append(41.3)
    
    base_max = max(rates)
    bonus = min(len([x for x in rates if x >= 45.0]) * 0.4, 3.0)
    return round(base_max + bonus, 2)

def calc_upgraded_dynamic_score(r, venue_name, track_type, dist_val, class_name, same_umaban_cnt=1):
    score = 0.0
    f_val = float(pd.to_numeric(r.get('F', 0.0), errors='coerce') or 0.0)
    f_rk = int(pd.to_numeric(r.get('F順位', 99), errors='coerce') or 99)
    fup = int(pd.to_numeric(r.get('Fup2', 0), errors='coerce') or 0)
    tua_rk = int(pd.to_numeric(r.get('TUA順位', 99), errors='coerce') or 99)
    s_val = float(pd.to_numeric(r.get('S', 0.0), errors='coerce') or 0.0)
    s_rk = int(pd.to_numeric(r.get('S順位', 99), errors='coerce') or 99)
    c_rk = int(pd.to_numeric(r.get('コース連順位', 99), errors='coerce') or 99)
    k_rk = int(pd.to_numeric(r.get('血統連順位', 99), errors='coerce') or 99)
    trainer = clean_str(r.get('調教師', ''))
    c_mark_str = clean_str(r.get('C(マーク)', ''))
    in_val = pd.to_numeric(r.get('印', 2), errors='coerce')
    if pd.isna(in_val): in_val = 2.0

    if in_val == 0: score -= 50.0
    elif in_val == 1: score += 10.0
    elif 3 <= in_val <= 4: score += 25.0
    elif 5 <= in_val <= 7: score += 45.0
    elif 8 <= in_val <= 10: score += 75.0
    elif in_val >= 11: score += 110.0
    
    combo_hits = []
    
    # 👑 驚異の高勝率パターン
    top3_win_rk, _, _, top3_lbl = evaluate_top3_win_pattern(r)
    if top3_win_rk == 1: score += 85.0; combo_hits.append(("top3_win", top3_lbl))
    elif top3_win_rk in [2, 3]: score += 80.0; combo_hits.append(("top3_win", top3_lbl))
    elif top3_win_rk == 4: score += 70.0; combo_hits.append(("top3_win", top3_lbl))

    # ★ コース特注条件の判定と統合 ★
    course_pts, is_c_win, is_c_place, is_c_ana, c_labels = evaluate_course_specific_patterns(r, venue_name, track_type, int(dist_val))
    score += course_pts
    for lbl, l_type in c_labels:
        combo_hits.append((l_type, lbl)) # win, place, ana

    # ベース加点
    if f_val >= 72.0: score += 65.0; combo_hits.append(("golden", "👑 鉄板級 F≧72"))
    elif f_val >= 70.0 and s_rk <= 3: score += 45.0
    if f_rk == 1 and s_rk <= 3 and c_rk <= 3: score += 75.0; combo_hits.append(("golden", "🌟 極限3重交差"))
    elif f_rk == 1 and c_rk <= 3: score += 50.0
    if f_rk == 1 and c_rk == 1: score += 25.0
    if f_val >= 70.0 and k_rk <= 3: score += 45.0
    elif f_rk == 1 and k_rk <= 3: score += 35.0
    
    is_as_cross = (f_rk <= 3) and (s_rk <= 3)
    if c_mark_str and is_as_cross: score += 60.0; combo_hits.append(("golden", f"🌟 C({c_mark_str})×AS交差"))
    elif c_mark_str and f_rk <= 3: score += 45.0
    
    is_ace_stbl = any(ac in trainer for ac in ACE_TRAINERS)
    if is_ace_stbl and is_as_cross: score += 45.0
    elif is_ace_stbl and f_rk <= 3: score += 25.0

    if track_type == 'ダ' and tua_rk == 1 and f_rk <= 3: score += 65.0; combo_hits.append(("golden", "🚀 ダート最強軸(TUA1×F上位)"))
    if c_rk == 1 and s_rk <= 3: score += 45.0
    if fup == 7: score += 50.0
    elif fup >= 5: score += 35.0
    
    emp_pr = calc_empirical_place_rate(r, same_umaban_cnt=same_umaban_cnt)
    return score, top3_win_rk, is_c_win, is_c_place, is_c_ana, combo_hits, emp_pr

def main():
    st.sidebar.markdown("## 📂 CSVデータ読込管理")
    uploaded_file = st.sidebar.file_uploader("全42列マスターCSVを指定", type=['csv'])
    
    # 簡易ダミーデータローダー (Streamlit環境用)
    df = pd.DataFrame()
    if uploaded_file is not None:
        try: df = pd.read_csv(uploaded_file, encoding='utf-8-sig', low_memory=False)
        except: df = pd.read_csv(uploaded_file, encoding='cp932', low_memory=False)
    else:
        # デフォルトファイル検索
        candidates = glob.glob("*.csv")
        for c in candidates:
            if "全指数統合" in c:
                try:
                    df = pd.read_csv(c, encoding='utf-8-sig', low_memory=False)
                    st.sidebar.success(f"ローカルから {c} を読み込みました")
                    break
                except: pass

    if df.empty:
        st.warning("⚠️ 全42列マスターCSVが見つかりません。サイドバーからCSVを指定してください。")
        st.stop()

    venue_dict = {"東": "東京", "中": "中山", "京": "京都", "阪": "阪神", "名": "中京", "小": "小倉", "新": "新潟", "福": "福島", "函": "函館", "札": "札幌"}
    records = []
    
    for _, row in df.iterrows():
        race_id = clean_str(row.get('場所R', ''))
        match_v = re.match(r'([^\d]+)(\d+)', race_id)
        v_name = venue_dict.get(match_v.group(1), match_v.group(1)) if match_v else "新"
        
        dist_raw = row.get('距離', 1600)
        dist_str = clean_str(dist_raw)
        track_change = clean_str(row.get('芝ダート変わり', ''))
        raw_c = clean_str(row.get('C', row.get('C(馬)', '')))
        
        if "ダ" in dist_str or "ダ" in raw_c or track_change.endswith("ダ"): track = "ダ"
        else: track = "芝"
        dist_int = int(re.sub(r'\D', '', str(dist_raw))) if re.sub(r'\D', '', str(dist_raw)).isdigit() else 1600
        
        umaban = row.get('馬番')
        if pd.isna(pd.to_numeric(umaban, errors='coerce')): continue
        
        records.append({
            'race_id': race_id, 'race_uid': race_id, '競馬場名': v_name, 'track': track, 'dist': dist_int, 
            'class_name': clean_str(str(row.iloc[3]) if row.shape[0] > 3 else "1勝クラス"),
            '馬番': int(float(umaban)), '馬名': row.get('馬名'), '印': row.get('印', 2), 'M2': row.get('M2', 0),
            'C(マーク)': clean_str(row.get('C(マーク)', '')), '調教師': clean_str(row.get('調教師', '')), '騎手': clean_str(row.get('騎手', '')),
            '人気順位': pd.to_numeric(row.get('人気順位', 99), errors='coerce'),
            'Fup2': pd.to_numeric(row.get('Fup2', 0), errors='coerce'), 'Fup2順位': pd.to_numeric(row.get('Fup2順位', 99), errors='coerce'),
            'F': pd.to_numeric(row.get('F', 0.0), errors='coerce'), 'F順位': pd.to_numeric(row.get('F順位', 99), errors='coerce'),
            'ARM': pd.to_numeric(row.get('ARM', 0.0), errors='coerce'), 'ARM順位': pd.to_numeric(row.get('ARM順位', 99), errors='coerce'),
            'TUA': pd.to_numeric(row.get('TUA', 0.0), errors='coerce'), 'TUA順位': pd.to_numeric(row.get('TUA順位', 99), errors='coerce'),
            'S': pd.to_numeric(row.get('S', 0.0), errors='coerce'), 'S順位': pd.to_numeric(row.get('S順位', 99), errors='coerce'),
            'コース連順位': pd.to_numeric(row.get('コース連順位', 99), errors='coerce'), '血統連順位': pd.to_numeric(row.get('血統連順位', 99), errors='coerce'),
            'バランス順位': pd.to_numeric(row.get('バランス順位', 99), errors='coerce'),
            '前走脚質': clean_str(row.get('前走脚質', '')), '前走決手': clean_str(row.get('前走決手', '')), 
            '間隔': clean_str(row.get('間隔', '')), '前場体重': clean_str(row.get('前場体重', '480')),
            '種牡馬': clean_str(row.get('種牡馬', '')), '芝ダート変わり': track_change
        })

    df_clean = pd.DataFrame(records)
    jockey_umaban_counts = df_clean.groupby(['騎手', '馬番']).size().to_dict()

    existing_venues = [v for v in ["東京", "中山", "京都", "阪神", "中京", "小倉", "新潟", "福島", "函館", "札幌", "新"] if v in df_clean['競馬場名'].unique()]
    chosen_venue = st.radio("開催場選択", options=existing_venues, horizontal=True)

    v_df = df_clean[df_clean['競馬場名'] == chosen_venue]
    races_in_v = v_df[['race_uid', 'track', 'dist', 'class_name']].drop_duplicates('race_uid')
    races_sorted = sorted(races_in_v.to_dict('records'), key=lambda x: int(re.search(r'\d+', str(x['race_uid'])).group()) if re.search(r'\d+', str(x['race_uid'])) else 99)

    race_options = {r['race_uid']: f"{r['race_uid']} ({r['track']}{r['dist']}m)" for r in races_sorted}
    selected_race_uid = st.selectbox("レース選択", options=list(race_options.keys()), format_func=lambda x: race_options[x])

    race_df = df_clean[df_clean['race_uid'] == selected_race_uid].copy()
    
    scores, t3_rks, c_wins, c_places, c_anas, c_hits_list, emp_prs = [], [], [], [], [], [], []
    for _, r in race_df.iterrows():
        u_cnt = jockey_umaban_counts.get((r['騎手'], int(r['馬番'])), 1)
        sc, t3_rk, c_win, c_place, c_ana, c_hits, emp_pr = calc_upgraded_dynamic_score(r, chosen_venue, r['track'], r['dist'], r['class_name'], u_cnt)
        scores.append(sc); t3_rks.append(t3_rk); c_wins.append(c_win); c_places.append(c_place); c_anas.append(c_ana); c_hits_list.append(c_hits); emp_prs.append(emp_pr)

    race_df['dynamic_score'] = scores
    race_df['top3_win_rk'] = t3_rks
    race_df['course_win'] = c_wins
    race_df['course_place'] = c_places
    race_df['course_ana'] = c_anas
    race_df['combo_hits'] = c_hits_list
    race_df['emp_place_rate'] = emp_prs

    s_l, f_l = get_race_balance_level(race_df, race_df['track'].iloc[0], race_df['class_name'].iloc[0])
    vol_title, vol_short, vol_rsn, vol_cls = judge_race_volatility(race_df, s_l, f_l)

    st.markdown(f"<div class='{vol_cls}'><div style='font-size: 15.5px; font-weight: bold;'>📘 {vol_title}</div><div style='font-size: 13.5px; opacity: 0.95;'>🔍 {vol_rsn}</div></div>", unsafe_allow_html=True)

    # =========================================================
    # ★ 第3の馬券 ＆ ハイブリッド馬券パック の自動構築ロジック ★
    # =========================================================
    top3_win_nums = race_df[race_df['top3_win_rk'] > 0]['馬番'].tolist()
    course_win_nums = race_df[race_df['course_win']]['馬番'].tolist()
    course_place_nums = race_df[race_df['course_place']]['馬番'].tolist()
    course_ana_nums = race_df[race_df['course_ana']]['馬番'].tolist()

    f_safe_top3 = race_df.sort_values('F順位').head(3)['馬番'].tolist()
    s_safe_top3 = race_df.sort_values('S順位').head(3)['馬番'].tolist()
    a_group_nums = sorted(list(set(f_safe_top3 + s_safe_top3)))
    
    # 第3の馬券プール構築
    all_high_prob_pool = list(set(a_group_nums + top3_win_nums + course_win_nums + course_place_nums + course_ana_nums))
    pool_df = race_df[race_df['馬番'].isin(all_high_prob_pool)].sort_values(['emp_place_rate', 'dynamic_score'], ascending=[False, False])
    if len(pool_df) < 5: pool_df = race_df.sort_values(['emp_place_rate', 'dynamic_score'], ascending=[False, False])
    ranked_prob_nums = pool_df['馬番'].tolist()

    # 1着候補（特注馬＋高確率上位）
    first_col_p3 = list(set(top3_win_nums + course_win_nums))
    first_col_p3 = race_df[race_df['馬番'].isin(first_col_p3)].sort_values(['emp_place_rate', 'dynamic_score'], ascending=[False, False])['馬番'].tolist()
    for n in ranked_prob_nums:
        if len(first_col_p3) >= 2: break
        if n not in first_col_p3: first_col_p3.append(n)

    # 2着候補（連軸特注馬＋高確率上位）
    second_col_p3 = list(first_col_p3)
    for n in course_place_nums:
        if len(second_col_p3) >= 4: break
        if n not in second_col_p3: second_col_p3.append(n)
    for n in ranked_prob_nums:
        if len(second_col_p3) >= 4: break
        if n not in second_col_p3: second_col_p3.append(n)

    # 3着候補（穴馬特注馬＋その他）
    third_col_p3 = list(dict.fromkeys(second_col_p3 + course_ana_nums + ranked_prob_nums[:6]))

    st.markdown(f"""
    <div class='recom-block' style='border: 2px solid #3b82f6;'>
        <h4 style='color: #60a5fa; margin-top: 0;'>🎯 第3の馬券パターン：特注コース＆馬券内率順フォーメーション</h4>
        <div style='font-size: 13.5px; color: #cbd5e1; margin-bottom: 8px;'>
            👑 <strong>【1着特注（勝率30%超）】</strong>: <span style='color: #fca5a5;'>{", ".join(map(str, course_win_nums)) if course_win_nums else "なし"}</span><br>
            🎯 <strong>【連軸鉄板（複勝率60%超）】</strong>: <span style='color: #6ee7b7;'>{", ".join(map(str, course_place_nums)) if course_place_nums else "なし"}</span><br>
            💣 <strong>【穴馬覚醒（特注穴・複50%超）】</strong>: <span style='color: #c4b5fd;'>{", ".join(map(str, course_ana_nums)) if course_ana_nums else "なし"}</span><br>
        </div>
        <div style='background: rgba(59, 130, 246, 0.12); border: 1px solid #3b82f6; border-radius: 6px; padding: 8px 12px; margin-top: 6px;'>
            <div style='font-size: 14.5px; line-height: 1.7;'>
                🥇 <strong>1着（2頭）</strong>: <span style='color: #fbbf24; font-weight: bold; font-size: 15.5px;'>{", ".join(map(str, first_col_p3))}</span><br>
                🥈 <strong>2着（{len(second_col_p3)}頭）</strong>: <span style='color: #34d399; font-weight: bold; font-size: 15px;'>{", ".join(map(str, second_col_p3))}</span><br>
                🥉 <strong>3着（計{len(third_col_p3)}頭）</strong>: <span style='color: #38bdf8; font-weight: bold;'>{", ".join(map(str, third_col_p3))}</span>
            </div>
            <div style='margin-top: 6px; font-size: 12px; color: #9ca3af;'>※波乱判定時は【馬連BOX】または【3連複5頭BOX】({", ".join(map(str, ranked_prob_nums[:5]))})への切り替えを推奨</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ハイブリッド馬券パック構築
    honmei = race_df.sort_values(['dynamic_score', 'emp_place_rate', 'F順位'], ascending=[False, False, True]).iloc[0]
    honmei_num = int(honmei['馬番'])
    opponents = race_df[race_df['馬番'] != honmei_num].copy()
    
    taikou_df = opponents.sort_values(['emp_place_rate', 'dynamic_score'], ascending=[False, False])
    taikou = taikou_df.iloc[0] if not taikou_df.empty else honmei
    taikou_num = int(taikou['馬番'])

    # 穴馬は course_ana_nums を最優先
    ana_cands = opponents[opponents['馬番'].isin(course_ana_nums)].sort_values('dynamic_score', ascending=False)
    if not ana_cands.empty:
        ana = ana_cands.iloc[0]
    else:
        ana_cands2 = opponents[opponents['人気順位'] >= 4].sort_values(['dynamic_score', 'コース連順位'], ascending=[False, True])
        ana = ana_cands2.iloc[0] if not ana_cands2.empty else opponents.iloc[-1]
    ana_num = int(ana['馬番'])

    st.markdown(f"""
    <div class='recom-panel-go'>
        <div class='recom-title-go'>🔥 ハイブリッド馬券パック（期待値軸 × 保険網完備）</div>
        <div class='recom-row'>🥇 <strong>本命・連軸</strong>: <span class='recom-val-num'>{honmei_num}番 {honmei['馬名']}</span>（F指数: {honmei['F']} / 実証複勝率: {honmei['emp_place_rate']:.1f}% / 動的スコア: {honmei['dynamic_score']:.1f}）</div>
        <div class='recom-row'>🛡️ <strong>対抗・相手筆頭</strong>: <span class='recom-val-num'>{taikou_num}番 {taikou['馬名']}</span>（F指数: {taikou['F']} / S順位: {taikou['S順位']}位 / 実証複勝率: {taikou['emp_place_rate']:.1f}%）</div>
        <div class='recom-row'>💣 <strong>激走穴特注（保険）</strong>: <span class='recom-val-num'>{ana_num}番 {ana['馬名']}</span>（{ana['人気順位']}番人気 / 特注穴指定）</div>
    </div>
    """, unsafe_allow_html=True)

    # カルテ表示
    st.markdown("### 🏇 出走馬詳細カルテ")
    sorted_df = race_df.sort_values(['dynamic_score', 'emp_place_rate'], ascending=[False, False])
    
    for _, h in sorted_df.iterrows():
        u_no = int(h['馬番'])
        badges = []
        if u_no == honmei_num: badges.append("<span class='badge-mark-honmei'>◎ 本命</span>")
        elif u_no == taikou_num: badges.append("<span class='badge-mark-taikou'>◯ 対抗</span>")
        elif u_no == ana_num: badges.append("<span class='badge-mark-ana'>🔥 穴特注(保険)</span>")

        for lbl, l_type in h['combo_hits']:
            if l_type == "top3_win": badges.append(f"<span class='badge-top3-win'>{lbl}</span>")
            elif l_type == "golden": badges.append(f"<span class='badge-golden-combo'>{lbl}</span>")
            elif l_type == "win": badges.append(f"<span class='badge-course-win'>{lbl}</span>")
            elif l_type == "place": badges.append(f"<span class='badge-course-place'>{lbl}</span>")
            elif l_type == "ana": badges.append(f"<span class='badge-course-ana'>{lbl}</span>")
            else: badges.append(f"<span class='badge-value-combo'>{lbl}</span>")

        f_rk_cls = f"val-rank-{h['F順位']}" if h['F順位'] <= 3 else ""
        s_rk_cls = f"val-rank-{h['S順位']}" if h['S順位'] <= 3 else ""
        c_rk_cls = f"val-rank-{h['コース連順位']}" if h['コース連順位'] <= 3 else ""
        
        st.markdown(f"""
        <div class='horse-card'>
            <div class='horse-card-header'>
                <span class='race-badge-title'>{chosen_venue} {u_no}番</span>
                <span class='horse-card-title'>{h['馬番']}番 {h['馬名']}</span>
                <span style='color: #9ca3af; font-size: 13.5px;'>（{h['調教師']} / {h['騎手']} / {h['人気順位']}番人気）</span>
            </div>
            <div style='margin-bottom: 8px;'>{' '.join(badges)}</div>
            <ul class='horse-card-list'>
                <li><strong>主要指数</strong>: F指数: <span class='{f_rk_cls}'>{h['F']} (順位{h['F順位']})</span> / S指数: <span class='{s_rk_cls}'>{h['S']} (順位{h['S順位']})</span> / コース連: <span class='{c_rk_cls}'>{h['コース連順位']}位</span></li>
                <li><strong>適性・血統</strong>: TUA順位: {h['TUA順位']}位 / ARM順位: {h['ARM順位']}位 / 父 {h['種牡馬']} </li>
                <li><strong>総合動的スコア</strong>: <span style='color: #facc15; font-weight: bold; font-size: 15px;'>{h['dynamic_score']:.1f}点</span> ｜ <strong>実証馬券内率</strong>: <span style='color: #38bdf8; font-weight: bold;'>{h['emp_place_rate']:.1f}%</span></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
