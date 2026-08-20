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
    .badge-train { background-color: #FF8500; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
    .badge-combo { background-color: #7209B7; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
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

# CSVアップローダー（2ファイル対応）
col_u1, col_u2 = st.columns(2)
with col_u1:
    shutsuba_file = st.file_uploader("① 出走表CSV（全24項目）", type=["csv", "txt"])
with col_u2:
    chokyo_file = st.file_uploader("② 調教CSV（坂路・ウッド）", type=["csv", "txt"])

# CSV読み込み共通関数
def load_csv_safely(file):
    try:
        return pd.read_csv(file, encoding="cp932", header=None)
    except:
        file.seek(0)
        return pd.read_csv(file, encoding="utf-8", header=None)

if shutsuba_file is not None:
    df_shutsuba = load_csv_safely(shutsuba_file)
    
    # 出走表列マッピング
    col_names = [
        "RaceID", "TrackType", "Distance", "HorseNum", "HorseName", "Affiliation", 
        "Trainer", "Jockey", "PopRank", "GTV", "Fup2Val", "Fup2Rank", 
        "SIndex", "SRank", "FIndex", "FRank", "ARMS2Index", "ARMS2Rank", 
        "TUAIndex", "TUARank", "ResultRank", "Sire"
    ]
    df_shutsuba = df_shutsuba.iloc[:, :len(col_names)]
    df_shutsuba.columns = col_names[:df_shutsuba.shape[1]]
    
    # 文字列クリーニング
    for col in ["RaceID", "TrackType", "HorseName", "Trainer", "Jockey", "Sire", "GTV"]:
        if col in df_shutsuba.columns:
            df_shutsuba[col] = df_shutsuba[col].astype(str).str.strip()
            
    # 数値型変換
    num_cols = ["HorseNum", "PopRank", "Fup2Val", "Fup2Rank", "SIndex", "SRank", "FIndex", "FRank", "ARMS2Index", "ARMS2Rank", "TUAIndex", "TUARank"]
    for c in num_cols:
        if c in df_shutsuba.columns:
            df_shutsuba[c] = pd.to_numeric(df_shutsuba[c], errors="coerce").fillna(0)

    # 調教初期値
    df_shutsuba["Train_Track"] = "調教なし"
    df_shutsuba["Train_Time4F"] = 0.0
    df_shutsuba["Train_Lap1"] = 0.0
    df_shutsuba["Train_Lap2"] = 0.0
    df_shutsuba["Train_Lap3"] = 0.0
    df_shutsuba["Train_Pattern"] = "通常"
    df_shutsuba["Is_Hanro_Acc"] = False
    df_shutsuba["Is_Wood"] = False
    
    if chokyo_file is not None:
        df_chokyo = load_csv_safely(chokyo_file)
        try:
            # 調教コース列・馬名列
            # TARGET標準: 0:場所 1:日付 2:所属 3:コース区分(坂/W等) 4:馬名 ... 11:4F 12:Lap4 13:Lap3 14:Lap2 15:Lap1
            c_horse_col = 4 if df_chokyo.shape[1] > 4 else 0
            df_chokyo[c_horse_col] = df_chokyo[c_horse_col].astype(str).str.strip()
            
            for col_idx in range(8, min(df_chokyo.shape[1], 17)):
                df_chokyo[col_idx] = pd.to_numeric(df_chokyo[col_idx], errors="coerce").fillna(0)

            chokyo_dict = {}
            for _, row in df_chokyo.iterrows():
                h_name = row[c_horse_col]
                t_course = str(row[0]) if df_chokyo.shape[1] > 0 else ""
                
                # 坂路判定
                if df_chokyo.shape[1] >= 16:
                    t4 = row[11]
                    l4, l3, l2, l1 = row[12], row[13], row[14], row[15]
                    
                    is_hanro_acc = False
                    p_tag = "通常"
                    is_wood = "W" in t_course or "CW" in t_course or "南W" in t_course
                    
                    # 坂路完全加速の厳格判定: 4F <= 56.0s & 1F <= 13.0s & Lap4 > Lap3 > Lap2 > Lap1
                    if ("坂" in t_course or not is_wood) and (t4 <= 56.0 and l1 <= 13.0 and (l4 > l3 > l2 > l1 > 0)):
                        is_hanro_acc = True
                        if l1 <= 11.9:
                            p_tag = "A3(終い11秒台🔥)"
                        elif l1 <= 12.4:
                            p_tag = "A2(完全加速)"
                        else:
                            p_tag = "A1(完全加速)"
                    elif is_wood:
                        p_tag = "ウッド調整"

                    chokyo_dict[h_name] = {
                        "Track": t_course,
                        "Pattern": p_tag,
                        "Time4F": t4,
                        "Lap1": l1,
                        "Lap2": l2,
                        "Lap3": l3,
                        "Is_Hanro_Acc": is_hanro_acc,
                        "Is_Wood": is_wood
                    }
            
            # 出走表へ結合
            for idx, r in df_shutsuba.iterrows():
                h_name = r["HorseName"]
                if h_name in chokyo_dict:
                    df_shutsuba.at[idx, "Train_Track"] = chokyo_dict[h_name]["Track"]
                    df_shutsuba.at[idx, "Train_Pattern"] = chokyo_dict[h_name]["Pattern"]
                    df_shutsuba.at[idx, "Train_Time4F"] = chokyo_dict[h_name]["Time4F"]
                    df_shutsuba.at[idx, "Train_Lap1"] = chokyo_dict[h_name]["Lap1"]
                    df_shutsuba.at[idx, "Train_Lap2"] = chokyo_dict[h_name]["Lap2"]
                    df_shutsuba.at[idx, "Train_Lap3"] = chokyo_dict[h_name]["Lap3"]
                    df_shutsuba.at[idx, "Is_Hanro_Acc"] = chokyo_dict[h_name]["Is_Hanro_Acc"]
                    df_shutsuba.at[idx, "Is_Wood"] = chokyo_dict[h_name]["Is_Wood"]
        except Exception as e:
            st.warning(f"調教データマージ警告: {e}")

    # ================= 判定ロジック =================
    # 1. 絶対能力マトリクス
    df_shutsuba["Is_SSS"] = (df_shutsuba["FIndex"] >= 70.0) & (df_shutsuba["ARMS2Index"] >= 120.0) & (df_shutsuba["TUAIndex"] >= 200.0)
    df_shutsuba["Is_FourCrown"] = (df_shutsuba["FIndex"] >= 70.0) & (df_shutsuba["ARMS2Index"] >= 115.0) & (df_shutsuba["TUAIndex"] >= 190.0) & (df_shutsuba["SIndex"] >= 70.0)
    df_shutsuba["Is_F1_Lap124"] = (df_shutsuba["FRank"] == 1) & (df_shutsuba["Train_Lap1"] > 0) & (df_shutsuba["Train_Lap1"] <= 12.4)
    df_shutsuba["Is_Haran_Trigger"] = (df_shutsuba["PopRank"] >= 10) & (df_shutsuba["Train_Lap3"] <= 14.0) & (df_shutsuba["Train_Lap3"] > df_shutsuba["Train_Lap2"]) & (df_shutsuba["Train_Lap2"] > df_shutsuba["Train_Lap1"])

    # 2. クッション値×種牡馬バイアス
    def check_sire_bias(row):
        sire = row["Sire"]
        c_cat = cushion_cat
        # 超高帯チェック（PDF準拠）
        if "≥10.5" in c_cat:
            if sire in ["サートゥルナーリア", "ゴールドシップ", "キングカメハメハ", "ハービンジャー", "ビッグアーサー"]:
                return "⚠️超高帯危険血統(消し)"
            if sire in ["エピファネイア", "キタサンブラック", "イスラボニータ", "ロードカナロア"]:
                return "🔥超高帯特注血統"
        # 各コース特注
        if "9.5-9.9" in c_cat and venue == "阪神" and sire == "キズナ": return "🔥超買い(阪神芝1800外)"
        if "9.5-9.9" in c_cat and venue == "東京" and sire in ["エピファネイア", "モーリス", "ディープインパクト"]: return "🔥超買い(東京芝)"
        if "8.6-9.4" in c_cat and venue == "東京" and sire == "キズナ": return "🔥超買い(東京芝2000)"
        if "8.6-9.4" in c_cat and venue == "中京" and sire == "ディープインパクト": return "🔥超買い(中京芝2000)"
        # 危険
        if "9.5-9.9" in c_cat and venue == "中山" and sire == "ダノンバラード": return "⚠️危険(中山芝2000)"
        if "8.6-9.4" in c_cat and venue == "東京" and sire in ["シルバーステート", "ゴールドシップ", "エイシンフラッシュ"]: return "⚠️危険(東京芝)"
        if "8.6-9.4" in c_cat and venue == "小倉" and sire in ["ジャスタウェイ", "ヴィクトワールピサ"]: return "⚠️危険(小倉芝1200)"
        return "中立"

    df_shutsuba["SireBias"] = df_shutsuba.apply(check_sire_bias, axis=1)

    # 3. Fup2地雷/確変
    def check_fup2(row):
        val = row["Fup2Val"]
        pop = row["PopRank"]
        f_val = row["FIndex"]
        trainer = row["Trainer"]
        jockey = row["Jockey"]
        
        # 木村哲也×ルメール特例
        if "木村" in trainer and "ルメール" in jockey:
            if val >= 5: return "🌟木村ルメール勝負(勝率35%)"
            elif val <= 4: return "⚠️木村ルメール罠(勝率10%消し)"

        if val == 7: return "🌟確変(超高期待値)"
        if val >= 5: return "◎連軸信頼(Fup2強)"
        if val == 1 and pop <= 3:
            if f_val > 72.0 or row["Is_SSS"]:
                return "買(Fup2例外規定)"
            return "⚠️ダミー看破(消し)"
        return ""

    df_shutsuba["Fup2Tag"] = df_shutsuba.apply(check_fup2, axis=1)

    # ================= サイドバー: 指数×調教 掛け合わせ検索 =================
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎯 指数 × 調教 掛け合わせ抽出")
    
    combo_sss_acc = st.sidebar.checkbox("SSS級 × 坂路完全加速 (A1〜A3)")
    combo_f1_lap124 = st.sidebar.checkbox("F指数1位 × 坂路究極ラップ (1F≦12.4s)")
    combo_four_crown = st.sidebar.checkbox("指数四冠馬 (単回418%)")
    combo_wood_fup = st.sidebar.checkbox("ウッド調教 × Fup2(5点以上)")
    combo_haran = st.sidebar.checkbox("波乱の使者トリガー (10人気以下×連続加速)")
    combo_sire_acc = st.sidebar.checkbox("ナダル/スクリーンH × 坂路完全加速")

    # ================= UI 描画 =================
    races = df_shutsuba["RaceID"].unique()
    selected_race = st.sidebar.selectbox("🏁 レースを選択", races)
    
    race_df = df_shutsuba[df_shutsuba["RaceID"] == selected_race].copy()

    # 掛け合わせフィルター適用
    if combo_sss_acc:
        race_df = race_df[race_df["Is_SSS"] & race_df["Is_Hanro_Acc"]]
    if combo_f1_lap124:
        race_df = race_df[race_df["Is_F1_Lap124"]]
    if combo_four_crown:
        race_df = race_df[race_df["Is_FourCrown"]]
    if combo_wood_fup:
        race_df = race_df[race_df["Is_Wood"] & (race_df["Fup2Val"] >= 5)]
    if combo_haran:
        race_df = race_df[race_df["Is_Haran_Trigger"]]
    if combo_sire_acc:
        race_df = race_df[race_df["Sire"].isin(["ナダル", "スクリーンヒーロー"]) & race_df["Is_Hanro_Acc"]]

    # メイン画面サマリー表
    st.subheader(f"📊 {selected_race} 解析サマリー")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("SSS級神域", f"{len(race_df[race_df['Is_SSS']])}頭")
    c2.metric("坂路究極ラップ🔥", f"{len(race_df[race_df['Is_F1_Lap124']])}頭")
    c3.metric("坂路完全加速", f"{len(race_df[race_df['Is_Hanro_Acc']])}頭")
    c4.metric("ダミー消し馬", f"{len(race_df[race_df['Fup2Tag'].str.contains('消し')])}頭")

    st.write("---")
    st.subheader("📋 出走馬カード（スマホ最適化・掛け合わせ照合）")

    search_query = st.text_input("🔍 馬名・調教師・騎手・父名で自由検索", "")
    if search_query:
        race_df = race_df[race_df.apply(lambda r: search_query in str(r.values), axis=1)]

    for _, h in race_df.iterrows():
        with st.container():
            c_head, c_tags = st.columns([2, 3])
            c_head.markdown(f"### **{int(h['HorseNum'])}番 {h['HorseName']}**")
            
            tags = []
            if h["Is_SSS"]: tags.append("<span class='badge-sss'>SSS級</span>")
            if h["Is_FourCrown"]: tags.append("<span class='badge-sss'>四冠馬</span>")
            if h["Is_F1_Lap124"]: tags.append("<span class='badge-combo'>🔥F1×究極ラップ(12.4s)</span>")
            if h["Is_Hanro_Acc"]: tags.append(f"<span class='badge-train'>🔥坂路:{h['Train_Pattern']}</span>")
            if h["Is_Wood"]: tags.append("<span class='badge-train'>ウッド追</span>")
            if "🔥" in h["SireBias"]: tags.append(f"<span class='badge-bias'>{h['SireBias']}</span>")
            if "⚠️" in h["SireBias"]: tags.append(f"<span class='badge-risk'>{h['SireBias']}</span>")
            if h["Fup2Tag"]: tags.append(f"<span class='badge-bias'>{h['Fup2Tag']}</span>")
            
            c_tags.markdown(" ".join(tags), unsafe_allow_html=True)
            
            st.markdown(f"""
            - **陣営/血統**: **{h['Trainer']}** 厩舎 / **{h['Jockey']}** 騎手 / 父: **{h['Sire']}**
            - **調教時計**: [{h['Train_Track']}] 4F **{h['Train_Time4F']:.1f}s** - 終い **{h['Train_Lap1']:.1f}s**（判定: {h['Train_Pattern']}）
            - **能力指数**: F: **{h['FIndex']:.1f}** ({int(h['FRank'])}位) | ARMS2: **{h['ARMS2Index']:.1f}** ({int(h['ARMS2Rank'])}位) | TUA: **{h['TUAIndex']:.1f}** ({int(h['TUARank'])}位) | S: {h['SIndex']:.1f}
            - **Fup2数値**: **{int(h['Fup2Val'])}点** | 人気: {int(h['PopRank'])}番人気 | GTV: {h['GTV']}
            """)
            st.write("---")
else:
    st.info("👆 出走表CSV（全24項目）と調教CSVをアップロードしてください。サイドバーから指数×坂路・ウッドの掛け合わせ検索が利用可能です。")
