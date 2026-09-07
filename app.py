import streamlit as st
import pandas as pd
import numpy as np
import os
import glob
import re
import datetime

# --- ページ基本設定 ---
st.set_page_config(
    page_title="競馬予想10 - 精鋭スマートエディション",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSSスタイル ---
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
        padding: 5px 14px;
        border-radius: 20px;
        color: #60a5fa;
        font-size: 14px;
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
        padding: 3px 9px;
        border-radius: 6px;
        font-weight: bold;
        margin-left: 8px;
    }
    .badge-decision-skip {
        background: linear-gradient(135deg, #64748b 0%, #475569 100%);
        color: #f1f5f9;
        font-size: 13px;
        padding: 3px 9px;
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
        font-size: 13px;
        color: #c9d1d9;
        margin-bottom: 4px;
        line-height: 1.5;
    }
    .horse-card-list li::before {
        content: "• ";
        color: #58a6ff;
        font-weight: bold;
    }

    /* 精鋭バッジ */
    .badge-iron {
        background: linear-gradient(135deg, #FFE259 0%, #FFA751 100%);
        color: #1a1000;
        font-weight: bold;
        font-size: 11.5px;
        padding: 2px 8px;
        border-radius: 6px;
    }
    .badge-high {
        background: linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%);
        color: #ffffff;
        font-weight: bold;
        font-size: 11.5px;
        padding: 2px 8px;
        border-radius: 6px;
    }
    .badge-speed {
        background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%);
        color: #ffffff;
        font-weight: bold;
        font-size: 11.5px;
        padding: 2px 8px;
        border-radius: 6px;
    }
    .badge-bomb {
        background: linear-gradient(135deg, #EB3349 0%, #F45C43 100%);
        color: #ffffff;
        font-weight: bold;
        font-size: 11.5px;
        padding: 2px 8px;
        border-radius: 6px;
    }
    .badge-danger {
        background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%);
        color: #fecaca;
        font-weight: bold;
        font-size: 11.5px;
        padding: 2px 8px;
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
            fup = pd.to_numeric(parts[10], errors='coerce') if n > 10 else 0
            s_val = pd.to_numeric(parts[12], errors='coerce') if n > 12 else 0.0
            s_rank = pd.to_numeric(parts[13], errors='coerce') if n > 13 else 99
            f_val = pd.to_numeric(parts[14], errors='coerce') if n > 14 else 0.0
            f_rank = pd.to_numeric(parts[15], errors='coerce') if n > 15 else 99
            arms_val = pd.to_numeric(parts[16], errors='coerce') if n > 16 else 0.0
            arms_rank = pd.to_numeric(parts[17], errors='coerce') if n > 17 else 99
            tua_val = pd.to_numeric(parts[18], errors='coerce') if n > 18 else 0.0
            tua_rank = pd.to_numeric(parts[19], errors='coerce') if n > 19 else 99
            finish = parts[-2] if n >= 22 else None
            sire = parts[-1] if n >= 22 else ""

            horse = clean_horse_name(horse_raw)
            if horse:
                fin_int = fw_map.get(str(finish), int(finish) if str(finish).isdigit() else np.nan)
                pop_int = int(pop) if str(pop).isdigit() else np.nan
                u_int = int(umaban) if str(umaban).isdigit() else 99

                records.append({
                    'race_id': race_id, 'track': track, 'dist': dist, '馬番': u_int,
                    '馬名': horse, '調教師': trainer, '騎手': clean_horse_name(jockey),
                    '種牡馬': sire, '人気': pop_int, '着順': fin_int,
                    'Fup': fup if not np.isnan(fup) else 0,
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

    # 同馬番集計
    ub_grp = df_main.groupby(['騎手', '馬番'])['race_id'].apply(list).to_dict()
    df_main['same_ub_count'] = df_main.apply(lambda r: len(ub_grp.get((r['騎手'], r['馬番']), [])), axis=1)
    df_main['is_same_ub'] = df_main['same_ub_count'] >= 2

    return df_main, detected_date


df, race_date = load_and_merge_all(up_index, up_sakaro, up_wood)

if df.empty:
    st.warning("⚠️ CSVデータが読み込まれていません。サイドバーからファイルを指定してください。")
    st.stop()


# ==============================================================================
# ★ コアロジック（精鋭フラグ判定）
# ==============================================================================
def is_danger_jk(row):
    jk = str(row.get('騎手', '')).strip()
    is_f3 = (row.get('F_rank', 99) <= 3)
    if is_f3 and any(d in jk for d in DANGER_JOCKEYS_F3): return True
    if any(d in jk for d in DANGER_JOCKEYS_GENERAL): return True
    return False

df['is_danger_jockey'] = df.apply(is_danger_jk, axis=1)
df['調教加速'] = df['坂路_完全加速'] | df['is_wood_accel']

# 💎 鉄板・黄金軸（複勝率60〜75%）
df['flag_iron_axis'] = (
    (df['F_rank'] <= 3) & df['調教加速'] & (
        (df['arms_rank'] <= 3) | (df['wood_1F'] <= 11.5) | (df['is_same_ub'] & (df['F_rank'] <= 2))
    )
) & (~df['is_danger_jockey'])

# ⚡ 先行・スピード軸（連対率60%）
df['flag_speed_axis'] = (df['S_rank'] == 1) & df['調教加速'] & (~df['is_danger_jockey'])

# 💣 爆弾穴馬（単勝回収率2,100%超ゾーン）
df['flag_bomb_horse'] = (
    (df['人気'] >= 6) & (df['Fup'] >= 4) & df['調教加速']
)

# 1着狙い・連対狙い
df['target_win'] = ((df['F_rank'] == 1) & (df['arms_rank'] <= 2) & df['調教加速']) & (~df['is_danger_jockey'])
df['target_axis'] = ((df['F_rank'] <= 2) & (df['tua_rank'] <= 3)) & (~df['is_danger_jockey'])


# ==============================================================================
# ★ 左側サイドバー: 厳選4大フィルター
# ==============================================================================
st.sidebar.markdown("### 🎯 厳選エリートフィルター")
st.sidebar.caption("※的中・回収率に直結する4大フラグのみに集約")

f_iron = st.sidebar.checkbox("💎 【鉄板・黄金軸】(複勝率60〜75%)", help="調教加速×F1〜3位×arms上位。不動の軸馬")
f_speed = st.sidebar.checkbox("⚡ 【先行・スピード軸】(連対率60%)", help="テン最速(S1位)×調教加速。押し切り連対")
f_bomb = st.sidebar.checkbox("💣 【爆弾穴馬】(単回収2,100%超)", help="6人気以下×Fup4点以上×調教加速。特大万馬券枠")
f_danger = st.sidebar.checkbox("⚠️ 【危険騎手】のみ表示", help="上位人気でも過去着外率が高い騎乗馬")

if st.sidebar.button("🔄 最新データ再読み込み", use_container_width=True):
    st.cache_data.clear()
    st.rerun()


# ==============================================================================
# ★ レース選択UI
# ==============================================================================
venue_sort_order = ['東京', '中山', '京都', '阪神', '中京', '小倉', '新潟', '福島', '函館', '札幌']
existing_venues = [v for v in venue_sort_order if v in df['競馬場名'].unique()]
if 'active_venue' not in st.session_state or st.session_state['active_venue'] not in existing_venues:
    st.session_state['active_venue'] = existing_venues[0]

chosen_venue = st.radio("開催場選択", options=existing_venues, horizontal=True, label_visibility="collapsed")
st.session_state['active_venue'] = chosen_venue

v_df = df[df['競馬場名'] == chosen_venue]
races_in_v = v_df[['race_uid', 'race_id', 'R番号', 'track', 'dist']].drop_duplicates('race_uid').sort_values('R番号')

race_options = {}
for _, r_row in races_in_v.iterrows():
    r_horses = df[df['race_uid'] == r_row['race_uid']]
    
    # 3大条件判定
    r_iron_c = int((r_horses['flag_iron_axis'] == True).sum())
    r_bomb_c = int((r_horses['flag_bomb_horse'] == True).sum())
    cond1 = (r_iron_c >= 1 and r_bomb_c <= 1)
    
    fav3 = r_horses[r_horses['人気'] <= 3]
    cond2 = not bool((fav3['is_danger_jockey'] == True).any()) if not fav3.empty else True
    
    f1_h = r_horses[r_horses['F_rank'] == 1]
    cond3 = bool(f1_h['F指数'].values[0] >= 60) if not f1_h.empty else False
    
    tag = "⭕勝負" if (cond1 and cond2 and cond3) else "⛔見送"
    marks = []
    if r_iron_c >= 1: marks.append("💎")
    if (r_horses['flag_speed_axis'] == True).any(): marks.append("⚡")
    if r_bomb_c >= 1: marks.append("💣")
    if (r_horses['is_danger_jockey'] == True).any(): marks.append("⚠️")

    lbl = f"{tag} {r_row['R番号']}R ({r_row['track']}{r_row['dist']}m) [{' '.join(marks)}]"
    race_options[r_row['race_uid']] = lbl

selected_race_uid = st.selectbox("レース選択", options=list(race_options.keys()), format_func=lambda x: race_options[x], label_visibility="collapsed")

race_df = df[df['race_uid'] == selected_race_uid].copy()
filtered_df = race_df.copy()


# ==============================================================================
# ★ レース判定バナー ＆ 自動買い目（馬番のみ）
# ==============================================================================
r_iron_cnt = int((race_df['flag_iron_axis'] == True).sum())
r_bomb_cnt = int((race_df['flag_bomb_horse'] == True).sum())
is_solid = (r_iron_cnt >= 1 and r_bomb_cnt <= 1)

fav3_cur = race_df[race_df['人気'] <= 3]
danger_in_fav3 = bool((fav3_cur['is_danger_jockey'] == True).any()) if not fav3_cur.empty else False

f1_cur = race_df[race_df['F_rank'] == 1]
f1_val = float(f1_cur['F指数'].values[0]) if not f1_cur.empty else 0.0
is_f1_ok = (f1_val >= 60)

is_go = is_solid and (not danger_in_fav3) and is_f1_ok

if is_go:
    banner_cls = "race-type-solid"
    banner_title = "🟢 堅調・軸不動レース"
    dec_badge = "<span class='badge-decision-go'>⭕ 【勝負厳選レース】3大条件クリア</span>"
    panel_cls = "recom-panel-go"
    title_cls = "recom-title-go"
    pts_cls = "recom-pts"
    p_title = "🎯 【勝負推奨】3連単＆ワイド買い目（馬番のみ）"
    
    c1 = race_df[race_df['flag_iron_axis'] | race_df['target_win']].sort_values('F_rank')['馬番'].tolist()[:2]
    if len(c1) == 0: c1 = race_df.sort_values('F_rank')['馬番'].tolist()[:2]
    c2 = list(c1)
    for h in race_df[race_df['target_axis'] | (race_df['F_rank'] <= 4)]['馬番'].tolist():
        if h not in c2: c2.append(h)
        if len(c2) >= 4: break
    c3 = list(c2)
    for h in race_df[race_df['flag_bomb_horse'] | (race_df['arms_rank'] <= 5)]['馬番'].tolist():
        if h not in c3: c3.append(h)
        if len(c3) >= 7: break
else:
    banner_cls = "race-type-chaos" if r_bomb_cnt >= 2 else "race-type-mix"
    banner_title = "🔴 波乱警戒レース" if r_bomb_cnt >= 2 else "🟡 混戦・軸波乱レース"
    dec_badge = "<span class='badge-decision-skip'>⛔ 【見送り推奨】波乱・地雷リスク</span>"
    panel_cls = "recom-panel-skip"
    title_cls = "recom-title-skip"
    pts_cls = "recom-pts-skip"
    p_title = "⚠️ 【参考算出】波乱対応型 買い目（馬番のみ）"

    c1 = race_df.sort_values('F_rank')['馬番'].tolist()[:3]
    for s in race_df[race_df['flag_speed_axis']]['馬番'].tolist()[:1]:
        if s not in c1: c1.append(s)
    c1 = c1[:4]
    c2 = list(c1)
    for h in race_df.sort_values('arms_rank')['馬番'].tolist()[:5]:
        if h not in c2: c2.append(h)
        if len(c2) >= 5: break
    c3 = list(c2)
    for h in race_df[race_df['flag_bomb_horse']]['馬番'].tolist():
        if h not in c3: c3.append(h)
    for h in race_df.sort_values('F_rank')['馬番'].tolist()[:7]:
        if h not in c3: c3.append(h)
        if len(c3) >= 7: break

# 点数計算
tickets = sum(1 for h1 in c1 for h2 in c2 if h2 != h1 for h3 in c3 if h3 not in [h1, h2])
c1_str = ", ".join(str(int(u)) for u in c1)
c2_str = ", ".join(str(int(u)) for u in c2)
c3_str = ", ".join(str(int(u)) for u in c3)
main_u = c1[0]
w_partners = [str(int(u)) for u in c2 if u != main_u][:3]
wide_str = f"{int(main_u)} - {', '.join(w_partners)}"

st.markdown(
    f"<div class='race-type-banner {banner_cls}'>"
    f"<div><strong>{banner_title}</strong> {dec_badge}</div>"
    f"<div>💎軸: {r_iron_cnt}頭 / 💣穴: {r_bomb_cnt}頭</div>"
    f"</div>",
    unsafe_allow_html=True
)

st.markdown(
    f"<div class='{panel_cls}'>"
    f"<div class='{title_cls}'>{p_title}</div>"
    f"<div class='recom-row'><span class='recom-label'>🎫 3連単フォーメーション</span> <span class='{pts_cls}'>計 {tickets}点</span><br>"
    f"&nbsp;&nbsp;&nbsp;&nbsp;1着: <span class='recom-val-num'>{c1_str}</span>&nbsp;&nbsp;→&nbsp;&nbsp;2着: <span class='recom-val-num'>{c2_str}</span>&nbsp;&nbsp;→&nbsp;&nbsp;3着: <span class='recom-val-num'>{c3_str}</span></div>"
    f"<div class='recom-row'><span class='recom-label'>🛡️ ワイド / 馬連本線</span> <span class='{pts_cls}'>計 {len(w_partners)}点</span><br>"
    f"&nbsp;&nbsp;&nbsp;&nbsp;流し: <span class='recom-val-num'>{wide_str}</span></div>"
    f"</div>",
    unsafe_allow_html=True
)


# ==============================================================================
# ★ 出走馬カード表示
# ==============================================================================
# フィルター適用
if f_iron: filtered_df = filtered_df[filtered_df['flag_iron_axis']]
if f_speed: filtered_df = filtered_df[filtered_df['flag_speed_axis']]
if f_bomb: filtered_df = filtered_df[filtered_df['flag_bomb_horse']]
if f_danger: filtered_df = filtered_df[filtered_df['is_danger_jockey']]

col_s1, col_s2 = st.columns([3, 1])
with col_s1:
    kw = st.text_input("🔍 馬名・騎手・調教師で検索", placeholder="検索ワードを入力...", label_visibility="collapsed")
    if kw:
        filtered_df = filtered_df[
            filtered_df['馬名'].str.contains(kw, na=False) |
            filtered_df['騎手'].str.contains(kw, na=False) |
            filtered_df['調教師'].str.contains(kw, na=False)
        ]
with col_s2:
    sort_opt = st.selectbox("並び順", ["単勝人気順 (1人気→)", "馬番順"], index=0, label_visibility="collapsed")

if sort_opt == "単勝人気順 (1人気→)":
    filtered_df = filtered_df.sort_values(['人気', '馬番'])
else:
    filtered_df = filtered_df.sort_values('馬番')

st.markdown(f"**出走馬一覧（該当: {len(filtered_df)}頭）**")

for _, row in filtered_df.iterrows():
    badges = []
    if row.get('is_danger_jockey'):
        badges.append("<span class='badge-danger'>⚠️ 危険騎手【危】</span>")
    if row.get('flag_iron_axis'):
        badges.append("<span class='badge-iron'>💎 鉄板・黄金軸 (複勝60〜75%)</span>")
    if row.get('flag_speed_axis'):
        badges.append("<span class='badge-speed'>⚡ 先行軸 (連対60%)</span>")
    if row.get('flag_bomb_horse'):
        badges.append("<span class='badge-bomb'>💣 爆弾穴馬</span>")
    if row.get('is_same_ub'):
        badges.append(f"<span style='background:#374151;color:#f3f4f6;font-size:11px;padding:2px 6px;border-radius:4px;'>🏇 同馬番({row['same_ub_count']}回目)</span>")

    u_no = int(row['馬番']) if pd.notnull(row['馬番']) else 99
    pop_str = f"{int(row['人気'])}人気" if pd.notnull(row['人気']) else "-人気"
    
    f_badge = f"<span class='rank-1st'>🥇1位</span>" if row['F_rank']==1 else f"{int(row['F_rank'])}位"
    arms_badge = f"<span class='rank-1st'>🥇1位</span>" if row['arms_rank']==1 else f"{int(row['arms_rank'])}位"
    s_badge = f"<span class='rank-1st'>🥇1位</span>" if row['S_rank']==1 else f"{int(row['S_rank'])}位"
    
    w_str = f"W: {row['wood_1F']:.1f}s 加速(+{row['wood_accel']:.1f}s)" if pd.notnull(row.get('wood_1F')) and row.get('is_wood_accel') else ("W: 計測有" if pd.notnull(row.get('wood_1F')) else "W: 計測無")
    s_str = f"坂路: 完全加速" if row.get('坂路_完全加速') else ("坂路: 計測有" if pd.notnull(row.get('坂路_4F')) else "坂路: 計測無")

    st.markdown(
        f"<div class='horse-card'>"
        f"<div class='horse-card-header'><span class='horse-card-title'>{u_no}番 {row['馬名']} ({pop_str})</span> {' '.join(badges)}</div>"
        f"<ul class='horse-card-list'>"
        f"<li><strong>騎手/厩舎</strong>: {row.get('騎手')} / {row.get('調教師')}</li>"
        f"<li><strong>調教ラップ</strong>: {w_str} | {s_str}</li>"
        f"<li><strong>能力指数</strong>: F: <strong>{row.get('F指数', 0.0)}</strong> ({f_badge}) | ARMS: <strong>{row.get('arms', 0.0)}</strong> ({arms_badge}) | S: <strong>{row.get('S指数', 0.0)}</strong> ({s_badge}) | Fup: <strong>{int(row.get('Fup', 0))}点</strong></li>"
        f"</ul></div>",
        unsafe_allow_html=True
    )
