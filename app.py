
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
