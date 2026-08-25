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
        padding: 18px;
        border-radius: 10px;
        margin-bottom: 25px;
        border: 1px solid #30363d;
    }
    .metric-box {
        text-align: center;
    }
    .metric-label {
        font-size: 14px;
        color: #8b949e;
        margin-bottom: 4px;
    }
    .metric-val {
        font-size: 32px;
        font-weight: bold;
        color: #f0f6fc;
    }
    .horse-card {
        background-color: #161e2e;
        border-left: 5px solid #238636;
        padding: 16px 20px;
        border-radius: 8px;
        margin-bottom: 18px;
        border-top: 1px solid #30363d;
        border-right: 1px solid #30363d;
        border-bottom: 1px solid #30363d;
    }
    .horse-card-title {
        font-size: 20px;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 10px;
    }
    .horse-detail-item {
        font-size: 14px;
        color: #c9d1d9;
        margin-bottom: 6px;
        line-height: 1.6;
    }
    .badge-iron {
        background-color: #D4AF37;
        color: #000000;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 12px;
        margin-left: 8px;
    }
    .badge-high {
        background-color: #da3633;
        color: #ffffff;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 12px;
        margin-left: 8px;
    }
    .badge-accel {
        background-color: #238636;
        color: #ffffff;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 11px;
    }
    .badge-decel {
        background-color: #6e7681;
        color: #ffffff;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 11px;
    }
</style>
""", unsafe_allow_html=True)


# --- サイドバー: CSVアップローダー ---
st.sidebar.markdown("### 📁 CSVデータ読み込み")
uploaded_wood = st.sidebar.file_uploader("ウッド調教CSV", type=['csv'])
uploaded_index = st.sidebar.file_uploader("指数・レースCSV", type=['csv'])


# --- データロード＆前処理関数 ---
@st.cache_data
def load_and_process_data(wood_file_obj, index_file_obj):
    # 1. ウッド調教データの読み込み
    df_wood = pd.DataFrame()
    wood_src = wood_file_obj if wood_file_obj is not None else ('ウッド、検証用.csv' if os.path.exists('ウッド、検証用.csv') else None)
    
    if wood_src is not None:
        try:
            df_w = pd.read_csv(wood_src, encoding='shift-jis')
        except Exception:
            try:
                wood_src.seek(0)
            except Exception:
                pass
            df_w = pd.read_csv(wood_src, encoding='utf-8', errors='ignore')
        
        df_w = df_w[df_w['場所'] != '場所'].copy()
        for col in ['6F', '5F', '4F', '3F', '2F', '1F', 'Lap6', 'Lap5', 'Lap4', 'Lap3', 'Lap2', 'Lap1']:
            if col in df_w.columns:
                df_w[col] = pd.to_numeric(df_w[col], errors='coerce')
        
        df_w['馬名'] = df_w['馬名'].astype(str).str.strip()
        df_w['調教日'] = pd.to_datetime(df_w['年月日'].astype(str), format='%Y%m%d', errors='coerce')
        df_w = df_w[(df_w['5F'] > 50) & (df_w['5F'] < 90) & (df_w['1F'] < 30)]
        df_wood = df_w.sort_values('調教日').groupby('馬名').last().reset_index()

    # 2. 指数・レースデータの読み込み
    df_race = pd.DataFrame()
    index_src = index_file_obj if index_file_obj is not None else ('指数、検証用.csv' if os.path.exists('指数、検証用.csv') else None)
    
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

        records = []
        for line_idx, line in enumerate(lines):
            parts = [p.strip() for p in line.strip().split(',')]
            n = len(parts)
            if n < 10:
                continue

            race_id, track, dist, umaban, horse = parts[0], None, None, None, None
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
                sire = parts[23] if len(parts) > 23 else ""
            elif n == 23:
                track, dist, umaban = parts[1], parts[2], parts[3]
                horse = parts[4].replace('*', '').replace('$', '').strip()
                trainer, jockey = parts[6], parts[7]
                pop = parts[8]
                fup = pd.to_numeric(parts[10], errors='coerce')
                finish = parts[20]
                sire = parts[21] if len(parts) > 21 else ""
            elif n == 26:
                track, dist, umaban = parts[1], parts[2], parts[3]
                trainer, jockey = parts[5], parts[6]
                horse = parts[7].replace('*', '').replace('$', '').strip()
                pop = parts[8]
                f_val = pd.to_numeric(parts[12], errors='coerce')
                f_rank = pd.to_numeric(parts[13], errors='coerce')
                arms_val = pd.to_numeric(parts[18], errors='coerce')
                arms_rank = pd.to_numeric(parts[19], errors='coerce')
                tua_val = pd.to_numeric(parts[21], errors='coerce')
                tua_rank = pd.to_numeric(parts[22], errors='coerce')
                finish = parts[24]
                sire = parts[25] if len(parts) > 25 else ""

            if horse:
                fin_int = fw_map.get(finish, int(finish) if str(finish).isdigit() else np.nan)
                pop_int = int(pop) if str(pop).isdigit() else np.nan
                records.append({
                    'line_idx': line_idx,
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

        df_race = pd.DataFrame(records)

        # レース区分の識別（五十音順リセット判定）
        if not df_race.empty:
            resets = [0]
            for i in range(1, len(df_race)):
                h_curr = df_race.loc[i, '馬名']
                h_prev = df_race.loc[i - 1, '馬名']
                if h_curr < h_prev and (h_prev > 'マ' and h_curr < 'ウ'):
                    resets.append(i)
            resets.append(len(df_race))

            batch_ids = []
            for i in range(len(resets) - 1):
                batch_ids.extend([i] * (resets[i + 1] - resets[i]))
            df_race['batch_id'] = batch_ids
            df_race['race_uid'] = df_race['batch_id'].astype(str) + "_" + df_race['race_id']

    # 3. マージと調教順位・加速タイムの算出
    if not df_race.empty and not df_wood.empty:
        merged = pd.merge(df_race, df_wood, on='馬名', how='left')
    else:
        merged = df_race

    # ウッド指標の計算
    if not merged.empty:
        if '5F' in merged.columns and '1F' in merged.columns:
            merged['wood_accel'] = merged['Lap2'] - merged['Lap1']
            merged['is_wood_accel'] = merged['wood_accel'] > 0
            if 'race_uid' in merged.columns:
                merged['wood_5F_rank'] = merged.groupby('race_uid')['5F'].rank(method='min', ascending=True)
            else:
                merged['wood_5F_rank'] = np.nan
        else:
            merged['wood_accel'] = np.nan
            merged['is_wood_accel'] = False
            merged['wood_5F_rank'] = np.nan

    return merged


# データ読み込み実行
df = load_and_process_data(uploaded_wood, uploaded_index)

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

syn_iron = st.sidebar.checkbox(
    "💎 鉄板軸馬 (F1位 × arms3位内 × ウッド加速11.5s以下)",
    help="実測検証値: 複勝率 61.9% / 連対率 46.3% / 勝率 25.2%"
)
syn_high = st.sidebar.checkbox(
    "🔥 高確率軸馬 (F1位/66以上 × ウッド加速11.5s以下)",
    help="実測検証値: 複勝率 54.8〜59.0% / 連対率 40.7〜44.3%"
)
syn_fup_sakaro = st.sidebar.checkbox("✨ Fup2(5〜7点) × 坂路完全加速", help="坂路完全加速かつFup高評価")
syn_f1_rap = st.sidebar.checkbox("🔥 SSS級・F1位 × 究極ラップ (1F≤12.4s)")
syn_bomb = st.sidebar.checkbox("💣 爆弾穴馬 (6人気以下 × Fup2≥4 × 加速)")

st.sidebar.markdown("---")

# --- 能力指数フィルター ---
st.sidebar.markdown("### 📊 能力指数フィルター")
f_rank_1 = st.sidebar.checkbox("F指数 1位")
f_rank_3 = st.sidebar.checkbox("F指数 3位以内")
wood_top3 = st.sidebar.checkbox("ウッド5F 3位以内")


# --- メイン画面 ---
if df.empty:
    st.warning("⚠️ CSVデータが読み込まれていません。サイドバーの「📁 CSVデータ読み込み」から2つのファイルをアップロードするか、同じフォルダ内に配置してください。")
    st.stop()

# レース選択プルダウン
all_races = df['race_id'].unique().tolist()
selected_race_id = st.selectbox("🎯 対象レースを選択してください", all_races, index=0)

# 該当レースのデータ抽出
race_df = df[df['race_id'] == selected_race_id].copy()

# フィルタリング適用
filtered_df = race_df.copy()

if syn_iron:
    filtered_df = filtered_df[
        (filtered_df['F_rank'] == 1) &
        (filtered_df['arms_rank'] <= 3) &
        (filtered_df['1F'] <= 11.5) &
        (filtered_df['is_wood_accel'] == True)
    ]

if syn_high:
    filtered_df = filtered_df[
        ((filtered_df['F_rank'] == 1) | (filtered_df['F指数'] >= 66)) &
        (filtered_df['1F'] <= 11.5) &
        (filtered_df['is_wood_accel'] == True)
    ]

if f_rank_1:
    filtered_df = filtered_df[filtered_df['F_rank'] == 1]

if f_rank_3:
    filtered_df = filtered_df[filtered_df['F_rank'] <= 3]

if wood_top3:
    filtered_df = filtered_df[filtered_df['wood_5F_rank'] <= 3]

# 検索バー
st.markdown("### 📋 出走馬カード（調教最速・指数・ウッド検証完備）")
search_kw = st.text_input("🔍 馬名・調教師・騎手・父名で自由検索", placeholder="検索キーワードを入力...")
if search_kw:
    filtered_df = filtered_df[
        filtered_df['馬名'].str.contains(search_kw, na=False) |
        filtered_df['調教師'].str.contains(search_kw, na=False) |
        filtered_df['騎手'].str.contains(search_kw, na=False) |
        filtered_df['種牡馬'].str.contains(search_kw, na=False)
    ]

# 上部サマリーカウンター
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"<div class='metric-box'><div class='metric-label'>表示頭数</div><div class='metric-val'>{len(filtered_df)}頭</div></div>", unsafe_allow_html=True)
with c2:
    wood_accel_count = len(race_df[race_df['is_wood_accel'] == True])
    st.markdown(f"<div class='metric-box'><div class='metric-label'>ウッド加速該当</div><div class='metric-val'>{wood_accel_count}頭</div></div>", unsafe_allow_html=True)
with c3:
    fup_high_count = len(race_df[race_df['Fup'] >= 4])
    st.markdown(f"<div class='metric-box'><div class='metric-label'>Fup(4点以上)</div><div class='metric-val'>{fup_high_count}頭</div></div>", unsafe_allow_html=True)
with c4:
    st.markdown(f"<div class='metric-box'><div class='metric-label'>クッション特注馬</div><div class='metric-val'>0頭</div></div>", unsafe_allow_html=True)

st.markdown("<hr style='border-color:#30363d;margin-top:10px;margin-bottom:25px;'>", unsafe_allow_html=True)

# 出走馬カード一覧の描画
if filtered_df.empty:
    st.info("条件に一致する馬が見つかりませんでした。")
else:
    for _, row in filtered_df.iterrows():
        # ウッド調教テキスト整形
        if pd.notnull(row.get('5F')):
            place = str(row.get('場所', ''))
            f5 = f"{row['5F']:.1f}"
            f1 = f"{row['1F']:.1f}"
            accel = row.get('wood_accel', 0)
            
            if accel > 0:
                accel_badge = f"<span class='badge-accel'>加速 +{accel:.1f}s</span>"
            else:
                accel_badge = f"<span class='badge-decel'>減速 {accel:.1f}s</span>"
                
            rank_str = f"{int(row['wood_5F_rank'])}位" if pd.notnull(row.get('wood_5F_rank')) else "-位"
            wood_info = f"{place} (5F: {f5}s | 1F: {f1}s | {accel_badge} | レース内5F: {rank_str})"
        else:
            wood_info = "ウッド計測データなし"

        # 特注バッジ判定
        badge_html = ""
        is_accel = row.get('is_wood_accel', False)
        f1_val = row.get('1F', 99)
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
            <div class='horse-detail-item'>• <strong>ウッド調教</strong>: {wood_info}</div>
            <div class='horse-detail-item'>• <strong>能力指数</strong>: F: <strong>{row.get('F指数', 0.0)}</strong> ({row.get('F_rank', '-')}位) | ARMS: <strong>{row.get('arms', 0.0)}</strong> ({row.get('arms_rank', '-')}位) | TUA: <strong>{row.get('tua', 0.0)}</strong> ({row.get('tua_rank', '-')}位)</div>
            <div class='horse-detail-item'>• <strong>Fup数値</strong>: {fup_str} | <strong>人気</strong>: {pop_str}</div>
        </div>
        """, unsafe_allow_html=True)
