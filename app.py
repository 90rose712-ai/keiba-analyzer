import streamlit as st
import pandas as pd
import numpy as np
import glob
import os

# ページ基本設定
st.set_page_config(
    page_title="競馬予想10 クッション値Vr",
    page_icon="🐎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------
# 安全な文字列・数値変換ヘルパー関数
# -------------------------------------------------------------
def safe_int_str(val, default="-"):
    if pd.isna(val) or val == "" or str(val).strip().lower() == "nan":
        return default
    try:
        return str(int(float(val)))
    except Exception:
        return default

def safe_float_str(val, default="-"):
    if pd.isna(val) or val == "" or str(val).strip().lower() == "nan":
        return default
    try:
        return f"{float(val):.1f}"
    except Exception:
        return default

# -------------------------------------------------------------
# 1. データ読み込み関数（キャッシュ対応・空白ストリップ完備）
# -------------------------------------------------------------
@st.cache_data
def load_and_preprocess_data():
    shisu_files = glob.glob("*指数*.csv") + glob.glob("指数、検証用.csv")
    sakuro_files = glob.glob("*坂路*.csv") + glob.glob("坂路、検証用.csv")
    
    if not shisu_files:
        return None, None

    # 指数CSV読み込み
    shisu_path = shisu_files[0]
    lines = []
    for enc in ['cp932', 'shift_jis', 'utf-8', 'utf-8-sig']:
        try:
            with open(shisu_path, "r", encoding=enc, errors="replace") as f:
                for line in f:
                    parts = [p.strip() for p in line.strip().split(",")]
                    if len(parts) >= 22:
                        lines.append(parts[:22])
            if lines:
                break
        except Exception:
            continue

    col_names = [
        "場所レース番号", "芝ダ", "距離", "馬番", "馬名", "所属", "調教師", "騎手", 
        "人気順位", "印_GTV", "Fup2数値", "Fup2順位", "S指数", "S指数順位", 
        "F指数", "F指数順位", "ARMS2指数", "ARMS2順位", "TUA指数", "TUA順位", 
        "結果着順", "種牡馬"
    ]
    df_shisu = pd.DataFrame(lines, columns=col_names)

    # 数値変換
    num_cols = ["距離", "馬番", "人気順位", "Fup2数値", "Fup2順位", "S指数", "S指数順位", 
                "F指数", "F指数順位", "ARMS2指数", "ARMS2順位", "TUA指数", "TUA順位", "結果着順"]
    for col in num_cols:
        df_shisu[col] = pd.to_numeric(df_shisu[col], errors='coerce')

    # 文字列クリーニング
    df_shisu['horse_clean'] = df_shisu['馬名'].astype(str).str.strip().str.replace(' ', '')
    df_shisu['trainer_clean'] = df_shisu['調教師'].astype(str).str.strip()
    df_shisu['jockey_clean'] = df_shisu['騎手'].astype(str).str.strip()
    df_shisu['sire_clean'] = df_shisu['種牡馬'].astype(str).str.strip()
    df_shisu['place_code'] = df_shisu['場所レース番号'].astype(str).str.extract(r'^([^\d]+)')[0]
    
    place_map = {
        '東': '東京', '京': '京都', '中': '中山', '阪': '阪神', '名': '中京',
        '新': '新潟', '福': '福島', '小': '小倉', '札': '札幌', '函': '函館'
    }
    df_shisu['track'] = df_shisu['place_code'].map(place_map).fillna(df_shisu['場所レース番号'])

    # 坂路CSV読み込み
    df_sakuro = None
    if sakuro_files:
        sakuro_path = sakuro_files[0]
        for enc in ['cp932', 'shift_jis', 'utf-8', 'utf-8-sig']:
            try:
                df_sakuro = pd.read_csv(sakuro_path, encoding=enc)
                break
            except Exception:
                continue
            
    if df_sakuro is not None:
        df_sakuro.columns = [c.strip() for c in df_sakuro.columns]
        for c in ["Time1", "Time2", "Time3", "Time4", "Lap4", "Lap3", "Lap2", "Lap1"]:
            df_sakuro[c] = pd.to_numeric(df_sakuro[c], errors='coerce')
        
        df_sakuro['horse_clean'] = df_sakuro['馬名'].astype(str).str.strip().str.replace(' ', '')
        
        # 坂路完全加速判定（実質負荷基準：4F 56.0s以下 かつ 1F 13.0s以下）
        df_sakuro['is_perfect_accel'] = (
            (df_sakuro['Lap4'] > df_sakuro['Lap3']) & 
            (df_sakuro['Lap3'] > df_sakuro['Lap2']) & 
            (df_sakuro['Lap2'] > df_sakuro['Lap1']) & 
            (df_sakuro['Time1'] <= 56.0) & 
            (df_sakuro['Lap1'] <= 13.0)
        )
        df_sakuro['is_ultimate_lap'] = (df_sakuro['Lap1'] <= 12.4) & (df_sakuro['Time1'] <= 56.0)
        df_sakuro['is_fast_t1'] = (df_sakuro['Time1'] <= 53.0)
        df_sakuro['is_friday'] = (df_sakuro['曜日'] == '金')

        sakuro_agg = df_sakuro.groupby('horse_clean').agg(
            min_time1=('Time1', 'min'),
            min_lap1=('Lap1', 'min'),
            min_lap3=('Lap3', 'min'),
            has_perfect_accel=('is_perfect_accel', 'max'),
            has_ultimate_lap=('is_ultimate_lap', 'max'),
            has_fast_t1=('is_fast_t1', 'max'),
            has_friday_accel=('is_friday', lambda x: any(x & df_sakuro.loc[x.index, 'is_perfect_accel'])),
            training_count=('Time1', 'count')
        ).reset_index()

        df_merged = pd.merge(df_shisu, sakuro_agg, on='horse_clean', how='left')
    else:
        df_merged = df_shisu.copy()
        df_merged['has_perfect_accel'] = False
        df_merged['has_ultimate_lap'] = False
        df_merged['has_fast_t1'] = False
        df_merged['has_friday_accel'] = False
        df_merged['training_count'] = 0
        df_merged['min_time1'] = np.nan
        df_merged['min_lap1'] = np.nan

    # 欠損値補正
    df_merged['has_perfect_accel'] = df_merged['has_perfect_accel'].fillna(False).astype(bool)
    df_merged['has_ultimate_lap'] = df_merged['has_ultimate_lap'].fillna(False).astype(bool)
    df_merged['has_fast_t1'] = df_merged['has_fast_t1'].fillna(False).astype(bool)
    df_merged['has_friday_accel'] = df_merged['has_friday_accel'].fillna(False).astype(bool)
    df_merged['training_count'] = df_merged['training_count'].fillna(0).astype(int)

    return df_merged, df_sakuro

# -------------------------------------------------------------
# 2. クッション値×種牡馬バイアス判定ロジック
# -------------------------------------------------------------
def eval_sire_cushion_bias(track, dist, sire, cv_band, cv_val):
    sire_str = str(sire).strip()
    
    # 京都
    if track == "京都":
        if "≥10.5" in cv_band or cv_val >= 10.5:
            if sire_str in ["キタサンブラック", "エピファネイア", "イスラボニータ", "ロードカナロア", "ファインニードル"]:
                return "超買い", "京都×超高帯(≥10.5) 特注種牡馬[cite: 1]"
            if sire_str in ["キングカメハメハ", "ゴールドシップ", "サートゥルナーリア", "ビッグアーサー", "ハービンジャー"]:
                return "危険消し", "京都×超高帯(≥10.5) 危険種牡馬（大幅割引）[cite: 1]"
    
    # 札幌・函館（場内相対）
    elif track in ["札幌", "函館"]:
        if sire_str in ["キズナ", "オルフェーヴル", "ウインブライト", "ファインニードル", "ジョーカプチーノ", "ドゥラメンテ"]:
            return "超買い", f"{track}×低クッション特化種牡馬[cite: 1]"
        if sire_str in ["ディープインパクト", "エピファネイア", "ルーラーシップ", "ゴールドシップ"]:
            return "危険消し", f"{track}×低クッション危険種牡馬[cite: 1]"

    # 中山
    elif track == "中山":
        if "9.5-9.9" in cv_band:
            if sire_str in ["シルバーステート", "ディープインパクト", "ハービンジャー"]:
                return "超買い", "中山芝×9.5-9.9 標準高 特注種牡馬[cite: 1]"
            if sire_str in ["ダノンバラード"]:
                return "危険消し", "中山芝2000×9.5-9.9 勝率0% 危険種牡馬[cite: 1]"
        if ("≥10.5" in cv_band or cv_val >= 10.5) and sire_str in ["ゴールドシップ"]:
            return "危険消し", "中山芝×超高帯(≥10.5) 危険種牡馬[cite: 1]"

    # 阪神
    elif track == "阪神":
        if "9.5-9.9" in cv_band and sire_str in ["キズナ", "ディープインパクト", "ドゥラメンテ"]:
            return "超買い", "阪神外回り×9.5-9.9 標準高 特注種牡馬[cite: 1]"
        if "9.5-9.9" in cv_band and sire_str in ["ハービンジャー", "ルーラーシップ", "ロードカナロア"]:
            return "危険消し", "阪神芝1800外×9.5-9.9 危険種牡馬[cite: 1]"
        if "8.6-9.4" in cv_band and sire_str in ["ルーラーシップ", "キズナ"]:
            return "超買い", "阪神芝×8.6-9.4 やや低 特注種牡馬[cite: 1]"

    # 東京
    elif track == "東京":
        if "9.5-9.9" in cv_band:
            if sire_str in ["エピファネイア", "モーリス", "ディープインパクト"]:
                return "超買い", "東京芝×9.5-9.9 標準高 瞬発力特注種牡馬[cite: 1]"
            if sire_str in ["ルーラーシップ", "ゴールドシップ", "シルバーステート"]:
                return "危険消し", "東京芝×9.5-9.9 危険種牡馬[cite: 1]"
        if "8.6-9.4" in cv_band:
            if sire_str in ["キズナ", "エピファネイア", "ロードカナロア", "イスラボニータ"]:
                return "超買い", "東京芝×8.6-9.4 やや低 特注種牡馬[cite: 1]"
            if sire_str in ["シルバーステート", "ゴールドシップ", "エイシンフラッシュ", "サトノクラウン", "オルフェーヴル"]:
                return "危険消し", "東京芝×8.6-9.4 危険種牡馬[cite: 1]"

    # 福島・小倉・新潟
    elif track in ["福島", "小倉", "新潟"]:
        if sire_str in ["ビッグアーサー", "ダノンバラード", "ダイワメジャー", "ロードカナロア"]:
            return "超買い", f"{track}×ローカル適性種牡馬[cite: 1]"
        if sire_str in ["ジャスタウェイ", "ヴィクトワールピサ", "マツリダゴッホ", "カレンブラックヒル", "リオンディーズ"]:
            return "危険消し", f"{track}×危険種牡馬[cite: 1]"

    return "標準", ""

# -------------------------------------------------------------
# 3. アプリケーションメイン
# -------------------------------------------------------------
df_all, df_sakuro = load_and_preprocess_data()

if df_all is None:
    st.error("⚠️ CSVファイル（`指数、検証用.csv`）が見つかりません。")
    st.stop()

# --- サイドバー描画 ---
st.sidebar.markdown("## ⚙️ 開催日・馬場環境設定")

available_places = [p for p in ["東京", "中山", "京都", "阪神", "中京", "新潟", "福島", "小倉", "札幌", "函館"] if p in df_all['track'].values]
if not available_places:
    available_places = ["東京", "中山", "京都", "阪神", "中京", "新潟", "福島", "小倉", "札幌", "函館"]

place = st.sidebar.selectbox("開催場所", available_places)
track_condition = st.sidebar.selectbox("芝馬場状態", ["良", "稍重", "重", "不良"])

cushion_val = st.sidebar.number_input(
    "芝クッション値",
    min_value=5.0,
    max_value=13.0,
    value=9.5,
    step=0.1,
    format="%.1f"
)

# 競馬場別・場内相対判定
def get_cushion_band(place_name, val):
    if place_name == "札幌":
        if val <= 7.3: return "札幌相対：場内低め(≤7.3)"
        elif val >= 7.7: return "札幌相対：場内高め(≥7.7)"
        else: return "札幌相対：場内標準(7.4-7.6)"
    elif place_name == "函館":
        if val <= 7.2: return "函館相対：場内低め(≤7.2)"
        elif val >= 7.5: return "函館相対：場内高め(≥7.5)"
        else: return "函館相対：場内標準(7.3-7.4)"
    else:
        if val < 8.6: return "≤8.5 (低め)"
        elif val <= 9.4: return "8.6-9.4 (やや低め)"
        elif val <= 9.9: return "9.5-9.9 (標準高)"
        elif val <= 10.4: return "10.0-10.4 (高め)"
        else: return "≥10.5 (超高帯🔥)"

cushion_band_str = get_cushion_band(place, cushion_val)
badge_bg = "#dc2626" if "≥10.5" in cushion_band_str else ("#2563eb" if "≤8.5" in cushion_band_str or "低め" in cushion_band_str else "#059669")

st.sidebar.markdown(
    f"""
    <div style="background-color: {badge_bg}; padding: 8px 12px; border-radius: 6px; color: white; font-weight: bold; text-align: center; margin-bottom: 12px;">
        📍 判定帯: {cushion_band_str}
    </div>
    """,
    unsafe_allow_html=True
)

if st.sidebar.button("🔄 最新データへ強制再読み込み", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")

# 黄金シナジー抽出
st.sidebar.markdown("## 👑 黄金シナジー抽出")
filter_gold_fup = st.sidebar.checkbox("🌟 Fup2(5〜7点) × 坂路完全加速", help="勝率12.2%・複勝率32.7%の超鉄板連軸候補")
filter_sss_f1 = st.sidebar.checkbox("🔥 SSS級・F1位 × 究極ラップ(1F≤12.4s)", help="複勝率40.6〜48.6%の究極軸馬")
filter_bomb_ana = st.sidebar.checkbox("💣 爆弾穴馬 (6人気以下×Fup2≥4×加速)", help="複勝率14.2%の特大ヒモ穴トリガー")

st.sidebar.markdown("---")

# 能力指数フィルター
st.sidebar.markdown("## 📊 能力指数フィルター")
f_rank1 = st.sidebar.checkbox("F指数 1位")
f_rank3 = st.sidebar.checkbox("F指数 3位以内")
f_val70 = st.sidebar.checkbox("F指数 70.0以上")
arms_rank3 = st.sidebar.checkbox("ARMS2 3位以内")
tua_rank3 = st.sidebar.checkbox("TUA 3位以内")

fup2_option = st.sidebar.selectbox(
    "Fup2数値（点数）フィルター",
    ["全表示", "5点以上（確変・超高期待値）", "4点以上（好走・爆弾馬）", "7点（最高評価）", "1点（ダミー警戒）"]
)

st.sidebar.markdown("---")

# 坂路調教フィルター
st.sidebar.markdown("## ⏱️ 坂路調教フィルター")
accel_only = st.sidebar.checkbox("坂路完全加速（A1〜A3）のみ", help="4F≤56.0s かつ 1F≤13.0s の完全加速")
lap1_124 = st.sidebar.checkbox("ラスト1F 12.4秒以下（究極ラップ）")
time1_53 = st.sidebar.checkbox("4F全体時計 53.0秒以下（勝負時計）")
training_11 = st.sidebar.checkbox("調教本数 11回以上（入念仕上げ）")
friday_accel = st.sidebar.checkbox("前日（金曜）坂路仕上げ馬")

st.sidebar.markdown("---")

# 血統バイアスフィルター
st.sidebar.markdown("## 🧬 クッション値×血統適性")
sire_bias_opt = st.sidebar.radio(
    "血統バイアス抽出",
    ["全頭", "超買い特注馬のみ表示", "危険消し馬を除外", "危険消し馬のみ表示"]
)

# -------------------------------------------------------------
# 4. データフィルタリング処理
# -------------------------------------------------------------
df_view = df_all[df_all['track'] == place].copy()

if df_view.empty:
    st.warning(f"現在選択された場所（{place}）のデータが存在しません。")
    st.stop()

# レース選択
race_list = sorted(df_view['場所レース番号'].dropna().unique())
selected_race = st.selectbox("🎯 対象レースを選択してください", race_list)

df_race = df_view[df_view['場所レース番号'] == selected_race].copy()

# クッション値バイアス付与
df_race[['sire_bias', 'sire_desc']] = df_race.apply(
    lambda r: pd.Series(eval_sire_cushion_bias(place, r['距離'], r['sire_clean'], cushion_band_str, cushion_val)),
    axis=1
)

# フィルタリング適用
if filter_gold_fup:
    df_race = df_race[(df_race['Fup2数値'] >= 5) & (df_race['has_perfect_accel'] == True)]

if filter_sss_f1:
    df_race = df_race[(df_race['F指数順位'] == 1) & (df_race['has_ultimate_lap'] == True)]

if filter_bomb_ana:
    df_race = df_race[(df_race['人気順位'] >= 6) & (df_race['Fup2数値'] >= 4) & (df_race['has_perfect_accel'] == True)]

if f_rank1:
    df_race = df_race[df_race['F指数順位'] == 1]
if f_rank3:
    df_race = df_race[df_race['F指数順位'] <= 3]
if f_val70:
    df_race = df_race[df_race['F指数'] >= 70.0]
if arms_rank3:
    df_race = df_race[df_race['ARMS2順位'] <= 3]
if tua_rank3:
    df_race = df_race[df_race['TUA順位'] <= 3]

if fup2_option == "5点以上（確変・超高期待値）":
    df_race = df_race[df_race['Fup2数値'] >= 5]
elif fup2_option == "4点以上（好走・爆弾馬）":
    df_race = df_race[df_race['Fup2数値'] >= 4]
elif fup2_option == "7点（最高評価）":
    df_race = df_race[df_race['Fup2数値'] == 7]
elif fup2_option == "1点（ダミー警戒）":
    df_race = df_race[df_race['Fup2数値'] == 1]

if accel_only:
    df_race = df_race[df_race['has_perfect_accel'] == True]
if lap1_124:
    df_race = df_race[df_race['has_ultimate_lap'] == True]
if time1_53:
    df_race = df_race[df_race['has_fast_t1'] == True]
if training_11:
    df_race = df_race[df_race['training_count'] >= 11]
if friday_accel:
    df_race = df_race[df_race['has_friday_accel'] == True]

if sire_bias_opt == "超買い特注馬のみ表示":
    df_race = df_race[df_race['sire_bias'] == "超買い"]
elif sire_bias_opt == "危険消し馬を除外":
    df_race = df_race[df_race['sire_bias'] != "危険消し"]
elif sire_bias_opt == "危険消し馬のみ表示":
    df_race = df_race[df_race['sire_bias'] == "危険消し"]

# -------------------------------------------------------------
# 5. メイン画面描画
# -------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("表示頭数", f"{len(df_race)}頭")
c2.metric("坂路完全加速", f"{len(df_race[df_race['has_perfect_accel'] == True])}頭")
c3.metric("Fup2(5点以上)", f"{len(df_race[df_race['Fup2数値'] >= 5])}頭")
c4.metric("クッション特注馬", f"{len(df_race[df_race['sire_bias'] == '超買い'])}頭")

st.markdown("---")
st.markdown("### 📋 出走馬カード（調教最速・指数・血統バイアス完備）")

search_kw = st.text_input("🔍 馬名・調教師・騎手・父名で自由検索", "")
if search_kw:
    df_race = df_race[
        df_race['馬名'].astype(str).str.contains(search_kw, na=False) |
        df_race['調教師'].astype(str).str.contains(search_kw, na=False) |
        df_race['騎手'].astype(str).str.contains(search_kw, na=False) |
        df_race['種牡馬'].astype(str).str.contains(search_kw, na=False)
    ]

# 出走馬カード出力
for _, horse in df_race.sort_values(by='馬番', na_position='last').iterrows():
    h_num = safe_int_str(horse['馬番'], default="")
    h_name = str(horse['馬名']).strip()
    
    # GTV印
    gtv_badge = f"<span style='background-color: #f59e0b; color: black; padding: 2px 6px; border-radius: 4px; font-weight: bold;'>印:{horse['印_GTV']}</span>" if pd.notna(horse['印_GTV']) and str(horse['印_GTV']).strip() != '' else ""
    
    # 血統バイアルバッジ
    if horse['sire_bias'] == "超買い":
        sire_badge = "<span style='background-color: #dc2626; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold;'>🔥 血統超買い</span>"
    elif horse['sire_bias'] == "危険消し":
        sire_badge = "<span style='background-color: #4b5563; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold;'>⚠️ 危険血統消し</span>"
    else:
        sire_badge = ""

    # 坂路調教バッジ
    if horse['has_perfect_accel']:
        accel_badge = "<span style='color: #10b981; font-weight: bold;'>【坂路完全加速(A1〜A3)達成】</span>"
    else:
        accel_badge = "<span style='color: #9ca3af;'>調教×（非加速/負荷なし）</span>"

    # Fup2カラー判定
    fup2_val = horse['Fup2数値']
    if pd.notna(fup2_val) and float(fup2_val) >= 5:
        fup2_color = "#ef4444"
    elif pd.notna(fup2_val) and float(fup2_val) == 4:
        fup2_color = "#f59e0b"
    else:
        fup2_color = "#9ca3af"

    t_cnt = safe_int_str(horse['training_count'], default="0")
    t1_val = safe_float_str(horse['min_time1'])
    lap1_val = safe_float_str(horse['min_lap1'])
    
    f_val = safe_float_str(horse['F指数'])
    f_rk = safe_int_str(horse['F指数順位'])
    arms_val = safe_float_str(horse['ARMS2指数'])
    arms_rk = safe_int_str(horse['ARMS2順位'])
    tua_val = safe_float_str(horse['TUA指数'])
    tua_rk = safe_int_str(horse['TUA順位'])
    s_val = safe_float_str(horse['S指数'])
    pop_rk = safe_int_str(horse['人気順位'])
    fup2_str = safe_int_str(horse['Fup2数値'])

    sire_desc_str = str(horse['sire_desc']) if horse['sire_desc'] else "基準内"

    st.markdown(
        f"""
        <div style="background-color: #1e293b; padding: 16px; border-radius: 8px; margin-bottom: 12px; border-left: 5px solid {badge_bg};">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 1.2rem; font-weight: bold; color: white;">{h_num}番 {h_name}</span>
                <div>{gtv_badge} {sire_badge}</div>
            </div>
            <ul style="color: #cbd5e1; font-size: 0.95rem; margin-bottom: 0px; padding-left: 20px;">
                <li><b>陣営/血統:</b> {horse['調教師']} / {horse['騎手']} / <b>父: {horse['種牡馬']}</b> ({sire_desc_str})</li>
                <li><b>坂路調教:</b> {accel_badge} (最速4F: {t1_val}s | 最速1F: {lap1_val}s | 登坂数: {t_cnt}回)</li>
                <li><b>能力指数:</b> F: <b>{f_val}</b> ({f_rk}位) | ARMS2: <b>{arms_val}</b> ({arms_rk}位) | TUA: <b>{tua_val}</b> ({tua_rk}位) | S: {s_val}</li>
                <li><b>Fup2数値:</b> <span style="color: {fup2_color}; font-weight: bold;">{fup2_str}点</span> | <b>人気:</b> {pop_rk} 番人気</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )
