import streamlit as st
import pandas as pd
import numpy as np
import os
import glob
import re
import datetime

# --- ページ基本設定 ---
st.set_page_config(
    page_title="Streamlit - 競馬予想10 完全統合版",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSSスタイル（ダークテーマUI & 豪華色分けバッジ） ---
st.markdown("""
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
    .race-type-mix {
        background: linear-gradient(135deg, #78350f 0%, #b45309 100%);
        color: #fffbeb;
        border: 1px solid #fbbf24;
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
        background: linear-gradient(135deg, #64748b 0%, #475569 100%);
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
    .recom-panel-skip {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 2px solid #64748b;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 20px;
    }
    .recom-title-go {
        font-size: 16px;
        font-weight: bold;
        color: #34d399;
        margin-bottom: 10px;
        border-bottom: 1px solid #374151;
        padding-bottom: 5px;
    }
    .recom-title-skip {
        font-size: 16px;
        font-weight: bold;
        color: #94a3b8;
        margin-bottom: 10px;
        border-bottom: 1px solid #334155;
        padding-bottom: 5px;
    }
    .recom-row {
        margin-bottom: 8px;
        font-size: 14.5px;
        color: #f3f4f6;
    }
    .recom-label {
        font-weight: bold;
        color: #fbbf24;
        display: inline-block;
        width: 155px;
    }
    .recom-val-num {
        color: #ffffff;
        font-weight: bold;
        font-size: 16px;
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
        margin-left: 10px;
    }
    .recom-pts-skip {
        display: inline-block;
        background-color: #334155;
        color: #cbd5e1;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
        margin-left: 10px;
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

    /* === 色分け同馬番バッジ === */
    .badge-jk-ub {
        background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
        color: #ffffff;
        font-weight: bold;
        font-size: 11.5px;
        padding: 2px 8px;
        border-radius: 6px;
        border: 1px solid #fcd34d;
        box-shadow: 0 1px 3px rgba(0,0,0,0.4);
    }
    .badge-tr-ub {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        color: #ffffff;
        font-weight: bold;
        font-size: 11.5px;
        padding: 2px 8px;
        border-radius: 6px;
        border: 1px solid #6ee7b7;
        box-shadow: 0 1px 3px rgba(0,0,0,0.4);
    }

    /* クッション値 適性・危険バッジ */
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

    /* 豪華特注バッジ */
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
    .rank-1st { color: #FFD700; font-weight: bold; }
    .rank-2nd { color: #E2E8F0; font-weight: bold; }
    .rank-3rd { color: #F97316; font-weight: bold; }
</style>
""", unsafe_allow_html=True)


# --- 危険騎手リスト ---
DANGER_JOCKEYS_F3 = ['斎藤新', '小沢大仁', '丸山元気', '池添謙一', '松若風馬', '菊沢一樹', '田辺裕信', '横山琉人', '岩田康誠', '吉田隼人', '菅原明良', '富田暁', '三浦皇成', '浜中俊', '鮫島克駿']
DANGER_JOCKEYS_GENERAL = ['小林脩斗', '川端海翼', '黛弘人', '野中悠太', '遠藤汰月', '亀田温心', '水沼元輝', '丸田恭介', '河原田菜', '古川吉洋', '国分優作', '永島まな', '柴田裕一', '木幡初也', '原田和真', '柴田大知', '古川奈穂', '中井裕二', '石橋脩', '嶋田純次']


# --- クッション値と種牡馬の適性マッピング ---
def get_cushion_band(venue, c_val):
    if c_val is None: return "standard"
    if venue in ['札幌', '函館']:
        if c_val >= 8.5: return "high"
        elif c_val >= 7.6: return "standard_high"
        elif c_val >= 7.0: return "standard"
        else: return "low"
    else:
        if c_val >= 10.0: return "high"
        elif c_val >= 9.5: return "standard_high"
        elif c_val >= 9.0: return "standard"
        else: return "low"


def evaluate_sire_cushion(sire_name, band):
    if not sire_name or pd.isnull(sire_name): return ""
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


# --- サイドバー: データ読み込み ---
st.sidebar.markdown("### 📁 CSVデータ読み込み")
with st.sidebar.expander("データ更新", expanded=False):
    up_index = st.file_uploader("出馬表・指数 CSV", type=['csv'], key='up_index')
    up_sakaro = st.file_uploader("坂路調教 CSV", type=['csv'], key='up_sakaro')
    up_wood = st.file_uploader("ウッド調教 CSV", type=['csv'], key='up_wood')


def clean_horse_name(name):
    if pd.isnull(name): return ""
    return str(name).strip().replace('*', '').replace('$', '').replace(' ', '').replace(' ', '')


@st.cache_data
def load_and_merge_all(f_index, f_sakaro, f_wood):
    index_patterns = ['data/出馬表_指数*.csv', '出馬表_指数*.csv']
    index_src = f_index
    if index_src is None:
        for pat in index_patterns:
            matches = glob.glob(pat)
            if matches: index_src = matches[0]; break

    records = []
    if index_src is not None:
        lines = open(index_src, 'r', encoding='shift-jis', errors='ignore').readlines() if isinstance(index_src, str) else index_src.read().decode('shift-jis', errors='ignore').splitlines()
        fw_map = {'１': 1, '２': 2, '３': 3, '４': 4, '５': 5, '６': 6, '７': 7, '８': 8, '９': 9, '10': 10,
                  '11': 11, '12': 12, '13': 13, '14': 14, '15': 15, '16': 16, '17': 17, '18': 18}

        for line in lines:
            parts = [p.strip() for p in line.strip().split(',')]
            n = len(parts)
            if n < 10 or parts[0] in ['場所', 'レースID', 'race_id']: continue

            race_id, track, dist, umaban, horse_raw = parts[0], parts[1], parts[2], parts[3], parts[4]
            trainer, jockey, pop = parts[6], parts[7], parts[8]
            mark = parts[9] if n > 9 else ""
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

            # 種牡馬名と着順を取得
            non_empty_parts = [p for p in parts if p != '']
            sire = non_empty_parts[-1] if len(non_empty_parts) > 0 else ""
            finish = non_empty_parts[-2] if len(non_empty_parts) > 1 else None

            horse = clean_horse_name(horse_raw)
            if horse:
                fin_int = fw_map.get(str(finish), int(finish) if str(finish).isdigit() else np.nan)
                pop_int = int(pop) if str(pop).isdigit() else np.nan
                u_int = int(umaban) if str(umaban).isdigit() else 99

                records.append({
                    'race_id': race_id, 'track': track, 'dist': dist, '馬番': u_int,
                    '馬名': horse, '印': mark, '調教師': clean_horse_name(trainer), '騎手': clean_horse_name(jockey),
                    '種牡馬': str(sire).strip(), '人気': pop_int, '着順': fin_int,
                    'Fup': fup if not np.isnan(fup) else 0, 'Fup_rank': int(fup_rank) if not np.isnan(fup_rank) else 99,
                    'S指数': s_val if not np.isnan(s_val) else 0.0, 'S_rank': int(s_rank) if not np.isnan(s_rank) else 99,
                    'F指数': f_val if not np.isnan(f_val) else 0.0, 'F_rank': int(f_rank) if not np.isnan(f_rank) else 99,
                    'arms': arms_val if not np.isnan(arms_val) else 0.0, 'arms_rank': int(arms_rank) if not np.isnan(arms_rank) else 99,
                    'tua': tua_val if not np.isnan(tua_val) else 0.0, 'tua_rank': int(tua_rank) if not np.isnan(tua_rank) else 99
                })

    df_main = pd.DataFrame(records)
    if df_main.empty: return pd.DataFrame(), None

    venue_dict = {'東': '東京', '中': '中山', '京': '京都', '阪': '阪神', '名': '中京', '小': '小倉', '新': '新潟', '福': '福島', '函': '函館', '札': '札幌'}
    def parse_race(rid):
        match = re.match(r'([^\d]+)(\d+)', str(rid))
        if match: return venue_dict.get(match.group(1), match.group(1)), int(match.group(2))
        return "その他", 99

    df_main[['競馬場名', 'R番号']] = df_main['race_id'].apply(lambda x: pd.Series(parse_race(x)))
    df_main['race_uid'] = df_main['race_id']
    detected_date = datetime.date(2026, 9, 6)

    # 坂路読み込み
    sakaro_src = f_sakaro or (glob.glob('出馬表_坂路*.csv') or [None])[0]
    if sakaro_src:
        s_lines = open(sakaro_src, 'r', encoding='shift-jis', errors='ignore').readlines() if isinstance(sakaro_src, str) else sakaro_src.read().decode('shift-jis', errors='ignore').splitlines()
        s_records = []
        for line in s_lines:
            parts = [p.strip() for p in line.strip().split(',')]
            if len(parts) < 4 or '馬名' in parts: continue
            h_name = next((clean_horse_name(p) for p in parts if re.match(r'^[\u30A0-\u30FF\* \$]{2,}$', p)), None)
            nums = [pd.to_numeric(p, errors='coerce') for p in parts if pd.to_numeric(p, errors='coerce') and 10.0 <= pd.to_numeric(p, errors='coerce') <= 120.0]
            if h_name and len(nums) >= 8:
                s_records.append({'馬名': h_name, '坂路_4F': nums[0], '坂路_1F': nums[3], '坂路_Lap4': nums[4], '坂路_Lap3': nums[5], '坂路_Lap2': nums[6], '坂路_Lap1': nums[7]})
        if s_records:
            df_s = pd.DataFrame(s_records).drop_duplicates('馬名')
            df_s['坂路_完全加速'] = (df_s['坂路_Lap4'] > df_s['坂路_Lap3']) & (df_s['坂路_Lap3'] > df_s['坂路_Lap2']) & (df_s['坂路_Lap2'] > df_s['坂路_Lap1'])
            df_main = pd.merge(df_main, df_s[['馬名', '坂路_4F', '坂路_1F', '坂路_完全加速']], on='馬名', how='left')

    if '坂路_完全加速' not in df_main.columns:
        df_main['坂路_4F'] = np.nan; df_main['坂路_1F'] = np.nan; df_main['坂路_完全加速'] = False

    # ウッド読み込み
    wood_src = f_wood or (glob.glob('出馬表_ウッド*.csv') or [None])[0]
    if wood_src:
        try:
            w_df = pd.read_csv(wood_src, encoding='shift-jis')
            c_name = next((c for c in ['馬名', '競走馬名'] if c in w_df.columns), w_df.columns[1])
            w_df['馬名'] = w_df[c_name].apply(clean_horse_name)
            c_1f = next((c for c in w_df.columns if '1F' in c.upper()), None)
            c_l2 = next((c for c in w_df.columns if 'LAP2' in c.upper()), None)
            c_l1 = next((c for c in w_df.columns if 'LAP1' in c.upper()), None)
            w_df['wood_1F'] = pd.to_numeric(w_df[c_1f], errors='coerce')
            w_df['wood_accel'] = pd.to_numeric(w_df[c_l2], errors='coerce') - pd.to_numeric(w_df[c_l1], errors='coerce')
            w_df['is_wood_accel'] = (w_df['wood_accel'] > 0) & (w_df['wood_accel'].notna())
            df_main = pd.merge(df_main, w_df[['馬名', 'wood_1F', 'wood_accel', 'is_wood_accel']].drop_duplicates('馬名'), on='馬名', how='left')
        except Exception: pass

    if 'is_wood_accel' not in df_main.columns:
        df_main['wood_1F'] = np.nan; df_main['wood_accel'] = np.nan; df_main['is_wood_accel'] = False

    df_main['坂路_完全加速'] = df_main['坂路_完全加速'].fillna(False).astype(bool)
    df_main['is_wood_accel'] = df_main['is_wood_accel'].fillna(False).astype(bool)

    # ★ 騎手の同馬番集計
    jk_ub_grp = df_main.groupby(['騎手', '馬番'])['race_id'].apply(list).to_dict()
    df_main['same_ub_jk_count'] = df_main.apply(lambda r: len(jk_ub_grp.get((r['騎手'], r['馬番']), [])), axis=1)
    df_main['same_ub_jk_races'] = df_main.apply(lambda r: ", ".join(jk_ub_grp.get((r['騎手'], r['馬番']), [])), axis=1)
    df_main['is_same_ub_jk'] = df_main['same_ub_jk_count'] >= 2

    # ★ 調教師の同馬番集計
    tr_ub_grp = df_main.groupby(['調教師', '馬番'])['race_id'].apply(list).to_dict()
    df_main['same_ub_tr_count'] = df_main.apply(lambda r: len(tr_ub_grp.get((r['調教師'], r['馬番']), [])), axis=1)
    df_main['same_ub_tr_races'] = df_main.apply(lambda r: ", ".join(tr_ub_grp.get((r['調教師'], r['馬番']), [])), axis=1)
    df_main['is_same_ub_tr'] = df_main['same_ub_tr_count'] >= 2

    return df_main, detected_date


df, race_date = load_and_merge_all(up_index, up_sakaro, up_wood)

if df.empty:
    st.warning("⚠️ CSVデータが読み込まれていません。サイドバーからファイルを指定してください。")
    st.stop()


# ==============================================================================
# ★ 全ファクター統合・判定ロジック
# ==============================================================================
def is_danger_jk(row):
    jk = str(row.get('騎手', '')).strip()
    is_f3 = (row.get('F_rank', 99) <= 3)
    is_any3 = (row.get('F_rank', 99) <= 3) or (row.get('arms_rank', 99) <= 3) or (row.get('tua_rank', 99) <= 3) or (row.get('S_rank', 99) <= 3)
    if is_f3 and any(d in jk for d in DANGER_JOCKEYS_F3): return True
    if is_any3 and any(d in jk for d in DANGER_JOCKEYS_GENERAL): return True
    return False

df['is_danger_jockey'] = df.apply(is_danger_jk, axis=1)
df['調教加速'] = df['坂路_完全加速'] | df['is_wood_accel']

# 🥇 1着狙い（勝率26%超）
df['target_win'] = (
    ((df['F_rank'] == 1) & (df['arms_rank'] == 1)) |
    ((df['Fup'] >= 5) & (df['F_rank'] == 1)) |
    ((df['F_rank'] == 1) & (df['arms_rank'] <= 3) & (df['S_rank'] <= 3)) |
    ((df['F指数'] >= 66) & (df['arms_rank'] == 1))
) & (~df['is_danger_jockey'])

# 🛡️ 軸・連対狙い（複勝率55%超）
df['target_axis'] = (
    ((df['F_rank'] <= 2) & (df['arms_rank'] <= 3)) |
    ((df['F_rank'] == 1) & (df['tua_rank'] <= 3)) |
    ((df['Fup'] >= 4) & (df['F_rank'] <= 3))
) & (~df['target_win']) & (~df['is_danger_jockey'])

# 💣 紐穴狙い
df['target_himo'] = (
    (df['人気'] >= 6) & df['調教加速'] & (
        (df['arms_rank'] <= 5) | (df['Fup'] >= 4) | (df['tua_rank'] <= 3)
    )
)

# 💎 鉄板軸馬（複勝率61.9%）
df['is_syn_iron'] = (
    (df['F_rank'] == 1) & (df['arms_rank'] <= 3) & (df['wood_1F'] <= 11.5) & df['is_wood_accel']
)

# 🔥 高確率軸馬（複勝率55%超）
df['is_syn_high'] = (
    ((df['F_rank'] == 1) | (df['F指数'] >= 66)) & (df['wood_1F'] <= 11.5) & df['is_wood_accel']
)

# ✨ Fup2(5〜7点) × 坂路完全加速
df['is_syn_fup_sakaro'] = (df['Fup'] >= 5) & df['坂路_完全加速']

# 💣 爆弾穴馬（単勝回収率2,100%超）
df['is_syn_bomb'] = (df['人気'] >= 6) & (df['Fup'] >= 4) & df['調教加速']

# 🔥 SSS級・F1位 × 究極ラップ
df['is_syn_f1_rap'] = (
    (df['F_rank'] == 1) & (
        ((df['wood_1F'] <= 12.4) & df['is_wood_accel']) |
        ((df['坂路_1F'] <= 12.4) & df['坂路_完全加速'])
    )
)

# 🏇 騎手同馬番 × シナジー
df['syn_jk_ub_wood'] = df['is_same_ub_jk'] & df['is_wood_accel'] & (df['F_rank'] <= 3)
df['syn_jk_ub_bomb'] = df['is_same_ub_jk'] & df['調教加速'] & (df['Fup'] >= 4) & (df['人気'] >= 6)

# 🏛️ 調教師同馬番 × シナジー（複勝率70%）
df['syn_tr_ub_arms'] = df['is_same_ub_tr'] & (df['arms_rank'] <= 3)


# ==============================================================================
# ★ サイドバー: 競馬場別クッション値 & 馬場状態
# ==============================================================================
st.sidebar.markdown("### 芝馬場状態")
turf_condition = st.sidebar.selectbox("芝馬場状態", ["良", "稍重", "重", "不良"], index=0, label_visibility="collapsed")

venue_sort_order = ['東京', '中山', '京都', '阪神', '中京', '小倉', '新潟', '福島', '函館', '札幌']
existing_venues = [v for v in venue_sort_order if v in df['競馬場名'].unique()]
if 'active_venue' not in st.session_state or st.session_state['active_venue'] not in existing_venues:
    st.session_state['active_venue'] = existing_venues[0]

default_cushions = {'札幌': 7.5, '函館': 7.4, '中京': 9.5, '新潟': 9.4, '東京': 9.6, '中山': 9.8, '京都': 9.5, '阪神': 9.6, '小倉': 9.3, '福島': 9.2}

st.sidebar.markdown(f"### 芝クッション値 ({st.session_state['active_venue']})")
cushion_state_key = f"cushion_val_{st.session_state['active_venue']}"
if cushion_state_key not in st.session_state:
    st.session_state[cushion_state_key] = default_cushions.get(st.session_state['active_venue'], 9.5)

current_cushion_val = st.sidebar.number_input(
    f"芝クッション値 ({st.session_state['active_venue']})",
    min_value=6.0, max_value=13.0, value=float(st.session_state[cushion_state_key]), step=0.1,
    key=cushion_state_key, label_visibility="collapsed"
)
current_band = get_cushion_band(st.session_state['active_venue'], current_cushion_val)


# ==============================================================================
# ★ 左側サイドバー: 黄金シナジー＆厳選フィルター
# ==============================================================================
st.sidebar.markdown("---")
st.sidebar.markdown("### 👑 黄金シナジー・絶対軸馬")
syn_iron = st.sidebar.checkbox(f"💎 鉄板軸馬 ({int(df['is_syn_iron'].sum())}頭)", help="複勝率 61.9% / 連対率 46.3%")
syn_high = st.sidebar.checkbox(f"🔥 高確率軸馬 ({int(df['is_syn_high'].sum())}頭)", help="複勝率 55%超ゾーン")
syn_fup_sakaro = st.sidebar.checkbox(f"✨ Fup坂路完全 ({int(df['is_syn_fup_sakaro'].sum())}頭)", help="Fup5点以上×坂路完全加速")
syn_f1_rap = st.sidebar.checkbox(f"🔥 SSS級・F1位×究極ラップ ({int(df['is_syn_f1_rap'].sum())}頭)")
syn_bomb = st.sidebar.checkbox(f"💣 爆弾穴馬 ({int(df['is_syn_bomb'].sum())}頭)", help="6人気以下×Fup4点以上×調教加速")

st.sidebar.markdown("### 🎯 狙い目抽出")
filter_target_win = st.sidebar.checkbox(f"🥇 1着狙い (勝率26%超) ({int(df['target_win'].sum())}頭)")
filter_target_axis = st.sidebar.checkbox(f"🛡️ 軸・連対狙い (複勝率55%超) ({int(df['target_axis'].sum())}頭)")
filter_target_himo = st.sidebar.checkbox(f"💣 紐穴狙い ({int(df['target_himo'].sum())}頭)")

st.sidebar.markdown("### 🏇 騎手・厩舎の同馬番抽出")
filter_same_ub_jk = st.sidebar.checkbox(f"🏇 騎手同馬番 ({int(df['is_same_ub_jk'].sum())}頭)")
filter_same_ub_tr = st.sidebar.checkbox(f"🏛️ 厩舎同馬番 ({int(df['is_same_ub_tr'].sum())}頭)")
filter_same_ub_wood = st.sidebar.checkbox(f"👑 騎手同馬番×W加速×F上位 ({int(df['syn_jk_ub_wood'].sum())}頭)", help="複勝率69.2%")
filter_same_ub_tr_arms = st.sidebar.checkbox(f"🚀 厩舎同馬番×arms上位 ({int(df['syn_tr_ub_arms'].sum())}頭)", help="複勝率70.0%")

st.sidebar.markdown("### 🧬 クッション値×血統適性")
filter_cushion_fit = st.sidebar.checkbox("🟢 クッション値・適性馬のみ")
filter_cushion_danger = st.sidebar.checkbox("🔴 クッション値・危険血統のみ")

st.sidebar.markdown("### ⚠️ 危険警告")
filter_danger_jockey = st.sidebar.checkbox(f"⚠️ 危険騎手【危】のみ表示 ({int(df['is_danger_jockey'].sum())}頭)")

if st.sidebar.button("🔄 最新データ再読み込み", use_container_width=True):
    st.cache_data.clear()
    st.rerun()


# ==============================================================================
# ★ レース選択UI（⭕勝負 / ⛔見送りを自動判定）
# ==============================================================================
weekday_kanji = ["月", "火", "水", "木", "金", "土", "日"]
w_str = weekday_kanji[race_date.weekday()]
st.markdown(f"<div class='date-header-badge'>📅 開催日時: {race_date.year}年{race_date.month}月{race_date.day}日 ({w_str})</div>", unsafe_allow_html=True)

chosen_venue = st.radio("開催場選択", options=existing_venues, horizontal=True, label_visibility="collapsed")
st.session_state['active_venue'] = chosen_venue

v_df = df[df['競馬場名'] == chosen_venue]
races_in_v = v_df[['race_uid', 'race_id', 'R番号', 'track', 'dist']].drop_duplicates('race_uid').sort_values('R番号')

race_options = {}
for _, r_row in races_in_v.iterrows():
    r_horses = df[df['race_uid'] == r_row['race_uid']]
    
    r_high_c = int((r_horses['is_syn_high'] == True).sum())
    r_iron_c = int((r_horses['is_syn_iron'] == True).sum())
    r_win_c = int((r_horses['target_win'] == True).sum())
    r_axis_c = int((r_horses['target_axis'] == True).sum())
    r_bomb_c = int((r_horses['is_syn_bomb'] == True).sum())
    
    cond1 = (r_high_c >= 2 or (r_win_c >= 1 and r_axis_c >= 1 and r_bomb_c <= 1)) or \
            ((r_iron_c >= 1 or r_high_c >= 1 or r_win_c >= 1) and r_bomb_c <= 1)
            
    fav3 = r_horses[r_horses['人気'] <= 3]
    cond2 = not bool((fav3['is_danger_jockey'] == True).any()) if not fav3.empty else True
    
    f1_h = r_horses[r_horses['F_rank'] == 1]
    f1_val = f1_h['F指数'].values[0] if not f1_h.empty else 0
    cond3 = (f1_val >= 60)
    
    tag = "⭕勝負" if (cond1 and cond2 and cond3) else "⛔見送"

    marks = []
    if r_iron_c >= 1: marks.append("💎鉄")
    if r_high_c >= 1: marks.append("🌟高")
    if (r_horses['syn_jk_ub_wood'] == True).any(): marks.append("👑騎")
    if (r_horses['syn_tr_ub_arms'] == True).any(): marks.append("🚀厩")
    if r_win_c >= 1: marks.append("🥇")
    if r_axis_c >= 1: marks.append("🛡️")
    if r_bomb_c >= 1: marks.append("💣")
    if (r_horses['is_danger_jockey'] == True).any(): marks.append("⚠️危")

    lbl = f"{tag} {r_row['R番号']}R ({r_row['track']}{r_row['dist']}m) [{' '.join(marks)}]"
    race_options[r_row['race_uid']] = lbl

selected_race_uid = st.selectbox("レース選択", options=list(race_options.keys()), format_func=lambda x: race_options[x], label_visibility="collapsed")

race_df = df[df['race_uid'] == selected_race_uid].copy()
filtered_df = race_df.copy()
is_turf_race = bool(filtered_df['track'].str.contains('芝').any()) if not filtered_df.empty else False


# ==============================================================================
# ★ レース判定バナー ＆ 全ファクター網羅の推奨買い目（馬番のみ）
# ==============================================================================
r_high_cnt = int((race_df['is_syn_high'] == True).sum())
r_iron_cnt = int((race_df['is_syn_iron'] == True).sum())
r_win_cnt = int((race_df['target_win'] == True).sum())
r_axis_cnt = int((race_df['target_axis'] == True).sum())
r_bomb_cnt = int((race_df['is_syn_bomb'] == True).sum())

if r_high_cnt >= 2 or (r_win_cnt >= 1 and r_axis_cnt >= 1 and r_bomb_cnt <= 1):
    banner_cls = "race-type-twin-axis"
    banner_title = "💎 2頭軸・本線レース"
    is_solid = True
elif (r_iron_cnt >= 1 or r_high_cnt >= 1 or r_win_cnt >= 1) and r_bomb_cnt <= 1:
    banner_cls = "race-type-solid"
    banner_title = "🟢 堅調・軸不動レース"
    is_solid = True
elif r_bomb_cnt >= 2:
    banner_cls = "race-type-chaos"
    banner_title = f"🔴 波乱警戒レース (爆弾穴馬 {r_bomb_cnt}頭 潜伏)"
    is_solid = False
else:
    banner_cls = "race-type-mix"
    banner_title = "🟡 混戦・軸波乱レース"
    is_solid = False

fav3_cur = race_df[race_df['人気'] <= 3]
danger_in_fav3 = bool((fav3_cur['is_danger_jockey'] == True).any()) if not fav3_cur.empty else False

f1_cur = race_df[race_df['F_rank'] == 1]
f1_val_cur = float(f1_cur['F指数'].values[0]) if not f1_cur.empty else 0.0
is_f1_ok = (f1_val_cur >= 60)

is_go = is_solid and (not danger_in_fav3) and is_f1_ok

# クッション値適性フラグ付与
race_df['cushion_badge_raw'] = race_df['種牡馬'].apply(lambda s: evaluate_sire_cushion(s, current_band) if is_turf_race else "")
race_df['is_cushion_fit'] = race_df['cushion_badge_raw'].str.contains('クッション適|軟馬場適')

if is_go:
    dec_badge = "<span class='badge-decision-go'>⭕ 【勝負厳選レース】3大条件クリア</span>"
    panel_cls = "recom-panel-go"
    title_cls = "recom-title-go"
    pts_cls = "recom-pts"
    p_title = "🎯 【勝負推奨】3連単＆ワイド買い目（全ファクター網羅 / 馬番のみ）"
    
    # 1着候補: 鉄板・高確率・騎手同馬番W加速・厩舎同馬番arms上位・1着狙い
    c1_cands = race_df[
        race_df['is_syn_iron'] | race_df['is_syn_high'] | 
        race_df['syn_jk_ub_wood'] | race_df['syn_tr_ub_arms'] | 
        race_df['target_win']
    ].sort_values('F_rank')['馬番'].tolist()
    
    if len(c1_cands) < 2:
        sup = race_df[(race_df['F_rank'] == 1) | (race_df['F指数'] >= 66)].sort_values('F_rank')['馬番'].tolist()
        for s in sup:
            if s not in c1_cands: c1_cands.append(s)
            if len(c1_cands) >= 2: break
    rec_c1 = c1_cands[:3]

    # 2着候補: 1着候補 + 軸連対 + tua上位 + S1位 + クッション適性馬
    rec_c2 = list(rec_c1)
    for h in race_df[race_df['target_axis'] | (race_df['tua_rank'] <= 2) | (race_df['S_rank'] == 1) | (race_df['is_cushion_fit'] & (race_df['F_rank'] <= 4))]['馬番'].tolist():
        if h not in rec_c2: rec_c2.append(h)
        if len(rec_c2) >= 5: break

    # 3着候補: 2着候補 + 爆弾穴馬(騎手/厩舎同馬番穴含む) + arms100+
    rec_c3 = list(rec_c2)
    for h in race_df[race_df['is_syn_bomb'] | race_df['syn_jk_ub_bomb'] | (race_df['arms'] >= 100)]['馬番'].tolist():
        if h not in rec_c3: rec_c3.append(h)
        if len(rec_c3) >= 8: break
else:
    reasons = []
    if not is_solid: reasons.append("混戦/波乱")
    if danger_in_fav3: reasons.append("1〜3人気に危騎手")
    if not is_f1_ok: reasons.append(f"F1位が{f1_val_cur:.0f}点")
    dec_badge = f"<span class='badge-decision-skip'>⛔ 【見送り推奨】({', '.join(reasons)})</span>"
    panel_cls = "recom-panel-skip"
    title_cls = "recom-title-skip"
    pts_cls = "recom-pts-skip"
    p_title = "⚠️ 【参考算出】波乱・混戦対応型 買い目（全ファクター網羅 / 馬番のみ）"

    # 混戦・波乱用: 頭を広げて高配当を捕獲
    c1_cands = []
    for h in race_df.sort_values('F_rank')['馬番'].tolist()[:3]:
        if h not in c1_cands: c1_cands.append(h)
    for h in race_df.sort_values('arms_rank')['馬番'].tolist()[:1]:
        if h not in c1_cands: c1_cands.append(h)
    for h in race_df[race_df['syn_jk_ub_wood'] | race_df['syn_tr_ub_arms']]['馬番'].tolist()[:1]:
        if h not in c1_cands: c1_cands.append(h)
    rec_c1 = c1_cands[:4]

    rec_c2 = list(rec_c1)
    for h in race_df.sort_values('tua_rank')['馬番'].tolist()[:2]:
        if h not in rec_c2: rec_c2.append(h)
    for h in race_df.sort_values('F_rank')['馬番'].tolist()[:5]:
        if h not in rec_c2: rec_c2.append(h)
        if len(rec_c2) >= 5: break

    rec_c3 = list(rec_c2)
    for h in race_df[race_df['is_syn_bomb'] | race_df['syn_jk_ub_bomb']]['馬番'].tolist():
        if h not in rec_c3: rec_c3.append(h)
    for h in race_df.sort_values('F_rank')['馬番'].tolist()[:7]:
        if h not in rec_c3: rec_c3.append(h)
        if len(rec_c3) >= 7: break

tickets = sum(1 for h1 in rec_c1 for h2 in rec_c2 if h2 != h1 for h3 in rec_c3 if h3 not in [h1, h2])
c1_str = ", ".join(str(int(u)) for u in rec_c1)
c2_str = ", ".join(str(int(u)) for u in rec_c2)
c3_str = ", ".join(str(int(u)) for u in rec_c3)
main_u = rec_c1[0]
w_partners = [str(int(u)) for u in rec_c2 if u != main_u][:3]
wide_str = f"{int(main_u)} - {', '.join(w_partners)}"

st.markdown(
    f"<div class='race-type-banner {banner_cls}'>"
    f"<div><strong>{banner_title}</strong> {dec_badge}</div>"
    f"<div>高確率軸: {r_high_cnt}頭 / 軸連対: {r_axis_cnt}頭 / 💣爆弾: {r_bomb_cnt}頭</div>"
    f"</div>",
    unsafe_allow_html=True
)

st.markdown(
    f"<div class='{panel_cls}'>"
    f"<div class='{title_cls}'>{p_title}</div>"
    f"<div class='recom-row'><span class='recom-label'>🎫 3連単フォーメーション</span> <span class='{pts_cls}'>計 {tickets}点</span><br>"
    f"&nbsp;&nbsp;&nbsp;&nbsp;<strong>1着</strong>: <span class='recom-val-num'>{c1_str}</span>&nbsp;&nbsp;→&nbsp;&nbsp;<strong>2着</strong>: <span class='recom-val-num'>{c2_str}</span>&nbsp;&nbsp;→&nbsp;&nbsp;<strong>3着</strong>: <span class='recom-val-num'>{c3_str}</span></div>"
    f"<div class='recom-row' style='margin-top:10px;'><span class='recom-label'>🛡️ ワイド / 馬連本線</span> <span class='{pts_cls}'>計 {len(w_partners)}点</span><br>"
    f"&nbsp;&nbsp;&nbsp;&nbsp;<strong>流し</strong>: <span class='recom-val-num'>{wide_str}</span></div>"
    f"</div>",
    unsafe_allow_html=True
)


# ==============================================================================
# ★ 出走馬カード表示 ＆ フィルター適用
# ==============================================================================
filtered_df['cushion_badge'] = filtered_df['種牡馬'].apply(lambda s: evaluate_sire_cushion(s, current_band) if is_turf_race else "")

if syn_iron: filtered_df = filtered_df[filtered_df['is_syn_iron']]
if syn_high: filtered_df = filtered_df[filtered_df['is_syn_high']]
if syn_fup_sakaro: filtered_df = filtered_df[filtered_df['is_syn_fup_sakaro']]
if syn_f1_rap: filtered_df = filtered_df[filtered_df['is_syn_f1_rap']]
if syn_bomb: filtered_df = filtered_df[filtered_df['is_syn_bomb']]
if filter_target_win: filtered_df = filtered_df[filtered_df['target_win']]
if filter_target_axis: filtered_df = filtered_df[filtered_df['target_axis']]
if filter_target_himo: filtered_df = filtered_df[filtered_df['target_himo']]
if filter_same_ub_jk: filtered_df = filtered_df[filtered_df['is_same_ub_jk']]
if filter_same_ub_tr: filtered_df = filtered_df[filtered_df['is_same_ub_tr']]
if filter_same_ub_wood: filtered_df = filtered_df[filtered_df['syn_jk_ub_wood']]
if filter_same_ub_tr_arms: filtered_df = filtered_df[filtered_df['syn_tr_ub_arms']]
if filter_danger_jockey: filtered_df = filtered_df[filtered_df['is_danger_jockey']]
if filter_cushion_fit: filtered_df = filtered_df[filtered_df['cushion_badge'].str.contains('クッション適|軟馬場適')]
if filter_cushion_danger: filtered_df = filtered_df[filtered_df['cushion_badge'].str.contains('危険血統')]

col_s1, col_s2 = st.columns([2.5, 1.5])
with col_s1:
    kw = st.text_input("🔍 馬名・騎手・調教師・父名で検索", placeholder="検索ワードを入力...", label_visibility="collapsed")
    if kw:
        filtered_df = filtered_df[
            filtered_df['馬名'].str.contains(kw, na=False) |
            filtered_df['騎手'].str.contains(kw, na=False) |
            filtered_df['調教師'].str.contains(kw, na=False) |
            filtered_df['種牡馬'].str.contains(kw, na=False)
        ]
with col_s2:
    sort_opt = st.selectbox(
        "並び順",
        [
            "単勝人気順 (1人気→)",
            "馬番順",
            "🔥 F指数 順位 (1位→)",
            "🚀 arms指数 順位 (1位→)",
            "⚡ S指数 順位 (1位→)",
            "🛡️ tua指数 順位 (1位→)",
            "✨ Fup 順位 (1位→)"
        ],
        index=0,
        label_visibility="collapsed"
    )

if sort_opt == "単勝人気順 (1人気→)": filtered_df = filtered_df.sort_values(['人気', '馬番'])
elif sort_opt == "🔥 F指数 順位 (1位→)": filtered_df = filtered_df.sort_values(['F_rank', '馬番'])
elif sort_opt == "🚀 arms指数 順位 (1位→)": filtered_df = filtered_df.sort_values(['arms_rank', '馬番'])
elif sort_opt == "⚡ S指数 順位 (1位→)": filtered_df = filtered_df.sort_values(['S_rank', '馬番'])
elif sort_opt == "🛡️ tua指数 順位 (1位→)": filtered_df = filtered_df.sort_values(['tua_rank', '馬番'])
elif sort_opt == "✨ Fup 順位 (1位→)": filtered_df = filtered_df.sort_values(['Fup_rank', '馬番'])
else: filtered_df = filtered_df.sort_values('馬番')

st.markdown(f"**出走馬一覧（該当: {len(filtered_df)}頭）**")

for _, row in filtered_df.iterrows():
    badges = []
    if row.get('is_danger_jockey'):
        badges.append("<span class='badge-danger-jockey'>⚠️ 危険騎手【危】</span>")
    if row.get('target_win'):
        badges.append("<span class='badge-target-win'>🥇 1着狙い (勝率26%超)</span>")
    elif row.get('target_axis'):
        badges.append("<span class='badge-target-axis'>🛡️ 軸・連対狙い (複勝率55%超)</span>")
    if row.get('is_syn_iron'):
        badges.append("<span class='badge-synergy badge-iron'>💎 鉄板軸馬 (複勝61.9%)</span>")
    elif row.get('is_syn_high'):
        badges.append("<span class='badge-synergy badge-high'>🔥 高確率軸 (複勝55%超)</span>")
    if row.get('is_syn_fup_sakaro'):
        badges.append("<span class='badge-synergy badge-sakaro-fup'>✨ Fup坂路完全</span>")
    if row.get('is_syn_f1_rap'):
        badges.append("<span class='badge-synergy badge-f1-rap'>🔥 SSS級・F1位×究極ラップ</span>")

    # ★ 色分け同馬番バッジ（騎手＝アンバー / 調教師＝エメラルド）
    if row.get('syn_jk_ub_wood'):
        badges.append("<span class='badge-jk-ub'>👑 騎手同馬番×W加速×F上位</span>")
    elif row.get('is_same_ub_jk'):
        badges.append(f"<span class='badge-jk-ub'>🏇 騎手同馬番{row['same_ub_jk_count']}回目 ({row['same_ub_jk_races']})</span>")

    if row.get('syn_tr_ub_arms'):
        badges.append("<span class='badge-tr-ub'>🚀 厩舎同馬番×arms上位 (複勝70%)</span>")
    elif row.get('is_same_ub_tr'):
        badges.append(f"<span class='badge-tr-ub'>🏛️ 厩舎同馬番{row['same_ub_tr_count']}回目 ({row['same_ub_tr_races']})</span>")

    if row.get('is_syn_bomb') or row.get('syn_jk_ub_bomb'):
        badges.append("<span class='badge-synergy badge-bomb'>💣 爆弾穴馬</span>")

    # クッション値 × 種牡馬バッジ
    if row.get('cushion_badge'):
        badges.append(row['cushion_badge'])

    u_no = int(row['馬番']) if pd.notnull(row['馬番']) else 99
    pop_str = f"{int(row['人気'])}人気" if pd.notnull(row['人気']) else "-人気"
    sire_display = row.get('種牡馬') if row.get('種牡馬') else "-"
    
    f_badge = f"<span class='rank-1st'>🥇1位</span>" if row['F_rank']==1 else f"{int(row['F_rank'])}位"
    arms_badge = f"<span class='rank-1st'>🥇1位</span>" if row['arms_rank']==1 else f"{int(row['arms_rank'])}位"
    s_badge = f"<span class='rank-1st'>🥇1位</span>" if row['S_rank']==1 else f"{int(row['S_rank'])}位"
    tua_badge = f"<span class='rank-1st'>🥇1位</span>" if row['tua_rank']==1 else f"{int(row['tua_rank'])}位"
    fup_badge = f"<span class='rank-1st'>🥇1位</span>" if row['Fup_rank']==1 else f"{int(row['Fup_rank'])}位"
    
    w_str = f"W: {row['wood_1F']:.1f}s 加速(+{row['wood_accel']:.1f}s)" if pd.notnull(row.get('wood_1F')) and row.get('is_wood_accel') else ("W: 計測有" if pd.notnull(row.get('wood_1F')) else "W: 計測無")
    s_str = "坂路: 完全加速" if row.get('坂路_完全加速') else ("坂路: 計測有" if pd.notnull(row.get('坂路_4F')) else "坂路: 計測無")

    st.markdown(
        f"<div class='horse-card'>"
        f"<div class='horse-card-header'><span class='horse-card-title'>{u_no}番 {row['馬名']} ({pop_str})</span> {' '.join(badges)}</div>"
        f"<ul class='horse-card-list'>"
        f"<li><strong>騎手/厩舎</strong>: {row.get('騎手')} / {row.get('調教師')} / <strong>父: {sire_display}</strong></li>"
        f"<li><strong>調教ラップ</strong>: {w_str} | {s_str}</li>"
        f"<li><strong>能力指数</strong>: F: <strong>{row.get('F指数', 0.0)}</strong> ({f_badge}) | ARMS: <strong>{row.get('arms', 0.0)}</strong> ({arms_badge}) | S: <strong>{row.get('S指数', 0.0)}</strong> ({s_badge}) | TUA: <strong>{row.get('tua', 0.0)}</strong> ({tua_badge}) | Fup: <strong>{int(row.get('Fup', 0))}点</strong> ({fup_badge})</li>"
        f"</ul></div>",
        unsafe_allow_html=True
    )
