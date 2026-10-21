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
# 競馬予想10 クッション値Vr - 完全統合Webアプリケーション
# 黄金マスター仕様準拠版（全38列マスター＆クッション値データブック完全連動）
# ==============================================================================

st.set_page_config(
    page_title='競馬予想10 クッション値Vr - 完全統合システム',
    layout='wide',
    initial_sidebar_state='expanded',
)

# ------------------------------------------------------------------------------
# 黄金マスター CSS スタイル定義（スマホ操作最適化・バッジ縦潰れ防止）
# ------------------------------------------------------------------------------
st.markdown(
    """
<style>
    /* スマホ操作最適化：セレクトボックス選択時にソフトウェアキーボードが立ち上がるのを完全防止 */
    div[data-baseweb="select"] input {
        inputmode: none !important;
        pointer-events: none !important;
    }
    
    .metric-container {
        display: flex;
        justify-content: space-around;
        background-color: #161b22;
        padding: 14px;
        border-radius: 10px;
        margin-bottom: 18px;
        border: 1px solid #30363d;
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
    
    /* レース判定バナー */
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
    .race-type-bonus {
        background: linear-gradient(135deg, #7c2d12 0%, #b45309 50%, #d97706 100%);
        color: #fef3c7;
        border: 2px solid #fde68a;
        box-shadow: 0 0 10px rgba(245, 158, 11, 0.5);
    }
    .race-type-hit {
        background: linear-gradient(135deg, #064e3b 0%, #047857 100%);
        color: #d1fae5;
        border: 2px solid #6ee7b7;
    }
    .race-type-recovery {
        background: linear-gradient(135deg, #4c1d95 0%, #6d28d9 100%);
        color: #ede9fe;
        border: 2px solid #c4b5fd;
    }
    .race-type-normal {
        background: #1f2937;
        color: #e5e7eb;
        border: 1px solid #4b5563;
    }
    
    /* 推奨馬パネル ＆ 馬券パックパネル */
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
    
    /* 出走馬カルテ */
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
    
    /* バッジ縦潰れ防止・可変パディング */
    .badge-mark-honmei {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
        color: #ffffff;
        font-size: 12.5px;
        font-weight: 900;
        padding: 2px 8px;
        border-radius: 4px;
        border: 1px solid #fca5a5;
        margin-right: 6px;
    }
    .badge-mark-taikou {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: #ffffff;
        font-size: 12.5px;
        font-weight: 900;
        padding: 2px 8px;
        border-radius: 4px;
        border: 1px solid #93c5fd;
        margin-right: 6px;
    }
    .badge-mark-ana {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
        color: #ffffff;
        font-size: 12.5px;
        font-weight: 900;
        padding: 2px 8px;
        border-radius: 4px;
        border: 1px solid #fde68a;
        margin-right: 6px;
    }
    .badge-mark-gtv {
        display: inline-flex;
        align-items: center;
        background-color: #374151;
        color: #fbbf24;
        font-weight: bold;
        font-size: 12px;
        padding: 2px 6px;
        border-radius: 4px;
        border: 1px solid #d97706;
    }
    .badge-cushion-fit {
        display: inline-flex;
        align-items: center;
        background-color: #064e3b;
        color: #6ee7b7;
        font-weight: bold;
        font-size: 12px;
        padding: 2px 8px;
        border-radius: 4px;
        border: 1px solid #10b981;
    }
    .badge-cushion-danger {
        display: inline-flex;
        align-items: center;
        background-color: #7f1d1d;
        color: #fca5a5;
        font-weight: bold;
        font-size: 12px;
        padding: 2px 8px;
        border-radius: 4px;
        border: 1px solid #ef4444;
    }
    .badge-accel-on {
        display: inline-flex;
        align-items: center;
        background-color: #1e3a8a;
        color: #93c5fd;
        font-weight: bold;
        font-size: 12px;
        padding: 2px 8px;
        border-radius: 4px;
        border: 1px solid #3b82f6;
    }
    .badge-rescued {
        display: inline-flex;
        align-items: center;
        background-color: #581c87;
        color: #f0abfc;
        font-weight: bold;
        font-size: 12px;
        padding: 2px 8px;
        border-radius: 4px;
        border: 1px solid #c084fc;
    }
    
    /* 指数カラーハイライト */
    .val-rank1-gold { color: #1a1000; background-color: #fcd34d; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #f59e0b; }
    .val-f-top { color: #ffffff; background-color: #ea580c; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #fb923c; }
    .val-s-top { color: #ffffff; background-color: #8b5cf6; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #c4b5fd; }
    .val-arms-top { color: #083344; background-color: #38bdf8; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #0284c7; }
    .val-tua-top { color: #022c22; background-color: #34d399; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #059669; }
</style>
""",
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------------------
# クッション値データブック（2020-2026）完全連動マトリクス
# ------------------------------------------------------------------------------
# 5区分判定関数
def get_cushion_category(cushion_val, venue_name):
  c_val = float(cushion_val)
  # 札幌・函館の場内相対区分
  if venue_name == '札幌':
    if c_val <= 7.3:
      return '場内低<=7.3'
    elif c_val >= 7.7:
      return '場内高>=7.7'
    else:
      return '場内中7.4-7.6'
  elif venue_name == '函館':
    if c_val <= 7.2:
      return '場内低<=7.2'
    elif c_val >= 7.5:
      return '場内高>=7.5'
    else:
      return '場内中7.3-7.4'

  # 全国5区分
  if c_val <= 8.5:
    return '<=8.5低'
  elif c_val <= 9.4:
    return '8.6-9.4 やや低'
  elif c_val <= 9.9:
    return '9.5-9.9 標準高'
  elif c_val <= 10.4:
    return '10.0-10.4高'
  else:
    return '>=10.5 超高'


# 最重要・狙い目＆危険マトリクス（データブック上位20抜粋）
CUSHION_DATA_BOOK = {
    (
        '阪神',
        '芝',
        1800,
        'キズナ',
        '9.5-9.9 標準高',
    ): (
        '最重要',
        'N56 勝19.6% 複41.1% 単421 複172',
    ),
    (
        '東京',
        '芝',
        1600,
        'エピファネイア',
        '9.5-9.9 標準高',
    ): (
        '最重要',
        'N98 勝13.3% 複39.8% 単277 複111',
    ),
    (
        '東京',
        '芝',
        1400,
        'モーリス',
        '9.5-9.9 標準高',
    ): (
        '最重要',
        'N69 勝10.1% 複29.0% 単408 複160',
    ),
    (
        '東京',
        '芝',
        1800,
        'ディープインパクト',
        '9.5-9.9 標準高',
    ): (
        '最重要',
        'N57 勝15.8% 複38.6% 単228 複156',
    ),
    (
        '東京',
        '芝',
        2000,
        'キズナ',
        '8.6-9.4 やや低',
    ): (
        '最重要',
        'N66 勝19.7% 複42.4% 単200 複121',
    ),
    (
        '中京',
        '芝',
        2000,
        'ディープインパクト',
        '8.6-9.4 やや低',
    ): (
        '最重要',
        'N61 勝18.0% 複42.6% 単178 複92',
    ),
    (
        '東京',
        '芝',
        1600,
        'イスラボニータ',
        '8.6-9.4 やや低',
    ): (
        '最重要',
        'N76 勝10.5% 複30.3% 単350 複120',
    ),
    (
        '東京',
        '芝',
        2000,
        'エピファネイア',
        '8.6-9.4 やや低',
    ): (
        '最重要',
        'N85 勝15.3% 複42.4% 単149 複84',
    ),
    (
        '函館',
        '芝',
        1800,
        'キズナ',
        '<=8.5低',
    ): (
        '最重要',
        'N62 勝17.7% 複38.7% 単143 複93',
    ),
    (
        '小倉',
        '芝',
        1200,
        'ダイワメジャー',
        '9.5-9.9 標準高',
    ): (
        '最重要',
        'N66 勝13.6% 複30.3% 単173 複111',
    ),
    (
        '札幌',
        '芝',
        2000,
        'オルフェーヴル',
        '<=8.5低',
    ): (
        '最重要',
        'N57 勝15.8% 複35.1% 単136 複145',
    ),
    (
        '東京',
        '芝',
        1400,
        'ロードカナロア',
        '8.6-9.4 やや低',
    ): (
        '最重要',
        'N154 勝15.6% 複32.5% 単123 複100',
    ),
    (
        '阪神',
        '芝',
        1600,
        'ルーラーシップ',
        '8.6-9.4 やや低',
    ): (
        '最重要',
        'N50 勝20.0% 複30.0% 単156 複89',
    ),
    (
        '東京',
        '芝',
        1600,
        'モーリス',
        '9.5-9.9 標準高',
    ): (
        '最重要',
        'N72 勝11.1% 複37.5% 単100 複122',
    ),
    (
        '阪神',
        '芝',
        2000,
        'キズナ',
        '8.6-9.4 やや低',
    ): (
        '最重要',
        'N85 勝11.8% 複41.2% 単152 複107',
    ),
    (
        '東京',
        '芝',
        1600,
        'スクリーンヒーロー',
        '8.6-9.4 やや低',
    ): (
        '最重要',
        'N71 勝9.9% 複35.2% 単72 複179',
    ),
    (
        '小倉',
        '芝',
        1200,
        'ビッグアーサー',
        '8.6-9.4 やや低',
    ): (
        '最重要',
        'N123 勝12.2% 複30.9% 単131 複101',
    ),
    (
        '中京',
        '芝',
        1600,
        'ロードカナロア',
        '10.0-10.4高',
    ): (
        '最重要',
        'N61 勝14.8% 複32.8% 単133 複79',
    ),
    (
        '福島',
        '芝',
        1200,
        'ビッグアーサー',
        '8.6-9.4 やや低',
    ): (
        '最重要',
        'N121 勝13.2% 複33.1% 単87 複102',
    ),
    (
        '札幌',
        '芝',
        1200,
        'ロードカナロア',
        '<=8.5低',
    ): (
        '最重要',
        'N100 勝15.0% 複33.0% 単121 複71',
    ),
    # 危険側
    (
        '中山',
        '芝',
        2000,
        'ダノンバラード',
        '9.5-9.9 標準高',
    ): (
        '危険',
        'N30 複0.0%',
    ),
    (
        '東京',
        '芝',
        2000,
        'ルーラーシップ',
        '9.5-9.9 標準高',
    ): (
        '危険',
        'N33 複9.1%',
    ),
    (
        '小倉',
        '芝',
        1200,
        'ジャスタウェイ',
        '8.6-9.4 やや低',
    ): (
        '危険',
        'N35 複2.9%',
    ),
    (
        '東京',
        '芝',
        1400,
        'シルバーステート',
        '8.6-9.4 やや低',
    ): (
        '危険',
        'N43 複4.7%',
    ),
    (
        '東京',
        '芝',
        1600,
        'ゴールドシップ',
        '8.6-9.4 やや低',
    ): (
        '危険',
        'N44 複4.5%',
    ),
    (
        '小倉',
        '芝',
        1200,
        'ヴィクトワールピサ',
        '8.6-9.4 やや低',
    ): (
        '危険',
        'N42 複4.8%',
    ),
    (
        '東京',
        '芝',
        1800,
        'ルーラーシップ',
        '9.5-9.9 標準高',
    ): (
        '危険',
        'N38 複10.5%',
    ),
    (
        '阪神',
        '芝',
        2000,
        'ゴールドシップ',
        '8.6-9.4 やや低',
    ): (
        '危険',
        'N40 複10.0%',
    ),
    (
        '東京',
        '芝',
        1600,
        'エイシンフラッシュ',
        '8.6-9.4 やや低',
    ): (
        '危険',
        'N41 複7.3%',
    ),
    (
        '東京',
        '芝',
        2000,
        'オルフェーヴル',
        '8.6-9.4 やや低',
    ): (
        '危険',
        'N38 複13.2%',
    ),
    (
        '福島',
        '芝',
        2000,
        'ルーラーシップ',
        '8.6-9.4 やや低',
    ): (
        '危険',
        'N43 複4.7%',
    ),
    (
        '新潟',
        '芝',
        1400,
        'リオンディーズ',
        '8.6-9.4 やや低',
    ): (
        '危険',
        'N30 複6.7%',
    ),
    (
        '東京',
        '芝',
        2400,
        'ゴールドシップ',
        '9.5-9.9 標準高',
    ): (
        '危険',
        'N36 複11.1%',
    ),
    (
        '小倉',
        '芝',
        1800,
        'ルーラーシップ',
        '9.5-9.9 標準高',
    ): (
        '危険',
        'N30 複10.0%',
    ),
    (
        '阪神',
        '芝',
        1800,
        'ハービンジャー',
        '9.5-9.9 標準高',
    ): (
        '危険',
        'N30 複10.0%',
    ),
    (
        '東京',
        '芝',
        1600,
        'サトノクラウン',
        '8.6-9.4 やや低',
    ): (
        '危険',
        'N31 複9.7%',
    ),
    (
        '福島',
        '芝',
        1200,
        'マツリダゴッホ',
        '8.6-9.4 やや低',
    ): (
        '危険',
        'N34 複5.9%',
    ),
    (
        '東京',
        '芝',
        1600,
        'シルバーステート',
        '9.5-9.9 標準高',
    ): (
        '危険',
        'N45 複8.9%',
    ),
    (
        '福島',
        '芝',
        1200,
        'カレンブラックヒル',
        '8.6-9.4 やや低',
    ): (
        '危険',
        'N31 複9.7%',
    ),
    (
        '中京',
        '芝',
        2000,
        'オルフェーヴル',
        '8.6-9.4 やや低',
    ): (
        '危険',
        'N33 複15.2%',
    ),
}

# 現役最強コース巧者辞書（同コース3戦以上＆複勝率80〜100%）
COURSE_SPECIALIST_DICT = {
    ('カンレイスター', '中山', 'ダ', 1200): '5戦1勝・3着内5回(複100%)',
    ('ルヴァレドクール', '東京', 'ダ', 1600): '4戦3勝・3着内4回(複100%)',
}

# ------------------------------------------------------------------------------
# データ読込＆クリーニング関数
# ------------------------------------------------------------------------------
def clean_str(val):
  if pd.isnull(val):
    return ''
  return (
      str(val)
      .strip()
      .replace('*', '')
      .replace('$', '')
      .replace(' ', '')
      .replace(' ', '')
  )


def read_csv_robust():
  # 最優先で最新統合マスターを検索
  candidates = [
      '当日全指数統合.csv',
      '当日全指数統合10.18.csv',
      'data/当日全指数統合.csv',
      '*全指数統合*.csv',
  ]
  all_found = []
  for c in candidates:
    all_found.extend(glob.glob(c))

  if all_found:
    newest = max(all_found, key=os.path.getmtime)
    for enc in ['utf-8-sig', 'utf-8', 'cp932', 'shift-jis']:
      try:
        df = pd.read_csv(newest, encoding=enc)
        if not df.empty and df.shape[1] >= 30:
          return df, newest
      except Exception:
        continue
  return pd.DataFrame(), ''


# ------------------------------------------------------------------------------
# 坂路調教ラップ判定（厳格な6大区分定義）
# ------------------------------------------------------------------------------
def get_sakaro_profile(lap4, lap3, lap2, lap1, total4f):
  """坂路終い2F（Lap2, Lap1）から厳格な6大区分（A1〜A3, B1〜B3）を判定"""
  try:
    l2 = float(lap2)
    l1 = float(lap1)
    tot = float(total4f)
    if tot > 56.0 or l1 > 13.0:
      return '判定対象外（軽負荷）'

    is_accel = l1 < l2
    is_decel = l1 >= l2

    # A3 / B3
    if is_accel and l1 <= 11.9:
      return 'A3（終い11秒台加速）'
    if is_decel and l2 <= 11.9:
      if tot <= 51.5:
        return 'B3（猛時計例外・勝負仕上）'
      return 'B3（2F目11秒台減速）'

    # A2 / B2
    if is_accel and (12.0 <= l2 <= 12.9) and (12.0 <= l1 <= 12.9):
      return 'A2（2F連続12秒台加速）'
    if is_decel and (12.0 <= l2 <= 12.9) and (12.0 <= l1 <= 12.9):
      if tot <= 51.5:
        return 'B2（猛時計例外・勝負仕上）'
      return 'B2（2F連続12秒台減速）'

    # A1 / B1
    if is_accel and l2 >= 13.0 and (12.0 <= l1 <= 12.9):
      return 'A1（終いのみ12秒台加速）'
    if is_decel and (12.0 <= l2 <= 12.9) and l1 >= 13.0:
      return 'B1（2Fのみ12秒台減速）'

    return '一般ラップ'
  except Exception:
    return '未判定'


# ------------------------------------------------------------------------------
# 23〜38列目加点 ＆ コア指数連動救済ロジック
# ------------------------------------------------------------------------------
def calc_upgraded_dynamic_score(r, venue_name, track_type, dist_val, c_category):
  score = 0.0

  f_val = r.get('F', 0.0)
  f_rk = r.get('F順位', 99)
  fup = r.get('Fup2', 0)
  arm_val = r.get('ARM', 0.0)
  arm_rk = r.get('ARM順位', 99)
  tua_val = r.get('TUA', 0.0)
  tua_rk = r.get('TUA順位', 99)
  s_rk = r.get('S順位', 99)
  pop = r.get('人気順位', 99)
  trainer = r.get('調教師', '')
  sire = r.get('種牡馬', '')
  h_name = r.get('馬名', '')

  hc_rk = r.get('坂路調順位', 99)
  hk_rk = r.get('坂路血順位', 99)
  tk_rk = r.get('時計血順位', 99)
  c_rk = r.get('コース連順位', 99)
  k_rk = r.get('血統連順位', 99)
  b_rk = r.get('バランス順位', 99)

  # コース巧者判定
  is_spec = (h_name, venue_name, track_type, dist_val) in COURSE_SPECIALIST_DICT

  # ① コア指数の基本加点
  if f_rk == 1:
    score += 50.0
  elif f_rk <= 3:
    score += 30.0

  if s_rk <= 3:
    score += 30.0
  if fup == 7:
    score += 45.0
  elif fup >= 5:
    score += 30.0
  elif fup == 4:
    score += 15.0

  # ② 23〜38列目の加点ロジック
  if hc_rk <= 3:
    score += 15.0
  if hk_rk <= 3 or tk_rk <= 3:
    score += 15.0
  if k_rk <= 3:
    score += 15.0
  if c_rk <= 3:
    score += 25.0
  if b_rk <= 3:
    score += 25.0
  if is_spec:
    score += 35.0

  # 回収率特注パターン加点
  if arm_rk == 1 and hc_rk == 1 and (3 <= pop <= 7):
    score += 25.0
  if tua_rk == 1 and hc_rk <= 3 and (4 <= pop <= 8) and track_type == '芝':
    score += 30.0

  # 厩舎黄金パターン特大加点（藤原・杉山・矢作・中内田・木村など）
  is_stable_gold = False
  if '藤原' in trainer:
    score += 20.0
    is_stable_gold = True
  if '杉山' in trainer:
    score += 20.0
    is_stable_gold = True
  if '矢作' in trainer:
    score += 20.0
    is_stable_gold = True
  if '中内田' in trainer and f_rk == 1:
    score += 25.0
    is_stable_gold = True
  if '木村' in trainer and fup >= 5:
    score += 20.0
    is_stable_gold = True

  # クッション値バイアス加点
  c_key = (venue_name, track_type, dist_val, sire, c_category)
  if c_key in CUSHION_DATA_BOOK:
    judg, _ = CUSHION_DATA_BOOK[c_key]
    if judg in ['最重要', '狙い目']:
      score += 35.0
    elif judg == '回収妙味':
      score += 20.0

  # ③ 主要指数によるフェイルセーフ救済規定
  # 【SSS級・絶対神域（F65以上・ARM120・TUA200）】新基準
  is_sss = (f_val >= 65.0) and (arm_val >= 120.0) and (tua_val >= 200.0)
  is_quad_crown = (
      (f_rk <= 3) and (arm_rk <= 3) and (tua_rk <= 3) and (fup >= 5)
  )
  is_solid_axis = (f_rk == 1) and (fup >= 5)
  is_kakugen = fup == 7
  is_f65_top = f_val >= 65.0

  is_rescued = (
      is_sss
      or is_quad_crown
      or is_solid_axis
      or is_kakugen
      or is_spec
      or is_stable_gold
      or is_f65_top
  )

  # ④ 減点処理（救済馬は減点を全免除）
  if not is_rescued:
    if c_rk >= 6:
      score -= 30.0
    if b_rk >= 6:
      score -= 15.0
    if pop <= 3 and fup <= 1:
      score -= 35.0
    if c_key in CUSHION_DATA_BOOK:
      judg, _ = CUSHION_DATA_BOOK[c_key]
      if judg == '危険':
        score -= 50.0

  return score, is_rescued, is_sss


# ------------------------------------------------------------------------------
# メインアプリケーション制御
# ------------------------------------------------------------------------------
def main():
  st.sidebar.markdown('## 📂 CSVデータ読込管理')
  df_raw, loaded_filename = read_csv_robust()

  uploaded_file = st.sidebar.file_uploader(
      '出馬表・全38列マスターCSVを指定', type=['csv']
  )
  if uploaded_file is not None:
    for enc in ['utf-8-sig', 'utf-8', 'cp932', 'shift-jis']:
      try:
        df_raw = pd.read_csv(uploaded_file, encoding=enc)
        if not df_raw.empty:
          loaded_filename = uploaded_file.name
          break
      except Exception:
        continue

  if df_raw.empty:
    st.markdown(
        "<div class='race-type-banner race-type-normal'>⚠️"
        ' CSVデータが読み込まれていません。サイドバーから「当日全指数統合.csv」を指定するか、作業フォルダに配置してください。</div>',
        unsafe_allow_html=True,
    )
    st.stop()

  st.sidebar.success(f'✅ 読込成功: {loaded_filename}')

  # クッション値＆芝馬場設定サイドバー
  st.sidebar.markdown('---')
  st.sidebar.markdown('### 🌿 馬場・クッション値設定')
  track_cond = st.sidebar.selectbox('芝馬場状態', ['良', '稍重', '重', '不良'], index=0)
  cushion_val = st.sidebar.slider(
      '当日クッション値',
      min_value=6.0,
      max_value=12.5,
      value=9.5,
      step=0.1,
      format='%.1f',
  )

  # データ標準化
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

  records = []
  for _, row in df_raw.iterrows():
    race_id = clean_str(row.get('場所R', ''))
    dist_raw = row.get('距離', 1600)
    umaban = row.get('馬番', 99)
    horse = clean_str(row.get('馬名', ''))
    trainer = clean_str(row.get('調教師', ''))
    jockey = clean_str(row.get('騎手', ''))
    pop = row.get('人気順位', 99)
    raw_c = clean_str(row.get('C', row.get('C(マーク)', '')))
    mark = clean_str(row.get('印', ''))
    blinkers = clean_str(row.get('C(馬)', ''))

    track = 'ダ' if 'ダ' in raw_c else ('芝' if '芝' in raw_c else '芝')
    dist_int = (
        int(re.sub(r'\D', '', str(dist_raw)))
        if re.sub(r'\D', '', str(dist_raw)).isdigit()
        else 1600
    )

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
    race_date = clean_str(row.get('日付', '10.18'))

    match_v = re.match(r'([^\d]+)(\d+)', race_id)
    v_name = (
        venue_dict.get(match_v.group(1), match_v.group(1))
        if match_v
        else '東京'
    )

    if horse:
      records.append({
          'race_id': race_id,
          'race_uid': race_id,
          '競馬場名': v_name,
          'track': track,
          'dist': dist_int,
          '馬番': int(float(umaban)),
          '馬名': horse,
          '印': mark,
          'ブリンカー': blinkers,
          '調教師': trainer,
          '騎手': jockey,
          '種牡馬': sire,
          '人気順位': int(float(pop)) if pd.notnull(pop) else 99,
          'Fup2': fup,
          'Fup2順位': fup_rk,
          'F': f_val,
          'F順位': f_rk,
          'ARM': arm_val,
          'ARM順位': arm_rk,
          'TUA': tua_val,
          'TUA順位': tua_rk,
          'S': s_val,
          'S順位': s_rk,
          '坂路調順位': hc_rk,
          '坂路血順位': hk_rk,
          '時計血順位': tk_rk,
          'コース連順位': c_rk,
          '血統連順位': k_rk,
          'バランス順位': b_rk,
          '前走脚質': run_style,
          '前走決手': pass_style,
          '日付': race_date,
      })

  df = pd.DataFrame(records)
  if df.empty:
    st.error('解析可能な有効データが存在しません。')
    st.stop()

  # メイン画面ヘッダー
  st.markdown(
      f"<div class='date-header-badge'>📅 開催日: 2026年{df['日付'].iloc[0]} |"
      ' JRAデータ解析エンジン「競馬予想10 クッション値Vr」</div>',
      unsafe_allow_html=True,
  )

  # 開催場ラジオボタン
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
  existing_venues = [
      v for v in venue_sort_order if v in df['競馬場名'].unique()
  ]
  chosen_venue = st.radio(
      '開催場選択', options=existing_venues, horizontal=True
  )

  # レース選択
  v_df = df[df['競馬場名'] == chosen_venue]
  races_in_v = v_df[['race_uid', 'race_id', 'track', 'dist']].drop_duplicates(
      'race_uid'
  )
  race_options = {
      r['race_uid']: f"{r['race_uid']} ({r['track']}{r['dist']}m)"
      for _, r in races_in_v.iterrows()
  }
  selected_race_uid = st.selectbox(
      'レース選択',
      options=list(race_options.keys()),
      format_func=lambda x: race_options[x],
  )

  race_df = df[df['race_uid'] == selected_race_uid].copy()

  # クッション区分判定
  c_cat = get_cushion_category(cushion_val, chosen_venue)

  # 動的スコアリング計算
  scores, rescued_flags, sss_flags = [], [], []
  for _, r in race_df.iterrows():
    sc, res, sss = calc_upgraded_dynamic_score(
        r, chosen_venue, r['track'], r['dist'], c_cat
    )
    scores.append(sc)
    rescued_flags.append(res)
    sss_flags.append(sss)

  race_df['dynamic_score'] = scores
  race_df['is_rescued'] = rescued_flags
  race_df['is_sss'] = sss_flags

  # レース判定バナー
  has_bonus = (
      (race_df['F順位'] <= 3) & (race_df['ARM順位'] <= 3) & (race_df['TUA順位'] <= 3)
  ).sum() >= 3
  has_sss = race_df['is_sss'].any()

  if has_bonus:
    banner_cls = 'race-type-bonus'
    banner_txt = '👑 ボーナスレース判定（1〜3位が主要指数を完全独占中）'
  elif has_sss:
    banner_cls = 'race-type-hit'
    banner_txt = (
        '🎯 SSS級・絶対神域出現（F指数65以上＋ARM120＋TUA200の鉄板軸が存在）'
    )
  else:
    banner_cls = 'race-type-recovery'
    banner_txt = '🔥 波乱抽出・標準ハイブリッド買い目連動レース'

  st.markdown(
      f"<div class='race-type-banner {banner_cls}'><div>{banner_txt}</div><div>クッション値帯:"
      f' {c_cat}</div></div>',
      unsafe_allow_html=True,
  )

  # ============================================================================
  # 【標準ハイブリッド馬券パック】YouTube解説・F指数65以上完全連動仕様
  # ============================================================================
  f65_horses = race_df[race_df['F'] >= 65.0].sort_values('F', ascending=False)
  has_f65 = len(f65_horses) > 0
  f_top3 = race_df.sort_values('F順位').head(3)
  f_top3_nums = f_top3['馬番'].tolist()

  if has_f65:
    mode_name = '👑 モードA：F指数65以上【絶対主役モード】'
    mode_desc = (
        'F指数65以上の抜けた馬を不動の連軸とし、F上位＋期待値穴馬へ網を張る構成'
    )
    honmei = f65_horses.iloc[0]
    honmei_num = int(honmei['馬番'])

    opponents = race_df[race_df['馬番'] != honmei_num].copy()
    taikou = opponents.sort_values(
        ['F順位', 'ARM順位', 'TUA順位', 'dynamic_score'],
        ascending=[True, True, True, False],
    ).iloc[0]
    taikou_num = int(taikou['馬番'])

    second_row = list(
        set(
            opponents.sort_values('F順位').head(2)['馬番'].tolist()
            + opponents.sort_values('ARM順位').head(1)['馬番'].tolist()
            + opponents.sort_values('TUA順位').head(1)['馬番'].tolist()
        )
    )
    third_row = list(
        set(
            second_row
            + opponents.sort_values('コース連順位').head(2)['馬番'].tolist()
            + opponents.sort_values('バランス順位').head(2)['馬番'].tolist()
        )
    )

    ana_candidates = opponents[opponents['人気順位'] >= 4].sort_values(
        ['ARM順位', 'TUA順位', 'dynamic_score'],
        ascending=[True, True, False],
    )
    ana = (
        ana_candidates.iloc[0]
        if not ana_candidates.empty
        else opponents.iloc[-1]
    )
    ana_num = int(ana['馬番'])

  else:
    mode_name = '🔥 モードB：単勝期待値軸 × F指数相手補完モード'
    mode_desc = (
        '単勝期待値馬（ARMS/坂路A3/Fup7）を軸にし、相手2列目に好走率約70%のF指数1〜3位を完全固定する構成'
    )
    honmei = race_df.sort_values(
        ['dynamic_score', 'Fup2', 'ARM順位'], ascending=[False, False, True]
    ).iloc[0]
    honmei_num = int(honmei['馬番'])

    second_row = [n for n in f_top3_nums if n != honmei_num]
    taikou_num = second_row[0] if second_row else f_top3_nums[0]
    taikou = race_df[race_df['馬番'] == taikou_num].iloc[0]

    opponents = race_df[race_df['馬番'] != honmei_num].copy()
    third_row = list(
        set(
            second_row
            + opponents.sort_values('坂路調順位').head(2)['馬番'].tolist()
            + opponents.sort_values('コース連順位').head(2)['馬番'].tolist()
        )
    )

    ana_candidates = opponents[opponents['人気順位'] >= 4].sort_values(
        ['ARM順位', 'TUA順位', 'dynamic_score'],
        ascending=[True, True, False],
    )
    ana = (
        ana_candidates.iloc[0]
        if not ana_candidates.empty
        else opponents.iloc[-1]
    )
    ana_num = int(ana['馬番'])

  # 推奨馬ピックアップパネル表示
  st.markdown(
      f"""
    <div class='recom-panel-go'>
        <div class='recom-title-go'>{mode_name}</div>
        <div style='font-size: 13px; color: #9ca3af; margin-bottom: 10px;'>{mode_desc}</div>
        <div class='recom-row'>🥇 <strong>本命・連軸</strong>: <span class='recom-val-num'>{honmei_num}番 {honmei['馬名']}</span>（F指数: {honmei['F']} / 動的スコア: {honmei['dynamic_score']:.1f}）</div>
        <div class='recom-row'>🛡️ <strong>対抗・相手筆頭</strong>: <span class='recom-val-num'>{taikou_num}番 {taikou['馬名']}</span>（F指数: {taikou['F']}）</div>
        <div class='recom-row'>💣 <strong>激走穴特注</strong>: <span class='recom-val-num'>{ana_num}番 {ana['馬名']}</span>（ARM: {ana['ARM']} / TUA: {ana['TUA']}）</div>
    </div>
    """,
      unsafe_allow_html=True,
  )

  # 標準ハイブリッド馬券パック パネル
  sec_nums_str = ', '.join(map(str, sorted(second_row)))
  third_nums_str = ', '.join(map(str, sorted(third_row)))

  st.markdown(
      f"""
    <div class='recom-block'>
        <h4 style='color: #60a5fa; margin-top: 0;'>🎯 標準ハイブリッド馬券パック フォーメーション</h4>
        <ul style='list-style-type: none; padding-left: 0; line-height: 1.8; font-size: 14px;'>
            <li><strong>【第1の網：主軸回収】</strong> 単勝: <span style='color: #fbbf24; font-weight: bold;'>{honmei_num}</span> ／ 馬単: <span style='color: #fbbf24; font-weight: bold;'>{honmei_num} → {taikou_num}</span>（相手筆頭裏抑え: {taikou_num} → {honmei_num}）</li>
            <li><strong>【第2の網：連対確保】</strong> 馬連: <span style='color: #38bdf8; font-weight: bold;'>{honmei_num} - {sec_nums_str}</span> ／ ワイド: <span style='color: #f472b6; font-weight: bold;'>{honmei_num} - {ana_num}</span></li>
            <li><strong>【第3の網：中配当網】</strong> 3連複F: <span style='color: #34d399; font-weight: bold;'>{honmei_num}</span> ＝ <span style='color: #38bdf8;'>{sec_nums_str}</span> ＝ <span style='color: #a78bfa;'>{third_nums_str}</span></li>
            <li><strong>【第4の網：高配当万馬券】</strong> 3連単F: <span style='color: #fbbf24; font-weight: bold;'>{honmei_num}</span> ⇄ <span style='color: #38bdf8;'>{taikou_num}</span> → <span style='color: #a78bfa;'>{third_nums_str}</span>（推奨裏表）</li>
        </ul>
    </div>
    """,
      unsafe_allow_html=True,
  )

  # ============================================================================
  # 出走馬詳細カルテ一覧
  # ============================================================================
  st.markdown('### 🏇 出走馬詳細カルテ')

  sorted_df = race_df.sort_values('dynamic_score', ascending=False)

  for _, h in sorted_df.iterrows():
    u_no = int(h['馬番'])
    badges = []

    # マークバッジ
    if u_no == honmei_num:
      badges.append("<span class='badge-mark-honmei'>◎ 本命</span>")
    elif u_no == taikou_num:
      badges.append("<span class='badge-mark-taikou'>◯ 対抗</span>")
    elif u_no == ana_num:
      badges.append("<span class='badge-mark-ana'>🔥 穴特注</span>")

    # フェイルセーフ救済バッジ
    if h['is_rescued']:
      badges.append(
          "<span class='badge-rescued'>🛡️ コア指数救済（減点免除）</span>"
      )

    # クッション値バイアス照合
    c_key = (
        chosen_venue,
        h['track'],
        h['dist'],
        h['種牡馬'],
        c_cat,
    )
    if c_key in CUSHION_DATA_BOOK:
      judg, stat_txt = CUSHION_DATA_BOOK[c_key]
      if judg in ['最重要', '狙い目']:
        badges.append(
            f"<span class='badge-cushion-fit'>🌿 クッション特注: {h['種牡馬']} ({stat_txt})</span>"
        )
      elif judg == '危険':
        badges.append(
            f"<span class='badge-cushion-danger'>⚠️ クッション危険: {h['種牡馬']} ({stat_txt})</span>"
        )

    # 指数ハイライト用スタイル
    f_style = 'val-f-top' if h['F順位'] <= 3 else ''
    s_style = 'val-s-top' if h['S順位'] <= 3 else ''
    arm_style = 'val-arms-top' if h['ARM順位'] <= 3 else ''
    tua_style = 'val-tua-top' if h['TUA順位'] <= 3 else ''

    st.markdown(
        f"""
        <div class='horse-card'>
            <div class='horse-card-header'>
                <span class='race-badge-title'>{u_no}番</span>
                <span class='horse-card-title'>{h['馬名']}</span>
                <span style='color: #9ca3af; font-size: 13.5px;'>（{h['調教師']} / {h['騎手']} / {h['人気順位']}番人気）</span>
            </div>
            <div style='margin-bottom: 8px;'>{' '.join(badges)}</div>
            <ul class='horse-card-list'>
                <li><strong>主要5大指数</strong>: 
                    F指数: <span class='{f_style}'>{h['F']}</span> (順位{h['F順位']}) / 
                    Fup2: <strong>{h['Fup2']}点</strong> (順位{h['Fup2順位']}) / 
                    ARM: <span class='{arm_style}'>{h['ARM']}</span> (順位{h['ARM順位']}) / 
                    TUA: <span class='{tua_style}'>{h['TUA']}</span> (順位{h['TUA順位']}) / 
                    S指数: <span class='{s_style}'>{h['S']}</span> (順位{h['S順位']})
                </li>
                <li><strong>適性・補正順位</strong>: 
                    坂路調: {h['坂路調順位']}位 / 坂路血: {h['坂路血順位']}位 / 時計血: {h['時計血順位']}位 / 
                    コース連: {h['コース連順位']}位 / 血統連: {h['血統連順位']}位 / バランス: {h['バランス順位']}位
                </li>
                <li><strong>血統＆展開</strong>: 父 {h['種牡馬']} ｜ 前走脚質: {h['前走脚質']}（決手: {h['前走決手']}）</li>
                <li><strong>総合動的評価スコア</strong>: <span style='color: #facc15; font-weight: bold; font-size: 15px;'>{h['dynamic_score']:.1f}点</span></li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == '__main__':
  main()
