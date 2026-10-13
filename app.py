import csv
import datetime
import glob
import io
import os
import re
import numpy as np
import pandas as pd
import streamlit as st

# ==============================================================================
# 競馬予想10 クッション値Vr 完全統合Webアプリケーション
# 【全11指数完全統合・10月12日データ直結・クッション値データブック完全連動版】
# ==============================================================================

st.set_page_config(
    page_title="競馬予想10 クッション値Vr - 全11指数完全統合システム",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    .metric-container { display: flex; justify-content: space-around; background-color: #161b22; padding: 14px; border-radius: 10px; margin-bottom: 18px; border: 1px solid #30363d; }
    .date-header-badge { display: inline-flex; align-items: center; gap: 8px; background: linear-gradient(135deg, #1f2937 0%, #111827 100%); border: 1px solid #3b82f6; padding: 6px 16px; border-radius: 20px; color: #60a5fa; font-size: 14.5px; font-weight: bold; margin-bottom: 12px; }
    .race-type-banner { padding: 12px 18px; border-radius: 8px; margin-bottom: 14px; font-size: 15px; font-weight: bold; display: flex; align-items: center; justify-content: space-between; }
    .race-type-solid { background: linear-gradient(135deg, #064e3b 0%, #047857 100%); color: #ecfdf5; border: 1px solid #34d399; }
    .race-type-bonus { background: linear-gradient(135deg, #7c2d12 0%, #b45309 50%, #d97706 100%); color: #fef3c7; border: 2px solid #fde68a; box-shadow: 0 0 10px rgba(245, 158, 11, 0.5); }
    .recom-panel-go { background: linear-gradient(135deg, #111827 0%, #1f2937 100%); border: 2px solid #10b981; border-radius: 10px; padding: 16px 20px; margin-bottom: 20px; }
    .recom-title-go { font-size: 16px; font-weight: bold; color: #34d399; margin-bottom: 12px; border-bottom: 1px solid #374151; padding-bottom: 5px; }
    .recom-row { margin-bottom: 8px; font-size: 14.5px; line-height: 1.6; }
    .recom-block { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; padding: 10px 14px; margin-bottom: 10px; }
    .recom-val-num { color: #ffffff; font-weight: bold; font-size: 15.5px; letter-spacing: 1px; }
    .horse-card { background-color: #161e2e; border-left: 5px solid #238636; padding: 14px 18px; border-radius: 8px; margin-bottom: 14px; border-top: 1px solid #30363d; border-right: 1px solid #30363d; border-bottom: 1px solid #30363d; }
    .horse-card-header { display: flex; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 8px; }
    .horse-card-title { font-size: 18px; font-weight: bold; color: #ffffff; }
    .race-badge-title { background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); color: #ffffff; font-weight: bold; font-size: 14px; padding: 2px 10px; border-radius: 6px; border: 1px solid #93c5fd; margin-right: 6px; }
    .horse-card-list { list-style-type: none; padding-left: 0; margin: 0; }
    .horse-card-list li { font-size: 13.5px; color: #c9d1d9; margin-bottom: 5px; line-height: 1.6; }
    .horse-card-list li::before { content: "• "; color: #58a6ff; font-weight: bold; }
    
    .badge-mark-gtv { background: linear-gradient(135deg, #b45309 0%, #d97706 100%); color: #ffffff; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #fde68a; }
    .badge-accel-on { background: linear-gradient(135deg, #059669 0%, #10b981 100%); color: #ffffff; font-weight: bold; font-size: 11.5px; padding: 2px 7px; border-radius: 4px; border: 1px solid #34d399; }
    .badge-style-senko { background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: #ffffff; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; }
    .badge-style-sashi { background: linear-gradient(135deg, #059669 0%, #047857 100%); color: #ffffff; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; }
    .badge-style-nige { background: linear-gradient(135deg, #e11d48 0%, #be123c 100%); color: #ffffff; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; }
    .badge-style-other { background-color: #374151; color: #e5e7eb; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; }

    .val-rank1-gold { color: #1a1000; background-color: #fcd34d; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #f59e0b; }
    .val-top-rank { color: #ffffff; background-color: #ea580c; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #fb923c; }
    .val-sub-rank { color: #083344; background-color: #38bdf8; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #0284c7; }
    .val-normal { color: #cbd5e1; font-weight: normal; }

    .badge-synergy { display: inline-flex; align-items: center; padding: 2px 8px; border-radius: 6px; font-weight: bold; font-size: 11.5px; }
    .badge-iron { background: linear-gradient(135deg, #FFE259 0%, #FFA751 100%); color: #1a1000; border: 1px solid #FFF275; }
    .badge-bomb { background: linear-gradient(135deg, #EB3349 0%, #F45C43 100%); color: #ffffff; border: 1px solid #FFA07A; }
    .badge-cushion-fit { display: inline-flex; align-items: center; background: linear-gradient(135deg, #059669 0%, #10b981 100%); color: #ffffff; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #34d399; }
    .badge-cushion-danger { display: inline-flex; align-items: center; background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%); color: #ffffff; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #f87171; }
    .badge-mark-honmei { display: inline-flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%); color: #ffffff; font-size: 16px; font-weight: 900; width: 30px; height: 30px; border-radius: 6px; border: 1.5px solid #fca5a5; margin-right: 6px; }
    .badge-mark-taikou { display: inline-flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: #ffffff; font-size: 16px; font-weight: 900; width: 30px; height: 30px; border-radius: 6px; border: 1.5px solid #93c5fd; margin-right: 6px; }
    .badge-mark-tanana { display: inline-flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #059669 0%, #047857 100%); color: #ffffff; font-size: 16px; font-weight: 900; width: 30px; height: 30px; border-radius: 6px; border: 1.5px solid #6ee7b7; margin-right: 6px; }
    .badge-mark-himo { display: inline-flex; align-items: center; justify-content: center; background-color: #374151; color: #f3f4f6; font-size: 14.5px; font-weight: bold; width: 30px; height: 30px; border-radius: 6px; border: 1px solid #6b7280; margin-right: 6px; }
    .badge-mark-ana { display: inline-flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #d97706 0%, #b45309 100%); color: #ffffff; font-size: 16px; font-weight: 900; width: 30px; height: 30px; border-radius: 6px; border: 1px solid #fde68a; margin-right: 6px; }
</style>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# クッション値＆種牡馬マトリクス定数
# ==============================================================================
SIRE_COURSE_MATRIX_TOP = {
    ('阪神', '1800', 'キズナ', '9.5-9.9 標準高'): '最重要特注 (勝19.6%/単421%)',
    ('東京', '1600', 'エピファネイア', '9.5-9.9 標準高'): '最重要特注 (勝13.3%/単277%)',
    ('東京', '1400', 'モーリス', '9.5-9.9 標準高'): '最重要特注 (勝10.1%/単408%)',
    ('東京', '1800', 'ディープインパクト', '9.5-9.9 標準高'): '最重要特注 (勝15.8%/単228%)',
    ('東京', '2000', 'キズナ', '8.6-9.4 やや低'): '最重要特注 (勝19.7%/単200%)',
    ('中京', '2000', 'ディープインパクト', '8.6-9.4 やや低'): '最重要特注 (勝18.0%/単178%)',
    ('東京', '1600', 'イスラボニータ', '8.6-9.4 やや低'): '最重要特注 (勝10.5%/単350%)',
    ('東京', '2000', 'エピファネイア', '8.6-9.4 やや低'): '最重要特注 (勝15.3%/単149%)',
    ('函館', '1800', 'キズナ', '≤8.5低'): '最重要特注 (勝17.7%/単143%)',
    ('小倉', '1200', 'ダイワメジャー', '9.5-9.9 標準高'): '最重要特注 (勝13.6%/単173%)',
    ('札幌', '2000', 'オルフェーヴル', '≤8.5低'): '最重要特注 (勝15.8%/単136%)',
    ('東京', '1400', 'ロードカナロア', '8.6-9.4 やや低'): '最重要特注 (勝15.6%/単123%)',
    ('阪神', '1600', 'ルーラーシップ', '8.6-9.4 やや低'): '最重要特注 (勝20.0%/単156%)',
    ('東京', '1600', 'モーリス', '9.5-9.9 標準高'): '最重要特注 (勝11.1%/単100%)',
    ('阪神', '2000', 'キズナ', '8.6-9.4 やや低'): '最重要特注 (勝11.8%/単152%)',
    ('東京', '1600', 'スクリーンヒーロー', '8.6-9.4 やや低'): '最重要特注 (勝9.9%/単72%)',
    ('小倉', '1200', 'ビッグアーサー', '8.6-9.4 やや低'): '最重要特注 (勝12.2%/単131%)',
    ('中京', '1600', 'ロードカナロア', '10.0-10.4高'): '最重要特注 (勝14.8%/単133%)',
    ('福島', '1200', 'ビッグアーサー', '8.6-9.4 やや低'): '最重要特注 (勝13.2%/単87%)',
    ('札幌', '1200', 'ロードカナロア', '≤8.5低'): '最重要特注 (勝15.0%/単121%)',
}

SIRE_COURSE_MATRIX_DANGER = {
    ('中山', '2000', 'ダノンバラード', '9.5-9.9 標準高'): '超危険 (複勝率0%)',
    ('東京', '2000', 'ルーラーシップ', '9.5-9.9 標準高'): '危険 (複勝率9.1%)',
    ('小倉', '1200', 'ジャスタウェイ', '8.6-9.4 やや低'): '超危険 (複勝率2.9%)',
    ('東京', '1400', 'シルバーステート', '8.6-9.4 やや低'): '超危険 (複勝率4.7%)',
    ('東京', '1600', 'ゴールドシップ', '8.6-9.4 やや低'): '超危険 (複勝率4.5%)',
    ('小倉', '1200', 'ヴィクトワールピサ', '8.6-9.4 やや低'): '超危険 (複勝率4.8%)',
    ('東京', '1800', 'ルーラーシップ', '9.5-9.9 標準高'): '危険 (複勝率10.5%)',
    ('阪神', '2000', 'ゴールドシップ', '8.6-9.4 やや低'): '危険 (複勝率10.0%)',
    ('東京', '1600', 'エイシンフラッシュ', '8.6-9.4 やや低'): '危険 (複勝率7.3%)',
    ('東京', '2000', 'オルフェーヴル', '8.6-9.4 やや低'): '危険 (複勝率13.2%)',
    ('福島', '2000', 'ルーラーシップ', '8.6-9.4 やや低'): '超危険 (複勝率4.7%)',
    ('新潟', '1400', 'リオンディーズ', '8.6-9.4 やや低'): '危険 (複勝率6.7%)',
    ('東京', '2400', 'ゴールドシップ', '9.5-9.9 標準高'): '危険 (複勝率11.1%)',
    ('小倉', '1800', 'ルーラーシップ', '9.5-9.9 標準高'): '危険 (複勝率10.0%)',
    ('阪神', '1800', 'ハービンジャー', '9.5-9.9 標準高'): '危険 (複勝率10.0%)',
    ('東京', '1600', 'サトノクラウン', '8.6-9.4 やや低'): '危険 (複勝率9.7%)',
    ('福島', '1200', 'マツリダゴッホ', '8.6-9.4 やや低'): '危険 (複勝率5.9%)',
    ('東京', '1600', 'シルバーステート', '9.5-9.9 標準高'): '危険 (複勝率8.9%)',
    ('福島', '1200', 'カレンブラックヒル', '8.6-9.4 やや低'): '危険 (複勝率9.7%)',
    ('中京', '2000', 'オルフェーヴル', '8.6-9.4 やや低'): '危険 (複勝率15.2%)',
}

def clean_name(name):
    if pd.isnull(name): return ''
    return str(name).strip().replace('*', '').replace('$', '').replace(' ', '')

def get_cushion_band(venue, c_val):
    c = float(c_val)
    if c <= 8.5: return '≤8.5低'
    elif c <= 9.4: return '8.6-9.4 やや低'
    elif c <= 9.9: return '9.5-9.9 標準高'
    elif c <= 10.4: return '10.0-10.4高'
    else: return '≥10.5 超高'

def get_current_cushion_bin_name(c_val):
    c = float(c_val)
    if c < 8.0: return '7以下'
    elif c < 9.0: return '8台'
    elif c < 10.0: return '9台'
    elif c < 11.0: return '10台'
    else: return '11以上'

def evaluate_sire_cushion(sire_name, venue, dist_str, band_str):
    sire = clean_name(sire_name)
    dist = re.sub(r'\D', '', str(dist_str))
    v = str(venue).strip()
    b = str(band_str).strip()
    key = (v, dist, sire, b)
    if key in SIRE_COURSE_MATRIX_TOP:
        return f"<span class='badge-cushion-fit'>🟢 {sire}特注 ({SIRE_COURSE_MATRIX_TOP[key]})</span>"
    if key in SIRE_COURSE_MATRIX_DANGER:
        return f"<span class='badge-cushion-danger'>⚠️ {sire}危険 ({SIRE_COURSE_MATRIX_DANGER[key]})</span>"
    if '≥10.5' in b or '10.5' in b:
        if sire in ['エピファネイア', 'キタサンブラック', 'イスラボニータ']:
            return f"<span class='badge-cushion-fit'>🟢 超高クッション特注 ({sire})</span>"
        if sire in ['キングカメハメハ', 'ビッグアーサー', 'レイデオロ', 'スワーヴリチャード', 'サートゥルナーリア', 'ゴールドシップ']:
            return f"<span class='badge-cushion-danger'>⚠️ 超高クッション危険 ({sire})</span>"
    return ""

def infer_track_type(venue, dist, r_no):
    # JRA主要コースの芝/ダート自動推定
    d = int(dist)
    if d in [1000, 1150, 1200, 1300, 1400, 1700, 1800, 1900, 2100, 2400]:
        if d in [1300, 1700, 1900, 2100, 1150]:
            return 'ダ'
    if d >= 2800:
        return '障'
    # 東京・京都特有
    if venue == '東京':
        if d in [1300, 2100]: return 'ダ'
        if d == 1400 and r_no in [1, 2]: return 'ダ'  # 一般的な朝ダート1400
    if venue == '京都':
        if d in [1200, 1400, 1800, 1900] and r_no in [1, 2, 4]: return 'ダ'
    return '芝'

# ==============================================================================
# ★ データロード：全11指数統合CSV
# ==============================================================================
@st.cache_data
def load_all_index_csv():
    target_files = ['2026_全11指数統合_出馬表.csv', 'data/2026_全11指数統合_出馬表.csv']
    chosen = None
    for f in target_files:
        if os.path.exists(f):
            chosen = f
            break
    if chosen is None:
        matched = glob.glob('*全11指数*.csv') or glob.glob('data/*全11指数*.csv')
        if matched: chosen = matched[0]
    
    if chosen is None:
        return pd.DataFrame()

    encodings = ['cp932', 'shift-jis', 'utf-8-sig', 'utf-8']
    for enc in encodings:
        try:
            df = pd.read_csv(chosen, encoding=enc, low_memory=False)
            if not df.empty: return df
        except Exception:
            continue
    return pd.DataFrame()

raw_df = load_all_index_csv()

if raw_df.empty:
    st.error("⚠️ 『2026_全11指数統合_出馬表.csv』が見つかりません。作業フォルダに配置してください。")
    st.stop()

# 日付選択 (デフォルト: 1012 = 10月12日)
available_dates = sorted(raw_df['日付'].dropna().unique().tolist(), reverse=True)
default_date_idx = available_dates.index(1012) if 1012 in available_dates else 0

st.sidebar.markdown('### 📅 対象開催日選択')
sel_date = st.sidebar.selectbox('開催日', available_dates, index=default_date_idx)
df_date = raw_df[raw_df['日付'] == sel_date].copy()

# ==============================================================================
# データクレンジング & 全11指数列マッピング
# ==============================================================================
venue_dict = {'東': '東京', '中': '中山', '京': '京都', '阪': '阪神', '名': '中京', '小': '小倉', '新': '新潟', '福': '福島', '函': '函館', '札': '札幌'}

def parse_basho_r(val):
    s = str(val).strip()
    m = re.match(r'([^\d]+)(\d+)', s)
    if m:
        v_short = m.group(1)
        r_num = int(m.group(2))
        return venue_dict.get(v_short, v_short), r_num
    return 'その他', 99

parsed_vr = df_date['場所R'].apply(parse_basho_r)
df_date['競馬場名'] = [p[0] for p in parsed_vr]
df_date['R番号'] = [p[1] for p in parsed_vr]
df_date['race_uid'] = df_date['場所R']
df_date['dist'] = pd.to_numeric(df_date['距離'], errors='coerce').fillna(1600).astype(int)
df_date['track'] = df_date.apply(lambda r: infer_track_type(r['競馬場名'], r['dist'], r['R番号']), axis=1)

# 数値化
idx_cols = ['Fup2', 'F', 'ARM', 'TUA', 'S', '坂路調', '坂路血', '時計血', 'コース連', '血統連', 'バランス']
for c in idx_cols:
    df_date[c] = pd.to_numeric(df_date[c], errors='coerce').fillna(0.0)
    rk_c = c + '順位'
    df_date[rk_c] = pd.to_numeric(df_date[rk_c], errors='coerce').fillna(99).astype(int)

df_date['人気'] = pd.to_numeric(df_date['人気順位'], errors='coerce').fillna(99).astype(int)
df_date['馬番'] = pd.to_numeric(df_date['馬番'], errors='coerce').fillna(99).astype(int)

# 枠番計算
total_horses = df_date.groupby('race_uid')['馬番'].transform('count')
def calc_waku(u, total):
    if total <= 8: return u
    base = total // 8
    rem = total % 8
    waku_counts = [base + (1 if 8 - i <= rem else 0) for i in range(8)]
    curr = 1
    for w_idx, cnt in enumerate(waku_counts, start=1):
        if curr <= u < curr + cnt: return w_idx
        curr += cnt
    return 8

df_date['枠番'] = [calc_waku(u, t) for u, t in zip(df_date['馬番'], total_horses)]

# 脚質
def infer_style(row):
    s1 = str(row.get('前脚質', '')).strip()
    if '逃' in s1: return '逃げ'
    if '先' in s1: return '先行'
    if '差' in s1: return '差し'
    if '追' in s1: return '追込'
    if '後' in s1: return '後方'
    # S順位/F順位からの補完
    if row['S順位'] <= 2: return '先行'
    if row['F順位'] <= 2 and row['S順位'] >= 6: return '差し'
    return '中団'

df_date['脚質'] = df_date.apply(infer_style, axis=1)

# ==============================================================================
# ★ 究極の解析ロジック（SSS級・黄金シナジー・穴トリガー）
# ==============================================================================
# SSS級・絶対神域
df_date['is_sss_level'] = (df_date['F'] >= 70) & (df_date['ARM'] >= 120) & (df_date['TUA'] >= 200)

# 指数の四冠馬
df_date['is_four_crown'] = (df_date['F順位'] <= 2) & (df_date['Fup2順位'] <= 2) & (df_date['ARM順位'] <= 2) & (df_date['TUA順位'] <= 2)

# 鉄板相手候補 (F1位 + ARM3位内 + TUA3位内)
df_date['is_iron_partner'] = (df_date['F順位'] == 1) & (df_date['ARM順位'] <= 3) & (df_date['TUA順位'] <= 3)

# コース連動・血統連動シナジー
df_date['is_course_syn'] = (df_date['コース連順位'] <= 3) & (df_date['F順位'] <= 3)
df_date['is_blood_syn'] = (df_date['血統連順位'] <= 3) & (df_date['S順位'] <= 3)

# 10番人気以下・爆弾穴馬
df_date['is_pop10_bomb'] = (df_date['人気'] >= 10) & (
    ((df_date['Fup2'] >= 4) & (df_date['S順位'] <= 5)) |
    ((df_date['F順位'] <= 5) & (df_date['ARM順位'] <= 5))
)

# 地雷判定
df_date['is_fup1_trap'] = (df_date['Fup2'] == 1) & (df_date['人気'] <= 3) & (~df_date['is_sss_level']) & (df_date['F'] < 72)

# 1着狙い・連対軸
df_date['target_win'] = (
    df_date['is_sss_level'] |
    (df_date['is_iron_partner'] & (df_date['Fup2'] >= 4) & (df_date['枠番'] <= 6)) |
    (df_date['F順位'] == 1) & (df_date['F'] >= 65) & (df_date['Fup2'] >= 5) & (df_date['枠番'] <= 6)
) & (~df_date['is_fup1_trap'])

df_date['target_axis'] = (
    df_date['is_four_crown'] |
    df_date['is_iron_partner'] |
    df_date['is_course_syn'] |
    ((df_date['Fup2'] >= 5) & (df_date['ARM順位'] <= 3)) |
    ((df_date['F順位'] <= 2) & (df_date['S順位'] <= 3))
) & (~df_date['target_win']) & (~df_date['is_fup1_trap'])

df_date['target_himo'] = (
    df_date['is_pop10_bomb'] |
    df_date['is_blood_syn'] |
    (df_date['バランス順位'] <= 3) |
    ((df_date['TUA'] >= 170) & (df_date['人気'] >= 6))
) & (~df_date['target_win']) & (~df_date['target_axis'])

# ==============================================================================
# クッション値設定 (サイドバー)
# ==============================================================================
st.sidebar.markdown('---')
st.sidebar.markdown('### 🏟️ クッション値設定')
default_cushions = {'東京': 9.3, '京都': 10.0, '阪神': 9.4, '中山': 9.6, '中京': 9.6}

cur_venues = df_date['競馬場名'].unique().tolist()
active_venue = st.sidebar.selectbox('開催場', cur_venues, index=0)
c_val = st.sidebar.number_input(f'芝クッション値 ({active_venue})', min_value=7.0, max_value=12.0, value=float(default_cushions.get(active_venue, 9.5)), step=0.1)

band_str = get_cushion_band(active_venue, c_val)
bin_name = get_current_cushion_bin_name(c_val)

df_date['cushion_badge_raw'] = df_date.apply(
    lambda r: evaluate_sire_cushion(r['種牡馬'], r['競馬場名'], r['dist'], band_str) if r['track'] == '芝' else '', axis=1
)
df_date['is_cushion_fit'] = df_date['cushion_badge_raw'].str.contains('特注')
df_date['is_cushion_danger'] = df_date['cushion_badge_raw'].str.contains('危険')

# ==============================================================================
# メイン画面ヘッダー
# ==============================================================================
date_obj = datetime.date(2026, 10, 12) if sel_date == 1012 else datetime.date.today()
st.markdown(
    f"<div class='date-header-badge'>📅 開催日: 2026年10月12日 (月・祝) | "
    f"{active_venue} 芝クッション値: {c_val} ({bin_name}: {band_str}) | 全11指数解析稼働中</div>",
    unsafe_allow_html=True,
)

# レース選択
v_df = df_date[df_date['競馬場名'] == active_venue]
races_in_v = v_df[['race_uid', 'R番号', 'track', 'dist']].drop_duplicates('race_uid').sort_values('R番号')

race_options = {}
for _, r_row in races_in_v.iterrows():
    r_horses = df_date[df_date['race_uid'] == r_row['race_uid']]
    is_bonus = bool(((r_horses['F順位'] <= 3) & (r_horses['ARM順位'] <= 3) & (r_horses['TUA順位'] <= 3)).sum() >= 3)
    f1_val = r_horses[r_horses['F順位'] == 1]['F'].values[0] if (r_horses['F順位'] == 1).any() else 0
    tag = '👑ボーナス' if is_bonus else ('🎯狙' if f1_val >= 60 else '🔥波乱')
    lbl = f"{tag} {r_row['R番号']}R ({r_row['track']}{r_row['dist']}m) [{len(r_horses)}頭]"
    race_options[r_row['race_uid']] = lbl

sel_race_uid = st.selectbox('レース選択', list(race_options.keys()), format_func=lambda x: race_options[x])
race_df = df_date[df_date['race_uid'] == sel_race_uid].copy()

# ==============================================================================
# 推奨馬・買い目生成
# ==============================================================================
win_cands = race_df[race_df['target_win']]
pick_win = win_cands.sort_values(['F', 'ARM'], ascending=[False, False]).iloc[0] if not win_cands.empty else race_df.sort_values(['F順位', 'ARM順位']).iloc[0]

axis_cands = race_df[(race_df['馬番'] != pick_win['馬番']) & (race_df['target_axis'] | (race_df['F順位'] <= 3))]
pick_axis = axis_cands.sort_values(['Fup2', 'ARM'], ascending=[False, False]).iloc[0] if not axis_cands.empty else race_df[race_df['馬番'] != pick_win['馬番']].iloc[0]

himo_cands = race_df[(race_df['馬番'] != pick_win['馬番']) & (race_df['馬番'] != pick_axis['馬番']) & race_df['target_himo']]
pick_himo = himo_cands.sort_values('TUA', ascending=False).iloc[0] if not himo_cands.empty else None

danger_cands = race_df[race_df['is_fup1_trap'] | race_df['is_cushion_danger']]
pick_danger = danger_cands.iloc[0] if not danger_cands.empty else None

# フォーメーション馬番リスト
rec_c1 = [int(pick_win['馬番'])]
rec_c2 = [int(pick_win['馬番']), int(pick_axis['馬番'])]
for u in race_df.sort_values(['F順位', 'ARM順位'])['馬番'].tolist():
    if int(u) not in rec_c2: rec_c2.append(int(u))
    if len(rec_c2) >= 4: break

rec_c3 = list(rec_c2)
if pick_himo is not None and int(pick_himo['馬番']) not in rec_c3:
    rec_c3.append(int(pick_himo['馬番']))
for u in race_df.sort_values(['TUA順位', 'バランス順位'])['馬番'].tolist():
    if int(u) not in rec_c3: rec_c3.append(int(u))
    if len(rec_c3) >= 7: break

bet_marks = {int(pick_win['馬番']): "<span class='badge-mark-honmei'>◎</span>"}
if int(pick_axis['馬番']) != int(pick_win['馬番']):
    bet_marks[int(pick_axis['馬番'])] = "<span class='badge-mark-taikou'>◯</span>"
for u in rec_c2:
    if u not in bet_marks: bet_marks[u] = "<span class='badge-mark-tanana'>▲</span>"
for u in rec_c3:
    if u not in bet_marks: bet_marks[u] = "<span class='badge-mark-himo'>△</span>"
if pick_himo is not None and int(pick_himo['馬番']) not in bet_marks:
    bet_marks[int(pick_himo['馬番'])] = "<span class='badge-mark-ana'>★</span>"

is_bonus_cur = bool(((race_df['F順位'] <= 3) & (race_df['ARM順位'] <= 3) & (race_df['TUA順位'] <= 3)).sum() >= 3)
wave_label = '【👑 ボーナスレース】' if is_bonus_cur else '【標準・堅調】'

st.markdown(f"<div class='race-type-banner race-type-solid'><div>🎯 レース判定: {wave_label}</div><div>推奨券種: 3連複フォーメーション / 単勝 / ワイド</div></div>", unsafe_allow_html=True)

himo_text = f"{int(pick_himo['馬番'])}番 {pick_himo['馬名']} (TUA:{pick_himo['TUA']:.1f} / {pick_himo['人気']}人気)" if pick_himo is not None else "上位人気均衡"
danger_text = f"{int(pick_danger['馬番'])}番 {pick_danger['馬名']} (消し理由: Fup1罠 / クッション値危険)" if pick_danger is not None else "該当なし"

st.markdown(
    f"<div class='recom-panel-go'><div class='recom-title-go'>📋 推奨馬ピックアップ（全11指数統合ロジック）</div>"
    f"<div class='recom-row'>🥇 <strong>1着狙い</strong>: <span class='recom-val-num'>{int(pick_win['馬番'])}番 {pick_win['馬名']}</span>（F:{pick_win['F']:.0f} / F{int(pick_win['F順位'])}位 / 枠{int(pick_win['枠番'])})</div>"
    f"<div class='recom-row'>🛡️ <strong>軸・連対狙い</strong>: <span class='recom-val-num'>{int(pick_axis['馬番'])}番 {pick_axis['馬名']}</span>（Fup:{int(pick_axis['Fup2'])}点 / arms:{pick_axis['ARM']:.0f}）</div>"
    f"<div class='recom-row'>💣 <strong>特注紐穴</strong>: <span class='recom-val-num'>{himo_text}</span></div>"
    f"<div class='recom-row'>⚠️ <strong>危険な人気馬</strong>: {danger_text}</div></div>",
    unsafe_allow_html=True,
)

st.markdown(
    f"<div class='recom-panel-go'><div class='recom-title-go'>🎫 推奨買い目フォーメーション</div>"
    f"<div class='recom-block'><strong>3連複</strong>: 1列目[{', '.join(str(x) for x in rec_c1)}] → 2列目[{', '.join(str(x) for x in rec_c2)}] → 3列目[{', '.join(str(x) for x in rec_c3)}]</div>"
    f"<div class='recom-block'><strong>単勝</strong>: {int(pick_win['馬番'])}番 / <strong>ワイド</strong>: {int(pick_win['馬番'])} - {int(pick_axis['馬番'])}, {int(pick_himo['馬番']) if pick_himo is not None else ''}</div></div>",
    unsafe_allow_html=True,
)

# ==============================================================================
# ★ 出走馬詳細カルテ（全11指数完全展開）
# ==============================================================================
st.markdown("### 🏇 出走馬カルテ（全11指数・調教・適性完全表示）")

sort_opt = st.selectbox(
    "🔄 カルテ並び替え",
    ['馬番順', 'F指数順', 'Fup点数順', 'ARMS指数順', 'TUA指数順', 'S指数順', 'コース連動順', '血統連動順'],
    index=0
)

disp_df = race_df.copy()
if sort_opt == '馬番順': disp_df = disp_df.sort_values('馬番')
elif sort_opt == 'F指数順': disp_df = disp_df.sort_values(['F順位', 'F'], ascending=[True, False])
elif sort_opt == 'Fup点数順': disp_df = disp_df.sort_values(['Fup2', 'Fup2順位'], ascending=[False, True])
elif sort_opt == 'ARMS指数順': disp_df = disp_df.sort_values(['ARM順位', 'ARM'], ascending=[True, False])
elif sort_opt == 'TUA指数順': disp_df = disp_df.sort_values(['TUA順位', 'TUA'], ascending=[True, False])
elif sort_opt == 'S指数順': disp_df = disp_df.sort_values(['S順位', 'S'], ascending=[True, False])
elif sort_opt == 'コース連動順': disp_df = disp_df.sort_values(['コース連順位', 'コース連'], ascending=[True, False])
elif sort_opt == '血統連動順': disp_df = disp_df.sort_values(['血統連順位', '血統連'], ascending=[True, False])

def fmt_badge(val, rank):
    v = f"{float(val):.0f}"
    r = int(rank)
    if r == 1: return f"<span class='val-rank1-gold'>{v}</span>(1位)"
    elif r <= 3: return f"<span class='val-top-rank'>{v}</span>({r}位)"
    elif r <= 5: return f"<span class='val-sub-rank'>{v}</span>({r}位)"
    return f"<span class='val-normal'>{v}</span>({r}位)"

for _, h in disp_df.iterrows():
    u_no = int(h['馬番'])
    mark_icon = bet_marks.get(u_no, '')
    
    badges = []
    if mark_icon: badges.append(mark_icon)
    if h['target_win']: badges.append("<span class='badge-synergy badge-iron'>🥇 1着本線</span>")
    if h['target_axis']: badges.append("<span class='badge-synergy badge-iron'>🛡️ 軸候補</span>")
    if h['is_sss_level']: badges.append("<span class='badge-synergy badge-iron'>🔥 SSS級神域</span>")
    if h['is_pop10_bomb']: badges.append("<span class='badge-synergy badge-bomb'>💣 特大爆弾穴馬</span>")
    if h['is_course_syn']: badges.append("<span class='badge-accel-on'>⚡ コース×F連動</span>")
    if h['is_blood_syn']: badges.append("<span class='badge-accel-on'>⚡ 血統×S先行連動</span>")
    if h['is_fup1_trap']: badges.append("<span class='badge-cushion-danger'>⚠️ Fup1地雷罠</span>")
    if h.get('cushion_badge_raw'): badges.append(str(h['cushion_badge_raw']))

    badges_html = " ".join([b for b in badges if b])
    
    st.markdown(
        f"<div class='horse-card'>"
        f"<div class='horse-card-header'>"
        f"<span class='race-badge-title'>{u_no}番</span>"
        f"<span class='horse-card-title'>{h['馬名']}</span>"
        f"<span style='color:#94a3b8; font-size:13.5px;'>（{h['人気']}番人気 / 枠{int(h['枠番'])} / {h.get('騎手','')}騎手 / {h.get('調教師','')}厩舎 / 脚質: {h.get('脚質','')}）</span>"
        f"</div>"
        f"<div style='margin-bottom: 8px;'>{badges_html}</div>"
        f"<ul class='horse-card-list'>"
        f"<li><strong>能力・展開4指数</strong>: F指数: {fmt_badge(h['F'], h['F順位'])} | S指数: {fmt_badge(h['S'], h['S順位'])} | Fup2点数: <strong style='color:#fcd34d;'>{int(h['Fup2'])}点</strong>({int(h['Fup2順位'])}位)</li>"
        f"<li><strong>総合・妙味3指数</strong>: ARMS指数: {fmt_badge(h['ARM'], h['ARM順位'])} | TUA指数: {fmt_badge(h['TUA'], h['TUA順位'])} | バランス指数: {fmt_badge(h['バランス'], h['バランス順位'])}</li>"
        f"<li><strong>調教・適性5指数</strong>: コース連動: {fmt_badge(h['コース連'], h['コース連順位'])} | 血統連動: {fmt_badge(h['血統連'], h['血統連順位'])} | 坂路調教: {fmt_badge(h['坂路調'], h['坂路調順位'])} | 坂路血統: {fmt_badge(h['坂路血'], h['坂路血順位'])} | 時計血統: {fmt_badge(h['時計血'], h['時計血順位'])}</li>"
        f"<li><strong>血統＆クッション値</strong>: 父: {h.get('種牡馬','-')} | クッション適性: {h.get('cushion_badge_raw','') if h['track']=='芝' else 'ダート戦（対象外）'}</li>"
        f"</ul>"
        f"</div>",
        unsafe_allow_html=True,
    )
