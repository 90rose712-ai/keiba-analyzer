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
                df = pd.read_csv(newest, encoding=enc)
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
        # ノートブックP.3準拠：指数順位1〜3位の指数平均値で計算
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

    # レース番号からもクラス基準（9-10R:2〜3勝、11R:OP/重賞）を自動補完
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
    """
    ノートブック『S・F指数レースバランス攻略』の水準・相手差・割引条件に基づき、
    レースが「堅い（順当）」か「荒れる（波乱）」かを事前判定する関数
    """
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

    # ① S・Fとも低水準（ノートブックP.4：両指数上位でも割引・人気だけで軸にしない）
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

    # ② S低水準（ノートブックP.4/P.8：F68〜70以上が軸、ただしS6位以下は割引条件）
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

    # ③ F低水準（ノートブックP.4/P.9：S60以上×F3位以内が軸、S値不足やF4位以下は割引条件）
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

    # ④ S・Fとも標準〜高水準（ノートブックP.4/P.10：数値抜け＋適性裏付け vs 上位密集）
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

def calc_upgraded_dynamic_score(r, race_subset, venue_name, track_type, dist_val, c_category, class_name, s_row_laps, w_row_data):
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

    trainer = clean_str(r.get('調教師', ''))
    sire = clean_str(r.get('種牡馬', ''))
    track_change = clean_str(r.get('芝ダート変わり', ''))
    interval = str(r.get('間隔', ''))
    weight = float(pd.to_numeric(str(r.get('前場体重', '480')).replace('kg', ''), errors='coerce') or 480.0)

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
    
    # -------------------------------------------------------------
    # ★ 実証データに基づく超高確率・高期待値パターンの動的加点＆バッジ付与
    # -------------------------------------------------------------
    if f_val >= 72.0:
        score += 65.0
        combo_hits.append(("golden", "👑 鉄板級 F≧72(複88.9%)"))
    elif f_val >= 70.0 and s_rk <= 3:
        score += 45.0
        combo_hits.append(("golden", "🔥 極限クロス(F≧70×S上位)"))

    if f_rk == 1 and s_rk <= 3 and c_rk <= 3:
        score += 75.0
        combo_hits.append(("golden", "🌟 極限3重交差(F1位×S上位×コース連上位)[勝66.7%/連83.3%]"))
    elif f_rk == 1 and c_rk <= 3:
        score += 50.0
        combo_hits.append(("golden", "🎯 F1位×コース連上位[勝44.4%/複77.8%]"))

    if f_rk == 1 and c_rk == 1:
        score += 25.0
        combo_hits.append(("golden", "💯 F1位×コース連1位(完全一致)"))

    if f_val >= 70.0 and k_rk <= 3:
        score += 45.0
        combo_hits.append(("golden", "🧬 F≧70×血統連上位[連72.7%]"))
    elif f_rk == 1 and k_rk <= 3:
        score += 35.0
        combo_hits.append(("golden", "🧬 F1位×血統連上位[複66.7%]"))

    if track_type == 'ダ' and tua_rk == 1 and f_rk <= 3:
        score += 65.0
        combo_hits.append(("golden", "🚀 ダート最強軸(TUA1位×F上位)[勝37.5%/連75.0%]"))
    elif track_type == '芝' and tua_rk == 1 and f_rk <= 3:
        score += 40.0
        combo_hits.append(("value", "🌐 TUA1位×F上位[複63.6%]"))

    if track_type == 'ダ' and f_rk == 1 and tua_rk <= 3 and tua_rk != 1:
        score += 45.0
        combo_hits.append(("golden", "🔥 ダート黄金(F1位×TUA上位)[複75.0%]"))

    if c_rk == 1 and s_rk <= 3:
        score += 45.0
        combo_hits.append(("value", "💣 歪み激走特注(コース連1位×S上位)[勝35.7%/複57.1%]"))

    if f_rk <= 3 and c_rk <= 3 and k_rk <= 3:
        score += 40.0
        combo_hits.append(("value", "💎 3複合上位(F×コース連×血統連)[複72.7%]"))
    if f_rk <= 3 and hc_rk <= 3 and c_rk <= 3:
        score += 40.0
        combo_hits.append(("value", "⚡ 3複合上位(F×坂路調×コース連)[連66.7%]"))

    if track_type == '芝' and s_rk <= 3 and fup_rk <= 3:
        score += 30.0
        combo_hits.append(("value", "🌱 芝ヒモ特注(S上位×Fup2上位)[複50.0%]"))
    if s_val >= 60.0:
        score += 30.0
        combo_hits.append(("value", "⚡ 高S指数(S≧60)[連52.6%]"))

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
        score += 50.0; nb_hits.append("✨ ARMS×FUP(黄金クロス)")

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

    return score, is_rescued, is_sss, nb_hits, stable_hits, f_eval_label, combo_hits

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
                df_raw = pd.read_csv(uploaded_file, encoding=enc)
                if not df_raw.empty and df_raw.shape[1] >= 38:
                    loaded_filename = uploaded_file.name
                    break
            except Exception:
                continue

    if df_raw.empty:
        st.markdown("<div class='race-type-banner race-type-normal'>⚠️ 全42列マスターCSVが見つかりません。サイドバーからCSVを指定してください。</div>", unsafe_allow_html=True)
        st.stop()

    st.sidebar.success(f"✅ 指数CSV読込成功: {loaded_filename} (全{len(df_raw)}頭)")

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

        if horse:
            records.append({
                'race_id': race_id, 'race_uid': race_id, '競馬場名': v_name, 'track': track, 'dist': dist_int, 'class_name': class_str,
                '馬番': int(float(umaban)), '馬名': horse, '印': in_num, 'M2': m2_num,
                'C(マーク)': c_mark, 'C(馬)': c_horse,
                '調教師': trainer, '騎手': jockey, '種牡馬': sire, '人気順位': int(float(pop)) if pd.notnull(pop) else 99,
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

            if filter_type == "high_in":
                if pd.notnull(r['印']) and float(r['印']) >= 3: is_match = True
            elif filter_type == "high_m2":
                if pd.notnull(r['M2']) and float(r['M2']) >= 5: is_match = True
            elif filter_type == "danger_in0":
                if pd.notnull(r['印']) and float(r['印']) == 0: is_match = True
            elif filter_type == "arms_fup":
                if pd.notnull(r['ARM順位']) and int(r['ARM順位']) == 1 and pd.notnull(r['Fup2']) and int(r['Fup2']) >= 6: is_match = True
            elif filter_type == "as_cross":
                if pd.notnull(r['F順位']) and int(r['F順位']) <= 3 and pd.notnull(r['S順位']) and int(r['S順位']) <= 3: is_match = True
            elif filter_type == "f1_course_blood":
                if pd.notnull(r['F順位']) and int(r['F順位']) == 1 and ((pd.notnull(r['コース連順位']) and int(r['コース連順位']) <= 3) or (pd.notnull(r['血統連順位']) and int(r['血統連順位']) <= 3)):
                    is_match = True
            elif filter_type == "tua1_f_top3":
                if pd.notnull(r['TUA順位']) and int(r['TUA順位']) == 1 and pd.notnull(r['F順位']) and int(r['F順位']) <= 3:
                    is_match = True
            elif filter_type == "course1_s_top3":
                if pd.notnull(r['コース連順位']) and int(r['コース連順位']) == 1 and pd.notnull(r['S順位']) and int(r['S順位']) <= 3:
                    is_match = True
            elif filter_type == "f70_or_s60":
                if (pd.notnull(r['F']) and float(r['F']) >= 70.0) or (pd.notnull(r['S']) and float(r['S']) >= 60.0):
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
                ace_trainers = ['藤原', '杉山', '矢作', '中内田', '木村', '堀', '友道', '池添', '吉岡', '大竹', '斉藤', '音無', '国枝']
                if any(ac in str(r['調教師']) for ac in ace_trainers): is_match = True
            elif filter_type == "same_umaban":
                if j_name and pair_cnt >= 2: is_match = True

            if is_match:
                m_rnum = re.search(r'\d+', str(r['race_id']))
                r_num_txt = m_rnum.group() if m_rnum else ""
                matched_records.append(f"【{r['競馬場名']}{r_num_txt}R】 {u_no}番 {r['馬名']} ({r['騎手']})")
        return matched_records

    c_high_in_matches = get_filter_matches("high_in")
    filter_high_level_in = st.sidebar.checkbox(f"👑 前走馬券内3頭以上 ({len(c_high_in_matches)}頭)")

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
    if filter_high_level_in: active_filters.append(("👑 前走馬券内3頭以上", c_high_in_matches))
    if filter_high_level_m2: active_filters.append(("⭐ 前走掲示板5頭以上", c_high_m2_matches))
    if filter_danger_in0: active_filters.append(("🚨 前走馬券内0頭", c_danger_matches))
    if filter_arms_fup: active_filters.append(("✨ ARMS×FUP黄金クロス", c_arms_fup_matches))
    if filter_as_cross: active_filters.append(("👑 AS交差馬(F&S上位)", c_as_matches))
    if filter_f1_course_blood: active_filters.append(("🎯 F1位×コース連/血統連上位 [複勝率66.7〜77.8%]", c_f1_cb_matches))
    if filter_tua1_f_top3: active_filters.append(("🚀 TUA1位×F1〜3位 [ダート連対75.0%/全場複63.6%]", c_tua1_f_matches))
    if filter_course1_s_top3: active_filters.append(("💣 コース連1位×S1〜3位 [勝率35.7%/中穴特注]", c_c1_s_matches))
    if filter_f70_or_s60: active_filters.append(("⚡ F≧70 または S≧60極限馬", c_f70_s60_matches))
    if filter_target_sakaro_a3: active_filters.append(("🔥 坂路A3(終い11秒台加速)", c_sakaro_matches))
    if filter_target_c_horse: active_filters.append(("🌲 Ｃ馬特注(ウッド鉄則)", c_c_horse_matches))
    if filter_target_stable_ace: active_filters.append(("👑 特選厩舎該当馬", c_stable_matches))
    if filter_target_same_umaban: active_filters.append(("🔥 同馬番複数騎乗馬", c_same_umaban_matches))

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

    scores, rescued_flags, sss_flags, nb_hits_list, stable_hits_list, f_eval_labels, combo_hits_list = [], [], [], [], [], [], []
    for _, r in race_df.iterrows():
        sc, res, sss, nb, stbl, f_lbl, cmb = calc_upgraded_dynamic_score(r, race_df, chosen_venue, r['track'], r['dist'], c_cat, r['class_name'], r['s_row'], r['w_row'])
        scores.append(sc); rescued_flags.append(res); sss_flags.append(sss); nb_hits_list.append(nb); stable_hits_list.append(stbl); f_eval_labels.append(f_lbl); combo_hits_list.append(cmb)

    race_df['dynamic_score'] = scores
    race_df['is_rescued'] = rescued_flags
    race_df['is_sss'] = sss_flags
    race_df['nb_hits'] = nb_hits_list
    race_df['stable_hits'] = stable_hits_list
    race_df['f_eval'] = f_eval_labels
    race_df['combo_hits'] = combo_hits_list

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
    
    safe_race_df = race_df[race_df['印'] > 0] if filter_danger_in0 else race_df
    f_safe_top3 = safe_race_df[safe_race_df['F順位'] <= 3]['馬番'].tolist() if (safe_race_df['F順位'] <= 3).any() else safe_race_df.sort_values('F順位').head(3)['馬番'].tolist()
    s_safe_top3 = safe_race_df[safe_race_df['S順位'] <= 3]['馬番'].tolist() if (safe_race_df['S順位'] <= 3).any() else safe_race_df.sort_values('S順位').head(3)['馬番'].tolist()

    f1_cb_nums = safe_race_df[(safe_race_df['F順位'] == 1) & ((safe_race_df['コース連順位'] <= 3) | (safe_race_df['血統連順位'] <= 3))]['馬番'].tolist()
    tua1_f_nums = safe_race_df[(safe_race_df['TUA順位'] == 1) & (safe_race_df['F順位'] <= 3)]['馬番'].tolist()
    c1_s_nums = safe_race_df[(safe_race_df['コース連順位'] == 1) & (safe_race_df['S順位'] <= 3)]['馬番'].tolist()
    turf_s_fup_nums = safe_race_df[(safe_race_df['track'] == '芝') & (safe_race_df['S順位'] <= 3) & (safe_race_df['Fup2順位'] <= 3)]['馬番'].tolist()

    a_group_nums = sorted(list(set(f_safe_top3 + s_safe_top3)))
    as_intersect_nums = sorted(list(set(f_safe_top3) & set(s_safe_top3)))
    f_arm_nums = sorted(list(set(f_safe_top3) & set(arm_top3_nums)))
    s_tua_nums = sorted(list(set(s_safe_top3) & set(tua_top3_nums)))
    quad_nums = sorted(list(set(f_safe_top3) & set(s_safe_top3) & set(arm_top3_nums) & set(tua_top3_nums)))

    z_candidates = safe_race_df[~safe_race_df['馬番'].isin(a_group_nums)].sort_values(
        ['コース連順位', '血統連順位', '坂路調順位', 'dynamic_score'], ascending=[True, True, True, False]
    )
    z_nums = z_candidates.head(3)['馬番'].tolist()

    as_str = ", ".join([f"<strong>{n}番</strong>" for n in as_intersect_nums]) if as_intersect_nums else "なし"
    f1_cb_str = ", ".join([f"<strong>{n}番</strong>" for n in f1_cb_nums]) if f1_cb_nums else "なし"
    tua1_f_str = ", ".join([f"<strong>{n}番</strong>" for n in tua1_f_nums]) if tua1_f_nums else "なし"
    c1_s_str = ", ".join([f"<strong>{n}番</strong>" for n in c1_s_nums]) if c1_s_nums else "なし"
    f_arm_str = ", ".join([f"<strong>{n}番</strong>" for n in f_arm_nums]) if f_arm_nums else "なし"
    s_tua_str = ", ".join([f"<strong>{n}番</strong>" for n in s_tua_nums]) if s_tua_nums else "なし"
    quad_str = ", ".join([f"<strong>{n}番</strong>" for n in quad_nums]) if quad_nums else "なし"
    z_str = ", ".join([f"<strong>{n}番</strong>" for n in z_nums]) if z_nums else "なし"

    st.markdown(f"""
    <div class='recom-block' style='border: 2px solid #3b82f6;'>
        <h4 style='color: #60a5fa; margin-top: 0;'>🎯 第3の馬券パターン：AS交差 ＆ レース水準[S:{s_lvl_sel}/F:{f_lvl_sel}]特化フォーメーション</h4>
        <div style='font-size: 13.5px; color: #cbd5e1; margin-bottom: 8px;'>
            <strong>A群（F上位1〜3位 ＋ S上位1〜3位）</strong>: {', '.join([f"<strong>{n}番</strong>" for n in a_group_nums])} (計{len(a_group_nums)}頭)<br>
            👑 <strong>【AS交差馬（F&S両方上位）】</strong>: {as_str}<br>
            🎯 <strong>【F1位 × コース連/血統連上位（複勝率66.7〜77.8%鉄板軸）】</strong>: <span style='color: #fde047;'>{f1_cb_str}</span><br>
            🚀 <strong>【TUA1位 × F1〜3位（ダート連対率75.0% / 全場複63.6%）】</strong>: <span style='color: #34d399;'>{tua1_f_str}</span><br>
            💣 <strong>【コース連1位 × S1〜3位（勝率35.7% / 中穴激走特注）】</strong>: <span style='color: #f472b6;'>{c1_s_str}</span><br>
            ⭐ <strong>【F × ARM交差馬（絶対能力 ＋ 高回収）】</strong>: {f_arm_str} ｜ 🚀 <strong>【S × TUA交差馬】</strong>: {s_tua_str}<br>
            💎 <strong>【4大指数完全網羅馬（F・S・ARM・TUAすべて上位）】</strong>: {quad_str}<br>
            🎯 <strong>【アプリ自動抽出・厳選Z馬（3列目特化候補・保険含む）】</strong>: <span style='color: #38bdf8; font-weight: bold;'>{z_str}</span>
        </div>
        <ul style='list-style-type: none; padding-left: 0; line-height: 1.8; font-size: 14px;'>
            <li><strong>【第3パターン構築】</strong> 3連単F: <span style='color: #fbbf24; font-weight: bold;'>{', '.join(map(str, a_group_nums))}</span> ＝ <span style='color: #fbbf24; font-weight: bold;'>{', '.join(map(str, a_group_nums))}</span> → <span style='color: #38bdf8; font-weight: bold;'>{z_str}</span></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    f65_horses = race_df[race_df['F'] >= 65.0].sort_values(['F', 'dynamic_score'], ascending=[False, False])
    has_f65 = len(f65_horses) > 0
    is_chaos_race = ("波乱" in vol_short)

    if has_f65 and not is_chaos_race:
        mode_name = "👑 モードA：F指数65以上【絶対主役モード】"
        mode_desc = "F指数65以上の抜けた馬を不動の連軸とし、実証高確率クロス（コース連・血統連・TUA・S上位）へ網を張る構成"
        honmei = f65_horses.iloc[0]
        honmei_num = int(honmei['馬番'])
        opponents = race_df[race_df['馬番'] != honmei_num].copy()
        taikou = opponents.sort_values(['dynamic_score', 'F順位', 'コース連順位', 'TUA順位'], ascending=[False, True, True, True]).iloc[0] if not opponents.empty else honmei
        taikou_num = int(taikou['馬番'])
        
        high_prob_2nd = [n for n in (tua1_f_nums + c1_s_nums + f1_cb_nums) if n != honmei_num]
        second_row = list(set(
            opponents.sort_values('F順位').head(2)['馬番'].tolist() +
            high_prob_2nd +
            opponents.sort_values('ARM順位').head(1)['馬番'].tolist() +
            opponents.sort_values('TUA順位').head(1)['馬番'].tolist()
        )) if not opponents.empty else [honmei_num]
        
        third_row = list(set(
            second_row +
            [n for n in turf_s_fup_nums if n != honmei_num] +
            opponents.sort_values('コース連順位').head(2)['馬番'].tolist() +
            opponents.sort_values('血統連順位').head(2)['馬番'].tolist() +
            opponents.sort_values('バランス順位').head(1)['馬番'].tolist()
        )) if not opponents.empty else [honmei_num]
        
        ana_candidates = opponents[opponents['人気順位'] >= 4].sort_values(['dynamic_score', 'コース連順位', 'TUA順位', 'ARM順位'], ascending=[False, True, True, True]) if not opponents.empty else pd.DataFrame()
        if not ana_candidates.empty:
            ana = ana_candidates.iloc[0]
            ana_num = int(ana['馬番'])
        elif not opponents.empty:
            ana = opponents.iloc[-1]
            ana_num = int(ana['馬番'])
        else:
            ana = honmei
            ana_num = honmei_num
    else:
        if is_chaos_race:
            mode_name = "🌪️ モードB（波乱警戒・高期待値モード）：動的スコア＆適性上位軸 × F/S上位補完"
            mode_desc = "ノートブックの波乱・割引条件に合致するため人気馬の過信を排し、適性（コース連・TUA・S上位）を兼ね備えた最高評価馬から中穴へ手広く網を張る構成"
        else:
            mode_name = "🔥 モードB：単勝期待値軸 × F指数・高確率クロス補完モード"
            mode_desc = "実証クロス（ダートTUA1位×F上位 / F1位×コース連 / コース連1位×S上位）＆最高動的スコア馬を軸に、F指数1〜3位を完全固定する構成"

        honmei = race_df.sort_values(['dynamic_score', 'F', 'Fup2', 'コース連順位'], ascending=[False, False, False, True]).iloc[0]
        honmei_num = int(honmei['馬番'])
        opponents = race_df[race_df['馬番'] != honmei_num].copy()
        
        high_prob_2nd = [n for n in (f_top3_nums + tua1_f_nums + c1_s_nums + f1_cb_nums) if n != honmei_num]
        second_row = list(dict.fromkeys(high_prob_2nd)) if high_prob_2nd else opponents.sort_values('F順位').head(3)['馬番'].tolist()
        
        taikou_df = opponents.sort_values(['dynamic_score', 'F順位', 'コース連順位'], ascending=[False, True, True])
        taikou = taikou_df.iloc[0] if not taikou_df.empty else honmei
        taikou_num = int(taikou['馬番'])
        if taikou_num not in second_row and taikou_num != honmei_num:
            second_row.append(taikou_num)
            
        third_row = list(set(
            second_row +
            [n for n in turf_s_fup_nums if n != honmei_num] +
            opponents.sort_values('コース連順位').head(2)['馬番'].tolist() +
            opponents.sort_values('血統連順位').head(2)['馬番'].tolist() +
            opponents.sort_values('坂路調順位').head(2)['馬番'].tolist()
        )) if not opponents.empty else [honmei_num]
        
        ana_candidates = opponents[opponents['人気順位'] >= 4].sort_values(['dynamic_score', 'コース連順位', 'TUA順位', 'ARM順位'], ascending=[False, True, True, True]) if not opponents.empty else pd.DataFrame()
        if not ana_candidates.empty:
            ana = ana_candidates.iloc[0]
            ana_num = int(ana['馬番'])
        elif not opponents.empty:
            ana = opponents.iloc[-1]
            ana_num = int(ana['馬番'])
        else:
            ana = honmei
            ana_num = honmei_num

    st.markdown(f"""
    <div class='recom-panel-go'>
        <div class='recom-title-go'>{mode_name}</div>
        <div style='font-size: 13px; color: #9ca3af; margin-bottom: 10px;'>{mode_desc}</div>
        <div class='recom-row'>🥇 <strong>本命・連軸</strong>: <span class='recom-val-num'>{honmei_num}番 {honmei['馬名']}</span>（F指数: {honmei['F']}[{honmei['F順位']}位] / コース連: {honmei['コース連順位']}位 / 動的スコア: {honmei['dynamic_score']:.1f}）</div>
        <div class='recom-row'>🛡️ <strong>対抗・相手筆頭</strong>: <span class='recom-val-num'>{taikou_num}番 {taikou['馬名']}</span>（F指数: {taikou['F']}[{taikou['F順位']}位] / S順位: {taikou['S順位']}位 / コース連: {taikou['コース連順位']}位）</div>
        <div class='recom-row'>💣 <strong>激走穴特注（保険推奨）</strong>: <span class='recom-val-num'>{ana_num}番 {ana['馬名']}</span>（{ana['人気順位']}番人気 / コース連: {ana['コース連順位']}位 / TUA: {ana['TUA']}[{ana['TUA順位']}位] / ARM: {ana['ARM']}）</div>
    </div>
    """, unsafe_allow_html=True)

    sec_nums_str = ", ".join(map(str, sorted(second_row)))
    third_nums_str = ", ".join(map(str, sorted(third_row)))

    st.markdown(f"""
    <div class='recom-block'>
        <h4 style='color: #60a5fa; margin-top: 0;'>🎯 標準ハイブリッド馬券パック フォーメーション（保険網完備）</h4>
        <ul style='list-style-type: none; padding-left: 0; line-height: 1.8; font-size: 14px;'>
            <li><strong>【第1の網：主軸回収】</strong> 単勝: <span style='color: #fbbf24; font-weight: bold;'>{honmei_num}</span> ／ 馬単: <span style='color: #fbbf24; font-weight: bold;'>{honmei_num} → {taikou_num}</span></li>
            <li><strong>【第2の網：連対確保・保険】</strong> 馬連: <span style='color: #38bdf8; font-weight: bold;'>{honmei_num} - {sec_nums_str}</span> ／ ワイド（保険）: <span style='color: #f472b6; font-weight: bold;'>{honmei_num} - {ana_num}</span></li>
            <li><strong>【第3の網：中配当網】</strong> 3連複F: <span style='color: #34d399; font-weight: bold;'>{honmei_num}</span> ＝ <span style='color: #38bdf8;'>{sec_nums_str}</span> ＝ <span style='color: #a78bfa;'>{third_nums_str}</span></li>
            <li><strong>【第4の網：高配当万馬券】</strong> 3連単F: <span style='color: #fbbf24; font-weight: bold;'>{honmei_num}</span> ⇄ <span style='color: #38bdf8;'>{taikou_num}</span> → <span style='color: #a78bfa;'>{third_nums_str}</span></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # 2. 出走馬詳細カルテ表示用データフレーム（チェックBOXオンの時だけ絞り込み、オフの時は全頭表示を完全保証）
    display_df = race_df.copy()
    if filter_f1_course_blood:
        filtered = display_df[(display_df['F順位'] == 1) & ((display_df['コース連順位'] <= 3) | (display_df['血統連順位'] <= 3))]
        if not filtered.empty: display_df = filtered
    if filter_tua1_f_top3:
        filtered = display_df[(display_df['TUA順位'] == 1) & (display_df['F順位'] <= 3)]
        if not filtered.empty: display_df = filtered
    if filter_course1_s_top3:
        filtered = display_df[(display_df['コース連順位'] == 1) & (display_df['S順位'] <= 3)]
        if not filtered.empty: display_df = filtered
    if filter_f70_or_s60:
        filtered = display_df[(display_df['F'] >= 70.0) | (display_df['S'] >= 60.0)]
        if not filtered.empty: display_df = filtered
    if filter_target_sakaro_a3:
        filtered = display_df[display_df['s_row'].apply(lambda x: isinstance(x, pd.Series) and not x.empty and float(x.get('Lap1', 99) or 99) <= 11.9 and float(x.get('Lap1', 99) or 99) < float(x.get('Lap2', 99) or 99))]
        if not filtered.empty: display_df = filtered
    if filter_target_c_horse:
        filtered = display_df[display_df.apply(lambda x: int(x['ARM順位']) <= 3 and float(x['w_row'].get('5F', 99) or 99) <= 69.0 and float(x['s_row'].get('Time1', 99) or 99) <= 59.9 if isinstance(x['w_row'], pd.Series) and isinstance(x['s_row'], pd.Series) else False, axis=1)]
        if not filtered.empty: display_df = filtered
    if filter_target_stable_ace:
        ace_trainers = ['藤原', '杉山', '矢作', '中内田', '木村', '堀', '友道', '池添', '吉岡', '大竹', '斉藤', '音無', '国枝']
        filtered = display_df[display_df['調教師'].apply(lambda t: any(ac in t for ac in ace_trainers))]
        if not filtered.empty: display_df = filtered
    if filter_target_same_umaban:
        j_counts = df.groupby(['騎手', '馬番']).size().to_dict()
        filtered = display_df[display_df.apply(lambda r: j_counts.get((r['騎手'], r['馬番']), 1) >= 2, axis=1)]
        if not filtered.empty: display_df = filtered

    jockey_umaban_counts = df.groupby(['騎手', '馬番']).size().to_dict() if {'騎手', '馬番'}.issubset(df.columns) else {}

    st.markdown("### 🏇 出走馬詳細カルテ ＆ レース内調教比較")
    sort_col1, sort_col2 = st.columns(2)
    with sort_col1:
        sort_criterion = st.selectbox('📊 並び替え基準（指数・調教比較）', [
            '総合動的評価スコア順', '坂路全体タイム順（速い順）', '坂路ラスト1F順（速い順）', '坂路加速量順（切れ味順）', 'ウッド全体タイム(5F)順', 'ウッドラスト1F順',
            'F指数 降順', 'ARM指数 降順', 'TUA指数 降順', 'S指数 降順', 'Fup2点数 降順', '馬番順'
        ], index=0)

    if sort_criterion == '総合動的評価スコア順': sorted_df = display_df.sort_values('dynamic_score', ascending=False)
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
        if u_no == honmei_num: badges.append("<span class='badge-mark-honmei'>◎ 本命</span>")
        elif u_no == taikou_num: badges.append("<span class='badge-mark-taikou'>◯ 対抗</span>")
        elif u_no == ana_num: badges.append("<span class='badge-mark-ana'>🔥 穴特注(保険)</span>")

        j_name = h['騎手']
        pair_cnt = jockey_umaban_counts.get((j_name, u_no), 1)
        if j_name and pair_cnt >= 2:
            badges.append(f"<span class='badge-jockey-same-umaban'>🔥 同馬番複数騎乗(勝負): {j_name}({pair_cnt}回・{u_no}番)</span>")

        in_v = h['印']
        m2_v = h['M2']
        c_mark_val = h['C(マーク)']
        c_horse_val = h['C(馬)']

        if c_mark_val: badges.append(f"<span class='badge-c-mark'>🏷️ C(マーク): {c_mark_val}</span>")
        if c_horse_val: badges.append(f"<span class='badge-c-horse'>🐴 C(馬): {c_horse_val}</span>")

        f_eval = h['f_eval']
        if f_eval == "S評価": badges.append("<span class='badge-f-eval-s'>🔥 F指数 S評価(特注馬)</span>")
        elif f_eval == "A評価": badges.append("<span class='badge-f-eval-a'>⭐ F指数 A評価</span>")
        elif f_eval == "B評価": badges.append("<span class='badge-f-eval-b'>📌 F指数 B評価</span>")

        for c_type, c_text in h.get('combo_hits', []):
            if c_type == "golden":
                badges.append(f"<span class='badge-golden-combo'>{c_text}</span>")
            else:
                badges.append(f"<span class='badge-value-combo'>{c_text}</span>")

        if in_v == 0: badges.append("<span class='badge-danger-fan'>🚨 前走相手馬券内0頭(凡戦注意)</span>")
        elif in_v >= 8: badges.append(f"<span class='badge-high-level'>👑 前走相手馬券内{in_v}頭(超ハイレベル)</span>")
        elif in_v >= 3: badges.append(f"<span class='badge-notebook-hit'>🔥 前走相手馬券内{in_v}頭</span>")

        if m2_v >= 5: badges.append(f"<span class='badge-cushion-fit'>⭐ 前走相手掲示板{m2_v}頭(出世レース)</span>")

        is_as = h['F順位'] <= 3 and h['S順位'] <= 3
        if is_as: badges.append("<span class='badge-as-intersect'>👑 AS交差馬 (F&S上位)</span>")

        if h['is_rescued']: badges.append("<span class='badge-rescued'>🛡️ 強力加点・保険救済馬</span>")
        for nb in h['nb_hits']: badges.append(f"<span class='badge-notebook-hit'>{nb}</span>")
        for stbl in h['stable_hits']: badges.append(f"<span class='badge-stable-hit'>{stbl}</span>")

        c_key = (chosen_venue, h['track'], h['dist'], h['種牡馬'], c_cat)
        if c_key in CUSHION_DATA_BOOK:
            judg, stat_txt = CUSHION_DATA_BOOK[c_key]
            if judg == '最重要': badges.append(f"<span class='badge-cushion-fit'>🌿 クッション特注: {h['種牡馬']} ({stat_txt})</span>")

        fup_val = int(h['Fup2'])
        fup_rk = int(h['Fup2順位'])
        if fup_rk == 1 and fup_val >= 5:
            fup_badge = f"<span class='fup-badge-rank1-high'>👑🔥 {fup_val}点 (順位1位)</span>"
        elif fup_rk == 1:
            fup_badge = f"<span class='fup-badge-rank1'>👑 {fup_val}点 (順位1位)</span>"
        elif fup_val >= 7:
            fup_badge = f"<span class='fup-badge-top'>⚡ {fup_val}点 (順位{fup_rk})</span>"
        elif fup_val >= 5:
            fup_badge = f"<span class='fup-badge-mid'>🔥 {fup_val}点 (順位{fup_rk})</span>"
        elif fup_rk == 2:
            fup_badge = f"<span class='val-rank-2'>{fup_val}点 (順位2)</span>"
        elif fup_rk == 3:
            fup_badge = f"<span class='val-rank-3'>{fup_val}点 (順位3)</span>"
        else:
            fup_badge = f"<span class='fup-badge-low'>{fup_val}点 (順位{fup_rk})</span>"

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

        judge_label, judge_color = parse_and_judge_lap(s_l1, s_l2, s_t4)
        sakaro_str = f"坂路[4F:{s_t4 if pd.notnull(s_t4) else '---'} | L2:{s_l2 if pd.notnull(s_l2) else '---'} → L1:{s_l1 if pd.notnull(s_l1) else '---'}]" if pd.notnull(s_t4) else "坂路データなし"
        wood_str = f"ウッド[5F:{w_5f if pd.notnull(w_5f) else '---'} → L1:{w_l1 if pd.notnull(w_l1) else '---'}]" if pd.notnull(w_5f) else "ウッドデータなし"
        choukyou_summary = f"{sakaro_str} ｜ {wood_str}"

        m_uid = re.search(r'\d+', str(h['race_uid']))
        r_num_str = m_uid.group() if m_uid else ''
        race_place_num_str = f"【{chosen_venue}{r_num_str}R】" if r_num_str else f"【{chosen_venue}】"

        st.markdown(f"""
        <div class='horse-card'>
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
                    <span style='font-size: 12.5px; color: #94a3b8;'>{choukyou_summary}</span> ｜ 坂路血: <span class='{hk_rk_cls}'>{h['坂路血順位']}位</span> / 時計血: <span class='{tk_rk_cls}'>{h['時計血順位']}位</span></li>
                <li><strong>適性・補正順位</strong>: コース連: <span class='{c_rk_cls}'>{h['コース連順位']}位</span> / 血統連: <span class='{k_rk_cls}'>{h['血統連順位']}位</span> / Balance: <span class='{b_rk_cls}'>{h['バランス順位']}位</span></li>
                <li><strong>血統＆展開</strong>: 父 {h['種牡馬']} ｜ トラック替: {h['芝ダート変わり']} ｜ 前走脚質: {h['前走脚質']}（決手: {h['前走決手']}）｜ 間隔: {h['間隔']}週 ｜ 前場体重: {h['前場体重']}kg</li>
                <li><strong>総合動的評価スコア</strong>: <span style='color: #facc15; font-weight: bold; font-size: 15px;'>{h['dynamic_score']:.1f}点</span></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
