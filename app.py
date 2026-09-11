import os
import glob
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
    "F指数・Fup2・各種指数・坂路完全加速・当日のクッション値×種牡馬バイアス・イージーモード（歪み判定）完全連動"
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
    # ルート直下にある場合のフォールバック
    p_shisu = "出馬表_指数.csv"
    p_hanro = "出馬表_坂路.csv"
    p_wood = "出馬表_ウッド.csv"

  # 1. 指数CSV (全24項目マッピング)
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
  # 予備列対応
  while len(col_names) < df_s.shape[1]:
    col_names.append(f"col_{len(col_names)}")
  df_s.columns = col_names[: df_s.shape[1]]

  # クレンジング
  str_cols = ["場所R", "芝ダ", "馬名", "所属", "調教師", "騎手", "種牡馬"]
  for c in str_cols:
    if c in df_s.columns:
      df_s[c] = df_s[c].astype(str).str.strip()

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

  # 2. 坂路調教CSV
  df_h = pd.read_csv(p_hanro, encoding="cp932")
  df_h["馬名"] = df_h["馬名"].astype(str).str.strip()
  for c in ["Time1", "Time2", "Time3", "Time4", "Lap4", "Lap3", "Lap2", "Lap1"]:
    if c in df_h.columns:
      df_h[c] = pd.to_numeric(df_h[c], errors="coerce")

  # 3. ウッド調教CSV
  df_w = pd.read_csv(p_wood, encoding="cp932")
  df_w["馬名"] = df_w["馬名"].astype(str).str.strip()
  for c in [
      "6F",
      "5F",
      "4F",
      "3F",
      "2F",
      "1F",
      "Lap6",
      "Lap5",
      "Lap4",
      "Lap3",
      "Lap2",
      "Lap1",
  ]:
    if c in df_w.columns:
      df_w[c] = pd.to_numeric(df_w[c], errors="coerce")

  return df_s, df_h, df_w


# ファイル更新日時の取得（ファイル差し替えで即時検知）
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
# クッション値データブック マスター辞書 (PDF準拠)
# ==========================================
SIRE_CV_MASTER = {
    # 形式: (コース名, クッション区分): {"type": "最重要"|"狙い目"|"回収妙味"|"危険", "sire": [...], "desc": "..."}
    "超高帯_特注種牡馬": [
        "エピファネイア",
        "キタサンブラック",
        "イスラボニータ",
        "ロードカナロア",
    ],
    "超高帯_危険種牡馬": [
        "キングカメハメハ",
        "ビッグアーサー",
        "レイデオロ",
        "スワーヴリチャード",
        "サートゥルナーリア",
        "ゴールドシップ",
    ],
}


def get_cv_band(place, cv_val):
  """全国5区分および札幌・函館の場内相対区分判定"""
  if place in ["札幌", "札"]:
    if cv_val <= 7.3:
      return "≤8.5低(場内低)"
    elif cv_val >= 7.7:
      return "≤8.5低(場内高)"
    else:
      return "≤8.5低(場内中)"
  elif place in ["函館", "函"]:
    if cv_val <= 7.2:
      return "≤8.5低(場内低)"
    elif cv_val >= 7.5:
      return "≤8.5低(場内高)"
    else:
      return "≤8.5低(場内中)"
  else:
    if cv_val <= 8.5:
      return "≤8.5低"
    elif 8.6 <= cv_val <= 9.4:
      return "8.6-9.4 やや低"
    elif 9.5 <= cv_val <= 9.9:
      return "9.5-9.9 標準高"
    elif 10.0 <= cv_val <= 10.4:
      return "10.0-10.4 高"
    else:
      return "≥10.5 超高"


# ==========================================
# サイドバー：レース選択・環境設定
# ==========================================
st.sidebar.header("⚙️ 設定パネル")
races_list = list(df_shisu["場所R"].unique())
selected_race = st.sidebar.selectbox("対象レースを選択", races_list)

# 選択レースの基本情報
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

# クッション値入力
st.sidebar.subheader("🌱 馬場・クッション値設定")
cv_default = (
    7.5
    if course_place in ["札幌", "函館"]
    else (10.0 if course_place == "京都" else 9.5)
)
cv_input = st.sidebar.number_input(
    f"{course_place} 芝クッション値",
    min_value=5.0,
    max_value=13.0,
    value=cv_default,
    step=0.1,
)
cv_band = get_cv_band(course_place, cv_input)
st.sidebar.info(f"判定区分: **{cv_band}**")

# 強制リロードボタン
if st.sidebar.button("🔄 データを強制再読込"):
  st.cache_data.clear()
  st.rerun()

# ==========================================
# 解析エンジンの実行
# ==========================================
# 坂路・ウッドの最新追い切りとマージ
hanro_latest = (
    df_hanro.sort_values("年月日", ascending=False)
    .groupby("馬名")
    .first()
    .reset_index()
)
wood_latest = (
    df_wood.sort_values("年月日", ascending=False)
    .groupby("馬名")
    .first()
    .reset_index()
)

df_eval = pd.merge(df_race, hanro_latest, on="馬名", how="left", suffixes=("", "_坂路"))
df_eval = pd.merge(
    df_eval, wood_latest, on="馬名", how="left", suffixes=("", "_ウッド")
)


# 調教完全加速・実質負荷判定
def judge_training(row):
  t1 = row.get("Time1", np.nan)
  l4 = row.get("Lap4", np.nan)
  l3 = row.get("Lap3", np.nan)
  l2 = row.get("Lap2", np.nan)
  l1 = row.get("Lap1", np.nan)

  # 実質負荷基準: 4F <= 56.0 かつ 1F <= 13.0
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
  return "坂路調教なし/コース追い"


df_eval["調教判定"] = df_eval.apply(judge_training, axis=1)


# クッション値×種牡馬判定ロジック
def judge_sire_cv(row):
  sire = str(row.get("種牡馬", "")).strip()
  if race_track != "芝":
    return "ダート（対象外）"

  # PDF『クッション値データブック』特注ルールの直結照合
  if course_place == "札幌" and race_dist == 2000 and "オルフェーヴル" in sire:
    return "最重要(オルフェーヴル×札幌2000/勝15.8%/単136/複145)"
  if course_place == "小倉" and race_dist == 1200 and "ビッグアーサー" in sire:
    return "最重要(ビッグアーサー×小倉1200/勝12.2%/複30.9%)"
  if course_place == "福島" and race_dist == 1200 and "ビッグアーサー" in sire:
    return "最重要(ビッグアーサー×福島1200/勝13.2%/複33.1%)"
  if course_place == "東京" and race_dist == 1600 and "エピファネイア" in sire:
    return "最重要(エピファネイア×東京1600/勝13.3%/複39.8%)"
  if course_place == "東京" and race_dist == 1400 and "モーリス" in sire:
    return "最重要(モーリス×東京1400/勝10.1%/複29.0%)"
  if course_place == "阪神" and race_dist == 1800 and "キズナ" in sire:
    return "最重要(キズナ×阪神1800/勝19.6%/複41.1%/単421)"
  if (
      course_place == "中山"
      and race_dist == 1600
      and "シルバーステート" in sire
      and "9.5-9.9" in cv_band
  ):
    return "最重要(シルバーステート×中山1600/勝17.1%/複43.9%/単225)"
  if (
      course_place == "京都"
      and race_dist == 2000
      and "キタサンブラック" in sire
      and "超高" in cv_band
  ):
    return "最重要(キタサンブラック×京都2000超高/勝21.1%/複50.0%)"

  # 危険種牡馬の消込
  if (
      course_place == "中山"
      and race_dist == 2000
      and "ダノンバラード" in sire
      and "9.5-9.9" in cv_band
  ):
    return "危険(ダノンバラード×中山2000標準高/複率0.0%)"
  if (
      course_place == "東京"
      and race_dist == 2000
      and "ルーラーシップ" in sire
      and "9.5-9.9" in cv_band
  ):
    return "危険(ルーラーシップ×東京2000標準高/複率9.1%)"
  if (
      course_place == "小倉"
      and race_dist == 1200
      and "ジャスタウェイ" in sire
      and "8.6-9.4" in cv_band
  ):
    return "危険(ジャスタウェイ×小倉1200やや低/複率2.9%)"
  if (
      course_place == "東京"
      and race_dist == 1400
      and "シルバーステート" in sire
      and "8.6-9.4" in cv_band
  ):
    return "危険(シルバーステート×東京1400やや低/複率4.7%)"
  if (
      course_place == "東京"
      and race_dist == 1600
      and "ゴールドシップ" in sire
      and "8.6-9.4" in cv_band
  ):
    return "危険(ゴールドシップ×東京1600やや低/複率4.5%)"

  # 一般帯判定
  if "超高" in cv_band:
    if any(s in sire for s in SIRE_CV_MASTER["超高帯_特注種牡馬"]):
      return "特注(超高クッション適性血統)"
    if any(s in sire for s in SIRE_CV_MASTER["超高帯_危険種牡馬"]):
      return "危険(超高クッション割引血統)"

  return "中立/平均"


df_eval["血統CV適性"] = df_eval.apply(judge_sire_cv, axis=1)


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
  tm = str(row.get("調教師", ""))
  jk = str(row.get("騎手", ""))

  score = 0
  tags = []

  # SSS級・絶対神域
  if f_val >= 70 and arms_val >= 120 and tua_val >= 200:
    tags.append("👑SSS級絶対神域")
    score += 50

  # Fup2 評価
  if fup_val == 7:
    tags.append("🔥Fup2確変(7点)")
    score += 25
  elif fup_val in [4, 5, 6]:
    tags.append(f"優位(Fup2:{int(fup_val)}点)")
    score += 15
  elif fup_val == 1 and ninki <= 3:
    if f_val < 72:
      tags.append("⚠️ダミーの罠(Fup2:1点消去)")
      score -= 30

  # 究極連系
  if f_rnk == 1 and arms_rnk <= 3 and tua_rnk <= 3:
    tags.append("🎯究極連系(F1位+ARMS3位内+TUA3位内)")
    score += 30

  # 調教加点
  if "A3" in tr_str or "A2" in tr_str:
    score += 20
    if f_rnk == 1:
      tags.append("🔥究極ラップ(F1位×坂路完全加速)")
      score += 25
  elif "完全加速" in tr_str:
    score += 10

  # 陣営コンビ特注
  if "木村哲也" in tm and "ルメール" in jk:
    if fup_val >= 5:
      tags.append("✨キムテツ×ルメール勝負(Fup5+)")
      score += 20
    elif fup_val <= 4:
      tags.append("⚠️キムテツ×ルメール危険(Fup4以下)")
      score -= 20
  if "中内田" in tm and "川田" in jk and f_rnk == 1:
    tags.append("✨中内田×川田×F1位(鉄板軸)")
    score += 25
  if ("斉藤崇史" in tm or "中舘" in tm) and f_rnk == 1:
    tags.append("✨特注厩舎×F1位")
    score += 20

  # クッション値加減点
  if "最重要" in cv_str:
    score += 30
    tags.append("🌟CV最重要適性")
  elif "危険" in cv_str:
    score -= 35
    tags.append("⚠️CV危険コース該当")

  # 谷の形
  if ninki <= 3 and f_rnk >= 8:
    tags.append("⚠️谷の形(過剰人気)")
    score -= 25

  return pd.Series([score, " / ".join(tags)])


df_eval[["総合スコア", "判定タグ"]] = df_eval.apply(evaluate_horse, axis=1)
df_eval = df_eval.sort_values(
    ["総合スコア", "F指数"], ascending=[False, False]
).reset_index(drop=True)

# 悪条件頭数（イージーモード歪み判定）
bad_count = 0
for idx, r in df_eval.iterrows():
  # ダミー消し・谷の形・CV危険・減速等
  if any(
      x in r["判定タグ"]
      for x in ["ダミー", "危険", "谷の形", "坂路実質負荷(減速/平坦)"]
  ):
    bad_count += 1

is_distorted = 7 <= bad_count <= 14

# ==========================================
# 画面出力部
# ==========================================
st.markdown(f"## 🏁 【{selected_race}】 {race_track}{race_dist}m 出馬解析")

# 概要メトリクス
m1, m2, m3, m4 = st.columns(4)
m1.metric(
    "レース波乱度",
    "ボーナスレース"
    if (df_eval["F指数順位"].iloc[0] == 1 and df_eval["総合スコア"].iloc[0] >= 60)
    else ("混戦・歪み波乱" if is_distorted else "堅調"),
)
m2.metric(
    "イージーモード歪み",
    f"{'歪みレースあり🔥' if is_distorted else '標準構成'} ({bad_count}頭該当)",
)
m3.metric("本日の芝CV値", f"{cv_input} ({cv_band})")
m4.metric(
    "連軸筆頭(◎)",
    f"{int(df_eval['馬番'].iloc[0])}番 {df_eval['馬名'].iloc[0]}",
)

st.markdown("---")

# 出馬表一覧テーブル
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
st.dataframe(
    df_eval[disp_cols].style.background_gradient(
        subset=["総合スコア", "F指数"], cmap="Blues"
    ),
    use_container_width=True,
    hide_index=True,
)

# 厳選ピックアップ
col_l, col_r = st.columns(2)

with col_l:
  st.subheader("🎯 推奨馬ピックアップ")
  top_horse = df_eval.iloc[0]
  st.success(
      f"**◎ 連軸筆頭**: **{int(top_horse['馬番'])}番 {top_horse['馬名']}**\n\n"
      f"- **選定理由**: F指数 {top_horse['F指数']} (順位:{int(top_horse['F指数順位'])}位) / Fup2: {int(top_horse['Fup2数値'])}点 / ARMS2:{int(top_horse['ARMS2指数'])} / TUA:{int(top_horse['TUA指数'])}\n"
      f"- **調教**: {top_horse['調教判定']}\n"
      f"- **血統CV**: {top_horse['血統CV適性']}\n"
      f"- **評価根拠**: {top_horse['判定タグ']}"
  )

  # ヒモ穴（人気薄×完全加速または高Fup）
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

  # ダミー消し馬
  keshi_horses = df_eval[df_eval["判定タグ"].str.contains("ダミー|谷の形|危険")]
  if not keshi_horses.empty:
    keshi_names = [
        f"{int(r['馬番'])}番 {r['馬名']} ({r['判定タグ']})"
        for _, r in keshi_horses.iterrows()
    ]
    st.error("**⚠️ ダミー看破・危険な消し馬**:\n" + "\n".join(keshi_names))

with col_r:
  st.subheader("🎫 競馬予想10 実戦買い目（新フォーミュラ）")
  top_id = int(df_eval["馬番"].iloc[0])
  sub_ids = [int(x) for x in df_eval["馬番"].iloc[1:4].tolist()]
  himo_ids = [int(x) for x in df_eval["馬番"].iloc[4:8].tolist()]

  st.markdown(f"""
    **【本線：単勝・複勝】**
    * 単勝: **{top_id}** (重点配分)
    * 複勝: **{sub_ids[0] if sub_ids else top_id}**
    
    **【本線：3連複フォーメーション】**
    * **1列目 (軸)**: `{top_id}`
    * **2列目 (相手)**: `{sub_ids}`
    * **3列目 (ヒモ)**: `{sub_ids + himo_ids}`
    
    **【高配当狙い：3連単 2・3着連軸マルチ】**
    * **1着**: `{top_id}`, `{sub_ids[0] if sub_ids else top_id}`
    * **2着**: `{top_id}`, `{sub_ids}`
    * **3着**: `{top_id}`, `{sub_ids + himo_ids}`
    
    **【抑え・資金回収：ワイド】**
    * `{top_id}` － `{sub_ids[0] if sub_ids else ''}`
    * `{top_id}` － `{sub_ids[1] if len(sub_ids) > 1 else ''}`
    """)

st.markdown("---")
st.caption(
    "💡 毎週の運用手順: TARGETから出力したCSVをGitHubの `data/`"
    " フォルダにそのままドラッグ＆ドロップしてコミットするだけで、自動的に即時反映されます。"
)
