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
# ARMS×Fup / ダートで食う / C馬判定 / 指数マトリクス / 調教完全加速 / クッション値特注
# 【NameError・KeyError完全解消・買い目印（◎◯▲△★）完全連動版】
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
    .recom-block { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; padding: 10px 14px; margin-bottom: 10px; }
    .recom-label { font-weight: bold; color: #fbbf24; display: inline-block; font-size: 14px; }
    .recom-val-num { color: #ffffff; font-weight: bold; font-size: 15.5px; letter-spacing: 1px; }
    .recom-pts { display: inline-block; background-color: #064e3b; color: #a7f3d0; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; margin-left: 8px; }
    .recom-pts-chaos { display: inline-block; background-color: #881337; color: #fecdd3; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; margin-left: 8px; }
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

    .val-f-super { color: #1a1000; background-color: #fcd34d; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #f59e0b; }
    .val-f-high { color: #ffffff; background-color: #ea580c; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #fb923c; }
    .val-arms-super { color: #083344; background-color: #38bdf8; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #0284c7; }
    .val-tua-super { color: #022c22; background-color: #34d399; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #059669; }
    .val-s-super { color: #ffffff; background-color: #8b5cf6; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #c4b5fd; }
    .badge-c-gold { background: linear-gradient(135deg, #b45309 0%, #f59e0b 50%, #d97706 100%); color: #ffffff; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #fde68a; box-shadow: 0 1px 4px rgba(245, 158, 11, 0.4); }
    .badge-c-fake { background: linear-gradient(135deg, #475569 0%, #334155 100%); color: #fca5a5; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #ef4444; }
    .badge-arms-fup { background: linear-gradient(135deg, #0284c7 0%, #0369a1 50%, #075985 100%); color: #ffffff; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #7dd3fc; box-shadow: 0 1px 4px rgba(2, 132, 199, 0.4); }
    .badge-dirt-eat { background: linear-gradient(135deg, #b45309 0%, #d97706 100%); color: #ffffff; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #fde68a; box-shadow: 0 1px 4px rgba(217, 119, 6, 0.4); }
    .badge-cushion-horse-star { background: linear-gradient(135deg, #d97706 0%, #f59e0b 50%, #fbbf24 100%); color: #111827; font-weight: bold; font-size: 12px; padding: 2px 9px; border-radius: 6px; border: 1px solid #fef08a; box-shadow: 0 1px 5px rgba(245, 158, 11, 0.4); }
    .badge-cushion-horse-danger { background: linear-gradient(135deg, #4b5563 0%, #1f2937 100%); color: #fca5a5; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #ef4444; }
    .badge-synergy { display: inline-flex; align-items: center; padding: 2px 8px; border-radius: 6px; font-weight: bold; font-size: 11.5px; }
    .badge-iron { background: linear-gradient(135deg, #FFE259 0%, #FFA751 100%); color: #1a1000; border: 1px solid #FFF275; }
    .badge-high { background: linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%); color: #ffffff; border: 1px solid #FF8E72; }
    .badge-sakaro-fup { background: linear-gradient(135deg, #8A2387 0%, #E94057 50%, #F27121 100%); color: #ffffff; border: 1px solid #FFA07A; }
    .badge-f1-rap { background: linear-gradient(135deg, #FF0844 0%, #FFB199 100%); color: #ffffff; border: 1px solid #FFD1C4; }
    .badge-bomb { background: linear-gradient(135deg, #EB3349 0%, #F45C43 100%); color: #ffffff; border: 1px solid #FFA07A; }
    .badge-target-win { background: linear-gradient(135deg, #e11d48 0%, #be123c 100%); color: #ffffff; font-weight: bold; font-size: 12px; padding: 2px 9px; border-radius: 6px; }
    .badge-target-axis { background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: #ffffff; font-weight: bold; font-size: 12px; padding: 2px 9px; border-radius: 6px; }
    .badge-danger-jockey-subtle { background-color: #262c36; color: #94a3b8; font-size: 11px; padding: 1px 6px; border-radius: 4px; border: 1px solid #334155; }
    .badge-tr-teppan { background: linear-gradient(135deg, #e11d48 0%, #be123c 100%); color: #ffffff; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #fda4af; }
    .badge-tr-shobu { background: linear-gradient(135deg, #d97706 0%, #b45309 100%); color: #ffffff; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #fde68a; }
    .badge-tr-tokuchu { background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); color: #ffffff; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #7dd3fc; }
    .badge-tr-danger { background: linear-gradient(135deg, #4b5563 0%, #1f2937 100%); color: #f87171; font-weight: bold; font-size: 11px; padding: 2px 7px; border-radius: 6px; border: 1px solid #ef4444; }
    .badge-jk-ub { background: linear-gradient(135deg, #d97706 0%, #b45309 100%); color: #ffffff; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #fcd34d; }
    .badge-tr-ub { background: linear-gradient(135deg, #059669 0%, #047857 100%); color: #ffffff; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #6ee7b7; }
    .badge-same-ub-f6 { background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); color: #ffffff; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #7dd3fc; }
    .badge-same-ub-s6 { background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%); color: #ffffff; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #c4b5fd; }
    .badge-same-ub-fs6 { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: #ffffff; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #fde68a; }
    .badge-fup6-sf { background: linear-gradient(135deg, #ff0844 0%, #ffb199 100%); color: #ffffff; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #ffe4e6; box-shadow: 0 1px 4px rgba(255, 8, 68, 0.4); }
    .badge-sf7-himo { background: linear-gradient(135deg, #0ea5e9 0%, #0369a1 100%); color: #ffffff; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #7dd3fc; }
    .badge-cushion-fit { display: inline-flex; align-items: center; background: linear-gradient(135deg, #059669 0%, #10b981 100%); color: #ffffff; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #34d399; }
    .badge-cushion-danger { display: inline-flex; align-items: center; background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%); color: #ffffff; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #f87171; }
    .badge-prev-han { background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); color: #ffffff; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #7dd3fc; box-shadow: 0 0 6px rgba(2, 132, 199, 0.4); }
    .badge-prev-fast { background: linear-gradient(135deg, #d97706 0%, #b45309 100%); color: #ffffff; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #fcd34d; box-shadow: 0 0 6px rgba(217, 119, 6, 0.5); }
    .badge-prev-kato { background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%); color: #fef08a; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #f87171; box-shadow: 0 0 8px rgba(220, 38, 38, 0.6); }
    .badge-prev-wood-dirt { background: linear-gradient(135deg, #7c2d12 0%, #9a3412 100%); color: #fef3c7; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #fdba74; }
    .tr-name-super { color: #facc15; font-weight: bold; text-decoration: underline; }
    .tr-name-bomb { color: #f87171; font-weight: bold; text-decoration: underline; }
    .tr-name-wood { color: #67e8f9; font-weight: bold; text-decoration: underline; }
    .rank-1st { color: #FFD700; font-weight: bold; }
    .rank-2nd { color: #E2E8F0; font-weight: bold; }
    .rank-3rd { color: #F97316; font-weight: bold; }

    /* 買い目印バッジ（◎、◯、▲、△、★） */
    .badge-mark-honmei { display: inline-flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%); color: #ffffff; font-size: 16px; font-weight: 900; width: 30px; height: 30px; border-radius: 6px; border: 1.5px solid #fca5a5; margin-right: 6px; box-shadow: 0 0 8px rgba(220, 38, 38, 0.7); }
    .badge-mark-taikou { display: inline-flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: #ffffff; font-size: 16px; font-weight: 900; width: 30px; height: 30px; border-radius: 6px; border: 1.5px solid #93c5fd; margin-right: 6px; box-shadow: 0 0 8px rgba(37, 99, 235, 0.7); }
    .badge-mark-tanana { display: inline-flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #059669 0%, #047857 100%); color: #ffffff; font-size: 16px; font-weight: 900; width: 30px; height: 30px; border-radius: 6px; border: 1.5px solid #6ee7b7; margin-right: 6px; }
    .badge-mark-himo { display: inline-flex; align-items: center; justify-content: center; background-color: #374151; color: #f3f4f6; font-size: 14.5px; font-weight: bold; width: 30px; height: 30px; border-radius: 6px; border: 1px solid #6b7280; margin-right: 6px; }
    .badge-mark-ana { display: inline-flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #d97706 0%, #b45309 100%); color: #ffffff; font-size: 16px; font-weight: 900; width: 30px; height: 30px; border-radius: 6px; border: 1.5px solid #fde68a; margin-right: 6px; box-shadow: 0 0 8px rgba(217, 119, 6, 0.7); }
</style>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# ★ 基本定数・危険騎手リスト & 前日坂路・ウッド特注厩舎リスト
# ==============================================================================
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

# ==============================================================================
# ★ 基本ユーティリティ関数
# ==============================================================================
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
    if '逃' in s:
        return "<span class='badge-style-nige'>🏃 逃げ</span>"
    elif '先' in s:
        return "<span class='badge-style-senko'>🐎 先行</span>"
    elif '差' in s:
        return "<span class='badge-style-sashi'>⚡ 差し</span>"
    elif '追' in s:
        return "<span class='badge-style-oikomi'>🔥 追込</span>"
    elif '後' in s:
        return "<span class='badge-style-oikomi'>後方</span>"
    elif '中' in s:
        return "<span class='badge-style-chudan'>中団</span>"
    elif 'マ' in s or 'ﾏ' in s:
        return "<span class='badge-style-other'>まくり</span>"
    return f"<span class='badge-style-other'>{s}</span>"

# ==============================================================================
# ★ 各種判定エンジン関数（最優先定義：NameError完全根絶）
# ==============================================================================
def evaluate_course_training(row):
    track_type = str(row.get('track', '芝')).strip()
    dist_val = int(re.sub(r'\D', '', str(row.get('dist', 1600)))) if row.get('dist') else 1600
    sakaro_full = bool(row.get('坂路_完全加速', False))
    sakaro_1f = float(row.get('坂路_1F', 99.0)) if pd.notnull(row.get('坂路_1F')) else 99.0
    wood_accel = bool(row.get('is_wood_accel', False))
    wood_1f = float(row.get('wood_1F', 99.0)) if pd.notnull(row.get('wood_1F')) else 99.0
    wood_accel_diff = float(row.get('wood_accel', 0.0)) if pd.notnull(row.get('wood_accel')) else 0.0

    badge_html = ""
    is_fit = False

    if 'ダ' in track_type:
        if dist_val <= 1400:
            if sakaro_full:
                badge_html = "<span class='badge-cushion-fit' style='background:linear-gradient(135deg, #d97706 0%, #b45309 100%);border-color:#fcd34d;'>⚡ コース特注 (ダ短×坂路完全加速)</span>"
                is_fit = True
        else:
            if sakaro_full and wood_accel:
                badge_html = "<span class='badge-cushion-fit' style='background:linear-gradient(135deg, #059669 0%, #047857 100%);border-color:#6ee7b7;'>⚡ コース特注 (中距離ダ×坂路W併用)</span>"
                is_fit = True
            elif sakaro_full:
                badge_html = "<span class='badge-cushion-fit' style='background:linear-gradient(135deg, #059669 0%, #047857 100%);border-color:#6ee7b7;'>⚡ コース特注 (中距離ダ×坂路完全加速)</span>"
                is_fit = True
    else:
        if dist_val <= 1400:
            if sakaro_full:
                badge_html = "<span class='badge-cushion-fit' style='background:linear-gradient(135deg, #059669 0%, #10b981 100%);border-color:#34d399;'>⚡ コース特注 (芝短距離×坂路完全加速)</span>"
                is_fit = True
        elif 1500 <= dist_val <= 1800:
            if wood_accel and wood_accel_diff >= 1.0:
                badge_html = "<span class='badge-cushion-fit' style='background:linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);border-color:#fca5a5;'>👑 マイル特注 (芝マイル×W大加速+1.0s超:複44%)</span>"
                is_fit = True
            elif sakaro_full and wood_accel and wood_1f <= 11.6:
                badge_html = "<span class='badge-cushion-fit' style='background:linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%);border-color:#c4b5fd;'>👑 コース特注 (芝マイル外×坂路W二刀流加速)</span>"
                is_fit = True
            elif sakaro_full:
                badge_html = "<span class='badge-cushion-fit' style='background:linear-gradient(135deg, #059669 0%, #10b981 100%);border-color:#34d399;'>⚡ コース特注 (芝マイル×坂路完全加速:複33%)</span>"
                is_fit = True
            elif wood_accel and wood_1f <= 11.2:
                badge_html = "<span class='badge-cushion-fit' style='background:linear-gradient(135deg, #0284c7 0%, #0369a1 100%);border-color:#7dd3fc;'>⚡ コース特注 (芝マイル×W猛時計加速)</span>"
                is_fit = True
        else:
            if sakaro_full and sakaro_1f <= 12.0:
                badge_html = "<span class='badge-cushion-fit' style='background:linear-gradient(135deg, #be123c 0%, #9f1239 100%);border-color:#fda4af;'>🔥 コース特注 (中長距離×坂路究極11秒台)</span>"
                is_fit = True
            elif sakaro_full and wood_accel:
                badge_html = "<span class='badge-cushion-fit' style='background:linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);border-color:#93c5fd;'>⚡ コース特注 (中長距離×坂路Wスタミナ加速)</span>"
                is_fit = True
            elif sakaro_full:
                badge_html = "<span class='badge-cushion-fit' style='background:linear-gradient(135deg, #059669 0%, #10b981 100%);border-color:#34d399;'>⚡ コース特注 (中長距離×坂路完全加速)</span>"
                is_fit = True

    return pd.Series([badge_html, is_fit])

def check_trainer_patterns(row):
    trainer = str(row.get('調教師', ''))
    course = str(row.get('追切コース', ''))
    f4 = row.get('坂路_4F', 999.0) if pd.notnull(row.get('坂路_4F')) else 999.0
    s_1f = row.get('坂路_1F', 999.0) if pd.notnull(row.get('坂路_1F')) else 999.0
    f5 = row.get('wood_5F', 999.0) if pd.notnull(row.get('wood_5F')) else 999.0
    f1 = row.get('wood_1F', 999.0) if pd.notnull(row.get('wood_1F')) else 999.0
    lap = str(row.get('追切ラップ型', ''))
    align = str(row.get('併せ結果', ''))
    mori_accel = bool(row.get('坂路_森加速', False))
    
    sun_sat_han = row.get('土日坂路最速', 999.0)
    sun_sat_wood = row.get('土日ウッド最速', 999.0)
    prev_day_han = bool(row.get('前日坂路あり', False))
    prev_day_han_time = row.get('前日坂路時計', 999.0)
    prev_day_wood = bool(row.get('前日ウッドあり', False))
    
    track = str(row.get('track', '芝'))
    venue = str(row.get('競馬場名', ''))
    race_class = str(row.get('クラス', ''))
    is_graded = '重賞' in race_class
    age = row.get('馬齢', 0)
    jockey = str(row.get('騎手', ''))
    pop = row.get('人気', 99)
    owner = str(row.get('馬主', ''))
    sex = str(row.get('性別', ''))
    f_rank = row.get('F_rank', 99)
    arms_rank = row.get('arms_rank', 99)
    fup_val = row.get('Fup', 0)

    status = None
    flags = []

    # 森秀行厩舎の狙い目自動判定（4F > 3F > 2F > 1F の完全加速）
    if '森秀' in trainer or '森' == trainer:
        if mori_accel:
            if pop <= 3:
                status = '鉄板'
                flags.append('森秀行:坂路完全加速(4F>3F>2F>1F勝負合図・上位人気鉄板)')
            else:
                status = '勝負'
                flags.append('森秀行:坂路完全加速(4F>3F>2F>1F穴馬激走パターン)')

    if prev_day_han and prev_day_han_time <= 65.9:
        if any(tr in trainer for tr in PREV_HAN_SOLID_TRAINERS) and pop in [1, 2, 3]:
            status = '鉄板'; flags.append(f'{trainer}:前日坂路65秒以下×上位人気(勝率40%超・鉄板軸)')
        elif any(tr in trainer for tr in PREV_HAN_BOMB_TRAINERS) and pop >= 6:
            status = '特注'; flags.append(f'{trainer}:前日坂路65秒以下×穴馬激走(単回100%超)')

    if prev_day_wood and 'ダ' in track:
        if any(tr in trainer for tr in PREV_WOOD_DIRT_TRAINERS):
            status = '特注'; flags.append(f'{trainer}:ダート戦×前日ウッド追い(単回収110%超・特注穴)')

    if '友道' in trainer:
        if '坂路' in course and lap == 'A1':
            status = status or '勝負'; flags.append('友道:坂路A1鉄板(重賞単回200%/若駒勝率30%)')
        if (sun_sat_han < 900) and (sun_sat_wood < 900):
            status = status or '勝負'; flags.append('友道:土日坂路+CWダブル(単回100%超)')
        if '芝' in course and align in ['先着', '併入'] and ('長' in race_class or int(re.sub(r'\D','',str(row.get('dist',0)))) >= 2200):
            status = '鉄板'; flags.append('友道:最終芝コース併せ馬(長距離勝負手)')
        if ('ポリ' in course) and (age <= 3 or not is_graded):
            status = status or '危険'; flags.append('友道:ポリ過信禁物(若駒/平場低期待値)')
    elif '宮田' in trainer:
        if ('南W' in course or 'ウッド' in course) and align in ['先着', '併入']:
            status = status or '勝負'; flags.append('宮田:南W馬なり格上追走同入先着(高連対率)')
    elif '戸田' in trainer:
        if f4 <= 52.5 and 'ダ' in track:
            status = '特注'; flags.append('戸田:坂路52秒台自己ベスト更新×ダート替わり(高回収率)')
    elif '大竹' in trainer:
        if ('ポリ' in course or 'PT' in course) and align == '先着':
            status = status or '勝負'; flags.append('大竹:最終PT併せ馬先着(休み明け勝負)')
    elif '安田' in trainer:
        if f4 <= 51.9 and int(re.sub(r'\D','',str(row.get('dist',1600)))) <= 1400:
            status = '鉄板'; flags.append('安田:坂路50-51秒台猛時計×短距離(単回収特大)')
    elif '松永幹' in trainer:
        if s_1f <= 12.0 and bool(row.get('坂路_完全加速', False)) and ('牝' in sex or '牝' in str(row.get('性', ''))):
            status = status or '勝負'; flags.append('松永幹:坂路終い12.0以下加速×牝馬芝(特注)')
    elif '藤原英' in trainer:
        if ('ウッド' in course or 'CW' in course) and f5 <= 82.0:
            status = '鉄板'; flags.append('藤原英:最終CW好時計6F82秒以下馬なり(軸信頼)')
    elif '木村哲' in trainer:
        if f1 <= 11.5 and align in ['先着', '併入']:
            status = '鉄板'; flags.append('木村哲:併せ強め終い11.5秒以下(外厩帰り鉄板)')
        if 'ルメール' in jockey:
            if fup_val >= 5:
                status = '鉄板'; flags.append('木村哲×ルメール×Fup5点以上(勝率33.3%超)')
            else:
                status = '危険'; flags.append('木村哲×ルメール×Fup4点以下(勝率0.0%地雷消し)')
    elif '堀' in trainer:
        if ('南W' in course or 'ウッド' in course) and align in ['先着', '併入'] and f5 >= 68.0:
            status = status or '勝負'; flags.append('堀:南W馬なり時計出しすぎず(休み明け2戦目上積み大)')
        if prev_day_han and prev_day_han_time <= 65.9:
            if pop == 1: status = '鉄板'; flags.append('堀:1人気×前日坂路65秒以下(勝率約50%)')
            elif pop in [2, 3]: status = '勝負'; flags.append('堀:2-3人気×前日坂路65秒以下(勝率約30%)')
        elif not prev_day_han and venue in ['東京', '中山']:
            status = status or '危険'; flags.append('堀:関東前日坂路なし(勝率急落・割引)')
    elif '国枝' in trainer:
        if '坂路' in course and align in ['先着', '併入'] and is_graded and ('牝' in sex or '牝' in str(row.get('性', ''))):
            status = status or '勝負'; flags.append('国枝:坂路併せ強め×牝馬重賞(的中率上昇)')
    elif '手塚' in trainer:
        if not prev_day_han and venue in ['東京', '中山']: status = '特注'; flags.append('手塚:前日坂路なし(単回123%)')
        elif prev_day_han and venue in ['東京', '中山']: status = status or '危険'; flags.append('手塚:前日坂路あり(単回51%割引)')
        if is_graded and 'ウッド' in course and f5 <= 66.9: status = status or '勝負'; flags.append('手塚:重賞CW66秒以下(勝率20%)')
    elif '中内田' in trainer:
        if f1 <= 11.3 and align in ['単走', '']:
            status = '鉄板'; flags.append('中内田:CW単走馬なり終い11.0-11.3秒(的中率50%超)')
        if '川田' in jockey and f_rank == 1:
            status = '鉄板'; flags.append('中内田×川田×F1位(新馬45%/未勝利50%/重賞35%勝率)')
        elif sun_sat_han <= 55.9 and '坂路' in course:
            status = status or '勝負'; flags.append('中内田:土日坂路55秒以下+最終坂路(勝率34%/単回140%)')
    elif '杉山晴' in trainer:
        if f4 <= 52.9 and s_1f <= 12.2:
            status = '鉄板'; flags.append('杉山晴:坂路4F52秒台+終い12.2以下黄金パターン(回収安定)')
        if lap == 'A3':
            status = status or '勝負'; flags.append('杉山晴:栗東坂路A3(終い11秒台加速:単回149%)')
        if '西村淳' in jockey:
            status = status or '勝負'; flags.append('杉山晴×西村淳也(単勝回収率120%超)')
    elif '矢作' in trainer:
        if 'ダ' in track and ('ウッド' in course or 'CW' in course):
            status = '特注'; flags.append('矢作:ダート戦×ウッド追い切りシフト馬(ダートで食う)')
        elif lap == 'A2' and f4 <= 53.0:
            status = '特注'; flags.append('矢作:栗東坂路A2×53秒以下(単回収145%/キャリア7戦超198%)')
    elif '斎藤誠' in trainer:
        if 'ダ' in track and '坂路' in course and f4 <= 53.9:
            status = '鉄板'; flags.append('斎藤誠:ダート戦×坂路53秒台以下(単回200%超・ダートで食う)')
    elif '野中' in trainer:
        if 'ダ' in track and '坂路' in course and lap in ['A1', 'A2', 'A3']:
            status = status or '勝負'; flags.append('野中:ダート×坂路加速ラップ(ダートで食う特注)')
    elif '寺島' in trainer:
        if 'ダ' in track and ('ウッド' in course or 'CW' in course):
            status = status or '勝負'; flags.append('寺島:ダート戦×ウッド追い切り(勝負合図・ダートで食う)')

    if '土井' in owner and venue == '中京':
        if 1 <= f_rank <= 6: flags.append('土井オーナー×中京: F指数1-6位(勝率26.6%/単回123%)')
        if arms_rank == 1: status = '鉄板'; flags.append('土井オーナー×中京: arms1位(勝率58.3%/単回273%)')
        elif arms_rank <= 2: status = status or '勝負'; flags.append('土井オーナー×中京: arms2位以内(勝率40.9%/単回189%)')

    badge_html = ""
    if status == '鉄板': badge_html = "<span class='badge-tr-teppan'>🔥【鉄板厩舎】</span>"
    elif status == '勝負': badge_html = "<span class='badge-tr-shobu'>⚔️【勝負気配】</span>"
    elif status == '特注': badge_html = "<span class='badge-tr-tokuchu'>💎【特注穴パターン】</span>"
    elif status == '危険': badge_html = "<span class='badge-tr-danger'>⚠【厩舎危険】</span>"

    flag_str = " / ".join(flags) if flags else ""
    return pd.Series([status, flag_str, badge_html], index=['調教ステータス', '厩舎狙い目フラグ', 'tr_badge_html'])

# ==============================================================================
# ★ クッション値帯別・種牡馬評価関数
# ==============================================================================
def get_cushion_band(venue, c_val):
    if c_val is None: return 'standard'
    if venue == '札幌':
        if c_val >= 7.7: return 'sapporo_high'
        elif c_val <= 7.3: return 'sapporo_low'
        else: return 'standard'
    elif venue == '函館':
        if c_val >= 7.5: return 'hakodate_high'
        elif c_val <= 7.2: return 'hakodate_low'
        else: return 'standard'
    if c_val >= 10.5: return 'super_high'
    elif c_val >= 10.0: return 'high'
    elif c_val >= 9.5: return 'standard_high'
    elif c_val >= 8.6: return 'standard_low'
    else: return 'low'

def get_current_cushion_bin_name(c_val):
    if c_val is None: return '9台'
    if c_val < 8.0: return '7以下'
    elif c_val < 9.0: return '8台'
    elif c_val < 10.0: return '9台'
    elif c_val < 11.0: return '10台'
    else: return '11以上'

def evaluate_sire_cushion(sire_name, venue, dist, band):
    if not sire_name or pd.isnull(sire_name): return ''
    sire = str(sire_name).strip()
    dist_val = int(re.sub(r'\D', '', str(dist))) if dist else 0
    course_key = f"{venue}芝{dist_val}"
    
    # コース×種牡馬 データブック最強マトリクス 上位20[cite: 97, 169]
    if course_key == "阪神芝1800" and band == 'standard_high' and 'キズナ' in sire: return "<span class='badge-cushion-fit'>🟢 阪神1800外×9.5-9.9 特注(勝19.6%/単421%)</span>"
    if course_key == "東京芝1600" and band == 'standard_high' and 'エピファネイア' in sire: return "<span class='badge-cushion-fit'>🟢 東京1600×9.5-9.9 特注(勝13.3%/単277%)</span>"
    if course_key == "東京芝1400" and band == 'standard_high' and 'モーリス' in sire: return "<span class='badge-cushion-fit'>🟢 東京1400×9.5-9.9 特注(勝10.1%/単408%)</span>"
    if course_key == "東京芝1800" and band == 'standard_high' and 'ディープインパクト' in sire: return "<span class='badge-cushion-fit'>🟢 東京1800×9.5-9.9 特注(勝15.8%/単228%)</span>"
    if course_key == "東京芝2000" and band == 'standard_low' and 'キズナ' in sire: return "<span class='badge-cushion-fit'>🟢 東京2000×8.6-9.4 特注(勝19.7%/単200%)</span>"
    if course_key == "中京芝2000" and band == 'standard_low' and 'ディープインパクト' in sire: return "<span class='badge-cushion-fit'>🟢 中京2000×8.6-9.4 特注(勝18.0%/単178%)</span>"
    if course_key == "東京芝1600" and band == 'standard_low' and 'イスラボニータ' in sire: return "<span class='badge-cushion-fit'>🟢 東京1600×8.6-9.4 特注(勝10.5%/単350%)</span>"
    if course_key == "東京芝2000" and band == 'standard_low' and 'エピファネイア' in sire: return "<span class='badge-cushion-fit'>🟢 東京2000×8.6-9.4 特注(勝15.3%/単149%)</span>"
    if course_key == "函館芝1800" and band in ['low', 'hakodate_low'] and 'キズナ' in sire: return "<span class='badge-cushion-fit'>🟢 函館1800×低帯 特注(勝17.7%/単143%)</span>"
    if course_key == "小倉芝1200" and band == 'standard_high' and 'ダイワメジャー' in sire: return "<span class='badge-cushion-fit'>🟢 小倉1200×9.5-9.9 特注(勝13.6%/単173%)</span>"
    if course_key == "札幌芝2000" and band in ['low', 'sapporo_low'] and 'オルフェーヴル' in sire: return "<span class='badge-cushion-fit'>🟢 札幌2000×低帯 特注(勝15.8%/単136%)</span>"
    if course_key == "東京芝1400" and band == 'standard_low' and 'ロードカナロア' in sire: return "<span class='badge-cushion-fit'>🟢 東京1400×8.6-9.4 特注(勝15.6%/単123%)</span>"
    if course_key == "阪神芝1600" and band == 'standard_low' and 'ルーラーシップ' in sire: return "<span class='badge-cushion-fit'>🟢 阪神1600外×8.6-9.4 特注(勝20.0%/単156%)</span>"
    if course_key == "東京芝1600" and band == 'standard_high' and 'モーリス' in sire: return "<span class='badge-cushion-fit'>🟢 東京1600×9.5-9.9 特注(勝11.1%/単100%)</span>"
    if course_key == "阪神芝2000" and band == 'standard_low' and 'キズナ' in sire: return "<span class='badge-cushion-fit'>🟢 阪神2000内×8.6-9.4 特注(勝11.8%/単152%)</span>"
    if course_key == "東京芝1600" and band == 'standard_low' and 'スクリーンヒーロー' in sire: return "<span class='badge-cushion-fit'>🟢 東京1600×8.6-9.4 特注(勝9.9%/単72%)</span>"
    if course_key == "小倉芝1200" and band == 'standard_low' and 'ビッグアーサー' in sire: return "<span class='badge-cushion-fit'>🟢 小倉1200×8.6-9.4 特注(勝12.2%/単131%)</span>"
    if course_key == "中京芝1600" and band == 'high' and 'ロードカナロア' in sire: return "<span class='badge-cushion-fit'>🟢 中京1600×10.0-10.4 特注(勝14.8%/単133%)</span>"
    if course_key == "福島芝1200" and band == 'standard_low' and 'ビッグアーサー' in sire: return "<span class='badge-cushion-fit'>🟢 福島1200×8.6-9.4 特注(勝13.2%/単87%)</span>"
    if course_key == "札幌芝1200" and band in ['low', 'sapporo_low'] and 'ロードカナロア' in sire: return "<span class='badge-cushion-fit'>🟢 札幌1200×低帯 特注(勝15.0%/単121%)</span>"

    # RISK LIST 危険・割引対象 上位20[cite: 98, 170]
    if course_key == "中山芝2000" and band == 'standard_high' and 'ダノンバラード' in sire: return "<span class='badge-cushion-danger'>🔴 中山2000×9.5-9.9 危険(複0%)</span>"
    if course_key == "東京芝2000" and band == 'standard_high' and 'ルーラーシップ' in sire: return "<span class='badge-cushion-danger'>🔴 東京2000×9.5-9.9 危険(複9.1%)</span>"
    if course_key == "小倉芝1200" and band == 'standard_low' and 'ジャスタウェイ' in sire: return "<span class='badge-cushion-danger'>🔴 小倉1200×8.6-9.4 危険(複2.9%)</span>"
    if course_key == "東京芝1400" and band == 'standard_low' and 'シルバーステート' in sire: return "<span class='badge-cushion-danger'>🔴 東京1400×8.6-9.4 危険(複4.7%)</span>"
    if course_key == "東京芝1600" and band == 'standard_low' and 'ゴールドシップ' in sire: return "<span class='badge-cushion-danger'>🔴 東京1600×8.6-9.4 危険(複4.5%)</span>"
    if course_key == "小倉芝1200" and band == 'standard_low' and 'ヴィクトワールピサ' in sire: return "<span class='badge-cushion-danger'>🔴 小倉1200×8.6-9.4 危険(複4.8%)</span>"
    if course_key == "東京芝1800" and band == 'standard_high' and 'ルーラーシップ' in sire: return "<span class='badge-cushion-danger'>🔴 東京1800×9.5-9.9 危険(複10.5%)</span>"
    if course_key == "阪神芝2000" and band == 'standard_low' and 'ゴールドシップ' in sire: return "<span class='badge-cushion-danger'>🔴 阪神2000内×8.6-9.4 危険(複10.0%)</span>"
    if course_key == "東京芝1600" and band == 'standard_low' and 'エイシンフラッシュ' in sire: return "<span class='badge-cushion-danger'>🔴 東京1600×8.6-9.4 危険(複7.3%)</span>"
    if course_key == "東京芝2000" and band == 'standard_low' and 'オルフェーヴル' in sire: return "<span class='badge-cushion-danger'>🔴 東京2000×8.6-9.4 危険(複13.2%)</span>"
    if course_key == "福島芝2000" and band == 'standard_low' and 'ルーラーシップ' in sire: return "<span class='badge-cushion-danger'>🔴 福島2000×8.6-9.4 危険(複4.7%)</span>"
    if course_key == "新潟芝1400" and band == 'standard_low' and 'リオンディーズ' in sire: return "<span class='badge-cushion-danger'>🔴 新潟1400内×8.6-9.4 危険(複6.7%)</span>"
    if course_key == "東京芝2400" and band == 'standard_high' and 'ゴールドシップ' in sire: return "<span class='badge-cushion-danger'>🔴 東京2400×9.5-9.9 危険(複11.1%)</span>"
    if course_key == "小倉芝1800" and band == 'standard_high' and 'ルーラーシップ' in sire: return "<span class='badge-cushion-danger'>🔴 小倉1800×9.5-9.9 危険(複10.0%)</span>"
    if course_key == "阪神芝1800" and band == 'standard_high' and 'ハービンジャー' in sire: return "<span class='badge-cushion-danger'>🔴 阪神1800外×9.5-9.9 危険(複10.0%)</span>"
    if course_key == "東京芝1600" and band == 'standard_low' and 'サトノクラウン' in sire: return "<span class='badge-cushion-danger'>🔴 東京1600×8.6-9.4 危険(複9.7%)</span>"
    if course_key == "福島芝1200" and band == 'standard_low' and 'マツリダゴッホ' in sire: return "<span class='badge-cushion-danger'>🔴 福島1200×8.6-9.4 危険(複5.9%)</span>"
    if course_key == "東京芝1600" and band == 'standard_high' and 'シルバーステート' in sire: return "<span class='badge-cushion-danger'>🔴 東京1600×9.5-9.9 危険(複8.9%)</span>"
    if course_key == "福島芝1200" and band == 'standard_low' and 'カレンブラックヒル' in sire: return "<span class='badge-cushion-danger'>🔴 福島1200×8.6-9.4 危険(複9.7%)</span>"
    if course_key == "中京芝2000" and band == 'standard_low' and 'オルフェーヴル' in sire: return "<span class='badge-cushion-danger'>🔴 中京2000×8.6-9.4 危険(複15.2%)</span>"

    # 超高帯（≥10.5）特注＆危険規定
    if band == 'super_high':
        if ('エピファネイア' in sire or 'キタサンブラック' in sire or 'イスラボニータ' in sire): return "<span class='badge-cushion-fit'>🟢 超高帯特注 (血統適性突出)</span>"
        if any(d in sire for d in ['キングカメハメハ', 'ビッグアーサー', 'レイデオロ', 'スワーヴリチャード', 'サートゥルナーリア', 'ゴールドシップ']): return "<span class='badge-cushion-danger'>🔴 超高帯危険 (大幅割引)</span>"

    if venue == '京都':
        if band == 'super_high':
            if 'キタサンブラック' in sire and dist_val == 2000: return "<span class='badge-cushion-fit'>🟢 京都2000×超高帯 特注 (勝21.1%)</span>"
            if 'エピファネイア' in sire and dist_val == 1600: return "<span class='badge-cushion-fit'>🟢 京都1600×超高帯 特注 (複50%)</span>"
            if 'ゴールドシップ' in sire and dist_val == 2000: return "<span class='badge-cushion-danger'>🔴 京都2000×超高帯 危険 (複12.1%)</span>"

    return ''

def check_cushion_special_horse(row, cur_bin):
    h_name = str(row.get('馬名', '')).strip()
    spec = CUSHION_SPECIAL_HORSES.get(h_name)
    if not spec:
        return pd.Series(['', False, False], index=['cushion_horse_badge', 'is_cushion_horse_fit', 'is_cushion_horse_danger'])
    
    best_b = spec.get('best_bin')
    danger_bs = spec.get('danger_bins', [])
    badge = ""
    is_fit = False
    is_danger = False

    if best_b == cur_bin:
        is_fit = True
        badge = f"<span class='badge-cushion-horse-star'>🎯【クッション特注】{spec['label']}</span>"
    elif cur_bin in danger_bs:
        is_danger = True
        badge = f"<span class='badge-cushion-horse-danger'>⚠️【クッション危険帯】{cur_bin}割引</span>"

    return pd.Series([badge, is_fit, is_danger], index=['cushion_horse_badge', 'is_cushion_horse_fit', 'is_cushion_horse_danger'])

def check_danger_jockey_info(row):
    jk = str(row.get('騎手', '')).strip()
    is_f3 = row.get('F_rank', 99) <= 3
    is_any3 = ((row.get('F_rank', 99) <= 3) or (row.get('arms_rank', 99) <= 3) or (row.get('tua_rank', 99) <= 3) or (row.get('S_rank', 99) <= 3))
    if is_f3 and any(d in jk for d in DANGER_JOCKEYS_F3): return True
    if is_any3 and any(d in jk for d in DANGER_JOCKEYS_GENERAL): return True
    return False

@st.cache_data(show_spinner=False)
def load_cushion_history_stats():
    candidates = ['data/クッション値馬データ.csv', 'クッション値馬データ.csv', '*クッション値馬データ*.csv']
    src = None
    for pat in candidates:
        m = glob.glob(pat)
        if m: src = m[0]; break
    if src is None or not os.path.exists(src): return {}

    for enc in ['cp932', 'shift_jis', 'utf-8-sig', 'utf-8']:
        try:
            raw = pd.read_csv(src, encoding=enc)
            if not raw.empty: break
        except Exception: continue
    else: return {}

    turf_sub = raw[raw['距離'].astype(str).str.startswith('芝')].copy()
    if turf_sub.empty: return {}

    def p_rank(val):
        v = str(val).strip().translate(str.maketrans('１２３４５６７８９０', '1234567890'))
        try: return int(v)
        except: return 99

    turf_sub['r_num'] = turf_sub['着順'].apply(p_rank)
    
    def p_bin(val):
        v = pd.to_numeric(val, errors='coerce')
        if pd.isnull(v): return '9台'
        if v < 80: return '7以下'
        elif v < 90: return '8台'
        elif v < 100: return '9台'
        elif v < 110: return '10台'
        else: return '11以上'

    turf_sub['c_bin'] = turf_sub['指数'].apply(p_bin)
    turf_sub['horse_clean'] = turf_sub['馬名'].astype(str).apply(
        lambda x: x.strip().replace('*', '').replace('$', '').replace(' ', '').replace(' ', '')
    )

    stats_dict = {}
    grouped = turf_sub.groupby(['horse_clean', 'c_bin'])['r_num'].agg(
        wins=lambda x: (x == 1).sum(),
        top2=lambda x: (x == 2).sum(),
        top3=lambda x: (x == 3).sum(),
        runs='count'
    ).reset_index()

    for h_name, group in grouped.groupby('horse_clean'):
        h_dict = {}
        for _, r in group.iterrows():
            w = int(r['wins']); p2 = int(r['top2']); p3 = int(r['top3']); tot = int(r['runs'])
            h_dict[r['c_bin']] = f"[{w}-{p2}-{p3}/{tot}]"
        stats_dict[h_name] = h_dict

    return stats_dict

cushion_history_data = load_cushion_history_stats()

# ==============================================================================
# ★ データ読み込み実行（全関数定義後に実行：NameError完全防止）
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

# 確実に全派生列を反映
df = populate_all_derived_columns(df)

df[['course_training_badge', 'is_course_training_fit']] = df.apply(evaluate_course_training, axis=1)
df[['調教ステータス', '厩舎狙い目フラグ', 'tr_badge_html']] = df.apply(check_trainer_patterns, axis=1)
df['is_danger_jockey'] = df.apply(check_danger_jockey_info, axis=1)

# ==============================================================================
# ★ サイドバー: 馬場設定＆クッション値 ＆ 前日坂路・森秀行検索欄
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

df[['cushion_horse_badge', 'is_cushion_horse_fit', 'is_cushion_horse_danger']] = df.apply(
    lambda r: check_cushion_special_horse(r, current_bin_name), axis=1
)

df['cushion_badge_raw'] = df.apply(
    lambda r: evaluate_sire_cushion(r['種牡馬'], r['競馬場名'], r['dist'], current_band) if '芝' in str(r.get('track', '')) else '', axis=1
)
df['is_cushion_fit'] = df['cushion_badge_raw'].str.contains('特注')
df['is_cushion_danger'] = df['cushion_badge_raw'].str.contains('危険')

# 1着狙い・軸連対狙い・紐穴判定
df['target_win'] = (
    (
        df['is_prev_han_solid']
        | (df['is_f1_accel'] & df['has_sharp_finishing'])
        | ((df['F_rank'] == 1) & (df['人気'] == 1) & (df['枠番'] <= 6) & df['has_sharp_finishing'])
        | df['is_arms_fup_super']
        | df['is_c_real_gold']
        | (df['is_iron_f72'] & (df['枠番'] <= 6) & (~df['is_cushion_danger']))
        | df['is_sss_level']
        | (df['flag_fup6_sf_any'] & (df['枠番'] <= 6))
        | ((df['F_rank'] == 1) & (df['arms_rank'] == 1) & (df['枠番'] <= 6) & df['has_sharp_finishing'])
        | ((df['Fup'] >= 5) & (df['F_rank'] == 1) & (df['枠番'] <= 6))
        | ((df['F指数'] >= 66) & (df['arms_rank'] == 1) & (df['枠番'] <= 6) & df['has_sharp_finishing'])
        | (df['is_short_sakaro_full'] & (df['F_rank'] <= 2) & (df['枠番'] <= 6))
        | (df['is_kyoto_sakaro_full'] & (df['F_rank'] <= 2) & (df['枠番'] <= 6))
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
    | (df['is_same_waku'] & (df['S_rank'] <= 6) & (df['人気'] >= 5))
    | (df['is_mile_wood_big_accel'] & (df['人気'] >= 5))
)

st.sidebar.markdown('---')
st.sidebar.markdown('### ⏱️ 前日坂路・調教検索')
search_prev_han = st.sidebar.text_input('前日坂路・厩舎検索', placeholder='例: 前日坂路, 堀, 森秀行, 加藤征...', label_visibility='collapsed')
filter_prev_han_all = st.sidebar.checkbox(f"🏇 前日坂路あり全頭 ({int(df['has_prev_han'].sum())}頭)")
filter_prev_han_fast = st.sidebar.checkbox(f"🔥 前日坂路65秒以下 ({int(df['has_prev_han_fast'].sum())}頭)", help='勝負気配・平均より2〜3秒以上速い')
filter_prev_han_solid = st.sidebar.checkbox(f"👑 前日坂路×王道上位人気 ({int(df['is_prev_han_solid'].sum())}頭)", help='堀・中内田・森秀行等×1〜3番人気(勝率40%超)')
filter_prev_han_bomb = st.sidebar.checkbox(f"💣 前日坂路×加藤征等穴馬 ({int(df['is_prev_han_bomb'].sum())}頭)", help='6番人気以下×単回収100%超')
filter_prev_wood_dirt = st.sidebar.checkbox(f"🏜️ ダート×前日ウッド追い ({int(df['is_prev_wood_dirt'].sum())}頭)", help='稲垣厩舎等×単回収110%超')

# ==============================================================================
# ★ 既存フィルター設定
# ==============================================================================
st.sidebar.markdown('---')
st.sidebar.markdown('### 👑 黄金シナジー・絶対軸馬')
syn_iron = st.sidebar.checkbox(f"💎 鉄板軸馬 ({int(df['is_syn_iron'].sum())}頭)", help='複勝率 61.9% / 連対率 46.3%')
syn_high = st.sidebar.checkbox(f"🔥 高確率軸馬 ({int(df['is_syn_high'].sum())}頭)", help='複勝率 55%超ゾーン')
filter_s_accel = st.sidebar.checkbox(f"👑 S1-3位×調教加速 最高安定軸 ({int(df['is_s_top_accel'].sum())}頭)", help='複勝率51.5%ゾーン')
filter_target_win = st.sidebar.checkbox(f"🥇 1着狙い ({int(df['target_win'].sum())}頭)")
filter_target_axis = st.sidebar.checkbox(f"🛡️ 軸・連対狙い ({int(df['target_axis'].sum())}頭)")
filter_waku_gold = st.sidebar.checkbox(f"👑 同枠×F1-2位 特注軸 ({int(df['waku_gold'].sum())}頭)", help='複勝率53.3%ゾーン')
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
        1. **阪神芝1800外 × キズナ** (9.5-9.9) - 勝19.6% / 単回421
        2. **東京芝1600 × エピファネイア** (9.5-9.9) - 勝13.3% / 単回277
        3. **東京芝1400 × モーリス** (9.5-9.9) - 勝10.1% / 単回408
        4. **東京芝1800 × ディープインパクト** (9.5-9.9) - 勝15.8% / 単回228
        5. **東京芝2000 × キズナ** (8.6-9.4) - 勝19.7% / 単回200
        6. **中京芝2000 × ディープインパクト** (8.6-9.4) - 勝18.0% / 単回178
        7. **東京芝1600 × イスラボニータ** (8.6-9.4) - 勝10.5% / 単回350
        8. **東京芝2000 × エピファネイア** (8.6-9.4) - 勝15.3% / 単回149
        9. **函館芝1800 × キズナ** (≤8.5低) - 勝17.7% / 単回143
        10. **小倉芝1200 × ダイワメジャー** (9.5-9.9) - 勝13.6% / 単回173
        """)
    with col_rk2:
        st.markdown("""
        11. **札幌芝2000 × オルフェーヴル** (≤8.5低) - 勝15.8% / 単回136
        12. **東京芝1400 × ロードカナロア** (8.6-9.4) - 勝15.6% / 単回123
        13. **阪神芝1600外 × ルーラーシップ** (8.6-9.4) - 勝20.0% / 単回156
        14. **東京芝1600 × モーリス** (9.5-9.9) - 勝11.1% / 単回100
        15. **阪神芝2000内 × キズナ** (8.6-9.4) - 勝11.8% / 単回152
        16. **東京芝1600 × スクリーンヒーロー** (8.6-9.4) - 勝9.9% / 単回72
        17. **小倉芝1200 × ビッグアーサー** (8.6-9.4) - 勝12.2% / 単回131
        18. **中京芝1600 × ロードカナロア** (10.0-10.4) - 勝14.8% / 単回133
        19. **福島芝1200 × ビッグアーサー** (8.6-9.4) - 勝13.2% / 単回87
        20. **札幌芝1200 × ロードカナロア** (≤8.5低) - 勝15.0% / 単回121
        """)
        
    st.markdown("### ⚠️ RISK LIST 危険・割引対象 上位20")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.markdown("""
        1. **中山芝2000 × ダノンバラード** (9.5-9.9) - 複勝率0.0%
        2. **東京芝2000 × ルーラーシップ** (9.5-9.9) - 複勝率9.1%
        3. **小倉芝1200 × ジャスタウェイ** (8.6-9.4) - 複勝率2.9%
        4. **東京芝1400 × シルバーステート** (8.6-9.4) - 複勝率4.7%
        5. **東京芝1600 × ゴールドシップ** (8.6-9.4) - 複勝率4.5%
        6. **小倉芝1200 × ヴィクトワールピサ** (8.6-9.4) - 複勝率4.8%
        7. **東京芝1800 × ルーラーシップ** (9.5-9.9) - 複勝率10.5%
        8. **阪神芝2000内 × ゴールドシップ** (8.6-9.4) - 複勝率10.0%
        9. **東京芝1600 × エイシンフラッシュ** (8.6-9.4) - 複勝率7.3%
        10. **東京芝2000 × オルフェーヴル** (8.6-9.4) - 複勝率13.2%
        """)
    with col_d2:
        st.markdown("""
        11. **福島芝2000 × ルーラーシップ** (8.6-9.4) - 複勝率4.7%
        12. **新潟芝1400内 × リオンディーズ** (8.6-9.4) - 複勝率6.7%
        13. **東京芝2400 × ゴールドシップ** (9.5-9.9) - 複勝率11.1%
        14. **小倉芝1800 × ルーラーシップ** (9.5-9.9) - 複勝率10.0%
        15. **阪神芝1800外 × ハービンジャー** (9.5-9.9) - 複勝率10.0%
        16. **東京芝1600 × サトノクラウン** (8.6-9.4) - 複勝率9.7%
        17. **福島芝1200 × マツリダゴッホ** (8.6-9.4) - 複勝率5.9%
        18. **東京芝1600 × シルバーステート** (9.5-9.9) - 複勝率8.9%
        19. **福島芝1200 × カレンブラックヒル** (8.6-9.4) - 複勝率9.7%
        20. **中京芝2000 × オルフェーヴル** (8.6-9.4) - 複勝率15.2%
        """)

chosen_venue = st.radio('開催場選択', options=existing_venues, horizontal=True, label_visibility='collapsed')
st.session_state['active_venue'] = chosen_venue

v_df = df[df['競馬場名'] == chosen_venue]
races_in_v = v_df[['race_uid', 'race_id', 'R番号', 'track', 'dist']].drop_duplicates('race_uid').sort_values('R番号')

# ==============================================================================
# レース選択肢の生成
# ==============================================================================
race_options = {}
for _, r_row in races_in_v.iterrows():
    r_horses = df[df['race_uid'] == r_row['race_uid']]

    r_high_c = int((r_horses['is_syn_high'] == True).sum())
    r_iron_c = int((r_horses['is_syn_iron'] == True).sum())
    r_win_c = int((r_horses['target_win'] == True).sum())
    r_axis_c = int((r_horses['target_axis'] == True).sum())
    r_bomb_c = int((r_horses['is_syn_bomb'] == True).sum())

    cond1 = (
        r_high_c >= 2
        or (r_win_c >= 1 and r_axis_c >= 1 and r_bomb_c <= 1)
        or ((r_iron_c >= 1 or r_high_c >= 1 or r_win_c >= 1) and r_bomb_c <= 1)
    )
    f1_h = r_horses[r_horses['F_rank'] == 1]
    f1_val = f1_h['F指数'].values[0] if not f1_h.empty else 0
    cond3 = f1_val >= 60

    is_bonus = bool(((r_horses['F_rank'] <= 3) & (r_horses['arms_rank'] <= 3) & (r_horses['tua_rank'] <= 3)).sum() >= 3)

    if is_bonus: tag = '👑ボーナス'
    elif cond1 and cond3: tag = '🎯狙'
    else: tag = '🔥荒'

    marks = []
    if is_bonus: marks.append('👑超ボーナス')
    if (r_horses['is_prev_han_solid'] == True).any(): marks.append('🔥前坂')
    if (r_horses['is_c_real_gold'] == True).any(): marks.append('👑C')
    if (r_horses['is_arms_fup_super'] == True).any(): marks.append('👑AF')
    if (r_horses['is_s_top_accel'] == True).any(): marks.append('👑S加')
    if (r_horses['is_f1_accel'] == True).any(): marks.append('⚡F加')
    if (r_horses['is_dirt_eat_super'] == True).any(): marks.append('🏜️ダ')
    if r_iron_c >= 1: marks.append('💎鉄')
    if r_high_c >= 1: marks.append('🌟高')
    if (r_horses['is_syn_fup_sakaro'] == True).any(): marks.append('✨坂')
    if (r_horses['is_sss_level'] == True).any(): marks.append('👑神')
    if (r_horses['is_syn_f1_rap'] == True).any(): marks.append('⚡極')
    if r_bomb_c >= 1: marks.append('💣爆')
    if (r_horses['is_cushion_horse_fit'] == True).any(): marks.append('🎯ク')

    if (r_horses['flag_fup6_sf_any'] == True).any(): marks.append('🔥頭')
    if r_win_c >= 1: marks.append('🥇勝')
    if r_axis_c >= 1: marks.append('🛡️軸')
    if (r_horses['waku_gold'] == True).any(): marks.append('👑枠')
    if (r_horses['flag_sf7_himo'] == True).any(): marks.append('🌪️SF')
    if (r_horses['target_himo'] == True).any(): marks.append('🎯使')

    if (r_horses['調教ステータス'] == '鉄板').any(): marks.append('🏛️鉄')
    if (r_horses['調教ステータス'] == '勝負').any(): marks.append('⚔️厩')
    if (r_horses['調教ステータス'] == '特注').any(): marks.append('💎特')

    lbl = f"{tag} {r_row['R番号']}R ({r_row['track']}{r_row['dist']}m) [{' '.join(marks)}]"
    race_options[r_row['race_uid']] = lbl

if not race_options:
    st.warning("⚠️ 選択した競馬場のレースデータが見つかりません。")
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

# ==============================================================================
# ★ 動的優先度スコアリング計算
# ==============================================================================
cur_track_type = race_df['track'].iloc[0] if not race_df.empty else '芝'
cur_dist_val = int(re.sub(r'\D', '', str(race_df['dist'].iloc[0]))) if not race_df.empty else 1600

def calculate_dynamic_priority_score(r):
    score = 0.0
    f_r = r.get('F_rank', 99)
    s_r = r.get('S_rank', 99)
    a_r = r.get('arms_rank', 99)
    t_r = r.get('tua_rank', 99)
    f_val = r.get('F指数', 0.0)
    arms_val = r.get('arms', 0.0)
    tua_val = r.get('tua', 0.0)
    c_fit = bool(r.get('is_cushion_fit', False))
    c_dang = bool(r.get('is_cushion_danger', False))
    c_tr_fit = bool(r.get('is_course_training_fit', False))
    c_h_fit = bool(r.get('is_cushion_horse_fit', False))
    c_h_dang = bool(r.get('is_cushion_horse_danger', False))
    sakaro_full = bool(r.get('坂路_完全加速', False))
    wood_acc = bool(r.get('is_wood_accel', False))
    tr_stat = str(r.get('調教ステータス', ''))
    waku_val = r.get('枠番', 8)
    prev_han = bool(r.get('has_prev_han', False))
    
    style = str(r.get('脚質', ''))
    is_senko = '先' in style
    is_nige = '逃' in style
    is_sashi = '差' in style
    is_oikomi = '追' in style
    is_back = '後' in style or '中' in style

    if cur_dist_val <= 1400:
        if is_senko: score += 35.0
        elif is_nige: score += 25.0
        elif is_back: score -= 30.0
    elif 1500 <= cur_dist_val <= 1800:
        if is_senko: score += 25.0
        elif is_sashi: score += 20.0
        if wood_acc and (is_sashi or is_oikomi): score += 20.0
    elif cur_dist_val >= 1900:
        if is_senko: score += 30.0
        elif is_sashi: score += 25.0
        elif is_back: score -= 15.0

    if f_val >= 72.0:
        score += 60.0 if is_senko else (45.0 if is_sashi else 35.0)

    if 'ダ' in cur_track_type:
        if s_r <= 3 and a_r <= 3 and is_sashi:
            score += 50.0
        if f_r == 1 and a_r <= 3 and is_senko:
            score += 45.0
    else:
        if f_r == 1 and a_r <= 3 and is_senko:
            score += 45.0

    if r.get('is_prev_han_solid', False): score += 60.0
    elif r.get('has_prev_han_fast', False): score += 30.0
    elif prev_han: score += 15.0

    if r.get('is_prev_han_bomb', False): score += 40.0
    if r.get('is_prev_wood_dirt', False): score += 40.0

    if r.get('is_f1_accel', False): score += 55.0
    if r.get('is_s_top_accel', False): score += 45.0
    if r.get('waku_gold', False): score += 35.0
    if r.get('is_mile_wood_big_accel', False): score += 40.0
    if r.get('is_kyoto_sakaro_full', False): score += 30.0
    if r.get('is_short_sakaro_full', False): score += 30.0

    if r.get('target_win', False): score += 45.0
    if r.get('is_arms_fup_super', False): score += 60.0
    elif r.get('is_arms_fup_solid', False): score += 35.0
    if r.get('is_c_real_gold', False): score += 40.0

    if r.get('is_sss_level', False): score += 50.0
    if r.get('is_fup_axis', False): score += 35.0

    if waku_val in [1, 2, 3]: score += 15.0
    elif waku_val in [7, 8]: score -= 25.0

    if 'ダ' in cur_track_type:
        if r.get('is_dirt_eat_super', False): score += 50.0
        elif tua_val >= 190.0 and t_r <= 3: score += 30.0
        
        if cur_dist_val <= 1400:
            score += (100 - s_r * 8) + (100 - f_r * 4)
            if sakaro_full: score += 40.0
        else:
            score += (100 - f_r * 8) + (100 - t_r * 8) + (100 - a_r * 4)
            if sakaro_full: score += 25.0
        if c_tr_fit: score += 25.0
    else:
        if c_h_fit: score += 40.0
        if c_fit: score += 30.0
        if 1500 <= cur_dist_val <= 1800:
            score += (100 - f_r * 7) + (100 - a_r * 5)
            if sakaro_full and wood_acc: score += 35.0
            elif sakaro_full or wood_acc: score += 15.0
        elif cur_dist_val >= 2000:
            score += (100 - a_r * 9) + (100 - f_r * 4) + (100 - t_r * 3)
            if r.get('is_syn_f1_rap', False): score += 35.0
        else:
            score += (100 - s_r * 7) + (100 - f_r * 5)
        if c_tr_fit: score += 25.0

    if tr_stat == '鉄板': score += 45.0
    elif tr_stat == '勝負': score += 30.0
    elif tr_stat == '特注': score += 20.0

    if arms_val >= 120.0: score += 25.0
    if r.get('is_syn_bomb', False): score += 20.0

    if r.get('is_dirt_wood_trap', False): score -= 65.0
    if r.get('is_valley_trap', False): score -= 55.0
    if r.get('is_c_fake_trap', False): score -= 45.0
    if c_h_dang: score -= 50.0
    if c_dang: score -= 40.0
    if tr_stat == '危険': score -= 45.0
    if r.get('is_fup_trap', False): score -= 65.0
    if r.get('is_danger_jockey', False): score -= 20.0
    if r.get('is_short_back_trap', False): score -= 40.0

    return score

race_df['dynamic_score'] = race_df.apply(calculate_dynamic_priority_score, axis=1)
sorted_dynamic = race_df.sort_values('dynamic_score', ascending=False)

# ==============================================================================
# ★ レース判定 ＆ プロの推奨買い目生成
# ==============================================================================
r_high_cnt = int((race_df['is_syn_high'] == True).sum())
r_iron_cnt = int((race_df['is_syn_iron'] == True).sum())
r_win_cnt = int((race_df['target_win'] == True).sum())
r_axis_cnt = int((race_df['target_axis'] == True).sum())
r_bomb_cnt = int((race_df['is_syn_bomb'] == True).sum())

f1_cur = race_df[race_df['F_rank'] == 1]
f1_val_cur = float(f1_cur['F指数'].values[0]) if not f1_cur.empty else 0.0
is_f1_ok = f1_val_cur >= 60

is_bonus_cur = bool(((race_df['F_rank'] <= 3) & (race_df['arms_rank'] <= 3) & (race_df['tua_rank'] <= 3)).sum() >= 3)
is_solid = (
    r_high_cnt >= 2
    or (r_win_cnt >= 1 and r_axis_c >= 1 and r_bomb_c <= 1)
    or ((r_iron_c >= 1 or r_high_c >= 1 or r_win_c >= 1) and r_bomb_c <= 1)
)
is_go = (is_solid and is_f1_ok) or is_bonus_cur

top3_fav_horses = race_df[race_df['人気'].isin([1, 2, 3])]['馬番'].tolist()

def get_horse_hierarchy_rank(r):
    p_rank = 0
    if r.get('F指数', 0) >= 72.0:
        p_rank += 600 if bool(r.get('is_cushion_danger')) else 1000
    elif r.get('F_rank', 99) == 1:
        p_rank += 500
    
    style = str(r.get('脚質', ''))
    if '先' in style: p_rank += 300
    elif '差' in style: p_rank += 200
    elif '後' in style or '中' in style: p_rank -= 300

    if bool(r.get('is_cushion_fit', False)) or bool(r.get('is_cushion_horse_fit', False)): p_rank += 150
    if bool(r.get('is_cushion_danger', False)) or bool(r.get('is_cushion_horse_danger', False)): p_rank -= 400

    if str(r.get('調教ステータス')) == '鉄板' or bool(r.get('is_prev_han_solid')): p_rank += 120
    elif str(r.get('調教ステータス')) == '勝負' or bool(r.get('坂路_完全加速')) or bool(r.get('坂路_森加速')): p_rank += 80

    if bool(r.get('has_sharp_finishing')): p_rank += 80

    if r.get('枠番', 8) <= 6: p_rank += 50
    else: p_rank -= 50

    return p_rank

sorted_dynamic['hierarchy_rank'] = sorted_dynamic.apply(get_horse_hierarchy_rank, axis=1)
hierarchy_sorted = sorted_dynamic.sort_values(['hierarchy_rank', 'dynamic_score'], ascending=[False, False])

pick_win_horse = hierarchy_sorted.iloc[0]
axis_cands = hierarchy_sorted[hierarchy_sorted['馬番'] != pick_win_horse['馬番']]
pick_axis_horse = axis_cands.iloc[0] if not axis_cands.empty else pick_win_horse

has_iron_solo = (
    pick_win_horse.get('F指数', 0) >= 72.0
    and '先' in str(pick_win_horse.get('脚質', ''))
    and not bool(pick_win_horse.get('is_cushion_danger'))
)
score_gap = pick_win_horse['dynamic_score'] - (pick_axis_horse['dynamic_score'] if len(hierarchy_sorted) > 1 else 0)
is_dominant_single = has_iron_solo or (score_gap >= 25.0)

himo_cands = sorted_dynamic[
    (sorted_dynamic['人気'] >= 4)
    & (
        sorted_dynamic['target_himo'] | sorted_dynamic['is_syn_bomb'] | sorted_dynamic['flag_sf7_himo']
        | sorted_dynamic['is_prev_han_bomb'] | sorted_dynamic['is_prev_wood_dirt']
        | sorted_dynamic['is_course_training_fit'] | sorted_dynamic['is_cushion_horse_fit'] | (sorted_dynamic['調教ステータス'] == '特注')
    )
]
pick_himo_horse = himo_cands.iloc[0] if not himo_cands.empty else (sorted_dynamic.iloc[-1] if len(sorted_dynamic) > 2 else pick_axis_horse)

danger_cands = race_df[
    (race_df['人気'] <= 5)
    & (
        race_df['is_fup_trap'] | race_df['is_c_fake_trap'] | race_df['is_valley_trap']
        | race_df['is_dirt_wood_trap'] | race_df['is_cushion_danger'] | race_df['is_cushion_horse_danger']
        | (race_df['調教ステータス'] == '危険') | race_df['is_short_back_trap']
    )
]
pick_danger_horse = danger_cands.iloc[0] if not danger_cands.empty else None

rec_c1 = [pick_win_horse['馬番']] if is_dominant_single else [pick_win_horse['馬番'], pick_axis_horse['馬番']]

max_c2 = 3 if cur_dist_val >= 2200 else (4 if is_dominant_single else 5)
rec_c2 = list(rec_c1)
for u in hierarchy_sorted['馬番'].tolist():
    h_row = race_df[race_df['馬番'] == u].iloc[0]
    if (u not in rec_c2 
        and not h_row.get('is_fup_trap', False) 
        and not h_row.get('is_c_fake_trap', False)
        and not h_row.get('is_valley_trap', False)
        and not h_row.get('is_dirt_wood_trap', False)
        and not h_row.get('is_cushion_danger', False)
        and not (h_row.get('調教ステータス') == '危険')
        and not h_row.get('is_short_back_trap', False)):
        rec_c2.append(u)
    if len(rec_c2) >= max_c2: break

max_c3 = 6 if cur_dist_val >= 2200 else (8 if cur_dist_val <= 1400 else 7)
rec_c3 = list(rec_c2)
for u in (
    sorted_dynamic.head(8)['馬番'].tolist()
    + race_df[race_df['waku_gold']]['馬番'].tolist()
    + race_df[race_df['is_s_top_accel']]['馬番'].tolist()
    + race_df[race_df['is_prev_han_bomb']]['馬番'].tolist()
    + race_df[race_df['is_prev_wood_dirt']]['馬番'].tolist()
    + race_df[race_df['is_mile_wood_big_accel']]['馬番'].tolist()
    + race_df[race_df['is_course_training_fit']]['馬番'].tolist()
    + race_df[race_df['is_cushion_horse_fit']]['馬番'].tolist()
    + race_df[race_df['is_dirt_eat_super']]['馬番'].tolist()
    + race_df[race_df['is_c_real_gold']]['馬番'].tolist()
    + race_df[race_df['flag_sf7_himo']]['馬番'].tolist()
    + race_df[race_df['is_syn_bomb']]['馬番'].tolist()
    + race_df[race_df['調教ステータス'].isin(['勝負', '特注'])]['馬番'].tolist()
):
    h_row = race_df[race_df['馬番'] == u].iloc[0]
    if (u not in rec_c3 
        and not h_row.get('is_valley_trap', False)
        and not h_row.get('is_dirt_wood_trap', False)
        and not h_row.get('is_cushion_danger', False)):
        rec_c3.append(u)
    if len(rec_c3) >= max_c3: break

# ==============================================================================
# ★ 出走馬カード用の推奨買い目印（◎、◯、▲、△、★）辞書生成
# ==============================================================================
bet_marks_dict = {}
p_win_u = int(pick_win_horse['馬番'])
p_axis_u = int(pick_axis_horse['馬番'])
p_himo_u = int(pick_himo_horse['馬番'])

bet_marks_dict[p_win_u] = "<span class='badge-mark-honmei'>◎</span>"
if p_axis_u != p_win_u:
    bet_marks_dict[p_axis_u] = "<span class='badge-mark-taikou'>◯</span>"

c2_remaining = [u for u in rec_c2 if u not in [p_win_u, p_axis_u]]
if c2_remaining:
    bet_marks_dict[c2_remaining[0]] = "<span class='badge-mark-tanana'>▲</span>"
    for u in c2_remaining[1:]:
        bet_marks_dict[u] = "<span class='badge-mark-himo'>△</span>"

for u in rec_c3:
    if u not in bet_marks_dict:
        bet_marks_dict[u] = "<span class='badge-mark-himo'>△</span>"

if p_himo_u not in [p_win_u, p_axis_u]:
    bet_marks_dict[p_himo_u] = "<span class='badge-mark-ana'>★</span>"

trio_combinations = set()
for h1, h2, h3 in itertools.product(rec_c1, rec_c2, rec_c3):
    trio = tuple(sorted([h1, h2, h3]))
    if len(trio) == 3 and any(fav in top3_fav_horses for fav in trio) and trio not in trio_combinations:
        trio_combinations.add(trio)
trio_pts = len(trio_combinations)

single_bets = [str(int(rec_c1[0]))] if pick_win_horse.get('target_win') else []

main_axis = rec_c1[0]
wide_opponents = [str(int(u)) for u in ([pick_himo_horse['馬番']] + [h for h in rec_c3 if h != main_axis and h in race_df[race_df['人気'] >= 4]['馬番'].tolist()]) if u != main_axis]
wide_opponents = list(dict.fromkeys(wide_opponents))[:2]
if not wide_opponents: wide_opponents = [str(int(u)) for u in rec_c2 if u != main_axis][:2]
wide_str = f"{int(main_axis)} - {', '.join(wide_opponents)}"

p1_1st = [rec_c1[0]]
p1_2nd = [h for h in rec_c2 if h not in p1_1st][:3]
p1_3rd = list(dict.fromkeys([h for h in rec_c3 if h not in p1_1st and h not in p1_2nd][:4] + p1_2nd))
trifecta_p1 = [(a, b, c) for a in p1_1st for b in p1_2nd for c in p1_3rd if len({a, b, c}) == 3]

p2_1st = [pick_himo_horse['馬番']] if pick_himo_horse['馬番'] != rec_c1[0] else ([rec_c2[1]] if len(rec_c2) > 1 else [])
p2_2nd = [rec_c1[0]]
p2_3rd = [h for h in rec_c3 if h not in p2_1st and h not in p2_2nd][:5]
trifecta_p2 = [(a, b, c) for a in p2_1st for b in p2_2nd for c in p2_3rd if len({a, b, c}) == 3]

p3_1st = [h for h in rec_c2 if h != rec_c1[0]][:2]
p3_2nd = [rec_c1[0]]
p3_3rd = [h for h in rec_c3 if h not in p3_1st and h not in p3_2nd][:5]
trifecta_p3 = [(a, b, c) for a in p3_1st for b in p3_2nd for c in p3_3rd if len({a, b, c}) == 3]

p1_c1_str = ', '.join(str(int(u)) for u in p1_1st); p1_c2_str = ', '.join(str(int(u)) for u in p1_2nd); p1_c3_str = ', '.join(str(int(u)) for u in p1_3rd)
p2_c1_str = ', '.join(str(int(u)) for u in p2_1st); p2_c2_str = ', '.join(str(int(u)) for u in p2_1st); p2_c3_str = ', '.join(str(int(u)) for u in p2_3rd)
p3_c1_str = ', '.join(str(int(u)) for u in p3_1st); p3_c2_str = ', '.join(str(int(u)) for u in p3_2nd); p3_c3_str = ', '.join(str(int(u)) for u in p3_3rd)

wave_label = '【👑 ボーナスレース (F・arms・tua 独占)】' if is_bonus_cur else ('【堅調（1頭突出）】' if is_dominant_single else ('【堅調】' if is_go else '【混戦・波乱】'))

if cur_dist_val <= 1400:
    dist_ticket_label = '【短距離戦：厳選単勝 ＋ ワイド流し・BOX ＋ 3連複ヒモ手広く】'
elif 1500 <= cur_dist_val <= 2000:
    dist_ticket_label = '【マイル〜中距離：3連複少数厚張り ＋ 馬単表裏 / 3連単マルチ】' if is_go else '【マイル〜中距離：単勝 ＋ ワイド ＋ 3連複フォーメーション】'
else:
    dist_ticket_label = '【長距離戦：馬連集中 ＋ 3連複少数精鋭】'

ticket_type_label = dist_ticket_label
banner_cls = 'race-type-bonus' if is_bonus_cur else ('race-type-solid' if is_go else 'race-type-chaos')
panel_cls = 'recom-panel-go' if is_go else 'recom-panel-chaos'
title_cls = 'recom-title-go' if is_go else 'recom-title-chaos'
pts_cls = 'recom-pts' if is_go else 'recom-pts-chaos'

st.markdown(f"<div class='race-type-banner {banner_cls}'><div><strong>🎯 レース判定: {wave_label}</strong></div><div>推奨券種: {ticket_type_label}</div></div>", unsafe_allow_html=True)

danger_str = (
    f"{int(pick_danger_horse['馬番'])}番 {pick_danger_horse['馬名']}（人気{int(pick_danger_horse['人気'])} / Fup{int(pick_danger_horse['Fup'])}点 / {'短距離後方消し・' if pick_danger_horse.get('is_short_back_trap') else ''}{'偽C馬・' if pick_danger_horse.get('is_c_fake_trap') else ''}{'谷の形・' if pick_danger_horse.get('is_valley_trap') else ''}{'ダート×ウッド加速消し・' if pick_danger_horse.get('is_dirt_wood_trap') else ''}罠・適性割引・{pick_danger_horse.get('調教ステータス', '')}調教）"
    if pick_danger_horse is not None else '該当なし（上位人気堅調）'
)

def get_horse_extra_tag(h_series):
    tags = []
    if h_series.get('is_prev_han_solid'): tags.append("🔥 前日坂路×王道厩舎(勝率40%+)")
    elif h_series.get('has_prev_han_fast'): tags.append("⏱️ 前日坂路65秒以下")
    if h_series.get('is_prev_han_bomb'): tags.append("💣 前日坂路穴馬(加藤征等)")
    if h_series.get('is_prev_wood_dirt'): tags.append("🏜️ ダート×前日ウッド(単回110%+)")
    if h_series.get('is_f1_accel'): tags.append("⚡ F1位×加速(勝45%)")
    if h_series.get('is_s_top_accel'): tags.append("👑 S1-3×加速(複51.5%)")
    if h_series.get('is_c_real_gold'): tags.append("👑 本物C馬(Fup4+)")
    if h_series.get('is_arms_fup_super'): tags.append("👑 ARMS×Fup黄金軸")
    if h_series.get('is_dirt_eat_super'): tags.append("🏜️ ダートで食う勝負馬")
    if h_series.get('is_iron_f72'): tags.append("⚡ F>72鉄板")
    if h_series.get('is_fup_axis'): tags.append("👑 Fup最上位軸")
    if h_series.get('waku_gold'): tags.append("👑 同枠×F1-2位(複53.3%)")
    if h_series.get('is_mile_wood_big_accel'): tags.append("🚀 マイル×W大加速(複44%)")
    if h_series.get('is_cushion_fit'): tags.append("🟢 クッション特注(上位ランク)")
    if h_series.get('is_cushion_horse_fit'): tags.append(f"🎯 クッション個体特注 ({current_bin_name}巧者)")
    tr_flag = h_series.get('厩舎狙い目フラグ', '')
    if tr_flag: tags.append(f"🏛️ {tr_flag}")
    return f" / {' / '.join(tags)}" if tags else ""

st.markdown(
    f"<div class='{panel_cls}'><div class='{title_cls}'>📋 推奨馬ピックアップ（前日調教＆指数統合）</div>"
    f"<div class='recom-row'>🥇 <strong>1着狙い（単勝厳選）</strong>: <span class='recom-val-num'>{int(pick_win_horse['馬番'])}番 {pick_win_horse['馬名']}</span>（動的適性最上位スコア / F{int(pick_win_horse['F_rank'])}位 × 枠{int(pick_win_horse['枠番'])}{get_horse_extra_tag(pick_win_horse)}）</div>"
    f"<div class='recom-row'>🛡️ <strong>軸・連対狙い（最高安定軸）</strong>: <span class='recom-val-num'>{int(pick_axis_horse['馬番'])}番 {pick_axis_horse['馬名']}</span>（F{int(pick_axis_horse['F_rank'])}位 × S{int(pick_axis_horse['S_rank'])}位 / 連対圏確度{get_horse_extra_tag(pick_axis_horse)}）</div>"
    f"<div class='recom-row'>💣 <strong>紐穴狙い</strong>: <span class='recom-val-num'>{int(pick_himo_horse['馬番'])}番 {pick_himo_horse['馬名']}</span>（{int(pick_himo_horse['人気'])}人気 / Fup{int(pick_himo_horse['Fup'])}点 / 前日調教・穴トリガー{get_horse_extra_tag(pick_himo_horse)}）</div>"
    f"<div class='recom-row'>⚠️ <strong>危険な人気馬</strong>: {danger_str}</div></div>",
    unsafe_allow_html=True,
)

c1_str = ', '.join(str(int(u)) for u in rec_c1)
c2_str = ', '.join(str(int(u)) for u in rec_c2)
c3_str = ', '.join(str(int(u)) for u in rec_c3)

single_disp = ', '.join(single_bets) if single_bets else '条件合致なし（見送り推奨）'
single_cnt = len(single_bets)

st.markdown(
    f"<div class='{panel_cls}'><div class='{title_cls}'>🎫 推奨買い目（実戦フォーメーション改善規定）</div>"
    f"<div class='recom-block'><span class='recom-label'>🎫 【本線：3連複フォーメーション】</span> <span class='{pts_cls}'>計 {trio_pts}点</span><br>&nbsp;&nbsp;&nbsp;&nbsp;<strong>1列目(軸)</strong>: <span class='recom-val-num'>{c1_str}</span>&nbsp;&nbsp;→&nbsp;&nbsp;<strong>2列目(相手)</strong>: <span class='recom-val-num'>{c2_str}</span>&nbsp;&nbsp;→&nbsp;&nbsp;<strong>3列目(ヒモ広め)</strong>: <span class='recom-val-num'>{c3_str}</span></div>"
    f"<div class='recom-block'><span class='recom-label'>🛡️ 【抑え・資金回収：ワイド ＆ 馬単表裏】</span><br>&nbsp;&nbsp;ワイド流し: <span class='recom-val-num'>{wide_str}</span> <span class='{pts_cls}'>計 {len(wide_opponents)}点</span><br>&nbsp;&nbsp;馬単表裏: <span class='recom-val-num'>{int(main_axis)} ⇄ {c2_str}</span></div>"
    f"<div class='recom-block'><span class='recom-label'>🥇 【厳選単勝】</span>&nbsp;&nbsp;<span class='recom-val-num'>{single_disp}</span> <span class='{pts_cls}'>計 {single_cnt}点</span>（※F1位×終い加速12.2s/11.4s以下×1〜6枠または前日坂路王道馬）</div>"
    f"<div class='recom-block'><span class='recom-label'>💥 【3連単フォーメーション（本命・穴頭・2着軸マルチ）】</span><br>&nbsp;&nbsp;<strong>パターンA（本命地力型・計{len(trifecta_p1)}点）</strong>: <span class='recom-val-num'>{p1_c1_str}</span> → <span class='recom-val-num'>{p1_c2_str}</span> → <span class='recom-val-num'>{p1_c3_str}</span><br>&nbsp;&nbsp;<strong>パターンB（穴頭急襲型・計{len(trifecta_p2)}点）</strong>: <span class='recom-val-num'>{p2_c1_str}</span> → <span class='recom-val-num'>{p2_c2_str}</span> → <span class='recom-val-num'>{p2_c3_str}</span><br>&nbsp;&nbsp;<strong>パターンC（軸2着連軸マルチ・計{len(trifecta_p3)}点）</strong>: <span class='recom-val-num'>{p3_c1_str}</span> → <span class='recom-val-num'>{p3_c2_str}</span> → <span class='recom-val-num'>{p3_c3_str}</span></div></div>",
    unsafe_allow_html=True,
)

# ==============================================================================
# ★ 出走馬カード表示 ＆ フィルター適用
# ==============================================================================
sidebar_filter_active = (
    bool(search_prev_han)
    or filter_prev_han_all or filter_prev_han_fast or filter_prev_han_solid or filter_prev_han_bomb or filter_prev_wood_dirt
    or syn_iron or syn_high or filter_s_accel or filter_target_win or filter_target_axis or filter_waku_gold
    or filter_c_gold or filter_arms_fup or filter_iron_f72 or filter_fup_axis or syn_fup_sakaro or syn_f1_rap
    or syn_bomb or filter_mile_wood or filter_dirt_eat or filter_cushion_horse or filter_value_arms or filter_fup6_sf
    or filter_sf7_himo or filter_target_himo or filter_tr_teppan or filter_tr_shobu or filter_tr_tokuchu
    or filter_dirt_wood or filter_c_fake or filter_valley_trap or filter_danger_jockey or filter_fup_trap or filter_tr_danger
)

if sidebar_filter_active:
    filtered_df = df.copy()
else:
    filtered_df = race_df.copy()

filtered_df = populate_all_derived_columns(filtered_df)

filtered_df['cushion_badge'] = filtered_df.get('cushion_badge_raw', '')
filtered_df['cushion_horse_badge'] = filtered_df.get('cushion_horse_badge', '')
filtered_df['course_training_badge'] = filtered_df.get('course_training_badge', '')
filtered_df['tr_badge'] = filtered_df.get('tr_badge_html', '')

if search_prev_han:
    filtered_df = filtered_df[
        filtered_df['馬名'].str.contains(search_prev_han, na=False)
        | filtered_df['調教師'].str.contains(search_prev_han, na=False)
        | filtered_df['騎手'].str.contains(search_prev_han, na=False)
        | (filtered_df['has_prev_han'] if '前日坂路' in search_prev_han else False)
    ]

if filter_prev_han_all: filtered_df = filtered_df[filtered_df['has_prev_han']]
if filter_prev_han_fast: filtered_df = filtered_df[filtered_df['has_prev_han_fast']]
if filter_prev_han_solid: filtered_df = filtered_df[filtered_df['is_prev_han_solid']]
if filter_prev_han_bomb: filtered_df = filtered_df[filtered_df['is_prev_han_bomb']]
if filter_prev_wood_dirt: filtered_df = filtered_df[filtered_df['is_prev_wood_dirt']]

if syn_iron: filtered_df = filtered_df[filtered_df['is_syn_iron']]
if syn_high: filtered_df = filtered_df[filtered_df['is_syn_high']]
if filter_s_accel: filtered_df = filtered_df[filtered_df['is_s_top_accel']]
if filter_c_gold: filtered_df = filtered_df[filtered_df['is_c_real_gold']]
if filter_arms_fup: filtered_df = filtered_df[filtered_df['is_arms_fup_super']]
if filter_dirt_eat: filtered_df = filtered_df[filtered_df['is_dirt_eat_super']]
if filter_iron_f72: filtered_df = filtered_df[filtered_df['is_iron_f72']]
if filter_fup_axis: filtered_df = filtered_df[filtered_df['is_fup_axis']]
if syn_fup_sakaro: filtered_df = filtered_df[filtered_df['is_syn_fup_sakaro']]
if syn_f1_rap: filtered_df = filtered_df[filtered_df['is_syn_f1_rap']]
if syn_bomb: filtered_df = filtered_df[filtered_df['is_syn_bomb']]
if filter_mile_wood: filtered_df = filtered_df[filtered_df['is_mile_wood_big_accel']]
if filter_cushion_horse: filtered_df = filtered_df[filtered_df['is_cushion_horse_fit']]
if filter_value_arms: filtered_df = filtered_df[filtered_df['is_value_arms120']]
if filter_fup6_sf: filtered_df = filtered_df[filtered_df['flag_fup6_sf_any']]
if filter_target_win: filtered_df = filtered_df[filtered_df['target_win']]
if filter_target_axis: filtered_df = filtered_df[filtered_df['target_axis']]
if filter_waku_gold: filtered_df = filtered_df[filtered_df['waku_gold']]
if filter_sf7_himo: filtered_df = filtered_df[filtered_df['flag_sf7_himo']]
if filter_target_himo: filtered_df = filtered_df[filtered_df['target_himo']]
if filter_tr_teppan: filtered_df = filtered_df[filtered_df['調教ステータス'] == '鉄板']
if filter_tr_shobu: filtered_df = filtered_df[filtered_df['調教ステータス'] == '勝負']
if filter_tr_tokuchu: filtered_df = filtered_df[filtered_df['調教ステータス'] == '特注']
if filter_dirt_wood: filtered_df = filtered_df[filtered_df['is_dirt_wood_trap']]
if filter_c_fake: filtered_df = filtered_df[filtered_df['is_c_fake_trap']]
if filter_valley_trap: filtered_df = filtered_df[filtered_df['is_valley_trap']]
if filter_danger_jockey: filtered_df = filtered_df[filtered_df['is_danger_jockey']]
if filter_fup_trap: filtered_df = filtered_df[filtered_df['is_fup_trap']]
if filter_tr_danger: filtered_df = filtered_df[filtered_df['調教ステータス'] == '危険']

col_s1, col_s2 = st.columns([2.5, 1.5])
with col_s1:
    kw = st.text_input('🔍 馬名・騎手・調教師・父名・脚質で検索', placeholder='検索ワードを入力...', label_visibility='collapsed')
    if kw:
        filtered_df = filtered_df[
            filtered_df['馬名'].str.contains(kw, na=False) | filtered_df['騎手'].str.contains(kw, na=False)
            | filtered_df['調教師'].str.contains(kw, na=False) | filtered_df['種牡馬'].str.contains(kw, na=False)
            | filtered_df['脚質'].str.contains(kw, na=False)
        ]
with col_s2:
    sort_opt = st.selectbox(
        '並び順',
        ['単勝人気順 (1人気→)', '🚀 調教加速順 (W加速幅・坂路完全)', 'レース順 (場・R番号)', '馬番順', '🔥 F指数 順位 (1位→)', '⚡ S指数 順位 (1位→)', '🚀 arms指数 順位 (1位→)', '🛡️ tua指数 順位 (1位→)', '✨ Fup 順位 (1位→)'],
        index=0 if not sidebar_filter_active else 2, label_visibility='collapsed'
    )

if sort_opt == '単勝人気順 (1人気→)': filtered_df = filtered_df.sort_values(['人気', '競馬場名', 'R番号', '馬番'])
elif sort_opt == '🚀 調教加速順 (W加速幅・坂路完全)':
    filtered_df['sort_accel_score'] = filtered_df['wood_accel'].fillna(-99.0) + (filtered_df['坂路_完全加速'].astype(int) * 2.0)
    filtered_df = filtered_df.sort_values(['sort_accel_score', '人気'], ascending=[False, True])
elif sort_opt == 'レース順 (場・R番号)': filtered_df = filtered_df.sort_values(['競馬場名', 'R番号', '馬番'])
elif sort_opt == '🔥 F指数 順位 (1位→)': filtered_df = filtered_df.sort_values(['F_rank', '馬番'])
elif sort_opt == '⚡ S指数 順位 (1位→)': filtered_df = filtered_df.sort_values(['S_rank', '馬番'])
elif sort_opt == '🚀 arms指数 順位 (1位→)': filtered_df = filtered_df.sort_values(['arms_rank', '馬番'])
elif sort_opt == '🛡️ tua指数 順位 (1位→)': filtered_df = filtered_df.sort_values(['tua_rank', '馬番'])
elif sort_opt == '✨ Fup 順位 (1位→)': filtered_df = filtered_df.sort_values(['Fup_rank', '馬番'])
else: filtered_df = filtered_df.sort_values('馬番')

list_scope_label = "【全レース一括抽出】" if sidebar_filter_active else "【レース出走馬】"
st.markdown(f'**{list_scope_label} 出走馬一覧（該当: {len(filtered_df)}頭）**')

for _, row in filtered_df.iterrows():
    badges = []
    
    style_badge = get_running_style_badge(row.get('脚質', ''))
    if style_badge:
        badges.append(style_badge)

    if row.get('is_prev_han_solid'):
        badges.append(f"<span class='badge-prev-fast'>🔥【前日坂路王道】4F {row.get('前日坂路時計'):.1f}s (勝率40%超)</span>")
    elif row.get('is_prev_han_bomb'):
        badges.append(f"<span class='badge-prev-kato'>💣【前日坂路穴特注】4F {row.get('前日坂路時計'):.1f}s (単回100%超)</span>")
    elif row.get('has_prev_han_fast'):
        badges.append(f"<span class='badge-prev-fast'>⏱️【前日坂路早め】4F {row.get('前日坂路時計'):.1f}s</span>")
    elif row.get('has_prev_han'):
        p_time = f"{row.get('前日坂路時計'):.1f}s" if pd.notnull(row.get('前日坂路時計')) and row.get('前日坂路時計') < 900 else "計測有"
        badges.append(f"<span class='badge-prev-han'>🏇【前日坂路あり】{p_time}</span>")

    if row.get('is_prev_wood_dirt'):
        badges.append("<span class='badge-prev-wood-dirt'>🏜️【ダート×前日ウッド】単回110%超</span>")

    if row.get('is_c_real_gold'): badges.append("<span class='badge-c-gold'>👑【本物C馬】Fup4+黄金パターン</span>")
    elif row.get('is_c_fake_trap'): badges.append("<span class='badge-c-fake'>⚠️【偽C馬注意】Fup3以下(頭危険)</span>")

    if row.get('is_f1_accel'): badges.append("<span class='badge-f1-rap'>⚡【最高勝率】F1位×調教加速(勝45%)</span>")
    if row.get('is_s_top_accel'): badges.append("<span class='badge-s-accel'>👑【最高安定軸】S1-3×加速(複51.5%)</span>")
    if row.get('waku_gold'): badges.append("<span class='badge-waku-gold'>👑 同枠×F1-2位 (複53.3%)</span>")
    if row.get('is_mile_wood_big_accel'): badges.append("<span class='badge-target-win'>🚀 マイル×W大加速+1.0s超(複44%)</span>")
    if row.get('is_dirt_wood_trap'): badges.append("<span class='badge-wood-danger'>⚠️ ダート×W追い切り(頭消し)</span>")
    if row.get('is_valley_trap'): badges.append("<span class='badge-c-fake'>⚠️【谷の形】地雷人気馬(頭消し)</span>")
    if row.get('is_short_back_trap'): badges.append("<span class='badge-c-fake'>⚠️ 短距離×後方脚質(頭消し)</span>")

    if row.get('is_arms_fup_super'): badges.append("<span class='badge-arms-fup'>👑 ARMS×Fup黄金軸</span>")
    if row.get('is_dirt_eat_super'): badges.append("<span class='badge-dirt-eat'>🏜️ ダートで食う勝戻馬</span>")
    if row.get('is_sss_level'): badges.append("<span class='badge-synergy' style='background:#f59e0b;color:#000;'>👑 SSS級・絶対神域</span>")
    if row.get('is_iron_f72'): badges.append("<span class='badge-synergy' style='background:#e11d48;color:#fff;'>⚡ F>72鉄板級 (勝率52%)</span>")
    if row.get('is_fup_axis'): badges.append("<span class='badge-synergy' style='background:#b45309;color:#fff;'>👑 Fup最上位評価 (軸)</span>")
    if row.get('is_value_arms120'): badges.append("<span class='badge-synergy' style='background:#0284c7;color:#fff;'>🚀 arms>120 期待値</span>")
    if row.get('is_dirt_tua190') and not row.get('is_dirt_eat_super'): badges.append("<span class='badge-synergy' style='background:#059669;color:#fff;'>🛡️ ダート×tua堅実</span>")
    if row.get('is_four_crown'): badges.append("<span class='badge-synergy' style='background:#10b981;color:#fff;'>👑 指数の四冠馬</span>")
    if row.get('is_fup_trap'): badges.append("<span class='badge-danger-jockey'>⚠️ Fup1の罠(ダミー消去)</span>")
    if row.get('is_fup_kakugen'): badges.append("<span class='badge-fup6-sf'>✨ Fup7確変馬</span>")

    if row.get('tr_badge'): badges.append(row['tr_badge'])
    if row.get('cushion_horse_badge'): badges.append(row['cushion_horse_badge'])
    if row.get('is_danger_jockey'): badges.append("<span class='badge-danger-jockey-subtle'>騎手注意</span>")
    if row.get('course_training_badge'): badges.append(row['course_training_badge'])

    if row.get('flag_fup6_s6'): badges.append("<span class='badge-fup6-sf'>🔥 Fup6+×S6 (勝率25%/回収200%)</span>")
    elif row.get('flag_fup6_f6'): badges.append("<span class='badge-fup6-sf'>🔥 Fup6+×F6 (勝率25%)</span>")

    if row.get('target_win'): badges.append("<span class='badge-target-win'>🥇 1着狙い (単勝厳選)</span>")
    elif row.get('target_axis'): badges.append("<span class='badge-target-axis'>🛡️ 軸・連対狙い (複勝率55%超)</span>")
    if row.get('is_syn_iron'): badges.append("<span class='badge-synergy badge-iron'>💎 鉄板軸馬 (複勝61.9%)</span>")
    elif row.get('is_syn_high'): badges.append("<span class='badge-synergy badge-high'>🔥 高確率軸 (複勝55%超)</span>")
    if row.get('is_syn_fup_sakaro'): badges.append("<span class='badge-synergy badge-sakaro-fup'>✨ Fup坂路完全</span>")
    if row.get('is_syn_f1_rap') and not row.get('is_f1_accel'): badges.append("<span class='badge-synergy badge-f1-rap'>🔥 SSS級・F1位×究極ラップ</span>")

    if row.get('syn_jk_ub_wood'): badges.append("<span class='badge-jk-ub'>👑 騎手同馬番×W加速×F上位</span>")
    elif row.get('is_same_ub_jk'): badges.append(f"<span class='badge-jk-ub'>🏇 騎手同馬番{row['same_ub_jk_count']}回目 ({row['same_ub_jk_races']})</span>")

    if row.get('syn_tr_ub_arms'): badges.append("<span class='badge-tr-ub'>🚀 厩舎同馬番×arms上位 (複勝70%)</span>")
    elif row.get('is_same_ub_tr'): badges.append(f"<span class='badge-tr-ub'>🏛️ 厩舎同馬番{row['same_ub_tr_count']}回目 ({row['same_ub_tr_races']})</span>")

    if row.get('syn_same_ub_fs6'): badges.append("<span class='badge-same-ub-fs6'>👑 同馬番×FS6 (複勝42%)</span>")
    elif row.get('syn_same_ub_f6'): badges.append("<span class='badge-same-ub-f6'>🎯 同馬番×F6 (複勝38%)</span>")
    elif row.get('syn_same_ub_s6'): badges.append("<span class='badge-same-ub-s6'>⚡ 同馬番×S6 (先行連対)</span>")

    if row.get('flag_sf7_himo'): badges.append("<span class='badge-sf7-himo'>🌪️ SF7×加速/同枠</span>")
    if row.get('is_syn_bomb') or row.get('syn_jk_ub_bomb'): badges.append("<span class='badge-synergy badge-bomb'>💣 爆弾穴馬</span>")
    if row.get('cushion_badge'): badges.append(row['cushion_badge'])

    u_no = int(row['馬番']) if pd.notnull(row['馬番']) else 99
    pop_str = f"{int(row['人気'])}人気" if pd.notnull(row['人気']) else '-人気'
    waku_str = f"{int(row['枠番'])}枠" if pd.notnull(row['枠番']) else '-枠'
    sire_display = row.get('種牡馬') if row.get('種牡馬') else '-'
    mark_val = str(row.get('印', '')).strip()
    mark_html = f"<span class='badge-mark-gtv'>印: {mark_val}</span>" if mark_val and mark_val != 'nan' else ""

    # 買い目印（◎、◯、▲、△、★）の取得＆ヘッダー表示
    bet_mark_html = bet_marks_dict.get(u_no, "")

    style_display = str(row.get('脚質', '')).strip()
    style_text = style_display if (style_display and style_display != 'nan') else '先行'

    tr_name_raw = str(row.get('調教師', ''))
    if any(x in tr_name_raw for x in PREV_HAN_SOLID_TRAINERS):
        tr_display_html = f"<span class='tr-name-super'>{tr_name_raw}</span> (前日王道)"
    elif any(x in tr_name_raw for x in PREV_HAN_BOMB_TRAINERS):
        tr_display_html = f"<span class='tr-name-bomb'>{tr_name_raw}</span> (前日穴王)"
    elif any(x in tr_name_raw for x in PREV_WOOD_DIRT_TRAINERS):
        tr_display_html = f"<span class='tr-name-wood'>{tr_name_raw}</span> (前日Wダート)"
    else:
        tr_display_html = tr_name_raw

    f_badge = "<span class='rank-1st'>🥇1位</span>" if row['F_rank'] == 1 else f"{int(row['F_rank'])}位"
    s_badge = "<span class='rank-1st'>🥇1位</span>" if row['S_rank'] == 1 else f"{int(row['S_rank'])}位"
    arms_badge = "<span class='rank-1st'>🥇1位</span>" if row['arms_rank'] == 1 else f"{int(row['arms_rank'])}位"
    tua_badge = "<span class='rank-1st'>🥇1位</span>" if row['tua_rank'] == 1 else f"{int(row['tua_rank'])}位"
    fup_badge = "<span class='rank-1st'>🥇1位</span>" if row['Fup_rank'] == 1 else f"{int(row['Fup_rank'])}位"

    f_val_num = float(row.get('F指数', 0.0))
    if f_val_num >= 72.0: f_val_html = f"<span class='val-f-super'>{f_val_num:.0f}</span>"
    elif f_val_num >= 66.0: f_val_html = f"<span class='val-f-high'>{f_val_num:.0f}</span>"
    elif f_val_num >= 50.0: f_val_html = f'<strong>{f_val_num:.0f}</strong>'
    else: f_val_html = f'{f_val_num:.0f}'

    s_val_num = float(row.get('S指数', 0.0))
    s_val_html = f"<span class='val-s-super'>{s_val_num:.0f}</span>" if s_val_num >= 30.0 else f'{s_val_num:.0f}'

    arms_val_num = float(row.get('arms', 0.0))
    if arms_val_num >= 120.0: arms_val_html = f"<span class='val-arms-super'>{arms_val_num:.0f}</span>"
    elif arms_val_num >= 100.0: arms_val_html = f'<strong>{arms_val_num:.0f}</strong>'
    else: arms_val_html = f'{arms_val_num:.0f}'

    tua_val_num = float(row.get('tua', 0.0))
    tua_val_html = f"<span class='val-tua-super'>{tua_val_num:.0f}</span>" if tua_val_num >= 190.0 else f'{tua_val_num:.0f}'

    fup_val_num = int(row.get('Fup', 0))
    if fup_val_num >= 5: fup_val_html = f"<span class='val-f-super'>{fup_val_num}点</span>"
    elif fup_val_num == 4: fup_val_html = f"<strong style='color:#f97316;'>{fup_val_num}点</strong>"
    else: fup_val_html = f'{fup_val_num}点'

    if pd.notnull(row.get('wood_1F')):
        w_5f_txt = f"{row['wood_5F']:.1f}s " if pd.notnull(row.get('wood_5F')) else ''
        w_acc_badge = f"<span class='badge-accel-on'>加速 +{row['wood_accel']:.1f}s</span>" if row.get('is_wood_accel') else (f"<span class='badge-accel-off'>減速 {row['wood_accel']:.1f}s</span>" if pd.notnull(row.get('wood_accel')) else '')
        w_str = f"W: {w_5f_txt}1F {row['wood_1F']:.1f}s {w_acc_badge}".strip()
    else:
        w_str = 'W: 計測無'

    if pd.notnull(row.get('坂路_4F')):
        s_acc_badge = "<span class='badge-accel-on'>実質完全加速</span>" if row.get('坂路_完全加速') else "<span class='badge-accel-off'>非完全加速</span>"
        s_str = f"坂路: 4F {row['坂路_4F']:.1f}s (1F {row['坂路_1F']:.1f}s) {s_acc_badge}"
    else:
        s_str = '坂路: 計測無'

    prev_h_txt = f" | <strong>前日坂路: {row.get('前日坂路時計'):.1f}s</strong>" if row.get('has_prev_han') and row.get('前日坂路時計') < 900 else ""

    tr_note = row.get('厩舎狙い目フラグ', '')
    tr_li = f"<li><strong>厩舎調教特注</strong>: <span style='color:#67e8f9;'>{tr_note}</span></li>" if tr_note else ""

    h_clean = clean_horse_name(row['馬名'])
    c_hist = cushion_history_data.get(h_clean, {})
    bins_order = ['7以下', '8台', '9台', '10台', '11以上']
    c_parts = []
    for b_key in bins_order:
        val = c_hist.get(b_key, '[0-0-0/0]')
        if b_key == current_bin_name:
            c_parts.append(f"<strong style='color:#facc15;text-decoration:underline;'>{b_key}:{val}</strong>")
        else:
            c_parts.append(f"{b_key}:{val}")
    cushion_stat_str = " | ".join(c_parts)
    cushion_li = f"<li><strong>クッション値別成績(芝)</strong>: <span style='font-size:12.5px;'>{cushion_stat_str}</span></li>"

    race_info_badge = f"<span class='race-badge-title'>{row.get('競馬場名', '')}{row.get('R番号', '')}R ({row.get('track', '')}{row.get('dist', '')}m)</span>"

    st.markdown(
        f"<div class='horse-card'>"
        f"<div class='horse-card-header'>{race_info_badge}{bet_mark_html}<span class='horse-card-title'>{u_no}番 ({waku_str}) {row['馬名']} ({pop_str}) {mark_html}</span> {' '.join(badges)}</div>"
        "<ul class='horse-card-list'>"
        f"<li><strong>騎手/厩舎</strong>: {row.get('騎手')} / {tr_display_html} / <strong>父: {sire_display}</strong> | <strong>脚質: <span style='color:#60a5fa;font-weight:bold;'>{style_text}</span></strong></li>"
        f"<li><strong>調教ラップ</strong>: <strong>{w_str}</strong> | <strong>{s_str}</strong>{prev_h_txt}</li>"
        f"{tr_li}"
        f"<li><strong>能力指数</strong>: F: {f_val_html} ({f_badge}) | S: {s_val_html} ({s_badge}) | ARMS: {arms_val_html} ({arms_badge}) | TUA: {tua_val_html} ({tua_badge}) | Fup: {fup_val_html} ({fup_badge})</li>"
        f"{cushion_li}"
        '</ul></div>',
        unsafe_allow_html=True,
    )
