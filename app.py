import datetime
import glob
import io
import itertools
import os
import re
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="競馬予想10 クッション値Vr - 完全統合システム",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    div[data-baseweb="select"] input {
        inputmode: none !important;
        pointer-events: none !important;
    }
    .date-header-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        border: 1px solid #3b82f6;
        padding: 6px 16px;
        border-radius: 20px;
        color: #60a5fa;
        font-size: 14.5px;
        font-weight: bold;
        margin-bottom: 12px;
    }
    .race-type-banner {
        padding: 12px 18px;
        border-radius: 8px;
        margin-bottom: 14px;
        font-size: 15px;
        font-weight: bold;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .race-type-bonus {
        background: linear-gradient(135deg, #7c2d12 0%, #b45309 50%, #d97706 100%);
        color: #fef3c7;
        border: 2px solid #fde68a;
        box-shadow: 0 0 10px rgba(245, 158, 11, 0.5);
    }
    .race-type-hit {
        background: linear-gradient(135deg, #064e3b 0%, #047857 100%);
        color: #d1fae5;
        border: 2px solid #6ee7b7;
    }
    .race-type-recovery {
        background: linear-gradient(135deg, #4c1d95 0%, #6d28d9 100%);
        color: #ede9fe;
        border: 2px solid #c4b5fd;
    }
    .race-type-normal {
        background: #1f2937;
        color: #e5e7eb;
        border: 1px solid #4b5563;
    }
    .recom-panel-go {
        background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
        border: 2px solid #10b981;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 20px;
    }
    .recom-title-go {
        font-size: 16px;
        font-weight: bold;
        color: #34d399;
        margin-bottom: 12px;
        border-bottom: 1px solid #374151;
        padding-bottom: 5px;
    }
    .recom-row {
        margin-bottom: 8px;
        font-size: 14.5px;
        line-height: 1.6;
    }
    .recom-block {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 10px;
    }
    .recom-val-num {
        color: #ffffff;
        font-weight: bold;
        font-size: 15.5px;
        letter-spacing: 1px;
    }
    .horse-card {
        background-color: #161e2e;
        border-left: 5px solid #238636;
        padding: 14px 18px;
        border-radius: 8px;
        margin-bottom: 14px;
        border: 1px solid #30363d;
    }
    .horse-card-header {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 8px;
    }
    .horse-card-title {
        font-size: 18px;
        font-weight: bold;
        color: #ffffff;
    }
    .race-badge-title {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: #ffffff;
        font-weight: bold;
        font-size: 14px;
        padding: 2px 10px;
        border-radius: 6px;
        border: 1px solid #93c5fd;
        margin-right: 6px;
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
    .badge-mark-honmei {
        display: inline-flex; align-items: center; justify-content: center;
        background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
        color: #ffffff; font-size: 12.5px; font-weight: 900; padding: 2px 8px; border-radius: 4px; border: 1px solid #fca5a5; margin-right: 6px;
    }
    .badge-mark-taikou {
        display: inline-flex; align-items: center; justify-content: center;
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: #ffffff; font-size: 12.5px; font-weight: 900; padding: 2px 8px; border-radius: 4px; border: 1px solid #93c5fd; margin-right: 6px;
    }
    .badge-mark-ana {
        display: inline-flex; align-items: center; justify-content: center;
        background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
        color: #ffffff; font-size: 12.5px; font-weight: 900; padding: 2px 8px; border-radius: 4px; border: 1px solid #fde68a; margin-right: 6px;
    }
    .badge-cushion-fit { display: inline-flex; align-items: center; background-color: #064e3b; color: #6ee7b7; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #10b981; }
    .badge-notebook-hit { display: inline-flex; align-items: center; background-color: #831843; color: #f472b6; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #db2777; margin-right: 4px; }
    .badge-stable-hit { display: inline-flex; align-items: center; background-color: #1e3a8a; color: #93c5fd; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #3b82f6; margin-right: 4px; }
    .badge-rescued { display: inline-flex; align-items: center; background-color: #581c87; color: #f0abfc; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #c084fc; }
    
    .badge-track-same { display: inline-flex; align-items: center; background-color: #374151; color: #9ca3af; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #4b5563; }
    .badge-track-turf2dirt { display: inline-flex; align-items: center; background-color: #c2410c; color: #ffedd5; font-weight: 900; font-size: 12.5px; padding: 3px 10px; border-radius: 4px; border: 1px solid #fb923c; box-shadow: 0 0 8px rgba(249, 115, 22, 0.4); }
    .badge-track-dirt2turf { display: inline-flex; align-items: center; background-color: #1d4ed8; color: #eff6ff; font-weight: 900; font-size: 12.5px; padding: 3px 10px; border-radius: 4px; border: 1px solid #60a5fa; box-shadow: 0 0 8px rgba(59, 130, 246, 0.4); }
    .badge-track-first { display: inline-flex; align-items: center; background-color: #047857; color: #ecfdf5; font-weight: 900; font-size: 12.5px; padding: 3px 10px; border-radius: 4px; border: 1px solid #34d399; }

    .fup-badge-rank1 { background: linear-gradient(135deg, #b45309 0%, #d97706 100%); color: #ffffff; font-weight: 900; padding: 2px 8px; border-radius: 4px; border: 1px solid #fde68a; font-size: 13.5px; box-shadow: 0 0 8px rgba(245, 158, 11, 0.5); }
    .fup-badge-top { background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%); color: #ffffff; font-weight: 900; padding: 2px 8px; border-radius: 4px; border: 1px solid #fca5a5; font-size: 13.5px; }
    .fup-badge-mid { background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: #ffffff; font-weight: bold; padding: 2px 8px; border-radius: 4px; border: 1px solid #93c5fd; font-size: 13px; }
    .fup-badge-low { background: #374151; color: #9ca3af; padding: 1px 6px; border-radius: 4px; font-size: 13px; }

    .val-f-top { color: #ffffff; background-color: #ea580c; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #fb923c; }
    .val-s-top { color: #ffffff; background-color: #8b5cf6; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #c4b5fd; }
    .val-arms-top { color: #083344; background-color: #38bdf8; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #0284c7; }
    .val-tua-top { color: #022c22; background-color: #34d399; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #059669; }
</style>
""", unsafe_allow_html=True)

def get_cushion_category(cushion_val, venue_name):
    c_val = float(cushion_val)
    if venue_name == "札幌":
        if c_val <= 7.3: return "場内低<=7.3"
        elif c_val >= 7.7: return "場内高>=7.7"
        else: return "場内中7.4-7.6"
    elif venue_name == "函館":
        if c_val <= 7.2: return "場内低<=7.2"
        elif c_val >= 7.5: return "場内高>=7.5"
        else: return "場内中7.3-7.4"
    
    if c_val <= 8.5: return "<=8.5低"
    elif c_val <= 9.4: return "8.6-9.4 やや低"
    elif c_val <= 9.9: return "9.5-9.9 標準高"
    elif c_val <= 10.4: return "10.0-10.4高"
    else: return ">=10.5 超高"

CUSHION_DATA_BOOK = {
    ("阪神", "芝", 1800, "キズナ", "9.5-9.9 標準高"): ("最重要", "N56 勝19.6% 複41.1% 単421"),
    ("東京", "芝", 1600, "エピファネイア", "9.5-9.9 標準高"): ("最重要", "N98 勝13.3% 複39.8% 単277"),
    ("東京", "芝", 1400, "モーリス", "9.5-9.9 標準高"): ("最重要", "N69 勝10.1% 複29.0% 単408"),
    ("東京", "芝", 1800, "ディープインパクト", "9.5-9.9 標準高"): ("最重要", "N57 勝15.8% 複38.6% 単228"),
    ("東京", "芝", 2000, "キズナ", "8.6-9.4 やや低"): ("最重要", "N66 勝19.7% 複42.4% 単200"),
    ("中京", "芝", 2000, "ディープインパクト", "8.6-9.4 やや低"): ("最重要", "N61 勝18.0% 複42.6% 単178"),
    ("小倉", "芝", 1200, "ダイワメジャー", "9.5-9.9 標準高"): ("最重要", "N66 勝13.6% 複30.3% 単173"),
    ("函館", "芝", 1800, "キズナ", "<=8.5低"): ("最重要", "N62 勝17.7% 複38.7% 単143"),
    ("札幌", "芝", 2000, "オルフェーヴル", "<=8.5低"): ("最重要", "N57 勝15.8% 複35.1% 単136"),
}

COURSE_SPECIALIST_DICT = {
    ("カンレイスター", "中山", "ダ", 1200): "5戦1勝・3着内5回(複100%)",
    ("ルヴァレドクール", "東京", "ダ", 1600): "4戦3勝・3着内4回(複100%)",
}

def clean_str(val):
    if pd.isnull(val): return ""
    return str(val).strip().replace("*", "").replace("$", "").replace(" ", "").replace(" ", "")

def read_csv_robust():
    candidates = ["当日全指数統合10.18.csv", "当日全指数統合.csv", "データ統合.csv", "*全指数統合*.csv"]
    all_found = []
    for c in candidates:
        all_found.extend(glob.glob(c))
    if all_found:
        newest = max(all_found, key=os.path.getmtime)
        for enc in ['utf-8-sig', 'utf-8', 'cp932', 'shift-jis']:
            try:
                df = pd.read_csv(newest, encoding=enc)
                if not df.empty and df.shape[1] >= 38:
                    return df, newest
            except Exception:
                continue
    return pd.DataFrame(), ""

def calc_upgraded_dynamic_score(r, venue_name, track_type, dist_val, c_category):
    score = 0.0
    f_val = float(pd.to_numeric(r.get('F', 0.0), errors='coerce') or 0.0)
    f_rk = int(pd.to_numeric(r.get('F順位', 99), errors='coerce') or 99)
    fup = int(pd.to_numeric(r.get('Fup2', 0), errors='coerce') or 0)
    arm_val = float(pd.to_numeric(r.get('ARM', 0.0), errors='coerce') or 0.0)
    arm_rk = int(pd.to_numeric(r.get('ARM順位', 99), errors='coerce') or 99)
    tua_val = float(pd.to_numeric(r.get('TUA', 0.0), errors='coerce') or 0.0)
    tua_rk = int(pd.to_numeric(r.get('TUA順位', 99), errors='coerce') or 99)
    s_val = float(pd.to_numeric(r.get('S', 0.0), errors='coerce') or 0.0)
    s_rk = int(pd.to_numeric(r.get('S順位', 99), errors='coerce') or 99)
    pop = int(pd.to_numeric(r.get('人気順位', 99), errors='coerce') or 99)

    trainer = clean_str(r.get('調教師', ''))
    sire = clean_str(r.get('種牡馬', ''))
    h_name = clean_str(r.get('馬名', ''))
    track_change = clean_str(r.get('芝ダート変わり', ''))
    interval = str(r.get('間隔', ''))
    weight = float(pd.to_numeric(str(r.get('前場体重', '480')).replace('kg', ''), errors='coerce') or 480.0)

    c_rk = int(pd.to_numeric(r.get('コース連順位', 99), errors='coerce') or 99)
    b_rk = int(pd.to_numeric(r.get('バランス順位', 99), errors='coerce') or 99)
    is_spec = (h_name, venue_name, track_type, dist_val) in COURSE_SPECIALIST_DICT

    nb_hits, stable_hits = [], []
    if track_type == 'ダ' and s_rk == 1 and weight >= 480:
        score += 40.0; nb_hits.append("🐎 ダートで食う(S1位・大型)")
    if interval.isdigit() and int(interval) >= 12:
        score += 30.0; nb_hits.append("🔥 Nなごり(休み明け特注)")
    if arm_rk == 1 and fup >= 6:
        score += 45.0; nb_hits.append("✨ ARMS×FUP(黄金クロス)")
    if track_type == 'ダ' and tua_val >= 190.0 and tua_rk <= 3 and s_rk <= 8:
        score += 35.0; nb_hits.append("💎 TUAダート特注")
    if arm_rk <= 3:
        score += 20.0; nb_hits.append("🌲 Ｃ馬・調教特注")
    if ('芝→ダ' in track_change or 'ダ→芝' in track_change) and tua_rk <= 3:
        score += 25.0; nb_hits.append("🔄 トラック変わり激走特注")

    if '藤原' in trainer: score += 25.0; stable_hits.append("厩舎: 藤原英昭（CW仕上がり鉄板）")
    if '杉山' in trainer: score += 25.0; stable_hits.append("厩舎: 杉山晴紀（坂路終い11秒台加速）")
    if '矢作' in trainer: score += 25.0; stable_hits.append("厩舎: 矢作芳人（坂路A2加速・連闘/中1週）")
    if '中内田' in trainer: score += (30.0 if f_rk == 1 else 20.0); stable_hits.append("厩舎: 中内田充正（CW単走馬なり・勝率抜群）")
    if '木村' in trainer: score += 25.0; stable_hits.append("厩舎: 木村哲也（南W併せ強め・外厩帰り）")
    if '堀' in trainer: score += 20.0; stable_hits.append("厩舎: 堀宣行（南W馬なり・上積み勝負）")
    if '友道' in trainer: score += 20.0; stable_hits.append("厩舎: 友道康夫（芝併せ長距離信頼）")

    if f_rk == 1: score += 50.0
    elif f_rk <= 3: score += 30.0
    if fup == 7: score += 45.0
    elif fup >= 5: score += 30.0
    if c_rk <= 3: score += 25.0
    if b_rk <= 3: score += 25.0
    if is_spec: score += 35.0

    is_sss = (f_val >= 65.0) and (arm_val >= 120.0) and (tua_val >= 200.0)
    is_quad_crown = (f_rk <= 3) and (arm_rk <= 3) and (tua_rk <= 3) and (fup >= 5)
    is_solid_axis = (f_rk == 1) and (fup >= 5)
    is_kakugen = (fup == 7)
    is_f65_top = (f_val >= 65.0)

    is_rescued = is_sss or is_quad_crown or is_solid_axis or is_kakugen or is_spec or len(nb_hits) > 0 or len(stable_hits) > 0 or is_f65_top
    if not is_rescued:
        if c_rk >= 6: score -= 30.0
        if b_rk >= 6: score -= 15.0
        if pop <= 3 and fup <= 1: score -= 35.0

    return score, is_rescued, is_sss, nb_hits, stable_hits

def main():
    st.sidebar.markdown("## 📂 CSVデータ読込管理")
    df_raw, loaded_filename = read_csv_robust()
    
    uploaded_file = st.sidebar.file_uploader("全42列マスターCSVを指定", type=['csv'])
    if uploaded_file is not None:
        for enc in ['utf-8-sig', 'utf-8', 'cp932', 'shift-jis']:
            try:
                df_raw = pd.read_csv(uploaded_file, encoding=enc)
                if not df_raw.empty and df_raw.shape[1] >= 38:
                    loaded_filename = uploaded_file.name
                    break
            except Exception:
                continue

    if df_raw.empty:
        st.markdown("<div class='race-type-banner race-type-normal'>⚠️ 全42列マスターCSVが見つかりません。「当日全指数統合10.18.csv」をアップロードしてください。</div>", unsafe_allow_html=True)
        st.stop()

    st.sidebar.success(f"✅ 読込成功: {loaded_filename} (全{len(df_raw)}頭)")

    venue_dict = {"東": "東京", "中": "中山", "京": "京都", "阪": "阪神", "名": "中京", "小": "小倉", "新": "新潟", "福": "福島", "函": "函館", "札": "札幌"}
    records = []
    for _, row in df_raw.iterrows():
        race_id = clean_str(row.get('場所R', ''))
        dist_raw = row.get('距離', 1600)
        umaban = row.get('馬番', 99)
        horse = clean_str(row.get('馬名', ''))
        trainer = clean_str(row.get('調教師', ''))
        jockey = clean_str(row.get('騎手', ''))
        pop = row.get('人気順位', 99)
        raw_c = clean_str(row.get('C', row.get('C(マーク)', '')))
        mark = clean_str(row.get('印', ''))
        blinkers = clean_str(row.get('C(馬)', ''))

        track = "ダ" if "ダ" in raw_c else ("芝" if "芝" in raw_c else "芝")
        dist_int = int(re.sub(r'\D', '', str(dist_raw))) if re.sub(r'\D', '', str(dist_raw)).isdigit() else 1600

        fup = int(pd.to_numeric(row.get('Fup2', 0), errors='coerce') or 0)
        fup_rk = int(pd.to_numeric(row.get('Fup2順位', 99), errors='coerce') or 99)
        f_val = float(pd.to_numeric(row.get('F', 0.0), errors='coerce') or 0.0)
        f_rk = int(pd.to_numeric(row.get('F順位', 99), errors='coerce') or 99)
        arm_val = float(pd.to_numeric(row.get('ARM', 0.0), errors='coerce') or 0.0)
        arm_rk = int(pd.to_numeric(row.get('ARM順位', 99), errors='coerce') or 99)
        tua_val = float(pd.to_numeric(row.get('TUA', 0.0), errors='coerce') or 0.0)
        tua_rk = int(pd.to_numeric(row.get('TUA順位', 99), errors='coerce') or 99)
        s_val = float(pd.to_numeric(row.get('S', 0.0), errors='coerce') or 0.0)
        s_rk = int(pd.to_numeric(row.get('S順位', 99), errors='coerce') or 99)

        sakaro_chou = clean_str(row.get('坂路調', ''))
        hc_rk = int(pd.to_numeric(row.get('坂路調順位', 99), errors='coerce') or 99)
        hk_rk = int(pd.to_numeric(row.get('坂路血順位', 99), errors='coerce') or 99)
        tk_rk = int(pd.to_numeric(row.get('時計血順位', 99), errors='coerce') or 99)
        c_rk = int(pd.to_numeric(row.get('コース連順位', 99), errors='coerce') or 99)
        k_rk = int(pd.to_numeric(row.get('血統連順位', 99), errors='coerce') or 99)
        b_rk = int(pd.to_numeric(row.get('バランス順位', 99), errors='coerce') or 99)

        sire = clean_str(row.get('種牡馬', ''))
        track_change = clean_str(row.get('芝ダート変わり', ''))
        run_style = clean_str(row.get('前走脚質', ''))
        pass_style = clean_str(row.get('前走決手', ''))
        interval = clean_str(row.get('間隔', ''))
        weight_val = clean_str(row.get('前場体重', '480'))
        race_date = clean_str(row.get('日付', '10.18'))

        match_v = re.match(r'([^\d]+)(\d+)', race_id)
        v_name = venue_dict.get(match_v.group(1), match_v.group(1)) if match_v else "東京"

        if horse:
            records.append({
                'race_id': race_id, 'race_uid': race_id, '競馬場名': v_name, 'track': track, 'dist': dist_int,
                '馬番': int(float(umaban)), '馬名': horse, '印': mark, 'ブリンカー': blinkers,
                '調教師': trainer, '騎手': jockey, '種牡馬': sire, '人気順位': int(float(pop)) if pd.notnull(pop) else 99,
                'Fup2': fup, 'Fup2順位': fup_rk, 'F': f_val, 'F順位': f_rk, 'ARM': arm_val, 'ARM順位': arm_rk,
                'TUA': tua_val, 'TUA順位': tua_rk, 'S': s_val, 'S順位': s_rk,
                '坂路調': sakaro_chou, '坂路調順位': hc_rk, '坂路血順位': hk_rk, '時計血順位': tk_rk,
                'コース連順位': c_rk, '血統連順位': k_rk, 'バランス順位': b_rk,
                '芝ダート変わり': track_change, '前走脚質': run_style, '前走決手': pass_style,
                '間隔': interval, '前場体重': weight_val, '日付': race_date
            })

    df = pd.DataFrame(records)
    if df.empty:
        st.error("解析可能な有効データが存在しません。")
        st.stop()

    all_scores, all_rescued, all_sss, all_nb, all_stbl = [], [], [], [], []
    c_dummy_cat = "9.5-9.9 標準高"
    for _, r in df.iterrows():
        sc, res, sss, nb, stbl = calc_upgraded_dynamic_score(r, r['競馬場名'], r['track'], r['dist'], c_dummy_cat)
        all_scores.append(sc); all_rescued.append(res); all_sss.append(sss); all_nb.append(nb); all_stbl.append(stbl)
    
    df['dynamic_score'] = all_scores
    df['is_rescued'] = all_rescued
    df['is_sss'] = all_sss
    df['nb_hits'] = all_nb
    df['stable_hits'] = all_stbl

    st.sidebar.markdown('---')
    st.sidebar.markdown("### 🎯 高確率・高回収 複合指数検索")
    filter_cross_arms_fup = st.sidebar.checkbox("✨ 【黄金クロス】ARM1位 ✕ Fup6-7点")
    filter_cross_f_tua = st.sidebar.checkbox("🔥 【高確率軸】F上位(1-3位) ✕ TUA上位(1-3位)")
    filter_cross_f65_arm = st.sidebar.checkbox("👑 【絶対神域】F≧65 ＋ ARM≧120 ＋ TUA≧200")
    filter_cross_fup7_arm1 = st.sidebar.checkbox("💎 【爆発力】Fup2=7点 ＋ ARM1〜2位")

    st.sidebar.markdown("#### 個別指数・ノートブック検索")
    filter_f65 = st.sidebar.checkbox("🔥 F指数 ≧ 65以上（絶対主役）")
    filter_fup7 = st.sidebar.checkbox("⚡ Fup2 = 7点（確変馬）")
    filter_arm1 = st.sidebar.checkbox("⭐ ARM 1位（高回収率ホース）")
    filter_tua1 = st.sidebar.checkbox("🚀 TUA 1位（ダート適性馬）")

    def get_matching_races_info(condition_func, condition_name):
        matched_rows = df[df.apply(condition_func, axis=1)]
        if matched_rows.empty: return f"*{condition_name}*: 該当馬なし"
        races = matched_rows['競馬場名'] + matched_rows['race_id'].astype(str) + " (" + matched_rows['馬番'].astype(str) + "番 " + matched_rows['馬名'] + ")"
        return f"**{condition_name}** ({len(matched_rows)}頭):\n" + "\n".join([f"- {r}" for r in races.tolist()])

    active_filters = []
    if filter_cross_arms_fup: active_filters.append((lambda r: r['ARM順位'] == 1 and r['Fup2'] >= 6, "✨ ARM1位×Fup6-7点"))
    if filter_cross_f_tua: active_filters.append((lambda r: r['F順位'] <= 3 and r['TUA順位'] <= 3, "🔥 F上位×TUA上位"))
    if filter_cross_f65_arm: active_filters.append((lambda r: r['F'] >= 65.0 and r['ARM'] >= 120.0 and r['TUA'] >= 200.0, "👑 F65+ARM120+TUA200"))
    if filter_cross_fup7_arm1: active_filters.append((lambda r: r['Fup2'] == 7 and r['ARM順位'] <= 2, "💎 Fup7+ARM上位"))
    if filter_f65: active_filters.append((lambda r: r['F'] >= 65.0, "🔥 F≧65"))
    if filter_fup7: active_filters.append((lambda r: r['Fup2'] == 7, "⚡ Fup2=7点"))
    if filter_arm1: active_filters.append((lambda r: r['ARM順位'] == 1, "⭐ ARM1位"))
    if filter_tua1: active_filters.append((lambda r: r['TUA順位'] == 1, "🚀 TUA1位"))

    if active_filters:
        st.sidebar.markdown('---')
        st.sidebar.markdown("### 📍 該当馬がいるレース一覧")
        for func, name in active_filters:
            st.sidebar.info(get_matching_races_info(func, name))

    st.sidebar.markdown('---')
    st.sidebar.markdown("### 🌿 馬場・クッション値設定")
    track_cond = st.sidebar.selectbox("芝馬場状態", ["良", "稍重", "重", "不良"], index=0)
    cushion_val = st.sidebar.slider("当日クッション値", min_value=6.0, max_value=12.5, value=9.5, step=0.1, format="%.1f")

    st.markdown(f"<div class='date-header-badge'>📅 開催日: 2026年{df['日付'].iloc[0]} | JRAデータ解析エンジン「競馬予想10 クッション値Vr」</div>", unsafe_allow_html=True)

    venue_sort_order = ["東京", "中山", "京都", "阪神", "中京", "小倉", "新潟", "福島", "函館", "札幌"]
    existing_venues = [v for v in venue_sort_order if v in df['競馬場名'].unique()]
    chosen_venue = st.radio("開催場選択", options=existing_venues, horizontal=True)

    v_df = df[df['競馬場名'] == chosen_venue]
    def extract_race_number(uid):
        m = re.search(r'\d+', str(uid))
        return int(m.group()) if m else 99

    races_in_v = v_df[['race_uid', 'race_id', 'track', 'dist']].drop_duplicates('race_uid')
    races_sorted = sorted(races_in_v.to_dict('records'), key=lambda x: extract_race_number(x['race_uid']))

    race_options = {r['race_uid']: f"{r['race_uid']} ({r['track']}{r['dist']}m)" for r in races_sorted}
    selected_race_uid = st.selectbox("レース選択（1R〜順次）", options=list(race_options.keys()), format_func=lambda x: race_options[x])

    race_df = df[df['race_uid'] == selected_race_uid].copy()
    c_cat = get_cushion_category(cushion_val, chosen_venue)

    scores, rescued_flags, sss_flags, nb_hits_list, stable_hits_list = [], [], [], [], []
    for _, r in race_df.iterrows():
        sc, res, sss, nb, stbl = calc_upgraded_dynamic_score(r, chosen_venue, r['track'], r['dist'], c_cat)
        scores.append(sc); rescued_flags.append(res); sss_flags.append(sss); nb_hits_list.append(nb); stable_hits_list.append(stbl)

    race_df['dynamic_score'] = scores
    race_df['is_rescued'] = rescued_flags
    race_df['is_sss'] = sss_flags
    race_df['nb_hits'] = nb_hits_list
    race_df['stable_hits'] = stable_hits_list

    for func, _ in active_filters:
        matched_in_race = race_df[race_df.apply(func, axis=1)]
        if not matched_in_race.empty:
            race_df.loc[race_df.apply(func, axis=1), 'dynamic_score'] += 100.0

    has_bonus = ((race_df['F順位'] <= 3) & (race_df['ARM順位'] <= 3) & (race_df['TUA順位'] <= 3)).sum() >= 3
    has_sss = race_df['is_sss'].any()

    if has_bonus:
        banner_cls = "race-type-bonus"; banner_txt = "👑 ボーナスレース判定（1〜3位が主要指数を完全独占中）"
    elif has_sss:
        banner_cls = "race-type-hit"; banner_txt = "🎯 SSS級・絶対神域出現（F指数65以上＋ARM120＋TUA200の鉄板軸が存在）"
    else:
        banner_cls = "race-type-recovery"; banner_txt = "🔥 波乱抽出・標準ハイブリッド買い目連動レース"

    st.markdown(f"<div class='race-type-banner {banner_cls}'><div>{banner_txt}</div><div>クッション値帯: {c_cat}</div></div>", unsafe_allow_html=True)

    f65_horses = race_df[race_df['F'] >= 65.0].sort_values('F', ascending=False)
    has_f65 = len(f65_horses) > 0
    f_top3 = race_df.sort_values('F順位').head(3)
    f_top3_nums = f_top3['馬番'].tolist()

    if has_f65:
        mode_name = "👑 モードA：F指数65以上【絶対主役モード】"
        mode_desc = "F指数65以上の抜けた馬を不動の連軸とし、F上位＋期待値穴馬へ網を張る構成"
        honmei = f65_horses.iloc[0]
        honmei_num = int(honmei['馬番'])
        opponents = race_df[race_df['馬番'] != honmei_num].copy()
        taikou = opponents.sort_values(['F順位', 'ARM順位', 'TUA順位', 'dynamic_score'], ascending=[True, True, True, False]).iloc[0]
        taikou_num = int(taikou['馬番'])
        second_row = list(set(opponents.sort_values('F順位').head(2)['馬番'].tolist() + opponents.sort_values('ARM順位').head(1)['馬番'].tolist() + opponents.sort_values('TUA順位').head(1)['馬番'].tolist()))
        third_row = list(set(second_row + opponents.sort_values('コース連順位').head(2)['馬番'].tolist() + opponents.sort_values('バランス順位').head(2)['馬番'].tolist()))
        ana_candidates = opponents[opponents['人気順位'] >= 4].sort_values(['ARM順位', 'TUA順位', 'dynamic_score'], ascending=[True, True, False])
        ana = ana_candidates.iloc[0] if not ana_candidates.empty else opponents.iloc[-1]
        ana_num = int(ana['馬番'])
    else:
        mode_name = "🔥 モードB：単勝期待値軸 × F指数相手補完モード"
        mode_desc = "単勝期待値馬を軸にし、相手2列目に好走率約70%のF指数1〜3位を完全固定する構成"
        honmei = race_df.sort_values(['dynamic_score', 'Fup2', 'ARM順位'], ascending=[False, False, True]).iloc[0]
        honmei_num = int(honmei['馬番'])
        second_row = [n for n in f_top3_nums if n != honmei_num]
        taikou_num = second_row[0] if second_row else f_top3_nums[0]
        taikou = race_df[race_df['馬番'] == taikou_num].iloc[0]
        opponents = race_df[race_df['馬番'] != honmei_num].copy()
        third_row = list(set(second_row + opponents.sort_values('坂路調順位').head(2)['馬番'].tolist() + opponents.sort_values('コース連順位').head(2)['馬番'].tolist()))
        ana_candidates = opponents[opponents['人気順位'] >= 4].sort_values(['ARM順位', 'TUA順位', 'dynamic_score'], ascending=[True, True, False])
        ana = ana_candidates.iloc[0] if not ana_candidates.empty else opponents.iloc[-1]
        ana_num = int(ana['馬番'])

    st.markdown(f"""
    <div class='recom-panel-go'>
        <div class='recom-title-go'>{mode_name}</div>
        <div style='font-size: 13px; color: #9ca3af; margin-bottom: 10px;'>{mode_desc}</div>
        <div class='recom-row'>🥇 <strong>本命・連軸</strong>: <span class='recom-val-num'>{honmei_num}番 {honmei['馬名']}</span>（F指数: {honmei['F']} / 動的スコア: {honmei['dynamic_score']:.1f}）</div>
        <div class='recom-row'>🛡️ <strong>対抗・相手筆頭</strong>: <span class='recom-val-num'>{taikou_num}番 {taikou['馬名']}</span>（F指数: {taikou['F']}）</div>
        <div class='recom-row'>💣 <strong>激走穴特注</strong>: <span class='recom-val-num'>{ana_num}番 {ana['馬名']}</span>（ARM: {ana['ARM']} / TUA: {ana['TUA']}）</div>
    </div>
    """, unsafe_allow_html=True)

    sec_nums_str = ", ".join(map(str, sorted(second_row)))
    third_nums_str = ", ".join(map(str, sorted(third_row)))

    st.markdown(f"""
    <div class='recom-block'>
        <h4 style='color: #60a5fa; margin-top: 0;'>🎯 標準ハイブリッド馬券パック フォーメーション</h4>
        <ul style='list-style-type: none; padding-left: 0; line-height: 1.8; font-size: 14px;'>
            <li><strong>【第1の網：主軸回収】</strong> 単勝: <span style='color: #fbbf24; font-weight: bold;'>{honmei_num}</span> ／ 馬単: <span style='color: #fbbf24; font-weight: bold;'>{honmei_num} → {taikou_num}</span></li>
            <li><strong>【第2の網：連対確保】</strong> 馬連: <span style='color: #38bdf8; font-weight: bold;'>{honmei_num} - {sec_nums_str}</span> ／ ワイド: <span style='color: #f472b6; font-weight: bold;'>{honmei_num} - {ana_num}</span></li>
            <li><strong>【第3の網：中配当網】</strong> 3連複F: <span style='color: #34d399; font-weight: bold;'>{honmei_num}</span> ＝ <span style='color: #38bdf8;'>{sec_nums_str}</span> ＝ <span style='color: #a78bfa;'>{third_nums_str}</span></li>
            <li><strong>【第4の網：高配当万馬券】</strong> 3連単F: <span style='color: #fbbf24; font-weight: bold;'>{honmei_num}</span> ⇄ <span style='color: #38bdf8;'>{taikou_num}</span> → <span style='color: #a78bfa;'>{third_nums_str}</span></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🏇 出走馬詳細カルテ")
    sort_col1, sort_col2 = st.columns(2)
    with sort_col1:
        sort_criterion = st.selectbox('📊 並び替え基準（指数・調教・脚質）', [
            '総合動的評価スコア順', 'F指数 降順', 'ARM指数 降順', 'TUA指数 降順', 'S指数 降順', 'Fup2点数 降順', '調教順（坂路調順位 昇順）', '脚質順（前走脚質別）', '馬番順'
        ], index=0)

    if sort_criterion == '総合動的評価スコア順': sorted_df = race_df.sort_values('dynamic_score', ascending=False)
    elif sort_criterion == 'F指数 降順': sorted_df = race_df.sort_values(['F', 'F順位'], ascending=[False, True])
    elif sort_criterion == 'ARM指数 降順': sorted_df = race_df.sort_values(['ARM', 'ARM順位'], ascending=[False, True])
    elif sort_criterion == 'TUA指数 降順': sorted_df = race_df.sort_values(['TUA', 'TUA順位'], ascending=[False, True])
    elif sort_criterion == 'S指数 降順': sorted_df = race_df.sort_values(['S', 'S順位'], ascending=[False, True])
    elif sort_criterion == 'Fup2点数 降順': sorted_df = race_df.sort_values(['Fup2', 'Fup2順位'], ascending=[False, True])
    elif sort_criterion == '調教順（坂路調順位 昇順）': sorted_df = race_df.sort_values('坂路調順位', ascending=True)
    elif sort_criterion == '脚質順（前走脚質別）':
        style_order = {'逃': 1, '先': 2, '中': 3, '後': 4}
        race_df['style_rank'] = race_df['前走脚質'].map(style_order).fillna(99)
        sorted_df = race_df.sort_values(['style_rank', '馬番'], ascending=[True, True])
    else: sorted_df = race_df.sort_values('馬番', ascending=True)

    for _, h in sorted_df.iterrows():
        u_no = int(h['馬番'])
        badges = []
        if u_no == honmei_num: badges.append("<span class='badge-mark-honmei'>◎ 本命</span>")
        elif u_no == taikou_num: badges.append("<span class='badge-mark-taikou'>◯ 対抗</span>")
        elif u_no == ana_num: badges.append("<span class='badge-mark-ana'>🔥 穴特注</span>")

        if h['is_rescued']: badges.append("<span class='badge-rescued'>🛡️ コア指数救済（減点免除）</span>")
        for nb in h['nb_hits']: badges.append(f"<span class='badge-notebook-hit'>{nb}</span>")
        for stbl in h['stable_hits']: badges.append(f"<span class='badge-stable-hit'>{stbl}</span>")

        c_key = (chosen_venue, h['track'], h['dist'], h['種牡馬'], c_cat)
        if c_key in CUSHION_DATA_BOOK:
            judg, stat_txt = CUSHION_DATA_BOOK[c_key]
            if judg == '最重要': badges.append(f"<span class='badge-cushion-fit'>🌿 クッション特注: {h['種牡馬']} ({stat_txt})</span>")

        tc = h['芝ダート変わり']
        if '芝→ダ' in tc:
            tc_badge = f"<span class='badge-track-turf2dirt'>🔄 {tc}</span>"
        elif 'ダ→芝' in tc:
            tc_badge = f"<span class='badge-track-dirt2turf'>🔄 {tc}</span>"
        elif '初出走' in tc:
            tc_badge = f"<span class='badge-track-first'>🆕 {tc}</span>"
        else:
            tc_badge = f"<span class='badge-track-same'>🔹 {tc}</span>"

        fup_val = h['Fup2']
        fup_rk = h['Fup2順位']
        if fup_rk == 1:
            fup_badge = f"<span class='fup-badge-rank1'>👑 {fup_val}点 (順位1位)</span>"
        elif fup_val >= 7:
            fup_badge = f"<span class='fup-badge-top'>⚡ {fup_val}点 (順位{fup_rk})</span>"
        elif fup_val >= 5:
            fup_badge = f"<span class='fup-badge-mid'>🔥 {fup_val}点 (順位{fup_rk})</span>"
        else:
            fup_badge = f"<span class='fup-badge-low'>{fup_val}点 (順位{fup_rk})</span>"

        f_style = "val-f-top" if h['F順位'] <= 3 else ""
        s_style = "val-s-top" if h['S順位'] <= 3 else ""
        arm_style = "val-arms-top" if h['ARM順位'] <= 3 else ""
        tua_style = "val-tua-top" if h['TUA順位'] <= 3 else ""

        choukyou_str = f"調教タイム/内容: <strong>{h['坂路調']}</strong> (順位{h['坂路調順位']})" if h['坂路調'] else f"坂路調順位: {h['坂路調順位']}位"

        st.markdown(f"""
        <div class='horse-card'>
            <div class='horse-card-header'>
                <span class='race-badge-title'>{u_no}番</span>
                <span class='horse-card-title'>{h['馬名']}</span>
                <span style='color: #9ca3af; font-size: 13.5px;'>（{h['調教師']} / {h['騎手']} / {h['人気順位']}番人気）</span>
            </div>
            <div style='margin-bottom: 8px;'>{' '.join(badges)}</div>
            <ul class='horse-card-list'>
                <li><strong>主要5大指数</strong>: 
                    F指数: <span class='{f_style}'>{h['F']}</span> (順位{h['F順位']}) / 
                    Fup2: {fup_badge} / 
                    ARM: <span class='{arm_style}'>{h['ARM']}</span> (順位{h['ARM順位']}) / 
                    TUA: <span class='{tua_style}'>{h['TUA']}</span> (順位{h['TUA順位']}) / 
                    S指数: <span class='{s_style}'>{h['S']}</span> (順位{h['S順位']})
                </li>
                <li><strong>調教データ</strong>: {choukyou_str} ｜ 坂路血: {h['坂路血順位']}位 / 時計血: {h['時計血順位']}位</li>
                <li><strong>適性・補正順位</strong>: コース連: {h['コース連順位']}位 / 血統連: {h['血統連順位']}位 / バランス: {h['バランス順位']}位</li>
                <li><strong>血統＆展開</strong>: 父 {h['種牡馬']} ｜ トラック替: {tc_badge} ｜ 前走脚質: {h['前走脚質']}（決手: {h['前走決手']}）｜ 間隔: {h['間隔']}週 ｜ 前場体重: {h['前場体重']}kg</li>
                <li><strong>総合動的評価スコア</strong>: <span style='color: #facc15; font-weight: bold; font-size: 15px;'>{h['dynamic_score']:.1f}点</span></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
