import glob
import os
import numpy as np
import pandas as pd
import streamlit as st

# ==========================================
# ページ基本設定
# ==========================================
st.set_page_config(
    page_title="競馬予想10 クッション値Vr",
    page_icon="🏇",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🏇 競馬予想10 クッション値Vr【完全自動解析システム】")
st.caption(
    "F指数・Fup2・各種指数・坂路完全加速・実質負荷判定・クッション値×種牡馬データブック（70コース×60頭）・競馬イージーモード完全連動"
)


# ==========================================
# データロード（更新タイムスタンプ連動・キャッシュ事故完全防止）
# ==========================================
def get_file_mtime(path):
  return os.path.getmtime(path) if os.path.exists(path) else 0


@st.cache_data
def load_all_data(mtime_shisu, mtime_hanro, mtime_wood):
  """TARGET Frontier JV出力のShift-JIS(CP932)形式CSVを確実に読み込み、

  馬名・調教師・騎手・種牡馬の前後空白をクレンジングする
  """
  p_shisu = "data/出馬表_指数.csv"
  p_hanro = "data/出馬表_坂路.csv"
  p_wood = "data/出馬表_ウッド.csv"

  if not os.path.exists(p_shisu):
    p_shisu = "出馬表_指数.csv"
    p_hanro = "出馬表_坂路.csv"
    p_wood = "出馬表_ウッド.csv"

  # 1. 出馬表・指数CSV (全24項目厳格マッピング)
  df_s = pd.read_csv(p_shisu, encoding="cp932", header=None)
  col_names = [
      "場所R",
      "芝ダ",
      "距離",
      "馬番",
      "馬名",
      "所属",
      "調教師",
      "騎手",
      "人気順位",
      "印GTV",
      "Fup2数値",
      "Fup2順位",
      "S指数",
      "S指数順位",
      "F指数",
      "F指数順位",
      "ARMS2指数",
      "ARMS2順位",
      "TUA指数",
      "TUA順位",
      "結果着順",
      "種牡馬",
  ]
  while len(col_names) < df_s.shape[1]:
    col_names.append(f"col_{len(col_names)}")
  df_s.columns = col_names[: df_s.shape[1]]

  # 文字列クレンジング
  str_cols = ["場所R", "芝ダ", "馬名", "所属", "調教師", "騎手", "種牡馬", "印GTV"]
  for c in str_cols:
    if c in df_s.columns:
      df_s[c] = df_s[c].astype(str).str.strip().replace("nan", "")

  # 数値型クレンジング
  num_cols = [
      "距離",
      "馬番",
      "人気順位",
      "Fup2数値",
      "Fup2順位",
      "S指数",
      "S指数順位",
      "F指数",
      "F指数順位",
      "ARMS2指数",
      "ARMS2順位",
      "TUA指数",
      "TUA順位",
  ]
  for c in num_cols:
    if c in df_s.columns:
      df_s[c] = pd.to_numeric(df_s[c], errors="coerce").fillna(0)

  # 2. 坂路調教CSV（全13列仕様）
  # 列1:場所, 列2:年月日, 列4:馬番馬名, 列6:性齢, 列8:調教師, 列9:Time1(4F), 列10:Lap4, 列11:Lap3, 列12:Lap2, 列13:Lap1
  try:
    df_h = pd.read_csv(p_hanro, encoding="cp932")
    # ヘッダー名による柔軟対応
    if "馬名" not in df_h.columns:
      df_h = pd.read_csv(p_hanro, encoding="cp932", header=None)
      df_h = df_h.rename(
          columns={
              0: "場所",
              1: "年月日",
              3: "馬名",
              7: "調教師",
              8: "Time1",
              9: "Lap4",
              10: "Lap3",
              11: "Lap2",
              12: "Lap1",
          }
      )
  except Exception:
    df_h = pd.DataFrame(
        columns=["馬名", "Time1", "Lap4", "Lap3", "Lap2", "Lap1"]
    )

  df_h["馬名"] = df_h["馬名"].astype(str).str.strip()
  for c in ["Time1", "Lap4", "Lap3", "Lap2", "Lap1"]:
    if c in df_h.columns:
      df_h[c] = pd.to_numeric(df_h[c], errors="coerce")

  # 3. ウッド調教CSV（全24列仕様）
  # 列1:場所, 列2:年月日, 列8:調教師, 列14:5FTime, 列21:Lap4, 列22:Lap3, 列23:Lap2, 列24:Lap1
  try:
    df_w = pd.read_csv(p_wood, encoding="cp932")
    if "馬名" not in df_w.columns:
      df_w = pd.read_csv(p_wood, encoding="cp932", header=None)
      df_w = df_w.rename(
          columns={
              0: "場所",
              1: "年月日",
              3: "馬名",
              7: "調教師",
              13: "5FTime",
              20: "Lap4",
              21: "Lap3",
              22: "Lap2",
              23: "Lap1",
          }
      )
  except Exception:
    df_w = pd.DataFrame(columns=["馬名", "5FTime", "1F"])

  df_w["馬名"] = df_w["馬名"].astype(str).str.strip()

  return df_s, df_h, df_w


# パス取得とmtime連動
shisu_path = (
    "data/出馬表_指数.csv"
    if os.path.exists("data/出馬表_指数.csv")
    else "出馬表_指数.csv"
)
hanro_path = (
    "data/出馬表_坂路.csv"
    if os.path.exists("data/出馬表_坂路.csv")
    else "出馬表_坂路.csv"
)
wood_path = (
    "data/出馬表_ウッド.csv"
    if os.path.exists("data/出馬表_ウッド.csv")
    else "出馬表_ウッド.csv"
)

if not os.path.exists(shisu_path):
  st.error(
      "CSVファイルが見つかりません。`data/`フォルダ内にCSVを配置してください。"
  )
  st.stop()

mt_s = get_file_mtime(shisu_path)
mt_h = get_file_mtime(hanro_path)
mt_w = get_file_mtime(wood_path)

df_shisu, df_hanro, df_wood = load_all_data(mt_s, mt_h, mt_w)

# ==========================================
# サイドバー：レース選択・環境設定
# ==========================================
st.sidebar.header("⚙️ レース・馬場選択")
races_list = list(df_shisu["場所R"].unique())
selected_race = st.sidebar.selectbox("対象レースを選択", races_list)

df_race = df_shisu[df_shisu["場所R"] == selected_race].copy()
race_track = df_race["芝ダ"].iloc[0]
race_dist = int(df_race["距離"].iloc[0])
place_code = (
    selected_race[:1] if not selected_race[:2].isalpha() else selected_race[:2]
)

place_name_map = {
    "札": "札幌",
    "函": "函館",
    "福": "福島",
    "新": "新潟",
    "東": "東京",
    "中": "中山",
    "名": "中京",
    "京": "京都",
    "阪": "阪神",
    "小": "小倉",
}
course_place = place_name_map.get(place_code, "東京")


# クッション区分判定
def get_cv_band(place, val):
  if place in ["札幌", "札"]:
    return (
        "≤8.5低(場内低)"
        if val <= 7.3
        else ("≤8.5低(場内高)" if val >= 7.7 else "≤8.5低(場内中)")
    )
  if place in ["函館", "函"]:
    return (
        "≤8.5低(場内低)"
        if val <= 7.2
        else ("≤8.5低(場内高)" if val >= 7.5 else "≤8.5低(場内中)")
    )
  if val <= 8.5:
    return "≤8.5低"
  elif 8.6 <= val <= 9.4:
    return "8.6-9.4 やや低"
  elif 9.5 <= val <= 9.9:
    return "9.5-9.9 標準高"
  elif 10.0 <= val <= 10.4:
    return "10.0-10.4 高"
  else:
    return "≥10.5 超高"


st.sidebar.subheader("🌱 クッション値入力")
default_cv = (
    7.5
    if course_place in ["札幌", "函館"]
    else (10.0 if course_place == "京都" else 9.5)
)
cv_input = st.sidebar.number_input(
    f"{course_place} 芝クッション値",
    min_value=5.0,
    max_value=13.0,
    value=default_cv,
    step=0.1,
)
cv_band = get_cv_band(course_place, cv_input)
st.sidebar.info(f"現在の判定区分: **{cv_band}**")

if st.sidebar.button("🔄 データを強制再読込"):
  st.cache_data.clear()
  st.rerun()

# ==========================================
# データ統合＆調教・適性判定エンジン
# ==========================================
# 坂路最新追い切り
if "年月日" in df_hanro.columns:
  hanro_latest = (
      df_hanro.sort_values("年月日", ascending=False)
      .groupby("馬名")
      .first()
      .reset_index()
  )
else:
  hanro_latest = df_hanro.groupby("馬名").first().reset_index()

df_eval = pd.merge(df_race, hanro_latest, on="馬名", how="left", suffixes=("", "_坂路"))


# 調教完全加速・実質負荷判定
def judge_training(row):
  t1 = row.get("Time1", np.nan)
  l4 = row.get("Lap4", np.nan)
  l3 = row.get("Lap3", np.nan)
  l2 = row.get("Lap2", np.nan)
  l1 = row.get("Lap1", np.nan)

  # 実質負荷基準: 4F <= 56.0秒 かつ 終い1F <= 13.0秒
  if pd.notna(t1) and pd.notna(l1) and t1 <= 56.0 and l1 <= 13.0:
    if pd.notna(l4) and pd.notna(l3) and pd.notna(l2):
      if l4 > l3 > l2 > l1:
        if l1 <= 11.9:
          return "坂路完全加速(A3終い11秒台🔥)"
        elif l1 <= 12.4:
          return "坂路完全加速(A2究極ラップ🔥)"
        else:
          return "坂路完全加速(A1)"
      elif l2 > l1:
        return "坂路終い加速"
    return "坂路実質負荷(減速/平坦)"
  elif pd.notna(t1):
    return "坂路軽め/非負荷"
  return "コース追い/調教なし"


df_eval["調教判定"] = df_eval.apply(judge_training, axis=1)


# クッション値×種牡馬データブック（70コース×60種牡馬編）照合
def judge_sire_book(row):
  if race_track != "芝":
    return "ダート戦（対象外）"
  sire = str(row.get("種牡馬", "")).strip()

  # 1. 最重要・狙い目 上位20組み合わせ（完全照合）
  if (
      course_place == "阪神"
      and race_dist == 1800
      and "キズナ" in sire
      and "9.5-9.9" in cv_band
  ):
    return "最重要(阪神1800外×9.5-9.9/勝19.6%/単421/複172)"
  if (
      course_place == "東京"
      and race_dist == 1600
      and "エピファネイア" in sire
      and "9.5-9.9" in cv_band
  ):
    return "最重要(東京1600×9.5-9.9/勝13.3%/単277/複111)"
  if (
      course_place == "東京"
      and race_dist == 1400
      and "モーリス" in sire
      and "9.5-9.9" in cv_band
  ):
    return "最重要(東京1400×9.5-9.9/勝10.1%/単408/複160)"
  if (
      course_place == "東京"
      and race_dist == 1800
      and "ディープインパクト" in sire
      and "9.5-9.9" in cv_band
  ):
    return "最重要(東京1800×9.5-9.9/勝15.8%/単228/複156)"
  if (
      course_place == "東京"
      and race_dist == 2000
      and "キズナ" in sire
      and "8.6-9.4" in cv_band
  ):
    return "最重要(東京2000×8.6-9.4/勝19.7%/単200/複121)"
  if (
      course_place == "中京"
      and race_dist == 2000
      and "ディープインパクト" in sire
      and "8.6-9.4" in cv_band
  ):
    return "最重要(中京2000×8.6-9.4/勝18.0%/単178/複92)"
  if (
      course_place == "東京"
      and race_dist == 1600
      and "イスラボニータ" in sire
      and "8.6-9.4" in cv_band
  ):
    return "最重要(東京1600×8.6-9.4/勝10.5%/単350/複120)"
  if (
      course_place == "東京"
      and race_dist == 2000
      and "エピファネイア" in sire
      and "8.6-9.4" in cv_band
  ):
    return "最重要(東京2000×8.6-9.4/勝15.3%/単149/複84)"
  if course_place == "函館" and race_dist == 1800 and "キズナ" in sire:
    return "最重要(函館1800×低/勝17.7%/単143/複93)"
  if (
      course_place == "小倉"
      and race_dist == 1200
      and "ダイワメジャー" in sire
      and "9.5-9.9" in cv_band
  ):
    return "最重要(小倉1200×9.5-9.9/勝13.6%/単173/複111)"
  if course_place == "札幌" and race_dist == 2000 and "オルフェーヴル" in sire:
    return "最重要(札幌2000×低/勝15.8%/単136/複145)"
  if (
      course_place == "東京"
      and race_dist == 1400
      and "ロードカナロア" in sire
      and "8.6-9.4" in cv_band
  ):
    return "最重要(東京1400×8.6-9.4/勝15.6%/単123/複100)"
  if (
      course_place == "阪神"
      and race_dist == 1600
      and "ルーラーシップ" in sire
      and "8.6-9.4" in cv_band
  ):
    return "最重要(阪神1600外×8.6-9.4/勝20.0%/単156/複89)"
  if (
      course_place == "東京"
      and race_dist == 1600
      and "モーリス" in sire
      and "9.5-9.9" in cv_band
  ):
    return "最重要(東京1600×9.5-9.9/勝11.1%/単100/複122)"
  if (
      course_place == "阪神"
      and race_dist == 2000
      and "キズナ" in sire
      and "8.6-9.4" in cv_band
  ):
    return "最重要(阪神2000内×8.6-9.4/勝11.8%/単152/複107)"
  if (
      course_place == "東京"
      and race_dist == 1600
      and "スクリーンヒーロー" in sire
      and "8.6-9.4" in cv_band
  ):
    return "最重要(東京1600×8.6-9.4/勝9.9%/単72/複179)"
  if (
      course_place == "小倉"
      and race_dist == 1200
      and "ビッグアーサー" in sire
      and "8.6-9.4" in cv_band
  ):
    return "最重要(小倉1200×8.6-9.4/勝12.2%/単131/複101)"
  if (
      course_place == "中京"
      and race_dist == 1600
      and "ロードカナロア" in sire
      and "10.0-10.4" in cv_band
  ):
    return "最重要(中京1600×10.0-10.4/勝14.8%/単133/複79)"
  if (
      course_place == "福島"
      and race_dist == 1200
      and "ビッグアーサー" in sire
      and "8.6-9.4" in cv_band
  ):
    return "最重要(福島1200×8.6-9.4/勝13.2%/単87/複102)"
  if course_place == "札幌" and race_dist == 1200 and "ロードカナロア" in sire:
    return "最重要(札幌1200×低/勝15.0%/単121/複71)"

  # 2. 危険・消し 上位20組み合わせ（完全消込照合）
  if (
      course_place == "中山"
      and race_dist == 2000
      and "ダノンバラード" in sire
      and "9.5-9.9" in cv_band
  ):
    return "危険(中山2000×9.5-9.9/複率0.0%/単0/複0)"
  if (
      course_place == "東京"
      and race_dist == 2000
      and "ルーラーシップ" in sire
      and "9.5-9.9" in cv_band
  ):
    return "危険(東京2000×9.5-9.9/複率9.1%/単0/複15)"
  if (
      course_place == "小倉"
      and race_dist == 1200
      and "ジャスタウェイ" in sire
      and "8.6-9.4" in cv_band
  ):
    return "危険(小倉1200×8.6-9.4/複率2.9%/単0/複29)"
  if (
      course_place == "東京"
      and race_dist == 1400
      and "シルバーステート" in sire
      and "8.6-9.4" in cv_band
  ):
    return "危険(東京1400×8.6-9.4/複率4.7%/単0/複50)"
  if (
      course_place == "東京"
      and race_dist == 1600
      and "ゴールドシップ" in sire
      and "8.6-9.4" in cv_band
  ):
    return "危険(東京1600×8.6-9.4/複率4.5%/単20/複9)"
  if (
      course_place == "小倉"
      and race_dist == 1200
      and "ヴィクトワールピサ" in sire
      and "8.6-9.4" in cv_band
  ):
    return "危険(小倉1200×8.6-9.4/複率4.8%/単17/複10)"
  if (
      course_place == "東京"
      and race_dist == 1800
      and "ルーラーシップ" in sire
      and "9.5-9.9" in cv_band
  ):
    return "危険(東京1800×9.5-9.9/複率10.5%/単0/複51)"
  if (
      course_place == "阪神"
      and race_dist == 2000
      and "ゴールドシップ" in sire
      and "8.6-9.4" in cv_band
  ):
    return "危険(阪神2000内×8.6-9.4/複率10.0%/単45/複19)"
  if (
      course_place == "東京"
      and race_dist == 1600
      and "エイシンフラッシュ" in sire
      and "8.6-9.4" in cv_band
  ):
    return "危険(東京1600×8.6-9.4/複率7.3%/単9/複13)"
  if (
      course_place == "東京"
      and race_dist == 2000
      and "オルフェーヴル" in sire
      and "8.6-9.4" in cv_band
  ):
    return "危険(東京2000×8.6-9.4/複率13.2%/単0/複33)"
  if (
      course_place == "福島"
      and race_dist == 2000
      and "ルーラーシップ" in sire
      and "8.6-9.4" in cv_band
  ):
    return "危険(福島2000×8.6-9.4/複率4.7%/単38/複12)"
  if (
      course_place == "新潟"
      and race_dist == 1400
      and "リオンディーズ" in sire
      and "8.6-9.4" in cv_band
  ):
    return "危険(新潟1400内×8.6-9.4/複率6.7%/単0/複15)"
  if (
      course_place == "東京"
      and race_dist == 2400
      and "ゴールドシップ" in sire
      and "9.5-9.9" in cv_band
  ):
    return "危険(東京2400×9.5-9.9/複率11.1%/単0/複40)"
  if (
      course_place == "小倉"
      and race_dist == 1800
      and "ルーラーシップ" in sire
      and "9.5-9.9" in cv_band
  ):
    return "危険(小倉1800×9.5-9.9/複率10.0%/単10/複16)"
  if (
      course_place == "阪神"
      and race_dist == 1800
      and "ハービンジャー" in sire
      and "9.5-9.9" in cv_band
  ):
    return "危険(阪神1800外×9.5-9.9/複率10.0%/単9/複17)"
  if (
      course_place == "東京"
      and race_dist == 1600
      and "サトノクラウン" in sire
      and "8.6-9.4" in cv_band
  ):
    return "危険(東京1600×8.6-9.4/複率9.7%/単0/複17)"
  if (
      course_place == "福島"
      and race_dist == 1200
      and "マツリダゴッホ" in sire
      and "8.6-9.4" in cv_band
  ):
    return "危険(福島1200×8.6-9.4/複率5.9%/単32/複18)"
  if (
      course_place == "東京"
      and race_dist == 1600
      and "シルバーステート" in sire
      and "9.5-9.9" in cv_band
  ):
    return "危険(東京1600×9.5-9.9/複率8.9%/単4/複28)"
  if (
      course_place == "福島"
      and race_dist == 1200
      and "カレンブラックヒル" in sire
      and "8.6-9.4" in cv_band
  ):
    return "危険(福島1200×8.6-9.4/複率9.7%/単0/複31)"
  if (
      course_place == "中京"
      and race_dist == 2000
      and "オルフェーヴル" in sire
      and "8.6-9.4" in cv_band
  ):
    return "危険(中京2000×8.6-9.4/複率15.2%/単0/複54)"

  # 3. 超高帯（>=10.5）独立ルール
  if "≥10.5" in cv_band:
    if any(
        s in sire
        for s in [
            "エピファネイア",
            "キタサンブラック",
            "イスラボニータ",
            "ロードカナロア",
        ]
    ):
      return "特注(超高帯適性血統🔥)"
    if any(
        s in sire
        for s in [
            "キングカメハメハ",
            "ビッグアーサー",
            "レイデオロ",
            "スワーヴリチャード",
            "サートゥルナーリア",
            "ゴールドシップ",
        ]
    ):
      return "危険(超高帯割引血統⚠️)"

  return "中立/平均"


df_eval["血統CV適性"] = df_eval.apply(judge_sire_book, axis=1)


# SSS級・四冠・イージーモード判定
def evaluate_horse(row):
  f_val = row.get("F指数", 0)
  f_rnk = row.get("F指数順位", 99)
  fup_val = row.get("Fup2数値", 0)
  arms_val = row.get("ARMS2指数", 0)
  arms_rnk = row.get("ARMS2順位", 99)
  tua_val = row.get("TUA指数", 0)
  tua_rnk = row.get("TUA順位", 99)
  tr_str = row.get("調教判定", "")
  cv_str = row.get("血統CV適性", "")
  ninki = row.get("人気順位", 99)
  gtv = str(row.get("印GTV", "")).strip()
  tm = str(row.get("調教師", ""))
  jk = str(row.get("騎手", ""))

  score = 0
  tags = []

  # SSS級・絶対神域
  if f_val >= 70 and arms_val >= 120 and tua_val >= 200:
    tags.append("👑SSS級絶対神域")
    score += 55

  # 指数の四冠馬
  if f_rnk == 1 and row.get("Fup2順位", 99) == 1 and arms_rnk == 1 and tua_rnk == 1:
    tags.append("🏆指数の四冠馬(単回418%)")
    score += 45

  # 究極連系
  if f_rnk == 1 and arms_rnk <= 3 and tua_rnk <= 3:
    tags.append("🎯究極連系(F1位+ARMS3位内+TUA3位内)")
    score += 30

  # Fup2 評価
  if fup_val == 7:
    tags.append("🔥Fup2確変(7点)")
    score += 30
  elif fup_val in [4, 5, 6]:
    tags.append(f"優位(Fup2:{int(fup_val)}点)")
    score += 15
  elif fup_val == 1 and ninki <= 3:
    if f_val < 72 and "👑SSS級絶対神域" not in tags:
      tags.append("⚠️ダミーの罠(Fup2:1点消去)")
      score -= 35

  # 谷の形
  if ninki <= 3 and f_rnk >= 8:
    tags.append("⚠️谷の形(過剰人気消去)")
    score -= 30

  # 調教評価
  if "A3" in tr_str or "A2" in tr_str:
    score += 25
    if f_rnk == 1:
      tags.append("🔥SSS級究極ラップ(F1位×坂路完全加速)")
      score += 25
  elif "完全加速" in tr_str:
    score += 15
  elif "坂路実質負荷(減速/平坦)" in tr_str and ninki <= 3:
    tags.append("⚠️坂路減速(実質負荷不足)")
    score -= 15

  # クッション値×種牡馬
  if "最重要" in cv_str:
    score += 35
    tags.append("🌟CV最重要適性")
  elif "特注" in cv_str:
    score += 20
    tags.append("✨CV特注血統")
  elif "危険" in cv_str:
    score -= 40
    tags.append("⚠️CV危険血統該当")

  # 陣営・黄金コンビ
  if "木村哲也" in tm and "ルメール" in jk:
    if fup_val >= 5:
      tags.append("✨キムテツ×ルメール勝負(Fup5+)")
      score += 20
    elif fup_val <= 4:
      tags.append("⚠️キムテツ×ルメール割引(Fup4以下)")
      score -= 20
  if "中内田" in tm and "川田" in jk and f_rnk == 1:
    tags.append("✨中内田×川田×F1位(鉄板軸)")
    score += 25
  if ("斉藤崇史" in tm or "中舘英二" in tm) and f_rnk == 1:
    tags.append("✨特注厩舎×F1位")
    score += 20

  # ダート短距離×坂路加速
  if race_track == "ダ" and race_dist <= 1400:
    if "完全加速" in tr_str and tua_rnk <= 3:
      tags.append("🔥ダ短距離特注(TUA上位×坂路加速)")
      score += 25

  # イージーモード単勝狙い
  if race_track == "ダ" and gtv != "" and gtv != "0":
    tags.append("🎯イージーモードGTV該当")
    score += 15

  return pd.Series([score, " / ".join(tags)])


df_eval[["総合スコア", "判定タグ"]] = df_eval.apply(evaluate_horse, axis=1)
df_eval = df_eval.sort_values(
    ["総合スコア", "F指数"], ascending=[False, False]
).reset_index(drop=True)

# 悪条件頭数（イージーモード歪みカウント）
bad_count = sum(
    df_eval["判定タグ"].str.contains(
        "ダミー|谷の形|CV危険|坂路減速|キムテツ×ルメール割引"
    )
)
is_distorted = 7 <= bad_count <= 12

# ==========================================
# 画面出力部（matplotlib非依存・高視認性）
# ==========================================
st.markdown(f"## 🏁 【{selected_race}】 {race_track}{race_dist}m 出馬解析")

# サマリーメトリクス
m1, m2, m3, m4 = st.columns(4)
m1.metric(
    "レース波乱度",
    "ボーナスレース"
    if (df_eval["F指数順位"].iloc[0] == 1 and df_eval["総合スコア"].iloc[0] >= 65)
    else ("混戦・波乱歪み🔥" if is_distorted else "堅調構成"),
)
m2.metric(
    "イージーモード歪み",
    f"{'歪みレース成立🔥' if is_distorted else '標準構成'} ({bad_count}頭該当)",
)
m3.metric("本日の芝CV値", f"{cv_input} ({cv_band})")
m4.metric(
    "連軸筆頭(◎)",
    f"{int(df_eval['馬番'].iloc[0])}番 {df_eval['馬名'].iloc[0]}",
)

st.markdown("---")

# 出馬表一覧テーブル（ImportErrorを完全回避するStreamlitネイティブ描画）
st.subheader("📋 【全出走馬 能力マトリクス・調教・適性一覧】")
disp_cols = [
    "馬番",
    "馬名",
    "人気順位",
    "Fup2数値",
    "F指数",
    "F指数順位",
    "ARMS2指数",
    "ARMS2順位",
    "TUA指数",
    "TUA順位",
    "調教判定",
    "血統CV適性",
    "判定タグ",
    "総合スコア",
]

# 数値カラムのフォーマット設定
st.dataframe(
    df_eval[disp_cols],
    column_config={
        "馬番": st.column_config.NumberColumn("馬番", format="%d"),
        "人気順位": st.column_config.NumberColumn("人気", format="%d位"),
        "Fup2数値": st.column_config.NumberColumn("Fup2", format="%d点"),
        "F指数": st.column_config.NumberColumn("F指数", format="%d"),
        "F指数順位": st.column_config.NumberColumn("F順", format="%d位"),
        "ARMS2指数": st.column_config.NumberColumn("ARMS", format="%d"),
        "ARMS2順位": st.column_config.NumberColumn("ARMS順", format="%d位"),
        "TUA指数": st.column_config.NumberColumn("TUA", format="%d"),
        "TUA順位": st.column_config.NumberColumn("TUA順", format="%d位"),
        "総合スコア": st.column_config.ProgressColumn(
            "総合評価",
            help="各種指数・調教・血統適性の合算値",
            format="%d",
            min_value=-50,
            max_value=120,
        ),
    },
    use_container_width=True,
    hide_index=True,
)

# 厳選ピックアップ・買い目
col_l, col_r = st.columns(2)

with col_l:
  st.subheader("🎯 推奨馬ピックアップ")
  top_horse = df_eval.iloc[0]
  st.success(
      f"**◎ 連軸筆頭**: **{int(top_horse['馬番'])}番 {top_horse['馬名']}** "
      f"（総合スコア: {top_horse['総合スコア']}点）\n\n"
      f"- **能力マトリクス**: F指数 {top_horse['F指数']} (順位:{int(top_horse['F指数順位'])}位) / Fup2: {int(top_horse['Fup2数値'])}点 / ARMS2: {int(top_horse['ARMS2指数'])} / TUA: {int(top_horse['TUA指数'])}\n"
      f"- **調教事実**: {top_horse['調教判定']}\n"
      f"- **血統CV適性**: {top_horse['血統CV適性']}\n"
      f"- **選定根拠**: {top_horse['判定タグ']}"
  )

  # 🔥 特大推奨穴馬（人気薄×高評価）
  ana_horses = df_eval[
      (df_eval["人気順位"] >= 5) & (df_eval["総合スコア"] >= 15)
  ]
  if not ana_horses.empty:
    ana_h = ana_horses.iloc[0]
    st.warning(
        f"**🔥 特大推奨ヒモ穴**: **{int(ana_h['馬番'])}番 {ana_h['馬名']}** "
        f"({int(ana_h['人気順位'])}番人気)\n\n"
        f"- **調教/適性**: {ana_h['調教判定']} | {ana_h['血統CV適性']}\n"
        f"- **激走根拠**: {ana_h['判定タグ']}"
    )

  # ⚠️ 危険な人気馬・ダミー消し馬
  keshi_horses = df_eval[
      df_eval["判定タグ"].str.contains("ダミー|谷の形|危険|割引")
  ]
  if not keshi_horses.empty:
    keshi_list = [
        f"・**{int(r['馬番'])}番 {r['馬名']}** : {r['判定タグ']}"
        for _, r in keshi_horses.iterrows()
    ]
    st.error("**⚠️ ダミー看破・危険な消し馬**:\n" + "\n".join(keshi_list))

with col_r:
  st.subheader("🎫 競馬予想10 実戦買い目フォーメーション")
  top_id = int(df_eval["馬番"].iloc[0])
  sub_ids = [int(x) for x in df_eval["馬番"].iloc[1:4].tolist()]
  himo_ids = [int(x) for x in df_eval["馬番"].iloc[4:8].tolist()]

  st.markdown(f"""
    **【本線：単勝・複勝】**
    * 単勝: **{top_id}**（本命連軸・重点配分）
    * 複勝 / ワイド: **{sub_ids[0] if sub_ids else top_id}**
    
    **【本線：3連複フォーメーション（回収率特化）】**
    * **1列目 (軸)**: `{top_id}`
    * **2列目 (相手)**: `{sub_ids}`
    * **3列目 (ヒモ)**: `{sub_ids + himo_ids}`
    
    **【高配当狙い：3連単 2・3着連軸マルチ（裏表標準化）】**
    * **1着**: `{top_id}`, `{sub_ids[0] if sub_ids else top_id}`
    * **2着**: `{top_id}`, `{sub_ids}`
    * **3着**: `{top_id}`, `{sub_ids + himo_ids}`
    
    **【抑え・資金回収：ワイド（1〜2点）】**
    * `{top_id}` － `{sub_ids[0] if sub_ids else ''}`
    * `{top_id}` － `{sub_ids[1] if len(sub_ids) > 1 else ''}`
    """)

st.markdown("---")
st.caption(
    "💡 自動更新仕様: TARGETから出力したCSV（Shift-JIS）をGitHubの `data/`"
    " にプッシュするだけで、ファイル更新日時の変更を自動検知して即座に画面へ反映されます。"
)
