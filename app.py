import streamlit as st
import pandas as pd
import numpy as np
import os
import re

st.set_page_config(page_title="競馬予想10 クッション値Vr", page_icon="🏇", layout="wide")

# カスタムCSS（スマホ最適化・カラーバッジ・買い目ボックス完備）
st.markdown("""
<style>
    .reportview-container .main .block-container { max-width: 100%; padding: 1rem; }
    .stMetric { background-color: #1E222D; padding: 10px; border-radius: 8px; }
    .badge-sss { background-color: #D90429; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
    .badge-four { background-color: #B5179E; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
    .badge-bias { background-color: #2B9348; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
    .badge-risk { background-color: #555555; color: #FFAAAA; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
    .badge-hanro { background-color: #FF8500; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
    .badge-wood { background-color: #3A86FF; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
    .badge-combo { background-color: #7209B7; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
    .badge-gtv { background-color: #FFB703; color: black; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
    
    .rank-1 { background-color: #FFD700; color: #000000; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
    .rank-2 { background-color: #0077B6; color: #FFFFFF; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
    .rank-3 { background-color: #2B9348; color: #FFFFFF; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
    .rank-other { color: #CCCCCC; }
    .no-train { color: #888888; }
    
    .card-box { background-color: #161B22; padding: 15px; border-radius: 8px; margin-bottom: 12px; border-left: 4px solid #30363D; }
    .bet-box { background-color: #1C2333; padding: 15px; border-radius: 8px; margin-top: 15px; border: 1px solid #38444D; }
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

    # 調教初期化
    df["Hanro_4F"] = 0.0
    df["Hanro_1F"] = 0.0
    df["Hanro_2F"] = 0.0
    df["Hanro_3F"] = 0.0
    df["Hanro_Pattern"] = "調教×"
    df["Is_Hanro_Acc"] = False
    
    df["Wood_6F"] = 0.0
    df["Wood_1F"] = 0.0
    df["Wood_Track"] = ""
    df["Is_Wood"] = False

    # ② 坂路調教マージ（複数本ある場合は最速4F時計を抽出）
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
                    if t4 <= 0: continue
                    
                    is_acc = False
                    p_tag = "通常"
                    # 負荷基準の厳格化: 4F <= 56.0s & 1F <= 13.0s & 完全加速
                    if t4 <= 56.0 and l1 <= 13.0 and (l4 > l3 > l2 > l1 > 0):
                        is_acc = True
                        if l1 <= 11.9: p_tag = "A3(終い11秒台🔥)"
                        elif l1 <= 12.4: p_tag = "A2(完全加速)"
                        else: p_tag = "A1(完全加速)"
                    
                    data_item = {
                        "4F": t4, "1F": l1, "2F": l2, "3F": l3,
                        "Pattern": p_tag, "Is_Acc": is_acc
                    }
                    if hn not in hanro_dict or t4 < hanro_dict[hn]["4F"]:
                        hanro_dict[hn] = data_item
            
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

    # ③ ウッド調教マージ（複数本ある場合は最速全体時計を抽出）
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
                if t_total <= 0: continue
                
                data_item = {"Track": w_track, "Total": t_total, "1F": l1}
                if hn not in wood_dict or t_total < wood_dict[hn]["Total"]:
                    wood_dict[hn] = data_item
                
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

    # 各レースごとの調教最速順位付け（調教なし馬は除外）
    h_series = df["Hanro_4F"].replace(0, np.nan)
    df["Hanro_Rank"] = df.groupby("RaceID")[h_series.name].transform(lambda x: x.rank(method="min", ascending=True)).fillna(0).astype(int)

    w_series = df["Wood_6F"].replace(0, np.nan)
    df["Wood_Rank"] = df.groupby("RaceID")[w_series.name].transform(lambda x: x.rank(method="min", ascending=True)).fillna(0).astype(int)

    # ================= 判定ロジック =================
    df["Is_SSS"] = (df["FIndex"] >= 70.0) & (df["ARMS2Index"] >= 120.0) & (df["TUAIndex"] >= 200.0)
    df["Is_FourCrown"] = (df["FIndex"] >= 70.0) & (df["ARMS2Index"] >= 115.0) & (df["TUAIndex"] >= 190.0) & (df["SIndex"] >= 70.0)
    df["Is_F1_Lap124"] = (df["FRank"] == 1) & (df["Hanro_1F"] > 0) & (df["Hanro_1F"] <= 12.4)
    df["Is_Haran_Trigger"] = (df["PopRank"] >= 10) & (df["Hanro_3F"] <= 14.0) & (df["Hanro_3F"] > df["Hanro_2F"]) & (df["Hanro_2F"] > df["Hanro_1F"]) & (df["Hanro_1F"] > 0)

    # クッション値×種牡馬バイアス判定（PDF完全同期）
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
        if "≤8.5" in c_cat and venue == "札幌" and sire == "オルフェーヴル": return "🔥超買い(札幌芝2000)"
        if "≤8.5" in c_cat and venue == "函館" and sire == "キズナ": return "🔥超買い(函館芝1800)"
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

    def get_rank_badge_html(rank_val):
        r = int(rank_val)
        if r == 1: return f"<span class='rank-1'>1位</span>"
        elif r == 2: return f"<span class='rank-2'>2位</span>"
        elif r == 3: return f"<span class='rank-3'>3位</span>"
        elif r > 0: return f"<span class='rank-other'>{r}位</span>"
        return "<span class='rank-other'>-</span>"

    # レース自然順ソート（開催場×1R〜12R昇順）
    def parse_race_sort_key(race_id_str):
        venue_order = ["札幌", "札", "函館", "函", "福島", "福", "新潟", "新", "東京", "東", "中山", "山", "中京", "名", "京都", "京", "阪神", "阪", "小倉", "小"]
        v_rank = 99
        for i, v in enumerate(venue_order):
            if race_id_str.startswith(v):
                v_rank = i // 2
                break
        r_nums = re.findall(r'\d+', race_id_str)
        r_num = int(r_nums[-1]) if r_nums else 0
        return (v_rank, r_num, race_id_str)

    unique_races = sorted(list(df["RaceID"].unique()), key=parse_race_sort_key)

    # ================= サイドバー: 分解型フィルター =================
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 能力指数フィルター")
    f_rank1 = st.sidebar.checkbox("F指数 1位")
    f_top3 = st.sidebar.checkbox("F指数 3位以内")
    f_over70 = st.sidebar.checkbox("F指数 70.0以上")
    arms_top3 = st.sidebar.checkbox("ARMS2 3位以内")
    tua_top3 = st.sidebar.checkbox("TUA 3位以内")
    is_sss = st.sidebar.checkbox("SSS級神域 (F≥70/ARMS≥120/TUA≥200)")
    is_four = st.sidebar.checkbox("指数四冠馬 (単回418%)")

    st.sidebar.markdown("---")
    st.sidebar.subheader("⚡ 坂路調教フィルター")
    hanro_acc = st.sidebar.checkbox("坂路 完全加速 (A1〜A3)")
    hanro_11s = st.sidebar.checkbox("坂路 終い11秒台 (A3🔥)")
    hanro_124 = st.sidebar.checkbox("坂路 終い12.4秒以下")
    hanro_54s = st.sidebar.checkbox("坂路 4F 54.0秒以下 (好時計)")
    hanro_rank1 = st.sidebar.checkbox("坂路 4Fタイム レース1位")
    hanro_haran = st.sidebar.checkbox("坂路 ラスト連続加速 (波乱トリガー)")

    st.sidebar.markdown("---")
    st.sidebar.subheader("🌲 ウッド調教フィルター")
    wood_any = st.sidebar.checkbox("ウッド調教該当馬 (南W / CW)")
    wood_11s = st.sidebar.checkbox("ウッド 終い11秒台")
    wood_rank1 = st.sidebar.checkbox("ウッド 全体タイム レース1位")

    st.sidebar.markdown("---")
    st.sidebar.subheader("🎯 Fup2・血統・特注フィルター")
    fup_5plus = st.sidebar.checkbox("Fup2 5点以上 (連軸信頼)")
    fup_7 = st.sidebar.checkbox("Fup2 7点 (確変)")
    gtv_any = st.sidebar.checkbox("GTV該当馬")
    sire_bias_hit = st.sidebar.checkbox("クッション値 特注血統 (🔥)")
    sire_special = st.sidebar.checkbox("ナダル / スクリーンヒーロー産駒")

    active_filters = any([
        f_rank1, f_top3, f_over70, arms_top3, tua_top3, is_sss, is_four,
        hanro_acc, hanro_11s, hanro_124, hanro_54s, hanro_rank1, hanro_haran,
        wood_any, wood_11s, wood_rank1,
        fup_5plus, fup_7, gtv_any, sire_bias_hit, sire_special
    ])

    def check_match(r_row):
        if f_rank1 and r_row["FRank"] != 1: return False
        if f_top3 and r_row["FRank"] not in [1, 2, 3]: return False
        if f_over70 and r_row["FIndex"] < 70.0: return False
        if arms_top3 and r_row["ARMS2Rank"] not in [1, 2, 3]: return False
        if tua_top3 and r_row["TUARank"] not in [1, 2, 3]: return False
        if is_sss and not r_row["Is_SSS"]: return False
        if is_four and not r_row["Is_FourCrown"]: return False
        if hanro_acc and not r_row["Is_Hanro_Acc"]: return False
        if hanro_11s and not (r_row["Hanro_1F"] > 0 and r_row["Hanro_1F"] <= 11.9): return False
        if hanro_124 and not (r_row["Hanro_1F"] > 0 and r_row["Hanro_1F"] <= 12.4): return False
        if hanro_54s and not (r_row["Hanro_4F"] > 0 and r_row["Hanro_4F"] <= 54.0): return False
        if hanro_rank1 and r_row["Hanro_Rank"] != 1: return False
        if hanro_haran and not r_row["Is_Haran_Trigger"]: return False
        if wood_any and not r_row["Is_Wood"]: return False
        if wood_11s and not (r_row["Is_Wood"] and r_row["Wood_1F"] > 0 and r_row["Wood_1F"] <= 11.9): return False
        if wood_rank1 and r_row["Wood_Rank"] != 1: return False
        if fup_5plus and r_row["Fup2Val"] < 5: return False
        if fup_7 and r_row["Fup2Val"] != 7: return False
        if gtv_any and (r_row["GTV"] == "" or r_row["GTV"] == "nan"): return False
        if sire_bias_hit and "🔥" not in r_row["SireBias"]: return False
        if sire_special and r_row["Sire"] not in ["ナダル", "スクリーンヒーロー"]: return False
        return True

    df["Is_Filter_Match"] = df.apply(check_match, axis=1) if active_filters else True

    # レース選択ラベル生成
    race_options = []
    race_map = {}
    for r_id in unique_races:
        match_count = len(df[(df["RaceID"] == r_id) & df["Is_Filter_Match"]])
        if active_filters and match_count > 0:
            label = f"{r_id} 🔥({match_count}頭)"
        elif active_filters:
            label = f"{r_id} (0頭)"
        else:
            label = r_id
        race_options.append(label)
        race_map[label] = r_id

    st.sidebar.markdown("---")
    selected_label = st.sidebar.selectbox("🏁 レースを選択 (該当レースに🔥表示)", race_options)
    selected_race = race_map[selected_label]

    # ================= 全場 厳選勝負レースサマリー表 =================
    st.subheader("📋 全場 厳選勝負レースサマリー表")
    summary_data = []
    for r_id in unique_races:
        rdf = df[df["RaceID"] == r_id]
        sss_m = rdf[rdf["Is_SSS"]]["HorseName"].tolist()
        f1_m = rdf[rdf["FRank"] == 1]["HorseName"].tolist()
        gtv_m = rdf[(rdf["GTV"] != "") & (rdf["GTV"] != "nan")]["HorseName"].tolist()
        dummy_m = rdf[rdf["Fup2Tag"].str.contains("消し")]["HorseName"].tolist()
        
        honmei = sss_m[0] if sss_m else (f1_m[0] if f1_m else "-")
        tokuda = gtv_m[0] if gtv_m else "-"
        keshi = dummy_m[0] if dummy_m else "-"
        grade = "★★★ (勝負)" if len(sss_m) > 0 or len(rdf[rdf["Is_FourCrown"]]) > 0 else "★★☆"
        
        summary_data.append({
            "場・R": r_id,
            "本命馬 (◎)": honmei,
            "特大推奨 (🔥)": tokuda,
            "ダミー消し (⚠️)": keshi,
            "勝負度": grade
        })
    st.dataframe(pd.DataFrame(summary_data), use_container_width=True)

    st.write("---")

    # ================= 選択レース詳細描画 =================
    race_df = df[df["RaceID"] == selected_race].sort_values("HorseNum").copy()
    display_df = race_df[race_df["Is_Filter_Match"]] if active_filters else race_df

    st.subheader(f"🏁 {selected_race} 解析サマリー")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("出走頭数", f"{len(race_df)}頭")
    c2.metric("SSS級神域", f"{len(race_df[race_df['Is_SSS']])}頭")
    c3.metric("坂路完全加速", f"{len(race_df[race_df['Is_Hanro_Acc']])}頭")
    c4.metric("ダミー消し馬", f"{len(race_df[race_df['Fup2Tag'].str.contains('消し')])}頭")

    st.write("---")
    st.subheader("📋 出走馬カード（調教最速順位・カラー表示完備）")

    search_query = st.text_input("🔍 馬名・調教師・騎手・父名で自由検索", "")
    if search_query:
        display_df = display_df[display_df.apply(lambda r: search_query in str(r.values), axis=1)]

    if display_df.empty:
        st.warning("⚠️ 選択した条件に一致する馬がいません。サイドバーのチェックを外して条件を緩めてください。")
    else:
        for _, h in display_df.iterrows():
            with st.container():
                c_head, c_tags = st.columns([2, 3])
                c_head.markdown(f"### **{int(h['HorseNum'])}番 {h['HorseName']}**")
                
                tags = []
                if h["Is_SSS"]: tags.append("<span class='badge-sss'>SSS級</span>")
                if h["Is_FourCrown"]: tags.append("<span class='badge-four'>四冠馬</span>")
                if h["Is_Hanro_Acc"]: tags.append(f"<span class='badge-hanro'>🔥坂路:{h['Hanro_Pattern']}</span>")
                if h["Is_Wood"]: tags.append(f"<span class='badge-wood'>ウッド:{h['Wood_Track']}</span>")
                if h["GTV"] and h["GTV"] != "nan" and h["GTV"] != "": tags.append(f"<span class='badge-gtv'>印:{h['GTV']}</span>")
                if "🔥" in h["SireBias"]: tags.append(f"<span class='badge-bias'>{h['SireBias']}</span>")
                if "⚠️" in h["SireBias"]: tags.append(f"<span class='badge-risk'>{h['SireBias']}</span>")
                if h["Fup2Tag"]: tags.append(f"<span class='badge-bias'>{h['Fup2Tag']}</span>")
                
                c_tags.markdown(" ".join(tags), unsafe_allow_html=True)

                f_badge = get_rank_badge_html(h['FRank'])
                arms_badge = get_rank_badge_html(h['ARMS2Rank'])
                tua_badge = get_rank_badge_html(h['TUARank'])
                s_badge = get_rank_badge_html(h['SRank'])

                if h["Hanro_4F"] > 0:
                    h_rank_badge = get_rank_badge_html(h['Hanro_Rank'])
                    hanro_text = f"4F **{h['Hanro_4F']:.1f}s** ({h_rank_badge}) - 3F {h['Hanro_3F']:.1f}s - 2F {h['Hanro_2F']:.1f}s - 終い **{h['Hanro_1F']:.1f}s**（{h['Hanro_Pattern']}）"
                else:
                    hanro_text = "<span class='no-train'>調教×</span>"

                if h["Is_Wood"] and h["Wood_6F"] > 0:
                    w_rank_badge = get_rank_badge_html(h['Wood_Rank'])
                    wood_text = f"{h['Wood_Track']} 6F **{h['Wood_6F']:.1f}s** ({w_rank_badge}) - 終い **{h['Wood_1F']:.1f}s**"
                else:
                    wood_text = "<span class='no-train'>調教×</span>"

                st.markdown(f"""
                - **陣営/血統**: **{h['Trainer']}** 厩舎 / **{h['Jockey']}** 騎手 / 父: **{h['Sire']}**
                - **坂路調教 (最速)**: {hanro_text}
                - **ウッド調教 (最速)**: {wood_text}
                - **能力指数**: F: **{h['FIndex']:.1f}** ({f_badge}) | ARMS2: **{h['ARMS2Index']:.1f}** ({arms_badge}) | TUA: **{h['TUAIndex']:.1f}** ({tua_badge}) | S: **{h['SIndex']:.1f}** ({s_badge})
                - **Fup2数値**: **{int(h['Fup2Val'])}点** | 人気: {int(h['PopRank'])}番人気
                """, unsafe_allow_html=True)
                st.write("---")

    # ================= プロの推奨買い目生成（新フォーメーション） =================
    st.subheader(f"🎯 {selected_race} プロの推奨買い目＆フォーメーション")
    
    # 候補馬抽出
    honmei_row = race_df[race_df["FRank"] == 1]
    honmei_name = f"{int(honmei_row['HorseNum'].values[0])}番 {honmei_row['HorseName'].values[0]}" if not honmei_row.empty else "該当なし"
    
    tokuda_rows = race_df[(race_df["GTV"] != "") & (race_df["GTV"] != "nan")]
    tokuda_names = [f"{int(r['HorseNum'])}番 {r['HorseName']}" for _, r in tokuda_rows.iterrows()]
    tokuda_str = ", ".join(tokuda_names) if tokuda_names else "なし"
    
    matrix_top = race_df[race_df["FRank"].isin([1, 2, 3]) | race_df["ARMS2Rank"].isin([1, 2]) | race_df["TUARank"].isin([1, 2])]
    box_horses = [f"{int(r['HorseNum'])}番" for _, r in matrix_top.iterrows()][:4]
    box_str = ", ".join(box_horses)

    st.markdown(f"""
    <div class='bet-box'>
        <h4>【1】勝負レース本命馬（連軸筆頭）</h4>
        <p>◎ <b>本命馬</b>: {honmei_name}</p>
        <h4>【2】特注ヒモ穴・危険な人気馬</h4>
        <p>🔥 <b>特大推奨馬</b>: {tokuda_str}</p>
        <h4>【3】プロの推奨買い目（回収率・的中両立）</h4>
        <ul>
            <li><b>単勝・複勝</b>: {honmei_name} / {tokuda_str}</li>
            <li><b>馬連・ワイドBOX (精鋭3〜4頭)</b>: {box_str}</li>
            <li><b>3連複BOX / フォーメーション</b>: {box_str}</li>
            <li><b>3連単フォーメーション（裏表マルチ対応）</b>:
                <br>1着: {honmei_name}, {tokuda_str}
                <br>2着: {box_str}
                <br>3着: {box_str}（※ヒモ穴1着・本命2/3着マルチ完備）
            </li>
        </ul>
        <h4>【4】⚠️ 本命馬が負けるパターンと保険シナリオ</h4>
        <p>・本命馬が先行争いやクッション値の死角により2・3着に取りこぼした場合に備え、特大推奨馬頭固定の3連単裏目マルチを保険として配分。</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("💡 GitHubの `data/` フォルダに有効なデータが配置されるのを待機しています。")
