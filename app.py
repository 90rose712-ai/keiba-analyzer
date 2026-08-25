import streamlit as st
import pandas as pd
import numpy as np
import os

# --- ページ基本設定 ---
st.set_page_config(
    page_title="Streamlit - 競馬予想10 クッション値Vr",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSSスタイル（ダークテーマUI） ---
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
        padding: 14px 18px;
        border-radius: 8px;
        margin-bottom: 14px;
        border-top: 1px solid #30363d;
        border-right: 1px solid #30363d;
        border-bottom: 1px solid #30363d;
    }
    .horse-card-title {
        font-size: 18px;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 8px;
    }
    .horse-detail-item {
        font-size: 13.5px;
        color: #c9d1d9;
        margin-bottom: 4px;
        line-height: 1.5;
    }
    .badge-iron {
        background-color: #D4AF37;
        color: #000000;
        padding: 2px 7px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 11px;
        margin-left: 6px;
    }
    .badge-high {
        background-color: #da3633;
        color: #ffffff;
        padding: 2px 7px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 11px;
        margin-left: 6px;
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


# --- データロード＆4CSV統合処理 ---
@st.cache_data
def load_and_merge_all(f_index, f_gtv, f_sakaro, f_wood):
    # 1. 出馬表・指数 CSV
    df_race_raw = read_csv_flexible(f_index, ['出馬表_指数.csv', '指数、検証用.csv', '指数.csv'])
    
    records = []
    if not df_race_raw.empty:
        fw_map = {'１': 1, '２': 2, '３': 3, '４': 4, '５': 5, '６': 6, '７': 7, '８': 8, '９': 9, '10': 10,
                  '11': 11, '12': 12, '13': 13, '14': 14, '15': 15, '16': 16, '17': 17, '18': 18}
        
        for idx, row in df_race_raw.iterrows():
            vals = [str(x).strip() if pd.notnull(x) else "" for x in row.values]
            n = len(vals)
            race_id, track, dist, umaban, horse = vals[0], None, None, None, None
            trainer, jockey, sire = "", "", ""
            pop, finish, fup, f_val, f_rank = None, None, 0, 0.0, 99
            arms_val, arms_rank, tua_val, tua_rank = 0.0, 99, 0.0, 99

            if n >= 24:
                track, dist, umaban = vals[1], vals[2], vals[3]
                horse = vals[4].replace('*', '').replace('$', '').strip()
                trainer, jockey = vals[6], vals[7]
                pop = vals[8]
                fup = pd.to_numeric(vals[10], errors='coerce')
                f_val = pd.to_numeric(vals[13], errors='coerce')
                f_rank = pd.to_numeric(vals[14], errors='coerce')
                arms_val = pd.to_numeric(vals[16], errors='coerce')
                arms_rank = pd.to_numeric(vals[17], errors='coerce')
                tua_val = pd.to_numeric(vals[19], errors='coerce')
                tua_rank = pd.to_numeric(vals[20], errors='coerce')
                finish = vals[22]
                sire = vals[23] if n > 23 else ""
            elif n == 23:
                track, dist, umaban = vals[1], vals[2], vals[3]
                horse = vals[4].replace('*', '').replace('$', '').strip()
                trainer, jockey = vals[6], vals[7]
                pop = vals[8]
                fup = pd.to_numeric(vals[10], errors='coerce')
                finish = vals[20]
                sire = vals[21] if n > 21 else ""
            elif n >= 26:
                track, dist, umaban = vals[1], vals[2], vals[3]
                trainer, jockey = vals[5], vals[6]
                horse = vals[7].replace('*', '').replace('$', '').strip()
                pop = vals[8]
                f_val = pd.to_numeric(vals[12], errors='coerce')
                f_rank = pd.to_numeric(vals[13], errors='coerce')
                arms_val = pd.to_numeric(vals[18], errors='coerce')
                arms_rank = pd.to_numeric(vals[19], errors='coerce')
                tua_val = pd.to_numeric(vals[21], errors='coerce')
                tua_rank = pd.to_numeric(vals[22], errors='coerce')
                finish = vals[24]
                sire = vals[25] if n > 25 else ""
            else:
                continue

            if horse:
                fin_int = fw_map.get(finish, int(finish) if str(finish).isdigit() else np.nan)
                pop_int = int(pop) if str(pop).isdigit() else np.nan
                records.append({
                    'race_id': race_id,
                    'track': track,
                    'dist': dist,
                    '馬番': umaban,
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

    # レース区分ID付与
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

    # 2. GTVオッズ CSV
    df_gtv = read_csv_flexible(f_gtv, ['GTV馬.csv', 'GTV.csv'])
    if not df_gtv.empty:
        name_col = find_col(df_gtv, ['馬名', '馬 名', '競走馬名'])
        if name_col:
            df_gtv['馬名'] = df_gtv[name_col].astype(str).str.strip()
            gtv_cols = [c for c in df_gtv.columns if c not in ['馬名', name_col]]
            df_main = pd.merge(df_main, df_gtv[['馬名'] + gtv_cols].drop_duplicates('馬名'), on='馬名', how='left')

    # 3. 坂路調教 CSV (安全結合)
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

            if c_lap4 and c_lap3 and c_lap2 and c_lap1:
                l4 = pd.to_numeric(df_sakaro[c_lap4], errors='coerce')
                l3 = pd.to_numeric(df_sakaro[c_lap3], errors='coerce')
                l2 = pd.to_numeric(df_sakaro[c_lap2], errors='coerce')
                l1 = pd.to_numeric(df_sakaro[c_lap1], errors='coerce')
                df_sakaro['坂路_完全加速'] = (l4 > l3) & (l3 > l2) & (l2 > l1)
            else:
                df_sakaro['坂路_完全加速'] = False

            sakaro_sub = df_sakaro[['馬名', '坂路_4F', '坂路_1F', '坂路_完全加速']].drop_duplicates('馬名')
            df_main = pd.merge(df_main, sakaro_sub, on='馬名', how='left')

    # 坂路列が存在しない場合の初期化
    if '坂路_4F' not in df_main.columns:
        df_main['坂路_4F'] = np.nan
        df_main['坂路_1F'] = np.nan
        df_main['坂路_完全加速'] = False

    # 4. ウッド調教 CSV (安全結合)
    df_wood_raw = read_csv_flexible(f_wood, ['ウッド、検証用.csv', 'ウッド調教.csv', 'ウッド.csv'])
    if not df_wood_raw.empty:
        w_df = df_wood_raw[df_wood_raw.iloc[:, 0] != '場所'].copy()
        
        c_w_name = find_col(w_df, ['馬名', '馬 名', '競走馬名'])
        if c_w_name:
            w_df['馬名'] = w_df[c_w_name].astype(str).str.strip()
            
            c_w_5f = find_col(w_df, ['5F', '５Ｆ', '５F', '5f'])
            c_w_1f = find_col(w_df, ['1F', '１Ｆ', '１F', '1f'])
            c_w_l2 = find_col(w_df, ['Lap2', 'lap2', 'LAP2', 'L2'])
            c_w_l1 = find_col(w_df, ['Lap1', 'lap1', 'LAP1', 'L1'])
            c_w_plc = find_col(w_df, ['場所', '調教場', '場'])
            c_w_date = find_col(w_df, ['年月日', '日付', '日付S'])

            w_df['wood_5F'] = pd.to_numeric(w_df[c_w_5f], errors='coerce') if c_w_5f else np.nan
            w_df['wood_1F'] = pd.to_numeric(w_df[c_w_1f], errors='coerce') if c_w_1f else np.nan
            w_df['wood_Lap2'] = pd.to_numeric(w_df[c_w_l2], errors='coerce') if c_w_l2 else np.nan
            w_df['wood_Lap1'] = pd.to_numeric(w_df[c_w_l1], errors='coerce') if c_w_l1 else np.nan
            w_df['wood_place'] = w_df[c_w_plc].astype(str) if c_w_plc else ""

            if c_w_date:
                w_df['調教日'] = pd.to_datetime(w_df[c_w_date].astype(str), format='%Y%m%d', errors='coerce')
                w_latest = w_df.sort_values('調教日').groupby('馬名').last().reset_index()
            else:
                w_latest = w_df.groupby('馬名').last().reset_index()

            w_latest = w_latest[(w_latest['wood_5F'] > 50) & (w_latest['wood_5F'] < 90) & (w_latest['wood_1F'] < 30)]
            wood_sub = w_latest[['馬名', 'wood_place', 'wood_5F', 'wood_1F', 'wood_Lap2', 'wood_Lap1']].drop_duplicates('馬名')
            df_main = pd.merge(df_main, wood_sub, on='馬名', how='left')

    # ウッド指標の安全計算
    if 'wood_5F' in df_main.columns:
        df_main['wood_accel'] = df_main['wood_Lap2'] - df_main['wood_Lap1']
        df_main['is_wood_accel'] = df_main['wood_accel'] > 0
        df_main['wood_5F_rank'] = df_main.groupby('race_uid')['wood_5F'].rank(method='min', ascending=True)
    else:
        df_main['wood_5F'] = np.nan
        df_main['wood_1F'] = np.nan
        df_main['wood_accel'] = np.nan
        df_main['is_wood_accel'] = False
        df_main['wood_5F_rank'] = np.nan

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

# --- 黄金シナジー抽出 ---
st.sidebar.markdown("### 👑 黄金シナジー抽出")
syn_iron = st.sidebar.checkbox("💎 鉄板軸馬 (F1位 × arms3位内 × ウッド加速11.5s以下)", help="複勝率 61.9% / 連対率 46.3%")
syn_high = st.sidebar.checkbox("🔥 高確率軸馬 (F1位/66以上 × ウッド加速11.5s以下)", help="複勝率 54.8〜59.0%")
syn_fup_sakaro = st.sidebar.checkbox("✨ Fup2(5〜7点) × 坂路完全加速", help="坂路完全加速かつFup高評価")
syn_f1_rap = st.sidebar.checkbox("🔥 SSS級・F1位 × 究極ラップ (1F≤12.4s)")
syn_bomb = st.sidebar.checkbox("💣 爆弾穴馬 (6人気以下 × Fup2≥4 × 加速)")


# --- メイン画面 ---
if df.empty:
    st.warning("⚠️ CSVデータが読み込まれていません。サイドバーの「📁 4大CSVデータ読み込み」からファイルを指定するか、同一フォルダにCSVを配置してください。")
    st.stop()

# レース選択
all_races = df['race_id'].unique().tolist()
selected_race_id = st.selectbox("🎯 対象レースを選択してください", all_races, index=0)
race_df = df[df['race_id'] == selected_race_id].copy()

# フィルタリング初期化
filtered_df = race_df.copy()

# シナジー抽出フィルターの適用
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
        (filtered_df.get('坂路_完全加速', False) == True)
    ]

# --- 検索・詳細フィルターバー（基本検索 ＋ 指数専用検索欄） ---
st.markdown("### 📋 出走馬カード（調教最速・指数・血統バイアス完備）")

search_kw = st.text_input("🔍 馬名・調教師・騎手・父名で自由検索", placeholder="検索キーワードを入力...")
if search_kw:
    filtered_df = filtered_df[
        filtered_df['馬名'].str.contains(search_kw, na=False) |
        filtered_df['調教師'].str.contains(search_kw, na=False) |
        filtered_df['騎手'].str.contains(search_kw, na=False) |
        filtered_df['種牡馬'].str.contains(search_kw, na=False)
    ]

# 指数専用検索・フィルター欄
with st.expander("📊 指数・調教の詳細検索欄（F指数・ARMS・TUA・Fup・ウッド・坂路）", expanded=False):
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)
    with f_col1:
        f_rank_filter = st.selectbox("F指数順位", ["指定なし", "1位のみ", "3位以内", "5位以内"], index=0)
        f_min_val = st.number_input("F指数 最小値", min_value=0.0, max_value=100.0, value=0.0, step=5.0)
    with f_col2:
        arms_rank_filter = st.selectbox("ARMS順位", ["指定なし", "1位のみ", "3位以内", "5位以内"], index=0)
        tua_rank_filter = st.selectbox("TUA順位", ["指定なし", "1位のみ", "3位以内", "5位以内"], index=0)
    with f_col3:
        fup_min_filter = st.selectbox("Fup最小点数", ["指定なし", "4点以上", "5点以上", "6点以上"], index=0)
        wood_rank_filter = st.selectbox("ウッド5F順位", ["指定なし", "1位のみ", "3位以内", "5位以内"], index=0)
    with f_col4:
        wood_accel_only = st.checkbox("ウッド加速ラップのみ", value=False)
        sakaro_accel_only = st.checkbox("坂路完全加速のみ", value=False)

    # フィルター処理
    if f_rank_filter == "1位のみ":
        filtered_df = filtered_df[filtered_df['F_rank'] == 1]
    elif f_rank_filter == "3位以内":
        filtered_df = filtered_df[filtered_df['F_rank'] <= 3]
    elif f_rank_filter == "5位以内":
        filtered_df = filtered_df[filtered_df['F_rank'] <= 5]

    if f_min_val > 0.0:
        filtered_df = filtered_df[filtered_df['F指数'] >= f_min_val]

    if arms_rank_filter == "1位のみ":
        filtered_df = filtered_df[filtered_df['arms_rank'] == 1]
    elif arms_rank_filter == "3位以内":
        filtered_df = filtered_df[filtered_df['arms_rank'] <= 3]
    elif arms_rank_filter == "5位以内":
        filtered_df = filtered_df[filtered_df['arms_rank'] <= 5]

    if tua_rank_filter == "1位のみ":
        filtered_df = filtered_df[filtered_df['tua_rank'] == 1]
    elif tua_rank_filter == "3位以内":
        filtered_df = filtered_df[filtered_df['tua_rank'] <= 3]
    elif tua_rank_filter == "5位以内":
        filtered_df = filtered_df[filtered_df['tua_rank'] <= 5]

    if fup_min_filter == "4点以上":
        filtered_df = filtered_df[filtered_df['Fup'] >= 4]
    elif fup_min_filter == "5点以上":
        filtered_df = filtered_df[filtered_df['Fup'] >= 5]
    elif fup_min_filter == "6点以上":
        filtered_df = filtered_df[filtered_df['Fup'] >= 6]

    if wood_rank_filter == "1位のみ":
        filtered_df = filtered_df[filtered_df['wood_5F_rank'] == 1]
    elif wood_rank_filter == "3位以内":
        filtered_df = filtered_df[filtered_df['wood_5F_rank'] <= 3]
    elif wood_rank_filter == "5位以内":
        filtered_df = filtered_df[filtered_df['wood_5F_rank'] <= 5]

    if wood_accel_only:
        filtered_df = filtered_df[filtered_df['is_wood_accel'] == True]

    if sakaro_accel_only:
        filtered_df = filtered_df[filtered_df.get('坂路_完全加速', False) == True]


# --- 上部サマリーカウンター ---
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"<div class='metric-box'><div class='metric-label'>表示頭数</div><div class='metric-val'>{len(filtered_df)}頭</div></div>", unsafe_allow_html=True)
with c2:
    sakaro_accel_cnt = len(race_df[race_df.get('坂路_完全加速', False) == True])
    st.markdown(f"<div class='metric-box'><div class='metric-label'>坂路完全加速</div><div class='metric-val'>{sakaro_accel_cnt}頭</div></div>", unsafe_allow_html=True)
with c3:
    fup_high_cnt = len(race_df[race_df['Fup'] >= 5])
    st.markdown(f"<div class='metric-box'><div class='metric-label'>Fup2(5点以上)</div><div class='metric-val'>{fup_high_cnt}頭</div></div>", unsafe_allow_html=True)
with c4:
    wood_accel_cnt = len(race_df[race_df.get('is_wood_accel', False) == True])
    st.markdown(f"<div class='metric-box'><div class='metric-label'>ウッド加速該当</div><div class='metric-val'>{wood_accel_cnt}頭</div></div>", unsafe_allow_html=True)

st.markdown("<hr style='border-color:#30363d;margin-top:8px;margin-bottom:20px;'>", unsafe_allow_html=True)


# --- 出走馬カード一覧の描画 ---
if filtered_df.empty:
    st.info("条件に一致する馬が見つかりませんでした。")
else:
    for _, row in filtered_df.iterrows():
        # ウッド調教テキスト
        if pd.notnull(row.get('wood_5F')):
            place = str(row.get('wood_place', ''))
            f5 = f"{row['wood_5F']:.1f}"
            f1 = f"{row['wood_1F']:.1f}"
            accel = row.get('wood_accel', 0)
            
            if accel > 0:
                accel_badge = f"<span class='badge-accel'>加速 +{accel:.1f}s</span>"
            else:
                accel_badge = f"<span class='badge-decel'>減速 {accel:.1f}s</span>"
                
            rank_str = f"{int(row['wood_5F_rank'])}位" if pd.notnull(row.get('wood_5F_rank')) else "-位"
            wood_info = f"{place} (5F: {f5}s | 1F: {f1}s | {accel_badge} | レース内5F: {rank_str})"
        else:
            wood_info = "ウッド計測なし"

        # 坂路調教テキスト
        if pd.notnull(row.get('坂路_4F')):
            s_accel_str = "完全加速" if row.get('坂路_完全加速', False) else "非加速"
            sakaro_info = f"4F: {row['坂路_4F']:.1f}s | 1F: {row.get('坂路_1F', 0.0):.1f}s ({s_accel_str})"
        else:
            sakaro_info = "調教×（非加速/負荷なし）"

        # 特注バッジ判定
        badge_html = ""
        is_accel = row.get('is_wood_accel', False)
        f1_val = row.get('wood_1F', 99)
        f_rank = row.get('F_rank', 99)
        arms_rank = row.get('arms_rank', 99)
        f_val = row.get('F指数', 0)

        if f_rank == 1 and arms_rank <= 3 and f1_val <= 11.5 and is_accel:
            badge_html = "<span class='badge-iron'>💎 鉄板軸馬 (複勝率61.9%)</span>"
        elif (f_rank == 1 or f_val >= 66) and f1_val <= 11.5 and is_accel:
            badge_html = "<span class='badge-high'>🔥 高確率軸 (複勝率55%超)</span>"

        umaban_str = f"{int(row['馬番'])}番" if pd.notnull(row.get('馬番')) and str(row['馬番']).isdigit() else "番"
        pop_str = f"{int(row['人気'])} 番人気" if pd.notnull(row.get('人気')) else "- 番人気"
        fup_str = f"{int(row['Fup'])}点" if pd.notnull(row.get('Fup')) else "- 点"

        st.markdown(f"""
        <div class='horse-card'>
            <div class='horse-card-title'>{umaban_str} {row['馬名']} {badge_html}</div>
            <div class='horse-detail-item'>• <strong>陣営/血統</strong>: {row.get('調教師', '-')} / {row.get('騎手', '-')} / <strong>父: {row.get('種牡馬', '-')}</strong></div>
            <div class='horse-detail-item'>• <strong>坂路調教</strong>: {sakaro_info}</div>
            <div class='horse-detail-item'>• <strong>ウッド調教</strong>: {wood_info}</div>
            <div class='horse-detail-item'>• <strong>能力指数</strong>: F: <strong>{row.get('F指数', 0.0)}</strong> ({row.get('F_rank', '-')}位) | ARMS: <strong>{row.get('arms', 0.0)}</strong> ({row.get('arms_rank', '-')}位) | TUA: <strong>{row.get('tua', 0.0)}</strong> ({row.get('tua_rank', '-')}位)</div>
            <div class='horse-detail-item'>• <strong>Fup数値</strong>: {fup_str} | <strong>人気</strong>: {pop_str}</div>
        </div>
        """, unsafe_allow_html=True)
