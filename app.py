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
# 【最新完全統合アップグレード版】
# 修正①:2着連軸マルチ・馬単表裏標準化 / 修正②:短距離マイル終い調教フィルター
# 修正③:爆弾穴馬脚質枠番2次選別 / 修正④:F72超クッション値危険ブレーキ連動
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
</style>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# ★ 基本定数・危険騎手リスト & 前日坂路・ウッド特注厩舎リスト（森秀行連動）
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
# ★ データ読み込み＆結合エンジン（前日坂路日付自動検知＆森秀行厩舎調教完全連動）
# ==============================================================================
def load_and_merge_all(f_index, f_sakaro, f_wood):
    index_patterns = [
        'data/出馬表_指数*.csv', '出馬表_指数*.csv', 'data/*指数*.csv', '*指数*.csv',
        'data/出馬表*.csv', '出馬表*.csv'
    ]
    index_src = f_index
    if index_src is None:
        matched = []
        for pat in index_patterns:
            matched.extend(glob.glob(pat))
        if matched:
            index_src = max(matched, key=os.path.getmtime)

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

        fw_map = {
            '１': 1, '２': 2, '３': 3, '４': 4, '５': 5, '６': 6, '７': 7, '８': 8, '９': 9,
            '10': 10, '11': 11, '12': 12, '13': 13, '14': 14, '15': 15, '16': 16, '17': 17, '18': 18,
        }

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
                fin_int = fw_map.get(str(finish), int(finish) if str(finish).isdigit() else np.nan)
                pop_int = int(pop) if str(pop).isdigit() else np.nan
                u_int = int(umaban) if str(umaban).isdigit() else 99

                records.append({
                    'race_id': race_id, 'track': track, 'dist': dist, '馬番': u_int, '馬名': horse,
                    'C馬': c_marker,
                    '印': str(mark).strip(), '調教師': clean_horse_name(trainer), '騎手': clean_horse_name(jockey),
                    '種牡馬': str(sire).strip(), '人気': pop_int, '着順': fin_int,
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

    sakaro_patterns = ['data/出馬表_坂路*.csv', '出馬表_坂路*.csv', 'data/*坂路*.csv', '*坂路*.csv']
    df_s_raw = read_csv_robust(f_sakaro, sakaro_patterns)
    if not df_s_raw.empty:
        c_s_name = find_col_regex(df_s_raw, ['^馬名$', '^競走馬名$']) or (
            df_s_raw.columns[4] if len(df_s_raw.columns) > 4 else df_s_raw.columns[1]
        )
        df_s_raw['clean_name'] = df_s_raw[c_s_name].apply(clean_horse_name)

        c_s_date = find_col_regex(df_s_raw, ['^年月日$', '^日付$', '^date$']) or (
            df_s_raw.columns[1] if len(df_s_raw.columns) > 1 else None
        )
        if c_s_date:
            df_s_raw['clean_date'] = pd.to_numeric(df_s_raw[c_s_date].astype(str).str.extract(r'(\d+)')[0], errors='coerce')
        else:
            df_s_raw['clean_date'] = np.nan

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
        c_align = find_col_regex(df_s_raw, ['^併せ', '^追切併せ'])

        if c_sun_sat_h: df_s_raw['土日坂路最速'] = pd.to_numeric(df_s_raw[c_sun_sat_h], errors='coerce')
        if c_align: df_s_raw['併せ結果'] = df_s_raw[c_align].astype(str)

        prev_target_date = int((detected_date - datetime.timedelta(days=1)).strftime('%Y%m%d'))
        df_s_prev_day = df_s_raw[df_s_raw['clean_date'] == prev_target_date].copy()
        
        if df_s_prev_day.empty and df_s_raw['clean_date'].notna().any():
            max_d = df_s_raw['clean_date'].max()
            if max_d >= prev_target_date - 1:
                df_s_prev_day = df_s_raw[df_s_raw['clean_date'] == max_d].copy()

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
        
        df_s_best['坂路_森加速'] = (
            (df_s_best['坂路_Lap4'] > df_s_best['坂路_Lap3'])
            & (df_s_best['坂路_Lap3'] > df_s_best['坂路_Lap2'])
            & (df_s_best['坂路_Lap2'] > df_s_best['坂路_Lap1'])
        )

        merge_cols = ['clean_name', '坂路_4F', '坂路_1F', '坂路_完全加速', '坂路_穴トリガー', '坂路_ラップ型', '坂路_森加速']
        for extra in ['土日坂路最速', '併せ結果']:
            if extra in df_s_best.columns: merge_cols.append(extra)

        df_main = pd.merge(df_main, df_s_best[merge_cols], left_on='馬名', right_on='clean_name', how='left')
        
        if not df_prev_merged.empty:
            df_main = pd.merge(df_main, df_prev_merged, left_on='馬名', right_on='clean_name', how='left')

    if '坂路_4F' not in df_main.columns:
        df_main['坂路_4F'] = np.nan; df_main['坂路_1F'] = np.nan
        df_main['坂路_完全加速'] = False; df_main['坂路_穴トリガー'] = False; df_main['坂路_ラップ型'] = ''; df_main['坂路_森加速'] = False

    if '前日坂路時計' not in df_main.columns: df_main['前日坂路時計'] = np.nan
    if '前日坂路あり' not in df_main.columns: df_main['前日坂路あり'] = False
    df_main['前日坂路あり'] = df_main['前日坂路あり'].fillna(False).astype(bool)

    wood_patterns = ['data/出馬表_ウッド*.csv', '出馬表_ウッド*.csv', 'data/*ウッド*.csv', '*ウッド*.csv']
    df_w_raw = read_csv_robust(f_wood, wood_patterns)
    if not df_w_raw.empty:
        c_w_name = find_col_regex(df_w_raw, ['^馬名$', '^競走馬名$']) or (
            df_w_raw.columns[4] if len(df_w_raw.columns) > 4 else df_w_raw.columns[1]
        )
        df_w_raw['clean_name'] = df_w_raw[c_w_name].apply(clean_horse_name)

        c_w_5f = find_col_regex(df_w_raw, ['^5f$', '^５ｆ$', '^5Ｆ$']) or df_w_raw.columns[13]
        c_w_4f = find_col_regex(df_w_raw, ['^4f$', '^４ｆ$', '^4Ｆ$'])
        c_w_1f = find_col_regex(df_w_raw, ['^1f$', '^１ｆ$', '^1Ｆ$']) or df_w_raw.columns[23]
        c_w_l2 = find_col_regex(df_w_raw, ['^lap2$', '^ｌａｐ２$']) or df_w_raw.columns[22]
        c_w_l1 = find_col_regex(df_w_raw, ['^lap1$', '^ｌａｐ１$']) or df_w_raw.columns[23]

        df_w_raw['wood_5F'] = pd.to_numeric(df_w_raw[c_w_5f], errors='coerce')
        if c_w_4f: df_w_raw['wood_4F'] = pd.to_numeric(df_w_raw[c_w_4f], errors='coerce')
        df_w_raw['wood_1F'] = pd.to_numeric(df_w_raw[c_w_1f], errors='coerce')
        df_w_raw['wood_Lap2'] = pd.to_numeric(df_w_raw[c_w_l2], errors='coerce')
        df_w_raw['wood_Lap1'] = pd.to_numeric(df_w_raw[c_w_l1], errors='coerce')

        c_sun_sat_w = find_col_regex(df_w_raw, ['^土日ウッド', '^週末ウッド'])
        c_prev_w = find_col_regex(df_w_raw, ['^前日ウッド'])

        if c_sun_sat_w: df_w_raw['土日ウッド最速'] = pd.to_numeric(df_w_raw[c_sun_sat_w], errors='coerce')
        if c_prev_w: df_w_raw['前日ウッドあり'] = True
        else: df_w_raw['前日ウッドあり'] = False

        df_w_best = df_w_raw.dropna(subset=['wood_1F']).sort_values('wood_1F').drop_duplicates('clean_name', keep='first').copy()
        df_w_best['wood_accel'] = df_w_best['wood_Lap2'] - df_w_best['wood_Lap1']
        df_w_best['is_wood_accel'] = (df_w_best['wood_accel'] > 0) & (df_w_best['wood_accel'].notna())

        w_merge_cols = ['clean_name', 'wood_5F', 'wood_1F', 'wood_accel', 'is_wood_accel']
        for extra in ['wood_4F', '土日ウッド最速', '前日ウッドあり']:
            if extra in df_w_best.columns: w_merge_cols.append(extra)

        df_main = pd.merge(df_main, df_w_best[w_merge_cols], left_on='馬名', right_on='clean_name', how='left')

    if 'wood_1F' not in df_main.columns:
        df_main['wood_5F'] = np.nan; df_main['wood_1F'] = np.nan
        df_main['wood_accel'] = np.nan; df_main['is_wood_accel'] = False

    df_main['坂路_完全加速'] = df_main['坂路_完全加速'].fillna(False).astype(bool)
    df_main['坂路_穴トリガー'] = df_main['坂路_穴トリガー'].fillna(False).astype(bool)
    df_main['坂路_森加速'] = df_main.get('坂路_森加速', pd.Series(False, index=df_main.index)).fillna(False).astype(bool)
    df_main['is_wood_accel'] = df_main['is_wood_accel'].fillna(False).astype(bool)

    def infer_course(r):
        if pd.notnull(r.get('坂路_4F')) and pd.isnull(r.get('wood_1F')): return '坂路'
        elif pd.notnull(r.get('wood_1F')) and pd.isnull(r.get('坂路_4F')): return 'ウッド'
        elif pd.notnull(r.get('坂路_4F')) and pd.notnull(r.get('wood_1F')):
            return 'ウッド' if r.get('wood_5F', 99) <= 70.0 else '坂路'
        return '坂路'

    if '追切コース' not in df_main.columns: df_main['追切コース'] = df_main.apply(infer_course, axis=1)
    if '追切ラップ型' not in df_main.columns: df_main['追切ラップ型'] = df_main.get('坂路_ラップ型', '')

    for c_need in ['土日坂路最速', '土日ウッド最速', '土日ウッド最速4F']:
        if c_need not in df_main.columns: df_main[c_need] = 999.0
    for c_bool in ['前日ウッドあり']:
        if c_bool not in df_main.columns: df_main[c_bool] = False
    for c_str in ['土日坂路ラップ型', '併せ結果', 'クラス', '前走追切コース', '馬主', '性別', '性', 'C馬', '脚質']:
        if c_str not in df_main.columns: df_main[c_str] = ''

    jk_ub_grp = df_main.groupby(['騎手', '馬番'])['race_id'].apply(list).to_dict()
    df_main['same_ub_jk_count'] = df_main.apply(lambda r: len(jk_ub_grp.get((r['騎手'], r['馬番']), [])), axis=1)
    df_main['same_ub_jk_races'] = df_main.apply(lambda r: ', '.join(jk_ub_grp.get((r['騎手'], r['馬番']), [])), axis=1)
    df_main['is_same_ub_jk'] = df_main['same_ub_jk_count'] >= 2

    tr_ub_grp = df_main.groupby(['調教師', '馬番'])['race_id'].apply(list).to_dict()
    df_main['same_ub_tr_count'] = df_main.apply(lambda r: len(tr_ub_grp.get((r['調教師'], r['馬番']), [])), axis=1)
    df_main['same_ub_tr_races'] = df_main.apply(lambda r: ', '.join(tr_ub_grp.get((r['調教師'], r['馬番']), [])), axis=1)
    df_main['is_same_ub_tr'] = df_main['same_ub_tr_count'] >= 2

    df_main['is_same_ub_any'] = df_main['is_same_ub_jk'] | df_main['is_same_ub_tr']
    jk_waku_grp = df_main.groupby(['競馬場名', '騎手', '枠番'])['race_id'].transform('count') >= 2
    tr_waku_grp = df_main.groupby(['競馬場名', '調教師', '枠番'])['race_id'].transform('count') >= 2
    df_main['is_same_waku'] = jk_waku_grp | tr_waku_grp

    return df_main, detected_date

# ==============================================================================
# ★ 各種判定エンジン群（森秀行厩舎坂路加速判定統合）
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
    
    # コース×種牡馬 データブック最強マトリクス 上位20[cite: 94, 166]
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

    # RISK LIST 危険・割引対象 上位20[cite: 95, 167]
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
# ★ サイドバー: データ読み込み
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

# ==============================================================================
# ★ 全ファクター統合・判定マトリクス（修正案①〜④完全統合）
# ==============================================================================
df['調教加速'] = df['坂路_完全加速'] | df['is_wood_accel']
df[['course_training_badge', 'is_course_training_fit']] = df.apply(evaluate_course_training, axis=1)
df[['調教ステータス', '厩舎狙い目フラグ', 'tr_badge_html']] = df.apply(check_trainer_patterns, axis=1)

df['is_c_horse'] = df['C馬'].astype(str).str.contains('C', na=False)
df['is_c_real_gold'] = df['is_c_horse'] & (df['Fup'] >= 4)
df['is_c_fake_trap'] = df['is_c_horse'] & (df['Fup'] <= 3)

df['dist_num'] = pd.to_numeric(df['dist'], errors='coerce').fillna(1600)

df['has_prev_han'] = df['前日坂路あり'].fillna(False).astype(bool)
df['has_prev_han_fast'] = df['has_prev_han'] & (df['前日坂路時計'] <= 65.9)
df['is_prev_han_solid'] = df['has_prev_han_fast'] & df['調教師'].apply(lambda t: any(x in str(t) for x in PREV_HAN_SOLID_TRAINERS)) & (df['人気'] <= 3)
df['is_prev_han_bomb'] = df['has_prev_han_fast'] & df['調教師'].apply(lambda t: any(x in str(t) for x in PREV_HAN_BOMB_TRAINERS)) & (df['人気'] >= 6)
df['is_prev_wood_dirt'] = df['前日ウッドあり'].fillna(False).astype(bool) & df['track'].str.contains('ダ', na=False) & df['調教師'].apply(lambda t: any(x in str(t) for x in PREV_WOOD_DIRT_TRAINERS))

# 脚質フラグ定義
df['is_style_senko'] = df['脚質'].str.contains('先', na=False)
df['is_style_sashi'] = df['脚質'].str.contains('差', na=False)
df['is_style_nige'] = df['脚質'].str.contains('逃', na=False)
df['is_style_oikomi'] = df['脚質'].str.contains('追', na=False)
df['is_style_front'] = df['is_style_senko'] | df['is_style_nige']
df['is_style_back'] = df['脚質'].str.contains('後|中', na=False)

# ★ 修正案②：短距離・マイルでの終い調教絶対値フィルター判定
# 坂路1F 12.2秒以下 または ウッド1F 11.4秒以下
df['has_sharp_finishing'] = (
    (df['坂路_1F'].fillna(99.0) <= 12.2)
    | (df['wood_1F'].fillna(99.0) <= 11.4)
)

df['is_s_top_accel'] = (df['S_rank'] <= 3) & df['調教加速']
df['is_f1_accel'] = (df['F_rank'] == 1) & df['調教加速']
df['is_dirt_wood_trap'] = df['track'].str.contains('ダ', na=False) & df['is_wood_accel'] & (~df['坂路_完全加速']) & (~df['is_prev_wood_dirt'])
df['is_mile_wood_big_accel'] = (df['track'].str.contains('芝', na=False)) & (df['dist_num'].between(1500, 1800)) & (df['wood_accel'] >= 1.0)
df['is_kyoto_sakaro_full'] = (df['競馬場名'] == '京都') & df['坂路_完全加速']
df['is_short_sakaro_full'] = (df['dist_num'] <= 1400) & df['坂路_完全加速']

df['is_arms_fup_super'] = (df['arms_rank'] <= 3) & (df['Fup'] >= 5) & (df['F_rank'] == 1)
df['is_arms_fup_solid'] = (df['arms_rank'] <= 3) & (df['Fup'] >= 4)
df['is_sss_level'] = ((df['F指数'] >= 70) & (df['arms'] >= 120) & (df['tua'] >= 200))
df['is_iron_f72'] = df['F指数'] >= 72.0
df['is_value_arms120'] = df['arms'] >= 120.0
df['is_dirt_eat_super'] = (df['track'].str.contains('ダ')) & (df['tua'] >= 190.0) & (df['tua_rank'] <= 3) & (df['S_rank'] <= 3)
df['is_dirt_tua190'] = (df['track'].str.contains('ダ')) & (df['tua'] >= 190.0) & (df['tua_rank'] <= 3)

df['is_four_crown'] = ((df['F_rank'] <= 2) & (df['Fup_rank'] <= 2) & (df['arms_rank'] <= 2) & (df['tua_rank'] <= 2))
df['is_fup_trap'] = ((df['Fup'] == 1) & (df['人気'] <= 3) & (df['F指数'] <= 72) & (~df['is_sss_level']))
df['is_fup_kakugen'] = df['Fup'] == 7
df['is_valley_trap'] = (df['人気'] <= 3) & (df['F_rank'] >= 4) & (~df['is_sss_level']) & (df['F指数'] <= 70)
df['is_short_back_trap'] = (df['dist_num'] <= 1400) & df['is_style_back'] & (df['人気'] <= 3) & (~df['is_sss_level'])

df['flag_fup6_s6'] = ((df['Fup'] >= 6) & (df['Fup_rank'] == 1) & (df['S_rank'] <= 6))
df['flag_fup6_f6'] = ((df['Fup'] >= 6) & (df['Fup_rank'] == 1) & (df['F_rank'] <= 6))
df['flag_fup6_sf_any'] = df['flag_fup6_s6'] | df['flag_fup6_f6']

df['is_syn_iron'] = ((df['F_rank'] == 1) & (df['arms_rank'] <= 3) & (df['wood_1F'] <= 11.5) & df['is_wood_accel'])
df['is_syn_high'] = (((df['F_rank'] == 1) | (df['F指数'] >= 66)) & (df['wood_1F'] <= 11.5) & df['is_wood_accel'])
df['is_syn_fup_sakaro'] = (df['Fup'] >= 5) & df['坂路_完全加速']

# ★ 修正案③：爆弾穴馬の選定を「前走先行・差し」かつ「1〜6枠」で2次選別（点数半減・精度向上）
df['is_syn_bomb'] = (
    (df['人気'] >= 6)
    & (df['Fup'] >= 4)
    & (df['調教加速'] | df['is_prev_han_bomb'])
    & (df['is_style_senko'] | df['is_style_sashi'])
    & (df['枠番'] <= 6)
)
df['is_syn_f1_rap'] = (df['F_rank'] == 1) & (((df['坂路_1F'] <= 12.4) & df['坂路_完全加速']) | ((df['wood_1F'] <= 11.5) & df['is_wood_accel']))

df['syn_jk_ub_wood'] = (df['is_same_ub_jk'] & df['is_wood_accel'] & (df['F_rank'] <= 3))
df['syn_jk_ub_bomb'] = (df['is_same_ub_jk'] & df['調教加速'] & (df['Fup'] >= 4) & (df['人気'] >= 6))
df['syn_tr_ub_arms'] = df['is_same_ub_tr'] & (df['arms_rank'] <= 3)

df['syn_same_ub_f6'] = df['is_same_ub_any'] & (df['F_rank'] <= 6)
df['syn_same_ub_s6'] = df['is_same_ub_any'] & (df['S_rank'] <= 6)
df['syn_same_ub_fs6'] = df['syn_same_ub_f6'] & df['syn_same_ub_s6']

df['waku_gold'] = df['is_same_waku'] & (df['F_rank'] <= 2)
df['flag_sf7_himo'] = ((df['S_rank'] <= 7) | (df['F_rank'] <= 7)) & (df['調教加速'] | df['is_same_waku'] | df['is_same_ub_any'] | df['has_prev_han'])

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

# ★ 修正案②＆④：1着狙い（単勝厳選）判定の強化
# 終い調教絶対値フィルター ＆ クッション値危険ブレーキ連動
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

# 軸・連対狙い判定（前走先行・差しを連軸の絶対条件化）
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

# 紐穴判定
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
