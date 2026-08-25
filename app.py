import streamlit as st
import pandas as pd
import numpy as np
import os
import re

# --- ページ基本設定 ---
st.set_page_config(
    page_title="Streamlit - 競馬予想10 クッション値Vr",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSSスタイル（ダークテーマUI & 順位カラー） ---
st.markdown("""
<style>
    .metric-container {
        display: flex;
        justify-content: space-around;
        background-color: #161b22;
        padding: 16px;
        border-radius: 10px;
        margin-bottom: 20px;
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
        font-size: 28px;
        font-weight: bold;
        color: #f0f6fc;
    }
    .horse-card {
        background-color: #161e2e;
        border-left: 5px solid #238636;
        padding: 16px 20px;
        border-radius: 8px;
        margin-bottom: 16px;
        border-top: 1px solid #30363d;
        border-right: 1px solid #30363d;
        border-bottom: 1px solid #30363d;
    }
    .horse-card-header {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 10px;
    }
    .horse-card-title {
        font-size: 19px;
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

    /* 豪華特注バッジ */
    .badge-synergy {
        display: inline-flex;
        align-items: center;
        padding: 2px 8px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 11.5px;
        letter-spacing: 0.3px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.5);
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
    .badge-f1 {
        background: linear-gradient(135deg, #F7971E 0%, #FFD200 100%);
        color: #2b1d00;
        border: 1px solid #FFE066;
    }
    .badge-arms1 {
        background: linear-gradient(135deg, #00B4DB 0%, #0083B0 100%);
        color: #ffffff;
        border: 1px solid #56CCF2;
    }
    .badge-tua1 {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: #052010;
        border: 1px solid #80FFB4;
    }
    .badge-bomb {
        background: linear-gradient(135deg, #EB3349 0%, #F45C43 100%);
        color: #ffffff;
        border: 1px solid #FFA07A;
    }

    .badge-accel {
        background-color: #238636;
        color: #ffffff;
        padding: 2px 5px;
        border-radius: 4px;
        font-size: 11px;
    }
    .badge-decel {
        background-color: #6e7681;
        color: #ffffff;
        padding: 2px 5px;
        border-radius: 4px;
        font-size: 11px;
    }

    /* 順位カラーハイライト */
    .rank-1st {
        color: #FFD700;
        font-weight: bold;
        background-color: rgba(255, 215, 0, 0.18);
        padding: 1px 5px;
        border-radius: 4px;
        border: 1px solid rgba(255, 215, 0, 0.5);
    }
    .rank-2nd {
        color: #E0E0E0;
        font-weight: bold;
        background-color: rgba(224, 224, 224, 0.18);
        padding: 1px 5px;
        border-radius: 4px;
        border: 1px solid rgba(224, 224, 224, 0.5);
    }
    .rank-3rd {
        color: #CD7F32;
        font-weight: bold;
        background-color: rgba(205, 127, 50, 0.18);
        padding: 1px 5px;
        border-radius: 4px;
        border: 1px solid rgba(205, 127, 50, 0.5);
    }
    .rank-normal {
        color: #8b949e;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)


# --- サイドバー: 4大CSVアップローダー ---
st.sidebar.markdown("### 📁 4大CSVデータ読み込み")
with st.sidebar.expander("CSVファイルの指定 / アップロード", expanded=False):
    up_index = st.file_uploader("1. 出馬表・指数 CSV", type=['csv'], key='up_index')
    up_gtv = st.file_uploader("2. GTVオッズ CSV", type=['csv'], key='up_gtv')
    up_sakaro = st.file_uploader("3. 坂路調教 CSV", type=['csv'], key='up_sakaro')
    up_wood = st.file_uploader("4. ウッド調教 CSV", type=['csv'], key='up_wood')


# --- CSV読み込み汎用ヘルパー ---
def read_csv_flexible(file_obj, default_names):
    src = file_obj
    if src is None:
        for name in default_names:
            if os.path.exists(name):
                src = name
                break
    if src is None:
        return pd.DataFrame()
    
    try:
        return pd.read_csv(src, encoding='shift-jis')
    except Exception:
        try:
            if hasattr(src, 'seek'):
                src.seek(0)
            return pd.read_csv(src, encoding='utf-8', errors='ignore')
        except Exception:
            return pd.DataFrame()


def find_col(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None


# --- 順位カラー整形ヘルパー ---
def format_rank_badge(rank_val):
    if pd.isnull(rank_val) or rank_val == 99 or rank_val == 0:
        return "<span class='rank-normal'>-位</span>"
    try:
        r = int(rank_val)
    except Exception:
        return "<span class='rank-normal'>-位</span>"
        
    if r == 1:
        return f"<span class='rank-1st'>🥇1位</span>"
    elif r == 2:
        return f"<span class='rank-2nd'>🥈2位</span>"
    elif r == 3:
        return f"<span class='rank-3rd'>🥉3位</span>"
    else:
        return f"<span class='rank-normal'>{r}位</span>"


# --- データロード＆4CSV統合処理 ---
@st.cache_data
def load_and_merge_all(f_index, f_gtv, f_sakaro, f_wood):
    index_src = f_index
    if index_src is None:
        for name in ['出馬表_指数.csv', '指数、検証用.csv', '指数.csv']:
            if os.path.exists(name):
                index_src = name
                break

    records = []
    if index_src is not None:
        if isinstance(index_src, str):
            with open(index_src, 'r', encoding='shift-jis', errors='ignore') as f:
                lines = f.readlines()
        else:
            content = index_src.read()
            try:
                lines = content.decode('shift-jis').splitlines()
            except Exception:
                lines = content.decode('utf-8', errors='ignore').splitlines()

        fw_map = {'１': 1, '２': 2, '３': 3, '４': 4, '５': 5, '６': 6, '７': 7, '８': 8, '９': 9, '10': 10,
                  '11': 11, '12': 12, '13': 13, '14': 14, '15': 15, '16': 16, '17': 17, '18': 18}

        for line_idx, line in enumerate(lines):
            parts = [p.strip() for p in line.strip().split(',')]
            n = len(parts)
            if n < 10:
                continue

            race_id, track, dist, umaban, horse = parts[0], "", "", "", None
            trainer, jockey, sire = "", "", ""
            pop, finish, fup, f_val, f_rank = None, None, 0, 0.0, 99
            arms_val, arms_rank, tua_val, tua_rank = 0.0, 99, 0.0, 99

            if n == 24:
                track, dist, umaban = parts[1], parts[2], parts[3]
                horse = parts[4].replace('*', '').replace('$', '').strip()
                trainer, jockey = parts[6], parts[7]
                pop = parts[8]
                fup = pd.to_numeric(parts[10], errors='coerce')
                f_val = pd.to_numeric(parts[13], errors='coerce')
                f_rank = pd.to_numeric(parts[14], errors='coerce')
                arms_val = pd.to_numeric(parts[16], errors='coerce')
                arms_rank = pd.to_numeric(parts[17], errors='coerce')
                tua_val = pd.to_numeric(parts[19], errors='coerce')
                tua_rank = pd.to_numeric(parts[20], errors='coerce')
                finish = parts[22]
                sire = parts[23] if n > 23 else ""
            elif n == 23:
                track, dist, umaban = parts[1], parts[2], parts[3]
                horse = parts[4].replace('*', '').replace('$', '').strip()
                trainer, jockey = parts[6], parts[7]
                pop = parts[8]
                fup = pd.to_numeric(parts[10], errors='coerce')
                f_val = pd.to_numeric(parts[12], errors='coerce')
                f_rank = pd.to_numeric(parts[13], errors='coerce')
                arms_val = pd.to_numeric(parts[16], errors='coerce')
                arms_rank = pd.to_numeric(parts[17], errors='coerce')
                tua_val = pd.to_numeric(parts[18], errors='coerce')
                tua_rank = pd.to_numeric(parts[19], errors='coerce')
                finish = parts[20]
                sire = parts[21] if n > 21 else ""
            elif n >= 26:
                track, dist, umaban = parts[1], parts[2], parts[3]
                trainer, jockey = parts[5], parts[6]
                horse = parts[7].replace('*', '').replace('$', '').strip()
                pop = parts[8]
                fup = pd.to_numeric(parts[10], errors='coerce')
                f_val = pd.to_numeric(parts[12], errors='coerce')
                f_rank = pd.to_numeric(parts[13], errors='coerce')
                arms_val = pd.to_numeric(parts[18], errors='coerce')
                arms_rank = pd.to_numeric(parts[19], errors='coerce')
                tua_val = pd.to_numeric(parts[21], errors='coerce')
                tua_rank = pd.to_numeric(parts[22], errors='coerce')
                finish = parts[24]
                sire = parts[25] if n > 25 else ""
            else:
                continue

            if horse:
                fin_int = fw_map.get(finish, int(finish) if str(finish).isdigit() else np.nan)
                pop_int = int(pop) if str(pop).isdigit() else np.nan
                u_int = int(umaban) if str(umaban).isdigit() else 99

                records.append({
                    'race_id': race_id,
                    'track': track,
                    'dist': dist,
                    '馬番': u_int,
                    '馬名': horse,
                    '調教師': trainer,
                    '騎手': jockey,
                    '種牡馬': sire,
                    '人気': pop_int,
                    '着順': fin_int,
                    'Fup': fup if not np.isnan(fup) else 0,
                    'F指数': f_val if not np.isnan(f_val) else 0.0,
                    'F_rank': int(f_rank) if not np.isnan(f_rank) else 99,
                    'arms': arms_val if not np.isnan(arms_val) else 0.0,
                    'arms_rank': int(arms_rank) if not np.isnan(arms_rank) else 99,
                    'tua': tua_val if not np.isnan(tua_val) else 0.0,
                    'tua_rank': int(tua_rank) if not np.isnan(tua_rank) else 99
                })

    df_main = pd.DataFrame(records)
    if df_main.empty:
        return pd.DataFrame()

    resets = [0]
    for i in range(1, len(df_main)):
        h_curr = df_main.loc[i, '馬名']
        h_prev = df_main.loc[i - 1, '馬名']
        if h_curr < h_prev and (h_prev > 'マ' and h_curr < 'ウ'):
            resets.append(i)
    resets.append(len(df_main))
    batch_ids = []
    for i in range(len(resets) - 1):
        batch_ids.extend([i] * (resets[i + 1] - resets[i]))
    df_main['batch_id'] = batch_ids
    df_main['race_uid'] = df_main['batch_id'].astype(str) + "_" + df_main['race_id']

    venue_dict = {'東': '東京', '中': '中山', '京': '京都', '阪': '阪神', '名': '中京', '小': '小倉', '新': '新潟', '福': '福島', '函': '函館', '札': '札幌'}
    def parse_race(rid):
        match = re.match(r'([^\d]+)(\d+)', str(rid))
        if match:
            v_code, r_no = match.group(1), int(match.group(2))
            v_name = venue_dict.get(v_code, v_code)
            return v_name, r_no
        return "その他", 99

    df_main[['競馬場名', 'R番号']] = df_main['race_id'].apply(lambda x: pd.Series(parse_race(x)))

    # GTVオッズ結合
    df_gtv = read_csv_flexible(f_gtv, ['GTV馬.csv', 'GTV.csv'])
    if not df_gtv.empty:
        name_col = find_col(df_gtv, ['馬名', '馬 名', '競走馬名'])
        if name_col:
            df_gtv['馬名'] = df_gtv[name_col].astype(str).str.strip()
            gtv_cols = [c for c in df_gtv.columns if c not in ['馬名', name_col]]
            df_main = pd.merge(df_main, df_gtv[['馬名'] + gtv_cols].drop_duplicates('馬名'), on='馬名', how='left')

    # 3. 坂路調教 CSV
    df_sakaro = read_csv_flexible(f_sakaro, ['出馬表_坂路.csv', '坂路調教.csv', '坂路.csv'])
    if not df_sakaro.empty:
        s_name = find_col(df_sakaro, ['馬名', '馬 名', '競走馬名'])
        if s_name:
            df_sakaro['馬名'] = df_sakaro[s_name].astype(str).str.strip()
            c_4f = find_col(df_sakaro, ['4F', '４Ｆ', '４F', '4f'])
            c_1f = find_col(df_sakaro, ['1F', '１Ｆ', '１F', '1f'])
            c_lap4 = find_col(df_sakaro, ['Lap4', 'lap4', 'LAP4', 'L4'])
            c_lap3 = find_col(df_sakaro, ['Lap3', 'lap3', 'LAP3', 'L3'])
            c_lap2 = find_col(df_sakaro, ['Lap2', 'lap2', 'LAP2', 'L2'])
            c_lap1 = find_col(df_sakaro, ['Lap1', 'lap1', 'LAP1', 'L1'])

            df_sakaro['坂路_4F'] = pd.to_numeric(df_sakaro[c_4f], errors='coerce') if c_4f else np.nan
            df_sakaro['坂路_1F'] = pd.to_numeric(df_sakaro[c_1f], errors='coerce') if c_1f else np.nan
            df_sakaro['坂路_Lap4'] = pd.to_numeric(df_sakaro[c_lap4], errors='coerce') if c_lap4 else np.nan
            df_sakaro['坂路_Lap3'] = pd.to_numeric(df_sakaro[c_lap3], errors='coerce') if c_lap3 else np.nan
            df_sakaro['坂路_Lap2'] = pd.to_numeric(df_sakaro[c_lap2], errors='coerce') if c_lap2 else np.nan
            df_sakaro['坂路_Lap1'] = pd.to_numeric(df_sakaro[c_lap1], errors='coerce') if c_lap1 else np.nan

            l4, l3, l2, l1 = df_sakaro['坂路_Lap4'], df_sakaro['坂路_Lap3'], df_sakaro['坂路_Lap2'], df_sakaro['坂路_Lap1']
            df_sakaro['坂路_完全加速'] = (l4 > l3) & (l3 > l2) & (l2 > l1)

            sakaro_cols = ['馬名', '坂路_4F', '坂路_1F', '坂路_Lap4', '坂路_Lap3', '坂路_Lap2', '坂路_Lap1', '坂路_完全加速']
            df_main = pd.merge(df_main, df_sakaro[sakaro_cols].drop_duplicates('馬名'), on='馬名', how='left')

    # 列未存在時の初期化
    if '坂路_4F' not in df_main.columns:
        df_main['坂路_4F'] = np.nan
        df_main['坂路_1F'] = np.nan
        df_main['坂路_Lap4'] = np.nan
        df_main['坂路_Lap3'] = np.nan
        df_main['坂路_Lap2'] = np.nan
        df_main['坂路_Lap1'] = np.nan
        df_main['坂路_完全加速'] = False

    # 4. ウッド調教 CSV
    df_wood_raw = read_csv_flexible(f_wood, ['ウッド、検証用.csv', 'ウッド調教.csv', 'ウッド.csv'])
    if not df_wood_raw.empty:
        w_df = df_wood_raw[df_wood_raw.iloc[:, 0] != '場所'].copy()
        c_w_name = find_col(w_df, ['馬名', '馬 名', '競走馬名'])
        if c_w_name:
            w_df['馬名'] = w_df[c_w_name].astype(str).str.strip()
            c_w_5f = find_col(w_df, ['5F', '５Ｆ', '５F', '5f'])
            c_w_1f = find_col(w_df, ['1F', '１Ｆ', '１F', '1f'])
            c_w_l4 = find_col(w_df, ['Lap4', 'lap4', 'LAP4', 'L4'])
            c_w_l3 = find_col(w_df, ['Lap3', 'lap3', 'LAP3', 'L3'])
            c_w_l2 = find_col(w_df, ['Lap2', 'lap2', 'LAP2', 'L2'])
            c_w_l1 = find_col(w_df, ['Lap1', 'lap1', 'LAP1', 'L1'])
            c_w_plc = find_col(w_df, ['場所', '調教場', '場'])
            c_w_date = find_col(w_df, ['年月日', '日付', '日付S'])

            w_df['wood_5F'] = pd.to_numeric(w_df[c_w_5f], errors='coerce') if c_w_5f else np.nan
            w_df['wood_1F'] = pd.to_numeric(w_df[c_w_1f], errors='coerce') if c_w_1f else np.nan
            w_df['wood_Lap4'] = pd.to_numeric(w_df[c_w_l4], errors='coerce') if c_w_l4 else np.nan
            w_df['wood_Lap3'] = pd.to_numeric(w_df[c_w_l3], errors='coerce') if c_w_l3 else np.nan
            w_df['wood_Lap2'] = pd.to_numeric(w_df[c_w_l2], errors='coerce') if c_w_l2 else np.nan
            w_df['wood_Lap1'] = pd.to_numeric(w_df[c_w_l1], errors='coerce') if c_w_l1 else np.nan
            w_df['wood_place'] = w_df[c_w_plc].astype(str) if c_w_plc else ""

            if c_w_date:
                w_df['調教日'] = pd.to_datetime(w_df[c_w_date].astype(str), format='%Y%m%d', errors='coerce')
                w_latest = w_df.sort_values('調教日').groupby('馬名').last().reset_index()
            else:
                w_latest = w_df.groupby('馬名').last().reset_index()

            wood_cols = ['馬名', 'wood_place', 'wood_5F', 'wood_1F', 'wood_Lap4', 'wood_Lap3', 'wood_Lap2', 'wood_Lap1']
            df_main = pd.merge(df_main, w_latest[wood_cols].drop_duplicates('馬名'), on='馬名', how='left')

    if 'wood_5F' not in df_main.columns:
        df_main['wood_place'] = ""
        df_main['wood_5F'] = np.nan
        df_main['wood_1F'] = np.nan
        df_main['wood_Lap4'] = np.nan
        df_main['wood_Lap3'] = np.nan
        df_main['wood_Lap2'] = np.nan
        df_main['wood_Lap1'] = np.nan

    # ウッド加速判定
    df_main['wood_accel'] = df_main['wood_Lap2'] - df_main['wood_Lap1']
    df_main['is_wood_accel'] = df_main['wood_accel'] > 0

    # 坂路・ウッドのレース内順位
    df_main['坂路_4F_rank'] = df_main.groupby('race_uid')['坂路_4F'].rank(method='min', ascending=True)
    df_main['坂路_Lap4_rank'] = df_main.groupby('race_uid')['坂路_Lap4'].rank(method='min', ascending=True)
    df_main['坂路_Lap3_rank'] = df_main.groupby('race_uid')['坂路_Lap3'].rank(method='min', ascending=True)
    df_main['坂路_Lap2_rank'] = df_main.groupby('race_uid')['坂路_Lap2'].rank(method='min', ascending=True)
    df_main['坂路_Lap1_rank'] = df_main.groupby('race_uid')['坂路_Lap1'].rank(method='min', ascending=True)

    df_main['wood_5F_rank'] = df_main.groupby('race_uid')['wood_5F'].rank(method='min', ascending=True)
    df_main['wood_Lap4_rank'] = df_main.groupby('race_uid')['wood_Lap4'].rank(method='min', ascending=True)
    df_main['wood_Lap3_rank'] = df_main.groupby('race_uid')['wood_Lap3'].rank(method='min', ascending=True)
    df_main['wood_Lap2_rank'] = df_main.groupby('race_uid')['wood_Lap2'].rank(method='min', ascending=True)
    df_main['wood_Lap1_rank'] = df_main.groupby('race_uid')['wood_Lap1'].rank(method='min', ascending=True)

    return df_main


# 統合データ読み込み実行
df = load_and_merge_all(up_index, up_gtv, up_sakaro, up_wood)


# --- サイドバー: 条件・操作エリア ---
st.sidebar.markdown("---")
st.sidebar.markdown("### 芝馬場状態")
turf_condition = st.sidebar.selectbox("芝馬場状態", ["良", "稍重", "重", "不良"], index=0, label_visibility="collapsed")

st.sidebar.markdown("### 芝クッション値")
cushion_val = st.sidebar.number_input("芝クッション値", min_value=7.0, max_value=12.0, value=9.5, step=0.1, label_visibility="collapsed")

if cushion_val >= 9.5 and cushion_val <= 9.9:
    band_label = "📍 判定帯: 9.5-9.9 (標準高)"
elif cushion_val >= 10.0:
    band_label = "📍 判定帯: 10.0以上 (硬め・高速)"
else:
    band_label = "📍 判定帯: 9.4以下 (標準〜軟らかめ)"

st.sidebar.button(band_label, use_container_width=True)

if st.sidebar.button("🔄 最新データへ強制再読み込み", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")


# --- サイドバー: 👑 黄金シナジー抽出 ---
st.sidebar.markdown("### 👑 黄金シナジー抽出")
syn_iron = st.sidebar.checkbox("💎 鉄板軸馬 (F1位 × arms3位内 × ウッド加速11.5s以下)", help="複勝率 61.9% / 連対率 46.3%")
syn_high = st.sidebar.checkbox("🔥 高確率軸馬 (F1位/66以上 × ウッド加速11.5s以下)", help="複勝率 54.8〜59.0%")
syn_fup_sakaro = st.sidebar.checkbox("✨ Fup2(5〜7点) × 坂路完全加速", help="坂路完全加速かつFup高評価")
syn_f1_rap = st.sidebar.checkbox("🔥 SSS級・F1位 × 究極ラップ (1F≤12.4s)")
syn_bomb = st.sidebar.checkbox("💣 爆弾穴馬 (6人気以下 × Fup2≥4 × 加速)")

st.sidebar.markdown("---")


# --- サイドバー: 📊 指数黄金パターン抽出 ---
st.sidebar.markdown("### 📊 指数黄金パターン抽出")
pat_f1 = st.sidebar.checkbox("🥇 F指数 1位 (勝率22.1% / 複勝率52.9%)")
pat_f66 = st.sidebar.checkbox("🔥 F指数 66以上 (高信頼)")
pat_f1_arms3 = st.sidebar.checkbox("🎯 F指数1位 ＋ arms3位以内")
pat_arms1 = st.sidebar.checkbox("🚀 arms指数 1位 (期待値ホース)")
pat_tua1 = st.sidebar.checkbox("🛡️ tua指数 1位 (堅実軸)")
pat_wood_top3 = st.sidebar.checkbox("⚡ ウッド5F 3位以内")


# --- メイン画面 ---
if df.empty:
    st.warning("⚠️ CSVデータが読み込まれていません。サイドバーの「📁 4大CSVデータ読み込み」からファイルを指定するか、同一フォルダにCSVを配置してください。")
    st.stop()


# --- レース選択UI ---
st.markdown("### 🎯 レース選択")
venue_sort_order = ['東京', '中山', '京都', '阪神', '中京', '小倉', '新潟', '福島', '函館', '札幌', 'その他']
existing_venues = [v for v in venue_sort_order if v in df['競馬場名'].unique()] + [v for v in df['競馬場名'].unique() if v not in venue_sort_order]

venue_tabs = st.tabs([f"🏟️ {v}" for v in existing_venues])
selected_race_uid = None

for i, v_name in enumerate(existing_venues):
    with venue_tabs[i]:
        v_df = df[df['競馬場名'] == v_name]
        races_in_v = v_df[['race_uid', 'race_id', 'R番号', 'track', 'dist']].drop_duplicates('race_uid').sort_values('R番号')
        
        race_options = {}
        for _, r_row in races_in_v.iterrows():
            n_horses = len(df[df['race_uid'] == r_row['race_uid']])
            lbl = f"{r_row['R番号']}R ({r_row['track']}{r_row['dist']}m / {n_horses}頭) [{r_row['race_id']}]"
            race_options[r_row['race_uid']] = lbl

        if race_options:
            chosen_uid = st.selectbox(
                f"{v_name}のレースを選択",
                options=list(race_options.keys()),
                format_func=lambda x: race_options[x],
                key=f"sel_race_{v_name}",
                label_visibility="collapsed"
            )
            if selected_race_uid is None:
                selected_race_uid = chosen_uid

if not selected_race_uid:
    selected_race_uid = df['race_uid'].iloc[0]

race_df = df[df['race_uid'] == selected_race_uid].copy().sort_values('馬番')
filtered_df = race_df.copy()


# --- フィルタリング処理（安全に条件適用） ---
if syn_iron:
    filtered_df = filtered_df[
        (filtered_df['F_rank'] == 1) &
        (filtered_df['arms_rank'] <= 3) &
        (filtered_df['wood_1F'] <= 11.5) &
        (filtered_df['is_wood_accel'] == True)
    ]

if syn_high:
    filtered_df = filtered_df[
        ((filtered_df['F_rank'] == 1) | (filtered_df['F指数'] >= 66)) &
        (filtered_df['wood_1F'] <= 11.5) &
        (filtered_df['is_wood_accel'] == True)
    ]

if syn_fup_sakaro:
    filtered_df = filtered_df[
        (filtered_df['Fup'] >= 5) &
        (filtered_df['坂路_完全加速'] == True)
    ]

if syn_bomb:
    filtered_df = filtered_df[
        (filtered_df['人気'] >= 6) &
        (filtered_df['Fup'] >= 4) &
        ((filtered_df['is_wood_accel'] == True) | (filtered_df['坂路_完全加速'] == True))
    ]

if pat_f1:
    filtered_df = filtered_df[filtered_df['F_rank'] == 1]

if pat_f66:
    filtered_df = filtered_df[filtered_df['F指数'] >= 66]

if pat_f1_arms3:
    filtered_df = filtered_df[(filtered_df['F_rank'] == 1) & (filtered_df['arms_rank'] <= 3)]

if pat_arms1:
    filtered_df = filtered_df[filtered_df['arms_rank'] == 1]

if pat_tua1:
    filtered_df = filtered_df[filtered_df['tua_rank'] == 1]

if pat_wood_top3:
    filtered_df = filtered_df[filtered_df['wood_5F_rank'] <= 3]


st.markdown("<hr style='border-color:#30363d;margin-top:10px;margin-bottom:15px;'>", unsafe_allow_html=True)


# --- 検索バー ---
st.markdown("### 📋 出走馬カード（調教最速・指数・血統バイアス完備）")

search_kw = st.text_input("🔍 馬名・調教師・騎手・父名で自由検索", placeholder="検索キーワードを入力...")
if search_kw:
    filtered_df = filtered_df[
        filtered_df['馬名'].str.contains(search_kw, na=False) |
        filtered_df['調教師'].str.contains(search_kw, na=False) |
        filtered_df['騎手'].str.contains(search_kw, na=False) |
        filtered_df['種牡馬'].str.contains(search_kw, na=False)
    ]


# --- 上部サマリーカウンター（安全集計） ---
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"<div class='metric-box'><div class='metric-label'>表示頭数</div><div class='metric-val'>{len(filtered_df)}頭</div></div>", unsafe_allow_html=True)
with c2:
    sakaro_accel_cnt = int((race_df['坂路_完全加速'] == True).sum()) if '坂路_完全加速' in race_df.columns else 0
    st.markdown(f"<div class='metric-box'><div class='metric-label'>坂路完全加速</div><div class='metric-val'>{sakaro_accel_cnt}頭</div></div>", unsafe_allow_html=True)
with c3:
    fup_high_cnt = int((race_df['Fup'] >= 5).sum()) if 'Fup' in race_df.columns else 0
    st.markdown(f"<div class='metric-box'><div class='metric-label'>Fup2(5点以上)</div><div class='metric-val'>{fup_high_cnt}頭</div></div>", unsafe_allow_html=True)
with c4:
    wood_accel_cnt = int((race_df['is_wood_accel'] == True).sum()) if 'is_wood_accel' in race_df.columns else 0
    st.markdown(f"<div class='metric-box'><div class='metric-label'>ウッド加速該当</div><div class='metric-val'>{wood_accel_cnt}頭</div></div>", unsafe_allow_html=True)

st.markdown("<hr style='border-color:#30363d;margin-top:8px;margin-bottom:20px;'>", unsafe_allow_html=True)


# --- 出走馬カード一覧の描画 ---
if filtered_df.empty:
    st.info("条件に一致する馬が見つかりませんでした。")
else:
    for _, row in filtered_df.iterrows():
        f_rank = row.get('F_rank', 99)
        f_val = row.get('F指数', 0.0)
        arms_rank = row.get('arms_rank', 99)
        tua_rank = row.get('tua_rank', 99)
        fup_val = row.get('Fup', 0)
        pop_val = row.get('人気', 99)
        
        is_w_accel = bool(row.get('is_wood_accel', False))
        w_1f = row.get('wood_1F', 99.0)
        is_s_accel = bool(row.get('坂路_完全加速', False))
        
        # 特注バッジ判定
        badges = []
        if f_rank == 1 and arms_rank <= 3 and w_1f <= 11.5 and is_w_accel:
            badges.append("<span class='badge-synergy badge-iron'>💎 鉄板軸馬 (複勝率61.9%)</span>")
        elif (f_rank == 1 or f_val >= 66) and w_1f <= 11.5 and is_w_accel:
            badges.append("<span class='badge-synergy badge-high'>🔥 高確率軸 (複勝率55%超)</span>")
            
        if fup_val >= 5 and is_s_accel:
            badges.append("<span class='badge-synergy badge-sakaro-fup'>✨ Fup坂路完全</span>")
            
        if f_rank == 1 and not (f_rank == 1 and arms_rank <= 3 and w_1f <= 11.5 and is_w_accel):
            badges.append("<span class='badge-synergy badge-f1'>👑 F1位</span>")
        elif f_val >= 66 and not (f_rank == 1 or (w_1f <= 11.5 and is_w_accel)):
            badges.append("<span class='badge-synergy badge-f1'>🔥 F66+</span>")
            
        if arms_rank == 1:
            badges.append("<span class='badge-synergy badge-arms1'>🚀 arms1位</span>")
            
        if tua_rank == 1:
            badges.append("<span class='badge-synergy badge-tua1'>🛡️ tua1位</span>")

        if pd.notnull(pop_val) and pop_val >= 6 and fup_val >= 4 and (is_w_accel or is_s_accel):
            badges.append("<span class='badge-synergy badge-bomb'>💣 爆弾穴馬</span>")

        badges_html = " ".join(badges)

        # ウッド調教テキスト（全Lap順位表記）
        if pd.notnull(row.get('wood_5F')):
            place = str(row.get('wood_place', ''))
            f5 = f"{row['wood_5F']:.1f}"
            accel = row.get('wood_accel', 0)
            accel_badge = f"<span class='badge-accel'>加速 +{accel:.1f}s</span>" if accel > 0 else f"<span class='badge-decel'>減速 {accel:.1f}s</span>"
            
            w_5f_rk = format_rank_badge(row.get('wood_5F_rank'))
            w_l4_rk = format_rank_badge(row.get('wood_Lap4_rank'))
            w_l3_rk = format_rank_badge(row.get('wood_Lap3_rank'))
            w_l2_rk = format_rank_badge(row.get('wood_Lap2_rank'))
            w_l1_rk = format_rank_badge(row.get('wood_Lap1_rank'))

            wood_info = f"{place} 5F: <strong>{f5}s</strong> ({w_5f_rk}) | {accel_badge} [ L4: {w_l4_rk} | L3: {w_l3_rk} | L2: {w_l2_rk} | L1: {w_l1_rk} ]"
        else:
            wood_info = "ウッド計測なし"

        # 坂路調教テキスト（全Lap順位表記）
        if pd.notnull(row.get('坂路_4F')):
            s_accel_str = "<span class='badge-accel'>完全加速</span>" if is_s_accel else "<span class='badge-decel'>非加速</span>"
            s_4f = f"{row['坂路_4F']:.1f}"
            
            s_4f_rk = format_rank_badge(row.get('坂路_4F_rank'))
            s_l4_rk = format_rank_badge(row.get('坂路_Lap4_rank'))
            s_l3_rk = format_rank_badge(row.get('坂路_Lap3_rank'))
            s_l2_rk = format_rank_badge(row.get('坂路_Lap2_rank'))
            s_l1_rk = format_rank_badge(row.get('坂路_Lap1_rank'))

            sakaro_info = f"4F: <strong>{s_4f}s</strong> ({s_4f_rk}) | {s_accel_str} [ L4: {s_l4_rk} | L3: {s_l3_rk} | L2: {s_l2_rk} | L1: {s_l1_rk} ]"
        else:
            sakaro_info = "坂路計測なし"

        u_no = row['馬番']
        umaban_str = f"{int(u_no)}番" if u_no != 99 and pd.notnull(u_no) else "番"
        pop_str = f"{int(row['人気'])} 番人気" if pd.notnull(row.get('人気')) else "- 番人気"
        fup_str = f"{int(row['Fup'])}点" if pd.notnull(row.get('Fup')) else "- 点"
        
        f_badge = format_rank_badge(row.get('F_rank'))
        arms_badge = format_rank_badge(row.get('arms_rank'))
        tua_badge = format_rank_badge(row.get('tua_rank'))

        # 純粋HTMLで完全レンダリング
        card_html = f"<div class='horse-card'><div class='horse-card-header'><span class='horse-card-title'>{umaban_str} {row['馬名']}</span> {badges_html}</div><ul class='horse-card-list'><li><strong>陣営/血統</strong>: {row.get('調教師', '-')} / {row.get('騎手', '-')} / <strong>父: {row.get('種牡馬', '-')}</strong></li><li><strong>坂路調教</strong>: {sakaro_info}</li><li><strong>ウッド調教</strong>: {wood_info}</li><li><strong>能力指数</strong>: F: <strong>{row.get('F指数', 0.0)}</strong> ({f_badge}) | ARMS: <strong>{row.get('arms', 0.0)}</strong> ({arms_badge}) | TUA: <strong>{row.get('tua', 0.0)}</strong> ({tua_badge})</li><li><strong>Fup数値</strong>: {fup_str} | <strong>人気</strong>: {pop_str}</li></ul></div>"

        st.markdown(card_html, unsafe_allow_html=True)
