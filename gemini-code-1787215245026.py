import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="競馬予想10 クッション値Vr", page_icon="🏇", layout="wide")

# カスタムCSS（スマホ最適化）
st.markdown("""
<style>
    .reportview-container .main .block-container { max-width: 100%; padding: 1rem; }
    .stMetric { background-color: #1E222D; padding: 10px; border-radius: 8px; }
    .badge-sss { background-color: #D90429; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
    .badge-bias { background-color: #2B9348; color: white; padding: 2px 6px; border-radius: 4px; }
    .badge-risk { background-color: #555555; color: #FFAAAA; padding: 2px 6px; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

st.title("🏇 競馬予想10 クッション値Vr")

# サイドバー: パラメータ・馬場設定
st.sidebar.header("⚙️ 開催日・馬場環境設定")
venue = st.sidebar.selectbox("開催場所", ["東京", "中山", "京都", "阪神", "中京", "新潟", "小倉", "福島", "札幌", "函館"])
track_condition = st.sidebar.selectbox("芝馬場状態", ["良", "稍重", "重", "不良"])
cushion_val = st.sidebar.number_input("芝クッション値", min_value=5.0, max_value=13.0, value=9.5, step=0.1)

# クッション帯判定ロジック（場内相対基準対応）
def get_cushion_category(v_name, c_val):
    if v_name == "札幌":
        return "札幌場内低 (≤7.3)" if c_val <= 7.3 else ("札幌場内高 (≥7.7)" if c_val >= 7.7 else "札幌場内中")
    elif v_name == "函館":
        return "函館場内低 (≤7.2)" if c_val <= 7.2 else ("函館場内高 (≥7.5)" if c_val >= 7.5 else "函館場内中")
    else:
        if c_val <= 8.5: return "≤8.5 (低め)"
        elif 8.6 <= c_val <= 9.4: return "8.6-9.4 (やや低め)"
        elif 9.5 <= c_val <= 9.9: return "9.5-9.9 (標準高)"
        elif 10.0 <= c_val <= 10.4: return "10.0-10.4 (高め)"
        else: return "≥10.5 (超高)"

cushion_cat = get_cushion_category(venue, cushion_val)
st.sidebar.info(f"📍 判定帯: **{cushion_cat}**")

# CSVアップローダー
uploaded_file = st.file_uploader("TARGET出走表CSV（全24項目）をアップロード", type=["csv", "txt"])

if uploaded_file is not None:
    # エンコーディング自動判定・読み込み
    try:
        df = pd.read_csv(uploaded_file, encoding="cp932", header=None)
    except:
        df = pd.read_csv(uploaded_file, encoding="utf-8", header=None)
    
    # 列マッピング
    col_names = [
        "RaceID", "TrackType", "Distance", "HorseNum", "HorseName", "Affiliation", 
        "Trainer", "Jockey", "PopRank", "GTV", "Fup2Val", "Fup2Rank", 
        "SIndex", "SRank", "FIndex", "FRank", "ARMS2Index", "ARMS2Rank", 
        "TUAIndex", "TUARank", "ResultRank", "Sire"
    ]
    # 列数調整
    df = df.iloc[:, :len(col_names)]
    df.columns = col_names[:df.shape[1]]
    
    # クリーニング
    for col in ["RaceID", "TrackType", "HorseName", "Trainer", "Jockey", "Sire", "GTV"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    
    # 数値型変換
    num_cols = ["HorseNum", "PopRank", "Fup2Val", "SIndex", "FIndex", "ARMS2Index", "TUAIndex"]
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    # 判定ロジック適用
    # 1. SSS級
    df["Is_SSS"] = (df["FIndex"] >= 70.0) & (df["ARMS2Index"] >= 120.0) & (df["TUAIndex"] >= 200.0)
    # 2. 四冠馬
    df["Is_FourCrown"] = (df["FIndex"] >= 70.0) & (df["ARMS2Index"] >= 115.0) & (df["TUAIndex"] >= 190.0) & (df["SIndex"] >= 70.0)
    
    # クッション値×種牡馬バイアス判定（超高帯および特定組み合わせ）
    def check_sire_bias(row):
        sire = row["Sire"]
        c_cat = cushion_cat
        # 超高帯チェック
        if "≥10.5" in c_cat:
            if sire in ["サートゥルナーリア", "ゴールドシップ", "キングカメハメハ", "ハービンジャー", "ビッグアーサー"]:
                return "⚠️超高帯危険血統"
            if sire in ["エピファネイア", "キタサンブラック", "イスラボニータ", "ロードカナロア"]:
                return "🔥超高帯特注血統"
        # 危険判定例
        if "9.5-9.9" in c_cat and venue == "中山" and sire == "ダノンバラード": return "⚠️危険(中山芝2000等)"
        if "8.6-9.4" in c_cat and venue == "東京" and sire in ["シルバーステート", "ゴールドシップ", "エイシンフラッシュ"]: return "⚠️危険(東京芝)"
        # 買い判定例
        if "9.5-9.9" in c_cat and venue == "阪神" and sire == "キズナ": return "🔥超買い(阪神芝)"
        if "9.5-9.9" in c_cat and venue == "東京" and sire in ["エピファネイア", "モーリス", "ディープインパクト"]: return "🔥超買い(東京芝)"
        return "中立"

    df["SireBias"] = df.apply(check_sire_bias, axis=1)

    # Fup2地雷/確変判定
    def check_fup2(row):
        val = row["Fup2Val"]
        pop = row["PopRank"]
        f_val = row["FIndex"]
        if val == 7: return "🌟確変(超期待値)"
        if val >= 5: return "◎連軸信頼"
        if val == 1 and pop <= 3:
            if f_val > 72.0 or row["Is_SSS"]:
                return "買(Fup2例外規定)"
            return "⚠️ダミー看破(消し)"
        return ""

    df["Fup2Tag"] = df.apply(check_fup2, axis=1)

    # ================= UI 画面 =================
    # レース一覧フィルター
    races = df["RaceID"].unique()
    selected_race = st.selectbox("🏁 レースを選択", races)
    
    race_df = df[df["RaceID"] == selected_race].sort_values("HorseNum")
    
    # 歪みレース（悪条件カウント）
    st.subheader(f"📊 {selected_race} 解析レポート")
    
    # スマホ向けサマリー表示
    col1, col2, col3 = st.columns(3)
    sss_horses = race_df[race_df["Is_SSS"]]["HorseName"].tolist()
    four_horses = race_df[race_df["Is_FourCrown"]]["HorseName"].tolist()
    dummy_horses = race_df[race_df["Fup2Tag"].str.contains("ダミー")]["HorseName"].tolist()
    
    col1.metric("SSS級該当", f"{len(sss_horses)}頭", ", ".join(sss_horses) if sss_horses else "なし")
    col2.metric("四冠馬該当", f"{len(four_horses)}頭", ", ".join(four_horses) if four_horses else "なし")
    col3.metric("ダミー消し", f"{len(dummy_horses)}頭", ", ".join(dummy_horses) if dummy_horses else "なし")
    
    st.write("---")
    st.subheader("📋 出走馬マトリクス＆判定一覧")
    
    # 検索バー
    search_query = st.text_input("🔍 馬名・調教師・騎手・種牡馬で絞り込み", "")
    if search_query:
        race_df = race_df[race_df.apply(lambda r: search_query in str(r.values), axis=1)]

    # 出走馬カード表示（スマホ最適化）
    for _, h in race_df.iterrows():
        with st.container():
            c_head, c_tags = st.columns([2, 3])
            c_head.markdown(f"### **{int(h['HorseNum'])}番 {h['HorseName']}**")
            
            tags = []
            if h["Is_SSS"]: tags.append("<span class='badge-sss'>SSS級</span>")
            if h["Is_FourCrown"]: tags.append("<span class='badge-sss'>四冠馬</span>")
            if "🔥" in h["SireBias"]: tags.append(f"<span class='badge-bias'>{h['SireBias']}</span>")
            if "⚠️" in h["SireBias"]: tags.append(f"<span class='badge-risk'>{h['SireBias']}</span>")
            if h["Fup2Tag"]: tags.append(f"<span class='badge-bias'>{h['Fup2Tag']}</span>")
            
            c_tags.markdown(" ".join(tags), unsafe_allow_html=True)
            
            st.markdown(f"""
            - **陣営/血統**: {h['Trainer']}厩舎 / {h['Jockey']}騎手 / 父: {h['Sire']}
            - **能力指数**: F指数: **{h['FIndex']:.1f}** ({int(h['FRank'])}位) | ARMS2: **{h['ARMS2Index']:.1f}** ({int(h['ARMS2Rank'])}位) | TUA: **{h['TUAIndex']:.1f}** ({int(h['TUARank'])}位) | S指数: {h['SIndex']:.1f}
            - **Fup2数値**: **{int(h['Fup2Val'])}点** | 人気: {int(h['PopRank'])}番人気 | GTV印: {h['GTV']}
            """)
            st.write("---")