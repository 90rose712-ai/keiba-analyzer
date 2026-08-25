import os
import re
import numpy as np
import pandas as pd
import streamlit as st

# ==============================================================================
# 1. ページ基本設定
# ==============================================================================
st.set_page_config(
    page_title="Streamlit - 競馬予想10 クッション値Vr",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================================
# 2. CSSスタイル（ダークテーマUI & 豪華特注バッジ）
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
        margin-bottom: 6px;
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
    .badge-fup-top {
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
    .badge-bomb {
        background: linear-gradient(135deg, #EB3349 0%, #F45C43 100%);
        color: #ffffff;
        border: 1px solid #FFA07A;
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
    
    /* Fup数値ハイライト */
    .fup-high-val {
        color: #FFD700;
        font-weight: bold;
        background-color: rgba(255, 165, 0, 0.2);
        padding: 1px 6px;
        border-radius: 4px;
        border: 1px solid rgba(255, 165, 0, 0.5);
    }

    /* サイドバー専用シナジーリストカード */
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
    .sidebar-synergy-header {
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 2px;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# 3. クリーニング＆汎用読み込みヘルパー
# ==============================================================================
st.sidebar.markdown("### 📁 4大CSVデータ読み込み")
with st.sidebar.expander("CSVファイルの指定 / アップロード", expanded=False):
  up_index = st.file_uploader(
      "1. 出馬表・指数 CSV", type=["csv"], key="up_index"
  )
  up_gtv = st.file_uploader("2. GTVオッズ CSV", type=["csv"], key="up_gtv")
  up_sakaro = st.file_uploader(
      "3. 坂路調教 CSV", type=["csv"], key="up_sakaro"
  )
  up_wood = st.file_uploader("4. ウッド調教 CSV", type=["csv"], key="up_wood")


def clean_horse_name(name):
  if pd.isnull(name):
    return ""
  s = str(name).strip()
  s = (
      s.replace("*", "")
      .replace("$", "")
      .replace(" ", "")
      .replace(" ", "")
      .replace("\t", "")
  )
  return s


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
    return pd.read_csv(src, encoding="shift-jis")
  except Exception:
    try:
      if hasattr(src, "seek"):
        src.seek(0)
      return pd.read_csv(src, encoding="utf-8", errors="ignore")
    except Exception:
      return pd.DataFrame()


def find_col(df, candidates):
  for c in candidates:
    if c in df.columns:
      return c
  return None


def format_rank_badge(rank_val):
  if pd.isnull(rank_val) or rank_val == 99 or rank_val == 0:
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


def format_fup_rank_badge(rank_val):
  if pd.isnull(rank_val) or rank_val == 99 or rank_val == 0:
    return "<span class='rank-normal'>-位</span>"
  try:
    r = int(rank_val)
  except Exception:
    return "<span class='rank-normal'>-位</span>"

  if r == 1:
    return "<span class='rank-1st'>🥇 1位</span>"
  else:
    return f"<span class='rank-normal'>{r}位</span>"


# ==============================================================================
# 4. データロード＆調教詳細（順位・ラスト2F加速）統合処理
# ==============================================================================
@st.cache_data
def load_and_merge_all(f_index, f_gtv, f_sakaro, f_wood):
  # 1. 出馬表・指数 CSV
  index_src = f_index
  if index_src is None:
    for name in ["出馬表_指数.csv", "指数、検証用.csv", "指数.csv"]:
      if os.path.exists(name):
        index_src = name
        break

  records = []
  if index_src is not None:
    if isinstance(index_src, str):
      with open(index_src, "r", encoding="shift-jis", errors="ignore") as f:
        lines = f.readlines()
    else:
      content = index_src.read()
      try:
        lines = content.decode("shift-jis").splitlines()
      except Exception:
        lines = content.decode("utf-8", errors="ignore").splitlines()

    fw_map = {
        "１": 1,
        "２": 2,
        "３": 3,
        "４": 4,
        "５": 5,
        "６": 6,
        "７": 7,
        "８": 8,
        "９": 9,
        "10": 10,
        "11": 11,
        "12": 12,
        "13": 13,
        "14": 14,
        "15": 15,
        "16": 16,
        "17": 17,
        "18": 18,
    }

    for line_idx, line in enumerate(lines):
      parts = [p.strip() for p in line.strip().split(",")]
      n = len(parts)
      if n < 10:
        continue

      race_id, track, dist, umaban, horse_raw = (
          parts[0],
          "",
          "",
          "",
          None,
      )
      trainer, jockey, sire = "", "", ""
      pop, finish, fup, fup_rank, f_val, f_rank = (
          None,
          None,
          0,
          99,
          0.0,
          99,
      )
      arms_val, arms_rank, tua_val, tua_rank = 0.0, 99, 0.0, 99

      if n == 24:
        track, dist, umaban = parts[1], parts[2], parts[3]
        horse_raw = parts[4]
        trainer, jockey = parts[6], parts[7]
        pop = parts[8]
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
        fup = pd.to_numeric(parts[10], errors="coerce")
        fup_rank = pd.to_numeric(parts[11], errors="coerce")
        f_val = pd.to_numeric(parts[12], errors="coerce")
        f_rank = pd.to_numeric(parts[13], errors="coerce")
        arms_val = pd.to_numeric(parts[16], errors="coerce")
        arms_rank = pd.to_numeric(parts[17], errors="coerce")
        tua_val = pd.to_numeric(parts[18], errors="coerce")
        tua_rank = pd.to_numeric(parts[19], errors="coerce")
        finish = parts[20]
        sire = parts[21] if n > 21 else ""
      elif n >= 26:
        track, dist, umaban = parts[1], parts[2], parts[3]
        trainer, jockey = parts[5], parts[6]
        horse_raw = parts[7]
        pop = parts[8]
        fup = pd.to_numeric(parts[10], errors="coerce")
        fup_rank = pd.to_numeric(parts[11], errors="coerce")
        f_val = pd.to_numeric(parts[12], errors="coerce")
        f_rank = pd.to_numeric(parts[13], errors="coerce")
        arms_val = pd.to_numeric(parts[18], errors="coerce")
        arms_rank = pd.to_numeric(parts[19], errors="coerce")
        tua_val = pd.to_numeric(parts[21], errors="coerce")
        tua_rank = pd.to_numeric(parts[22], errors="coerce")
        finish = parts[24]
        sire = parts[25] if n > 25 else ""
      else:
        continue

      horse = clean_horse_name(horse_raw)
      if horse:
        fin_int = fw_map.get(
            finish, int(finish) if str(finish).isdigit() else np.nan
        )
        pop_int = int(pop) if str(pop).isdigit() else np.nan
        u_int = int(umaban) if str(umaban).isdigit() else 99

        records.append({
            "race_id": race_id,
            "track": track,
            "dist": dist,
            "馬番": u_int,
            "馬名": horse,
            "調教師": str(trainer).strip(),
            "騎手": str(jockey).strip(),
            "種牡馬": str(sire).strip(),
            "人気": pop_int,
            "着順": fin_int,
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
  df_main["race_uid"] = (
      df_main["batch_id"].astype(str) + "_" + df_main["race_id"]
  )

  venue_dict = {
      "東": "東京",
      "中": "中山",
      "京": "京都",
      "阪": "阪神",
      "名": "中京",
      "小": "小倉",
      "新": "新潟",
      "福": "福島",
      "函": "函館",
      "札": "札幌",
  }

  def parse_race(rid):
    match = re.match(r"([^\d]+)(\d+)", str(rid))
    if match:
      v_code, r_no = match.group(1), int(match.group(2))
      v_name = venue_dict.get(v_code, v_code)
      return v_name, r_no
    return "その他", 99

  df_main[["競馬場名", "R番号"]] = df_main["race_id"].apply(
      lambda x: pd.Series(parse_race(x))
  )

  # 2. GTVオッズ CSV
  df_gtv = read_csv_flexible(f_gtv, ["GTV馬.csv", "GTV.csv"])
  if not df_gtv.empty:
    name_col = find_col(df_gtv, ["馬名", "馬 名", "競走馬名"])
    if name_col:
      df_gtv["馬名"] = df_gtv[name_col].apply(clean_horse_name)
      gtv_cols = [c for c in df_gtv.columns if c not in ["馬名", name_col]]
      df_main = pd.merge(
          df_main,
          df_gtv[["馬名"] + gtv_cols].drop_duplicates("馬名"),
          on="馬名",
          how="left",
      )

  # 3. 坂路調教 CSV
  df_sakaro = read_csv_flexible(
      f_sakaro, ["出馬表_坂路.csv", "坂路調教.csv", "坂路.csv"]
  )
  if not df_sakaro.empty:
    s_name = find_col(df_sakaro, ["馬名", "馬 名", "競走馬名"])
    if s_name:
      df_sakaro["馬名"] = df_sakaro[s_name].apply(clean_horse_name)
      c_4f = find_col(df_sakaro, ["Time1", "4F", "４Ｆ", "４F", "4f"])
      c_lap4 = find_col(df_sakaro, ["Lap4", "lap4", "LAP4", "L4"])
      c_lap3 = find_col(df_sakaro, ["Lap3", "lap3", "LAP3", "L3"])
      c_lap2 = find_col(df_sakaro, ["Lap2", "lap2", "LAP2", "L2"])
      c_lap1 = find_col(df_sakaro, ["Lap1", "lap1", "LAP1", "L1", "1F"])

      df_sakaro["坂路_4F"] = (
          pd.to_numeric(df_sakaro[c_4f], errors="coerce") if c_4f else np.nan
      )
      df_sakaro["坂路_Lap4"] = (
          pd.to_numeric(df_sakaro[c_lap4], errors="coerce")
          if c_lap4
          else np.nan
      )
      df_sakaro["坂路_Lap3"] = (
          pd.to_numeric(df_sakaro[c_lap3], errors="coerce")
          if c_lap3
          else np.nan
      )
      df_sakaro["坂路_Lap2"] = (
          pd.to_numeric(df_sakaro[c_lap2], errors="coerce")
          if c_lap2
          else np.nan
      )
      df_sakaro["坂路_Lap1"] = (
          pd.to_numeric(df_sakaro[c_lap1], errors="coerce")
          if c_lap1
          else np.nan
      )

      # 坂路実質負荷 & 完全加速（Lap4 > Lap3 > Lap2 > Lap1 かつ 4F<=56.0 & 1F<=13.0）
      t1 = df_sakaro["坂路_4F"]
      l4, l3, l2, l1 = (
          df_sakaro["坂路_Lap4"],
          df_sakaro["坂路_Lap3"],
          df_sakaro["坂路_Lap2"],
          df_sakaro["坂路_Lap1"],
      )
      df_sakaro["坂路_ラスト2F加速"] = np.round(l2 - l1, 2)
      df_sakaro["坂路_完全加速"] = (
          (l4 > l3)
          & (l3 > l2)
          & (l2 > l1)
          & (t1 <= 56.0)
          & (l1 <= 13.0)
      )

      # 総合評価スコア（調教順位用）
      df_sakaro["坂路_スコア"] = (
          np.where(df_sakaro["坂路_完全加速"], 100, 0)
          + (60.0 - df_sakaro["坂路_Lap1"].fillna(20.0)) * 3
          + df_sakaro["坂路_ラスト2F加速"].fillna(0.0) * 5
          + (60.0 - df_sakaro["坂路_4F"].fillna(65.0))
      )

      # 最良調教を馬ごとに抽出
      s_best = (
          df_sakaro.sort_values(
              by=["坂路_完全加速", "坂路_スコア", "坂路_Lap1"],
              ascending=[False, False, True],
          )
          .groupby("馬名")
          .first()
          .reset_index()
      )

      sakaro_cols = [
          "馬名",
          "坂路_4F",
          "坂路_Lap4",
          "坂路_Lap3",
          "坂路_Lap2",
          "坂路_Lap1",
          "坂路_ラスト2F加速",
          "坂路_完全加速",
          "坂路_スコア",
      ]
      df_main = pd.merge(
          df_main,
          s_best[sakaro_cols].drop_duplicates("馬名"),
          on="馬名",
          how="left",
      )

  if "坂路_4F" not in df_main.columns:
    df_main["坂路_4F"] = np.nan
    df_main["坂路_Lap4"] = np.nan
    df_main["坂路_Lap3"] = np.nan
    df_main["坂路_Lap2"] = np.nan
    df_main["坂路_Lap1"] = np.nan
    df_main["坂路_ラスト2F加速"] = np.nan
    df_main["坂路_完全加速"] = False
    df_main["坂路_スコア"] = -999

  # 4. ウッド調教 CSV
  df_wood_raw = read_csv_flexible(
      f_wood, ["出馬表_ウッド.csv", "ウッド、検証用.csv", "ウッド.csv"]
  )
  if not df_wood_raw.empty:
    w_df = df_wood_raw[df_wood_raw.iloc[:, 0] != "場所"].copy()
    c_w_name = find_col(w_df, ["馬名", "馬 名", "競走馬名"])
    if c_w_name:
      w_df["馬名"] = w_df[c_w_name].apply(clean_horse_name)
      c_w_5f = find_col(w_df, ["5F", "５Ｆ", "５F", "5f"])
      c_w_4f = find_col(w_df, ["4F", "４Ｆ", "４F", "4f"])
      c_w_l4 = find_col(w_df, ["Lap4", "lap4", "LAP4", "L4"])
      c_w_l3 = find_col(w_df, ["Lap3", "lap3", "LAP3", "L3"])
      c_w_l2 = find_col(w_df, ["Lap2", "lap2", "LAP2", "L2"])
      c_w_l1 = find_col(w_df, ["Lap1", "lap1", "LAP1", "L1", "1F"])
      c_w_plc = find_col(w_df, ["場所", "調教場", "場"])

      w_df["wood_5F"] = (
          pd.to_numeric(w_df[c_w_5f], errors="coerce") if c_w_5f else np.nan
      )
      w_df["wood_4F"] = (
          pd.to_numeric(w_df[c_w_4f], errors="coerce") if c_w_4f else np.nan
      )
      w_df["wood_Lap4"] = (
          pd.to_numeric(w_df[c_w_l4], errors="coerce") if c_w_l4 else np.nan
      )
      w_df["wood_Lap3"] = (
          pd.to_numeric(w_df[c_w_l3], errors="coerce") if c_w_l3 else np.nan
      )
      w_df["wood_Lap2"] = (
          pd.to_numeric(w_df[c_w_l2], errors="coerce") if c_w_l2 else np.nan
      )
      w_df["wood_Lap1"] = (
          pd.to_numeric(w_df[c_w_l1], errors="coerce") if c_w_l1 else np.nan
      )
      w_df["wood_place"] = w_df[c_w_plc].astype(str) if c_w_plc else ""

      w_df["wood_ラスト2F加速"] = np.round(
          w_df["wood_Lap2"] - w_df["wood_Lap1"], 2
      )
      w_df["is_wood_accel"] = (w_df["wood_ラスト2F加速"] > 0) & (
          w_df["wood_ラスト2F加速"].notna()
      )

      # ウッド総合スコア
      w_df["wood_スコア"] = (
          (20.0 - w_df["wood_Lap1"].fillna(20.0)) * 3
          + w_df["wood_ラスト2F加速"].fillna(0.0) * 4
          + (75.0 - w_df["wood_5F"].fillna(85.0))
      )

      w_best = (
          w_df.sort_values(
              by=["wood_スコア", "wood_Lap1"], ascending=[False, True]
          )
          .groupby("馬名")
          .first()
          .reset_index()
      )

      wood_cols = [
          "馬名",
          "wood_place",
          "wood_5F",
          "wood_4F",
          "wood_Lap4",
          "wood_Lap3",
          "wood_Lap2",
          "wood_Lap1",
          "wood_ラスト2F加速",
          "is_wood_accel",
          "wood_スコア",
      ]
      df_main = pd.merge(
          df_main,
          w_best[wood_cols].drop_duplicates("馬名"),
          on="馬名",
          how="left",
      )

  if "wood_Lap1" not in df_main.columns:
    df_main["wood_place"] = ""
    df_main["wood_5F"] = np.nan
    df_main["wood_4F"] = np.nan
    df_main["wood_Lap4"] = np.nan
    df_main["wood_Lap3"] = np.nan
    df_main["wood_Lap2"] = np.nan
    df_main["wood_Lap1"] = np.nan
    df_main["wood_ラスト2F加速"] = np.nan
    df_main["is_wood_accel"] = False
    df_main["wood_スコア"] = -999

  # ==============================================================================
  # レース内での馬同士の調教順位付け (スコア降順 & 終いタイム昇順)
  # ==============================================================================
  # 坂路総合順位（レース内）
  df_main["坂路_調教順位"] = df_main.groupby("race_uid")["坂路_スコア"].rank(
      method="min", ascending=False
  )
  df_main.loc[df_main["坂路_4F"].isna(), "坂路_調教順位"] = np.nan

  # ウッド総合順位（レース内）
  df_main["wood_調教順位"] = df_main.groupby("race_uid")[
      "wood_スコア"
  ].rank(method="min", ascending=False)
  df_main.loc[df_main["wood_Lap1"].isna(), "wood_調教順位"] = np.nan

  # 各ラップタイム順位
  df_main["坂路_4F_rank"] = df_main.groupby("race_uid")["坂路_4F"].rank(
      method="min", ascending=True
  )
  df_main["坂路_Lap1_rank"] = df_main.groupby("race_uid")["坂路_Lap1"].rank(
      method="min", ascending=True
  )
  df_main["wood_5F_rank"] = df_main.groupby("race_uid")["wood_5F"].rank(
      method="min", ascending=True
  )
  df_main["wood_Lap1_rank"] = df_main.groupby("race_uid")["wood_Lap1"].rank(
      method="min", ascending=True
  )

  return df_main


# 統合データ読み込み実行
df = load_and_merge_all(up_index, up_gtv, up_sakaro, up_wood)

# ==============================================================================
# 5. クッション値×種牡馬バイアス判定ロジック
# ==============================================================================


def evaluate_cushion_sire(sire, track_name, dist_str, surface, c_val):
  if pd.isnull(sire) or not str(sire).strip():
    return None, ""
  s = str(sire).strip()
  track = str(track_name).strip()

  # クッション区分
  if c_val <= 8.5:
    c_band = "低め"
  elif c_val <= 9.4:
    c_band = "やや低め"
  elif c_val <= 9.9:
    c_band = "標準高"
  elif c_val <= 10.4:
    c_band = "高め"
  else:
    c_band = "超高"

  # 1. 超高帯（>=10.5）判定
  if c_val >= 10.5:
    if any(k in s for k in ["エピファネイア", "キタサンブラック", "イスラボニータ"]):
      return (
          "good",
          f"✨ 超高クッション特注血統 ({s}: 複差大幅プラス)",
      )
    if any(
        k in s
        for k in [
            "キングカメハメハ",
            "ビッグアーサー",
            "レイデオロ",
            "スワーヴリチャード",
            "サートゥルナーリア",
            "ゴールドシップ",
        ]
    ):
      return (
          "risk",
          f"⚠️ 超高クッション危険血統 ({s}: 複勝率急落)",
      )

  # 2. コース別特注・危険判定
  if track == "中京" and "ディープインパクト" in s and c_band == "やや低め":
    return (
        "good",
        "🎯 中京芝2000×ディープインパクト (勝率18.0% / 単回178%)",
    )
  if track == "東京" and "エピファネイア" in s and c_band == "標準高":
    return (
        "good",
        "🎯 東京芝1600×エピファネイア (勝率13.3% / 単回277%)",
    )
  if track == "東京" and "モーリス" in s and c_band == "標準高":
    return (
        "good",
        "🎯 東京芝1400×モーリス (勝率10.1% / 単回408%)",
    )
  if track == "東京" and "ディープインパクト" in s and c_band == "標準高":
    return (
        "good",
        "🎯 東京芝1800×ディープインパクト (勝率15.8% / 単回228%)",
    )
  if track == "東京" and "キズナ" in s and c_band == "やや低め":
    return "good", "🎯 東京芝2000×キズナ (勝率19.7% / 単回200%)"
  if track == "阪神" and "キズナ" in s and c_band == "標準高":
    return "good", "🎯 阪神芝1800×キズナ (勝率19.6% / 単回421%)"
  if track == "阪神" and "ルーラーシップ" in s and c_band == "やや低め":
    return (
        "good",
        "🎯 阪神芝1600×ルーラーシップ (勝率20.0% / 単回156%)",
    )
  if track == "中山" and "シルバーステート" in s and c_band == "標準高":
    return (
        "good",
        "🎯 中山芝1600×シルバーステート (勝率17.1% / 単回225%)",
    )
  if track == "札幌" and "オルフェーヴル" in s and c_val <= 8.5:
    return (
        "good",
        "🎯 札幌芝2000×オルフェーヴル (勝率15.8% / 単回136%)",
    )
  if track == "函館" and "キズナ" in s and c_val <= 8.5:
    return "good", "🎯 函館芝1800×キズナ (勝率17.7% / 単回143%)"
  if track == "福島" and "ダノンバラード" in s and c_band == "やや低め":
    return (
        "good",
        "🎯 福島芝1800×ダノンバラード (勝率19.4% / 単回413%)",
    )
  if track == "小倉" and "ダイワメジャー" in s and c_band == "標準高":
    return (
        "good",
        "🎯 小倉芝1200×ダイワメジャー (勝率13.6% / 単回173%)",
    )
  if track == "新潟" and "ロードカナロア" in s and c_band == "やや低め":
    return (
        "good",
        "🎯 新潟芝1400×ロードカナロア (勝率10.9% / 単回174%)",
    )

  # 危険コース判定
  if track == "中山" and "ダノンバラード" in s and c_band == "標準高":
    return "risk", "⚠️ 中山芝2000×ダノンバラード (複勝率0.0%)"
  if track == "東京" and "ルーラーシップ" in s and c_band == "標準高":
    return "risk", "⚠️ 東京芝×ルーラーシップ (高クッション帯勝率0%)"
  if track == "東京" and "ゴールドシップ" in s and c_band == "やや低め":
    return "risk", "⚠️ 東京芝×ゴールドシップ (複勝率4.5%極小)"
  if track == "小倉" and "ジャスタウェイ" in s and c_band == "やや低め":
    return "risk", "⚠️ 小倉芝1200×ジャスタウェイ (複勝率2.9%)"
  if track == "新潟" and "リオンディーズ" in s and c_band == "やや低め":
    return "risk", "⚠️ 新潟芝1400×リオンディーズ (複勝率6.7%)"

  return None, ""


# ==============================================================================
# 6. 黄金シナジー該当フラグを全データに付与
# ==============================================================================
if not df.empty:
  df["is_syn_iron"] = (
      (df["F_rank"] == 1)
      & (df["arms_rank"] <= 3)
      & (df["wood_Lap1"] <= 11.5)
      & (df["is_wood_accel"] == True)
  )
  df["is_syn_high"] = (
      ((df["F_rank"] == 1) | (df["F指数"] >= 66))
      & (df["wood_Lap1"] <= 11.5)
      & (df["is_wood_accel"] == True)
  )
  df["is_syn_fup_sakaro"] = (df["Fup"] >= 5) & (df["坂路_完全加速"] == True)
  df["is_syn_bomb"] = (
      (df["人気"] >= 6)
      & (df["Fup"] >= 4)
      & ((df["is_wood_accel"] == True) | (df["坂路_完全加速"] == True))
  )
  df["is_syn_f1_rap"] = (df["F_rank"] == 1) & (
      ((df["wood_Lap1"] <= 12.4) & (df["is_wood_accel"] == True))
      | ((df["坂路_Lap1"] <= 12.4) & (df["坂路_完全加速"] == True))
  )

# ==============================================================================
# 7. サイドバー: 条件・操作エリア
# ==============================================================================
st.sidebar.markdown("---")
st.sidebar.markdown("### 芝馬場状態")
turf_condition = st.sidebar.selectbox(
    "芝馬場状態",
    ["良", "稍重", "重", "不良"],
    index=0,
    label_visibility="collapsed",
)

st.sidebar.markdown("### 芝クッション値")
cushion_val = st.sidebar.number_input(
    "芝クッション値",
    min_value=7.0,
    max_value=12.0,
    value=9.5,
    step=0.1,
    label_visibility="collapsed",
)

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

st.sidebar.button(band_label, use_container_width=True)

if st.sidebar.button("🔄 最新データへ強制再読み込み", use_container_width=True):
  st.cache_data.clear()
  st.rerun()

st.sidebar.markdown("---")

# ==============================================================================
# 8. 左側サイドバー: 全レース横断 黄金シナジー抽出
# ==============================================================================
st.sidebar.markdown("### 👑 黄金シナジー抽出")

if not df.empty:
  iron_cnt = int(df["is_syn_iron"].sum())
  high_cnt = int(df["is_syn_high"].sum())
  fup_sakaro_cnt = int(df["is_syn_fup_sakaro"].sum())
  f1_rap_cnt = int(df["is_syn_f1_rap"].sum())
  bomb_cnt = int(df["is_syn_bomb"].sum())
else:
  iron_cnt, high_cnt, fup_sakaro_cnt, f1_rap_cnt, bomb_cnt = 0, 0, 0, 0, 0

syn_iron = st.sidebar.checkbox(
    f"💎 鉄板軸馬 (該当: {iron_cnt}頭)",
    help="複勝率 61.9% / 連対率 46.3%",
)
syn_high = st.sidebar.checkbox(
    f"🔥 高確率軸馬 (該当: {high_cnt}頭)", help="複勝率 54.8〜59.0%"
)
syn_fup_sakaro = st.sidebar.checkbox(
    f"✨ Fup2(5〜7点) × 坂路完全 (該当: {fup_sakaro_cnt}頭)",
    help="坂路完全加速かつFup高評価",
)
syn_f1_rap = st.sidebar.checkbox(
    f"🔥 SSS級・F1位 × 究極ラップ (該当: {f1_rap_cnt}頭)"
)
syn_bomb = st.sidebar.checkbox(f"💣 爆弾穴馬 (該当: {bomb_cnt}頭)")

with st.sidebar.expander("📋 【全レース】黄金シナジー該当馬一覧", expanded=True):
  if not df.empty:
    any_synergy_df = df[
        (df["is_syn_iron"] == True)
        | (df["is_syn_high"] == True)
        | (df["is_syn_fup_sakaro"] == True)
        | (df["is_syn_bomb"] == True)
    ].copy()

    if any_synergy_df.empty:
      st.caption("現在該当する馬はいません。")
    else:
      for _, s_row in any_synergy_df.iterrows():
        s_tags = []
        if s_row["is_syn_iron"]:
          s_tags.append("💎鉄板軸")
        elif s_row["is_syn_high"]:
          s_tags.append("🔥高確率軸")
        if s_row["is_syn_fup_sakaro"]:
          s_tags.append("✨Fup坂路")
        if s_row["is_syn_bomb"]:
          s_tags.append("💣爆弾")

        tag_str = " ".join(s_tags)
        u_str = (
            f"{int(s_row['馬番'])}番"
            if pd.notnull(s_row["馬番"]) and s_row["馬番"] != 99
            else ""
        )

        st.markdown(
            f"""
                <div class='sidebar-synergy-item'>
                    <div class='sidebar-synergy-header'>[{s_row['race_id']}] {u_str} {s_row['馬名']}</div>
                    <div style='color:#58a6ff;font-weight:bold;margin-top:2px;'>{tag_str}</div>
                    <div style='color:#8b949e;font-size:11px;'>F:{s_row['F指数']}({s_row['F_rank']}位) | Fup:{int(s_row['Fup'])}点</div>
                </div>
                """,
            unsafe_allow_html=True,
        )

st.sidebar.markdown("---")

# ==============================================================================
# 9. メイン画面 & レース選択
# ==============================================================================
if df.empty:
  st.warning(
      "⚠️ CSVデータが読み込まれていません。サイドバーの「📁"
      " 4大CSVデータ読み込み」からファイルを指定するか、同一フォルダにCSVを配置してください。"
  )
  st.stop()

st.markdown("### 🎯 レース選択")
venue_sort_order = [
    "東京",
    "中山",
    "京都",
    "阪神",
    "中京",
    "小倉",
    "新潟",
    "福島",
    "函館",
    "札幌",
    "その他",
]
existing_venues = [
    v for v in venue_sort_order if v in df["競馬場名"].unique()
] + [v for v in df["競馬場名"].unique() if v not in venue_sort_order]

venue_tabs = st.tabs([f"🏟️ {v}" for v in existing_venues])
selected_race_uid = None

for i, v_name in enumerate(existing_venues):
  with venue_tabs[i]:
    v_df = df[df["競馬場名"] == v_name]
    races_in_v = (
        v_df[["race_uid", "race_id", "R番号", "track", "dist"]]
        .drop_duplicates("race_uid")
        .sort_values("R番号")
    )

    race_options = {}
    for _, r_row in races_in_v.iterrows():
      n_horses = len(df[df["race_uid"] == r_row["race_uid"]])
      lbl = f"{r_row['R番号']}R ({r_row['track']}{r_row['dist']}m / {n_horses}頭) [{r_row['race_id']}]"
      race_options[r_row["race_uid"]] = lbl

    if race_options:
      chosen_uid = st.selectbox(
          f"{v_name}のレースを選択",
          options=list(race_options.keys()),
          format_func=lambda x: race_options[x],
          key=f"sel_race_{v_name}",
          label_visibility="collapsed",
      )
      if selected_race_uid is None:
        selected_race_uid = chosen_uid

if not selected_race_uid:
  selected_race_uid = df["race_uid"].iloc[0]

race_df = df[df["race_uid"] == selected_race_uid].copy().sort_values("馬番")
filtered_df = race_df.copy()

# フィルタリング
if syn_iron:
  filtered_df = filtered_df[filtered_df["is_syn_iron"] == True]
if syn_high:
  filtered_df = filtered_df[filtered_df["is_syn_high"] == True]
if syn_fup_sakaro:
  filtered_df = filtered_df[filtered_df["is_syn_fup_sakaro"] == True]
if syn_f1_rap:
  filtered_df = filtered_df[filtered_df["is_syn_f1_rap"] == True]
if syn_bomb:
  filtered_df = filtered_df[filtered_df["is_syn_bomb"] == True]

st.markdown(
    "<hr style='border-color:#30363d;margin-top:10px;margin-bottom:15px;'>",
    unsafe_allow_html=True,
)

# ==============================================================================
# 10. 検索バー & 上部サマリーカウンター
# ==============================================================================
st.markdown(
    "### 📋 出走馬カード（調教最速・馬間順位・ラスト2F加速・血統バイアス完備）"
)

search_kw = st.text_input(
    "🔍 馬名・調教師・騎手・父名で自由検索",
    placeholder="検索キーワードを入力...",
)
if search_kw:
  filtered_df = filtered_df[
      filtered_df["馬名"].str.contains(search_kw, na=False)
      | filtered_df["調教師"].str.contains(search_kw, na=False)
      | filtered_df["騎手"].str.contains(search_kw, na=False)
      | filtered_df["種牡馬"].str.contains(search_kw, na=False)
  ]

c1, c2, c3, c4 = st.columns(4)
with c1:
  st.markdown(
      f"<div class='metric-box'><div class='metric-label'>表示頭数</div><div"
      f" class='metric-val'>{len(filtered_df)}頭</div></div>",
      unsafe_allow_html=True,
  )
with c2:
  sakaro_accel_cnt = (
      int((race_df["坂路_完全加速"] == True).sum())
      if "坂路_完全加速" in race_df.columns
      else 0
  )
  st.markdown(
      f"<div class='metric-box'><div"
      " class='metric-label'>坂路完全加速</div><div"
      f" class='metric-val'>{sakaro_accel_cnt}頭</div></div>",
      unsafe_allow_html=True,
  )
with c3:
  fup_high_cnt = (
      int((race_df["Fup"] >= 5).sum()) if "Fup" in race_df.columns else 0
  )
  st.markdown(
      f"<div class='metric-box'><div"
      " class='metric-label'>Fup2(5点以上)</div><div"
      f" class='metric-val'>{fup_high_cnt}頭</div></div>",
      unsafe_allow_html=True,
  )
with c4:
  wood_accel_cnt = (
      int((race_df["is_wood_accel"] == True).sum())
      if "is_wood_accel" in race_df.columns
      else 0
  )
  st.markdown(
      f"<div class='metric-box'><div"
      " class='metric-label'>ウッド加速該当</div><div"
      f" class='metric-val'>{wood_accel_cnt}頭</div></div>",
      unsafe_allow_html=True,
  )

st.markdown(
    "<hr style='border-color:#30363d;margin-top:8px;margin-bottom:20px;'>",
    unsafe_allow_html=True,
)

# ==============================================================================
# 11. 出走馬カード一覧の描画（調教順位・ラスト2F加速秒数を完全網羅）
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

    # クッション値×種牡馬バイアス判定
    c_status, c_msg = evaluate_cushion_sire(
        row.get("種牡馬", ""),
        row.get("競馬場名", ""),
        row.get("dist", ""),
        row.get("track", ""),
        cushion_val,
    )

    badges = []
    # 1. 鉄板軸馬
    if row.get("is_syn_iron", False):
      badges.append(
          "<span class='badge-synergy badge-iron'>💎 鉄板軸馬"
          " (複勝率61.9%)</span>"
      )
    elif row.get("is_syn_high", False):
      badges.append(
          "<span class='badge-synergy badge-high'>🔥 高確率軸"
          " (複勝率55%超)</span>"
      )

    # 2. Fup2 坂路完全加速
    if row.get("is_syn_fup_sakaro", False):
      badges.append(
          "<span class='badge-synergy badge-sakaro-fup'>✨ Fup坂路完全</span>"
      )

    # 3. Fup 1位 & 5点以上バッジ
    if fup_rank == 1 and fup_val >= 5:
      badges.append(
          "<span class='badge-synergy badge-fup-top'>🌟 Fup 1位"
          " (5点+)</span>"
      )
    elif fup_rank == 1:
      badges.append("<span class='badge-synergy badge-fup-top'>👑 Fup 1位</span>")
    elif fup_val >= 5:
      badges.append(
          "<span class='badge-synergy badge-fup-high'>⚡ Fup 5点+</span>"
      )

    # 4. F指数 1位
    if f_rank == 1 and not row.get("is_syn_iron", False):
      badges.append("<span class='badge-synergy badge-f1'>👑 F1位</span>")
    elif f_val >= 66:
      badges.append("<span class='badge-synergy badge-f1'>🔥 F66+</span>")

    # 5. arms / tua 1位
    if arms_rank == 1:
      badges.append("<span class='badge-synergy badge-arms1'>🚀 arms1位</span>")
    if tua_rank == 1:
      badges.append("<span class='badge-synergy badge-tua1'>🛡️ tua1位</span>")

    # 6. 爆弾穴馬
    if row.get("is_syn_bomb", False):
      badges.append("<span class='badge-synergy badge-bomb'>💣 爆弾穴馬</span>")

    # 7. クッション値バイアスバッジ
    if c_status == "good":
      badges.append(
          f"<span class='badge-synergy badge-cushion-good'>{c_msg}</span>"
      )
    elif c_status == "risk":
      badges.append(
          f"<span class='badge-synergy badge-cushion-risk'>{c_msg}</span>"
      )

    badges_html = " ".join(badges)

    # 坂路調教フォーマット
    has_sakaro = pd.notnull(row.get("坂路_4F")) or pd.notnull(
        row.get("坂路_Lap1")
    )
    if has_sakaro:
      is_s_accel = bool(row.get("坂路_完全加速", False))
      s_accel_badge = (
          "<span class='badge-accel'>完全加速(A1〜A3)</span>"
          if is_s_accel
          else "<span class='badge-decel'>非加速</span>"
      )

      # ラスト2F加速秒数（Lap2 - Lap1）
      s_acc2 = row.get("坂路_ラスト2F加速")
      if pd.notnull(s_acc2):
        s_acc2_str = (
            f"<strong style='color:#38ef7d;'>+{s_acc2:.1f}s</strong>"
            if s_acc2 > 0
            else f"<span style='color:#8b949e;'>{s_acc2:.1f}s</span>"
        )
      else:
        s_acc2_str = "-s"

      # 調教馬間順位
      s_rank_badge = format_rank_badge(row.get("坂路_調教順位"))
      s_4f_rk = format_rank_badge(row.get("坂路_4F_rank"))
      s_l1_rk = format_rank_badge(row.get("坂路_Lap1_rank"))

      s_4f_val = (
          f"{row['坂路_4F']:.1f}s" if pd.notnull(row.get("坂路_4F")) else "-s"
      )
      s_l4_val = (
          f"{row['坂路_Lap4']:.1f}" if pd.notnull(row.get("坂路_Lap4")) else "-"
      )
      s_l3_val = (
          f"{row['坂路_Lap3']:.1f}" if pd.notnull(row.get("坂路_Lap3")) else "-"
      )
      s_l2_val = (
          f"{row['坂路_Lap2']:.1f}" if pd.notnull(row.get("坂路_Lap2")) else "-"
      )
      s_l1_val = (
          f"{row['坂路_Lap1']:.1f}" if pd.notnull(row.get("坂路_Lap1")) else "-"
      )

      sakaro_info = (
          f"坂路順位: {s_rank_badge} | 4F: <strong>{s_4f_val}</strong>"
          f" ({s_4f_rk}) | {s_accel_badge} | <strong>ラスト2F加速:"
          f" {s_acc2_str}</strong> [ {s_l4_val} - {s_l3_val} - {s_l2_val} -"
          f" <strong>{s_l1_val}s</strong> ({s_l1_rk}) ]"
      )
    else:
      sakaro_info = "坂路計測なし"

    # ウッド調教フォーマット
    has_wood = pd.notnull(row.get("wood_Lap1")) or pd.notnull(
        row.get("wood_5F")
    )
    if has_wood:
      place = str(row.get("wood_place", "")).strip()
      f5_str = (
          f"{row['wood_5F']:.1f}s" if pd.notnull(row.get("wood_5F")) else "-s"
      )

      w_acc2 = row.get("wood_ラスト2F加速")
      if pd.notnull(w_acc2):
        w_acc2_str = (
            f"<strong style='color:#38ef7d;'>+{w_acc2:.1f}s</strong>"
            if w_acc2 > 0
            else f"<span style='color:#8b949e;'>{w_acc2:.1f}s</span>"
        )
      else:
        w_acc2_str = "-s"

      w_rank_badge = format_rank_badge(row.get("wood_調教順位"))
      w_5f_rk = format_rank_badge(row.get("wood_5F_rank"))
      w_l1_rk = format_rank_badge(row.get("wood_Lap1_rank"))

      w_l4_val = (
          f"{row['wood_Lap4']:.1f}" if pd.notnull(row.get("wood_Lap4")) else "-"
      )
      w_l3_val = (
          f"{row['wood_Lap3']:.1f}" if pd.notnull(row.get("wood_Lap3")) else "-"
      )
      w_l2_val = (
          f"{row['wood_Lap2']:.1f}" if pd.notnull(row.get("wood_Lap2")) else "-"
      )
      w_l1_val = (
          f"{row['wood_Lap1']:.1f}" if pd.notnull(row.get("wood_Lap1")) else "-"
      )

      wood_info = (
          f"ウッド順位: {w_rank_badge} | {place} 5F: <strong>{f5_str}</strong>"
          f" ({w_5f_rk}) | <strong>ラスト2F加速: {w_acc2_str}</strong> [ {w_l4_val}"
          f" - {w_l3_val} - {w_l2_val} - <strong>{w_l1_val}s</strong> ({w_l1_rk})"
          " ]"
      )
    else:
      wood_info = "ウッド計測なし"

    u_no = row["馬番"]
    umaban_str = (
        f"{int(u_no)}番" if u_no != 99 and pd.notnull(u_no) else "番"
    )
    pop_str = (
        f"{int(row['人気'])} 番人気"
        if pd.notnull(row.get("人気"))
        else "- 番人気"
    )

    if pd.notnull(fup_val) and fup_val >= 5:
      fup_val_html = f"<span class='fup-high-val'>{int(fup_val)}点</span>"
    elif pd.notnull(fup_val):
      fup_val_html = f"<strong>{int(fup_val)}点</strong>"
    else:
      fup_val_html = "- 点"

    fup_rank_html = format_fup_rank_badge(fup_rank)
    f_badge = format_rank_badge(row.get("F_rank"))
    arms_badge = format_rank_badge(row.get("arms_rank"))
    tua_badge = format_rank_badge(row.get("tua_rank"))

    card_html = f"""
        <div class='horse-card'>
            <div class='horse-card-header'>
                <span class='horse-card-title'>{umaban_str} {row['馬名']}</span> {badges_html}
            </div>
            <ul class='horse-card-list'>
                <li><strong>陣営/血統</strong>: {row.get('調教師', '-')} / {row.get('騎手', '-')} / <strong>父: {row.get('種牡馬', '-')}</strong></li>
                <li><strong>坂路調教</strong>: {sakaro_info}</li>
                <li><strong>ウッド調教</strong>: {wood_info}</li>
                <li><strong>能力指数</strong>: F: <strong>{row.get('F指数', 0.0)}</strong> ({f_badge}) | ARMS: <strong>{row.get('arms', 0.0)}</strong> ({arms_badge}) | TUA: <strong>{row.get('tua', 0.0)}</strong> ({tua_badge})</li>
                <li><strong>Fup</strong>: {fup_val_html} ({fup_rank_html}) | <strong>人気</strong>: {pop_str}</li>
            </ul>
        </div>
        """
    st.markdown(card_html, unsafe_allow_html=True)
