import streamlit as st
import pandas as pd
import numpy as np

# ==========================================
# 1. 究極バイアス・ランキングデータ定義
# ==========================================

# 全国横断 最重要・馬券内率最強マトリクス
# 複勝率40%超、単勝回収率特大のSSS級バイアス
TOP_MATRIX_RULES = [
    {"course": "中京芝2000", "cushion_category": "8.6-9.4 やや低", "sire": "ディープインパクト", "bonus": 50, "desc": "複勝率42.6% / 単回178"},
    {"course": "東京芝2000", "cushion_category": "8.6-9.4 やや低", "sire": "キズナ", "bonus": 50, "desc": "複勝率42.4% / 単回200"},
    {"course": "東京芝2000", "cushion_category": "8.6-9.4 やや低", "sire": "エピファネイア", "bonus": 50, "desc": "複勝率42.4% / 単回149"},
    {"course": "阪神芝1800外", "cushion_category": "9.5-9.9 標準高", "sire": "キズナ", "bonus": 50, "desc": "複勝率41.1% / 単回421"},
    {"course": "東京芝1600", "cushion_category": "9.5-9.9 標準高", "sire": "エピファネイア", "bonus": 50, "desc": "複勝率39.8% / 単回277"}
]

# 競馬場・コース別 超高複勝率・局地ロジック[cite: 13, 19, 26, 32, 43, 48, 49, 59, 65, 68, 78, 86]
LOCAL_BONUS_RULES = [
    {"course": "福島芝2600", "cushion_category": "≤8.5 低", "sire": "ゴールドシップ", "bonus": 40, "desc": "複勝率54.2% / 単回255"},
    {"course": "新潟芝1800外", "cushion_category": "9.5-9.9 標準高", "sire": "ハーツクライ", "bonus": 40, "desc": "複勝率50.0%"},
    {"course": "中山芝1800", "cushion_category": "8.6-9.4 やや低", "sire": "キズナ", "bonus": 40, "desc": "複勝率45.7%"},
    {"course": "中京芝2200", "cushion_category": "8.6-9.4 やや低", "sire": "ディープインパクト", "bonus": 40, "desc": "複勝率54.5%"},
    {"course": "京都芝2000内", "cushion_category": "≥10.5 超高", "sire": "キタサンブラック", "bonus": 40, "desc": "複勝率50.0%"},
    {"course": "函館芝1800", "cushion_category": "≤7.2 場内低", "sire": "キズナ", "bonus": 45, "desc": "複勝率51.9% / 単回209"},
    {"course": "札幌芝1800", "cushion_category": "≤8.5 低", "sire": "ドゥラメンテ", "bonus": 40, "desc": "複勝率48.8%"}
]

# ==========================================
# 2. 関数定義（ロジック完全集約）
# ==========================================

def get_cushion_category(place, cv):
    """馬場と当日のクッション値から区分を判定"""
    if place in ["札幌", "函館"]:
        if place == "札幌":
            return "≤7.3 場内低" if cv <= 7.3 else "≥7.7 場内高" if cv >= 7.7 else "平均"
        else:
            return "≤7.2 場内低" if cv <= 7.2 else "≥7.5 場内高" if cv >= 7.5 else "平均"
    
    if cv <= 8.5: return "≤8.5 低"
    elif 8.6 <= cv <= 9.4: return "8.6-9.4 やや低"
    elif 9.5 <= cv <= 9.9: return "9.5-9.9 標準高"
    elif 10.0 <= cv <= 10.4: return "10.0-10.4 高"
    else: return "≥10.5 超高"

def evaluate_lap(row):
    """坂路・ウッドの調教ラップ判定（完全加速等の評価）"""
    if pd.isna(row.get('Lap4')): return "評価なし"
    l4, l3, l2, l1 = row['Lap4'], row['Lap3'], row['Lap2'], row['Lap1']
    # 坂路完全加速判定 (A1〜A3) ※実質負荷基準
    if l4 > l3 > l2 > l1 and row.get('Time1', 99) <= 56.0 and l1 <= 13.0:
        if l1 < 12.0: return "A3特大(終い11秒台)"
        elif l1 <= 12.4: return "A2特注(12.4秒以下)"
        else: return "A1(完全加速)"
    return "非加速・減速"

def check_trainer_jockey_bias(row):
    """調教師・騎手の特注パターン判定"""
    trainer, jockey = str(row.get('調教師', '')), str(row.get('騎手', ''))
    f_rank = int(row.get('F指数順位', 99))
    fup_val = float(row.get('Fup2数値', 0)) # 順位ではなく数値を厳格に取得
    lap_eval = row.get('Lap_Eval', '')

    if "斉藤崇史" in trainer or "中舘英二" in trainer:
        if f_rank == 1: return 20
    if "中内田充正" in trainer and "川田" in jockey and f_rank == 1:
        return 30
    if "杉山晴紀" in trainer and "西村" in jockey and "A3" in lap_eval:
        return 35
    if "木村哲也" in trainer and "ルメール" in jockey:
        if fup_val >= 5: return 25
        if fup_val <= 4: return -50 # 危険馬指定
    return 0

def calculate_tier_score(df, place, cv):
    """各馬の総合スコアリングとTier判定"""
    cushion_cat = get_cushion_category(place, cv)
    
    scores = []
    for idx, row in df.iterrows():
        score = 0
        notes = []
        
        # 指数マトリクス評価
        f_val, f_rank = row.get('F指数', 0), row.get('F指数順位', 99)
        arms_val = row.get('ARMS2指数', 0)
        tua_val = row.get('TUA指数', 0) # tuaは分析指標として扱う
        fup_val = row.get('Fup2数値', 0) # 順位と混同しない
        
        # SSS級判定
        is_sss = False
        if f_val >= 70 and arms_val >= 120 and tua_val >= 200:
            score += 100
            notes.append("🔥SSS級絶対神域")
            is_sss = True
            
        # 指数四冠
        if f_rank == 1 and row.get('Fup2順位') == 1 and row.get('ARMS2順位') == 1 and row.get('TUA順位') == 1:
            score += 80
            notes.append("👑四冠馬")
            
        # Fup2の罠と確変
        if fup_val == 7:
            score += 50
            notes.append("🎯Fup確変(7)")
        elif fup_val >= 5:
            score += 30
        elif fup_val == 1 and not is_sss and f_val <= 72:
            score -= 100
            notes.append("⚠️Fup1ダミー消去")
            
        # 調教加点
        lap_eval = row.get('Lap_Eval', '')
        if "A3特大" in lap_eval: score += 40
        elif "A2特注" in lap_eval: score += 30
        elif "A1" in lap_eval: score += 15
        
        # SSS×究極ラップシナジー
        if f_rank == 1 and ("A2特注" in lap_eval or "A3特大" in lap_eval):
            score += 60
            notes.append("⚡F1位×究極ラップ")

        # 陣営バイアス加点
        bias_score = check_trainer_jockey_bias(row)
        if bias_score > 0: notes.append("🏇陣営特注")
        elif bias_score < 0: notes.append("⚠️陣営危険")
        score += bias_score

        # クッション値 × コース × 種牡馬の最強マトリクス判定
        course_name = f"{place}{row.get('芝ダ', '')}{row.get('距離', '')}"
        sire = str(row.get('種牡馬', '')).strip()
        
        for rule in TOP_MATRIX_RULES + LOCAL_BONUS_RULES:
            if course_name.startswith(rule['course']) and cushion_cat == rule['cushion_category'] and sire == rule['sire']:
                score += rule['bonus']
                notes.append(f"🏆ランキング特注 ({rule['desc']})")
                
        df.at[idx, 'Score'] = score
        df.at[idx, 'Notes'] = " / ".join(notes)
        
    return df

def evaluate_easy_mode(df):
    """イージーモード（歪みレース）の判定"""
    # モック判定（本来は連闘・叩き2戦目の頭数をカウント）
    bad_cond_count = np.random.randint(4, 10)
    is_easy_mode = 7 <= bad_cond_count <= 12
    return is_easy_mode, bad_cond_count

def generate_formation(df, is_easy_mode):
    """Tierに基づく買い目の自動構築"""
    df_sorted = df.sort_values(by='Score', ascending=False)
    
    tier1 = df_sorted[df_sorted['Score'] >= 100]['馬番'].tolist()
    tier2 = df_sorted[(df_sorted['Score'] >= 60) & (df_sorted['Score'] < 100)]['馬番'].tolist()
    tier3 = df_sorted[(df_sorted['Score'] >= 30) & (df_sorted['Score'] < 60)]['馬番'].tolist()
    
    # イージーモードかつTier1にSSS級がいる場合、裏表マルチ発動
    if is_easy_mode and tier1:
        formation = f"【勝負フォーメーション (マルチ推奨)】\n1着: {tier1}\n2着: {tier1 + tier2}\n3着: {tier1 + tier2 + tier3}"
    else:
        formation = f"【標準フォーメーション】\n1列目: {tier1 if tier1 else tier2[:1]}\n2列目: {tier2}\n3列目: {tier2 + tier3}"
    return formation

# ==========================================
# 3. Streamlit UI 構築
# ==========================================

st.set_page_config(page_title="競馬予想10 クッション値Vr", layout="wide")
st.title("🏇 競馬予想10 クッション値Vr - SSSマトリクスシステム")
st.markdown("オッズ断層予想を排除し、F指数・ARMS2・TUA・完全加速ラップ・当日クッション値を論理的に融合した究極のデータ分析基盤。")

# サイドバー: 設定
with st.sidebar:
    st.header("環境設定")
    place = st.selectbox("開催場所", ["東京", "中山", "京都", "阪神", "中京", "新潟", "福島", "小倉", "札幌", "函館"])
    cv = st.number_input("当日のクッション値", min_value=5.0, max_value=12.5, value=9.5, step=0.1)
    st.info(f"判定区分: {get_cushion_category(place, cv)}")

# ランキングデータ表示タブ
st.subheader("🏆 最強マトリクス ＆ 局地ロジックランキング")
with st.expander("データブック上位ロジックを確認する (Click to expand)"):
    st.markdown("以下の条件に該当する出走馬には、自動的に特大ボーナススコアが付与されます。")
    st.markdown("### 全国横断 最重要マトリクス トップ5[cite: 89, 161]")
    st.table(pd.DataFrame(TOP_MATRIX_RULES)[['course', 'cushion_category', 'sire', 'desc']])
    
    st.markdown("### 競馬場・コース別 局地ロジック[cite: 13, 19, 26, 32, 43, 48, 49, 59, 65, 68, 78, 86]")
    st.table(pd.DataFrame(LOCAL_BONUS_RULES)[['course', 'cushion_category', 'sire', 'desc']])

st.divider()

# デモ用データ生成（本来はCSVアップロード）
st.subheader("📊 出走馬データ解析結果")
if st.button("マトリクス解析を実行"):
    # モックデータ生成
    mock_data = {
        '馬番': [1, 2, 3, 4, 5],
        '馬名': ['ディープモンスター', 'キズナボーイ', 'ルメールマジック', 'ダミーホース', 'カナロアキング'],
        '芝ダ': ['芝', '芝', '芝', '芝', '芝'],
        '距離': ['2000', '2000', '2000', '2000', '1600'],
        '調教師': ['矢作芳人', '中内田充正', '木村哲也', '不明', '杉山晴紀'],
        '騎手': ['武豊', '川田将雅', 'ルメール', '新人', '西村淳也'],
        '種牡馬': ['ディープインパクト', 'キズナ', 'エピファネイア', 'マツリダゴッホ', 'ロードカナロア'],
        'F指数': [71, 65, 75, 40, 60],
        'F指数順位': [2, 3, 1, 10, 4],
        'Fup2数値': [6, 5, 7, 1, 4], # 数値として扱う
        'ARMS2指数': [125, 110, 130, 80, 100],
        'TUA指数': [210, 190, 205, 100, 150],
        'Lap4': [14.0, 14.5, 13.5, 15.0, 14.2],
        'Lap3': [13.5, 14.0, 13.0, 15.5, 13.8],
        'Lap2': [13.0, 13.5, 12.5, 14.0, 12.5],
        'Lap1': [12.2, 12.8, 11.8, 14.5, 11.5],
        'Time1': [52.7, 54.8, 50.8, 59.0, 52.0]
    }
    df = pd.DataFrame(mock_data)
    
    # ラップ評価
    df['Lap_Eval'] = df.apply(evaluate_lap, axis=1)
    
    # スコアリング
    df['Score'] = 0
    df['Notes'] = ""
    df = calculate_tier_score(df, place, cv)
    
    # イージーモード判定
    is_easy, count = evaluate_easy_mode(df)
    
    # 結果表示UI
    col1, col2 = st.columns([2, 1])
    with col1:
        st.dataframe(df[['馬番', '馬名', '種牡馬', 'Score', 'Notes', 'Lap_Eval']], use_container_width=True)
    with col2:
        st.info(f"**レース環境歪み判定**\n悪条件該当馬: {count}頭\n判定: {'🚨 イージーモード (歪み大)' if is_easy else '⚠️️ 通常モード'}")
        st.success(generate_formation(df, is_easy))
