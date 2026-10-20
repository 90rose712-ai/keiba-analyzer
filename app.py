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
# 【全11指数底上げ＆色付け・坂路6大区分＆猛時計例外・芝ダ完全復元・全指数ソート・3連単マルチ版】
# ==============================================================================

st.set_page_config(
    page_title="競馬予想10 クッション値Vr - 完全統合システム",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    /* スマホでセレクトボックスをタップしてもキーボードを出さない設定 */
    div[data-baseweb="select"] input {
        inputmode: none !important;
        pointer-events: none !important;
    }
    .metric-container { display: flex; justify-content: space-around; background-color: #161b22; padding: 14px; border-radius: 10px; margin-bottom: 18px; border: 1px solid #30363d; }
    .date-header-badge { display: inline-flex; align-items: center; gap: 8px; background: linear-gradient(135deg, #1f2937 0%, #111827 100%); border: 1px solid #3b82f6; padding: 6px 16px; border-radius: 20px; color: #60a5fa; font-size: 14.5px; font-weight: bold; margin-bottom: 12px; }
    .race-type-banner { padding: 12px 18px; border-radius: 8px; margin-bottom: 14px; font-size: 15px; font-weight: bold; display: flex; align-items: center; justify-content: space-between; }
    .race-type-solid { background: linear-gradient(135deg, #064e3b 0%, #047857 100%); color: #ecfdf5; border: 1px solid #34d399; }
    .race-type-bonus { background: linear-gradient(135deg, #7c2d12 0%, #b45309 50%, #d97706 100%); color: #fef3c7; border: 2px solid #fde68a; box-shadow: 0 0 10px rgba(245, 158, 11, 0.5); }
    .race-type-recovery { background: linear-gradient(135deg, #831843 0%, #be123c 100%); color: #fff1f2; border: 1px solid #fb7185; box-shadow: 0 0 8px rgba(251, 113, 133, 0.4); }
    .race-type-chaos { background: linear-gradient(135deg, #374151 0%, #1f2937 100%); color: #e5e7eb; border: 1px solid #6b7280; }
    
    .recom-panel-go { background: linear-gradient(135deg, #111827 0%, #1f2937 100%); border: 2px solid #10b981; border-radius: 10px; padding: 16px 20px; margin-bottom: 20px; }
    .recom-title-go { font-size: 16px; font-weight: bold; color: #34d399; margin-bottom: 12px; border-bottom: 1px solid #374151; padding-bottom: 5px; }
    .recom-row { margin-bottom: 8px; font-size: 14.5px; line-height: 1.6; }
    .recom-block { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; padding: 10px 14px; margin-bottom: 10px; }
    .recom-label { font-weight: bold; color: #fbbf24; display: inline-block; font-size: 14px; }
    .recom-val-num { color: #ffffff; font-weight: bold; font-size: 15.5px; letter-spacing: 1px; }
    
    .horse-card { background-color: #161e2e; border-left: 5px solid #238636; padding: 14px 18px; border-radius: 8px; margin-bottom: 14px; border-top: 1px solid #30363d; border-right: 1px solid #30363d; border-bottom: 1px solid #30363d; }
    .horse-card-header { display: flex; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 8px; }
    .horse-card-title { font-size: 18px; font-weight: bold; color: #ffffff; }
    .race-badge-title { background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); color: #ffffff; font-weight: bold; font-size: 14px; padding: 2px 10px; border-radius: 6px; border: 1px solid #93c5fd; margin-right: 6px; }
    .horse-card-list { list-style-type: none; padding-left: 0; margin: 0; }
    .horse-card-list li { font-size: 13.5px; color: #c9d1d9; margin-bottom: 6px; line-height: 1.6; }
    .horse-card-list li::before { content: "• "; color: #58a6ff; font-weight: bold; }

    /* 印バッジ */
    .badge-mark-gtv { background: linear-gradient(135deg, #b45309 0%, #d97706 100%); color: #ffffff; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #fde68a; }
    .badge-mark-c { background: linear-gradient(135deg, #0891b2 0%, #06b6d4 100%); color: #ffffff; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #a5f3fc; }

    .badge-accel-on { background: linear-gradient(135deg, #059669 0%, #10b981 100%); color: #ffffff; font-weight: bold; font-size: 11.5px; padding: 2px 7px; border-radius: 4px; border: 1px solid #34d399; }
    .badge-accel-off { background-color: #374151; color: #9ca3af; font-size: 11.5px; padding: 2px 7px; border-radius: 4px; border: 1px solid #4b5563; }

    .badge-style-nige { background: linear-gradient(135deg, #e11d48 0%, #be123c 100%); color: #ffffff; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #fda4af; }
    .badge-style-senko { background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: #ffffff; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #93c5fd; }
    .badge-style-sashi { background: linear-gradient(135deg, #059669 0%, #047857 100%); color: #ffffff; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #6ee7b7; }
    .badge-style-oikomi { background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%); color: #ffffff; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #c4b5fd; }
    .badge-style-chudan { background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); color: #ffffff; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #7dd3fc; }
    .badge-style-other { background-color: #374151; color: #e5e7eb; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #6b7280; }

    /* 全指数色分けハイライトスタイル */
    .val-rank1-gold { color: #1a1000; background-color: #fcd34d; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #f59e0b; }
    .val-f-top { color: #ffffff; background-color: #ea580c; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #fb923c; }
    .val-s-top { color: #ffffff; background-color: #8b5cf6; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #c4b5fd; }
    .val-arms-top { color: #083344; background-color: #38bdf8; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #0284c7; }
    .val-tua-top { color: #022c22; background-color: #34d399; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #059669; }
    .val-course-top { color: #ffffff; background-color: #0d9488; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #2dd4bf; }
    .val-sub-top { color: #e0f2fe; background-color: #1e40af; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #60a5fa; }
    .val-normal { color: #cbd5e1; font-weight: normal; }

    /* 坂路調教秒数ハイライト */
    .highlight-han-a3 { color: #10b981; font-weight: bold; background-color: rgba(16, 185, 129, 0.15); padding: 1px 5px; border-radius: 4px; border: 1px solid #059669; }
    .highlight-han-a2 { color: #38bdf8; font-weight: bold; background-color: rgba(56, 189, 248, 0.15); padding: 1px 5px; border-radius: 4px; border: 1px solid #0284c7; }
    .highlight-han-a1 { color: #fcd34d; font-weight: bold; background-color: rgba(252, 211, 77, 0.15); padding: 1px 5px; border-radius: 4px; border: 1px solid #d97706; }
    .highlight-han-fast1f-super { color: #ef4444; font-weight: 900; background: rgba(239, 68, 68, 0.2); padding: 1px 6px; border-radius: 4px; border: 1px solid #f87171; }
    .highlight-han-fast1f-good { color: #f59e0b; font-weight: bold; background: rgba(245, 158, 11, 0.15); padding: 1px 6px; border-radius: 4px; border: 1px solid #fbbf24; }
    .highlight-han-fast4f { color: #38bdf8; font-weight: bold; }
    
    .badge-cushion-fit { display: inline-flex; align-items: center; background: linear-gradient(135deg, #059669 0%, #10b981 100%); color: #ffffff; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #34d399; }
    .badge-cushion-danger { display: inline-flex; align-items: center; background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%); color: #ffffff; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #f87171; }
    
    /* マークバッジ：文字が縦に潰れないよう横幅・高さを自動調整 */
    .badge-mark-honmei { display: inline-flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%); color: #ffffff; font-size: 12.5px; font-weight: 900; width: auto; height: auto; padding: 2px 8px; border-radius: 4px; border: 1px solid #fca5a5; margin-right: 6px; }
    .badge-mark-taikou { display: inline-flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: #ffffff; font-size: 12.5px; font-weight: 900; width: auto; height: auto; padding: 2px 8px; border-radius: 4px; border: 1px solid #93c5fd; margin-right: 6px; }
    .badge-mark-tanana { display: inline-flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #059669 0%, #047857 100%); color: #ffffff; font-size: 12.5px; font-weight: 900; width: auto; height: auto; padding: 2px 8px; border-radius: 4px; border: 1px solid #6ee7b7; margin-right: 6px; }
    .badge-mark-himo { display: inline-flex; align-items: center; justify-content: center; background-color: #374151; color: #f3f4f6; font-size: 12.5px; font-weight: bold; width: auto; height: auto; padding: 2px 8px; border-radius: 4px; border: 1px solid #6b7280; margin-right: 6px; }
    .badge-mark-ana { display: inline-flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #d97706 0%, #b45309 100%); color: #ffffff; font-size: 12.5px; font-weight: 900; width: auto; height: auto; padding: 2px 8px; border-radius: 4px; border: 1px solid #fde68a; margin-right: 6px; }
</style>
""",
    unsafe_allow_html=True,
)

PREV_HAN_SOLID_TRAINERS = ['堀', '中内田', '友道', '杉山晴', '田中博', '高柳大', '斎藤誠', '寺島', '岡田', '辻野', '平田', '鹿戸', '野中', '池添', '吉岡', '武英', '田中克', '四位', '森秀']
PREV_HAN_BOMB_TRAINERS = ['加藤征', '上村', '大竹', '牧', '杉浦', '武市', '和田正']
PREV_WOOD_DIRT_TRAINERS = ['稲垣', '小笠', '武英', '長谷川', '田中克', '本田']

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

    encodings = ['utf-8', 'utf-8-sig', 'cp932', 'shift-jis']
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

    if isinstance(source_obj, str) and os.path.exists(source_obj):
        return datetime.date.fromtimestamp(os.path.getmtime(source_obj))

    for pat in candidate_patterns:
        matched = glob.glob(pat)
        if matched:
            newest = max(matched, key=os.path.getmtime)
            return datetime.date.fromtimestamp(os.path.getmtime(newest))

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
        elif 'マ' in s or 'ﾏ' in s: return 'まくり'
        return s

    if s_rank == 1 and s_val >= 50.0: return '逃げ'
    elif s_rank <= 3: return '先行'
    elif f_rank <= 3 and s_rank >= 5: return '差し'
    elif f_rank <= 2 and s_rank >= 8: return '追込'
    elif s_rank <= 6: return '先行'
    else: return '中団'

def get_running_style_badge(style_str):
    if not style_str or pd.isnull(style_str) or style_str in ['-', '－', '不明', 'nan', '']:
        return ""
    s = str(style_str).strip()
    if '逃' in s: return "<span class='badge-style-nige'>🏃 逃げ</span>"
    elif '先' in s: return "<span class='badge-style-senko'>🐎 先行</span>"
    elif '差' in s: return "<span class='badge-style-sashi'>⚡ 差し</span>"
    elif '追' in s: return "<span class='badge-style-oikomi'>🔥 追込</span>"
    elif '後' in s: return "<span class='badge-style-oikomi'>後方</span>"
    elif '中' in s: return "<span class='badge-style-chudan'>中団</span>"
    elif 'マ' in s or 'ﾏ' in s: return "<span class='badge-style-other'>まくり</span>"
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

    if '≥10.5' in b or '10.5' in b:
        if sire in ['エピファネイア', 'キタサンブラック', 'イスラボニータ']:
            return f"<span class='badge-cushion-fit'>🟢 超高クッション特注 ({sire})</span>"
        if sire in ['キングカメハメハ', 'ビッグアーサー', 'レイデオロ', 'スワーヴリチャード', 'サートゥルナーリア', 'ゴールドシップ']:
            return f"<span class='badge-cushion-danger'>⚠️ 超高クッション危険 ({sire})</span>"
    return ""

# ==============================================================================
# ★ データロード＆結合エンジン（芝ダート完全復元・Fup自動補正・型安全性確保）
# ==============================================================================
def load_and_merge_all(f_index, f_sakaro, f_wood):
    index_patterns = [
        'data/当日全指数統合*.csv', '当日全指数統合*.csv',
        'data/2026_全11指数統合_出馬表*.csv', '2026_全11指数統合_出馬表*.csv',
        'data/出馬表_指数*.csv', '出馬表_指数*.csv', 'data/*指数*.csv', '*指数*.csv',
        'data/出馬表*.csv', '出馬表*.csv'
    ]
    index_src = f_index
    if index_src is None:
        matched = []
        for pat in index_patterns: matched.extend(glob.glob(pat))
        if matched: index_src = max(matched, key=os.path.getmtime)

    records = []
    lines = []
    
    df_raw = read_csv_robust(index_src, index_patterns)
    
    if not df_raw.empty and '場所R' in df_raw.columns:
        for _, row in df_raw.iterrows():
            race_id = str(row.get('場所R', '')).strip()
            dist_val = row.get('距離', 1600)
            umaban = row.get('馬番', 99)
            horse = clean_horse_name(row.get('馬名', ''))
            trainer = clean_horse_name(row.get('調教師', ''))
            jockey = clean_horse_name(row.get('騎手', ''))
            pop = row.get('人気順位', 99)
            raw_c = str(row.get('C', '')).strip()
            mark = row.get('印', '')

            # ★ 芝・ダート（track）の正確な復元：統合CSVの「C」列から取得
            if 'ダ' in raw_c:
                track = 'ダ'
                c_marker = ''
            elif '芝' in raw_c:
                track = '芝'
                c_marker = ''
            else:
                dist_tmp = int(re.sub(r'\D', '', str(dist_val))) if re.sub(r'\D', '', str(dist_val)).isdigit() else 1600
                track = 'ダ' if dist_tmp in [1150, 1300, 1700, 1900, 2100] else '芝'
                c_marker = raw_c if raw_c not in ['nan', 'None', ''] else ''

            dist_int = int(re.sub(r'\D', '', str(dist_val))) if re.sub(r'\D', '', str(dist_val)).isdigit() else 1600
            
            # ★ Fup2数値の取得（列名で取れない・0点の場合はCSV内の予備列から直接自動判定）
            fup = pd.to_numeric(row.get('Fup2'), errors='coerce')
            fup_rank = pd.to_numeric(row.get('Fup2順位'), errors='coerce')
            
            if pd.isnull(fup) or fup == 0:
                for c_idx in [12, 10, 11, 13]:
                    if len(row) > c_idx:
                        cand = pd.to_numeric(row.iloc[c_idx], errors='coerce')
                        if pd.notnull(cand) and 1 <= cand <= 7:
                            fup = cand
                            if len(row) > c_idx + 1:
                                fup_rank = pd.to_numeric(row.iloc[c_idx + 1], errors='coerce')
                            break
            
            fup = 0 if pd.isnull(fup) else int(fup)
            fup_rank = 99 if pd.isnull(fup_rank) else int(fup_rank)

            f_val = pd.to_numeric(row.get('F', 0.0), errors='coerce')
            f_rank = pd.to_numeric(row.get('F順位', 99), errors='coerce')
            arms_val = pd.to_numeric(row.get('ARM', 0.0), errors='coerce')
            arms_rank = pd.to_numeric(row.get('ARM順位', 99), errors='coerce')
            tua_val = pd.to_numeric(row.get('TUA', 0.0), errors='coerce')
            tua_rank = pd.to_numeric(row.get('TUA順位', 99), errors='coerce')
            s_val = pd.to_numeric(row.get('S', 0.0), errors='coerce')
            s_rank = pd.to_numeric(row.get('S順位', 99), errors='coerce')
            
            # 追加11指標
            hanro_cho_val = pd.to_numeric(row.get('坂路調', 0.0), errors='coerce')
            hanro_cho_rank = pd.to_numeric(row.get('坂路調順位', 99), errors='coerce')
            course_ren_val = pd.to_numeric(row.get('コース連', 0.0), errors='coerce')
            course_ren_rank = pd.to_numeric(row.get('コース連順位', 99), errors='coerce')
            ketsu_ren_val = pd.to_numeric(row.get('血統連', 0.0), errors='coerce')
            ketsu_ren_rank = pd.to_numeric(row.get('血統連順位', 99), errors='coerce')
            tokei_ketsu_val = pd.to_numeric(row.get('時計血', 0.0), errors='coerce')
            tokei_ketsu_rank = pd.to_numeric(row.get('時計血順位', 99), errors='coerce')
            hanro_ketsu_val = pd.to_numeric(row.get('坂路血', 0.0), errors='coerce')
            hanro_ketsu_rank = pd.to_numeric(row.get('坂路血順位', 99), errors='coerce')
            balance_val = pd.to_numeric(row.get('バランス', 0.0), errors='coerce')
            balance_rank = pd.to_numeric(row.get('バランス順位', 99), errors='coerce')
            
            finish = row.get('着順', None)
            sire = row.get('種牡馬', '')
            raw_style = row.get('前脚質', '')

            final_style = resolve_running_style(raw_style, '', s_rank, f_rank, s_val)

            if horse:
                records.append({
                    'race_id': race_id, 'track': track, 'dist': dist_int,
                    '馬番': int(float(umaban)) if pd.notnull(umaban) and str(umaban).replace('.','',1).isdigit() else 99,
                    '馬名': horse, 'C馬': c_marker, '印': str(mark).strip(),
                    '調教師': trainer, '騎手': jockey,
                    '種牡馬': str(sire).strip(),
                    '人気': int(float(pop)) if pd.notnull(pop) and str(pop).replace('.','',1).isdigit() else 99,
                    '着順': finish,
                    '脚質': final_style,
                    'Fup': fup,
                    'Fup_rank': fup_rank,
                    'S指数': s_val if not np.isnan(s_val) else 0.0,
                    'S_rank': int(s_rank) if not np.isnan(s_rank) else 99,
                    'F指数': f_val if not np.isnan(f_val) else 0.0,
                    'F_rank': int(f_rank) if not np.isnan(f_rank) else 99,
                    'arms': arms_val if not np.isnan(arms_val) else 0.0,
                    'arms_rank': int(arms_rank) if not np.isnan(arms_rank) else 99,
                    'tua': tua_val if not np.isnan(tua_val) else 0.0,
                    'tua_rank': int(tua_rank) if not np.isnan(tua_rank) else 99,
                    '坂路調': hanro_cho_val if not np.isnan(hanro_cho_val) else 0.0,
                    '坂路調順位': int(hanro_cho_rank) if not np.isnan(hanro_cho_rank) else 99,
                    'コース連': course_ren_val if not np.isnan(course_ren_val) else 0.0,
                    'コース連順位': int(course_ren_rank) if not np.isnan(course_ren_rank) else 99,
                    '血統連': ketsu_ren_val if not np.isnan(ketsu_ren_val) else 0.0,
                    '血統連順位': int(ketsu_ren_rank) if not np.isnan(ketsu_ren_rank) else 99,
                    '時計血': tokei_ketsu_val if not np.isnan(tokei_ketsu_val) else 0.0,
                    '時計血順位': int(tokei_ketsu_rank) if not np.isnan(tokei_ketsu_rank) else 99,
                    '坂路血': hanro_ketsu_val if not np.isnan(hanro_ketsu_val) else 0.0,
                    '坂路血順位': int(hanro_ketsu_rank) if not np.isnan(hanro_ketsu_rank) else 99,
                    'バランス': balance_val if not np.isnan(balance_val) else 0.0,
                    'バランス順位': int(balance_rank) if not np.isnan(balance_rank) else 99,
                })
    elif index_src is not None:
        for enc in ['cp932', 'shift-jis', 'utf-8-sig', 'utf-8']:
            try:
                if isinstance(index_src, str):
                    with open(index_src, 'r', encoding=enc, errors='ignore') as f:
                        lines = [l.strip() for l in f if l.strip()]
                else:
                    index_src.seek(0)
                    content = index_src.read()
                    if isinstance(content, bytes):
                        lines = [l.strip() for l in content.decode(enc, errors='ignore').splitlines() if l.strip()]
                    else:
                        lines = [l.strip() for l in content.splitlines() if l.strip()]
                if lines: break
            except Exception: continue

        reader = csv.reader(lines)
        for parts in reader:
            n = len(parts)
            if n < 8 or parts[0] in ['場所', '場所R', 'レースID', 'race_id']: continue

            race_id = parts[0]
            track_raw = str(parts[1]).strip() if n > 1 else '芝'
            dist_val = parts[2] if n > 2 else '1600'
            umaban = parts[3] if n > 3 else '99'
            horse_raw = parts[4] if n > 4 else ''
            c_marker = str(parts[5]).strip() if n > 5 else ''
            trainer = parts[6] if n > 6 else ''
            jockey = parts[7] if n > 7 else ''
            pop = parts[8] if n > 8 else '99'
            mark = parts[9] if n > 9 else ''
            
            track = 'ダ' if 'ダ' in track_raw else '芝'

            fup = pd.to_numeric(parts[12], errors='coerce') if n > 12 else 0
            fup_rank = pd.to_numeric(parts[13], errors='coerce') if n > 13 else 99
            
            s_val = 0.0
            s_rank = 99
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
            dist_int = int(re.sub(r'\D', '', str(dist_val))) if re.sub(r'\D', '', str(dist_val)).isdigit() else 1600

            if horse:
                records.append({
                    'race_id': race_id, 'track': track, 'dist': dist_int,
                    '馬番': int(umaban) if str(umaban).isdigit() else 99,
                    '馬名': horse, 'C馬': c_marker, '印': str(mark).strip(),
                    '調教師': clean_horse_name(trainer), '騎手': clean_horse_name(jockey),
                    '種牡馬': str(sire).strip(),
                    '人気': int(pop) if str(pop).isdigit() else 99,
                    '着順': finish, '脚質': final_style,
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
                    '坂路調': 0.0, '坂路調順位': 99, 'コース連': 0.0, 'コース連順位': 99,
                    '血統連': 0.0, '血統連順位': 99, '時計血': 0.0, '時計血順位': 99,
                    '坂路血': 0.0, '坂路血順位': 99, 'バランス': 0.0, 'バランス順位': 99
                })

    df_main = pd.DataFrame(records)
    if df_main.empty: return pd.DataFrame(), datetime.date.today()

    venue_dict = {
        '東': '東京', '中': '中山', '京': '京都', '阪': '阪神', '名': '中京',
        '小': '小倉', '新': '新潟', '福': '福島', '函': '函館', '札': '札幌',
    }

    def parse_race(rid):
        match = re.match(r'([^\d]+)(\d+)', str(rid))
        if match: return venue_dict.get(match.group(1), match.group(1)), int(match.group(2))
        return 'その他', 99

    df_main[['競馬場名', 'R番号']] = df_main['race_id'].apply(lambda x: pd.Series(parse_race(x)))
    df_main['race_uid'] = df_main['race_id']
    detected_date = extract_date_from_source(index_src, index_patterns, lines)
    df_main['total_horses'] = df_main.groupby('race_id')['馬番'].transform('count')
    df_main['枠番'] = df_main.apply(lambda r: get_jra_waku(r['馬番'], r['total_horses']), axis=1)

    # 坂路実測CSV読み込み
    sakaro_patterns = [
        'data/出馬表_坂路*.csv', '出馬表_坂路*.csv',
        'data/坂路、検証用*.csv', '坂路、検証用*.csv',
        'data/*坂路*.csv', '*坂路*.csv'
    ]
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

        # ★ 坂路6大区分（A1〜A3、B1〜B3）厳格判定関数
        def determine_sakaro_lap_type(r):
            t1 = r.get('坂路_4F')
            l1 = r.get('坂路_Lap1')
            l2 = r.get('坂路_Lap2')
            if pd.isnull(t1) or pd.isnull(l1) or pd.isnull(l2):
                return ''
            
            # 実質負荷基準: 4F <= 56.0s かつ 終い1F <= 13.0s
            t1_val = float(t1)
            l1_val = float(l1)
            l2_val = float(l2)
            if t1_val > 56.0 or l1_val > 13.0 or t1_val < 45.0:
                return '負荷不足'
                
            is_accel = l1_val < l2_val

            # A3: 終い11秒台加速ラップ（2F目が11秒台含む）
            if is_accel and l1_val <= 11.9:
                return 'A3'
            # B3: 2F11秒台減速ラップ（2F目または終い1Fが11秒台）
            if not is_accel and (l2_val <= 11.9 or l1_val <= 11.9):
                return 'B3'
            # A2: 終い2F12秒台加速ラップ
            if is_accel and (12.0 <= l2_val <= 12.9) and (12.0 <= l1_val <= 12.9):
                return 'A2'
            # B2: 終い2F12秒台減速ラップ
            if not is_accel and (12.0 <= l2_val <= 12.9) and (12.0 <= l1_val <= 12.9):
                return 'B2'
            # A1: 終いのみ12秒台加速ラップ（Lap2 >= 13.0, Lap1 12秒台）
            if is_accel and l2_val >= 13.0 and (12.0 <= l1_val <= 12.9):
                return 'A1'
            # B1: 2Fのみ12秒台減速ラップ（Lap2 12秒台, Lap1 >= 13.0）
            if not is_accel and (12.0 <= l2_val <= 12.9) and l1_val >= 13.0:
                return 'B1'
                
            return 'A1' if is_accel else 'B2'

        df_s_raw['坂路_ラップ型'] = df_s_raw.apply(determine_sakaro_lap_type, axis=1)
        df_s_best = (
            df_s_raw.dropna(subset=['坂路_4F']).sort_values('坂路_4F').drop_duplicates('clean_name', keep='first').copy()
        )
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

    # ★ TAKE TUBE動画の知見：4F 51.5s以下の猛時計減速例外判定
    df_main['is_super_fast_b'] = (
        (pd.to_numeric(df_main['坂路_4F'], errors='coerce') <= 51.5)
        & (pd.to_numeric(df_main['坂路_4F'], errors='coerce') >= 45.0)
        & (df_main['坂路_ラップ型'].isin(['B2', 'B3']))
    )
    df_main['is_complete_accel'] = df_main['坂路_完全加速'].fillna(False).astype(bool) | df_main['坂路_ラップ型'].isin(['A1', 'A2', 'A3'])
    df_main['accel_11s'] = (df_main['坂路_ラップ型'] == 'A3') | (df_main['is_complete_accel'] & (pd.to_numeric(df_main['坂路_1F'], errors='coerce') < 12.0))
    df_main['has_prev_han'] = False
    df_main['wood_1F'] = np.nan
    df_main['is_wood_accel'] = False

    def get_sakaro_sort_rank(row):
        score = 0
        l_type = str(row.get('坂路_ラップ型', ''))
        if l_type == 'A3': score += 1000
        elif l_type == 'A2': score += 800
        elif l_type == 'A1': score += 600
        elif row.get('is_super_fast_b', False): score += 550  # 猛時計減速を上位へ
        elif row.get('is_complete_accel', False): score += 500
        elif l_type == 'B3': score += 300
        elif l_type == 'B2': score += 200

        s_1f = pd.to_numeric(row.get('坂路_1F'), errors='coerce')
        if pd.notnull(s_1f):
            if s_1f <= 12.0: score += 150
            elif s_1f <= 12.4: score += 100
        return score

    df_main['sakaro_sort_score'] = df_main.apply(get_sakaro_sort_rank, axis=1)

    return df_main, detected_date

# ==============================================================================
# ★ データ読み込み実行 ＆ 型安全性確保
# ==============================================================================
st.sidebar.markdown('### 📁 CSVデータ読み込み')
with st.sidebar.expander('データ更新', expanded=False):
    up_index = st.file_uploader('出馬表・全11指数 CSV', type=['csv'], key='up_index')
    up_sakaro = st.file_uploader('坂路調教実測 CSV', type=['csv'], key='up_sakaro')
    up_wood = st.file_uploader('ウッド調教 CSV', type=['csv'], key='up_wood')

df, race_date = load_and_merge_all(up_index, up_sakaro, up_wood)

if df.empty:
    st.warning('⚠️ CSVデータが読み込まれていません。サイドバーから出走表・坂路・ウッドのCSVファイルを指定するか、リポジトリに配置してください。')
    st.stop()

# ★ 重要：TypeError防止（距離および各指数を確実に数値型へ変換）
df['dist'] = pd.to_numeric(df['dist'].astype(str).str.replace(r'\D', '', regex=True), errors='coerce').fillna(1600).astype(int)
for col_name in ['F指数', 'S指数', 'arms', 'tua', 'コース連', '血統連', '時計血', '坂路血', '坂路調', 'バランス', 'Fup']:
    if col_name in df.columns:
        df[col_name] = pd.to_numeric(df[col_name], errors='coerce').fillna(0.0)

# ==============================================================================
# ★ コース・クッション値・全11指数底上げスコア
# ==============================================================================
st.sidebar.markdown('### 芝馬場状態')
turf_condition = st.sidebar.selectbox('芝馬場状態', ['良', '稍重', '重', '不良'], index=0, label_visibility='collapsed')

venue_sort_order = ['東京', '中山', '京都', '阪神', '中京', '小倉', '新潟', '福島', '函館', '札幌']
existing_venues = [v for v in venue_sort_order if v in df['競馬場名'].unique()]
if 'active_venue' not in st.session_state or st.session_state['active_venue'] not in existing_venues:
    st.session_state['active_venue'] = existing_venues[0] if existing_venues else '東京'

default_cushions = {
    '札幌': 7.5, '函館': 7.4, '中京': 9.6, '新潟': 9.3, '東京': 9.3,
    '中山': 9.6, '京都': 10.0, '阪神': 9.4, '小倉': 9.2, '福島': 8.9,
}

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

df['cushion_badge_raw'] = df.apply(
    lambda r: evaluate_sire_cushion(r['種牡馬'], r['競馬場名'], r['dist'], current_band) if '芝' in str(r.get('track', '')) else '', axis=1
)
df['is_cushion_fit'] = df['cushion_badge_raw'].str.contains('特注')
df['is_cushion_danger'] = df['cushion_badge_raw'].str.contains('危険')

df['p1_hit_solid'] = (df['track'] == '芝') & (df['dist'].between(1500, 1800)) & (df['競馬場名'].isin(['東京', '中山', '京都', '阪神'])) & (df['F_rank'] <= 3) & (df['F指数'] >= 55) & (df['S_rank'] <= 3) & (df['S指数'] >= 40)
df['p2_dirt_tua'] = (df['track'] == 'ダ') & (df['S_rank'] <= 3) & (df['tua'] >= 190.0)
df['p3_short_local'] = ((df['dist'] <= 1400) | (df['競馬場名'].isin(['福島', '小倉', '函館']))) & (df['S_rank'] <= 3) & (df['坂路調順位'] <= 3)
df['roi_tua1_dirt_ana'] = (df['track'] == 'ダ') & (df['tua_rank'] == 1) & (df['人気'].between(4, 8))
df['roi_tua1_turf_ana'] = (df['track'] == '芝') & (df['tua_rank'] == 1) & (df['坂路調順位'] <= 3) & (df['人気'].between(4, 8))
df['roi_arm1_hanro1'] = (df['arms_rank'] == 1) & (df['坂路調順位'] == 1) & (df['人気'].between(3, 7))
df['roi_11s_ana'] = df['accel_11s'] & (df['人気'].between(3, 7))

# ★ 全統合動的スコア（6大区分・猛時計例外・バランス・コース連・前脚質・Fup2完全連動）
def calc_upgraded_dynamic_score(r):
    score = 0.0
    f_val = r.get('F指数', 0.0)
    f_rk = r.get('F_rank', 99)
    s_rk = r.get('S_rank', 99)
    c_rk = r.get('コース連順位', 99)
    k_rk = r.get('血統連順位', 99)
    hk_rk = r.get('坂路血順位', 99)
    tk_rk = r.get('時計血順位', 99)
    hc_rk = r.get('坂路調順位', 99)
    b_rk = r.get('バランス順位', 99)
    fup = r.get('Fup', 0)
    pop = r.get('人気', 99)
    l_type = str(r.get('坂路_ラップ型', ''))
    style = str(r.get('脚質', ''))
    is_sb = r.get('is_super_fast_b', False)

    # 1. 坂路ラップ区分加点 ＆ 動画知見（猛時計減速例外）
    if l_type == 'A3':
        score += 45.0
        if f_rk <= 3: score += 15.0  # A3×F上位の絶対軸ボーナス
        if '先' in style or '逃' in style: score += 15.0
    elif l_type == 'A2':
        score += 25.0
        if f_rk <= 3 and s_rk <= 3: score += 15.0  # 的中重視軸ボーナス
    elif l_type == 'A1':
        score += 15.0
    elif is_sb:
        # ★ TAKE TUBE動画知見：4F 51.5s以下の猛時計減速は減点を免除し特注加点
        score += 30.0
    elif l_type == 'B1':
        score -= 25.0  # 終いバテ減速は大幅割引
    elif l_type in ['B2', 'B3']:
        score -= 10.0  # 通常減速は軽微割引

    # 2. バランス順位（1位勝率トップ）＆ コース連
    if b_rk <= 3:
        score += 25.0
        if l_type in ['A2', 'A3']: score += 15.0  # バランス×加速シナジー
    elif b_rk >= 6:
        score -= 15.0

    if c_rk <= 3: score += 25.0
    elif c_rk >= 6: score -= 30.0  # コース不適合足切り

    # 3. 血統・調教補正
    if hk_rk <= 3 or tk_rk <= 3: score += 15.0
    if k_rk <= 3: score += 15.0
    if hc_rk <= 3: score += 15.0

    # 4. F/S/Fup基礎
    if f_rk == 1: score += 50.0
    elif f_rk <= 3: score += 30.0
    if s_rk <= 3: score += 30.0

    if fup == 7: score += 45.0
    elif fup >= 5: score += 30.0
    elif fup == 4: score += 15.0
    
    # 5. 危険な人気馬ペナルティ（実証：1〜3人気×減速×バランス6位以下は着外率52.1%）
    if pop <= 3:
        if l_type in ['B1', 'B2', 'B3'] and not is_sb and b_rk >= 6:
            score -= 40.0
        elif fup <= 1:
            score -= 35.0

    # 6. クッション値バイアス
    if r.get('is_cushion_fit', False): score += 35.0
    if r.get('is_cushion_danger', False): score -= 50.0
    
    return score

df['dynamic_score'] = df.apply(calc_upgraded_dynamic_score, axis=1)

# ==============================================================================
# ★ サイドバー：新ロジック検索フィルタ
# ==============================================================================
st.sidebar.markdown('---')
st.sidebar.markdown('### 🎯 新ロジック特注・回収率検索')
f_p1_solid = st.sidebar.checkbox(f"🎯 的中重視: 芝マイル中距離 F×S上位 ({int(df['p1_hit_solid'].sum())}頭)")
f_p2_dirt = st.sidebar.checkbox(f"🏜️ ダート堅実先行: S1-3位×TUA190+ ({int(df['p2_dirt_tua'].sum())}頭)")
f_p3_short = st.sidebar.checkbox(f"⚡ 短距離/ローカル先行×調教上位 ({int(df['p3_short_local'].sum())}頭)")
f_roi_dirt = st.sidebar.checkbox(f"💰 単回105%超: ダートTUA1位×4-8人気 ({int(df['roi_tua1_dirt_ana'].sum())}頭)")
f_roi_turf = st.sidebar.checkbox(f"💰 単回122%超: 芝TUA1位×坂路上位×穴 ({int(df['roi_tua1_turf_ana'].sum())}頭)")
f_roi_arm = st.sidebar.checkbox(f"💰 単回103%超: ARM1位×坂路1位×中穴 ({int(df['roi_arm1_hanro1'].sum())}頭)")
f_roi_11s = st.sidebar.checkbox(f"🔥 単回101%超: 終い11秒台加速×中穴 ({int(df['roi_11s_ana'].sum())}頭)")
f_complete_accel = st.sidebar.checkbox(f"⚡ 坂路完全加速(A1〜A3) ({int(df['is_complete_accel'].sum())}頭)")
f_super_b = st.sidebar.checkbox(f"🔥 猛時計減速特注(4F51.5s以下) ({int(df['is_super_fast_b'].sum())}頭)")
f_course_ren = st.sidebar.checkbox(f"🏰 コース連1〜3位 (適性合致) ({int((df['コース連順位'] <= 3).sum())}頭)")

active_filters = []
f_map = [
    (f_p1_solid, df['p1_hit_solid']),
    (f_p2_dirt, df['p2_dirt_tua']),
    (f_p3_short, df['p3_short_local']),
    (f_roi_dirt, df['roi_tua1_dirt_ana']),
    (f_roi_turf, df['roi_tua1_turf_ana']),
    (f_roi_arm, df['roi_arm1_hanro1']),
    (f_roi_11s, df['roi_11s_ana']),
    (f_complete_accel, df['is_complete_accel']),
    (f_super_b, df['is_super_fast_b']),
    (f_course_ren, df['コース連順位'] <= 3),
]
for act, srs in f_map:
    if act: active_filters.append(srs)

has_filter = len(active_filters) > 0
if has_filter:
    c_mask = pd.Series(True, index=df.index)
    for m in active_filters: c_mask = c_mask & m
    filtered_df = df[c_mask]
else:
    filtered_df = df.copy()

# ==============================================================================
# ★ メイン画面表示
# ==============================================================================
weekday_kanji = ['月', '火', '水', '木', '金', '土', '日']
w_str = weekday_kanji[race_date.weekday()]
st.markdown(
    f"<div class='date-header-badge'>📅 開催日: {race_date.year}年{race_date.month}月{race_date.day}日"
    f" ({w_str}) | クッション値Vr ({current_active_v}: {current_cushion_val} / {current_bin_name}) 稼働中</div>",
    unsafe_allow_html=True,
)

chosen_venue = st.radio('開催場選択', options=existing_venues, horizontal=True, label_visibility='collapsed')
st.session_state['active_venue'] = chosen_venue

v_df = filtered_df[filtered_df['競馬場名'] == chosen_venue]
races_in_v = v_df[['race_uid', 'race_id', 'R番号', 'track', 'dist']].drop_duplicates('race_uid').sort_values('R番号')

race_options = {}
for _, r_row in races_in_v.iterrows():
    r_horses = df[df['race_uid'] == r_row['race_uid']]
    
    p1_cnt = r_horses['p1_hit_solid'].sum()
    roi_cnt = r_horses['roi_tua1_dirt_ana'].sum() + r_horses['roi_tua1_turf_ana'].sum() + r_horses['roi_11s_ana'].sum()
    is_bonus = bool(((r_horses['F_rank'] <= 3) & (r_horses['arms_rank'] <= 3) & (r_horses['tua_rank'] <= 3)).sum() >= 3)
    
    if is_bonus:
        tag = '👑ボーナス'
    elif p1_cnt >= 2:
        tag = '🎯的中重視'
    elif roi_cnt >= 1 or (r_row['track'] == 'ダ' and r_horses['p2_dirt_tua'].sum() >= 2):
        tag = '🔥回収重視'
    else:
        tag = '⚖️標準'

    cnt_str = f" [{len(v_df[v_df['race_uid'] == r_row['race_uid']])}頭合致]" if has_filter else ""
    lbl = f"{tag} {r_row['R番号']}R ({r_row['track']}{r_row['dist']}m){cnt_str}"
    race_options[r_row['race_uid']] = lbl

if not race_options:
    st.warning("⚠️ 選択した開催場・フィルタ条件に合致するレースがありません。")
    st.stop()

selected_race_uid = st.selectbox(
    'レース選択',
    options=list(race_options.keys()),
    format_func=lambda x: race_options[x],
    label_visibility='collapsed',
)

race_df = df[df['race_uid'] == selected_race_uid].copy()
sorted_race = race_df.sort_values('dynamic_score', ascending=False)

# 的中重視・回収重視判定バナー
p1_c = race_df['p1_hit_solid'].sum()
p2_c = race_df['p2_dirt_tua'].sum()
p3_c = race_df['p3_short_local'].sum()
bonus_c = bool(((race_df['F_rank'] <= 3) & (race_df['arms_rank'] <= 3) & (race_df['tua_rank'] <= 3)).sum() >= 3)

if bonus_c:
    b_class = 'race-type-bonus'
    b_title = '👑 ボーナスレース（指数4冠・上位独占候補）'
    b_desc = '推奨券種: 3連複BOX / 3連単フォーメーション'
elif p1_c >= 2:
    b_class = 'race-type-solid'
    b_title = '🎯 的中重視レース（芝マイル中距離・先行能力合致）'
    b_desc = '推奨券種: 馬連・3連複フォーメーション（点数絞り込み）'
elif p2_c >= 2 or p3_c >= 2 or race_df['roi_tua1_dirt_ana'].sum() >= 1:
    b_class = 'race-type-recovery'
    b_title = '🔥 回収率重視レース（オッズ乖離・先行調教穴馬）'
    b_desc = '推奨券種: 単勝 / ワイド / 3連単マルチ（中穴爆弾狙い）'
else:
    b_class = 'race-type-chaos'
    b_title = '⚖️ 標準・混戦レース'
    b_desc = '推奨券種: ワイド / 3連複'

st.markdown(
    f"<div class='race-type-banner {b_class}'>"
    f"<div><strong>{b_title}</strong></div>"
    f"<div>{b_desc}</div>"
    f"</div>",
    unsafe_allow_html=True,
)

pick_honmei = sorted_race.iloc[0]
rem_axis = sorted_race[sorted_race['馬番'] != pick_honmei['馬番']]
pick_taikou = rem_axis.iloc[0] if not rem_axis.empty else pick_honmei

ana_cands = sorted_race[
    (sorted_race['馬番'] != pick_honmei['馬番'])
    & (sorted_race['馬番'] != pick_taikou['馬番'])
    & (
        sorted_race['roi_tua1_dirt_ana']
        | sorted_race['roi_tua1_turf_ana']
        | sorted_race['roi_11s_ana']
        | sorted_race['is_super_fast_b']  # 猛時計減速穴馬
        | (sorted_race['Fup'] >= 4)
        | sorted_race['is_complete_accel']
    )
]
pick_ana = ana_cands.iloc[0] if not ana_cands.empty else (sorted_race.iloc[2] if len(sorted_race) > 2 else pick_taikou)

danger_cands = race_df[
    (race_df['コース連順位'] >= 6)
    | (race_df['is_cushion_danger'])
    | ((race_df['人気'] <= 3) & (race_df['Fup'] <= 1))
    | ((race_df['人気'] <= 3) & (race_df['坂路_ラップ型'].isin(['B1', 'B2'])) & (~race_df['is_super_fast_b']) & (race_df['バランス順位'] >= 6))
    | ((race_df['track'] == 'ダ') & (race_df['dist'] <= 1400) & (~race_df['is_complete_accel']) & (~race_df['is_super_fast_b']))
]
pick_danger = danger_cands.iloc[0] if not danger_cands.empty else None

rec_col1 = [int(pick_honmei['馬番']), int(pick_taikou['馬番'])]
rec_col2 = list(rec_col1)
for u in sorted_race['馬番'].tolist():
    if int(u) not in rec_col2: rec_col2.append(int(u))
    if len(rec_col2) >= 4: break

rec_col3 = list(rec_col2)
if int(pick_ana['馬番']) not in rec_col3: rec_col3.append(int(pick_ana['馬番']))
for u in sorted_race['馬番'].tolist():
    if int(u) not in rec_col3: rec_col3.append(int(u))
    if len(rec_col3) >= 7: break

if pick_danger is not None:
    danger_info_str = f"{int(pick_danger['馬番'])}番 {pick_danger['馬名']} (コース連{int(pick_danger['コース連順位'])}位/消し要素該当)"
else:
    danger_info_str = "該当なし"

st.markdown(
    f"<div class='recom-panel-go'><div class='recom-title-go'>📋 推奨馬ピックアップ（新統合ロジック）</div>"
    f"<div class='recom-row'>🥇 <strong>本命・連軸</strong>: <span class='recom-val-num'>{int(pick_honmei['馬番'])}番 {pick_honmei['馬名']}</span>（F{int(pick_honmei['F_rank'])}位 / バランス{int(pick_honmei['バランス順位'])}位 / スコア:{pick_honmei['dynamic_score']:.1f}）</div>"
    f"<div class='recom-row'>🛡️ <strong>対抗・相手筆頭</strong>: <span class='recom-val-num'>{int(pick_taikou['馬番'])}番 {pick_taikou['馬名']}</span>（F{int(pick_taikou['F_rank'])}位 × S{int(pick_taikou['S_rank'])}位）</div>"
    f"<div class='recom-row'>💣 <strong>激走穴馬</strong>: <span class='recom-val-num'>{int(pick_ana['馬番'])}番 {pick_ana['馬名']}</span>（人気{int(pick_ana['人気'])}位 / TUA:{float(pick_ana['tua']):.1f} / 調教:{'猛時計特注' if pick_ana['is_super_fast_b'] else ('加速' if pick_ana['is_complete_accel'] else '-')}）</div>"
    f"<div class='recom-row'>⚠️ <strong>危険な人気馬・割引</strong>: {danger_info_str}</div></div>",
    unsafe_allow_html=True,
)

c1_str = ', '.join(map(str, rec_col1))
c2_str = ', '.join(map(str, rec_col2))
c3_str = ', '.join(map(str, rec_col3))

st.markdown(
    f"<div class='recom-panel-go'><div class='recom-title-go'>🎫 実戦買い目フォーメーション（的中・回収両立）</div>"
    f"<div class='recom-block'><strong>3連単フォーメーション (裏表・10点推奨)</strong>: 1・2着裏表 [{c1_str}] ⇄ 3着 [{c3_str}]</div>"
    f"<div class='recom-block'><strong>3連複フォーメーション</strong>: 1列目[{c1_str}] → 2列目[{c2_str}] → 3列目[{c3_str}]</div>"
    f"<div class='recom-block'><strong>単勝・複勝</strong>: {int(pick_honmei['馬番'])}番 (本線) / {int(pick_ana['馬番'])}番 (穴単複) | <strong>ワイド</strong>: {int(pick_honmei['馬番'])} - {int(pick_taikou['馬番'])}, {int(pick_ana['馬番'])}</div></div>",
    unsafe_allow_html=True,
)

# ==============================================================================
# ★ 出走馬カルテ＆全指標ソート
# ==============================================================================
st.markdown("### 🏇 出走馬詳細カルテ")

sort_col, _ = st.columns([3, 1])
with sort_col:
    sort_option = st.selectbox(
        "🔄 カルテ並び替え（全11指数＆調教ソート対応）",
        options=[
            '馬番順',
            '推奨度(動的スコア)順',
            '⚡ 坂路加速判定順(A3/A2/A1/猛時計優先)',
            'F指数順(降順)',
            'S指数順(降順)',
            'arms指数順(降順)',
            'tua指数順(降順)',
            'Fup得点順(降順)',
            'バランス順位(昇順)',
            '🏰 コース連順位(昇順)',
            '血統連順位(昇順)',
            '時計血順位(昇順)',
            '坂路血順位(昇順)',
            '坂路調順位(昇順)'
        ],
        index=0
    )

display_df = race_df.copy()
if sort_option == '馬番順':
    display_df = display_df.sort_values('馬番', ascending=True)
elif sort_option == '推奨度(動的スコア)順':
    display_df = display_df.sort_values('dynamic_score', ascending=False)
elif sort_option == '⚡ 坂路加速判定順(A3/A2/A1/猛時計優先)':
    display_df = display_df.sort_values(['sakaro_sort_score', '坂路_1F', '坂路_4F'], ascending=[False, True, True])
elif sort_option == 'F指数順(降順)':
    display_df = display_df.sort_values(['F_rank', 'F指数'], ascending=[True, False])
elif sort_option == 'S指数順(降順)':
    display_df = display_df.sort_values(['S_rank', 'S指数'], ascending=[True, False])
elif sort_option == 'arms指数順(降順)':
    display_df = display_df.sort_values(['arms_rank', 'arms'], ascending=[True, False])
elif sort_option == 'tua指数順(降順)':
    display_df = display_df.sort_values(['tua_rank', 'tua'], ascending=[True, False])
elif sort_option == 'Fup得点順(降順)':
    display_df = display_df.sort_values(['Fup', 'Fup_rank'], ascending=[False, True])
elif sort_option == 'バランス順位(昇順)':
    display_df = display_df.sort_values(['バランス順位', 'バランス'], ascending=[True, False])
elif sort_option == '🏰 コース連順位(昇順)':
    display_df = display_df.sort_values(['コース連順位', 'コース連'], ascending=[True, False])
elif sort_option == '血統連順位(昇順)':
    display_df = display_df.sort_values(['血統連順位', '血統連'], ascending=[True, False])
elif sort_option == '時計血順位(昇順)':
    display_df = display_df.sort_values(['時計血順位', '時計血'], ascending=[True, False])
elif sort_option == '坂路血順位(昇順)':
    display_df = display_df.sort_values(['坂路血順位', '坂路血'], ascending=[True, False])
elif sort_option == '坂路調順位(昇順)':
    display_df = display_df.sort_values(['坂路調順位', '坂路調'], ascending=[True, False])

# 指数3位以内色分けフォーマッター
def format_index_badge(val, rank, metric_type):
    if pd.isnull(val): return "-"
    v_str = f"{float(val):.1f}"
    r_int = int(rank) if pd.notnull(rank) else 99
    if r_int == 1: return f"<span class='val-rank1-gold'>{v_str}</span> (1位)"
    if r_int in [2, 3]:
        if metric_type == 'F': return f"<span class='val-f-top'>{v_str}</span> ({r_int}位)"
        elif metric_type == 'S': return f"<span class='val-s-top'>{v_str}</span> ({r_int}位)"
        elif metric_type == 'arms': return f"<span class='val-arms-top'>{v_str}</span> ({r_int}位)"
        elif metric_type == 'tua': return f"<span class='val-tua-top'>{v_str}</span> ({r_int}位)"
        elif metric_type == 'course': return f"<span class='val-course-top'>{v_str}</span> ({r_int}位)"
        else: return f"<span class='val-sub-top'>{v_str}</span> ({r_int}位)"
    return f
