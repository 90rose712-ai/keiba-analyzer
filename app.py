import streamlit as st
import pandas as pd
import numpy as np
import os
import glob
import re

st.set_page_config(
    page_title="競馬予想10 クッション値Vr - 完全統合システム",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    /* ★ 堅い／荒れる（波乱度）判定バナー専用スタイル */
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
        padding: 10px 14px;
        margin-bottom: 10px;
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
    .badge-mark-honmei {
        display: inline-flex; align-items: center; justify-content: center;
        background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
        color: #ffffff; font-size: 12.5px; font-weight: 900; padding: 2px 8px; border-radius: 4px; border: 1px solid #fca5a5; margin-right: 6px; width: auto; height: auto;
    }
    .badge-mark-taikou {
        display: inline-flex; align-items: center; justify-content: center;
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: #ffffff; font-size: 12.5px; font-weight: 900; padding: 2px 8px; border-radius: 4px; border: 1px solid #93c5fd; margin-right: 6px; width: auto; height: auto;
    }
    .badge-mark-ana {
        display: inline-flex; align-items: center; justify-content: center;
        background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
        color: #ffffff; font-size: 12.5px; font-weight: 900; padding: 2px 8px; border-radius: 4px; border: 1px solid #fde68a; margin-right: 6px; width: auto; height: auto;
    }
    .badge-c-mark { display: inline-flex; align-items: center; background: linear-gradient(135deg, #b45309 0%, #d97706 100%); color: #fff; font-weight: 900; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #fde68a; margin-right: 4px; width: auto; height: auto; }
    .badge-c-horse { display: inline-flex; align-items: center; background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); color: #fff; font-weight: 900; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #93c5fd; margin-right: 4px; width: auto; height: auto; }
    .badge-cushion-fit { display: inline-flex; align-items: center; background-color: #064e3b; color: #6ee7b7; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #10b981; margin-right: 4px; width: auto; height: auto; }
    .badge-notebook-hit { display: inline-flex; align-items: center; background-color: #831843; color: #f472b6; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #db2777; margin-right: 4px; width: auto; height: auto; }
    .badge-stable-hit { display: inline-flex; align-items: center; background-color: #1e3a8a; color: #93c5fd; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #3b82f6; margin-right: 4px; width: auto; height: auto; }
    .badge-rescued { display: inline-flex; align-items: center; background-color: #581c87; color: #f0abfc; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #c084fc; margin-right: 4px; width: auto; height: auto; }
    .badge-as-intersect { display: inline-flex; align-items: center; background: linear-gradient(135deg, #7c3aed 0%, #4c1d95 100%); color: #f5f3ff; font-weight: 900; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #a78bfa; margin-right: 4px; width: auto; height: auto; }
    .badge-top3-win { display: inline-flex; align-items: center; background: linear-gradient(135deg, #b91c1c 0%, #7c2d12 50%, #d97706 100%); color: #ffffff; font-weight: 900; font-size: 12.5px; padding: 3px 10px; border-radius: 4px; border: 2px solid #fef08a; margin-right: 5px; box-shadow: 0 0 12px rgba(250,204,21,0.8); width: auto; height: auto; }
    .badge-golden-combo { display: inline-flex; align-items: center; background: linear-gradient(135deg, #991b1b 0%, #d97706 100%); color: #fef08a; font-weight: 900; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #fde047; margin-right: 4px; box-shadow: 0 0 8px rgba(245,158,11,0.5); width: auto; height: auto; }
    .badge-value-combo { display: inline-flex; align-items: center; background: linear-gradient(135deg, #065f46 0%, #0284c7 100%); color: #e0f2fe; font-weight: 900; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #7dd3fc; margin-right: 4px; width: auto; height: auto; }
    .badge-danger-fan { display: inline-flex; align-items: center; background-color: #7f1d1d; color: #fca5a5; font-weight: 900; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #ef4444; margin-right: 4px; width: auto; height: auto; }
    .badge-high-level { display: inline-flex; align-items: center; background-color: #065f46; color: #34d399; font-weight: 900; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #10b981; margin-right: 4px; width: auto; height: auto; }
    .badge-f-eval-s { display: inline-flex; align-items: center; background: linear-gradient(135deg, #7c2d12 0%, #dc2626 100%); color: #fff; font-weight: 900; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #f87171; margin-right: 4px; box-shadow: 0 0 8px rgba(239,68,68,0.5); width: auto; height: auto; }
    .badge-f-eval-a { display: inline-flex; align-items: center; background: linear-gradient(135deg, #b45309 0%, #d97706 100%); color: #fff; font-weight: 900; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #fde68a; margin-right: 4px; width: auto; height: auto; }
    .badge-f-eval-b { display: inline-flex; align-items: center; background: #2563eb; color: #fff; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #93c5fd; margin-right: 4px; width: auto; height: auto; }
    .badge-jockey-same-umaban { display: inline-flex; align-items: center; background: linear-gradient(135deg, #b45309 0%, #d97706 100%); color: #fff; font-weight: 900; font-size: 12.5px; padding: 3px 10px; border-radius: 4px; border: 1px solid #fde68a; margin-right: 6px; box-shadow: 0 0 10px rgba(245,158,11,0.7); width: auto; height: auto; }

    /* 指数・適性順位ハイライト用スタイル（1位〜3位） */
    .val-rank-1 { color: #ffffff; background-color: #d97706; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #fde68a; }
    .val-rank-2 { color: #ffffff; background-color: #2563eb; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #93c5fd; }
    .val-rank-3 { color: #ffffff; background-color: #047857; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #6ee7b7; }

    /* ★ Fup2専用ハイライト（順位1位は必ず色付け、5点以上も順位関係なく必ず色付け） */
    .fup-badge-rank1-high { color: #ffffff; background: linear-gradient(135deg, #dc2626 0%, #d97706 100%); font-weight: 900; padding: 1px 7px; border-radius: 4px; border: 1px solid #fef08a; box-shadow: 0 0 8px rgba(245,158,11,0.6); }
    .fup-badge-rank1 { color: #ffffff; background-color: #d97706; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #fde68a; }
    .fup-badge-top { color: #ffffff; background: linear-gradient(135deg, #991b1b 0%, #dc2626 100%); font-weight: 900; padding: 1px 7px; border-radius: 4px; border: 1px solid #fca5a5; box-shadow: 0 0 6px rgba(239,68,68,0.5); }
    .fup-badge-mid { color: #ffffff; background: linear-gradient(135deg, #b45309 0%, #ea580c 100%); font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #fdba74; }
    .fup-badge-low { color: #c9d1d9; }
    
    .filter-result-box {
        background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
        border: 2px solid #3b82f6;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

ACE_TRAINERS = ['藤原', '杉山', '矢作', '中内田', '木村', '堀', '友道', '池添', '吉岡', '大竹', '斉藤', '音無', '国枝']

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

    if t4 > 56.0 or l1 > 13.0:
        return "基準外(軽め)", "#374151"

    if l1 < l2: # 加速ラップ
        if l1 <= 11.9: return "A3 (終い11秒台加速🔥)", "#dc2626"
        elif 12.0 <= l2 <= 12.9 and 12.0 <= l1 <= 12.9: return "A2 (終い2Fともに12秒台加速)", "#d97706"
        elif l2 >= 13.0 and 12.0 <= l1 <= 12.9: return "A1 (終いのみ12秒台加速)", "#2563eb"
        else: return "A型 (加速)", "#047857"
    else: # 減速ラップ
        if l2 <= 11.9: return "B3 (2F目11秒台減速)", "#7c2d12"
        elif 12.0 <= l2 <= 12.9 and 12.0 <= l1 <= 12.9: return "B2 (終い2Fともに12秒台減速)", "#4b5563"
        elif 12.0 <= l2 <= 12.9 and l1 >= 13.0: return "B1 (2Fのみ12秒台減速)", "#4b5563"
        else: return "B型 (減速)", "#374151"

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
        else:
            cond_c = False
    except:
        cond_c = False

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
        if s_vals.empty:
            s_vals = pd.to_numeric(race_subset['S'], errors='coerce').dropna().sort_values(ascending=False).head(3)
        if f_vals.empty:
            f_vals = pd.to_numeric(race_subset['F'], errors='coerce').dropna().sort_values(ascending=False).head(3)
        s_avg_top3 = s_vals.mean() if len(s_vals) > 0 else 50.0
        f_avg_top3 = f_vals.mean() if len(f_vals) > 0 else 60.0
    except:
        return "標準", "標準"

    r_uid_str = str(race_subset['race_uid'].iloc[0]) if not race_subset.empty and 'race_uid' in race_subset.columns else ""
    m_rn = re.search(r'\d+', r_uid_str)
    r_no = int(m_rn.group()) if m_rn else 1

    if track_type == "芝":
        if "重賞" in class_name or "G" in class_name:
            s_low, s_high, f_low, f_high = 53.7, 56.7, 66.0, 68.3
        elif "OP" in class_name or "L" in class_name or "オープン" in class_name or r_no == 11:
            s_low, s_high, f_low, f_high = 53.3, 56.0, 62.7, 65.0
        elif "2勝" in class_name or "3勝" in class_name or r_no in [9, 10]:
            s_low, s_high, f_low, f_high = 53.3, 55.7, 64.0, 66.0
        else:
            s_low, s_high, f_low, f_high = 52.3, 55.3, 62.6, 65.0
    else:
        if "重賞" in class_name or "G" in class_name:
            s_low, s_high, f_low, f_high = 57.0, 58.3, 64.0, 67.3
        elif "OP" in class_name or "L" in class_name or "オープン" in class_name or r_no == 11:
            s_low, s_high, f_low, f_high = 53.7, 56.3, 63.7, 66.0
        elif "2勝" in class_name or "3勝" in class_name or r_no in [9, 10]:
            s_low, s_high, f_low, f_high = 54.3, 56.7, 63.7, 65.7
        else:
            s_low, s_high, f_low, f_high = 53.7, 56.0, 62.0, 64.3

    s_level = "高" if s_avg_top3 >= s_high else ("低" if s_avg_top3 <= s_low else "標準")
    f_level = "高" if f_avg_top3 >= f_high else ("低" if f_avg_top3 <= f_low else "標準")
    return s_level, f_level

def judge_race_volatility(race_df, s_lvl, f_lvl):
    if race_df.empty:
        return "⚖️ 標準〜小波乱（ヒモ荒れ注意）", "⚖️【標準:ヒモ荒れ】", "データなし", "vol-banner-std"

    is_newcomer = (race_df['間隔'].astype(str) == '初走').mean() > 0.5
    f_sorted = race_df.sort_values('F順位')
    s_sorted = race_df.sort_values('S順位')

    f1_h = f_sorted.iloc[0]
    s1_h = s_sorted.iloc[0]

    f1_val = float(pd.to_numeric(f1_h['F'], errors='coerce') or 0.0)
    f2_series = pd.to_numeric(race_df[race_df['F順位'] == 2]['F'], errors='coerce').dropna()
    f2_val = float(f2_series.max()) if not f2_series.empty else f1_val
    f_gap12 = f1_val - f2_val

    f_2_5_series = pd.to_numeric(race_df[(race_df['F順位'] >= 2) & (race_df['F順位'] <= 5)]['F'], errors='coerce').dropna()
    f_2_5_mean = float(f_2_5_series.mean()) if not f_2_5_series.empty else f1_val
    f_diff_25 = f1_val - f_2_5_mean

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
        if is_newcomer and f1_c_rk == 1:
            solid_score += 2
            reasons.append("新馬戦×F1位馬がコース連1位も独占し適性突出")
        elif f_gap12 >= 15.0:
            solid_score += 1
            reasons.append(f"両低水準だがF1位が2位に+{f_gap12:.0f}ptの大差")
        else:
            chaos_score += 3
            reasons.append("S・Fとも低水準（ノートブック割引条件：両指数上位でも過信禁物・波乱傾向）")
    elif s_lvl == '低':
        if f1_s_rk >= 6 and f1_val < 72.0:
            chaos_score += 3
            reasons.append(f"S低水準×F1位のS順位が{f1_s_rk}位（ノートブック割引条件：S6位以下は人気でも一段下げる）")
        elif f1_val >= 72.0 or (f1_val >= 68.0 and f_diff_25 >= 8.0 and f1_s_rk <= 5 and (f1_c_rk <= 3 or f1_k_rk <= 3 or as_cnt >= 2)):
            solid_score += 3
            reasons.append(f"S低水準×F1位({f1_val:.0f})が絶対値・相手差(+{f_diff_25:.1f}pt)とも抜けS5位以内を確保")
        else:
            chaos_score += 2
            reasons.append("S低水準だがF上位馬に相手差・適性裏付け不足")
    elif f_lvl == '低':
        if s1_val >= 60.0 and s1_f_rk <= 3:
            solid_score += 3
            reasons.append(f"F低水準×S1位({s1_val:.0f})がS60以上＆F3位以内で抜ける")
        elif f_diff_25 >= 11.0 and s1_val >= 55.0:
            solid_score += 2
            reasons.append(f"F低水準だがF1位が相手2〜5位平均に+{f_diff_25:.1f}ptの大差")
        else:
            chaos_score += 3
            reasons.append(f"F低水準×S1位(S{s1_val:.0f}/F{s1_f_rk}位)がS60未満またはF4位以下の割引条件に合致")
    else:
        has_aptitude = (f1_c_rk <= 3) or (f1_k_rk <= 3)
        if f1_val >= 70.0 and f_diff_25 >= 6.0 and has_aptitude and f1_in != 0:
            solid_score += 3
            reasons.append(f"高水準×F1位({f1_val:.0f})が相手差+{f_diff_25:.1f}pt＆コース/血統連上位の鉄板条件")
        elif f1_val >= 71.0 and f_gap12 >= 8.0:
            solid_score += 3
            reasons.append(f"高水準×F1位({f1_val:.0f})が2位に+{f_gap12:.0f}ptの能力断層")
        else:
            if not has_aptitude:
                chaos_score += 2
                reasons.append(f"高水準だがF1位のコース連({f1_c_rk}位)・血統連({f1_k_rk}位)が共に4位以下で適性裏付けなし")
            if f_diff_25 < 6.0 or f_gap12 <= 1.0:
                chaos_score += 2
                reasons.append(f"高水準で上位密集の潰し合い(F1-2差{f_gap12:.0f}pt/対2-5位差+{f_diff_25:.1f}pt)")
            if f1_in == 0:
                chaos_score += 2
                reasons.append("F1位が前走馬券内0頭(印=0)で信頼度低下")

    if solid_score >= 2 and chaos_score == 0:
        return (
            "🔒 堅い（順当・軸信頼） [検証実績: 1番人気複勝率88.2% / F1位複勝率82.4% / 波乱率0%]",
            "🔒【堅い:軸信頼】",
            " / ".join(reasons) + " ➔ 本命・F1位からの単勝・馬単・絞った連系勝負推奨",
            "vol-banner-solid"
        )
    elif chaos_score >= 3:
        return (
            "🌪️ 荒れる（波乱・穴狙い） [検証実績: 波乱発生率73.3% / 1番人気複勝率20.0%(危険)]",
            "🌪️【波乱:穴狙い】",
            " / ".join(reasons) + " ➔ 人気馬過信禁物！コース連1位×S上位やTUA/ARM上位の中穴・ワイド・3連複手広め推奨",
            "vol-banner-chaos"
        )
    else:
        return (
            "⚖️ 標準〜小波乱（ヒモ荒れ注意） [検証実績: 軸は堅実も2〜3着に中穴台頭]",
            "⚖️【標準:ヒモ荒れ】",
            " / ".join(reasons) + " ➔ A群上位を軸にしつつ3列目・ワイド保険に中穴（Z馬・コース連上位）を絡める構成推奨",
            "vol-banner-std"
        )

def evaluate_top3_win_pattern(r):
    """
    ★ 2026年間4.1万頭検証：1着固定で勝負できる驚異の高勝率パターン（トップ3＋準特注）判定関数
    戻り値: (該当ランク: 1〜4 or 0, 推定勝率, 推定複勝率, バッジラベル)
    """
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

    # 👑 第1位: F≧72 × 前走[後] × 500kg以上 (勝率45.5% / 複勝率72.7%)
    if f_val >= 72.0 and style == '後' and weight >= 500.0:
        return 1, 45.5, 72.7, "👑【驚異の勝率1位:45.5%/複72.7%】F≧72×追込×500kg超"

    # 👑 第2位: C(マーク)あり × AS交差 × 前走[先] × 459kg以下 (勝率42.5% / 複勝率55.0%)
    if c_mark != "" and is_as and style == '先' and 0 < weight <= 459.0:
        return 2, 42.5, 55.0, f"👑【驚異の勝率2位:42.5%/複55.0%】C({c_mark})×AS交差×先行×459kg以下"

    # 👑 第3位: F≧72 × 前走[中] × 459kg以下 (勝率42.2% / 複勝率73.4%)
    if f_val >= 72.0 and style == '中' and 0 < weight <= 459.0:
        return 3, 42.2, 73.4, "👑【驚異の勝率3位:42.2%/複73.4%】F≧72×中団×459kg以下"

    # 🔥 準特注(40%前後): 極限3重交差×中団×459kg以下(42.1%) / F≧72×先行×459kg以下(41.7%) / F≧72×先行×500kg以上(37.5%)
    if is_triple and style == '中' and 0 < weight <= 459.0:
        return 4, 42.1, 63.2, "🔥【驚異の勝率:42.1%/複63.2%】極限3重交差×中団×459kg以下"
    if f_val >= 72.0 and style == '先' and 0 < weight <= 459.0:
        return 4, 41.7, 77.1, "🔥【驚異の勝率:41.7%/複77.1%】F≧72×先行×459kg以下"
    if f_val >= 72.0 and style == '先' and weight >= 500.0:
        return 4, 37.5, 70.8, "🔥【驚異の勝率:37.5%/複70.8%】F≧72×先行×500kg超"

    return 0, 0.0, 0.0, ""

def calc_empirical_place_rate(r, same_umaban_cnt=1):
    """
    ★ これまでのロジックに基づく「年間4.1万頭実証・馬券内率（複勝率%）」算出関数
    第3の馬券パターンで馬券内率が高い順に序列化する際に使用
    """
    f_val = float(pd.to_numeric(r.get('F', 0.0), errors='coerce') or 0.0)
    f_rk = int(pd.to_numeric(r.get('F順位', 99), errors='coerce') or 99)
    s_val = float(pd.to_numeric(r.get('S', 0.0), errors='coerce') or 0.0)
    s_rk = int(pd.to_numeric(r.get('S順位', 99), errors='coerce') or 99)
    c_rk = int(pd.to_numeric(r.get('コース連順位', 99), errors='coerce') or 99)
    k_rk = int(pd.to_numeric(r.get('血統連順位', 99), errors='coerce') or 99)
    tua_rk = int(pd.to_numeric(r.get('TUA順位', 99), errors='coerce') or 99)
    arm_rk = int(pd.to_numeric(r.get('ARM順位', 99), errors='coerce') or 99)
    fup = int(pd.to_numeric(r.get('Fup2', 0), errors='coerce') or 0)
    fup_rk = int(pd.to_numeric(r.get('Fup2順位', 99), errors='coerce') or 99)
    in_v = float(pd.to_numeric(r.get('印', 2), errors='coerce') or 2.0)
    w_raw = pd.to_numeric(str(r.get('前場体重', '')).replace('kg', ''), errors='coerce')
    weight = float(w_raw) if pd.notnull(w_raw) else 470.0
    c_mark = clean_str(r.get('C(マーク)', ''))
    trainer = clean_str(r.get('調教師', ''))
    track = r.get('track', '芝')

    is_as = (f_rk <= 3) and (s_rk <= 3)
    is_ace = any(ac in trainer for ac in ACE_TRAINERS)

    rates = [15.0]
    win_rk, _, win_fuku, _ = evaluate_top3_win_pattern(r)
    if win_rk > 0:
        rates.append(win_fuku)

    if f_val >= 72.0: rates.append(68.2)
    if f_rk == 1 and s_rk <= 3 and k_rk <= 3: rates.append(71.1)
    if f_rk == 1 and s_rk <= 3 and c_rk <= 3: rates.append(64.6)
    if f_val >= 70.0 and s_rk <= 3: rates.append(67.6)
    if c_mark != "" and is_as:
        rates.append(61.6 if weight >= 460.0 else 59.7)
    if is_ace and is_as:
        rates.append(59.5 if weight >= 460.0 else 57.2)
    if same_umaban_cnt >= 2 and is_as:
        rates.append(58.6 if weight >= 460.0 else 55.2)
    if f_rk == 1 and fup >= 6: rates.append(58.6)
    if s_val >= 60.0: rates.append(57.4)
    if f_val >= 70.0: rates.append(60.5)
    if f_rk == 1 and (c_rk <= 3 or k_rk <= 3): rates.append(56.1)
    if c_mark != "" and f_rk <= 3: rates.append(55.4)
    if is_as:
        rates.append(53.8 if weight >= 460.0 else 52.0)
    if f_rk == 1: rates.append(53.5)
    if is_ace and f_rk <= 3:
        rates.append(53.3 if weight >= 460.0 else 50.9)
    if same_umaban_cnt >= 2 and f_rk <= 3:
        rates.append(49.4 if weight >= 460.0 else 47.5)
    if in_v >= 3 and f_rk <= 3: rates.append(47.4)
    if s_rk <= 3 and fup_rk == 1: rates.append(47.4)
    if s_rk == 1: rates.append(47.0)
    if f_rk <= 3: rates.append(45.3)
    if track == 'ダ' and tua_rk == 1 and f_rk <= 3:
        rates.append(45.6 if weight >= 460.0 else 43.7)
    if arm_rk == 1 and fup >= 6: rates.append(42.8)
    if c_rk == 1 and s_rk <= 3: rates.append(41.3)
    if s_rk <= 3: rates.append(39.5)

    # 複数条件が重なった場合の微小ボーナスを加味して返す
    base_max = max(rates)
    bonus = min(len([x for x in rates if x >= 45.0]) * 0.4, 3.0)
    return round(base_max + bonus, 2)

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
    sire = clean_str(r.get('種牡馬', ''))
    track_change = clean_str(r.get('芝ダート変わり', ''))
    run_style = clean_str(r.get('前走脚質', ''))
    interval = str(r.get('間隔', ''))
    weight = float(pd.to_numeric(str(r.get('前場体重', '480')).replace('kg', ''), errors='coerce') or 480.0)
    c_mark_str = clean_str(r.get('C(マーク)', ''))

    f_eval_label, f_eval_score = evaluate_f_index_strict(r, race_subset)
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

    # -------------------------------------------------------------
    # ★ 1着固定で勝負できる驚異の高勝率パターン（トップ3＋準特注）の判定・特大加点
    # -------------------------------------------------------------
    top3_win_rk, top3_w_rate, top3_p_rate, top3_lbl = evaluate_top3_win_pattern(r)
    if top3_win_rk == 1:
        score += 85.0
        combo_hits.append(("top3_win", top3_lbl))
    elif top3_win_rk in [2, 3]:
        score += 80.0
        combo_hits.append(("top3_win", top3_lbl))
    elif top3_win_rk == 4:
        score += 70.0
        combo_hits.append(("top3_win", top3_lbl))

    # -------------------------------------------------------------
    # ★ 京都芝2200m 特注セオリー（記憶済みルール）の自動連動
    # -------------------------------------------------------------
    if venue_name == "京都" and track_type == "芝" and int(dist_val) == 2200:
        if f_rk == 1 or f_val >= 70.0:
            score += 40.0
            combo_hits.append(("golden", "🎯 京都芝2200特注: F1位/F≧70[複83〜85%]"))
        if f_rk == 1 and c_rk <= 3:
            score += 35.0
            combo_hits.append(("golden", "👑 京都芝2200絶対軸: F1位×コース連上位[複100%]"))
        if run_style == "先" or is_as_cross:
            score += 20.0
        elif run_style == "後":
            score -= 20.0
            combo_hits.append(("value", "⚠️ 京都芝2200割引: 前走後方脚質"))
        if 5 <= u_no <= 7:
            score += 25.0
            combo_hits.append(("value", f"🎯 京都芝2200絶好枠({u_no}番)"))
        elif u_no in [11, 13]:
            score -= 20.0
    
    # -------------------------------------------------------------
    # ★ 年間41,018頭検証に基づく超高確率・高期待値パターンの動的加点＆バッジ付与
    # -------------------------------------------------------------
    if f_val >= 72.0:
        score += 65.0
        combo_hits.append(("golden", "👑 鉄板級 F≧72 [年間複68.2%]"))
    elif f_val >= 70.0 and s_rk <= 3:
        score += 45.0
        combo_hits.append(("golden", "🔥 極限クロス(F≧70×S上位)[複67.6%]"))

    if f_rk == 1 and s_rk <= 3 and c_rk <= 3:
        score += 75.0
        combo_hits.append(("golden", "🌟 極限3重交差(F1位×S上位×コース連上位)[複64.6%]"))
    elif f_rk == 1 and c_rk <= 3:
        score += 50.0
        combo_hits.append(("golden", "🎯 F1位×コース連上位[年間複56.1%]"))

    if f_rk == 1 and c_rk == 1:
        score += 25.0
        combo_hits.append(("golden", "💯 F1位×コース連1位(完全一致)"))

    if f_val >= 70.0 and k_rk <= 3:
        score += 45.0
        combo_hits.append(("golden", "🧬 F≧70×血統連上位[高信頼]"))
    elif f_rk == 1 and k_rk <= 3:
        score += 35.0
        combo_hits.append(("golden", "🧬 F1位×血統連上位[年間複56.1%]"))

    if c_mark_str and is_as_cross:
        score += 60.0
        combo_hits.append(("golden", f"🌟 C({c_mark_str})×AS交差 [年間勝31.9%/複59.7%]"))
    elif c_mark_str and f_rk <= 3:
        score += 45.0
        combo_hits.append(("golden", f"🌟 C({c_mark_str})×F上位 [年間勝28.1%/複55.4%]"))

    if is_ace_stbl and is_as_cross:
        score += 45.0
        combo_hits.append(("golden", "🌟 特選厩舎×AS交差 [年間勝25.5%/複57.2%]"))
    elif is_ace_stbl and f_rk <= 3:
        score += 25.0
        combo_hits.append(("value", "⭐ 特選厩舎×F上位 [年間複50.9%]"))

    if same_umaban_cnt >= 2 and is_as_cross:
        score += 45.0
        combo_hits.append(("golden", "🌟 同馬番複数×AS交差 [年間複55.2%]"))
    elif same_umaban_cnt >= 2 and f_rk <= 3:
        score += 30.0
        combo_hits.append(("value", "⭐ 同馬番複数×F上位 [年間複47.5%]"))

    if in_val >= 3 and f_rk <= 3:
        score += 30.0
        combo_hits.append(("value", f"🌟 前走{int(in_val)}頭馬券内×F上位 [年間複47.4%]"))

    if track_type == 'ダ' and tua_rk == 1 and f_rk <= 3:
        score += 65.0
        combo_hits.append(("golden", "🚀 ダート最強軸(TUA1位×F上位)[年間複43.7%]"))
    elif track_type == '芝' and tua_rk == 1 and f_rk <= 3:
        score += 40.0
        combo_hits.append(("value", "🌐 TUA1位×F上位"))

    if track_type == 'ダ' and f_rk == 1 and tua_rk <= 3 and tua_rk != 1:
        score += 45.0
        combo_hits.append(("golden", "🔥 ダート黄金(F1位×TUA上位)"))

    if c_rk == 1 and s_rk <= 3:
        score += 45.0
        combo_hits.append(("value", "💣 歪み激走特注(コース連1位×S上位)[年間複41.3%/平均3.5人気]"))

    if f_rk <= 3 and c_rk <= 3 and k_rk <= 3:
        score += 40.0
        combo_hits.append(("value", "💎 3複合上位(F×コース連×血統連)"))
    if f_rk <= 3 and hc_rk <= 3 and c_rk <= 3:
        score += 40.0
        combo_hits.append(("value", "⚡ 3複合上位(F×坂路調×コース連)"))

    if track_type == '芝' and s_rk <= 3 and fup_rk <= 3:
        score += 30.0
        combo_hits.append(("value", "🌱 芝ヒモ特注(S上位×Fup2上位)"))
    if s_val >= 60.0:
        score += 30.0
        combo_hits.append(("value", "⚡ 高S指数(S≧60)[年間複57.4%]"))

    # -------------------------------------------------------------
    # ★ ノートブック『S・F指数レースバランス攻略』条件の個別馬加点・割引
    # -------------------------------------------------------------
    s_lvl_r, f_lvl_r = get_race_balance_level(race_subset, track_type, class_name)
    if s_lvl_r == "低" and f_rk <= 3 and f_val >= 68.0 and s_rk <= 5:
        score += 35.0
        combo_hits.append(("golden", "📘 NB信頼: S低水準×F上位(F≧68)"))
    elif s_lvl_r == "低" and f_rk <= 3 and s_rk >= 6 and f_val < 72.0:
        score -= 20.0
        combo_hits.append(("value", "⚠️ NB割引: S低水準×F上位のみ(S6位以下)"))

    if f_lvl_r == "低" and s_rk <= 3 and s_val >= 60.0 and f_rk <= 3:
        score += 35.0
        combo_hits.append(("golden", "📘 NB信頼: F低水準×S≧60＆F上位"))
    elif f_lvl_r == "低" and s_rk <= 3 and f_rk >= 4:
        score -= 15.0
        combo_hits.append(("value", "⚠️ NB割引: F低水準×S上位(F4位以下)"))

    # -------------------------------------------------------------
    # 既存の極秘ノートブック＆厩舎ロジック（完全維持）
    # -------------------------------------------------------------
    if track_type == 'ダ' and s_rk == 1 and weight >= 480:
        score += 50.0; nb_hits.append("🐎 ダートで食う(S1位・大型)")
    
    is_a3_lap = False
    try:
        l1 = float(s_row_laps.get('Lap1', 99) or 99)
        l2 = float(s_row_laps.get('Lap2', 99) or 99)
        if l1 <= 11.9 and l1 < l2:
            is_a3_lap = True
    except:
        pass

    if interval.isdigit() and int(interval) >= 12 and is_a3_lap:
        score += 60.0; nb_hits.append("🔥 Z11/Nなごり(休み明け12週+A3)")

    try:
        w_5f_val = float(w_row_data.get('5F', 99) or 99)
        s_time1 = float(s_row_laps.get('Time1', 99) or 99)
        if arm_rk <= 3 and w_5f_val <= 69.0 and s_time1 <= 59.9:
            score += 55.0; nb_hits.append("🌲 Ｃ馬特注(ウッド鉄則)")
    except:
        pass

    if arm_rk == 1 and fup >= 6:
        score += 50.0; nb_hits.append("✨ ARMS×FUP(黄金クロス:単勝特化)")

    if track_type == 'ダ' and tua_val >= 190.0 and tua_rk <= 3 and s_rk <= 8:
        score += 40.0; nb_hits.append("💎 TUAダート特注")

    if ('芝→ダ' in track_change or 'ダ→芝' in track_change) and tua_rk <= 3:
        score += 30.0; nb_hits.append("🔄 トラック変わり激走特注")

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

    is_sss = (f_val >= 65.0) and (arm_val >= 120.0) and (tua_val >= 200.0)
    is_quad_crown = (f_rk <= 3) and (arm_rk <= 3) and (tua_rk <= 3) and (fup >= 5)
    is_solid_axis = (f_rk == 1) and (fup >= 5)
    is_kakugen = (fup == 7)
    is_f65_top = (f_val >= 65.0) or (f_eval_label == "S評価")
    has_strong_bonus = is_sss or is_quad_crown or is_solid_axis or is_kakugen or is_f65_top or len(nb_hits) > 0 or len(stable_hits) > 0 or len(combo_hits) > 0 or (fup >= 6) or (arm_rk <= 2)

    is_rescued = has_strong_bonus
    if not is_rescued:
        if c_rk >= 6: score -= 10.0
        if b_rk >= 6: score -= 5.0
        if pop <= 3 and fup <= 1: score -= 15.0

    emp_place_rate = calc_empirical_place_rate(r, same_umaban_cnt=same_umaban_cnt)
    return score, is_rescued, is_sss, nb_hits, stable_hits, f_eval_label, combo_hits, top3_win_rk, emp_place_rate

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
    
    if max_f >= 72.0:
        return "S"
    elif max_f >= 66.0 and (high_in_count >= 3 or high_m2_count >= 3 or f1_course_count >= 1 or dirt_tua_f_count >= 1):
        return "S"
    elif as_count == 1 and max_f >= 63.0:
        return "S"
    elif max_f >= 62.0 or gc_count >= 1 or high_in_count >= 2 or f1_course_count >= 1 or dirt_tua_f_count >= 1:
        return "A"
    elif max_f >= 55.0 or as_count >= 2:
        return "B"
    else:
        return "C"

def get_rank_class(rank_val):
    try:
        r = int(rank_val)
        if r == 1: return "val-rank-1"
        elif r == 2: return "val-rank-2"
        elif r == 3: return "val-rank-3"
    except:
        pass
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
      
    uploaded_file = st.sidebar.file_uploader("全42列マスターCSVを指定", type=['csv'])
    if uploaded_file is not None:
        for enc in ['utf-8-sig', 'utf-8', 'cp932', 'shift-jis']:
            try:
                df_raw = pd.read_csv(uploaded_file, encoding=enc, low_memory=False)
                if not df_raw.empty and df_raw.shape[1] >= 38:
                    loaded_filename = uploaded_file.name
                    break
            except Exception:
                continue

    if df_raw.empty:
        st.markdown("<div class='race-type-banner race-type-normal'>⚠️ 全42列マスターCSVが見つかりません。サイドバーからCSVを指定してください。</div>", unsafe_allow_html=True)
        st.stop()

    if '日付' in df_raw.columns:
        unique_dates = [str(d).strip() for d in df_raw['日付'].dropna().unique() if str(d).strip() != "" and str(d).strip() != "日付"]
        if len(unique_dates) > 1:
            selected_date_filter = st.sidebar.selectbox("📅 開催日選択（年間CSV対応）", options=unique_dates[::-1], index=0)
            df_raw = df_raw[df_raw['日付'].astype(str).str.strip() == selected_date_filter].copy()

    st.sidebar.success(f"✅ 指数CSV読込成功: {loaded_filename} (対象{len(df_raw)}頭)")

    venue_dict = {"東": "東京", "中": "中山", "京": "京都", "阪": "阪神", "名": "中京", "小": "小倉", "新": "新潟", "福": "福島", "函": "函館", "札": "札幌"}
    records = []
    
    sakaro_dict = {}
    if not sakaro_raw.empty:
        s_df = sakaro_raw.copy()
        s_df['馬名_clean'] = s_df['馬名'].astype(str).str.strip().str.replace(r'[\*\$\s ]', '', regex=True)
        s_df['調教師_clean'] = s_df['調教師'].astype(str).str.strip().str.replace(r'[\*\$\s ]', '', regex=True)
        s_df['年月日_num'] = pd.to_numeric(s_df['年月日'], errors='coerce')
        for (h_name, t_name), group in s_df.groupby(['馬名_clean', '調教師_clean']):
            latest_row = group.sort_values('年月日_num').iloc[-1]
            sakaro_dict[(h_name, t_name)] = latest_row

    wood_dict = {}
    if not wood_raw.empty:
        w_df = wood_raw.copy()
        w_df['馬名_clean'] = w_df['馬名'].astype(str).str.strip().str.replace(r'[\*\$\s ]', '', regex=True)
        w_df['調教師_clean'] = w_df['調教師'].astype(str).str.strip().str.replace(r'[\*\$\s ]', '', regex=True)
        w_df['年月日_num'] = pd.to_numeric(w_df['年月日'], errors='coerce')
        for (h_name, t_name), group in w_df.groupby(['馬名_clean', '調教師_clean']):
            latest_row = group.sort_values('年月日_num').iloc[-1]
            wood_dict[(h_name, t_name)] = latest_row

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
        if "ダ" in dist_str or "ダ" in raw_c or track_change.endswith("ダ"):
            track = "ダ"
        elif "芝" in dist_str or "芝" in raw_c or track_change.endswith("芝"):
            track = "芝"
        else:
            track = "芝"
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

        h_clean = clean_str(horse).replace('*', '').replace('$', '')
        t_clean = clean_str(trainer)
        
        s_row = sakaro_dict.get((h_clean, t_clean), pd.Series())
        w_row = wood_dict.get((h_clean, t_clean), pd.Series())

        if horse and pd.notnull(pd.to_numeric(umaban, errors='coerce')):
            records.append({
                'race_id': race_id, 'race_uid': race_id, '競馬場名': v_name, 'track': track, 'dist': dist_int, 'class_name': class_str,
                '馬番': int(float(umaban)), '馬名': horse, '印': in_num, 'M2': m2_num,
                'C(マーク)': c_mark, 'C(馬)': c_horse,
                '調教師': trainer, '騎手': jockey, '種牡馬': sire, '人気順位': int(float(pop)) if pd.notnull(pd.to_numeric(pop, errors='coerce')) else 99,
                'Fup2': fup, 'Fup2順位': fup_rk, 'F': f_val, 'F順位': f_rk, 'ARM': arm_val, 'ARM順位': arm_rk,
                'TUA': tua_val, 'TUA順位': tua_rk, 'S': s_val, 'S順位': s_rk,
                's_row': s_row, 'w_row': w_row,
                '坂路T4': pd.to_numeric(s_row.get('Time4', np.nan), errors='coerce'),
                '坂路L2': pd.to_numeric(s_row.get('Lap2', np.nan), errors='coerce'),
                '坂路L1': pd.to_numeric(s_row.get('Lap1', np.nan), errors='coerce'),
                '坂路加速': pd.to_numeric(s_row.get('Lap2', np.nan), errors='coerce') - pd.to_numeric(s_row.get('Lap1', np.nan), errors='coerce'),
                'ウッド5F': pd.to_numeric(w_row.get('5F', np.nan), errors='coerce'),
                'ウッドL1': pd.to_numeric(w_row.get('Lap1', np.nan), errors='coerce'),
                '坂路調順位': hc_rk, '坂路血順位': hk_rk, '時計血順位': tk_rk,
                'コース連順位': c_rk, '血統連順位': k_rk, 'バランス順位': b_rk,
                '芝ダート変わり': track_change, '前走脚質': run_style, '前走決手': pass_style,
                '間隔': interval, '前場体重': weight_val, '日付': race_date
            })

    df = pd.DataFrame(records)
    if df.empty:
        st.error("解析可能な有効データが存在しません。")
        st.stop()

    race_date_str = str(df['日付'].iloc[0]) if not df.empty and '日付' in df.columns else "11.01"

    st.sidebar.markdown('---')
    st.sidebar.markdown("### 🌿 馬場・クッション値設定")
    track_cond = st.sidebar.selectbox("芝馬場状態", ["良", "稍重", "重", "不良"], index=0)
    cushion_val = st.sidebar.slider("当日クッション値", min_value=6.0, max_value=12.5, value=9.5, step=0.1, format="%.1f")

    st.markdown(f"<div class='date-header-badge'>📅 開催日: 2026年{race_date_str} | JRAデータ解析エンジン「競馬予想10 クッション値Vr」</div>", unsafe_allow_html=True)

    # 全レースの波乱度（堅い／荒れる）を事前計算してキャッシュ
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
    # ★ サイドバー：フィルタチェックボックス ＆ リアルタイム該当馬リスト表示
    # -------------------------------------------------------------
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎯 チェックBOX 狙い目・レベルフィルタ")

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
            f_rk_v = int(r['F順位']) if pd.notnull(r['F順位']) else 99
            s_rk_v = int(r['S順位']) if pd.notnull(r['S順位']) else 99
            is_ace = any(ac in str(r['調教師']) for ac in ACE_TRAINERS)
            c_mk = str(r['C(マーク)']).strip() if pd.notnull(r['C(マーク)']) else ""

            if filter_type == "top3_win_pattern":
                w_rk, _, _, _ = evaluate_top3_win_pattern(r)
                if w_rk > 0: is_match = True
            elif filter_type == "high_in":
                if pd.notnull(r['印']) and float(r['印']) >= 3: is_match = True
            elif filter_type == "high_in_f_top3":
                if pd.notnull(r['印']) and float(r['印']) >= 3 and f_rk_v <= 3: is_match = True
            elif filter_type == "high_m2":
                if pd.notnull(r['M2']) and float(r['M2']) >= 5: is_match = True
            elif filter_type == "danger_in0":
                if pd.notnull(r['印']) and float(r['印']) == 0: is_match = True
            elif filter_type == "arms_fup":
                if pd.notnull(r['ARM順位']) and int(r['ARM順位']) == 1 and pd.notnull(r['Fup2']) and int(r['Fup2']) >= 6: is_match = True
            elif filter_type == "as_cross":
                if f_rk_v <= 3 and s_rk_v <= 3: is_match = True
            elif filter_type == "f1_course_blood":
                if f_rk_v == 1 and ((pd.notnull(r['コース連順位']) and int(r['コース連順位']) <= 3) or (pd.notnull(r['血統連順位']) and int(r['血統連順位']) <= 3)):
                    is_match = True
            elif filter_type == "tua1_f_top3":
                if pd.notnull(r['TUA順位']) and int(r['TUA順位']) == 1 and f_rk_v <= 3:
                    is_match = True
            elif filter_type == "course1_s_top3":
                if pd.notnull(r['コース連順位']) and int(r['コース連順位']) == 1 and s_rk_v <= 3:
                    is_match = True
            elif filter_type == "f70_or_s60":
                if (pd.notnull(r['F']) and float(r['F']) >= 70.0) or (pd.notnull(r['S']) and float(r['S']) >= 60.0):
                    is_match = True
            elif filter_type == "c_mark_f_top3":
                if c_mk != "" and f_rk_v <= 3:
                    is_match = True
            elif filter_type == "stable_as_cross":
                if is_ace and f_rk_v <= 3 and s_rk_v <= 3:
                    is_match = True
            elif filter_type == "same_umaban_f_top3":
                if j_name and pair_cnt >= 2 and f_rk_v <= 3:
                    is_match = True
            elif filter_type == "sakaro_a3":
                s_row = r['s_row']
                if isinstance(s_row, pd.Series) and not s_row.empty:
                    try:
                        l1 = float(s_row.get('Lap1', 99) or 99)
                        l2 = float(s_row.get('Lap2', 99) or 99)
                        if l1 <= 11.9 and l1 < l2: is_match = True
                    except: pass
            elif filter_type == "c_horse":
                s_row, w_row = r['s_row'], r['w_row']
                if isinstance(s_row, pd.Series) and isinstance(w_row, pd.Series):
                    try:
                        arm_rk = int(r['ARM順位'])
                        w_5f = float(w_row.get('5F', 99) or 99)
                        s_t1 = float(s_row.get('Time1', 99) or 99)
                        if arm_rk <= 3 and w_5f <= 69.0 and s_t1 <= 59.9: is_match = True
                    except: pass
            elif filter_type == "stable_ace":
                if is_ace: is_match = True
            elif filter_type == "same_umaban":
                if j_name and pair_cnt >= 2: is_match = True

            if is_match:
                m_rnum = re.search(r'\d+', str(r['race_id']))
                r_num_txt = m_rnum.group() if m_rnum else ""
                matched_records.append(f"【{r['競馬場名']}{r_num_txt}R】 {u_no}番 {r['馬名']} ({r['騎手']})")
        return matched_records

    c_top3_win_matches = get_filter_matches("top3_win_pattern")
    filter_top3_win = st.sidebar.checkbox(f"👑 驚異の高勝率TOP3+α [1着固定] ({len(c_top3_win_matches)}頭)")

    c_high_in_matches = get_filter_matches("high_in")
    filter_high_level_in = st.sidebar.checkbox(f"👑 前走馬券内3頭以上 ({len(c_high_in_matches)}頭)")

    c_high_in_f_matches = get_filter_matches("high_in_f_top3")
    filter_high_in_f_top3 = st.sidebar.checkbox(f"🌟 印≧3×F1〜3位 [複47.4%] ({len(c_high_in_f_matches)}頭)")

    c_high_m2_matches = get_filter_matches("high_m2")
    filter_high_level_m2 = st.sidebar.checkbox(f"⭐ 前走掲示板5頭以上 ({len(c_high_m2_matches)}頭)")

    c_danger_matches = get_filter_matches("danger_in0")
    filter_danger_in0 = st.sidebar.checkbox(f"🚨 前走馬券内0頭 ({len(c_danger_matches)}頭)")

    c_arms_fup_matches = get_filter_matches("arms_fup")
    filter_arms_fup = st.sidebar.checkbox(f"✨ ARMS×FUP黄金クロス ({len(c_arms_fup_matches)}頭)")

    c_as_matches = get_filter_matches("as_cross")
    filter_as_cross = st.sidebar.checkbox(f"👑 AS交差馬(F&S上位) ({len(c_as_matches)}頭)")

    c_f1_cb_matches = get_filter_matches("f1_course_blood")
    filter_f1_course_blood = st.sidebar.checkbox(f"🎯 F1位×コース連/血統連上位 ({len(c_f1_cb_matches)}頭)")

    c_tua1_f_matches = get_filter_matches("tua1_f_top3")
    filter_tua1_f_top3 = st.sidebar.checkbox(f"🚀 TUA1位×F1〜3位[ダート特注] ({len(c_tua1_f_matches)}頭)")

    c_c1_s_matches = get_filter_matches("course1_s_top3")
    filter_course1_s_top3 = st.sidebar.checkbox(f"💣 コース連1位×S1〜3位[中穴] ({len(c_c1_s_matches)}頭)")

    c_f70_s60_matches = get_filter_matches("f70_or_s60")
    filter_f70_or_s60 = st.sidebar.checkbox(f"⚡ F≧70 または S≧60極限馬 ({len(c_f70_s60_matches)}頭)")

    c_cmark_f_matches = get_filter_matches("c_mark_f_top3")
    filter_cmark_f_top3 = st.sidebar.checkbox(f"🌟 C(マーク)×F1〜3位 [複55.4%] ({len(c_cmark_f_matches)}頭)")

    c_stbl_as_matches = get_filter_matches("stable_as_cross")
    filter_stable_as_cross = st.sidebar.checkbox(f"🌟 特選厩舎×AS交差 [複57.2%] ({len(c_stbl_as_matches)}頭)")

    c_same_f_matches = get_filter_matches("same_umaban_f_top3")
    filter_same_umaban_f_top3 = st.sidebar.checkbox(f"🌟 同馬番複数×F1〜3位 [複47.5%] ({len(c_same_f_matches)}頭)")

    c_sakaro_matches = get_filter_matches("sakaro_a3")
    filter_target_sakaro_a3 = st.sidebar.checkbox(f"🔥 坂路A3(終い11秒台加速) ({len(c_sakaro_matches)}頭)")

    c_c_horse_matches = get_filter_matches("c_horse")
    filter_target_c_horse = st.sidebar.checkbox(f"🌲 Ｃ馬特注(ウッド鉄則) ({len(c_c_horse_matches)}頭)")

    c_stable_matches = get_filter_matches("stable_ace")
    filter_target_stable_ace = st.sidebar.checkbox(f"👑 特選厩舎該当馬 ({len(c_stable_matches)}頭)")

    c_same_umaban_matches = get_filter_matches("same_umaban")
    filter_target_same_umaban = st.sidebar.checkbox(f"🔥 同馬番複数騎乗馬 ({len(c_same_umaban_matches)}頭)")

    # -------------------------------------------------------------
    # 💡 サイドバーでチェックされたフィルターの該当馬・該当Rリストを右側上部に一発表示
    # -------------------------------------------------------------
    active_filters = []
    if filter_vol_solid: active_filters.append(("🔒 ノートブック判定：堅いレース一覧（1番人気複勝率88.2% / 波乱率0%）", solid_race_summary))
    if filter_vol_chaos: active_filters.append(("🌪️ ノートブック判定：荒れるレース一覧（波乱発生率73.3% / 1番人気危険）", chaos_race_summary))
    if filter_top3_win: active_filters.append(("👑 驚異の高勝率パターンTOP3+α [勝率37.5〜45.5% / 1着固定特注]", c_top3_win_matches))
    if filter_high_level_in: active_filters.append(("👑 前走馬券内3頭以上 (年間複勝率29.7%)", c_high_in_matches))
    if filter_high_in_f_top3: active_filters.append(("🌟 前走馬券内3頭以上(印≧3) × F1〜3位 [年間勝率20.1% / 複勝率47.4%]", c_high_in_f_matches))
    if filter_high_level_m2: active_filters.append(("⭐ 前走掲示板5頭以上", c_high_m2_matches))
    if filter_danger_in0: active_filters.append(("🚨 前走馬券内0頭 [年間勝率4.3% / 複勝率19.0%・危険]", c_danger_matches))
    if filter_arms_fup: active_filters.append(("✨ ARMS×FUP黄金クロス [年間勝率19.1% / 複勝率42.8%・単勝特化]", c_arms_fup_matches))
    if filter_as_cross: active_filters.append(("👑 AS交差馬(F&S上位) [年間勝率21.2% / 複勝率52.0%]", c_as_matches))
    if filter_f1_course_blood: active_filters.append(("🎯 F1位×コース連/血統連上位 [年間勝率25.3% / 複勝率56.1%]", c_f1_cb_matches))
    if filter_tua1_f_top3: active_filters.append(("🚀 TUA1位×F1〜3位 [年間ダート複勝率43.7%]", c_tua1_f_matches))
    if filter_course1_s_top3: active_filters.append(("💣 コース連1位×S1〜3位 [年間複勝率41.3% / 平均3.5人気中穴]", c_c1_s_matches))
    if filter_f70_or_s60: active_filters.append(("⚡ F≧70 または S≧60極限馬 [年間複勝率54.2% / F≧72は複68.2%]", c_f70_s60_matches))
    if filter_cmark_f_top3: active_filters.append(("🌟 C(マーク)あり × F1〜3位 [年間勝率28.1% / 複勝率55.4% (AS交差なら複59.7%)]", c_cmark_f_matches))
    if filter_stable_as_cross: active_filters.append(("🌟 特選厩舎 × AS交差馬(F&S上位) [年間勝率25.5% / 複勝率57.2%]", c_stbl_as_matches))
    if filter_same_umaban_f_top3: active_filters.append(("🌟 同馬番複数騎乗 × F1〜3位 [年間複勝率47.5% (AS交差なら複55.2%)]", c_same_f_matches))
    if filter_target_sakaro_a3: active_filters.append(("🔥 坂路A3(終い11秒台加速)", c_sakaro_matches))
    if filter_target_c_horse: active_filters.append(("🌲 Ｃ馬特注(ウッド鉄則)", c_c_horse_matches))
    if filter_target_stable_ace: active_filters.append(("👑 特選厩舎該当馬 (単体)", c_stable_matches))
    if filter_target_same_umaban: active_filters.append(("🔥 同馬番複数騎乗馬 (単体)", c_same_umaban_matches))

    if active_filters:
        st.markdown("<div class='filter-result-box'>", unsafe_allow_html=True)
        st.markdown("### 📌 選択中フィルターの該当一覧（リアルタイム抽出）", unsafe_allow_html=True)
        for f_name, f_list in active_filters:
            st.markdown(f"**{f_name}** (計 {len(f_list)}件)")
            if f_list:
                formatted_items = " ｜ ".join([f"<span style='background:#1f2937; padding:2px 8px; border-radius:4px; border:1px solid #374151; color:#60a5fa;'>{item}</span>" for item in f_list])
                st.markdown(f"<div style='margin: 6px 0 12px 0; line-height: 2.2;'>{formatted_items}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='color: #9ca3af; margin: 4px 0 10px 0;'>該当なし</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

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
    for r in races_sorted:
        r_uid = r['race_uid']
        r_subset = v_df[v_df['race_uid'] == r_uid]
        
        r_rating = evaluate_race_rating(r_subset)
        s_lvl, f_lvl, _, v_short, _, _ = race_vol_map.get(r_uid, ("標準", "標準", "", "⚖️【標準】", "", ""))
        
        race_tags = []
        if r_rating == "S": race_tags.append("🔥【S級勝負】")
        elif r_rating == "A": race_tags.append("🎯【A級準勝負】")
        elif r_rating == "B": race_tags.append("⚖️【B級標準】")
        else: race_tags.append("📌【見送り推奨】")

        race_tags.append(v_short)
        race_tags.append(f"水準[S:{s_lvl}/F:{f_lvl}]")

        tag_str = f" [{' '.join(race_tags)}]"
        race_options[r_uid] = f"{r['race_uid']} ({r['track']}{r['dist']}m){tag_str}"

    selected_race_uid = st.selectbox("レース選択（1R〜順次）", options=list(race_options.keys()), format_func=lambda x: race_options[x])

    race_df = df[df['race_uid'] == selected_race_uid].copy()
    c_cat = get_cushion_category(cushion_val, chosen_venue)

    scores, rescued_flags, sss_flags, nb_hits_list, stable_hits_list, f_eval_labels, combo_hits_list, top3_win_rks, emp_place_rates = [], [], [], [], [], [], [], [], []
    for _, r in race_df.iterrows():
        u_cnt = jockey_umaban_counts.get((r['騎手'], int(r['馬番'])), 1)
        sc, res, sss, nb, stbl, f_lbl, cmb, t3_rk, emp_pr = calc_upgraded_dynamic_score(r, race_df, chosen_venue, r['track'], r['dist'], c_cat, r['class_name'], r['s_row'], r['w_row'], same_umaban_cnt=u_cnt)
        scores.append(sc); rescued_flags.append(res); sss_flags.append(sss); nb_hits_list.append(nb); stable_hits_list.append(stbl); f_eval_labels.append(f_lbl); combo_hits_list.append(cmb); top3_win_rks.append(t3_rk); emp_place_rates.append(emp_pr)

    race_df['dynamic_score'] = scores
    race_df['is_rescued'] = rescued_flags
    race_df['is_sss'] = sss_flags
    race_df['nb_hits'] = nb_hits_list
    race_df['stable_hits'] = stable_hits_list
    race_df['f_eval'] = f_eval_labels
    race_df['combo_hits'] = combo_hits_list
    race_df['top3_win_rk'] = top3_win_rks
    race_df['emp_place_rate'] = emp_place_rates

    current_track = race_df['track'].iloc[0] if not race_df.empty else '芝'
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

    st.markdown(f"<div class='race-type-banner {banner_cls}'><div>{banner_txt}</div><div>クッション値帯: {c_cat}</div></div>", unsafe_allow_html=True)

    # ★ ノートブック基準「堅い／荒れる（波乱度）」自動判定パネル表示
    st.markdown(f"""
    <div class='{vol_banner_cls}'>
        <div style='font-size: 15.5px; font-weight: bold; margin-bottom: 4px;'>📘 ノートブック『S・Fバランス攻略』波乱度判定：{vol_title}</div>
        <div style='font-size: 13.5px; opacity: 0.95;'>🔍 <strong>判定根拠＆馬券戦略</strong>: {vol_reason}</div>
    </div>
    """, unsafe_allow_html=True)

    f_top3_df = race_df[race_df['F順位'] <= 3].sort_values('F順位') if (race_df['F順位'] <= 3).any() else race_df.sort_values('F順位').head(3)
    s_top3_df = race_df[race_df['S順位'] <= 3].sort_values('S順位') if (race_df['S順位'] <= 3).any() else race_df.sort_values('S順位').head(3)
    arm_top3_df = race_df[race_df['ARM順位'] <= 3].sort_values('ARM順位') if (race_df['ARM順位'] <= 3).any() else race_df.sort_values('ARM順位').head(3)
    tua_top3_df = race_df[race_df['TUA順位'] <= 3].sort_values('TUA順位') if (race_df['TUA順位'] <= 3).any() else race_df.sort_values('TUA順位').head(3)

    f_top3_nums = f_top3_df['馬番'].tolist()
    s_top3_nums = s_top3_df['馬番'].tolist()
    arm_top3_nums = arm_top3_df['馬番'].tolist() if 'ARM順位' in race_df.columns else []
    tua_top3_nums = tua_top3_df['馬番'].tolist() if 'TUA順位' in race_df.columns else []
    
    safe_race_df = race_df[race_df['印'] > 0].copy() if filter_danger_in0 else race_df.copy()
    if safe_race_df.empty:
        safe_race_df = race_df.copy()

    f_safe_top3 = safe_race_df[safe_race_df['F順位'] <= 3]['馬番'].tolist() if (safe_race_df['F順位'] <= 3).any() else safe_race_df.sort_values('F順位').head(3)['馬番'].tolist()
    s_safe_top3 = safe_race_df[safe_race_df['S順位'] <= 3]['馬番'].tolist() if (safe_race_df['S順位'] <= 3).any() else safe_race_df.sort_values('S順位').head(3)['馬番'].tolist()

    top3_win_df = safe_race_df[safe_race_df['top3_win_rk'] > 0].sort_values(['top3_win_rk', 'emp_place_rate', 'dynamic_score'], ascending=[True, False, False])
    top3_win_nums = top3_win_df['馬番'].tolist()

    f1_cb_nums = safe_race_df[(safe_race_df['F順位'] == 1) & ((safe_race_df['コース連順位'] <= 3) | (safe_race_df['血統連順位'] <= 3))]['馬番'].tolist()
    tua1_f_nums = safe_race_df[(safe_race_df['TUA順位'] == 1) & (safe_race_df['F順位'] <= 3)]['馬番'].tolist()
    c1_s_nums = safe_race_df[(safe_race_df['コース連順位'] == 1) & (safe_race_df['S順位'] <= 3)]['馬番'].tolist()
    turf_s_fup_nums = safe_race_df[(safe_race_df['track'] == '芝') & (safe_race_df['S順位'] <= 3) & (safe_race_df['Fup2順位'] <= 3)]['馬番'].tolist()

    cmark_f_nums = safe_race_df[(safe_race_df['C(マーク)'].astype(str).str.strip() != '') & (safe_race_df['F順位'] <= 3)]['馬番'].tolist()
    stbl_as_nums = safe_race_df[safe_race_df['調教師'].apply(lambda t: any(ac in str(t) for ac in ACE_TRAINERS)) & (safe_race_df['F順位'] <= 3) & (safe_race_df['S順位'] <= 3)]['馬番'].tolist()
    same_f_nums = safe_race_df[safe_race_df.apply(lambda r: jockey_umaban_counts.get((r['騎手'], int(r['馬番'])), 1) >= 2 and int(r['F順位']) <= 3, axis=1)]['馬番'].tolist()

    a_group_nums = sorted(list(set(f_safe_top3 + s_safe_top3)))
    as_intersect_nums = sorted(list(set(f_safe_top3) & set(s_safe_top3)))
    f_arm_nums = sorted(list(set(f_safe_top3) & set(arm_top3_nums)))
    s_tua_nums = sorted(list(set(s_safe_top3) & set(tua_top3_nums)))
    quad_nums = sorted(list(set(f_safe_top3) & set(s_safe_top3) & set(arm_top3_nums) & set(tua_top3_nums)))

    z_candidates = safe_race_df[~safe_race_df['馬番'].isin(a_group_nums)].sort_values(
        ['コース連順位', '血統連順位', '坂路調順位', 'dynamic_score'], ascending=[True, True, True, False]
    )
    z_nums = z_candidates.head(3)['馬番'].tolist()

    # -------------------------------------------------------------
    # ★ 第3の馬券パターン：3連単フォーメーション構築（1着2頭 / 2着3〜4頭 / 3着複数頭）
    #   ・驚異の高勝率パターン該当馬がいる場合 ➔ その馬を優先して1着(2頭)に配置
    #   ・該当しない場合 ➔ これまでのロジックで馬券内率(emp_place_rate)が高い順に1着(2頭)→2着(3〜4頭)→3着(複数頭)を構成
    # -------------------------------------------------------------
    all_high_prob_pool = list(set(a_group_nums + top3_win_nums + f1_cb_nums + cmark_f_nums + stbl_as_nums + same_f_nums + tua1_f_nums + c1_s_nums))
    pool_df = safe_race_df[safe_race_df['馬番'].isin(all_high_prob_pool)].sort_values(
        ['emp_place_rate', 'dynamic_score', 'F'], ascending=[False, False, False]
    )
    if len(pool_df) < 4:
        pool_df = safe_race_df.sort_values(['emp_place_rate', 'dynamic_score', 'F'], ascending=[False, False, False])

    ranked_prob_nums = pool_df['馬番'].tolist()

    if len(top3_win_nums) > 0:
        pat3_mode_label = "👑【驚異の高勝率パターン合致モード（1着固定特注2頭 ➔ 2着3〜4頭 ➔ 3着複数）】"
        first_col_p3 = list(top3_win_nums[:2])
        for n in ranked_prob_nums:
            if len(first_col_p3) >= 2:
                break
            if n not in first_col_p3:
                first_col_p3.append(n)
    else:
        pat3_mode_label = "📊【従来ロジック・馬券内率（複勝率）最上位順モード（1着上位2頭 ➔ 2着3〜4頭 ➔ 3着複数）】"
        first_col_p3 = list(ranked_prob_nums[:2])

    second_col_p3 = list(first_col_p3)
    for n in ranked_prob_nums:
        if len(second_col_p3) >= 4:
            break
        if n not in second_col_p3:
            second_col_p3.append(n)

    third_col_p3 = list(dict.fromkeys(second_col_p3 + ranked_prob_nums + z_nums))

    # 馬券内率順の序列表示テキスト作成
    rank_order_str = " ➔ ".join([
        f"<strong>{int(r_row['馬番'])}番</strong>(複{r_row['emp_place_rate']:.1f}%)"
        for _, r_row in pool_df.head(6).iterrows()
    ])

    top3_win_str = ", ".join([f"<strong>{n}番</strong>" for n in top3_win_nums]) if top3_win_nums else "なし（従来ロジックの馬券内率順を自動適用）"
    as_str = ", ".join([f"<strong>{n}番</strong>" for n in as_intersect_nums]) if as_intersect_nums else "なし"
    f1_cb_str = ", ".join([f"<strong>{n}番</strong>" for n in f1_cb_nums]) if f1_cb_nums else "なし"
    tua1_f_str = ", ".join([f"<strong>{n}番</strong>" for n in tua1_f_nums]) if tua1_f_nums else "なし"
    c1_s_str = ", ".join([f"<strong>{n}番</strong>" for n in c1_s_nums]) if c1_s_nums else "なし"
    cmark_f_str = ", ".join([f"<strong>{n}番</strong>" for n in cmark_f_nums]) if cmark_f_nums else "なし"
    stbl_as_str = ", ".join([f"<strong>{n}番</strong>" for n in stbl_as_nums]) if stbl_as_nums else "なし"
    same_f_str = ", ".join([f"<strong>{n}番</strong>" for n in same_f_nums]) if same_f_nums else "なし"
    f_arm_str = ", ".join([f"<strong>{n}番</strong>" for n in f_arm_nums]) if f_arm_nums else "なし"
    s_tua_str = ", ".join([f"<strong>{n}番</strong>" for n in s_tua_nums]) if s_tua_nums else "なし"
    quad_str = ", ".join([f"<strong>{n}番</strong>" for n in quad_nums]) if quad_nums else "なし"
    z_str = ", ".join([f"<strong>{n}番</strong>" for n in z_nums]) if z_nums else "なし"

    p3_1st_str = ", ".join([f"{n}番" for n in first_col_p3])
    p3_2nd_str = ", ".join([f"{n}番" for n in second_col_p3])
    p3_3rd_str = ", ".join([f"{n}番" for n in third_col_p3])

    st.markdown(f"""
    <div class='recom-block' style='border: 2px solid #3b82f6;'>
        <h4 style='color: #60a5fa; margin-top: 0;'>🎯 第3の馬券パターン：驚異の高勝率TOP3 ＆ 馬券内率順フォーメーション</h4>
        <div style='font-size: 13.5px; color: #cbd5e1; margin-bottom: 8px;'>
            🔥 <strong>【驚異の高勝率パターン（勝率37.5〜45.5% / 1着固定特注）】</strong>: <span style='color: #fef08a; font-weight: bold;'>{top3_win_str}</span><br>
            📈 <strong>【従来ロジック・実証馬券内率（複勝率）上位順】</strong>: <span style='color: #93c5fd;'>{rank_order_str}</span><br>
            <strong>A群（F上位1〜3位 ＋ S上位1〜3位）</strong>: {', '.join([f"<strong>{n}番</strong>" for n in a_group_nums])} (計{len(a_group_nums)}頭) ｜ 👑 <strong>【AS交差馬（複52.0%）】</strong>: {as_str}<br>
            🎯 <strong>【F1位 × コース連/血統連上位（複56.1%鉄板軸）】</strong>: <span style='color: #fde047;'>{f1_cb_str}</span><br>
            🌟 <strong>【C(マーク)×F上位（複55.4〜59.7%）】</strong>: <span style='color: #fde047;'>{cmark_f_str}</span> ｜ 🌟 <strong>【特選厩舎×AS交差（複57.2%）】</strong>: <span style='color: #fde047;'>{stbl_as_str}</span> ｜ 🌟 <strong>【同馬番複数×F上位（複47.5〜55.2%）】</strong>: <span style='color: #38bdf8;'>{same_f_str}</span><br>
            🚀 <strong>【TUA1位 × F1〜3位（ダート複43.7%）】</strong>: <span style='
