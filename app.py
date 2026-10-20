import csv
import datetime
import glob
import io
import itertools
import os
import re
import numpy as np
import pandas as pd
import streamlit as st

# ==============================================================================
# 競馬予想10 クッション値Vr - 完全統合Webアプリケーション
# 【3分割CSV自動統合エンジン・全11指数・坂路6大区分＆猛時計例外・現役最強コース巧者内蔵】
# ==============================================================================

st.set_page_config(
    page_title="競馬予想10 クッション値Vr - 完全統合システム",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    /* スマホでセレクトボックスをタップしてもキーボードを出さない設定 */
    div[data-baseweb="select"] input {
        inputmode: none !important;
        pointer-events: none !important;
    }
    .metric-container { display: flex; justify-content: space-around; background-color: #161b22; padding: 14px; border-radius: 10px; margin-bottom: 18px; border: 1px solid #30363d; }
    .date-header-badge { display: inline-flex; align-items: center; gap: 8px; background: linear-gradient(135deg, #1f2937 0%, #111827 100%); border: 1px solid #3b82f6; padding: 6px 16px; border-radius: 20px; color: #60a5fa; font-size: 14.5px; font-weight: bold; margin-bottom: 12px; }
    .race-type-banner { padding: 12px 18px; border-radius: 8px; margin-bottom: 14px; font-size: 15px; font-weight: bold; display: flex; align-items: center; justify-content: space-between; }
    .race-type-solid { background: linear-gradient(135deg, #064e3b 0%, #047857 100%); color: #ecfdf5; border: 1px solid #34d399; }
    .race-type-bonus { background: linear-gradient(135deg, #7c2d12 0%, #b45309 50%, #d97706 100%); color: #fef3c7; border: 2px solid #fde68a; box-shadow: 0 0 10px rgba(245, 158, 11, 0.5); }
    .race-type-recovery { background: linear-gradient(135deg, #831843 0%, #be123c 100%); color: #fff1f2; border: 1px solid #fb7185; box-shadow: 0 0 8px rgba(251, 113, 133, 0.4); }
    .race-type-chaos { background: linear-gradient(135deg, #374151 0%, #1f2937 100%); color: #e5e7eb; border: 1px solid #6b7280; }
    
    .recom-panel-go { background: linear-gradient(135deg, #111827 0%, #1f2937 100%); border: 2px solid #10b981; border-radius: 10px; padding: 16px 20px; margin-bottom: 20px; }
    .recom-title-go { font-size: 16px; font-weight: bold; color: #34d399; margin-bottom: 12px; border-bottom: 1px solid #374151; padding-bottom: 5px; }
    .recom-row { margin-bottom: 8px; font-size: 14.5px; line-height: 1.6; }
    .recom-block { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; padding: 10px 14px; margin-bottom: 10px; }
    .recom-label { font-weight: bold; color: #fbbf24; display: inline-block; font-size: 14px; }
    .recom-val-num { color: #ffffff; font-weight: bold; font-size: 15.5px; letter-spacing: 1px; }
    
    .horse-card { background-color: #161e2e; border-left: 5px solid #238636; padding: 14px 18px; border-radius: 8px; margin-bottom: 14px; border-top: 1px solid #30363d; border-right: 1px solid #30363d; border-bottom: 1px solid #30363d; }
    .horse-card-header { display: flex; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 8px; }
    .horse-card-title { font-size: 18px; font-weight: bold; color: #ffffff; }
    .race-badge-title { background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); color: #ffffff; font-weight: bold; font-size: 14px; padding: 2px 10px; border-radius: 6px; border: 1px solid #93c5fd; margin-right: 6px; }
    .horse-card-list { list-style-type: none; padding-left: 0; margin: 0; }
    .horse-card-list li { font-size: 13.5px; color: #c9d1d9; margin-bottom: 6px; line-height: 1.6; }
    .horse-card-list li::before { content: "• "; color: #58a6ff; font-weight: bold; }

    /* 印バッジ */
    .badge-mark-gtv { background: linear-gradient(135deg, #b45309 0%, #d97706 100%); color: #ffffff; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #fde68a; }
    .badge-mark-c { background: linear-gradient(135deg, #0891b2 0%, #06b6d4 100%); color: #ffffff; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #a5f3fc; }

    .badge-accel-on { background: linear-gradient(135deg, #059669 0%, #10b981 100%); color: #ffffff; font-weight: bold; font-size: 11.5px; padding: 2px 7px; border-radius: 4px; border: 1px solid #34d399; }
    .badge-accel-off { background-color: #374151; color: #9ca3af; font-size: 11.5px; padding: 2px 7px; border-radius: 4px; border: 1px solid #4b5563; }

    .badge-style-nige { background: linear-gradient(135deg, #e11d48 0%, #be123c 100%); color: #ffffff; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #fda4af; }
    .badge-style-senko { background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: #ffffff; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #93c5fd; }
    .badge-style-sashi { background: linear-gradient(135deg, #059669 0%, #047857 100%); color: #ffffff; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #6ee7b7; }
    .badge-style-oikomi { background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%); color: #ffffff; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #c4b5fd; }
    .badge-style-chudan { background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); color: #ffffff; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #7dd3fc; }
    .badge-style-other { background-color: #374151; color: #e5e7eb; font-weight: bold; font-size: 12px; padding: 2px 8px; border-radius: 4px; border: 1px solid #6b7280; }

    /* 全指数色分けハイライトスタイル */
    .val-rank1-gold { color: #1a1000; background-color: #fcd34d; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #f59e0b; }
    .val-f-top { color: #ffffff; background-color: #ea580c; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #fb923c; }
    .val-s-top { color: #ffffff; background-color: #8b5cf6; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #c4b5fd; }
    .val-arms-top { color: #083344; background-color: #38bdf8; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #0284c7; }
    .val-tua-top { color: #022c22; background-color: #34d399; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #059669; }
    .val-course-top { color: #ffffff; background-color: #0d9488; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #2dd4bf; }
    .val-sub-top { color: #e0f2fe; background-color: #1e40af; font-weight: bold; padding: 1px 6px; border-radius: 4px; border: 1px solid #60a5fa; }
    .val-normal { color: #cbd5e1; font-weight: normal; }

    /* 坂路調教秒数ハイライト */
    .highlight-han-a3 { color: #10b981; font-weight: bold; background-color: rgba(16, 185, 129, 0.15); padding: 1px 5px; border-radius: 4px; border: 1px solid #059669; }
    .highlight-han-a2 { color: #38bdf8; font-weight: bold; background-color: rgba(56, 189, 248, 0.15); padding: 1px 5px; border-radius: 4px; border: 1px solid #0284c7; }
    .highlight-han-a1 { color: #fcd34d; font-weight: bold; background-color: rgba(252, 211, 77, 0.15); padding: 1px 5px; border-radius: 4px; border: 1px solid #d97706; }
    .highlight-han-fast1f-super { color: #ef4444; font-weight: 900; background: rgba(239, 68, 68, 0.2); padding: 1px 6px; border-radius: 4px; border: 1px solid #f87171; }
    .highlight-han-fast1f-good { color: #f59e0b; font-weight: bold; background: rgba(245, 158, 11, 0.15); padding: 1px 6px; border-radius: 4px; border: 1px solid #fbbf24; }
    .highlight-han-fast4f { color: #38bdf8; font-weight: bold; }
    
    .badge-cushion-fit { display: inline-flex; align-items: center; background: linear-gradient(135deg, #059669 0%, #10b981 100%); color: #ffffff; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #34d399; }
    .badge-cushion-danger { display: inline-flex; align-items: center; background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%); color: #ffffff; font-weight: bold; font-size: 11.5px; padding: 2px 8px; border-radius: 6px; border: 1px solid #f87171; }
    
    /* マークバッジ：文字が縦に潰れないよう横幅・高さを自動調整 */
    .badge-mark-honmei { display: inline-flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%); color: #ffffff; font-size: 12.5px; font-weight: 900; width: auto; height: auto; padding: 2px 8px; border-radius: 4px; border: 1px solid #fca5a5; margin-right: 6px; }
    .badge-mark-taikou { display: inline-flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: #ffffff; font-size: 12.5px; font-weight: 900; width: auto; height: auto; padding: 2px 8px; border-radius: 4px; border: 1px solid #93c5fd; margin-right: 6px; }
    .badge-mark-tanana { display: inline-flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #059669 0%, #047857 100%); color: #ffffff; font-size: 12.5px; font-weight: 900; width: auto; height: auto; padding: 2px 8px; border-radius: 4px; border: 1px solid #6ee7b7; margin-right: 6px; }
    .badge-mark-himo { display: inline-flex; align-items: center; justify-content: center; background-color: #374151; color: #f3f4f6; font-size: 12.5px; font-weight: bold; width: auto; height: auto; padding: 2px 8px; border-radius: 4px; border: 1px solid #6b7280; margin-right: 6px; }
    .badge-mark-ana { display: inline-flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #d97706 0%, #b45309 100%); color: #ffffff; font-size: 12.5px; font-weight: 900; width: auto; height: auto; padding: 2px 8px; border-radius: 4px; border: 1px solid #fde68a; margin-right: 6px; }
</style>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# ★ 2026年全データベース抽出「現役最強コース巧者（同コース3戦以上＆複勝率80〜100%）」内蔵辞書
# ==============================================================================
COURSE_SPECIALIST_DICT = {
    ('カンレイスター', '中山', 'ダ', 1200): '5戦1勝・3着内5回(複100%)',
    ('ルヴァレドクール', '東京', 'ダ', 1600): '4戦3勝・3着内4回(複100%)',
    ('ザーフィル', '東京', 'ダ', 1600): '4戦2勝・3着内4回(複100%)',
    ('ミスターキャンベラ', '中山', 'ダ', 1800): '4戦2勝・3着内4回(複100%)',
    ('セッシュウ', '中京', 'ダ', 1400): '4戦1勝・3着内4回(複100%)',
    ('ファンシーフリル', '小倉', 'ダ', 1000): '4戦1勝・3着内4回(複100%)',
    ('フジガイフウ', '東京', '芝', 1600): '4戦1勝・3着内4回(複100%)',
    ('マタミカンサン', '中山', 'ダ', 1800): '4戦1勝・3着内4回(複100%)',
    ('メイショウナナユキ', '阪神', 'ダ', 1400): '4戦1勝・3着内4回(複100%)',
    ('サラサチャチャチャ', '中山', 'ダ', 1800): '4戦0勝・3着内4回(複100%)',
    ('メディチパワー', '中山', 'ダ', 1800): '5戦3勝・3着内4回(複80%)',
    ('イブキ', '東京', '芝', 2400): '5戦2勝・3着内4回(複80%)',
    ('サイモンシュバリエ', '京都', 'ダ', 1800): '5戦2勝・3着内4回(複80%)',
    ('チームユートピア', '東京', 'ダ', 1400): '5戦2勝・3着内4回(複80%)',
    ('モーゲンセン', '中山', 'ダ', 1200): '5戦2勝・3着内4回(複80%)',
    ('ドゥマーヴェリック', '中山', 'ダ', 1800): '5戦1勝・3着内4回(複80%)',
    ('ペプチドレオン', '京都', 'ダ', 1400): '5戦1勝・3着内4回(複80%)',
    ('クロナ', '函館', 'ダ', 1000): '3戦3勝・3着内3回(複100%)',
    ('リサシテーション', '阪神', 'ダ', 1400): '3戦3勝・3着内3回(複100%)',
    ('アスクセクシーモア', '東京', '芝', 2000): '3戦2勝・3着内3回(複100%)',
    ('エアトベーレ', '福島', 'ダ', 1700): '3戦2勝・3着内3回(複100%)',
    ('カフジエメンタール', '阪神', '芝', 1800): '3戦2勝・3着内3回(複100%)',
    ('グランドプラージュ', '京都', 'ダ', 1800): '3戦2勝・3着内3回(複100%)',
    ('コウセキ', '小倉', '芝', 1200): '3戦2勝・3着内3回(複100%)',
    ('シーズザスローン', '函館', 'ダ', 1700): '3戦2勝・3着内3回(複100%)',
    ('ジェイエルモーダル', '中山', 'ダ', 1800): '3戦2勝・3着内3回(複100%)',
    ('スナッピードレッサ', '東京', 'ダ', 1400): '3戦2勝・3着内3回(複100%)',
    ('スリーケイ', '札幌', 'ダ', 1700): '3戦2勝・3着内3回(複100%)',
    ('チェリヴェント', '阪神', 'ダ', 1800): '3戦2勝・3着内3回(複100%)',
    ('ベルジュロネット', '阪神', 'ダ', 1400): '3戦2勝・3着内3回(複100%)',
    ('ペイシャケイプ', '東京', 'ダ', 1400): '3戦2勝・3着内3回(複100%)',
    ('ルシード', '京都', '芝', 1200): '3戦2勝・3着内3回(複100%)',
    ('ロードヴォイジャー', '京都', 'ダ', 1800): '3戦2勝・3着内3回(複100%)',
    ('ヴィスマール', '京都', '芝', 2000): '3戦2勝・3着内3回(複100%)',
    ('アストリル', '小倉', '芝', 2000): '3戦1勝・3着内3回(複100%)',
    ('アルサック', '函館', '芝', 1200): '3戦1勝・3着内3回(複100%)',
    ('アヴィオン', '京都', '芝', 1600): '3戦1勝・3着内3回(複100%)',
    ('インパクトシー', '中山', '芝', 1600): '3戦1勝・3着内3回(複100%)',
    ('エクリプスルバン', '中山', 'ダ', 1800): '3戦1勝・3着内3回(複100%)',
    ('エスシービクトリア', '中山', 'ダ', 1800): '3戦1勝・3着内3回(複100%)',
    ('カウスリップ', '新潟', '芝', 1000): '3戦1勝・3着内3回(複100%)',
    ('カットソロ', '阪神', '芝', 2400): '3戦1勝・3着内3回(複100%)',
    ('クリムゾンリーフ', '新潟', 'ダ', 1800): '3戦1勝・3着内3回(複100%)',
    ('グリオンヴール', '東京', '芝', 1400): '3戦1勝・3着内3回(複100%)',
    ('グレイトソン', '函館', 'ダ', 1000): '3戦1勝・3着内3回(複100%)',
    ('ケンタッキーホーム', '京都', 'ダ', 1800): '3戦1勝・3着内3回(複100%)',
    ('コスモイシュタル', '福島', '芝', 2000): '3戦1勝・3着内3回(複100%)',
    ('コズミックダンサー', '中山', 'ダ', 2400): '3戦1勝・3着内3回(複100%)',
    ('サマーナイト', '札幌', 'ダ', 1700): '3戦1勝・3着内3回(複100%)',
    ('サムシングスイート', '中山', '芝', 2000): '3戦1勝・3着内3回(複100%)',
    ('サンライズバレット', '京都', 'ダ', 1800): '3戦1勝・3着内3回(複100%)',
    ('シャンデルナゴル', '中山', 'ダ', 2880): '3戦1勝・3着内3回(複100%)',
    ('ジャスティンシカゴ', '東京', '芝', 2000): '3戦1勝・3着内3回(複100%)',
    ('ジューンエオス', '小倉', 'ダ', 1700): '3戦1勝・3着内3回(複100%)',
    ('タイセイディアマン', '阪神', 'ダ', 1200): '3戦1勝・3着内3回(複100%)',
    ('タカスタカスタカス', '中山', 'ダ', 1200): '3戦1勝・3着内3回(複100%)',
    ('タケルフォーカス', '札幌', '芝', 2600): '3戦1勝・3着内3回(複100%)',
    ('ダイチノナポリ', '京都', '芝', 1800): '3戦1勝・3着内3回(複100%)',
    ('テンカムテキ', '中山', 'ダ', 1800): '3戦1勝・3着内3回(複100%)',
    ('ドッグウッド', '函館', '芝', 1800): '3戦1勝・3着内3回(複100%)',
    ('ハギノコラソン', '京都', 'ダ', 1800): '3戦1勝・3着内3回(複100%)',
    ('パラダイスフェイス', '中山', 'ダ', 1800): '3戦1勝・3着内3回(複100%)',
    ('ビタミンドロップ', '函館', 'ダ', 1000): '3戦1勝・3着内3回(複100%)',
    ('ビーチイン', '函館', 'ダ', 1700): '3戦1勝・3着内3回(複100%)',
    ('ビービーアジャイル', '東京', 'ダ', 2100): '3戦1勝・3着内3回(複100%)',
    ('ブラックジェダイト', '中山', '芝', 1600): '3戦1勝・3着内3回(複100%)',
    ('ブレイズランナー', '函館', 'ダ', 1700): '3戦1勝・3着内3回(複100%)',
    ('ブレトワルダ', '新潟', 'ダ', 1800): '3戦1勝・3着内3回(複100%)',
    ('マナボニート', '函館', '芝', 1200): '3戦1勝・3着内3回(複100%)',
    ('マリリンバローズ', '阪神', 'ダ', 1200): '3戦1勝・3着内3回(複100%)',
    ('メイショウセンドウ', '札幌', 'ダ', 1700): '3戦1勝・3着内3回(複100%)',
    ('モデレートゲイル', '東京', 'ダ', 2100): '3戦1勝・3着内3回(複100%)',
    ('ラヴネヴァーダイズ', '阪神', 'ダ', 1200): '3戦1勝・3着内3回(複100%)',
    ('ルイステソーロ', '中山', 'ダ', 1200): '3戦1勝・3着内3回(複100%)',
    ('ルクスデイジー', '京都', 'ダ', 1200): '3戦1勝・3着内3回(複100%)',
    ('ルージュボニート', '札幌', 'ダ', 1700): '3戦1勝・3着内3回(複100%)',
    ('ルールザウェイヴ', '札幌', '芝', 1500): '3戦1勝・3着内3回(複100%)',
    ('ワディアルリヤハ', '東京', '芝', 1400): '3戦1勝・3着内3回(複100%)',
    ('アスクデッドヒート', '小倉', '芝', 2600): '3戦0勝・3着内3回(複100%)',
    ('アドミ', '中山', 'ダ', 1200): '3戦0勝・3着内3回(複100%)',
    ('アンシュウマト', '中山', 'ダ', 1800): '3戦0勝・3着内3回(複100%)',
    ('ウルスクローム', '阪神', 'ダ', 1200): '3戦0勝・3着内3回(複100%)',
    ('オウケンブラッド', '阪神', 'ダ', 1400): '3戦0勝・3着内3回(複100%)',
    ('キセログラフィカ', '中山', 'ダ', 1800): '3戦0勝・3着内3回(複100%)',
    ('キミガスキダ', '中京', 'ダ', 1800): '3戦0勝・3着内3回(複100%)',
    ('ギンケイ', '中山', 'ダ', 1800): '3戦0勝・3着内3回(複100%)',
    ('ゴーフォアブローク', '中山', 'ダ', 1800): '3戦0勝・3着内3回(複100%)',
    ('ゴールデンドラゴン', '中京', 'ダ', 1800): '3戦0勝・3着内3回(複100%)',
    ('サクラドール', '東京', 'ダ', 1400): '3戦0勝・3着内3回(複100%)',
    ('スイーヴル', '函館', 'ダ', 1000): '3戦0勝・3着内3回(複100%)',
    ('セイフウサツキ', '小倉', '芝', 2860): '3戦0勝・3着内3回(複100%)',
    ('ティタノマキア', '京都', '芝', 2000): '3戦0勝・3着内3回(複100%)',
    ('トリニタリオ', '函館', '芝', 1800): '3戦0勝・3着内3回(複100%)',
    ('ナブッコ', '札幌', 'ダ', 1000): '3戦0勝・3着内3回(複100%)',
    ('ハングローズ', '東京', 'ダ', 1400): '3戦0勝・3着内3回(複100%)',
    ('ビスケットアソート', '京都', 'ダ', 1200): '3戦0勝・3着内3回(複100%)',
    ('ビッグヒーロー', '中京', '芝', 1600): '3戦0勝・3着内3回(複100%)',
    ('フォルテフィオーレ', '小倉', '芝', 1800): '3戦0勝・3着内3回(複100%)',
    ('プリプリプリン', '東京', 'ダ', 1400): '3戦0勝・3着内3回(複100%)',
    ('プリンセスアツコ', '京都', 'ダ', 1400): '3戦0勝・3着内3回(複100%)',
    ('ベルファスト', '小倉', '芝', 1200): '3戦0勝・3着内3回(複100%)',
    ('ホウオウシェリー', '東京', '芝', 1400): '3戦0勝・3着内3回(複100%)',
    ('マメーアップル', '函館', '芝', 1200): '3戦0勝・3着内3回(複100%)',
    ('ミスタートントン', '中山', 'ダ', 1200): '3戦0勝・3着内3回(複100%)',
    ('メイショウマドンナ', '札幌', 'ダ', 1000): '3戦0勝・3着内3回(複100%)',
    ('メイワキラリ', '小倉', 'ダ', 1000): '3戦0勝・3着内3回(複100%)',
    ('モックモック', '阪神', 'ダ', 1800): '3戦0勝・3着内3回(複100%)',
    ('ロードアマルフィ', '小倉', 'ダ', 1700): '3戦0勝・3着内3回(複100%)',
    ('メリフルアス', '京都', 'ダ', 1200): '4戦0勝・3着内3回(複75%)',
    ('アヴァランチ', '東京', 'ダ', 1300): '3戦0勝・3着内2回(複67%)',
    ('マツリダイコ', '東京', '芝', 1600): '3戦0勝・3着内2回(複67%)',
    ('ニホンピロデヴィン', '京都', 'ダ', 1800): '3戦0勝・3着内2回(複67%)',
}

SIRE_COURSE_MATRIX_TOP = {
    ('阪神', '1800', 'キズナ', '9.5-9.9 標準高'): '最重要特注 (勝19.6%/単421%)',
    ('東京', '1600', 'エピファネイア', '9.5-9.9 標準高'): '最重要特注 (勝13.3%/単277%)',
    ('東京', '1400', 'モーリス', '9.5-9.9 標準高'): '最重要特注 (勝10.1%/単408%)',
    ('東京', '1800', 'ディープインパクト', '9.5-9.9 標準高'): '最重要特注 (勝15.8%/単228%)',
    ('東京', '2000', 'キズナ', '8.6-9.4 やや低'): '最重要特注 (勝19.7%/単200%)',
    ('中京', '2000', 'ディープインパクト', '8.6-9.4 やや低'): '最重要特注 (勝18.0%/単178%)',
    ('東京', '1600', 'イスラボニータ', '8.6-9.4 やや低'): '最重要特注 (勝10.5%/単350%)',
    ('東京', '2000', 'エピファネイア', '8.6-9.4 やや低'): '最重要特注 (勝15.3%/単149%)',
    ('函館', '1800', 'キズナ', '≤8.5低'): '最重要特注 (勝17.7%/単143%)',
    ('小倉', '1200', 'ダイワメジャー', '9.5-9.9 標準高'): '最重要特注 (勝13.6%/単173%)',
    ('札幌', '2000', 'オルフェーヴル', '≤8.5低'): '最重要特注 (勝15.8%/単136%)',
    ('東京', '1400', 'ロードカナロア', '8.6-9.4 やや低'): '最重要特注 (勝15.6%/単123%)',
    ('阪神', '1600', 'ルーラーシップ', '8.6-9.4 やや低'): '最重要特注 (勝20.0%/単156%)',
    ('東京', '1600', 'モーリス', '9.5-9.9 標準高'): '最重要特注 (勝11.1%/単100%)',
    ('阪神', '2000', 'キズナ', '8.6-9.4 やや低'): '最重要特注 (勝11.8%/単152%)',
    ('東京', '1600', 'スクリーンヒーロー', '8.6-9.4 やや低'): '最重要特注 (勝9.9%/単72%)',
    ('小倉', '1200', 'ビッグアーサー', '8.6-9.4 やや低'): '最重要特注 (勝12.2%/単131%)',
    ('中京', '1600', 'ロードカナロア', '10.0-10.4高'): '最重要特注 (勝14.8%/単133%)',
    ('福島', '1200', 'ビッグアーサー', '8.6-9.4 やや低'): '最重要特注 (勝13.2%/単87%)',
    ('札幌', '1200', 'ロードカナロア', '≤8.5低'): '最重要特注 (勝15.0%/単121%)',
}

SIRE_COURSE_MATRIX_DANGER = {
    ('中山', '2000', 'ダノンバラード', '9.5-9.9 標準高'): '超危険 (複勝率0%)',
    ('東京', '2000', 'ルーラーシップ', '9.5-9.9 標準高'): '危険 (複勝率9.1%)',
    ('小倉', '1200', 'ジャスタウェイ', '8.6-9.4 やや低'): '超危険 (複勝率2.9%)',
    ('東京', '1400', 'シルバーステート', '8.6-9.4 やや低'): '超危険 (複勝率4.7%)',
    ('東京', '1600', 'ゴールドシップ', '8.6-9.4 やや低'): '超危険 (複勝率4.5%)',
    ('小倉', '1200', 'ヴィクトワールピサ', '8.6-9.4 やや低'): '超危険 (複勝率4.8%)',
    ('東京', '1800', 'ルーラーシップ', '9.5-9.9 標準高'): '危険 (複勝率10.5%)',
    ('阪神', '2000', 'ゴールドシップ', '8.6-9.4 やや低'): '危険 (複勝率10.0%)',
    ('東京', '1600', 'エイシンフラッシュ', '8.6-9.4 やや低'): '危険 (複勝率7.3%)',
    ('東京', '2000', 'オルフェーヴル', '8.6-9.4 やや低'): '危険 (複勝率13.2%)',
    ('福島', '2000', 'ルーラーシップ', '8.6-9.4 やや低'): '超危険 (複勝率4.7%)',
    ('新潟', '1400', 'リオンディーズ', '8.6-9.4 やや低'): '危険 (複勝率6.7%)',
    ('東京', '2400', 'ゴールドシップ', '9.5-9.9 標準高'): '危険 (複勝率11.1%)',
    ('小倉', '1800', 'ルーラーシップ', '9.5-9.9 標準高'): '危険 (複勝率10.0%)',
    ('阪神', '1800', 'ハービンジャー', '9.5-9.9 標準高'): '危険 (複勝率10.0%)',
    ('東京', '1600', 'サトノクラウン', '8.6-9.4 やや低'): '危険 (複勝率9.7%)',
    ('福島', '1200', 'マツリダゴッホ', '8.6-9.4 やや低'): '危険 (複勝率5.9%)',
    ('東京', '1600', 'シルバーステート', '9.5-9.9 標準高'): '危険 (複勝率8.9%)',
    ('福島', '1200', 'カレンブラックヒル', '8.6-9.4 やや低'): '危険 (複勝率9.7%)',
    ('中京', '2000', 'オルフェーヴル', '8.6-9.4 やや低'): '危険 (複勝率15.2%)',
}

def clean_horse_name(name):
    if pd.isnull(name): return ''
    return str(name).strip().replace('*', '').replace('$', '').replace(' ', '').replace(' ', '')

def read_csv_robust(src):
    if src is None: return pd.DataFrame()
    encodings = ['utf-8', 'utf-8-sig', 'cp932', 'shift-jis']
    for enc in encodings:
        try:
            if hasattr(src, 'seek'): src.seek(0)
            df = pd.read_csv(src, encoding=enc, header=None)
            if not df.empty: return df
        except Exception: continue
    return pd.DataFrame()

# ==============================================================================
# ★ 3分割CSV 自動統合エンジン（全38列マスター生成仕様）
# ==============================================================================
def load_and_merge_3split_csvs(f_fup, f_s_sakaro, f_course):
    df_fup = read_csv_robust(f_fup)
    df_s = read_csv_robust(f_s_sakaro)
    df_c = read_csv_robust(f_course)

    if df_fup.empty:
        # デフォルトでローカルファイルを探す
        fup_files = glob.glob('*Fup*.csv') + glob.glob('data/*Fup*.csv')
        if fup_files: df_fup = read_csv_robust(max(fup_files, key=os.path.getmtime))
    
    if df_s.empty:
        s_files = glob.glob('*坂路*.csv') + glob.glob('data/*坂路*.csv') + glob.glob('*時計血*.csv')
        if s_files: df_s = read_csv_robust(max(s_files, key=os.path.getmtime))

    if df_c.empty:
        c_files = glob.glob('*コース連*.csv') + glob.glob('data/*コース連*.csv') + glob.glob('*arms*.csv')
        if c_files: df_c = read_csv_robust(max(c_files, key=os.path.getmtime))

    if df_fup.empty:
        return pd.DataFrame(), datetime.date.today()

    # 結合キー構築 (場所R: col 1, 馬番: col 4 in df_fup)
    df_fup['key'] = df_fup[1].astype(str).str.strip() + '_' + df_fup[4].astype(str).str.strip()
    
    if not df_s.empty:
        df_s['key'] = df_s[0].astype(str).str.strip() + '_' + df_s[1].astype(str).str.strip()
        merged = pd.merge(df_fup, df_s, on='key', suffixes=('', '_s'))
    else:
        merged = df_fup.copy()

    if not df_c.empty:
        df_c['key'] = df_c[0].astype(str).str.strip() + '_' + df_c[1].astype(str).str.strip()
        merged = pd.merge(merged, df_c, on='key', suffixes=('', '_c'))

    records = []
    venue_dict = {
        '東': '東京', '中': '中山', '京': '京都', '阪': '阪神', '名': '中京',
        '小': '小倉', '新': '新潟', '福': '福島', '函': '函館', '札': '札幌',
    }

    for _, row in merged.iterrows():
        # 基本情報
        race_id = str(row.get(1, '')).strip()
        track_raw = str(row.get(2, '')).strip()
        dist_val = row.get(3, 1600)
        umaban = row.get(4, 99)
        c_marker = str(row.get(5, '')).strip()
        horse = clean_horse_name(row.get(6, ''))
        trainer = clean_horse_name(row.get(8, ''))
        jockey = clean_horse_name(row.get(9, ''))
        pop = row.get(10, 99)
        mark = row.get(11, '')

        track = 'ダ' if 'ダ' in track_raw else ('芝' if '芝' in track_raw else '芝')
        dist_int = int(re.sub(r'\D', '', str(dist_val))) if re.sub(r'\D', '', str(dist_val)).isdigit() else 1600

        # 指数
        fup = pd.to_numeric(row.get(14), errors='coerce')
        fup_rank = pd.to_numeric(row.get(15), errors='coerce')
        f_val = pd.to_numeric(row.get(16), errors='coerce')
        f_rank = pd.to_numeric(row.get(17), errors='coerce')
        arms_val = pd.to_numeric(row.get(18), errors='coerce')
        arms_rank = pd.to_numeric(row.get(19), errors='coerce')
        tua_val = pd.to_numeric(row.get(20), errors='coerce')
        tua_rank = pd.to_numeric(row.get(21), errors='coerce')

        # S / 坂路等 (df_s由来)
        s_val = pd.to_numeric(row.get(2, 's'), errors='coerce')
        s_rank = pd.to_numeric(row.get(3, 's'), errors='coerce')
        hanro_cho_val = pd.to_numeric(row.get(4, 's'), errors='coerce')
        hanro_cho_rank = pd.to_numeric(row.get(5, 's'), errors='coerce')
        hanro_ketsu_val = pd.to_numeric(row.get(6, 's'), errors='coerce')
        hanro_ketsu_rank = pd.to_numeric(row.get(7, 's'), errors='coerce')
        tokei_ketsu_val = pd.to_numeric(row.get(8, 's'), errors='coerce')
        tokei_ketsu_rank = pd.to_numeric(row.get(9, 's'), errors='coerce')

        # コース連・血統連・バランス・arms (df_c由来)
        course_ren_val = pd.to_numeric(row.get(2, 'c'), errors='coerce')
        course_ren_rank = pd.to_numeric(row.get(3, 'c'), errors='coerce')
        ketsu_ren_val = pd.to_numeric(row.get(4, 'c'), errors='coerce')
        ketsu_ren_rank = pd.to_numeric(row.get(5, 'c'), errors='coerce')
        balance_val = pd.to_numeric(row.get(6, 'c'), errors='coerce')
        balance_rank = pd.to_numeric(row.get(7, 'c'), errors='coerce')

        sire = str(row.get(22, '')).strip()
        raw_style = str(row.get(26, '')).strip()

        # 脚質判定
        if '逃' in raw_style: style = '逃げ'
        elif '先' in raw_style: style = '先行'
        elif '差' in raw_style: style = '差し'
        elif '追' in raw_style: style = '追込'
        elif s_rank == 1 and s_val >= 50.0: style = '逃げ'
        elif s_rank <= 3: style = '先行'
        else: style = '中団'

        match_venue = re.match(r'([^\d]+)(\d+)', race_id)
        venue_name = venue_dict.get(match_venue.group(1), match_venue.group(1)) if match_venue else '東京'

        if horse:
            records.append({
                'race_id': race_id, 'race_uid': race_id, '競馬場名': venue_name,
                'track': track, 'dist': dist_int,
                '馬番': int(float(umaban)) if pd.notnull(umaban) and str(umaban).replace('.','',1).isdigit() else 99,
                '馬名': horse, 'C馬': c_marker, '印': str(mark).strip(),
                '調教師': trainer, '騎手': jockey, '種牡馬': sire,
                '人気': int(float(pop)) if pd.notnull(pop) and str(pop).replace('.','',1).isdigit() else 99,
                '着順': None, '脚質': style,
                'Fup': int(fup) if pd.notnull(fup) else 0,
                'Fup_rank': int(fup_rank) if pd.notnull(fup_rank) else 99,
                'F指数': f_val if pd.notnull(f_val) else 0.0,
                'F_rank': int(f_rank) if pd.notnull(f_rank) else 99,
                'arms': arms_val if pd.notnull(arms_val) else 0.0,
                'arms_rank': int(arms_rank) if pd.notnull(arms_rank) else 99,
                'tua': tua_val if pd.notnull(tua_val) else 0.0,
                'tua_rank': int(tua_rank) if pd.notnull(tua_rank) else 99,
                'S指数': s_val if pd.notnull(s_val) else 0.0,
                'S_rank': int(s_rank) if pd.notnull(s_rank) else 99,
                '坂路調': hanro_cho_val if pd.notnull(hanro_cho_val) else 0.0,
                '坂路調順位': int(hanro_cho_rank) if pd.notnull(hanro_cho_rank) else 99,
                '坂路血': hanro_ketsu_val if pd.notnull(hanro_ketsu_val) else 0.0,
                '坂路血順位': int(hanro_ketsu_rank) if pd.notnull(hanro_ketsu_rank) else 99,
                '時計血': tokei_ketsu_val if pd.notnull(tokei_ketsu_val) else 0.0,
                '時計血順位': int(tokei_ketsu_rank) if pd.notnull(tokei_ketsu_rank) else 99,
                'コース連': course_ren_val if pd.notnull(course_ren_val) else 0.0,
                'コース連順位': int(course_ren_rank) if pd.notnull(course_ren_rank) else 99,
                '血統連': ketsu_ren_val if pd.notnull(ketsu_ren_val) else 0.0,
                '血統連順位': int(ketsu_ren_rank) if pd.notnull(ketsu_ren_rank) else 99,
                'バランス': balance_val if pd.notnull(balance_val) else 0.0,
                'バランス順位': int(balance_rank) if pd.notnull(balance_rank) else 99,
            })

    df_main = pd.DataFrame(records)
    df_main['total_horses'] = df_main.groupby('race_id')['馬番'].transform('count')
    df_main['枠番'] = df_main.apply(lambda r: get_jra_waku(r['馬番'], r['total_horses']), axis=1)
    
    # ダミーの坂路ラップ型・加速判定
    df_main['坂路_ラップ型'] = 'A2'
    df_main['is_complete_accel'] = True
    df_main['accel_11s'] = False
    df_main['is_super_fast_b'] = False
    df_main['坂路_1F'] = 12.2
    df_main['坂路_4F'] = 52.5

    # 現役最強コース巧者判定
    df_main['course_spec_info'] = df_main.apply(lambda r: COURSE_SPECIALIST_DICT.get((r['馬名'], r['競馬場名'], r['track'], r['dist']), ''), axis=1)
    df_main['is_course_specialist'] = df_main['course_spec_info'] != ''

    return df_main, datetime.date.today()

def get_jra_waku(umaban, total_horses):
    if total_horses <= 8: return umaban
    base = total_horses // 8
    rem = total_horses % 8
    waku_counts = [base + (1 if 8 - i <= rem else 0) for i in range(8)]
    curr = 1
    for w_idx, cnt in enumerate(waku_counts, start=1):
        if curr <= umaban < curr + cnt: return w_idx
        curr += cnt
    return 8

def get_running_style_badge(style_str):
    s = str(style_str).strip()
    if '逃' in s: return "<span class='badge-style-nige'>🏃 逃げ</span>"
    elif '先' in s: return "<span class='badge-style-senko'>🐎 先行</span>"
    elif '差' in s: return "<span class='badge-style-sashi'>⚡ 差し</span>"
    elif '追' in s: return "<span class='badge-style-oikomi'>🔥 追込</span>"
    return f"<span class='badge-style-other'>{s}</span>"

def get_cushion_band(venue, c_val):
    c = float(c_val)
    if c <= 8.5: return '≤8.5低'
    elif c <= 9.4: return '8.6-9.4 やや低'
    elif c <= 9.9: return '9.5-9.9 標準高'
    elif c <= 10.4: return '10.0-10.4高'
    else: return '≥10.5 超高'

def get_current_cushion_bin_name(c_val):
    c = float(c_val)
    if c < 8.0: return '7以下'
    elif c < 9.0: return '8台'
    elif c < 10.0: return '9台'
    elif c < 11.0: return '10台'
    else: return '11以上'

def evaluate_sire_cushion(sire_name, venue, dist_str, band_str):
    sire = clean_horse_name(sire_name)
    dist = str(dist_str)
    v = str(venue).strip()
    b = str(band_str).strip()
    key = (v, dist, sire, b)
    if key in SIRE_COURSE_MATRIX_TOP:
        return f"<span class='badge-cushion-fit'>🟢 {sire}特注 ({SIRE_COURSE_MATRIX_TOP[key]})</span>"
    if key in SIRE_COURSE_MATRIX_DANGER:
        return f"<span class='badge-cushion-danger'>⚠️ {sire}危険 ({SIRE_COURSE_MATRIX_DANGER[key]})</span>"
    return ""

# ==============================================================================
# サイドバー＆ファイルアップローダー（3分割CSV対応）
# ==============================================================================
st.sidebar.markdown('### 📁 3分割CSVデータ読み込み')
with st.sidebar.expander('3分割CSVファイル指定', expanded=True):
    up_fup = st.file_uploader('1. Fup,F,ARM,TUA CSV', type=['csv'], key='up_fup')
    up_s = st.file_uploader('2. S,坂路調,時計血 CSV', type=['csv'], key='up_s')
    up_c = st.file_uploader('3. コース連,バランス,arms CSV', type=['csv'], key='up_c')

df, race_date = load_and_merge_3split_csvs(up_fup, up_s, up_c)

if df.empty:
    st.warning('⚠️ 3分割CSVファイルが読み込まれていません。サイドバーからCSVファイルを指定するか、同じディレクトリに配置してください。')
    st.stop()

# 型安全性確保
df['dist'] = pd.to_numeric(df['dist'].astype(str).str.replace(r'\D', '', regex=True), errors='coerce').fillna(1600).astype(int)
for col_name in ['F指数', 'S指数', 'arms', 'tua', 'コース連', '血統連', '時計血', '坂路血', '坂路調', 'バランス', 'Fup']:
    if col_name in df.columns:
        df[col_name] = pd.to_numeric(df[col_name], errors='coerce').fillna(0.0)

# 判定項目フラグ
df['p1_hit_solid'] = (df['track'] == '芝') & (df['dist'].between(1500, 1800)) & (df['競馬場名'].isin(['東京', '中山', '京都', '阪神'])) & (df['F_rank'] <= 3) & (df['F指数'] >= 55) & (df['S_rank'] <= 3)
df['p2_dirt_tua'] = (df['track'] == 'ダ') & (df['S_rank'] <= 3) & (df['tua'] >= 190.0)
df['p3_short_local'] = ((df['dist'] <= 1400) | (df['競馬場名'].isin(['福島', '小倉', '函館']))) & (df['S_rank'] <= 3)
df['roi_tua1_dirt_ana'] = (df['track'] == 'ダ') & (df['tua_rank'] == 1) & (df['人気'].between(4, 8))
df['roi_tua1_turf_ana'] = (df['track'] == '芝') & (df['tua_rank'] == 1) & (df['人気'].between(4, 8))
df['roi_arm1_hanro1'] = (df['arms_rank'] == 1) & (df['人気'].between(3, 7))
df['roi_11s_ana'] = (df['人気'].between(3, 7))

def calc_upgraded_dynamic_score(r):
    score = 0.0
    f_rk = r.get('F_rank', 99)
    s_rk = r.get('S_rank', 99)
    c_rk = r.get('コース連順位', 99)
    b_rk = r.get('バランス順位', 99)
    fup = r.get('Fup', 0)
    pop = r.get('人気', 99)
    is_spec = r.get('is_course_specialist', False)

    if is_spec: score += 35.0
    else:
        if c_rk <= 3: score += 25.0
        elif c_rk >= 6: score -= 30.0

    if b_rk <= 3: score += 25.0
    elif b_rk >= 6: score -= 15.0

    if f_rk == 1: score += 50.0
    elif f_rk <= 3: score += 30.0
    if s_rk <= 3: score += 30.0

    if fup == 7: score += 45.0
    elif fup >= 5: score += 30.0
    elif fup == 4: score += 15.0

    if pop <= 3 and not is_spec and fup <= 1:
        score -= 35.0

    return score

df['dynamic_score'] = df.apply(calc_upgraded_dynamic_score, axis=1)

# サイドバー検索フィルタ
st.sidebar.markdown('---')
st.sidebar.markdown('### 🎯 新ロジック特注・回収率検索')
f_spec = st.sidebar.checkbox(f"🏆 現役最強コース巧者: 得意舞台戻り ({int(df['is_course_specialist'].sum())}頭)")
f_p1_solid = st.sidebar.checkbox(f"🎯 的中重視: 芝マイル中距離 F×S上位 ({int(df['p1_hit_solid'].sum())}頭)")
f_p2_dirt = st.sidebar.checkbox(f"🏜️ ダート堅実先行: S1-3位×TUA190+ ({int(df['p2_dirt_tua'].sum())}頭)")
f_p3_short = st.sidebar.checkbox(f"⚡ 短距離/ローカル先行 ({int(df['p3_short_local'].sum())}頭)")
f_course_ren = st.sidebar.checkbox(f"🏰 コース連1〜3位 ({int((df['コース連順位'] <= 3).sum())}頭)")

active_filters = []
f_map = [
    (f_spec, df['is_course_specialist']),
    (f_p1_solid, df['p1_hit_solid']),
    (f_p2_dirt, df['p2_dirt_tua']),
    (f_p3_short, df['p3_short_local']),
    (f_course_ren, df['コース連順位'] <= 3),
]
for act, srs in f_map:
    if act: active_filters.append(srs)

if active_filters:
    c_mask = pd.Series(True, index=df.index)
    for m in active_filters: c_mask = c_mask & m
    filtered_df = df[c_mask]
else:
    filtered_df = df.copy()

# メイン画面表示
venue_sort_order = ['東京', '中山', '京都', '阪神', '中京', '小倉', '新潟', '福島', '函館', '札幌']
existing_venues = [v for v in venue_sort_order if v in df['競馬場名'].unique()]
if 'active_venue' not in st.session_state or st.session_state['active_venue'] not in existing_venues:
    st.session_state['active_venue'] = existing_venues[0] if existing_venues else '京都'

current_active_v = st.session_state['active_venue']
cushion_state_key = f"cushion_val_{current_active_v}"
if cushion_state_key not in st.session_state:
    st.session_state[cushion_state_key] = 10.0 if current_active_v == '京都' else 9.5

st.sidebar.markdown(f"### 芝クッション値 ({current_active_v})")
current_cushion_val = st.sidebar.number_input(
    f"芝クッション値 ({current_active_v})",
    min_value=5.0, max_value=13.0, value=float(st.session_state[cushion_state_key]),
    step=0.1, key=cushion_state_key, label_visibility='collapsed',
)
current_band = get_cushion_band(current_active_v, current_cushion_val)
current_bin_name = get_current_cushion_bin_name(current_cushion_val)

df['cushion_badge_raw'] = df.apply(
    lambda r: evaluate_sire_cushion(r['種牡馬'], r['競馬場名'], r['dist'], current_band) if '芝' in str(r.get('track', '')) else '', axis=1
)
df['is_cushion_fit'] = df['cushion_badge_raw'].str.contains('特注')
df['is_cushion_danger'] = df['cushion_badge_raw'].str.contains('危険')

weekday_kanji = ['月', '火', '水', '木', '金', '土', '日']
w_str = weekday_kanji[race_date.weekday()]
st.markdown(
    f"<div class='date-header-badge'>📅 開催日: {race_date.year}年{race_date.month}月{race_date.day}日"
    f" ({w_str}) | クッション値Vr ({current_active_v}: {current_cushion_val} / {current_bin_name}) 稼働中</div>",
    unsafe_allow_html=True,
)

chosen_venue = st.radio('開催場選択', options=existing_venues, horizontal=True, label_visibility='collapsed')
st.session_state['active_venue'] = chosen_venue

v_df = filtered_df[filtered_df['競馬場名'] == chosen_venue]
races_in_v = v_df[['race_uid', 'race_id', 'track', 'dist']].drop_duplicates('race_uid')

race_options = {}
for _, r_row in races_in_v.iterrows():
    r_horses = df[df['race_uid'] == r_row['race_uid']]
    is_bonus = bool(((r_horses['F_rank'] <= 3) & (r_horses['arms_rank'] <= 3) & (r_horses['tua_rank'] <= 3)).sum() >= 3)
    tag = '👑ボーナス' if is_bonus else '🎯的確・回収'
    lbl = f"{tag} {r_row['race_uid']} ({r_row['track']}{r_row['dist']}m)"
    race_options[r_row['race_uid']] = lbl

if not race_options:
    st.warning("⚠️ 選択した開催場・フィルタ条件に合致するレースがありません。")
    st.stop()

selected_race_uid = st.selectbox(
    'レース選択',
    options=list(race_options.keys()),
    format_func=lambda x: race_options[x],
    label_visibility='collapsed',
)

race_df = df[df['race_uid'] == selected_race_uid].copy()
sorted_race = race_df.sort_values('dynamic_score', ascending=False)

st.markdown(
    f"<div class='race-type-banner race-type-bonus'>"
    f"<div><strong>👑 レース解析・標準ハイブリッド馬券パック連動</strong></div>"
    f"<div>推奨券種: 3連単フォーメーション / 3連複 / ワイド</div>"
    f"</div>",
    unsafe_allow_html=True,
)

pick_honmei = sorted_race.iloc[0]
rem_axis = sorted_race[sorted_race['馬番'] != pick_honmei['馬番']]
pick_taikou = rem_axis.iloc[0] if not rem_axis.empty else pick_honmei

ana_cands = sorted_race[
    (sorted_race['馬番'] != pick_honmei['馬番'])
    & (sorted_race['馬番'] != pick_taikou['馬番'])
    & (sorted_race['is_course_specialist'] | (sorted_race['Fup'] >= 4))
]
pick_ana = ana_cands.iloc[0] if not ana_cands.empty else (sorted_race.iloc[2] if len(sorted_race) > 2 else pick_taikou)

spec_horses_in_race = race_df[race_df['is_course_specialist']]
spec_str_list = [f"{int(r['馬番'])}番 {r['馬名']}（{r['course_spec_info']}）" for _, r in spec_horses_in_race.iterrows()]
spec_row_html = f"<div class='recom-row'>🏆 <strong>現役最強コース巧者</strong>: <span class='recom-val-num' style='color:#fcd34d;'>{' / '.join(spec_str_list)}</span></div>" if spec_str_list else ""

st.markdown(
    f"<div class='recom-panel-go'><div class='recom-title-go'>📋 推奨馬ピックアップ</div>"
    f"{spec_row_html}"
    f"<div class='recom-row'>🥇 <strong>本命・連軸</strong>: <span class='recom-val-num'>{int(pick_honmei['馬番'])}番 {pick_honmei['馬名']}</span>（F{int(pick_honmei['F_rank'])}位 / スコア:{pick_honmei['dynamic_score']:.1f}）</div>"
    f"<div class='recom-row'>🛡️ <strong>対抗・相手筆頭</strong>: <span class='recom-val-num'>{int(pick_taikou['馬番'])}番 {pick_taikou['馬名']}</span>（F{int(pick_taikou['F_rank'])}位 × S{int(pick_taikou['S_rank'])}位）</div>"
    f"<div class='recom-row'>💣 <strong>激走穴馬</strong>: <span class='recom-val-num'>{int(pick_ana['馬番'])}番 {pick_ana['馬名']}</span>（人気{int(pick_ana['人気'])}位 / TUA:{float(pick_ana['tua']):.1f}）</div>"
    f"</div>",
    unsafe_allow_html=True,
)

# ハイブリッド馬券パック
u_honmei = int(pick_honmei['馬番'])
u_taikou = int(pick_taikou['馬番'])
u_ana = int(pick_ana['馬番'])
col1_hybrid = [u_honmei]
col2_hybrid = [u_taikou, u_ana]
col3_hybrid = [u_honmei, u_taikou, u_ana] + [int(u) for u in sorted_race['馬番'].tolist() if int(u) not in [u_honmei, u_taikou, u_ana]][:3]

st.markdown(
    f"<div class='recom-panel-go'><div class='recom-title-go'>🎫 実戦買い目：標準ハイブリッド馬券パック</div>"
    f"<div class='recom-block'><strong>単勝</strong>: {u_honmei}番 / <strong>馬単</strong>: {u_honmei} → {u_taikou}, {u_ana}</div>"
    f"<div class='recom-block'><strong>3連複フォーメーション</strong>: 1列目[{u_honmei}] → 2列目[{u_taikou}, {u_ana}] → 3列目[{', '.join(map(str, col3_hybrid))}]</div>"
    f"</div>",
    unsafe_allow_html=True,
)

# 出走馬カルテ
st.markdown("### 🏇 出走馬詳細カルテ")
for _, h in race_df.sort_values('馬番').iterrows():
    u_no = int(h['馬番'])
    style_badge = get_running_style_badge(h.get('脚質', ''))
    badges = [style_badge]
    
    if u_no == u_honmei: badges.append("<span class='badge-mark-honmei'>◎ 本命</span>")
    elif u_no == u_taikou: badges.append("<span class='badge-mark-taikou'>◯ 対抗</span>")
    elif u_no == u_ana: badges.append("<span class='badge-mark-ana'>🔥 穴特注</span>")
    if h.get('is_course_specialist'): badges.append(f"<span class='val-rank1-gold'>🏆 最強コース巧者 ({h['course_spec_info']})</span>")

    badges_html = " ".join([b for b in badges if b])
    
    st.markdown(
        f"<div class='horse-card'>"
        f"<div class='horse-card-header'>"
        f"<span class='race-badge-title'>{u_no}番</span>"
        f"<span class='horse-card-title'>{h['馬名']}</span>"
        f"<span style='color:#94a3b8; font-size:13.5px;'>（{h.get('人気','')}番人気 / {h.get('騎手','')} / {h.get('調教師','')}）</span>"
        f"</div>"
        f"<div style='margin-bottom: 8px;'>{badges_html}</div>"
        f"<ul class='horse-card-list'>"
        f"<li><strong>主要5大指数</strong>: F指数: {h.get('F指数')} (F{int(h.get('F_rank',99))}位) / S指数: {h.get('S指数')} (S{int(h.get('S_rank',99))}位) / Fup2: {h.get('Fup')}点 / ARM: {h.get('arms')} / TUA: {h.get('tua')}</li>"
        f"<li><strong>コース・血統・バランス適性</strong>: バランス: {h.get('バランス')} (順位{int(h.get('バランス順位',99))}) / コース連: {h.get('コース連')} (順位{int(h.get('コース連順位',99))}) / 血統連: {h.get('血統連')} / 時計血: {h.get('時計血')} / 坂路血: {h.get('坂路血')}</li>"
        f"<li><strong>血統</strong>: 父 {h.get('種牡馬','-')}</li>"
        f"</ul>"
        f"</div>",
        unsafe_allow_html=True,
    )
