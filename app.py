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
# 競馬予想10 クッション値Vr 完全統合Webアプリケーション【極限勝率ロジック搭載版】
# ARMS×Fup / ダートで食う / C馬判定 / 指数マトリクス / 調教完全加速 / クッション値特注 / 鉄壁神域
# ==============================================================================

st.set_page_config(
    page_title="競馬予想10 クッション値Vr - 完全統合システム",
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
    .recom-panel-chaos { background: linear-gradient(135deg, #1e111a 0%, #2e1020 100%); border: 2px solid #fb7185; border-radius: 10px; padding: 16px 20px; margin-bottom: 20px; }
    .recom-title-go { font-size: 16px; font-weight: bold; color: #34d399; margin-bottom: 12px; border-bottom: 1px solid #374151; padding-bottom: 5px; }
    .recom-title-chaos { font-size: 16px; font-weight: bold; color: #fb7185; margin-bottom: 12px; border-bottom: 1px solid #4c1d2e; padding-bottom: 5px; }
    .recom-row { margin-bottom: 8px; font-size: 14.5px; line-height: 1.6; }
    .recom-block { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; padding: 10px 14px; margin-bottom: 10px; }
    .recom-label { font-weight: bold; color: #fbbf24; display: inline-block; font-size: 14px; }
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
    .badge-accel-off { background-color: #374151; color: #9ca3af; font-size: 11.5px; padding: 2px 7px; border-radius: 4px; border: 1px solid #4b5563; }

    .badge-style-nige { background: linear-gradient(135deg, #e11d48 0%, #be123c 100%); color: #ffffff; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #fda4af; }
    .badge-style-senko { background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: #ffffff; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #93c5fd; }
    .badge-style-sashi { background: linear-gradient(135deg, #059669 0%, #047857 100%); color: #ffffff; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #6ee7b7; }
    .badge-style-oikomi { background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%); color: #ffffff; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #c4b5fd; }
    .badge-style-chudan { background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); color: #ffffff; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #7dd3fc; }
    .badge-style-other { background-color: #374151; color: #e5e7eb; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #6b7280; }

    .val-rank1-gold { color: #1a1000; background-color: #fcd34d; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #f59e0b; }
    .val-f-top { color: #ffffff; background-color: #ea580c; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #fb923c; }
    .val-arms-top { color: #083344; background-color: #38bdf8; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #0284c7; }
    .val-tua-top { color: #022c22; background-color: #34d399; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #059669; }
    .val-s-top { color: #ffffff; background-color: #8b5cf6; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #c4b5fd; }
    .val-normal { color: #cbd5e1; font-weight: normal; }

    .badge-c-gold { background: linear-gradient(135deg, #b45309 0%, #f59e0b 50%, #d97706 100%); color: #ffffff; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #fde68a; box-shadow: 0 1px 4px rgba(245, 158, 11, 0.4); }
    .badge-c-fake { background: linear-gradient(135deg, #475569 0%, #334155 100%); color: #fca5a5; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #ef4444; }
    .badge-arms-fup { background: linear-gradient(135deg, #0284c7 0%, #0369a1 50%, #075985 100%); color: #ffffff; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #7dd3fc; }
    .badge-dirt-eat { background: linear-gradient(135deg, #b45309 0%, #d97706 100%); color: #ffffff; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #fde68a; }
    .badge-cushion-horse-star { background: linear-gradient(135deg, #d97706 0%, #f59e0b 50%, #fbbf24 100%); color: #111827; font-weight: bold; font-size: 12px; padding: 2px 9px; border-radius: 6px; border: 1px solid #fef08a; }
    .badge-cushion-horse-danger { background: linear-gradient(135deg, #4b5563 0%, #1f2937 100%); color: #fca5a5; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #ef4444; }
    .badge-synergy { display: inline-flex; align-items: center; padding: 2px 8px; border-radius: 6px; font-weight: bold; font-size: 11.5px; }
    .badge-iron { background: linear-gradient(135deg, #FFE259 0%, #FFA751 100%); color: #1a1000; border: 1px solid #FFF275; }
    .badge-high { background: linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%); color: #ffffff; border: 1px solid #FF8E72; }
    .badge-bomb { background: linear-gradient(135deg, #EB3349 0%, #F45C43 100%); color: #ffffff; border: 1px solid #FFA07A; }
    
    /* ★ 極限ロジック・新設バッジ */
    .badge-ultimate-win { background: linear-gradient(135deg, #ff0844 0%, #ffb199 100%); color: #ffffff; font-weight: 900; font-size: 12.5px; padding: 3px 10px; border-radius: 6px; border: 1px solid #ffe3d8; box-shadow: 0 0 10px rgba(255, 8, 68, 0.6); }
    .badge-sss-crown { background: linear-gradient(135deg, #8a2387 0%, #e94057 50%, #f27121 100%); color: #ffffff; font-weight: bold; font-size: 12px; padding: 2px 9px; border-radius: 6px; border: 1px solid #ffccd2; }
    .badge-dirt-lead { background: linear-gradient(135deg, #b45309 0%, #d97706 100%); color: #ffffff; font-weight: bold; font-size: 12px; padding: 2px 9px; border-radius: 6px; border: 1px solid #fde68a; }

    .badge-target-win { background: linear-gradient(135deg, #e11d48 0%, #be123c 100%); color: #ffffff; font-weight: bold; font-size: 12px; padding: 2px 9px; border-radius: 6px; }
    .badge-target-axis { background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: #ffffff; font-weight: bold; font-size: 12px; padding: 2px 9px; border-radius: 6px; }
    .badge-danger-jockey-subtle { background-color: #262c36; color: #94a3b8; font-size: 11px; padding: 1px 6px; border-radius: 4px; border: 1px solid #334155; }
    .badge-tr-teppan { background: linear-gradient(135deg, #e11d48 0%, #be123c 100%); color: #ffffff; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #fda4af; }
    .badge-tr-shobu { background: linear-gradient(135deg, #d97706 0%, #b45309 100%); color: #ffffff; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #fde68a; }
    .badge-tr-tokuchu { background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); color: #ffffff; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #7dd3fc; }
    .badge-tr-danger { background: linear-gradient(135deg, #4b5563 0%, #1f2937 100%); color: #f87171; font-weight: bold; font-size: 11px; padding: 2px 7px; border-radius: 6px; border: 1px solid #ef4444; }
    .badge-cushion-fit { display: inline-flex; align-items: center; background: linear-gradient(135deg, #059669 0%, #10b981 100%); color: #ffffff; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #34d399; }
    .badge-cushion-danger { display: inline-flex; align-items: center; background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%); color: #ffffff; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #f87171; }
    .badge-prev-fast { background: linear-gradient(135deg, #d97706 0%, #b45309 100%); color: #ffffff; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #fcd34d; }
    .badge-prev-han { background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); color: #ffffff; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #7dd3fc; }

    .badge-mark-honmei { display: inline-flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%); color: #ffffff; font-size: 16px; font-weight: 900; width: 30px; height: 30px; border-radius: 6px; border: 1.5px solid #fca5a5; margin-right: 6px; }
    .badge-mark-taikou { display: inline-flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: #ffffff; font-size: 16px; font-weight: 900; width: 30px; height: 30px; border-radius: 6px; border: 1.5px solid #93c5fd; margin-right: 6px; }
    .badge-mark-tanana { display: inline-flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #059669 0%, #047857 100%); color: #ffffff; font-size: 16px; font-weight: 900; width: 30px; height: 30px; border-radius: 6px; border: 1.5px solid #6ee7b7; margin-right: 6px; }
    .badge-mark-himo { display: inline-flex; align-items: center; justify-content: center; background-color: #374151; color: #f3f4f6; font-size: 14.5px; font-weight: bold; width: 30px; height: 30px; border-radius: 6px; border: 1px solid #6b7280; margin-right: 6px; }
    .badge-mark-ana { display: inline-flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #d97706 0%, #b45309 100%); color: #ffffff; font-size: 16px; font-weight: 900; width: 30px; height: 30px; border-radius: 6px; border: 1.5px solid #fde68a; margin-right: 6px; }
</style>
""",
    unsafe_allow_html=True,
)

# 定数定義
DANGER_JOCKEYS_F3 = ['斎藤新', '小沢大仁', '丸山元気', '池添謙一', '松若風馬', '菊沢一樹', '田辺裕信', '横山琉人', '岩田康誠', '吉田隼人', '菅原明良', '富田暁', '三浦皇成', '浜中俊', '鮫島克駿']
DANGER_JOCKEYS_GENERAL = ['小林脩斗', '川端海翼', '黛弘人', '野中悠太', '遠藤汰月', '亀田温心', '水沼元輝', '丸田恭介', '河原田菜', '古川吉洋', '国分優作', '永島まな', '柴田裕一', '木幡初也', '原田和真', '柴田大知', '古川奈穂', '中井裕二', '石橋脩', '嶋田純次']

PREV_HAN_SOLID_TRAINERS = ['堀', '中内田', '友道', '杉山晴', '田中博', '高柳大', '斎藤誠', '寺島', '岡田', '辻野', '平田', '鹿戸', '野中', '池添', '吉岡', '武英', '田中克', '四位', '森秀']
PREV_HAN_BOMB_TRAINERS = ['加藤征', '上村', '大竹', '牧', '杉浦', '武市', '和田正']
PREV_WOOD_DIRT_TRAINERS = ['稲垣', '小笠', '武英', '長谷川', '田中克', '本田']

CUSHION_SPECIAL_HORSES = {
    'ウインベラーノ': {'best_bin': '7以下', 'label': '7以下巧者 (複85%)'},
    'ヨヒーン': {'best_bin': '7以下', 'label': '7以下巧者 (複85%/3勝)'},
    'タケルフォーカス': {'best_bin': '7以下', 'label': '7以下特注 (連100%)'},
    'ビーナスローズ': {'best_bin': '7以下', 'label': '7以下特注 (複100%)'},
    'カテリーナ': {'best_bin': '7以下', 'label': '7以下特化 (4勝)'},
    'グランテレーズ': {'best_bin': '7以下', 'label': '7以下巧者 (6好走)'},
    'カルプスペルシュ': {'best_bin': '7以下', 'label': '7以下特化 (4勝/複71%)'},
    'ワタシマツワ': {'best_bin': '7以下', 'label': '7以下巧者 (複83%)'},
    'アルマデオロ': {'best_bin': '7以下', 'label': '7以下特注 (連100%/3勝)'},
    'ハートホイップ': {'best_bin': '7以下', 'label': '7以下巧者 (複71%)'},
    'マリノトニトゥルス': {'best_bin': '8台', 'label': '8台絶対巧者 (連100%/3勝)'},
    'ジェルブロア': {'best_bin': '8台', 'label': '8台特化 (複83%)'},
    'ピューロマジック': {'best_bin': '8台', 'danger_bins': ['10台', '11以上'], 'label': '8台特注 (葵S/北九州記念)'},
    'エボルヴィング': {'best_bin': '8台', 'label': '8台巧者 (複80%)'},
    'ディオアステリア': {'best_bin': '8台', 'label': '8台巧者 (複80%)'},
    'ヨウシタンレイ': {'best_bin': '8台', 'label': '8台巧者 (5好走)'},
    'ロードトレゾール': {'best_bin': '8台', 'label': '8台巧者 (複80%)'},
    'ミュージシャン': {'best_bin': '8台', 'label': '8台特注 (連100%/3勝)'},
    'ジェニファー': {'best_bin': '8台', 'label': '8台巧者 (複80%)'},
    'クールベイビー': {'best_bin': '8台', 'label': '8台巧者 (複66%)'},
    'ユハンヌス': {'best_bin': '9台', 'label': '9台絶対巧者 (11好走)'},
    'リポサンテ': {'best_bin': '9台', 'label': '9台特化 (複81%)'},
    'オルグジェシダ': {'best_bin': '9台', 'label': '9台絶対連対 (9戦全連対)'},
    'オルトパラティウム': {'best_bin': '9台', 'label': '9台巧者 (複72%)'},
    'ジューンベロシティ': {'best_bin': '9台', 'label': '9台特化 (4勝/複90%)'},
    'スカイハイ': {'best_bin': '9台', 'label': '9台巧者 (10好走)'},
    'ティムール': {'best_bin': '9台', 'label': '9台巧者 (10好走)'},
    'ホウオウシェリー': {'best_bin': '9台', 'label': '9台巧者 (9好走)'},
    'タガノデュード': {'best_bin': '9台', 'label': '9台巧者 (9好走)'},
    'ディアドコス': {'best_bin': '9台', 'label': '9台巧者 (複72%)'},
    'スリールミニョン': {'best_bin': '10台', 'danger_bins': ['7以下', '8台', '9台'], 'label': '10台超特化 (4勝/複62%)'},
    'ロードガレリア': {'best_bin': '10台', 'label': '10台絶対連対 (6戦全連対)'},
    'ダンツウルス': {'best_bin': '10台', 'label': '10台絶対連対 (5戦全連対)'},
    'アイサンサン': {'best_bin': '10台', 'label': '10台特化 (4勝/複83%)'},
    'レッドエヴァンス': {'best_bin': '10台', 'label': '10台巧者 (7好走/複87%)'},
    'ビップディラン': {'best_bin': '10台', 'label': '10台巧者 (3勝/複66%)'},
    'アスクコモンタレヴ': {'best_bin': '10台', 'label': '10台特注 (5戦全好走)'},
    'チムグクル': {'best_bin': '10台', 'label': '10台特注 (5戦全好走)'},
    'モンテシート': {'best_bin': '10台', 'label': '10台巧者 (複83%)'},
    'ティタノマキア': {'best_bin': '10台', 'label': '10台特注 (5戦全好走)'},
    'ルージュスティーズ': {'best_bin': '11以上', 'label': '11以上超特化 (3戦全好走)'},
    'ラヴェル': {'best_bin': '11以上', 'label': '11以上特注 (2戦全好走)'},
    'インプロバイザー': {'best_bin': '11以上', 'label': '11以上特注 (連100%)'},
    'パープルパライソ': {'best_bin': '11以上', 'label': '11以上特注 (2戦全好走)'},
    'アブキールベイ': {'best_bin': '11以上', 'label': '11以上特注 (連100%)'},
    'サフィラ': {'best_bin': '11以上', 'label': '11以上巧者 (複66%)'},
    'テラステラ': {'best_bin': '11以上', 'label': '11以上巧者 (複66%)'},
    'オンザブルースカイ': {'best_bin': '11以上', 'label': '11以上巧者 (複66%)'},
    'セクシーマージュ': {'best_bin': '11以上', 'label': '11以上巧者 (複66%)'},
    'レジェンドシップ': {'best_bin': '11以上', 'label': '11以上巧者 (複66%)'},
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

    if s_rank == 1 and s_val >= 50.0:
        return '逃げ'
    elif s_rank <= 3:
        return '先行'
    elif f_rank <= 3 and s_rank >= 5:
        return '差し'
    elif f_rank <= 2 and s_rank >= 8:
        return '追込'
    elif s_rank <= 6:
        return '先行'
    else:
        return '中団'

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

def evaluate_course_training(r):
    track = str(r.get('track', ''))
    dist = pd.to_numeric(r.get('dist', 1600), errors='coerce')
    s_full = bool(r.get('坂路_完全加速', False))
    w_acc = bool(r.get('is_wood_accel', False))
    w_acc_val = pd.to_numeric(r.get('wood_accel', 0.0), errors='coerce')

    if 'ダ' in track and s_full:
        return pd.Series(["<span class='badge-cushion-fit'>🏜️ ダート坂路完全適合</span>", True])
    if '芝' in track and (1500 <= dist <= 1800) and w_acc and (w_acc_val >= 1.0):
        return pd.Series(["<span class='badge-cushion-fit'>🚀 マイルW加速適合</span>", True])
    if s_full or w_acc:
        return pd.Series(["<span class='badge-accel-on'>⚡ 調教加速適合</span>", True])
    return pd.Series(["", False])

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

def check_danger_jockey_info(r):
    jk = str(r.get('騎手', ''))
    f_rank = pd.to_numeric(r.get('F_rank', 99), errors='coerce')
    if (f_rank <= 3) and (jk in DANGER_JOCKEYS_F3): return True
    if jk in DANGER_JOCKEYS_GENERAL: return True
    return False

def check_cushion_special_horse(r, current_bin_name):
    h_name = clean_horse_name(r.get('馬名', ''))
    if h_name in CUSHION_SPECIAL_HORSES:
        meta = CUSHION_SPECIAL_HORSES[h_name]
        best_b = meta.get('best_bin')
        dang_b = meta.get('danger_bins', [])
        lbl = meta.get('label', '')
        if current_bin_name == best_b:
            return pd.Series([f"<span class='badge-cushion-horse-star'>🎯 {lbl}</span>", True, False])
        elif current_bin_name in dang_b:
            return pd.Series([f"<span class='badge-cushion-horse-danger'>⚠️ {current_bin_name}割引</span>", False, True])
    return pd.Series(["", False, False])

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

    if '≥10.5' in b or '10.5' in b:
        if sire in ['エピファネイア', 'キタサンブラック', 'イスラボニータ']:
            return f"<span class='badge-cushion-fit'>🟢 超高クッション特注 ({sire})</span>"
        if sire in ['キングカメハメハ', 'ビッグアーサー', 'レイデオロ', 'スワーヴリチャード', 'サートゥルナーリア', 'ゴールドシップ']:
            return f"<span class='badge-cushion-danger'>⚠️ 超高クッション危険 ({sire})</span>"
    return ""

# ==============================================================================
# ★ 安全化された派生列生成関数（極限ロジック完全実装）
# ==============================================================================
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

    mark_s = res['印'].astype(str) if '印' in res.columns else pd.Series('', index=res.index)
    res['is_gtv_marked'] = mark_s.str.contains(r'GTV|G|Ｔ|★|☆|特|注', na=False, regex=True)

    style_s = res['脚質'].astype(str) if '脚質' in res.columns else pd.Series('', index=res.index)
    res['is_style_senko'] = style_s.str.contains('先', na=False)
    res['is_style_sashi'] = style_s.str.contains('差', na=False)
    res['is_style_nige'] = style_s.str.contains('逃', na=False)
    res['is_style_oikomi'] = style_s.str.contains('追', na=False)
    res['is_style_front'] = res['is_style_senko'] | res['is_style_nige']
    res['is_style_back'] = style_s.str.contains('後|中|追', na=False)

    res['has_sharp_finishing'] = (
        (pd.to_numeric(res.get('坂路_1F', 99.0), errors='coerce').fillna(99.0) <= 12.2)
        | (pd.to_numeric(res.get('wood_1F', 99.0), errors='coerce').fillna(99.0) <= 11.4)
    )

    c_s = res['C馬'].astype(str) if 'C馬' in res.columns else pd.Series('', index=res.index)
    res['is_c_horse'] = c_s.str.contains('C|Ｃ', na=False)
    res['is_c_real_gold'] = res['is_c_horse'] & (res['Fup'] >= 4)
    res['is_c_fake_trap'] = res['is_c_horse'] & (res['Fup'] <= 3)

    res['has_prev_han'] = res['前日坂路あり'].fillna(False).astype(bool) if '前日坂路あり' in res.columns else False
    res['has_prev_han_fast'] = res['has_prev_han'] & (pd.to_numeric(res.get('前日坂路時計', 999.0), errors='coerce').fillna(999.0) <= 65.9)
    
    tr_s = res['調教師'].astype(str) if '調教師' in res.columns else pd.Series('', index=res.index)
    res['is_prev_han_solid'] = res['has_prev_han_fast'] & tr_s.apply(lambda t: any(x in str(t) for x in PREV_HAN_SOLID_TRAINERS)) & (res['人気'] <= 3)
    res['is_prev_han_bomb'] = res['has_prev_han_fast'] & tr_s.apply(lambda t: any(x in str(t) for x in PREV_HAN_BOMB_TRAINERS)) & (res['人気'] >= 6)
    
    prev_w_s = res['前日ウッドあり'].fillna(False).astype(bool) if '前日ウッドあり' in res.columns else False
    tk_s = res['track'].astype(str) if 'track' in res.columns else pd.Series('', index=res.index)
    res['is_prev_wood_dirt'] = prev_w_s & tk_s.str.contains('ダ', na=False) & tr_s.apply(lambda t: any(x in str(t) for x in PREV_WOOD_DIRT_TRAINERS))

    res['坂路_完全加速'] = res['坂路_完全加速'].fillna(False).astype(bool) if '坂路_完全加速' in res.columns else False
    res['坂路_穴トリガー'] = res['坂路_穴トリガー'].fillna(False).astype(bool) if '坂路_穴トリガー' in res.columns else False
    res['坂路_森加速'] = res['坂路_森加速'].fillna(False).astype(bool) if '坂路_森加速' in res.columns else False
    res['is_wood_accel'] = res['is_wood_accel'].fillna(False).astype(bool) if 'is_wood_accel' in res.columns else False

    res['調教加速'] = res['坂路_完全加速'] | res['is_wood_accel']
    res['is_s_top_accel'] = (res['S_rank'] <= 3) & res['調教加速']
    res['is_f1_accel'] = (res['F_rank'] == 1) & res['調教加速']
    res['is_dirt_wood_trap'] = tk_s.str.contains('ダ', na=False) & res['is_wood_accel'] & (~res['坂路_完全加速']) & (~res['is_prev_wood_dirt'])
    res['is_mile_wood_big_accel'] = (tk_s.str.contains('芝', na=False)) & (res['dist_num'].between(1500, 1800)) & (pd.to_numeric(res.get('wood_accel', 0.0), errors='coerce').fillna(0.0) >= 1.0)
    
    venue_s = res['競馬場名'].astype(str) if '競馬場名' in res.columns else pd.Series('', index=res.index)
    res['is_kyoto_sakaro_full'] = (venue_s == '京都') & res['坂路_完全加速']
    res['is_short_sakaro_full'] = (res['dist_num'] <= 1400) & res['坂路_完全加速']

    res['is_arms_fup_super'] = (res['arms_rank'] <= 3) & (res['Fup'] >= 5) & (res['F_rank'] == 1)
    res['is_arms_fup_solid'] = (res['arms_rank'] <= 3) & (res['Fup'] >= 4)
    res['is_sss_level'] = (res['F指数'] >= 70) & (res['arms'] >= 120) & (res['tua'] >= 200)
    res['is_iron_f72'] = res['F指数'] >= 72.0
    res['is_value_arms120'] = res['arms'] >= 120.0
    res['is_dirt_eat_super'] = tk_s.str.contains('ダ', na=False) & (res['tua'] >= 190.0) & (res['tua_rank'] <= 3) & (res['S_rank'] <= 3)
    res['is_dirt_tua190'] = tk_s.str.contains('ダ', na=False) & (res['tua'] >= 190.0) & (res['tua_rank'] <= 3)

    res['is_fup_axis'] = (res['Fup'].between(4, 7)) & (res['Fup_rank'] == 1)
    res['is_fup_trap'] = (res['Fup'] == 1) & (res['人気'] <= 3) & (res['F指数'] <= 72) & (~res['is_sss_level'])
    res['is_fup_kakugen'] = res['Fup'] == 7
    res['is_valley_trap'] = (res['人気'] <= 3) & (res['F_rank'] >= 4) & (~res['is_sss_level']) & (res['F指数'] <= 70)
    res['is_short_back_trap'] = (res['dist_num'] <= 1400) & res['is_style_back'] & (res['人気'] <= 3) & (~res['is_sss_level'])

    res['flag_fup6_s6'] = (res['Fup'] >= 6) & (res['Fup_rank'] == 1) & (res['S_rank'] <= 6)
    res['flag_fup6_f6'] = (res['Fup'] >= 6) & (res['Fup_rank'] == 1) & (res['F_rank'] <= 6)
    res['flag_fup6_sf_any'] = res['flag_fup6_s6'] | res['flag_fup6_f6']
    res['is_four_crown'] = (res['F_rank'] <= 2) & (res['Fup_rank'] <= 2) & (res['arms_rank'] <= 2) & (res['tua_rank'] <= 2)

    res['is_syn_iron'] = (res['F_rank'] == 1) & (res['arms_rank'] <= 3) & (pd.to_numeric(res.get('wood_1F', 99), errors='coerce').fillna(99) <= 11.5) & res['is_wood_accel']
    res['is_syn_high'] = ((res['F_rank'] == 1) | (res['F指数'] >= 66)) & (pd.to_numeric(res.get('wood_1F', 99), errors='coerce').fillna(99) <= 11.5) & res['is_wood_accel']
    res['is_syn_fup_sakaro'] = (res['Fup'] >= 5) & res['坂路_完全加速']
    res['is_syn_bomb'] = (
        (res['人気'] >= 6)
        & (res['Fup'] >= 4)
        & (res['調教加速'] | res['is_prev_han_bomb'])
        & (res['is_style_senko'] | res['is_style_sashi'])
        & (res['枠番'] <= 6)
    )
    res['is_syn_f1_rap'] = (res['F_rank'] == 1) & (
        ((pd.to_numeric(res.get('坂路_1F', 99), errors='coerce').fillna(99) <= 12.4) & res['坂路_完全加速'])
        | ((pd.to_numeric(res.get('wood_1F', 99), errors='coerce').fillna(99) <= 11.5) & res['is_wood_accel'])
    )

    # ★【新設】極限勝率・鉄壁神域ホース判定 (勝率40〜50%超・複勝率80〜85%超)
    sire_s = res['種牡馬'].astype(str) if '種牡馬' in res.columns else pd.Series('', index=res.index)
    res['is_elite_sire'] = sire_s.str.contains('キタサンブラック|キズナ|ドレフォン|エピファネイア|ロードカナロア', na=False)
    
    res['is_ultimate_win_horse'] = (
        (res['人気'] <= 2)
        & (res['F_rank'] == 1)
        & (res['F指数'] >= 66.0)
        & res['is_style_front']
        & (~res['is_fup_trap'])
        & (~res['is_valley_trap'])
        & (~res['is_dirt_wood_trap'])
    )
    
    # ダートTUA先行特注
    res['is_dirt_tua_front'] = (
        tk_s.str.contains('ダ', na=False)
        & (res['tua'] >= 180.0)
        & (res['tua_rank'] <= 3)
        & res['is_style_front']
    )

    same_waku = res['is_same_waku'] if 'is_same_waku' in res.columns else pd.Series(False, index=res.index)
    same_ub = res['is_same_ub_any'] if 'is_same_ub_any' in res.columns else pd.Series(False, index=res.index)
    res['waku_gold'] = same_waku & (res['F_rank'] <= 2)
    res['flag_sf7_himo'] = ((res['S_rank'] <= 7) | (res['F_rank'] <= 7)) & (res['調教加速'] | same_waku | same_ub | res['has_prev_han'])

    return res

# ==============================================================================
# ★ データロード＆結合エンジン
# ==============================================================================
def load_and_merge_all(f_index, f_sakaro, f_wood):
    index_patterns = [
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
    if index_src is not None:
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

            if not raw_style_full and not raw_style_short:
                for p in parts[20:]:
                    p_str = str(p).strip()
                    if p_str in ['逃げ', '先行', '差し', '中団', '追込', '後方', 'まくり', '逃', '先', '中', '差', '追', '後']:
                        raw_style_full = p_str
                        break

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

    exact_prev_day_int = int((detected_date - datetime.timedelta(days=1)).strftime('%Y%m%d'))

    # 坂路データ結合
    sakaro_patterns = ['data/出馬表_坂路*.csv', '出馬表_坂路*.csv', 'data/*坂路*.csv', '*坂路*.csv']
    df_s_raw = read_csv_robust(f_sakaro, sakaro_patterns)
    if not df_s_raw.empty:
        c_s_name = find_col_regex(df_s_raw, ['^馬名$', '^競走馬名$']) or df_s_raw.columns[4]
        df_s_raw['clean_name'] = df_s_raw[c_s_name].apply(clean_horse_name)

        c_s_date = find_col_regex(df_s_raw, ['^年月日$', '^日付$', '^date$']) or df_s_raw.columns[1]
        df_s_raw['clean_date'] = pd.to_numeric(df_s_raw[c_s_date].astype(str).str.extract(r'(\d+)')[0], errors='coerce')

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
                elif l1 >= 13.0 and 12.0 <= l2 <= 12.9: return 'B1'
            return ''

        df_s_raw['坂路_ラップ型'] = df_s_raw.apply(determine_sakaro_lap_type, axis=1)

        c_sun_sat_h = find_col_regex(df_s_raw, ['^土日坂路', '^週末坂路'])
        if c_sun_sat_h: df_s_raw['土日坂路最速'] = pd.to_numeric(df_s_raw[c_sun_sat_h], errors='coerce')

        df_s_prev_day = df_s_raw[df_s_raw['clean_date'] == exact_prev_day_int].copy()
        if not df_s_prev_day.empty:
            df_s_prev_best = (
                df_s_prev_day.dropna(subset=['坂路_4F'])
                .sort_values('坂路_4F')
                .drop_duplicates('clean_name', keep='first')
                .copy()
            )
            df_s_prev_best['前日坂路時計'] = df_s_prev_best['坂路_4F']
            df_s_prev_best['前日坂路あり'] = True
            df_prev_merged = df_s_prev_best[['clean_name', '前日坂路時計', '前日坂路あり']]
        else:
            df_prev_merged = pd.DataFrame(columns=['clean_name', '前日坂路時計', '前日坂路あり'])

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
        if '土日坂路最速' in df_s_best.columns: merge_cols.append('土日坂路最速')

        df_main = pd.merge(df_main, df_s_best[merge_cols], left_on='馬名', right_on='clean_name', how='left')
        if not df_prev_merged.empty:
            df_main = pd.merge(df_main, df_prev_merged, left_on='馬名', right_on='clean_name', how='left')

    if '坂路_4F' not in df_main.columns:
        df_main['坂路_4F'] = np.nan; df_main['坂路_1F'] = np.nan
        df_main['坂路_完全加速'] = False; df_main['坂路_穴トリガー'] = False; df_main['坂路_ラップ型'] = ''

    if '前日坂路時計' not in df_main.columns: df_main['前日坂路時計'] = np.nan
    if '前日坂路あり' not in df_main.columns: df_main['前日坂路あり'] = False
    df_main['前日坂路あり'] = df_main['前日坂路あり'].fillna(False).astype(bool)

    # ウッドデータ結合
    wood_patterns = ['data/出馬表_ウッド*.csv', '出馬表_ウッド*.csv', 'data/*ウッド*.csv', '*ウッド*.csv']
    df_w_raw = read_csv_robust(f_wood, wood_patterns)
    if not df_w_raw.empty:
        c_w_name = find_col_regex(df_w_raw, ['^馬名$', '^競走馬名$']) or df_w_raw.columns[4]
        df_w_raw['clean_name'] = df_w_raw[c_w_name].apply(clean_horse_name)

        c_w_5f = find_col_regex(df_w_raw, ['^5f$', '^５ｆ$', '^5Ｆ$']) or df_w_raw.columns[9]
        c_w_1f = find_col_regex(df_w_raw, ['^1f$', '^１ｆ$', '^1Ｆ$']) or df_w_raw.columns[13]
        c_w_l2 = find_col_regex(df_w_raw, ['^lap2$', '^ｌａｐ２$']) or df_w_raw.columns[18]
        c_w_l1 = find_col_regex(df_w_raw, ['^lap1$', '^ｌａｐ１$']) or df_w_raw.columns[19]

        df_w_raw['wood_5F'] = pd.to_numeric(df_w_raw[c_w_5f], errors='coerce')
        df_w_raw['wood_1F'] = pd.to_numeric(df_w_raw[c_w_1f], errors='coerce')
        df_w_raw['wood_Lap2'] = pd.to_numeric(df_w_raw[c_w_l2], errors='coerce')
        df_w_raw['wood_Lap1'] = pd.to_numeric(df_w_raw[c_w_l1], errors='coerce')

        c_prev_w = find_col_regex(df_w_raw, ['^前日ウッド'])
        df_w_raw['前日ウッドあり'] = True if c_prev_w else False

        df_w_best = df_w_raw.dropna(subset=['wood_1F']).sort_values('wood_1F').drop_duplicates('clean_name', keep='first').copy()
        df_w_best['wood_accel'] = df_w_best['wood_Lap2'] - df_w_best['wood_Lap1']
        df_w_best['is_wood_accel'] = (df_w_best['wood_accel'] > 0) & (df_w_best['wood_accel'].notna())

        w_merge_cols = ['clean_name', 'wood_5F', 'wood_1F', 'wood_accel', 'is_wood_accel']
        if '前日ウッドあり' in df_w_best.columns: w_merge_cols.append('前日ウッドあり')

        df_main = pd.merge(df_main, df_w_best[w_merge_cols], left_on='馬名', right_on='clean_name', how='left')

    if 'wood_1F' not in df_main.columns:
        df_main['wood_5F'] = np.nan; df_main['wood_1F'] = np.nan
        df_main['wood_accel'] = np.nan; df_main['is_wood_accel'] = False

    df_main['坂路_完全加速'] = df_main['坂路_完全加速'].fillna(False).astype(bool)
    df_main['坂路_穴トリガー'] = df_main['坂路_穴トリガー'].fillna(False).astype(bool)
    df_main['is_wood_accel'] = df_main['is_wood_accel'].fillna(False).astype(bool)

    if '土日坂路最速' not in df_main.columns: df_main['土日坂路最速'] = 999.0
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
    st.warning('⚠️ CSVデータが読み込まれていません。サイドバーから出走表・坂路・ウッドのCSVファイルを指定するか、data/フォルダに配置してください。')
    st.stop()

# 二重初期化保証
df = populate_all_derived_columns(df)

df[['course_training_badge', 'is_course_training_fit']] = df.apply(evaluate_course_training, axis=1)
df[['調教ステータス', '厩舎狙い目フラグ', 'tr_badge_html']] = df.apply(check_trainer_patterns, axis=1)
df['is_danger_jockey'] = df.apply(check_danger_jockey_info, axis=1)

# サイドバー: 馬場設定＆クッション値
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

df[['cushion_horse_badge', 'is_cushion_horse_fit', 'is_cushion_horse_danger']] = df.apply(
    lambda r: check_cushion_special_horse(r, current_bin_name), axis=1
)

df['cushion_badge_raw'] = df.apply(
    lambda r: evaluate_sire_cushion(r['種牡馬'], r['競馬場名'], r['dist'], current_band) if '芝' in str(r.get('track', '')) else '', axis=1
)
df['is_cushion_fit'] = df['cushion_badge_raw'].str.contains('特注')
df['is_cushion_danger'] = df['cushion_badge_raw'].str.contains('危険')

# 1着狙い・軸連対狙い・紐穴判定（勝率極限ロジック連動）
df['target_win'] = (
    (
        df['is_ultimate_win_horse']
        | df['is_prev_han_solid']
        | (df['is_f1_accel'] & df['has_sharp_finishing'])
        | ((df['F_rank'] == 1) & (df['人気'] <= 2) & (df['枠番'] <= 6) & df['is_style_front'])
        | df['is_arms_fup_super']
        | df['is_c_real_gold']
        | (df['is_iron_f72'] & (df['枠番'] <= 6) & (~df['is_cushion_danger']))
        | df['is_sss_level']
        | (df['flag_fup6_sf_any'] & (df['枠番'] <= 6))
        | (df['調教ステータス'] == '鉄板')
    )
    & (~df['is_fup_trap'])
    & (~df['is_c_fake_trap'])
    & (~df['is_valley_trap'])
    & (~df['is_dirt_wood_trap'])
    & (~df['is_short_back_trap'])
    & (~df['is_cushion_danger'])
    & (df['枠番'] <= 6)
)

df['target_axis'] = (
    (
        df['is_s_top_accel']
        | df['waku_gold']
        | df['is_dirt_tua_front']
        | df['is_prev_han_solid']
        | df['is_prev_wood_dirt']
        | df['is_mile_wood_big_accel']
        | df['is_arms_fup_solid']
        | df['is_dirt_eat_super']
        | df['is_c_real_gold']
        | df['is_fup_axis']
        | ((df['F_rank'] <= 2) & (df['arms_rank'] <= 3))
        | ((df['F_rank'] == 1) & (df['tua_rank'] <= 3))
        | ((df['Fup'] >= 4) & (df['F_rank'] <= 3))
        | df['is_four_crown']
        | (df['is_course_training_fit'] & (df['F_rank'] <= 4))
        | (df['調教ステータス'] == '勝負')
        | (df['is_iron_f72'] & ((df['枠番'] >= 7) | df['is_cushion_danger']))
    )
    & (df['is_style_senko'] | df['is_style_sashi'])
    & (~df['target_win'])
    & (~df['is_fup_trap'])
    & (~df['is_c_fake_trap'])
    & (~df['is_dirt_wood_trap'])
    & (~df['is_short_back_trap'])
)

df['target_himo'] = (
    ((df['人気'] >= 6) & df['調教加速'] & ((df['arms_rank'] <= 5) | (df['Fup'] >= 4) | (df['tua_rank'] <= 3)))
    | ((df['人気'] >= 6) & (df['人気'] <= 10) & df['坂路_穴トリガー'] & (df['Fup'] >= 4))
    | ((df['人気'] >= 5) & df['is_course_training_fit'])
    | ((df['人気'] >= 4) & (df['調教ステータス'] == '特注'))
    | df['is_syn_bomb']
    | df['is_prev_han_bomb']
    | df['is_prev_wood_dirt']
)

# ==============================================================================
# ★ サイドバー：フィルタ定義（極限ロジック検索の追加）
# ==============================================================================
st.sidebar.markdown('---')
st.sidebar.markdown('### 👑 極限勝率・鉄壁神域検索')
filter_ultimate_win = st.sidebar.checkbox(f"🏆 鉄壁神域 (1-2人気×先行×F66+) ({int(df['is_ultimate_win_horse'].sum())}頭)")
filter_sss_crown = st.sidebar.checkbox(f"✨ SSS級絶対神域 ({int(df['is_sss_level'].sum())}頭)")
filter_dirt_tua_lead = st.sidebar.checkbox(f"🏜️ ダート×TUA180+先行 ({int(df['is_dirt_tua_front'].sum())}頭)")

st.sidebar.markdown('---')
st.sidebar.markdown('### ⏱️ 前日坂路・調教検索')
filter_prev_han_all = st.sidebar.checkbox(f"🏇 前日坂路あり全頭 ({int(df['has_prev_han'].sum())}頭)")
filter_prev_han_fast = st.sidebar.checkbox(f"🔥 前日坂路65秒以下 ({int(df['has_prev_han_fast'].sum())}頭)")
filter_prev_han_solid = st.sidebar.checkbox(f"👑 前日坂路×王道上位人気 ({int(df['is_prev_han_solid'].sum())}頭)")
filter_prev_han_bomb = st.sidebar.checkbox(f"💣 前日坂路×加藤征等穴馬 ({int(df['is_prev_han_bomb'].sum())}頭)")
filter_prev_wood_dirt = st.sidebar.checkbox(f"🏜️ ダート×前日ウッド追い ({int(df['is_prev_wood_dirt'].sum())}頭)")

st.sidebar.markdown('---')
st.sidebar.markdown('### 👑 黄金シナジー・絶対軸馬')
syn_iron = st.sidebar.checkbox(f"💎 鉄板軸馬 ({int(df['is_syn_iron'].sum())}頭)")
syn_high = st.sidebar.checkbox(f"🔥 高確率軸馬 ({int(df['is_syn_high'].sum())}頭)")
filter_s_accel = st.sidebar.checkbox(f"👑 S1-3位×調教加速 最高安定軸 ({int(df['is_s_top_accel'].sum())}頭)")
filter_target_win = st.sidebar.checkbox(f"🥇 1着狙い ({int(df['target_win'].sum())}頭)")
filter_target_axis = st.sidebar.checkbox(f"🛡️ 軸・連対狙い ({int(df['target_axis'].sum())}頭)")
filter_waku_gold = st.sidebar.checkbox(f"👑 同枠×F1-2位 特注軸 ({int(df['waku_gold'].sum())}頭)")
filter_c_gold = st.sidebar.checkbox(f"👑 本物C馬 (Fup4+) ({int(df['is_c_real_gold'].sum())}頭)")
filter_arms_fup = st.sidebar.checkbox(f"👑 ARMS×Fup黄金軸 ({int(df['is_arms_fup_super'].sum())}頭)")
filter_iron_f72 = st.sidebar.checkbox(f"⚡ F指数>72 鉄板級 ({int(df['is_iron_f72'].sum())}頭)")
filter_fup_axis = st.sidebar.checkbox(f"👑 Fup1位(4〜7点) 最上位軸 ({int(df['is_fup_axis'].sum())}頭)")
syn_fup_sakaro = st.sidebar.checkbox(f"✨ Fup坂路完全 ({int(df['is_syn_fup_sakaro'].sum())}頭)")
syn_f1_rap = st.sidebar.checkbox(f"🔥 SSS級・究極ラップ ({int(df['is_syn_f1_rap'].sum())}頭)")
syn_bomb = st.sidebar.checkbox(f"💣 爆弾穴馬 ({int(df['is_syn_bomb'].sum())}頭)")

st.sidebar.markdown('### 🎯 狙い目・ノートブック抽出')
filter_mile_wood = st.sidebar.checkbox(f"🚀 マイル×W大加速 (+1.0s+) ({int(df['is_mile_wood_big_accel'].sum())}頭)")
filter_dirt_eat = st.sidebar.checkbox(f"🏜️ ダートで食う勝負馬 ({int(df['is_dirt_eat_super'].sum())}頭)")
filter_cushion_horse = st.sidebar.checkbox(f"🎯 クッション値特注馬 ({int(df['is_cushion_horse_fit'].sum())}頭)")
filter_value_arms = st.sidebar.checkbox(f"🚀 arms>120 期待値ホース ({int(df['is_value_arms120'].sum())}頭)")
filter_fup6_sf = st.sidebar.checkbox(f"🔥 Fup1位(6点+) × S/F6位内 ({int(df['flag_fup6_sf_any'].sum())}頭)")
filter_sf7_himo = st.sidebar.checkbox(f"🌪 SF7×加速/同枠 ({int(df['flag_sf7_himo'].sum())}頭)")
filter_target_himo = st.sidebar.checkbox(f"💣 紐穴・使者狙い ({int(df['target_himo'].sum())}頭)")

st.sidebar.markdown('### 🏛 厩舎勝負・特注抽出')
filter_tr_teppan = st.sidebar.checkbox(f"🔥 厩舎鉄板馬 ({(df['調教ステータス'] == '鉄板').sum()}頭)")
filter_tr_shobu = st.sidebar.checkbox(f"⚔️ 厩舎勝負気配馬 ({(df['調教ステータス'] == '勝負').sum()}頭)")
filter_tr_tokuchu = st.sidebar.checkbox(f"💎 厩舎特注穴馬 ({(df['調教ステータス'] == '特注').sum()}頭)")

st.sidebar.markdown('### ⚠️ 危険警告')
filter_dirt_wood = st.sidebar.checkbox(f"⚠️ ダート×ウッド追い切り消し ({int(df['is_dirt_wood_trap'].sum())}頭)")
filter_c_fake = st.sidebar.checkbox(f"⚠️ 偽C馬 (Fup3以下) ({int(df['is_c_fake_trap'].sum())}頭)")
filter_valley_trap = st.sidebar.checkbox(f"⚠️ 谷の形・地雷馬 ({int(df['is_valley_trap'].sum())}頭)")
filter_danger_jockey = st.sidebar.checkbox(f"⚠️ 危険騎手騎乗馬 ({int(df['is_danger_jockey'].sum())}頭)")
filter_fup_trap = st.sidebar.checkbox(f"⚠️ Fup1の罠馬 ({int(df['is_fup_trap'].sum())}頭)")
filter_tr_danger = st.sidebar.checkbox(f"⚠️ 厩舎危険調教馬 ({(df['調教ステータス'] == '危険').sum()}頭)")

if st.sidebar.button('🔄 最新データ再読み込み', use_container_width=True):
    st.session_state.clear()
    st.rerun()

# フィルタ条件の集約マスク生成
active_filter_masks = []
filter_map = [
    (filter_ultimate_win, df['is_ultimate_win_horse']),
    (filter_sss_crown, df['is_sss_level']),
    (filter_dirt_tua_lead, df['is_dirt_tua_front']),
    (filter_prev_han_all, df['has_prev_han']),
    (filter_prev_han_fast, df['has_prev_han_fast']),
    (filter_prev_han_solid, df['is_prev_han_solid']),
    (filter_prev_han_bomb, df['is_prev_han_bomb']),
    (filter_prev_wood_dirt, df['is_prev_wood_dirt']),
    (syn_iron, df['is_syn_iron']),
    (syn_high, df['is_syn_high']),
    (filter_s_accel, df['is_s_top_accel']),
    (filter_target_win, df['target_win']),
    (filter_target_axis, df['target_axis']),
    (filter_waku_gold, df['waku_gold']),
    (filter_c_gold, df['is_c_real_gold']),
    (filter_arms_fup, df['is_arms_fup_super']),
    (filter_iron_f72, df['is_iron_f72']),
    (filter_fup_axis, df['is_fup_axis']),
    (syn_fup_sakaro, df['is_syn_fup_sakaro']),
    (syn_f1_rap, df['is_syn_f1_rap']),
    (syn_bomb, df['is_syn_bomb']),
    (filter_mile_wood, df['is_mile_wood_big_accel']),
    (filter_dirt_eat, df['is_dirt_eat_super']),
    (filter_cushion_horse, df['is_cushion_horse_fit']),
    (filter_value_arms, df['is_value_arms120']),
    (filter_fup6_sf, df['flag_fup6_sf_any']),
    (filter_sf7_himo, df['flag_sf7_himo']),
    (filter_target_himo, df['target_himo']),
    (filter_tr_teppan, df['調教ステータス'] == '鉄板'),
    (filter_tr_shobu, df['調教ステータス'] == '勝負'),
    (filter_tr_tokuchu, df['調教ステータス'] == '特注'),
    (filter_dirt_wood, df['is_dirt_wood_trap']),
    (filter_c_fake, df['is_c_fake_trap']),
    (filter_valley_trap, df['is_valley_trap']),
    (filter_danger_jockey, df['is_danger_jockey']),
    (filter_fup_trap, df['is_fup_trap']),
    (filter_tr_danger, df['調教ステータス'] == '危険'),
]

for is_active, m_series in filter_map:
    if is_active:
        active_filter_masks.append(m_series)

has_active_filter = len(active_filter_masks) > 0
if has_active_filter:
    combined_filter_mask = pd.Series(True, index=df.index)
    for m in active_filter_masks:
        combined_filter_mask = combined_filter_mask & m
    filtered_df = df[combined_filter_mask]
else:
    filtered_df = df.copy()

# ==============================================================================
# ★ メインヘッダー＆開催場
# ==============================================================================
weekday_kanji = ['月', '火', '水', '木', '金', '土', '日']
w_str = weekday_kanji[race_date.weekday()]
st.markdown(
    f"<div class='date-header-badge'>📅 開催日時: {race_date.year}年{race_date.month}月{race_date.day}日"
    f" ({w_str}) | クッション値Vr ({current_active_v}: {current_cushion_val} / {current_bin_name}) 稼働中</div>",
    unsafe_allow_html=True,
)

with st.expander("🏆 コース×種牡馬 データブック最強マトリクス ＆ 危険リスト", expanded=False):
    st.markdown("### 🔥 最重要・狙い目 上位20")
    col_rk1, col_rk2 = st.columns(2)
    with col_rk1:
        st.markdown("""
        1. **阪神芝1800外 × キズナ** (9.5-9.9) - 勝19.6% / 単回421[cite: 77, 89]
        2. **東京芝1600 × エピファネイア** (9.5-9.9) - 勝13.3% / 単回277[cite: 39, 89]
        3. **東京芝1400 × モーリス** (9.5-9.9) - 勝10.1% / 単回408[cite: 38, 89]
        4. **東京芝1800 × ディープインパクト** (9.5-9.9) - 勝15.8% / 単回228[cite: 40, 89]
        5. **東京芝2000 × キズナ** (8.6-9.4) - 勝19.7% / 単回200[cite: 41, 89]
        6. **中京芝2000 × ディープインパクト** (8.6-9.4) - 勝18.0% / 単回178[cite: 58, 89]
        7. **東京芝1600 × イスラボニータ** (8.6-9.4) - 勝10.5% / 単回350[cite: 39, 89]
        8. **東京芝2000 × エピファネイア** (8.6-9.4) - 勝15.3% / 単回149[cite: 41, 89]
        9. **函館芝1800 × キズナ** (≤8.5低) - 勝17.7% / 単回143[cite: 19, 89]
        10. **小倉芝1200 × ダイワメジャー** (9.5-9.9) - 勝13.6% / 単回173[cite: 85, 89]
        """)
    with col_rk2:
        st.markdown("""
        11. **札幌芝2000 × オルフェーヴル** (≤8.5低) - 勝15.8% / 単回136[cite: 14, 89]
        12. **東京芝1400 × ロードカナロア** (8.6-9.4) - 勝15.6% / 単回123[cite: 38, 89]
        13. **阪神芝1600外 × ルーラーシップ** (8.6-9.4) - 勝20.0% / 単回156[cite: 76, 89]
        14. **東京芝1600 × モーリス** (9.5-9.9) - 勝11.1% / 単回100[cite: 39, 89]
        15. **阪神芝2000内 × キズナ** (8.6-9.4) - 勝11.8% / 単回152[cite: 78, 89]
        16. **東京芝1600 × スクリーンヒーロー** (8.6-9.4) - 勝9.9% / 単回72[cite: 39, 89]
        17. **小倉芝1200 × ビッグアーサー** (8.6-9.4) - 勝12.2% / 単回131[cite: 85, 89]
        18. **中京芝1600 × ロードカナロア** (10.0-10.4) - 勝14.8% / 単回133[cite: 57, 89]
        19. **福島芝1200 × ビッグアーサー** (8.6-9.4) - 勝13.2% / 単回87[cite: 23, 89]
        20. **札幌芝1200 × ロードカナロア** (≤8.5低) - 勝15.0% / 単回121[cite: 11, 89]
        """)

    st.markdown("### ⚠️ RISK LIST 危険・割引対象 上位20")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.markdown("""
        1. **中山芝2000 × ダノンバラード** (9.5-9.9) - 複勝率0.0%[cite: 50, 90]
        2. **東京芝2000 × ルーラーシップ** (9.5-9.9) - 複勝率9.1%[cite: 41, 90]
        3. **小倉芝1200 × ジャスタウェイ** (8.6-9.4) - 複勝率2.9%[cite: 85, 90]
        4. **東京芝1400 × シルバーステート** (8.6-9.4) - 複勝率4.7%[cite: 38, 90]
        5. **東京芝1600 × ゴールドシップ** (8.6-9.4) - 複勝率4.5%[cite: 39, 90]
        6. **小倉芝1200 × ヴィクトワールピサ** (8.6-9.4) - 複勝率4.8%[cite: 85, 90]
        7. **東京芝1800 × ルーラーシップ** (9.5-9.9) - 複勝率10.5%[cite: 40, 90]
        8. **阪神芝2000内 × ゴールドシップ** (8.6-9.4) - 複勝率10.0%[cite: 78, 90]
        9. **東京芝1600 × エイシンフラッシュ** (8.6-9.4) - 複勝率7.3%[cite: 39, 90]
        10. **東京芝2000 × オルフェーヴル** (8.6-9.4) - 複勝率13.2%[cite: 41, 90]
        """)
    with col_d2:
        st.markdown("""
        11. **福島芝2000 × ルーラーシップ** (8.6-9.4) - 複勝率4.7%[cite: 25, 90]
        12. **新潟芝1400内 × リオンディーズ** (8.6-9.4) - 複勝率6.7%[cite: 30, 90]
        13. **東京芝2400 × ゴールドシップ** (9.5-9.9) - 複勝率11.1%[cite: 43, 90]
        14. **小倉芝1800 × ルーラーシップ** (9.5-9.9) - 複勝率10.0%[cite: 86, 90]
        15. **阪神芝1800外 × ハービンジャー** (9.5-9.9) - 複勝率10.0%[cite: 77, 90]
        16. **東京芝1600 × サトノクラウン** (8.6-9.4) - 複勝率9.7%[cite: 39, 90]
        17. **福島芝1200 × マツリダゴッホ** (8.6-9.4) - 複勝率5.9%[cite: 23, 90]
        18. **東京芝1600 × シルバーステート** (9.5-9.9) - 複勝率8.9%[cite: 90, 112]
        19. **福島芝1200 × カレンブラックヒル** (8.6-9.4) - 複勝率9.7%[cite: 23, 90]
        20. **中京芝2000 × オルフェーヴル** (8.6-9.4) - 複勝率15.2%[cite: 58, 90]
        """)

if has_active_filter:
    st.info(f"🔍 狙い目フィルタ適用中: 合計 {len(filtered_df)} 頭が該当しています（該当馬が存在するレースのみ抽出）")

chosen_venue = st.radio('開催場選択', options=existing_venues, horizontal=True, label_visibility='collapsed')
st.session_state['active_venue'] = chosen_venue

v_df = filtered_df[filtered_df['競馬場名'] == chosen_venue]
races_in_v = v_df[['race_uid', 'race_id', 'R番号', 'track', 'dist']].drop_duplicates('race_uid').sort_values('R番号')

race_options = {}
for _, r_row in races_in_v.iterrows():
    r_horses = df[df['race_uid'] == r_row['race_uid']]
    f1_h = r_horses[r_horses['F_rank'] == 1]
    f1_val = f1_h['F指数'].values[0] if not f1_h.empty else 0
    is_bonus = bool(((r_horses['F_rank'] <= 3) & (r_horses['arms_rank'] <= 3) & (r_horses['tua_rank'] <= 3)).sum() >= 3)
    has_ultimate = bool(r_horses['is_ultimate_win_horse'].any())
    tag = '👑極限' if has_ultimate else ('👑ボーナス' if is_bonus else ('🎯狙' if f1_val >= 60 else '🔥荒'))

    matched_cnt = len(v_df[v_df['race_uid'] == r_row['race_uid']]) if has_active_filter else len(r_horses)
    cnt_str = f" [{matched_cnt}頭合致]" if has_active_filter else ""
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
race_df = populate_all_derived_columns(race_df)

is_turf_race = bool(race_df['track'].str.contains('芝').any()) if not race_df.empty else False
race_df['cushion_badge_raw'] = race_df.apply(
    lambda r: evaluate_sire_cushion(r['種牡馬'], r['競馬場名'], r['dist'], current_band) if is_turf_race else '', axis=1
)
race_df['is_cushion_fit'] = race_df['cushion_badge_raw'].str.contains('特注')
race_df['is_cushion_danger'] = race_df['cushion_badge_raw'].str.contains('危険')

cur_track_type = race_df['track'].iloc[0] if not race_df.empty else '芝'
cur_dist_val = int(re.sub(r'\D', '', str(race_df['dist'].iloc[0]))) if not race_df.empty else 1600

# ==============================================================================
# ★ 動的優先度スコアリング（勝率極限ロジック完全補正）
# ==============================================================================
def calculate_dynamic_priority_score(r):
    score = 0.0
    f_r, s_r, a_r, t_r = r.get('F_rank', 99), r.get('S_rank', 99), r.get('arms_rank', 99), r.get('tua_rank', 99)
    f_val, arms_val, tua_val = r.get('F指数', 0.0), r.get('arms', 0.0), r.get('tua', 0.0)
    c_fit, c_dang = bool(r.get('is_cushion_fit', False)), bool(r.get('is_cushion_danger', False))
    sakaro_full, wood_acc = bool(r.get('坂路_完全加速', False)), bool(r.get('is_wood_accel', False))
    tr_stat = str(r.get('調教ステータス', ''))
    waku_val = r.get('枠番', 8)
    prev_han = bool(r.get('has_prev_han', False))

    style = str(r.get('脚質', ''))
    is_senko, is_nige, is_sashi, is_back = '先' in style, '逃' in style, '差' in style, ('後' in style or '中' in style or '追' in style)

    # 脚質バイアス（前受け優遇・追込厳罰）
    if cur_dist_val <= 1400:
        if is_senko: score += 35.0
        elif is_nige: score += 30.0
        elif is_back: score -= 35.0
    elif 1500 <= cur_dist_val <= 1800:
        if is_senko: score += 30.0
        elif is_sashi: score += 15.0
        elif is_back: score -= 20.0
    elif cur_dist_val >= 1900:
        if is_senko: score += 35.0
        elif is_sashi: score += 20.0
        elif is_back: score -= 25.0

    # ★ 極限神域ホース判定ボーナス (+120点)
    if r.get('is_ultimate_win_horse', False): score += 120.0
    if r.get('is_sss_level', False): score += 80.0
    if r.get('is_dirt_tua_front', False): score += 65.0
    if r.get('is_elite_sire', False) and is_senko: score += 25.0

    if f_val >= 72.0: score += 65.0 if is_senko else 45.0
    elif f_val >= 66.0: score += 40.0
    
    if r.get('is_prev_han_solid', False): score += 60.0
    elif r.get('has_prev_han_fast', False): score += 30.0
    elif prev_han: score += 15.0

    if r.get('is_f1_accel', False): score += 55.0
    if r.get('is_s_top_accel', False): score += 45.0
    if r.get('target_win', False): score += 45.0
    if r.get('is_arms_fup_super', False): score += 60.0
    if r.get('is_c_real_gold', False): score += 40.0

    if waku_val in [1, 2, 3]: score += 15.0
    elif waku_val in [7, 8]: score -= 25.0

    if tr_stat == '鉄板': score += 45.0
    elif tr_stat == '勝負': score += 30.0
    elif tr_stat == '特注': score += 20.0
    elif tr_stat == '危険': score -= 45.0

    # 負けトリガー・地雷要因の減点
    if r.get('is_dirt_wood_trap', False): score -= 70.0
    if r.get('is_valley_trap', False): score -= 60.0
    if r.get('is_c_fake_trap', False): score -= 50.0
    if c_dang: score -= 45.0
    if r.get('is_fup_trap', False): score -= 70.0
    if r.get('is_danger_jockey', False): score -= 25.0

    return score

race_df['dynamic_score'] = race_df.apply(calculate_dynamic_priority_score, axis=1)
sorted_dynamic = race_df.sort_values('dynamic_score', ascending=False)

def get_horse_hierarchy_rank(r):
    p_rank = 0
    if r.get('is_ultimate_win_horse', False): p_rank += 2000
    elif r.get('is_sss_level', False): p_rank += 1500
    elif r.get('F指数', 0) >= 72.0: p_rank += 1000
    elif r.get('F_rank', 99) == 1: p_rank += 500
    style = str(r.get('脚質', ''))
    if '先' in style: p_rank += 300
    elif '差' in style: p_rank += 150
    if bool(r.get('is_cushion_fit', False)): p_rank += 150
    if bool(r.get('is_cushion_danger', False)): p_rank -= 400
    if str(r.get('調教ステータス')) == '鉄板' or bool(r.get('is_prev_han_solid')): p_rank += 120
    if r.get('枠番', 8) <= 6: p_rank += 50
    return p_rank

sorted_dynamic['hierarchy_rank'] = sorted_dynamic.apply(get_horse_hierarchy_rank, axis=1)
hierarchy_sorted = sorted_dynamic.sort_values(['hierarchy_rank', 'dynamic_score'], ascending=[False, False])

pick_win_horse = hierarchy_sorted.iloc[0]
axis_cands = hierarchy_sorted[hierarchy_sorted['馬番'] != pick_win_horse['馬番']]
pick_axis_horse = axis_cands.iloc[0] if not axis_cands.empty else pick_win_horse

himo_cands = sorted_dynamic[
    (sorted_dynamic['人気'] >= 4)
    & (
        sorted_dynamic['target_himo'] | sorted_dynamic['is_syn_bomb'] | sorted_dynamic['flag_sf7_himo']
        | sorted_dynamic['is_prev_han_bomb'] | sorted_dynamic['is_prev_wood_dirt'] | (sorted_dynamic['調教ステータス'] == '特注')
        | (sorted_dynamic['arms'] >= 115)
    )
]
pick_himo_horse = himo_cands.iloc[0] if not himo_cands.empty else (sorted_dynamic.iloc[-1] if len(sorted_dynamic) > 2 else pick_axis_horse)

danger_cands = race_df[
    (race_df['人気'] <= 5)
    & (
        race_df['is_fup_trap'] | race_df['is_c_fake_trap'] | race_df['is_valley_trap']
        | race_df['is_dirt_wood_trap'] | race_df['is_cushion_danger'] | (race_df['調教ステータス'] == '危険')
        | (race_df['is_style_back'] & (race_df['dist_num'] <= 1400))
    )
]
pick_danger_horse = danger_cands.iloc[0] if not danger_cands.empty else None

# フォーメーション構成
rec_c1 = [pick_win_horse['馬番']]
rec_c2 = [pick_win_horse['馬番'], pick_axis_horse['馬番']]
for u in hierarchy_sorted['馬番'].tolist():
    if u not in rec_c2: rec_c2.append(u)
    if len(rec_c2) >= 4: break

rec_c3 = list(rec_c2)
for u in sorted_dynamic['馬番'].tolist():
    if u not in rec_c3: rec_c3.append(u)
    if len(rec_c3) >= 7: break

bet_marks_dict = {}
bet_marks_dict[int(pick_win_horse['馬番'])] = "<span class='badge-mark-honmei'>◎</span>"
if pick_axis_horse['馬番'] != pick_win_horse['馬番']:
    bet_marks_dict[int(pick_axis_horse['馬番'])] = "<span class='badge-mark-taikou'>◯</span>"
for u in rec_c2:
    if int(u) not in bet_marks_dict: bet_marks_dict[int(u)] = "<span class='badge-mark-tanana'>▲</span>"
for u in rec_c3:
    if int(u) not in bet_marks_dict: bet_marks_dict[int(u)] = "<span class='badge-mark-himo'>△</span>"
if int(pick_himo_horse['馬番']) not in bet_marks_dict:
    bet_marks_dict[int(pick_himo_horse['馬番'])] = "<span class='badge-mark-ana'>★</span>"

is_bonus_cur = bool(((race_df['F_rank'] <= 3) & (race_df['arms_rank'] <= 3) & (race_df['tua_rank'] <= 3)).sum() >= 3)
has_ult_flag = bool(race_df['is_ultimate_win_horse'].any())

if has_ult_flag:
    wave_label = '【👑 極限勝率・鉄壁神域レース】'
    banner_cls = 'race-type-bonus'
elif is_bonus_cur:
    wave_label = '【👑 ボーナスレース】'
    banner_cls = 'race-type-bonus'
else:
    wave_label = '【標準・堅調】'
    banner_cls = 'race-type-solid'

st.markdown(f"<div class='race-type-banner {banner_cls}'><div><strong>🎯 レース判定: {wave_label}</strong></div><div>推奨券種: 単勝重点 / 3連単マルチ / 3連複</div></div>", unsafe_allow_html=True)

if pick_danger_horse is not None:
    danger_text = f"{int(pick_danger_horse['馬番'])}番 {pick_danger_horse['馬名']}（{danger_cands.iloc[0].get('脚質','')} / F{int(danger_cands.iloc[0].get('F_rank',99))}位 / 地雷判定）"
else:
    danger_text = "該当なし（人気順当戦）"

# ==============================================================================
# ★ 推奨馬ピックアップ＆馬券構成欄（新フォーメーション適用）
# ==============================================================================
win_horse_stats = "勝率極限・鉄壁神域" if pick_win_horse.get('is_ultimate_win_horse') else f"F{int(pick_win_horse['F_rank'])}位(値{float(pick_win_horse['F指数']):.1f}) × 先行"

st.markdown(
    f"<div class='recom-panel-go'><div class='recom-title-go'>📋 推奨馬ピックアップ（人気×脚質×指数極限モデル）</div>"
    f"<div class='recom-row'>🥇 <strong>1着狙い (連軸筆頭)</strong>: <span class='recom-val-num'>{int(pick_win_horse['馬番'])}番 {pick_win_horse['馬名']}</span>（{win_horse_stats} / 枠{int(pick_win_horse['枠番'])})</div>"
    f"<div class='recom-row'>🛡️ <strong>軸・連対狙い</strong>: <span class='recom-val-num'>{int(pick_axis_horse['馬番'])}番 {pick_axis_horse['馬名']}</span>（F{int(pick_axis_horse['F_rank'])}位 × S{int(pick_axis_horse['S_rank'])}位）</div>"
    f"<div class='recom-row'>💣 <strong>紐穴狙い (爆弾)</strong>: <span class='recom-val-num'>{int(pick_himo_horse['馬番'])}番 {pick_himo_horse['馬名']}</span>（{int(pick_himo_horse['人気'])}人気 / arms:{float(pick_himo_horse['arms']):.1f} / Fup{int(pick_himo_horse['Fup'])}点）</div>"
    f"<div class='recom-row'>⚠️ <strong>危険な人気馬 (ダミー消し)</strong>: <span style='color:#f87171; font-weight:bold;'>{danger_text}</span></div></div>",
    unsafe_allow_html=True,
)

c1_str = ', '.join(str(int(x)) for x in rec_c1)
c2_str = ', '.join(str(int(x)) for x in rec_c2)
c3_str = ', '.join(str(int(x)) for x in rec_c3)

st.markdown(
    f"<div class='recom-panel-go'><div class='recom-title-go'>🎫 推奨買い目フォーメーション（回収率×的中率極限化）</div>"
    f"<div class='recom-block'><strong>単勝</strong>: <span class='recom-val-num'>{int(pick_win_horse['馬番'])}番</span> （※極限条件合致時は単勝厚め勝負）</div>"
    f"<div class='recom-block'><strong>3連複フォーメーション</strong>: 1列目[{c1_str}] → 2列目[{c2_str}] → 3列目[{c3_str}]</div>"
    f"<div class='recom-block'><strong>3連単（裏表マルチ対応）</strong>: 1着[{int(pick_win_horse['馬番'])}, {int(pick_himo_horse['馬番'])}] ⇄ 2・3着[{c2_str}]（マーク集中惜敗対策）</div>"
    f"<div class='recom-block'><strong>馬連 / ワイド</strong>: {int(pick_win_horse['馬番'])} - {int(pick_axis_horse['馬番'])}, {int(pick_himo_horse['馬番'])}</div></div>",
    unsafe_allow_html=True,
)

# ==============================================================================
# ★ 出走馬詳細カルテ（フィルタ一括抽出の反映）
# ==============================================================================
st.markdown("### 🏇 出走馬詳細カルテ")

col_sort, _ = st.columns([3, 1])
with col_sort:
    sort_option = st.selectbox(
        "🔄 カルテ並び替え（ソート順）",
        options=['馬番順', '推奨度(動的スコア)順', 'F指数順(降順)', 'Fup得点順(降順)', 'arms指数順(降順)', 'tua指数順(降順)', 'S指数順(降順)'],
        index=0
    )

display_horses_df = race_df.copy()
if has_active_filter:
    display_horses_df = display_horses_df[display_horses_df['馬名'].isin(filtered_df['馬名'])]

if sort_option == '馬番順':
    display_horses_df = display_horses_df.sort_values('馬番', ascending=True)
elif sort_option == '推奨度(動的スコア)順':
    display_horses_df = display_horses_df.sort_values('dynamic_score', ascending=False)
elif sort_option == 'F指数順(降順)':
    display_horses_df = display_horses_df.sort_values(['F_rank', 'F指数'], ascending=[True, False])
elif sort_option == 'Fup得点順(降順)':
    display_horses_df = display_horses_df.sort_values(['Fup', 'Fup_rank'], ascending=[False, True])
elif sort_option == 'arms指数順(降順)':
    display_horses_df = display_horses_df.sort_values(['arms_rank', 'arms'], ascending=[True, False])
elif sort_option == 'tua指数順(降順)':
    display_horses_df = display_horses_df.sort_values(['tua_rank', 'tua'], ascending=[True, False])
elif sort_option == 'S指数順(降順)':
    display_horses_df = display_horses_df.sort_values(['S_rank', 'S指数'], ascending=[True, False])

def format_index_badge(val, rank, metric_type):
    if pd.isnull(val): return "-"
    v_str = f"{float(val):.1f}"
    r_int = int(rank) if pd.notnull(rank) else 99
    if r_int == 1: return f"<span class='val-rank1-gold'>{v_str}</span> (第1位)"
    if r_int in [2, 3]:
        if metric_type == 'F': return f"<span class='val-f-top'>{v_str}</span> (第{r_int}位)"
        elif metric_type == 'arms': return f"<span class='val-arms-top'>{v_str}</span> (第{r_int}位)"
        elif metric_type == 'tua': return f"<span class='val-tua-top'>{v_str}</span> (第{r_int}位)"
        elif metric_type == 'S': return f"<span class='val-s-top'>{v_str}</span> (第{r_int}位)"
    return f"<span class='val-normal'>{v_str}</span> (第{r_int}位)"

def format_fup_badge(fup_val, fup_rank):
    val_int = int(fup_val) if pd.notnull(fup_val) else 0
    rk_int = int(fup_rank) if pd.notnull(fup_rank) else 99
    if val_int == 7: return f"<span class='val-rank1-gold'>{val_int}点</span> (第{rk_int}位)"
    elif val_int in [5, 6]: return f"<span class='val-f-top'>{val_int}点</span> (第{rk_int}位)"
    elif val_int == 4: return f"<span class='val-arms-top'>{val_int}点</span> (第{rk_int}位)"
    return f"<span class='val-normal'>{val_int}点</span> (第{rk_int}位)"

for _, h in display_horses_df.iterrows():
    u_no = int(h['馬番'])
    h_mark = bet_marks_dict.get(u_no, '')
    style_badge = get_running_style_badge(h.get('脚質', ''))

    badges = []
    if h_mark: badges.append(h_mark)
    if style_badge: badges.append(style_badge)
    
    # ★ 新設：極限勝率・神域バッジの付与
    if h.get('is_ultimate_win_horse'):
        badges.append("<span class='badge-ultimate-win'>🏆 鉄壁神域ホース (勝率極大)</span>")
    if h.get('is_sss_level'):
        badges.append("<span class='badge-sss-crown'>✨ SSS級・絶対神域</span>")
    if h.get('is_dirt_tua_front'):
        badges.append("<span class='badge-dirt-lead'>🏜️ TUAダート先行特注</span>")

    mark_val = str(h.get('印', '')).strip()
    if mark_val and mark_val not in ['nan', 'None', '']:
        badges.append(f"<span class='badge-mark-gtv'>🏷️ 印: {mark_val}</span>")

    if h.get('target_win'): badges.append("<span class='badge-target-win'>🥇 1着狙い</span>")
    if h.get('target_axis'): badges.append("<span class='badge-target-axis'>🛡️ 軸候補</span>")
    if h.get('is_syn_iron'): badges.append("<span class='badge-synergy badge-iron'>💎 鉄板軸馬</span>")
    if h.get('is_syn_high'): badges.append("<span class='badge-synergy badge-high'>🔥 高確率軸馬</span>")
    if h.get('is_syn_bomb'): badges.append("<span class='badge-synergy badge-bomb'>💣 爆弾穴馬</span>")
    if h.get('is_prev_han_solid'): badges.append("<span class='badge-prev-fast'>🔥 前日坂路×王道厩舎</span>")
    elif h.get('has_prev_han_fast'): badges.append("<span class='badge-prev-han'>⏱️ 前日坂路速時計</span>")
    elif h.get('has_prev_han'): badges.append("<span class='badge-prev-han'>🏇 前日坂路あり</span>")

    if h.get('is_c_real_gold'): badges.append("<span class='badge-c-gold'>👑 本物C馬</span>")
    elif h.get('is_c_fake_trap'): badges.append("<span class='badge-c-fake'>⚠️ 偽C馬罠</span>")
    if h.get('is_arms_fup_super'): badges.append("<span class='badge-arms-fup'>👑 ARMS×Fup黄金軸</span>")
    if h.get('is_dirt_eat_super'): badges.append("<span class='badge-dirt-eat'>🏜️ ダートで食う勝負馬</span>")
    if h.get('cushion_horse_badge'): badges.append(str(h['cushion_horse_badge']))
    if h.get('cushion_badge_raw'): badges.append(str(h['cushion_badge_raw']))
    if h.get('tr_badge_html'): badges.append(str(h['tr_badge_html']))

    if h.get('坂路_完全加速'): badges.append("<span class='badge-accel-on'>⚡ 坂路完全加速</span>")
    elif h.get('is_wood_accel'): badges.append("<span class='badge-accel-on'>⚡ ウッド連続加速</span>")
    if h.get('坂路_穴トリガー'): badges.append("<span class='badge-bomb'>💣 坂路穴トリガー</span>")

    # 地雷・罠警告
    if h.get('is_valley_trap'): badges.append("<span class='badge-tr-danger'>⚠️ 谷の形罠</span>")
    if h.get('is_fup_trap'): badges.append("<span class='badge-tr-danger'>⚠️ Fup1の罠</span>")
    if h.get('is_dirt_wood_trap'): badges.append("<span class='badge-tr-danger'>⚠️ ダート×W追消し</span>")
    if h.get('is_danger_jockey'): badges.append("<span class='badge-danger-jockey-subtle'>⚠️ 騎手割引</span>")

    badges_html = " ".join([b for b in badges if b])

    f_badge_html = format_index_badge(h.get('F指数'), h.get('F_rank'), 'F')
    fup_badge_html = format_fup_badge(h.get('Fup'), h.get('Fup_rank'))
    arms_badge_html = format_index_badge(h.get('arms'), h.get('arms_rank'), 'arms')
    tua_badge_html = format_index_badge(h.get('tua'), h.get('tua_rank'), 'tua')
    s_badge_html = format_index_badge(h.get('S指数'), h.get('S_rank'), 'S')

    han_4f_str = f"{h['坂路_4F']:.1f}s" if pd.notnull(h.get('坂路_4F')) else "-"
    han_1f_str = f"{h['坂路_1F']:.1f}s" if pd.notnull(h.get('坂路_1F')) else "-"
    wood_1f_str = f"{h['wood_1F']:.1f}s" if pd.notnull(h.get('wood_1F')) else "-"
    prev_han_str = f"{h['前日坂路時計']:.1f}s" if pd.notnull(h.get('前日坂路時計')) and h.get('has_prev_han') else "なし"
    sat_sun_str = f"{h['土日坂路最速']:.1f}s" if pd.notnull(h.get('土日坂路最速')) and h.get('土日坂路最速') < 900 else "-"

    st.markdown(
        f"<div class='horse-card'>"
        f"<div class='horse-card-header'>"
        f"<span class='race-badge-title'>{u_no}番</span>"
        f"<span class='horse-card-title'>{h['馬名']}</span>"
        f"<span style='color:#94a3b8; font-size:13.5px;'>（{h.get('騎手','')} / {h.get('調教師','')}厩舎 / {int(h.get('人気',99))}番人気 / 枠{int(h.get('枠番',8))}）</span>"
        f"</div>"
        f"<div style='margin-bottom: 8px;'>{badges_html}</div>"
        f"<ul class='horse-card-list'>"
        f"<li><strong>指数マトリクス</strong>: F指数 {f_badge_html} / Fup2: {fup_badge_html} / arms: {arms_badge_html} / tua: {tua_badge_html} / S指数: {s_badge_html}</li>"
        f"<li><strong>調教時計・加速</strong>: 坂路4F {han_4f_str} - 1F {han_1f_str} ({h.get('坂路_ラップ型','-')}) / W終い {wood_1f_str} / 前日坂路: {prev_han_str} / 週末最速: {sat_sun_str}</li>"
        f"<li><strong>血統＆クッション値</strong>: 父 {h.get('種牡馬','-')} / 当日クッション値帯 ({current_bin_name}: {current_band}) 適性判定: {h.get('cushion_badge_raw','') if is_turf_race else 'ダート戦（対象外）'}</li>"
        f"</ul>"
        f"</div>",
        unsafe_allow_html=True,
    )
