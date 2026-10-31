    if ('芝→ダ' in track_change or 'ダ→芝' in track_change) and tua_rk <= 3:
        score += 25.0; nb_hits.append("🔄 トラック変わり激走特注")

    if '藤原' in trainer: score += 25.0; stable_hits.append("厩舎: 藤原英昭")
    if '杉山' in trainer: score += 25.0; stable_hits.append("厩舎: 杉山晴紀")
    if '矢作' in trainer: score += 25.0; stable_hits.append("厩舎: 矢作芳人")
    if '中内田' in trainer: score += (30.0 if f_rk == 1 else 20.0); stable_hits.append("厩舎: 中内田充正")
    if '木村' in trainer: score += 25.0; stable_hits.append("厩舎: 木村哲也")
    if '堀' in trainer: score += 20.0; stable_hits.append("厩舎: 堀宣行")
    if '友道' in trainer: score += 20.0; stable_hits.append("厩舎: 友道康夫")

    if f_rk == 1: score += 50.0
    elif f_rk <= 3: score += 30.0
    if fup == 7: score += 45.0
    elif fup >= 5: score += 30.0
    if c_rk <= 3: score += 25.0
    if b_rk <= 3: score += 25.0

    is_sss = (f_val >= 65.0) and (arm_val >= 120.0) and (tua_val >= 200.0)
    is_quad_crown = (f_rk <= 3) and (arm_rk <= 3) and (tua_rk <= 3) and (fup >= 5)
    is_solid_axis = (f_rk == 1) and (fup >= 5)
    is_kakugen = (fup == 7)
    is_f65_top = (f_val >= 65.0)

    if in_val == 0:
        is_rescued = False
    else:
        is_rescued = is_sss or is_quad_crown or is_solid_axis or is_kakugen or len(nb_hits) > 0 or len(stable_hits) > 0 or is_f65_top

    if not is_rescued:
        if c_rk >= 6: score -= 30.0
        if b_rk >= 6: score -= 15.0
        if pop <= 3 and fup <= 1: score -= 35.0

    return score, is_rescued, is_sss, nb_hits, stable_hits

def main():
    st.sidebar.markdown("## 📂 CSVデータ読込管理")
    df_raw, loaded_filename = read_csv_robust()
    sakaro_raw, wood_raw = load_external_training_csvs()

    if not sakaro_raw.empty:
        st.sidebar.success(f"✅ 坂路調教CSV読込成功 ({len(sakaro_raw)}件)")
    else:
        st.sidebar.warning("⚠️ 出馬表_坂路.csv が見つかりません。")

    if not wood_raw.empty:
        st.sidebar.success(f"✅ ウッド調教CSV読込成功 ({len(wood_raw)}件)")
    else:
        st.sidebar.warning("⚠️ 出馬表_ウッド.csv が見つかりません。")
      
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
        st.markdown("<div class='race-type-banner race-type-normal'>⚠️ 全42列マスターCSVが見つかりません。サイドバーからCSVを指定してください。</div>", unsafe_allow_html=True)
        st.stop()

    st.sidebar.success(f"✅ 指数CSV読込成功: {loaded_filename} (全{len(df_raw)}頭)")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎯 チェックBOX 狙い目・レベルフィルタ")
    filter_high_level_in = st.sidebar.checkbox("👑 前走馬券内3頭以上 (ハイレベル特注)")
    filter_high_level_m2 = st.sidebar.checkbox("⭐ 前走掲示板5頭以上 (出世レース特注)")
    filter_danger_in0 = st.sidebar.checkbox("🚨 前走馬券内0頭 (凡戦危険馬を除外)")
    filter_nb_dart = st.sidebar.checkbox("🐎 ノートブック: ダートで食う(S1位・大型)")
    filter_nb_nagori = st.sidebar.checkbox("🔥 ノートブック: Nなごり(休み明け)")
    filter_arms_fup = st.sidebar.checkbox("✨ 指数特注: ARMS×FUP黄金クロス")
    filter_as_cross = st.sidebar.checkbox("👑 指数特注: AS交差馬(F&S上位)")

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
        raw_c = clean_str(row.get('C', row.get('C(馬)', '')))
        mark = row.get('印', 2)
        m2_raw = row.get('M2', 0)

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
        race_date = clean_str(row.get('日付', '10.25'))

        in_num = pd.to_numeric(mark, errors='coerce')
        if pd.isna(in_num): in_num = 2
        m2_num = pd.to_numeric(m2_raw, errors='coerce')
        if pd.isna(m2_num): m2_num = 0

        match_v = re.match(r'([^\d]+)(\d+)', race_id)
        v_name = venue_dict.get(match_v.group(1), match_v.group(1)) if match_v else "新"

        s_row = pd.Series()
        if not sakaro_raw.empty and horse:
            matched_s = sakaro_raw[sakaro_raw['馬名'].astype(str).str.strip() == horse]
            if not matched_s.empty:
                s_row = matched_s.iloc[-1]

        w_row = pd.Series()
        if not wood_raw.empty and horse:
            matched_w = wood_raw[wood_raw['馬名'].astype(str).str.strip() == horse]
            if not matched_w.empty:
                w_row = matched_w.iloc[-1]

        if horse:
            records.append({
                'race_id': race_id, 'race_uid': race_id, '競馬場名': v_name, 'track': track, 'dist': dist_int,
                '馬番': int(float(umaban)), '馬名': horse, '印': in_num, 'M2': m2_num,
                '調教師': trainer, '騎手': jockey, '種牡馬': sire, '人気順位': int(float(pop)) if pd.notnull(pop) else 99,
                'Fup2': fup, 'Fup2順位': fup_rk, 'F': f_val, 'F順位': f_rk, 'ARM': arm_val, 'ARM順位': arm_rk,
                'TUA': tua_val, 'TUA順位': tua_rk, 'S': s_val, 'S順位': s_rk,
                '坂路T1': s_row.get('Time1', ''), '坂路L2': s_row.get('Lap2', ''), '坂路L1': s_row.get('Lap1', ''),
                '坂路T4': s_row.get('Time4', ''), 'ウッド5F': w_row.get('5F', ''), 'ウッドL2': w_row.get('Lap2', ''), 'ウッドL1': w_row.get('Lap1', ''),
                '坂路調順位': hc_rk, '坂路血順位': hk_rk, '時計血順位': tk_rk,
                'コース連順位': c_rk, '血統連順位': k_rk, 'バランス順位': b_rk,
                '芝ダート変わり': track_change, '前走脚質': run_style, '前走決手': pass_style,
                '間隔': interval, '前場体重': weight_val, '日付': race_date
            })

    df = pd.DataFrame(records)
    if df.empty:
        st.error("解析可能な有効データが存在しません。")
        st.stop()

    race_date_str = str(df['日付'].iloc[0]) if not df.empty and '日付' in df.columns else "10.25"

    st.sidebar.markdown('---')
    st.sidebar.markdown("### 🌿 馬場・クッション値設定")
    track_cond = st.sidebar.selectbox("芝馬場状態", ["良", "稍重", "重", "不良"], index=0)
    cushion_val = st.sidebar.slider("当日クッション値", min_value=6.0, max_value=12.5, value=9.5, step=0.1, format="%.1f")

    st.markdown(f"<div class='date-header-badge'>📅 開催日: 2026年{race_date_str} | JRAデータ解析エンジン「競馬予想10 クッション値Vr」</div>", unsafe_allow_html=True)

    venue_sort_order = ["東京", "中山", "京都", "阪神", "中京", "小倉", "新潟", "福島", "函館", "札幌", "新"]
    existing_venues = [v for v in venue_sort_order if v in df['競馬場名'].unique()]
    chosen_venue = st.radio("開催場選択", options=existing_venues, horizontal=True)

    v_df = df[df['競馬場名'] == chosen_venue]
    def extract_race_number(uid):
        m = re.search(r'\d+', str(uid))
        return int(m.group()) if m else 99

    races_in_v = v_df[['race_uid', 'race_id', 'track', 'dist']].drop_duplicates('race_uid')
    races_sorted = sorted(races_in_v.to_dict('records'), key=lambda x: extract_race_number(x['race_uid']))

    race_options = {}
    for r in races_sorted:
        r_uid = r['race_uid']
        r_subset = v_df[v_df['race_uid'] == r_uid]
        
        race_tags = []
        if filter_high_level_in and (r_subset['印'] >= 3).any(): race_tags.append("👑印≧3")
        if filter_high_level_m2 and (r_subset['M2'] >= 5).any(): race_tags.append("⭐M2≧5")
        if filter_danger_in0 and (r_subset['印'] == 0).any(): race_tags.append("🚨印0除外")
        if filter_nb_dart:
            has_dart = r_subset.apply(lambda row: (row['track'] == 'ダ' and row['S順位'] == 1 and float(str(row['前場体重']).replace('kg','')) >= 480), axis=1).any()
            if has_dart: race_tags.append("🐎ダート特注")
        if filter_nb_nagori:
            has_nagori = r_subset.apply(lambda row: (str(row['間隔']).isdigit() and int(row['間隔']) >= 12), axis=1).any()
            if has_nagori: race_tags.append("🔥Nなごり")
        if filter_arms_fup:
            has_af = r_subset.apply(lambda row: (row['ARM順位'] == 1 and row['Fup2'] >= 6), axis=1).any()
            if has_af: race_tags.append("✨ARMSクロス")
        if filter_as_cross:
            has_as = r_subset.apply(lambda row: (row['F順位'] <= 3 and row['S順位'] <= 3), axis=1).any()
            if has_as: race_tags.append("👑AS交差")

        tag_str = f" [{' '.join(race_tags)}]" if race_tags else ""
        race_options[r_uid] = f"{r['race_uid']} ({r['track']}{r['dist']}m){tag_str}"

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

    has_bonus = ((race_df['F順位'] <= 3) & (race_df['ARM順位'] <= 3) & (race_df['TUA順位'] <= 3)).sum() >= 3
    has_cross = ((race_df['ARM順位'] == 1) & (race_df['Fup2'] >= 6)).any()
    has_sss = race_df['is_sss'].any()
    is_race_pikai = has_bonus or has_cross or has_sss

    if is_race_pikai:
        banner_cls = "race-type-bonus"; banner_txt = "👑👑【該当馬確認】最強ロジック合致レース（期待値・勝率MAX）"
    elif has_sss:
        banner_cls = "race-type-hit"; banner_txt = "🎯 SSS級・絶対神域出現（F指数65以上＋ARM120＋TUA200の鉄板軸が存在）"
    else:
        banner_cls = "race-type-recovery"; banner_txt = "🔥 波乱抽出・標準ハイブリッド買い目連動レース"

    st.markdown(f"<div class='race-type-banner {banner_cls}'><div>{banner_txt}</div><div>クッション値帯: {c_cat}</div></div>", unsafe_allow_html=True)

    f_top3_df = race_df.sort_values('F順位').head(3)
    s_top3_df = race_df.sort_values('S順位').head(3)
    arm_top3_df = race_df.sort_values('ARM順位').head(3)
    tua_top3_df = race_df.sort_values('TUA順位').head(3)

    f_top3_nums = f_top3_df['馬番'].tolist()
    s_top3_nums = s_top3_df['S順位'].tolist()
    arm_top3_nums = arm_top3_df['ARM順位'].tolist() if 'ARM順位' in arm_top3_df else []
    tua_top3_nums = tua_top3_df['TUA順位'].tolist() if 'TUA順位' in tua_top3_df else []

    safe_race_df = race_df[race_df['印'] > 0] if filter_danger_in0 else race_df

    f_safe_top3 = safe_race_df.sort_values('F順位').head(3)['馬番'].tolist()
    s_safe_top3 = safe_race_df.sort_values('S順位').head(3)['馬番'].tolist()

    a_group_nums = sorted(list(set(f_safe_top3 + s_safe_top3)))
    as_intersect_nums = sorted(list(set(f_safe_top3) & set(s_safe_top3)))
    f_arm_nums = sorted(list(set(f_safe_top3) & set(arm_top3_nums)))
    s_tua_nums = sorted(list(set(s_safe_top3) & set(tua_top3_nums)))
    quad_nums = sorted(list(set(f_safe_top3) & set(s_safe_top3) & set(arm_top3_nums) & set(tua_top3_nums)))

    z_candidates = safe_race_df[~safe_race_df['馬番'].isin(a_group_nums)].sort_values(
        ['坂路調順位', 'コース連順位', 'バランス順位'], ascending=[True, True, True]
    )
    z_nums = z_candidates.head(3)['馬番'].tolist()

    as_str = ", ".join([f"<strong>{n}番</strong>" for n in as_intersect_nums]) if as_intersect_nums else "なし"
    f_arm_str = ", ".join([f"<strong>{n}番</strong>" for n in f_arm_nums]) if f_arm_nums else "なし"
    s_tua_str = ", ".join([f"<strong>{n}番</strong>" for n in s_tua_nums]) if s_tua_nums else "なし"
    quad_str = ", ".join([f"<strong>{n}番</strong>" for n in quad_nums]) if quad_nums else "なし"
    z_str = ", ".join([f"<strong>{n}番</strong>" for n in z_nums]) if z_nums else "なし"

    filter_notice = " [🚨 前走0頭消し・チェックBOX連動適用済み]" if (filter_danger_in0 or filter_high_level_in) else ""

    st.markdown(f"""
    <div class='recom-block' style='border: 2px solid #3b82f6;'>
        <h4 style='color: #60a5fa; margin-top: 0;'>🎯 第3の馬券パターン：AS交差 ＆ 種別シナジー・Z特化フォーメーション{filter_notice}</h4>
        <div style='font-size: 13.5px; color: #cbd5e1; margin-bottom: 8px;'>
            <strong>A群（F上位1〜3位 ＋ S上位1〜3位）</strong>: {', '.join([f"<strong>{n}番</strong>" for n in a_group_nums])} (計{len(a_group_nums)}頭)<br>
            👑 <strong>【AS交差馬（F&S両方上位）】</strong>: {as_str}<br>
            ⭐ <strong>【F × ARM交差馬（絶対能力 ＋ 高回収）】</strong>: {f_arm_str}<br>
            🚀 <strong>【S × TUA交差馬（スピード ＋ 機動力）】</strong>: {s_tua_str}<br>
            💎 <strong>【4大指数完全網羅馬（F・S・ARM・TUAすべて上位）】</strong>: {quad_str}<br>
            🎯 <strong>【アプリ自動抽出・厳選Z馬（3列目特化候補）】</strong>: <span style='color: #38bdf8; font-weight: bold;'>{z_str}</span><br>
            ※前走頭数ロジック（危険馬除外・ハイレベル裏付け）を完全反映した鉄壁の3連単構成。
        </div>
        <ul style='list-style-type: none; padding-left: 0; line-height: 1.8; font-size: 14px;'>
            <li><strong>【第3パターン構築】</strong> 3連単F: <span style='color: #fbbf24; font-weight: bold;'>{', '.join(map(str, a_group_nums))}</span> ＝ <span style='color: #fbbf24; font-weight: bold;'>{', '.join(map(str, a_group_nums))}</span> → <span style='color: #38bdf8; font-weight: bold;'>{z_str}</span></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    f65_horses = race_df[race_df['F'] >= 65.0].sort_values('F', ascending=False)
    has_f65 = len(f65_horses) > 0

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

        in_v = h['印']
        m2_v = h['M2']
        if in_v == 0:
            badges.append("<span class='badge-danger-fan'>🚨 前走相手馬券内0頭(凡戦危険馬)</span>")
        elif in_v >= 8:
            badges.append(f"<span class='badge-high-level'>👑 前走相手馬券内{in_v}頭(超ハイレベル)</span>")
        elif in_v >= 3:
            badges.append(f"<span class='badge-notebook-hit'>🔥 前走相手馬券内{in_v}頭</span>")

        if m2_v >= 5:
            badges.append(f"<span class='badge-cushion-fit'>⭐ 前走相手掲示板{m2_v}頭(出世レース)</span>")

        is_as = h['F順位'] <= 3 and h['S順位'] <= 3
        if is_as: badges.append("<span class='badge-as-intersect'>👑 AS交差馬 (F&S上位)</span>")

        if h['is_rescued']: badges.append("<span class='badge-rescued'>🛡️ コア指数救済（減点免除）</span>")
        for nb in h['nb_hits']: badges.append(f"<span class='badge-notebook-hit'>{nb}</span>")
        for stbl in h['stable_hits']: badges.append(f"<span class='badge-stable-hit'>{stbl}</span>")

        c_key = (chosen_venue, h['track'], h['dist'], h['種牡馬'], c_cat)
        if c_key in CUSHION_DATA_BOOK:
            judg, stat_txt = CUSHION_DATA_BOOK[c_key]
            if judg == '最重要': badges.append(f"<span class='badge-cushion-fit'>🌿 クッション特注: {h['種牡馬']} ({stat_txt})</span>")

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

        s_t4 = h.get('坂路T4', '')
        s_l2 = h.get('坂路L2', '')
        s_l1 = h.get('坂路L1', '')
        w_5f = h.get('ウッド5F', '')
        w_l2 = h.get('ウッドL2', '')
        w_l1 = h.get('ウッドL1', '')

        judge_label, judge_color = parse_and_judge_lap(s_l1, s_l2, s_t4)
        
        sakaro_str = f"坂路[4F:{s_t4 or '---'} | L2:{s_l2 or '---'} → L1:{s_l1 or '---'}]" if s_t4 else "坂路データなし"
        wood_str = f"ウッド[5F:{w_5f or '---'} | L2:{w_l2 or '---'} → L1:{w_l1 or '---'}]" if w_5f else "ウッドデータなし"
        choukyou_summary = f"{sakaro_str} ｜ {wood_str}"

        race_place_num_str = f"【{chosen_venue}{re.search(r'\d+', str(h['race_uid'])).group()}R】" if re.search(r'\d+', str(h['race_uid'])) else f"【{chosen_venue}】"

        st.markdown(f"""
        <div class='horse-card'>
            <div class='horse-card-header'>
                <span class='race-badge-title'>{race_place_num_str} {u_no}番</span>
                <span class='horse-card-title'>{h['馬番']}番 {h['馬名']}</span>
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
                <li><strong>対戦レベル評価</strong>: 前走馬券内頭数(印): <strong>{in_v}頭</strong> ｜ 前走掲示板内頭数(M2): <strong>{m2_v}頭</strong></li>
                <li><strong>調教ラップ＆判定</strong>: <span style='background-color: {judge_color}; color: #fff; padding: 2px 6px; border-radius: 4px; font-weight: bold;'>{judge_label}</span><br>
                    <span style='font-size: 12.5px; color: #94a3b8;'>{choukyou_summary}</span> ｜ 坂路血: {h['坂路血順位']}位 / 時計血: {h['時計血順位']}位</li>
                <li><strong>適性・補正順位</strong>: コース連: {h['コース連順位']}位 / 血統連: {h['血統連順位']}位 / Balance: {h['バランス順位']}位</li>
                <li><strong>血統＆展開</strong>: 父 {h['種牡馬']} ｜ トラック替: {h['芝ダート変わり']} ｜ 前走脚質: {h['前走脚質']}（決手: {h['前走決手']}）｜ 間隔: {h['間隔']}週 ｜ 前場体重: {h['前場体重']}kg</li>
                <li><strong>総合動的評価スコア</strong>: <span style='color: #facc15; font-weight: bold; font-size: 15px;'>{h['dynamic_score']:.1f}点</span></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
