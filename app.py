import streamlit as st
import pandas as pd
import numpy as np
import os
import glob
import re
import datetime

# --- ページ基本設定 ---
st.set_page_config(
    page_title="Streamlit - 競馬予想10 クッション値Vr",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSSスタイル（ダークテーマUI & 豪華バッジ） ---
st.markdown("""
<style>
    .metric-container {
        display: flex;
        justify-content: space-around;
        background-color: #161b22;
        padding: 16px;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid #30363d;
    }
    .metric-box {
        text-align: center;
    }
    .metric-label {
        font-size: 13px;
        color: #8b949e;
        margin-bottom: 2px;
    }
    .metric-val {
        font-size: 28px;
        font-weight: bold;
        color: #f0f6fc;
    }
    
    /* 開催日時表示バッジ */
    .date-header-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        border: 1px solid #3b82f6;
        padding: 6px 16px;
        border-radius: 20px;
        color: #60a5fa;
        font-size: 15px;
        font-weight: bold;
        margin-bottom: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.4);
    }
    
    .horse-card {
        background-color: #161e2e;
        border-left: 5px solid #238636;
        padding: 16px 20px;
        border-radius: 8px;
        margin-bottom: 16px;
        border-top: 1px solid #30363d;
        border-right: 1px solid #30363d;
        border-bottom: 1px solid #30363d;
    }
    .horse-card-header {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 10px;
    }
    .horse-card-title {
        font-size: 19px;
        font-weight: bold;
        color: #ffffff;
    }
    .horse-card-list {
        list-style-type: none;
        padding-left: 0;
        margin: 0;
    }
    .horse-card-list li {
        font-size: 13.5px;
        color: #c9d1d9;
        margin-bottom: 5px;
        line-height: 1.6;
    }
    .horse-card-list li::before {
        content: "• ";
        color: #58a6ff;
        font-weight: bold;
    }

    /* === 🎯 狙い目専用バッジ === */
    .badge-target-win {
        background: linear-gradient(135deg, #e11d48 0%, #be123c 100%);
        color: #ffffff;
        font-weight: bold;
        font-size: 12px;
        padding: 3px 10px;
        border-radius: 6px;
        border: 1px solid #fda4af;
        box-shadow: 0 2px 6px rgba(225, 29, 72, 0.5);
    }
    .badge-target-axis {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: #ffffff;
        font-weight: bold;
        font-size: 12px;
        padding: 3px 10px;
        border-radius: 6px;
        border: 1px solid #93c5fd;
        box-shadow: 0 2px 6px rgba(37, 99, 235, 0.5);
    }
    .badge-target-himo {
        background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
        color: #ffffff;
        font-weight: bold;
        font-size: 12px;
        padding: 3px 10px;
        border-radius: 6px;
        border: 1px solid #fde68a;
        box-shadow: 0 2px 6px rgba(217, 119, 6, 0.5);
    }

    /* 厩舎好走パターン専用バッジ */
    .badge-stable-sugiyama {
        background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
        color: #ffffff;
        font-weight: bold;
        font-size: 11.5px;
        padding: 2px 8px;
        border-radius: 6px;
        border: 1px solid #fcd34d;
        box-shadow: 0 1px 3px rgba(0,0,0,0.4);
    }
    .badge-stable-nakauchida {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        color: #ffffff;
        font-weight: bold;
        font-size: 11.5px;
        padding: 2px 8px;
        border-radius: 6px;
        border: 1px solid #6ee7b7;
        box-shadow: 0 1px 3px rgba(0,0,0,0.4);
    }
    .badge-stable-yahagi {
        background: linear-gradient(135deg, #4338ca 0%, #3730a3 100%);
        color: #ffffff;
        font-weight: bold;
        font-size: 11.5px;
        padding: 2px 8px;
        border-radius: 6px;
        border: 1px solid #a5b4fc;
        box-shadow: 0 1px 3px rgba(0,0,0,0.4);
    }
    .badge-stable-kimura {
        background: linear-gradient(135deg, #be123c 0%, #9f1239 100%);
        color: #ffffff;
        font-weight: bold;
        font-size: 11.5px;
        padding: 2px 8px;
        border-radius: 6px;
        border: 1px solid #fda4af;
        box-shadow: 0 1px 3px rgba(0,0,0,0.4);
    }
    .badge-stable-general {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        color: #ffffff;
        font-weight: bold;
        font-size: 11.5px;
        padding: 2px 8px;
        border-radius: 6px;
        border: 1px solid #7dd3fc;
        box-shadow: 0 1px 3px rgba(0,0,0,0.4);
    }

    /* GTV馬専用バッジ */
    .badge-gtv-dirt {
        display: inline-flex;
        align-items: center;
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: #ffffff;
        font-weight: bold;
        font-size: 12px;
        padding: 2px 8px;
        border-radius: 6px;
        border: 1px solid #fbbf24;
        box-shadow: 0 1px 4px rgba(245, 158, 11, 0.4);
    }
    .badge-gtv-normal {
        display: inline-flex;
        align-items: center;
        background: linear-gradient(135deg, #4b5563 0%, #374151 100%);
        color: #f3f4f6;
        font-weight: bold;
        font-size: 12px;
        padding: 2px 8px;
        border-radius: 6px;
        border: 1px solid #9ca3af;
        box-shadow: 0 1px 3px rgba(0,0,0,0.3);
    }

    /* 10列目「印（C, K等）」専用バッジ */
    .badge-mark-c {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #00c6ff 0%, #0072ff 100%);
        color: #ffffff;
        font-weight: bold;
        font-size: 12.5px;
        padding: 2px 8px;
        border-radius: 6px;
        border: 1px solid #67e8f9;
        box-shadow: 0 1px 4px rgba(0, 198, 255, 0.4);
    }
    .badge-mark-k {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #f12711 0%, #f5af19 100%);
        color: #ffffff;
        font-weight: bold;
        font-size: 12.5px;
        padding: 2px 8px;
        border-radius: 6px;
        border: 1px solid #fde047;
        box-shadow: 0 1px 4px rgba(245, 175, 25, 0.4);
    }
    .badge-mark-general {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #8a2387 0%, #e94057 100%);
        color: #ffffff;
        font-weight: bold;
        font-size: 12.5px;
        padding: 2px 8px;
        border-radius: 6px;
        border: 1px solid #f472b6;
        box-shadow: 0 1px 4px rgba(233, 64, 87, 0.4);
    }

    /* クッション値 適性・危険バッジ */
    .badge-cushion-fit {
        display: inline-flex;
        align-items: center;
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        color: #ffffff;
        font-weight: bold;
        font-size: 12px;
        padding: 2px 8px;
        border-radius: 6px;
        border: 1px solid #34d399;
        box-shadow: 0 1px 3px rgba(0,0,0,0.4);
    }
    .badge-cushion-danger {
        display: inline-flex;
        align-items: center;
        background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
        color: #ffffff;
        font-weight: bold;
        font-size: 12px;
        padding: 2px 8px;
        border-radius: 6px;
        border: 1px solid #f87171;
        box-shadow: 0 1px 3px rgba(0,0,0,0.4);
    }

    /* 豪華特注バッジ */
    .badge-synergy {
        display: inline-flex;
        align-items: center;
        padding: 2px 8px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 11.5px;
        letter-spacing: 0.3px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.5);
    }
    .badge-iron {
        background: linear-gradient(135deg, #FFE259 0%, #FFA751 100%);
        color: #1a1000;
        border: 1px solid #FFF275;
    }
    .badge-high {
        background: linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%);
        color: #ffffff;
        border: 1px solid #FF8E72;
    }
    .badge-sakaro-fup {
        background: linear-gradient(135deg, #8A2387 0%, #E94057 50%, #F27121 100%);
        color: #ffffff;
        border: 1px solid #FFA07A;
    }
    .badge-fup-top {
        background: linear-gradient(135deg, #FF512F 0%, #DD2476 100%);
        color: #ffffff;
        border: 1px solid #FFA07A;
    }
    .badge-fup-high {
        background: linear-gradient(135deg, #F09819 0%, #EDDE5D 100%);
        color: #2b1d00;
        border: 1px solid #FFE066;
    }
    .badge-s1 {
        background: linear-gradient(135deg, #9C27B0 0%, #E040FB 100%);
        color: #ffffff;
        border: 1px solid #EA80FC;
    }
    .badge-f1 {
        background: linear-gradient(135deg, #F7971E 0%, #FFD200 100%);
        color: #2b1d00;
        border: 1px solid #FFE066;
    }
    .badge-arms1 {
        background: linear-gradient(135deg, #00B4DB 0%, #0083B0 100%);
        color: #ffffff;
        border: 1px solid #56CCF2;
    }
    .badge-tua1 {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: #052010;
        border: 1px solid #80FFB4;
    }
    .badge-bomb {
        background: linear-gradient(135deg, #EB3349 0%, #F45C43 100%);
        color: #ffffff;
        border: 1px solid #FFA07A;
    }

    .badge-accel {
        background-color: #238636;
        color: #ffffff;
        padding: 2px 5px;
        border-radius: 4px;
        font-size: 11px;
    }
    .badge-decel {
        background-color: #6e7681;
        color: #ffffff;
        padding: 2px 5px;
        border-radius: 4px;
        font-size: 11px;
    }

    /* === 順位カラーハイライト（馬券内率の高い1〜5位まで色付け） === */
    .rank-1st {
        color: #FFD700;
        font-weight: bold;
        background-color: rgba(255, 215, 0, 0.22);
        padding: 2px 6px;
        border-radius: 4px;
        border: 1px solid rgba(255, 215, 0, 0.6);
    }
    .rank-2nd {
        color: #E2E8F0;
        font-weight: bold;
        background-color: rgba(226, 232, 240, 0.20);
        padding: 2px 6px;
        border-radius: 4px;
        border: 1px solid rgba(226, 232, 240, 0.6);
    }
    .rank-3rd {
        color: #F97316;
        font-weight: bold;
        background-color: rgba(249, 115, 22, 0.20);
        padding: 2px 6px;
        border-radius: 4px;
        border: 1px solid rgba(249, 115, 22, 0.6);
    }
    .rank-top5 {
        color: #34D399;
        font-weight: bold;
        background-color: rgba(52, 211, 153, 0.15);
        padding: 2px 6px;
        border-radius: 4px;
        border: 1px solid rgba(52, 211, 153, 0.45);
    }
    .rank-normal {
        color: #8b949e;
        font-size: 12px;
    }
    
    /* Fup数値ハイライト */
    .fup-high-val {
        color: #FFD700;
        font-weight: bold;
        background-color: rgba(255, 165, 0, 0.2);
        padding: 1px 6px;
        border-radius: 4px;
        border: 1px solid rgba(255, 165, 0, 0.5);
    }
</style>
""", unsafe_allow_html=True)


# --- サイドバー: 4大CSVアップローダー ---
st.sidebar.markdown("### 📁 4大CSVデータ読み込み")
with st.sidebar.expander("CSVファイルの指定 / アップロード", expanded=False):
    up_index = st.file_uploader("1. 出馬表・指数 CSV", type=['csv'], key='up_index')
    up_gtv = st.file_uploader("2. GTVオッズ CSV", type=['csv'], key='up_gtv')
    up_sakaro = st.file_uploader("3. 坂路調教 CSV", type=['csv'], key='up_sakaro')
    up_wood = st.file_uploader("4. ウッド調教 CSV", type=['csv'], key='up_wood')


# --- 馬名クリーニング統一関数 ---
def clean_horse_name(name):
    if pd.isnull(name):
        return ""
    s = str(name).strip()
    s = s.replace('*', '').replace('$', '').replace(' ', '').replace(' ', '')
    return s


# --- CSV読み込み汎用ヘルパー ---
def read_csv_flexible(file_obj, candidate_patterns):
    src = file_obj
    if src is None:
        for pat in candidate_patterns:
            matches = glob.glob(pat)
            if matches:
                src = matches[0]
                break
    if src is None:
        return pd.DataFrame()
    
    encodings = ['utf-8-sig', 'shift-jis', 'utf-8', 'cp932']
    for enc in encodings:
        try:
            if hasattr(src, 'seek'):
                src.seek(0)
            df = pd.read_csv(src, encoding=enc)
            if not df.empty:
                return df
        except Exception:
            continue
    return pd.DataFrame()


def find_col(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None


# --- 順位カラー整形ヘルパー（1〜5位までハイライト） ---
def format_rank_badge(rank_val):
    if pd.isnull(rank_val) or rank_val == 99 or rank_val == 0:
        return "<span class='rank-normal'>-位</span>"
    try:
        r = int(rank_val)
    except Exception:
        return "<span class='rank-normal'>-位</span>"
        
    if r == 1:
        return f"<span class='rank-1st'>🥇1位</span>"
    elif r == 2:
        return f"<span class='rank-2nd'>🥈2位</span>"
    elif r == 3:
        return f"<span class='rank-3rd'>🥉3位</span>"
    elif r in [4, 5]:
        return f"<span class='rank-top5'>{r}位</span>"
    else:
        return f"<span class='rank-normal'>{r}位</span>"


def format_fup_rank_badge(rank_val):
    if pd.isnull(rank_val) or rank_val == 99 or rank_val == 0:
        return "<span class='rank-normal'>-位</span>"
    try:
        r = int(rank_val)
    except Exception:
        return "<span class='rank-normal'>-位</span>"
        
    if r == 1:
        return f"<span class='rank-1st'>🥇 1位</span>"
    elif r in [2, 3]:
        return f"<span class='rank-top5'>{r}位</span>"
    else:
        return f"<span class='rank-normal'>{r}位</span>"


# --- 10列目の印（C, K等）バッジ生成ヘルパー ---
def format_mark_badge(mark_str):
    if not mark_str or pd.isnull(mark_str):
        return ""
    m = str(mark_str).strip()
    if not m or m in ['nan', 'None', '-', '0']:
        return ""
    
    if m.upper() == 'C':
        return f"<span class='badge-mark-c'>C</span>"
    elif m.upper() == 'K':
        return f"<span class='badge-mark-k'>K</span>"
    else:
        return f"<span class='badge-mark-general'>{m}</span>"


# --- クッション値 × 種牡馬適性ロジック ---
def get_cushion_band(venue, c_val):
    if c_val is None:
        return "standard"
    if venue in ['札幌', '函館']:
        if c_val >= 8.5:
            return "high"
        elif c_val >= 7.6:
            return "standard_high"
        elif c_val >= 7.0:
            return "standard"
        else:
            return "low"
    else:
        if c_val >= 10.0:
            return "high"
        elif c_val >= 9.5:
            return "standard_high"
        elif c_val >= 9.0:
            return "standard"
        else:
            return "low"


def evaluate_sire_cushion(sire_name, band):
    if not sire_name or pd.isnull(sire_name):
        return ""
    sire = str(sire_name).strip()
    
    high_fit_sires = ['ロードカナロア', 'エピファネイア', 'キズナ', 'モーリス', 'ディープインパクト', 'ドゥラメンテ', 'イスラボニータ', 'ダイワメジャー', 'スワーヴリチャード', 'ブリックスアンドモルタル']
    high_danger_sires = ['ハービンジャー', 'オルフェーヴル', 'ルーラーシップ', 'ドレフォン', 'ゴールドシップ', 'リアルスティール']

    low_fit_sires = ['ハービンジャー', 'オルフェーヴル', 'ルーラーシップ', 'ゴールドシップ', 'キタサンブラック', 'バゴ', 'スクリーンヒーロー', 'サトノダイヤモンド']
    low_danger_sires = ['ロードカナロア', 'エピファネイア', 'モーリス', 'イスラボニータ']

    std_high_fit_sires = ['エピファネイア', 'キズナ', 'ドゥラメンテ', 'モーリス', 'ロードカナロア', 'ハーツクライ']

    if band == "high":
        if any(h in sire for h in high_fit_sires):
            return "<span class='badge-cushion-fit'>🟢 クッション適 (硬)</span>"
        elif any(d in sire for d in high_danger_sires):
            return "<span class='badge-cushion-danger'>🔴 危険血統 (硬)</span>"
    elif band == "low":
        if any(l in sire for l in low_fit_sires):
            return "<span class='badge-cushion-fit'>🟢 軟馬場適</span>"
        elif any(d in sire for d in low_danger_sires):
            return "<span class='badge-cushion-danger'>🔴 危険血統 (軟)</span>"
    elif band == "standard_high":
        if any(sh in sire for sh in std_high_fit_sires):
            return "<span class='badge-cushion-fit'>🟢 クッション適</span>"
            
    return ""


# ==============================================================================
# ★ 厩舎好走パターン 自動判定関数
# ==============================================================================
def get_stable_synergy_badges(row):
    trainer = str(row.get('調教師', ''))
    jockey = str(row.get('騎手', ''))
    f_rank = row.get('F_rank', 99)
    fup_val = row.get('Fup', 0)
    
    s_4f = row.get('坂路_4F', np.nan)
    s_1f = row.get('坂路_1F', np.nan)
    s_l2 = row.get('坂路_Lap2', np.nan)
    s_l1 = row.get('坂路_Lap1', np.nan)
    is_s_accel = bool(row.get('坂路_完全加速', False))
    
    w_6f = row.get('wood_6F', np.nan)
    w_1f = row.get('wood_1F', np.nan)
    
    badges = []
    
    # 1. 杉山晴紀厩舎
    if '杉山晴' in trainer:
        if pd.notnull(s_1f) and s_1f <= 11.9 and is_s_accel:
            badges.append("<span class='badge-stable-sugiyama'>🏅 杉山・MAX坂路</span>")
        elif pd.notnull(s_4f) and s_4f <= 52.9 and pd.notnull(s_1f) and s_1f <= 12.2:
            badges.append("<span class='badge-stable-sugiyama'>🏅 杉山・黄金坂路</span>")
        if '西村淳' in jockey:
            badges.append("<span class='badge-stable-sugiyama'>🤝 杉山×西村淳</span>")
            
    # 2. 中内田充正厩舎
    if '中内田' in trainer:
        if '川田' in jockey and f_rank == 1:
            badges.append("<span class='badge-stable-nakauchida'>👑 中内田×川田×F1</span>")
        if pd.notnull(w_1f) and 11.0 <= w_1f <= 11.3:
            badges.append("<span class='badge-stable-nakauchida'>⚔️ 中内田・CW究極</span>")
            
    # 3. 矢作芳人厩舎
    if '矢作' in trainer:
        if pd.notnull(s_l2) and pd.notnull(s_l1) and 12.0 <= s_l2 <= 12.9 and 12.0 <= s_l1 <= 12.9 and s_l2 > s_l1:
            if pd.notnull(s_4f) and s_4f <= 53.0:
                badges.append("<span class='badge-stable-yahagi'>🌪️ 矢作・A2猛時計</span>")
            else:
                badges.append("<span class='badge-stable-yahagi'>🌪️ 矢作・A2加速</span>")
                
    # 4. 木村哲也厩舎
    if '木村哲' in trainer or '木村' in trainer:
        if 'ルメール' in jockey and fup_val >= 5:
            badges.append("<span class='badge-stable-kimura'>🎯 木村哲×ルメール</span>")
        if pd.notnull(w_1f) and w_1f <= 11.5:
            badges.append("<span class='badge-stable-kimura'>⚔️ 木村哲・南W勝負</span>")
            
    # 5. 安田厩舎 (安田隆行 / 安田翔伍)
    if '安田' in trainer:
        if pd.notnull(s_4f) and s_4f <= 51.9:
            badges.append("<span class='badge-stable-general'>⚡ 安田・坂路猛時計</span>")
            
    # 6. 松永幹夫厩舎
    if '松永幹' in trainer:
        if pd.notnull(s_1f) and s_1f <= 12.0 and is_s_accel:
            badges.append("<span class='badge-stable-general'>🏇 松永幹・坂路加速</span>")
            
    # 7. 藤原英昭厩舎
    if '藤原英' in trainer or '藤原' in trainer:
        if pd.notnull(w_6f) and w_6f <= 82.0:
            badges.append("<span class='badge-stable-general'>🏛️ 藤原英・CW好時計</span>")
            
    return badges


# --- データロード＆4CSV統合処理 ---
@st.cache_data
def load_and_merge_all(f_index, f_gtv, f_sakaro, f_wood):
    index_patterns = [
        'data/出馬表_指数*.csv', '出馬表_指数*.csv',
        'data/指数、検証用*.csv', '指数、検証用*.csv',
        'data/指数*.csv', '指数*.csv'
    ]
    index_src = f_index
    if index_src is None:
        for pat in index_patterns:
            matches = glob.glob(pat)
            if matches:
                index_src = matches[0]
                break

    records = []
    if index_src is not None:
        if isinstance(index_src, str):
            with open(index_src, 'r', encoding='shift-jis', errors='ignore') as f:
                lines = f.readlines()
        else:
            content = index_src.read()
            try:
                lines = content.decode('shift-jis').splitlines()
            except Exception:
                lines = content.decode('utf-8', errors='ignore').splitlines()

        fw_map = {'１': 1, '２': 2, '３': 3, '４': 4, '５': 5, '６': 6, '７': 7, '８': 8, '９': 9, '10': 10,
                  '11': 11, '12': 12, '13': 13, '14': 14, '15': 15, '16': 16, '17': 17, '18': 18}

        for line_idx, line in enumerate(lines):
            parts = [p.strip() for p in line.strip().split(',')]
            n = len(parts)
            if n < 10:
                continue

            race_id, track, dist, umaban, horse_raw = parts[0], "", "", "", None
            trainer, jockey, sire = "", "", ""
            mark = ""
            pop, finish = None, None
            fup, fup_rank = 0, 99
            s_val, s_rank = 0.0, 99
            f_val, f_rank = 0.0, 99
            arms_val, arms_rank = 0.0, 99
            tua_val, tua_rank = 0.0, 99

            if n >= 24:
                track, dist, umaban = parts[1], parts[2], parts[3]
                horse_raw = parts[4]
                trainer, jockey = parts[6], parts[7]
                pop = parts[8]
                mark = parts[9] if n > 9 else ""
                s_val = pd.to_numeric(parts[10], errors='coerce')
                s_rank = pd.to_numeric(parts[11], errors='coerce')
                fup = pd.to_numeric(parts[10], errors='coerce')
                fup_rank = pd.to_numeric(parts[11], errors='coerce')
                f_val = pd.to_numeric(parts[13], errors='coerce')
                f_rank = pd.to_numeric(parts[14], errors='coerce')
                arms_val = pd.to_numeric(parts[16], errors='coerce')
                arms_rank = pd.to_numeric(parts[17], errors='coerce')
                tua_val = pd.to_numeric(parts[19], errors='coerce')
                tua_rank = pd.to_numeric(parts[20], errors='coerce')
                finish = parts[22] if n > 22 else ""
                sire = parts[23] if n > 23 else ""
            elif n == 23:
                track, dist, umaban = parts[1], parts[2], parts[3]
                horse_raw = parts[4]
                trainer, jockey = parts[6], parts[7]
                pop = parts[8]
                mark = parts[9] if n > 9 else ""
                s_val = pd.to_numeric(parts[10], errors='coerce')
                s_rank = pd.to_numeric(parts[11], errors='coerce')
                fup = pd.to_numeric(parts[10], errors='coerce')
                fup_rank = pd.to_numeric(parts[11], errors='coerce')
                f_val = pd.to_numeric(parts[12], errors='coerce')
                f_rank = pd.to_numeric(parts[13], errors='coerce')
                arms_val = pd.to_numeric(parts[16], errors='coerce')
                arms_rank = pd.to_numeric(parts[17], errors='coerce')
                tua_val = pd.to_numeric(parts[18], errors='coerce')
                tua_rank = pd.to_numeric(parts[19], errors='coerce')
                finish = parts[20]
                sire = parts[21] if n > 21 else ""
            else:
                continue

            horse = clean_horse_name(horse_raw)
            if horse:
                fin_int = fw_map.get(finish, int(finish) if str(finish).isdigit() else np.nan)
                pop_int = int(pop) if str(pop).isdigit() else np.nan
                u_int = int(umaban) if str(umaban).isdigit() else 99

                records.append({
                    'race_id': race_id,
                    'track': track,
                    'dist': dist,
                    '馬番': u_int,
                    '馬名': horse,
                    '印': str(mark).strip(),
                    '調教師': trainer,
                    '騎手': jockey,
                    '種牡馬': sire,
                    '人気': pop_int,
                    '着順': fin_int,
                    'Fup': fup if not np.isnan(fup) else 0,
                    'Fup_rank': int(fup_rank) if not np.isnan(fup_rank) else 99,
                    'S指数': s_val if not np.isnan(s_val) else 0.0,
                    'S_rank': int(s_rank) if not np.isnan(s_rank) else 99,
                    'F指数': f_val if not np.isnan(f_val) else 0.0,
                    'F_rank': int(f_rank) if not np.isnan(f_rank) else 99,
                    'arms': arms_val if not np.isnan(arms_val) else 0.0,
                    'arms_rank': int(arms_rank) if not np.isnan(arms_rank) else 99,
                    'tua': tua_val if not np.isnan(tua_val) else 0.0,
                    'tua_rank': int(tua_rank) if not np.isnan(tua_rank) else 99
                })

    df_main = pd.DataFrame(records)
    if df_main.empty:
        return pd.DataFrame(), None

    resets = [0]
    for i in range(1, len(df_main)):
        h_curr = df_main.loc[i, '馬名']
        h_prev = df_main.loc[i - 1, '馬名']
        if h_curr < h_prev and (h_prev > 'マ' and h_curr < 'ウ'):
            resets.append(i)
    resets.append(len(df_main))
    batch_ids = []
    for i in range(len(resets) - 1):
        batch_ids.extend([i] * (resets[i + 1] - resets[i]))
    df_main['batch_id'] = batch_ids
    df_main['race_uid'] = df_main['batch_id'].astype(str) + "_" + df_main['race_id']

    venue_dict = {'東': '東京', '中': '中山', '京': '京都', '阪': '阪神', '名': '中京', '小': '小倉', '新': '新潟', '福': '福島', '函': '函館', '札': '札幌'}
    def parse_race(rid):
        match = re.match(r'([^\d]+)(\d+)', str(rid))
        if match:
            v_code, r_no = match.group(1), int(match.group(2))
            v_name = venue_dict.get(v_code, v_code)
            return v_name, r_no
        return "その他", 99

    df_main[['競馬場名', 'R番号']] = df_main['race_id'].apply(lambda x: pd.Series(parse_race(x)))

    # GTV馬 CSV 結合
    detected_date = None
    gtv_patterns = ['data/GTV馬*.csv', 'GTV馬*.csv', 'data/GTV*.csv', 'GTV*.csv', 'data/*GTV*.csv', '*GTV*.csv']
    df_gtv = read_csv_flexible(f_gtv, gtv_patterns)
    
    source_name = getattr(f_gtv, 'name', '') if f_gtv is not None else ''
    if not source_name:
        for pat in gtv_patterns:
            matched = glob.glob(pat)
            if matched:
                source_name = os.path.basename(matched[0])
                break

    if source_name:
        d_match = re.search(r'(\d{1,4})[._](\d{1,2})[._](\d{1,2})', source_name)
        if d_match:
            y_raw = int(d_match.group(1))
            y = y_raw + 2000 if y_raw < 100 else y_raw
            m = int(d_match.group(2))
            d = int(d_match.group(3))
            try:
                detected_date = datetime.date(y, m, d)
            except Exception:
                pass
        else:
            d_match_short = re.search(r'(\d{1,2})[._](\d{1,2})', source_name)
            if d_match_short:
                m = int(d_match_short.group(1))
                d = int(d_match_short.group(2))
                try:
                    detected_date = datetime.date(2026, m, d)
                except Exception:
                    pass

    if not df_gtv.empty:
        name_col = find_col(df_gtv, ['馬名', '馬 名', '競走馬名'])
        if name_col:
            df_gtv['馬名'] = df_gtv[name_col].apply(clean_horse_name)
            df_gtv['is_gtv_horse'] = True
            gtv_cols = [c for c in df_gtv.columns if c not in ['馬名', name_col]]
            df_main = pd.merge(df_main, df_gtv[['馬名', 'is_gtv_horse'] + [c for c in gtv_cols if c != 'is_gtv_horse']].drop_duplicates('馬名'), on='馬名', how='left')
    
    if 'is_gtv_horse' not in df_main.columns:
        df_main['is_gtv_horse'] = False
    else:
        df_main['is_gtv_horse'] = df_main['is_gtv_horse'].fillna(False).astype(bool)

    # 3. 坂路調教 CSV
    sakaro_patterns = [
        'data/出馬表_坂路*.csv', '出馬表_坂路*.csv',
        'data/坂路、検証用*.csv', '坂路、検証用*.csv',
        'data/坂路調教*.csv', '坂路調教*.csv',
        'data/坂路*.csv', '坂路*.csv'
    ]
    sakaro_src = f_sakaro
    if sakaro_src is None:
        for pat in sakaro_patterns:
            matches = glob.glob(pat)
            if matches:
                sakaro_src = matches[0]
                break

    df_sakaro_clean = pd.DataFrame()
    if sakaro_src is not None:
        if isinstance(sakaro_src, str):
            with open(sakaro_src, 'r', encoding='shift-jis', errors='ignore') as f:
                s_lines = f.readlines()
        else:
            try:
                sakaro_src.seek(0)
            except Exception:
                pass
            content = sakaro_src.read()
            try:
                s_lines = content.decode('shift-jis').splitlines()
            except Exception:
                s_lines = content.decode('utf-8', errors='ignore').splitlines()

        s_records = []
        for line in s_lines:
            parts = [p.strip() for p in line.strip().split(',')]
            n = len(parts)
            if n < 4 or '馬名' in parts or '4F' in parts:
                continue

            h_name, s_4f, s_1f, s_l4, s_l3, s_l2, s_l1 = None, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan
            for idx, p in enumerate(parts):
                if re.match(r'^[\u30A0-\u30FF\* \$]{2,}$', p) and h_name is None:
                    h_name = clean_horse_name(p)
            
            numeric_parts = []
            for p in parts:
                val = pd.to_numeric(p, errors='coerce')
                if pd.notnull(val) and 10.0 <= val <= 120.0:
                    numeric_parts.append(val)
            
            if len(numeric_parts) >= 8:
                s_4f = numeric_parts[0]
                s_1f = numeric_parts[3]
                s_l4 = numeric_parts[4]
                s_l3 = numeric_parts[5]
                s_l2 = numeric_parts[6]
                s_l1 = numeric_parts[7]
            elif len(numeric_parts) >= 4:
                s_4f = numeric_parts[0]
                s_1f = numeric_parts[-1]
                if len(numeric_parts) >= 5:
                    s_l1 = numeric_parts[-1]
                    s_l2 = numeric_parts[-2]

            if h_name:
                s_records.append({
                    '馬名': h_name,
                    '坂路_4F': s_4f,
                    '坂路_1F': s_1f,
                    '坂路_Lap4': s_l4,
                    '坂路_Lap3': s_l3,
                    '坂路_Lap2': s_l2,
                    '坂路_Lap1': s_l1
                })

        if s_records:
            df_s_all = pd.DataFrame(s_records)
            df_s_valid = df_s_all.dropna(subset=['坂路_4F']).sort_values('坂路_4F', ascending=True)
            df_sakaro_clean = df_s_valid.drop_duplicates('馬名', keep='first').copy()
            remaining = df_s_all[~df_s_all['馬名'].isin(df_sakaro_clean['馬名'])].drop_duplicates('馬名')
            df_sakaro_clean = pd.concat([df_sakaro_clean, remaining], ignore_index=True)

            df_sakaro_clean['坂路_完全加速'] = (
                (df_sakaro_clean['坂路_Lap4'] > df_sakaro_clean['坂路_Lap3']) &
                (df_sakaro_clean['坂路_Lap3'] > df_sakaro_clean['坂路_Lap2']) &
                (df_sakaro_clean['坂路_Lap2'] > df_sakaro_clean['坂路_Lap1'])
            )
            df_main = pd.merge(df_main, df_sakaro_clean, on='馬名', how='left')

    if '坂路_4F' not in df_main.columns:
        df_main['坂路_4F'] = np.nan
        df_main['坂路_1F'] = np.nan
        df_main['坂路_Lap4'] = np.nan
        df_main['坂路_Lap3'] = np.nan
        df_main['坂路_Lap2'] = np.nan
        df_main['坂路_Lap1'] = np.nan
        df_main['坂路_完全加速'] = False

    # 4. ウッド調教 CSV
    wood_patterns = [
        'data/出馬表_ウッド*.csv', '出馬表_ウッド*.csv',
        'data/ウッド、検証用*.csv', 'ウッド、検証用*.csv',
        'data/ウッド調教*.csv', 'ウッド調教*.csv',
        'data/ウッド*.csv', 'ウッド*.csv'
    ]
    df_wood_raw = read_csv_flexible(f_wood, wood_patterns)
    if not df_wood_raw.empty:
        w_df = df_wood_raw[df_wood_raw.iloc[:, 0] != '場所'].copy()
        c_w_name = find_col(w_df, ['馬名', '馬 名', '競走馬名'])
        if c_w_name:
            w_df['馬名'] = w_df[c_w_name].apply(clean_horse_name)
            c_w_6f = find_col(w_df, ['6F', '６Ｆ', '６F', '6f'])
            c_w_5f = find_col(w_df, ['5F', '５Ｆ', '５F', '5f'])
            c_w_4f = find_col(w_df, ['4F', '４Ｆ', '４F', '4f'])
            c_w_1f = find_col(w_df, ['1F', '１Ｆ', '１F', '1f'])
            c_w_l4 = find_col(w_df, ['Lap4', 'lap4', 'LAP4', 'L4'])
            c_w_l3 = find_col(w_df, ['Lap3', 'lap3', 'LAP3', 'L3'])
            c_w_l2 = find_col(w_df, ['Lap2', 'lap2', 'LAP2', 'L2'])
            c_w_l1 = find_col(w_df, ['Lap1', 'lap1', 'LAP1', 'L1'])
            c_w_plc = find_col(w_df, ['場所', '調教場', '場'])
            c_w_date = find_col(w_df, ['年月日', '日付', '日付S'])

            w_df['wood_6F'] = pd.to_numeric(w_df[c_w_6f], errors='coerce') if c_w_6f else np.nan
            w_df['wood_5F'] = pd.to_numeric(w_df[c_w_5f], errors='coerce') if c_w_5f else np.nan
            w_df['wood_4F'] = pd.to_numeric(w_df[c_w_4f], errors='coerce') if c_w_4f else np.nan
            w_df['wood_1F'] = pd.to_numeric(w_df[c_w_1f], errors='coerce') if c_w_1f else np.nan
            w_df['wood_Lap4'] = pd.to_numeric(w_df[c_w_l4], errors='coerce') if c_w_l4 else np.nan
            w_df['wood_Lap3'] = pd.to_numeric(w_df[c_w_l3], errors='coerce') if c_w_l3 else np.nan
            w_df['wood_Lap2'] = pd.to_numeric(w_df[c_w_l2], errors='coerce') if c_w_l2 else np.nan
            w_df['wood_Lap1'] = pd.to_numeric(w_df[c_w_l1], errors='coerce') if c_w_l1 else np.nan
            w_df['wood_place'] = w_df[c_w_plc].astype(str) if c_w_plc else ""

            if c_w_date:
                w_df['調教日'] = pd.to_datetime(w_df[c_w_date].astype(str), format='%Y%m%d', errors='coerce')
                if detected_date is None and not w_df['調教日'].dropna().empty:
                    detected_date = w_df['調教日'].dropna().iloc[-1].date()
            
            w_sorted_5f = w_df.dropna(subset=['wood_5F']).sort_values('wood_5F', ascending=True)
            w_best = w_sorted_5f.drop_duplicates('馬名', keep='first').copy()
            w_remain = w_df[~w_df['馬名'].isin(w_best['馬名'])].sort_values('wood_1F', ascending=True).drop_duplicates('馬名', keep='first')
            w_final = pd.concat([w_best, w_remain], ignore_index=True)

            wood_cols = ['馬名', 'wood_place', 'wood_6F', 'wood_5F', 'wood_4F', 'wood_1F', 'wood_Lap4', 'wood_Lap3', 'wood_Lap2', 'wood_Lap1']
            df_main = pd.merge(df_main, w_final[wood_cols].drop_duplicates('馬名'), on='馬名', how='left')

    if 'wood_1F' not in df_main.columns:
        df_main['wood_place'] = ""
        df_main['wood_6F'] = np.nan
        df_main['wood_5F'] = np.nan
        df_main['wood_4F'] = np.nan
        df_main['wood_1F'] = np.nan
        df_main['wood_Lap4'] = np.nan
        df_main['wood_Lap3'] = np.nan
        df_main['wood_Lap2'] = np.nan
        df_main['wood_Lap1'] = np.nan

    df_main['wood_accel'] = df_main['wood_Lap2'] - df_main['wood_Lap1']
    df_main['is_wood_accel'] = (df_main['wood_accel'] > 0) & (df_main['wood_accel'].notna())

    df_main['坂路_4F_rank'] = df_main.groupby('race_uid')['坂路_4F'].rank(method='min', ascending=True)
    df_main['坂路_Lap4_rank'] = df_main.groupby('race_uid')['坂路_Lap4'].rank(method='min', ascending=True)
    df_main['坂路_Lap3_rank'] = df_main.groupby('race_uid')['坂路_Lap3'].rank(method='min', ascending=True)
    df_main['坂路_Lap2_rank'] = df_main.groupby('race_uid')['坂路_Lap2'].rank(method='min', ascending=True)
    df_main['坂路_Lap1_rank'] = df_main.groupby('race_uid')['坂路_Lap1'].rank(method='min', ascending=True)

    df_main['wood_5F_rank'] = df_main.groupby('race_uid')['wood_5F'].rank(method='min', ascending=True)
    df_main['wood_Lap4_rank'] = df_main.groupby('race_uid')['wood_Lap4'].rank(method='min', ascending=True)
    df_main['wood_Lap3_rank'] = df_main.groupby('race_uid')['wood_Lap3'].rank(method='min', ascending=True)
    df_main['wood_Lap2_rank'] = df_main.groupby('race_uid')['wood_Lap2'].rank(method='min', ascending=True)
    df_main['wood_Lap1_rank'] = df_main.groupby('race_uid')['wood_Lap1'].rank(method='min', ascending=True)

    if detected_date is None:
        detected_date = datetime.date(2026, 8, 30)

    return df_main, detected_date


df, race_date = load_and_merge_all(up_index, up_gtv, up_sakaro, up_wood)


# ==============================================================================
# ★ 狙い目フラグ（1着狙い・軸連対狙い・紐穴狙い）の自動判定ロジック
# ==============================================================================
if not df.empty:
    # 🥇 1着狙い（単勝 / 3連単アタマ固定）
    df['target_win'] = (
        ((df['F_rank'] == 1) & (df['arms_rank'] == 1)) |
        ((df['Fup'] >= 5) & (df['F_rank'] == 1)) |
        ((df['F_rank'] == 1) & (df['arms_rank'] <= 3) & (df['S_rank'] <= 3)) |
        ((df['F指数'] >= 66) & (df['arms_rank'] == 1))
    )
    
    # 🛡️ 軸・連対狙い（ワイド・3連複軸 / 複勝率50%〜60%）
    df['target_axis'] = (
        ((df['F_rank'] <= 2) & (df['arms_rank'] <= 3)) |
        ((df['F_rank'] == 1) & (df['tua_rank'] <= 3)) |
        ((df['Fup'] >= 4) & (df['F_rank'] <= 3))
    ) & (~df['target_win'])  # 1着狙いとは重複させない
    
    # 💣 紐穴狙い（3連複3列目 / 爆発的回収率）
    df['target_himo'] = (
        (df['人気'] >= 6) &
        ((df['坂路_完全加速'] == True) | (df['is_wood_accel'] == True)) &
        ((df['arms_rank'] <= 5) | (df['Fup'] >= 4) | (df['tua_rank'] <= 3))
    )

    # 黄金シナジー該当フラグ
    df['is_syn_iron'] = (
        (df['F_rank'] == 1) &
        (df['arms_rank'] <= 3) &
        (df['wood_1F'] <= 11.5) &
        (df['is_wood_accel'] == True)
    )
    df['is_syn_high'] = (
        ((df['F_rank'] == 1) | (df['F指数'] >= 66)) &
        (df['wood_1F'] <= 11.5) &
        (df['is_wood_accel'] == True)
    )
    df['is_syn_fup_sakaro'] = (
        (df['Fup'] >= 5) &
        (df['坂路_完全加速'] == True)
    )
    df['is_syn_bomb'] = (
        (df['人気'] >= 6) &
        (df['Fup'] >= 4) &
        ((df['is_wood_accel'] == True) | (df['坂路_完全加速'] == True))
    )
    df['is_syn_f1_rap'] = (
        (df['F_rank'] == 1) &
        (
            ((df['wood_1F'] <= 12.4) & (df['is_wood_accel'] == True)) |
            ((df['坂路_1F'] <= 12.4) & (df['坂路_完全加速'] == True))
        )
    )
    # 厩舎好走パターンの判定フラグ
    df['has_stable_pattern'] = df.apply(lambda r: len(get_stable_synergy_badges(r)) > 0, axis=1)


# --- メイン画面準備 & 競馬場一覧取得 ---
if df.empty:
    st.warning("⚠️ CSVデータが読み込まれていません。サイドバーの「📁 4大CSVデータ読み込み」からファイルを指定するか、同一フォルダにCSVを配置してください。")
    st.stop()

venue_sort_order = ['東京', '中山', '京都', '阪神', '中京', '小倉', '新潟', '福島', '函館', '札幌', 'その他']
existing_venues = [v for v in venue_sort_order if v in df['競馬場名'].unique()] + [v for v in df['競馬場名'].unique() if v not in venue_sort_order]

if 'active_venue' not in st.session_state or st.session_state['active_venue'] not in existing_venues:
    st.session_state['active_venue'] = existing_venues[0]


# ==============================================================================
# ★ サイドバー: 競馬場別クッション値 & 馬場状態
# ==============================================================================
st.sidebar.markdown("---")
st.sidebar.markdown("### 芝馬場状態")
turf_condition = st.sidebar.selectbox("芝馬場状態", ["良", "稍重", "重", "不良"], index=0, label_visibility="collapsed")

st.sidebar.markdown(f"### 芝クッション値 ({st.session_state['active_venue']})")

default_cushions = {'札幌': 7.5, '函館': 7.4, '中京': 9.5, '新潟': 9.4, '東京': 9.6, '中山': 9.8, '京都': 9.5, '阪神': 9.6, '小倉': 9.3, '福島': 9.2}

cushion_state_key = f"cushion_val_{st.session_state['active_venue']}"
if cushion_state_key not in st.session_state:
    st.session_state[cushion_state_key] = default_cushions.get(st.session_state['active_venue'], 9.5)

current_cushion_val = st.sidebar.number_input(
    f"芝クッション値 ({st.session_state['active_venue']})",
    min_value=6.0,
    max_value=13.0,
    value=float(st.session_state[cushion_state_key]),
    step=0.1,
    key=cushion_state_key,
    label_visibility="collapsed"
)

current_band = get_cushion_band(st.session_state['active_venue'], current_cushion_val)
if current_band == "high":
    band_label = f"📍 判定帯: 硬め・高クッション ({current_cushion_val})"
elif current_band == "standard_high":
    band_label = f"📍 判定帯: 標準高 ({current_cushion_val})"
elif current_band == "low":
    band_label = f"📍 判定帯: 軟らかめ・タフ ({current_cushion_val})"
else:
    band_label = f"📍 判定帯: 標準 ({current_cushion_val})"

st.sidebar.button(band_label, use_container_width=True)

if st.sidebar.button("🔄 最新データへ強制再読み込み", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")


# ==============================================================================
# ★ 左側サイドバー: 🎯 狙い目抽出フィルター（新設）
# ==============================================================================
st.sidebar.markdown("### 🎯 狙い目抽出")
win_cnt = int(df['target_win'].sum())
axis_cnt = int(df['target_axis'].sum())
himo_cnt = int(df['target_himo'].sum())

filter_target_win = st.sidebar.checkbox(f"🥇 1着狙い (勝率25%超) (該当: {win_cnt}頭)", help="F1位×arms1位、Fup5+×F1位など単勝・頭固定")
filter_target_axis = st.sidebar.checkbox(f"🛡️ 軸・連対狙い (複勝率55%超) (該当: {axis_cnt}頭)", help="ワイド・3連複1〜2列目の安定軸")
filter_target_himo = st.sidebar.checkbox(f"💣 紐穴狙い (6人気以下加速) (該当: {himo_cnt}頭)", help="3連複3列目・ワイドの高回収率穴馬")

st.sidebar.markdown("---")


# ==============================================================================
# ★ 左側サイドバー: 🎯 GTV馬抽出 ＆ 10列目印フィルター
# ==============================================================================
st.sidebar.markdown("### 🎯 GTV該当馬 抽出")
gtv_cnt = int(df['is_gtv_horse'].sum())
gtv_dirt_cnt = int((df['is_gtv_horse'] & df['track'].str.contains('ダ') & (df['人気'] >= 4)).sum())

filter_gtv_all = st.sidebar.checkbox(f"🎯 GTV該当馬すべて (該当: {gtv_cnt}頭)", help="単勝回収率86%・万能高期待値ロジック")
filter_gtv_dirt = st.sidebar.checkbox(f"🔥 GTVダート穴馬 (4人気以下) (該当: {gtv_dirt_cnt}頭)", help="ダート×4人気以下＝単勝回収率97%")

st.sidebar.markdown("### 🎯 印（10列目）抽出")

valid_marks_in_df = [m for m in df['印'].dropna().unique() if str(m).strip() not in ['', 'nan', 'None', '-', '0']]
has_any_mark_cnt = int(df['印'].isin(valid_marks_in_df).sum())

filter_mark_any = st.sidebar.checkbox(f"🎯 印付き馬すべて (該当: {has_any_mark_cnt}頭)")

has_c = 'C' in [str(m).upper() for m in valid_marks_in_df]
has_k = 'K' in [str(m).upper() for m in valid_marks_in_df]

c_m1, c_m2 = st.sidebar.columns(2)
with c_m1:
    filter_mark_c = st.checkbox("【C】印馬", value=False) if has_c else False
with c_m2:
    filter_mark_k = st.checkbox("【K】印馬", value=False) if has_k else False

other_marks = [m for m in valid_marks_in_df if str(m).upper() not in ['C', 'K']]
selected_other_marks = []
if other_marks:
    selected_other_marks = st.sidebar.multiselect("その他印選択", options=other_marks, default=[])

st.sidebar.markdown("---")


# ==============================================================================
# ★ 左側サイドバー: 🏛️ 厩舎黄金パターン抽出
# ==============================================================================
st.sidebar.markdown("### 🏛️ 厩舎黄金調教 抽出")
stable_pat_cnt = int(df['has_stable_pattern'].sum())
filter_stable_all = st.sidebar.checkbox(f"🏅 厩舎好走パターン該当馬 (該当: {stable_pat_cnt}頭)", help="杉山・中内田・矢作・木村哲などの調教黄金パターン")

st.sidebar.markdown("---")


# ==============================================================================
# ★ 左側サイドバー: 👑 黄金シナジー抽出
# ==============================================================================
st.sidebar.markdown("### 👑 黄金シナジー抽出")

iron_cnt = int(df['is_syn_iron'].sum())
high_cnt = int(df['is_syn_high'].sum())
fup_sakaro_cnt = int(df['is_syn_fup_sakaro'].sum())
f1_rap_cnt = int(df['is_syn_f1_rap'].sum())
bomb_cnt = int(df['is_syn_bomb'].sum())

syn_iron = st.sidebar.checkbox(f"💎 鉄板軸馬 (該当: {iron_cnt}頭)", help="複勝率 61.9% / 連対率 46.3%")
syn_high = st.sidebar.checkbox(f"🔥 高確率軸馬 (該当: {high_cnt}頭)", help="複勝率 54.8〜59.0%")
syn_fup_sakaro = st.sidebar.checkbox(f"✨ Fup2(5〜7点) × 坂路完全 (該当: {fup_sakaro_cnt}頭)", help="坂路完全加速かつFup高評価")
syn_f1_rap = st.sidebar.checkbox(f"🔥 SSS級・F1位 × 究極ラップ (該当: {f1_rap_cnt}頭)")
syn_bomb = st.sidebar.checkbox(f"💣 爆弾穴馬 (該当: {bomb_cnt}頭)")

st.sidebar.markdown("---")


# --- サイドバー: 📊 指数黄金パターン抽出 ---
st.sidebar.markdown("### 📊 指数黄金パターン抽出")
pat_s1 = st.sidebar.checkbox("⚡ S指数 1位 (スピード軸)")
pat_f1 = st.sidebar.checkbox("🥇 F指数 1位 (勝率22.7% / 複勝率53.4%)")
pat_f66 = st.sidebar.checkbox("🔥 F指数 66以上 (高信頼)")
pat_f1_arms3 = st.sidebar.checkbox("🎯 F指数1位 ＋ arms3位以内")
pat_fup_top = st.sidebar.checkbox("🌟 Fup 1位 (最上位評価・軸候補)")
pat_fup5 = st.sidebar.checkbox("✨ Fup 5点以上 (高期待値)")
pat_arms1 = st.sidebar.checkbox("🚀 arms指数 1位 (期待値ホース)")
pat_tua1 = st.sidebar.checkbox("🛡️ tua指数 1位 (堅実軸)")
pat_wood_top3 = st.sidebar.checkbox("⚡ ウッド5F 3位以内")


# ==============================================================================
# ★ 開催日時バッジ表示
# ==============================================================================
weekday_kanji = ["月", "火", "水", "木", "金", "土", "日"]
w_str = weekday_kanji[race_date.weekday()]
formatted_date_str = f"📅 開催日時: {race_date.year}年{race_date.month}月{race_date.day}日 ({w_str})"

st.markdown(f"<div class='date-header-badge'>{formatted_date_str}</div>", unsafe_allow_html=True)


# ==============================================================================
# ★ レース選択UI
# ==============================================================================
st.markdown("### 🎯 レース選択")

chosen_venue = st.radio(
    "開催場選択",
    options=existing_venues,
    index=existing_venues.index(st.session_state['active_venue']),
    horizontal=True,
    label_visibility="collapsed"
)
st.session_state['active_venue'] = chosen_venue

v_df = df[df['競馬場名'] == chosen_venue]
races_in_v = v_df[['race_uid', 'race_id', 'R番号', 'track', 'dist']].drop_duplicates('race_uid').sort_values('R番号')

race_options = {}
for _, r_row in races_in_v.iterrows():
    r_horses = df[df['race_uid'] == r_row['race_uid']]
    n_horses = len(r_horses)
    
    marks = []
    if (r_horses['target_win'] == True).any():
        marks.append("🥇")
    if (r_horses['target_axis'] == True).any():
        marks.append("🛡️")
    if (r_horses['target_himo'] == True).any():
        marks.append("💣")
    if (r_horses['has_stable_pattern'] == True).any():
        marks.append("🏅")
    if (r_horses['is_gtv_horse'] == True).any():
        marks.append("🎯")
        
    marks_str = f" {' '.join(marks)}" if marks else ""
    
    race_horse_marks = []
    for hm in r_horses['印'].dropna().unique():
        hm_s = str(hm).strip()
        if hm_s and hm_s not in ['', 'nan', 'None', '-', '0'] and hm_s not in race_horse_marks:
            race_horse_marks.append(hm_s)
    
    horse_marks_str = f" [{ ' '.join(race_horse_marks) }]" if race_horse_marks else ""

    lbl = f"{r_row['R番号']}R ({r_row['track']}{r_row['dist']}m / {n_horses}頭) [{r_row['race_id']}]{marks_str}{horse_marks_str}"
    race_options[r_row['race_uid']] = lbl

race_uid_list = list(race_options.keys())

venue_race_key = f"sel_race_uid_{chosen_venue}"
if venue_race_key not in st.session_state or st.session_state[venue_race_key] not in race_uid_list:
    st.session_state[venue_race_key] = race_uid_list[0]

selected_race_uid = st.selectbox(
    f"{chosen_venue}のレース選択",
    options=race_uid_list,
    format_func=lambda x: race_options[x],
    index=race_uid_list.index(st.session_state[venue_race_key]),
    key=venue_race_key,
    label_visibility="collapsed"
)

race_df = df[df['race_uid'] == selected_race_uid].copy().sort_values('馬番')
filtered_df = race_df.copy()

is_turf_race = bool(filtered_df['track'].str.contains('芝').any()) if not filtered_df.empty else False
is_dirt_race = bool(filtered_df['track'].str.contains('ダ').any()) if not filtered_df.empty else False


# --- 狙い目フィルタリング ---
if filter_target_win:
    filtered_df = filtered_df[filtered_df['target_win'] == True]

if filter_target_axis:
    filtered_df = filtered_df[filtered_df['target_axis'] == True]

if filter_target_himo:
    filtered_df = filtered_df[filtered_df['target_himo'] == True]

# --- 厩舎好走パターンフィルタリング ---
if filter_stable_all:
    filtered_df = filtered_df[filtered_df['has_stable_pattern'] == True]

# --- GTV馬フィルタリング処理 ---
if filter_gtv_all:
    filtered_df = filtered_df[filtered_df['is_gtv_horse'] == True]

if filter_gtv_dirt:
    filtered_df = filtered_df[filtered_df['is_gtv_horse'] & is_dirt_race & (filtered_df['人気'] >= 4)]

# --- 10列目印フィルタリング処理 ---
if filter_mark_any:
    filtered_df = filtered_df[filtered_df['印'].isin(valid_marks_in_df)]

if filter_mark_c:
    filtered_df = filtered_df[filtered_df['印'].str.upper() == 'C']

if filter_mark_k:
    filtered_df = filtered_df[filtered_df['印'].str.upper() == 'K']

if selected_other_marks:
    filtered_df = filtered_df[filtered_df['印'].isin(selected_other_marks)]

# --- シナジー・指数フィルタリング処理 ---
if syn_iron:
    filtered_df = filtered_df[filtered_df['is_syn_iron'] == True]

if syn_high:
    filtered_df = filtered_df[filtered_df['is_syn_high'] == True]

if syn_fup_sakaro:
    filtered_df = filtered_df[filtered_df['is_syn_fup_sakaro'] == True]

if syn_f1_rap:
    filtered_df = filtered_df[filtered_df['is_syn_f1_rap'] == True]

if syn_bomb:
    filtered_df = filtered_df[filtered_df['is_syn_bomb'] == True]

if pat_s1:
    filtered_df = filtered_df[filtered_df['S_rank'] == 1]

if pat_f1:
    filtered_df = filtered_df[filtered_df['F_rank'] == 1]

if pat_f66:
    filtered_df = filtered_df[filtered_df['F指数'] >= 66]

if pat_f1_arms3:
    filtered_df = filtered_df[(filtered_df['F_rank'] == 1) & (filtered_df['arms_rank'] <= 3)]

if pat_fup_top:
    filtered_df = filtered_df[filtered_df['Fup_rank'] == 1]

if pat_fup5:
    filtered_df = filtered_df[filtered_df['Fup'] >= 5]

if pat_arms1:
    filtered_df = filtered_df[filtered_df['arms_rank'] == 1]

if pat_tua1:
    filtered_df = filtered_df[filtered_df['tua_rank'] == 1]

if pat_wood_top3:
    filtered_df = filtered_df[filtered_df['wood_5F_rank'] <= 3]


st.markdown("<hr style='border-color:#30363d;margin-top:10px;margin-bottom:15px;'>", unsafe_allow_html=True)


# --- 検索バー ---
st.markdown("### 📋 出走馬カード（狙い目判定・上位5位色分け・厩舎調教完備）")

search_kw = st.text_input("🔍 馬名・調教師・騎手・父名で自由検索", placeholder="検索キーワードを入力...")
if search_kw:
    filtered_df = filtered_df[
        filtered_df['馬名'].str.contains(search_kw, na=False) |
        filtered_df['調教師'].str.contains(search_kw, na=False) |
        filtered_df['騎手'].str.contains(search_kw, na=False) |
        filtered_df['種牡馬'].str.contains(search_kw, na=False)
    ]


# --- 上部サマリーカウンター ---
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"<div class='metric-box'><div class='metric-label'>表示頭数</div><div class='metric-val'>{len(filtered_df)}頭</div></div>", unsafe_allow_html=True)
with c2:
    r_win_cnt = int((race_df['target_win'] == True).sum())
    st.markdown(f"<div class='metric-box'><div class='metric-label'>🥇 1着狙い</div><div class='metric-val'>{r_win_cnt}頭</div></div>", unsafe_allow_html=True)
with c3:
    r_axis_cnt = int((race_df['target_axis'] == True).sum())
    st.markdown(f"<div class='metric-box'><div class='metric-label'>🛡️ 軸・連対狙い</div><div class='metric-val'>{r_axis_cnt}頭</div></div>", unsafe_allow_html=True)
with c4:
    r_himo_cnt = int((race_df['target_himo'] == True).sum())
    st.markdown(f"<div class='metric-box'><div class='metric-label'>💣 紐穴狙い</div><div class='metric-val'>{r_himo_cnt}頭</div></div>", unsafe_allow_html=True)

st.markdown("<hr style='border-color:#30363d;margin-top:8px;margin-bottom:20px;'>", unsafe_allow_html=True)


# --- 出走馬カード一覧の描画 ---
if filtered_df.empty:
    st.info("条件に一致する馬が見つかりませんでした。")
else:
    for _, row in filtered_df.iterrows():
        s_rank = row.get('S_rank', 99)
        s_val = row.get('S指数', 0.0)
        f_rank = row.get('F_rank', 99)
        f_val = row.get('F指数', 0.0)
        arms_rank = row.get('arms_rank', 99)
        tua_rank = row.get('tua_rank', 99)
        fup_val = row.get('Fup', 0)
        fup_rank = row.get('Fup_rank', 99)
        pop_val = row.get('人気', 99)
        mark_val = row.get('印', '')
        sire_name = row.get('種牡馬', '')
        is_gtv = bool(row.get('is_gtv_horse', False))

        is_w_accel = bool(row.get('is_wood_accel', False))
        w_1f = row.get('wood_1F', 99.0)
        is_s_accel = bool(row.get('坂路_完全加速', False))
        
        # --- 豪華特注バッジ判定 ---
        badges = []
        
        # 1. 狙い目バッジ（最優先表示）
        if row.get('target_win', False):
            badges.append("<span class='badge-target-win'>🥇 1着狙い (勝率26%超)</span>")
        elif row.get('target_axis', False):
            badges.append("<span class='badge-target-axis'>🛡️ 軸・連対狙い (複勝率55%超)</span>")
            
        if row.get('target_himo', False):
            badges.append("<span class='badge-target-himo'>💣 紐穴狙い</span>")

        # 2. 厩舎黄金パターンバッジ
        stable_badges = get_stable_synergy_badges(row)
        badges.extend(stable_badges)

        # 3. GTV馬バッジ
        if is_gtv:
            if is_dirt_race and pd.notnull(pop_val) and pop_val >= 4:
                badges.append("<span class='badge-gtv-dirt'>🔥 GTVダート穴 (回収97%)</span>")
            else:
                badges.append("<span class='badge-gtv-normal'>🎯 GTV該当馬</span>")

        # 4. クッション値 × 種牡馬バイアス（芝レースのみ）
        cushion_badge_html = ""
        if is_turf_race and sire_name:
            cushion_badge_html = evaluate_sire_cushion(sire_name, current_band)
            if cushion_badge_html:
                badges.append(cushion_badge_html)

        # 5. 指数シナジーバッジ
        if row.get('is_syn_iron', False):
            badges.append("<span class='badge-synergy badge-iron'>💎 鉄板軸馬 (複勝率61.9%)</span>")
        elif row.get('is_syn_high', False):
            badges.append("<span class='badge-synergy badge-high'>🔥 高確率軸 (複勝率55%超)</span>")
            
        if row.get('is_syn_fup_sakaro', False):
            badges.append("<span class='badge-synergy badge-sakaro-fup'>✨ Fup坂路完全</span>")
            
        if fup_rank == 1 and fup_val >= 5:
            badges.append("<span class='badge-synergy badge-fup-top'>🌟 Fup 1位 (5点+)</span>")
        elif fup_rank == 1:
            badges.append("<span class='badge-synergy badge-fup-top'>👑 Fup 1位</span>")
        elif fup_val >= 5:
            badges.append("<span class='badge-synergy badge-fup-high'>⚡ Fup 5点+</span>")
            
        # S指数1位
        if s_rank == 1:
            badges.append("<span class='badge-synergy badge-s1'>⚡ S1位</span>")
            
        # F指数1位
        if f_rank == 1 and not row.get('is_syn_iron', False):
            badges.append("<span class='badge-synergy badge-f1'>👑 F1位</span>")
        elif f_val >= 66 and not (f_rank == 1 or (w_1f <= 11.5 and is_w_accel)):
            badges.append("<span class='badge-synergy badge-f1'>🔥 F66+</span>")
            
        # arms指数1位
        if arms_rank == 1:
            badges.append("<span class='badge-synergy badge-arms1'>🚀 arms1位</span>")
            
        # tua指数1位
        if tua_rank == 1:
            badges.append("<span class='badge-synergy badge-tua1'>🛡️ tua1位</span>")

        # 爆弾穴馬
        if row.get('is_syn_bomb', False):
            badges.append("<span class='badge-synergy badge-bomb'>💣 爆弾穴馬</span>")

        badges_html = " ".join(badges)
        
        # 10列目の印（C, K等）バッジ生成
        mark_badge_html = format_mark_badge(mark_val)

        # ウッド調教テキスト（最速タイム採用）
        has_wood = pd.notnull(row.get('wood_1F')) or pd.notnull(row.get('wood_5F')) or pd.notnull(row.get('wood_4F'))
        if has_wood:
            place = str(row.get('wood_place', ''))
            f5_str = f"{row['wood_5F']:.1f}s" if pd.notnull(row.get('wood_5F')) else "-s"
            
            accel = row.get('wood_accel', 0)
            if pd.notnull(accel) and accel != 0:
                accel_badge = f"<span class='badge-accel'>加速 +{accel:.1f}s</span>" if accel > 0 else f"<span class='badge-decel'>減速 {accel:.1f}s</span>"
            else:
                accel_badge = ""
                
            w_5f_rk = format_rank_badge(row.get('wood_5F_rank'))
            w_l4_rk = format_rank_badge(row.get('wood_Lap4_rank'))
            w_l3_rk = format_rank_badge(row.get('wood_Lap3_rank'))
            w_l2_rk = format_rank_badge(row.get('wood_Lap2_rank'))
            w_l1_rk = format_rank_badge(row.get('wood_Lap1_rank'))

            wood_info = f"{place} 5F: <strong>{f5_str}</strong> ({w_5f_rk}) {accel_badge} [ L4: {w_l4_rk} | L3: {w_l3_rk} | L2: {w_l2_rk} | L1: {w_l1_rk} ]"
        else:
            wood_info = "ウッド計測なし"

        # 坂路調教テキスト（全体4F最速タイム採用）
        has_sakaro = pd.notnull(row.get('坂路_4F')) or pd.notnull(row.get('坂路_1F'))
        if has_sakaro:
            s_accel_str = "<span class='badge-accel'>完全加速</span>" if is_s_accel else "<span class='badge-decel'>非加速</span>"
            s_4f_str = f"{row['坂路_4F']:.1f}s" if pd.notnull(row.get('坂路_4F')) else "-s"
            
            s_4f_rk = format_rank_badge(row.get('坂路_4F_rank'))
            s_l4_rk = format_rank_badge(row.get('坂路_Lap4_rank'))
            s_l3_rk = format_rank_badge(row.get('坂路_Lap3_rank'))
            s_l2_rk = format_rank_badge(row.get('坂路_Lap2_rank'))
            s_l1_rk = format_rank_badge(row.get('坂路_Lap1_rank'))

            sakaro_info = f"4F: <strong>{s_4f_str}</strong> ({s_4f_rk}) | {s_accel_str} [ L4: {s_l4_rk} | L3: {s_l3_rk} | L2: {s_l2_rk} | L1: {s_l1_rk} ]"
        else:
            sakaro_info = "坂路計測なし"

        u_no = row['馬番']
        umaban_str = f"{int(u_no)}番" if u_no != 99 and pd.notnull(u_no) else "番"
        pop_str = f"{int(row['人気'])} 番人気" if pd.notnull(row.get('人気')) else "- 番人気"
        
        # Fup数値 & 順位のカラーハイライト
        if pd.notnull(fup_val) and fup_val >= 5:
            fup_val_html = f"<span class='fup-high-val'>{int(fup_val)}点</span>"
        elif pd.notnull(fup_val):
            fup_val_html = f"<strong>{int(fup_val)}点</strong>"
        else:
            fup_val_html = "- 点"
            
        fup_rank_html = format_fup_rank_badge(fup_rank)
        
        # S指数・F指数・arms・tua 各順位バッジ生成（1〜5位まで色分け）
        s_badge = format_rank_badge(row.get('S_rank'))
        f_badge = format_rank_badge(row.get('F_rank'))
        arms_badge = format_rank_badge(row.get('arms_rank'))
        tua_badge = format_rank_badge(row.get('tua_rank'))

        mark_display = f" {mark_badge_html}" if mark_badge_html else ""
        
        card_html = f"<div class='horse-card'><div class='horse-card-header'><span class='horse-card-title'>{umaban_str} {row['馬名']}{mark_display}</span> {badges_html}</div><ul class='horse-card-list'><li><strong>陣営/血統</strong>: {row.get('調教師', '-')} / {row.get('騎手', '-')} / <strong>父: {row.get('種牡馬', '-')}</strong></li><li><strong>坂路調教</strong>: {sakaro_info}</li><li><strong>ウッド調教</strong>: {wood_info}</li><li><strong>能力指数</strong>: S: <strong>{row.get('S指数', 0.0)}</strong> ({s_badge}) | F: <strong>{row.get('F指数', 0.0)}</strong> ({f_badge}) | ARMS: <strong>{row.get('arms', 0.0)}</strong> ({arms_badge}) | TUA: <strong>{row.get('tua', 0.0)}</strong> ({tua_badge})</li><li><strong>Fup</strong>: {fup_val_html} ({fup_rank_html}) | <strong>人気</strong>: {pop_str}</li></ul></div>"

        st.markdown(card_html, unsafe_allow_html=True)
