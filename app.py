import os
import re
import numpy as np
import pandas as pd
import streamlit as st

# ==============================================================================
# 1. ページ基本設定 & タイトル
# ==============================================================================
st.set_page_config(
    page_title="競馬予想10 クッション値Vr - 完全自動解析システム",
    page_icon="🏇",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================================
# 2. CSSスタイル（洗練されたダークテーマUI & 豪華特注バッジ）
# ==============================================================================
st.markdown(
    """
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
        font-size: 26px;
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
        margin-bottom: 6px;
        line-height: 1.6;
    }
    .horse-card-list li::before {
        content: "• ";
        color: #58a6ff;
        font-weight: bold;
    }

    /* 豪華特注バッジ群 */
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
    .badge-sss {
        background: linear-gradient(135deg, #FF007F 0%, #7928CA 100%);
        color: #ffffff;
        border: 1px solid #FF79C6;
    }
    .badge-four-crown {
        background: linear-gradient(135deg, #FFD700 0%, #FF8C00 100%);
        color: #000000;
        border: 1px solid #FFF275;
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
    .badge-fup-7 {
        background: linear-gradient(135deg, #FF512F 0%, #DD2476 100%);
        color: #ffffff;
        border: 1px solid #FFA07A;
    }
    .badge-fup-high {
        background: linear-gradient(135deg, #F09819 0%, #EDDE5D 100%);
        color: #2b1d00;
        border: 1px solid #FFE066;
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
    .badge-cushion-good {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: #052010;
        border: 1px solid #80FFB4;
        font-weight: bold;
    }
    .badge-cushion-risk {
        background: linear-gradient(135deg, #cb2d3e 0%, #ef473a 100%);
        color: #ffffff;
        border: 1px solid #ff7878;
        font-weight: bold;
    }
    .badge-dummy {
        background: #442727;
        color: #ff7b72;
        border: 1px solid #da3633;
        font-weight: bold;
    }
    .badge-accel {
        background-color: #238636;
        color: #ffffff;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: bold;
    }
    .badge-decel {
        background-color: #6e7681;
        color: #ffffff;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 11px;
    }

    .rank-1st { color: #FFD700; font-weight: bold; background-color: rgba(255, 215, 0, 0.18); padding: 1px 5px; border-radius: 4px; border: 1px solid rgba(255, 215, 0, 0.5); }
    .rank-2nd { color: #E0E0E0; font-weight: bold; background-color: rgba(224, 224, 224, 0.18); padding: 1px 5px; border-radius: 4px; border: 1px solid rgba(224, 224, 224, 0.5); }
    .rank-3rd { color: #CD7F32; font-weight: bold; background-color: rgba(205, 127, 50, 0.18); padding: 1px 5px; border-radius: 4px; border: 1px solid rgba(205, 127, 50, 0.5); }
    .rank-normal { color: #8b949e; font-size: 12px; }
    
    .fup-high-val { color: #FFD700; font-weight: bold; background-color: rgba(255, 165, 0, 0.2); padding: 1px 6px; border-radius: 4px; border: 1px solid rgba(255, 165, 0, 0.5); }
    .fup-danger-val { color: #ff7b72; font-weight: bold; background-color: rgba(255, 0, 0, 0.2); padding: 1px 6px; border-radius: 4px; border: 1px solid #da3633; }

    .sidebar-synergy-item {
        background-color: #0d1117;
        border: 1px solid #30363d;
        border-left: 3px solid #f78166;
        padding: 8px 10px;
        border-radius: 6px;
        margin-bottom: 6px;
        font-size: 12px;
        line-height: 1.4;
    }
    .sidebar-synergy-header { font-weight: bold; color: #ffffff; margin-bottom: 2px; }
</style>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# 3. 汎用ヘルパー & クリーニング関数
# ==============================================================================
def clean_horse_name(name):
    if pd.isnull(name):
        return ""
    s = str(name).strip()
    return s.replace("*", "").replace("$", "").replace(" ", "").replace(" ", "").replace("\t", "")

def format_rank_badge(rank_val):
    if pd.isnull(rank_val) or rank_val in [99, 0]:
        return "<span class='rank-normal'>-位</span>"
    try:
        r = int(rank_val)
    except Exception:
        return "<span class='rank-normal'>-位</span>"
    if r == 1:
        return "<span class='rank-1st'>🥇1位</span>"
    elif r == 2:
        return "<span class='rank-2nd'>🥈2位</span>"
    elif r == 3:
        return "<span class='rank-3rd'>🥉3位</span>"
    else:
        return f"<span class='rank-normal'>{r}位</span>"

def get_file_mtime(path):
    return os.path.getmtime(path) if os.path.exists(path) else 0

# ==============================================================================
# 4. データロード＆マッピング（mtime連動・Shift-JIS完全対応）
# ==============================================================================
def get_csv_paths():
    candidates = {
        "shisu": ["data/出馬表_指数.csv", "出馬表_指数.csv", "指数.csv"],
        "hanro": ["data/出馬表_坂路.csv", "出馬表_坂路.csv", "坂路調教.csv", "坂路.csv"],
        "wood": ["data/出馬表_ウッド.csv", "出馬表_ウッド.csv", "ウッド調教.csv", "ウッド.csv"],
        "gtv": ["data/GTV馬.csv", "GTV馬.csv", "GTV.csv"]
    }
    resolved = {}
    for k, paths in candidates.items():
        resolved[k] = None
        for p in paths:
            if os.path.exists(p):
                resolved[k] = p
                break
    return resolved

paths = get_csv_paths()
mtime_shisu = get_file_mtime(paths["shisu"]) if paths["shisu"] else 0
mtime_hanro = get_file_mtime(paths["hanro"]) if paths["hanro"] else 0
mtime_wood = get_file_mtime(paths["wood"]) if paths["wood"] else 0
mtime_gtv = get_file_mtime(paths["gtv"]) if paths["gtv"] else 0

@st.cache_data
def load_and_merge_all(p_shisu, p_hanro, p_wood, p_gtv, mt_s, mt_h, mt_w, mt_g):
    if not p_shisu or not os.path.exists(p_shisu):
        return pd.DataFrame()

    # 1. 出馬表・指数 CSV (全24項目マッピング)
    try:
        with open(p_shisu, "r", encoding="shift-jis", errors="ignore") as f:
            lines = f.readlines()
    except Exception:
        with open(p_shisu, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

    fw_map = {"１": 1, "２": 2, "３": 3, "４": 4, "５": 5, "６": 6, "７": 7, "８": 8, "９": 9,
              "10": 10, "11": 11, "12": 12, "13": 13, "14": 14, "15": 15, "16": 16, "17": 17, "18": 18}

    records = []
    for line in lines:
        parts = [p.strip() for p in line.strip().split(",")]
        n = len(parts)
        if n < 10:
            continue

        race_id, track, dist, umaban, horse_raw = parts[0], "", "", "", None
        trainer, jockey, sire, gtv = "", "", "", ""
        pop, finish, fup, fup_rank, f_val, f_rank = None, None, 0, 99, 0.0, 99
        arms_val, arms_rank, tua_val, tua_rank = 0.0, 99, 0.0, 99

        if n == 24:
            track, dist, umaban = parts[1], parts[2], parts[3]
            horse_raw = parts[4]
            trainer, jockey = parts[6], parts[7]
            pop = parts[8]
            gtv = parts[9]
            fup = pd.to_numeric(parts[10], errors="coerce")
            fup_rank = pd.to_numeric(parts[11], errors="coerce")
            f_val = pd.to_numeric(parts[13], errors="coerce")
            f_rank = pd.to_numeric(parts[14], errors="coerce")
            arms_val = pd.to_numeric(parts[16], errors="coerce")
            arms_rank = pd.to_numeric(parts[17], errors="coerce")
            tua_val = pd.to_numeric(parts[19], errors="coerce")
            tua_rank = pd.to_numeric(parts[20], errors="coerce")
            finish = parts[22]
            sire = parts[23] if n > 23 else ""
        elif n == 23:
            track, dist, umaban = parts[1], parts[2], parts[3]
            horse_raw = parts[4]
            trainer, jockey = parts[6], parts[7]
            pop = parts[8]
            gtv = parts[9]
            fup = pd.to_numeric(parts[10], errors="coerce")
            fup_rank = pd.to_numeric(parts[11], errors="coerce")
            f_val = pd.to_numeric(parts[14], errors="coerce")
            f_rank = pd.to_numeric(parts[15], errors="coerce")
            arms_val = pd.to_numeric(parts[16], errors="coerce")
            arms_rank = pd.to_numeric(parts[17], errors="coerce")
            tua_val = pd.to_numeric(parts[18], errors="coerce")
            tua_rank = pd.to_numeric(parts[19], errors="coerce")
            finish = parts[20]
            sire = parts[21] if n > 21 else ""
        else:
            continue

        horse = clean_horse_name(horse_raw)
        if horse:
            fin_int = fw_map.get(finish, int(finish) if str(finish).isdigit() else np.nan)
            pop_int = int(pop) if str(pop).isdigit() else np.nan
            u_int = int(umaban) if str(umaban).isdigit() else 99

            records.append({
                "race_id": race_id, "track": track, "dist": dist, "馬番": u_int, "馬名": horse,
                "調教師": str(trainer).strip(), "騎手": str(jockey).strip(), "種牡馬": str(sire).strip(),
                "人気": pop_int, "着順": fin_int, "GTV": str(gtv).strip(),
                "Fup": fup if not np.isnan(fup) else 0,
                "Fup_rank": int(fup_rank) if not np.isnan(fup_rank) else 99,
                "F指数": f_val if not np.isnan(f_val) else 0.0,
                "F_rank": int(f_rank) if not np.isnan(f_rank) else 99,
                "arms": arms_val if not np.isnan(arms_val) else 0.0,
                "arms_rank": int(arms_rank) if not np.isnan(arms_rank) else 99,
                "tua": tua_val if not np.isnan(tua_val) else 0.0,
                "tua_rank": int(tua_rank) if not np.isnan(tua_rank) else 99,
            })

    df_main = pd.DataFrame(records)
    if df_main.empty:
        return pd.DataFrame()

    # レース区分ID生成
    resets = [0]
    for i in range(1, len(df_main)):
        h_curr = df_main.loc[i, "馬名"]
        h_prev = df_main.loc[i - 1, "馬名"]
        if h_curr < h_prev and (h_prev > "マ" and h_curr < "ウ"):
            resets.append(i)
    resets.append(len(df_main))
    batch_ids = []
    for i in range(len(resets) - 1):
        batch_ids.extend([i] * (resets[i + 1] - resets[i]))
    df_main["batch_id"] = batch_ids
    df_main["race_uid"] = df_main["batch_id"].astype(str) + "_" + df_main["race_id"]

    venue_dict = {"東": "東京", "中": "中山", "京": "京都", "阪": "阪神", "名": "中京", "小": "小倉", "新": "新潟", "福": "福島", "函": "函館", "札": "札幌"}
    def parse_race(rid):
        match = re.match(r"([^\d]+)(\d+)", str(rid))
        if match:
            v_code, r_no = match.group(1), int(match.group(2))
            return venue_dict.get(v_code, v_code), r_no
        return "その他", 99

    df_main[["競馬場名", "R番号"]] = df_main["race_id"].apply(lambda x: pd.Series(parse_race(x)))

    # 2. 坂路調教 CSV（実質負荷基準: 4F <= 56.0 かつ 1F <= 13.0）
    if p_hanro and os.path.exists(p_hanro):
        try:
            df_s_raw = pd.read_csv(p_hanro, encoding="shift-jis")
        except Exception:
            df_s_raw = pd.read_csv(p_hanro, encoding="utf-8", errors="ignore")

        s_name_col = "馬名" if "馬名" in df_s_raw.columns else df_s_raw.columns[4] if len(df_s_raw.columns) > 4 else None
        if s_name_col:
            df_s_raw["馬名"] = df_s_raw[s_name_col].apply(clean_horse_name)
            c_4f = "Time1" if "Time1" in df_s_raw.columns else df_s_raw.columns[9] if len(df_s_raw.columns) > 9 else None
            c_l4 = "Lap4" if "Lap4" in df_s_raw.columns else df_s_raw.columns[13] if len(df_s_raw.columns) > 13 else None
            c_l3 = "Lap3" if "Lap3" in df_s_raw.columns else df_s_raw.columns[14] if len(df_s_raw.columns) > 14 else None
            c_l2 = "Lap2" if "Lap2" in df_s_raw.columns else df_s_raw.columns[15] if len(df_s_raw.columns) > 15 else None
            c_l1 = "Lap1" if "Lap1" in df_s_raw.columns else df_s_raw.columns[16] if len(df_s_raw.columns) > 16 else None

            df_s_raw["坂路_4F"] = pd.to_numeric(df_s_raw[c_4f], errors="coerce") if c_4f else np.nan
            df_s_raw["坂路_Lap4"] = pd.to_numeric(df_s_raw[c_l4], errors="coerce") if c_l4 else np.nan
            df_s_raw["坂路_Lap3"] = pd.to_numeric(df_s_raw[c_l3], errors="coerce") if c_l3 else np.nan
            df_s_raw["坂路_Lap2"] = pd.to_numeric(df_s_raw[c_l2], errors="coerce") if c_l2 else np.nan
            df_s_raw["坂路_Lap1"] = pd.to_numeric(df_s_raw[c_l1], errors="coerce") if c_l1 else np.nan

            # 実質負荷基準判定
            t1 = df_s_raw["坂路_4F"]
            l4, l3, l2, l1 = df_s_raw["坂路_Lap4"], df_s_raw["坂路_Lap3"], df_s_raw["坂路_Lap2"], df_s_raw["坂路_Lap1"]
            df_s_raw["坂路_完全加速"] = (
                (l4 > l3) & (l3 > l2) & (l2 > l1) &
                (t1 <= 56.0) & (l1 <= 13.0)
            )
            df_s_raw["坂路_ラスト2F加速"] = np.round(l2 - l1, 2)
            df_s_raw["坂路_スコア"] = (
                np.where(df_s_raw["坂路_完全加速"], 100, 0)
                + (60.0 - l1.fillna(20.0)) * 3
                + df_s_raw["坂路_ラスト2F加速"].fillna(0.0) * 5
                + (60.0 - t1.fillna(65.0))
            )

            s_best = df_s_raw.sort_values(by=["坂路_完全加速", "坂路_スコア", "坂路_Lap1"], ascending=[False, False, True]).groupby("馬名").first().reset_index()
            cols_s = ["馬名", "坂路_4F", "坂路_Lap4", "坂路_Lap3", "坂路_Lap2", "坂路_Lap1", "坂路_ラスト2F加速", "坂路_完全加速", "坂路_スコア"]
            df_main = pd.merge(df_main, s_best[cols_s].drop_duplicates("馬名"), on="馬名", how="left")

    for col in ["坂路_4F", "坂路_Lap4", "坂路_Lap3", "坂路_Lap2", "坂路_Lap1", "坂路_ラスト2F加速"]:
        if col not in df_main.columns:
            df_main[col] = np.nan
    if "坂路_完全加速" not in df_main.columns:
        df_main["坂路_完全加速"] = False
    if "坂路_スコア" not in df_main.columns:
        df_main["坂路_スコア"] = -999

    # 3. ウッド調教 CSV
    if p_wood and os.path.exists(p_wood):
        try:
            df_w_raw = pd.read_csv(p_wood, encoding="shift-jis")
        except Exception:
            df_w_raw = pd.read_csv(p_wood, encoding="utf-8", errors="ignore")

        w_name_col = "馬名" if "馬名" in df_w_raw.columns else df_w_raw.columns[4] if len(df_w_raw.columns) > 4 else None
        if w_name_col:
            df_w_raw["馬名"] = df_w_raw[w_name_col].apply(clean_horse_name)
            c_w_5f = "5F" if "5F" in df_w_raw.columns else df_w_raw.columns[9] if len(df_w_raw.columns) > 9 else None
            c_w_l4 = "Lap4" if "Lap4" in df_w_raw.columns else df_w_raw.columns[16] if len(df_w_raw.columns) > 16 else None
            c_w_l3 = "Lap3" if "Lap3" in df_w_raw.columns else df_w_raw.columns[17] if len(df_w_raw.columns) > 17 else None
            c_w_l2 = "Lap2" if "Lap2" in df_w_raw.columns else df_w_raw.columns[18] if len(df_w_raw.columns) > 18 else None
            c_w_l1 = "Lap1" if "Lap1" in df_w_raw.columns else df_w_raw.columns[19] if len(df_w_raw.columns) > 19 else None
            c_w_plc = "場所" if "場所" in df_w_raw.columns else df_w_raw.columns[0]

            df_w_raw["wood_5F"] = pd.to_numeric(df_w_raw[c_w_5f], errors="coerce") if c_w_5f else np.nan
            df_w_raw["wood_Lap4"] = pd.to_numeric(df_w_raw[c_w_l4], errors="coerce") if c_w_l4 else np.nan
            df_w_raw["wood_Lap3"] = pd.to_numeric(df_w_raw[c_w_l3], errors="coerce") if c_w_l3 else np.nan
            df_w_raw["wood_Lap2"] = pd.to_numeric(df_w_raw[c_w_l2], errors="coerce") if c_w_l2 else np.nan
            df_w_raw["wood_Lap1"] = pd.to_numeric(df_w_raw[c_w_l1], errors="coerce") if c_w_l1 else np.nan
            df_w_raw["wood_place"] = df_w_raw[c_w_plc].astype(str) if c_w_plc else ""

            df_w_raw["wood_ラスト2F加速"] = np.round(df_w_raw["wood_Lap2"] - df_w_raw["wood_Lap1"], 2)
            df_w_raw["is_wood_accel"] = (df_w_raw["wood_ラスト2F加速"] > 0) & (df_w_raw["wood_ラスト2F加速"].notna())
            df_w_raw["wood_スコア"] = (
                (20.0 - df_w_raw["wood_Lap1"].fillna(20.0)) * 3
                + df_w_raw["wood_ラスト2F加速"].fillna(0.0) * 4
                + (75.0 - df_w_raw["wood_5F"].fillna(85.0))
            )

            w_best = df_w_raw.sort_values(by=["wood_スコア", "wood_Lap1"], ascending=[False, True]).groupby("馬名").first().reset_index()
            cols_w = ["馬名", "wood_place", "wood_5F", "wood_Lap4", "wood_Lap3", "wood_Lap2", "wood_Lap1", "wood_ラスト2F加速", "is_wood_accel", "wood_スコア"]
            df_main = pd.merge(df_main, w_best[cols_w].drop_duplicates("馬名"), on="馬名", how="left")

    for col in ["wood_5F", "wood_Lap4", "wood_Lap3", "wood_Lap2", "wood_Lap1", "wood_ラスト2F加速"]:
        if col not in df_main.columns:
            df_main[col] = np.nan
    if "is_wood_accel" not in df_main.columns:
        df_main["is_wood_accel"] = False
    if "wood_place" not in df_main.columns:
        df_main["wood_place"] = ""
    if "wood_スコア" not in df_main.columns:
        df_main["wood_スコア"] = -999

    # 調教馬間順位
    df_main["坂路_調教順位"] = df_main.groupby("race_uid")["坂路_スコア"].rank(method="min", ascending=False)
    df_main.loc[df_main["坂路_4F"].isna(), "坂路_調教順位"] = np.nan
    df_main["坂路_4F_rank"] = df_main.groupby("race_uid")["坂路_4F"].rank(method="min", ascending=True)
    df_main["坂路_Lap1_rank"] = df_main.groupby("race_uid")["坂路_Lap1"].rank(method="min", ascending=True)

    df_main["wood_調教順位"] = df_main.groupby("race_uid")["wood_スコア"].rank(method="min", ascending=False)
    df_main.loc[df_main["wood_Lap1"].isna(), "wood_調教順位"] = np.nan
    df_main["wood_5F_rank"] = df_main.groupby("race_uid")["wood_5F"].rank(method="min", ascending=True)
    df_main["wood_Lap1_rank"] = df_main.groupby("race_uid")["wood_Lap1"].rank(method="min", ascending=True)

    return df_main

df = load_and_merge_all(paths["shisu"], paths["hanro"], paths["wood"], paths["gtv"],
                        mtime_shisu, mtime_hanro, mtime_wood, mtime_gtv)

if df.empty:
    st.error("⚠️ CSVデータを読み込めませんでした。`data/` フォルダ内に `出馬表_指数.csv` などを配置してください。")
    st.stop()

# ==============================================================================
# 5. クッション値×種牡馬バイアス完全判定（70コース×主要60種牡馬データブック直結）
# ==============================================================================
def evaluate_cushion_sire(sire, track_name, dist_val, surface, c_val):
    if pd.isnull(sire) or not str(sire).strip() or surface != "芝":
        return None, ""
    s = str(sire).strip()
    track = str(track_name).strip()
    try:
        dist = int(dist_val)
    except Exception:
        dist = 0

    # 競馬場別クッション区分
    if track in ["札幌"]:
        c_band = "場内低" if c_val <= 7.3 else ("場内高" if c_val >= 7.7 else "場内中")
    elif track in ["函館"]:
        c_band = "場内低" if c_val <= 7.2 else ("場内高" if c_val >= 7.5 else "場内中")
    else:
        if c_val <= 8.5: c_band = "低め"
        elif c_val <= 9.4: c_band = "やや低め"
        elif c_val <= 9.9: c_band = "標準高"
        elif c_val <= 10.4: c_band = "高め"
        else: c_band = "超高"

    # 1. 超高帯（>=10.5）独立評価
    if c_val >= 10.5 or c_band == "超高":
        if any(k in s for k in ["エピファネイア", "キタサンブラック", "イスラボニータ", "ロードカナロア"]):
            return "good", f"✨ 超高クッション特注血統 ({s}: 複差大幅プラス)"
        if any(k in s for k in ["キングカメハメハ", "ビッグアーサー", "レイデオロ", "スワーヴリチャード", "サートゥルナーリア", "ゴールドシップ"]):
            return "risk", f"⚠️ 超高クッション危険血統 ({s}: 複勝率急落)"

    # 2. 『最重要・狙い目 上位20』完全照合
    if track == "阪神" and dist == 1800 and "キズナ" in s and c_band == "標準高":
        return "good", "🎯 最重要: 阪神1800外×キズナ (勝率19.6%/複率41.1%/単421/複172)"
    if track == "東京" and dist == 1600 and "エピファネイア" in s and c_band == "標準高":
        return "good", "🎯 最重要: 東京1600×エピファネイア (勝率13.3%/複率39.8%/単277/複111)"
    if track == "東京" and dist == 1400 and "モーリス" in s and c_band == "標準高":
        return "good", "🎯 最重要: 東京1400×モーリス (勝率10.1%/複率29.0%/単408/複160)"
    if track == "東京" and dist == 1800 and "ディープインパクト" in s and c_band == "標準高":
        return "good", "🎯 最重要: 東京1800×ディープインパクト (勝率15.8%/複率38.6%/単228/複156)"
    if track == "東京" and dist == 2000 and "キズナ" in s and c_band == "やや低め":
        return "good", "🎯 最重要: 東京2000×キズナ (勝率19.7%/複率42.4%/単200/複121)"
    if track == "中京" and dist == 2000 and "ディープインパクト" in s and c_band == "やや低め":
        return "good", "🎯 最重要: 中京2000×ディープインパクト (勝率18.0%/複率42.6%/単178/複92)"
    if track == "東京" and dist == 1600 and "イスラボニータ" in s and c_band == "やや低め":
        return "good", "🎯 最重要: 東京1600×イスラボニータ (勝率10.5%/複率30.3%/単350/複120)"
    if track == "東京" and dist == 2000 and "エピファネイア" in s and c_band == "やや低め":
        return "good", "🎯 最重要: 東京2000×エピファネイア (勝率15.3%/複率42.4%/単149/複84)"
    if track == "函館" and dist == 1800 and "キズナ" in s and (c_val <= 8.5 or c_band in ["場内低", "場内中"]):
        return "good", "🎯 最重要: 函館1800×キズナ (勝率17.7%/複率38.7%/単143/複93)"
    if track == "小倉" and dist == 1200 and "ダイワメジャー" in s and c_band == "標準高":
        return "good", "🎯 最重要: 小倉1200×ダイワメジャー (勝率13.6%/複率30.3%/単173/複111)"
    if track == "札幌" and dist == 2000 and "オルフェーヴル" in s and (c_val <= 8.5 or c_band in ["場内低", "場内中"]):
        return "good", "🎯 最重要: 札幌2000×オルフェーヴル (勝率15.8%/複率35.1%/単136/複145)"
    if track == "東京" and dist == 1400 and "ロードカナロア" in s and c_band == "やや低め":
        return "good", "🎯 最重要: 東京1400×ロードカナロア (勝率15.6%/複率32.5%/単123/複100)"
    if track == "阪神" and dist == 1600 and "ルーラーシップ" in s and c_band == "やや低め":
        return "good", "🎯 最重要: 阪神1600外×ルーラーシップ (勝率20.0%/複率30.0%/単156/複89)"
    if track == "東京" and dist == 1600 and "モーリス" in s and c_band == "標準高":
        return "good", "🎯 最重要: 東京1600×モーリス (勝率11.1%/複率37.5%/単100/複122)"
    if track == "阪神" and dist == 2000 and "キズナ" in s and c_band == "やや低め":
        return "good", "🎯 最重要: 阪神2000内×キズナ (勝率11.8%/複率41.2%/単152/複107)"
    if track == "東京" and dist == 1600 and "スクリーンヒーロー" in s and c_band == "やや低め":
        return "good", "🎯 最重要: 東京1600×スクリーンヒーロー (勝率9.9%/複率35.2%/単72/複179)"
    if track == "小倉" and dist == 1200 and "ビッグアーサー" in s and c_band == "やや低め":
        return "good", "🎯 最重要: 小倉1200×ビッグアーサー (勝率12.2%/複率30.9%/単131/複101)"
    if track == "中京" and dist == 1600 and "ロードカナロア" in s and c_band == "高め":
        return "good", "🎯 最重要: 中京1600×ロードカナロア (勝率14.8%/複率32.8%/単133/複79)"
    if track == "福島" and dist == 1200 and "ビッグアーサー" in s and c_band == "やや低め":
        return "good", "🎯 最重要: 福島1200×ビッグアーサー (勝率13.2%/複率33.1%/単87/複102)"
    if track == "札幌" and dist == 1200 and "ロードカナロア" in s and (c_val <= 8.5 or c_band in ["場内低", "場内中"]):
        return "good", "🎯 最重要: 札幌1200×ロードカナロア (勝率15.0%/複率33.0%/単121/複71)"

    # 3. 『危険 上位20』完全照合
    if track == "中山" and dist == 2000 and "ダノンバラード" in s and c_band == "標準高":
        return "risk", "⚠️ 危険: 中山2000×ダノンバラード (複勝率0.0%/単0/複0)"
    if track == "東京" and dist == 2000 and "ルーラーシップ" in s and c_band == "標準高":
        return "risk", "⚠️ 危険: 東京2000×ルーラーシップ (複勝率9.1%/単0/複15)"
    if track == "小倉" and dist == 1200 and "ジャスタウェイ" in s and c_band == "やや低め":
        return "risk", "⚠️ 危険: 小倉1200×ジャスタウェイ (複勝率2.9%/単0/複29)"
    if track == "東京" and dist == 1400 and "シルバーステート" in s and c_band == "やや低め":
        return "risk", "⚠️ 危険: 東京1400×シルバーステート (複勝率4.7%/単0/複50)"
    if track == "東京" and dist == 1600 and "ゴールドシップ" in s and c_band == "やや低め":
        return "risk", "⚠️ 危険: 東京1600×ゴールドシップ (複勝率4.5%/単20/複9)"
    if track == "小倉" and dist == 1200 and "ヴィクトワールピサ" in s and c_band == "やや低め":
        return "risk", "⚠️ 危険: 小倉1200×ヴィクトワールピサ (複勝率4.8%/単17/複10)"
    if track == "東京" and dist == 1800 and "ルーラーシップ" in s and c_band == "標準高":
        return "risk", "⚠️ 危険: 東京1800×ルーラーシップ (複勝率10.5%/単0/複51)"
    if track == "阪神" and dist == 2000 and "ゴールドシップ" in s and c_band == "やや低め":
        return "risk", "⚠️ 危険: 阪神2000内×ゴールドシップ (複勝率10.0%/単45/複19)"
    if track == "東京" and dist == 1600 and "エイシンフラッシュ" in s and c_band == "やや低め":
        return "risk", "⚠️ 危険: 東京1600×エイシンフラッシュ (複勝率7.3%/単9/複13)"
    if track == "東京" and dist == 2000 and "オルフェーヴル" in s and c_band == "やや低め":
        return "risk", "⚠️ 危険: 東京2000×オルフェーヴル (複勝率13.2%/単0/複33)"
    if track == "福島" and dist == 2000 and "ルーラーシップ" in s and c_band == "やや低め":
        return "risk", "⚠️ 危険: 福島2000×ルーラーシップ (複勝率4.7%/単38/複12)"
    if track == "新潟" and dist == 1400 and "リオンディーズ" in s and c_band == "やや低め":
        return "risk", "⚠️ 危険: 新潟1400内×リオンディーズ (複勝率6.7%/単0/複15)"
    if track == "東京" and dist == 2400 and "ゴールドシップ" in s and c_band == "標準高":
        return "risk", "⚠️ 危険: 東京2400×ゴールドシップ (複勝率11.1%/単0/複40)"
    if track == "小倉" and dist == 1800 and "ルーラーシップ" in s and c_band == "標準高":
        return "risk", "⚠️ 危険: 小倉1800×ルーラーシップ (複勝率10.0%/単10/複16)"
    if track == "阪神" and dist == 1800 and "ハービンジャー" in s and c_band == "標準高":
        return "risk", "⚠️ 危険: 阪神1800外×ハービンジャー (複勝率10.0%/単9/複17)"
    if track == "東京" and dist == 1600 and "サトノクラウン" in s and c_band == "やや低め":
        return "risk", "⚠️ 危険: 東京1600×サトノクラウン (複勝率9.7%/単0/複17)"
    if track == "福島" and dist == 1200 and "マツリダゴッホ" in s and c_band == "やや低め":
        return "risk", "⚠️ 危険: 福島1200×マツリダゴッホ (複勝率5.9%/単32/複18)"
    if track == "東京" and dist == 1600 and "シルバーステート" in s and c_band == "標準高":
        return "risk", "⚠️ 危険: 東京1600×シルバーステート (複勝率8.9%/単4/複28)"
    if track == "福島" and dist == 1200 and "カレンブラックヒル" in s and c_band == "やや低め":
        return "risk", "⚠️ 危険: 福島1200×カレンブラックヒル (複勝率9.7%/単0/複31)"
    if track == "中京" and dist == 2000 and "オルフェーヴル" in s and c_band == "やや低め":
        return "risk", "⚠️ 危険: 中京2000×オルフェーヴル (複勝率15.2%/単0/複54)"

    return None, ""

# ==============================================================================
# 6. サイドバー: 馬場・クッション値設定 & 黄金シナジー抽出
# ==============================================================================
st.sidebar.markdown("### 🌱 馬場・クッション値設定")
cushion_val = st.sidebar.number_input("芝クッション値", min_value=5.0, max_value=13.0, value=9.5, step=0.1)

if cushion_val <= 8.5:
    band_label = "📍 判定帯: 8.5以下 (低め・軟らかめ)"
elif cushion_val <= 9.4:
    band_label = "📍 判定帯: 8.6-9.4 (やや低め)"
elif cushion_val <= 9.9:
    band_label = "📍 判定帯: 9.5-9.9 (標準高)"
elif cushion_val <= 10.4:
    band_label = "📍 判定帯: 10.0-10.4 (高め・硬め)"
else:
    band_label = "📍 判定帯: 10.5以上 (超高・高速馬場)"

st.sidebar.info(band_label)

if st.sidebar.button("🔄 最新データへ強制再読み込み", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")

# ==============================================================================
# 7. 全レース横断 黄金シナジーフラグ付与
# ==============================================================================
df["is_sss"] = (df["F指数"] >= 70) & (df["arms"] >= 120) & (df["tua"] >= 200)
df["is_four_crown"] = (df["F_rank"] == 1) & (df["Fup_rank"] == 1) & (df["arms_rank"] == 1) & (df["tua_rank"] == 1)
df["is_syn_iron"] = (df["F_rank"] == 1) & (df["arms_rank"] <= 3) & (df["wood_Lap1"] <= 11.5) & (df["is_wood_accel"] == True)
df["is_syn_high"] = ((df["F_rank"] == 1) | (df["F指数"] >= 66)) & (df["wood_Lap1"] <= 11.5) & (df["is_wood_accel"] == True)
df["is_syn_fup_sakaro"] = (df["Fup"] >= 5) & (df["坂路_完全加速"] == True)
df["is_syn_bomb"] = (df["人気"] >= 6) & (df["Fup"] >= 4) & (df["坂路_完全加速"] == True)
df["is_syn_f1_rap"] = (df["F_rank"] == 1) & (df["坂路_Lap1"] <= 12.4) & (df["坂路_完全加速"] == True)

st.sidebar.markdown("### 👑 黄金シナジー抽出")
syn_sss = st.sidebar.checkbox(f"👑 SSS級絶対神域 ({int(df['is_sss'].sum())}頭)", help="F>=70 & ARMS>=120 & TUA>=200")
syn_iron = st.sidebar.checkbox(f"💎 鉄板軸馬 ({int(df['is_syn_iron'].sum())}頭)", help="複勝率61.9%")
syn_high = st.sidebar.checkbox(f"🔥 高確率軸馬 ({int(df['is_syn_high'].sum())}頭)", help="複勝率55%超")
syn_fup_sakaro = st.sidebar.checkbox(f"✨ Fup2(5〜7点)×坂路完全 ({int(df['is_syn_fup_sakaro'].sum())}頭)")
syn_f1_rap = st.sidebar.checkbox(f"🔥 F1位×究極ラップ ({int(df['is_syn_f1_rap'].sum())}頭)")
syn_bomb = st.sidebar.checkbox(f"💣 爆弾穴馬 ({int(df['is_syn_bomb'].sum())}頭)")

with st.sidebar.expander("📋 【全レース】黄金シナジー該当馬一覧", expanded=False):
    syn_all = df[df["is_sss"] | df["is_four_crown"] | df["is_syn_iron"] | df["is_syn_high"] | df["is_syn_fup_sakaro"] | df["is_syn_bomb"] | df["is_syn_f1_rap"]].copy()
    if syn_all.empty:
        st.caption("現在該当する馬はいません。")
    else:
        for _, s_row in syn_all.iterrows():
            s_tags = []
            if s_row["is_sss"]: s_tags.append("👑SSS級")
            if s_row["is_four_crown"]: s_tags.append("🏆四冠馬")
            if s_row["is_syn_iron"]: s_tags.append("💎鉄板軸")
            elif s_row["is_syn_high"]: s_tags.append("🔥高確率軸")
            if s_row["is_syn_f1_rap"]: s_tags.append("🔥究極ラップ")
            if s_row["is_syn_fup_sakaro"]: s_tags.append("✨Fup坂路")
            if s_row["is_syn_bomb"]: s_tags.append("💣爆弾")
            tag_str = " ".join(s_tags)
            u_str = f"{int(s_row['馬番'])}番" if pd.notnull(s_row["馬番"]) and s_row["馬番"] != 99 else ""
            st.markdown(f"""
                <div class='sidebar-synergy-item'>
                    <div class='sidebar-synergy-header'>[{s_row['race_id']}] {u_str} {s_row['馬名']}</div>
                    <div style='color:#58a6ff;font-weight:bold;margin-top:2px;'>{tag_str}</div>
                    <div style='color:#8b949e;font-size:11px;'>F:{s_row['F指数']}({s_row['F_rank']}位) | Fup:{int(s_row['Fup'])}点</div>
                </div>
            """, unsafe_allow_html=True)

st.sidebar.markdown("---")

# ==============================================================================
# 8. メイン画面: レース選択（場別タブ切り替え）
# ==============================================================================
st.markdown("### 🎯 レース選択")
venue_sort_order = ["東京", "中山", "京都", "阪神", "中京", "小倉", "新潟", "福島", "函館", "札幌", "その他"]
existing_venues = [v for v in venue_sort_order if v in df["競馬場名"].unique()] + [v for v in df["競馬場名"].unique() if v not in venue_sort_order]

venue_tabs = st.tabs([f"🏟️ {v}" for v in existing_venues])
selected_race_uid = None

for i, v_name in enumerate(existing_venues):
    with venue_tabs[i]:
        v_df = df[df["競馬場名"] == v_name]
        races_in_v = v_df[["race_uid", "race_id", "R番号", "track", "dist"]].drop_duplicates("race_uid").sort_values("R番号")
        race_options = {}
        for _, r_row in races_in_v.iterrows():
            n_horses = len(df[df["race_uid"] == r_row["race_uid"]])
            lbl = f"{r_row['R番号']}R ({r_row['track']}{r_row['dist']}m / {n_horses}頭) [{r_row['race_id']}]"
            race_options[r_row["race_uid"]] = lbl

        if race_options:
            chosen_uid = st.selectbox(f"{v_name}のレースを選択", options=list(race_options.keys()), format_func=lambda x: race_options[x], key=f"sel_race_{v_name}", label_visibility="collapsed")
            if selected_race_uid is None:
                selected_race_uid = chosen_uid

if not selected_race_uid:
    selected_race_uid = df["race_uid"].iloc[0]

race_df = df[df["race_uid"] == selected_race_uid].copy().sort_values("馬番")
filtered_df = race_df.copy()

# フィルタ連動
if syn_sss: filtered_df = filtered_df[filtered_df["is_sss"]]
if syn_iron: filtered_df = filtered_df[filtered_df["is_syn_iron"]]
if syn_high: filtered_df = filtered_df[filtered_df["is_syn_high"]]
if syn_fup_sakaro: filtered_df = filtered_df[filtered_df["is_syn_fup_sakaro"]]
if syn_f1_rap: filtered_df = filtered_df[filtered_df["is_syn_f1_rap"]]
if syn_bomb: filtered_df = filtered_df[filtered_df["is_syn_bomb"]]

# ==============================================================================
# 9. 検索バー & レース概要メトリクス
# ==============================================================================
st.markdown("### 📋 出走馬カード（調教最速・実質負荷判定・血統バイアス・イージーモード完備）")

search_kw = st.text_input("🔍 馬名・調教師・騎手・父名で自由検索", placeholder="検索キーワードを入力...")
if search_kw:
    filtered_df = filtered_df[
        filtered_df["馬名"].str.contains(search_kw, na=False) |
        filtered_df["調教師"].str.contains(search_kw, na=False) |
        filtered_df["騎手"].str.contains(search_kw, na=False) |
        filtered_df["種牡馬"].str.contains(search_kw, na=False)
    ]

# 歪みレース悪条件カウント（ダミー・谷の形・減速調教等）
bad_cond_cnt = 0
for _, r_check in race_df.iterrows():
    if (r_check["Fup"] == 1 and r_check["人気"] <= 3 and r_check["F指数"] < 72) or \
       (r_check["人気"] <= 3 and r_check["F_rank"] >= 8) or \
       (pd.notna(r_check["坂路_4F"]) and not r_check["坂路_完全加速"] and r_check["坂路_4F"] <= 56.0):
        bad_cond_cnt += 1

is_distorted_race = 7 <= bad_cond_cnt <= 12

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"<div class='metric-box'><div class='metric-label'>表示頭数</div><div class='metric-val'>{len(filtered_df)}頭</div></div>", unsafe_allow_html=True)
with c2:
    sakaro_accel_cnt = int((race_df["坂路_完全加速"] == True).sum())
    st.markdown(f"<div class='metric-box'><div class='metric-label'>坂路実質完全加速(A1-A3)</div><div class='metric-val'>{sakaro_accel_cnt}頭</div></div>", unsafe_allow_html=True)
with c3:
    fup_high_cnt = int((race_df["Fup"] >= 5).sum())
    st.markdown(f"<div class='metric-box'><div class='metric-label'>Fup2(5〜7点)</div><div class='metric-val'>{fup_high_cnt}頭</div></div>", unsafe_allow_html=True)
with c4:
    distort_str = "歪みあり🔥" if is_distorted_race else "標準構成"
    st.markdown(f"<div class='metric-box'><div class='metric-label'>歪み判定({bad_cond_cnt}頭該当)</div><div class='metric-val'>{distort_str}</div></div>", unsafe_allow_html=True)

st.markdown("<hr style='border-color:#30363d;margin-top:8px;margin-bottom:20px;'>", unsafe_allow_html=True)

# ==============================================================================
# 10. 出走馬カード一覧の描画
# ==============================================================================
if filtered_df.empty:
    st.info("条件に一致する馬が見つかりませんでした。")
else:
    for _, row in filtered_df.iterrows():
        f_rank = row.get("F_rank", 99)
        f_val = row.get("F指数", 0.0)
        arms_rank = row.get("arms_rank", 99)
        tua_rank = row.get("tua_rank", 99)
        fup_val = row.get("Fup", 0)
        fup_rank = row.get("Fup_rank", 99)
        pop_val = row.get("人気", 99)
        trainer = str(row.get("調教師", "")).strip()
        jockey = str(row.get("騎手", "")).strip()

        # クッション値×種牡馬バイアス
        c_status, c_msg = evaluate_cushion_sire(
            row.get("種牡馬", ""), row.get("競馬場名", ""), row.get("dist", ""), row.get("track", ""), cushion_val
        )

        badges = []
        # SSS級・四冠馬
        if row.get("is_sss", False):
            badges.append("<span class='badge-synergy badge-sss'>👑 SSS級絶対神域</span>")
        if row.get("is_four_crown", False):
            badges.append("<span class='badge-synergy badge-four-crown'>🏆 指数の四冠馬 (単回418%)</span>")

        # 鉄板軸・高確率軸
        if row.get("is_syn_iron", False):
            badges.append("<span class='badge-synergy badge-iron'>💎 鉄板軸馬 (複勝率61.9%)</span>")
        elif row.get("is_syn_high", False):
            badges.append("<span class='badge-synergy badge-high'>🔥 高確率軸 (複勝率55%超)</span>")

        # F1位 × 究極ラップ
        if row.get("is_syn_f1_rap", False):
            badges.append("<span class='badge-synergy badge-f1'>🔥 究極ラップ (F1位×坂路≦12.4s)</span>")

        # Fup2 評価 & ダミー看破
        if fup_val == 7:
            badges.append("<span class='badge-synergy badge-fup-7'>🔥 Fup2確変 (7点)</span>")
        elif fup_val >= 5:
            badges.append(f"<span class='badge-synergy badge-fup-high'>⚡ Fup2優位 ({int(fup_val)}点)</span>")
        elif fup_val == 1 and pop_val <= 3 and f_val < 72:
            badges.append("<span class='badge-synergy badge-dummy'>⚠️ ダミーの罠 (Fup2:1点消去)</span>")

        # 谷の形
        if pop_val <= 3 and f_rank >= 8:
            badges.append("<span class='badge-synergy badge-dummy'>⚠️ 谷の形 (過剰人気消去)</span>")

        # 究極連系
        if f_rank == 1 and arms_rank <= 3 and tua_rank <= 3:
            badges.append("<span class='badge-synergy badge-f1'>🎯 究極連系 (F1+ARMS3内+TUA3内)</span>")

        # F1位 / ARMS1位 / TUA1位
        if f_rank == 1 and not row.get("is_syn_iron", False) and not row.get("is_syn_f1_rap", False):
            badges.append("<span class='badge-synergy badge-f1'>👑 F1位</span>")
        if arms_rank == 1:
            badges.append("<span class='badge-synergy badge-arms1'>🚀 ARMS1位</span>")
        if tua_rank == 1:
            badges.append("<span class='badge-synergy badge-tua1'>🛡️ TUA1位</span>")

        # 爆弾穴馬
        if row.get("is_syn_bomb", False):
            badges.append("<span class='badge-synergy badge-bomb'>💣 爆弾穴馬</span>")

        # 陣営黄金コンビ
        if "木村哲也" in trainer and "ルメール" in jockey:
            if fup_val >= 5:
                badges.append("<span class='badge-synergy badge-cushion-good'>✨ キムテツ×ルメール勝負 (Fup5+)</span>")
            else:
                badges.append("<span class='badge-synergy badge-dummy'>⚠️ キムテツ×ルメール割引 (Fup4以下)</span>")
        if "中内田" in trainer and "川田" in jockey and f_rank == 1:
            badges.append("<span class='badge-synergy badge-cushion-good'>✨ 中内田×川田×F1位 (鉄板軸)</span>")
        if ("斉藤崇史" in trainer or "中舘英二" in trainer) and f_rank == 1:
            badges.append("<span class='badge-synergy badge-cushion-good'>✨ 特注厩舎×F1位 (勝率40%超)</span>")

        # クッション値×種牡馬バイアス
        if c_status == "good":
            badges.append(f"<span class='badge-synergy badge-cushion-good'>{c_msg}</span>")
        elif c_status == "risk":
            badges.append(f"<span class='badge-synergy badge-cushion-risk'>{c_msg}</span>")

        badges_html = " ".join(badges)

        # 坂路調教フォーマット
        has_sakaro = pd.notnull(row.get("坂路_4F")) or pd.notnull(row.get("坂路_Lap1"))
        if has_sakaro:
            is_s_accel = bool(row.get("坂路_完全加速", False))
            s_accel_badge = "<span class='badge-accel'>完全加速(A1〜A3)🔥</span>" if is_s_accel else "<span class='badge-decel'>非加速/減速</span>"
            s_acc2 = row.get("坂路_ラスト2F加速")
            s_acc2_str = f"<strong style='color:#38ef7d;'>+{s_acc2:.1f}s</strong>" if pd.notnull(s_acc2) and s_acc2 > 0 else f"<span style='color:#8b949e;'>{s_acc2:.1f}s</span>" if pd.notnull(s_acc2) else "-s"
            s_rank_badge = format_rank_badge(row.get("坂路_調教順位"))
            s_4f_rk = format_rank_badge(row.get("坂路_4F_rank"))
            s_l1_rk = format_rank_badge(row.get("坂路_Lap1_rank"))
            s_4f_val = f"{row['坂路_4F']:.1f}s" if pd.notnull(row.get("坂路_4F")) else "-s"
            s_l4_val = f"{row['坂路_Lap4']:.1f}" if pd.notnull(row.get("坂路_Lap4")) else "-"
            s_l3_val = f"{row['坂路_Lap3']:.1f}" if pd.notnull(row.get("坂路_Lap3")) else "-"
            s_l2_val = f"{row['坂路_Lap2']:.1f}" if pd.notnull(row.get("坂路_Lap2")) else "-"
            s_l1_val = f"{row['坂路_Lap1']:.1f}" if pd.notnull(row.get("坂路_Lap1")) else "-"

            sakaro_info = (
                f"坂路順位: {s_rank_badge} | 4F全体: <strong>{s_4f_val}</strong> ({s_4f_rk}) | {s_accel_badge} | "
                f"<strong>ラスト2F加速: {s_acc2_str}</strong> [ {s_l4_val} - {s_l3_val} - {s_l2_val} - <strong>{s_l1_val}s</strong> ({s_l1_rk}) ]"
            )
        else:
            sakaro_info = "坂路計測なし"

        # ウッド調教フォーマット
        has_wood = pd.notnull(row.get("wood_Lap1")) or pd.notnull(row.get("wood_5F"))
        if has_wood:
            place = str(row.get("wood_place", "")).strip()
            f5_str = f"{row['wood_5F']:.1f}s" if pd.notnull(row.get("wood_5F")) else "-s"
            w_acc2 = row.get("wood_ラスト2F加速")
            w_acc2_str = f"<strong style='color:#38ef7d;'>+{w_acc2:.1f}s</strong>" if pd.notnull(w_acc2) and w_acc2 > 0 else f"<span style='color:#8b949e;'>{w_acc2:.1f}s</span>" if pd.notnull(w_acc2) else "-s"
            w_rank_badge = format_rank_badge(row.get("wood_調教順位"))
            w_5f_rk = format_rank_badge(row.get("wood_5F_rank"))
            w_l1_rk = format_rank_badge(row.get("wood_Lap1_rank"))
            w_l4_val = f"{row['wood_Lap4']:.1f}" if pd.notnull(row.get("wood_Lap4")) else "-"
            w_l3_val = f"{row['wood_Lap3']:.1f}" if pd.notnull(row.get("wood_Lap3")) else "-"
            w_l2_val = f"{row['wood_Lap2']:.1f}" if pd.notnull(row.get("wood_Lap2")) else "-"
            w_l1_val = f"{row['wood_Lap1']:.1f}" if pd.notnull(row.get("wood_Lap1")) else "-"

            wood_info = (
                f"ウッド順位: {w_rank_badge} | {place} 5F: <strong>{f5_str}</strong> ({w_5f_rk}) | "
                f"<strong>ラスト2F加速: {w_acc2_str}</strong> [ {w_l4_val} - {w_l3_val} - {w_l2_val} - <strong>{w_l1_val}s</strong> ({w_l1_rk}) ]"
            )
        else:
            wood_info = "ウッド計測なし"

        u_no = row["馬番"]
        umaban_str = f"{int(u_no)}番" if u_no != 99 and pd.notnull(u_no) else "番"
        pop_str = f"{int(row['人気'])} 番人気" if pd.notnull(row.get("人気")) else "- 番人気"

        if pd.notnull(fup_val) and fup_val >= 5:
            fup_val_html = f"<span class='fup-high-val'>{int(fup_val)}点</span>"
        elif pd.notnull(fup_val) and fup_val == 1 and pop_val <= 3:
            fup_val_html = f"<span class='fup-danger-val'>{int(fup_val)}点(消)</span>"
        elif pd.notnull(fup_val):
            fup_val_html = f"<strong>{int(fup_val)}点</strong>"
        else:
            fup_val_html = "- 点"

        f_badge = format_rank_badge(row.get("F_rank"))
        arms_badge = format_rank_badge(row.get("arms_rank"))
        tua_badge = format_rank_badge(row.get("tua_rank"))

        card_html = f"""
        <div class='horse-card'>
            <div class='horse-card-header'>
                <span class='horse-card-title'>{umaban_str} {row['馬名']}</span> {badges_html}
            </div>
            <ul class='horse-card-list'>
                <li><strong>陣営/血統</strong>: {trainer} / {jockey} / <strong>父: {row.get('種牡馬', '-')}</strong></li>
                <li><strong>坂路調教 (実質負荷)</strong>: {sakaro_info}</li>
                <li><strong>ウッド調教</strong>: {wood_info}</li>
                <li><strong>能力指数</strong>: F指数: <strong>{row.get('F指数', 0.0)}</strong> ({f_badge}) | ARMS2: <strong>{row.get('arms', 0.0)}</strong> ({arms_badge}) | TUA: <strong>{row.get('tua', 0.0)}</strong> ({tua_badge})</li>
                <li><strong>Fup2</strong>: {fup_val_html} (順位: {format_rank_badge(fup_rank)}) | <strong>人気</strong>: {pop_str} | <strong>GTV印</strong>: {row.get('GTV', '-')}</li>
            </ul>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)

# ==============================================================================
# 11. 競馬予想10 実戦買い目フォーメーション改善規定（新フォーミュラ）
# ==============================================================================
st.markdown("---")
st.subheader("🎫 競馬予想10 実戦買い目フォーメーション（新フォーミュラ完全準拠）")

# 軸馬・相手・ヒモ候補の自動選定
sorted_race = race_df.sort_values(by=["F_rank", "F指数", "Fup"], ascending=[True, False, False])
axis_horse = sorted_race.iloc[0]
axis_id = int(axis_horse["馬番"]) if pd.notnull(axis_horse["馬番"]) else 1

opp_horses = sorted_race.iloc[1:4]["馬番"].dropna().astype(int).tolist()
himo_horses = sorted_race.iloc[4:8]["馬番"].dropna().astype(int).tolist()

b1, b2 = st.columns(2)

with b1:
    st.markdown(f"""
    **【本線：単勝・複勝】**
    * 単勝: **{axis_id}**（本命連軸・重点配分）
    * 複勝: **{opp_horses[0] if opp_horses else axis_id}**
    
    **【本線：3連複フォーメーション（中京8R的中モデル）】**
    * **1列目 (軸)**: `{axis_id}`
    * **2列目 (相手)**: `{opp_horses}`
    * **3列目 (ヒモ広め)**: `{opp_horses + himo_horses}`
    """)

with b2:
    st.markdown(f"""
    **【高配当狙い：3連単 2・3着連軸マルチ（裏表標準化）】**
    * **1着**: `{axis_id}`, `{opp_horses[0] if opp_horses else axis_id}`
    * **2着**: `{axis_id}`, `{opp_horses}`
    * **3着**: `{axis_id}`, `{opp_horses + himo_horses}`
    
    **【抑え・資金回収：ワイド（1〜2点）】**
    * `{axis_id}` － `{opp_horses[0] if opp_horses else ''}`（高回収狙い）
    * `{axis_id}` － `{opp_horses[1] if len(opp_horses) > 1 else ''}`
    """)

st.caption("💡 毎週の運用: TARGETから出力したCSVをGitHubの `data/` にコミットするだけで、自動的に即時画面が切り替わります。")
