import csv
import datetime
import glob
import io
import itertools
import os
import re
import numpy as np
import pandas as pd
import streamlit as st

# ==============================================================================
# 競馬予想10 クッション値Vr 完全統合Webアプリケーション
# 4段階ゲートキーパー ＆ 【実践馬券構成フォーミュラ完全連動版】
# ==============================================================================

st.set_page_config(
    page_title="競馬予想10 クッション値Vr - 実戦馬券構成完全連動",
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
    .race-type-chaos { background: linear-gradient(135deg, #881337 0%, #be123c 100%); color: #fff1f2; border: 1px solid #fb7185; }
    
    .recom-panel-go { background: linear-gradient(135deg, #111827 0%, #1f2937 100%); border: 2px solid #10b981; border-radius: 10px; padding: 16px 20px; margin-bottom: 20px; }
    .recom-title-go { font-size: 16px; font-weight: bold; color: #34d399; margin-bottom: 12px; border-bottom: 1px solid #374151; padding-bottom: 5px; }
    .recom-row { margin-bottom: 8px; font-size: 14.5px; line-height: 1.6; }
    .recom-block { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; padding: 12px 16px; margin-bottom: 10px; }
    .recom-val-num { color: #ffffff; font-weight: bold; font-size: 15.5px; letter-spacing: 1px; }

    /* 出走馬カルテ通常 */
    .horse-card { background-color: #161e2e; border-left: 5px solid #238636; padding: 14px 18px; border-radius: 8px; margin-bottom: 14px; border-top: 1px solid #30363d; border-right: 1px solid #30363d; border-bottom: 1px solid #30363d; }
    .horse-card-danger { background-color: #1a1618 !important; border-left: 5px solid #ef4444 !important; padding: 14px 18px; border-radius: 8px; margin-bottom: 14px; border-top: 1px solid #4c1d24; border-right: 1px solid #4c1d24; border-bottom: 1px solid #4c1d24; }
    
    .horse-card-header { display: flex; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 8px; }
    .horse-card-title { font-size: 18px; font-weight: bold; color: #ffffff; }
    .race-badge-title { background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); color: #ffffff; font-weight: bold; font-size: 14px; padding: 2px 10px; border-radius: 6px; border: 1px solid #93c5fd; margin-right: 6px; }
    .horse-card-list { list-style-type: none; padding-left: 0; margin: 0; }
    .horse-card-list li { font-size: 13.5px; color: #c9d1d9; margin-bottom: 5px; line-height: 1.6; }
    .horse-card-list li::before { content: "• "; color: #58a6ff; font-weight: bold; }
    
    /* バッジ */
    .badge-mark-gtv { background: linear-gradient(135deg, #b45309 0%, #d97706 100%); color: #ffffff; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #fde68a; }
    .badge-accel-on { background: linear-gradient(135deg, #059669 0%, #10b981 100%); color: #ffffff; font-weight: bold; font-size: 11.5px; padding: 2px 7px; border-radius: 4px; border: 1px solid #34d399; }
    .badge-c-gold { background: linear-gradient(135deg, #b45309 0%, #f59e0b 50%, #d97706 100%); color: #ffffff; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #fde68a; }
    .badge-c-fake { background: linear-gradient(135deg, #475569 0%, #334155 100%); color: #fca5a5; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #ef4444; }
    .badge-target-win { background: linear-gradient(135deg, #e11d48 0%, #be123c 100%); color: #ffffff; font-weight: bold; font-size: 12px; padding: 2px 9px; border-radius: 6px; }
    .badge-target-axis { background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: #ffffff; font-weight: bold; font-size: 12px; padding: 2px 9px; border-radius: 6px; }
    .badge-tr-teppan { background: linear-gradient(135deg, #e11d48 0%, #be123c 100%); color: #ffffff; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #fda4af; }
    .badge-tr-shobu { background: linear-gradient(135deg, #d97706 0%, #b45309 100%); color: #ffffff; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #fde68a; }
    .badge-tr-tokuchu { background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); color: #ffffff; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #7dd3fc; }
    .badge-tr-danger { background: linear-gradient(135deg, #4b5563 0%, #1f2937 100%); color: #f87171; font-weight: bold; font-size: 11px; padding: 2px 7px; border-radius: 6px; border: 1px solid #ef4444; }
    .badge-cushion-fit { display: inline-flex; align-items: center; background: linear-gradient(135deg, #059669 0%, #10b981 100%); color: #ffffff; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #34d399; }
    .badge-cushion-danger { display: inline-flex; align-items: center; background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%); color: #ffffff; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #f87171; }
    .badge-bomb { background: linear-gradient(135deg, #EB3349 0%, #F45C43 100%); color: #ffffff; border: 1px solid #FFA07A; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; }

    /* 脚質 */
    .badge-style-nige { background: linear-gradient(135deg, #e11d48 0%, #be123c 100%); color: #ffffff; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; }
    .badge-style-senko { background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: #ffffff; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; }
    .badge-style-sashi { background: linear-gradient(135deg, #059669 0%, #047857 100%); color: #ffffff; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; }
    .badge-style-oikomi { background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%); color: #ffffff; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; }
    .badge-style-chudan { background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); color: #ffffff; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; }
    .badge-style-other { background-color: #374151; color: #e5e7eb; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; }

    /* 買い目マーク */
    .badge-mark-honmei { display: inline-flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%); color: #ffffff; font-size: 16px; font-weight: 900; width: 30px; height: 30px; border-radius: 6px; border: 1.5px solid #fca5a5; margin-right: 6px; }
    .badge-mark-taikou { display: inline-flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: #ffffff; font-size: 16px; font-weight: 900; width: 30px; height: 30px; border-radius: 6px; border: 1.5px solid #93c5fd; margin-right: 6px; }
    .badge-mark-tanana { display: inline-flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #059669 0%, #047857 100%); color: #ffffff; font-size: 16px; font-weight: 900; width: 30px; height: 30px; border-radius: 6px; border: 1.5px solid #6ee7b7; margin-right: 6px; }
    .badge-mark-himo { display: inline-flex; align-items: center; justify-content: center; background-color: #374151; color: #f3f4f6; font-size: 14.5px; font-weight: bold; width: 30px; height: 30px; border-radius: 6px; border: 1px solid #6b7280; margin-right: 6px; }
    .badge-mark-ana { display: inline-flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #d97706 0%, #b45309 100%); color: #ffffff; font-size: 16px; font-weight: 900; width: 30px; height: 30px; border-radius: 6px; border: 1.5px solid #fde68a; margin-right: 6px; }
</style>
""",
    unsafe_allow_html=True,
)

PREV_HAN_SOLID_TRAINERS = ['堀', '中内田', '友道', '杉山晴', '田中博', '高柳大', '斎藤誠', '寺島', '岡田', '辻野', '平田', '鹿戸', '野中', '池添', '吉岡', '武英', '田中克', '四位', '森秀']
PREV_HAN_BOMB_TRAINERS = ['加藤征', '上村', '大竹', '牧', '杉浦', '武市', '和田正']
PREV_WOOD_DIRT_TRAINERS = ['稲垣', '小笠', '武英', '長谷川', '田中克', '本田']

def clean_horse_name(name):
    if pd.isnull(name): return ''
    return str(name).strip().replace('*', '').replace('$', '').replace(' ', '').replace(' ', '')

def find_col_regex(df, patterns):
    for pat in patterns:
        for col in df.columns:
            if re.search(pat, str(col), re.IGNORECASE): return col
    return None

def read_csv_robust(file_obj, candidate_patterns):
    src = file_obj
    if src is None:
        matched = []
        for pat in candidate_patterns: matched.extend(glob.glob(pat))
        if matched: src = max(matched, key=os.path.getmtime)
    if src is None: return pd.DataFrame()

    encodings = ['cp932', 'shift-jis', 'utf-8-sig', 'utf-8']
    for enc in encodings:
        try:
            if hasattr(src, 'seek'): src.seek(0)
            df = pd.read_csv(src, encoding=enc)
            if not df.empty: return df
        except Exception: continue
    return pd.DataFrame()

def extract_date_from_source(source_obj, candidate_patterns, lines):
    fn = ""
    if source_obj is not None:
        if isinstance(source_obj, str): fn = source_obj
        elif hasattr(source_obj, 'name'): fn = source_obj.name
    if fn:
        m = re.search(r'(20\d{2})[-_/]?([01]\d)[-_/]?([0-3]\d)', fn)
        if m:
            try: return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            except Exception: pass

    for line in lines[:25]:
        m = re.search(r'(20\d{2})[年/-](0?[1-9]|1[0-2])[月/-](0?[1-9]|[12]\d|3[01])', line)
        if m:
            try: return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            except Exception: pass
        m8 = re.search(r'\b(20\d{2})(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\b', line)
        if m8:
            try: return datetime.date(int(m8.group(1)), int(m8.group(2)), int(m8.group(3)))
            except Exception: pass

    return datetime.date.today()

def get_jra_waku(umaban, total_horses):
    if total_horses <= 8: return umaban
    base = total_horses // 8
    rem = total_horses % 8
    waku_counts = [base + (1 if 8 - i <= rem else 0) for i in range(8)]
    curr = 1
    for w_idx, cnt in enumerate(waku_counts, start=1):
        if curr <= umaban < curr + cnt: return w_idx
        curr += cnt
    return 8

def resolve_running_style(raw_style_full, raw_style_short, s_rank, f_rank, s_val):
    s = str(raw_style_full).strip() if pd.notnull(raw_style_full) else ''
    if not s or s in ['nan', 'None', '', '不明', '未設定', '-', '－']:
        s = str(raw_style_short).strip() if pd.notnull(raw_style_short) else ''

    if s and s not in ['nan', 'None', '', '不明', '未設定', '-', '－']:
        if '逃' in s: return '逃げ'
        elif '先' in s: return '先行'
        elif '差' in s: return '差し'
        elif '追' in s: return '追込'
        elif '後' in s: return '後方'
        elif '中' in s: return '中団'
        return s

    if s_rank == 1 and s_val >= 50.0: return '逃げ'
    elif s_rank <= 3: return '先行'
    elif f_rank <= 3 and s_rank >= 5: return '差し'
    elif f_rank <= 2 and s_rank >= 8: return '追込'
    elif s_rank <= 6: return '先行'
    else: return '中団'

def get_running_style_badge(style_str):
    if not style_str or pd.isnull(style_str) or style_str in ['-', '－', '不明', 'nan', '']: return ""
    s = str(style_str).strip()
    if '逃' in s: return "<span class='badge-style-nige'>🏃 逃げ</span>"
    elif '先' in s: return "<span class='badge-style-senko'>🐎 先行</span>"
    elif '差' in s: return "<span class='badge-style-sashi'>⚡ 差し</span>"
    elif '追' in s: return "<span class='badge-style-oikomi'>🔥 追込</span>"
    elif '後' in s: return "<span class='badge-style-oikomi'>後方</span>"
    elif '中' in s: return "<span class='badge-style-chudan'>中団</span>"
    return f"<span class='badge-style-other'>{s}</span>"

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

def evaluate_sire_cushion(sire_name, venue, dist_str, band_str):
    sire = clean_horse_name(sire_name)
    dist = re.sub(r'\D', '', str(dist_str))
    v = str(venue).strip()
    b = str(band_str).strip()

    key = (v, dist, sire, b)
    if key in SIRE_COURSE_MATRIX_TOP:
        return f"<span class='badge-cushion-fit'>🟢 {sire}特注 ({SIRE_COURSE_MATRIX_TOP[key]})</span>"
    if key in SIRE_COURSE_MATRIX_DANGER:
        return f"<span class='badge-cushion-danger'>⚠️ {sire}危険 ({SIRE_COURSE_MATRIX_DANGER[key]})</span>"
    return ""

def check_trainer_patterns(r):
    trainer = str(r.get('調教師', ''))
    s_full = bool(r.get('坂路_完全加速', False))
    w_acc = bool(r.get('is_wood_accel', False))
    w_1f = pd.to_numeric(r.get('wood_1F', 99.0), errors='coerce')
    s_1f = pd.to_numeric(r.get('坂路_1F', 99.0), errors='coerce')
    s_4f = pd.to_numeric(r.get('坂路_4F', 99.0), errors='coerce')
    track = str(r.get('track', ''))
    
    sat_sun_s = pd.to_numeric(r.get('土日坂路最速', 999.0), errors='coerce')
    prev_han = bool(r.get('has_prev_han', False))
    prev_han_fast = bool(r.get('has_prev_han_fast', False))

    if '木村' in trainer and w_1f <= 11.5 and w_acc:
        return pd.Series(['鉄板', '木村哲也×W終い11.5s以下鉄板', "<span class='badge-tr-teppan'>🏛️ 木村×W11.5s鉄板</span>"])
    if '中内田' in trainer and w_1f <= 11.3:
        return pd.Series(['鉄板', '中内田×W終い11.3s以下鉄板', "<span class='badge-tr-teppan'>🏛️ 中内田×W抜根鉄板</span>"])
    if '杉山晴' in trainer and (s_4f <= 52.9) and (s_1f <= 12.2) and s_full:
        return pd.Series(['鉄板', '杉山晴×坂路52秒終い12.2s鉄板', "<span class='badge-tr-teppan'>🏛️ 杉山晴×坂路黄金鉄板</span>"])

    if 'ダ' in track and w_acc and not s_full and not r.get('is_prev_wood_dirt', False):
        return pd.Series(['危険', 'ダート×ウッド追い切り罠', "<span class='badge-tr-danger'>⚠️ ダート×W追危険</span>"])

    if '矢作' in trainer and s_full and s_4f <= 53.5:
        return pd.Series(['勝負', '矢作×坂路加速パターン', "<span class='badge-tr-shobu'>⚔️ 矢作×坂路加速勝負</span>"])
    if prev_han_fast and r.get('is_prev_han_solid', False):
        return pd.Series(['勝負', '王道厩舎×前日坂路勝負', "<span class='badge-tr-shobu'>⚔️ 王道×前日坂路勝負</span>"])

    is_main_tuned = (s_full and s_4f <= 54.0 and s_1f <= 12.5) or (w_acc and w_1f <= 11.8)
    has_sub_backing = (sat_sun_s <= 56.5) or prev_han or r.get('坂路_穴トリガー', False)
    if is_main_tuned and has_sub_backing:
        return pd.Series(['特注', '水木本追×土日/前日裏付け特注', "<span class='badge-tr-tokuchu'>💎 調教特注</span>"])

    return pd.Series(['通常', '', ""])

def populate_all_derived_columns(d):
    res = d.copy()
    res['dist_num'] = pd.to_numeric(res.get('dist', 1600), errors='coerce').fillna(1600)
    res['Fup'] = pd.to_numeric(res.get('Fup', 0), errors='coerce').fillna(0)
    res['Fup_rank'] = pd.to_numeric(res.get('Fup_rank', 99), errors='coerce').fillna(99)
    res['F指数'] = pd.to_numeric(res.get('F指数', 0.0), errors='coerce').fillna(0.0)
    res['F_rank'] = pd.to_numeric(res.get('F_rank', 99), errors='coerce').fillna(99)
    res['S指数'] = pd.to_numeric(res.get('S指数', 0.0), errors='coerce').fillna(0.0)
    res['S_rank'] = pd.to_numeric(res.get('S_rank', 99), errors='coerce').fillna(99)
    res['arms'] = pd.to_numeric(res.get('arms', 0.0), errors='coerce').fillna(0.0)
    res['arms_rank'] = pd.to_numeric(res.get('arms_rank', 99), errors='coerce').fillna(99)
    res['tua'] = pd.to_numeric(res.get('tua', 0.0), errors='coerce').fillna(0.0)
    res['tua_rank'] = pd.to_numeric(res.get('tua_rank', 99), errors='coerce').fillna(99)
    res['人気'] = pd.to_numeric(res.get('人気', 99), errors='coerce').fillna(99)
    res['枠番'] = pd.to_numeric(res.get('枠番', 8), errors='coerce').fillna(8)

    if '印' in res.columns:
        mark_s = res['印'].astype(str)
        res['is_gtv_marked'] = mark_s.str.contains(r'GTV|G|Ｔ|★|☆|特|注', na=False, regex=True)
    else:
        res['is_gtv_marked'] = False

    if '脚質' in res.columns:
        style_s = res['脚質'].astype(str)
    else:
        style_s = pd.Series('', index=res.index)
    res['is_style_senko'] = style_s.str.contains('先', na=False)
    res['is_style_sashi'] = style_s.str.contains('差', na=False)
    res['is_style_nige'] = style_s.str.contains('逃', na=False)
    res['is_style_oikomi'] = style_s.str.contains('追', na=False)
    res['is_style_front'] = res['is_style_senko'] | res['is_style_nige']
    res['is_style_back'] = style_s.str.contains('後|中', na=False)

    if '坂路_4F' in res.columns: s_4f_val = pd.to_numeric(res['坂路_4F'], errors='coerce').fillna(99.0)
    else: s_4f_val = pd.Series(99.0, index=res.index)

    if '坂路_1F' in res.columns: s_1f_val = pd.to_numeric(res['坂路_1F'], errors='coerce').fillna(99.0)
    else: s_1f_val = pd.Series(99.0, index=res.index)

    if 'wood_1F' in res.columns: w_1f_val = pd.to_numeric(res['wood_1F'], errors='coerce').fillna(99.0)
    else: w_1f_val = pd.Series(99.0, index=res.index)

    res['has_sharp_finishing'] = (s_1f_val <= 12.2) | (w_1f_val <= 11.4)
    res['坂路_完全加速'] = res['坂路_完全加速'].fillna(False).astype(bool) if '坂路_完全加速' in res.columns else False
    res['坂路_穴トリガー'] = res['坂路_穴トリガー'].fillna(False).astype(bool) if '坂路_穴トリガー' in res.columns else False
    res['is_wood_accel'] = res['is_wood_accel'].fillna(False).astype(bool) if 'is_wood_accel' in res.columns else False

    res['坂路_完全加速_有効'] = res['坂路_完全加速'] & (s_4f_val <= 56.0) & (s_1f_val <= 13.0)
    res['調教加速'] = res['坂路_完全加速_有効'] | res['is_wood_accel']

    if 'C馬' in res.columns: c_s = res['C馬'].astype(str)
    else: c_s = pd.Series('', index=res.index)
    res['is_c_horse'] = c_s.str.contains('C|Ｃ', na=False)
    res['is_c_real_gold'] = res['is_c_horse'] & (res['Fup'] >= 4)
    res['is_c_fake_trap'] = res['is_c_horse'] & (res['Fup'] <= 3) & (res['F_rank'] > 1)

    if '前日坂路あり' in res.columns: res['has_prev_han'] = res['前日坂路あり'].fillna(False).astype(bool)
    else: res['has_prev_han'] = pd.Series(False, index=res.index)

    if '前日坂路時計' in res.columns: prev_han_clock = pd.to_numeric(res['前日坂路時計'], errors='coerce').fillna(999.0)
    else: prev_han_clock = pd.Series(999.0, index=res.index)
    res['has_prev_han_fast'] = res['has_prev_han'] & (prev_han_clock <= 65.9)

    if '調教師' in res.columns: tr_s = res['調教師'].astype(str)
    else: tr_s = pd.Series('', index=res.index)
    res['is_prev_han_solid'] = res['has_prev_han_fast'] & tr_s.apply(lambda t: any(x in str(t) for x in PREV_HAN_SOLID_TRAINERS)) & (res['人気'] <= 3)
    res['is_prev_han_bomb'] = res['has_prev_han_fast'] & tr_s.apply(lambda t: any(x in str(t) for x in PREV_HAN_BOMB_TRAINERS)) & (res['人気'] >= 6)

    if '前日ウッドあり' in res.columns: prev_w_s = res['前日ウッドあり'].fillna(False).astype(bool)
    else: prev_w_s = pd.Series(False, index=res.index)

    if 'track' in res.columns: tk_s = res['track'].astype(str)
    else: tk_s = pd.Series('', index=res.index)
    res['is_prev_wood_dirt'] = prev_w_s & tk_s.str.contains('ダ', na=False) & tr_s.apply(lambda t: any(x in str(t) for x in PREV_WOOD_DIRT_TRAINERS))

    # ダート×ウッド追い判定
    res['is_dirt_wood_trap'] = tk_s.str.contains('ダ', na=False) & res['is_wood_accel'] & (~res['坂路_完全加速_有効']) & (~res['is_prev_wood_dirt']) & (res['F_rank'] >= 4)

    # SSS級＆確変馬
    res['is_sss_level'] = (res['F指数'] >= 70) & (res['arms'] >= 120) & (res['tua'] >= 200)
    res['is_iron_f72'] = res['F指数'] >= 72.0
    res['is_value_arms120'] = res['arms'] >= 120.0

    # 谷の形・Fupの罠
    res['is_fup_trap'] = (res['Fup'] == 1) & (res['人気'] <= 3) & (res['F指数'] <= 72) & (~res['is_sss_level'])
    res['is_valley_trap'] = (res['人気'] <= 3) & (res['F_rank'] >= 4) & (res['S_rank'] >= 4) & (~res['is_sss_level']) & (res['F指数'] <= 70)
    res['is_short_back_trap'] = (res['dist_num'] <= 1400) & res['is_style_back'] & (res['人気'] <= 3) & (~res['is_sss_level'])

    c_dang = res['is_cushion_danger'] if 'is_cushion_danger' in res.columns else pd.Series(False, index=res.index)
    res['is_gate1_fatal_trap'] = (
        res['is_dirt_wood_trap']
        | res['is_c_fake_trap']
        | res['is_fup_trap']
        | res['is_valley_trap']
        | res['is_short_back_trap']
        | c_dang
    )

    res['is_gate2_axis_qualified'] = (
        (~res['is_gate1_fatal_trap'])
        & ((res['Fup'] >= 4) | (res['F_rank'] == 1) | (res['S_rank'] == 1))
        & (res['枠番'] <= 6)
        & (res['坂路_完全加速_有効'] | res['is_prev_han_solid'] | (res['F指数'] >= 65.0))
    )

    res['is_gate3_bomb_qualified'] = (
        (res['人気'] >= 4)
        & (~res['is_gate1_fatal_trap'])
        & ((res['arms'] >= 110.0) | (res['tua'] >= 180.0) | (res['Fup'] >= 4) | res['坂路_穴トリガー'])
    )

    return res

def load_and_merge_all(f_index, f_sakaro, f_wood):
    index_patterns = ['data/出馬表_指数*.csv', '出馬表_指数*.csv', 'data/*指数*.csv', '*指数*.csv', 'data/出馬表*.csv', '出馬表*.csv']
    index_src = f_index
    if index_src is None:
        matched = []
        for pat in index_patterns: matched.extend(glob.glob(pat))
        if matched: index_src = max(matched, key=os.path.getmtime)

    records = []
    lines = []
    if index_src is not None:
        for enc in ['cp932', 'shift-jis', 'utf-8-sig', 'utf-8']:
            try:
                if isinstance(index_src, str):
                    with open(index_src, 'r', encoding=enc, errors='ignore') as f: lines = [l.strip() for l in f if l.strip()]
                else:
                    index_src.seek(0)
                    content = index_src.read()
                    if isinstance(content, bytes): lines = [l.strip() for l in content.decode(enc, errors='ignore').splitlines() if l.strip()]
                    else: lines = [l.strip() for l in content.splitlines() if l.strip()]
                if lines: break
            except Exception: continue

        reader = csv.reader(lines)
        for parts in reader:
            n = len(parts)
            if n < 8 or parts[0] in ['場所', 'レースID', 'race_id']: continue

            race_id = parts[0]
            track = parts[1] if n > 1 else '芝'
            dist = parts[2] if n > 2 else '1600'
            umaban = parts[3] if n > 3 else '99'
            horse_raw = parts[4] if n > 4 else ''
            c_marker = str(parts[5]).strip() if n > 5 else ''
            trainer = parts[6] if n > 6 else ''
            jockey = parts[7] if n > 7 else ''
            pop = parts[8] if n > 8 else '99'
            mark = parts[9] if n > 9 else ''
            fup = pd.to_numeric(parts[10], errors='coerce') if n > 10 else 0
            fup_rank = pd.to_numeric(parts[11], errors='coerce') if n > 11 else 99
            s_val = pd.to_numeric(parts[12], errors='coerce') if n > 12 else 0.0
            s_rank = pd.to_numeric(parts[13], errors='coerce') if n > 13 else 99
            f_val = pd.to_numeric(parts[14], errors='coerce') if n > 14 else 0.0
            f_rank = pd.to_numeric(parts[15], errors='coerce') if n > 15 else 99
            arms_val = pd.to_numeric(parts[16], errors='coerce') if n > 16 else 0.0
            arms_rank = pd.to_numeric(parts[17], errors='coerce') if n > 17 else 99
            tua_val = pd.to_numeric(parts[18], errors='coerce') if n > 18 else 0.0
            tua_rank = pd.to_numeric(parts[19], errors='coerce') if n > 19 else 99
            finish = parts[20] if n > 20 else None
            sire = parts[21] if n > 21 else ''

            raw_style_short = str(parts[22]).strip() if n > 22 else ''
            raw_style_full = str(parts[23]).strip() if n > 23 else ''
            final_style = resolve_running_style(raw_style_full, raw_style_short, s_rank, f_rank, s_val)
            horse = clean_horse_name(horse_raw)

            if horse:
                records.append({
                    'race_id': race_id, 'track': track, 'dist': dist,
                    '馬番': int(umaban) if str(umaban).isdigit() else 99,
                    '馬名': horse, 'C馬': c_marker, '印': str(mark).strip(),
                    '調教師': clean_horse_name(trainer), '騎手': clean_horse_name(jockey),
                    '種牡馬': str(sire).strip(),
                    '人気': int(pop) if str(pop).isdigit() else 99,
                    '着順': int(finish) if str(finish).isdigit() else np.nan,
                    '脚質': final_style,
                    'Fup': fup if not np.isnan(fup) else 0,
                    'Fup_rank': int(fup_rank) if not np.isnan(fup_rank) else 99,
                    'S指数': s_val if not np.isnan(s_val) else 0.0,
                    'S_rank': int(s_rank) if not np.isnan(s_rank) else 99,
                    'F指数': f_val if not np.isnan(f_val) else 0.0,
                    'F_rank': int(f_rank) if not np.isnan(f_rank) else 99,
                    'arms': arms_val if not np.isnan(arms_val) else 0.0,
                    'arms_rank': int(arms_rank) if not np.isnan(arms_rank) else 99,
                    'tua': tua_val if not np.isnan(tua_val) else 0.0,
                    'tua_rank': int(tua_rank) if not np.isnan(tua_rank) else 99,
                })

    df_main = pd.DataFrame(records)
    if df_main.empty: return pd.DataFrame(), datetime.date.today()

    venue_dict = {'東': '東京', '中': '中山', '京': '京都', '阪': '阪神', '名': '中京', '小': '小倉', '新': '新潟', '福': '福島', '函': '函館', '札': '札幌'}
    def parse_race(rid):
        match = re.match(r'([^\d]+)(\d+)', str(rid))
        if match: return venue_dict.get(match.group(1), match.group(1)), int(match.group(2))
        return 'その他', 99

    df_main[['競馬場名', 'R番号']] = df_main['race_id'].apply(lambda x: pd.Series(parse_race(x)))
    df_main['race_uid'] = df_main['race_id']
    detected_date = extract_date_from_source(index_src, index_patterns, lines)
    df_main['total_horses'] = df_main.groupby('race_id')['馬番'].transform('count')
    df_main['枠番'] = df_main.apply(lambda r: get_jra_waku(r['馬番'], r['total_horses']), axis=1)

    exact_prev_day_int = int((detected_date - datetime.timedelta(days=1)).strftime('%Y%m%d'))

    # 坂路データ結合
    sakaro_patterns = ['data/出馬表_坂路*.csv', '出馬表_坂路*.csv', 'data/*坂路*.csv', '*坂路*.csv']
    df_s_raw = read_csv_robust(f_sakaro, sakaro_patterns)
    if not df_s_raw.empty:
        c_s_name = find_col_regex(df_s_raw, ['^馬名$', '^競走馬名$']) or df_s_raw.columns[4]
        df_s_raw['clean_name'] = df_s_raw[c_s_name].apply(clean_horse_name)

        c_s_4f = find_col_regex(df_s_raw, ['^time1$', '^4f$', '^４ｆ$', '^4Ｆ$']) or df_s_raw.columns[9]
        c_s_1f = find_col_regex(df_s_raw, ['^time4$', '^1f$', '^１ｆ$', '^1Ｆ$']) or df_s_raw.columns[12]
        c_s_l4 = find_col_regex(df_s_raw, ['^lap4$', '^ｌａｐ４$']) or df_s_raw.columns[13]
        c_s_l3 = find_col_regex(df_s_raw, ['^lap3$', '^ｌａｐ３$']) or df_s_raw.columns[14]
        c_s_l2 = find_col_regex(df_s_raw, ['^lap2$', '^ｌａｐ２$']) or df_s_raw.columns[15]
        c_s_l1 = find_col_regex(df_s_raw, ['^lap1$', '^ｌａｐ１$']) or df_s_raw.columns[16]

        df_s_raw['坂路_4F'] = pd.to_numeric(df_s_raw[c_s_4f], errors='coerce')
        df_s_raw['坂路_1F'] = pd.to_numeric(df_s_raw[c_s_1f], errors='coerce')
        df_s_raw['坂路_Lap4'] = pd.to_numeric(df_s_raw[c_s_l4], errors='coerce')
        df_s_raw['坂路_Lap3'] = pd.to_numeric(df_s_raw[c_s_l3], errors='coerce')
        df_s_raw['坂路_Lap2'] = pd.to_numeric(df_s_raw[c_s_l2], errors='coerce')
        df_s_raw['坂路_Lap1'] = pd.to_numeric(df_s_raw[c_s_l1], errors='coerce')

        def determine_sakaro_lap_type(r):
            l1, l2 = r['坂路_Lap1'], r['坂路_Lap2']
            if pd.isnull(l1) or pd.isnull(l2): return ''
            if l1 < l2:
                if l1 <= 11.9: return 'A3'
                elif 12.0 <= l1 <= 12.9 and 12.0 <= l2 <= 12.9: return 'A2'
                elif 12.0 <= l1 <= 12.9 and l2 >= 13.0: return 'A1'
            else:
                if l1 <= 11.9 and l2 <= 11.9: return 'B3'
                elif 12.0 <= l1 <= 12.9 and 12.0 <= l2 <= 12.9: return 'B2'
                elif 12.0 <= l2 <= 12.9: return 'B1'
            return ''

        df_s_raw['坂路_ラップ型'] = df_s_raw.apply(determine_sakaro_lap_type, axis=1)
        df_s_best = df_s_raw.dropna(subset=['坂路_4F']).sort_values('坂路_4F').drop_duplicates('clean_name', keep='first').copy()
        
        df_s_best['坂路_完全加速'] = (
            (df_s_best['坂路_Lap4'] > df_s_best['坂路_Lap3'])
            & (df_s_best['坂路_Lap3'] > df_s_best['坂路_Lap2'])
            & (df_s_best['坂路_Lap2'] > df_s_best['坂路_Lap1'])
            & (df_s_best['坂路_4F'] <= 56.0)
            & (df_s_best['坂路_Lap1'] <= 13.0)
        )
        df_s_best['坂路_穴トリガー'] = (df_s_best['坂路_Lap3'] <= 14.0) & (df_s_best['坂路_Lap2'] > df_s_best['坂路_Lap1'])

        merge_cols = ['clean_name', '坂路_4F', '坂路_1F', '坂路_完全加速', '坂路_穴トリガー', '坂路_ラップ型']
        df_main = pd.merge(df_main, df_s_best[merge_cols], left_on='馬名', right_on='clean_name', how='left')

    if '坂路_4F' not in df_main.columns:
        df_main['坂路_4F'] = np.nan; df_main['坂路_1F'] = np.nan
        df_main['坂路_完全加速'] = False; df_main['坂路_穴トリガー'] = False; df_main['坂路_ラップ型'] = ''
    if '前日坂路時計' not in df_main.columns: df_main['前日坂路時計'] = np.nan
    if '前日坂路あり' not in df_main.columns: df_main['前日坂路あり'] = False

    # ウッドデータ結合
    wood_patterns = ['data/出馬表_ウッド*.csv', '出馬表_ウッド*.csv', 'data/*ウッド*.csv', '*ウッド*.csv']
    df_w_raw = read_csv_robust(f_wood, wood_patterns)
    if not df_w_raw.empty:
        c_w_name = find_col_regex(df_w_raw, ['^馬名$', '^競走馬名$']) or df_w_raw.columns[4]
        df_w_raw['clean_name'] = df_w_raw[c_w_name].apply(clean_horse_name)
        c_w_1f = find_col_regex(df_w_raw, ['^1f$', '^１ｆ$', '^1Ｆ$']) or df_w_raw.columns[13]
        c_w_l2 = find_col_regex(df_w_raw, ['^lap2$', '^ｌａｐ２$']) or df_w_raw.columns[18]
        c_w_l1 = find_col_regex(df_w_raw, ['^lap1$', '^ｌａｐ１$']) or df_w_raw.columns[19]

        df_w_raw['wood_1F'] = pd.to_numeric(df_w_raw[c_w_1f], errors='coerce')
        df_w_raw['wood_Lap2'] = pd.to_numeric(df_w_raw[c_w_l2], errors='coerce')
        df_w_raw['wood_Lap1'] = pd.to_numeric(df_w_raw[c_w_l1], errors='coerce')

        df_w_best = df_w_raw.dropna(subset=['wood_1F']).sort_values('wood_1F').drop_duplicates('clean_name', keep='first').copy()
        df_w_best['wood_accel'] = df_w_best['wood_Lap2'] - df_w_best['wood_Lap1']
        df_w_best['is_wood_accel'] = (df_w_best['wood_accel'] > 0) & (df_w_best['wood_accel'].notna())

        w_merge_cols = ['clean_name', 'wood_1F', 'wood_accel', 'is_wood_accel']
        df_main = pd.merge(df_main, df_w_best[w_merge_cols], left_on='馬名', right_on='clean_name', how='left')

    if 'wood_1F' not in df_main.columns:
        df_main['wood_1F'] = np.nan; df_main['wood_accel'] = np.nan; df_main['is_wood_accel'] = False
    if '前日ウッドあり' not in df_main.columns: df_main['前日ウッドあり'] = False

    df_main = populate_all_derived_columns(df_main)
    return df_main, detected_date

# ==============================================================================
# ★ データ読み込み実行
# ==============================================================================
st.sidebar.markdown('### 📁 CSVデータ読み込み')
with st.sidebar.expander('データ更新', expanded=False):
    up_index = st.file_uploader('出馬表・指数 CSV', type=['csv'], key='up_index')
    up_sakaro = st.file_uploader('坂路調教 CSV', type=['csv'], key='up_sakaro')
    up_wood = st.file_uploader('ウッド調教 CSV', type=['csv'], key='up_wood')

df, race_date = load_and_merge_all(up_index, up_sakaro, up_wood)

if df.empty:
    st.warning('⚠️ CSVデータが読み込まれていません。サイドバーからCSVファイルを指定してください。')
    st.stop()

# 競馬場・クッション値設定
venue_sort_order = ['東京', '中山', '京都', '阪神', '中京', '小倉', '新潟', '福島', '函館', '札幌']
existing_venues = [v for v in venue_sort_order if v in df['競馬場名'].unique()]
if 'active_venue' not in st.session_state or st.session_state['active_venue'] not in existing_venues:
    st.session_state['active_venue'] = existing_venues[0] if existing_venues else '東京'

default_cushions = {'札幌': 7.5, '函館': 7.4, '中京': 9.6, '新潟': 9.3, '東京': 9.3, '中山': 9.6, '京都': 10.0, '阪神': 9.4, '小倉': 9.2, '福島': 8.9}
current_active_v = st.session_state['active_venue']
cushion_state_key = f"cushion_val_{current_active_v}"
if cushion_state_key not in st.session_state:
    st.session_state[cushion_state_key] = float(default_cushions.get(current_active_v, 9.5))

st.sidebar.markdown(f"### 芝クッション値 ({current_active_v})")
current_cushion_val = st.sidebar.number_input(
    f"芝クッション値 ({current_active_v})",
    min_value=5.0, max_value=13.0, value=float(st.session_state[cushion_state_key]),
    step=0.1, key=cushion_state_key, label_visibility='collapsed',
)
current_band = get_cushion_band(current_active_v, current_cushion_val)
current_bin_name = get_current_cushion_bin_name(current_cushion_val)

df['cushion_badge_raw'] = df.apply(lambda r: evaluate_sire_cushion(r['種牡馬'], r['競馬場名'], r['dist'], current_band) if '芝' in str(r.get('track', '')) else '', axis=1)
df['is_cushion_fit'] = df['cushion_badge_raw'].str.contains('特注')
df['is_cushion_danger'] = df['cushion_badge_raw'].str.contains('危険')
df[['調教ステータス', '厩舎狙い目フラグ', 'tr_badge_html']] = df.apply(check_trainer_patterns, axis=1)
df = populate_all_derived_columns(df)

# メイン画面ヘッダー
chosen_venue = st.radio('開催場選択', options=existing_venues, horizontal=True, label_visibility='collapsed')
st.session_state['active_venue'] = chosen_venue

v_df = df[df['競馬場名'] == chosen_venue]
races_in_v = v_df[['race_uid', 'race_id', 'R番号', 'track', 'dist']].drop_duplicates('race_uid').sort_values('R番号')

race_options = {}
for _, r_row in races_in_v.iterrows():
    r_horses = df[df['race_uid'] == r_row['race_uid']]
    f1_h = r_horses[r_horses['F_rank'] == 1]
    f1_val = f1_h['F指数'].values[0] if not f1_h.empty else 0
    is_bonus = bool(((r_horses['F_rank'] <= 3) & (r_horses['arms_rank'] <= 3) & (r_horses['tua_rank'] <= 3)).sum() >= 3)
    tag = '👑ボーナス' if is_bonus else ('🎯狙' if f1_val >= 60 else '🔥荒')
    race_options[r_row['race_uid']] = f"{tag} {r_row['R番号']}R ({r_row['track']}{r_row['dist']}m)"

selected_race_uid = st.selectbox('レース選択', options=list(race_options.keys()), format_func=lambda x: race_options[x], label_visibility='collapsed')
race_df = df[df['race_uid'] == selected_race_uid].copy()
race_df = populate_all_derived_columns(race_df)

# ==============================================================================
# ★ 動的スコア算出（能力・調教・減点ペナルティ統合評価）
# ==============================================================================
def calculate_dynamic_priority_score(r):
    score = 0.0
    f_val, arms_val, tua_val = r.get('F指数', 0.0), r.get('arms', 0.0), r.get('tua', 0.0)
    waku_val = r.get('枠番', 8)
    style = str(r.get('脚質', ''))

    # 能力加点
    if f_val >= 70.0: score += 55.0
    elif r.get('F_rank', 99) == 1: score += 40.0
    elif r.get('F_rank', 99) == 2: score += 30.0

    if r.get('S_rank', 99) == 1: score += 35.0
    elif r.get('S_rank', 99) <= 3: score += 20.0

    if arms_val >= 120.0: score += 25.0
    if tua_val >= 190.0: score += 20.0

    if r.get('Fup', 0) >= 5: score += 35.0
    elif r.get('Fup', 0) == 4: score += 20.0

    # 先行・枠順加点
    if '先' in style or '逃' in style: score += 20.0
    if waku_val in [1, 2, 3]: score += 15.0
    elif waku_val in [7, 8]: score -= 15.0

    # 調教加点
    if bool(r.get('坂路_完全加速_有効', False)): score += 30.0
    if bool(r.get('is_prev_han_solid', False)): score += 35.0
    if bool(r.get('is_cushion_fit', False)): score += 35.0

    # 減点ペナルティ
    if bool(r.get('is_c_fake_trap', False)): score -= 45.0
    if bool(r.get('is_fup_trap', False)): score -= 45.0
    if bool(r.get('is_dirt_wood_trap', False)): score -= 40.0
    if bool(r.get('is_valley_trap', False)): score -= 40.0
    if bool(r.get('is_cushion_danger', False)): score -= 35.0

    return score

race_df['dynamic_score'] = race_df.apply(calculate_dynamic_priority_score, axis=1)
sorted_dynamic = race_df.sort_values('dynamic_score', ascending=False)

# ==============================================================================
# ★ 【完全連動】新実戦馬券構成フォーミュラ自動生成エンジン
# ==============================================================================

# ① 本命馬◎（連軸筆頭：動的スコア最上位）
pick_win_horse = sorted_dynamic.iloc[0]

# ② 対抗馬◯（軸・連対狙い：2番手実力馬）
remain_pool = sorted_dynamic[sorted_dynamic['馬番'] != pick_win_horse['馬番']]
pick_axis_horse = remain_pool.iloc[0] if not remain_pool.empty else pick_win_horse

# ③ 特大推奨穴馬★（GATE3適合、または4人気以降のスコア最上位）
bomb_pool = sorted_dynamic[
    (sorted_dynamic['人気'] >= 4) &
    (sorted_dynamic['is_gate3_bomb_qualified'] | (sorted_dynamic['arms'] >= 110.0) | (sorted_dynamic['tua'] >= 180.0))
]
if not bomb_pool.empty:
    pick_himo_horse = bomb_pool.iloc[0]
else:
    pick_himo_horse = remain_pool.iloc[1] if len(remain_pool) > 1 else pick_axis_horse

# ④ 危険な人気馬⚠️（3人気以内で何らかの減点要因あり）
danger_cands = race_df[
    (race_df['人気'] <= 3) &
    (race_df['is_gate1_fatal_trap'] | (race_df['Fup'] <= 2))
]
pick_danger_horse = danger_cands.iloc[0] if not danger_cands.empty else None

# ------------------------------------------------------------------------------
# 🎫 3連複フォーメーション生成（中京8R的中モデル・多重防壁型）
# ------------------------------------------------------------------------------
# 1列目（軸・2頭）: 本命◎ ＋ 対抗◯
col1_horses = [int(pick_win_horse['馬番'])]
if pick_axis_horse['馬番'] != pick_win_horse['馬番']:
    col1_horses.append(int(pick_axis_horse['馬番']))

# 2列目（相手・3〜4頭）: 1列目 ＋ マトリクス強者（F上位・S上位・arms上位）
col2_horses = list(col1_horses)
for u in sorted_dynamic['馬番'].tolist():
    u_int = int(u)
    if u_int not in col2_horses:
        col2_horses.append(u_int)
    if len(col2_horses) >= 4:
        break

# 3列目（ヒモ広め・6〜7頭）: 2列目 ＋ 特大穴馬★ ＋ 調教加速馬 ＋ 押さえ
col3_horses = list(col2_horses)
if int(pick_himo_horse['馬番']) not in col3_horses:
    col3_horses.append(int(pick_himo_horse['馬番']))

# スコア上位馬を追加して最大7頭まで展開
for u in sorted_dynamic['馬番'].tolist():
    u_int = int(u)
    if u_int not in col3_horses:
        col3_horses.append(u_int)
    if len(col3_horses) >= 7:
        break

# ------------------------------------------------------------------------------
# 🎫 精鋭BOX（馬連・ワイド・4頭）: 本命 ＋ 対抗 ＋ マトリクス3位 ＋ 特大穴馬
# ------------------------------------------------------------------------------
box_cands = [int(pick_win_horse['馬番']), int(pick_axis_horse['馬番']), int(pick_himo_horse['馬番'])]
for u in sorted_dynamic['馬番'].tolist():
    u_int = int(u)
    if u_int not in box_cands:
        box_cands.append(u_int)
    if len(box_cands) >= 4:
        break
box_horses = sorted(list(dict.fromkeys(box_cands)))

# ------------------------------------------------------------------------------
# 🎫 3連単フォーメーション（高配当・裏表マルチ対応）
# ------------------------------------------------------------------------------
trio_1st = [int(pick_win_horse['馬番'])]
if int(pick_himo_horse['馬番']) not in trio_1st:
    trio_1st.append(int(pick_himo_horse['馬番']))

trio_2nd = list(dict.fromkeys(trio_1st + [int(pick_axis_horse['馬番'])] + col2_horses[:3]))
trio_3rd = list(col3_horses)

# 印マッピング
bet_marks_dict = {}
bet_marks_dict[int(pick_win_horse['馬番'])] = "<span class='badge-mark-honmei'>◎</span>"
if pick_axis_horse['馬番'] != pick_win_horse['馬番']:
    bet_marks_dict[int(pick_axis_horse['馬番'])] = "<span class='badge-mark-taikou'>◯</span>"
for u in col2_horses:
    if int(u) not in bet_marks_dict: bet_marks_dict[int(u)] = "<span class='badge-mark-tanana'>▲</span>"
for u in col3_horses:
    if int(u) not in bet_marks_dict: bet_marks_dict[int(u)] = "<span class='badge-mark-himo'>△</span>"
if int(pick_himo_horse['馬番']) not in bet_marks_dict:
    bet_marks_dict[int(pick_himo_horse['馬番'])] = "<span class='badge-mark-ana'>★</span>"

# ==============================================================================
# ★ UIパネル表示（実戦推奨買い目完全連動出力）
# ==============================================================================
if pick_danger_horse is not None:
    danger_horse_label = f"{int(pick_danger_horse['馬番'])}番 {pick_danger_horse['馬名']}（人気先行・割引要素あり）"
else:
    danger_horse_label = "該当なし"

is_bonus_cur = bool(((race_df['F_rank'] <= 3) & (race_df['arms_rank'] <= 3) & (race_df['tua_rank'] <= 3)).sum() >= 3)
wave_label = '【👑 ボーナスレース】' if is_bonus_cur else '【標準・混戦レース】'

st.markdown(
    f"<div class='race-type-banner race-type-solid'>"
    f"<div><strong>🎯 レース波乱度判定: {wave_label}</strong></div>"
    f"<div>推奨券種: 3連複フォーメーション / 馬連・ワイド精鋭BOX / 単勝</div></div>",
    unsafe_allow_html=True,
)

st.markdown(
    f"<div class='recom-panel-go'><div class='recom-title-go'>📋 推奨馬ピックアップ（能力マトリクス×実質負荷調教）</div>"
    f"<div class='recom-row'>🥇 <strong>1着狙い（◎）</strong>: <span class='recom-val-num'>{int(pick_win_horse['馬番'])}番 {pick_win_horse['馬名']}</span>（F{int(pick_win_horse['F_rank'])}位 / S{int(pick_win_horse['S_rank'])}位 / 枠{int(pick_win_horse['枠番'])})</div>"
    f"<div class='recom-row'>🛡️ <strong>軸・連対狙い（◯）</strong>: <span class='recom-val-num'>{int(pick_axis_horse['馬番'])}番 {pick_axis_horse['馬名']}</span>（F{int(pick_axis_horse['F_rank'])}位 / arms{int(pick_axis_horse['arms_rank'])}位）</div>"
    f"<div class='recom-row'>💣 <strong>紐穴狙い・特大推奨（★）</strong>: <span class='recom-val-num'>{int(pick_himo_horse['馬番'])}番 {pick_himo_horse['馬名']}</span>（{int(pick_himo_horse['人気'])}人気 / arms: {pick_himo_horse['arms']:.1f} / tua: {pick_himo_horse['tua']:.1f}）</div>"
    f"<div class='recom-row'>⚠️ <strong>危険な人気馬</strong>: <span style='color:#ef4444; font-weight:bold;'>{danger_horse_label}</span></div></div>",
    unsafe_allow_html=True,
)

st.markdown(
    f"<div class='recom-panel-go'><div class='recom-title-go'>🎫 実戦推奨買い目フォーメーション（完全連動出力）</div>"
    f"<div class='recom-block'><strong>【本線：3連複フォーメーション（中京8R的中モデル）】</strong><br>"
    f"・<strong>1列目（軸）</strong>: [{', '.join(str(x) for x in col1_horses)}]<br>"
    f"・<strong>2列目（相手）</strong>: [{', '.join(str(x) for x in col2_horses)}]<br>"
    f"・<strong>3列目（ヒモ広め）</strong>: [{', '.join(str(x) for x in col3_horses)}]</div>"
    f"<div class='recom-block'><strong>【守り・保険：精鋭4頭BOX（馬連・ワイド）】</strong><br>"
    f"・<strong>BOX対象馬</strong>: [{', '.join(str(x) for x in box_horses)}] （計6点：軸飛び・縦目完全ケア）</div>"
    f"<div class='recom-block'><strong>【攻め：3連単フォーメーション（裏表マルチ対応）】</strong><br>"
    f"・1着: [{', '.join(str(x) for x in trio_1st)}]<br>"
    f"・2着: [{', '.join(str(x) for x in trio_2nd)}]<br>"
    f"・3着: [{', '.join(str(x) for x in trio_3rd)}]</div>"
    f"<div class='recom-block'><strong>【単勝・複勝】</strong>: 単勝 {int(pick_win_horse['馬番'])}番 / 複勝・ワイド特注 {int(pick_himo_horse['馬番'])}番</div></div>",
    unsafe_allow_html=True,
)

# ==============================================================================
# ★ 出走馬カルテ表示
# ==============================================================================
st.markdown("### 🏇 出走馬詳細カルテ")

for _, h in sorted_dynamic.iterrows():
    u_no = int(h['馬番'])
    is_fatal = bool(h['is_gate1_fatal_trap'])
    h_mark = bet_marks_dict.get(u_no, '')
    style_badge = get_running_style_badge(h.get('脚質', ''))

    badges = []
    if h_mark: badges.append(h_mark)
    if style_badge: badges.append(style_badge)
    
    mark_val = str(h.get('印', '')).strip()
    if mark_val and mark_val not in ['nan', 'None', '']:
        badges.append(f"<span class='badge-mark-gtv'>🏷️ 印: {mark_val}</span>")

    # 警告バッジ
    if h.get('is_dirt_wood_trap'): badges.append("<span class='badge-tr-danger'>⚠️ ダート×W追割引</span>")
    if h.get('is_c_fake_trap'): badges.append("<span class='badge-c-fake'>⚠️ 偽C馬(Fup3以下)</span>")
    if h.get('is_fup_trap'): badges.append("<span class='badge-tr-danger'>⚠️ Fup1の罠</span>")
    if h.get('is_cushion_danger'): badges.append("<span class='badge-cushion-danger'>⚠️ クッション危険</span>")

    # 加点バッジ
    if h.get('is_gate2_axis_qualified'): badges.append("<span class='badge-target-win'>👑 有力軸候補</span>")
    if h.get('is_gate3_bomb_qualified'): badges.append("<span class='badge-bomb'>🔥 爆発穴トリガー</span>")
    if h.get('坂路_完全加速_有効'): badges.append("<span class='badge-accel-on'>⚡ 坂路完全加速</span>")
    if h.get('is_c_real_gold'): badges.append("<span class='badge-c-gold'>👑 本物C馬</span>")
    if h.get('cushion_badge_raw'): badges.append(str(h['cushion_badge_raw']))

    badges_html = " ".join([b for b in badges if b])
    card_class = "horse-card-danger" if (is_fatal and h.get('人気', 99) <= 3) else "horse-card"

    st.markdown(
        f"<div class='{card_class}'>"
        f"<div class='horse-card-header'>"
        f"<span class='race-badge-title'>{u_no}番</span>"
        f"<span class='horse-card-title'>{h['馬名']}</span>"
        f"<span style='color:#94a3b8; font-size:13.5px;'>（{h.get('騎手','')} / {h.get('調教師','')}厩舎 / {int(h.get('人気',99))}番人気 / 枠{int(h.get('枠番',8))}）</span>"
        f"</div>"
        f"<div style='margin-bottom: 8px;'>{badges_html}</div>"
        f"<ul class='horse-card-list'>"
        f"<li><strong>指数マトリクス</strong>: F指数 {h['F指数']:.1f} (第{int(h['F_rank'])}位) / Fup2: {int(h['Fup'])}点 (第{int(h['Fup_rank'])}位) / arms: {h['arms']:.1f} (第{int(h['arms_rank'])}位) / tua: {h['tua']:.1f} (第{int(h['tua_rank'])}位) / S指数: {h['S指数']:.1f} (第{int(h['S_rank'])}位)</li>"
        f"<li><strong>調教時計</strong>: 坂路4F {h.get('坂路_4F','-')}s - 1F {h.get('坂路_1F','-')}s ({h.get('坂路_ラップ型','-')}) / W終い {h.get('wood_1F','-')}s</li>"
        f"<li><strong>判定ステータス</strong>: 動的スコア: {h['dynamic_score']:.1f} 点</li>"
        f"</ul>"
        f"</div>",
        unsafe_allow_html=True,
    )
