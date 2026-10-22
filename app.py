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
# 競馬予想10 クッション値Vr - 完全統合Webアプリケーション（黄金マスター完全版）
# 全42列マスターCSV読込・調教タイム表示・調教順/脚質順ソート完全対応
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
        color: #ffffff; font-size: 12.5px; font-weight: 900; padding: 2px 8px; border-radius: 4px; border: 1px solid #fca5a5; margin-right: 6px;
    }
    .badge-mark-taikou {
        display: inline-flex; align-items: center; justify-content: center;
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: #ffffff; font-size: 12.5px; font-weight: 900; padding: 2px 8px; border-radius: 4px; border: 1px solid #93c5fd; margin-right: 6px;
    }
    .badge-mark-ana {
        display: inline-flex; align-items: center; justify-content: center;
        background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
        color: #ffffff; font-size: 12.5px; font-weight: 900; padding: 2px 8px; border-radius: 4px; border: 1px solid #fde68a; margin-right: 6px;
    }
    .badge-cushion-fit { display: inline-flex; align-items: center; background-color: #064e3b; color: #6ee7b7; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #10b981; }
    .badge-cushion-danger { display: inline-flex; align-items: center; background-color: #7f1d1d; color: #fca5a5; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #ef4444; }
    .badge-notebook-hit { display: inline-flex; align-items: center; background-color: #831843; color: #f472b6; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #db2777; margin-right: 4px; }
    .badge-stable-hit { display: inline-flex; align-items: center; background-color: #1e3a8a; color: #93c5fd; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #3b82f6; margin-right: 4px; }
    .badge-rescued { display: inline-flex; align-items: center; background-color: #581c87; color: #f0abfc; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #c084fc; }
    .val-rank1-gold { color: #1a1000; background-color: #fcd34d; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #f59e0b; }
    .val-f-top { color: #ffffff; background-color: #ea580c; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #fb923c; }
    .val-s-top { color: #ffffff; background-color: #8b5cf6; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #c4b5fd; }
    .val-arms-top { color: #083344; background-color: #38bdf8; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #0284c7; }
    .val-tua-top { color: #022c22; background-color: #34d399; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #059669; }
</style>
""",
    unsafe_allow_html=True,
)


def get_cushion_category(cushion_val, venue_name):
  c_val = float(cushion_val)
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


CUSHION_DATA_BOOK = {
    ('阪神', '芝', 1800, 'キズナ', '9.5-9.9 標準高'): (
        '最重要',
        'N56 勝19.6% 複41.1% 単421',
    ),
    ('東京', '芝', 1600, 'エピファネイア', '9.5-9.9 標準高'): (
        '最重要',
        'N98 勝13.3% 複39.8% 単277',
    ),
    ('東京', '芝', 1400, 'モーリス', '9.5-9.9 標準高'): (
        '最重要',
        'N69 勝10.1% 複29.0% 単408',
    ),
    ('東京', '芝', 1800, 'ディープインパクト', '9.5-9.9 標準高'): (
        '最重要',
        'N57 勝15.8% 複38.6% 単228',
    ),
    ('東京', '芝', 2000, 'キズナ', '8.6-9.4 やや低'): (
        '最重要',
        'N66 勝19.7% 複42.4% 単200',
    ),
    ('中京', '芝', 2000, 'ディープインパクト', '8.6-9.4 やや低'): (
        '最重要',
        'N61 勝18.0% 複42.6% 単178',
    ),
    ('小倉', '芝', 1200, 'ダイワメジャー', '9.5-9.9 標準高'): (
        '最重要',
        'N66 勝13.6% 複30.3% 単173',
    ),
    ('函館', '芝', 1800, 'キズナ', '<=8.5低'): (
        '最重要',
        'N62 勝17.7% 複38.7% 単143',
    ),
    ('札幌', '芝', 2000, 'オルフェーヴル', '<=8.5低'): (
        '最重要',
        'N57 勝15.8% 複35.1% 単136',
    ),
    ('中山', '芝', 2000, 'ダノンバラード', '9.5-9.9 標準高'): (
        '危険',
        'N30 複0.0%',
    ),
    ('東京', '芝', 2000, 'ルーラーシップ', '9.5-9.9 標準高'): (
        '危険',
        'N33 複9.1%',
    ),
    ('小倉', '芝', 1200, 'ジャスタウェイ', '8.6-9.4 やや低'): (
        '危険',
        'N35 複2.9%',
    ),
    ('東京', '芝', 1600, 'ゴールドシップ', '8.6-9.4 やや低'): (
        '危険',
        'N44 複4.5%',
    ),
}

COURSE_SPECIALIST_DICT = {
    ('カンレイスター', '中山', 'ダ', 1200): '5戦1勝・3着内5回(複100%)',
    ('ルヴァレドクール', '東京', 'ダ', 1600): '4戦3勝・3着内4回(複100%)',
}


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
  candidates = [
      '当日全指数統合.csv',
      '当日全指数統合10.18.csv',
      '10.18全指数統合シート - 全指数統合.csv',
      'データ統合.csv',
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
        if not df.empty and df.shape[1] >= 38:
          return df, newest
      except Exception:
        continue
  return pd.DataFrame(), ''


def calc_upgraded_dynamic_score(r, venue_name, track_type, dist_val, c_category):
  score = 0.0

  f_val = float(pd.to_numeric(r.get('F', 0.0), errors='coerce') or 0.0)
  f_rk = int(pd.to_numeric(r.get('F順位', 99), errors='coerce') or 99)
  fup = int(pd.to_numeric(r.get('Fup2', 0), errors='coerce') or 0)
  arm_val = float(pd.to_numeric(r.get('ARM', 0.0), errors='coerce') or 0.0)
  arm_rk = int(pd.to_numeric(r.get('ARM順位', 99), errors='coerce') or 99)
  tua_val = float(pd.to_numeric(r.get('TUA', 0.0), errors='coerce') or 0.0)
  tua_rk = int(pd.to_numeric(r.get('TUA順位', 99), errors='coerce') or 99)
  s_val = float(pd.to_numeric(r.get('S', 0.0), errors='coerce') or 0.0)
  s_rk = int(pd.to_numeric(r.get('S順位', 99), errors='coerce') or 99)
  pop = int(pd.to_numeric(r.get('人気順位', 99), errors='coerce') or 99)

  trainer = clean_str(r.get('調教師', ''))
  sire = clean_str(r.get('種牡馬', ''))
  h_name = clean_str(r.get('馬名', ''))
  track_change = clean_str(r.get('芝ダート変わり', ''))
  interval = str(r.get('間隔', ''))
  weight = float(
      pd.to_numeric(
          str(r.get('前場体重', '480')).replace('kg', ''), errors='coerce'
      )
      or 480.0
  )

  hc_rk = int(pd.to_numeric(r.get('坂路調順位', 99), errors='coerce') or 99)
  hk_rk = int(pd.to_numeric(r.get('坂路血順位', 99), errors='coerce') or 99)
  tk_rk = int(pd.to_numeric(r.get('時計血順位', 99), errors='coerce') or 99)
  c_rk = int(pd.to_numeric(r.get('コース連順位', 99), errors='coerce') or 99)
  k_rk = int(pd.to_numeric(r.get('血統連順位', 99), errors='coerce') or 99)
  b_rk = int(pd.to_numeric(r.get('バランス順位', 99), errors='coerce') or 99)

  is_spec = (h_name, venue_name, track_type, dist_val) in COURSE_SPECIALIST_DICT

  nb_hits = []
  stable_hits = []

  if track_type == 'ダ' and s_rk == 1 and weight >= 480:
    score += 40.0
    nb_hits.append('🐎 ダートで食う(S1位・大型)')

  is_long_rest = interval.isdigit() and int(interval) >= 12
  if is_long_rest:
    score += 30.0
    nb_hits.append('🔥 Nなごり(休み明け特注)')

  if arm_rk == 1 and fup >= 6:
    score += 45.0
    nb_hits.append('✨ ARMS×FUP(黄金クロス)')

  if track_type == 'ダ' and tua_val >= 190.0 and tua_rk <= 3 and s_rk <= 8:
    score += 35.0
    nb_hits.append('💎 TUAダート特注')

  if arm_rk <= 3:
    score += 20.0
    nb_hits.append('🌲 Ｃ馬・調教特注')

  if track_change == '芝→ダ' and tua_rk <= 3:
    score += 25.0
    nb_hits.append('🔄 芝→ダ激走特注')

  if '藤原' in trainer:
    score += 25.0
    stable_hits.append('厩舎: 藤原英昭（CW仕上がり鉄板）')
  if '杉山' in trainer:
    score += 25.0
    stable_hits.append('厩舎: 杉山晴紀（坂路終い11秒台加速）')
  if '矢作' in trainer:
    score += 25.0
    stable_hits.append('厩舎: 矢作芳人（坂路A2加速・連闘/中1週）')
  if '中内田' in trainer:
    score += 30.0 if f_rk == 1 else 20.0
    stable_hits.append('厩舎: 中内田充正（CW単走馬なり・勝率抜群）')
  if '木村' in trainer:
    score += 25.0
    stable_hits.append('厩舎: 木村哲也（南W併せ強め・外厩帰り）')
  if '堀宣行' in trainer:
    score += 20.0
    stable_hits.append('厩舎: 堀宣行（南W馬なり・上積み勝負）')
  if '友道' in trainer:
    score += 20.0
    stable_hits.append('厩舎: 友道康夫（芝併せ長距離信頼）')

  if f_rk == 1:
    score += 50.0
  elif f_rk <= 3:
    score += 30.0
  if fup == 7:
    score += 45.0
  elif fup >= 5:
    score += 30.0
  if c_rk <= 3:
    score += 25.0
  if b_rk <= 3:
    score += 25.0
  if is_spec:
    score += 35.0

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
      or len(nb_hits) > 0
      or len(stable_hits) > 0
      or is_f65_top
  )

  if not is_rescued:
    if c_rk >= 6:
      score -= 30.0
    if b_rk >= 6:
      score -= 15.0
    if pop <= 3 and fup <= 1:
      score -= 35.0

  return score, is_rescued, is_sss, nb_hits, stable_hits


def main():
  st.sidebar.markdown('## 📂 CSVデータ読込管理')
  df_raw, loaded_filename = read_csv_robust()

  uploaded_file = st.sidebar.file_uploader(
      '全42列マスターCSVを指定', type=['csv']
  )
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
    st.markdown(
        "<div class='race-type-banner race-type-normal'>⚠️"
        ' 全42列マスターCSVが読み込まれていません。サイドバーから「当日全指数統合.csv」を指定してください。</div>',
        unsafe_allow_html=True,
    )
    st.stop()

  st.sidebar.success(f'✅ 読込成功: {loaded_filename} (全{len(df_raw)}頭)')

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
    tua_rk = int(pd.to_numeric(row.get('TUA順位', 9
