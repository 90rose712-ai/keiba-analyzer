import streamlit as st
import pandas as pd
import numpy as np
import os
import re

st.set_page_config(page_title="競馬予想10 クッション値Vr", page_icon="🏇", layout="wide")

# カスタムCSS（スマホ最適化）
st.markdown("""
<style>
    .reportview-container .main .block-container { max-width: 100%; padding: 1rem; }
    .stMetric { background-color: #1E222D; padding: 10px; border-radius: 8px; }
    .badge-sss { background-color: #D90429; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
    .badge-four { background-color: #B5179E; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
    .badge-bias { background-color: #2B9348; color: white; padding: 2px 6px; border-radius: 4px; }
    .badge-risk { background-color: #555555; color: #FFAAAA; padding: 2px 6px; border-radius: 4px; }
    .badge-hanro { background-color: #FF8500; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
    .badge-wood { background-color: #3A86FF; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
    .badge-combo { background-color: #7209B7; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
    .badge-gtv { background-color: #FFB703; color: black; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
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

# CSV安全読み込み関数
def load_csv_candidates(candidates):
    for path in candidates:
        if os.path.exists(path) and os.path.getsize(path) > 0:
            try:
                df_read = pd.read_csv(path, encoding="cp932", header=None)
                if not df_read.empty: return df_read
            except Exception:
                try:
                    df_read = pd.read_csv(path, encoding="utf-8", header=None)
                    if not df_read.empty: return df_read
                except Exception:
                    continue
    return None

SHUTSUBA_CANDIDATES = ["data/出馬表_指数.csv", "data/shutsuba.csv", "data/出馬表.csv"]
HANRO_CANDIDATES = ["data/出馬表_坂路.csv", "data/hanro.csv", "data/坂路.csv"]
WOOD_CANDIDATES = ["data/出馬表_ウッド.csv", "data/wood.csv", "data/ウッド.csv"]
GTV_CANDIDATES = ["data/GTV馬.csv", "data/gtv.csv", "data/GTV.csv"]

df_raw = load_csv_candidates(SHUTSUBA_CANDIDATES)

if df_raw is not None:
    col_names = [
        "RaceID", "TrackType", "Distance", "HorseNum", "HorseName", "Affiliation", 
        "Trainer", "Jockey", "PopRank", "GTV", "Fup2Val", "Fup2Rank", 
        "SIndex", "SRank", "FIndex", "FRank", "ARMS2Index", "ARMS2Rank", 
        "TUAIndex", "TUARank", "ResultRank", "Sire"
    ]
    df = df_raw.iloc[:, :len(col_names)].copy()
    df.columns = col_names[:df.shape[1]]
    
    for col in ["RaceID", "TrackType", "HorseName", "Trainer", "Jockey", "Sire", "GTV"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            
    num_cols = ["HorseNum", "PopRank", "Fup2Val", "Fup2Rank", "SIndex", "SRank", "FIndex", "FRank", "ARMS2Index", "ARMS2Rank", "TUAIndex", "TUARank"]
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    df["Hanro_4F"] = 0.0
    df["Hanro_1F"] = 0.0
    df["Hanro_2F"] = 0.0
    df["Hanro_3F"] = 0.0
    df["Hanro_Pattern"] = "通常"
    df["Is_Hanro_Acc"] = False
    
    df["Wood_6F"] = 0.0
    df["Wood_1F"] = 0.0
    df["Wood_Track"] = "なし"
    df["Is_Wood"] = False

    # ② 坂路調教マージ
    df_h = load_csv_candidates(HANRO_CANDIDATES)
    if df_h is not None:
        try:
            h_name_idx = 4 if df_h.shape[1] > 4 else 0
            df_h[h_name_idx] = df_h[h_name_idx].astype(str).str.strip()
            for ci in range(8, min(df_h.shape[1], 17)):
                df_h[ci] = pd.to_numeric(df_h[ci], errors="coerce").fillna(0)

            hanro_dict = {}
            for _, r in df_h.iterrows():
                hn = r[h_name_idx]
                if df_h.shape[1] >= 16:
                    t4 = r[11]
                    l4, l3, l2, l1 = r[12], r[13], r[14], r[15]
                    is_acc = False
                    p_tag = "通常"
                    if t4 <= 56.0 and l1 <= 13.0 and (l4 > l3 > l2 > l1 > 0):
                        is_acc = True
                        if l1 <= 11.9: p_tag = "A3(終い11秒台🔥)"
                        elif l1 <= 12.4: p_tag = "A2(完全加速)"
                        else: p_tag = "A1(完全加速)"
                    
                    hanro_dict[hn] = {
                        "4F": t4, "1F": l1, "2F": l2, "3F": l3,
                        "Pattern": p_tag, "Is_Acc": is_acc
                    }
            for idx, r in df.iterrows():
                hn = r["HorseName"]
                if hn in hanro_dict:
                    df.at[idx, "Hanro_4F"] = hanro_dict[hn]["4F"]
                    df.at[idx, "Hanro_1F"] = hanro_dict[hn]["1F"]
                    df.at[idx, "Hanro_2F"] = hanro_dict[hn]["2F"]
                    df.at[idx, "Hanro_3F"] = hanro_dict[hn]["3F"]
                    df.at[idx, "Hanro_Pattern"] = hanro_dict[hn]["Pattern"]
                    df.at[idx, "Is_Hanro_Acc"] = hanro_dict[hn]["Is_Acc"]
        except Exception:
            pass

    # ③ ウッド調教マージ
    df_w = load_csv_candidates(WOOD_CANDIDATES)
    if df_w is not None:
        try:
            w_name_idx = 4 if df_w.shape[1] > 4 else 0
            df_w[w_name_idx] = df_w[w_name_idx].astype(str).str.strip()
            for ci in range(8, min(df_w.shape[1], 17)):
                df_w[ci] = pd.to_numeric(df_w[ci], errors="coerce").fillna(0)

            wood_dict = {}
            for _, r in df_w.iterrows():
                hn = r[w_name_idx]
                w_track = str(r[0]) if df_w.shape[1] > 0 else "CW/南W"
                t_total = r[11] if df_w.shape[1] >= 12 else 0.0
                l1 = r[15] if df_w.shape[1] >= 16 else 0.0
                wood_dict[hn] = {"Track": w_track, "Total": t_total, "1F": l1}
                
            for idx, r in df.iterrows():
                hn = r["HorseName"]
                if hn in wood_dict:
                    df.at[idx, "Is_Wood"] = True
                    df.at[idx, "Wood_Track"] = wood_dict[hn]["Track"]
                    df.at[idx, "Wood_6F"] = wood_dict[hn]["Total"]
                    df.at[idx, "Wood_1F"] = wood_dict[hn]["1F"]
        except Exception:
            pass

    # ④ GTV/オッズマージ
    df_g = load_csv_candidates(GTV_CANDIDATES)
    if df_g is not None:
        try:
            g_name_idx = 4 if df_g.shape[1] > 4 else 0
            df_g[g_name_idx] = df_g[g_name_idx].astype(str).str.strip()
            gtv_dict = {}
            for _, r in df_g.iterrows():
                hn = r[g_name_idx]
                gtv_mark = str(r[9]).strip() if df_g.shape[1] > 9 else "GTV"
                gtv_dict[hn] = gtv_mark
            for idx, r in df.iterrows():
                hn = r["HorseName"]
                if hn in gtv_dict:
                    df.at[idx, "GTV"] = gtv_dict[hn]
        except Exception:
            pass

    # ================= 判定ロジック =================
    df["Is_SSS"] = (df["FIndex"] >= 70.0) & (df["ARMS2Index"] >= 120.0) & (df["TUAIndex"] >= 200.0)
    df["Is_FourCrown"] = (df["FIndex"] >= 70.0) & (df["ARMS2Index"] >= 115.0) & (df["TUAIndex"] >= 190.0) & (df["SIndex"] >= 70.0)
    df["Is_F1_Lap124"] = (df["FRank"] == 1) & (df["Hanro_1F"] > 0) & (df["Hanro_1F"] <= 12.4)
    df["Is_Haran_Trigger"] = (df["PopRank"] >= 10) & (df["Hanro_3F"] <= 14.0) & (df["Hanro_3F"] > df["Hanro_2F"]) & (df["Hanro_2F"] > df["Hanro_1F"]) & (df["Hanro_1F"] > 0)

    # クッション値×種牡馬バイアス判定
    def check_sire_bias(row):
        sire = row["Sire"]
        c_cat = cushion_cat
        if "≥10.5" in c_cat:
            if sire in ["サートゥルナーリア", "ゴールドシップ", "キングカメハメハ", "ハービンジャー", "ビッグアーサー"]:
                return "⚠️超高帯危険血統(消し)"
            if sire in ["エピファネイア", "キタサンブラック", "イスラボニータ", "ロードカナロア"]:
                return "🔥超高帯特注血統"
        if "9.5-9.9" in c_cat and venue == "阪神" and sire == "キズナ": return "🔥超買い(阪神芝1800外)"
        if "9.5-9.9" in c_cat and venue == "東京" and sire in ["エピファネイア", "モーリス", "ディープインパクト"]: return "🔥超買い(東京芝)"
        if "8.6-9.4" in c_cat and venue == "東京" and sire in ["キズナ", "ロードカナロア", "イスラボニータ"]: return "🔥超買い(東京芝)"
        if "8.6-9.4" in c_cat and venue == "中京" and sire == "ディープインパクト": return "🔥超買い(中京芝2000)"
        if "9.5-9.9" in c_cat and venue == "中山" and sire == "ダノンバラード": return "⚠️危険(中山芝2000)"
        if "8.6-9.4" in c_cat and venue == "東京" and sire in ["シルバーステート", "ゴールドシップ", "エイシンフラッシュ"]: return "⚠️危険(東京芝)"
        if "8.6-9.4" in c_cat and venue == "小倉" and sire in ["ジャスタウェイ", "ヴィクトワールピサ"]: return "⚠️危険(小倉芝1200)"
        return "中立"

    df["SireBias"] = df.apply(check_sire_bias, axis=1)

    def check_fup2(row):
        val = row["Fup2Val"]
        pop = row["PopRank"]
        f_val = row["FIndex"]
        trainer = row["Trainer"]
        jockey = row["Jockey"]
        
        if "木村" in trainer and "ルメール" in jockey:
            if val >= 5: return "🌟木村ルメール勝負(勝率35%)"
            elif val <= 4: return "⚠️木村ルメール罠(勝率10%消し)"

        if val == 7: return "🌟確変(超期待値)"
        if val >= 5: return "◎連軸信頼(Fup2強)"
        if val == 1 and pop <= 3:
            if f_val > 72.0 or row["Is_SSS"]: return "買(Fup2例外規定)"
            return "⚠️ダミー看破(消し)"
        return ""

    df["Fup2Tag"] = df.apply(check_fup2, axis=1)

    # ================= レース番号の自然順（開催場×1R〜12R昇順）ソート =================
    def parse_race_sort_key(race_id_str):
        # 開催場優先順位（例: 札幌, 函館, 福島, 新潟, 東京, 中山, 中京, 京都, 阪神, 小倉）
        venue_order = ["札幌", "札", "函館", "函", "福島", "福", "新潟", "新", "東京", "東", "中山", "山", "中京", "名", "京都", "京", "阪神", "阪", "小倉", "小"]
        v_rank = 99
        for i, v in enumerate(venue_order):
            if race_id_str.startswith(v):
                v_rank = i // 2  # 略称と通常名を同格化
                break
        
        # レース番号（数字）を抽出
        r_nums = re.findall(r'\d+', race_id_str)
        r_num = int(r_nums[-1]) if r_nums else 0
        return (v_rank, r_num, race_id_str)

    unique_races = list(df["RaceID"].unique())
    sorted_races = sorted(unique_races, key=parse_race_sort_key)

    # ================= サイドバー: 検索・選択UI =================
    selected_race = st.sidebar.selectbox("🏁 レースを選択 (開催順・1R〜12R昇順)", sorted_races)

    st.sidebar.markdown("---")
    st.sidebar.subheader("🎯 指数 × 調教 掛け合わせ抽出")
    combo_sss_acc = st.sidebar.checkbox("SSS級 × 坂路完全加速 (A1〜A3)")
    combo_f1_lap124 = st.sidebar.checkbox("F指数1位 × 坂路究極ラップ (1F≦12.4s)")
    combo_four_crown = st.sidebar.checkbox("指数四冠馬 (単回418%)")
    combo_wood_fup = st.sidebar.checkbox("ウッド調教 × Fup2 (5点以上)")
    combo_gtv_tua = st.sidebar.checkbox("GTV該当 × TUA上位 (均等配分狙い)")
    combo_haran = st.sidebar.checkbox("波乱の使者トリガー (10人気以下×連続加速)")
    combo_sire_acc = st.sidebar.checkbox("ナダル/スクリーンH × 坂路完全加速")

    # ================= UI 描画 =================
    race_df = df[df["RaceID"] == selected_race].sort_values("HorseNum").copy()

    # フィルター適用
    if combo_sss_acc: race_df = race_df[race_df["Is_SSS"] & race_df["Is_Hanro_Acc"]]
    if combo_f1_lap124: race_df = race_df[race_df["Is_F1_Lap124"]]
    if combo_four_crown: race_df = race_df[race_df["Is_FourCrown"]]
    if combo_wood_fup: race_df = race_df[race_df["Is_Wood"] & (race_df["Fup2Val"] >= 5)]
    if combo_gtv_tua: race_df = race_df[(race_df["GTV"] != "") & (race_df["TUARank"] <= 3)]
    if combo_haran: race_df = race_df[race_df["Is_Haran_Trigger"]]
    if combo_sire_acc: race_df = race_df[race_df["Sire"].isin(["ナダル", "スクリーンヒーロー"]) & race_df["Is_Hanro_Acc"]]

    st.subheader(f"📊 {selected_race} 解析サマリー")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("SSS級神域", f"{len(race_df[race_df['Is_SSS']])}頭")
    c2.metric("坂路究極ラップ🔥", f"{len(race_df[race_df['Is_F1_Lap124']])}頭")
    c3.metric("坂路完全加速", f"{len(race_df[race_df['Is_Hanro_Acc']])}頭")
    c4.metric("ダミー消し馬", f"{len(race_df[race_df['Fup2Tag'].str.contains('消し')])}頭")

    st.write("---")
    st.subheader("📋 出走馬カード（スマホ最適化）")

    search_query = st.text_input("🔍 馬名・調教師・騎手・父名で自由検索", "")
    if search_query:
        race_df = race_df[race_df.apply(lambda r: search_query in str(r.values), axis=1)]

    for _, h in race_df.iterrows():
        with st.container():
            c_head, c_tags = st.columns([2, 3])
            c_head.markdown(f"### **{int(h['HorseNum'])}番 {h['HorseName']}**")
            
            tags = []
            if h["Is_SSS"]: tags.append("<span class='badge-sss'>SSS級</span>")
            if h["Is_FourCrown"]: tags.append("<span class='badge-four'>四冠馬</span>")
            if h["Is_F1_Lap124"]: tags.append("<span class='badge-combo'>🔥F1×究極ラップ(12.4s)</span>")
            if h["Is_Hanro_Acc"]: tags.append(f"<span class='badge-hanro'>🔥坂路:{h['Hanro_Pattern']}</span>")
            if h["Is_Wood"]: tags.append(f"<span class='badge-wood'>ウッド:{h['Wood_Track']}</span>")
            if h["GTV"] and h["GTV"] != "nan" and h["GTV"] != "": tags.append(f"<span class='badge-gtv'>印:{h['GTV']}</span>")
            if "🔥" in h["SireBias"]: tags.append(f"<span class='badge-bias'>{h['SireBias']}</span>")
            if "⚠️" in h["SireBias"]: tags.append(f"<span class='badge-risk'>{h['SireBias']}</span>")
            if h["Fup2Tag"]: tags.append(f"<span class='badge-bias'>{h['Fup2Tag']}</span>")
            
            c_tags.markdown(" ".join(tags), unsafe_allow_html=True)
            
            st.markdown(f"""
            - **陣営/血統**: **{h['Trainer']}** 厩舎 / **{h['Jockey']}** 騎手 / 父: **{h['Sire']}**
            - **坂路調教**: 4F **{h['Hanro_4F']:.1f}s** - 3F {h['Hanro_3F']:.1f}s - 2F {h['Hanro_2F']:.1f}s - 終い **{h['Hanro_1F']:.1f}s**（{h['Hanro_Pattern']}）
            - **ウッド調教**: {h['Wood_Track']} 6F **{h['Wood_6F']:.1f}s** - 終い **{h['Wood_1F']:.1f}s**
            - **能力指数**: F: **{h['FIndex']:.1f}** ({int(h['FRank'])}位) | ARMS2: **{h['ARMS2Index']:.1f}** ({int(h['ARMS2Rank'])}位) | TUA: **{h['TUAIndex']:.1f}** ({int(h['TUARank'])}位) | S: {h['SIndex']:.1f}
            - **Fup2数値**: **{int(h['Fup2Val'])}点** | 人気: {int(h['PopRank'])}番人気
            """)
            st.write("---")
else:
    st.info("💡 GitHubの `data/` フォルダに有効なデータが配置されるのを待機しています。")
