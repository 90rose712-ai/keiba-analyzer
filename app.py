import datetime
import glob
import itertools
import os
import re
import numpy as np
import pandas as pd
import streamlit as st

# ==============================================================================
# 競馬予想10 クッション値Vr 完全統合Webアプリケーション
# TARGET Frontier JV / 指数マトリクス / 調教完全加速 / クッション値×種牡馬完全統合版
# ==============================================================================

# --- ページ基本設定 ---
st.set_page_config(
    page_title="競馬予想10 クッション値Vr - 完全統合システム",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CSSスタイル設定 ---
st.markdown(
    """
<style>
    .metric-container {
        display: flex;
        justify-content: space-around;
        background-color: #161b22;
        padding: 14px;
        border-radius: 10px;
        margin-bottom: 18px;
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
        font-size: 26px;
        font-weight: bold;
        color: #f0f6fc;
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
        margin-bottom: 14px;
        font-size: 15px;
        font-weight: bold;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .race-type-solid {
        background: linear-gradient(135deg, #064e3b 0%, #047857 100%);
        color: #ecfdf5;
        border: 1px solid #34d399;
    }
    .race-type-twin-axis {
        background: linear-gradient(135deg, #1e3a8a 0%, #1d4ed8 100%);
        color: #eff6ff;
        border: 1px solid #60a5fa;
    }
    .race-type-chaos {
        background: linear-gradient(135deg, #881337 0%, #be123c 100%);
        color: #fff1f2;
        border: 1px solid #fb7185;
    }

    .badge-decision-go {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: #ffffff;
        font-size: 13px;
        padding: 3px 10px;
        border-radius: 6px;
        font-weight: bold;
        margin-left: 8px;
    }
    .badge-decision-skip {
        background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
        color: #f1f5f9;
        font-size: 13px;
        padding: 3px 10px;
        border-radius: 6px;
        font-weight: bold;
        margin-left: 8px;
    }

    .recom-panel-go {
        background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
        border: 2px solid #10b981;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 20px;
    }
    .recom-panel-chaos {
        background: linear-gradient(135deg, #1e111a 0%, #2e1020 100%);
        border: 2px solid #fb7185;
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
    .recom-title-chaos {
        font-size: 16px;
        font-weight: bold;
        color: #fb7185;
        margin-bottom: 12px;
        border-bottom: 1px solid #4c1d2e;
        padding-bottom: 5px;
    }
    .recom-block {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 10px;
    }
    .recom-label {
        font-weight: bold;
        color: #fbbf24;
        display: inline-block;
        font-size: 14px;
    }
    .recom-val-num {
        color: #ffffff;
        font-weight: bold;
        font-size: 15.5px;
        letter-spacing: 1px;
    }
    .recom-pts {
        display: inline-block;
        background-color: #064e3b;
        color: #a7f3d0;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
        margin-left: 8px;
    }
    .recom-pts-chaos {
        display: inline-block;
        background-color: #881337;
        color: #fecdd3;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
        margin-left: 8px;
    }
    
    .horse-card {
        background-color: #161e2e;
        border-left: 5px solid #238636;
        padding: 14px 18px;
        border-radius: 8px;
        margin-bottom: 14px;
        border-top: 1px solid #30363d;
        border-right: 1px solid #30363d;
        border-bottom: 1px solid #30363d;
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

    .badge-accel-on {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        color: #ffffff;
        font-weight: bold;
        font-size: 11.5px;
        padding: 2px 7px;
        border-radius: 4px;
        border: 1px solid #34d399;
    }
    .badge-accel-off {
        background-color: #374151;
        color: #9ca3af;
        font-size: 11.5px;
        padding: 2px 7px;
        border-radius: 4px;
        border: 1px solid #4b5563;
    }

    .val-f-super {
        color: #1a1000;
        background-color: #fcd34d;
        font-weight: bold;
        padding: 1px 6px;
        border-radius: 4px;
        border: 1px solid #f59e0b;
    }
    .val-f-high {
        color: #ffffff;
        background-color: #ea580c;
        font-weight: bold;
        padding: 1px 6px;
        border-radius: 4px;
        border: 1px solid #fb923c;
    }
    .val-arms-super {
        color: #083344;
        background-color: #38bdf8;
        font-weight: bold;
        padding: 1px 6px;
        border-radius: 4px;
        border: 1px solid #0284c7;
    }
    .val-tua-super {
        color: #022c22;
        background-color: #34d399;
        font-weight: bold;
        padding: 1px 6px;
        border-radius: 4px;
        border: 1px solid #059669;
    }
    .val-s-super {
        color: #ffffff;
        background-color: #8b5cf6;
        font-weight: bold;
        padding: 1px 6px;
        border-radius: 4px;
        border: 1px solid #c4b5fd;
    }

    .badge-jk-ub {
        background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
        color: #ffffff;
        font-weight: bold;
        font-size: 11.5px;
        padding: 2px 8px;
        border-radius: 6px;
        border: 1px solid #fcd34d;
    }
    .badge-tr-ub {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        color: #ffffff;
        font-weight: bold;
        font-size: 11.5px;
        padding: 2px 8px;
        border-radius: 6px;
        border: 1px solid #6ee7b7;
    }
    .badge-same-ub-f6 {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        color: #ffffff;
        font-weight: bold;
        font-size: 11.5px;
        padding: 2px 8px;
        border-radius: 6px;
        border: 1px solid #7dd3fc;
    }
    .badge-same-ub-s6 {
        background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%);
        color: #ffffff;
        font-weight: bold;
        font-size: 11.5px;
        padding: 2px 8px;
        border-radius: 6px;
        border: 1px solid #c4b5fd;
    }
    .badge-same-ub-fs6 {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: #ffffff;
        font-weight: bold;
        font-size: 11.5px;
        padding: 2px 8px;
        border-radius: 6px;
        border: 1px solid #fde68a;
    }
    .badge-fup6-sf {
        background: linear-gradient(135deg, #ff0844 0%, #ffb199 100%);
        color: #ffffff;
        font-weight: bold;
        font-size: 11.5px;
        padding: 2px 8px;
        border-radius: 6px;
        border: 1px solid #ffe4e6;
        box-shadow: 0 1px 4px rgba(255, 8, 68, 0.4);
    }
    .badge-sf7-himo {
        background: linear-gradient(135deg, #0ea5e9 0%, #0369a1 100%);
        color: #ffffff;
        font-weight: bold;
        font-size: 11.5px;
        padding: 2px 8px;
        border-radius: 6px;
        border: 1px solid #7dd3fc;
        box-shadow: 0 1px 3px rgba(0,0,0,0.3);
    }

    .badge-cushion-fit {
        display: inline-flex;
        align-items: center;
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        color: #ffffff;
        font-weight: bold;
        font-size: 11.5px;
        padding: 2px 8px;
        border-radius: 6px;
        border: 1px solid #34d399;
    }
    .badge-cushion-danger {
        display: inline-flex;
        align-items: center;
        background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
        color: #ffffff;
        font-weight: bold;
        font-size: 11.5px;
        padding: 2px 8px;
        border-radius: 6px;
        border: 1px solid #f87171;
    }
    .badge-synergy {
        display: inline-flex;
        align-items: center;
        padding: 2px 8px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 11.5px;
        letter-spacing: 0.3px;
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
    .badge-f1-rap {
        background: linear-gradient(135deg, #FF0844 0%, #FFB199 100%);
        color: #ffffff;
        border: 1px solid #FFD1C4;
    }
    .badge-bomb {
        background: linear-gradient(135deg, #EB3349 0%, #F45C43 100%);
        color: #ffffff;
        border: 1px solid #FFA07A;
    }
    .badge-target-win {
        background: linear-gradient(135deg, #e11d48 0%, #be123c 100%);
        color: #ffffff;
        font-weight: bold;
        font-size: 12px;
        padding: 2px 9px;
        border-radius: 6px;
    }
    .badge-target-axis {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: #ffffff;
        font-weight: bold;
        font-size: 12px;
        padding: 2px 9px;
        border-radius: 6px;
    }
    .badge-danger-jockey {
        background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%);
        color: #fecaca;
        font-weight: bold;
        font-size: 12px;
        padding: 2px 9px;
        border-radius: 6px;
        border: 1px solid #ef4444;
    }
    .badge-danger-rescued {
        background: linear-gradient(135deg, #431407 0%, #9a3412 100%);
        color: #ffedd5;
        font-weight: bold;
        font-size: 12px;
        padding: 2px 9px;
        border-radius: 6px;
        border: 1px solid #f97316;
    }
    .rank-1st { color: #FFD700; font-weight: bold; }
    .rank-2nd { color: #E2E8F0; font-weight: bold; }
    .rank-3rd { color: #F97316; font-weight: bold; }
</style>
""",
    unsafe_allow_html=True,
)

# --- 危険騎手リスト定義 ---
DANGER_JOCKEYS_F3 = [
    '斎藤新',
    '小沢大仁',
    '丸山元気',
    '池添謙一',
    '松若風馬',
    '菊沢一樹',
    '田辺裕信',
    '横山琉人',
    '岩田康誠',
    '吉田隼人',
    '菅原明良',
    '富田暁',
    '三浦皇成',
    '浜中俊',
    '鮫島克駿',
]
DANGER_JOCKEYS_GENERAL = [
    '小林脩斗',
    '川端海翼',
    '黛弘人',
    '野中悠太',
    '遠藤汰月',
    '亀田温心',
    '水沼元輝',
    '丸田恭介',
    '河原田菜',
    '古川吉洋',
    '国分優作',
    '永島まな',
    '柴田裕一',
    '木幡初也',
    '原田和真',
    '柴田大知',
    '古川奈穂',
    '中井裕二',
    '石橋脩',
    '嶋田純次',
]


# --- クッション値×種牡馬バイアス判定マッピング ---
def get_cushion_band(venue, c_val):
  if c_val is None:
    return 'standard'
  if venue == '札幌':
    if c_val >= 7.7:
      return 'sapporo_high'
    elif c_val <= 7.3:
      return 'sapporo_low'
    else:
      return 'standard'
  elif venue == '函館':
    if c_val >= 7.5:
      return 'hakodate_high'
    elif c_val <= 7.2:
      return 'hakodate_low'
    else:
      return 'standard'
  if c_val >= 10.5:
    return 'super_high'
  elif c_val >= 10.0:
    return 'high'
  elif c_val >= 9.5:
    return 'standard_high'
  elif c_val >= 8.6:
    return 'standard_low'
  else:
    return 'low'


def evaluate_sire_cushion(sire_name, venue, dist, band):
  if not sire_name or pd.isnull(sire_name):
    return ''
  sire = str(sire_name).strip()
  dist_val = int(re.sub(r'\D', '', str(dist))) if dist else 0

  if band == 'super_high':
    if (
        'エピファネイア' in sire
        or 'キタサンブラック' in sire
        or 'イスラボニータ' in sire
    ):
      return (
          "<span class='badge-cushion-fit'>🟢 超高クッション特注"
          ' (適性突出)</span>'
      )
    if 'ロードカナロア' in sire and dist_val == 1800:
      return (
          "<span class='badge-cushion-fit'>🟢 超高クッション特注"
          ' (芝1800)</span>'
      )
    if any(
        d in sire
        for d in [
            'キングカメハメハ',
            'ビッグアーサー',
            'レイデオロ',
            'スワーヴリチャード',
            'サートゥルナーリア',
            'ゴールドシップ',
        ]
    ):
      return (
          "<span class='badge-cushion-danger'>🔴 超高帯危険血統"
          ' (大幅割引)</span>'
      )

  if venue == '京都':
    if band == 'super_high':
      if 'キタサンブラック' in sire and dist_val == 2000:
        return (
            "<span class='badge-cushion-fit'>🟢 京都2000×超高帯 特注"
            ' (勝21.1%)</span>'
        )
      if 'エピファネイア' in sire and dist_val == 1600:
        return (
            "<span class='badge-cushion-fit'>🟢 京都1600×超高帯 特注"
            ' (複50%)</span>'
        )
      if 'ゴールドシップ' in sire and dist_val == 2000:
        return (
            "<span class='badge-cushion-danger'>🔴 京都2000×超高帯 危険"
            ' (複12.1%)</span>'
        )
  elif venue == '東京':
    if band == 'standard_high':
      if 'エピファネイア' in sire and dist_val == 1600:
        return (
            "<span class='badge-cushion-fit'>🟢 東京1600×9.5-9.9 特注"
            ' (単277%)</span>'
        )
      if 'モーリス' in sire and dist_val == 1400:
        return (
            "<span class='badge-cushion-fit'>🟢 東京1400×9.5-9.9 特注"
            ' (単408%)</span>'
        )
      if 'ディープインパクト' in sire and dist_val == 1800:
        return (
            "<span class='badge-cushion-fit'>🟢 東京1800×9.5-9.9 特注"
            ' (単228%)</span>'
        )
      if 'ルーラーシップ' in sire and dist_val in [1800, 2000]:
        return (
            "<span class='badge-cushion-danger'>🔴 東京中距離×9.5-9.9 危険"
            ' (勝0%)</span>'
        )
      if 'ゴールドシップ' in sire and dist_val in [1600, 2400]:
        return (
            "<span class='badge-cushion-danger'>🔴 東京×9.5-9.9 危険"
            ' (複極小)</span>'
        )
    elif band == 'standard_low':
      if 'キズナ' in sire and dist_val == 2000:
        return (
            "<span class='badge-cushion-fit'>🟢 東京2000×8.6-9.4 特注"
            ' (単200%)</span>'
        )
      if 'シルバーステート' in sire and dist_val == 1400:
        return (
            "<span class='badge-cushion-danger'>🔴 東京1400×8.6-9.4 危険"
            ' (勝0%)</span>'
        )
  elif venue == '中山':
    if band == 'standard_high':
      if 'シルバーステート' in sire and dist_val == 1600:
        return (
            "<span class='badge-cushion-fit'>🟢 中山1600×9.5-9.9 特注"
            ' (単225%)</span>'
        )
      if 'ダノンバラード' in sire and dist_val == 2000:
        return (
            "<span class='badge-cushion-danger'>🔴 中山2000×9.5-9.9 危険"
            ' (複0%)</span>'
        )
      if 'エピファネイア' in sire and dist_val == 1600:
        return (
            "<span class='badge-cushion-danger'>🔴 中山1600×9.5-9.9 危険"
            ' (複14.5%)</span>'
        )
  elif venue == '阪神':
    if band == 'standard_high':
      if 'キズナ' in sire and dist_val == 1800:
        return (
            "<span class='badge-cushion-fit'>🟢 阪神1800外×9.5-9.9 特注"
            ' (単421%)</span>'
        )
      if 'ハービンジャー' in sire and dist_val == 1800:
        return (
            "<span class='badge-cushion-danger'>🔴 阪神1800外×9.5-9.9 危険"
            ' (複10%)</span>'
        )
    elif band == 'standard_low':
      if 'ルーラーシップ' in sire and dist_val == 1600:
        return (
            "<span class='badge-cushion-fit'>🟢 阪神1600外×8.6-9.4 特注"
            ' (単156%)</span>'
        )
      if 'ゴールドシップ' in sire and dist_val == 2000:
        return (
            "<span class='badge-cushion-danger'>🔴 阪神2000内×8.6-9.4 危険"
            ' (複10%)</span>'
        )
  elif venue == '函館':
    if 'キズナ' in sire and dist_val == 1800:
      return (
          "<span class='badge-cushion-fit'>🟢 函館1800×低クッション 特注"
          ' (単143%)</span>'
      )
    if 'モーリス' in sire and dist_val == 1200:
      return (
          "<span class='badge-cushion-fit'>🟢 函館1200×低クッション 特注"
          ' (単136%)</span>'
      )
    if 'ディープインパクト' in sire and dist_val == 1200:
      return (
          "<span class='badge-cushion-danger'>🔴 函館1200×低クッション 危険"
          ' (勝0%)</span>'
      )
    if 'ルーラーシップ' in sire and dist_val == 1800:
      return (
          "<span class='badge-cushion-danger'>🔴 函館1800×低クッション 危険"
          ' (複17%)</span>'
      )
  elif venue == '札幌':
    if 'オルフェーヴル' in sire and dist_val == 2000:
      return (
          "<span class='badge-cushion-fit'>🟢 札幌2000×低クッション 特注"
          ' (単136%)</span>'
      )
    if 'ロードカナロア' in sire and dist_val == 1200:
      return (
          "<span class='badge-cushion-fit'>🟢 札幌1200×低クッション 特注"
          ' (単121%)</span>'
      )
    if 'エピファネイア' in sire and dist_val == 1800:
      return (
          "<span class='badge-cushion-danger'>🔴 札幌1800×低クッション 危険"
          ' (単14%)</span>'
      )
    if 'ゴールドシップ' in sire and dist_val == 2600:
      return (
          "<span class='badge-cushion-danger'>🔴 札幌2600×低クッション 危険"
          ' (複17.5%)</span>'
      )
  elif venue == '小倉':
    if (
        band == 'standard_low'
        and 'ビッグアーサー' in sire
        and dist_val == 1200
    ):
      return (
          "<span class='badge-cushion-fit'>🟢 小倉1200×8.6-9.4 特注"
          ' (複30.9%)</span>'
      )
    if (
        band == 'standard_high'
        and 'ダイワメジャー' in sire
        and dist_val == 1200
    ):
      return (
          "<span class='badge-cushion-fit'>🟢 小倉1200×9.5-9.9 特注"
          ' (単173%)</span>'
      )
    if dist_val == 1200 and (
        'ジャスタウェイ' in sire or 'ヴィクトワールピサ' in sire
    ):
      return (
          "<span class='badge-cushion-danger'>🔴 小倉1200 危険血統"
          ' (勝0〜2%)</span>'
      )
  elif venue == '福島':
    if band == 'standard_low':
      if 'ビッグアーサー' in sire and dist_val == 1200:
        return (
            "<span class='badge-cushion-fit'>🟢 福島1200×8.6-9.4 特注"
            ' (複33.1%)</span>'
        )
      if 'ダノンバラード' in sire and dist_val == 1800:
        return (
            "<span class='badge-cushion-fit'>🟢 福島1800×8.6-9.4 特注"
            ' (単413%)</span>'
        )
      if dist_val == 1200 and (
          'マツリダゴッホ' in sire or 'カレンブラックヒル' in sire
      ):
        return (
            "<span class='badge-cushion-danger'>🔴 福島1200×8.6-9.4"
            ' 危険血統</span>'
        )
      if dist_val == 2000 and 'ルーラーシップ' in sire:
        return (
            "<span class='badge-cushion-danger'>🔴 福島2000×8.6-9.4 危険"
            ' (複4.7%)</span>'
        )
  elif venue == '新潟':
    if 'ロードカナロア' in sire:
      if band == 'standard_low' and dist_val == 1400:
        return (
            "<span class='badge-cushion-fit'>🟢 新潟1400内×8.6-9.4 特注"
            ' (単174%)</span>'
        )
      if band == 'standard_high' and dist_val == 1000:
        return (
            "<span class='badge-cushion-fit'>🟢 新潟1000直×9.5-9.9 特注"
            ' (単344%)</span>'
        )
    if band == 'standard_high' and 'ハーツクライ' in sire and dist_val == 1800:
      return (
          "<span class='badge-cushion-fit'>🟢 新潟1800外×9.5-9.9 特注"
          ' (複50%)</span>'
      )
    if dist_val == 1400 and 'リオンディーズ' in sire:
      return (
          "<span class='badge-cushion-danger'>🔴 新潟1400内 危険血統"
          ' (複6.7%)</span>'
      )
    if dist_val == 1800 and 'ジャスタウェイ' in sire:
      return (
          "<span class='badge-cushion-danger'>🔴 新潟1800外 危険血統"
          ' (勝0%)</span>'
      )

  return ''


# --- JRA枠番計算関数 ---
def get_jra_waku(umaban, total_horses):
  if total_horses <= 8:
    return umaban
  base = total_horses // 8
  rem = total_horses % 8
  waku_counts = [base + (1 if 8 - i <= rem else 0) for i in range(8)]
  curr = 1
  for w_idx, cnt in enumerate(waku_counts, start=1):
    if curr <= umaban < curr + cnt:
      return w_idx
    curr += cnt
  return 8


# --- サイドバー: データ読み込み ---
st.sidebar.markdown('### 📁 CSVデータ読み込み')
with st.sidebar.expander('データ更新', expanded=False):
  up_index = st.file_uploader('出馬表・指数 CSV', type=['csv'], key='up_index')
  up_sakaro = st.file_uploader('坂路調教 CSV', type=['csv'], key='up_sakaro')
  up_wood = st.file_uploader('ウッド調教 CSV', type=['csv'], key='up_wood')


def clean_horse_name(name):
  if pd.isnull(name):
    return ''
  return (
      str(name)
      .strip()
      .replace('*', '')
      .replace('$', '')
      .replace(' ', '')
      .replace(' ', '')
  )


def read_csv_robust(file_obj, candidate_patterns):
  src = file_obj
  if src is None:
    matched = []
    for pat in candidate_patterns:
      matched.extend(glob.glob(pat))
    if matched:
      src = max(matched, key=os.path.getmtime)
  if src is None:
    return pd.DataFrame()

  encodings = ['cp932', 'shift-jis', 'utf-8-sig', 'utf-8']
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


def find_col_regex(df, patterns):
  for pat in patterns:
    for col in df.columns:
      if re.search(pat, str(col), re.IGNORECASE):
        return col
  return None


def load_and_merge_all(f_index, f_sakaro, f_wood):
  index_patterns = [
      'data/出馬表_指数*.csv',
      '出馬表_指数*.csv',
      'data/*指数*.csv',
      '*指数*.csv',
  ]
  index_src = f_index
  if index_src is None:
    matched = []
    for pat in index_patterns:
      matched.extend(glob.glob(pat))
    if matched:
      index_src = max(matched, key=os.path.getmtime)

  records = []
  if index_src is not None:
    lines = []
    for enc in ['cp932', 'shift-jis', 'utf-8-sig', 'utf-8']:
      try:
        if isinstance(index_src, str):
          with open(index_src, 'r', encoding=enc, errors='ignore') as f:
            lines = f.readlines()
        else:
          index_src.seek(0)
          lines = index_src.read().decode(enc, errors='ignore').splitlines()
        if lines:
          break
      except Exception:
        continue

    fw_map = {
        '１': 1,
        '２': 2,
        '３': 3,
        '４': 4,
        '５': 5,
        '６': 6,
        '７': 7,
        '８': 8,
        '９': 9,
        '10': 10,
        '11': 11,
        '12': 12,
        '13': 13,
        '14': 14,
        '15': 15,
        '16': 16,
        '17': 17,
        '18': 18,
    }

    for line in lines:
      parts = [p.strip() for p in line.strip().split(',')]
      n = len(parts)
      if n < 10 or parts[0] in ['場所', 'レースID', 'race_id']:
        continue

      race_id, track, dist, umaban, horse_raw = (
          parts[0],
          parts[1],
          parts[2],
          parts[3],
          parts[4],
      )
      trainer, jockey, pop = parts[6], parts[7], parts[8]
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

      non_empty_parts = [p for p in parts if p != '']
      sire = non_empty_parts[-1] if len(non_empty_parts) > 0 else ''
      finish = non_empty_parts[-2] if len(non_empty_parts) > 1 else None

      horse = clean_horse_name(horse_raw)
      if horse:
        fin_int = fw_map.get(
            str(finish), int(finish) if str(finish).isdigit() else np.nan
        )
        pop_int = int(pop) if str(pop).isdigit() else np.nan
        u_int = int(umaban) if str(umaban).isdigit() else 99

        records.append({
            'race_id': race_id,
            'track': track,
            'dist': dist,
            '馬番': u_int,
            '馬名': horse,
            '印': mark,
            '調教師': clean_horse_name(trainer),
            '騎手': clean_horse_name(jockey),
            '種牡馬': str(sire).strip(),
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
            'tua_rank': int(tua_rank) if not np.isnan(tua_rank) else 99,
        })

  df_main = pd.DataFrame(records)
  if df_main.empty:
    return pd.DataFrame(), None

  venue_dict = {
      '東': '東京',
      '中': '中山',
      '京': '京都',
      '阪': '阪神',
      '名': '中京',
      '小': '小倉',
      '新': '新潟',
      '福': '福島',
      '函': '函館',
      '札': '札幌',
  }

  def parse_race(rid):
    match = re.match(r'([^\d]+)(\d+)', str(rid))
    if match:
      return venue_dict.get(match.group(1), match.group(1)), int(match.group(2))
    return 'その他', 99

  df_main[['競馬場名', 'R番号']] = df_main['race_id'].apply(
      lambda x: pd.Series(parse_race(x))
  )
  df_main['race_uid'] = df_main['race_id']
  detected_date = datetime.date(2026, 9, 12)

  df_main['total_horses'] = df_main.groupby('race_id')['馬番'].transform('count')
  df_main['枠番'] = df_main.apply(
      lambda r: get_jra_waku(r['馬番'], r['total_horses']), axis=1
  )

  # 坂路調教CSV読み込み（実質負荷基準：4F<=56.0s かつ 1F<=13.0s）
  sakaro_patterns = [
      'data/出馬表_坂路*.csv',
      '出馬表_坂路*.csv',
      'data/*坂路*.csv',
      '*坂路*.csv',
  ]
  df_s_raw = read_csv_robust(f_sakaro, sakaro_patterns)
  if not df_s_raw.empty:
    c_s_name = find_col_regex(df_s_raw, ['^馬名$', '^競走馬名$']) or (
        df_s_raw.columns[3]
        if len(df_s_raw.columns) > 3
        else df_s_raw.columns[1]
    )
    df_s_raw['clean_name'] = df_s_raw[c_s_name].apply(clean_horse_name)

    c_s_4f = (
        find_col_regex(df_s_raw, ['^time1$', '^4f$', '^４ｆ$', '^4Ｆ$'])
        or df_s_raw.columns[8]
    )
    c_s_1f = (
        find_col_regex(df_s_raw, ['^time4$', '^1f$', '^１ｆ$', '^1Ｆ$'])
        or df_s_raw.columns[12]
    )
    c_s_l4 = (
        find_col_regex(df_s_raw, ['^lap4$', '^ｌａｐ４$']) or df_s_raw.columns[9]
    )
    c_s_l3 = (
        find_col_regex(df_s_raw, ['^lap3$', '^ｌａｐ３$']) or df_s_raw.columns[10]
    )
    c_s_l2 = (
        find_col_regex(df_s_raw, ['^lap2$', '^ｌａｐ２$']) or df_s_raw.columns[11]
    )
    c_s_l1 = (
        find_col_regex(df_s_raw, ['^lap1$', '^ｌａｐ１$']) or df_s_raw.columns[12]
    )

    df_s_raw['坂路_4F'] = pd.to_numeric(df_s_raw[c_s_4f], errors='coerce')
    df_s_raw['坂路_1F'] = pd.to_numeric(df_s_raw[c_s_1f], errors='coerce')
    df_s_raw['坂路_Lap4'] = pd.to_numeric(df_s_raw[c_s_l4], errors='coerce')
    df_s_raw['坂路_Lap3'] = pd.to_numeric(df_s_raw[c_s_l3], errors='coerce')
    df_s_raw['坂路_Lap2'] = pd.to_numeric(df_s_raw[c_s_l2], errors='coerce')
    df_s_raw['坂路_Lap1'] = pd.to_numeric(df_s_raw[c_s_l1], errors='coerce')

    df_s_best = (
        df_s_raw.dropna(subset=['坂路_4F'])
        .sort_values('坂路_4F')
        .drop_duplicates('clean_name', keep='first')
        .copy()
    )

    df_s_best['坂路_完全加速'] = (
        (df_s_best['坂路_Lap4'] > df_s_best['坂路_Lap3'])
        & (df_s_best['坂路_Lap3'] > df_s_best['坂路_Lap2'])
        & (df_s_best['坂路_Lap2'] > df_s_best['坂路_Lap1'])
        & (df_s_best['坂路_4F'] <= 56.0)
        & (df_s_best['坂路_Lap1'] <= 13.0)
    )
    df_s_best['坂路_穴トリガー'] = (df_s_best['坂路_Lap3'] <= 14.0) & (
        df_s_best['坂路_Lap2'] > df_s_best['坂路_Lap1']
    )

    df_main = pd.merge(
        df_main,
        df_s_best[[
            'clean_name',
            '坂路_4F',
            '坂路_1F',
            '坂路_完全加速',
            '坂路_穴トリガー',
        ]],
        left_on='馬名',
        right_on='clean_name',
        how='left',
    )

  if '坂路_4F' not in df_main.columns:
    df_main['坂路_4F'] = np.nan
    df_main['坂路_1F'] = np.nan
    df_main['坂路_完全加速'] = False
    df_main['坂路_穴トリガー'] = False

  # ウッド調教CSV読み込み
  wood_patterns = [
      'data/出馬表_ウッド*.csv',
      '出馬表_ウッド*.csv',
      'data/*ウッド*.csv',
      '*ウッド*.csv',
  ]
  df_w_raw = read_csv_robust(f_wood, wood_patterns)
  if not df_w_raw.empty:
    c_w_name = find_col_regex(df_w_raw, ['^馬名$', '^競走馬名$']) or (
        df_w_raw.columns[3]
        if len(df_w_raw.columns) > 3
        else df_w_raw.columns[1]
    )
    df_w_raw['clean_name'] = df_w_raw[c_w_name].apply(clean_horse_name)

    c_w_5f = (
        find_col_regex(df_w_raw, ['^5f$', '^５ｆ$', '^5Ｆ$'])
        or df_w_raw.columns[13]
    )
    c_w_1f = (
        find_col_regex(df_w_raw, ['^1f$', '^１ｆ$', '^1Ｆ$'])
        or df_w_raw.columns[23]
    )
    c_w_l2 = (
        find_col_regex(df_w_raw, ['^lap2$', '^ｌａｐ２$']) or df_w_raw.columns[22]
    )
    c_w_l1 = (
        find_col_regex(df_w_raw, ['^lap1$', '^ｌａｐ１$']) or df_w_raw.columns[23]
    )

    df_w_raw['wood_5F'] = pd.to_numeric(df_w_raw[c_w_5f], errors='coerce')
    df_w_raw['wood_1F'] = pd.to_numeric(df_w_raw[c_w_1f], errors='coerce')
    df_w_raw['wood_Lap2'] = pd.to_numeric(df_w_raw[c_w_l2], errors='coerce')
    df_w_raw['wood_Lap1'] = pd.to_numeric(df_w_raw[c_w_l1], errors='coerce')

    df_w_best = (
        df_w_raw.dropna(subset=['wood_1F'])
        .sort_values('wood_1F')
        .drop_duplicates('clean_name', keep='first')
        .copy()
    )
    df_w_best['wood_accel'] = df_w_best['wood_Lap2'] - df_w_best['wood_Lap1']
    df_w_best['is_wood_accel'] = (df_w_best['wood_accel'] > 0) & (
        df_w_best['wood_accel'].notna()
    )

    df_main = pd.merge(
        df_main,
        df_w_best[[
            'clean_name',
            'wood_5F',
            'wood_1F',
            'wood_accel',
            'is_wood_accel',
        ]],
        left_on='馬名',
        right_on='clean_name',
        how='left',
    )

  if 'wood_1F' not in df_main.columns:
    df_main['wood_5F'] = np.nan
    df_main['wood_1F'] = np.nan
    df_main['wood_accel'] = np.nan
    df_main['is_wood_accel'] = False

  df_main['坂路_完全加速'] = df_main['坂路_完全加速'].fillna(False).astype(bool)
  df_main['坂路_穴トリガー'] = df_main['坂路_穴トリガー'].fillna(False).astype(bool)
  df_main['is_wood_accel'] = df_main['is_wood_accel'].fillna(False).astype(bool)

  # 騎手・調教師の同馬番・同枠集計
  jk_ub_grp = df_main.groupby(['騎手', '馬番'])['race_id'].apply(list).to_dict()
  df_main['same_ub_jk_count'] = df_main.apply(
      lambda r: len(jk_ub_grp.get((r['騎手'], r['馬番']), [])), axis=1
  )
  df_main['same_ub_jk_races'] = df_main.apply(
      lambda r: ', '.join(jk_ub_grp.get((r['騎手'], r['馬番']), [])), axis=1
  )
  df_main['is_same_ub_jk'] = df_main['same_ub_jk_count'] >= 2

  tr_ub_grp = (
      df_main.groupby(['調教師', '馬番'])['race_id'].apply(list).to_dict()
  )
  df_main['same_ub_tr_count'] = df_main.apply(
      lambda r: len(tr_ub_grp.get((r['調教師'], r['馬番']), [])), axis=1
  )
  df_main['same_ub_tr_races'] = df_main.apply(
      lambda r: ', '.join(tr_ub_grp.get((r['調教師'], r['馬番']), [])), axis=1
  )
  df_main['is_same_ub_tr'] = df_main['same_ub_tr_count'] >= 2

  df_main['is_same_ub_any'] = df_main['is_same_ub_jk'] | df_main['is_same_ub_tr']

  jk_waku_grp = (
      df_main.groupby(['騎手', '枠番'])['race_id'].transform('count') >= 2
  )
  tr_waku_grp = (
      df_main.groupby(['調教師', '枠番'])['race_id'].transform('count') >= 2
  )
  df_main['is_same_waku'] = jk_waku_grp | tr_waku_grp

  return df_main, detected_date


# データロード実行
df, race_date = load_and_merge_all(up_index, up_sakaro, up_wood)

if df.empty:
  st.warning(
      '⚠️ CSVデータが読み込まれていません。サイドバーから出走表・坂路・ウッドのCSVファイルを指定してください。'
  )
  st.stop()

# ==============================================================================
# ★ 全ファクター統合・判定マトリクス
# ==============================================================================
df['調教加速'] = df['坂路_完全加速'] | df['is_wood_accel']

# SSS級・絶対神域
df['is_sss_level'] = (
    (df['F指数'] >= 70) & (df['arms'] >= 120) & (df['tua'] >= 200)
)

# 指数の四冠馬
df['is_four_crown'] = (
    (df['F_rank'] <= 2)
    & (df['Fup_rank'] <= 2)
    & (df['arms_rank'] <= 2)
    & (df['tua_rank'] <= 2)
)

# Fup2の罠と確変判定
df['is_fup_trap'] = (
    (df['Fup'] == 1)
    & (df['人気'] <= 3)
    & (df['F指数'] <= 72)
    & (~df['is_sss_level'])
)
df['is_fup_kakugen'] = df['Fup'] == 7

# 陣営黄金コンビ・特注バイアス判定
def check_camp_bias(row):
  tr = str(row.get('調教師', ''))
  jk = str(row.get('騎手', ''))
  f_rank = row.get('F_rank', 99)
  fup = row.get('Fup', 0)

  if '中内田' in tr and '川田' in jk and f_rank == 1:
    return 'camp_nakauchida_kawada'
  if '木村哲也' in tr and 'ルメール' in jk:
    return 'camp_kimura_lemaire_ok' if fup >= 5 else 'camp_kimura_lemaire_ng'
  if ('斉藤崇史' in tr or '中舘英二' in tr) and f_rank == 1:
    return 'camp_saito_nakadate'
  return ''


df['camp_bias'] = df.apply(check_camp_bias, axis=1)

# Fup 1位(6点以上) × S/F6位以内
df['flag_fup6_s6'] = (
    (df['Fup'] >= 6) & (df['Fup_rank'] == 1) & (df['S_rank'] <= 6)
)
df['flag_fup6_f6'] = (
    (df['Fup'] >= 6) & (df['Fup_rank'] == 1) & (df['F_rank'] <= 6)
)
df['flag_fup6_sf_any'] = df['flag_fup6_s6'] | df['flag_fup6_f6']

# シナジー定義
df['is_syn_iron'] = (
    (df['F_rank'] == 1)
    & (df['arms_rank'] <= 3)
    & (df['wood_1F'] <= 11.5)
    & df['is_wood_accel']
)
df['is_syn_high'] = (
    ((df['F_rank'] == 1) | (df['F指数'] >= 66))
    & (df['wood_1F'] <= 11.5)
    & df['is_wood_accel']
)
df['is_syn_fup_sakaro'] = (df['Fup'] >= 5) & df['坂路_完全加速']
df['is_syn_bomb'] = (df['人気'] >= 6) & (df['Fup'] >= 4) & df['調教加速']
df['is_syn_f1_rap'] = (df['F_rank'] == 1) & (
    ((df['坂路_1F'] <= 12.4) & df['坂路_完全加速'])
    | ((df['wood_1F'] <= 11.5) & df['is_wood_accel'])
)

df['syn_jk_ub_wood'] = (
    df['is_same_ub_jk'] & df['is_wood_accel'] & (df['F_rank'] <= 3)
)
df['syn_jk_ub_bomb'] = (
    df['is_same_ub_jk']
    & df['調教加速']
    & (df['Fup'] >= 4)
    & (df['人気'] >= 6)
)
df['syn_tr_ub_arms'] = df['is_same_ub_tr'] & (df['arms_rank'] <= 3)

df['syn_same_ub_f6'] = df['is_same_ub_any'] & (df['F_rank'] <= 6)
df['syn_same_ub_s6'] = df['is_same_ub_any'] & (df['S_rank'] <= 6)
df['syn_same_ub_fs6'] = df['syn_same_ub_f6'] & df['syn_same_ub_s6']

df['flag_sf7_himo'] = ((df['S_rank'] <= 7) | (df['F_rank'] <= 7)) & (
    df['調教加速'] | df['is_same_waku'] | df['is_same_ub_any']
)

# ------------------------------------------------------------------------------
# ★ 危険騎手の判定 ＆ 複数狙い目重複による救済ロジック
# ------------------------------------------------------------------------------
def evaluate_danger_jockey(row):
  jk = str(row.get('騎手', '')).strip()
  is_f3 = row.get('F_rank', 99) <= 3
  is_any3 = (
      (row.get('F_rank', 99) <= 3)
      or (row.get('arms_rank', 99) <= 3)
      or (row.get('tua_rank', 99) <= 3)
      or (row.get('S_rank', 99) <= 3)
  )

  is_raw_danger = False
  if is_f3 and any(d in jk for d in DANGER_JOCKEYS_F3):
    is_raw_danger = True
  if is_any3 and any(d in jk for d in DANGER_JOCKEYS_GENERAL):
    is_raw_danger = True

  if not is_raw_danger:
    return False, False  # 危険なし

  # 狙い目項目の重複カウント（2つ以上あれば救済）
  synergy_count = 0
  if row.get('flag_fup6_sf_any'):
    synergy_count += 1
  if row.get('is_syn_iron') or row.get('is_syn_high'):
    synergy_count += 1
  if row.get('is_syn_f1_rap'):
    synergy_count += 1
  if row.get('is_syn_fup_sakaro') or row.get('坂路_完全加速'):
    synergy_count += 1
  if row.get('is_same_ub_any'):
    synergy_count += 1
  if row.get('is_sss_level') or row.get('is_four_crown'):
    synergy_count += 1
  if row.get('flag_sf7_himo'):
    synergy_count += 1

  if synergy_count >= 2:
    return False, True  # 救済（危険判定解除・救済フラグON）
  return True, False  # 本物の危険騎手（消去対象）


eval_jk = df.apply(evaluate_danger_jockey, axis=1)
df['is_danger_jockey'] = [e[0] for e in eval_jk]
df['is_danger_rescued'] = [e[1] for e in eval_jk]

# 1着狙い・連対狙い定義（救済馬も組み込み対象）
df['target_win'] = (
    (
        ((df['F_rank'] == 1) & (df['arms_rank'] == 1))
        | ((df['Fup'] >= 5) & (df['F_rank'] == 1))
        | (
            (df['F_rank'] == 1)
            & (df['arms_rank'] <= 3)
            & (df['S_rank'] <= 3)
        )
        | ((df['F指数'] >= 66) & (df['arms_rank'] == 1))
        | df['flag_fup6_sf_any']
        | df['is_sss_level']
        | (
            df['camp_bias'].isin(
                ['camp_nakauchida_kawada', 'camp_saito_nakadate']
            )
        )
        | (df['is_danger_rescued'] & (df['F_rank'] <= 2))
    )
    & (~df['is_danger_jockey'])
    & (~df['is_fup_trap'])
)

df['target_axis'] = (
    (
        ((df['F_rank'] <= 2) & (df['arms_rank'] <= 3))
        | ((df['F_rank'] == 1) & (df['tua_rank'] <= 3))
        | ((df['Fup'] >= 4) & (df['F_rank'] <= 3))
        | df['is_four_crown']
        | df['is_danger_rescued']
    )
    & (~df['target_win'])
    & (~df['is_danger_jockey'])
    & (~df['is_fup_trap'])
)

df['target_himo'] = (
    (df['人気'] >= 6)
    & df['調教加速']
    & (
        (df['arms_rank'] <= 5)
        | (df['Fup'] >= 4)
        | (df['tua_rank'] <= 3)
    )
) | (
    (df['人気'] >= 6)
    & (df['人気'] <= 10)
    & df['坂路_穴トリガー']
    & (df['Fup'] >= 4)
)

# ==============================================================================
# ★ サイドバー: 馬場設定＆クッション値
# ==============================================================================
st.sidebar.markdown('### 芝馬場状態')
turf_condition = st.sidebar.selectbox(
    '芝馬場状態',
    ['良', '稍重', '重', '不良'],
    index=0,
    label_visibility='collapsed',
)

venue_sort_order = [
    '東京',
    '中山',
    '京都',
    '阪神',
    '中京',
    '小倉',
    '新潟',
    '福島',
    '函館',
    '札幌',
]
existing_venues = [v for v in venue_sort_order if v in df['競馬場名'].unique()]
if (
    'active_venue' not in st.session_state
    or st.session_state['active_venue'] not in existing_venues
):
  st.session_state['active_venue'] = existing_venues[0]

default_cushions = {
    '札幌': 7.5,
    '函館': 7.4,
    '中京': 9.6,
    '新潟': 9.3,
    '東京': 9.3,
    '中山': 9.6,
    '京都': 10.0,
    '阪神': 9.4,
    '小倉': 9.2,
    '福島': 8.9,
}

st.sidebar.markdown(f"### 芝クッション値 ({st.session_state['active_venue']})")
cushion_state_key = f"cushion_val_{st.session_state['active_venue']}"
if cushion_state_key not in st.session_state:
  st.session_state[cushion_state_key] = default_cushions.get(
      st.session_state['active_venue'], 9.5
  )

current_cushion_val = st.sidebar.number_input(
    f"芝クッション値 ({st.session_state['active_venue']})",
    min_value=5.0,
    max_value=13.0,
    value=float(st.session_state[cushion_state_key]),
    step=0.1,
    key=cushion_state_key,
    label_visibility='collapsed',
)
current_band = get_cushion_band(
    st.session_state['active_venue'], current_cushion_val
)

# ==============================================================================
# ★ フィルター設定
# ==============================================================================
st.sidebar.markdown('---')
st.sidebar.markdown('### 👑 黄金シナジー・絶対軸馬')
syn_iron = st.sidebar.checkbox(
    f"💎 鉄板軸馬 ({int(df['is_syn_iron'].sum())}頭)",
    help='複勝率 61.9% / 連対率 46.3%',
)
syn_high = st.sidebar.checkbox(
    f"🔥 高確率軸馬 ({int(df['is_syn_high'].sum())}頭)",
    help='複勝率 55%超ゾーン',
)
syn_fup_sakaro = st.sidebar.checkbox(
    f"✨ Fup坂路完全 ({int(df['is_syn_fup_sakaro'].sum())}頭)",
    help='Fup5点以上×坂路完全加速',
)
syn_f1_rap = st.sidebar.checkbox(
    f"🔥 SSS級・究極ラップ ({int(df['is_syn_f1_rap'].sum())}頭)"
)
syn_bomb = st.sidebar.checkbox(
    f"💣 爆弾穴馬 ({int(df['is_syn_bomb'].sum())}頭)",
    help='6人気以下×Fup4点以上×調教加速',
)

st.sidebar.markdown('### 🎯 狙い目抽出')
filter_fup6_sf = st.sidebar.checkbox(
    f"🔥 Fup1位(6点+) × S/F6位内 ({int(df['flag_fup6_sf_any'].sum())}頭)",
    help='勝率25.0%・単回収200%超のアタマ特化',
)
filter_target_win = st.sidebar.checkbox(
    f"🥇 1着狙い (勝率26%超) ({int(df['target_win'].sum())}頭)"
)
filter_target_axis = st.sidebar.checkbox(
    f"🛡️ 軸・連対狙い (複勝率55%超) ({int(df['target_axis'].sum())}頭)"
)
filter_sf7_himo = st.sidebar.checkbox(
    f"🌪️ SF7×加速/同枠 (穴ヒモ) ({int(df['flag_sf7_himo'].sum())}頭)"
)
filter_target_himo = st.sidebar.checkbox(
    f"💣 紐穴・使者狙い ({int(df['target_himo'].sum())}頭)"
)

st.sidebar.markdown('### ⚠️ 危険警告')
filter_danger_jockey = st.sidebar.checkbox(
    f"⚠️ 危険騎手【危】のみ表示 ({int(df['is_danger_jockey'].sum())}頭)"
)
filter_fup_trap = st.sidebar.checkbox(
    f"⚠️ Fup1の罠馬 ({int(df['is_fup_trap'].sum())}頭)"
)

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
    f" ({w_str}) | クッション値Vr 稼働中</div>",
    unsafe_allow_html=True,
)

chosen_venue = st.radio(
    '開催場選択',
    options=existing_venues,
    horizontal=True,
    label_visibility='collapsed',
)
st.session_state['active_venue'] = chosen_venue

v_df = df[df['競馬場名'] == chosen_venue]
races_in_v = (
    v_df[['race_uid', 'race_id', 'R番号', 'track', 'dist']]
    .drop_duplicates('race_uid')
    .sort_values('R番号')
)

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
  fav3 = r_horses[r_horses['人気'] <= 3]
  cond2 = (
      not bool((fav3['is_danger_jockey'] == True).any())
      if not fav3.empty
      else True
  )
  f1_h = r_horses[r_horses['F_rank'] == 1]
  f1_val = f1_h['F指数'].values[0] if not f1_h.empty else 0
  cond3 = f1_val >= 60

  tag = '🎯狙' if (cond1 and cond2 and cond3) else '🔥荒'

  marks = []
  if r_iron_c >= 1:
    marks.append('💎鉄')
  if r_high_c >= 1:
    marks.append('🌟高')
  if (r_horses['flag_fup6_sf_any'] == True).any():
    marks.append('🔥頭')
  if (r_horses['is_sss_level'] == True).any():
    marks.append('👑神')
  if (r_horses['is_syn_f1_rap'] == True).any():
    marks.append('⚡極')
  if r_bomb_c >= 1:
    marks.append('💣穴')
  if (r_horses['is_danger_jockey'] == True).any():
    marks.append('⚠️危')

  lbl = (
      f"{tag} {r_row['R番号']}R ({r_row['track']}{r_row['dist']}m)"
      f" [{' '.join(marks)}]"
  )
  race_options[r_row['race_uid']] = lbl

selected_race_uid = st.selectbox(
    'レース選択',
    options=list(race_options.keys()),
    format_func=lambda x: race_options[x],
    label_visibility='collapsed',
)

race_df = df[df['race_uid'] == selected_race_uid].copy()
filtered_df = race_df.copy()
is_turf_race = (
    bool(filtered_df['track'].str.contains('芝').any())
    if not filtered_df.empty
    else False
)
track_dist = filtered_df['dist'].values[0] if not filtered_df.empty else ''

# クッション値バッジ計算
race_df['cushion_badge_raw'] = race_df.apply(
    lambda r: (
        evaluate_sire_cushion(
            r['種牡馬'], r['競馬場名'], r['dist'], current_band
        )
        if is_turf_race
        else ''
    ),
    axis=1,
)
race_df['is_cushion_fit'] = race_df['cushion_badge_raw'].str.contains('特注')
race_df['is_cushion_danger'] = race_df['cushion_badge_raw'].str.contains('危険')

# ==============================================================================
# ★ レース判定 ＆ 【単勝】【馬連・ワイド】【3連単】完全馬券構成
# ==============================================================================
r_high_cnt = int((race_df['is_syn_high'] == True).sum())
r_iron_cnt = int((race_df['is_syn_iron'] == True).sum())
r_win_cnt = int((race_df['target_win'] == True).sum())
r_axis_cnt = int((race_df['target_axis'] == True).sum())
r_bomb_cnt = int((race_df['is_syn_bomb'] == True).sum())

fav3_cur = race_df[race_df['人気'] <= 3]
danger_in_fav3 = (
    bool((fav3_cur['is_danger_jockey'] == True).any())
    if not fav3_cur.empty
    else False
)

f1_cur = race_df[race_df['F_rank'] == 1]
f1_val_cur = float(f1_cur['F指数'].values[0]) if not f1_cur.empty else 0.0
is_f1_ok = f1_val_cur >= 60

is_solid = (
    r_high_cnt >= 2
    or (r_win_cnt >= 1 and r_axis_cnt >= 1 and r_bomb_cnt <= 1)
    or ((r_iron_cnt >= 1 or r_high_cnt >= 1 or r_win_cnt >= 1) and r_bomb_c <= 1)
)
is_go = is_solid and (not danger_in_fav3) and is_f1_ok

# 1〜3番人気アンカーの抽出と除外馬整理
top3_fav_horses = race_df[race_df['人気'].isin([1, 2, 3])]['馬番'].tolist()
solid_top3 = []
dummy_horses = []

for h in top3_fav_horses:
  row_h = race_df[race_df['馬番'] == h].iloc[0]
  if (
      row_h.get('is_fup_trap', False)
      or row_h.get('is_cushion_danger', False)
      or row_h.get('is_danger_jockey', False)
  ):
    dummy_horses.append(h)
  else:
    solid_top3.append(h)

if not solid_top3 and top3_fav_horses:
  fallback_top = (
      race_df[race_df['馬番'].isin(top3_fav_horses)]
      .sort_values('F指数', ascending=False)
      .iloc[0]['馬番']
  )
  solid_top3 = [fallback_top]

# 救済された危険騎手
rescued_horses = race_df[race_df['is_danger_rescued']]['馬番'].tolist()

if is_go:
  # --------------------------------------------------------------------------
  # 🎯 【狙】勝負厳選レース
  # --------------------------------------------------------------------------
  banner_cls = 'race-type-solid' if r_bomb_cnt <= 1 else 'race-type-twin-axis'
  banner_title = '🎯 【狙】勝負厳選レース（3大条件クリア・軸堅調）'
  dec_badge = "<span class='badge-decision-go'>⭕ 勝負厳選</span>"
  panel_cls = 'recom-panel-go'
  title_cls = 'recom-title-go'
  pts_cls = 'recom-pts'

  # 1列目（軸）
  c1_cands = race_df[
      race_df['is_sss_level']
      | race_df['is_syn_iron']
      | race_df['is_syn_f1_rap']
      | race_df['is_syn_high']
      | race_df['flag_fup6_sf_any']
      | race_df['target_win']
  ].sort_values('F_rank')['馬番'].tolist()

  if len(c1_cands) < 2:
    for u in race_df.sort_values('F_rank')['馬番'].tolist():
      if (
          u not in c1_cands
          and u not in race_df[race_df['is_fup_trap']]['馬番'].tolist()
      ):
        c1_cands.append(u)
      if len(c1_cands) >= 2:
        break
  rec_c1 = c1_cands[:2]

  # 2列目（相手）
  rec_c2 = list(rec_c1)
  for u in race_df[
      race_df['target_axis']
      | (race_df['arms_rank'] <= 3)
      | (race_df['tua_rank'] <= 3)
      | (race_df['is_cushion_fit'] & (race_df['F_rank'] <= 4))
      | race_df['is_danger_rescued']
  ].sort_values('F_rank')['馬番'].tolist():
    if (
        u not in rec_c2
        and u not in race_df[race_df['is_fup_trap']]['馬番'].tolist()
    ):
      rec_c2.append(u)
    if len(rec_c2) >= 5:
      break

  # 3列目（ヒモ広め）
  rec_c3 = list(rec_c2)
  for u in race_df[
      race_df['flag_sf7_himo']
      | race_df['syn_same_ub_f6']
      | race_df['syn_same_ub_s6']
      | race_df['is_syn_bomb']
      | race_df['坂路_完全加速']
  ].sort_values('F_rank')['馬番'].tolist():
    if u not in rec_c3:
      rec_c3.append(u)
    if len(rec_c3) >= 8:
      break

  # 【単勝】
  single_bets = [str(int(rec_c1[0]))]

  # 【馬連・ワイド】
  main_axis = rec_c1[0]
  umaren_targets = [str(int(u)) for u in rec_c2 if u != main_axis][:3]
  umaren_str = f"{int(main_axis)} - {', '.join(umaren_targets)}"
  wide_targets = [str(int(u)) for u in rec_c2 if u != main_axis][:2]
  wide_str = f"{int(main_axis)} - {', '.join(wide_targets)}"

  # 【3連単】（1〜3人気アンカー制約適用）
  raw_trifecta = [
      (h1, h2, h3)
      for h1 in rec_c1
      for h2 in rec_c2
      for h3 in rec_c3
      if len({h1, h2, h3}) == 3 and any(fav in top3_fav_horses for fav in (h1, h2, h3))
  ]
  trifecta_pts = len(raw_trifecta)

  c1_str = ', '.join(str(int(u)) for u in rec_c1)
  c2_str = ', '.join(str(int(u)) for u in rec_c2)
  c3_str = ', '.join(str(int(u)) for u in rec_c3)

  st.markdown(
      f"<div class='race-type-banner {banner_cls}'>"
      f'<div><strong>{banner_title}</strong> {dec_badge}</div>'
      f'<div>高確率軸: {r_high_cnt}頭 / 連対候補: {r_axis_cnt}頭 / 潜伏爆弾:'
      f' {r_bomb_cnt}頭</div>'
      '</div>',
      unsafe_allow_html=True,
  )

  st.markdown(
      f"<div class='{panel_cls}'>"
      f"<div class='{title_cls}'>🎯 【狙：本線推奨】プロの推奨買い目（単勝 /"
      ' 馬連・ワイド / 3連単）</div>'
      f"<div class='recom-block'><span class='recom-label'>🥇"
      f" 【単勝】</span>&nbsp;&nbsp;<span class='recom-val-num'>{', '.join(single_bets)}</span>"
      f" <span class='{pts_cls}'>計 {len(single_bets)}点</span></div>"
      f"<div class='recom-block'><span class='recom-label'>⚔️"
      f" 【馬連】</span>&nbsp;&nbsp;本線流し: <span"
      f" class='recom-val-num'>{umaren_str}</span> <span class='{pts_cls}'>計"
      f' {len(umaren_targets)}点</span><br>'
      f"<span class='recom-label' style='margin-top:6px;'>🛡️"
      f" 【ワイド】</span>&nbsp;&nbsp;資金回収流し: <span"
      f" class='recom-val-num'>{wide_str}</span> <span class='{pts_cls}'>計"
      f' {len(wide_targets)}点</span></div>'
      f"<div class='recom-block'><span class='recom-label'>🎫"
      f" 【3連単フォーメーション】</span> <span class='{pts_cls}'>計"
      f' {trifecta_pts}点</span><br>'
      "&nbsp;&nbsp;&nbsp;&nbsp;<strong>1着(軸)</strong>: <span class='recom-val-num'>"
      f"{c1_str}</span>&nbsp;&nbsp;→&nbsp;&nbsp;<strong>2着(相手)</strong>: <span"
      f" class='recom-val-num'>{c2_str}</span>&nbsp;&nbsp;→&nbsp;&nbsp;<strong>3着(ヒモ)</strong>:"
      f" <span class='recom-val-num'>{c3_str}</span></div>"
      '</div>',
      unsafe_allow_html=True,
  )

else:
  # --------------------------------------------------------------------------
  # 🔥 【荒】波乱特化レース（上位人気アンカー×爆弾穴馬 ハイブリッドモデル）
  # --------------------------------------------------------------------------
  reasons = []
  if not is_solid:
    reasons.append('混戦・軸不在')
  if danger_in_fav3:
    reasons.append('上位人気に危険騎手')
  if not is_f1_ok:
    reasons.append(f'F1位能力不足({f1_val_cur:.0f}点)')

  banner_cls = 'race-type-chaos'
  banner_title = '🔥 【荒】波乱特化レース（上位崩壊警戒・高配当照準）'
  dec_badge = (
      f"<span class='badge-decision-skip'>⚡ 波乱警報 ({', '.join(reasons)})</span>"
  )
  panel_cls = 'recom-panel-chaos'
  title_cls = 'recom-title-chaos'
  pts_cls = 'recom-pts-chaos'

  # 1着狙い・頭特化穴馬
  head_explosive = race_df[
      race_df['flag_fup6_sf_any']
      | race_df['is_syn_f1_rap']
      | (race_df['target_win'] & (race_df['人気'] >= 4))
  ]['馬番'].tolist()

  # 爆弾穴馬プール
  bomb_pool = race_df[
      race_df['is_syn_bomb']
      | race_df['syn_jk_ub_bomb']
      | race_df['target_himo']
      | (race_df['調教加速'] & (race_df['人気'] >= 5))
  ]['馬番'].tolist()

  # 1列目（頭特化穴馬 ＋ 信頼できる上位人気アンカー）
  col1_cands = list(dict.fromkeys(head_explosive[:2] + solid_top3[:2]))
  if not col1_cands:
    col1_cands = (
        bomb_pool[:1]
        + race_df.sort_values('F_rank').head(2)['馬番'].tolist()
    )
  rec_c1 = [h for h in col1_cands if h not in dummy_horses][:3]

  # 2列目（1列目 ＋ 指数上位 ＋ 爆弾穴馬 ＋ 救済騎手馬）
  rec_c2 = list(rec_c1)
  for u in (
      race_df[
          (~race_df['is_danger_jockey'])
          & (~race_df['is_fup_trap'])
          & (
              (race_df['arms_rank'] <= 3)
              | (race_df['tua_rank'] <= 3)
              | (race_df['F_rank'] <= 4)
              | race_df['is_danger_rescued']
          )
      ]
      .sort_values('arms_rank')['馬番']
      .tolist()
      + bomb_pool[:3]
  ):
    if u not in rec_c2 and u not in dummy_horses:
      rec_c2.append(u)
    if len(rec_c2) >= 6:
      break

  # 3列目（2列目 ＋ SF7穴ヒモ ＋ 調教加速全馬）
  rec_c3 = list(rec_c2)
  for u in (
      race_df[
          race_df['flag_sf7_himo']
          | (race_df['F_rank'] <= 6)
          | (race_df['S_rank'] <= 6)
          | race_df['調教加速']
      ]
      .sort_values('F_rank')['馬番']
      .tolist()
      + bomb_pool
  ):
    if u not in rec_c3:
      rec_c3.append(u)
    if len(rec_c3) >= 8:
      break

  # 【単勝】
  single_bets = [str(int(u)) for u in rec_c1[:2]]

  # 【馬連・ワイド】
  anchor_horse = (
      solid_top3[0]
      if solid_top3
      else (rec_c1[0] if rec_c1 else race_df.iloc[0]['馬番'])
  )
  umaren_targets = [
      str(int(u))
      for u in (bomb_pool + rescued_horses + rec_c2)
      if u != anchor_horse
  ][:3]
  umaren_str = f"{int(anchor_horse)} - {', '.join(umaren_targets)}"

  wide_targets = [
      str(int(u))
      for u in (
          bomb_pool
          + race_df[race_df['flag_sf7_himo']]['馬番'].tolist()
          + rescued_horses
      )
      if u != anchor_horse
  ][:3]
  if not wide_targets:
    wide_targets = [str(int(u)) for u in rec_c2 if u != anchor_horse][:3]
  wide_str = f"{int(anchor_horse)} - {', '.join(wide_targets)}"

  # 【3連単】（1〜3人気アンカー制約適用）
  raw_trifecta = [
      (h1, h2, h3)
      for h1 in rec_c1
      for h2 in rec_c2
      for h3 in rec_c3
      if len({h1, h2, h3}) == 3 and any(fav in top3_fav_horses for fav in (h1, h2, h3))
  ]
  trifecta_pts = len(raw_trifecta)

  c1_str = ', '.join(str(int(u)) for u in rec_c1)
  c2_str = ', '.join(str(int(u)) for u in rec_c2)
  c3_str = ', '.join(str(int(u)) for u in rec_c3)

  st.markdown(
      f"<div class='race-type-banner {banner_cls}'>"
      f'<div><strong>{banner_title}</strong> {dec_badge}</div>'
      f'<div>潜伏爆弾: {r_bomb_cnt}頭 / 危険騎手該当: {int(danger_in_fav3)}件 /'
      f' 救済馬: {len(rescued_horses)}頭</div>'
      '</div>',
      unsafe_allow_html=True,
  )

  st.markdown(
      f"<div class='{panel_cls}'>"
      f"<div class='{title_cls}'>💣 【荒：高配当特化】プロの推奨買い目（単勝 /"
      ' 馬連・ワイド / 3連単）</div>'
      f"<div class='recom-block'><span class='recom-label'>🥇"
      f" 【単勝（波乱アタマ狙い）】</span>&nbsp;&nbsp;<span"
      f" class='recom-val-num'>{', '.join(single_bets)}</span> <span"
      f" class='{pts_cls}'>計 {len(single_bets)}点</span></div>"
      f"<div class='recom-block'><span class='recom-label'>⚔️"
      f" 【馬連（人気×激走穴馬）】</span>&nbsp;&nbsp;流し: <span"
      f" class='recom-val-num'>{umaren_str}</span> <span class='{pts_cls}'>計"
      f' {len(umaren_targets)}点</span><br>'
      f"<span class='recom-label' style='margin-top:6px;'>💥"
      f" 【ワイド（一撃高回収）】</span>&nbsp;&nbsp;アンカー流し: <span"
      f" class='recom-val-num'>{wide_str}</span> <span class='{pts_cls}'>計"
      f' {len(wide_targets)}点</span></div>'
      f"<div class='recom-block'><span class='recom-label'>🎫"
      f" 【3連単(人気×穴ハイブリッド)】</span> <span class='{pts_cls}'>計"
      f' {trifecta_pts}点</span><br>'
      "&nbsp;&nbsp;&nbsp;&nbsp;<strong>1着(軸候補)</strong>: <span class='recom-val-num'>"
      f"{c1_str}</span>&nbsp;&nbsp;→&nbsp;&nbsp;<strong>2着(相手)</strong>: <span"
      f" class='recom-val-num'>{c2_str}</span>&nbsp;&nbsp;→&nbsp;&nbsp;<strong>3着(ヒモ)</strong>:"
      f" <span class='recom-val-num'>{c3_str}</span></div>"
      '</div>',
      unsafe_allow_html=True,
  )

# ==============================================================================
# ★ 出走馬カード表示 ＆ フィルター適用
# ==============================================================================
filtered_df['cushion_badge'] = race_df['cushion_badge_raw']

if syn_iron:
  filtered_df = filtered_df[filtered_df['is_syn_iron']]
if syn_high:
  filtered_df = filtered_df[filtered_df['is_syn_high']]
if syn_fup_sakaro:
  filtered_df = filtered_df[filtered_df['is_syn_fup_sakaro']]
if syn_f1_rap:
  filtered_df = filtered_df[filtered_df['is_syn_f1_rap']]
if syn_bomb:
  filtered_df = filtered_df[filtered_df['is_syn_bomb']]
if filter_fup6_sf:
  filtered_df = filtered_df[filtered_df['flag_fup6_sf_any']]
if filter_target_win:
  filtered_df = filtered_df[filtered_df['target_win']]
if filter_target_axis:
  filtered_df = filtered_df[filtered_df['target_axis']]
if filter_sf7_himo:
  filtered_df = filtered_df[filtered_df['flag_sf7_himo']]
if filter_target_himo:
  filtered_df = filtered_df[filtered_df['target_himo']]
if filter_danger_jockey:
  filtered_df = filtered_df[filtered_df['is_danger_jockey']]
if filter_fup_trap:
  filtered_df = filtered_df[filtered_df['is_fup_trap']]

col_s1, col_s2 = st.columns([2.5, 1.5])
with col_s1:
  kw = st.text_input(
      '🔍 馬名・騎手・調教師・父名で検索',
      placeholder='検索ワードを入力...',
      label_visibility='collapsed',
  )
  if kw:
    filtered_df = filtered_df[
        filtered_df['馬名'].str.contains(kw, na=False)
        | filtered_df['騎手'].str.contains(kw, na=False)
        | filtered_df['調教師'].str.contains(kw, na=False)
        | filtered_df['種牡馬'].str.contains(kw, na=False)
    ]
with col_s2:
  sort_opt = st.selectbox(
      '並び順',
      [
          '単勝人気順 (1人気→)',
          '🚀 調教加速順 (W加速幅・坂路完全)',
          '馬番順',
          '🔥 F指数 順位 (1位→)',
          '🚀 arms指数 順位 (1位→)',
          '⚡ S指数 順位 (1位→)',
          '🛡️ tua指数 順位 (1位→)',
          '✨ Fup 順位 (1位→)',
      ],
      index=0,
      label_visibility='collapsed',
  )

if sort_opt == '単勝人気順 (1人気→)':
  filtered_df = filtered_df.sort_values(['人気', '馬番'])
elif sort_opt == '🚀 調教加速順 (W加速幅・坂路完全)':
  filtered_df['sort_accel_score'] = filtered_df['wood_accel'].fillna(
      -99.0
  ) + (filtered_df['坂路_完全加速'].astype(int) * 2.0)
  filtered_df = filtered_df.sort_values(
      ['sort_accel_score', '人気'], ascending=[False, True]
  )
elif sort_opt == '🔥 F指数 順位 (1位→)':
  filtered_df = filtered_df.sort_values(['F_rank', '馬番'])
elif sort_opt == '🚀 arms指数 順位 (1位→)':
  filtered_df = filtered_df.sort_values(['arms_rank', '馬番'])
elif sort_opt == '⚡ S指数 順位 (1位→)':
  filtered_df = filtered_df.sort_values(['S_rank', '馬番'])
elif sort_opt == '🛡️ tua指数 順位 (1位→)':
  filtered_df = filtered_df.sort_values(['tua_rank', '馬番'])
elif sort_opt == '✨ Fup 順位 (1位→)':
  filtered_df = filtered_df.sort_values(['Fup_rank', '馬番'])
else:
  filtered_df = filtered_df.sort_values('馬番')

st.markdown(f'**出走馬一覧（該当: {len(filtered_df)}頭）**')

for _, row in filtered_df.iterrows():
  badges = []
  if row.get('is_sss_level'):
    badges.append(
        "<span class='badge-synergy' style='background:#f59e0b;color:#000;'>👑"
        ' SSS級・絶対神域</span>'
    )
  if row.get('is_four_crown'):
    badges.append(
        "<span class='badge-synergy' style='background:#10b981;color:#fff;'>👑"
        ' 指数の四冠馬</span>'
    )
  if row.get('is_fup_trap'):
    badges.append("<span class='badge-danger-jockey'>⚠️ Fup1の罠(ダミー消去)</span>")
  if row.get('is_fup_kakugen'):
    badges.append("<span class='badge-fup6-sf'>✨ Fup7確変馬</span>")

  # 危険騎手＆救済バッジ
  if row.get('is_danger_jockey'):
    badges.append("<span class='badge-danger-jockey'>⚠️ 危険騎手【危】</span>")
  elif row.get('is_danger_rescued'):
    badges.append(
        "<span class='badge-danger-rescued'>🛡️ 危険騎手救済(複数狙い目一致)</span>"
    )

  # 陣営コンビバイアス
  if row.get('camp_bias') == 'camp_nakauchida_kawada':
    badges.append(
        "<span class='badge-jk-ub'>👑 中内田×川田×F1位 (勝率50%)</span>"
    )
  elif row.get('camp_bias') == 'camp_kimura_lemaire_ok':
    badges.append("<span class='badge-jk-ub'>👑 木村哲×ルメール (勝率35.4%)</span>")
  elif row.get('camp_bias') == 'camp_kimura_lemaire_ng':
    badges.append(
        "<span class='badge-danger-jockey'>⚠️ 木村哲×ルメールFup不足"
        ' (勝率10%)</span>'
    )
  elif row.get('camp_bias') == 'camp_saito_nakadate':
    badges.append("<span class='badge-tr-ub'>🚀 特注厩舎×F1位 (勝率40%)</span>")

  # 指数・シナジーバッジ
  if row.get('flag_fup6_s6'):
    badges.append(
        "<span class='badge-fup6-sf'>🔥 Fup6+×S6 (勝率25%/回収200%)</span>"
    )
  elif row.get('flag_fup6_f6'):
    badges.append("<span class='badge-fup6-sf'>🔥 Fup6+×F6 (勝率25%)</span>")

  if row.get('target_win'):
    badges.append("<span class='badge-target-win'>🥇 1着狙い (勝率26%超)</span>")
  elif row.get('target_axis'):
    badges.append(
        "<span class='badge-target-axis'>🛡️ 軸・連対狙い (複勝率55%超)</span>"
    )
  if row.get('is_syn_iron'):
    badges.append(
        "<span class='badge-synergy badge-iron'>💎 鉄板軸馬 (複勝61.9%)</span>"
    )
  elif row.get('is_syn_high'):
    badges.append(
        "<span class='badge-synergy badge-high'>🔥 高確率軸 (複勝55%超)</span>"
    )
  if row.get('is_syn_fup_sakaro'):
    badges.append(
        "<span class='badge-synergy badge-sakaro-fup'>✨ Fup坂路完全</span>"
    )
  if row.get('is_syn_f1_rap'):
    badges.append(
        "<span class='badge-synergy badge-f1-rap'>🔥 SSS級・F1位×究極ラップ</span>"
    )

  # 同馬番バッジ
  if row.get('syn_jk_ub_wood'):
    badges.append("<span class='badge-jk-ub'>👑 騎手同馬番×W加速×F上位</span>")
  elif row.get('is_same_ub_jk'):
    badges.append(
        f"<span class='badge-jk-ub'>🏇 騎手同馬番{row['same_ub_jk_count']}回目"
        f" ({row['same_ub_jk_races']})</span>"
    )

  if row.get('syn_tr_ub_arms'):
    badges.append(
        "<span class='badge-tr-ub'>🚀 厩舎同馬番×arms上位 (複勝70%)</span>"
    )
  elif row.get('is_same_ub_tr'):
    badges.append(
        f"<span class='badge-tr-ub'>🏛️ 厩舎同馬番{row['same_ub_tr_count']}回目"
        f" ({row['same_ub_tr_races']})</span>"
    )

  if row.get('syn_same_ub_fs6'):
    badges.append(
        "<span class='badge-same-ub-fs6'>👑 同馬番×FS6 (複勝42%)</span>"
    )
  elif row.get('syn_same_ub_f6'):
    badges.append(
        "<span class='badge-same-ub-f6'>🎯 同馬番×F6 (複勝38%)</span>"
    )
  elif row.get('syn_same_ub_s6'):
    badges.append("<span class='badge-same-ub-s6'>⚡ 同馬番×S6 (先行連対)</span>")

  if row.get('flag_sf7_himo'):
    badges.append("<span class='badge-sf7-himo'>🌪️ SF7×加速/同枠</span>")

  if row.get('is_syn_bomb') or row.get('syn_jk_ub_bomb'):
    badges.append("<span class='badge-synergy badge-bomb'>💣 爆弾穴馬</span>")

  if row.get('cushion_badge'):
    badges.append(row['cushion_badge'])

  u_no = int(row['馬番']) if pd.notnull(row['馬番']) else 99
  pop_str = f"{int(row['人気'])}人気" if pd.notnull(row['人気']) else '-人気'
  sire_display = row.get('種牡馬') if row.get('種牡馬') else '-'

  # 指数バッジ
  f_badge = (
      "<span class='rank-1st'>🥇1位</span>"
      if row['F_rank'] == 1
      else f"{int(row['F_rank'])}位"
  )
  arms_badge = (
      "<span class='rank-1st'>🥇1位</span>"
      if row['arms_rank'] == 1
      else f"{int(row['arms_rank'])}位"
  )
  s_badge = (
      "<span class='rank-1st'>🥇1位</span>"
      if row['S_rank'] == 1
      else f"{int(row['S_rank'])}位"
  )
  tua_badge = (
      "<span class='rank-1st'>🥇1位</span>"
      if row['tua_rank'] == 1
      else f"{int(row['tua_rank'])}位"
  )
  fup_badge = (
      "<span class='rank-1st'>🥇1位</span>"
      if row['Fup_rank'] == 1
      else f"{int(row['Fup_rank'])}位"
  )

  f_val_num = float(row.get('F指数', 0.0))
  if f_val_num >= 72.0:
    f_val_html = f"<span class='val-f-super'>{f_val_num:.0f}</span>"
  elif f_val_num >= 66.0:
    f_val_html = f"<span class='val-f-high'>{f_val_num:.0f}</span>"
  elif f_val_num >= 50.0:
    f_val_html = f'<strong>{f_val_num:.0f}</strong>'
  else:
    f_val_html = f'{f_val_num:.0f}'

  arms_val_num = float(row.get('arms', 0.0))
  if arms_val_num >= 120.0:
    arms_val_html = f"<span class='val-arms-super'>{arms_val_num:.0f}</span>"
  elif arms_val_num >= 100.0:
    arms_val_html = f'<strong>{arms_val_num:.0f}</strong>'
  else:
    arms_val_html = f'{arms_val_num:.0f}'

  tua_val_num = float(row.get('tua', 0.0))
  if tua_val_num >= 190.0:
    tua_val_html = f"<span class='val-tua-super'>{tua_val_num:.0f}</span>"
  else:
    tua_val_html = f'{tua_val_num:.0f}'

  s_val_num = float(row.get('S指数', 0.0))
  if s_val_num >= 30.0:
    s_val_html = f"<span class='val-s-super'>{s_val_num:.0f}</span>"
  else:
    s_val_html = f'{s_val_num:.0f}'

  fup_val_num = int(row.get('Fup', 0))
  if fup_val_num >= 5:
    fup_val_html = f"<span class='val-f-super'>{fup_val_num}点</span>"
  elif fup_val_num == 4:
    fup_val_html = f"<strong style='color:#f97316;'>{fup_val_num}点</strong>"
  else:
    fup_val_html = f'{fup_val_num}点'

  # 調教テキストの生成
  if pd.notnull(row.get('wood_1F')):
    w_5f_txt = (
        f"{row['wood_5F']:.1f}s " if pd.notnull(row.get('wood_5F')) else ''
    )
    if row.get('is_wood_accel'):
      w_acc_badge = (
          f"<span class='badge-accel-on'>加速 +{row['wood_accel']:.1f}s</span>"
      )
    elif pd.notnull(row.get('wood_accel')):
      w_acc_badge = (
          f"<span class='badge-accel-off'>減速 {row['wood_accel']:.1f}s</span>"
      )
    else:
      w_acc_badge = ''
    w_str = f"W: {w_5f_txt}1F {row['wood_1F']:.1f}s {w_acc_badge}".strip()
  else:
    w_str = 'W: 計測無'

  if pd.notnull(row.get('坂路_4F')):
    if row.get('坂路_完全加速'):
      s_acc_badge = "<span class='badge-accel-on'>実質完全加速</span>"
    else:
      s_acc_badge = "<span class='badge-accel-off'>非完全加速</span>"
    s_str = (
        f"坂路: 4F {row['坂路_4F']:.1f}s (1F {row['坂路_1F']:.1f}s) {s_acc_badge}"
    )
  else:
    s_str = '坂路: 計測無'

  st.markdown(
      f"<div class='horse-card'>"
      f"<div class='horse-card-header'><span class='horse-card-title'>{u_no}番"
      f" {row['馬名']} ({pop_str})</span> {' '.join(badges)}</div>"
      "<ul class='horse-card-list'>"
      f"<li><strong>騎手/厩舎</strong>: {row.get('騎手')} / {row.get('調教師')} /"
      f" <strong>父: {sire_display}</strong></li>"
      f'<li><strong>調教ラップ</strong>: <strong>{w_str}</strong> |'
      f' <strong>{s_str}</strong></li>'
      f'<li><strong>能力指数</strong>: F: {f_val_html} ({f_badge}) | ARMS:'
      f' {arms_val_html} ({arms_badge}) | S: {s_val_html} ({s_badge}) | TUA:'
      f' {tua_val_html} ({tua_badge}) | Fup: {fup_val_html} ({fup_badge})</li>'
      '</ul></div>',
      unsafe_allow_html=True,
  )
